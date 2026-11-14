"""Read-only access to the locally built market and feature panels."""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PROCESSED = ROOT / "data" / "processed"
BENCHMARK = "^NSEI"
# Agreed chronological boundaries (DECISIONS.md, 2026-11-13; local Mac build).
TRAIN_END = pd.Timestamp("2023-12-31")
VALIDATION_END = pd.Timestamp("2026-05-08")


class DataUnavailable(RuntimeError):
    """Raised when a required local dataset is missing."""


def _read(name: str) -> pd.DataFrame:
    path = PROCESSED / name
    if not path.exists():
        raise DataUnavailable(f"{path.relative_to(ROOT)} not found. Build it with the scripts in scripts/ (see README).")
    return pd.read_csv(path, parse_dates=["Date"])


@lru_cache(maxsize=1)
def load_panel() -> pd.DataFrame:
    """Daily OHLCV panel (Yahoo Finance) with a `suspect_bar` flag. Data values are not altered."""
    df = _read("market_panel.csv").sort_values(["Ticker", "Date"]).reset_index(drop=True)
    flat = (df.Open == df.High) & (df.High == df.Low) & (df.Low == df.Close)
    df["suspect_bar"] = (df.Ticker != BENCHMARK) & (df.Volume == 0) & flat
    return df


@lru_cache(maxsize=1)
def load_features() -> pd.DataFrame:
    """Feature panel written by scripts/build_features.py (24 backward-looking features)."""
    return _read("feature_panel.csv").sort_values(["Ticker", "Date"]).reset_index(drop=True)


def tickers(include_benchmark: bool = False) -> list[str]:
    names = sorted(load_panel().Ticker.unique())
    return names if include_benchmark else [t for t in names if t != BENCHMARK]


def names() -> dict[str, str]:
    return load_panel().drop_duplicates("Ticker").set_index("Ticker").Name.to_dict()


def period_label(date: pd.Timestamp) -> str:
    if date <= TRAIN_END:
        return "train"
    return "validation" if date <= VALIDATION_END else "held-out test window"
