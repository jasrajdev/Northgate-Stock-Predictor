#!/usr/bin/env python3
"""Download PRD and India-specific macro series from public FRED CSV endpoints.

Run:
  python scripts/download_macro_context.py

Outputs raw observation-date series and a QA report. This script deliberately
does NOT merge macro observations into daily equity rows: reference dates are
not publication timestamps, and standard FRED CSV downloads do not preserve
historical vintages. Release-time alignment must be completed separately.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed" / "macro_context"
SERIES = {
    # Explicit PRD reference series (United States/global context)
    "DGS3MO": {"name": "US Treasury 3-Month Constant Maturity Rate", "frequency": "daily", "units": "percent", "role": "PRD global short-rate reference"},
    "DGS10": {"name": "US Treasury 10-Year Constant Maturity Rate", "frequency": "daily", "units": "percent", "role": "PRD global long-yield reference"},
    "CPIAUCSL": {"name": "US CPI All Urban Consumers", "frequency": "monthly", "units": "index", "role": "PRD global inflation reference"},
    "UNRATE": {"name": "US Civilian Unemployment Rate", "frequency": "monthly", "units": "percent", "role": "PRD global labour-market reference"},
    # India-specific supplementary context (OECD series distributed by FRED)
    "INDIRLTLT01STM": {"name": "India 10-Year Government Bond Yield", "frequency": "monthly", "units": "percent", "role": "India local long-yield context"},
    "INDIR3TIB01STM": {"name": "India 3-Month Interbank Rate", "frequency": "monthly", "units": "percent", "role": "India local short-rate context"},
    "IRSTCB01INM156N": {"name": "India Central Bank Rate", "frequency": "monthly", "units": "percent", "role": "India policy-rate context"},
}


def fetch_series(series_id: str) -> pd.DataFrame:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    frame = pd.read_csv(url)
    if list(frame.columns)[:1] != ["observation_date"]:
        # FRED's graph CSV has used observation_date as its first column.
        frame = frame.rename(columns={frame.columns[0]: "observation_date"})
    if series_id not in frame.columns:
        raise ValueError(f"Expected column {series_id}; got {list(frame.columns)}")
    frame = frame.rename(columns={series_id: "value"})
    frame["observation_date"] = pd.to_datetime(frame["observation_date"], errors="coerce")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["observation_date"]).sort_values("observation_date")
    frame["series_id"] = series_id
    return frame[["observation_date", "series_id", "value"]]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panels = []
    report = {
        "source": "FRED graph CSV; India series sourced from OECD via FRED",
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "series": {},
        "warnings": [
            "Observation date is not necessarily public release date; do not merge by observation date alone.",
            "Standard graph CSV is a current data snapshot, not a point-in-time vintage archive.",
            "For a historical backtest, retrieve ALFRED vintages or reconstruct actual release timestamps before using revised macro values.",
            "India OECD 10-year and 3-month series are monthly averages/observations, not daily RBI market yields.",
            "US PRD reference series are global context and must not be mislabeled as Indian macro indicators.",
            "Check FRED/OECD series copyright and citation terms before redistribution.",
        ],
    }
    for series_id, metadata in SERIES.items():
        try:
            frame = fetch_series(series_id)
            panels.append(frame)
            report["series"][series_id] = {
                **metadata,
                "status": "downloaded",
                "rows": int(len(frame)),
                "start": frame["observation_date"].min().date().isoformat() if len(frame) else None,
                "end": frame["observation_date"].max().date().isoformat() if len(frame) else None,
                "missing_values": int(frame["value"].isna().sum()),
                "duplicate_dates": int(frame.duplicated(["observation_date"]).sum()),
            }
        except Exception as exc:
            report["series"][series_id] = {**metadata, "status": "error", "error": str(exc)}
    if panels:
        panel = pd.concat(panels, ignore_index=True).sort_values(["series_id", "observation_date"])
        panel.to_csv(OUT / "macro_observation_panel.csv", index=False)
        report["total_rows"] = int(len(panel))
        report["duplicate_series_date_keys"] = int(panel.duplicated(["series_id", "observation_date"]).sum())
    else:
        report["total_rows"] = 0
        report["duplicate_series_date_keys"] = 0
    (OUT / "macro_context_qa.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
