"""Download and validate Northgate's initial Indian-equity market dataset.

Source: Yahoo Finance via yfinance.
This is a convenience research source, not an exchange-certified archive.
Raw ticker files are preserved separately; the processed panel is a combined copy.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "yahoo"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "reports" / "data_quality"

START_DATE = "2016-01-01"
# yfinance treats end as exclusive. Use today's date so the latest available
# completed session is included when Yahoo has published it.
END_DATE = datetime.now(timezone.utc).date().isoformat()

# Provisional, diversified large-cap candidates. This is not a final universe
# decision; change only after checking availability and documenting the choice.
TICKERS = {
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "TCS.NS": "Tata Consultancy Services",
    "INFY.NS": "Infosys",
    "RELIANCE.NS": "Reliance Industries",
    "ITC.NS": "ITC",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "SUNPHARMA.NS": "Sun Pharma",
    "BHARTIARTL.NS": "Bharti Airtel",
    "LT.NS": "Larsen & Toubro",
}
BENCHMARK = {"^NSEI": "NIFTY 50 price index"}

REQUIRED = ["Open", "High", "Low", "Close", "Volume"]


def flatten_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert yfinance's possible MultiIndex columns to simple field names."""
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = [
            str(col[0] if col[0] in REQUIRED + ["Adj Close", "Dividends", "Stock Splits"]
                else col[-1])
            for col in frame.columns
        ]
    frame.columns = [str(c).strip() for c in frame.columns]
    return frame


def download_one(symbol: str, name: str, is_benchmark: bool = False) -> tuple[pd.DataFrame, dict]:
    frame = yf.download(
        symbol,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=False,
        actions=True,
        progress=False,
        threads=False,
    )
    if frame is None or frame.empty:
        raise RuntimeError(f"No rows returned for {symbol}")

    frame = flatten_columns(frame.copy())
    frame.index = pd.to_datetime(frame.index).tz_localize(None)
    frame.index.name = "Date"
    frame = frame.reset_index()

    # Some Yahoo responses may omit adjusted close or corporate-action columns.
    for col in ["Adj Close", "Dividends", "Stock Splits"]:
        if col not in frame.columns:
            frame[col] = pd.NA

    missing_required = [c for c in REQUIRED if c not in frame.columns]
    if missing_required:
        raise RuntimeError(f"{symbol}: missing required columns: {missing_required}")

    frame.insert(1, "Ticker", symbol)
    frame.insert(2, "Name", name)
    frame["Date"] = pd.to_datetime(frame["Date"]).dt.strftime("%Y-%m-%d")

    # Preserve the provider response (including Adj Close/actions) in raw storage.
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = symbol.replace("^", "").replace(".", "_")
    raw_path = RAW_DIR / f"{safe_name}.csv"
    frame.to_csv(raw_path, index=False)

    numeric = frame[REQUIRED + ["Adj Close"]].apply(pd.to_numeric, errors="coerce")
    bad_ohlc = (
        (numeric["High"] < numeric[["Open", "Close", "Low"]].max(axis=1))
        | (numeric["Low"] > numeric[["Open", "Close", "High"]].min(axis=1))
        | (numeric[REQUIRED[:4]] <= 0).any(axis=1)
    )
    dates = pd.to_datetime(frame["Date"])
    gaps = dates.sort_values().diff().dt.days
    report = {
        "ticker": symbol,
        "name": name,
        "benchmark": is_benchmark,
        "rows": int(len(frame)),
        "first_date": str(frame["Date"].min()),
        "last_date": str(frame["Date"].max()),
        "duplicate_dates": int(frame["Date"].duplicated().sum()),
        "missing_required_values": {
            c: int(numeric[c].isna().sum()) for c in REQUIRED
        },
        "missing_adjusted_close": int(numeric["Adj Close"].isna().sum()),
        "invalid_ohlc_or_nonpositive_price_rows": int(bad_ohlc.sum()),
        "calendar_gaps_over_7_days": int((gaps > 7).sum()),
        "raw_file": str(raw_path.relative_to(ROOT)),
        "status": "OK" if len(frame) > 0 else "EMPTY",
    }
    return frame, report


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    all_frames: list[pd.DataFrame] = []
    reports: list[dict] = []
    failures: list[dict] = []

    instruments = {**TICKERS, **BENCHMARK}
    for symbol, name in instruments.items():
        print(f"Downloading {symbol} — {name} ...", flush=True)
        try:
            frame, report = download_one(
                symbol, name, is_benchmark=symbol in BENCHMARK
            )
            all_frames.append(frame)
            reports.append(report)
            print(
                f"  OK: {report['rows']} rows "
                f"({report['first_date']} to {report['last_date']})",
                flush=True,
            )
        except Exception as exc:
            failures.append({"ticker": symbol, "error": str(exc)})
            print(f"  FAILED: {exc}", file=sys.stderr, flush=True)

    if all_frames:
        panel = pd.concat(all_frames, ignore_index=True)
        panel["Date"] = pd.to_datetime(panel["Date"])
        panel = panel.sort_values(["Ticker", "Date"]).reset_index(drop=True)
        panel_path = PROCESSED_DIR / "market_panel.csv"
        panel.to_csv(panel_path, index=False)
    else:
        panel_path = None

    summary = {
        "source": "Yahoo Finance via yfinance",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "start_date": START_DATE,
        "end_date_exclusive": END_DATE,
        "tickers_requested": list(instruments),
        "tickers_downloaded": [r["ticker"] for r in reports],
        "failures": failures,
        "total_rows": int(sum(r["rows"] for r in reports)),
        "processed_panel": str(panel_path.relative_to(ROOT)) if panel_path else None,
        "ticker_checks": reports,
        "limitations": [
            "Yahoo Finance data is third-party convenience data, not an exchange-certified archive.",
            "Today's stock list can create survivorship bias; historical index membership is not reconstructed.",
            "The NIFTY 50 ticker downloaded here is the price index (^NSEI), not the Total Returns Index.",
            "Calendar gaps are flagged for inspection; weekends and exchange holidays are not treated as missing rows.",
            "This first pass preserves raw downloads and creates a combined panel; it does not impute missing prices.",
        ],
    }
    report_path = REPORT_DIR / "download_report.json"
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\n=== DOWNLOAD SUMMARY ===")
    print(f"Successful tickers: {len(reports)}/{len(instruments)}")
    print(f"Total rows: {summary['total_rows']}")
    print(f"Processed panel: {panel_path if panel_path else 'NOT CREATED'}")
    print(f"Quality report: {report_path}")
    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"  {failure['ticker']}: {failure['error']}")

    # Non-zero exit alerts the user that one or more requested symbols failed.
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
