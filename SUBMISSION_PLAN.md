# Northgate — Submission Plan (Priority File)

Updated: 2026-11-12  
Status: ACTIVE WORKING PLAN — this file is the current execution checklist until the submission.

> Keep the immediate work focused on building a reliable PRD-aligned submission. Do not expand into the broader research vision unless the user explicitly asks. Preserve unresolved choices as open questions; do not silently convert suggestions into decisions.

## Immediate objective

Build and verify the data foundation first, then proceed to baseline modelling and the remaining PRD deliverables in the time available. The recorded deadline is 15 November 2026. The complete PRD may not be achievable to its intended standard by that date; report what is actually completed and what remains incomplete.

## Data pipeline — execution order

1. **Confirm universe and benchmark**
   - Select 8–15 liquid Indian equities across sectors and one broad-market benchmark (candidate: NIFTY 50).
   - Exact tickers and benchmark series remain unconfirmed.
   - Keep training universe, prediction coverage, and portfolio universe conceptually distinct; do not claim generalisation to unseen stocks without a dedicated test.

2. **Run a small data-source pilot**
   - Test a small number of representative tickers plus the benchmark before bulk collection.
   - Verify historical coverage, available columns, adjusted-price behaviour, date/time conventions, symbol changes, and repeatability.
   - Record provider limitations and terms. Do not assume a free source is complete or archival-grade.

3. **Download and preserve raw data**
   - Target the PRD's 8–10 years of daily OHLCV and adjusted-price history.
   - Keep source downloads immutable under `data/raw/`; record provider, retrieval timestamp, ticker, date range, and download status.
   - Do not overwrite raw files during cleaning.

4. **Validate raw data**
   - Check schema, date parsing, duplicate dates, sort order, missing observations, OHLC consistency, non-positive prices, volume anomalies, and adjusted-price availability.
   - Distinguish exchange holidays/non-trading days from missing data.
   - Do not fabricate or interpolate market prices to force a complete calendar.
   - Produce a per-ticker data-quality report.

5. **Clean and standardise**
   - Apply documented, deterministic cleaning rules.
   - Standardise column names, ticker identifiers, dates, and numeric types.
   - Keep exclusions and unresolved gaps visible in the report.

6. **Build the processed panel**
   - Combine cleaned observations into a ticker-aware dataset under `data/processed/`.
   - Preserve ticker and date keys; never mix one ticker's rows into another ticker's calculations.
   - Prefer Parquet if the environment supports it; CSV is an acceptable fallback.

7. **Engineer features**
   - Add backward-looking returns, lagged returns, trend/momentum, rolling volatility, and volume features.
   - Calculate features separately within each ticker.
   - Ensure every feature uses only information available at its timestamp.
   - Fit learned preprocessing/scalers on training data only, not on the full dataset.

8. **Define the prediction target**
   - The PRD discusses next-day adjusted close and next-day log return; the final target/horizon is not yet approved.
   - Resolve and document target, forecast timestamp, and signal timing before model training.
   - Keep target construction separate from features to make leakage checks possible.

9. **Verify and freeze the data foundation**
   - Rerun the pipeline and compare outputs.
   - Save data manifest, quality report, feature schema, and reproducible run instructions.
   - No model-training claim until data checks and target definition are verified.

## After the data pipeline

1. EDA: distributions, stationarity checks, volatility, correlations, volume, missingness.
2. Finance calculations: returns, volatility, covariance, beta, Sharpe, drawdown; verify manual linear regression/gradient descent against a library implementation as required by the PRD.
3. Establish naive/random-walk baseline.
4. Run classical ML comparisons (Linear/Ridge, Random Forest, XGBoost, SVR) using chronological validation.
5. Proceed to required deep-learning models (LSTM, GRU, BiLSTM, Transformer) only if time/data quality permit; clearly report any not completed.
6. Add sentiment/news only after price/volume baseline and timestamp alignment are reliable; compare with and without sentiment.
7. Portfolio optimisation and backtesting against equal-weight and market benchmark, including costs and turnover where feasible.
8. Recommendation layer with transparent rules and the confirmed no-forced-trade principle.
9. Streamlit dashboard reading saved outputs (no retraining on page load), report, README and reproducibility instructions.

## Non-negotiable research safeguards

- Chronological train/validation/test; walk-forward evaluation where appropriate.
- Keep final test period untouched until model choices are frozen.
- No look-ahead leakage; align after-close data/news to the next eligible session.
- Purge overlapping forward-label periods at split boundaries where relevant.
- Fit scalers and preprocessing on training data only.
- Compare models on identical dates, targets, features and baselines.
- Report MAE/RMSE and directional accuracy separately from recommendation and portfolio outcomes.
- Include realistic costs/slippage where feasible and disclose limitations.
- Never claim a model, result, test, download, or deliverable is complete unless verified.

## Confirmed user requirements and preferences

- Immediate priority is the PRD submission, not the larger post-submission research vision.
- Work quickly in small, practical steps using Terminal, Python, and GitHub; prefer free tools.
- User is a beginner at model training; explain commands and unfamiliar terms briefly.
- Preserve raw data and make the pipeline reproducible.
- No forced daily trade: the whole portfolio may receive a no-action recommendation.
- Do not sell a holding merely because another stock has a higher forecast; exits/rebalances need separate explicit rules.
- Do not promise profits or invent model performance.

## Open questions — do not guess

- Exact Desktop project-folder name/path (user will provide the exact name).
- Final ticker list and benchmark data series.
- Data provider and verified historical coverage.
- Forecast target and horizon (next-day adjusted close vs next-day log return remains unresolved).
- Training, prediction, and portfolio universe definitions.
- Scope prioritisation if all PRD deliverables cannot be completed by the deadline.

## Current verified state (2026-11-12)

- GitHub project scaffold exists.
- Market-data download executed successfully on the user's Mac: 29,484 rows across 10 provisional stocks plus the NIFTY 50 price index. Detailed quality validation remains pending.
- No model has been trained.
- No backtest/dashboard/performance result has been verified.
- Existing project status, notebook, decisions, continuity protocol, and implementation plan were reviewed before creating this priority plan.

## Working log

Append concise dated entries here after meaningful, verified progress:
- What changed.
- Commands/tests run and their actual outcomes.
- Files created/updated.
- Blockers and next action.


### 2026-11-12 — Initial Yahoo Finance downloader added
- Added `scripts/download_market_data.py` and fetched it back from GitHub to verify the saved file.
- Script requests daily OHLCV, Adj Close, dividends, and stock splits from Yahoo Finance via yfinance for 10 provisional Indian large-cap candidates plus the NIFTY 50 price index, from 2016-01-01 to the latest available session.
- Script preserves per-symbol raw CSVs, writes a combined processed panel, and creates a JSON data-quality/download report. It flags failures and basic data anomalies rather than filling or inventing prices.
- The ticker list is provisional, not a final universe decision. The downloaded `^NSEI` is the NIFTY 50 price index, not TRI; today's constituents also create survivorship-bias limitations.
- **Execution verified from user's Mac terminal output:** repository cloned to `~/Desktop/Northgate-Stock-Predictor`; Python virtual environment created and requirements installed successfully under Python 3.14; Yahoo Finance download completed for all 11 requested instruments (10 provisional stocks plus `^NSEI`), with 29,484 rows total. Each stock returned 2,681 rows from 2016-01-01 through 2026-11-09; NIFTY 50 returned 2,674 rows from 2016-01-04 through 2026-11-09. Files reported by script: `data/processed/market_panel.csv` and `reports/data_quality/download_report.json`, plus per-symbol CSVs under `data/raw/yahoo/`. These are user-reported local outputs; the assistant has not independently inspected the local files or JSON quality report.
- **Next:** inspect the locally generated JSON quality report and run additional panel-level checks. Do not yet describe the dataset as fully validated.
