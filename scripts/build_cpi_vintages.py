"""Extract reproducible point-in-time CPI vintages from MoSPI Excel annexures.

The MoSPI annexure number changed during the supplied period. This script
classifies historical time-series sheets by their title, not by a fixed
Annex-V/VI/VII number.

Usage:
  python scripts/build_cpi_vintages.py \
    --input-dir data/raw/cpi_annexures \
    --output-dir data/processed/cpi \
    --availability-map data/external/cpi_mospi_2012_release_availability_map_2024-07_to_2025-12.csv
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def parse_value(value):
    if pd.isna(value) or str(value).strip() in {"", "-", "nan"}:
        return None, False, None
    raw = str(value).strip()
    provisional = "*" in raw
    cleaned = raw.replace("*", "").replace(",", "")
    try:
        return float(cleaned), provisional, raw
    except ValueError:
        return None, provisional, raw


def release_month_from_name(path: Path) -> str:
    match = re.search(r"Excel ([A-Za-z]+) (20[0-9]{2})", path.name)
    if not match:
        raise ValueError(f"Cannot infer release month/year from {path.name}")
    return pd.to_datetime(f"{match.group(1)} 1 {match.group(2)}").strftime("%Y-%m")


def classify_time_series_sheet(path: Path, sheet: str) -> str | None:
    """Return index/inflation only for the cumulative All-India general CPI tables."""
    frame = pd.read_excel(path, sheet_name=sheet, header=None, nrows=4)
    title = " ".join(str(v) for v in frame.fillna("").to_numpy().ravel()).lower()
    if "base 2012" not in title or "since january" not in title:
        return None
    if "inflation rate" in title and ("general cpi" in title or "based on cpi" in title):
        return "inflation"
    if "general cpi" in title and "inflation rate" not in title:
        return "index"
    return None


def extract_sheet(path: Path, sheet: str, series: str) -> list[dict]:
    frame = pd.read_excel(path, sheet_name=sheet, header=None)
    release_month = release_month_from_name(path)
    rows = []
    for _, row in frame.iterrows():
        year = row.iloc[0]
        if pd.isna(year):
            continue
        try:
            year = int(float(year))
        except (TypeError, ValueError):
            continue
        for col, month in enumerate(MONTHS, start=1):
            if col >= len(row):
                continue
            value, provisional, raw = parse_value(row.iloc[col])
            if raw is None:
                continue
            rows.append({
                "release_workbook_month": release_month,
                "reference_month": f"{year:04d}-{int(pd.to_datetime(month, format='%b').month):02d}",
                "series": series,
                "value": value,
                "raw_value": raw,
                "provisional_marker": provisional,
                "base_year": 2012,
                "source_file": path.name,
                "source_sheet": sheet,
            })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--availability-map", type=Path, default=None)
    args = parser.parse_args()

    files = sorted(args.input_dir.glob("Annexures for Press Release in Excel *.xlsx"))
    if not files:
        raise SystemExit(f"No MoSPI annexure workbooks found in {args.input_dir}")

    records = []
    detected = []
    for path in files:
        book = pd.ExcelFile(path)
        for sheet in book.sheet_names:
            series = classify_time_series_sheet(path, sheet)
            if series:
                detected.append((release_month_from_name(path), sheet, series))
                records.extend(extract_sheet(path, sheet, series))

    out = pd.DataFrame(records)
    if out.empty:
        raise SystemExit("No cumulative All-India CPI time-series tables detected")

    key = ["release_workbook_month", "reference_month", "series"]
    duplicates = int(out.duplicated(key).sum())
    if duplicates:
        raise SystemExit(f"Duplicate vintage keys found: {duplicates}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = out.sort_values(key).reset_index(drop=True)

    if args.availability_map:
        availability = pd.read_csv(args.availability_map, dtype={"release_workbook_month": str})
        required = {"release_workbook_month", "actual_release_date", "embargo_time_ist", "next_nse_session"}
        missing = required - set(availability.columns)
        if missing:
            raise SystemExit(f"Availability map missing columns: {sorted(missing)}")
        out = out.merge(availability[list(required)], on="release_workbook_month", how="left", validate="many_to_one")
        if out["actual_release_date"].isna().any() or out["next_nse_session"].isna().any():
            missing_releases = sorted(out.loc[out["actual_release_date"].isna(), "release_workbook_month"].unique())
            raise SystemExit(f"Missing verified release dates for snapshots: {missing_releases}")
        out["available_at_ist"] = pd.to_datetime(
            out["actual_release_date"] + " " + out["embargo_time_ist"], errors="raise"
        ).dt.strftime("%Y-%m-%d %H:%M:%S")
        out["available_from_session"] = out["next_nse_session"]
        out["availability_policy"] = (
            "First eligible NSE session after actual MoSPI release; never available on release date"
        )

    target = args.output_dir / "cpi_2012base_point_in_time_vintages.csv"
    out.to_csv(target, index=False)
    print(f"Workbooks scanned: {len(files)}")
    print(f"Time-series sheets detected: {len(detected)}")
    print(f"Detected sheet mapping: {detected}")
    print(f"Rows: {len(out)}")
    print(f"Release snapshots: {out.release_workbook_month.nunique()}")
    print(f"Reference months: {out.reference_month.nunique()}")
    print(f"Provisional-marked values: {int(out.provisional_marker.sum())}")
    print(f"Duplicate vintage keys: {duplicates}")
    print(f"Saved: {target}")
    print("Point-in-time timestamps attached: " + str(args.availability_map is not None))


if __name__ == "__main__":
    main()
