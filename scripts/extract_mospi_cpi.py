#!/usr/bin/env python3
"""Extract headline India CPI observations from supplied MoSPI Excel workbooks.

Usage:
  python scripts/extract_mospi_cpi.py --input-dir data/raw/cpi --output-dir data/processed/cpi

The script preserves base-2012 release vintages separately from the base-2024
current series. It deliberately does not invent exact publication timestamps.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import json
import re
from datetime import date, timedelta
from pathlib import Path

from openpyxl import load_workbook


def month_start(year: int, month: int) -> date:
    return date(year, month, 1)


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def extract_base2012(input_dir: Path) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    files = sorted(input_dir.glob("Annexures for Press Release in Excel *.xlsx"))
    for path in files:
        match = re.search(r"Excel ([A-Za-z]+) (\d{4})\.xlsx$", path.name)
        if not match:
            continue
        release_month_num = list(calendar.month_name).index(match.group(1))
        release_month = month_start(int(match.group(2)), release_month_num)
        workbook = load_workbook(path, read_only=True, data_only=True)
        try:
            sheet = workbook["Annex-I"]
            general = None
            for values in sheet.iter_rows(values_only=True):
                if any(isinstance(value, str) and "General Index (All Groups)" in value for value in values):
                    general = values
                    break
            if general is None:
                raise ValueError(f"Headline General Index row not found: {path.name}")
            previous_month = (release_month - timedelta(days=1)).replace(day=1)
            for sector, (previous_col, current_col) in {
                "Rural": (4, 5), "Urban": (7, 8), "Combined": (10, 11)
            }.items():
                for reference_month, col, status in (
                    (previous_month, previous_col, "Final"),
                    (release_month, current_col, "Provisional"),
                ):
                    value = general[col]
                    rows.append({
                        "reference_month": reference_month.isoformat(),
                        "sector": sector,
                        "cpi_index": value,
                        "status_in_release": status,
                        "release_month": release_month.isoformat(),
                        "release_date_exact": "",
                        "base_year": 2012,
                        "source_file": path.name,
                        "source_sheet": "Annex-I",
                        "source_row": "General Index (All Groups)",
                    })
        finally:
            workbook.close()
    rows.sort(key=lambda row: (row["reference_month"], row["sector"], row["release_month"], row["status_in_release"]))
    return rows, [path.name for path in files]


def extract_base2024(path: Path) -> list[dict]:
    if not path.exists():
        return []
    workbook = load_workbook(path, read_only=True, data_only=True)
    rows: list[dict] = []
    try:
        sheet = workbook["CPI Data"]
        iterator = sheet.iter_rows(values_only=True)
        headers = next(iterator)
        for values in iterator:
            record = dict(zip(headers, values))
            if not (
                str(record.get("base_year")) == "2024"
                and record.get("series") == "Current"
                and record.get("state") == "All India"
                and record.get("division") == "CPI (General)"
                and record.get("sector") in {"Rural", "Urban", "Combined"}
            ):
                continue
            month_num = list(calendar.month_name).index(str(record["month"]))
            reference_month = month_start(int(record["year"]), month_num)
            rows.append({
                "reference_month": reference_month.isoformat(),
                "sector": record["sector"],
                "cpi_index": record.get("index"),
                "inflation_yoy_pct": record.get("inflation"),
                "base_year": 2024,
                "series": "Current",
                "release_date_exact": "",
                "source_file": path.name,
                "source_sheet": "CPI Data",
                "source_filter": "All India | CPI (General) | headline row",
            })
    finally:
        workbook.close()
    rows.sort(key=lambda row: (row["reference_month"], row["sector"]))
    return rows


def extract_base2012_full_timeseries(path: Path) -> list[dict]:
    """Read the official monthly CPI 2012 headline index and YoY sheets."""
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        def read_sheet(sheet_name: str, value_name: str) -> dict[str, tuple[float, bool]]:
            sheet = workbook[sheet_name]
            values = list(sheet.iter_rows(values_only=True))
            months = [str(value).strip() for value in values[2][1:13]]
            result: dict[str, tuple[float, bool]] = {}
            for row in values[3:]:
                year = row[0]
                if not isinstance(year, int):
                    continue
                for month_number, month_name in enumerate(months, start=1):
                    value = row[month_number]
                    if value in (None, ""):
                        continue
                    provisional = str(value).strip().endswith("*")
                    number = float(str(value).strip().replace("*", ""))
                    result[month_start(year, month_number).isoformat()] = (number, provisional)
            return result

        indices = read_sheet("Annex-VI", "cpi_index")
        inflation = read_sheet("Annex-VII", "inflation_yoy_pct")
        rows = []
        for reference_month, (index_value, provisional) in sorted(indices.items()):
            inflation_value = inflation.get(reference_month, (None, False))[0]
            rows.append({
                "reference_month": reference_month,
                "sector": "Combined",
                "cpi_index": index_value,
                "inflation_yoy_pct": inflation_value,
                "status_in_latest_snapshot": "Provisional" if provisional else "Historical/final",
                "snapshot_release_date": "2026-01-12",
                "snapshot_release_time_ist": "16:00",
                "base_year": 2012,
                "source_file": path.name,
                "source_sheet": "Annex-VI + Annex-VII",
            })
        return rows
    finally:
        workbook.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    base12, files = extract_base2012(args.input_dir)
    base24_path = args.input_dir / "cpi_33.xlsx"
    base24 = extract_base2024(base24_path)
    base12_full = extract_base2012_full_timeseries(base24_path.parent / "Annexures for Press Release in Excel December 2025.xlsx")

    fields12 = ["reference_month", "sector", "cpi_index", "status_in_release",
                "release_month", "release_date_exact", "base_year", "source_file",
                "source_sheet", "source_row"]
    fields_full = ["reference_month", "sector", "cpi_index", "inflation_yoy_pct", "status_in_latest_snapshot", "snapshot_release_date", "snapshot_release_time_ist", "base_year", "source_file", "source_sheet"]
    write_csv(args.output_dir / "india_cpi_base2012_combined_full_timeseries.csv", base12_full, fields_full)
    fields24 = ["reference_month", "sector", "cpi_index", "inflation_yoy_pct",
                "base_year", "series", "release_date_exact", "source_file",
                "source_sheet", "source_filter"]
    write_csv(args.output_dir / "india_cpi_base2012_release_vintages.csv", base12, fields12)
    latest_by_key: dict[tuple[str, str], dict] = {}
    for row in base12:
        key = (row["reference_month"], row["sector"])
        if key not in latest_by_key or row["release_month"] >= latest_by_key[key]["release_month"]:
            latest_by_key[key] = row
    latest = sorted(latest_by_key.values(), key=lambda row: (row["reference_month"], row["sector"]))
    write_csv(args.output_dir / "india_cpi_base2012_latest_available.csv", latest, fields12)
    write_csv(args.output_dir / "india_cpi_base2024_current_headline.csv", base24, fields24)

    def coverage(rows: list[dict]) -> dict:
        dates = sorted({row["reference_month"] for row in rows})
        return {
            "rows": len(rows),
            "unique_reference_months": len(dates),
            "coverage_start": dates[0] if dates else None,
            "coverage_end": dates[-1] if dates else None,
            "sectors": sorted({row["sector"] for row in rows}),
            "missing_index_values": sum(row.get("cpi_index") in (None, "") for row in rows),
        }

    qa = {
        "source_files_base2012": files,
        "base2012_release_vintages": coverage(base12),
        "base2012_combined_full_snapshot": coverage(base12_full),
        "base2024_current_headline": coverage(base24),
        "exact_publication_timestamps_available": False,
        "base2012_full_snapshot_release": "2026-01-12 16:00 IST (from the December 2025 MoSPI CPI press release)",
        "controls": [
            "Base-2012 and base-2024 series are kept separate; no splicing is performed.",
            "Prior-month Final and current-month Provisional observations are retained as release vintages.",
            "Do not merge CPI to daily prices by reference month alone.",
            "Use a CPI observation only after its exact publication timestamp is known and is <= prediction timestamp.",
            "The latest-available CSV is a convenience snapshot, not a point-in-time backtest panel.",
        ],
    }
    (args.output_dir / "india_cpi_dataset_qa.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
    print(json.dumps(qa, indent=2))


if __name__ == "__main__":
    main()
