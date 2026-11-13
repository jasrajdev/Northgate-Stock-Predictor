"""Fast first-pass per-stock forecasting benchmark.

Uses train/validation only. The final test partition is deliberately not loaded.
Target: next-session adjusted close. Features are numeric values known at t.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

ROOT = Path(__file__).resolve().parents[1]
SPLIT_DIR = ROOT / "data" / "processed" / "splits"
OUT_DIR = ROOT / "reports" / "validation"
TARGET = "target_adj_close_t1"
CURRENT_PRICE = "Adj Close"
NON_FEATURES = {
    "Date", "Ticker", "Name", "target_date_t1", "target_adj_close_t1",
    "target_log_return_t1", "target_direction_t1",
}


def make_models(xgb_device="cuda"):
    models = {
        "Ridge": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", Ridge(alpha=10.0)),
        ]),
        "RandomForest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestRegressor(
                n_estimators=120, min_samples_leaf=3,
                max_features=0.8, n_jobs=-1, random_state=42,
            )),
        ]),
        "SVR_RBF": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", SVR(C=1.0, epsilon=0.01, kernel="rbf")),
        ]),
    }
    try:
        from xgboost import XGBRegressor
        models["XGBoost"] = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", XGBRegressor(
                n_estimators=250, max_depth=4, learning_rate=0.04,
                subsample=0.85, colsample_bytree=0.85,
                objective="reg:squarederror", n_jobs=-1,
                tree_method="hist", device=xgb_device,
                random_state=42,
            )),
        ])
    except ImportError:
        models["XGBoost"] = None
    return models


def metrics(y_true, y_pred, current):
    actual_direction = np.sign(np.asarray(y_true) - np.asarray(current))
    predicted_direction = np.sign(np.asarray(y_pred) - np.asarray(current))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "directional_accuracy": float(np.mean(actual_direction == predicted_direction)),
    }


def main():
    train_path = SPLIT_DIR / "train.csv"
    val_path = SPLIT_DIR / "validation.csv"
    if not train_path.exists() or not val_path.exists():
        raise FileNotFoundError(
            "Missing train/validation splits. Run scripts/create_chronological_splits.py first."
        )

    train = pd.read_csv(train_path)
    valid = pd.read_csv(val_path)
    required = {"Ticker", TARGET, CURRENT_PRICE}
    for name, frame in [("train", train), ("validation", valid)]:
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"{name}.csv missing columns: {sorted(missing)}")

    # The index is a market benchmark/context series, not an individual stock.
    train = train[train["Ticker"] != "^NSEI"].copy()
    valid = valid[valid["Ticker"] != "^NSEI"].copy()
    if train.empty or valid.empty:
        raise ValueError("No equity rows remain after excluding the ^NSEI benchmark.")

    feature_cols = [
        c for c in train.select_dtypes(include=[np.number]).columns
        if c not in NON_FEATURES
    ]
    feature_cols = [c for c in feature_cols if c in valid.columns]
    if CURRENT_PRICE not in feature_cols:
        raise ValueError(f"{CURRENT_PRICE} must be retained as a valid time-t feature.")
    if not feature_cols:
        raise ValueError("No numeric feature columns found.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    skipped = []
    xgb_device = os.getenv("NORTHGATE_XGB_DEVICE", "cuda").lower()
    print(f"XGBoost requested device: {xgb_device}")
    start = time.time()

    for ticker in sorted(set(train["Ticker"]) & set(valid["Ticker"])):
        tr = train[train["Ticker"] == ticker].copy()
        va = valid[valid["Ticker"] == ticker].copy()
        tr = tr.replace([np.inf, -np.inf], np.nan)
        va = va.replace([np.inf, -np.inf], np.nan)
        tr = tr.dropna(subset=[TARGET, CURRENT_PRICE])
        va = va.dropna(subset=[TARGET, CURRENT_PRICE])
        if len(tr) < 100 or len(va) < 20:
            skipped.append({"ticker": ticker, "reason": "insufficient rows"})
            continue

        X_train = tr[feature_cols]
        y_train = tr[TARGET]
        X_val = va[feature_cols]
        y_val = va[TARGET]
        current = va[CURRENT_PRICE]

        baseline = metrics(y_val, current, current)
        rows.append({
            "ticker": ticker, "model": "Naive_Last_Adjusted_Close",
            "train_rows": len(tr), "validation_rows": len(va),
            **baseline,
        })

        for model_name, model in make_models(xgb_device).items():
            if model is None:
                skipped.append({"ticker": ticker, "model": model_name,
                                "reason": "xgboost is not installed"})
                continue
            try:
                model.fit(X_train, y_train)
                pred = model.predict(X_val)
                rows.append({
                    "ticker": ticker, "model": model_name,
                    "train_rows": len(tr), "validation_rows": len(va),
                    **metrics(y_val, pred, current),
                })
            except Exception as exc:
                # If CUDA is unavailable/unsupported, retry XGBoost on CPU once.
                if model_name == "XGBoost" and xgb_device == "cuda" and any(
                    token in str(exc).lower() for token in ("cuda", "gpu", "device")
                ):
                    try:
                        from xgboost import XGBRegressor
                        fallback = Pipeline([
                            ("imputer", SimpleImputer(strategy="median")),
                            ("model", XGBRegressor(
                                n_estimators=250, max_depth=4, learning_rate=0.04,
                                subsample=0.85, colsample_bytree=0.85,
                                objective="reg:squarederror", n_jobs=-1,
                                tree_method="hist", device="cpu", random_state=42,
                            )),
                        ])
                        fallback.fit(X_train, y_train)
                        pred = fallback.predict(X_val)
                        rows.append({"ticker": ticker, "model": "XGBoost_CPU_Fallback",
                                     "train_rows": len(tr), "validation_rows": len(va),
                                     **metrics(y_val, pred, current)})
                    except Exception as fallback_exc:
                        skipped.append({"ticker": ticker, "model": model_name,
                                         "reason": f"CUDA failed: {exc}; CPU fallback failed: {fallback_exc}"})
                else:
                    skipped.append({"ticker": ticker, "model": model_name,
                                    "reason": f"{type(exc).__name__}: {exc}"})

    result = pd.DataFrame(rows)
    if result.empty:
        raise RuntimeError("No model results produced.")
    result.to_csv(OUT_DIR / "model_comparison_validation.csv", index=False)
    summary = (
        result.groupby("model")[["mae", "rmse", "directional_accuracy"]]
        .mean().sort_values("mae").reset_index()
    )
    summary.to_csv(OUT_DIR / "model_summary_validation.csv", index=False)
    report = {
        "target": TARGET,
        "feature_count": len(feature_cols),
        "features": feature_cols,
        "training_tickers": sorted(train["Ticker"].unique().tolist()),
        "benchmark_excluded_from_stock_training": "^NSEI",
        "train_rows": int(len(train)),
        "validation_rows": int(len(valid)),
        "test_partition_loaded": False,
        "selection_rule": "Use validation only; final test remains untouched.",
        "xgboost_requested_device": xgb_device,
        "elapsed_seconds": round(time.time() - start, 2),
        "skipped": skipped,
        "summary": summary.to_dict(orient="records"),
    }
    (OUT_DIR / "model_training_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(summary.to_string(index=False))
    print(f"\nResults: {OUT_DIR}")
    print(f"Feature count: {len(feature_cols)} | Elapsed: {report['elapsed_seconds']}s")
    print("Final test partition was not loaded.")


if __name__ == "__main__":
    main()
