# Data Research Plan — India-First

Updated: 2026-11-11  
Status: candidate sources identified; no final dataset specification or bulk download.

## Market and universe
- Research focus: Indian equities.
- NIFTY 50 is a candidate starting universe, not a final stock list.
- The PRD calls for 8–15 liquid large-cap equities plus a broad-market benchmark.
- Avoid survivorship bias: today's constituents may not represent historical membership. Prefer point-in-time constituents where accessible; otherwise document the limitation.
- Benchmark candidate: NIFTY 50 Total Returns Index (TRI), which includes dividends. Verify series availability and terms before selection.

## Required data fields
For each instrument and trading session, verify:
- Date/session and instrument identifier.
- Open, High, Low, Close, Volume.
- Adjusted price series or documented corporate-action treatment.
- Benchmark series.
- Timestamped financial news and relevant macroeconomic series, as required by the PRD.

## Candidate sources to verify
- NSE All Reports: https://www.nseindia.com/all-reports
- NSE End-of-Day/Historical Data subscription information: https://www.nseindia.com/static/market-data/eod-historical-data-subscription
- RBI Database on Indian Economy: https://data.rbi.org.in/
- yfinance is listed in the current project dependencies, but its Indian-equity coverage, adjustment behaviour, history, and repeatability must be tested before relying on it.

Do not assume official long-range NSE history or third-party adjusted data is free. Check coverage, terms, field definitions, and reproducibility.

## Data validation
1. Confirm date coverage and trading calendar.
2. Check missing sessions, duplicate dates, OHLC consistency, volume anomalies, symbol changes, and corporate actions.
3. Do not back-fill prices or silently create observations.
4. Preserve raw files separately from cleaned data.
5. Record source, retrieval time, date range, transformations, and exclusions.
6. Align all features to the time they would have become available.

## News and macro data
News/event information is part of the PRD scope, but providers, coverage, historical access, and modelling approach are not selected. Company announcements and targeted contextual news are a research direction to evaluate, not a final architecture.
For all time-sensitive information, retain publication/filing timestamps. Information released after the market close must not influence that day's simulated decision.

## Research reference
“Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques” (2022): https://doi.org/10.1080/08839514.2022.2111134
See `docs/RESEARCH_PAPER_REVIEW.md` for the paper-specific notes and limitations.

## Current recommendation
Run a small data-source feasibility pilot before selecting the final universe or downloading the full history. Verify target/horizon and evaluation rules before feature engineering and model training.
