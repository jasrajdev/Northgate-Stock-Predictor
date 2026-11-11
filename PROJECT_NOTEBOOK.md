# Project Notebook

## Research question
Can machine learning and carefully time-aligned information improve decisions about Indian equities out of sample, compared with simple baselines?

## Project scope reference
The original PRD (not currently present as a standalone file in the GitHub tree reviewed on 2026-11-11) specifies:
- 8–15 liquid large-cap equities plus a broad-market benchmark, with 8–10 years of daily OHLCV/adjusted-price data, macro series, and timestamped financial news.
- EDA and finance mathematics.
- Four classical ML models: Linear/Ridge, Random Forest, XGBoost, and SVR.
- Four deep-learning models: LSTM, GRU, BiLSTM, and Transformer.
- FinBERT/VADER sentiment comparison.
- Mean-variance portfolio optimisation, backtesting, BUY/HOLD/SELL recommendations, a seven-panel Streamlit dashboard, reproducible workflow, and a 10–15 page report.
- Chronological evaluation and comparisons with simple baselines.

Use the original PRD for exact acceptance wording. Do not silently remove requirements; record any agreed scope change explicitly.

## Confirmed direction
- India-first research.
- NIFTY 50 is a candidate starting universe, not a final choice.
- Start with a small, reliable data and baseline pipeline before expanding complexity.
- Treat the system as research/decision support, not live brokerage execution.
- Evaluate forecasting, recommendations, and portfolio performance separately.
- Prevent look-ahead/data leakage: only use information available at the simulated decision time.
- Compare against naive forecasting and equal-weight/market benchmarks as appropriate.
- Report costs, limitations, uncertainty, and negative results honestly.

## Open design choices
- Exact universe, benchmark, data providers, and point-in-time constituent history.
- Forecast target and horizon.
- Recommendation logic, trade timing, holding period, exit logic, and capital allocation.
- Whether and how the earlier 70% profitable-BUY aspiration should be retained as a secondary research objective; it is not a guaranteed outcome or a PRD acceptance criterion.
- News/event data sources, scope, event classification, timestamp handling, and whether news adds measurable value beyond price/volume.
- Feasible implementation scope against the recorded 15 November 2026 deadline.

## Research safeguards
1. Use chronological train/validation/test splits and walk-forward validation where appropriate.
2. At every prediction timestamp, use only data that was actually available then.
3. Fit preprocessing/scalers on training data only.
4. Align after-close announcements and news to the next eligible trading session.
5. Avoid survivorship bias; prefer point-in-time universe membership or disclose the limitation.
6. Compare models on the same dates, targets, features, and baselines.
7. Keep the final test period untouched until choices are frozen.
8. Include transaction costs/slippage where feasible.
9. Do not equate forecast error, a recommendation win rate, and portfolio profitability.

## Current implementation state (updated 2026-11-12)
- Yahoo Finance ingestion script is in the repository. User reports successful local download of 10 provisional Indian equities plus the NIFTY 50 price index: 29,484 combined rows through 2026-11-09.
- A combined market panel and 24 backward-looking features per instrument have been generated locally. Feature calculations are grouped by ticker; raw zero-volume observations are preserved while zero volume is excluded from equity volume indicators, and NIFTY 50 volume indicators are disabled.
- First-pass user-reported validation found no duplicate ticker/date keys, unsorted rows, or missing values in the combined panel's 11 columns. This is not a complete audit of expected exchange sessions or vendor accuracy.
- A next-session supervised dataset builder has been added to GitHub and run successfully by the user. Terminal output reports 29,473 labelled rows across 11 instruments, with one final unlabeled row removed per ticker. Checks report zero duplicate ticker/date keys, all target dates later than feature dates, zero missing target values, and zero non-positive target adjusted closes. Local CSV and JSON report paths were printed by the script; the files were not independently inspected in this session.
- No model has been trained; no backtest, dashboard, or measured performance result has been verified. The next preparation work is macro/market data and timestamped news/sentiment, followed by time-aligned dataset merging and chronological splits.
- Next data families required by the PRD: macro/market indicators and timestamped financial news/sentiment. Multi-day target horizons remain unspecified in the PRD and need an explicit choice.
