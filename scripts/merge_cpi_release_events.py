"""Merge monthly CPI release events onto an actual market-session panel without look-ahead.

Usage:
  python scripts/merge_cpi_release_events.py \
    --market-panel data/processed/market_panel.csv \
    --cpi-events data/external/cpi_mospi_2012base_release_events_2024-07_to_2025-12.csv \
    --output data/processed/market_panel_with_cpi.csv

The market panel must contain one row per instrument/session and a date column.
CPI becomes usable from next_nse_session, never on the publication date.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

EVENT_COLUMNS = [
    "reference_month",
    "release_workbook_month",
    "base_year",
    "combined_cpi_index_2012",
    "combined_cpi_yoy_inflation_pct",
    "actual_release_date",
    "available_at_ist",
    "next_nse_session",
    "timestamp_status",
    "provisional",
]


def merge_cpi_events(
    market: pd.DataFrame,
    events: pd.DataFrame,
    date_column: str = "date",
) -> pd.DataFrame:
    """Backward as-of join; every matched event must be available by market date."""
    if date_column not in market.columns:
        raise ValueError(f"Market panel is missing date column: {date_column}")
    missing = set(EVENT_COLUMNS) - set(events.columns)
    if missing:
        raise ValueError(f"CPI event file is missing columns: {sorted(missing)}")

    left = market.copy()
    left["_original_order"] = range(len(left))
    left["_market_date"] = pd.to_datetime(left[date_column], errors="raise").dt.normalize()
    right = events[EVENT_COLUMNS].copy()
    right["_available_session"] = pd.to_datetime(right["next_nse_session"], errors="raise").dt.normalize()

    if right["_available_session"].duplicated().any():
        raise ValueError("CPI events contain duplicate availability sessions")
    if right["_available_session"].isna().any():
        raise ValueError("CPI event availability session contains null values")
    if right["base_year"].astype(int).ne(2012).any():
        raise ValueError("This event file must contain only the CPI 2012=100 series")

    left = left.sort_values("_market_date")
    right = right.sort_values("_available_session")
    merged = pd.merge_asof(
        left,
        right,
        left_on="_market_date",
        right_on="_available_session",
        direction="backward",
        allow_exact_matches=True,
    )

    matched = merged["_available_session"].notna()
    if (merged.loc[matched, "_available_session"] > merged.loc[matched, "_market_date"]).any():
        raise AssertionError("Look-ahead detected: CPI event after market date")
    if (merged.loc[matched, "actual_release_date"] > merged.loc[matched, date_column].astype(str).str[:10]).any():
        raise AssertionError("Look-ahead detected: CPI release date after market date")

    merged["cpi_age_calendar_days"] = (
        merged["_market_date"] - merged["_available_session"]
    ).dt.days
    merged = merged.sort_values("_original_order").drop(
        columns=["_original_order", "_market_date", "_available_session"]
    )
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--market-panel", type=Path, required=True)
    parser.add_argument("--cpi-events", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--date-column", default="date")
    args = parser.parse_args()

    market = pd.read_csv(args.market_panel)
    events = pd.read_csv(args.cpi_events)
    merged = merge_cpi_events(market, events, args.date_column)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.output, index=False)

    matched = merged["next_nse_session"].notna().sum()
    print(f"Market rows: {len(market)}")
    print(f"Rows with an available CPI event: {matched}")
    print(f"Rows before first CPI event (left unmatched): {len(market) - matched}")
    print(f"Unique CPI release months used: {merged['release_workbook_month'].nunique()}")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
