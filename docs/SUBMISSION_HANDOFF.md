# Submission Handoff — Kaggle Artifacts and Dashboard Integration

Updated: 2026-11-15

## Purpose

This handoff connects the user's Kaggle training run to the local Streamlit application. It does not claim that Northgate is PRD-complete. The PRD remains the acceptance source; see `docs/PRD_REQUIREMENTS.md`.

## Verified Kaggle run

The user reported a successful Kaggle run on a Tesla T4:
- Classical model implementations run: Ridge, Random Forest, SVR-RBF, XGBoost.
- Deep model checkpoints saved: LSTM, GRU, BiLSTM, Transformer.
- Deep checkpoint files reported: `lstm_best.pt`, `gru_best.pt`, `bilstm_best.pt`, `transformer_best.pt`.
- Validation outputs reported: `model_comparison_validation.csv`, `model_summary_validation.csv`, `model_training_report.json`, `deep_model_comparison_validation.csv`, `deep_training_history.json`, `deep_training_report.json`.
- Both training reports state `test_partition_loaded: false`.
- The user-reported run is a first price/volume-only experiment, not the full PRD data/model system.

Important artifact limitation:
- The current deep training script saves reusable PyTorch checkpoints including architecture metadata and train-fitted preprocessing statistics.
- The current classical training script writes validation metrics but does **not** persist fitted Ridge, Random Forest, SVR, or XGBoost estimators. Do not present the CSV metrics as deployable fitted models. If the application needs live inference from these four classical models, add a reproducible persistence step using training data only; do not load the final test split.
- The eight model families are required as a benchmark. The PRD recommendation signal is the forecast from the best model; it does not explicitly require averaging all eight into an ensemble. Do not silently invent an ensemble.

## Kaggle export procedure

Run this cell in the existing Kaggle notebook after training. It packages model checkpoints, validation reports, the data-quality report, and only the train/validation splits. The final test split is intentionally excluded.

```python
from pathlib import Path
import zipfile
import json
from datetime import datetime, timezone

PROJECT = Path("/kaggle/working/Northgate-Stock-Predictor")
OUT = Path("/kaggle/working/northgate_submission_artifacts.zip")

include = [
    "models/deep/lstm_best.pt",
    "models/deep/gru_best.pt",
    "models/deep/bilstm_best.pt",
    "models/deep/transformer_best.pt",
    "reports/validation/model_comparison_validation.csv",
    "reports/validation/model_summary_validation.csv",
    "reports/validation/model_training_report.json",
    "reports/validation/deep_model_comparison_validation.csv",
    "reports/validation/deep_training_history.json",
    "reports/validation/deep_training_report.json",
    "reports/data_quality/gpu_data_build_report.json",
    "data/processed/splits/train.csv",
    "data/processed/splits/validation.csv",
]

missing = [p for p in include if not (PROJECT / p).is_file()]
if missing:
    raise FileNotFoundError("Missing required artifact(s): " + ", ".join(missing))

manifest = {
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "source": "Kaggle Northgate Stock Predictor training run",
    "included": include,
    "excluded": ["data/processed/splits/test.csv"],
    "test_partition_loaded_by_training_scripts": False,
    "notes": [
        "Price/volume-only first experiment; not full PRD completion.",
        "Deep checkpoints include model architecture and train-fitted preprocessing metadata.",
        "Classical training script currently saves metrics, not fitted estimators.",
    ],
}

with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for rel in include:
        z.write(PROJECT / rel, arcname=rel)
    z.writestr("ARTIFACT_MANIFEST.json", json.dumps(manifest, indent=2))

print(f"Created: {OUT}")
print(f"Size: {OUT.stat().st_size / 1024 / 1024:.2f} MB")
print("Included files:", len(include) + 1)
print("Final test split included: NO")

from IPython.display import FileLink, display
display(FileLink(str(OUT)))
```

Download the ZIP from the clickable link printed by the cell (or from the Kaggle notebook's Output/Files panel).

## Local placement

In the cloned repository, place the downloaded ZIP at:

`artifacts/incoming/northgate_submission_artifacts.zip`

Extract it so the paths resolve as:

- `artifacts/kaggle/models/deep/*.pt`
- `artifacts/kaggle/reports/validation/*`
- `artifacts/kaggle/reports/data_quality/gpu_data_build_report.json`
- `artifacts/kaggle/data/processed/splits/train.csv`
- `artifacts/kaggle/data/processed/splits/validation.csv`

Do not copy or export `test.csv`. Do not commit raw market data or split CSVs to Git without checking data-provider redistribution terms. The four small deep checkpoints may be committed only if repository policy and file-size checks permit; otherwise keep them as documented local artifacts or attach them to a versioned GitHub Release.

## Claude Code implementation brief

Claude Code should:
1. Read `README.md`, `STATUS.md`, `PROJECT_NOTEBOOK.md`, `DECISIONS.md`, `docs/CONTINUITY_PROTOCOL.md`, `docs/PRD_REQUIREMENTS.md`, and this handoff.
2. Inspect the existing Streamlit application before changing it. Do not create a second app or replace working components blindly.
3. Rework the primary user experience around investor tasks: portfolio overview, watchlist/covered stocks, BUY/HOLD/SELL recommendations, stock detail with forecast, portfolio allocation, risk, sentiment, and rebalancing. Keep model comparison and training diagnostics in a secondary Research/Model Comparison area because the PRD explicitly requires that panel.
4. Make the app read cached artifacts and saved predictions; never train models on page load.
5. Load the four PyTorch checkpoints using the exact model definitions and preprocessing metadata in `scripts/train_deep_models.py`. Verify feature order, ticker map, sequence length, and training-only normalization. Do not guess or silently reshape incompatible checkpoint data.
6. For classical models, recognise that only validation metrics currently exist. If live inference is required, add a deterministic persistence/training script that fits only the training partition, saves each fitted estimator and metadata, and never reads `test.csv`. Clearly label any unavailable inference model instead of fabricating a forecast.
7. Implement only recommendations whose inputs and rules are documented. The existing decision is that HOLD/no-trade is valid and the app must not force a trade. Do not invent unapproved numeric thresholds; make thresholds explicit configuration and document assumptions.
8. Never label raw model outputs as calibrated probabilities or guaranteed buy signals. Include educational-not-financial-advice and research limitations.
9. Complete the remaining PRD backend modules where feasible: financial metrics, long-only mean-variance optimisation, efficient frontier, risk metrics, benchmark/equal-weight comparisons, sentiment ingestion/scoring and time alignment. Clearly separate implemented, simulated/demo, and pending functionality.
10. Keep the seven PRD dashboard panels accessible: Overview; Price & Prediction; Model Comparison; Portfolio Analytics; Risk; Sentiment; Recommendations. The Model Comparison panel may be secondary and must not dominate the landing page.
11. Add/update README setup and run instructions, config examples, dependency pins, and a 10–15 page report outline or honest current report. Never claim an acceptance criterion is met without evidence.
12. Run focused unit tests, import checks, and a local Streamlit startup smoke test. Report exact commands and outcomes. Do not open the held-out test partition.

## Definition of done for this handoff

- The Kaggle ZIP is downloaded and extracted into the specified local folder.
- Claude reports which checkpoints load successfully and which classical estimators need persistence.
- The Streamlit landing page is investor-facing, with recommendations and portfolio context first.
- The seven PRD panels are present, with Research/Model Comparison secondary.
- Missing data and unavailable signals are labelled honestly; no fabricated BUY/HOLD/SELL outputs.
- Setup/run instructions and remaining PRD gaps are documented.
