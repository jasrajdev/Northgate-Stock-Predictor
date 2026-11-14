"""READ-ONLY: event windows around corporate actions in the original Yahoo data."""
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
EV = Path(__file__).resolve().parents[1] / "evidence"
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
p = pd.read_csv(ROOT / "data/processed/market_panel.csv", parse_dates=["Date"])
nse = pd.read_csv(EV / "nse_vs_yahoo_all_universe_rows.csv", parse_dates=["date"])
EVENTS = [
 ("ITC","2016-07-01","bonus 1:2 (Yahoo split 1.5)"),("ICICIBANK","2017-06-20","bonus 1:10 (Yahoo split 1.1)"),
 ("LT","2017-07-13","bonus 1:2 (Yahoo split 1.5)"),("RELIANCE","2017-09-07","bonus 1:1 (Yahoo split 2.0)"),
 ("TCS","2018-05-31","bonus 1:1 (Yahoo split 2.0)"),("INFY","2018-09-04","bonus 1:1 (Yahoo split 2.0)"),
 ("BHARTIARTL","2019-04-23","rights 19:67 @220"),("HDFCBANK","2019-09-19","face-value split 2->1 (Yahoo split 2.0)"),
 ("RELIANCE","2020-05-13","rights 1:15 @1257 partly paid"),("BHARTIARTL","2021-09-27","rights 1:14 @535"),
 ("RELIANCE","2023-07-20","demerger Jio Financial"),("RELIANCE","2024-10-28","bonus 1:1"),
 ("ITC","2025-01-06","demerger ITC Hotels 1:10"),("HDFCBANK","2025-08-26","bonus 1:1"),
 ("HINDUNILVR","2025-12-05","demerger Kwality Wall's 1:1"),
]
rows = []
for sym, d, desc in EVENTS:
    g = p[p.Ticker == sym + ".NS"].sort_values("Date").reset_index(drop=True)
    g["close_ret"] = g.Close.pct_change(); g["adj_ret"] = g["Adj Close"].pct_change()
    g["adj_over_close"] = g["Adj Close"] / g.Close
    g["label_logret_t1"] = np.log(g["Adj Close"].shift(-1) / g["Adj Close"])
    i = g.index[g.Date == pd.Timestamp(d)]
    if len(i) == 0: print("EVENT DATE NOT IN PANEL", sym, d); continue
    i = i[0]
    w = g.iloc[i-3:i+4].copy(); w["rel"] = range(-3, 4); w["symbol"] = sym; w["event"] = desc; w["event_date"] = d
    w = w.merge(nse[nse.symbol == sym][["date","nse_close","nse_prev_close"]], left_on="Date", right_on="date", how="left")
    w["nse_raw_ret"] = w.nse_close / w.nse_prev_close - 1
    rows.append(w)
    r = g.iloc[i]
    print(f"\n{sym} {d} {desc}: Yahoo close_ret on ex-date={r.close_ret:+.4%} adj_ret={r.adj_ret:+.4%} | label on prior session (crosses event)={g.iloc[i-1].label_logret_t1:+.5f} | Dividends={r.Dividends} Splits={r['Stock Splits']}")
    print(w[["rel","Date","Open","Close","Adj Close","Volume","Dividends","Stock Splits","close_ret","adj_ret","adj_over_close","nse_close","nse_raw_ret"]].round(5).to_string(index=False))
allw = pd.concat(rows)
allw.drop(columns=["date"]).to_csv(EV / "yahoo_event_windows.csv", index=False)

print("\n\nLARGE MOVES NEEDING EXPLANATION")
for sym, d in [("ITC","2026-01-01"),("RELIANCE","2026-11-02"),("ITC","2020-02-03"),("LT","2024-06-04")]:
    g = p[p.Ticker == sym + ".NS"].sort_values("Date").reset_index(drop=True); g["close_ret"] = g.Close.pct_change()
    i = g.index[g.Date == pd.Timestamp(d)][0]
    print(sym, d); print(g.iloc[i-2:i+3][["Date","Open","High","Low","Close","Adj Close","Volume","Dividends","Stock Splits","close_ret"]].round(4).to_string(index=False))

print("\n\nPHANTOM / STALE BAR DETAIL")
for d in ["2025-03-17","2025-03-18","2025-03-19","2026-01-14","2026-01-15","2026-01-16"]:
    print(d); print(p[p.Date == d][["Ticker","Open","High","Low","Close","Volume"]].round(2).to_string(index=False))

print("\n\nLAST ROWS OF PANEL / FRESHNESS")
print(p[p.Ticker.isin(["RELIANCE.NS","^NSEI"])].groupby("Ticker").tail(4)[["Date","Ticker","Close","Volume"]].to_string(index=False))
print("\nSpecial-session presence (date -> n tickers):")
for d in ["2016-10-30","2017-10-19","2018-11-07","2019-10-27","2020-02-01","2020-11-14","2021-11-04","2022-10-24","2023-11-12","2024-01-20","2024-03-02","2024-05-18","2024-11-01","2025-02-01","2025-10-21","2026-02-01","2026-11-08","2026-11-10"]:
    print(" ", d, pd.Timestamp(d).day_name()[:3], int((p.Date == d).sum()))
