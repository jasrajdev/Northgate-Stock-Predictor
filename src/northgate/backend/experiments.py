"""Saved results of Experiment 01 (Kaggle walk-forward validation), transcribed from the notebook."""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
EXP01 = ROOT / "reports" / "experiments" / "exp01_kaggle_walk_forward"
NAIVE = "Naive_Last_Adjusted_Close"
ALWAYS_UP = "Always_Up_Direction_Baseline"
BASELINES = [NAIVE, ALWAYS_UP]
FAMILY = {"Ridge": "Classical", "RandomForest": "Classical", "SVR_RBF": "Classical", "XGBoost": "Classical",
          "LSTM": "Deep", "GRU": "Deep", "BiLSTM": "Deep", "Transformer": "Deep"}


def available() -> bool:
    return (EXP01 / "model_summary.csv").exists() and (EXP01 / "fold_model_summary.csv").exists()


@lru_cache(maxsize=1)
def load() -> dict:
    if not available():
        raise FileNotFoundError(f"{EXP01.relative_to(ROOT)} is missing. Run scripts/extract_exp01_notebook_tables.py.")
    read_json = lambda n: json.loads((EXP01 / n).read_text()) if (EXP01 / n).exists() else {}
    return {"summary": pd.read_csv(EXP01 / "model_summary.csv"), "folds": pd.read_csv(EXP01 / "fold_model_summary.csv"),
            "report": read_json("walk_forward_report.json"), "provenance": read_json("PROVENANCE.json")}


def overall_vs_baselines() -> pd.DataFrame:
    """Each trained model against the naive price forecast and the always-up direction rule."""
    s = load()["summary"].set_index("model")
    naive_mae, up_da = s.loc[NAIVE, "mae"], s.loc[ALWAYS_UP, "directional_accuracy"]
    m = s.drop(index=BASELINES).copy()
    m["family"] = m.index.map(FAMILY)
    m["mae_vs_naive_pct"] = (m["mae"] / naive_mae - 1) * 100          # positive = worse than naive
    m["direction_vs_always_up_pp"] = (m["directional_accuracy"] - up_da) * 100
    return m.sort_values("mae_vs_naive_pct")


def folds_vs_baselines() -> pd.DataFrame:
    f = load()["folds"]
    naive = f[f.model == NAIVE].set_index("fold")["mae"]
    up = f[f.model == ALWAYS_UP].set_index("fold")["directional_accuracy"]
    m = f[~f.model.isin(BASELINES)].copy()
    m["mae_vs_naive_pct"] = (m["mae"] / m["fold"].map(naive) - 1) * 100
    m["direction_vs_always_up_pp"] = (m["directional_accuracy"] - m["fold"].map(up)) * 100
    return m
