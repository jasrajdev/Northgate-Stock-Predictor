"""Central paths, universe and evaluation boundaries. No values are hidden in other modules."""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
MODELS = ROOT / "models"
ARTIFACTS = ROOT / "artifacts" / "kaggle"
REPORTS = ROOT / "reports"
BENCHMARK = "^NSEI"
# Agreed chronological boundaries (DECISIONS.md 2026-11-13; dates of the local Mac build).
TRAIN_TARGET_END = pd.Timestamp("2023-12-31")
VALIDATION_TARGET_END = pd.Timestamp("2026-05-08")
IST_CLOSE = (15, 30)


@lru_cache(maxsize=1)
def universe() -> dict:
    return json.loads((ROOT / "config" / "northgate_universe.json").read_text())


@lru_cache(maxsize=1)
def recommendation() -> dict:
    return json.loads((ROOT / "config" / "recommendation.json").read_text())
