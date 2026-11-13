#!/usr/bin/env python3
"""Normalize cumulative MoSPI CPI annexure sheets into tidy monthly observations.

The workbook release month (vintage) is kept separate from the observation month.
Publication timestamps are deliberately not inferred from filenames; add them from
verified release metadata in a later step.
"""
from __future__ import annotations

import argparse
import csv
import re
from datetime import date
from pathlib import Path
from typing import Iterable

import openpyxl

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_LOOKUP = {m.lower(): i for i, m in enumerate(MONTHS, 1)}
FILENAME_RE = re.compile(r"Annexures for Press Release in Excel ([A-Za-z]+) (20\d{2})\.xlsx$", re.I)


def release_month(path: Path) -> date:
    match = FILENAME_RE.search(path.name)
    if not match:
        raise ValueError(f"Cannot infer release reference month from filename: {path.name}")
    month = MONTH_LOOKUP.get(match.group(1)[:3].lower())
    if not month:
        raise ValueError(f"Unknown month in filename: {path.name}")
    return date(int(match.group(2)), month, 1)


def find_table(sheet):
    title = " ".join(str(sheet.cell(r, c).value or "") for r in range(1, min(3, sheet.max_row) + 1) for c in range(1, sheet.max_column + 1))
    lower = re.sub(r"[, ]+", " ", title.lower()).strip()
    if "all india general cpi" in lower and "since january 2013" in lower:
        series = "general_cpi_index"
        start_year = 2013
    elif "inflation" in lower and "since january 2014" in lower and "cpi" in lower:
        series = "general_cpi_yoy_inflation_pct"
        start_year = 2014
    else:
        return None

    header_row = None
    month_columns = {}
    year_column = None
    for r in range(1, min(6, sheet.max_row) + 1):
        vals = [sheet.cell(r, c).value for c in range(1, sheet.max_column + 1)]
        normalized = [str(v).strip().lower() if v is not None else "" for v in vals]
        if "year" in normalized:
            year_column = normalized.index("year") + 1
            month_columns = {MONTH_LOOKUP[v[:3]]: i + 1 for i, v in enumerate(normalized) if v[:3] in MONTH_LOOKUP}
            if len(month_columns) == 12:
                header_row = r
                break
    if header_row is None:
        raise ValueError(f"Could not locate Year/Jan-Dec header in {sheet.title}")
    return series, start_year, header_row, year_column, month_columns


def parse_workbook(path: Path) -> list[dict]:
    vintage = release_month(path)
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    records = []
    for sheet in wb.worksheets:
        table = find_table(sheet)
        if not table:
            continue
        series, start_year, header_row, year_col, month_cols = table
        for r in range(header_row + 1, sheet.max_row + 1):
            year = sheet.cell(r, year_col).value
            if not isinstance(year, (int, float)) or int(year) != year:
                continue
            year = int(year)
            if year < start_year:
                continue
            for month_num, col in month_cols.items():
                value = sheet.cell(r, col).value
                if value is None or not isinstance(value, (int, float)):
                    continue
                obs_month = date(year, month_num, 1)
                if obs_month > vintage:
                    continue
                records.append({
                    "release_reference_month": vintage.isoformat(),
                    "observation_month": obs_month.isoformat(),
                    "series": series,
                    "base_year": 2012,
                    "value": value,
                    "release_timestamp": "",
                    "source_file": path.name,
                    "source_sheet": sheet.title,
                })
    wb.close()
    return records


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbooks", nargs="+", help="MoSPI monthly annexure .xlsx files")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args(argv)
    all_records = []
    for name in args.workbooks:
        all_records.extend(parse_workbook(Path(name)))
    key_fields = ("release_reference_month", "observation_month", "series")
    seen = set()
    duplicates = []
    for row in all_records:
        key = tuple(row[k] for k in key_fields)
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    if duplicates:
        raise SystemExit(f"Duplicate vintage/observation/series keys: {duplicates[:5]}")
    fields = ["release_reference_month", "observation_month", "series", "base_year", "value", "release_timestamp", "source_file", "source_sheet"]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(all_records, key=lambda x: (x["release_reference_month"], x["series"], x["observation_month"])))
    print(f"workbooks={len(args.workbooks)} records={len(all_records)} unique_keys={len(seen)} output={output}")
    print("series_counts=" + str({s: sum(r['series'] == s for r in all_records) for s in sorted({r['series'] for r in all_records})}))
    print("release_timestamps=not populated; must be sourced from verified release metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
