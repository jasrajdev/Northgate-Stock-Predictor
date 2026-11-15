# Northgate Stock Predictor

India-focused research project testing whether machine-learning forecasts and carefully time-aligned information can improve investment decisions versus simple baselines. This is a decision-support research tool, not a live trading bot; profitability is not guaranteed.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dashboard.txt -r requirements-dl.txt   # exact versions: requirements-lock.txt
python scripts/download_market_data.py        # Yahoo prices -> data/raw/yahoo, data/processed/market_panel.csv (re-downloads; history may differ slightly)
python scripts/build_features.py              # feature panel used by the dashboard's price charts
python scripts/persist_classical_models.py    # fits Ridge / Random Forest / SVR / XGBoost on the TRAIN partition only (~1 min)
python scripts/download_market_context.py     # optional: India VIX and NIFTY sector indices
python scripts/download_macro_context.py      # optional: FRED macro series (latest values, not point-in-time)
streamlit run dashboard/app.py                # investor dashboard at http://localhost:8501
pytest                                        # 20 unit tests + dashboard smoke test
python scripts/build_notebooks.py             # optional: re-executes notebooks/01_eda.ipynb and 02_finance_math_verification.ipynb
```

What is and is not available:
- **Forecasts:** the four classical models. The Kaggle deep checkpoints (install with `python scripts/install_kaggle_artifacts.py` from `artifacts/incoming/northgate_submission_artifacts.zip`) are **incompatible** with the current 25-input pipeline (they expect 32 inputs), so the dashboard reports them as unavailable.
- **Sentiment:** `scripts/fetch_news_gdelt.py` then `scripts/score_news_sentiment.py` (FinBERT also needs `pip install transformers`). The free GDELT API returned no data from this machine, so the Sentiment panel currently shows the pipeline status only.
- **Evaluation:** all reported model and portfolio results are validation results. The final six-month test window is sealed and is not read by any script or by the dashboard.

Data, models and Kaggle artefacts are local and git-ignored (data-provider terms). The steps above were each run on the development machine; a single end-to-end rebuild on a fresh machine has not been verified.

Layout: `src/northgate/` (features, models, finance, recommendations, sentiment, backend API), `dashboard/` (Streamlit app, 7 panels), `scripts/` (data and model pipelines), `notebooks/` (EDA, finance verification), `tests/`, `config/` (universe; recommendation assumptions). Report: `docs/RESEARCH_REPORT.md`. Outstanding work: `docs/POST_SUBMISSION_BACKLOG.md`.

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
