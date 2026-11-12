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


## Macro and news source research — 2026-11-13
These are research candidates, not final provider decisions. Coverage, terms, revision history and reproducible access still require a local pilot.

### Indian macroeconomic and market-context candidates
- **MOSPI eSankhyiki CPI API** — official CPI/inflation endpoint. The published API description covers CPI base years 2010, 2012 and 2024; it is described as open, with bearer token optional and per-IP rate limits. Endpoint documented as `/api/cpi/getCPIData`. Need inspect the OpenAPI schema and test pagination, date coverage, base-year breaks and release dates before use. Source: https://esankhyiki.mospi.gov.in/macroindicators?product=cpi&tab=api
- **MOSPI eSankhyiki IIP API** — official industrial-production endpoint documented as `/api/iip/getIIPData`. Parameters, historical depth, revisions and release timestamps remain to be verified. Source: https://esankhyiki.mospi.gov.in/macroindicators?product=iip&tab=api
- **RBI Database on Indian Economy (DBIE)** — official historical repository; RBI says it contains time-series data and publications across national income, prices, money, banking, markets, public finances and foreign trade. DBIE is at https://data.rbi.org.in/. RBI's Data Releases page also exposes daily, weekly, monthly, quarterly and annual releases: https://www.rbi.org.in/scriptS/Statistics.aspx. Export format, automation, historical depth and actual release timestamps must be tested series by series.
- **NSE India VIX historical page** — NSE exposes a custom-period historical page with CSV download. A web snapshot displayed no records, so availability and automated retrieval are not yet verified. Source: https://www.nseindia.com/reports-indices-historical-vix
- **NIFTY Indices historical data** — official portal exposes historical index values and a separate Total Returns Index/Net Total Returns Index report. This is worth investigating for benchmark TRI rather than relying only on the downloaded NIFTY price index. Source: https://www.niftyindices.com/reports/historical-data

### News and event candidates
- **GDELT 2.0** — strongest no-key research candidate so far. Official project documentation describes 15-minute updates and a historical archive beginning in February 2015; the GKG provides article-level entities/themes/tone and a publication timestamp, while event data has a separate DATEADDED field that should be used as the time GDELT first observed the item. The archive is very large (the 2015 GKG alone has been reported at multi-terabyte scale); do not attempt a full archive download. Start with a small date/ticker pilot and test whether relevant Indian company stories are captured. Preserve original publication time, GDELT first-seen time, URL, language/translation status, source and duplicate/story identifiers. Sources: https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/ ; https://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf ; https://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf
- **NewsAPI.org free Developer plan** — unsuitable as the main historical backfill: its official pricing page says search is limited to articles up to one month old, has a 24-hour delay and 100 requests/day; use is limited to development/testing. Source: https://newsapi.org/pricing
- **Alpha Vantage News & Sentiment** — API documentation describes historical news/sentiment queries, but explicitly marks the NEWS_SENTIMENT endpoint as premium. Not a zero-budget default. Source: https://www.alphavantage.co/documentation/
- **NewsAPI.ai** — free allowance is a finite 2,000 searches; historical archive access is a paid-tier feature according to its pricing page. Not selected for the full backfill. Source: https://newsapi.ai/plans

### Point-in-time rules for every macro/news feature
1. Store at least `observation_period`, `published_at` or `released_at`, `first_seen_at` (where supplied), `retrieved_at`, `source`, and `revision/version` where available.
2. Never join a macro observation to dates before its actual public release. The month/quarter being measured is not its availability date. If historical release timestamps or vintage values cannot be recovered, either lag conservatively and disclose the limitation, or exclude the series from leakage-sensitive backtests.
3. For news, use the earliest defensible public publication timestamp; where the data provider only supplies a crawl/first-seen time, use that as a conservative availability timestamp. Convert timestamps consistently to Asia/Kolkata and map after-market-close items to the next eligible NSE session.
4. Deduplicate syndicated/repeated stories before calculating daily article counts or sentiment. Keep article-level raw records separate from derived daily ticker features.
5. Evaluate price/volume-only and price/volume-plus-context models on the same dates. Do not assume sentiment adds predictive value.

### Current research recommendation (not yet a user-approved decision)
Pilot MOSPI CPI, one RBI series, NSE India VIX, and a small GDELT company-news sample before bulk collection. Do not download the complete GDELT archive. If the pilot cannot establish reliable point-in-time timestamps and relevant coverage, report the limitation rather than manufacture a 10-year sentiment history.
