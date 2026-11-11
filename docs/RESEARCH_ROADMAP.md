# Research Progress — Northgate Stock Predictor

Updated: 2026-11-11

## Purpose

This file preserves research continuity across conversations. It records **which sources we are reviewing, what each source is intended to teach us, and the verified progress/findings**. It is not a prompt library, tutorial, or place to store every brainstorming idea.

## Research discipline

- Findings must be grounded in the specific paper or source being reviewed.
- Do not fill gaps with assumptions or general knowledge. If the source does not state something, record **“Not stated in source.”**
- Record page, section, table, figure, or appendix references for important findings.
- Distinguish source findings from Northgate interpretations and decisions.
- Do not mark a source reviewed until the full accessible material has been examined. If only an abstract is available, record that limitation.
- No research finding becomes a project decision until its relevance to Northgate is discussed and explicitly agreed.

## Current research phase

### Phase 1 — Training dataset design

**Purpose:** establish what data Northgate should train on: company universe, number of companies, historical coverage, observation frequency, target variable/horizon, predictor characteristics, and missing-data/universe-selection treatment.

| # | Source | Why we are reviewing it | Status |
|---|---|---|---|
| 1 | Lalwani & Meshram (2022), [The cross-section of Indian stock returns: evidence using machine learning](https://doi.org/10.1080/00036846.2021.1982132) | India-specific evidence: universe construction, firm count, survivorship-bias treatment, 35 stock characteristics, return target and out-of-sample design. | Not yet reviewed |
| 2 | Gu, Kelly & Xiu (2020), [Empirical Asset Pricing via Machine Learning](https://doi.org/10.1093/rfs/hhaa009) — [NBER full-text PDF](https://www.nber.org/system/files/working_papers/w25398/w25398.pdf) | Large cross-sectional panel: number of stocks and observations, pooled learning design, predictor set, publication lags, missing data and training timeline. | Not yet reviewed |
| 3 | Fieberg et al. (2023), [Machine learning techniques for cross-sectional equity returns’ prediction](https://doi.org/10.1007/s00291-022-00693-w) | Sparse predictor design, missing-data considerations, overfitting controls, cross-sectional universe breadth and large-cap subset comparison. | Not yet reviewed |
| 4 | Chen, Pelger & Zhu (2024), [Deep Learning in Asset Pricing](https://doi.org/10.1287/mnsc.2023.4695) | Dataset structure for deep-learning asset pricing: assets, dates, frequency, targets, firm characteristics, macro inputs and out-of-sample design. | Not yet reviewed |
| 5 | [Stock picking with machine learning](https://doi.org/10.1002/for.3021) | Optional comparison of a weekly pooled stock-selection design and its training-window/data choices. Review only if the full paper is accessible. | Optional — not yet reviewed |

### Phase 1 progress log

| Date | Source / activity | Verified progress | Open questions / limitations |
|---|---|---|---|
| 2026-11-11 | Research set selected | Five candidate papers identified for dataset-design research; four are the core set and one is optional. No paper has yet been fully reviewed in this research phase. | Full-text access and exact source findings remain to be checked. |

### Phase 1 questions to resolve

1. Should Northgate train a pooled model across companies, separate models per company, or compare both?
2. What number and diversity of companies are defensible for the intended model and dataset?
3. Is the PRD's 8–10-year daily history sufficient, and what are the trade-offs of daily versus weekly/monthly observations?
4. What target should be modelled: raw/adjusted price, simple/log return, excess return, or another target?
5. What forecast horizons are supported by the intended use and evidence?
6. Which company characteristics, market variables, macro variables and technical features are actually justified?
7. How should point-in-time universe membership, delisted companies, publication lags and missing observations be handled?
8. What limitations will remain if a survivorship-free Indian dataset is unavailable?

**Phase 1 is not complete** until findings from the accessible sources have been compared and the unresolved questions are explicitly listed. No company count, target, horizon, or dataset design is approved yet.

## Later research phases

These are scope headings only. Add specific sources and progress when each phase begins.

- **Phase 2 — Training and validation:** chronological splits, walk-forward validation, leakage, lookback windows, batches, epochs, early stopping and tuning.
- **Phase 3 — Prediction models:** Linear/Ridge, Random Forest, XGBoost, SVR, LSTM, GRU, BiLSTM and Transformer; suitability, data needs, tuning and limitations.
- **Phase 4 — Financial features/statistics:** indicators, returns, stationarity, volatility, feature selection and macro/fundamental data timing.
- **Phase 5 — News and sentiment:** deployable hosted models/APIs, reusable repositories, official announcements, timestamped news and optional public investor sentiment.
- **Phase 6 — Decision/risk methods:** BUY/HOLD/SELL evaluation, stop-loss and trailing-stop research, transaction costs, holding periods and portfolio optimisation.
- **Phase 7 — Practical system:** cloud scheduling, hosted inference, data pipelines, costs, dashboard, reproducibility and reporting.

## How to update this file

After a source is reviewed in chat, update only:
1. That source's status.
2. A concise dated progress-log entry with findings that were actually extracted and their source locations.
3. Remaining unanswered questions or access limitations.
4. Any decision only after the user explicitly agrees to it.

Do not paste research prompts, full paper summaries, speculative architecture ideas, or unverified conclusions into this file.
