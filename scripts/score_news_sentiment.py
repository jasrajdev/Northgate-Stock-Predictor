"""Score fetched headlines with VADER (always) and FinBERT (if `transformers` is installed),
then map each item to its first available NSE session (after-close -> next session).

Usage: python scripts/score_news_sentiment.py [--no-finbert]
Output (git-ignored): data/processed/news_scored.csv, data/processed/sentiment_daily.csv
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from northgate import config, sentiment as S


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--no-finbert", action="store_true"); a = ap.parse_args()
    items = pd.read_csv(config.PROCESSED / "news_items.csv")
    items = items.dropna(subset=["title"]).drop_duplicates(["ticker", "title"]).reset_index(drop=True)
    panel = pd.read_csv(config.PROCESSED / "market_panel.csv", usecols=["Date", "Ticker"], parse_dates=["Date"])
    sessions = pd.DatetimeIndex(panel[panel.Ticker != config.BENCHMARK].Date.unique())
    items = pd.concat([items, S.first_available_session(items.first_seen_utc, sessions)], axis=1)
    items["vader_compound"] = S.vader_scores(items.title)
    score = "vader_compound"
    if not a.no_finbert:
        try:
            items = pd.concat([items, S.finbert_scores(items.title)], axis=1); score = "finbert_polarity"
            items["finbert_model"] = "ProsusAI/finbert"
        except Exception as e:
            print("FinBERT unavailable, VADER only:", type(e).__name__, str(e)[:120])
    items.to_csv(config.PROCESSED / "news_scored.csv", index=False)
    d = S.daily(items, score); d["score_source"] = score
    if score != "vader_compound":
        d = d.merge(S.daily(items, "vader_compound")[["ticker", "session", "score"]].rename(columns={"score": "vader_score"}), on=["ticker", "session"])
    d.to_csv(config.PROCESSED / "sentiment_daily.csv", index=False)
    print(f"{len(items)} items scored ({score}); {len(d)} ticker-sessions; sessions {d.session.min()} .. {d.session.max()}")


if __name__ == "__main__":
    main()
