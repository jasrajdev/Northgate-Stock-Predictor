"""Feature set v1: the 25 model inputs used by Experiment 01 (Kaggle).

Reproduces `engineer_one` in scripts/prepare_gpu_training_data.py with the two changes the
Kaggle run applied in-session (see reports/claude_dataset_audit_2026-11-14/NORTHGATE_EXPERIMENT_RECOVERY.md):
  * ATR built from High/Low rescaled to the adjusted-close basis (notebook cell 26);
  * raw OHLCV / Dividends / Stock Splits are not model inputs; `Adj Close` is.
`volume_change_1d` follows pandas-2 `pct_change()` semantics (forward-fill before the ratio),
which is what ran on Kaggle, made explicit so it does not depend on the pandas version.
Every column uses only the current and earlier sessions of the same ticker.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .config import BENCHMARK, TRAIN_TARGET_END, VALIDATION_TARGET_END

FEATURES = ["Adj Close", "return_1d", "return_2d", "return_5d", "return_10d", "return_20d",
            "price_sma_ratio_5", "price_sma_ratio_10", "price_sma_ratio_20", "price_sma_ratio_50",
            "price_sma_ratio_100", "price_sma_ratio_200", "price_ema_ratio_12", "price_ema_ratio_26",
            "volatility_5d", "volatility_10d", "volatility_20d", "volatility_60d", "rsi_14", "macd_pct",
            "macd_signal_pct", "atr_14_pct", "volume_sma_ratio_20", "volume_change_1d", "obv_change_20"]
TARGET = "target_log_return_t1"


def _one(g: pd.DataFrame) -> pd.DataFrame:
    g = g.sort_values("Date").copy()
    px, close = g["Adj Close"].astype(float), g["Close"].astype(float)
    high, low = g["High"].astype(float), g["Low"].astype(float)
    logret = np.log(px).diff()
    for n in (1, 2, 5, 10, 20):
        g[f"return_{n}d"] = px / px.shift(n) - 1
    for n in (5, 10, 20, 50, 100, 200):
        g[f"price_sma_ratio_{n}"] = px / px.rolling(n, min_periods=n).mean() - 1
    for n in (12, 26):
        g[f"price_ema_ratio_{n}"] = px / px.ewm(span=n, adjust=False, min_periods=n).mean() - 1
    for n in (5, 10, 20, 60):
        g[f"volatility_{n}d"] = logret.rolling(n, min_periods=n).std()
    delta = px.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    g["rsi_14"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    ema12 = px.ewm(span=12, adjust=False, min_periods=12).mean()
    ema26 = px.ewm(span=26, adjust=False, min_periods=26).mean()
    macd = ema12 - ema26
    g["macd_pct"] = macd / px
    g["macd_signal_pct"] = (macd - macd.ewm(span=9, adjust=False, min_periods=9).mean()) / px
    factor = px / close
    adj_high, adj_low, prev = high * factor, low * factor, px.shift(1)
    tr = pd.concat([adj_high - adj_low, (adj_high - prev).abs(), (adj_low - prev).abs()], axis=1).max(axis=1)
    g["atr_14_pct"] = tr.rolling(14, min_periods=14).mean() / px
    if g["Ticker"].iloc[0] == BENCHMARK:
        g["volume_sma_ratio_20"] = g["volume_change_1d"] = g["obv_change_20"] = np.nan
    else:
        vol = g["Volume"].replace(0, np.nan).astype(float)
        g["volume_sma_ratio_20"] = vol / vol.rolling(20, min_periods=20).mean() - 1
        vf = vol.ffill()
        g["volume_change_1d"] = vf / vf.shift(1) - 1
        obv = (np.sign(px.pct_change(fill_method=None)).fillna(0) * vol.fillna(0)).cumsum()
        g["obv_change_20"] = obv.diff(20) / vol.rolling(20, min_periods=20).sum().replace(0, np.nan)
    return g


def build(panel: pd.DataFrame) -> pd.DataFrame:
    """Feature panel (all sessions). Labels are added separately and masked after validation."""
    return pd.concat([_one(g) for _, g in panel.groupby("Ticker", sort=False)], ignore_index=True).sort_values(["Ticker", "Date"]).reset_index(drop=True)


def add_labels(feat: pd.DataFrame, last_target_date: pd.Timestamp = VALIDATION_TARGET_END) -> pd.DataFrame:
    """Next-session log-return label. Labels whose outcome falls after `last_target_date`
    (the held-out test window) are left missing and never computed into any statistic."""
    out = []
    for _, g in feat.groupby("Ticker", sort=False):
        g = g.sort_values("Date").copy()
        nd, npx = g["Date"].shift(-1), g["Adj Close"].shift(-1)
        keep = nd <= last_target_date
        g["target_date_t1"] = nd.where(keep)
        g[TARGET] = np.log(npx / g["Adj Close"]).where(keep)
        out.append(g)
    return pd.concat(out, ignore_index=True)


def partition(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Rows of the train or validation partition (by target date). The test window is not offered."""
    t = df["target_date_t1"]
    if name == "train":
        return df[t <= TRAIN_TARGET_END]
    if name == "validation":
        return df[(t > TRAIN_TARGET_END) & (t <= VALIDATION_TARGET_END)]
    raise ValueError("Only 'train' and 'validation' partitions are available here.")
