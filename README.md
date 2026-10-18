# Northgate Stock Predictor

Research project: test whether ML/DL forecasts and sentiment can improve portfolio decisions versus simple baselines. This is a decision-support research tool, not a trading bot; profitability is not guaranteed.

## Source of truth
- `STATUS.md` — current state and next actions
- `PROJECT_NOTEBOOK.md` — durable context and reasoning
- `IDEAS_BACKLOG.md` — all ideas, including untested ones
- `DECISIONS.md` — choices and why
- `LEARNING_LOG.md` — concepts learned and experiments
- `QUESTIONS.md` — unresolved questions
- `docs/CONTINUITY_PROTOCOL.md` — instructions for every AI session

## Start every session
Read `STATUS.md`, `PROJECT_NOTEBOOK.md`, `DECISIONS.md`, and relevant backlog/log entries before advising or changing anything. After meaningful progress, update relevant files and verify by reading them back.

## Research safeguards
Use chronological splits; prevent look-ahead/data leakage; compare against naive forecast, equal-weight portfolio, and a benchmark; report costs/limitations and honest negative results. Never claim a model works without out-of-sample evidence.