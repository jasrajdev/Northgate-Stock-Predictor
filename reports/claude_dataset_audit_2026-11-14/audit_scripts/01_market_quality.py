"""READ-ONLY market-data quality audit. Writes only into the audit directory."""
from pathlib import Path
import json, hashlib
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parents[1] / "evidence"
RAW = ROOT / "data/raw/yahoo"
panel = pd.read_csv(ROOT / "data/processed/market_panel.csv", parse_dates=["Date"])
print("panel shape", panel.shape, "cols", list(panel.columns))
print("dtypes ok; date range", panel.Date.min().date(), panel.Date.max().date(), "tickers", panel.Ticker.nunique())
print("dup keys", int(panel.duplicated(["Ticker", "Date"]).sum()), "| NaN cells", int(panel.isna().sum().sum()))
print("sorted by Ticker,Date:", bool(panel.equals(panel.sort_values(["Ticker", "Date"]).reset_index(drop=True))))

# raw vs panel: full equality
mism = {}
frames = []
for f in sorted(RAW.glob("*.csv")):
    r = pd.read_csv(f, parse_dates=["Date"])
    frames.append(r)
    t = r.Ticker.iloc[0]
    p = panel[panel.Ticker == t].reset_index(drop=True)
    same = r.shape == p.shape and r.reset_index(drop=True).equals(p[r.columns])
    mism[t] = bool(same)
print("raw==panel per ticker (all rows, all columns):", mism)

eq = panel[panel.Ticker != "^NSEI"]
all_dates = pd.DatetimeIndex(sorted(panel.Date.unique()))
eq_dates = pd.DatetimeIndex(sorted(eq.Date.unique()))
idx_dates = pd.DatetimeIndex(sorted(panel[panel.Ticker == "^NSEI"].Date.unique()))
print("union dates", len(all_dates), "equity-union", len(eq_dates), "index", len(idx_dates))
print("weekend dates in panel:", [str(d.date()) + "(" + d.day_name()[:3] + ")" for d in all_dates if d.dayofweek >= 5])
print("in equities not index:", [str(d.date()) for d in eq_dates.difference(idx_dates)])
print("in index not equities:", [str(d.date()) for d in idx_dates.difference(eq_dates)])

# zero-volume / stale-bar analysis across equities
e = eq.sort_values(["Ticker", "Date"]).copy()
e["prev_close"] = e.groupby("Ticker")["Close"].shift(1)
e["stale"] = (e.Close == e.prev_close)
e["flat"] = (e.Open == e.High) & (e.High == e.Low) & (e.Low == e.Close)
e["zero_vol"] = e.Volume == 0
bydate = e.groupby("Date").agg(n=("Ticker", "size"), zero_vol=("zero_vol", "sum"), stale=("stale", "sum"), flat=("flat", "sum"))
sus = bydate[(bydate.zero_vol >= 5) | (bydate.stale >= 5)]
print("\nDates where >=5 of 10 equities have zero volume or unchanged close:")
print(sus.to_string())
sus.to_csv(OUT / "suspect_stale_or_zero_volume_dates.csv")
idx = panel[panel.Ticker == "^NSEI"].set_index("Date")
print("\nIndex rows on those dates (Close, Volume):")
print(idx.reindex(sus.index)[["Open", "High", "Low", "Close", "Volume"]].to_string())

rows = []
for t, g in panel.groupby("Ticker"):
    g = g.sort_values("Date")
    num = g[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
    bad_hl = int(((g.High < g[["Open", "Close", "Low"]].max(axis=1)) | (g.Low > g[["Open", "Close", "High"]].min(axis=1))).sum())
    nonpos = int((g[["Open", "High", "Low", "Close", "Adj Close"]] <= 0).any(axis=1).sum())
    lr = np.log(g["Adj Close"]).diff()
    lrc = np.log(g["Close"]).diff()
    gaps = g.Date.diff().dt.days
    union = eq_dates if t != "^NSEI" else idx_dates
    ref = all_dates[(all_dates >= g.Date.min()) & (all_dates <= g.Date.max())]
    missing = ref.difference(pd.DatetimeIndex(g.Date))
    ratio = g["Adj Close"] / g["Close"]
    big = g.loc[lr.abs() > 0.10, "Date"].dt.strftime("%Y-%m-%d").tolist()
    rows.append(dict(
        ticker=t, first_date=str(g.Date.min().date()), last_date=str(g.Date.max().date()), rows=len(g),
        union_sessions_in_span=len(ref), missing_vs_union=len(missing),
        missing_dates=";".join(str(d.date()) for d in missing),
        duplicate_dates=int(g.Date.duplicated().sum()), missing_values=int(g.isna().sum().sum()),
        invalid_high_low=bad_hl, nonpositive_price_rows=nonpos, negative_volume=int((g.Volume < 0).sum()),
        zero_volume_rows=int((g.Volume == 0).sum()),
        unchanged_close_rows=int((g.Close == g.Close.shift(1)).sum()),
        flat_ohlc_rows=int(((g.Open == g.High) & (g.High == g.Low) & (g.Low == g.Close)).sum()),
        max_calendar_gap_days=int(gaps.max()), gaps_over_5_days=int((gaps > 5).sum()),
        abs_adj_logret_gt_10pct=len(big), big_move_dates=";".join(big),
        min_adj_logret=round(float(lr.min()), 5), max_adj_logret=round(float(lr.max()), 5),
        max_abs_diff_close_vs_adj_logret=round(float((lr - lrc).abs().max()), 5),
        dividend_events=int((g.Dividends != 0).sum()), split_events=int((g["Stock Splits"] != 0).sum()),
        split_dates=";".join(f"{d.date()}:{s}" for d, s in zip(g.Date[g["Stock Splits"] != 0], g["Stock Splits"][g["Stock Splits"] != 0])),
        adj_over_close_min=round(float(ratio.min()), 6), adj_over_close_max=round(float(ratio.max()), 6),
        years_of_history=round((g.Date.max() - g.Date.min()).days / 365.25, 2),
        source="Yahoo Finance via yfinance 1.8.0 (auto_adjust=False)",
    ))
q = pd.DataFrame(rows)
q.to_csv(OUT / "per_ticker_quality.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print("\nPER-TICKER QUALITY")
print(q.drop(columns=["missing_dates", "big_move_dates", "split_dates", "source"]).T.to_string())
for _, r in q.iterrows():
    print(r.ticker, "| missing:", r.missing_dates or "-", "| big moves:", r.big_move_dates or "-", "| splits:", r.split_dates or "-")

# dividends: does Adj/Close ratio step exactly at dividend dates?
print("\nAdj/Close ratio step dates not matching a Dividends entry (tolerance 1e-4), per ticker:")
for t, g in eq.groupby("Ticker"):
    g = g.sort_values("Date").reset_index(drop=True)
    ratio = g["Adj Close"] / g["Close"]
    step = (ratio / ratio.shift(1) - 1).abs() > 1e-4
    div = g.Dividends != 0
    print(f"  {t}: steps={int(step.sum())} dividends={int(div.sum())} step_without_div={int((step & ~div).sum())} div_without_step={int((div & ~step).sum())}",
          "| dates:", g.Date[step & ~div].dt.strftime("%Y-%m-%d").tolist()[:8])
