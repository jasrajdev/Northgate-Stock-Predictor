"""Fetch recent timestamped English headlines per covered company from the GDELT DOC 2.0 API.

Usage: python scripts/fetch_news_gdelt.py [--timespan 3months]

* Free, no key. GDELT asks for at most one request every 5 seconds; this script waits and backs off.
* The DOC API covers a rolling recent window only; it cannot backfill 2016-2025 history.
* Stores headline, URL, domain and GDELT first-seen time (UTC) only, not article text.
* Output (git-ignored): data/raw/news/gdelt/<UTC timestamp>/<ticker>.json and data/processed/news_items.csv
"""
from __future__ import annotations
import argparse, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
import pandas as pd, requests

QUERIES = {
    "BHARTIARTL.NS": '"Bharti Airtel"', "HDFCBANK.NS": '"HDFC Bank"', "HINDUNILVR.NS": '"Hindustan Unilever"',
    "ICICIBANK.NS": '"ICICI Bank"', "INFY.NS": '"Infosys"', "ITC.NS": '("ITC Ltd" OR "ITC Limited")',
    "LT.NS": '"Larsen & Toubro"', "RELIANCE.NS": '"Reliance Industries"', "SUNPHARMA.NS": '"Sun Pharma"',
    "TCS.NS": '"Tata Consultancy Services"', "^NSEI": '("Nifty 50" OR Sensex)',
}
URL = "https://api.gdeltproject.org/api/v2/doc/doc"


def fetch(q: str, timespan: str) -> list:
    wait = 10
    for _ in range(8):
        r = requests.get(URL, params={"query": f"{q} sourcelang:english", "mode": "ArtList", "maxrecords": 250,
                                      "format": "json", "timespan": timespan, "sort": "DateDesc"},
                         timeout=60, headers={"User-Agent": "northgate-research"})
        if r.status_code == 200 and r.text.strip().startswith("{"):
            return r.json().get("articles", [])
        print(f"  HTTP {r.status_code}; waiting {wait}s", flush=True); time.sleep(wait); wait = min(wait * 2, 120)
    raise RuntimeError("GDELT kept refusing requests")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--timespan", default="3months"); a = ap.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw = ROOT / "data" / "raw" / "news" / "gdelt" / stamp; raw.mkdir(parents=True, exist_ok=True)
    rows = []
    for t, q in QUERIES.items():
        arts = fetch(q, a.timespan)
        (raw / f"{t.replace('^', '')}.json").write_text(json.dumps({"query": q, "retrieved_utc": stamp, "articles": arts}, indent=1))
        for x in arts:
            rows.append({"ticker": t, "scope": "market" if t == "^NSEI" else "company", "title": x.get("title"), "url": x.get("url"),
                         "domain": x.get("domain"), "language": x.get("language"), "source_country": x.get("sourcecountry"),
                         "first_seen_utc": pd.to_datetime(x.get("seendate"), format="%Y%m%dT%H%M%SZ", utc=True),
                         "source_system": "gdelt_doc_v2", "retrieved_utc": stamp, "query": q})
        print(f"{t}: {len(arts)} articles", flush=True); time.sleep(7)
    df = pd.DataFrame(rows).drop_duplicates(["ticker", "url"])
    out = ROOT / "data" / "processed" / "news_items.csv"; df.to_csv(out, index=False)
    print("saved", len(df), "items to", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
