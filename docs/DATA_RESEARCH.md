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

### MOSPI CPI API pilot — 2026-11-13
- User successfully fetched the official OpenAPI document and tested the CPI endpoint. The filter lookup confirmed state_code=1 = All India, sector_code=3 = Combined, and division_code=0 = CPI (General). The request with base_year=2024, series=Current, years 2025–2026, and those filters returned exactly 22 monthly records (Jan 2025–Oct 2026); this is a successful small pilot, not yet a production ingestion pipeline.
- The API response is newest-first. The 2025 index observations are present, but their inflation fields are null; 2026 inflation fields are populated. Do not fill these nulls or interpret month-on-month index changes as year-on-year inflation.
- MoSPI's official material confirms CPI 2024=100 was first released on 12 February 2026. The new series supplies index observations from January 2025, while year-on-year inflation under the new series starts in January 2026. MoSPI says old CPI 2012-series inflation is available through December 2025 and new CPI 2024-series inflation from January 2026; direct comparison across the two inflation series is not feasible because basket, weights, coverage and methodology changed. Sources: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2227012&lang=1&reg=6 ; https://www.pib.gov.in/PressReleasePage.aspx?PRID=2291051&lang=1&reg=48
- Point-in-time implication: CPI 2024 index observations for 2025 were first disseminated with the new series in February 2026. They must not be backfilled into model features for 2025 decision dates as if then-known. For a leakage-sensitive historical backtest, use the CPI 2012 series through December 2025 as the contemporaneously available series (subject to release-date alignment); use CPI 2024 observations only from their actual public release dates onward. Keep series/base-year metadata and a regime indicator; do not splice index levels or inflation rates across bases without a documented methodology and explicit evaluation of comparability.
- The official MoSPI release for October 2026 is dated 12 November 2026, with publication embargo until 4:00 PM; the API returned the October observation in the user's 13 November test. Record actual publication timestamps from official release records, not observation month-end. Source: https://mospi.gov.in/uploads/latestreleasesfiles/1794480048335-Press%20Release%20of%20CPI%20for%20October%202026%20.pdf
- Remaining checks before production use: verify historical 2012-series endpoint coverage and actual monthly release dates; determine whether API exposes provisional/final status and revisions/vintages; compare selected API rows against official monthly press releases; decide a conservative NSE-session availability rule. No CPI file has yet been committed or merged into the modelling dataset.
### MOSPI CPI 2012 headline-series filter confirmed — 2026-11-13
- User successfully queried the 2012-base headline CPI observation for January 2025. Confirmed filters: base_year=2012, level=Group, series=Current, state_code=99 (All India), sector_code=3 (Combined), group_code=0 (General), subgroup_code=0.99 (General-Overall). The API returned one row: index 193.4, inflation 4.26, status F. This confirms the filter combination for a single month; full historical coverage and release-time alignment remain untested.
- Important distinction: series=Current is the series selector; General is the group, not the series. The earlier 2024-base filter codes are not interchangeable with the 2012-base codes.
- Next validation: request a limited historical range/month-by-month sample from the 2012-base headline series, verify earliest/latest available observations and compare selected months with official MoSPI releases. Then establish each month's publication date/time and any provisional/final revision behaviour before building an as-of macro feature table. No CPI dataset has been saved or merged into modelling data.
### MOSPI CPI 2012-base full-year response confirmed — 2026-11-13
- User queried the 2012-base All India / Combined / General-Overall headline series for year=2024 with limit=100, page=1. API returned HTTP 200, `totalRecords=12`, `totalPages=1`, and all 12 calendar months (January–December 2024). All returned rows had `status=F`.
- Returned headline index / year-on-year inflation pairs (month order Jan–Dec): Jan 185.5 / 5.10%; Feb 185.8 / 5.09%; Mar 185.8 / 4.85%; Apr 186.7 / 4.83%; May 187.7 / 4.80%; Jun 190.2 / 5.08%; Jul 193.0 / 3.60%; Aug 193.0 / 3.65%; Sep 194.2 / 5.49%; Oct 196.8 / 6.21%; Nov 196.5 / 5.48%; Dec 195.4 / 5.22%. API response is newest-first.
- This verifies full-year retrieval for 2024 with one request and a page size of 100. It does not yet prove complete coverage for every year, explain `status=F`, or establish when each observation became publicly available. No macro dataset has been created or merged into the modelling dataset.
### MOSPI CPI 2012-base boundary-year coverage test — 2026-11-13
- User queried the 2012-base All India / Combined / General-Overall headline series for 2011 and 2025 using `series=Current`, `limit=100`, `page=1`.
- 2011 returned HTTP 200 but `msg=No Data Found` and no metadata. Do not treat the filter endpoint's listed year range as proof that every year has observations.
- 2025 returned HTTP 200, `totalRecords=12`, `totalPages=1`; all 12 months were present, newest-first, and each had `status=F`. Headline index / year-on-year inflation pairs (Jan–Dec): Jan 193.4 / 4.26%; Feb 192.5 / 3.61%; Mar 192.0 / 3.34%; Apr 192.6 / 3.16%; May 193.0 / 2.82%; Jun 194.2 / 2.10%; Jul 196.1 / 1.61%; Aug 197.0 / 2.07%; Sep 197.0 / 1.44%; Oct 197.3 / 0.25%; Nov 197.9 / 0.71%; Dec 198.0 / 1.33%.
- This verifies complete year retrieval for 2025 and no returned data for 2011. It does not yet establish the earliest year with data (next test: 2012), explain `status=F`, or prove point-in-time publication/revision history. The 2012-base 2025 series should not be confused with the separately rebased 2024-base CPI series. No CPI data has been merged into the modelling dataset.
### MOSPI CPI 2012-base earliest-year check — 2026-11-13
- User queried the 2012-base All India / Combined / General-Overall headline series for year=2012 using `series=Current`, `limit=100`, `page=1`. API returned HTTP 200 with `msg=No Data Found` and no metadata.
- Together with the 2011 no-data result and verified full-year responses for 2024 and 2025, this indicates the 2012-base API series does not expose observations for its nominal base year or 2011 through this filter. Do not infer the actual earliest available year from these tests; test 2013 onward (or inspect official published archives) before defining coverage.
- No CPI data has been merged into modelling data. Publication-date alignment, `status=F` meaning, and revision/vintage behaviour remain open.
### MOSPI CPI 2012-base 2013 coverage test — 2026-11-13
- User queried year=2013 for the 2012-base All India / Combined / General-Overall headline series (`series=Current`, `limit=100`, `page=1`). API returned HTTP 200, `totalRecords=12`, `totalPages=1`, with all 12 months January–December 2013.
- Index values (Jan–Dec): 104.6, 105.3, 105.5, 106.1, 106.9, 109.3, 111.0, 112.4, 113.7, 114.8, 116.3, 114.5. All rows have `status=F`; the API's `inflation` field is null for every month in 2013.
- Since 2012 returned no data, the missing 2013 inflation values are consistent with the API not having a prior-year comparison available in this query. Treat this as an interpretation, not a confirmed API rule. Preserve the index observations and do not fill missing inflation values with zero.
- This confirms 2013 index coverage but not a continuous 2013–2025 history; intermediate years, publication timestamps, `status=F` meaning, and revision/vintage behaviour remain to be checked. No CPI data has been merged into modelling data.
### MOSPI CPI 2012-base 2014 coverage test — 2026-11-13
- User queried year=2014 for the 2012-base All India / Combined / General-Overall headline series (`series=Current`, `limit=100`, `page=1`). API returned HTTP 200, `totalRecords=12`, `totalPages=1`, covering January–December 2014.
- Index / year-on-year inflation pairs (Jan–Dec): Jan 113.6 / 8.60%; Feb 113.6 / 7.88%; Mar 114.2 / 8.25%; Apr 115.1 / 8.48%; May 115.8 / 8.33%; Jun 116.7 / 6.77%; Jul 119.2 / 7.39%; Aug 120.3 / 7.03%; Sep 120.1 / 5.63%; Oct 120.1 / 4.62%; Nov 120.1 / 3.27%; Dec 119.4 / 4.28%. All records have `status=F`.
- This verifies full-year 2014 retrieval. Together with the 2013 result, it shows the 2013 inflation nulls are not a general property of the endpoint; their cause remains unconfirmed. Continue testing year coverage and validate values against official releases before production use. No CPI data has been merged into modelling data.
### MOSPI CPI 2012-base 2015 coverage test — 2026-11-13
- User queried year=2015 for the 2012-base All India / Combined / General-Overall headline series (`series=Current`, `limit=100`, `page=1`). API returned HTTP 200, `totalRecords=12`, `totalPages=1`, covering January–December 2015.
- Index / year-on-year inflation pairs (Jan–Dec): Jan 119.5 / 5.19%; Feb 119.7 / 5.37%; Mar 120.2 / 5.25%; Apr 120.7 / 4.87%; May 121.6 / 5.01%; Jun 123.0 / 5.40%; Jul 123.6 / 3.69%; Aug 124.8 / 3.74%; Sep 125.4 / 4.41%; Oct 126.1 / 5.00%; Nov 126.6 / 5.41%; Dec 126.1 / 5.61%. All records have `status=F`.
- This confirms full-year 2015 retrieval. No CPI dataset has been merged into modelling data.

### CPI API pilot — compact running evidence log (2026-11-13)
- Endpoint: `GET https://api.mospi.gov.in/api/cpi/getCPIData`.
- Verified headline filters for 2012 base: `base_year=2012`, `level=Group`, `series=Current`, `state_code=99` (All India), `sector_code=3` (Combined), `group_code=0` (General), `subgroup_code=0.99` (General-Overall). Use `limit=100`, `page=1` for a year; returned rows are newest-first.
- Year coverage tests so far: 2011 = no data; 2012 = no data; 2013 = 12 records, index present but inflation null for all months; 2014 = 12 records with index and inflation; 2015 = 12 records with index and inflation; 2024 = 12 records with index and inflation; 2025 = 12 records with index and inflation. Years 2016–2023 have not yet been tested, so continuous coverage is not established.
- 2025 values belong to the 2012-base series and must not be confused with the separately rebased 2024-base CPI series. The 2024-base series was first released in 2026; its index history starts Jan 2025 and its new-series year-on-year inflation starts Jan 2026. Do not splice index/inflation values across bases as if they were one continuous series.
- Every returned 2013–2025 row observed so far has `status=F`; meaning of this status remains unverified. Preserve the 2013 null inflation values as null; do not impute zero.
- Evidence still required before model use: test intermediate years 2016–2023; decode status field; cross-check sample values against official MoSPI releases; record each release's actual publication date/time and applicable NSE session; determine whether API values are revised and whether historical vintages are available. Join by public-availability timestamp, not CPI observation month-end. Until then, this is a source/API feasibility pilot only, not a production-ready macro feature.
### MOSPI CPI 2012-base 2016 coverage test — 2026-11-13
- User queried year=2016 for the 2012-base All India / Combined / General-Overall headline series (`series=Current`, `limit=100`, `page=1`). API returned HTTP 200, `totalRecords=12`, `totalPages=1`, covering January–December 2016.
- Index / year-on-year inflation pairs (Jan–Dec): Jan 126.3 / 5.69%; Feb 126.0 / 5.26%; Mar 126.0 / 4.83%; Apr 127.3 / 5.47%; May 128.6 / 5.76%; Jun 130.1 / 5.77%; Jul 131.1 / 6.07%; Aug 131.1 / 5.05%; Sep 130.9 / 4.39%; Oct 131.4 / 4.20%; Nov 131.2 / 3.63%; Dec 130.4 / 3.41%. All records have `status=F`.
- This confirms full-year 2016 retrieval. No CPI data has been merged into modelling data.
### MOSPI CPI 2012-base 2017 coverage test — 2026-11-13
- User queried year=2017 for the 2012-base All India / Combined / General-Overall headline series (`series=Current`, `limit=100`, `page=1`). API returned HTTP 200, `totalRecords=12`, `totalPages=1`, covering January–December 2017.
- Index / year-on-year inflation pairs (Jan–Dec): Jan 130.3 / 3.17%; Feb 130.6 / 3.65%; Mar 130.9 / 3.89%; Apr 131.1 / 2.99%; May 131.4 / 2.18%; Jun 132.0 / 1.46%; Jul 134.2 / 2.36%; Aug 135.4 / 3.28%; Sep 135.2 / 3.28%; Oct 136.1 / 3.58%; Nov 137.6 / 4.88%; Dec 137.2 / 5.21%. All records have `status=F`.
- This confirms full-year 2017 retrieval. No CPI data has been merged into modelling data.
### MOSPI CPI 2012-base 2018 coverage test — 2026-11-13
- User queried year=2018 for the 2012-base All India / Combined / General-Overall headline series (`series=Current`, `limit=100`, `page=1`). API returned HTTP 200, `totalRecords=12`, `totalPages=1`, covering January–December 2018.
- Index / year-on-year inflation pairs (Jan–Dec): Jan 136.9 / 5.07%; Feb 136.4 / 4.44%; Mar 136.5 / 4.28%; Apr 137.1 / 4.58%; May 137.8 / 4.87%; Jun 138.5 / 4.92%; Jul 139.8 / 4.17%; Aug 140.4 / 3.69%; Sep 140.2 / 3.70%; Oct 140.7 / 3.38%; Nov 140.8 / 2.33%; Dec 140.1 / 2.11%. All records have `status=F`.
- This confirms full-year 2018 retrieval. No CPI data has been merged into modelling data.
### MOSPI CPI 2012-base 2019 coverage test — 2026-11-13
- User queried year=2019 for the 2012-base All India / Combined / General-Overall headline series (`series=Current`, `limit=100`, `page=1`). API returned HTTP 200, `totalRecords=12`, `totalPages=1`, covering January–December 2019.
- Index / year-on-year inflation pairs (Jan–Dec): Jan 139.6 / 1.97%; Feb 139.9 / 2.57%; Mar 140.4 / 2.86%; Apr 141.2 / 2.99%; May 142.0 / 3.05%; Jun 142.9 / 3.18%; Jul 144.2 / 3.15%; Aug 145.0 / 3.28%; Sep 145.8 / 3.99%; Oct 147.2 / 4.62%; Nov 148.6 / 5.54%; Dec 150.4 / 7.35%. All records have `status=F`.
- This confirms full-year 2019 retrieval. No CPI data has been merged into modelling data.
### MOSPI CPI 2012-base 2020 coverage test — 2026-11-13
- User queried year=2020 for the 2012-base All India / Combined / General-Overall headline series (`series=Current`, `limit=100`, `page=1`). API returned HTTP 200, `totalRecords=12`, `totalPages=1`, covering January–December 2020.
- Index / year-on-year inflation pairs (Jan–Dec): Jan 150.2 / 7.59%; Feb 149.1 / 6.58%; Mar 148.6 / 5.84%; Apr 151.4 / null; May 150.9 / null; Jun 151.8 / 6.23%; Jul 153.9 / 6.73%; Aug 154.7 / 6.69%; Sep 156.4 / 7.27%; Oct 158.4 / 7.61%; Nov 158.9 / 6.93%; Dec 157.3 / 4.59%. January–March and June–December have `status=F`; April and May have `status=F*` and null inflation.
- Preserve April/May 2020 inflation as null. The `F*` marker may relate to COVID-era data collection or publication caveats, but its exact meaning has not yet been verified from an official codebook/footnote; do not interpret it as confirmed. This is an important data-quality flag for later validation.
- This confirms 12 monthly index records for 2020, but two inflation fields are null and two rows have a distinct status marker. No CPI data has been merged into modelling data.
### MOSPI CPI 2012-base 2021 coverage test — 2026-11-13
- User queried year=2021 for the 2012-base All India / Combined / General-Overall headline series (`series=Current`, `limit=100`, `page=1`). API returned HTTP 200, `totalRecords=12`, `totalPages=1`, covering January–December 2021.
- Index / year-on-year inflation pairs (Jan–Dec): Jan 156.3 / 4.06%; Feb 156.6 / 5.03%; Mar 156.8 / 5.52%; Apr 157.8 / 4.23%; May 160.4 / 6.30%; Jun 161.3 / 6.26%; Jul 162.5 / 5.59%; Aug 162.9 / 5.30%; Sep 163.2 / 4.35%; Oct 165.5 / 4.48%; Nov 166.7 / 4.91%; Dec 166.2 / 5.66%. All records have `status=F`.
- This confirms full-year 2021 retrieval. Unlike April/May 2020, all 2021 monthly inflation values are populated and all statuses are `F`. No CPI data has been merged into modelling data.