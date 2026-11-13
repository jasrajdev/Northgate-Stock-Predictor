"""Train LSTM, GRU, BiLSTM and Transformer on train/validation only.

The final test partition is never opened by this script. Defaults are deliberately
conservative for a 4 GB RTX 3050; override with NORTHGATE_* environment variables.
"""
from __future__ import annotations

import json
import os
import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ROOT / "data" / "processed" / "splits"
OUT = ROOT / "models" / "deep"
REPORT = ROOT / "reports" / "validation"

SEQ = int(os.getenv("NORTHGATE_SEQ_LEN", "30"))
EPOCHS = int(os.getenv("NORTHGATE_EPOCHS", "30"))
BATCH = int(os.getenv("NORTHGATE_BATCH_SIZE", "16"))
HIDDEN = int(os.getenv("NORTHGATE_HIDDEN_SIZE", "32"))
PATIENCE = int(os.getenv("NORTHGATE_PATIENCE", "6"))
SEED = 42
USE_AMP = os.getenv("NORTHGATE_AMP", "1") == "1"

def seed_all():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)

class Recurrent(nn.Module):
    def __init__(self, kind: str, n_features: int):
        super().__init__()
        bidir = kind == "BiLSTM"
        rnn_cls = nn.GRU if kind == "GRU" else nn.LSTM
        self.rnn = rnn_cls(
            n_features, HIDDEN, num_layers=1, batch_first=True,
            dropout=0.0, bidirectional=bidir,
        )
        width = HIDDEN * (2 if bidir else 1)
        self.head = nn.Sequential(
            nn.Dropout(0.15), nn.Linear(width, 16), nn.ReLU(), nn.Linear(16, 1)
        )

    def forward(self, x):
        z, _ = self.rnn(x)
        return self.head(z[:, -1]).squeeze(-1)

class TransformerRegressor(nn.Module):
    def __init__(self, n_features: int):
        super().__init__()
        self.proj = nn.Linear(n_features, HIDDEN)
        self.pos = nn.Parameter(torch.zeros(1, SEQ, HIDDEN))
        layer = nn.TransformerEncoderLayer(
            d_model=HIDDEN, nhead=4, dim_feedforward=HIDDEN * 2,
            dropout=0.1, batch_first=True, activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=1)
        self.head = nn.Sequential(
            nn.LayerNorm(HIDDEN), nn.Linear(HIDDEN, 16), nn.GELU(), nn.Linear(16, 1)
        )

    def forward(self, x):
        return self.head(self.encoder(self.proj(x) + self.pos)[:, -1]).squeeze(-1)

def make_sequences(frame, feature_cols, ticker_map, medians, means, stds):
    xs, ys, prices = [], [], []
    for ticker, group in frame.groupby("Ticker", sort=False):
        group = group.sort_values("Date")
        values = group[feature_cols].replace([np.inf, -np.inf], np.nan)
        values = values.fillna(medians)
        values = ((values - means) / stds).clip(-10, 10).to_numpy(dtype=np.float32)
        one_hot = np.zeros(len(ticker_map), dtype=np.float32)
        one_hot[ticker_map[ticker]] = 1.0
        values = np.concatenate(
            [values, np.repeat(one_hot[None, :], len(group), axis=0)], axis=1
        )
        returns = pd.to_numeric(group["target_log_return_t1"], errors="coerce").to_numpy()
        current = pd.to_numeric(group["Adj Close"], errors="coerce").to_numpy()
        for end in range(SEQ - 1, len(group)):
            if not np.isfinite(returns[end]) or not np.isfinite(current[end]) or current[end] <= 0:
                continue
            xs.append(values[end - SEQ + 1:end + 1])
            ys.append(returns[end])
            prices.append(current[end])
    if not xs:
        raise RuntimeError("No sequences built; inspect split length and input columns.")
    return (
        np.asarray(xs, dtype=np.float32),
        np.asarray(ys, dtype=np.float32),
        np.asarray(prices, dtype=np.float64),
    )

def evaluate(y_true, y_pred, current):
    actual = current * np.exp(y_true)
    predicted = current * np.exp(y_pred)
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "mape_pct": float(np.mean(np.abs((actual - predicted) / actual)) * 100),
        "r2": float(r2_score(actual, predicted)),
        "directional_accuracy": float(np.mean(np.sign(y_true) == np.sign(y_pred))),
    }

def predict_in_batches(model, x, device, use_amp):
    model.eval()
    preds = []
    with torch.no_grad():
        for start in range(0, len(x), BATCH):
            xb = torch.from_numpy(x[start:start + BATCH]).to(device)
            with torch.autocast(
                device_type="cuda", dtype=torch.float16,
                enabled=(device.type == "cuda" and use_amp),
            ):
                out = model(xb)
            preds.append(out.float().cpu().numpy())
    return np.concatenate(preds)

def train_one(name, model, train_data, val_data, device, metadata):
    x_train, y_train, _ = train_data
    x_val, y_val, current_val = val_data
    loader = DataLoader(
        TensorDataset(torch.from_numpy(x_train), torch.from_numpy(y_train)),
        batch_size=BATCH, shuffle=True, drop_last=False,
        pin_memory=(device.type == "cuda"), num_workers=0,
    )
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn = nn.HuberLoss()
    amp_enabled = device.type == "cuda" and USE_AMP
    scaler = torch.amp.GradScaler("cuda", enabled=amp_enabled)
    best_loss, best_state, stale = float("inf"), None, 0
    history = []

    for epoch in range(EPOCHS):
        model.train()
        losses = []
        for xb, yb in loader:
            xb = xb.to(device, non_blocking=True)
            yb = yb.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=amp_enabled):
                loss = loss_fn(model(xb), yb)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            losses.append(float(loss.detach().cpu()))

        val_preds = predict_in_batches(model, x_val, device, USE_AMP)
        val_loss = float(np.mean(np.square(val_preds - y_val)))
        history.append({
            "epoch": epoch + 1,
            "train_huber_loss": float(np.mean(losses)),
            "validation_mse_log_return": val_loss,
        })
        if val_loss < best_loss:
            best_loss, stale = val_loss, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            stale += 1
            if stale >= PATIENCE:
                break

    if best_state is None:
        raise RuntimeError(f"{name}: no valid checkpoint produced.")
    model.load_state_dict(best_state)
    val_preds = predict_in_batches(model, x_val, device, USE_AMP)
    OUT.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": best_state,
            "model": name,
            "sequence_length": SEQ,
            "hidden_size": HIDDEN,
            "ticker_map": metadata["ticker_map"],
            "feature_columns": metadata["feature_columns"],
            "medians": metadata["medians"],
            "means": metadata["means"],
            "stds": metadata["stds"],
        },
        OUT / f"{name.lower()}_best.pt",
    )
    return evaluate(y_val, val_preds, current_val), history

def main():
    seed_all()
    train_path, val_path = SPLITS / "train.csv", SPLITS / "validation.csv"
    if not train_path.exists() or not val_path.exists():
        raise FileNotFoundError(
            "Train/validation splits missing. Run scripts/prepare_gpu_training_data.py first."
        )

    train = pd.read_csv(train_path, parse_dates=["Date"])
    valid = pd.read_csv(val_path, parse_dates=["Date"])
    required = {"Ticker", "Date", "Adj Close", "target_log_return_t1"}
    for label, frame in (("train", train), ("validation", valid)):
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"{label}.csv missing required columns: {sorted(missing)}")

    train = train[train["Ticker"] != "^NSEI"].copy()
    valid = valid[valid["Ticker"] != "^NSEI"].copy()
    tickers = sorted(set(train["Ticker"]) & set(valid["Ticker"]))
    if not tickers:
        raise RuntimeError("No overlapping equity tickers in train and validation.")
    train = train[train["Ticker"].isin(tickers)].copy()
    valid = valid[valid["Ticker"].isin(tickers)].copy()

    excluded = {
        "Date", "Ticker", "Name", "target_date_t1", "target_adj_close_t1",
        "target_log_return_t1", "target_direction_t1",
    }
    features = [
        c for c in train.select_dtypes(include=[np.number]).columns
        if c not in excluded and c in valid.columns
    ]
    if "Adj Close" not in features:
        raise ValueError("Adj Close must be retained as a time-t feature.")
    if any(c.startswith("target_") for c in features):
        raise AssertionError("Target leakage: target_* column entered feature list.")

    numeric_train = train[features].replace([np.inf, -np.inf], np.nan)
    medians = numeric_train.median().fillna(0.0)
    filled = numeric_train.fillna(medians)
    means = filled.mean()
    stds = filled.std().replace(0, 1).fillna(1)
    ticker_map = {ticker: i for i, ticker in enumerate(tickers)}
    train_data = make_sequences(train, features, ticker_map, medians, means, stds)
    val_data = make_sequences(valid, features, ticker_map, medians, means, stds)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        props = torch.cuda.get_device_properties(0)
        print(f"GPU: {props.name} | VRAM: {props.total_memory / 1024**3:.2f} GiB")
    print(
        f"Device={device} | train_sequences={len(train_data[0]):,} "
        f"| validation_sequences={len(val_data[0]):,} | features={len(features)} "
        f"| sequence={SEQ} | batch={BATCH} | hidden={HIDDEN} | AMP={USE_AMP}"
    )

    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    metadata = {
        "ticker_map": ticker_map,
        "feature_columns": features,
        "medians": medians.to_dict(),
        "means": means.to_dict(),
        "stds": stds.to_dict(),
    }
    constructors = {
        "LSTM": lambda n: Recurrent("LSTM", n),
        "GRU": lambda n: Recurrent("GRU", n),
        "BiLSTM": lambda n: Recurrent("BiLSTM", n),
        "Transformer": lambda n: TransformerRegressor(n),
    }
    results, histories = [], {}
    for name, build in constructors.items():
        if device.type == "cuda":
            torch.cuda.empty_cache()
        model = build(train_data[0].shape[2])
        scores, history = train_one(name, model, train_data, val_data, device, metadata)
        results.append({"model": name, "device": str(device), **scores})
        histories[name] = history
        print(f"{name}: {scores}")

    pd.DataFrame(results).to_csv(REPORT / "deep_model_comparison_validation.csv", index=False)
    (REPORT / "deep_training_history.json").write_text(json.dumps(histories, indent=2))
    report = {
        "device": str(device),
        "cuda_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "gpu_vram_gib": (
            round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 3)
            if torch.cuda.is_available() else None
        ),
        "sequence_length": SEQ,
        "batch_size": BATCH,
        "hidden_size": HIDDEN,
        "amp_enabled": USE_AMP and device.type == "cuda",
        "feature_count": len(features),
        "features": features,
        "tickers": tickers,
        "train_sequences": len(train_data[0]),
        "validation_sequences": len(val_data[0]),
        "test_partition_loaded": False,
        "target": "next-session log return; converted to adjusted-close prediction",
        "preprocessing_fit_on_training_only": True,
        "target_columns_excluded": True,
        "results": results,
    }
    (REPORT / "deep_training_report.json").write_text(json.dumps(report, indent=2))
    print(f"Reports and checkpoints: {REPORT} and {OUT}")
    print("Final test partition was not loaded.")

if __name__ == "__main__":
    main()
