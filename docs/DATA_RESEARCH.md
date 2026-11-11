# Data Research Plan — India-First

Updated: 2026-11-12  
Status: initial market dataset downloaded and processed locally; macro and timestamped news/sentiment source selection remains pending.

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
- yfinance was used for the initial local download. User reports 29,484 rows across 10 provisional equities plus the NIFTY 50 price index, covering 2016-01-01 to 2026-11-09 for stocks (NIFTY starts 2016-01-04). This is a provisional source, not archival-grade validation; corporate-action adjustment, expected-session completeness, survivorship bias and terms remain limitations to document.

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

## Current implementation update (2026-11-12)
- Initial Yahoo Finance market panel and 24 backward-looking features have been generated locally by the user.
- First next-session supervised dataset generated: 29,473 rows across 11 instruments, with user-reported target integrity checks passing.
- The 10 equity tickers are provisional; `^NSEI` is the NIFTY 50 price index, not TRI and not an investable stock. Current index constituents create survivorship-bias limitations.
- Macro and timestamped news/sentiment datasets have not yet been prepared.

## Current recommendation
Proceed with macro/market data and timestamped news/sentiment collection. Before merging, verify source coverage, licensing/usage terms, historical availability and timestamps. Treat revised macro releases and after-close news as available only from their actual publication time. Compare sentiment features incrementally against a price/volume-only baseline on identical chronological dates. The exact multi-day forecast horizons remain open.
