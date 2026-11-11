"""Create backward-looking price/volume features per instrument.

This script does not create a prediction target or train a model.
All rolling features use current/past observations only. Warm-up NaNs are
preserved intentionally and reported; they must not be filled from the future.
"""
from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "market_panel.csv"
OUTPUT = ROOT / "data" / "processed" / "feature_panel.csv"
REPORT = ROOT / "reports" / "data_quality" / "feature_report.json"


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    relative_strength = avg_gain / avg_loss.replace(0, np.nan)
    result = 100 - (100 / (1 + relative_strength))
    # If there were gains and no losses, RSI is 100.
    result = result.mask((avg_loss == 0) & (avg_gain > 0), 100)
    return result


def build_features(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values("Date").copy()
    price = pd.to_numeric(group["Adj Close"], errors="coerce")
    close = pd.to_numeric(group["Close"], errors="coerce")
    volume = pd.to_numeric(group["Volume"], errors="coerce")

    group["log_return_1d"] = np.log(price / price.shift(1))
    for lag in (1, 2, 3, 5, 10):
        group[f"log_return_lag_{lag}"] = group["log_return_1d"].shift(lag)

    for window in (5, 10, 20, 50):
        group[f"sma_{window}"] = price.rolling(window, min_periods=window).mean()
        group[f"price_to_sma_{window}"] = price / group[f"sma_{window}"] - 1

    group["ema_12"] = price.ewm(span=12, adjust=False, min_periods=12).mean()
    group["ema_26"] = price.ewm(span=26, adjust=False, min_periods=26).mean()
    group["macd"] = group["ema_12"] - group["ema_26"]
    group["rsi_14"] = rsi(price, 14)

    group["volatility_20d"] = group["log_return_1d"].rolling(
        20, min_periods=20
    ).std()
    rolling_mean = price.rolling(20, min_periods=20).mean()
    rolling_std = price.rolling(20, min_periods=20).std()
    upper = rolling_mean + 2 * rolling_std
    lower = rolling_mean - 2 * rolling_std
    group["bollinger_width_20"] = (upper - lower) / rolling_mean

    # Yahoo Finance returned zero volume on dates where equity prices are
    # present across many unrelated stocks. Treat zero as unavailable volume,
    # not as a genuine zero-trading observation. Preserve the raw Volume column.
    # The NIFTY 50 price index is not an individual traded security; do not
    # derive volume indicators from its Yahoo Volume field.
    if group["Ticker"].iloc[0] == "^NSEI":
        volume_for_features = pd.Series(np.nan, index=group.index, dtype="float64")
    else:
        volume_for_features = volume.where(volume > 0)

    group["volume_change_1d"] = volume_for_features.pct_change(fill_method=None)
    group["volume_sma_20"] = volume_for_features.rolling(
        20, min_periods=20
    ).mean()
    group["volume_to_sma_20"] = (
        volume_for_features / group["volume_sma_20"]
    )

    # Retain raw columns; close is used only as a cross-check, not as the
    # adjusted-price basis for return/indicator features.
    group["adj_close_vs_close"] = price / close - 1
    return group


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing input dataset: {INPUT}")

    df = pd.read_csv(INPUT, parse_dates=["Date"])
    required = {"Date", "Ticker", "Adj Close", "Close", "Volume"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Input is missing columns: {sorted(missing)}")

    df = df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
    parts = [
        build_features(group)
        for _, group in df.groupby("Ticker", sort=False, group_keys=False)
    ]
    result = pd.concat(parts, ignore_index=True)
    result = result.sort_values(["Ticker", "Date"]).reset_index(drop=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)

    feature_columns = [
        c for c in result.columns
        if c not in df.columns
    ]
    report = {
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "rows": int(len(result)),
        "tickers": sorted(result["Ticker"].unique().tolist()),
        "feature_columns": feature_columns,
        "missing_values_by_feature": {
            c: int(result[c].isna().sum()) for c in feature_columns
        },
        "notes": [
            "Features are calculated independently per ticker.",
            "Zero equity-volume observations are treated as unavailable for volume features; raw Volume is preserved.",
            "Volume-derived features are not calculated for the NIFTY 50 price index.",
            "All indicators use current/past observations only.",
            "Warm-up NaNs are expected and intentionally preserved.",
            "No prediction target is created in this step.",
            "No learned scaler or imputer is fitted here.",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Input rows: {len(df):,}")
    print(f"Output rows: {len(result):,}")
    print(f"Tickers: {result['Ticker'].nunique()}")
    print(f"Features created: {len(feature_columns)}")
    print(f"Feature dataset: {OUTPUT}")
    print(f"Feature report: {REPORT}")
    print("\nWarm-up/missing values:")
    for col, count in report["missing_values_by_feature"].items():
        print(f"  {col}: {count}")


if __name__ == "__main__":
    main()
