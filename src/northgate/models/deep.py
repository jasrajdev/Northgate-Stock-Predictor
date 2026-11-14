"""PyTorch sequence models: definitions identical to scripts/train_deep_models.py (and the
Kaggle walk-forward runner), plus a strict checkpoint loader.

The loader rebuilds the architecture from the hyper-parameters stored in the checkpoint,
loads weights with strict=True, and applies the checkpoint's own train-fitted medians,
means and standard deviations in the checkpoint's own feature order and ticker map. Any
mismatch raises; nothing is reshaped or guessed.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED = {"state_dict", "model", "sequence_length", "hidden_size", "medians", "means", "stds"}


def _torch():
    import torch
    from torch import nn
    return torch, nn


def build(kind: str, n_features: int, hidden: int, seq: int):
    torch, nn = _torch()

    class Recurrent(nn.Module):
        def __init__(self):
            super().__init__()
            bidir = kind == "BiLSTM"
            rnn_cls = nn.GRU if kind == "GRU" else nn.LSTM
            self.rnn = rnn_cls(n_features, hidden, num_layers=1, batch_first=True, dropout=0.0, bidirectional=bidir)
            width = hidden * (2 if bidir else 1)
            self.head = nn.Sequential(nn.Dropout(0.15), nn.Linear(width, 16), nn.ReLU(), nn.Linear(16, 1))

        def forward(self, x):
            z, _ = self.rnn(x)
            return self.head(z[:, -1]).squeeze(-1)

    class TransformerRegressor(nn.Module):
        def __init__(self):
            super().__init__()
            self.proj = nn.Linear(n_features, hidden)
            self.pos = nn.Parameter(torch.zeros(1, seq, hidden))
            layer = nn.TransformerEncoderLayer(d_model=hidden, nhead=4, dim_feedforward=hidden * 2, dropout=0.1,
                                               batch_first=True, activation="gelu")
            self.encoder = nn.TransformerEncoder(layer, num_layers=1)
            self.head = nn.Sequential(nn.LayerNorm(hidden), nn.Linear(hidden, 16), nn.GELU(), nn.Linear(16, 1))

        def forward(self, x):
            return self.head(self.encoder(self.proj(x) + self.pos)[:, -1]).squeeze(-1)

    if kind in ("LSTM", "GRU", "BiLSTM"):
        return Recurrent()
    if kind == "Transformer":
        return TransformerRegressor()
    raise KeyError(kind)


@dataclass
class LoadedModel:
    name: str
    path: Path
    module: object
    seq: int
    hidden: int
    features: list
    tickers: list
    medians: pd.Series
    means: pd.Series
    stds: pd.Series

    def window(self, frame: pd.DataFrame, ticker: str) -> np.ndarray:
        """Standardised (seq, n_features + n_tickers) window ending at the last row of `frame`."""
        if ticker not in self.tickers:
            raise KeyError(f"{ticker} not in checkpoint ticker map")
        g = frame[frame.Ticker == ticker].sort_values("Date")
        if len(g) < self.seq:
            raise ValueError(f"need {self.seq} sessions, have {len(g)}")
        v = g[self.features].tail(self.seq).replace([np.inf, -np.inf], np.nan).fillna(self.medians)
        v = ((v - self.means) / self.stds).clip(-10, 10).to_numpy(dtype=np.float32)
        onehot = np.zeros((self.seq, len(self.tickers)), dtype=np.float32)
        onehot[:, self.tickers.index(ticker)] = 1.0
        return np.concatenate([v, onehot], axis=1)

    def predict(self, frame: pd.DataFrame, ticker: str) -> float:
        torch, _ = _torch()
        x = torch.from_numpy(self.window(frame, ticker)[None])
        self.module.eval()
        with torch.no_grad():
            return float(self.module(x).item())


def load(path: Path, expected_features: list | None = None) -> LoadedModel:
    torch, _ = _torch()
    try:
        ck = torch.load(path, map_location="cpu", weights_only=True)
    except Exception:
        # Own training artefact containing plain dicts; fall back to full unpickling.
        ck = torch.load(path, map_location="cpu", weights_only=False)
    missing = REQUIRED - set(ck)
    if missing:
        raise ValueError(f"{path.name}: checkpoint is missing keys {sorted(missing)}")
    features = ck.get("feature_columns") or ck.get("features")
    if "ticker_map" in ck:
        tm = ck["ticker_map"]; tickers = [t for t, _ in sorted(tm.items(), key=lambda kv: kv[1])]
    else:
        tickers = list(ck.get("tickers") or [])
    if not features or not tickers:
        raise ValueError(f"{path.name}: checkpoint has no feature list or ticker map")
    if expected_features is not None and list(features) != list(expected_features):
        raise ValueError(f"{path.name}: feature order differs from the pipeline ({len(features)} vs {len(expected_features)})")
    seq, hidden, name = int(ck["sequence_length"]), int(ck["hidden_size"]), str(ck["model"])
    module = build(name, len(features) + len(tickers), hidden, seq)
    module.load_state_dict(ck["state_dict"], strict=True)
    s = lambda k: pd.Series(ck[k], dtype=float).reindex(features)
    med, mu, sd = s("medians"), s("means"), s("stds")
    if med.isna().any() or mu.isna().any() or sd.isna().any():
        raise ValueError(f"{path.name}: preprocessing statistics do not cover every feature")
    return LoadedModel(name, path, module, seq, hidden, list(features), tickers, med, mu, sd)
