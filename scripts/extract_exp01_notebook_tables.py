"""Transcribe Experiment-01 result tables from the saved outputs of the Kaggle notebook.

This does NOT run the notebook or any model. It copies numbers that the notebook printed
(model_summary.csv, fold_model_summary.csv and walk_forward_report.json as displayed in
cells 73 and 75) into small files the dashboard can read. The original Kaggle files were
not recovered; these transcripts are the only machine-readable copy.

Usage: python scripts/extract_exp01_notebook_tables.py PATH/TO/notebookf887dc542c.ipynb
"""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "experiments" / "exp01_kaggle_walk_forward"
METRICS = ["mae", "rmse", "mape_pct", "r2", "directional_accuracy"]


def cell_text(nb, i):
    return "\n".join("".join(o.get("text", "")) for o in nb["cells"][i].get("outputs", []) if "text" in o)


def main(path: Path) -> None:
    raw = path.read_bytes()
    nb = json.loads(raw)
    text = cell_text(nb, 73)
    overall, folds = text.split("FOLD-BY-FOLD COMPARISON")
    rows = [ln.split() for ln in overall.splitlines() if re.match(r"\s*[A-Za-z_]+\s+\d", ln)]
    summary = pd.DataFrame(rows, columns=["model"] + METRICS)
    rows = [ln.split() for ln in folds.splitlines() if re.match(r"\s*20\d\d-\S+\s+[A-Za-z_]+\s+\d", ln)]
    fold = pd.DataFrame(rows, columns=["fold", "model"] + METRICS)
    for df in (summary, fold):
        df[METRICS] = df[METRICS].astype(float)
    assert len(summary) == 10 and len(fold) == 50, (len(summary), len(fold))
    t75 = cell_text(nb, 75)
    report = json.loads(t75[t75.index("{", t75.index("walk_forward_report.json")):t75.rindex("}") + 1])
    OUT.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT / "model_summary.csv", index=False)
    fold.to_csv(OUT / "fold_model_summary.csv", index=False)
    (OUT / "walk_forward_report.json").write_text(json.dumps(report, indent=2))
    (OUT / "PROVENANCE.json").write_text(json.dumps({
        "source": "Printed outputs of Kaggle notebook cells 73 and 75 (0-based)",
        "notebook_file": path.name,
        "notebook_sha256": hashlib.sha256(raw).hexdigest(),
        "status": "TRANSCRIPT of validation results. Original Kaggle CSV/JSON files and all model checkpoints were not recovered.",
        "partition": "validation only (five expanding folds); test partition not evaluated",
        "not_available": ["fold_results.csv (per ticker x fold rows)", "20 walk-forward checkpoints", "Kaggle-built dataset"],
    }, indent=2))
    print("wrote", OUT, "| models", len(summary), "| fold rows", len(fold), "| elapsed_seconds", report.get("elapsed_seconds"))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
