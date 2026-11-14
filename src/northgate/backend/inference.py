"""Model registry and forecasting service.

* Classical models: persisted estimators in models/classical (scripts/persist_classical_models.py).
* Deep models: Kaggle checkpoints in artifacts/kaggle/models/deep (or models/deep), loaded with
  northgate.models.deep using the checkpoint's own architecture and preprocessing metadata.
* Selection: among models that load, the one with the lowest validation MAE in Experiment 01
  (Kaggle walk-forward, the only validation run covering all eight families on one basis).
* `validated_edge` is True only if that model's validation MAE is below the naive forecast's.
Forecasts are next-session log returns; prices are derived as price x exp(return).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
import numpy as np
import pandas as pd
from .. import config, features as F
from ..models import CLASSICAL, DEEP, classical, deep
from . import experiments, market

CKPT_DIRS = [config.ARTIFACTS / "models" / "deep", config.MODELS / "deep"]


class InferenceUnavailable(RuntimeError):
    pass


@dataclass
class ModelStatus:
    name: str
    family: str
    loaded: bool
    source: str
    detail: str
    validation_mae: float | None = None


@dataclass
class Registry:
    models: list = field(default_factory=list)
    deep_loaded: dict = field(default_factory=dict)
    selected: str | None = None
    naive_mae: float | None = None
    validated_edge: bool = False

    def table(self) -> pd.DataFrame:
        return pd.DataFrame([vars(m) for m in self.models])


@lru_cache(maxsize=1)
def feature_panel() -> pd.DataFrame:
    """v1 features for every session (no labels)."""
    return F.build(market.load_panel().drop(columns=["suspect_bar"]))


def _ckpt(name: str) -> Path | None:
    for d in CKPT_DIRS:
        p = d / f"{name.lower()}_best.pt"
        if p.exists():
            return p
    return None


@lru_cache(maxsize=1)
def registry() -> Registry:
    reg = Registry()
    wf = experiments.load()["summary"].set_index("model")["mae"] if experiments.available() else pd.Series(dtype=float)
    reg.naive_mae = float(wf.get(experiments.NAIVE, np.nan)) if len(wf) else None
    eq = market.tickers()
    for n in CLASSICAL:
        ok = classical.available(n, eq)
        reg.models.append(ModelStatus(n, "Classical", ok, "models/classical (fit on train partition)" if ok else "-",
                                      "persisted estimator per stock" if ok else "run scripts/persist_classical_models.py", wf.get(n)))
    for n in DEEP:
        p = _ckpt(n)
        if p is None:
            reg.models.append(ModelStatus(n, "Deep", False, "-", "checkpoint not present (expected artifacts/kaggle/models/deep/)", wf.get(n)))
            continue
        try:
            m = deep.load(p, expected_features=F.FEATURES)
            missing = [t for t in eq if t not in m.tickers]
            if missing:
                raise ValueError(f"ticker map lacks {missing}")
            reg.deep_loaded[n] = m
            reg.models.append(ModelStatus(n, "Deep", True, str(p.relative_to(config.ROOT)), f"seq {m.seq}, hidden {m.hidden}, {len(m.features)} features", wf.get(n)))
        except Exception as e:  # incompatible checkpoint: report, never guess
            reg.models.append(ModelStatus(n, "Deep", False, str(p.relative_to(config.ROOT)), f"failed to load: {e}", wf.get(n)))
    loaded = [m for m in reg.models if m.loaded and m.validation_mae is not None and np.isfinite(m.validation_mae)]
    if loaded:
        best = min(loaded, key=lambda m: m.validation_mae)
        reg.selected = best.name
        reg.validated_edge = bool(reg.naive_mae is not None and best.validation_mae < reg.naive_mae)
    return reg


def predict_latest(model: str) -> pd.DataFrame:
    """Next-session forecast for every covered stock from the latest session in the data."""
    reg, fp = registry(), feature_panel()
    rows = []
    for t in market.tickers():
        g = fp[fp.Ticker == t].sort_values("Date")
        last = g.iloc[-1]
        if model in CLASSICAL:
            if not classical.available(model, [t]):
                raise InferenceUnavailable(f"{model} is not persisted")
            r = float(classical.predict(model, t, g.tail(1))[0])
        elif model in reg.deep_loaded:
            r = reg.deep_loaded[model].predict(g, t)
        else:
            raise InferenceUnavailable(f"{model} is not available")
        rows.append({"ticker": t, "as_of": last.Date, "price": float(last["Adj Close"]), "forecast_log_return": r,
                     "forecast_return": float(np.expm1(r)), "forecast_price": float(last["Adj Close"] * np.exp(r))})
    return pd.DataFrame(rows).set_index("ticker")


def all_forecasts() -> pd.DataFrame:
    out = []
    for m in registry().models:
        if m.loaded:
            f = predict_latest(m.name)["forecast_return"].rename(m.name); out.append(f)
    return pd.concat(out, axis=1) if out else pd.DataFrame()


def validation_path(model: str, ticker: str) -> pd.DataFrame:
    """Out-of-sample predictions over the VALIDATION partition only (2024-01-01..2026-05-08)."""
    if model not in CLASSICAL:
        raise InferenceUnavailable("validation paths are computed for persisted classical models")
    v = F.partition(F.add_labels(feature_panel()), "validation")
    v = v[v.Ticker == ticker].dropna(subset=[F.TARGET]).copy()
    v["pred"] = classical.predict(model, ticker, v)
    v["actual_price"] = v["Adj Close"] * np.exp(v[F.TARGET]); v["pred_price"] = v["Adj Close"] * np.exp(v["pred"])
    return v[["Date", "target_date_t1", "Adj Close", "actual_price", "pred_price", "pred", F.TARGET]]


def error_band(model: str, ticker: str, q=(0.1, 0.9)) -> tuple[float, float]:
    """Empirical 10th/90th percentile of validation log-return errors (actual - predicted)."""
    v = validation_path(model, ticker)
    e = v[F.TARGET] - v["pred"]
    return float(e.quantile(q[0])), float(e.quantile(q[1]))
