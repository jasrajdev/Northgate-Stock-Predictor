# Northgate Stock Predictor

India-focused research project testing whether machine-learning forecasts and carefully time-aligned information can improve investment decisions versus simple baselines. This is a decision-support research tool, not a live trading bot; profitability is not guaranteed.

## Quick start (dashboard)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dashboard.txt -r requirements-dl.txt   # or: pip install -r requirements-lock.txt
python scripts/download_market_data.py           # Yahoo prices -> data/raw, data/processed/market_panel.csv
python scripts/build_features.py                 # feature panel used by the Stock Explorer charts
python scripts/persist_classical_models.py       # fits Ridge/RF/SVR/XGBoost on the TRAIN partition only
python scripts/download_market_context.py        # optional: India VIX + NIFTY sector indices
python scripts/download_macro_context.py         # optional: FRED macro series (latest values, not point-in-time)
python scripts/fetch_news_gdelt.py && python scripts/score_news_sentiment.py   # optional: recent headlines + VADER/FinBERT
streamlit run dashboard/app.py                   # opens the investor dashboard
pytest                                           # unit tests + dashboard smoke test
```

Deep models: place the Kaggle export at `artifacts/incoming/northgate_submission_artifacts.zip` and run
`python scripts/install_kaggle_artifacts.py`. It extracts to `artifacts/kaggle/`, refuses any test split and
verifies each checkpoint loads. The dashboard picks the checkpoints up automatically.

The dashboard reads saved data and persisted models only; it never trains a model or opens the held-out test
window. Data, models and artefacts are local and git-ignored. Code layout: `src/northgate/` (features, models,
finance, recommendations, sentiment, backend API), `dashboard/` (Streamlit app), `scripts/` (data and model
pipelines), `tests/`, `config/` (universe and recommendation assumptions). Report draft: `docs/RESEARCH_REPORT.md`.

## Source of truth
- `STATUS.md` — verified project state and next action
- `PROJECT_NOTEBOOK.md` — durable project context and research safeguards
- `DECISIONS.md` — confirmed decisions only
- `QUESTIONS.md` — unresolved choices
- `IDEAS_BACKLOG.md` — a concise list of research directions, not a transcript of brainstorming
- `LEARNING_LOG.md` — concepts learned
- `docs/IMPLEMENTATION_PLAN.md` — staged project plan
- `docs/DATA_RESEARCH.md` — data-source and dataset research
- `docs/RESEARCH_ROADMAP.md` — research questions, source-only prompts, Phase 1 source pack, and research log
- `docs/PRD_REQUIREMENTS.md` — traceable requirements reference from the supplied PRD v1.0
- `docs/DATASET_INVENTORY.md` — verified data inventory, source coverage and gaps
- `docs/MODEL_TRAINING_GUIDE.md` — model-training workflow, datasets, model order, outputs and safeguards
- `docs/GPU_LAPTOP_SETUP.md` — exact HP Victus Windows/PyTorch/CUDA setup and commands
- `docs/CONTINUITY_PROTOCOL.md` — instructions for future project sessions
- `docs/SUBMISSION_HANDOFF.md` — Kaggle artifact export, local folder layout, and Claude Code dashboard integration handoff

## Start every session
Read `STATUS.md`, `PROJECT_NOTEBOOK.md`, `DECISIONS.md`, and the relevant plan/research files. Keep conversational brainstorming separate from confirmed repository decisions. After a requested repository edit, fetch and verify every changed file.

## Research safeguards
Use chronological splits; prevent look-ahead/data leakage; align information to its actual publication time; compare against simple baselines; include costs and limitations; report negative results honestly. Never claim a model works without out-of-sample evidence.
