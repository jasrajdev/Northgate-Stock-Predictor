"""Per-ticker classical regressors (same configuration as Experiment 01), persisted with joblib.

Fitting uses the TRAIN partition only (target dates <= 2023-12-31). Nothing here reads the
held-out test window: labels after the validation end are never created (features.add_labels).
"""
from __future__ import annotations
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from ..config import MODELS
from ..features import FEATURES

DIR = MODELS / "classical"
SEED = 42


def make(name: str) -> Pipeline:
    if name == "Ridge":
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler()), ("model", Ridge(alpha=10.0))])
    if name == "RandomForest":
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", RandomForestRegressor(
            n_estimators=120, min_samples_leaf=3, max_features=0.8, n_jobs=-1, random_state=SEED))])
    if name == "SVR_RBF":
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler()), ("model", SVR(C=1.0, epsilon=0.01, kernel="rbf"))])
    if name == "XGBoost":
        from xgboost import XGBRegressor
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", XGBRegressor(
            n_estimators=250, max_depth=4, learning_rate=0.04, subsample=0.85, colsample_bytree=0.85,
            objective="reg:squarederror", n_jobs=-1, tree_method="hist", device="cpu", random_state=SEED))])
    raise KeyError(name)


def path(name: str, ticker: str) -> Path:
    return DIR / name / f"{ticker.replace('^', '')}.joblib"


def save(model, name: str, ticker: str) -> None:
    p = path(name, ticker); p.parent.mkdir(parents=True, exist_ok=True); joblib.dump(model, p)


def load(name: str, ticker: str):
    p = path(name, ticker)
    return joblib.load(p) if p.exists() else None


def metadata() -> dict:
    p = DIR / "metadata.json"
    return json.loads(p.read_text()) if p.exists() else {}


def available(name: str, tickers: list[str]) -> bool:
    return all(path(name, t).exists() for t in tickers)


def predict(name: str, ticker: str, X: pd.DataFrame) -> np.ndarray:
    m = load(name, ticker)
    if m is None:
        raise FileNotFoundError(f"No persisted {name} model for {ticker}; run scripts/persist_classical_models.py")
    return m.predict(X[FEATURES].replace([np.inf, -np.inf], np.nan))
