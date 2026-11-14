"""Fit and persist the four classical models per ticker on the TRAIN partition only.

Usage:  python scripts/persist_classical_models.py

* Input: data/processed/market_panel.csv (local Yahoo build). splits/test.csv is never read.
* Features: northgate.features (Experiment-01 v1 set, 25 inputs). Target: next-session log return.
* Train rows: target date <= 2023-12-31. Validation metrics: target dates 2024-01-01..2026-05-08.
  Labels after the validation end are never created.
* Output (local, git-ignored): models/classical/<Model>/<TICKER>.joblib, metadata.json,
  validation_metrics.csv. Deterministic (random_state=42).
"""
from __future__ import annotations
import hashlib, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
import numpy as np, pandas as pd, sklearn
from northgate import config, features as F
from northgate.models import CLASSICAL, classical
from northgate.models.metrics import regression_metrics


def main() -> None:
    src = config.PROCESSED / "market_panel.csv"
    panel = pd.read_csv(src, parse_dates=["Date"])
    data = F.add_labels(F.build(panel))
    train, valid = F.partition(data, "train"), F.partition(data, "validation")
    tickers = [t for t in sorted(panel.Ticker.unique()) if t != config.BENCHMARK]
    rows, t0 = [], time.time()
    for t in tickers:
        tr = train[train.Ticker == t].dropna(subset=[F.TARGET]).replace([np.inf, -np.inf], np.nan)
        va = valid[valid.Ticker == t].dropna(subset=[F.TARGET]).replace([np.inf, -np.inf], np.nan)
        zero = np.zeros(len(va))
        rows.append({"ticker": t, "model": "Naive_Last_Adjusted_Close", **regression_metrics(va[F.TARGET], zero, va["Adj Close"])})
        rows.append({"ticker": t, "model": "Always_Up_Direction_Baseline", **regression_metrics(va[F.TARGET], zero, va["Adj Close"], np.ones(len(va)))})
        for name in CLASSICAL:
            m = classical.make(name).fit(tr[F.FEATURES], tr[F.TARGET])
            classical.save(m, name, t)
            rows.append({"ticker": t, "model": name, "train_rows": len(tr), "validation_rows": len(va),
                         **regression_metrics(va[F.TARGET], m.predict(va[F.FEATURES]), va["Adj Close"])})
        print(f"{t}: fitted {len(CLASSICAL)} models on {len(tr)} train rows; scored {len(va)} validation rows", flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(classical.DIR / "validation_metrics.csv", index=False)
    summary = res.groupby("model")[["mae", "rmse", "mape_pct", "r2", "directional_accuracy"]].mean().sort_values("mae")
    summary.to_csv(classical.DIR / "validation_summary.csv")
    meta = {"created_utc": datetime.now(timezone.utc).isoformat(), "script": "scripts/persist_classical_models.py",
            "source_panel": str(src.relative_to(ROOT)), "source_panel_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
            "features": F.FEATURES, "target": F.TARGET, "models": CLASSICAL, "tickers": tickers,
            "train_rows_rule": "target_date_t1 <= 2023-12-31", "validation_rows_rule": "2023-12-31 < target_date_t1 <= 2026-05-08",
            "test_partition_read": False, "sklearn_version": sklearn.__version__, "random_state": classical.SEED,
            "elapsed_seconds": round(time.time() - t0, 1),
            "note": "Local Mac data build; differs from the Kaggle build used in Experiment 01, so metrics are comparable in method, not identical in value."}
    (classical.DIR / "metadata.json").write_text(json.dumps(meta, indent=2))
    print(summary.round(4).to_string()); print("saved to", classical.DIR.relative_to(ROOT))


if __name__ == "__main__":
    main()
