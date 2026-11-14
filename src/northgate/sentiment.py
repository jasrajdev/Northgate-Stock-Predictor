"""News timestamps -> NSE sessions, and headline sentiment scoring (VADER; FinBERT optional).

Rule (PRD 10.1, DECISIONS): an item published at or after the 15:30 IST close, or on a
non-trading day, counts for the NEXT trading session. Sessions come from the observed panel;
dates beyond the panel use weekdays and are flagged `calendar_extrapolated`.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .config import IST_CLOSE

IST = "Asia/Kolkata"


def first_available_session(published_utc: pd.Series, sessions: pd.DatetimeIndex) -> pd.DataFrame:
    ts = pd.to_datetime(published_utc, utc=True).dt.tz_convert(IST)
    day = ts.dt.tz_localize(None).dt.normalize()
    after_close = (ts.dt.hour * 60 + ts.dt.minute) >= IST_CLOSE[0] * 60 + IST_CLOSE[1]
    sessions = pd.DatetimeIndex(sorted(sessions))
    last = sessions.max()
    out, extrap = [], []
    for d, ac in zip(day, after_close):
        if d <= last:
            # first session >= d, or > d if the item arrived after the close on a session day
            i = sessions.searchsorted(d, side="right" if ac else "left")
            if i < len(sessions):
                out.append(sessions[i]); extrap.append(False); continue
            d = last
        nxt = d + pd.Timedelta(days=1) if (ac or d <= last) else d
        while nxt.weekday() >= 5:
            nxt += pd.Timedelta(days=1)
        out.append(nxt); extrap.append(True)
    return pd.DataFrame({"published_ist": ts, "session": out, "calendar_extrapolated": extrap})


def vader_scores(texts) -> pd.Series:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    a = SentimentIntensityAnalyzer()
    return pd.Series([a.polarity_scores(str(t))["compound"] for t in texts])


def finbert_scores(texts, model: str = "ProsusAI/finbert") -> pd.DataFrame:
    """P(positive) - P(negative) plus the three probabilities. Requires `transformers` and torch."""
    from transformers import pipeline
    clf = pipeline("text-classification", model=model, top_k=None, truncation=True)
    rows = []
    for res in clf(list(map(str, texts)), batch_size=32):
        p = {d["label"].lower(): d["score"] for d in res}
        rows.append({"finbert_pos": p.get("positive", np.nan), "finbert_neg": p.get("negative", np.nan),
                     "finbert_neu": p.get("neutral", np.nan), "finbert_polarity": p.get("positive", 0) - p.get("negative", 0)})
    return pd.DataFrame(rows)


def daily(items: pd.DataFrame, score_col: str) -> pd.DataFrame:
    """Per ticker and session: mean score, article count, 3-session momentum, volume-spike flag."""
    g = items.groupby(["ticker", "session"]).agg(score=(score_col, "mean"), articles=(score_col, "size")).reset_index()
    parts = []
    for t, x in g.groupby("ticker"):
        x = x.sort_values("session").copy()
        x["momentum_3"] = x.score.rolling(3, min_periods=1).mean()
        base = x.articles.shift(1).rolling(20, min_periods=5)
        x["volume_spike"] = x.articles > base.mean() + 2 * base.std()
        parts.append(x)
    return pd.concat(parts, ignore_index=True) if parts else g
