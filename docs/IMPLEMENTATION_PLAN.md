# Northgate Implementation Plan

Updated: 2026-11-09
Status: proposed sequence; no bulk data download or model training has started.

## Project objective
Build the Northgate PRD's reproducible India-focused research and decision-support system. Preserve the PRD's acceptance criteria while adding the user's practical recommendation objective.

## Two levels of success — do not confuse them
1. **Forecasting model:** On the same unseen dates, compare the four required ML models and four required DL models. The PRD requires the best forecaster to beat a naive last-value/random-walk predictor on MAE and directional accuracy.
2. **Trading recommendations and portfolio:** Simulate the BUY/HOLD/SELL decisions and portfolio weights. The PRD requires the optimised portfolio to beat an equal-weight portfolio on out-of-sample Sharpe. Also compare with a broad-market benchmark.

### User-defined additional objective (research target, not guarantee)
- Aim for at least 70% of BUY recommendations to have positive net returns over a five-trading-session holding period.
- A 70% win rate is not sufficient on its own: report average win, average loss, net return after costs, profit factor, drawdown, Sharpe, number of trades, and uncertainty/confidence intervals.
- A high win rate can still lose money if losses are much larger than wins.
- Do not interpret a regression forecast as a probability of success. A predicted price/return is not automatically a calibrated 70% chance. If the system later reports probabilities, calibrate and evaluate them separately.

## Proposed trade definition — pending confirmation
- Generate the signal after session t has closed, using only information available by that close.
- Enter at session t+1 open.
- Exit at the close of the fifth trading session after signal generation (t+5 close).
- Calculate the realised trade return from corporate-action-adjusted prices and deduct documented brokerage, taxes, fees, and slippage assumptions.
- Treat this as a proposed, testable convention, not yet a final decision. Verify whether the available data source supports adjusted open/close prices or another reliable total-return calculation.
- Decide how concurrent recommendations share capital, whether a stock can be re-entered while an earlier trade is open, and how position limits work before portfolio backtesting.

## PRD requirements that remain mandatory
- 8–15 liquid large-cap equities plus a broad-market index; at least 8–10 years of daily data.
- Daily OHLCV and adjusted close, macroeconomic series, and timestamped financial news.
- EDA and finance maths; implement core return/risk calculations from first principles once and verify against libraries.
- Four classical ML regressors: Linear/Ridge, Random Forest, XGBoost, SVR.
- Four DL architectures: LSTM, GRU, BiLSTM, Transformer.
- Chronological validation; scaler fit on training data only; fixed seeds; early stopping for DL.
- Naive random-walk baseline; compare all models on identical held-out dates/features.
- FinBERT and VADER sentiment comparison; align after-close news to next session.
- Mean-variance optimisation, efficient frontier, max-Sharpe weights, Monte Carlo cross-check, and comparison against equal-weight and benchmark buy-and-hold.
- Transparent BUY/HOLD/SELL recommendations; seven Streamlit panels; reproducible commands; 10–15 page report.

## Stepwise build sequence

### Step 1 — Freeze the evaluation contract (next task)
Agree/document:
- Primary target and five-session holding convention.
- Signal time, entry/exit prices, corporate-action treatment.
- What counts as a BUY recommendation and what counts as a winning trade.
- Cost/slippage assumptions and capital/position constraints.
- Metrics for model forecasting vs recommendation win rate vs portfolio performance.
Why: without this contract, two models or backtests can appear different simply because they were evaluated differently.

### Step 2 — Data-source and universe feasibility pilot
- Start with a small cross-sector sample of Indian large-cap shares plus the benchmark; the PRD limits the final universe to 8–15 equities, not the 20–30 suggested in external brainstorming.
- NIFTY 50 is a sensible candidate universe, not a final commitment. Choose 8–15 with a reproducible rule.
- Test a small recent and historical download from the proposed source before bulk collection. Verify date coverage, missing dates, adjusted prices, volume, symbol changes, and repeatability.
- Prefer point-in-time historical index membership where available. If unavailable, disclose survivorship bias from using current constituents retrospectively.
- Do not assume a free source provides 8–10 years of reliable adjusted Indian equity data until the pilot proves it.

### Step 3 — Build ingestion and quality checks
- Preserve downloaded raw files unchanged under data/raw/.
- Create cleaned data separately under data/processed/.
- Validate duplicates, missing sessions, OHLC consistency, corporate actions, zero/missing volume, symbol changes, and date/time conventions.
- Never back-fill prices. Investigate gaps; do not silently fabricate observations.
- Record source, download time, date range, fields, transformations, and any exclusions.

### Step 4 — EDA and baseline features
- Plot prices, returns, volume, volatility, correlations, distributions, and missingness.
- Create only explainable initial features (e.g. lagged returns, rolling volatility, moving averages, volume changes).
- Ensure every feature at date t uses only data available by the signal time at t.
- Implement naive forecasting baselines before complex models.

### Step 5 — Chronological model experiments
- Keep train/validation/test chronological; PRD DL starting split is 70/15/15.
- Use expanding-window TimeSeriesSplit/walk-forward validation for model selection.
- Fit scalers on each training fold only, then transform validation/test.
- For a five-session forward target, purge at least the overlapping label horizon at split boundaries (and apply an embargo if needed) so labels do not share future outcome periods across folds.
- Tune on validation only. Keep the final test untouched until choices are frozen.
- Compare all eight required models on the same dates, target, features, and baseline.
- Record MAE/RMSE and directional accuracy as required; also evaluate recommendation-level and portfolio-level results.

### Step 6 — Recommendation and portfolio backtest
- Convert forecast outputs to transparent BUY/HOLD/SELL rules using thresholds selected on validation data, not the final test.
- If a probability threshold is used, first establish calibrated probabilities; do not treat a raw regression output as probability.
- Apply consistent capital allocation, per-stock caps, turnover rules, and transaction costs.
- Compare optimised portfolio with equal-weight and benchmark buy-and-hold over the same out-of-sample dates.
- Report Sharpe, Sortino, annualised volatility, Beta, maximum drawdown, net return, turnover, win rate, profit factor, and trade count.
- Use block bootstrap confidence intervals for Sharpe as specified by the PRD.

### Step 7 — Add news and macro features
- Only after the price/volume baseline works.
- Add RBI/macro and timestamped company/sector/policy/global news; test each group incrementally.
- Compare with/without sentiment using the same chronological test dates.
- Preserve the broad event-analysis idea in the backlog.

### Step 8 — Dashboard, report, reproducibility
- Build dashboard only after outputs are stable; it reads cached results and must not retrain on page load.
- Verify one command rebuilds data, one command trains/evaluates, and dashboard launches.
- Write the 10–15 page report with limitations and honest failure analysis.

## Immediate next action
Complete Step 1: agree the trade timing/return definition and the recommendation-vs-portfolio scorecard. Then run a small data-source feasibility pilot. Do not start all eight models or download the full universe yet.

## Timeline risk
The original PRD describes a four-week, 25–30-hours/week plan. The current project deadline recorded in STATUS.md is 15 November 2026, only six calendar days from this update. The complete PRD scope is unlikely to be delivered to its intended quality in that time without substantial scope/risk. Prioritise a correct, reproducible core and clearly label incomplete modules rather than faking completeness or skipping validation.

## Strategy-design update — 2026-11-11: return-based exits, time as a maximum
The user has refined the objective: five sessions should be a maximum holding period, not a mandatory exit date or a requirement that every stock rise by a fixed amount exactly on day five. The desired strategy should seek a sensible, positive net return while avoiding both tiny uninteresting gains and unrealistic high-return assumptions.

### Proposed research framing (not yet a final rule)
- Treat each candidate trade as having three possible exit events: a take-profit target, a stop-loss/risk exit, or a maximum holding-time exit (up to five trading sessions).
- The target return and stop-loss must be tested, not guessed. Do not assume 5%, 10%, or any other fixed number is optimal.
- Test a small, predeclared grid of take-profit and stop-loss settings on chronological validation data only. Include a no-fixed-profit-target / time-exit baseline.
- Consider volatility-scaled barriers (e.g. multiples of recent ATR or rolling volatility) alongside fixed percentage barriers. ATR means Average True Range, a measure of typical price movement. Volatility scaling may make thresholds more comparable between calm and volatile stocks, but is only a hypothesis.
- For daily OHLC data, if both take-profit and stop-loss are crossed within the same candle, their order is unknown. Use intraday data or a conservative assumption (count the adverse exit first) and document it; never assume the favourable sequence.
- Model target may be framed as probability of reaching a specified net-return barrier before a stop barrier within five sessions, or as the distribution/expected value of forward returns. Choose after comparing simple baselines and data feasibility. A raw regression prediction is not a probability.
- Report net expectancy (average net profit per trade), win rate, average win/loss, profit factor, drawdown, Sharpe, trade frequency, exposure, and uncertainty. Optimise for a robust net risk-adjusted objective, not win rate alone.
- Threshold search creates overfitting risk. Use validation/walk-forward folds for selection, keep the final chronological test untouched, and account for multiple configurations tested.
- There is no universal profit target that maximises profit for all stocks and market regimes.

### Evidence leads
- Lo & Remorov (2017), “Stop-loss strategies with serial correlation, regime switching, and transaction costs,” Journal of Financial Markets. Their U.S. stock study reports tight stop-loss rules can underperform buy-and-hold after transaction costs due to excessive trading; outcomes depend on return autocorrelation/regimes. DOI: https://doi.org/10.1016/j.finmar.2017.02.003
- Kaminski & Lo (2014), “When do stop-loss rules stop losses?”, Journal of Financial Markets. Theoretical and empirical results indicate stop-loss value depends on return dynamics; under random-walk assumptions, stop-loss rules can reduce expected returns, while momentum conditions may change outcomes. DOI: https://doi.org/10.1016/J.FINMAR.2013.07.001
- Dai et al. (2020), “Risk reduction using trailing stop-loss rules,” International Review of Financial Analysis. Trailing stops reduced downside risk in their study but had lower mean returns than a mean-variance benchmark; transaction costs weakened tight rules. DOI: https://doi.org/10.1111/irfi.12328
- NSE India lists statutory charges/levies for equity trades; use current official charges and a chosen broker tariff when modelling costs. https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies
These papers are not evidence of a best Indian-equity target for Northgate; their markets, instruments, and assumptions differ.

### Research sequence
1. First calculate the empirical distribution of 1–5 session forward returns and realised volatility for a broad, feasible Indian stock sample.
2. Measure how often different gross return barriers are reached within five sessions, how long they take, and adverse excursion before exit.
3. Add transaction costs and slippage; discard thresholds whose gross edge disappears net of costs.
4. Compare fixed-percentage barriers with volatility-scaled barriers on chronological validation folds.
5. Select a simple robust rule, freeze it, and report final out-of-sample results without retuning.

## Universe and model breadth
- The PRD's 8–15 stocks are a starting project scope, not a universal statistical optimum. A broader research universe can improve cross-sectional coverage if reliable point-in-time data and compute/time permit.
- Do not expand merely to claim "more data". More tickers add observations but also sector correlation, survivorship, symbol-history and data-quality complexity. Start with a manageable liquid universe, validate the pipeline, then expand systematically.
- Test model families in stages: naive baseline first; simple linear/logistic baseline next; tree-based model next; one sequence model (e.g. LSTM/GRU) only if the simpler models show useful signal. Add remaining PRD architectures if time permits or if comparison is a deliverable. No need to train all eight simultaneously.
- Model selection is based on identical chronological out-of-sample comparisons and net strategy utility, not training accuracy or popularity.

### Next action
Research/measure Indian stock return and volatility distributions for the proposed maximum five-session window before selecting take-profit/stop-loss thresholds. Do not lock 5% or 10% now.
