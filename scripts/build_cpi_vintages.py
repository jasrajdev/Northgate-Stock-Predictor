"""Extract point-in-time India CPI vintages from MoSPI monthly annexure workbooks.

Usage:
  python scripts/build_cpi_vintages.py --input-dir data/raw/cpi_annexures --output-dir data/processed/cpi

The script reads Annexure VI (general CPI index, 2012=100) and Annexure VII
(year-on-year inflation, 2012=100) from each monthly workbook. Each row keeps
both the observation month and the release vintage. It does not forward-fill,
interpolate, or treat revised values as historically known.
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


def extract_sheet(path: Path, sheet: str, series: str) -> list[dict]:
    frame = pd.read_excel(path, sheet_name=sheet, header=None)
    release = re.search(r"Excel ([A-Za-z]+) (20\\d{2})", path.name)
    if not release:
        raise ValueError(f"Cannot infer release month/year from {path.name}")
    release_month = pd.to_datetime(f"{release.group(1)} 1 {release.group(2)}").strftime("%Y-%m")
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
    args = parser.parse_args()
    files = sorted(args.input_dir.glob("Annexures for Press Release in Excel *.xlsx"))
    if not files:
        raise SystemExit(f"No MoSPI annexure workbooks found in {args.input_dir}")
    records = []
    for path in files:
        book = pd.ExcelFile(path)
        if "Annex-VI" in book.sheet_names:
            records += extract_sheet(path, "Annex-VI", "index")
        if "Annex-VII" in book.sheet_names:
            records += extract_sheet(path, "Annex-VII", "inflation")
    out = pd.DataFrame(records)
    if out.empty:
        raise SystemExit("No CPI time-series records extracted")
    key = ["release_workbook_month", "reference_month", "series"]
    duplicates = int(out.duplicated(key).sum())
    if duplicates:
        raise SystemExit(f"Duplicate vintage keys found: {duplicates}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = out.sort_values(key).reset_index(drop=True)
    target = args.output_dir / "cpi_2012base_point_in_time_vintages.csv"
    out.to_csv(target, index=False)
    print(f"Workbooks: {len(files)}")
    print(f"Rows: {len(out)}")
    print(f"Release snapshots: {out.release_workbook_month.nunique()}")
    print(f"Reference months: {out.reference_month.nunique()}")
    print(f"Provisional-marked values: {int(out.provisional_marker.sum())}")
    print(f"Duplicate keys: {duplicates}")
    print(f"Saved: {target}")


if __name__ == "__main__":
    main()
