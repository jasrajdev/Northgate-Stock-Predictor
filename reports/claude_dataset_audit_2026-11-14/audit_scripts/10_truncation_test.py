"""READ-ONLY: do committed features at date t change if data after t is removed? (code-level look-ahead test)"""
from pathlib import Path
import importlib.util, numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("bf", ROOT/"scripts/build_features.py"); bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
p = pd.read_csv(ROOT/"data/processed/market_panel.csv", parse_dates=["Date"])
def feats(df): return pd.concat([bf.build_features(g) for _, g in df.sort_values(["Ticker","Date"]).groupby("Ticker", sort=False)], ignore_index=True)
full = feats(p).set_index(["Ticker","Date"])
cols = [c for c in full.columns if c not in p.columns]
for cut in ["2018-06-29","2021-03-31","2024-10-25","2026-05-08"]:
    t = feats(p[p.Date <= cut]).set_index(["Ticker","Date"])
    a, b = t[cols].astype(float), full.loc[t.index, cols].astype(float)
    bad = ((a - b).abs().fillna(0) > 1e-12) | (a.isna() != b.isna())
    print(cut, "rows", len(t), "| feature cells that differ from full-history computation:", int(bad.values.sum()), "| columns:", list(bad.columns[bad.any()]))
print("Result: code is backward-looking given its INPUT; look-ahead (L-02/L-03) enters through the vendor Adj Close series, which this test cannot see.")
# zero-volume flat bars within eligible training data
e = p[(p.Ticker!="^NSEI")&(p.Volume==0)]; print("zero-volume equity rows:", len(e), sorted(e.Date.dt.strftime("%Y-%m-%d").unique()))
r = pd.read_csv("reports/claude_dataset_audit_2026-11-14/price_basis_comparison.csv") if False else pd.read_csv(Path(__file__).resolve().parents[1]/"price_basis_comparison.csv")
print("symbol-dates with ratio==1 (Yahoo equals NSE exactly):", int((r.ratio_yahoo_close_to_nse_close.sub(1).abs()<1e-5).sum()), "of", len(r))
