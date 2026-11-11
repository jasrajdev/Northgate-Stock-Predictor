"""Create a first supervised dataset for next-session adjusted-close forecasting.

Each row contains information available at session t and labels from the next
observed session for the same ticker. No future values are used as features.
Multi-day labels are intentionally deferred until their horizon is agreed.
"""
from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "feature_panel.csv"
OUTPUT = ROOT / "data" / "processed" / "modeling_dataset_next_day.csv"
REPORT = ROOT / "reports" / "data_quality" / "next_day_dataset_report.json"


def add_next_day_targets(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values("Date").copy()
    next_date = group["Date"].shift(-1)
    next_adj_close = pd.to_numeric(group["Adj Close"], errors="coerce").shift(-1)
    current_adj_close = pd.to_numeric(group["Adj Close"], errors="coerce")

    group["target_date_t1"] = next_date
    group["target_adj_close_t1"] = next_adj_close
    group["target_log_return_t1"] = np.log(
        next_adj_close / current_adj_close
    )
    group["target_direction_t1"] = np.sign(group["target_log_return_t1"])
    return group


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing feature dataset: {INPUT}")

    df = pd.read_csv(INPUT, parse_dates=["Date"])
    required = {"Date", "Ticker", "Adj Close"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Input is missing columns: {sorted(missing)}")

    df = df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
    result = pd.concat(
        [
            add_next_day_targets(group)
            for _, group in df.groupby("Ticker", sort=False)
        ],
        ignore_index=True,
    )
    # The last observation for each ticker has no observed next-session label.
    before = len(result)
    result = result.dropna(
        subset=["target_date_t1", "target_adj_close_t1", "target_log_return_t1"]
    ).copy()
    result["target_direction_t1"] = result["target_direction_t1"].astype("int8")
    result = result.sort_values(["Ticker", "Date"]).reset_index(drop=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)

    report = {
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "rows_before_label_filter": int(before),
        "rows_after_label_filter": int(len(result)),
        "rows_without_next_session_label_removed": int(before - len(result)),
        "ticker_counts": {
            str(ticker): int(count)
            for ticker, count in result.groupby("Ticker").size().items()
        },
        "date_range": {
            "feature_date_start": result["Date"].min().date().isoformat(),
            "feature_date_end": result["Date"].max().date().isoformat(),
            "target_date_end": result["target_date_t1"].max().date().isoformat(),
        },
        "target_columns": [
            "target_date_t1",
            "target_adj_close_t1",
            "target_log_return_t1",
            "target_direction_t1",
        ],
        "checks": {
            "duplicate_ticker_feature_dates": int(
                result.duplicated(["Ticker", "Date"]).sum()
            ),
            "target_date_after_feature_date_all_rows": bool(
                (result["target_date_t1"] > result["Date"]).all()
            ),
            "missing_target_values": int(
                result[
                    [
                        "target_date_t1",
                        "target_adj_close_t1",
                        "target_log_return_t1",
                        "target_direction_t1",
                    ]
                ].isna().sum().sum()
            ),
            "non_positive_target_adjusted_close": int(
                (result["target_adj_close_t1"] <= 0).sum()
            ),
        },
        "important_notes": [
            "Targets are created independently within each ticker using the next observed row.",
            "The target is the next observed trading session in the source data, not the next calendar day.",
            "Feature columns remain unchanged and use information available at the feature date.",
            "target_* columns are labels and must never be included in model input features.",
            "The final row per ticker is removed because its next-session target is not yet observed.",
            "This first dataset supports one-session-ahead forecasting only; multi-day horizons are not defined in the PRD and remain open.",
            "No train/validation/test split or scaler is created here.",
            "This does not yet add macroeconomic or news-sentiment data required elsewhere in the PRD.",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Input rows: {before:,}")
    print(f"Rows with next-session targets: {len(result):,}")
    print(f"Rows removed (last row per ticker): {before - len(result):,}")
    print(f"Tickers: {result['Ticker'].nunique()}")
    print(f"Dataset: {OUTPUT}")
    print(f"Report: {REPORT}")
    print("\nChecks:")
    for name, value in report["checks"].items():
        print(f"  {name}: {value}")


if __name__ == "__main__":
    main()
