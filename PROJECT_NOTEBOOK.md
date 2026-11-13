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

## Research continuation — 2026-11-14 (additional source verification)
- RBI monthly government-security yield curve: monthly 1–30 year residual maturities from Apr-1996 to Aug-2026 (RBI DBIE report 1368 / Handbook Table 217). This offers a legitimate low-frequency candidate, but the daily generic 10-year benchmark remains unresolved. Never interpolate monthly yields to daily observations.
- RBI daily call/notice money rates are documented in official daily statistics (weighted averages, ranges and turnover); a long-history machine-readable daily export was not acquired.
- Official MoSPI PLFS MCP code documents the /api/plfs/getData workflow and monthly (Apr-2025–Sep-2026, All India, indicators 1–3) versus quarterly frequency rules. No API data rows were retrieved in this pass.
- NSE official India VIX page exposes custom date ranges and CSV download with OHLC/change fields; actual historical export remains unacquired.
- TejHQ is the strongest immediately inspectable private-research cross-check candidate, but provider terms acknowledge no exchange licence and prohibit raw redistribution; NSEDATA4ME and historical-membership reconstructions remain unverified candidates. Existing Northgate panel remains unchanged.
- No new raw data was downloaded or merged. The public-source route does not depend on an academic institution or user-side contact.

## Research continuation — 2026-11-14 (TejHQ and NSE source audit)
- TejHQ's current landing page describes raw NSE/BSE bhavcopy, corporate actions, back-adjusted prices, ISIN symbol history and derived metrics; its claimed monthly top-500 liquidity universe could support survivorship-aware research if the historical membership logic is independently verified.
- TejHQ reports only 89% of 25k Yahoo close comparisons within ±1%. This is not independent QA. Compare raw closes against exchange-origin bhavcopy, then compare adjusted values only after aligning dividend/split/demerger conventions.
- TejHQ's landing page calls the Parquet data MIT/open, but its dedicated data terms say MIT covers code only, no exchange licence exists, personal model training/local retention is permitted, raw redistribution is not, and exchange terms apply. Treat as private-research candidate only and preserve this conflict.
- NSE's All Reports page indexes a VIX sample with date-range mismatch and a duplicate preview row; actual CSV and archive coverage remain unverified. India VIX is 30-calendar-day implied volatility from NIFTY options, not realised volatility.
- PLFS MCP metadata rules reconfirmed: annual 1, quarterly 2, monthly 3; monthly Apr-2025–Sep-2026 All India indicators 1–3; one indicator_code per request.
- Google BigQuery's documented 1 TB/month free query processing allowance could support a bounded GDELT GKG pilot with strict bytes-scanned limits.
- No raw data was downloaded or merged in this pass.


## Research continuation — 2026-11-14 (NSE bhavcopy and PLFS release calendar)
- Confirmed the official NSE All Reports page lists the final CM-UDiFF Common Bhavcopy ZIP/CSV and Full Bhavcopy + Security Deliverable CSV. NSE states older CM Bhavcopy CSV formats were discontinued from 08-Jul-2024. This creates a clear official post-transition candidate but requires schema inspection and a pre/post-transition compatibility plan.
- The NSE Historical Reports directory lists historical India VIX, index, TRI and valuation archives. The dedicated VIX page has date-range controls and CSV export; an unfiltered “No Records” view is inconclusive. No raw file acquired.
- MoSPI's October-2026-updated release calendar schedules the October monthly PLFS bulletin for 15-Nov-2026. This is a future scheduled date as of 14-Nov, not a verified publication. Keep it separate from the July-Sep quarterly bulletin and MCP API series.
- No raw observations downloaded, validated or merged. No change to market panel, splits or model status.


## Research continuation — 2026-11-14 (TejHQ revision/terms audit)
- Hugging Face search now shows a 7.36M-row NSE price subset and a commit dated 2026-11-09 that updates NSE/BSE 2026 price Parquet files. The current card describes seven data trees including raw/adjusted prices, corporate actions, symbol history, derived metrics, liquidity universe and delivery data.
- The opened viewer and card contain conflicting snapshots: MIT badge vs specific TejHQ terms, 8.33M corporate-action rows vs 7.36M NSE price rows, and older card language that says corporate actions/adjusted close are not yet available. Coverage and layout also differ across snapshots. Do not merge those statements into one stable manifest.
- TejHQ's specific 2026-11-08 terms say MIT covers code only, no exchange licence/clarification exists, personal private research/model training/local storage is allowed by TejHQ, raw data redistribution is prohibited, and exchange terms still apply. This supersedes the generic HF licence badge for practical handling.
- No Parquet file downloaded or validated. Next: pin the 2026-11-09 revision, inspect file tree and schema, then test one bounded yearly or daily partition against independently sourced NSE bhavcopy.


## 2026-11-14 — Continued data-source audit

- Live TejHQ Hugging Face tree now displays verified 2026-11-11 revision short hash `10bd698`, ~1.25 GB, with annual NSE adjusted Parquet files from 2010–2026. This supersedes the earlier 2026-11-09 candidate snapshot for further inspection, but the full revision hash and raw tree path must be resolved before acquisition.
- TejHQ's public pipeline README appears stale against the live dataset tree (five trees/2024 start vs seven trees/2010+ adjusted partitions). The README's corporate-action back-adjustment process is retrospective; historical backtests must not assume today's adjusted prices were available at the time.
- NSE All Reports confirms CM-UDiFF final ZIP and separate new-format readme workbook; legacy CM CSV discontinued 2024-07-08. UDiFF guidance establishes general CSV/ISO date/ASCII/compression rules, not the exact CM field mapping.
- No raw data downloaded, compared, validated or merged. No model trained. Next: pin full HF revision and inspect a small raw partition; separately inspect official NSE readme/sample.


## Research log — 2026-11-14 (TejHQ parser and adjustment review)
- Confirmed current public dataset card and README agree on NSE 2010-01-04 onward, BSE 2024-07-08 onward, seven trees and annual raw NSE Parquet layout.
- Inspected public parser, instrument-chain and adjustment code. Legacy NSE schema is handled separately; pre-2012 ISIN/trades nulls are intentional. ISIN continuity uses a same-symbol <=30-day heuristic. Adjustment factors cover splits, bonuses and dividends; demerger/merger/rights/buyback/other remain unadjusted (factor 1.0), and missing dividend inputs also fall back to 1.0.
- Back-adjusted history is revised when later corporate actions are added. Preserve PRD target but explicitly test whether an absolute adjusted-close target creates scale/revision issues; return-ratio representation may be an experimental comparator only.
- Provider's Yahoo adjusted-close reconciliation (96.88%, 25,329 comparisons, 48/50 symbols, 2024-01-01 to 2026-05-06) is not independent exchange-source validation and has convention exceptions (TRENT, ITC).
- No data download, raw NSE comparison, test execution, panel update or model training. Full HF revision SHA not yet pinned.


- Freshness correction: subsequent live-tree check shows TejHQ's newest observed publication is 2026-11-12 (raw NSE tree short hash `d6f1912`; adjusted NSE 2024 file short hash `8b77c06`). The prior 2026-11-11 note is superseded. Full commit SHA still unavailable, so revision pin remains incomplete.


- Additional pipeline QA notes: TejHQ transform includes NSE EQ/BE/BZ by default, drops zero-volume rows, and deduplicates on (date,symbol) keeping first; low>0 and non-negative turnover/trades are not explicit invariants, and no rejected-row audit output is described. Need a Northgate series/zero-volume policy and raw-vs-cleaned row audit before adoption.

- Target universe coverage check: TejHQ pages report all ten Northgate equities beginning before 2016 (nine on 2010-01-04; INFY on 2011-06-29). Provider pages are not row-level validation. Latest displayed page dates differ between 2026-11-11 and 2026-11-12, requiring API/raw confirmation.
- Rights/format check: TejHQ terms permit individual research/backtesting/local storage but say no exchange licence, MIT is code-only, raw redistribution is prohibited, and exchange terms apply. HF search metadata says exchange-public-data while cached page says mit; do not infer data rights from the badge. NSE UDiFF official page lists catalogue v1–v4 and CM sample files; Circular 62424 confirms 2024-07-08 cutover. Binary sample retrieval failed, so field-level reconciliation remains open.
- No API data or Parquet downloaded, no official sample acquired, no data comparison run, no panel changed, no model trained.

- Target-specific events strengthen the corporate-action caveat: ITC demerger 2025-01-06; HINDUNILVR demerger 2025-12-05; RELIANCE demerger 2023-07-20 and rights 2020-05-13; BHARTIARTL rights 2019-04-23 and 2021-09-27. Current TejHQ factor code leaves rights/demerger at 1.0. Test event windows before adjusted-close labels are accepted.


## NSE official data access research (2026-11-14)
NSE's Data for Research page, updated 04-Nov-2026, offers an official application route for academic/non-commercial research. Requests are sent with a Data Seeking Request Form to nseri@nse.co.in. NSE's disclaimer restricts research data access/download to individuals from accredited academic institutions, recognised research organisations and think tanks; an NDA involving the researcher/parent institution may be required, and periodic progress reporting may be imposed.

SEBI Circular 2024/178 provides a two-basket data-sharing framework. NSE's published Basket 1 list includes daily security-wise OHLC/turnover, Bhavcopy archives, historical index data, FII/FPI/DII activity, financial results, shareholding, corporate announcements and corporate actions. Up to 2 GB per researcher/year is the reasonable free amount where no extra computation is required; high-volume or processed data may be charged. NSE classifies voluminous historical EOD/Bhavcopy and corporate data as chargeable above 2 GB. Basket 2 includes identifiable/re-identifiable client data and is unnecessary for this project.

The older NSE Data Sharing & Usage Policy definition mentions students/researchers among non-commercial users, but the current Data for Research disclaimer sets an institutional eligibility condition. Do not assume individual student eligibility. Written confirmation is needed. No request was sent, no eligibility or licence was confirmed, and no data was received. This is an official-source candidate, not a verified dataset.


## Official historical-data page audit (2026-11-14)
Official NSE pages expose several potentially useful manual CSV routes:
- Security-wise Archives: per-symbol/series date filters, up to 5Y preset plus Custom, with OHLC, VWAP, traded quantity, turnover, trades, deliverable quantity and delivery percentage.
- Corporate Actions: company/purpose/date filters and CSV, including ex-date, record date and book-closure dates. Ex-date does not reveal when an announcement first became public.
- NIFTY Indices Historical Data: date-range selection and CSV, including separate Total Returns Index and Net Total Return Index values. This is a candidate official benchmark series.
- India VIX: date-range presets and Custom with CSV.
- FII/FPI and DII: separate NSE-only and combined-exchange CSV downloads; aggregate market context only, not stock-level flows.
- Historical All Reports: date-filtered CM UDiFF ZIP and related Bhavcopy/delivery reports; old CM CSV formats discontinued from 08-Jul-2024.

These pages demonstrate that official UI routes exist, but not that every date/symbol is covered, that a full 2016–2026 history is freely downloadable, or that scripted retrieval is permitted. No files were downloaded or validated. Use manual UI or approved research access; do not reverse-engineer protected endpoints.

## Follow-up on official market-data coverage (2026-11-14)

- NSE Indices' official NIFTY 50 whitepaper states NIFTY 50 Total Return values are available from 30-Jun-1999. The historical UI exposes both TR and Net TR with date-range CSV. Since a total-return benchmark includes reinvested dividends, it is the stronger candidate for portfolio-performance comparison than the current price-only ^NSEI series. Do not replace the existing benchmark until the CSV, definition, availability and terms are checked.
- NSE's 19-Jul-2010 press release establishes India VIX dissemination before Northgate's 2016 start. The historical page exposes Custom/CSV, but daily coverage has not been downloaded or verified. India VIX is implied expected volatility over the next 30 calendar days, not realised volatility.
- An official NSE ITC Corporate Actions result contains 20 records reaching 2015, including a bonus and dividends, plus the 06-Jan-2025 demerger. This is useful evidence for one ticker only. Ex-date is not the announcement publication time; retain filing/dissemination timestamps for point-in-time event features.
- NSE labels FII/FPI flow as provisional and subject to custodial confirmation/modification. The report is aggregate category-level flow, not stock-level activity. Historical vintages should not be overwritten if the series becomes a feature.
- NSE discontinued legacy CM Bhavcopy CSV formats effective 08-Jul-2024 and directs users to CM-UDiFF Common Bhavcopy Final ZIP. Any stitched history must document schema transition and validate comparable fields across the boundary.
- No official files were downloaded; no additional data was ingested or validated. The model-training and backtesting state is unchanged.


## Target-universe corporate-action spot-check (2026-11-14)

Official NSE/MSEI pages confirm representative event dates across the provisional universe: HINDUNILVR demerger 05-Dec-2025; ITC demerger 06-Jan-2025; HDFCBANK 1:1 bonus 26-Aug-2025; RELIANCE 1:1 bonus 28-Oct-2024 and rights documentation in May 2020; BHARTIARTL rights 19:67 on 23-Apr-2019 and 1:14 on 27-Sep-2021 (MSEI action table). Current NSE pages also show dividend events for ICICIBANK, LT, SUNPHARMA and TCS. This is a spot-check, not a complete corporate-action history; INFY remains unverified in this pass.

NSE integrated filings include Original/Revision labels and separate broadcast/revised timestamps. For point-in-time features, preserve each revision as a new event with its own timestamp. Do not backdate corrected information.

Before training, run an event-window audit around every rights, bonus and demerger: compare raw Close, Adj Close, dividend/split metadata and the forward adjusted-close label for at least two sessions before and after the ex-date. Do not assume vendor adjustment logic correctly represents rights/de-merger economics. No action CSVs or filing attachments were acquired in this pass, and no labels were modified.
