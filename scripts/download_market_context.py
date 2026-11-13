#!/usr/bin/env python3
"""Download India VIX and NIFTY sector-index context from Yahoo Finance.

This creates a separate context panel. It does not merge the data into stock
features; that merge must be reviewed for date alignment and leakage first.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

TICKERS = {
    "^INDIAVIX": "India VIX",
    "^NSEBANK": "NIFTY Bank",
    "^CNXIT": "NIFTY IT",
    "^CNXPHARMA": "NIFTY Pharma",
    "^CNXAUTO": "NIFTY Auto",
    "^CNXFMCG": "NIFTY FMCG",
    "^CNXMETAL": "NIFTY Metal",
    "^CNXREALTY": "NIFTY Realty",
    "^CNXENERGY": "NIFTY Energy",
    "^CNXPSUBANK": "NIFTY PSU Bank",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2016-01-01")
    parser.add_argument("--end", default=None, help="Exclusive end date; defaults to latest")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/market_context"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    panels = []
    report = {
        "source": "Yahoo Finance via yfinance",
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "start_requested": args.start,
        "end_requested_exclusive": args.end,
        "tickers": {},
        "limitations": [
            "Yahoo Finance is a secondary vendor, not the official NSE archive.",
            "Index histories and ticker availability can change; inspect coverage before use.",
            "This context panel is not yet merged into model features.",
            "Index observation date is not the same as the time the value became available.",
        ],
    }

    for ticker, name in TICKERS.items():
        try:
            data = yf.download(
                ticker,
                start=args.start,
                end=args.end,
                auto_adjust=False,
                actions=False,
                progress=False,
                threads=False,
            )
            if data.empty:
                report["tickers"][ticker] = {"name": name, "status": "empty"}
                continue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            data = data.reset_index()
            date_col = "Date" if "Date" in data.columns else data.columns[0]
            data = data.rename(columns={date_col: "Date"})
            keep = [col for col in ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"] if col in data.columns]
            data = data[keep].copy()
            data["Ticker"] = ticker
            data["Name"] = name
            data["Date"] = pd.to_datetime(data["Date"]).dt.date.astype(str)
            data = data.drop_duplicates(["Ticker", "Date"]).sort_values("Date")
            panels.append(data)
            report["tickers"][ticker] = {
                "name": name,
                "status": "downloaded",
                "rows": int(len(data)),
                "start": str(data["Date"].min()),
                "end": str(data["Date"].max()),
                "missing_close": int(data["Close"].isna().sum()) if "Close" in data else None,
            }
        except Exception as exc:
            report["tickers"][ticker] = {"name": name, "status": "error", "error": str(exc)}

    if panels:
        panel = pd.concat(panels, ignore_index=True)
        panel = panel.sort_values(["Ticker", "Date"]).reset_index(drop=True)
        panel.to_csv(args.output_dir / "market_context_panel.csv", index=False)
        report["total_rows"] = int(len(panel))
        report["duplicate_ticker_date_keys"] = int(panel.duplicated(["Ticker", "Date"]).sum())
    else:
        report["total_rows"] = 0
        report["duplicate_ticker_date_keys"] = 0

    (args.output_dir / "market_context_qa.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
