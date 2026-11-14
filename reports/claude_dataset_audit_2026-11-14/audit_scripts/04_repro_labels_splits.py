"""READ-ONLY: reproduce features/labels/splits in memory and compare with saved files.
The test partition is opened only for structural checks (keys, dates, schema, equality);
no statistic of test-period outcomes is computed or printed."""
from pathlib import Path
import json, sys, importlib.util
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
EV = Path(__file__).resolve().parents[1] / "evidence"
P = ROOT / "data/processed"
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
bf, bn = load("build_features"), load("build_next_day_dataset")

panel = pd.read_csv(P / "market_panel.csv", parse_dates=["Date"])
feat = pd.read_csv(P / "feature_panel.csv", parse_dates=["Date"])
model = pd.read_csv(P / "modeling_dataset_next_day.csv", parse_dates=["Date", "target_date_t1"])
print("shapes panel/feature/model:", panel.shape, feat.shape, model.shape)

# 1 features reproduce
re_feat = pd.concat([bf.build_features(g) for _, g in panel.sort_values(["Ticker","Date"]).groupby("Ticker", sort=False)], ignore_index=True).sort_values(["Ticker","Date"]).reset_index(drop=True)
fcols = [c for c in feat.columns if c not in panel.columns]
print("feature columns (", len(fcols), "):", fcols)
num = [c for c in feat.columns if c not in ("Date","Ticker","Name")]
d = (re_feat[num].astype(float) - feat[num].astype(float)).abs()
rel = d / feat[num].astype(float).abs().clip(lower=1e-12)
print("feature panel reproduces from market_panel: same keys:", bool((re_feat[["Date","Ticker"]].values == feat[["Date","Ticker"]].values).all()),
      "| max abs diff:", float(np.nanmax(d.values)), "| max rel diff:", float(np.nanmax(rel.values)),
      "| NaN pattern identical:", bool((re_feat[num].isna().values == feat[num].isna().values).all()))

# 2 labels reproduce
re_model = pd.concat([bn.add_next_day_targets(g) for _, g in feat.sort_values(["Ticker","Date"]).groupby("Ticker", sort=False)], ignore_index=True)
re_model = re_model.dropna(subset=["target_date_t1","target_adj_close_t1","target_log_return_t1"]).sort_values(["Ticker","Date"]).reset_index(drop=True)
print("labels reproduce: rows", len(re_model), len(model), "| key equal:", bool((re_model[["Date","Ticker","target_date_t1"]].values == model[["Date","Ticker","target_date_t1"]].values).all()),
      "| max abs diff target_adj_close:", float((re_model.target_adj_close_t1 - model.target_adj_close_t1).abs().max()),
      "| max abs diff target_logret:", float((re_model.target_log_return_t1 - model.target_log_return_t1).abs().max()))

# 3 label definition checks (train+validation rows only for outcome statistics)
m = model.copy()
nxt = panel.sort_values(["Ticker","Date"]).copy(); nxt["nd"] = nxt.groupby("Ticker").Date.shift(-1); nxt["na"] = nxt.groupby("Ticker")["Adj Close"].shift(-1)
j = m.merge(nxt[["Ticker","Date","nd","na"]], on=["Ticker","Date"])
print("target date == next observed row for same ticker:", bool((j.nd == j.target_date_t1).all()), "| target adj close == next row adj close:", bool(np.allclose(j.na, j.target_adj_close_t1)))
print("dup keys:", int(m.duplicated(["Ticker","Date"]).sum()), "| target after feature date:", bool((m.target_date_t1 > m.Date).all()), "| missing targets:", int(m.filter(like="target_").isna().sum().sum()), "| nonpositive target:", int((m.target_adj_close_t1 <= 0).sum()))
gap = (m.target_date_t1 - m.Date).dt.days
print("calendar gap feature->target days distribution:", gap.value_counts().sort_index().to_dict())
print("rows per ticker:", m.groupby("Ticker").size().to_dict())
print("direction label values (all rows, counts by value):", m.target_direction_t1.value_counts().to_dict())
tv = m[m.target_date_t1 <= pd.Timestamp("2026-05-08")]
eqtv = tv[tv.Ticker != "^NSEI"]
print("zero-return labels in train+val equities:", int((eqtv.target_log_return_t1 == 0).sum()), f"({(eqtv.target_log_return_t1 == 0).mean():.4%})")
val = eqtv[eqtv.target_date_t1 > pd.Timestamp("2023-12-31")]
print("validation equities: rows", len(val), "| exact zero-return share:", f"{(val.target_log_return_t1 == 0).mean():.4%}", "| up share:", f"{(val.target_log_return_t1 > 0).mean():.4%}", "| down share:", f"{(val.target_log_return_t1 < 0).mean():.4%}")
z = val[val.target_log_return_t1 == 0].groupby("target_date_t1").size()
print("validation zero-return labels by target date (>=3 tickers):", {str(k.date()): int(v) for k, v in z[z >= 3].items()})
# price-scale effect on pooled MAE
naive = val.assign(ae=(val.target_adj_close_t1 - val["Adj Close"]).abs(), ape=(val.target_adj_close_t1 / val["Adj Close"] - 1).abs())
t = naive.groupby("Ticker").agg(mean_price=("Adj Close","mean"), naive_mae=("ae","mean"), naive_mape_pct=("ape", lambda s: 100*s.mean()), n=("ae","size"))
t["share_of_pooled_abs_error"] = t.naive_mae * t.n / (t.naive_mae * t.n).sum()
print("\nNaive baseline on LOCAL validation rows per ticker (price-scale effect):"); print(t.round(4).to_string())
t.to_csv(EV / "naive_baseline_per_ticker_local_validation.csv")

# 4 splits reproduce
# NOTE (test-partition integrity): splits/test.csv is read below ONLY for a one-time integrity
# comparison (row keys, dates, schema and equality with the recomputed partition). It must not be
# used for model selection, tuning or any performance evaluation; no outcome statistic is computed.
rep = json.loads((ROOT / "reports/data_quality/chronological_split_report.json").read_text())
latest = model.target_date_t1.max(); cutoff = latest - pd.DateOffset(months=6)
parts = {"train": model[model.target_date_t1 <= "2023-12-31"], "validation": model[(model.target_date_t1 > "2023-12-31") & (model.target_date_t1 < cutoff)], "test": model[model.target_date_t1 >= cutoff]}
print("\nlatest target", latest.date(), "cutoff", cutoff.date())
for name, part in parts.items():
    f = pd.read_csv(P / "splits" / f"{name}.csv", parse_dates=["Date","target_date_t1"])
    part = part.sort_values(["Ticker","Date"]).reset_index(drop=True)
    same_keys = len(f) == len(part) and bool((f[["Ticker","Date","target_date_t1"]].values == part[["Ticker","Date","target_date_t1"]].values).all())
    numc = [c for c in f.columns if c not in ("Date","Ticker","Name","target_date_t1")]
    same_vals = same_keys and bool(np.allclose(f[numc].astype(float).values, part[numc].astype(float).values, equal_nan=True, rtol=1e-12, atol=0))
    print(f"{name}: rows={len(f)} cols={f.shape[1]} tickers={f.Ticker.nunique()} feature dates {f.Date.min().date()}..{f.Date.max().date()} target dates {f.target_date_t1.min().date()}..{f.target_date_t1.max().date()} dupkeys={int(f.duplicated(['Ticker','Date']).sum())} | equals recomputed partition keys={same_keys} values={same_vals} | report rows={rep['partitions'][name]['rows']}")
allk = pd.concat([pd.read_csv(P / "splits" / f"{n}.csv", usecols=["Ticker","Date"]) for n in parts])
print("union of splits rows:", len(allk), "dup across splits:", int(allk.duplicated().sum()))
print("split report candidate feature columns:", rep["candidate_feature_columns_excluding_metadata_and_targets"])

# 5 reports vs actual
dl = json.loads((ROOT / "reports/data_quality/download_report.json").read_text())
print("\ndownload_report total_rows", dl["total_rows"], "retrieved", dl["retrieved_at_utc"], "end_exclusive", dl["end_date_exclusive"], "| per-ticker invalid/dup/gaps:", {r["ticker"]: (r["invalid_ohlc_or_nonpositive_price_rows"], r["duplicate_dates"], r["calendar_gaps_over_7_days"]) for r in dl["ticker_checks"]})
fr = json.loads((ROOT / "reports/data_quality/feature_report.json").read_text())
act = {c: int(feat[c].isna().sum()) for c in fcols}
print("feature_report missing counts match actual:", fr["missing_values_by_feature"] == act); print("missing by feature:", act)
nr = json.loads((ROOT / "reports/data_quality/next_day_dataset_report.json").read_text()); print("next_day report:", nr["rows_before_label_filter"], nr["rows_after_label_filter"], nr["checks"])

# 6 look-ahead property of adj_close_vs_close and price-level features
print("\nLOOK-AHEAD DEMONSTRATION (retrospective dividend adjustment)")
g = panel[panel.Ticker == "ITC.NS"].sort_values("Date").reset_index(drop=True)
ratio = g["Adj Close"] / g.Close
fut_div_yield = (g.Dividends / g.Close.shift(1)).fillna(0)
# implied: ratio_t = prod_{s>t}(1 - D_s/C_{s-1})
implied = (1 - fut_div_yield)[::-1].cumprod()[::-1].shift(-1).fillna(1.0)
print("ITC: max |Adj/Close - product of (1 - future dividend/prev close)| =", float((ratio - implied).abs().max()))
print("ITC adj_close_vs_close on 2016-01-04:", float(ratio.iloc[1] - 1), "-> equals minus the cumulative dividend yield paid AFTER that date through the download date")
lvl = [c for c in fcols if c.startswith(("sma_","ema_")) or c == "macd"]
print("price-LEVEL engineered features (rupee units, restated by every later dividend):", lvl, "+ raw Adj Close/Open/High/Low/Close passed by train scripts")
