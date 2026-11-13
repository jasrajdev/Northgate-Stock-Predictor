# Northgate Implementation Plan

Updated: 2026-11-12  
Status: active implementation. Market data, feature panel, and first next-session supervised dataset have been generated locally by the user; macro/news datasets and model experiments remain pending.

## Objective
Build the India-focused research and decision-support system described in the Northgate PRD. The PRD is referenced in project context but is not currently present as a standalone file in the GitHub repository tree reviewed on 2026-11-11. Its requirements remain the scope reference until a change is explicitly approved.

## Evaluation layers
1. **Forecasting:** compare the required models on identical chronological held-out dates and against a naive random-walk baseline. Report the PRD metrics, including MAE and directional accuracy.
2. **Recommendations:** evaluate BUY/HOLD/SELL outcomes only after defining the signal timestamp, entry/exit convention, holding horizon, costs, and what counts as a successful trade.
3. **Portfolio:** evaluate capital-weighted results against equal-weight and market benchmarks on the same out-of-sample dates. Report risk, costs, turnover, and drawdown.

Do not treat these three evaluations as interchangeable. A forecast metric or BUY win rate alone does not establish portfolio profitability.

## PRD scope to preserve
- 8–15 liquid large-cap equities plus a broad-market benchmark.
- 8–10 years of daily OHLCV and adjusted-price data, relevant macroeconomic series, and timestamped financial news.
- EDA and core finance calculations.
- Four classical ML models: Linear/Ridge, Random Forest, XGBoost, and SVR.
- Four DL architectures: LSTM, GRU, BiLSTM, and Transformer.
- FinBERT/VADER sentiment comparison.
- Chronological validation and leakage safeguards.
- Mean-variance optimisation, efficient frontier, maximum-Sharpe portfolio, Monte Carlo cross-check, and comparison with equal-weight and benchmark buy-and-hold.
- BUY/HOLD/SELL recommendation logic, seven-panel Streamlit dashboard, reproducible workflow, and 10–15 page report.

If deadline or resources make full scope infeasible, propose a clear prioritisation and obtain approval before changing the scope.

## Staged implementation sequence

### 1. Agree the evaluation contract
Define the forecast target(s), recommendation outcome, signal time, trade entry/exit convention, holding horizon, transaction costs, and portfolio constraints. No fixed return target, stop-loss, score threshold, or holding period is assumed at this stage.

### 2. Verify data feasibility
- Test a small sample of Indian equities and a candidate benchmark.
- Verify historical coverage, field definitions, adjustments for corporate actions, missing dates, symbol changes, terms, and repeatable downloads.
- Prefer point-in-time constituent history. If unavailable, document survivorship bias.
- Do not bulk-download until the pilot succeeds.

### 3. Build ingestion and data-quality checks
- Preserve raw downloads separately from processed data.
- Check duplicate dates, missing sessions, OHLC consistency, volume anomalies, corporate actions, and symbol changes.
- Do not back-fill prices or silently fabricate observations.
- Record source, retrieval time, date range, transformations, and exclusions.

### 4. EDA and baseline
- Examine price/return distributions, volatility, volume, correlations, and missingness.
- Create explainable lagged features only from information available at the decision time.
- Establish naive forecasting and simple portfolio baselines before adding complexity.

### 5. Model experiments
- Use chronological train/validation/test partitions and walk-forward validation.
- Fit scalers and preprocessing only on each training fold.
- Purge overlapping forward-label periods at split boundaries.
- Tune on validation data; keep the final test untouched.
- Compare the PRD-required model families on consistent data, targets, features, dates, and baselines.
- Record MAE/RMSE and directional accuracy; separately assess recommendation and portfolio utility.

### 6. Recommendation and portfolio evaluation
- Define transparent BUY/HOLD/SELL rules only after the evaluation contract is agreed.
- Do not interpret raw regression outputs as calibrated probabilities.
- Include capital allocation, position limits, turnover, brokerage/statutory costs, and slippage.
- Compare with equal-weight and benchmark portfolios on identical out-of-sample periods.
- Report net return, Sharpe/Sortino, volatility, beta, maximum drawdown, turnover, trade count, and other PRD metrics.

### 7. News and sentiment evaluation
- Implement only after the price/volume baseline and timestamp handling are reliable.
- Verify access to official announcements and timestamped news, including historical coverage and usage terms.
- Add news features incrementally and compare with/without them on the same chronological dates.
- Handle after-close information at the next eligible session; deduplicate stories and preserve source timestamps.
- Do not assume news improves performance until an out-of-sample comparison demonstrates incremental value.

### 8. Dashboard, report, reproducibility
- Build the Streamlit dashboard after stable data/model outputs exist; it should read saved results rather than retrain on page load.
- Verify reproducible commands for data preparation, training/evaluation, and dashboard launch.
- Report limitations, incomplete requirements, and negative findings honestly.

## Current verified implementation milestone (2026-11-12)
- Yahoo Finance data download: 29,484 rows across 10 provisional Indian equities plus NIFTY 50 price index, as reported by user.
- Per-ticker feature engineering: 24 generated features; zero-volume anomalies are excluded from equity volume indicators while raw volume is preserved; NIFTY 50 volume-derived indicators are disabled.
- First supervised next-session dataset generated by user: 29,473 labelled rows across 11 instruments. Reported checks: no duplicate ticker/date keys, target dates later than feature dates, no missing target values, and no non-positive target adjusted closes.
- Script outputs: `data/processed/modeling_dataset_next_day.csv` and `reports/data_quality/next_day_dataset_report.json`. These are local user-reported outputs and have not been independently inspected in this session.
- No models, backtest, dashboard, or performance results have been verified.

## Immediate next action
Prepare the PRD's macro/market context data and timestamped financial news/sentiment data. Retain source timestamps and release/publication availability; align after-close information to the next eligible trading session. Merge only after checking coverage and missingness. Then create chronological train/validation/test splits and establish the naive baseline before model comparisons. Define the unspecified multi-day horizons before adding those labels.

## Timeline risk
The recorded deadline is 15 November 2026. The complete PRD scope may not be achievable to its intended standard in the remaining time. Preserve methodological correctness; if prioritisation is necessary, document the proposed scope change and get approval rather than pretending incomplete work is complete.


## Chronological split protocol agreed (2026-11-13)
For the existing one-session-ahead target, the working split is:
- Training outcomes through 2023-12-31.
- Validation outcomes after 2023-12-31 and before the final six-calendar-month test cutoff.
- Final six calendar months of labelled data reserved as the untouched test window.

The cutoff is computed from the latest `target_date_t1` in the dataset. Rows are assigned by target date, because that is when the forecast outcome becomes known. The script `scripts/create_chronological_splits.py` writes the three partitions and a quality report. Do not fit scalers, imputers, or feature selectors on validation/test data; do not use any `target_*` column as an input. The current script handles the one-session target only. Multi-session horizons require an explicit decision and review of overlapping-label purge/embargo requirements.

## Training-first acceleration (2026-11-13)

The first baseline model experiment starts on the existing price/volume-only next-session dataset. Macro/CPI and news/sentiment collection are deferred until after a baseline result; they are incremental features, not gates to first training. This is sequencing, not removal from the PRD scope.

Added scripts/train_baseline_models.py:
- Fits separate per-equity models to avoid mixing raw price scales across different stocks.
- Uses the existing chronological train and validation partitions; excludes the NIFTY 50 index row from equity model fitting.
- Models: Ridge, Random Forest, RBF-SVR and XGBoost.
- Compares validation MAE, RMSE and directional accuracy with a naive last-adjusted-close forecast.
- Does not load or evaluate the final test partition.
- Learned preprocessing is contained inside each sklearn Pipeline and is fitted on that ticker's training rows only.

The script is committed but has not yet been executed. No performance result is claimed. Next: run it locally, inspect per-ticker results and failures, then select/tune using validation only. Add macro/news features after this first baseline has established a comparison point.

