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
- Additional multi-day forecast horizons beyond the confirmed next-session adjusted-close target.
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


## Chronological evaluation split — agreed 2026-11-13
For the first next-session forecasting dataset, use target-date-based chronological partitions:
- Training: target dates through 2023-12-31.
- Validation: target dates after 2023-12-31 and before the final six-calendar-month test cutoff.
- Final test: target dates in the last six calendar months of available labelled data. Calculate the cutoff from the latest target date rather than hard-coding it.

The currently reported latest target date is 2026-11-09, so the calendar cutoff is 2026-05-09; the first observed test target session should be the next eligible trading session. Assign by target date (not only feature date) because that is when the prediction outcome becomes known. Keep test results untouched until model choices are frozen. Fit all learned preprocessing on training data only. Exclude every `target_*` column from model inputs. This protocol covers the existing one-session target only; multi-day horizons and their purge/embargo rules remain open.


## PRD v1.0 requirements reference and dataset audit (2026-11-13)

The original 30-page PRD v1.0 has now been supplied in the Northgate project context. A traceable condensed requirements reference is committed as `docs/PRD_REQUIREMENTS.md`. The PRD's full data contract includes 8–15 equities plus benchmark, 8–10 years daily OHLCV/adjusted close, market/volatility indices, macro series, timestamped company and broad-market news, four classical models, four deep architectures, FinBERT/VADER, portfolio optimisation, recommendations, seven dashboard panels and a 10–15 page report.

The uploaded market panel was independently inspected in this conversation: 29,484 rows, ten provisional Indian equities plus ^NSEI, with OHLCV/adjusted-close and corporate-action columns. The uploaded CPI workbook has 31,460 rows for base-2024 Current data from Jan 2025 through Oct 2026 in the inspected records. Neither upload has been committed as a raw binary data file to GitHub. The user's previously reported feature panel, labelled dataset and split CSVs are not in the GitHub repository.

A reproducible GPU-laptop preparation script is now committed to regenerate the first price/volume-only dataset. This is baseline-trainable but not full PRD-complete. Macro/news/sentiment and point-in-time universe limitations remain. See `docs/DATASET_INVENTORY.md` and `docs/GPU_LAPTOP_SETUP.md`.

## Research continuation — 2026-11-14

Expanded the official/free data-source search without relying on user-specific access or academic sponsorship.

### New evidence
- Extracted actual values from MoSPI's 10-Nov-2026 PLFS quarterly bulletin: CWS age 15+ combined LFPR 55.5%, WPR 52.7%, unemployment 5.1%; rural/urban splits and five quarters of context recorded in DATA_RESEARCH.md.
- Identified official RBI DBIE daily USD/INR interbank table (Aug-2000 to Jun-2026, OHLC + RBI reference rate) and RBI daily call/notice money rates as a useful short-term liquidity source. A daily official 10Y generic G-Sec yield endpoint remains unconfirmed.
- Identified broad public EOD dataset candidates (aswinv90, TejHQ, NSEDATA4ME), historical index-membership reconstructions, official NSE corporate-action CSV and trading calendar, NSE breadth archives, FRED/ALFRED vintage API and GDELT GKG 2.1.
- News search found multiple Indian sentiment-labelled corpora, but none yet supplies a complete, verified 8–10-year Indian company-specific timestamped article archive. GDELT GKG metadata is the strongest historical open candidate, but full archive is too large to mirror locally.
- Identified NSE terms that restrict systematic automated collection; documented source-rights cautions. Public website visibility or a third-party mirror is not proof of a licence for automated ingestion or redistribution.

### Research status / limitations
No new raw Parquet/CSV/API data files were downloaded or merged in this session. PLFS quarterly figures are manually extracted from an official published bulletin; all other newly identified sources remain candidates pending bounded sample retrieval and QA. Do not claim the PRD data layer is complete.

### Next research sequence
1. Test bounded official RBI DBIE exports (daily USD/INR, daily call/notice money, key rates) and preserve original raw files/retrieval metadata.
2. Test a bounded MoSPI PLFS API metadata/data request; keep monthly and quarterly tables separate.
3. Compare a small set of Northgate's 10 symbols and NIFTY 50 against one survivorship-aware public EOD candidate, including corporate-action and date-gap checks.
4. Inspect historical NSE corporate-action exports and point-in-time index-membership reconstruction against original circulars.
5. Pilot GDELT GKG queries for selected Indian issuers, measuring entity precision, timestamp availability and data volume before any broader pull.
6. Extend FRED retrieval to ALFRED vintage-aware observations; keep latest-value graph CSVs explicitly non-PIT.
