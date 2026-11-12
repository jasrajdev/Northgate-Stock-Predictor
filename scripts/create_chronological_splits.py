"""Create leakage-aware chronological train/validation/test partitions.

Rows are assigned by target_date_t1 (the date the forecast outcome becomes
known), not merely by feature Date. The final six calendar months are held
out as the untouched test period. No scaler or imputer is fitted here.
"""
from __future__ import annotations

from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "modeling_dataset_next_day.csv"
OUTPUT_DIR = ROOT / "data" / "processed" / "splits"
REPORT = ROOT / "reports" / "data_quality" / "chronological_split_report.json"

# Agreed working boundary: use 2016–2023 outcomes for model fitting.
TRAIN_TARGET_END = pd.Timestamp("2023-12-31")
TEST_MONTHS = 6


def date_summary(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {"rows": 0, "feature_date_start": None, "feature_date_end": None,
                "target_date_start": None, "target_date_end": None}
    return {
        "rows": int(len(frame)),
        "feature_date_start": frame["Date"].min().date().isoformat(),
        "feature_date_end": frame["Date"].max().date().isoformat(),
        "target_date_start": frame["target_date_t1"].min().date().isoformat(),
        "target_date_end": frame["target_date_t1"].max().date().isoformat(),
        "rows_by_ticker": {
            str(ticker): int(count)
            for ticker, count in frame.groupby("Ticker").size().items()
        },
    }


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing modelling dataset: {INPUT}")

    df = pd.read_csv(INPUT, parse_dates=["Date", "target_date_t1"])
    required = {"Date", "Ticker", "target_date_t1", "target_adj_close_t1",
                "target_log_return_t1", "target_direction_t1"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {sorted(missing)}")
    if df[["Date", "Ticker", "target_date_t1"]].isna().any().any():
        raise ValueError("Date, Ticker, and target_date_t1 must not contain missing values.")
    if df.duplicated(["Ticker", "Date"]).any():
        raise ValueError("Duplicate (Ticker, Date) rows found.")
    if not (df["target_date_t1"] > df["Date"]).all():
        raise ValueError("Every target date must be later than its feature date.")

    latest_target_date = df["target_date_t1"].max()
    test_cutoff = latest_target_date - pd.DateOffset(months=TEST_MONTHS)

    train = df[df["target_date_t1"] <= TRAIN_TARGET_END].copy()
    validation = df[
        (df["target_date_t1"] > TRAIN_TARGET_END)
        & (df["target_date_t1"] < test_cutoff)
    ].copy()
    test = df[df["target_date_t1"] >= test_cutoff].copy()

    partitions = {"train": train, "validation": validation, "test": test}
    empty = [name for name, part in partitions.items() if part.empty]
    if empty:
        raise ValueError(f"Empty partition(s): {empty}. Review split boundaries.")

    # The target-date intervals must be strictly ordered and non-overlapping.
    if not (
        train["target_date_t1"].max() < validation["target_date_t1"].min()
        and validation["target_date_t1"].max() < test["target_date_t1"].min()
    ):
        raise AssertionError("Target-date ranges overlap or are not chronological.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, part in partitions.items():
        part.sort_values(["Ticker", "Date"]).to_csv(
            OUTPUT_DIR / f"{name}.csv", index=False
        )

    target_columns = [c for c in df.columns if c.startswith("target_")]
    metadata_columns = ["Date", "Ticker", "Name", "target_date_t1"]
    candidate_feature_columns = [
        c for c in df.columns
        if c not in metadata_columns and c not in target_columns
    ]

    report = {
        "input": str(INPUT.relative_to(ROOT)),
        "output_directory": str(OUTPUT_DIR.relative_to(ROOT)),
        "method": "Chronological partitions assigned by target_date_t1.",
        "training_target_end_inclusive": TRAIN_TARGET_END.date().isoformat(),
        "final_test_window_calendar_months": TEST_MONTHS,
        "latest_target_date": latest_target_date.date().isoformat(),
        "test_cutoff_calendar_date": test_cutoff.date().isoformat(),
        "actual_first_test_target_date": test["target_date_t1"].min().date().isoformat(),
        "partitions": {
            name: date_summary(part) for name, part in partitions.items()
        },
        "target_columns_excluded_from_model_inputs": target_columns,
        "candidate_feature_columns_excluding_metadata_and_targets": candidate_feature_columns,
        "checks": {
            "duplicate_ticker_feature_dates": int(
                df.duplicated(["Ticker", "Date"]).sum()
            ),
            "all_target_dates_after_feature_dates": bool(
                (df["target_date_t1"] > df["Date"]).all()
            ),
            "train_before_validation": bool(
                train["target_date_t1"].max() < validation["target_date_t1"].min()
            ),
            "validation_before_test": bool(
                validation["target_date_t1"].max() < test["target_date_t1"].min()
            ),
            "all_rows_assigned_once": int(sum(map(len, partitions.values()))) == len(df),
            "target_columns_excluded_from_candidate_features": not (
                set(target_columns) & set(candidate_feature_columns)
            ),
        },
        "important_notes": [
            "The final six calendar months are reserved as the untouched test period.",
            "Rows are assigned by target date so outcomes in the test window cannot enter training or validation.",
            "The feature row immediately before the test window may belong to test if its next-session target falls inside the test window.",
            "The NIFTY 50 benchmark remains in the partitions for market-context/baseline work; it is not an investable equity.",
            "All target_* columns are labels and must never be passed as model inputs.",
            "Fit scalers, imputers, feature selectors, and other learned preprocessing on training data only, then apply unchanged to validation/test.",
            "Use validation only for model selection. Do not tune against the final test period.",
            "For multi-session targets, purge any training rows whose forward-label intervals overlap a later partition; this script currently handles the agreed one-session target only.",
            "This script creates partitions only; it does not train models or establish model performance.",
        ],
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Input rows: {len(df):,}")
    print(f"Latest target date: {latest_target_date.date()}")
    print(f"Six-month test cutoff: {test_cutoff.date()}")
    print(f"First observed test target date: {test['target_date_t1'].min().date()}")
    for name, part in partitions.items():
        print(f"{name.title():<12} rows: {len(part):,} | "
              f"target dates: {part['target_date_t1'].min().date()} to "
              f"{part['target_date_t1'].max().date()}")
    print(f"Split files: {OUTPUT_DIR}")
    print(f"Report: {REPORT}")
    print("\nChecks:")
    for key, value in report["checks"].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
