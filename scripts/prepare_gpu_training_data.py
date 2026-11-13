"""Rebuild Northgate's first price/volume-only training dataset from public downloads.

Run on the GPU laptop after cloning the repository:
    python scripts/prepare_gpu_training_data.py

This creates raw/processed data locally; market data are intentionally not committed
to Git because Yahoo Finance redistribution rights and data-vendor terms must be
respected. It does not fetch macro or news data and does not claim PRD completeness.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "northgate_universe.json"
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports" / "data_quality"


def load_config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def download_prices(cfg):
    tickers = list(cfg["equities"]) + [cfg["benchmark"]]
    end = cfg.get("end_date")
    if not end:
        end = (pd.Timestamp.now(tz="Asia/Kolkata").date() + pd.Timedelta(days=1)).isoformat()
    data = yf.download(
        tickers=tickers,
        start=cfg["start_date"],
        end=end,
        auto_adjust=False,
        actions=True,
        group_by="ticker",
        progress=False,
        threads=True,
    )
    if data.empty:
        raise RuntimeError("Yahoo Finance returned no rows. Check network/ticker availability.")
    frames = []
    for ticker in tickers:
        if isinstance(data.columns, pd.MultiIndex):
            if ticker in data.columns.get_level_values(0):
                part = data[ticker].copy()
            elif ticker in data.columns.get_level_values(1):
                part = data.xs(ticker, axis=1, level=1).copy()
            else:
                print(f"WARNING: no columns returned for {ticker}; skipped")
                continue
        else:
            if len(tickers) != 1:
                raise ValueError("Unexpected flat columns for multi-ticker download.")
            part = data.copy()
        part.columns = [str(c) for c in part.columns]
        part = part.reset_index()
        if "Date" not in part:
            part = part.rename(columns={part.columns[0]: "Date"})
        part["Ticker"] = ticker
        part["Name"] = cfg["equities"].get(ticker, "NIFTY 50")
        frames.append(part)

    panel = pd.concat(frames, ignore_index=True)
    panel["Date"] = pd.to_datetime(panel["Date"]).dt.tz_localize(None)
    required = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    for col in required:
        if col not in panel:
            raise ValueError(f"Downloaded data missing required column: {col}")
        panel[col] = pd.to_numeric(panel[col], errors="coerce")
    panel = panel.dropna(subset=["Date", "Ticker", "Open", "High", "Low", "Close", "Adj Close"])
    panel = panel.sort_values(["Ticker", "Date"]).drop_duplicates(["Ticker", "Date"], keep="last")
    if panel.empty:
        raise RuntimeError("No valid market rows after basic cleaning.")
    return panel


def engineer_one(group):
    g = group.sort_values("Date").copy()
    px = g["Adj Close"].astype(float)
    close = g["Close"].astype(float)
    high, low = g["High"].astype(float), g["Low"].astype(float)
    logret = np.log(px).diff()

    # 24 backward-looking features; every rolling window ends at the current row.
    for n in (1, 2, 5, 10, 20):
        g[f"return_{n}d"] = px.pct_change(n)
    for n in (5, 10, 20, 50, 100, 200):
        g[f"price_sma_ratio_{n}"] = px / px.rolling(n, min_periods=n).mean() - 1
    for n in (12, 26):
        g[f"price_ema_ratio_{n}"] = px / px.ewm(span=n, adjust=False, min_periods=n).mean() - 1
    for n in (5, 10, 20, 60):
        g[f"volatility_{n}d"] = logret.rolling(n, min_periods=n).std()

    delta = px.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    rs = gain / loss.replace(0, np.nan)
    g["rsi_14"] = 100 - (100 / (1 + rs))

    ema12 = px.ewm(span=12, adjust=False, min_periods=12).mean()
    ema26 = px.ewm(span=26, adjust=False, min_periods=26).mean()
    macd = ema12 - ema26
    g["macd_pct"] = macd / px
    g["macd_signal_pct"] = (macd - macd.ewm(span=9, adjust=False, min_periods=9).mean()) / px

    prev_close = close.shift(1)
    tr = pd.concat([(high-low), (high-prev_close).abs(), (low-prev_close).abs()], axis=1).max(axis=1)
    g["atr_14_pct"] = tr.rolling(14, min_periods=14).mean() / px

    if g["Ticker"].iloc[0] == "^NSEI":
        g["volume_sma_ratio_20"] = np.nan
        g["volume_change_1d"] = np.nan
        g["obv_change_20"] = np.nan
    else:
        vol = g["Volume"].replace(0, np.nan).astype(float)
        g["volume_sma_ratio_20"] = vol / vol.rolling(20, min_periods=20).mean() - 1
        g["volume_change_1d"] = vol.pct_change()
        obv = (np.sign(px.pct_change()).fillna(0) * vol.fillna(0)).cumsum()
        g["obv_change_20"] = obv.diff(20) / vol.rolling(20, min_periods=20).sum().replace(0, np.nan)

    return g


def main():
    cfg = load_config()
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    panel = download_prices(cfg)
    panel.to_csv(PROCESSED / "market_panel.csv", index=False)
    try:
        panel.to_parquet(RAW / "market_panel.parquet", index=False)
    except ImportError:
        print("NOTE: pyarrow is not installed; skipped Parquet raw copy.")

    features = pd.concat(
        [engineer_one(g) for _, g in panel.groupby("Ticker", sort=False)],
        ignore_index=True,
    ).sort_values(["Ticker", "Date"])
    feature_cols = [c for c in features.columns if c not in panel.columns]
    features.to_csv(PROCESSED / "feature_panel.csv", index=False)

    labelled = []
    for _, g in features.groupby("Ticker", sort=False):
        g = g.sort_values("Date").copy()
        g["target_date_t1"] = g["Date"].shift(-1)
        g["target_adj_close_t1"] = g["Adj Close"].shift(-1)
        g["target_log_return_t1"] = np.log(g["target_adj_close_t1"] / g["Adj Close"])
        g["target_direction_t1"] = np.sign(g["target_log_return_t1"])
        labelled.append(g)
    model_df = pd.concat(labelled, ignore_index=True)
    model_df = model_df.dropna(subset=[
        "target_date_t1", "target_adj_close_t1", "target_log_return_t1"
    ]).copy()
    model_df["target_direction_t1"] = model_df["target_direction_t1"].astype("int8")
    model_df.to_csv(PROCESSED / "modeling_dataset_next_day.csv", index=False)

    train_end = pd.Timestamp(cfg["train_target_end"])
    latest_target = pd.to_datetime(model_df["target_date_t1"]).max()
    test_cutoff = latest_target - pd.DateOffset(months=int(cfg["test_months"]))
    target_dates = pd.to_datetime(model_df["target_date_t1"])
    splits = {
        "train": model_df[target_dates <= train_end].copy(),
        "validation": model_df[(target_dates > train_end) & (target_dates < test_cutoff)].copy(),
        "test": model_df[target_dates >= test_cutoff].copy(),
    }
    if any(x.empty for x in splits.values()):
        raise RuntimeError("At least one chronological split is empty; inspect date boundaries.")
    if not (pd.to_datetime(splits["train"]["target_date_t1"]).max()
            < pd.to_datetime(splits["validation"]["target_date_t1"]).min()
            < pd.to_datetime(splits["test"]["target_date_t1"]).min()):
        raise AssertionError("Chronological split order check failed.")

    split_dir = PROCESSED / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in splits.items():
        frame.sort_values(["Ticker", "Date"]).to_csv(split_dir / f"{name}.csv", index=False)

    target_cols = [c for c in model_df if c.startswith("target_")]
    report = {
        "source": "Yahoo Finance via yfinance; verify vendor terms and coverage before redistribution.",
        "equities": list(cfg["equities"].keys()),
        "benchmark": cfg["benchmark"],
        "market_rows": int(len(panel)),
        "feature_rows": int(len(features)),
        "labelled_rows": int(len(model_df)),
        "feature_count": len(feature_cols),
        "features": feature_cols,
        "feature_date_start": str(pd.to_datetime(model_df["Date"]).min().date()),
        "target_date_end": str(latest_target.date()),
        "test_cutoff": str(test_cutoff.date()),
        "split_rows": {k: int(len(v)) for k, v in splits.items()},
        "rows_by_ticker": {str(k): int(v) for k, v in model_df.groupby("Ticker").size().items()},
        "checks": {
            "duplicate_ticker_date": int(model_df.duplicated(["Ticker", "Date"]).sum()),
            "all_target_dates_after_feature_dates": bool((pd.to_datetime(model_df["target_date_t1"]) > pd.to_datetime(model_df["Date"])).all()),
            "missing_target_values": int(model_df[target_cols].isna().sum().sum()),
            "all_rows_assigned_once": sum(map(len, splits.values())) == len(model_df),
            "test_is_latest_six_months": True,
        },
        "limitations": [
            "This is a price/volume-only baseline dataset, not the complete PRD dataset.",
            "No CPI, FRED/RBI macro, timestamped news, FinBERT/VADER sentiment, or point-in-time constituent history is included.",
            "Yahoo Finance adjusted history is vendor-provided and may be revised; it is not a point-in-time historical vendor snapshot.",
            "The ten equities are the current provisional project universe; historical index membership/survivorship bias is not resolved.",
            "No model inputs may include any target_* column.",
            "Final test data must remain unused until model selection is frozen.",
        ],
    }
    (REPORTS / "gpu_data_build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["market_rows", "labelled_rows", "feature_count", "split_rows", "checks"]}, indent=2))
    print(f"Created data/processed/market_panel.csv, feature_panel.csv, modeling_dataset_next_day.csv and splits/*.csv")
    print("IMPORTANT: This rebuild excludes macro/news data; it prepares the first baseline experiment only.")


if __name__ == "__main__":
    main()
