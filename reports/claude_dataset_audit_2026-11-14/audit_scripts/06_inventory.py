"""READ-ONLY inventory of every dataset-like file.

Usage:
  python 06_inventory.py ORIGIN_CHECKOUT [--external-dir DIR] [--extra-file FILE ...]

ORIGIN_CHECKOUT  directory holding an export of origin/main (e.g. from `git archive`).
--external-dir   optional folder outside the repo to list (CPI workbooks, notebook, papers).
--extra-file     optional individual files outside the repo to list (repeatable).
No machine-specific location is assumed: if the optional arguments are omitted,
only the repository and ORIGIN_CHECKOUT are inventoried.
"""
import sys, json, hashlib, subprocess, csv, io, zipfile, argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
ROOT = Path(__file__).resolve().parents[3]; OUT = Path(__file__).resolve().parents[1]
_ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
_ap.add_argument("origin_checkout", type=Path)
_ap.add_argument("--external-dir", type=Path, default=None)
_ap.add_argument("--extra-file", type=Path, action="append", default=[])
_args = _ap.parse_args()
ORI = _args.origin_checkout; EXT = _args.external_dir; EXTRA_FILES = _args.extra_file
# Notes for known files outside the repo, keyed by file name (not by location).
EXTRA_NOTES = {
    "cpi_33.xlsx": "MoSPI CPI base-2024 granular extract (documented as 31,460 rows; row count NOT re-verified here)",
    "f773513d5994f93126d19f185d32a851.docx": "Original PRD v1.0 (Northgate Quantitative Research capstone brief) - governing scope; NOT in repo",
}
tracked_local = set(subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n"))
tracked_origin = set(subprocess.run(["git", "ls-tree", "-r", "--name-only", "origin/main"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n"))
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def describe_csv(p):
    d = {}
    try:
        head = pd.read_csv(p, nrows=5, skipinitialspace=True)
        cols = [c.strip() for c in head.columns]; d["columns"] = "|".join(cols); d["n_columns"] = len(cols)
        with open(p, "rb") as f: d["rows"] = max(sum(1 for _ in f) - 1, 0)
        datecol = next((c for c in ["Date", "DATE1", "TIMESTAMP", "reference_month", "observation_date"] if c in cols), None)
        tick = next((c for c in ["Ticker", "SYMBOL"] if c in cols), None)
        use = [c for c in [datecol, tick, "target_date_t1"] if c and c in cols]
        if use and d["rows"] < 400000:
            x = pd.read_csv(p, usecols=lambda c: c.strip() in use, skipinitialspace=True, on_bad_lines="skip"); x.columns = [c.strip() for c in x.columns]
            if datecol:
                dt = pd.to_datetime(x[datecol].astype(str).str.strip(), errors="coerce", format="mixed"); d["date_min"] = str(dt.min())[:10]; d["date_max"] = str(dt.max())[:10]
            if tick: d["n_tickers"] = int(x[tick].nunique()); d["tickers"] = ";".join(sorted(x[tick].astype(str).str.strip().unique())[:15]) if x[tick].nunique() <= 15 else f"{x[tick].nunique()} symbols (full exchange file)"
            if "target_date_t1" in x: d["target_date_min"] = str(x.target_date_t1.min())[:10]; d["target_date_max"] = str(x.target_date_t1.max())[:10]
    except Exception as e:
        d["parse_note"] = f"{type(e).__name__}: {str(e)[:120]}"
    return d
META = {  # path prefix -> (source, validation status, rights note)
 "data/raw/yahoo/": ("Yahoo Finance via yfinance 1.8.0, retrieved 2026-11-11T19:53Z (auto_adjust=False, actions=True)", "VERIFIED: identical to market_panel for all rows; price basis = back-adjusted (see CORPORATE_ACTION_AUDIT.md)", "Yahoo terms: personal use; do not redistribute; keep out of Git"),
 "data/raw/nse_bhavcopy/": ("NSE archives (nsearchives.nseindia.com), user-downloaded 2026-11-14", "VERIFIED in this audit: SHA-256 matches documented value, schema parsed, one EQ row per target symbol/date", "NSE website terms restrict automated collection/redistribution; keep local, do not commit"),
 "data/processed/market_panel.csv": ("Concatenation of data/raw/yahoo by scripts/download_market_data.py", "VERIFIED reproducible; contains 10 phantom rows (2026-01-15) and 9 stale rows (2025-03-18)", "Derived from Yahoo; do not redistribute"),
 "data/processed/feature_panel.csv": ("scripts/build_features.py (Mac pipeline, 24 features)", "VERIFIED bit-identical on recomputation; includes look-ahead feature adj_close_vs_close and rupee-level features", "Derived from Yahoo"),
 "data/processed/modeling_dataset_next_day.csv": ("scripts/build_next_day_dataset.py", "VERIFIED bit-identical on recomputation; all reported checks reproduce", "Derived from Yahoo"),
 "data/processed/splits/": ("scripts/create_chronological_splits.py", "VERIFIED identical to recomputed partitions; NOT the dataset used by the Kaggle experiment", "Derived from Yahoo; test.csv SEALED (opened here for keys/dates/equality only)"),
 "reports/data_quality/": ("Pipeline QA reports written by the scripts", "VERIFIED consistent with data", "No restriction"),
}
rows = []
def add(p, location, relname, git_status, extra=None):
    st = p.stat(); r = dict(path=relname, location=location, file_type=p.suffix.lstrip(".") or "none", size_bytes=st.st_size,
                            modified_local=datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"), sha256=sha(p), git_status=git_status)
    if p.suffix == ".csv": r.update(describe_csv(p))
    if p.suffix == ".zip":
        z = zipfile.ZipFile(p); n = z.namelist()[0]; t = z.read(n).decode("utf-8-sig"); hdr = [c for c in t.split("\n", 1)[0].strip().split(",") if c]
        r.update(columns="|".join(hdr), n_columns=len(hdr), rows=t.count("\n") - 1, date_min=p.name[2:11], date_max=p.name[2:11], tickers="full exchange file")
    if p.suffix == ".json":
        try: r["columns"] = "keys: " + "|".join(list(json.loads(p.read_text()).keys())[:12])
        except Exception: pass
    for k, v in META.items():
        if relname.startswith(k): r.update(source=v[0], validation_status=v[1], rights_note=v[2])
    if extra: r.update(extra)
    rows.append(r)
for sub in ["data", "reports/data_quality", "notebooks", "models"]:
    base = ROOT / sub
    if not base.exists(): continue
    for p in sorted(base.rglob("*")):
        if p.is_file() and p.name not in (".DS_Store", ".gitkeep"):
            rel = str(p.relative_to(ROOT)); add(p, "local working tree", rel, "tracked" if rel in tracked_local else "untracked (not in Git, not ignored)")
add(ROOT / "download_nse_bhavcopy.py", "local working tree", "download_nse_bhavcopy.py", "untracked script at repo root", dict(source="User-written downloader for 5 legacy bhavcopy ZIPs", validation_status="Inspected; writes only to data/raw/nse_bhavcopy", rights_note="Automated NSE access - see rights finding"))
for p in sorted((ORI / "data/external").glob("*")):
    rel = "data/external/" + p.name
    add(p, "GitHub origin/main only (MISSING from local working tree)", rel, "tracked on origin/main; local clone 319 commits behind",
        dict(source="MoSPI CPI press-release annexure workbooks (2012 base), extracted by repo scripts", validation_status="VERIFIED: rebuilt from the 18 local workbooks, 3,990 rows identical" if "vintages_part" in p.name or "snapshots" in p.name else "VERIFIED against workbooks/panel calendar" , rights_note="Government of India open data; cite MoSPI"))
for p in (sorted(EXT.glob("*")) if EXT else []):
    if p.is_file() and p.name != ".DS_Store":
        kind = "MoSPI CPI annexure workbook (original source for data/external CPI files)" if p.suffix == ".xlsx" else ("Kaggle notebook holding the ONLY copy of the walk-forward code and printed results" if p.suffix == ".ipynb" else "Reference document (paper / press release)")
        add(p, f"outside repo: {EXT.name}/", p.name, "not in any Git repository", dict(source=kind, validation_status="Inspected" if p.suffix in (".xlsx", ".ipynb") else "Listed only", rights_note="MoSPI open data" if p.suffix == ".xlsx" else ("Own work" if p.suffix == ".ipynb" else "Publisher copyright - do not commit")))
for p, note in [(f, EXTRA_NOTES.get(f.name, "File outside the repository (no note recorded)")) for f in EXTRA_FILES]:
    if p.exists(): add(p, f"outside repo: {p.parent.name}/", p.name, "not in any Git repository", dict(source=note, validation_status="Text extracted and read in full" if p.suffix == ".docx" else "Listed and hashed only", rights_note="Project brief / MoSPI open data"))
MISSING = [("data/processed/market_panel_with_cpi.csv", "CPI as-of merge output; documented at /mnt/data (chat sandbox) only. Reproduced in this audit to scratch: 29,484 rows, 22 cols, 6,115 matched"),
 ("reports/validation/* (Kaggle)", "Experiment-01 single-split results; exist only on Kaggle /kaggle/working and as printed tables inside the notebook"),
 ("reports/walk_forward/* (Kaggle)", "fold_results.csv (500 rows), model_summary.csv, fold_model_summary.csv, walk_forward_report.json, dry_run_audit.json - Kaggle only"),
 ("models/walk_forward/*.pt, models/deep/*.pt (Kaggle)", "20 walk-forward checkpoints + 4 single-split checkpoints - Kaggle only; not downloaded"),
 ("scripts/run_walk_forward.py", "30 KB script written inside the notebook (cell 70); not in GitHub or local repo"),
 ("data/processed/macro_context/*", "Output of scripts/download_macro_context.py - script never run; no file anywhere"),
 ("data/processed/market_context/*", "Output of scripts/download_market_context.py - script never run; no file anywhere"),
 ("data/raw/cpi_annexures/", "Expected input dir of build_cpi_vintages.py; the 18 workbooks actually live outside the repo"),
 ("IN-FINews (Zenodo 16991843)", "Referenced news corpus (3,348 articles, Feb-Aug 2025); no local copy found - size/dates remain documentation claims"),
 ("any news / sentiment / RBI / VIX / TRI / FII-DII / fundamentals file", "None acquired; research notes only")]
for path, note in MISSING:
    rows.append(dict(path=path, location="EXPECTED BUT ABSENT", file_type="-", git_status="absent locally and on GitHub", validation_status="MISSING", source=note))
cols = ["path", "location", "file_type", "size_bytes", "rows", "n_columns", "columns", "date_min", "date_max", "target_date_min", "target_date_max", "n_tickers", "tickers", "source", "sha256", "validation_status", "rights_note", "git_status", "modified_local", "parse_note"]
df = pd.DataFrame(rows).reindex(columns=cols)
df.to_csv(OUT / "DATASET_INVENTORY.csv", index=False)
(OUT / "DATASET_INVENTORY.json").write_text(json.dumps({"generated": datetime.now().astimezone().isoformat(), "n_entries": len(df), "entries": json.loads(df.to_json(orient="records"))}, indent=1))
print(len(df), "entries;", int(df.size_bytes.fillna(0).sum() / 1e6), "MB")
print(df[["path", "size_bytes", "rows", "n_columns", "date_min", "date_max", "n_tickers", "git_status"]].to_string(max_colwidth=58))
