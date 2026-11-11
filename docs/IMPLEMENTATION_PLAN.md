# Northgate Implementation Plan

Updated: 2026-11-11  
Status: planning document. Only the initial repository scaffold exists; no market data or model results have been verified.

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

## Immediate next action
Agree the evaluation contract, then run a small data-source feasibility pilot. Do not bulk-download data or start model training before these foundations are checked.

## Timeline risk
The recorded deadline is 15 November 2026. The complete PRD scope may not be achievable to its intended standard in the remaining time. Preserve methodological correctness; if prioritisation is necessary, document the proposed scope change and get approval rather than pretending incomplete work is complete.
