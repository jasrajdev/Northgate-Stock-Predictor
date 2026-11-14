"""READ-ONLY CPI checks. argv[1]=origin/main checkout, argv[2]=scratch rebuild dir."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
G = Path(sys.argv[1]) / "data/external"; RB = Path(sys.argv[2])
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
ev = pd.read_csv(G / "cpi_mospi_2012base_release_events_2024-07_to_2025-12.csv", dtype=str)
m1 = pd.read_csv(G / "cpi_mospi_2012_release_availability_map_2024-07_to_2025-12.csv", dtype=str).fillna("")
m2 = pd.read_csv(G / "cpi_release_availability_map_2012base.csv", dtype=str).fillna("")
import io, re
def read_repaired(path):
    """Committed part files contain fused records (missing newline). Repair IN MEMORY only; report count."""
    text = path.read_text()
    fixed, n = re.subn(r"(never available on release date)(20\d\d-\d\d,)", r"\1\n\2", text)
    print(f"  {path.name}: fused records repaired in memory = {n}")
    return pd.read_csv(io.StringIO(fixed))
parts = pd.concat([read_repaired(G / f) for f in ["cpi_mospi_2012base_point_in_time_vintages_part1_2024-11_to_2025-05.csv", "cpi_mospi_2012base_point_in_time_vintages_part2_2025-06_to_2025-12.csv"]], ignore_index=True)
snap = pd.read_csv(G / "cpi_mospi_2012_historical_table_snapshots_2024-07_to_2025-12.csv")
vint = pd.read_csv(G / "cpi_mospi_2012_release_vintages_2024-07_to_2025-12.csv")
rb = pd.read_csv(RB / "cpi_2012base_point_in_time_vintages.csv")
print("rows: events", len(ev), "map1", len(m1), "map2", len(m2), "PIT parts", len(parts), "snapshots", len(snap), "headline vintages", len(vint), "rebuilt", len(rb))
key = ["release_workbook_month", "reference_month", "series"]
a = parts.sort_values(key).reset_index(drop=True); b = rb.sort_values(key).reset_index(drop=True)
print("rebuilt vs committed PIT parts: same keys", bool((a[key].values == b[key].values).all()), "| values equal", bool(np.allclose(a.value, b.value, equal_nan=True)),
      "| release dates equal", bool((a.actual_release_date.values == b.actual_release_date.values).all()), "| sessions equal", bool((a.available_from_session.values == b.next_nse_session.values).all()))
s = snap.sort_values(key).reset_index(drop=True)
print("snapshot CSV vs PIT parts: same keys", bool((s[key].values == a[key].values).all()), "| values equal", bool(np.allclose(s.value, a.value, equal_nan=True)), "| dup keys", int(parts.duplicated(key).sum()))
dm = [(c, int((m1[c] != m2[c]).sum())) for c in m1.columns]
print("two availability maps: column-wise differing rows:", dm)
print("  differing source_url rows:", m1.loc[m1.source_url != m2.source_url, ["release_workbook_month", "source_url"]].values.tolist(), "vs", m2.loc[m1.source_url != m2.source_url, "source_url"].tolist())
print("events vs map1: release date equal", bool((ev.actual_release_date.values == m1.actual_release_date.values).all()), "| session equal", bool((ev.next_nse_session.values == m1.next_nse_session.values).all()), "| source_url equal rows", int((ev.source_url.values == m1.source_url.values).sum()), "/18")

# next_nse_session == first observed equity session strictly after release date in the LOCAL panel
panel = pd.read_csv(ROOT / "data/processed/market_panel.csv", parse_dates=["Date"])
eqd = np.array(sorted(panel[panel.Ticker != "^NSEI"].Date.unique())); idxd = np.array(sorted(panel[panel.Ticker == "^NSEI"].Date.unique()))
chk = []
for _, r in ev.iterrows():
    rel = pd.Timestamp(r.actual_release_date)
    nxt = pd.Timestamp(eqd[eqd > rel][0]); chk.append((r.reference_month, r.actual_release_date, rel.day_name()[:3], r.embargo_time_ist, r.next_nse_session, str(nxt.date()), str(nxt.date()) == r.next_nse_session, bool(rel in eqd)))
c = pd.DataFrame(chk, columns=["ref_month", "release", "dow", "time", "next_session_in_file", "first_panel_session_after", "match", "release_day_is_session"])
print(c.to_string(index=False))
# events vs cumulative snapshot of the same release
x = ev.merge(parts[parts.series == "index"][["release_workbook_month", "reference_month", "value", "provisional_marker"]], on=["release_workbook_month", "reference_month"], how="left")
y = ev.merge(parts[parts.series == "inflation"][["release_workbook_month", "reference_month", "value"]], on=["release_workbook_month", "reference_month"], how="left")
print("event index == same-release snapshot value (14 releases with snapshots):", int((x.value.notna()).sum()), "comparable;", int((x.value.dropna().values == x.loc[x.value.notna(), "combined_cpi_index_2012"].astype(float).values).sum()), "equal | inflation diffs max abs:", float((y.value - y.combined_cpi_yoy_inflation_pct.astype(float)).abs().max()))
hv = vint[(vint.sector == "combined") & (vint.vintage_status == "provisional")][["reference_month", "index_2012", "inflation_yoy_pct"]].astype({"reference_month": str})
z = ev.merge(hv, on="reference_month", how="left")
print("event vs Annex-I provisional headline (18): index equal", int((z.index_2012 == z.combined_cpi_index_2012.astype(float)).sum()), "| inflation equal", int(np.isclose(z.inflation_yoy_pct, z.combined_cpi_yoy_inflation_pct.astype(float)).sum()))
# revisions: provisional -> final across vintages
idx = parts[parts.series == "index"].pivot(index="reference_month", columns="release_workbook_month", values="value")
rev = idx.loc["2024-11":].apply(lambda r: r.dropna().iloc[[0, -1]].tolist() + [r.dropna().nunique()], axis=1, result_type="expand"); rev.columns = ["first_published", "latest_published", "n_distinct_values"]
print("combined index, first vs latest vintage (months with >1 distinct value):"); print(rev[rev.n_distinct_values > 1].to_string())
older = idx.loc[:"2024-10"]; print("pre-Nov-2024 reference months with any cross-vintage difference:", int((older.nunique(axis=1) > 1).sum()), "of", len(older))
# merged artefact
mg = pd.read_csv(RB / "market_panel_with_cpi.csv", parse_dates=["Date"])
mt = mg[mg.next_nse_session.notna()]
print("\nmerged rows", len(mg), "cols", mg.shape[1], "matched", len(mt), "first matched date", mt.Date.min().date(), "max cpi age days", int(mg.cpi_age_calendar_days.max()), "| matched rows per ticker:", mt.groupby("Ticker").size().to_dict())
print("order preserved vs panel:", bool((mg[["Date", "Ticker"]].values == panel[["Date", "Ticker"]].values).all()), "| one vintage per date:", bool((mt.groupby("Date").release_workbook_month.nunique() == 1).all()))
print("rows with CPI older than 45 days:", int((mg.cpi_age_calendar_days > 45).sum()), "| share of all panel rows with any CPI:", f"{len(mt)/len(mg):.2%}", "| train-partition rows with CPI (Date<=2023-12-28):", int((mt.Date <= '2023-12-28').sum()))
for d in ["2024-08-12", "2024-08-13", "2025-05-13", "2025-05-14", "2026-01-12", "2026-01-13", "2026-01-15"]:
    r = mg[(mg.Date == d) & (mg.Ticker == "ITC.NS")]
    print(" ", d, r.reference_month.tolist(), r.combined_cpi_index_2012.tolist())
