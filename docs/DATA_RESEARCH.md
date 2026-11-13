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
### MOSPI CPI 2012-base 2022 coverage test — 2026-11-13
- User queried year=2022 for the 2012-base All India / Combined / General-Overall headline series (`series=Current`, `limit=100`, `page=1`). API returned HTTP 200, `totalRecords=12`, `totalPages=1`, covering January–December 2022.
- Index / year-on-year inflation pairs (Jan–Dec): Jan 165.7 / 6.01%; Feb 166.1 / 6.07%; Mar 167.7 / 6.95%; Apr 170.1 / 7.79%; May 171.7 / 7.04%; Jun 172.6 / 7.01%; Jul 173.4 / 6.71%; Aug 174.3 / 7.00%; Sep 175.3 / 7.41%; Oct 176.7 / 6.77%; Nov 176.5 / 5.88%; Dec 175.7 / 5.72%. All records have `status=F`.
- This confirms full-year 2022 retrieval. No CPI data has been merged into modelling data.
### MOSPI CPI 2012-base 2023 coverage test — 2026-11-13
- User queried year=2023 for the 2012-base All India / Combined / General-Overall headline series (`series=Current`, `limit=100`, `page=1`). API returned HTTP 200, `totalRecords=12`, `totalPages=1`, covering January–December 2023.
- Index / year-on-year inflation pairs (Jan–Dec): Jan 176.5 / 6.52%; Feb 176.8 / 6.44%; Mar 177.2 / 5.66%; Apr 178.1 / 4.70%; May 179.1 / 4.31%; Jun 181.0 / 4.87%; Jul 186.3 / 7.44%; Aug 186.2 / 6.83%; Sep 184.1 / 5.02%; Oct 185.3 / 4.87%; Nov 186.3 / 5.55%; Dec 185.7 / 5.69%. All records have `status=F`.
- This confirms full-year 2023 retrieval. The year-by-year pilot now has observed full 12-month responses for every year 2013–2025, with the recorded exceptions of null inflation in all 2013 months and April/May 2020. Years 2011 and 2012 returned no data. This is a tested set of individual years, not yet a bulk extraction or proof of release-time/vintage validity. No CPI data has been merged into modelling data.
### MoSPI CPI point-in-time availability and release-policy research — 2026-11-13

Official-source findings:
- MoSPI's CPI FAQ states the regular release time is 5:30 PM on the 12th of the month following the reference month; if the 12th is a holiday, release is on the next working day. Source: https://mospi.gov.in/faq
- MoSPI's National Metadata Structure for CPI says provisional monthly Rural/Urban/Combined CPI is released on the 12th of the following month (next working day if holiday), and final indices for the previous month are released alongside the provisional current-month indices. It also says an advance release calendar gives precise release dates one quarter ahead. Source: https://cpi.mospi.gov.in/PDFile/National_Metadata_Structure_for_CPI.pdf
- A historical primary-source example confirms the 5:30 PM embargo convention: the January 2015 CPI press release is dated 12 February 2015 and says it was embargoed until 5:30 PM that day. It reports January 2015 as provisional and December 2014 final. Source: https://www.mospi.gov.in/sites/default/files/press_release/cpi_pr_12feb15t.pdf
- A second historical example: the May 2019 CPI press release is embargoed until 5:30 PM on 12 June 2019. Source: https://www.mospi.gov.in/sites/default/files/press_release/Press%20Statement_3.pdf
- The MoSPI eSankhyiki CPI catalogue exposes an explicit per-record "Release Date" field. Example catalogue entry for July 2026 shows release date 12 Aug 2026. This is preferable to reconstructing all historic dates from the nominal 12th-day rule. Source: https://esankhyiki.mospi.gov.in/catalogue-main/catalogue?product=CPI
- MoSPI's 2026-27 advance release calendar lists exact CPI release dates (e.g. 12 Nov 2026 and 12 Dec 2026). Calendar is subject to updates. Source: https://www.mospi.gov.in/uploads/documents/releaseCalender/1793948871564-ARC%202026-27%20updated%20till%20October%202026.pdf

Base-series transition and revision evidence:
- The first CPI 2024=100 press release is dated 12 February 2026 and explicitly embargoed until 4:00 PM that day. It presents January 2026 as provisional on the 2024 base and December 2025 as final on the 2012 base. Source: https://mospi.gov.in/uploads/latestReleases/latest_release_1770891893893_6b458c0a-c327-4fef-a554-41131ea67273_Press_Relase_of_CPI_for_Jan26.pdf
- That release states CPI 2024=100 uses HCES 2023-24 weights, 2024 price reference period, revised basket/weights, and a new COICOP-2018 classification. It provides a linked back series for the general index only; it explicitly cautions that the two classification systems can be directly linked only at the general index level. Do not splice 2012-base subgroup values with 2024-base division/subgroup values as if definitions were identical.
- The release says the 2024-base back series covers All India general indices Jan 2013–Dec 2024 and annual inflation Jan 2014–Dec 2024; the link factor uses the overlapping 2025 period. This is a retrospective linked series, not evidence that the linked 2024-base history was available to market participants on those historical dates.

Point-in-time modelling implications:
- For a model decision made on a release date, do not assume the CPI value is available at market open. The regular 5:30 PM release is after the NSE cash-market close, so its first usable trading session should ordinarily be the next NSE trading session. Verify exchange holidays and actual release timestamps for each row.
- Preferred implementation: construct a release-vintage table from the official catalogue/press-release archive with fields such as reference_month, base_year, series, release_date, release_time, provisional_or_final, source_url, retrieved_at, and value. Join to stock observations only when release timestamp is strictly earlier than the prediction timestamp.
- The API pilot's `status=F` and observed 2020 `F*` values have not yet been mapped to documented meanings. Do not interpret F as "final" or F* as a COVID flag until the API schema or MoSPI confirms it. The current API response may expose latest/current historical values rather than original release vintages; the pilot has not established vintage history or revision behaviour.
- The 2012-base API annual retrieval pilot establishes endpoint coverage only. It does not establish the exact date each historical monthly value first became public, nor whether today's API values equal the first-release values. CPI data remains excluded from modelling data pending vintage/release-date validation.

### CPI release-date archive investigation — 2026-11-13

Additional official-source checks:
- The current eSankhyiki CPI catalogue is a paginated catalogue with 495 CPI entries in the search result. It exposes a per-entry Release Date and Reference Period. The first visible entries are recent 2026 records; the result page does not by itself prove that all historical 2013–2025 releases are represented or easily enumerable. Example catalogue: https://esankhyiki.mospi.gov.in/catalogue-main/catalogue?product=CPI
- MoSPI's National Metadata Structure (current version) clarifies the data-access split: monthly press releases and annexures are posted on the MoSPI website; item/higher-level data are on eSankhyiki; 2024-base back series Jan 2013–Dec 2024 is on eSankhyiki; old 2012-base CPI data through Dec 2025 is in the CPI warehouse at https://www.cpi.mospi.gov.in. Source: https://mospi.gov.in/sites/default/files/CPI/National_Metadata_Structure_for_CPI.pdf
- The MoSPI website has a CPI press-release collection labelled Jan 2011–Dec 2025, but its product page currently returns “No data found” to the public page reader. It is therefore not yet a usable machine-readable archive index: https://mospi.gov.in/product/more/9-CPI%20Press%20Releases%20%28Jan%202011%20to%20Dec%202025%29
- Historical primary-source PDFs confirm that actual release dates can deviate from the 12th: January 2017 CPI was dated/released 13 Feb 2017 (embargo 5:30 PM) and the press note explicitly names the next release date; March 2017 CPI was dated 12 Apr 2017; December 2017 CPI was dated 12 Jan 2018. Sources: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_13feb17m.pdf ; https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12apr17w.pdf ; https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12jan18f.pdf
- October 2020 CPI press release is dated 12 Nov 2020 and embargoed until 5:30 PM; the September 2020 release states the next release date as 12 Nov 2020. Sources: https://mospi.gov.in/uploads/documents/CPI/Press/PR%20October%202020.pdf ; https://mospi.gov.in/sites/default/files/press_release/Press%20Statementsept20.pdf
- Some historical releases include the next scheduled release date, which can help cross-check dates, but does not replace the dated press release itself. A scheduled date can still be revised.

Working conclusion / next research actions:
- The catalogue is promising for exact release-date extraction but historical coverage and pagination/filter semantics remain unverified. Do not yet claim it covers the entire 2013–2025 period.
- The official metadata points to the CPI warehouse (cpi.mospi.gov.in) as the source for old 2012-base historical values through Dec 2025. Next inspect its downloadable tables / release archive and compare a few overlapping months with the API.
- Build a small pilot across selected months (including ordinary 12th releases and a holiday-shifted release) before attempting all months. For each month capture the dated official press release or catalogue Release Date and the source URL. Keep release time as 17:30 only where the specific release explicitly confirms the embargo time; otherwise record time as unknown rather than blindly imputing it.
- Since the press release is issued at 5:30 PM in the historical examples, the first usable NSE session is normally the next trading session, subject to actual date and exchange holiday calendar. The exact timestamp, not reference month, controls availability.

### CPI warehouse verification and release-time caveat — 2026-11-13

Official warehouse metadata and archive findings:
- The official CPI warehouse homepage is indexed and describes the old 2012=100 series as covering All India sub-group/group/general/CFPI indices from Jan 2013 onward; it also describes older 2010-base and back-series coverage. Source: https://cpi.mospi.gov.in/
- MoSPI's National Metadata Structure explicitly says the warehouse has downloadable Excel files under tabs including "Time Series", "All India Item Index", "Annual Inflation Rates", and "All India Item Inflation Rates". This confirms a direct downloadable-data route; browser opening the homepage itself timed out in this research session, so the actual Excel download path and format remain untested. Source: https://cpi.mospi.gov.in/PDFile/National_Metadata_Structure_for_CPI.pdf
- The official CPI warehouse hosts monthly press-release PDFs under https://www.cpi.mospi.gov.in/PDFile/Press/. Search indexing surfaced the March 2025 release and September 2025 release, both with an Annexure time series of All India General CPI values since Jan 2013. The December 2025 release PDF is directly accessible and provides the final 2012-base release, including Annexures I–VII and the CPI time series. Sources: https://cpi.mospi.gov.in/PDFile/Press/PR%20March%202025.pdf ; https://www.cpi.mospi.gov.in/PDFile/Press/PR%20September%202025.pdf ; https://www.cpi.mospi.gov.in/PDFile/Press/PR%20December%202025.pdf
- December 2025 press release: dated 12 Jan 2026 and embargoed until 4:00 PM; explicitly says it is the last CPI release on base 2012=100, and the revised 2024=100 series would be released on 12 Feb 2026 or next working day if holiday. It marks Dec 2025 provisional and Nov 2025 final. This confirms status/provisional-final language in the press release itself, but does not yet decode the API's separate status field. Source: https://www.cpi.mospi.gov.in/PDFile/Press/PR%20December%202025.pdf
- Important correction to the blanket time assumption: historical examples included 5:30 PM embargoes (e.g. Jan 2015; Feb 2017), but the Dec 2025 release is explicitly embargoed until 4:00 PM. The first 2024-base release (Jan 2026 reference month) was also embargoed until 4:00 PM. Therefore do not hard-code 17:30 for all history. Capture the exact embargo/release time from each monthly release where available; if absent, leave time unknown and conservatively assign availability no earlier than the next NSE session.
- Official metadata says provisional CPI is normally released on the 12th of the following month (next working day if holiday), final indices for the prior month alongside it; exact release calendar dates are published one quarter ahead. Treat this as a schedule rule, not a substitute for actual release evidence. Source: https://cpi.mospi.gov.in/PDFile/National_Metadata_Structure_for_CPI.pdf
- The warehouse home page itself timed out when opened through the web reader in this session. The downloadable Excel section is confirmed by metadata but not yet manually downloaded/inspected. This is not a verified API/download implementation.

Point-in-time dataset decision proposal (not yet user-approved):
- Store reference_month, base_year, release_date, release_time_local, timestamp_precision/source (exact vs date-only vs estimated), provisional/final, value, source_url, retrieved_at, and source-vintage notes.
- For modelling, join a value only after its known publication timestamp. If exact time is missing, use next eligible NSE session rather than same-day market use.
- Keep each published vintage/version where obtainable. Do not overwrite earlier provisional values with later final values in the research archive.

### Three-release primary-source timestamp pilot — 2026-11-13

The three proposed sample releases have now been checked against the original MoSPI press-release PDFs:

| Reference month | Official document date | Embargo / publication time | Evidence |
|---|---|---|---|
| January 2015 (2012-base) | 12 Feb 2015 | 17:30 IST | https://mospi.gov.in/sites/default/files/press_release/cpi_pr_12feb15t.pdf |
| January 2017 (2012-base) | 13 Feb 2017 | 17:30 IST | https://mospi.gov.in/sites/default/files/press_release/CPI_PR_13feb17m.pdf |
| December 2025 (2012-base) | 12 Jan 2026 | 16:00 IST | https://www.cpi.mospi.gov.in/PDFile/Press/PR%20December%202025.pdf |

Observed details:
- January 2015 release explicitly says it is embargoed until 5:30 PM on 12 Feb 2015; it labels January 2015 provisional and December 2014 final. It gives next release date 12 Mar 2015.
- January 2017 release explicitly says it is embargoed until 5:30 PM on 13 Feb 2017; it labels January 2017 provisional and December 2016 final. It gives next release date 14 Mar 2017. This is a concrete example of the actual release date moving beyond the nominal 12th.
- December 2025 release explicitly says embargoed until 4:00 PM on 12 Jan 2026; December 2025 is provisional and November 2025 final. It identifies itself as the last CPI release on base 2012=100.
- These examples establish that the release time changed over time and that reference-month and finalisation status must be stored separately. They do not establish the timestamp for every intervening month.
- A 4:00 PM or 5:30 PM publication is after the NSE regular cash-market close. For a daily model using close-timestamped observations, conservatively make the new CPI value usable from the next eligible NSE trading session, not the release-date close.
- MoSPI's NMDS says the monthly annexure Excel is published with the press release and that the CPI warehouse offers downloadable Excel time-series data. This pilot used the PDF press releases only; warehouse Excel download and automated extraction remain untested. Source: https://nmds.mospi.gov.in/

Implementation status:
- Three exact historical date/time examples are verified from original official PDFs.
- Do not extrapolate the 17:30 or 16:00 times across the entire archive. For every monthly record, capture the PDF's explicit embargo time when present; if absent, retain date-only/unknown time and use next-session availability conservatively.
- Next pilot should validate a date-only or exceptional holiday case and inspect whether the warehouse's historical Excel table contains observation values only or any release/vintage metadata.


### CPI warehouse and monthly-annexure access verification — 2026-11-13

Further primary-source verification:
- The current MoSPI National Metadata Structure (metadata last updated 15 Feb 2025) explicitly states that the monthly CPI press release is issued simultaneously to interested parties, and that a monthly Excel annexure is uploaded alongside the press release under Statistics → Download Tables/Data → CPI. It separately states that the CPI warehouse exposes downloadable Excel tables under tabs including Time Series, All India Item Index, Annual Inflation Rates, and All India Item Inflation Rates. Source: https://cpi.mospi.gov.in/PDFile/National_Metadata_Structure_for_CPI.pdf (sections 3.3–3.5).
- The same metadata says the regular provisional release is on the 12th of the following month (next working day if holiday), final indices for the previous month are released alongside it, and the advance release calendar gives precise dates one quarter ahead. It describes the release lag as 12 days. Treat these as general policy, not as substitutes for each dated release document. Source: https://cpi.mospi.gov.in/PDFile/National_Metadata_Structure_for_CPI.pdf.
- The official warehouse landing page is indexed and describes the 2012=100 series availability, but attempts to open the landing page and its interactive cross-tab in the browser reader timed out. Search indexing does expose pages such as the 2012-base inflation cross-tab and item-weight table. The exact Excel download URL, workbook structure, and programmatic download workflow therefore remain untested. Sources: https://www.cpi.mospi.gov.in/Default1.aspx ; https://www.cpi.mospi.gov.in/Inflation_CurrentSeries_2012_Crosstab.aspx ; https://www.cpi.mospi.gov.in/Weight_AI_Item_Combined_2012.aspx.
- Official monthly press-release PDFs are a practical alternative source for spot-checking: for example, the October 2025 release includes an Annexure VI table of All India General CPI (2012=100) from Jan 2013 through Oct 2025, marking Oct 2025 provisional; the December 2025 release contains the same type of long time-series annexure and separately identifies the latest month as provisional and the preceding month as final. Sources: https://cpi.mospi.gov.in/PDFile/Press/PR%20October%202025.pdf ; https://www.cpi.mospi.gov.in/PDFile/Press/PR%20December%202025.pdf.
- Important distinction: the historical time-series annexure is a convenient way to obtain the latest published historical path, but it is not itself a monthly archive of every past vintage. Its presence does not prove that values match what investors saw at each earlier date. Use the dated release's current/previous-month annexures for first-publication values and retain each release as a separate vintage where obtainable.
- The API status codes (F and F*) remain undocumented in the official metadata and accessible sources reviewed here. Do not map them to provisional/final or any event flag without an official schema/definition.

Research outcome:
- Official documentation confirms that both monthly release annexures and warehouse Excel downloads exist.
- Automated access to the warehouse workbook itself has not been demonstrated. This is a browser-reader access limitation, not evidence that the data is unavailable.
- Next useful experiment: obtain one monthly annexure workbook or inspect the live warehouse in a normal browser, then record its actual filename, columns, sheet names, and whether it contains only the current/previous vintage or longer revised histories. Compare one overlapping observation against the API and the release PDF. Do not merge CPI into the model until point-in-time vintage handling is resolved.


### CPI API missing-value cross-check against official release annexure — 2026-11-13

- The December 2025 official 2012-base CPI press release includes Annexure VII, a monthly time series of All India year-on-year inflation from January 2014 through November 2025. It explicitly shows April and May 2020 as `-` and explains that inflation was not compiled and released for those months due to the COVID-19 pandemic. It marks November 2025 inflation as provisional. Source: https://cpi.mospi.gov.in/PDFile/Press/PR%20December%202025.pdf (Annexure VII, page 11).
- This independently corroborates the API pilot's null inflation values for April and May 2020. The API's separate `F*` status remains unexplained; the PDF footnote explains the missing inflation values but does not define the API status code. Keep the API status field raw and preserve the inflation values as missing, not zero or interpolated.
- The December 2025 release also explicitly labels November 2025 as final in its detailed annexures, while the November 2025 release had labelled November as provisional. This demonstrates a concrete two-vintage sequence for the same reference month: first published provisional, then final in the following monthly release. The release PDFs can therefore support a small vintage reconstruction pilot even if the warehouse's interactive Excel interface remains inaccessible. Sources: https://cpi.mospi.gov.in/PDFile/Press/PR%20November%202025.pdf ; https://cpi.mospi.gov.in/PDFile/Press/PR%20December%202025.pdf.
- Research implication: for each month, retain the original release's provisional value and the next release's final value as separate records when both source documents are available. Do not overwrite provisional history with final values when constructing point-in-time features.


### CPI November 2025 provisional-to-final vintage comparison — 2026-11-13

A two-release pilot was completed using the official November and December 2025 MoSPI press releases:

| Field (All India, Combined, CPI General, 2012=100) | November 2025 first release (provisional; 12 Dec 2025, 16:00 IST) | December 2025 release (November final; 12 Jan 2026, 16:00 IST) |
|---|---:|---:|
| CPI index | 197.9 | 197.9 |
| Year-on-year inflation | 0.71% | 0.71% |

- November 2025 release labels November provisional and reports combined CPI General index 197.9 and year-on-year inflation 0.71%. It states the December CPI release date as 12 January 2026. Source: https://www.mospi.gov.in/uploads/latestreleasesfiles/1765535702131-Press%20Release_CPI_November_2025.pdf ; PIB mirror: https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2202940&lang=2&reg=48.
- December 2025 release labels November final and reports the same combined index 197.9 and year-on-year inflation 0.71%, while December 2025 itself is provisional. It is embargoed until 4:00 PM on 12 January 2026. Source: https://mospi.gov.in/uploads/release_calendar/1768214980837_Press_Release_of_CPI_for_December_2025.pdf ; PIB mirror: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2213736&lang=2&reg=3.
- At the one-decimal index and two-decimal inflation precision exposed in the press-release tables, no revision is visible for November 2025 between provisional and final. This does not prove that unrounded underlying values were identical; the public tables may round values.
- This is a valid proof-of-process for storing separate provisional and final vintage records, but not yet evidence that revisions are large or frequent. Retain both records even when their displayed values match; their availability dates differ by one month.
- Availability: November provisional became public at 16:00 IST on 12 Dec 2025; November final became public at 16:00 IST on 12 Jan 2026. Both timestamps are after the NSE cash-market close, so for a daily close-based model the earliest eligible use is the next NSE trading session after each release.
- The December 2025 press release also states April and May 2020 inflation was not compiled/released due to the COVID-19 pandemic. Preserve those observations as missing; do not impute zero. This matches the API pilot's null inflation values, but does not decode its `F*` status code.

Research limitation: this pilot compares the headline All India Combined CPI General values as printed in two press releases. It does not yet extract Excel annexures, access unrounded data, reconstruct all monthly vintages, or validate the API status codes.


### CPI historical revision example — September 2018 provisional versus final — 2026-11-13

A second vintage comparison found an actual visible revision, unlike the November 2025 example:

| All India CPI General, 2012=100 | First release: Sep 2018 provisional (12 Oct 2018, 17:30 IST) | Next release: Sep 2018 final (12 Nov 2018, 17:30 IST) |
|---|---:|---:|
| Rural index | 142.2 | 142.1 |
| Urban index | 138.1 | 138.1 |
| Combined index | 140.3 | 140.2 |
| Combined year-on-year inflation | 3.77% | 3.70% |

- The 12 Oct 2018 press release labels September 2018 provisional and reports the General CPI indices as Rural 142.2, Urban 138.1, Combined 140.3; its combined year-on-year inflation is 3.77%. It was embargoed until 17:30 IST on 12 Oct 2018. Source: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12oct18f.pdf.
- The 12 Nov 2018 press release labels September 2018 final and reports the same reference month's General CPI indices as Rural 142.1, Urban 138.1, Combined 140.2; combined year-on-year inflation is 3.70%. It was embargoed until 17:30 IST on 12 Nov 2018. Source: https://mospi.gov.in/sites/default/files/press_release/Press%20Statement.pdf (page 1 and Annexure I, page 2).
- Thus, at published precision, September 2018's combined index was revised downward by 0.1 index point and combined year-on-year inflation by 0.07 percentage points between the provisional and final releases. Rural index also changed by -0.1; urban index was unchanged.
- Point-in-time consequence: a backtest using the September 2018 final value before 17:30 IST on 12 Nov 2018 would leak later information. The provisional vintage is the correct value for earlier decision dates; the final vintage becomes available only after its actual release timestamp. For a close-based daily stock model, use it from the next eligible NSE session.
- This establishes that revisions are not merely theoretical and that using the latest API history alone can introduce look-ahead bias. Keep each vintage as a separate record with its own release timestamp and source document. The magnitude and frequency of revisions across all months remain unmeasured; this is one concrete historical example, not a full revision study.


### CPI additional vintage check — October 2020 provisional versus final — 2026-11-13

A further same-month comparison was checked using the original October 2020 release and MoSPI's subsequent November 2020 release summary:

| October 2020 CPI General, Combined | First release (12 Nov 2020, 17:30 IST) | Final release (14 Dec 2020) |
|---|---:|---:|
| Year-on-year inflation | 7.61% provisional | 7.61% final |

- The 12 Nov 2020 release labels October 2020 provisional and reports combined CPI General year-on-year inflation of 7.61%. Its headline index table reports combined index 158.4. Source: https://mospi.gov.in/uploads/documents/CPI/Press/PR%20October%202020.pdf.
- MoSPI's subsequent monthly summary states that October 2020 was finalised on 14 Dec 2020 and reports final combined year-on-year inflation of 7.61%. Source: https://mospi.gov.in/sites/default/files/publication_reports/Summary_Nov_Dec20_22jan21.pdf.
- This is a no-visible-change result for the published combined inflation rate (two decimal places). The final combined index value was not independently extracted from the November 2020 press-release annexure in this check, so no claim is made that the index itself was unchanged.
- Evidence set now contains two months with visible published changes (September 2018 and September 2020? Correction: the September 2020 release pair has not yet been checked through its final release here; only October 2020 inflation is a no-visible-change example) and two no-visible-change examples (November 2025 and October 2020 combined inflation). The September 2018 pair is the only confirmed visible revision in the tested examples.
- These are purposively selected examples, not a random or representative sample. They cannot estimate the frequency, average size, or distribution of revisions.


### CPI September 2020 COVID-period provisional-to-final comparison — 2026-11-13

The September 2020 vintage comparison is now verified from two consecutive official MoSPI releases:

| All India CPI General, Combined (2012=100) | First release: Sep 2020 provisional (12 Oct 2020, 17:30 IST) | Next release: Sep 2020 final (12 Nov 2020, 17:30 IST) |
|---|---:|---:|
| Combined index | 156.5 | 156.4 |
| Combined year-on-year inflation | 7.34% | 7.27% |

- The 12 Oct 2020 release identifies September 2020 as provisional. It reports combined CPI General index 156.5 and combined year-on-year inflation 7.34%. It also reports that prices were collected from 98.0% of villages and 97.8% of urban markets, while prices were reported for 83.0% of rural and 87.9% of urban markets. Source: https://www.mospi.gov.in/sites/default/files/press_release/Press%20Statementsept20.pdf.
- The 12 Nov 2020 release identifies September 2020 as final. Its comparison table reports September combined CPI General index 156.4 and combined year-on-year inflation 7.27%. Source: https://mospi.gov.in/uploads/documents/CPI/Press/PR%20October%202020.pdf.
- At published precision, the combined index was revised downward by 0.1 point and year-on-year inflation by 0.07 percentage points. This is a confirmed visible revision during the COVID-affected period.
- The provisional release's reported price coverage is a relevant data-quality caveat, but the release does not establish that lower reporting coverage caused the revision. Do not infer causation.
- Point-in-time rule: September provisional values became public at 17:30 IST on 12 Oct 2020; final values became public at 17:30 IST on 12 Nov 2020. A close-based daily model must not use the final vintage before the next eligible NSE session after the latter timestamp.
- This comparison is one further purposively selected example, not a representative sample or estimate of typical revision size/frequency.


### CPI September 2019 provisional-to-final comparison — 2026-11-13

The September 2019 vintage pair was checked using consecutive MoSPI releases:

| All India CPI General, Combined (2012=100) | First release: Sep 2019 provisional (14 Oct 2019, 17:30 IST) | Next release: Sep 2019 final (13 Nov 2019, 17:30 IST) |
|---|---:|---:|
| Combined index | 145.8 | 145.8 |
| Combined year-on-year inflation | 3.99% | 3.99% |

- The 14 Oct 2019 MoSPI release identifies September 2019 as provisional and reports combined General CPI index 145.8 and combined annual inflation 3.99%. Source: https://www.mospi.gov.in/sites/default/files/press_release/Press%20statement_1.pdf.
- The 13 Nov 2019 MoSPI release identifies September 2019 as final and reports combined annual inflation 3.99%; Annexure I reports September combined General CPI index 145.8 (final). Source: https://www.mospi.gov.in/sites/default/files/press_release/cpi_oct.pdf. PIB mirror: https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1591469&lang=2&reg=48.
- No visible revision is present at published precision for either the combined index (one decimal) or annual inflation (two decimals). This does not establish that unrounded underlying values were identical.
- Both releases were embargoed until 17:30 IST. For a close-based daily model, the final vintage is usable only from the next eligible NSE session after 13 Nov 2019's release timestamp; before then the provisional vintage is the latest available observation.
- This is another selected example, not a representative sample or an estimate of CPI revision frequency.


### CPI systematic retrieval route and vintage-archive limitation — 2026-11-13

Official MoSPI documentation and portal discovery establish two distinct retrieval routes; they should not be confused:

1. **Current historical time series (latest available values):** MoSPI's CPI warehouse describes the 2012-base current series as available from January 2013 onward for All India Group/Sub-group/General/CFPI, and provides a Time Series interface with downloadable data. A World Bank reproducibility package independently documents a successful 2025 download of the warehouse's current series (January 2013-May 2025) by selecting Time Series > Base 2012 > Current Series and exporting CSV. This is useful for a latest-value history, but it does not preserve what was known at each original release date. Sources: https://cpi.mospi.gov.in/ (warehouse; search-indexed content: https://www.cpi.mospi.gov.in/Default1.aspx); https://reproducibility.worldbank.org/catalog/541.
2. **Monthly release annexures (release-specific snapshots):** MoSPI's CPI metadata says a monthly press release PDF and its annexure in Excel are uploaded every month; it also says warehouse indices and inflation data are downloadable in Excel. The current eSankhyiki data catalogue exposes directly indexed monthly Excel annexure files, including October 2025 Annexure VII and November 2025 Annexure VII. Example files: https://esankhyiki.mospi.gov.in/datacatalogue/CPI/2026/Annexures_for_Press_Release_in_Excel_October2025_Annex-VII.xlsx and https://esankhyiki.mospi.gov.in/datacatalogue/CPI/2026/Annexures_for_Press_Release_in_Excel_November2025_Annex-VII.xlsx. The web reader cannot inspect the binary workbook contents, and a complete older-month URL pattern/archive has not yet been verified. Sources: https://mospi.gov.in/sites/default/files/CPI/National_Metadata_Structure_for_CPI.pdf ; https://esankhyiki.mospi.gov.in/datacatalogue/CPI/2026/Annexures_for_Press_Release_in_Excel_October2025_Annex-VII.xlsx.
3. **Release PDFs as a durable vintage fallback:** each monthly PDF contains the headline figures and, in some releases, a long historical time-series annexure. Example: the October 2025 release includes Annexure VI with All India General CPI history from January 2013 through October 2025, with October 2025 marked provisional. This is a latest-vintage series embedded in that release, not a complete historical vintage archive by itself. Source: https://cpi.mospi.gov.in/PDFile/Press/PR%20October%202025.pdf.
4. **Current API:** the eSankhyiki CPI API documentation describes a paginated JSON endpoint covering 2010, 2012 and 2024 bases, with an optional bearer token and per-IP rate limiting. The API pilot previously completed for 2012 base retrieved annual records, but its response did not establish a historical vintage archive or release timestamps. Source: https://esankhyiki.mospi.gov.in/macroindicators?product=cpi&tab=api.

**Important distinction:** the warehouse Time Series/current API provide historical observations as currently held, while a point-in-time backtest needs each release's contemporaneous value and actual publication timestamp. The monthly annexure archive may provide release-specific snapshots, but this remains unproven until we can retrieve and compare the same reference month across two archived Excel releases. The manually checked PDF pairs already demonstrate that revisions exist.

**Next practical pilot:** download one indexed annexure workbook (e.g. October 2025 Annexure VII), inspect workbook sheets/columns and confirm whether it contains the headline series and vintage labels. Then locate the corresponding November 2025 workbook and test whether its November/October rows expose the provisional-to-final transition. If the eSankhyiki catalogue does not expose older monthly workbooks consistently, use official release PDFs as a fallback and automate extraction only after validating a small set against the published tables. Do not merge the latest-value CPI API series into modelling features as if it were point-in-time safe.


### CPI retrieval research — official API manual, catalogue access, and implementation implications — 2026-11-13

A deeper check of MoSPI's official documentation clarifies the available routes and exposes an API-version distinction:

- The official CPI API user manual documents a platform at `https://api.mospi.gov.in`, with `/api/getCPIIndex` for group/subgroup index and inflation from January 2013, and `/api/getItemIndex` for item-level data from January 2014. It documents `Current_series_2012` and `Back_series_2012`, JSON/CSV output, multi-year/month filters, and a signup/login bearer-token flow. The manual says tokens last 15 minutes and unauthenticated Swagger access returns only the first 10 records. Source: https://api.mospi.gov.in/API/CPI%20API%20User%20Manual.pdf.
- This manual documents an API interface different from the previously piloted `/api/cpi/getCPIData` endpoint. Do not assume their parameter names, authentication, status codes or vintage behaviour are interchangeable. The earlier API pilot's 2013–2025 records remain evidence only for that endpoint and its tested parameters.
- The manual's examples show `status` values such as `P`, `F` and `M`, but the manual does not define these codes. Preserve raw status values; do not decode them by assumption. Its example records include 2013 inflation nulls and later provisional records, which is consistent with retaining missing values and status as separate fields.
- MoSPI's current FAQ confirms the CPI warehouse Time Series tab is the official route for monthly Rural, Urban and Combined CPI time series and directs users to the warehouse for downloadable data. Source: https://mospi.gov.in/faq.
- MoSPI's CPI warehouse page describes the 2012-base current series as beginning January 2013, item indices from January 2014, and 2012-base back-series data for January 2011–December 2012. The warehouse page itself timed out when opened during this research, so no actual download was performed. Source: https://www.cpi.mospi.gov.in/Default1.aspx.
- The eSankhyiki catalogue states that its Data Catalogue downloads released statements in Excel and the Macro Indicators module offers downloadable filtered time series. It states that registration is not required for browsing/downloading. Source: https://esankhyiki.mospi.gov.in/datacatalogue/CPI/2025/.
- The official CPI metadata states that monthly press release PDFs and Excel annexures are uploaded every month, and that the CPI warehouse provides downloadable Excel tables. Sources: https://nmds.mospi.gov.in/ and https://mospi.gov.in/sites/default/files/CPI/National_Metadata_Structure_for_CPI.pdf.
- Directly indexed October 2025 and November 2025 Annexure VII XLSX URLs were found in the eSankhyiki catalogue. The browser reader could not fetch/inspect the binary XLSX, so sheet names, headers, exact series and historical catalogue depth remain unverified. A direct URL open returned inaccessible through the browser reader; this is not proof the file is unavailable to a normal browser or Python client.

**Interpretation and caution:** the official release schedule says the provisional current-month CPI and final previous-month CPI are published together. Our September 2018 and September 2020 PDF comparisons show that provisional values can differ from their subsequent final values at published precision. A third-party CPI guide surfaced in search claiming CPI is never revised, but that conflicts with these directly compared official release tables and is not adopted as evidence. The primary-source month-to-month comparisons take precedence for the tested months; the full policy and frequency of revisions still require systematic study.

**Recommended data architecture (proposal, not yet implemented):** store CPI releases as append-only vintage observations, not overwriting a single month row. Suggested key: `(series_id, reference_month, sector, group_code, subgroup_code, release_timestamp, vintage_status)`. Store at least `index_value`, `inflation_yoy`, raw `status_code`, `source_document_url`, `retrieved_at`, and `base_year`. Preserve both release timestamp and retrieval timestamp. For a close-based equity model, map a release to the first eligible NSE trading session strictly after its actual publication timestamp. Do not use the retrospective 2024=100 back series as if it had been available to investors in 2013–2024.

**Next practical step:** perform a local download-and-inspect pilot of one official Excel annexure and its immediately following month's annexure. Validate the extracted rows against the two official PDFs already checked. If workbook access or archive depth fails, use PDFs as source records and keep the latest-value API only as a cross-check. Do not integrate CPI into the model until this validation is complete.


### Important terminology correction — provisional-to-final publication is not proof of post-final revision — 2026-11-13

The CPI vintage research needs a precise distinction that was not sufficiently explicit in earlier notes:

- MoSPI's official CPI metadata says provisional monthly indices for the current reference month and final indices for the penultimate month are released together. Thus a reference month's provisional value is expected to be replaced by its final value in the next monthly release. The September 2018 and September 2020 comparisons document this provisional-to-final update; calling these simply 'revisions' without qualification is ambiguous and may incorrectly imply MoSPI revised already-final data. Source: https://mospi.gov.in/sites/default/files/CPI/National_Metadata_Structure_for_CPI.pdf.
- A secondary compilation, Measure of India, describes CPI as 'final on release; never revised' for the 2012-base and 2024-base series. This is not an official MoSPI policy statement, but it is consistent with the distinction that the final value is not subsequently revised. Source: https://measure.thisindianlife.today/data/cpi/ and https://measure.thisindianlife.today/data/cpi-2024/.
- Therefore, current evidence supports a provisional-to-final transition for the same reference month, but does **not** establish that MoSPI routinely revises a value after it has been declared final. The previous research notes' phrase 'visible revision' should be read as 'visible provisional-to-final update'. The September 2018 and September 2020 numeric differences remain valid; the terminology is corrected.
- This changes the data requirement slightly: a point-in-time dataset must preserve the provisional value from its first release and the final value from the following release. It does not require assuming an indefinite series of post-final revisions. Continue to retain release timestamp and status to verify this empirically.
- The official API manual for the older API platform states that `/api/getCPIIndex` returns group/subgroup CPI and inflation from January 2013 and `/api/getItemIndex` returns item-level data from January 2014. It requires one-time signup and a bearer token valid for 15 minutes for full results; without a token the API returns only the first 10 records. It documents `Current_series_2012` and `Back_series_2012`, JSON/CSV, and raw `status` values, but does not define the status codes. Source: https://www.api.mospi.gov.in/API/CPI%20API%20User%20Manual.pdf.
- The newer eSankhyiki `/api/cpi/getCPIData` is documented as an open, paginated API covering base years 2010, 2012 and 2024, with optional bearer token and per-IP rate limits. It is a different API from the older manual's endpoints. Source: https://esankhyiki.mospi.gov.in/macroindicators?product=cpi&tab=api.
- MoSPI's current National Metadata Structure says the old 2012-base CPI data are available in the CPI warehouse only through December 2025, while the 2024-base back series for January 2013–December 2024 is available through eSankhyiki. Do not assume the older 2012-base API is the current long-term route without testing. Source: https://mospi.gov.in/sites/default/files/CPI/National_Metadata_Structure_for_CPI.pdf.

**Revised conclusion:** the 2012-base CPI headline is a feasible macro candidate if we preserve its original provisional release and subsequent final release with actual timestamps. We have not yet proved systematic automated recovery of all monthly release snapshots. The monthly Excel-annexure route remains a potential source; the current keyless eSankhyiki API is suitable for a latest-value cross-check, not automatically a vintage archive. No CPI series should be merged until the extraction and point-in-time rules are validated.


### Official MoSPI CPI press-release Excel annexures — retrieval route verified — 2026-11-13
- The eSankhyiki **Macro Indicators** CPI parameter form exports a user-filtered time-series dataset; it is not the monthly press-release Annexure workbook. The user's `cpi_33.xlsx` came from that route and should be retained as a separate current-series extract, not treated as a release-vintage archive.
- MoSPI's FAQ states that Excel statements annexed to a press notes are downloadable from the blue link in paragraph 2 or 3 of the press note. The same FAQ describes the website route as Statistics → Download Tables/Data → CPI folder. Source: https://mospi.gov.in/faq
- For the October 2025 provisional observation, use the CPI release dated 12 November 2025: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12nov25.pdf . It identifies October 2025 as provisional and lists Annexures I–VII. For October 2025 final, use the November 2025 release dated 12 December 2025: https://mospi.gov.in/uploads/release_calendar/1765536182952_Press_Release_CPI_November_2025.pdf . It identifies October 2025 as final and November 2025 as provisional, and also lists Annexures I–VII.
- The official press release PDFs are available even if the Excel link is difficult to open. The eSankhyiki Data Catalogue is a separate module from Macro Indicators; its FAQ says Data Catalogue datasets are downloadable in Excel. Do not use the Macro Indicators parameter-download button as a substitute for the press-release annexures.
- For the provisional-to-final comparison, Annexure I contains general/group/sub-group CPI index values and Annexure VII contains the all-India general CPI year-on-year inflation time series. Retain the release PDF and original Excel file together with retrieval date and release date. Do not interpret latest-current API data as a historical release vintage.


### CPI provisional-to-final comparison — first historical release-vintage sample — 2026-11-13
The following are direct comparisons of official monthly MoSPI press releases. Values below are All-India Combined CPI (2012 base); index points and year-on-year inflation percentage points are distinct measures.

| Reference month | First release (provisional) | Next release (final) | Index: provisional → final | YoY inflation: provisional → final | Interpretation |
|---|---|---|---:|---:|---|
| Sep 2018 | 12 Oct 2018 | 12 Nov 2018 | 140.3 → 140.2 | 3.77% → 3.70% | Both changed at displayed precision |
| Sep 2019 | 12 Oct 2019 | 13 Nov 2019 | 145.8 → 145.8 | 3.99% → 3.99% | No displayed change |
| Sep 2020 | 12 Oct 2020 | 12 Nov 2020 | 156.5 → 156.4 | 7.34% → 7.27% | Both changed at displayed precision |
| Oct 2025 | 12 Nov 2025 | 12 Dec 2025 | 197.3 → 197.3 | 0.25% → 0.25% | No displayed change |

Evidence: September 2018 provisional release (12 Oct 2018), https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12oct18f.pdf ; the 12 Nov 2018 release reports September 2018 final inflation 3.70% and combined index 140.2, https://www.mospi.gov.in/sites/default/files/press_release/Press%20Statement.pdf . September 2019 provisional release, https://www.mospi.gov.in/sites/default/files/press_release/Press%20statement_1.pdf ; 13 Nov 2019 release reports September 2019 final combined inflation 3.99%, https://mospi.gov.in/sites/default/files/press_release/cpi_oct.pdf . September 2020 provisional release, https://mospi.gov.in/sites/default/files/press_release/Press%20Statementsept20.pdf ; 12 Nov 2020 release reports September 2020 final combined inflation 7.27% and index 156.4, https://mospi.gov.in/sites/default/files/press_release/CPI_Press_Statement_12nov20.pdf . October 2025 comparison uses the user's uploaded PIB copy of the 12 Nov 2025 MoSPI release and 12 Dec 2025 MoSPI release (Annexures VI and VII).

This is a small, deliberately selected sample, not a frequency estimate. It establishes that provisional-to-final changes can occur, and that some months show no change at published precision. The observed changes here are small (0.1 index point and 0.07 percentage point in Sep 2018 and Sep 2020), but they are not guaranteed to be small in all months or in unrounded source data. The 2019 and 2025 pairs are equality only at the published precision.

### Modelling implication for CPI vintages
- Preserve the first published provisional observation and the subsequent final observation as separate release-vintage records; never overwrite the provisional record with the final value.
- For historical simulation, use the provisional observation from its actual publication timestamp until the final observation becomes public. After the final release, use the final value. A model trained on today's latest historical CPI series alone would otherwise leak later finalisation into earlier prediction dates.
- Store at minimum: reference_month, series/sector, base_year, value_type (index/inflation), value, publication_timestamp, vintage_status (as published by MoSPI), source_release_url, retrieved_at, and original status/asterisk markers. Keep unrounded precision only if the source actually supplies it; do not infer it from rounded releases.
- The sample supports point-in-time vintage handling as a prudent data-engineering safeguard. It does not yet prove that CPI vintage changes materially affect Northgate model performance. That requires a later paired experiment comparing latest-vintage history against as-published point-in-time history on identical chronological splits, without touching the held-out test set during development.
- Do not label these provisional-to-final updates as evidence of post-final revisions. The inspected documents show the provisional current month and final previous month being published together; the sample does not establish a policy or pattern of revisions after an observation is marked final.


### Official CPI Excel annexure workbooks obtained and inspected — 2026-11-13
The user downloaded both original Excel workbooks from the MoSPI CPI Press Releases archive (green XLS icon), and both files were inspected locally with pandas/openpyxl:
- `Annexures for Press Release in Excel October 2025.xlsx` — sheets Annex-I through Annex-VII.
- `Annexures for Press Release in Excel November 2025.xlsx` — sheets Annex-I through Annex-VII.

The workbooks are the exact official annexure files sought. Annexure VI contains the All-India General CPI (2012=100) monthly index time series from Jan 2013; Annexure VII contains the corresponding year-on-year inflation series from Jan 2014. Annex-I provides detailed All-India group/subgroup CPI and CFPI data; Annexes II–V provide additional inflation/state/key-item breakdowns.

Direct workbook comparison for October 2025 (All Groups / General Index):
| Measure | October 2025 workbook (Oct provisional) | November 2025 workbook (Oct final) |
|---|---:|---:|
| Rural CPI index | 198.8 | 199.0 |
| Urban CPI index | 194.9 | 195.4 |
| Combined CPI index | 197.3 | 197.3 |
| Combined YoY inflation (Annexure VII) | 0.25% | 0.25% |

Thus, the aggregate combined index and inflation rate are unchanged at displayed precision, but the rural and urban general index values each increase by 0.2 and 0.5 respectively between provisional and final releases. This is important: comparing only the combined national headline would miss revisions/updates in its rural and urban components. Here, call these provisional-to-final updates, not post-final revisions. Do not infer unrounded equality from displayed rounded values.

Both workbooks contain 7 sheets (Annex-I, Annex-II, Annex-III, Annex-IV, Annex-V, Annex-VI, Annex-VII). Excel files are preferable for systematic extraction versus manually parsing PDFs. The archive's monthly XLS links should be the primary retrieval path for building a historical release-vintage inventory. Preserve original files, filenames, retrieval date and release date; retain PDF release alongside each workbook when available.


### CPI archive coverage, base transitions and first structured extract — 2026-11-13

#### Archive coverage: what is established vs not yet counted
- The MoSPI page is explicitly titled **“CPI Press Releases (Jan 2011 to Dec 2025)”**. At monthly frequency, that date span contains **180 possible reference months** (Jan 2011–Dec 2025 inclusive). The archive UI shows a paginated list of monthly release records and separate PDF/XLS actions.
- **Important limitation:** the live archive page's machine-readable response did not expose a complete list/count of XLS links during this research run. Therefore 180 is the number of monthly slots implied by the advertised coverage, **not yet a verified count of successfully downloadable Excel files**. A complete per-month link audit is still required before claiming 180 files exist.
- Official MoSPI metadata states that monthly releases include a PDF press release and an Excel annexure; it also says final indices for the penultimate month are released alongside provisional indices for the previous/current month. Sources: https://mospi.gov.in/sites/default/files/CPI/National_Metadata_Structure_for_CPI.pdf and https://mospi.gov.in/faq .
- Official CPI warehouse page describes the historical coverage: old 2010-base series Jan 2011–Dec 2014; revised 2012-base series from Jan 2013 onward; and 2012-base back series Jan 2011–Dec 2012. Source: https://cpi.mospi.gov.in/ . The back series is retrospective and must not be mistaken for what was available to users in 2011–2012.

#### Base-year regimes — do not concatenate raw index levels
| Publication/reference period | Base | Treatment |
|---|---|---|
| Jan 2011–Dec 2014 contemporaneous old series | 2010=100 | Preserve as its own series/vintage |
| Jan 2015–Dec 2025 contemporaneous revised series | 2012=100 | Preserve as a separate series |
| Jan 2026 onward | 2024=100 | New series; separate series identifier |
| Jan 2011–Dec 2012 2012-base back series | 2012=100 | Retrospective back series; not contemporaneously available in 2011–2012 |
| Jan 2013–Dec 2024 2024-base back series | 2024=100 | Retrospective back series; not contemporaneously available before its publication |

MoSPI FAQ confirms CPI began with base 2010=100 from January 2011 and changed to 2012=100 effective with January 2015; the first 2024-base release was January 2026. Sources: https://mospi.gov.in/faq and https://mospi.gov.in/sites/default/files/press_release/Press%20Release%20of%20CPI%20for%20January%202026.pdf (first 2024-base release; official PDF is also indexed at https://www.mospi.gov.in/uploads/latestreleasesfiles/1770893247472-Press%20Relase%20of%20CPI%20for%20Jan26.pdf).
- Do not join the three index levels directly or apply an undocumented linking factor. If a continuous index is required, select a documented official linked/back series and retain its derivation and availability date. For model features, inflation rates may be more comparable but still require base/regime and methodology flags.

#### First machine-readable extract from the supplied official November 2025 workbook
The November 2025 workbook (release dated 12 Dec 2025) was parsed from Annexure VI and VII:
- Annexure VI: **155 monthly combined General CPI index observations**, Jan 2013–Nov 2025 (2012=100).
- Annexure VII: **141 non-missing monthly combined General CPI year-on-year inflation observations**, Jan 2014–Nov 2025. April and May 2020 are explicit dashes because inflation was not compiled during the COVID-19 interruption; they remain missing, not zero.
- November 2025 is marked provisional in both series. October 2025 is final in this release.
- This is one **latest-vintage snapshot as of the 12 Dec 2025 release**, not a point-in-time archive of each month’s original publication vintage. It is useful for a non-vintage historical series, but cannot alone support a leakage-safe backtest.

#### Critical correction — October 2025 workbook comparison
An earlier note in this document incorrectly compared September 2025 final values from the October workbook with October 2025 provisional values, and incorrectly described them as the October provisional-to-final change. The workbook column labels show:
- October 2025 release (12 Nov 2025): September final → October provisional. General CPI index: Rural **198.8 → 199.0**, Urban **194.9 → 195.4**, Combined **197.0 → 197.3**.
- November 2025 release (12 Dec 2025): October final → November provisional. General CPI index: Rural **199.0 → 199.6**, Urban **195.4 → 195.9**, Combined **197.3 → 197.9**.
Therefore the actual October 2025 provisional-to-final comparison is:
| Sector | 12 Nov 2025 October provisional | 12 Dec 2025 October final | Difference |
|---|---:|---:|---:|
| Rural | 199.0 | 199.0 | 0.0 |
| Urban | 195.4 | 195.4 | 0.0 |
| Combined | 197.3 | 197.3 | 0.0 |
The combined year-on-year inflation rate is 0.25% in both releases at published precision. The earlier claimed rural/urban differences (198.8→199.0 and 194.9→195.4) were a month-alignment error and must not be used.
- The workbook Annexure VI/VII historical time series in the November 2025 workbook ends at Nov 2025; it is not an all-history vintage database.
- Source files supplied by user: `Annexures for Press Release in Excel October 2025.xlsx` and `Annexures for Press Release in Excel November 2025.xlsx`. Matching release PDFs are dated 12 Nov and 12 Dec 2025 respectively.

#### Release timing and vintage schedule caveats
- Do not hardcode “12th at 5:30 PM” for every historical release. Current MoSPI FAQ describes a regular 12th-day/next-working-day schedule and 5:30 PM, but actual inspected release PDFs include 4:00 PM releases (e.g. 12 Nov and 12 Dec 2025). Use each PDF's explicit date and embargo/publication time.
- The earliest 2011 releases used a different provisional revision convention: the official February 2011 release says January 2011 provisional indices had been released on 18 Feb 2011 and “would be revised with a time lag of two months”; it gives 18 Mar 2011 as the next release date. Source: https://mospi.gov.in/sites/default/files/press_release/t4_18mar11.pdf . Therefore the later “final previous month + provisional current month” schedule must not be assumed to describe all 2011 releases.
- The archive inventory must store the reference month separately from the release date and record the actual status/revision language in each document. Do not automatically infer that every next-month publication finalises the previous month across all eras.

#### Remaining work to reach a complete vintage dataset
1. Obtain a machine-readable inventory of every monthly archive row and its XLS/PDF URLs; verify actual link count (expected 180 slots, not yet proven 180 files).
2. Download and parse each Excel annexure, accommodating different sheet names/layouts across 2011–2014 (2010 base), 2015–2025 (2012 base), and 2026 onward (2024 base).
3. Parse each paired PDF to capture exact release date/time and provisional/final/revision status, including the early 2011 two-month revision rule.
4. Compare each reference month across successive releases and retain immutable observation-vintage records.
5. Only then create the final point-in-time macro feature table; do not treat the Dec 2025 historical snapshot as vintage-safe.


### CPI press-release archive inventory confirmed from full pagination — 2026-11-13
- User supplied screenshots of all four pages of the official MoSPI CPI Press Releases archive, with page size set to 50.
- Pagination shows 4 pages: 50 + 50 + 50 + 30 = **180 monthly release entries**, matching the displayed archive range January 2011 through December 2025 inclusive. This confirms the count of release-list entries, not the count of downloadable Excel files.
- The screenshots show both PDF (red) and Excel (green) action icons on recent entries, while many older entries show only the PDF icon. Therefore do not claim 180 Excel annexure workbooks exist. Exact monthly XLS coverage and the first/last month with an XLS link remain to be inventoried from the archive itself.
- Practical retrieval plan: use the green XLS action wherever present; where only PDF exists, preserve the PDF and extract annexures from it if the tables are available. Record per-month file availability and format explicitly (XLS, PDF-only, missing entry, or inaccessible).
- This archive is the authoritative discovery index for monthly release documents. Its existence does not prove that every listed release has comparable annexures, consistent table layouts, or directly comparable base-year series. Treat Jan 2011–Dec 2014 and later base periods separately, and inspect each release's own metadata before combining.


### CPI archive format inventory and PDF extraction feasibility — 2026-11-13
**Archive inventory from user-provided full-pagination screenshots:** page size 50; four pages; 50 + 50 + 50 + 30 = 180 monthly release entries (Jan 2011–Dec 2025). On page 1, green XLS icons are visible for exactly the 18 entries from July 2024 through December 2025 inclusive. From June 2024 backwards, the screenshots show red PDF icons only. Therefore current observed archive format coverage is 180 PDF entries and 18 XLS entries (the 18 XLS are a subset of the 180 PDF entries), subject to link-level download validation. Do not describe this as 180 Excel workbooks.

**PDF-only older releases are still usable for headline vintage extraction.** Official PDF examples were inspected:
- 12 Feb 2014 release for Jan 2014 (base 2010=100) explicitly states Jan 2014 provisional and Dec 2013 final, gives rural/urban/combined general indices and inflation in the press note, and includes Annex I with rural/urban/combined group/subgroup indices. Source: https://www.mospi.gov.in/sites/default/files/press_release/t4_12feb14.pdf . It has 4 pages and Annex I begins on page 2.
- 12 Mar 2014 release for Feb 2014 (base 2010=100) explicitly states Feb 2014 provisional and Jan 2014 final; combined headline inflation is 8.10% provisional for Feb and 8.79% final for Jan. Source: https://www.mospi.gov.in/sites/default/files/press_release/t4_12mar14.pdf .
- 12 Jan 2017 release for Dec 2016 (base 2012=100) explicitly labels Dec 2016 provisional and Nov 2016 final, and gives rural/urban/combined headline inflation and index values in the press note and Annexure I. Source: https://www.mospi.gov.in/sites/default/files/press_release/CPI_PR12jan17th.pdf .
This proves PDF-only entries can support at least the headline general CPI vintage extraction; annexure depth/layout varies by period and must be checked per document. Do not assume every PDF contains the same Annexure VI/VII time-series format found in recent XLS workbooks.

**Correct base-series chronology (distinguish original publication series from retrospective back-series):**
- Original contemporaneous CPI release series: Jan 2011–Dec 2014, base 2010=100.
- Original contemporaneous CPI release series: Jan 2015–Dec 2025, base 2012=100 (base change effective with Jan 2015 release).
- First release of CPI base 2024=100: 12 Feb 2026, for Jan 2026. MoSPI/PIB states CPI 2012 series remains through Dec 2025; CPI 2024 inflation series starts Jan 2026. A 2025 overlap is used to calculate linking factors, and retrospective 2024-base back-series is available for Jan 2013–Dec 2024. Do not treat the 2024-base 2025 overlap/linking data as a series investors could have observed during 2025. Sources: https://mospi.gov.in/uploads/documents/productKpiIcon/1770896304774-Press%20Relase%20of%20CPI%20for%20Jan26.pdf ; PIB explanation https://www.pib.gov.in/PressReleasePage.aspx?PRID=2291051&lang=1&reg=48 ; CPI warehouse https://www.cpi.mospi.gov.in/Default1.aspx .
- The current NMDS metadata's wording about 2024-base CPI from Jan 2025 onwards overlaps with its statement that the old 2012 series runs through Dec 2025. Resolve this using the dated first-release and PIB explanation: Jan 2025–Dec 2025 2024-base values are an overlap/linking series, not the contemporaneous official CPI release series. Preserve source vintage and release timestamp.

**Historical extraction coverage status:**
- Archive entries confirmed: 180.
- Visible XLS entries confirmed: 18 (Jul 2024–Dec 2025).
- PDF entries visible: 180.
- Older PDF-only release format can contain usable provisional-current/final-previous headline data, demonstrated for 2014 and 2017.
- Full month-by-month extracted vintage table and per-month exact publication timestamps are NOT yet built. Release dates/times must be parsed from each PDF, not imputed from a fixed monthly rule. The older MoSPI FAQ says 12th at 5:30 PM subject to next working day; the newer 2025/2026 releases use 4:00 PM, so hardcoding one time across the full history would be wrong.

**Extraction method proposed:** for each release PDF/XLS, extract the current reference month provisional General CPI index (rural, urban, combined) and inflation, plus the prior month final values, source release date/time, base year, file URL and extraction confidence. Cross-check each reference month's provisional value in release t against its final value in release t+1. Keep 2010=100 and 2012=100 histories in separate series. Retain raw PDF/XLS and a provenance log; flag OCR/manual corrections for review.


### PDF-only vintage extraction pilot — 2014 and 2016 — 2026-11-13
Two PDF-only historical month pairs were parsed directly from the official MoSPI PDFs, confirming the older archive is usable for headline General CPI vintages even without XLS files.

| Reference month | First release provisional (Rural / Urban / Combined index) | Following release final (Rural / Urban / Combined index) | First release inflation (R/U/C) | Following release final inflation (R/U/C) |
|---|---|---|---|---|
| Jan 2014 (base 2010) | 139.3 / 135.0 / 137.4 | 139.2 / 135.0 / 137.4 | 9.43 / 8.09 / 8.79% | 9.35 / 8.09 / 8.79% |
| Dec 2016 (base 2012) | 132.8 / 127.6 / 130.4 | 132.8 / 127.6 / 130.4 | 3.83 / 2.90 / 3.41% | 3.83 / 2.90 / 3.41% |

Jan 2014 evidence: 12 Feb 2014 PDF gives Jan provisional index and inflation (https://www.mospi.gov.in/sites/default/files/press_release/t4_12feb14.pdf); 12 Mar 2014 PDF gives Jan final index in Annex I and Jan final inflation in the press note (https://www.mospi.gov.in/sites/default/files/press_release/t4_12mar14.pdf). At displayed precision, only the rural index and rural inflation change (each down 0.1 index point / 0.08 percentage point); urban and combined are unchanged.

Dec 2016 evidence: 12 Jan 2017 PDF gives Dec provisional index and inflation (https://www.mospi.gov.in/sites/default/files/press_release/CPI_PR12jan17th.pdf); 13 Feb 2017 PDF gives Dec final index and inflation (https://www.mospi.gov.in/sites/default/files/press_release/CPI_PR_13feb17m.pdf). No displayed change in rural, urban, combined index or inflation.

These examples are extraction pilots only, not a complete vintage dataset or a statistically representative sample. PDF text extraction exposes the key headline tables for these periods; automated extraction across the full 180-PDF archive remains unimplemented and needs validation against page/table layout changes.


### Important refinement — CPI provisional-to-final lag is not constant across the archive — 2026-11-13
The early 2010-base series explicitly documents a two-month revision/finalisation lag: the 18 March 2011 release says provisional indices would be revised with a time lag of two months; the 18 July 2011 release publishes June 2011 provisional and April 2011 final. This means the archive's early release vintages cannot be modelled using a universal “next month's release finalises last month's provisional” assumption. Sources: https://mospi.gov.in/sites/default/files/press_release/t4_18mar11.pdf ; https://mospi.gov.in/sites/default/files/press_release/t4_18july11.pdf .

By December 2012, the release for November 2012 labels November provisional and October final, while also providing September final in Annex I. Thus the finalisation lag / number of months shown in each release changed over time and must be read from each release's explicit labels, not inferred from a fixed rule. Source: https://www.mospi.gov.in/sites/default/files/press_release/t4_12dec12.pdf .

**Vintage database rule updated:** each release record must identify the reference month and status of every observation exactly as labelled in that document. A reference month may have one or more provisional observations before finalisation; preserve all published stages if present. For a historical simulation, the active value at time t is the latest officially published record whose release timestamp is <= t, regardless of whether that record is labelled provisional or final. Do not hardcode finalisation to t+1.

**Extraction validation correction:** earlier sample comparisons are selected spot checks only. The Jan 2014 and Dec 2016 provisional/final examples remain pilot cases, but full row-level comparisons should be rechecked against the actual PDF text and table headings before the dataset is used. Never infer values from a later time-series annexure alone, because it may only show the latest finalised snapshot.

**Availability vs extraction status:** screenshots establish 180 archive entries and visible XLS icons for Jul 2024–Dec 2025 (18 entries); older entries appear PDF-only. This is a screenshot-based inventory, not a link-by-link automated crawl. The official NMDS portal confirms that monthly press releases are PDFs and annexures are Excel, and that time-series warehouse downloads are separate from the press-release vintage documents. Source: https://nmds.mospi.gov.in/ .


### Cross-era extraction pilot — 2011, 2015, 2019/20 and archive methodology — 2026-11-13
A further direct extraction test confirms that the press-note format supports vintage records across the 2010 and 2012 base eras, but the vintage lag and available measures changed.

**2011 (base 2010=100):** The 18 March 2011 release explicitly says January 2011 provisional figures would be revised with a two-month lag; the February release itself gives rounded general index only as 107 rural / 104 urban / 105 combined, and does not yet publish annual inflation because a full year of observations was not available. In the 20 June 2011 release, May is provisional while March is final; by the 18 July 2011 release, June is provisional and April is final. This demonstrates both a longer lag and that early 2011 releases may not contain the modern monthly YoY inflation table. Sources: https://mospi.gov.in/sites/default/files/press_release/t4_18mar11.pdf ; https://mospi.gov.in/sites/default/files/press_release/t4_20june11.pdf ; https://mospi.gov.in/sites/default/files/press_release/t4_18july11.pdf .

**2015 base transition and January 2015 vintage (base 2012=100):** The first 2012-base release (12 Feb 2015) gives Jan 2015 provisional general indices 120.2 rural / 118.5 urban / 119.4 combined, and inflation 5.25% / 4.96% / 5.11%. The 12 Mar 2015 release labels Jan 2015 final and reports indices 120.3 / 118.5 / 119.5 and inflation 5.34% / 4.96% / 5.19%. Therefore Jan 2015 changed by +0.1 rural, 0.0 urban, +0.1 combined index points; inflation changed +0.09, 0.00, +0.08 percentage points respectively. Sources: https://mospi.gov.in/sites/default/files/press_release/cpi_pr_12feb15t.pdf ; https://www.mospi.gov.in/sites/default/files/press_release/cpi_pr_12mar15th.pdf .

**2019/20 release format:** The 13 Jan 2020 release (5:30 PM embargo) labels Dec 2019 provisional and Nov 2019 final, reports December general CPI inflation 7.26% rural / 7.46% urban / 7.35% combined and indices 152.2 / 148.3 / 150.4. It explicitly identifies the following release date as 12 Feb 2020 for Jan 2020. This confirms the standard previous-month-final convention by 2020; it does not itself supply the subsequent final Dec 2019 observation, which must be read from the Feb 2020 release. Source: https://mospi.gov.in/sites/default/files/press_release/cpi_pr_13jan20.pdf .

**Timestamp handling:** Release PDFs may carry an embargo timestamp (e.g. 5:30 PM on 12 Feb/12 Mar 2015; 5:30 PM 13 Jan 2020), while PIB page publication metadata can show the actual posted time. Store the source's explicit embargo/publication time and distinguish it from a page-crawl timestamp. For market simulation, use the earliest confirmed public availability time; when only embargo time is available, treat it conservatively as the earliest release time, not assume the date alone. Check whether publication occurred before or after NSE cash close and map to the next eligible session accordingly.

**Extraction feasibility conclusion (still pilot, not complete archive):** The headline general index can be extracted from PDF text in both 2011 and 2015; the 2011 rounded integer precision is lower than later decimal precision. Inflation YoY is not consistently available from the beginning of the 2010-base series; do not manufacture missing values. A robust parser needs period-specific schema branches: 2011–2011 initial releases (rounded index, no YoY), 2012 onward (inflation appears once full year is available), 2015 base transition (new base and methodology), modern 2012-base releases (index + YoY tables), and 2024-base release era. Always preserve source precision and source-reported missingness.


### Alternative machine-readable CPI source investigated — IEM Lab archive and official API — 2026-11-13
A third-party compilation, IEM Lab Living Inflation Data, reports an India MoSPI CPI archive with 8,689 series, 315,757 observations, period Jan 2011–Sep 2026, six vintages, daily polling, and raw resources named `mospi/cpi/*.json.gz`; it attributes the underlying source to MoSPI/eSankhyiki and the Government Open Data License (India). Source landing page: https://www.iemlab.org/livingdata/sources/mospi . Its six “vintages” are not demonstrated to be six historical monthly MoSPI release vintages; they may be snapshots of the third-party collector's dataset. Therefore do NOT use them as provisional/final release history unless the raw archive metadata and timestamps prove that interpretation. It is a lead for bulk latest-series extraction and cross-checking, not currently a validated source for point-in-time vintage reconstruction.

IEM Lab's India CPI page reports quality-register findings including missing/suppressed values and source-published blank fields, including item-level missingness in parts of 2015/2018/2019 and March–May 2020. This reinforces that third-party compiled datasets must be checked against original MoSPI records and that nulls must not be silently imputed. Source: https://www.iemlab.org/livingdata/IND/cpi .

Official eSankhyiki CPI API documentation confirms an open, paginated endpoint `/api/cpi/getCPIData` covering base years 2010, 2012 and 2024; bearer token optional, requests rate-limited per IP. This is useful for reproducible extraction of the current API dataset and cross-checking base-series values, but the documentation does not say it preserves historical publication vintages. Do not mistake a current API response for an as-published release archive. Source: https://esankhyiki.mospi.gov.in/macroindicators?product=cpi&tab=api .

Official CPI warehouse documentation describes downloadable time-series, item-level and annual inflation tables and the old 2012-base data through Dec 2025. These are useful for coverage validation and latest-value history, but they are distinct from monthly press-release vintages. Source: https://www.cpi.mospi.gov.in/Default1.aspx .

**Current source decision:** use MoSPI monthly press-release PDFs/XLS as the primary vintage source; use the official API/warehouse as cross-checks and to fill latest-series context where clearly labelled; use IEM Lab only as a secondary discovery/QA lead until its raw archive vintage semantics and licensing are independently checked. No third-party vintage data has been merged into Northgate.


### CPI publication timestamp regime — verified market-close implications — 2026-11-13
The official PIB notice dated 5 Nov 2024 states that MoSPI changed the CPI release time from 5:30 PM to 4:00 PM on the 12th (or next working day if holiday), effective with the October 2024 CPI release on 12 Nov 2024. Source: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2070932 . Therefore the timestamp parser must use at least two time regimes for the modern monthly schedule: pre-change 5:30 PM, and from 12 Nov 2024 onward 4:00 PM, while still reading the actual date/time on each release. Both scheduled times are after the regular NSE cash-market close (3:30 PM), so for a close-to-close daily feature the earliest usable market observation is normally the next eligible NSE session. Holiday shifts, exceptional releases, and any evidence of earlier public availability must be checked individually; do not infer exact publication time from the scheduled convention alone.

The official CPI metadata states provisional monthly figures are disseminated on the 12th of the following month (next working day if holiday) and final indices for the penultimate month are released alongside the provisional previous month. This describes the modern dissemination convention, not the earlier 2011 two-month finalisation regime documented in the original releases. Keep both the general metadata rule and explicit historical release-level labels; the latter take precedence for point-in-time reconstruction. Sources: https://mospi.gov.in/sites/default/files/CPI/National_Metadata_Structure_for_CPI.pdf ; https://www.pib.gov.in/PressReleasePage.aspx?PRID=2070932 .


## MoSPI monthly CPI workbook extraction — 2026-11-13

### Source files inspected
- Materialized and inspected all 18 Project-backed monthly Excel workbooks from July 2024 through December 2025. The workbooks were already present in Project files; no further upload was needed.
- Each workbook's Annex-I and Annex-II were inspected. The extraction uses the `General Index (All Groups)` row: Annex-I contains rural, urban and combined index values for the previous reference month (Final) and current reference month (Provisional); Annex-II contains the current reference month's year-on-year inflation rates.
- Created `data/external/cpi_mospi_2012_release_vintages_2024-07_to_2025-12.csv`: 108 rows, 10 columns, 18 release-workbook months, 19 distinct reference months (June 2024–December 2025), and three sectors (rural, urban, combined). Each release contributes three prior-month Final rows and three current-month Provisional rows. The CSV was fetched back from GitHub and verified to contain 108 data rows.
- The CSV preserves the source workbook name and release-workbook month. `publication_timestamp` is intentionally blank because the Excel annexures do not encode the actual release date/time. This dataset is an extraction of published values, not yet a point-in-time-ready macro feature table.

### Provisional-to-final index revision check
Comparing each month's Provisional index in its own workbook with the next workbook's Final index for the same reference month gives 17 matched months (July 2024–November 2025):
- Combined index changed in 4/17 months; largest absolute change 0.2 index points.
- Rural index changed in 1/17 months; largest absolute change 0.1 points.
- Urban index changed in 5/17 months; largest absolute change 0.4 points.
- Combined examples: July 2024 192.9 to 193.0; January 2025 193.5 to 193.4; July 2025 196.0 to 196.1; September 2025 197.2 to 197.0. Other matched combined months were unchanged at the workbook's displayed precision.
- October 2025 combined index is 197.3 provisional and 197.3 final; November 2025 is 197.9 provisional and 197.9 final. The corresponding 0.25% and 0.71% figures in this extraction are provisional rates from Annex-II; do not label them as final inflation rates merely because the index later finalised unchanged.
- This is a small, 17-month observed revision sample, not proof that revisions are generally immaterial. Preserve all vintages and do not replace provisional observations with final values in historical simulations.

### Separate uploaded `cpi_33.xlsx` inspection
- The workbook contains one sheet (`CPI Data`) with 31,460 rows and 15 columns. It contains base_year=2024, series=Current, 22 monthly periods (January 2025–October 2026), 37 state/UT labels and Rural/Urban/Combined sectors.
- There are 1,430 rows per month and zero duplicate keys across the available geographic/sector/division/category fields.
- All 17,160 rows in 2025 have null inflation values; all 14,300 rows in 2026 have populated inflation values. This agrees with the previously recorded limitation that the new base-year series does not provide 2025 YoY inflation in the API extract.
- The workbook itself does not contain publication timestamps or historical release-vintage identifiers. Its origin/retrieval metadata has not been established in this extraction. Treat it as a separate current-series snapshot for validation/cross-checking, not as an as-published 2025 vintage archive.
- Do not join 2024-base 2025 observations into 2025 market decisions: the new series was first published in February 2026. Keep the 2012 and 2024 bases separate.

### Extraction limitations and next work
1. The monthly Excel workbooks identify the reference month and provisional/final status, but not the actual publication timestamp. Populate release dates/times from the corresponding official MoSPI press-release PDFs/archive before using CPI in a leakage-sensitive market backtest.
2. The CSV currently includes YoY inflation for the Provisional current-month rows only; previous-month Final rows have blank inflation fields. Annex-VI/VII historical tables should be extracted separately and reconciled by vintage before creating a final macro feature table.
3. Preserve source precision (the workbooks generally display one decimal for index levels and two decimals for inflation) and explicit missing values; do not infer unavailable observations.
4. The 17-month revision comparison is restricted to July 2024–November 2025 because the December 2025 provisional has no January 2026 2012-base follow-up workbook in the supplied set.


### Historical time-series snapshot extraction — 2026-11-13
- A second extraction captures the full historical CPI index and year-on-year inflation tables from every supplied workbook that contains them. The source sheet names differ by release (Annex-V/VI in early 2025 and late 2024; Annex-VI/VII in later 2025 releases), so extraction matched the table title and Year/month layout rather than assuming a fixed annex number.
- Added `data/external/cpi_mospi_2012_historical_table_snapshots_2024-07_to_2025-12.csv`: 3,990 data rows across 14 release-workbook snapshots; 2,093 CPI-index observations (Jan 2013–Dec 2025) and 1,897 inflation observations (Jan 2014–Dec 2025). The file preserves release-workbook month, reference month, series, numeric value, whether the source value carried a provisional asterisk, the original raw value, source workbook and sheet. The complete 3,990-row GitHub file was fetched back and verified after correcting chunk-boundary handling.
- Four supplied workbooks (July–October 2024) do not include the historical time-series annexures; their monthly Annex-I/II values are still captured in the separate 108-row release-vintage CSV.
- The historical tables contain 156 monthly CPI index observations and 142 monthly inflation observations per full snapshot. The two missing inflation months are April and May 2020, represented as absent/dash in the source during the COVID collection disruption; they are not imputed.
- Across the 14 available snapshots, only three reference months have more than one displayed CPI index value (January, July and September 2025), and only those same three months have more than one displayed inflation value. The largest observed range is 0.2 index points and 0.10 percentage points respectively. This is an observation about the supplied snapshot vintages only; it does not establish that earlier CPI history was never revised.
- The asterisk is retained explicitly as `provisional_marker`; unstarred historical cells are not independently reclassified beyond the source table. Use release-workbook month as a vintage label until exact publication dates/times are mapped.

### Revised next step
The extraction layer is now present in the repository. Before merging CPI into market features, map each monthly workbook to its official MoSPI press-release publication date/time (and confirm the post-close NSE availability session), reconcile the historical Annex-V/VI/VII tables with the monthly Annex-I/II vintages, and then build an as-of CPI feature table. Do not use the current 2024-base snapshot as a substitute for the 2012-base values that investors actually saw in 2025.


### Official CPI release-date/time cross-check — 2026-11-13
The monthly Excel files do not contain publication timestamps. A first cross-check against official MoSPI press-release PDFs and its Advance Release Calendar confirms that actual release dates must be stored separately from the workbook's reference month:
- July 2024 CPI: released 12 Aug 2024, embargoed until 5:30 PM.
- August 2024 CPI: released 12 Sep 2024, embargoed until 5:30 PM.
- September 2024 CPI: released 14 Oct 2024, embargoed until 5:30 PM (not the nominal 12th; the ARC allowed the 14th).
- October 2024 CPI: released 12 Nov 2024, embargoed until 4:00 PM.
- November 2024 CPI: released 12 Dec 2024, embargoed until 4:00 PM.
- December 2024 CPI: released 13 Jan 2025, embargoed until 4:00 PM.
- January 2025 CPI: released 12 Feb 2025, embargoed until 4:00 PM.
- February 2025 CPI: released 12 Mar 2025, embargoed until 4:00 PM.
- March 2025 CPI: released 15 Apr 2025, embargoed until 4:00 PM (the expected ARC date was 14 April, so the actual PDF date must take precedence).
- May 2025 CPI: released 12 Jun 2025, embargoed until 4:00 PM.
- June 2025 CPI: released 14 Jul 2025, embargoed until 4:00 PM.
- July 2025 CPI: released 12 Aug 2025, embargoed until 4:00 PM.
- August 2025 CPI: released 12 Sep 2025, embargoed until 4:00 PM.
- September 2025 CPI: released 13 Oct 2025, embargoed until 4:00 PM.
- October 2025 CPI: released 12 Nov 2025, embargoed until 4:00 PM.
- Dates for the remaining workbook months still need direct official-PDF verification; do not fill them solely from a planned calendar.

Official source references:
- MoSPI Advance Release Calendar (updated 1 Aug 2024; expected dates, explicitly subject to change): https://www.mospi.gov.in/sites/default/files/main_menu/CPI_ARC/ARC_PSD_1aug2024.pdf
- July 2024 PDF: https://www.cpi.mospi.gov.in/PDFile/Press/PR%20July%202024.pdf
- August 2024 PDF: https://www.mospi.gov.in/sites/default/files/press_release/CPI_PR_12sep24.pdf
- September 2024 PDF: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_14oct24.pdf
- October 2024 PDF: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12nov24.pdf
- November 2024 PDF: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12dec24.pdf
- December 2024 PDF: https://www.cpi.mospi.gov.in/PDFile/Press/PR%20December%202024.pdf
- January 2025 PDF: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12Feb25.pdf
- February 2025 PDF: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12Mar25.pdf
- March 2025 PDF: https://www.cpi.mospi.gov.in/PDFile/Press/PR%20March%202025.pdf
- May 2025 PDF: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12Jun25.pdf
- June 2025 PDF: https://www.mospi.gov.in/sites/default/files/press_release/CPI_PR_14Jun25.pdf (the PDF itself states 14 July 2025; preserve the content's date, not the filename)
- July 2025 PDF: https://www.cpi.mospi.gov.in/PDFile/Press/PR%20July%202025.pdf
- August 2025 PDF: https://www.cpi.mospi.gov.in/PDFile/Press/PR%20August%202025.pdf
- September 2025 PDF: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_13oct25.pdf
- October 2025 PDF: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12nov25.pdf

The official FAQ currently states a general 5:30 PM schedule, but contemporaneous PDFs show a 4:00 PM embargo for the later regime. For backtesting, use each PDF's dated embargo/release time, not the FAQ's generic schedule or the ARC's expected date. Both regimes are after the NSE cash close (3:30 PM); the first eligible NSE session after the actual release timestamp is the conservative feature-availability date. Verify holidays/session mapping separately.


#### Additional date verification
- November 2025 CPI: released 12 Dec 2025, embargoed until 4:00 PM. The release explicitly states that December 2025 CPI is scheduled for 12 Jan 2026. Source: https://www.mospi.gov.in/uploads/latestreleasesfiles/1765535702131-Press%20Release_CPI_November_2025.pdf
- December 2025 CPI: released 12 Jan 2026, embargoed until 4:00 PM; this was the last release on base 2012=100. Source: https://mospi.gov.in/uploads/release_calendar/1768214980837_Press_Release_of_CPI_for_December_2025.pdf
- The March 2025 release (dated 15 Apr 2025) says April 2025 CPI was due 12 May 2025. The corresponding April PDF's actual embargo/date has not yet been independently retrieved, so 12 May remains a scheduled date rather than a verified actual timestamp in this register. Source for scheduled date: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_15Apr25.pdf

The remaining gap in the release-date register is the direct PDF confirmation for the April 2025 reference-month workbook. Keep its timestamp blank until that PDF is located. The other 17 workbook reference months now have an official PDF date/time or a release PDF explicitly establishing the next scheduled date; only direct-confirmed timestamps should be used for production as-of joins.


### Release availability and next-session map
- Added `data/external/cpi_mospi_2012_release_availability_map_2024-07_to_2025-12.csv` (18 rows). It separates reference month from actual release date, embargo time (IST), evidence status, next NSE cash-market session, source URL and notes.
- Seventeen of the 18 dates are directly supported by official MoSPI press-release PDFs. April 2025 reference-month CPI remains `scheduled_only`: the preceding March release says 12 May 2025 was the next scheduled date, but the corresponding April PDF's own embargo/date has not yet been independently verified. Its actual date/time and next session remain blank.
- All verified CPI releases in this set occurred after the NSE cash-market close. The conservative availability date is therefore the next eligible NSE session, not the reference month and not the release date itself. Weekend transitions are accounted for (e.g. 12 Sep 2025 release -> Monday 15 Sep 2025 session; 12 Dec 2025 release -> Monday 15 Dec 2025 session).
- The map's next-session field was checked against NSE's published 2024, 2025 and 2026 equity-market holiday calendars; official NSE regular equity hours show a 15:30 close. Sources: https://nsearchives.nseindia.com/content/circulars/CMTR59722.pdf ; https://nsearchives.nseindia.com/content/circulars/CMTR65587.pdf ; https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf ; https://www.nseindia.com/resources/exchange-communication-holidays
- The release availability map is a separate audit table; it has not yet been merged into the two extracted observation CSVs. Keep the April 2025 row unavailable for point-in-time features until its own PDF is verified.


## CPI vintage extraction and point-in-time alignment — 2026-11-13

### April 2025 source clarification
- The newly supplied file named `Annexures for Press Release in Excel April 2025.xlsx` is an Excel annexure workbook, not a PDF. It contains all seven annexures, including Annex-VI (historical All-India General CPI index, base 2012=100) and Annex-VII (historical year-on-year inflation, base 2012=100).
- Its Annex-I explicitly labels March 2025 as final and April 2025 as provisional. Annex-VI marks the April 2025 combined index (192.6) provisional; Annex-VII marks April 2025 inflation (3.16%) provisional. The workbook therefore closes the April 2025 workbook gap in the monthly Excel sequence.
- The corresponding official MoSPI press release PDF is dated 13 May 2025 and embargoed until 4:00 PM. PIB records it as posted 13 May 2025 at 4:00 PM (PRID 2128387). The prior expected date of 12 May was not the actual publication date. Source PDF: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_13May25.pdf ; PIB: https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2128387

### Extracted point-in-time history
- The 18 monthly workbooks July 2024–December 2025 were inspected. The Annex-VI/VII historical time-series tables are present in 14 workbooks from November 2024 through December 2025. These contain 3,990 long-form records: 2,093 CPI index observations and 1,897 YoY inflation observations, covering reference months January 2013–December 2025 (index) and January 2014–December 2025 (inflation).
- Asterisks in the source tables are preserved as `provisional_marker` and in `raw_value`; missing values and dash markers are not imputed. The extracted snapshots contain 26 provisional-marked values. No duplicate keys were found for (release_workbook_month, reference_month, series).
- Each snapshot is a distinct vintage: a later workbook may revise a prior reference month's value. Never replace the vintage history with only the latest value when building historical model features.
- The separate `cpi_33.xlsx` file is a 2024-base CPI snapshot (31,460 rows, January 2025–October 2026), not a contemporaneous 2012-base vintage archive. It must remain a separate base-year series and cannot be backfilled into 2025 decision dates.

### Publication-time mapping and feature availability
- Added `data/external/cpi_release_availability_map_2012base.csv`, with 18 reference-month/workbook-month rows, actual release dates, embargo times, source links and next eligible NSE sessions. The April 2025 release is verified as 13 May 2025 at 16:00 IST, becoming eligible from the 14 May 2025 NSE session.
- The official release-time change was announced 5 November 2024: CPI moved from 17:30 to 16:00, beginning with October 2024 CPI. Both regimes are after NSE cash-market close (15:30); use the next eligible NSE session, not the reference month or same-day close. Source: https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2070932&lang=2&reg=48
- Added `scripts/build_cpi_vintages.py` to reproducibly extract Annex-VI/VII into long-form vintage records. It can attach actual publication and next-session availability fields using the release map. The script was committed and fetched back for verification; it has not yet been run locally against the user's full input folder.
- The point-in-time merge rule is: for a simulated decision date, select only the latest release vintage whose `available_from_session` is on or before that date, and select the matching reference-month observation from that vintage. Keep base year, series, reference month, release date, vintage marker and source metadata.
- Do not create a daily market-aligned feature table until the user's actual NSE session calendar / modelling panel is available in the repository or working environment. The CPI vintage table is the auditable source layer; a later deterministic join can carry the latest known value forward only after its availability session.
- Remaining limitation: release-time mappings for the 18 monthly workbooks are based on the official release PDFs/PIB evidence linked in the CSV. Recheck each linked PDF if any release date or embargo time is changed in a later official archive. Historical time-series Annex-VI/VII snapshots start in November 2024; the earlier July–October 2024 workbooks do not contribute those cumulative sheets to this extracted vintage panel.


### Reproducibility correction — annexure numbering and point-in-time event output
- A code review found that the original extraction script assumed the cumulative historical index/inflation tables always appeared in Annex-VI/VII. That assumption is false: November 2024 through March 2025 use Annex-V (index) and Annex-VI (inflation); from April 2025 the tables move to Annex-VI/VII. The script was corrected to classify the tables by their titles/content ("General CPI", "Inflation rate", base 2012, "Since January") across all workbook sheets.
- Re-ran the corrected detection logic against all 18 workbooks: 28 historical time-series sheets detected, 3,990 rows, 14 release snapshots, 156 distinct reference months, 26 provisional markers, zero duplicate keys. The extracted rows exactly match the previously generated 3,990-row snapshot file.
- Added the timestamp-enriched 3,990-row vintage history as two CSV parts in `data/external/` to avoid a single oversized file: part 1 covers release snapshots Nov 2024–May 2025; part 2 covers June–December 2025. The former one-file upload was removed after its full contents could not be verified; use the two split files instead.
- Added `cpi_mospi_2012base_release_events_2024-07_to_2025-12.csv`, an 18-row compact table of each release's current-month provisional combined index and YoY inflation, with actual release timestamp and first eligible NSE session. April 2025 becomes available on 14 May 2025 following its actual 13 May 16:00 release.
- Added `data/external/README_CPI.md` describing the files, base-year boundaries, annexure-numbering change and backward as-of join rule.
- The as-of event source is ready, but a daily market-aligned feature table has not yet been generated: the 29,484-row market panel remains local to the user's Mac and is not present in the GitHub repository. Do not substitute an invented calendar or synthetic sessions. Once that market panel is accessible, join on its actual trading dates using the latest event with `next_nse_session <= market_date`.


### Leakage-safe market-panel join — prepared 2026-11-13
- Added `scripts/merge_cpi_release_events.py`. It performs a backward as-of join from actual market dates to the latest CPI release event whose `next_nse_session` is on/before the market date. It preserves the market panel's row order, leaves dates before the first event unmatched, and checks for duplicate CPI availability sessions and future-dated matches.
- Added `tests/test_cpi_asof.py` with tests for release-day exclusion/next-session inclusion, original market-row ordering and duplicate event rejection. The committed pytest file has not yet been run in the repository environment.
- A separate synthetic boundary check was executed in the analysis environment: 15 April 2025 (release date) correctly retained the prior CPI event; 16 April switched to March 2025 CPI; 13 May retained March CPI; 14 May switched to April CPI. Result: PASS for these four date boundaries.
- A daily join against the actual market panel is still pending because the market panel CSV is not available in GitHub or the current Project file list. The script is ready to run when that exact local dataset is supplied; no synthetic trading calendar has been substituted.

## CPI source extension research — 2026-11-13

### Official source findings
- MoSPI's CPI warehouse explicitly lists the 2010=100 series for Jan 2011–Dec 2014, the 2012=100 series from Jan 2013 through Dec 2025, and a back series on 2012=100 for Jan 2011–Dec 2012. This supports a long historical level series, but does not itself prove when each historical value became public. Source: https://www.cpi.mospi.gov.in/Default1.aspx
- The current National Metadata Structure states that CPI data on the old 2012 base are available through Dec 2025 in the CPI warehouse; the new 2024-base series is published from Jan 2025, with a back series from Jan 2013 to Dec 2024 available on eSankhyiki. It says data are disseminated at 4 PM on the 12th of each month (or next working day if the 12th is a holiday), and that the provisional current-month index and final penultimate-month index are released together. Sources: https://mospi.gov.in/sites/default/files/CPI/National_Metadata_Structure_for_CPI.pdf ; https://esankhyiki.mospi.gov.in/macroindicators?product=cpi&tab=api
- The eSankhyiki catalogue exposes individual CPI dataset entries with a Release Date and table identifiers, and lists hundreds of CPI datasets. This may provide a more structured way to reconstruct official release dates and retrieve release-specific tables than manually guessing PDF URLs. Example catalogue: https://esankhyiki.mospi.gov.in/catalogue-main/catalogue?product=CPI
- The eSankhyiki CPI API is documented as an open, paginated endpoint covering base years 2010, 2012 and 2024. It is useful for retrieving current available observations, but the public description does not establish a historical as-published vintage archive. API endpoint: /api/cpi/getCPIData; docs: https://esankhyiki.mospi.gov.in/macroindicators?product=cpi&tab=api
- MoSPI's current release policy says provisional CPI for the reference month and final indices for the preceding month are published together. Do not collapse these into a single timeless series: the observation's reference month, provisional/final status, release date, and the value as published in that release are distinct fields.
- The new 2024-base back series is a retrospectively constructed linked series. It must not be treated as information available to a model in 2013–2024. Keep it separate from contemporaneously published 2012-base vintages.

### What this means for Northgate
- We can likely extend current historical CPI observations well before Aug 2024 from the official warehouse/API. That would improve descriptive macro coverage, but it does not by itself create point-in-time training features.
- For a leakage-safe feature, we need a release-event ledger: reference month, exact release date, publication time, current-month provisional value, preceding-month final value, base year, source URL/table ID, and first eligible NSE session.
- For a release-specific value archive, prefer monthly MoSPI annexure workbooks/PDFs or release-specific eSankhyiki catalogue records. The current API/warehouse snapshot alone should be labelled current-vintage, not historical as-published.
- The metadata's regular 12th/next-working-day and 4 PM rule is a useful default for recent releases, but actual release calendars and exceptional dates must be verified. For older 2012-base releases, do not assume the post-November-2024 16:00 regime; verify the historical publication-time regime from official source documents.
- The 2010=100, 2012=100 and 2024=100 series are separate statistical bases. Do not concatenate index levels across base breaks or use a retrospectively linked 2024-base series as a contemporaneous historical feature.

### Next research step
Pilot the eSankhyiki CPI catalogue/API to identify a stable all-India combined General CPI series for base 2012, confirm pagination and exact field semantics, and test whether catalogue records expose release dates and downloadable monthly annexures across 2016–2025. In parallel, sample historical press releases to verify actual release dates and time-of-day conventions. Only then decide whether the historical release ledger can be built reproducibly.

### eSankhyiki catalogue/API pilot — additional findings (2026-11-13)
- The current eSankhyiki CPI API documentation describes an open, paginated endpoint at `/api/cpi/getCPIData`, covering base years 2010, 2012 and 2024. Guest requests are allowed but rate-limited; the portal's Swagger preview returns only the first 10 records. Source: https://esankhyiki.mospi.gov.in/macroindicators?product=cpi&tab=api
- The current API's OpenAPI schema is distinct from the older 2023 MoSPI API manual. The older manual documents `/api/getCPIIndex`, requires signup/login for pagination beyond the first 10 records, and exposes year/month/state/group/subgroup/sector filters. Do not build against the old endpoint without confirming it is still supported. Sources: https://github.com/nso-india/esankhyiki-mcp/blob/main/swagger/swagger_user_cpi.yaml ; https://www.api.mospi.gov.in/API/CPI%20API%20User%20Manual.pdf
- The official eSankhyiki Data Catalogue provides release-specific CPI table records with a release date and table identifier. A current example is All India Combined (General), base 2024=100, reference period August 2026, released 14 September 2026, table ID CPIMCY26004AUG. Catalogue records also expose a route for viewing tables/charts and downloadable statement files. Source: https://esankhyiki.mospi.gov.in/catalogue-main/catalogue?product=CPI
- The official MoSPI press-release archive is searchable and confirms historical CPI releases. Sample official 2016 PDFs show the embargo timestamp and actual release date explicitly: January 2016 CPI released 12 February 2016 at 17:30; April 2016 released 12 May 2016 at 17:30; March 2016 released 12 April 2016 at 17:30; October 2016 released 15 November 2016 at 17:30; November 2016 released 13 December 2016 at 17:30. Sources: https://mospi.gov.in/sites/default/files/press_release/cpi_pr_12feb16f.pdf ; https://www.mospi.gov.in/sites/default/files/press_release/cpi_pr_12may16th.pdf ; https://mospi.gov.in/uploads/documents/CPI/Press/PR%20March%202016.pdf ; https://mospi.gov.in/sites/default/files/press_release/cpi_pr_15nov16t.pdf ; https://www.mospi.gov.in/sites/default/files/press_release/CPI_PR13dec16t_0.pdf
- The MoSPI CPI FAQ currently says the 2012-base CPI release is at 5:30 PM on the 12th (or next working day), while newer metadata/current eSankhyiki pages describe a 4 PM dissemination convention. This is a documentation/version conflict. For Northgate, use release-specific PDF embargo timestamps whenever available; do not infer all historical times from the current FAQ or current metadata. Sources: https://mospi.gov.in/faq ; https://mospi.gov.in/sites/default/files/CPI/National_Metadata_Structure_for_CPI.pdf
- A third-party CPI archive surfaced in research with month-by-month pages, claimed release-file hashes, and explicit “as published” values, including Nov 2016 headline inflation 3.6%. This is a discovery lead only; no values are accepted into Northgate until they are independently reconciled against official MoSPI releases/workbooks. Example: https://deshboard.app/data/prices/inflation/2016-11
- Another third-party guide claims to offer MoSPI 2012-base combined CPI data from Jan 2016–Dec 2025 with a 2026-08-08 vintage. This appears to be a current-vintage historical dataset, not proof of original monthly release vintages. Do not use it as point-in-time data without release-by-release verification. Source: https://measure.thisindianlife.today/guides/cpi/

### Updated research conclusion
The official catalogue is now the preferred discovery route for historical monthly release statements because it exposes release dates and table IDs; the official press-release PDF remains the strongest source for actual publication/embargo time. The current API can provide structured observations but is not yet proven to preserve historical vintages. Next pilot: identify the catalogue's stable query/filter or table-download URL pattern for 2016–2025, retrieve a small 3-month sample (including a normal 12th release and a delayed/holiday release), and reconcile headline combined General index/inflation values and status against the official PDFs. Only after that sample passes should the process be scaled to all months.

### Official archive spot-check — 2016 release sample (2026-11-13)
The official MoSPI press-release archive contains machine-readable/indexed historical PDFs with the publication date, embargo time, provisional CPI index and inflation values. A November 2016 spot-check was parsed directly from the official PDF:
- October 2016 reference CPI was released on 15 November 2016 and embargoed until 17:30 IST.
- Combined General CPI index: 131.4 provisional.
- Combined General CPI year-over-year inflation: 4.20% provisional.
- September 2016 final combined index: 130.9; final YoY inflation: 4.39%.
- The PDF explicitly states that provisional October and final September figures are released together.
Source: https://mospi.gov.in/sites/default/files/press_release/cpi_pr_15nov16t.pdf
This confirms that a release-event ledger can preserve both the current provisional month and preceding-month final value, with the release date/time taken from the source document.

Other official 2016 spot-checks surfaced:
- January 2016 reference month release dated 12 February 2016, 17:30 embargo: https://www.mospi.gov.in/sites/default/files/press_release/cpi_pr_12feb16f.pdf
- April 2016 reference month release dated 12 May 2016, 17:30 embargo: https://www.mospi.gov.in/sites/default/files/press_release/cpi_pr_12may16th.pdf
- March 2016 reference month release dated 12 April 2016, 17:30 embargo: https://mospi.gov.in/uploads/documents/CPI/Press/PR%20March%202016.pdf
- November 2016 reference month release dated 13 December 2016, 17:30 embargo: https://mospi.gov.in/sites/default/files/press_release/CPI_PR13dec16t_0.pdf

### Revised source acquisition approach
1. Use the official MoSPI press-release archive and catalogue to enumerate the release months and obtain the release-specific PDF/Excel files.
2. Extract from each release the current provisional headline combined General CPI index and YoY inflation, plus the preceding month's final index/inflation where shown.
3. Store the source PDF/workbook URL, file hash, reference month, actual publication date/time, base year, provisional/final status and first eligible NSE session.
4. Independently reconcile a sample of API/catalogue observations against the official release PDFs before scaling extraction.
5. Treat third-party month-by-month historical pages only as discovery/QA aids; official MoSPI release files remain the accepted evidence.

Do not assume the CPI API's latest historical values are the same as the values published at each original release. The API's usefulness for structured current-vintage data is separate from its suitability for point-in-time vintage reconstruction.

### eSankhyiki catalogue file-path discovery and API schema versioning (2026-11-13)
- The catalogue FAQ explicitly says Data Catalogue datasets are downloadable as Excel files according to released statements, while Macro Indicators offers CSV downloads of filtered datasets. This distinction matters: the Data Catalogue may preserve release-specific annexure files; the Macro Indicators API may serve a current time series. Source: https://esankhyiki.mospi.gov.in/datacatalogue/CPI/2025/
- Search indexing exposed an actual official catalogue-hosted Excel URL: https://esankhyiki.mospi.gov.in/datacatalogue/CPI/2026/Annexures_for_Press_Release_in_Excel_November2025_Annex-VII.xlsx . The directory year is 2026 although the workbook is November 2025, so do not assume directory year equals reference month or release month. This is a concrete lead to direct monthly workbook files, but historical 2016–2023 path availability remains unverified.
- The current portal API documentation identifies version 2.0.0 and GET `/api/cpi/getCPIData`, supporting base years 2010/2012/2024, pagination and guest access with per-IP rate limits. Source: https://esankhyiki.mospi.gov.in/macroindicators?product=cpi&tab=api
- The publicly indexed MoSPI MCP repository's Swagger file (version 1.0.11) instead documents `/api/cpi/getCPIIndex` and `/api/cpi/getItemIndex`, with parameters such as `base_year`, `series`, `year`, `month_code`, `state_code`, `sector_code`, `group_code`, `subgroup_code`, `limit`, `page`, and `Format`. Its code routes CPI queries to the older `/api/cpi/getCPIIndex` endpoint. This appears to be an older API contract than the current portal's v2.0.0 page; it is a useful historical reference but must not be treated as the current schema. Sources: https://github.com/nso-india/esankhyiki-mcp/blob/main/swagger/swagger_user_cpi.yaml ; https://github.com/nso-india/esankhyiki-mcp/blob/main/mospi_server.py
- The catalogue currently reports 495 CPI datasets, with each record exposing product, year, frequency, reference period, release date and table number. Example current records include distinct table IDs for group-wise, division-wise, state-wise and combined-general CPI. Source: https://esankhyiki.mospi.gov.in/catalogue-main/catalogue?product=CPI

### Pilot decision
Prioritize direct official catalogue statement workbooks/PDFs for vintage reconstruction. The next test should retrieve one catalogue-hosted annexure workbook (the indexed November 2025 Annex-VII file), inspect its sheet names and headline values, and compare it with the user's already supplied November 2025 workbook. Then attempt to locate a pre-2024 file by the same naming convention. If older catalogue files are unavailable, use the official press-release PDFs and MoSPI's legacy CPI warehouse as separate sources; do not infer availability from the current catalogue's recent records.

### CPI warehouse and cumulative historical annexure route — confirmed (2026-11-13)
- The latest official National Metadata Structure (last posted 13 February 2026) explicitly distinguishes three series: 2024=100 from Jan 2025 onward; 2012=100 through Dec 2025; and 2010=100 from Jan 2011 through Dec 2014. It explicitly says the old 2012-base series through Dec 2025 remains in the CPI warehouse at cpi.mospi.gov.in. This confirms the old and new base-year series must be handled separately. Source: https://mospi.gov.in/sites/default/files/CPI/National_Metadata_Structure_for_CPI.pdf (see sections 2.1 and 3.5).
- The older CPI metadata explains that the warehouse exposes downloadable Excel datasets under tabs including Time Series, All India Item Index, Annual Inflation Rates and All India Item Inflation Rates. Source: https://cpi.mospi.gov.in/PDFile/National_Metadata_Structure_for_CPI.pdf
- Crucially, official MoSPI press releases themselves include cumulative Annexure time series for All India General CPI (2012=100) since Jan 2013 and year-on-year inflation since Jan 2014. Example: October 2025 CPI press release, published 12 Nov 2025 at 4 PM, includes Annexure VI with monthly index values from 2013 through October 2025 and Annexure VII for YoY inflation. October 2025 is explicitly marked provisional. Source: https://cpi.mospi.gov.in/PDFile/Press/PR%20October%202025.pdf
- December 2025 release includes Annexure VI time series since Jan 2013 and is embargoed until 4 PM on 12 Jan 2026. Source: https://cpi.mospi.gov.in/PDFile/Press/PR%20December%202025.pdf
- January 2025 release includes the same cumulative 2012-base General CPI series. Source: https://www.cpi.mospi.gov.in/PDFile/Press/PR%20January%202025.pdf
- May 2025 release explicitly lists Annexure VI (index time series since Jan 2013) and Annexure VII (YoY inflation since Jan 2014), while the main release tables identify current provisional and preceding final values. Source: https://www.cpi.mospi.gov.in/PDFile/Press/PR%20May%202025.pdf

### Implication for vintage reconstruction
The cumulative tables in each release are a major acquisition route: each monthly press-release PDF provides a snapshot of the entire historical index/inflation series as known in that release. They can therefore be parsed into a genuine release-by-release vintage panel, rather than using a single latest-vintage time series. We should extract both index and YoY inflation from each release, retain release date/time and provisional/final markers, and compare successive release snapshots to quantify revisions. This route is more directly aligned with point-in-time modelling than the current API or a single warehouse download.

### Immediate implementation pilot
Use a small set of official PDFs already confirmed by search indexing (e.g. January 2025, May 2025, October 2025, December 2025) to verify the table structure and extraction reliability. Then scale across monthly PDFs from Jan 2016 to Dec 2025. Where a release PDF omits a cumulative annexure or has a layout change, preserve a gap and use the corresponding official Excel annexure or warehouse download as a separately labelled source. The live CPI warehouse page timed out in the current research environment, so no warehouse Excel download has yet been obtained.

### Important correction: cumulative annexures are NOT present in early CPI press releases (2026-11-13)
A direct inspection of official early-release PDFs narrows the cumulative-vintage strategy substantially:
- The January 2016 CPI release (dated 12 Feb 2016, embargo 17:30) has only Annexures I–IV. Its headline tables report January 2016 provisional and December 2015 final figures; `find` confirms no Annexure VI. Source: https://mospi.gov.in/sites/default/files/press_release/cpi_pr_12feb16f.pdf
- The January 2017 CPI release (dated 13 Feb 2017, embargo 17:30) likewise has Annexures I–IV only; it reports January 2017 provisional and December 2016 final figures and has no Annexure VI. Source: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_13feb17m.pdf
- By the October 2025 release (dated 12 Nov 2025, embargo 16:00), Annexures VI and VII explicitly provide cumulative 2012-base combined General index (since Jan 2013) and YoY inflation (since Jan 2014). Source: https://new.mospi.gov.in/uploads/latestReleases/latest_release_1762943528848_3d8d7b84-4ce5-4995-8ccc-3e51617d8356_Press_Release_CPI_Oct_2025.pdf
- The 2016/2017 PDFs therefore disprove the earlier broad wording that monthly press releases across 2016–2025 all contain cumulative time-series annexures. The cumulative annexure route is verified for late 2024/2025 only based on currently inspected source workbooks/PDFs; exact first introduction date needs further verification.

### Revised historical reconstruction design
1. For releases before cumulative annexures were introduced, extract the headline combined General CPI index and YoY inflation for the current provisional reference month and preceding final reference month from each monthly press release. Preserve each row's publication date/time, status, source URL and first eligible NSE session.
2. Treat the provisional-to-final transition as a two-vintage sequence (initial provisional, next month's final) only where the next release confirms the final value. Do not invent older monthly revisions that the release record does not show.
3. For each release from the first confirmed cumulative-annexure month onward, preserve the full historical index and inflation snapshots as separate vintages. Compare snapshots month-over-month to measure later revisions.
4. Use the official CPI warehouse/current time series as a cross-check, not as a replacement for historical release snapshots. Clearly label current-vintage values separately.
5. Establish the exact first release month containing Annexures VI/VII by inspecting the November 2024 workbook/PDF and preceding October 2024 release; the uploaded July–October 2024 workbooks contain only Annexures I–IV, while November 2024 onward workbooks in the current local source set include historical snapshots.

This correction supersedes any earlier statement in this document that implies full cumulative release snapshots are available in every monthly press release from 2016 onward.

### Exact first confirmed cumulative annexure release — November 2024 reference month
- The official November 2024 CPI press release was published 12 Dec 2024 at 4 PM. Its annex list explicitly includes Annex V: All India General CPI index time series since Jan 2013, and Annex VI: YoY inflation time series since Jan 2014. This is the earliest cumulative annexure release confirmed in the currently inspected official release series. Source: https://mospi.gov.in/sites/default/files/press_release/CPI_PR_12dec24.pdf
- The November 2024 release reports November 2024 provisional combined General index 196.5 and YoY inflation 5.48%; October 2024 final combined index 196.8 and YoY inflation 6.21%. It also provides a 13-month chart of headline CPI inflation from Nov 2023 to Nov 2024, but the full cumulative historical tables are in Annex V/VI.
- The annexure numbers changed after the 2024 redesign: November 2024 uses Annex V for index and Annex VI for inflation; later releases such as October 2025 use Annex VI for index and Annex VII for inflation. Extraction must identify table titles/content, never hard-code annexure numbers.
- Combined with inspected Jan 2016 and Jan 2017 releases (only Annex I–IV, no cumulative series), and uploaded July–October 2024 workbooks (only Annex I–IV), the best-supported boundary is: cumulative CPI index/inflation annexures first appear in the November 2024 reference-month release (released 12 Dec 2024). The preceding October 2024 release should still be treated as pre-cumulative unless a contrary primary source is found.
- This means cumulative historical vintage snapshots are available for the release sequence Nov 2024–Dec 2025 in the current dataset. For earlier releases, collect monthly headline provisional/final records from original releases; do not claim full monthly historical snapshots.

### Uploaded MoSPI Excel annexure audit — 2026-11-13

I inspected the 18 uploaded official monthly annexure workbooks directly with the Python openpyxl library in read-only/data-only mode. This is a local source-file audit; the source files themselves have not been committed to the repository.

**Coverage and table availability**

| Release month | Cumulative General CPI index | Cumulative YoY inflation |
|---|---|---|
| Jul–Oct 2024 (4 workbooks) | Absent | Absent |
| Nov–Dec 2024 (2 workbooks) | Present | Present |
| Jan–Dec 2025 (12 workbooks) | Present | Present |

The cumulative index table is titled as the All India General CPI (2012=100) since January 2013; the companion table is All India year-on-year inflation based on General CPI (2012=100) since January 2014. Annexure numbering changes between releases (e.g. Annex V/VI in late 2024 and Annex VI/VII in later 2025 files), so extraction must identify tables by title, not fixed sheet/annexure number.

**Extraction smoke test**

- The November 2024 workbook's cumulative index sheet has a year-by-month layout (2013 onward); the inflation sheet begins in 2014.
- The current-month headline table in Annex-I separately identifies the previous month as Final and the current month as Provisional. Example: the November 2024 workbook labels October 2024 Final and November 2024 Provisional, with the Combined General Index values in the “General Index (All Groups)” row.
- Across overlapping CPI index and YoY observations in the uploaded cumulative sheets, 281 distinct month/series keys were present. Comparing every repeated key across workbook vintages found no differing values at the precision stored in the spreadsheets.
- This is only an extraction/consistency smoke test. It does not prove there were no revisions in unprovided releases, does not validate the original source's calculation, and does not establish a full 2016–2025 vintage history.

**Source-set limitations**

- Uploaded releases cover July 2024 through December 2025, but only 18 monthly workbooks; no 2016–June 2024 workbook set is present.
- July–October 2024 workbooks contain only Annex-I to Annex-IV. November 2024 is the first cumulative historical snapshot in the uploaded set.
- The current local source set does not include every month before July 2024, so monthly provisional/final headline history for 2016–June 2024 still needs separate official releases/workbooks.
- The workbook audit did not yet export a normalized CPI CSV or vintage panel. No model-ready macro dataset has been created.

**Next extraction step**

Build a reproducible parser that detects the CPI index and YoY sheets by their titles, converts the year/month matrices into tidy records, and attaches each workbook's release reference month, actual publication timestamp, source filename, base year, series type, and vintage. Add tests for month coverage, duplicate keys, expected start months, latest published month, and agreement between the Annex-I provisional/final General Index row and the corresponding cumulative series endpoint. Keep release vintage separate from observation month; do not treat the latest snapshot as the value available historically.

### CPI parser pilot — 2026-11-13

A first reusable parser is now in the repository at scripts/parse_mospi_cpi_annexures.py, with openpyxl declared in requirements.txt. It identifies tables by their titles (not annexure numbers), parses the year/month matrix, preserves the workbook release reference month separately from the observation month, and retains source filename/sheet and an explicitly blank release_timestamp field. It excludes observations later than the workbook's release reference month and rejects duplicate vintage/observation/series keys.

**Local pilot result on the 18 uploaded workbooks**
- 3,948 tidy records across 14 cumulative-table vintages (the four Jul–Oct 2024 files correctly contribute no cumulative series).
- General CPI index: 2,078 records; observations span Jan 2013–Nov 2025.
- General CPI YoY inflation: 1,870 records; observations span Jan 2014–Nov 2025.
- 3,948 unique vintage/observation/series keys; no duplicates.
- Every observation month is on or before its release reference month.
- The generated pilot CSV was written to /tmp/mospi_cpi_vintages.csv for testing only; it has not been committed and is not yet part of the Northgate modelling dataset.

The parser deliberately does not invent exact publication timestamps. These must be populated from verified official release metadata before historical availability can be aligned to NSE sessions. The current parser is a first extraction utility, not yet a complete production-quality data pipeline: headline Annex-I provisional/final cross-checks, automated tests, source checksums, and a verified release-time lookup remain to be implemented.

Run from the repository root:
python scripts/parse_mospi_cpi_annexures.py /path/to/Annexures*.xlsx --output data/raw/mospi_cpi_vintages.csv



## Verified 2026-11-13 update

- Inspected user-uploaded market panel: 29,484 rows, ten provisional Indian equities plus ^NSEI; fields include Date, ticker/name, adjusted close, close, dividends, OHLC, stock splits and volume. This is a user-provided yfinance panel, not official exchange archival data.
- Inspected user-uploaded `cpi_33.xlsx`: 31,460 rows, 15 columns; base year 2024 Current series, with records from Jan 2025 through Oct 2026 in the inspected workbook. This is not a complete historical headline CPI series.
- MoSPI e-Sankhyiki CPI API documentation supports base years 2010, 2012 and 2024, Current/Back series, and pagination. MoSPI's 2024 CPI FAQ describes the linked base-2024 All-India Rural/Urban/Combined back series for Jan 2013–Dec 2024, with annual inflation rates from Jan 2014–Dec 2024. Treat linked back-series data as distinct from contemporaneous 2012-base release vintages.
- RBI's DBIE is the official long-series macro download portal; its 2026 handbook says extended historical time series are available there. Align macro data by release availability, not merely observation period.
- GDELT raw archives provide historical news metadata from 2015, but the DOC API has a rolling search horizon and GDELT is not a complete financial article archive. The Zenodo IN-FINews corpus (3,348 India-focused articles, Feb–Aug 2025) is only a small supplemental corpus.
- See `docs/DATASET_INVENTORY.md` for the source-by-source inventory and current gaps.


## 2026-11-13 — User-verified MoSPI CPI API specification (OpenAPI 2.0.0)

The user ran Python requests.get against https://esankhyiki.mospi.gov.in/layout/swagger_user_cpi.yaml; terminal evidence returned HTTP 200 and content type application/octet-stream. This is the CPI API specification, not PLFS. Official e-Sankhyiki also renders this specification on its CPI API tab.

Verified contract from the retrieved OpenAPI document:
- Production host: https://api.mospi.gov.in/.
- Endpoint: GET /api/cpi/getCPIData.
- CPI base years: 2010, 2012, 2024. Bearer token is optional; guest requests are supported and rate-limited per IP.
- For 2010/2012, level (Group or Item) is required; without base_year, the API returns 2010 and 2012 together. 2024 does not use level.
- Filters vary by base year and level. 2010/2012 Group filters include series, year, month_code, state_code, sector_code, group_code, subgroup_code; Item filters include year, month_code, item_code. 2024 filters include series, year, month_code, state_code, sector_code, division_code, group_code, class_code, sub_class_code, item_code and imputation_code.
- Multi-code filters accept comma-separated values. Codes are not validated: an invalid code can return HTTP 200 with No Data Found; retrieve valid codes from GET /api/cpi/getCpiFilterByLevelAndBaseYear?base_year=...&level=....
- Pagination is 1-based (page), limit range 10–100 (default 10); viz_req=true requests the complete filtered result for chart rendering. Responses carry statusCode, msg, data and (where applicable) pagination metadata.
- The published OpenAPI example for base 2024 shows totalRecords=1,445,316 and totalPages=144,532 at the default 10 records/page. This is a documentation example illustrating scale, not a claim that this many rows were downloaded in Northgate.

### Interpretation and safeguards
1. This API is a route to retrieve current API records. The spec does not document historical release-vintage snapshots or as-of queries. Do not treat a current response for an old reference month as the value investors could have known at that historical date.
2. Keep this API path separate from the existing point-in-time CPI archive built from contemporaneous monthly release annexures (base 2012, July 2024–December 2025). The latter preserves release snapshots and availability events; the former can provide a current/expanded CPI panel and metadata.
3. Never call the endpoint unfiltered or set viz_req=true for broad data without a bounded, reviewed filter and an explicit row/page cap. Rate limits are per IP.
4. First retrieve filter-code metadata, then pilot one narrowly bounded query, inspect returned fields and pagination, save the untouched JSON response and retrieval timestamp, and only then consider a larger pull.
5. Preserve base year, series, reference year/month, geography, sector, classification codes, imputation flag, index, inflation, status, request parameters, page, retrieval timestamp and raw response. Do not splice 2012 and 2024 series without an explicit linking methodology.

### Status
Specification successfully retrieved by the user (HTTP 200). No CPI API observation page was downloaded by this work session; no API rows have been merged into market data. The existing Excel-annexure parser and release-vintage pipeline remain the only established point-in-time CPI path in the repository.


### Additional official CPI 2024 methodological finding (MoSPI FAQ)
MoSPI's CPI 2024 FAQ states that the base-2024 back series for All-India Rural, Urban and Combined covers Jan 2013–Dec 2024 and is linked using the 2025 overlap between old (2012) and new (2024) series. The general-level linking factors listed are Rural 0.5222, Urban 0.5320 and Combined 0.5267; the FAQ defines the factor as the ratio of annual-average (geometric-mean) new-series CPI to old-series CPI for the overlap year. This creates a comparable historical index scale; it does not make those linked historical values contemporaneous release vintages. Do not use the back series as point-in-time investor information for 2013–2024. Preserve source series and vintage separately. MoSPI FAQ: https://mospi.gov.in/uploads/documents/documents/1770891066052-Annexure_V.pdf (questions 36–38, pp. 4–5).


## 2026-11-13 — October 2026 CPI release and current source-state recheck

- Verified the official MoSPI October 2026 CPI release. It is a **2024-base (2024=100)** release dated 12 November 2026 and embargoed until **16:00 IST**. Combined General CPI index = **110.05** and year-on-year inflation = **6.09% (provisional)**; rural = 6.63%, urban = 5.41%. Combined CFPI food inflation = 8.94% (provisional). The preceding September 2026 combined CPI inflation is shown as 5.54% (final).
- Point-in-time rule: because the release embargo is 16:00 IST, it must not be used for a same-day 15:30 NSE close forecast. Assign it only from the next eligible NSE session onward. Preserve base year, provisional/final status, release timestamp and source PDF. Do not splice this 2024-base observation into the 2012-base CPI series without an explicit methodology/series indicator.
- Official source: https://www.mospi.gov.in/uploads/latestReleases/latest_release_1794478693814_7c90e80f-9e64-4aa4-b44a-1dc727b0fed9_Press_Release_of_CPI_for_October_2026_.pdf (dated 12 Nov 2026; 16:00 embargo).
- Rechecked the MoSPI 2026–27 advance release calendar: the July–September 2026 quarterly PLFS bulletin was scheduled and published 10 November; October 2026 monthly PLFS bulletin is scheduled for 15 November. As of 13 November, it is not yet due. These are separate products/frequencies; the September 2026 monthly bulletin was released 15 October.
- Rechecked official RBI DBIE Key Rates: the indexed table reports 271 effective-date rows through 7 October 2026 and CSV/JSON controls. No export has been downloaded in this session. NSE's official India VIX page still exposes date-range controls and CSV download; an unfiltered “No Records” display is not proof of an empty archive. No VIX CSV has been downloaded.
- NSE Corporate Filings Summary Documents exposes company/subject/date filters and CSV download; indexed page evidence displays broadcast and exchange-dissemination timestamps. This remains a regulatory-disclosure candidate, not a complete editorial-news dataset; archive depth and machine-readable timestamp/timezone semantics remain to be tested.
- No PLFS, RBI, VIX or corporate-announcement observations were downloaded or merged in this recheck. This entry records source and release verification only.


## 2026-11-13 — MoSPI direct CPI API vs public MCP route discrepancy

A fresh inspection of the official NSO India esankhyiki-mcp source exposed an integration detail that must be resolved before automating CPI retrieval:

- The user's retrieved portal OpenAPI notes in this repository describe direct CPI endpoint GET /api/cpi/getCPIData.
- The current official MCP server source maps CPI Group requests to /api/cpi/getCPIIndex and CPI Item requests to /api/cpi/getItemIndex; PLFS maps to /api/plfs/getData.
- These are not interchangeable endpoint contracts. The direct CPI API pilot already performed by the user should remain recorded as a direct-REST pilot. A future MCP call should follow the server's ordered list_datasets → get_indicators → get_metadata → get_data workflow and let the MCP server select its endpoint.
- The official MCP source documents PLFS frequency codes: 1 annual, 2 quarterly, 3 monthly; monthly indicator codes 1–3 cover April 2025–September 2026. It warns that frequency_code selects the indicator set and that exact valid filters must come from get_metadata. Monthly bulletin catalogue metadata defines the published monthly estimates as CWS; do not infer that definition from an annual-only weekly_status_code parameter.
- Sources: https://github.com/nso-india/esankhyiki-mcp/blob/main/mospi_server.py ; https://github.com/nso-india/esankhyiki-mcp/blob/main/README.md
- Open question: determine whether the portal's getCPIData route is a parallel/legacy/current direct endpoint and whether its output matches the MCP Group/Item routes for identical bounded filters. Compare a small common month set before choosing a production route. Do not silently replace the already documented pilot endpoint or combine outputs until reconciled.

## 2026-11-14 — NSE market-data and disclosure access deep dive

### Official NSE historical market data
A fresh review of NSE's official All Reports / Historical Reports pages confirms more than a generic VIX download link:
- NSE All Reports has date-range controls for **Historical Index Data** and **Historical Data – India VIX**. The rendered VIX table schema is Date, Open, High, Low, Close, Previous Close, Change and % Change. The rendered NIFTY 50 example includes Date, OHLC, Shares Traded and Turnover. These are UI examples; no CSV was downloaded in this review.
- NSE's historical reports directory separately lists Historical Index Data, Historical Data – India VIX, Archives of Daily/Monthly Reports (Indices), P/E/P/B/Dividend Yield and Total Returns Index Values.
- NSE's daily equity reports page explicitly says the old CM Bhavcopy CSV/common CSV formats were discontinued from 8 July 2024 and directs users to **CM-UDiFF Common Bhavcopy Final (zip)**. The same page lists daily volatility, security-wise delivery positions, market activity and other end-of-day reports. This is a useful official cross-check source for the Yahoo-derived price/volume panel, subject to obtaining and parsing the files.
- NSE Indices' official Historical Data page exposes an index-type/sub-index/index selector and date range, with CSV output for historical index OHLC, valuation ratios and total-return index values. Its selector lists broad-market and many sectoral indices (including NIFTY AUTO, BANK, FMCG, IT, PHARMA, METAL, etc.). This is the strongest official candidate for consistent sector-index context and TRI benchmarks. The site itself says fixed-income indices are generally total-return indices, except Nifty 10 yr Benchmark G-Sec (Clean Price).
- NSE defines India VIX as an options-derived, annualised measure of expected NIFTY volatility over the next 30 calendar days. It is a forward-looking implied-volatility measure, not realised volatility.

### NSE corporate announcements — important distinction
- Official NSE Corporate Filings Summary Documents page exposes Company/Symbol, Subject, From/To date filters, CSV download, and columns SYMBOL, COMPANY NAME, Subject, DETAILS, ATTACHMENT, XBRL, TYPE OF SUBMISSION and BROADCAST DATE/TIME. The page's sample explicitly shows a broadcast at 19-Sep-2026 14:47:29, exchange dissemination at 14:47:34 and 5-second time taken.
- A third-party technical investigation published 10-Nov-2026 reports that NSE's public filing pages call an undocumented JSON route, `GET https://www.nseindia.com/api/corporate-announcements`, with index/date filters; it also documents an official RSS announcements feed at `https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml`. The article reports a 10-Nov sample of 6,029 equity filings for 3–9 Nov and 14,045 for October, with fields including seq_id, symbol, ISIN, subject, attachment URL, broadcast and dissemination times. These counts and the undocumented route are third-party-observed, not an official NSE API contract; independently verify a small sample and inspect NSE website terms before relying on it. Do not treat it as a supported free developer API or assume permanent endpoint stability.
- The RSS feed is an official NSE-published channel according to that investigation, but its observed announcement feed contained only the current day and lacked symbol/ISIN/category fields. It may be useful for current-day discovery, not historical backtesting, unless its retention is independently shown to be longer.
- Store announcement broadcast time and dissemination time separately; parse timestamps in Asia/Kolkata only after confirming the source's timezone convention. After-close disclosures must become eligible on the next NSE session. Preserve source record ID and attachment URL for deduplication and audit.

### RBI DBIE Key Rates status
- Official DBIE page remains the source of record for `financial_sector.r531_key_rates`; indexed page reports 271 effective-date observations from 06-Jul-1935 through 07-Oct-2026 and CSV/JSON download controls. Fields include Effective Date, LAF fixed-rate range, Bank Rate, Repo, Reverse Repo, SDF, MSF and CRR.
- No export file or public API contract has been retrieved. The next acquisition step remains a manual bounded CSV/JSON export. Preserve the event/effective date and forward-fill only from that date; never backfill or interpolate rate changes.

### PLFS release calendar recheck (14-Nov-2026)
- MoSPI's 2026–27 advance release calendar schedules the October 2026 monthly PLFS bulletin for **15-Nov-2026**. As of this 14-Nov research pass, it is not yet due. The latest confirmed monthly bulletin remains September 2026 (released 15-Oct-2026); the July–September quarterly bulletin was published 10-Nov-2026.
- The catalogue identifies monthly September 2026 LFPR, WPR and UR as All-India CWS estimates, reference period Sep 2026, with release date 15-Oct-2026. No PLFS API observations have been downloaded.

### Acquisition state and caveats
No RBI export, India VIX CSV, sector-index CSV, official NSE bhavcopy archive, PLFS API response or announcement corpus was downloaded in this research pass. This is a source-contract and acquisition-route review, not an acquisition milestone. Official NSE UI controls and schemas are verified from rendered pages; undocumented API behavior and third-party sample counts remain provisional until independently tested.

## 2026-11-14 — Financial-news feasibility and market-data usage terms

### NSE/BSE data-use constraint (material)
- NSE's current website Terms of Use prohibit systematic or automated data collection (including scraping/data mining/extraction/harvesting) on or in relation to its website. The terms also restrict copying/storing/disseminating content and explicitly mention virtual trading/simulation activities. NSE's copyright policy separately permits viewing/printing/downloading for personal, non-commercial or educational purposes with accurate reproduction and acknowledgement, but this must be read together with the Terms of Use and any product-specific rules.
- Therefore, do **not** build an automated scraper against NSE's undocumented JSON endpoints or RSS pages as a default Northgate ingestion route. A visible CSV download control does not automatically grant bulk automated collection, model-training, storage or redistribution rights. For automated or persistent use, obtain written clarification/permission or use an appropriately licensed provider. Keep any manually downloaded research files local/private, preserve attribution and terms, and confirm whether model backtesting/simulation is permitted before relying on exchange-origin data.
- NSE Data Sharing & Usage Policy confirms market-data access, handling, dissemination and end-user restrictions are governed by relevant agreements; redistribution is not automatically granted.
- BSE's information-products tariff sheet identifies EOD, historical and corporate data as products offered to researchers/academicians, which indicates that free website visibility should not be equated with blanket reuse rights. A BSE RSS URL appears in third-party feed directories, but the feed itself and terms were not independently verified in this pass.
- SEBI circular SEBI/HO/DEPA-II/DEPA-II_SRG/P/CIR/2024/178 dated 20-Dec-2024 concerns sharing data for research/analysis; review the full circular and exchange-specific implementation before concluding a particular data use is permitted.

### Third-party EOD data candidate: TejHQ / tej-bazaar
- A new public candidate was found: TejHQ's tej-bazaar pipeline and tejhq/indian-markets Hugging Face dataset. The project claims NSE EOD coverage from 2010 and BSE from 2024-07-08, with raw OHLCV, corporate actions, adjusted prices, symbol history, liquidity-universe and delivery trees; the dataset card currently previews about 7.36 million NSE rows and the full dataset reports about 34.35 million rows.
- GitHub repository code is MIT-licensed, but its own data terms explicitly say MIT does **not** cover exchange-derived data and TejHQ holds no NSE/BSE licence or written clarification. TejHQ allows personal research/backtesting/model training and local storage under its own terms, but says raw data cannot be redistributed; the exchanges' terms apply independently. This does not resolve the NSE restriction above. Treat it as a promising validation/cross-check candidate, not a legally cleared production source.
- Data caveats from its own dataset card: daily data is usually available next morning IST; anomalies such as close outside low/high and zero-volume rows may be dropped; corporate-action classifier can leave type=other; adjusted prices and symbol-history joins need scrutiny. Do not replace the existing 10-stock Yahoo panel until independently compare overlapping sessions, corporate actions, price conventions, gaps and delisted-symbol handling.
- The public dataset is large (about 1.25 GB). Avoid pulling the whole corpus until a narrow 10–15 ticker sample and legal suitability are checked.

### Financial news and sentiment sources
- GDELT DOC 2.0 is a rolling full-text *search* interface, not a durable 8–10 year article archive: official GDELT documentation says the DOC API's default search window is three months and precise STARTDATETIME/ENDDATETIME searches must remain inside that window. Older full-text article retrieval is not guaranteed. GDELT GKG/Event archives provide long historical metadata, themes, entities, URLs and tone/context signals, but not a complete, reusable full article-text corpus. BigQuery public datasets have a 1 TB/month free query allowance, subject to query pricing and project setup.
- The Zenodo Indian Stock Market News Dataset / IN-FINews is a concrete India-focused supplemental corpus: 3,348 English articles from early Feb to late Aug 2025, 13.1 MB CSV / 13.6 MB JSON. This is too short and small for the PRD's 8–10-year daily news requirement; inspect its record-level fields and licence before use. It can support a small sentiment-model smoke test or domain vocabulary analysis, not a long historical backtest.
- Economic Times / Times Internet RSS terms say feeds are free for personal, non-commercial use but prohibit storing copies (except personal use), redistribution, aggregation/resale and commercial use. Do not assume RSS article text may be retained as a training corpus. For each publisher, verify licence/retention rights separately.
- The current feasible free path is therefore likely a **two-stream design**: (1) timestamped official exchange disclosures as structured events, subject to rights/terms and a durable archive; (2) GDELT metadata/tone or a small licensed/open article corpus for broader media context. These are not interchangeable: filings are issuer/regulatory disclosures, not editorial reporting. Compare sentiment features against the price/volume baseline on identical dates; do not assume added value.

### Evidence and source links
- NSE Terms of Use: https://www.nseindia.com/static/nse-terms-of-use
- NSE Copyright Policy: https://www.nseindia.com/static/nse-copyright
- NSE Data Sharing & Usage Policy: https://www.nseindia.com/static/market-data/nse-data-policy
- SEBI research-data circular: https://www.bseindia.com/downloads1/SEBI_circular_Policy_Sharing_Data.pdf
- TejHQ data terms: https://tejhq.dev/data-terms
- TejHQ dataset: https://huggingface.co/datasets/tejhq/indian-markets
- GDELT DOC API documentation: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
- GDELT data portal: https://www.gdeltproject.org/data.html
- IN-FINews: https://zenodo.org/records/16991843
- Economic Times RSS terms: https://economictimes.indiatimes.com/rss.cms

No additional article corpus, exchange data file or third-party Parquet was downloaded in this review. Usage rights and actual record-level quality remain open.

### SEBI research-data circular — eligibility nuance (full PDF reviewed 14-Nov-2026)
SEBI Circular SEBI/HO/DEPA-II/DEPA-II_SRG/P/CIR/2024/178 (20-Dec-2024) is more specific than a general “free research data” rule:
- The circular's voluminous-data free request mechanism (reasonable amount up to 2 GB per researcher per year, no extra computation) is for **research/research publications undertaken by accredited academic institutions**.
- The circular divides MII data into a public first basket (aggregate/analysed data plus regulator-mandated disclosures and data already public) and a non-public second basket (identifiable or sensitive/confidential information).
- Its illustrative first-basket examples include publicly available bhavcopy, index snapshots, trading statistics, category-wise turnover/open interest, historical trading statistics, historical daily OHLC/volume/turnover/open interest, and historical spot/futures prices beyond 30 days. It directs MIIs to publish a data-seeking request form explaining the research hypothesis.
- This creates a legitimate route worth investigating if Northgate can be submitted through an accredited academic institution. It does **not** itself prove that any specific raw dataset is available to this user, waive exchange-specific conditions, or override NSE website terms. We need the exchange's published data-basket list and request form, and confirmation of eligibility/conditions.
- Source: https://www.bseindia.com/downloads1/SEBI_circular_Policy_Sharing_Data.pdf (paras 3–8 and Annexure I, pp. 1–4).

### NSE's implemented research-data route found (official; material breakthrough)
A current NSE “Data for Research” page and its linked 28-Jul-2025 dataset classification PDF were located:
- NSE explicitly says its Economic Policy & Research team facilitates market-data access for **approved academic and policy research projects** and that data supplied under this route is strictly for academic and non-commercial use.
- The page provides a Data Seeking Request Form and instructs applicants to send it to **nseri@nse.co.in**.
- The official NSE dataset list identifies first-basket publicly available data including daily historical security OHLC/turnover, bhavcopy and daily/monthly reports, historical index data, FII/FPI and DII activity, and listed-company financial results, shareholding, corporate announcements and corporate actions.
- The list separately identifies a **voluminous first-basket** (above 2 GB, chargeable) including historical end-of-day bhavcopy across CM/WDM/F&O, corporate data (fundamentals, announcements, shareholding, voting results, financial result calendar, governance, corporate actions), historical security/contract masters and historical instrument-wise turnover. Read together with SEBI's circular, the up-to-2-GB/researcher/year no-extra-computation route may be free; above that or value-added processing may be charged. Confirm the applicable quantity, time window, and price directly with NSE.
- The NSE request form asks for name, institution, country, contact details, project title, objective and market relevance, data type, data justification, period, signature and date. The application requires a specific research hypothesis/justification, not a generic data request.
- This route is materially better than scraping public pages: submit the request through an eligible institution and obtain the data/terms directly. It does not automatically approve the project or guarantee all requested fields/periods.

Official links:
- NSE Data for Research: https://www.nseindia.com/static/research/initiatives-data-for-research
- NSE data list (28-Jul-2025): https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Data%20list%20under%20NSE%20Data%20Sharing%20Policy%20for%20Research%20and%20Analysis_20250728.pdf
- NSE Data Seeking Request Form: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Data%20Seeking%20Request%20Form-20250319.pdf
- Contact specified by NSE: nseri@nse.co.in

**Practical implication for Northgate:** a research request could potentially cover historical EOD price/volume, corporate disclosures and other official data, avoiding the need to automate NSE website collection. The user's institution/supervisor and the project hypothesis need to be confirmed before the form can be completed. Do not send the form or claim eligibility/approval without the user's review.

### Additional official daily market-context candidate: FII/FPI and DII flows
- NSE's FII/FPI & DII page exposes two CSV-download tables: NSE-only Capital Market segment and combined NSE+BSE+MSEI Capital Market segment. Fields are Category, Date, Buy Value, Sell Value and Net Value (₹ crore). The official page explicitly warns that FII/FPI values are provisional and can change after custodial confirmation/modifications; it directs users to NSDL/CDSL for final FPI data.
- This could be a useful daily market-wide context feature, but is not a company-specific flow series. Preserve both the NSE-only and combined versions as distinct datasets; do not merge or overwrite one with the other.
- Because the page describes activity for “today” but does not expose a reliable publication timestamp in the reviewed rendering, treat the observation as unavailable to the same-day close prediction until its actual dissemination time is measured. Safest baseline alignment is next eligible trading session; preserve retrieval timestamp and any provisional/final status.
- The official NSE data-for-research list includes FII/FPI and DII trading activity, so include it in a research data request if useful.
- Source: https://www.nseindia.com/reports/fii-dii

## 2026-11-14 — Additional public Indian-market dataset audit

### Candidate A: aswinv90/indian-market-historical-data
A second broad public dataset was discovered and its GitHub repository metadata, licence, README and verification script were inspected directly.
- Repository was created 18-Sep-2026 and last pushed 12-Nov-2026. It is a large repository (GitHub reports size 3,016,379 KB); its README claims NSE 2,577 symbols and BSE 4,399 symbols from 1991 to present, plus NIFTY/SENSEX, sector indices, India VIX, corporate actions, FII/DII cash/derivatives, macro series (CPI, RBI rates, 10-year yield, FX), commodities and mutual funds.
- The repository contains an explicit **Non-Commercial Research and Personal Use License**. It permits personal, non-commercial and educational research, but prohibits commercial use, redistribution and paid/proprietary automated trading systems without written permission. It is not an OSI/open-data licence; GitHub reports license SPDX as NOASSERTION. Data source rights are not independently established by the repository licence.
- README-reported equity history, indices, corporate actions and macro data are unusually broad, but the repository is very new (created Sep 2026) and its counts/coverage are publisher claims, not independently validated. No data files were downloaded or parsed in this research pass.
- Its own `scripts/verify_data.py` checks file existence, emptiness, staleness, date ranges and failed tickers, but that is not a statistical QA audit: it does not establish correct adjustment factors, point-in-time availability, duplicate handling, price continuity, survivorship correctness, corporate-action correctness or source reconciliation. It reads Parquet files locally; it was not executed here.
- Promising for a narrow sample cross-check, but not yet an approved replacement for the project's existing labelled panel. A validation must compare several representative tickers and the benchmark against independent sources over identical dates; inspect splits/dividends, missing sessions, symbol/ISIN changes, adjusted vs raw close, and exact licence/source provenance.
- Links: https://github.com/aswinv90/indian-market-historical-data ; https://github.com/aswinv90/indian-market-historical-data/blob/main/LICENSE ; https://github.com/aswinv90/indian-market-historical-data/blob/main/scripts/verify_data.py

### Candidate B: tejhq/indian-markets
- Hugging Face dataset card currently previews 7.36M NSE rows, partitioned Parquet, with raw OHLCV and separate trees for corporate actions, adjusted prices, symbol history, derived metrics, liquidity universe and delivery. Publisher claims NSE coverage from 2010-01-04 and BSE from 2024-07-08. Its GitHub pipeline reports daily updates and end-of-day availability.
- This source has more explicit provenance from official Bhavcopy ingestion and a more focused market-data pipeline than the broad multi-domain repository above, but the exchange-derived data is not covered by the code's MIT licence. Its own terms allow personal research/backtesting/model training and local storage, prohibit redistribution and state that exchange terms still apply.
- Neither source is yet validated against the Northgate panel. Keep both as independent candidate sources; do not blend them together or replace the current dataset on claims alone.

### Candidate-source triage
1. Keep existing Northgate 29,473-row labelled panel as the current baseline source until a controlled comparison is complete.
2. Sample aswinv90 and TejHQ for the exact 8–15 project symbols and benchmark only after checking licences and data terms.
3. For every source, preserve raw vendor file, retrieval timestamp, original columns, source version/commit, licence text and checksum; create a separate canonical panel after QA.
4. Compare date coverage, duplicates, OHLC invariants, zero-volume handling, corporate-action discontinuities, adjusted-price factors, symbol changes, delisted securities and cross-source price differences.
5. Do not use back-adjusted prices containing future corporate-action factors as historical point-in-time inputs without explicitly checking the effect on features/labels. For return targets, use a consistent corporate-action-adjusted target definition and avoid leakage from adjustments not known at prediction time.

No candidate Parquet data was downloaded, and no independent quality score is claimed.

## 2026-11-14 — PLFS quarterly bulletin values extracted from official PDF

The official MoSPI PLFS Quarterly Bulletin QB-31 (July–September 2026), dated 10-Nov-2026, was opened and its all-India tables were inspected. This is actual published data, not merely API metadata.

### Headline CWS values (age 15 years and above)
| Indicator | Rural | Urban | Rural + urban |
|---|---:|---:|---:|
| LFPR | 58.1% | 50.4% | 55.5% |
| WPR | 55.6% | 46.9% | 52.7% |
| Unemployment rate | 4.3% | 6.8% | 5.1% |

The bulletin also reports all-India UR for age 15–29 at 15.3%. These values are CWS and should not be confused with the annual Usual Status (ps+ss) estimates.

### Historical quarterly context in the same bulletin
For persons age 15+, all-India rural+urban UR by quarter:
- Jul–Sep 2025: 5.2%
- Oct–Dec 2025: 4.8%
- Jan–Mar 2026: 5.0%
- Apr–Jun 2026: 5.4%
- Jul–Sep 2026: 5.1%

For the same quarters, all-India LFPR was 55.1%, 55.8%, 55.5%, 54.6%, 55.5%; WPR was 52.2%, 53.1%, 52.8%, 51.7%, 52.7%.

### Statistical reliability / methodology
- The July–September 2026 bulletin's sample-size table reports 11,229 FSUs, 1,33,570 households and 5,55,593 persons for rural+urban estimates. RSE of all-India UR (15+) is 1.72%; corresponding LFPR and WPR RSEs are 0.27% and 0.29%.
- The revamped design from Jan 2025 supports monthly all-India rural/urban CWS indicators and quarterly rural+urban coverage. Pre-Jan-2025 quarterly bulletins covered urban areas only; do not splice the pre-2025 urban-only quarterly series with the post-2025 national rural+urban series without explicit geography flags.
- Monthly September 2026 catalogue records are released 15-Oct-2026, separately for LFPR/WPR/UR. Quarterly July–September bulletin publication date is 10-Nov-2026. Preserve these distinct publication products.
- October 2026 monthly bulletin is scheduled for 15-Nov-2026 in the latest 2026–27 advance release calendar. It is not yet available in this 14-Nov review; verify actual publication rather than assuming the schedule guarantees release.

Sources:
- Official MoSPI PLFS QB-31 PDF: https://www.mospi.gov.in/uploads/publications_reports/publications_reports1794297172776_05eae330-7f2d-45ec-84c5-07031201ecf1_PLFS_QB_July-Sept_2026_m.pdf
- Official e-Sankhyiki PLFS catalogue: https://esankhyiki.mospi.gov.in/catalogue-main/catalogue?page=1&product=PLFS
- Official 2026–27 advance release calendar updated through October: https://www.mospi.gov.in/uploads/documents/releaseCalender/1793948871564-ARC%202026-27%20updated%20till%20October%202026.pdf

This is a manual extraction of a published bulletin. No raw MCP API response has yet been acquired; the quarterly values must not be described as monthly observations.

## 2026-11-14 — FRED/ALFRED point-in-time macro and market-breadth research

### FRED vs ALFRED: a practical leakage-control distinction
- FRED's current observation view generally returns the latest known/revised value. The official FRED API documents `realtime_start`, `realtime_end` and `vintage_dates` so a user can request the information known during a historical real-time period. ALFRED preserves the history of when series values were released or revised.
- The FRED API's `series/vintagedates` endpoint lists dates when values changed or new values were released; `series/observations` can request observations for one or more vintage dates. This is exactly the mechanism needed to avoid using today's revised macro values in historical backtests.
- FRED API requires a registered API key (free registration); the existing Northgate FRED graph-CSV script retrieves latest observations, not ALFRED vintages. The script's current output must remain labelled latest-vintage / not point-in-time until it is extended to store vintage dates or real-time periods.
- For each macro series, store observation date, value, realtime_start, realtime_end or vintage_date, source release date/time, retrieval timestamp, units, seasonal adjustment and series ID. Join to Indian trading sessions only after the data's actual release timestamp in IST. If the exact release timestamp is unavailable, apply conservative next-session availability.
- Official docs: https://fred.stlouisfed.org/docs/api/fred/realtime_period.html ; https://fred.stlouisfed.org/docs/api/fred/series_vintagedates.html ; https://fred.stlouisfed.org/docs/api/fred/series_observations.html ; https://fred.stlouisfed.org/docs/api/fred/

### CBOE VIX and India VIX are complementary, not interchangeable
- FRED series VIXCLS is daily CBOE VIX close. FRED's series notes describe it as the market's expected near-term volatility implied by S&P 500 option prices; the source is CBOE and the series carries CBOE copyright/citation conditions.
- India VIX from NSE is the local NIFTY options-implied 30-calendar-day volatility measure. For Indian equities, India VIX is the directly local volatility regime feature; CBOE VIX may add global risk-appetite context.
- CBOE's close occurs after the Indian cash session. For a next-Indian-session forecast, the latest completed US close before the Indian session can be available before the Indian market opens, but exact US holiday/timezone/DST alignment must be handled. Never align same-calendar-date US VIX close to an Indian close without checking timestamps.
- Keep both series separate and test incremental out-of-sample value rather than assuming one substitutes for the other.
- Sources: https://fred.stlouisfed.org/series/VIXCLS ; https://www.nseindia.com/all-reports

### Market breadth: an additional low-cost context feature
- NSE's historical reports archive explicitly lists daily/monthly Advances/Declines as well as historical index, VIX, price-volume, delivery and total-return-index reports. SEBI's equity-cash-market data directory independently lists NSE and BSE Daily and Monthly Advancing and Declining Stocks.
- A third-party Indian-market breadth study publishes a daily breadth.csv since October 2015 under CC BY 4.0 and describes it as derived from NSE daily price/index files. This is a potential comparison dataset, but its raw constituent prices remain exchange-origin and subject to exchange terms; its calculations and exact methodology should be reviewed before reuse.
- Preferred Northgate approach: calculate breadth internally from a documented, point-in-time universe (e.g., advances/declines, % above 20/50/200-day moving averages, equal-weight vs cap-weight return spread) after verifying survivorship-safe membership. Never compute historical breadth from today's surviving constituents only.
- Candidate source: https://markets.ashwinraghavan.com/research.html ; NSE archive: https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives ; SEBI data directory: https://www.sebi.gov.in/curation/equity_cash_market.html

### Implication for Northgate's macro feature table
The PRD lists DGS3MO, DGS10, CPIAUCSL, UNRATE and VIX as examples. For an India-first model, keep PRD-specified US series where required but separately evaluate Indian equivalents: RBI policy repo/short-term money-market rate, India 10Y government yield, MoSPI CPI, PLFS unemployment, India VIX, and USD/INR. Do not silently replace US features with India equivalents; document both and compare ablations. Low-frequency series must be released-time aligned and should not be interpolated into fictional daily observations.

## 2026-11-14 — Financial-news corpus search expanded

### GDELT GKG 2.1: strongest open historical metadata candidate
- GDELT's official data portal offers raw Event and Global Knowledge Graph (GKG) files. The GKG 2.1 codebook describes document-level rows with a globally unique record ID whose first portion encodes the 15-minute processing batch timestamp, a separate document publication timestamp (V2.1DATE), source URL, extracted people/organizations/locations/themes, and GCAM emotional/theme scores. GKG 2.1 has one row per document rather than grouping articles with identical extracted metadata.
- This is materially more useful than DOC API search for historical features: GKG 2.1 has a long-running downloadable archive (since Feb 2015), can support company/entity-specific article counts and broad tone/theme aggregates without storing full article text, and preserves a processing/publication time distinction. However, article coverage is global and noisy; company alias resolution, source relevance, duplicates, language/translation, and exact article timestamps must be tested. Publication time may be missing/zero for some special collections.
- Scale warning: GDELT says the 2015 GKG alone requires more than 2.5 TB. A full local mirror is inappropriate for Northgate. Better route: use bounded GDELT BigQuery queries (public dataset; check the current 1 TB/month free query allowance and cloud billing safeguards), or filter daily files to Indian financial/business domains and relevant company aliases before retaining compact event rows. Query-cost and data-retention controls are essential.
- GDELT DOC API remains a rolling full-text search tool (three-month search horizon), not a substitute for the historical GKG archive.
- Sources: https://www.gdeltproject.org/data.html ; https://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf ; https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/

### India-focused news datasets: candidates and limits
- **IN-FINews (Zenodo)**: 3,348 English Indian e-news articles, early Feb–late Aug 2025, across auto, banking, healthcare, IT and other sectors. Suitable for a sentiment-model smoke test/domain vocabulary review; far too short for 8–10 years of historical features. Licence/individual article provenance should be checked before training.
- **Financial News Headlines (Mendeley, CC BY 4.0)**: 18k labelled headlines, published Aug 2024, extracted from Financial Express market pages with positive/negative/neutral labels. It is a labelled sentiment corpus, not a demonstrated 8–10-year timestamped company-news feed. Reuse the labels/headlines only under the dataset's stated CC BY 4.0 terms and independently consider the underlying publisher's rights.
- **Indian_Financial_News (Hugging Face)**: publisher card describes 26,000 Indian-market article rows with URL, scraped content, T5-generated summary and GPT-labelled sentiment, last updated Jan 2024. The card does not establish reliable publication timestamps, historical completeness, company ticker mapping or the underlying publisher's permission. Candidate for qualitative NLP experimentation only until those are verified.
- **FLAME multilingual financial sentiment v2**: publisher card claims 145,637 labelled headlines across 10 languages including Hindi, 2024–2026, with local-investor-perspective labels. This is a sentiment classifier training/benchmark corpus, not an event feed with a long historical article archive. Useful for comparing sentiment models, but label provenance, dataset licence and time split must be checked before use.
- **Webz.io weekly financial news datasets**: global English financial article datasets with publication metadata and sentiment; provider describes free research/journalistic use and an API Lite tier. Terms and retention rights need inspection; weekly sample datasets do not by themselves establish 8–10 years of historical coverage.
- **FNSPID / multi-source finance news**: a large US-oriented corpus includes ticker-linked news from 1999–2023 and multiple other news collections, but it is not an India-specific coverage source. Could support general model pretraining/benchmarking only, not Indian company event backtests.
- **Reuters Corpus (RCV1/RCV2)**: extensive timestamped historical full-text archives (1996–97 and 2008–09) exist through institutional licensed access; not free public data and not aligned to current Indian listed companies.

### Recommended news architecture for a realistic MVP
1. Use GDELT GKG 2.1 as a **metadata/event-volume/tone** source for historical broad and company-specific context, after a small query proves Indian issuer coverage and ticker-alias quality.
2. Use IN-FINews, FinancialPhraseBank-style open corpora, and/or FLAME only to benchmark/train sentiment classifiers; do not mistake a labelled training corpus for a historical market-news feed.
3. Keep official company announcements as a distinct regulatory-disclosure stream. Do not conflate issuer filings with independent editorial news.
4. Store source URL, original publication timestamp, GDELT processing timestamp, publisher/domain, entity/ticker mapping confidence, language, duplicate cluster, tone/sentiment model version, retrieval timestamp and source licence. If only a date is known, do not fabricate intraday order; map to next eligible session conservatively.
5. Evaluate the news feature ablation on exactly the same dates and baseline: price/volume only vs price/volume + broad news vs price/volume + company news. Use only headlines available before the prediction cutoff; after-close news rolls to the next session. Sentiment may reduce performance; report that honestly.

Links:
- GDELT portal and archive: https://www.gdeltproject.org/data.html
- GDELT GKG 2.1 codebook: https://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf
- IN-FINews: https://zenodo.org/records/16991843
- Mendeley Financial News Headlines: https://data.mendeley.com/datasets/fk37gb6dmp/1
- Indian_Financial_News: https://huggingface.co/datasets/pranali96/Indian_Financial_News
- FLAME: https://huggingface.co/datasets/Kenpache/multilingual-financial-sentiment-v2
- Webz.io weekly financial news: https://github.com/Webhose/financial-news-dataset
- FNSPID: https://huggingface.co/datasets/Zihan1004/FNSPID
- Reuters Corpus: https://www.library.hbs.edu/databases-cases-and-more/datasets/reuters-corpus

No news corpus or GDELT query output has been downloaded or benchmarked in this pass.

## 2026-11-14 — Corporate actions, trading calendar and point-in-time index membership

### NSE Corporate Actions page
- NSE's official Corporate Actions page exposes company/symbol, purpose keyword, meeting type, date-range presets (1D/1W/1M/3M/6M/1Y/custom) and CSV download. Rendered columns include SYMBOL, COMPANY NAME, SERIES, PURPOSE, FACE VALUE, EX-DATE, RECORD DATE, BOOK CLOSURE START DATE and BOOK CLOSURE END DATE. This is a direct structured source for corporate-action terms and dates.
- A separate NSE investor-relations Corporate Actions archive lists historical company-level action announcements with Announcement Date, Record Date and attachment links, with visible examples back to 2012. It is potentially useful for action terms and event-date research, but its archive coverage/CSV export and announcement-time precision still need validation.
- Important distinction: ex-date/record-date data is not the same as the timestamp at which an investor first knew about the action. For point-in-time features, retain the original announcement/broadcast timestamp from the filing; use ex-date for price adjustment and corporate-action accounting, never as a substitute for announcement availability.
- Sources: https://www.nseindia.com/companies-listing/corporate-filings-actions ; https://www.nseindia.com/static/investor-relations/corporate-actions

### NSE trading calendar and special sessions
- NSE's official Market Timings & Holidays page exposes year/product selectors and the current 2026 equity holiday table. The 2026 schedule includes 16 regular listed holidays and separately notes Muhurat Trading on Sunday 08-Nov-2026. This confirms that a simple weekday calendar is insufficient.
- Build the trading-session calendar from actual observed index/equity trading dates, then reconcile it against official holiday notices and special-session circulars. Keep regular sessions, Muhurat/special sessions, partial sessions, and unscheduled closures separately flagged. Do not infer that all weekends/holidays are no-session days or treat a Muhurat Sunday as a normal full session.
- Source: https://www.nseindia.com/resources/exchange-communication-holidays

### Point-in-time index membership: two independent community reconstructions
- **BKKB20/nse-index-history** claims 28 NSE index constituent histories from 2004–2026 reconstructed from about 100 NSE reconstitution circulars (PDF/HTM). Its README discloses 3 unprocessed scanned 2018–2019 circulars and weaker pre-2010 ticker mapping. GitHub repository metadata shows no declared licence; do not assume reuse permission. This is a candidate to inspect/reconcile, not a trusted source of record.
- **aditya-jha/nse-historical-membership** claims PIT membership for NIFTY 50, NIFTY Next 50, NIFTY 100, NIFTY 500, Midcap 150 and Smallcap 250 reliably from Apr-2018 onward, with best-effort earlier coverage and explicit warnings for Microcap 250 pre-2021-10. It is reconstructed by walking backward through NSE replacement press releases. Validate index cardinality, constituent change dates and ticker aliases against original NSE circulars; no declared licence has been established in this review.
- This matters even if the model only forecasts 8–15 current large caps: benchmark/sector breadth, universe selection and portfolio backtests can otherwise inherit survivorship bias. Keep point-in-time index membership separate from the chosen current prediction universe.
- Sources: https://github.com/BKKB20/nse-index-history ; https://github.com/aditya-jha/nse-historical-membership

### NSEDATA4ME — another independent survivorship-aware EOD candidate
- Public repository `ancap97/NSEDATA4ME` claims NSE daily EOD history from 03-Jan-2005, 4,583 securities including 1,037 delisted/inactive, 232 NSE indices from Feb-2012, and 5,407 days of market breadth. It says the first local snapshot is about 430 MB, with raw NSE reports, corporate actions, symbol/ISIN history, adjustment factors and delivery data.
- Its README documents a coherent raw-to-derived pipeline: legacy bhavcopy through 05-Jul-2024, UDiFF from 08-Jul-2024, MTO/full bhavcopy delivery reports, index reports and corporate-action PR zip files. It uses ISIN-aware symbol history and includes delisted securities, which is valuable for backtesting.
- GitHub lists the code repository under GPL-3.0, but this does not itself license NSE-origin data or grant exchange redistribution/automated-collection rights. The pipeline is described as downloading NSE reports with retries and rate delays; do not assume this makes the method permitted under NSE terms. No dataset snapshot downloaded or executed.
- This may be the strongest open pipeline candidate for independently rebuilding/spot-checking Northgate's price panel and market breadth, but must be treated as a research candidate until source permissions, adjustment logic and data QA are checked.
- Links: https://github.com/ancap97/NSEDATA4ME ; https://github.com/ancap97/NSEDATA4ME/blob/main/README.md

No calendar, corporate-action CSV, historical membership file or EOD database was downloaded in this review.

## 2026-11-14 — Official RBI daily FX source confirmed

- RBI DBIE has an official table, **Daily interbank forex rates (USD vis-a-vis INR)**, with daily frequency and 6,319 rows from 08-Aug-2000 through 30-Jun-2026. It exposes Download CSV and JSON. Fields include Date, Interbank Open/High/Low/Close and RBI Reference Rate. This is a stronger official long-history FX source than the previously identified third-party FRED/OECD monthly proxies.
- RBI's separate Reference Rate Archive provides date-range selection and Excel download for USD, GBP, EUR, JPY, AED, IDR and RUB. RBI states it stopped publishing its own major-currency reference rates from 10-Jul-2018 when FBIL took over computation/publication; use the DBIE series or FBIL continuation and do not assume one uninterrupted RBI-only publisher.
- A public CC0 Zenodo reconstruction of RBI/FBIL reference rates covers 25-Aug-1998 to 30-Sep-2026, with CSV/Parquet. Its README says it filled the RBI archive's Jul-2018–Mar-2022 gap using FBIL data and cross-checked public APIs. This is a candidate for a convenient mirror, but the official RBI/FBIL records remain the validation authority.
- MSEI's public RBI-reference-rate page displays recent rates and notes the rates are for viewing only and should not be used for any other purpose; do not use that page as a licensed model-training data source.
- Availability timing still needs validation. Preserve rate date and retrieval/publication timestamp; until confirmed, apply only from the next eligible NSE session. RBI reference rate is a fixing, not a continuously tradable spot quote.
- Sources:
  - RBI DBIE daily USD/INR: https://dbie.rbihub.in/tables?table=financial_markets.r691_daily_interbank_forex_rates_usd_vis_a_vis_inr
  - RBI Reference Rate Archive: https://rbi.org.in/scripts/ReferenceRateArchive.aspx
  - RBI notice on FBIL taking over from 10-Jul-2018: https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=44447
  - CC0 archive: https://zenodo.org/records/23076503
  - MSEI reference rate archive: https://www.msei.in/markets/Currency/Historical-Data/RBIReferenceRateArchives

No RBI forex CSV/JSON export was downloaded in this pass.

## 2026-11-14 — RBI short-term money-market rate source and 10Y yield gap

### Daily call/notice money rate
- RBI's April 2026 Handbook of Statistics documents **Table 27: Daily Call Money Rates**: daily interbank overnight call and notice money transactions, with borrowing/lending range and weighted-average rates, sourced from RBI/FMOD and based on reported transactions. The weighted-average call rate is an observable short-term liquidity indicator, not a policy target.
- RBI's current-statistics publication **Table 225: Daily Weighted Average Call/Notice Money Rates** provides date-level borrowing/lending range, weighted rates and turnover; a Jul-2026 publication displays daily rows for Feb–May 2026. RBI's data-release page classifies Money Market Operations and LAF results as daily releases.
- DBIE exposes a separate monthly weighted-average call money table from Mar-1991 to Mar-2026 (1,275 records); that monthly aggregate is not the same thing as the daily table. Preserve frequency and aggregation level.
- This is a better India-specific daily short-rate/liquidity candidate than a sparse policy repo event alone. Retrieve the full daily series from DBIE Monthly RBI Bulletin / Statistics → Financial Market → Money Market and capture publication lag. Until exact release timing is verified, lag to next eligible session.
- Sources: https://www.rbi.org.in/SCRIPTs/PublicationsView.aspx?id=24094 (April 2026 Handbook, Table 27) ; https://www.rbi.org.in/scripts/PublicationsView.aspx?id=24050 (Table 225) ; https://www.rbi.org.in/scripts/Statistics.aspx ; https://dbie.rbihub.in/tables?table=financial_markets.war_call_money_rn

### Daily Indian 10-year government yield remains unresolved
- The RBI/FBIL sources located so far establish benchmark identification and monthly/annual yields, but no official free daily 10-year generic yield download endpoint was confirmed in this search. FIMMDA methodology documents how the 10-year benchmark security is selected; RBI publications show historical yield charts but not a convenient daily downloadable long panel.
- The third-party aswinv90 dataset claims a daily India 10Y benchmark yield series from 2000 onward (6,901 rows), but source-level provenance and corporate licensing are not independently established. Keep it as an unverified candidate, not an authoritative source.
- For the PRD-required US DGS10, continue using FRED but add ALFRED vintages if revised data are possible. For the India model, compare daily call money + RBI repo events against the monthly OECD/FRED India 10Y series until a suitable daily yield source is established.
- Do not fill daily gaps by linear interpolation; only forward-fill known effective/available values where the economic definition supports it.

### Follow-up source verification — 2026-11-14 (public-source route check)

#### RBI government-security yields: daily gap narrowed, monthly route verified
- RBI Handbook of Statistics Table 217 / DBIE report 1368 is identified as Month-end Yield of SGL Transactions in Government Dated Securities for Various Maturities. A public reproduction provides 31 monthly series (1–30 year residual maturities plus the 10Y–1Y spread), April 1996–August 2026, with each observation dated on the first day of the month representing the prior month-end. This is a useful monthly 10-year yield feature, not a daily benchmark yield. Secondary locator: https://measure.thisindianlife.today/data/rates-gsec-curve/; RBI source series: DBIE report 1368 / Handbook report 217.
- RBI's official Compendium of Datasets records annual central/state government-security yield ranges and weighted averages, with digitised coverage from 30-Jun-2005 and annual frequency. This is not a daily 10-year series. Source: https://www.mospi.gov.in/sites/default/files/publication_reports/Compendium_of_Datasets_and_Registries_in_India_2024.pdf (dataset entry 4.1.66).
- RBI's official G-Sec FAQ directs users to negotiated-dealing-system order-matching trade information and CCIL for traded security prices. That is security-level trade data, not a ready-made generic constant-maturity 10-year yield history. Source: https://m.rbi.org.in/CommonPerson/english/Scripts/FAQs.aspx?Id=711.
- Conclusion: use the monthly RBI yield curve as a separately labelled low-frequency candidate if useful; do not interpolate it to daily frequency or relabel it as a daily 10Y benchmark. The daily generic 10Y series remains unresolved. Third-party daily 10Y history claims remain unverified until sample values can be reconciled against official security-level trades/benchmark methodology.

#### RBI call/notice money rates: official daily publication identified, archive export still open
- RBI's Data Releases page explicitly lists daily LAF Result, Money Market Operations and Reference Rate releases; RBI current-statistics Table 225 and Handbook Table 27 document daily call/notice money borrowing/lending ranges, weighted-average rates and turnover. Sources: https://www.rbi.org.in/scripts/Statistics.aspx and https://www.rbi.org.in/scripts/PublicationsView.aspx?id=24050.
- The DBIE monthly weighted-average call-money series is not a substitute for the daily market statistic. The daily release page currently describes a rolling recent period; a long-history machine-readable daily archive/export route was not verified in this pass.
- Feature handling: preserve borrowing/lending rates, turnover and publication date separately; until release-time availability is established, make the observation available only from the next eligible NSE session. Do not backfill or interpolate missing days.

#### MoSPI PLFS: official API workflow and coverage confirmed; no API rows retrieved here
- Official NSO India e-Sankhyiki MCP source maps PLFS to /api/plfs/getData and prescribes the four-step sequence: list datasets → indicators → metadata → data. It states indicator_code accepts one integer only; frequency_code=3 selects the monthly indicator set (Apr-2025–Sep-2026, All India only; indicators 1–3), while frequency_code=2 selects quarterly bulletin data (2018–2026; indicators 1–4). These are implementation details from the official server source, not a successful API retrieval by Northgate. Sources: https://github.com/nso-india/esankhyiki-mcp and https://github.com/nso-india/esankhyiki-mcp/blob/main/mospi_server.py.
- Monthly and quarterly PLFS must remain separate datasets with explicit frequency/status/geography. Monthly estimates are CWS and All India only in the documented current API window. Quarterly bulletin values already extracted in this project are not API observations. No PLFS API rows were downloaded in this pass.

#### NSE India VIX: official date-range CSV route verified, export not acquired
- NSE's official historical VIX page provides 1D/1W/1M/3M/6M/1Y/custom date selection and a CSV download control. Fields shown are Date, Open, High, Low, Close, Previous Close, Change and % Change. Sources: https://www.nseindia.com/reports-indices-historical-vix and https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives.
- The page's indexed snapshot returned No Records; therefore the interface/schema are confirmed but actual range retrieval, earliest date, completeness and export terms are not. No CSV was downloaded. Do not build an automated scraper against NSE pages or undocumented JSON endpoints given the previously recorded NSE terms restrictions.

#### Public EOD and survivorship-aware candidates: terms and limitations sharpened
- TejHQ / tejhq/indian-markets: Hugging Face lists a 1.25 GB Parquet dataset with daily updates and folders for NSE/BSE prices, adjusted prices, actions, delivery, symbol history and universe. TejHQ's data terms (updated 8-Nov-2026) expressly say it has no NSE/BSE/NSE Indices licence or written clarification; MIT covers code only, not data. Provider terms permit an individual's private research, backtesting and model training and local retention, but prohibit raw-data publication/redistribution; exchange terms independently apply. This is the clearest immediately inspectable candidate for a private sample cross-check, not a rights-cleared public dataset. Sources: https://huggingface.co/datasets/tejhq/indian-markets and https://tejhq.dev/data-terms.
- NSEDATA4ME: README claims 2005+ NSE daily OHLCV/delivery, delisted securities, corporate-action adjustment, ISIN-based symbol changes, index history and breadth; it describes an approximately 430 MB starting snapshot on a separate data branch. README explicitly says market data remains subject to NSE terms. GPL-3.0 applies to code, not exchange-derived data. No snapshot was downloaded or verified. Source: https://github.com/ancap97/NSEDATA4ME.
- BKKB20/nse-index-history: README claims 28 index histories from 2004–2026 reconstructed from roughly 100 NSE circulars. It documents three unprocessed scanned circulars from 2018–2019 and weaker pre-2010 name-to-ticker mapping; BSE indices are absent. No dataset licence was identified in the reviewed public page. Treat as an audit lead only; validate against original circulars before any PIT membership use. Source: https://github.com/BKKB20/nse-index-history.
- Existing Northgate panel remains the baseline. None of these candidate files has been downloaded, reconciled or merged. A reproducible sample comparison should check symbol aliases/ISIN, date coverage, OHLCV, corporate-action factors, delisted names, duplicates and adjusted-price methodology before considering replacement.

#### Rights/access correction
- No institutional sponsor, academic contact or user-side access request is required for the public-source research sequence. The previously identified academic research-data route is optional background only and is not a Northgate blocker. Continue with public API/exports and provider terms; do not make the user obtain institutional access.

- **TejHQ listing snapshot discrepancy (important):** the Hugging Face search-index result showed a 1.25 GB dataset with a 2026-11-11 update, while opening the dataset tree in this pass displayed 222 MB, 27 commits and a latest visible data commit dated 2026-08-06. The listing is mutable and the indexed result/page snapshot disagree. Do not quote a fixed dataset size or latest coverage until the exact repository revision/file manifest is pinned and inspected. This reinforces treating it as a candidate, not a verified complete cross-check. Source: https://huggingface.co/datasets/tejhq/indian-markets.
- Dataful's RBI-derived annual government-securities yield table is a separate annual aggregate: 90 rows, 5 columns, fiscal years 1980-81 to 2024-25 in the opened page. It is not the monthly maturity-specific curve and not daily 10Y data. Source: https://dataful.in/datasets/17685/.

### TejHQ deeper review — 2026-11-14

- The current TejHQ landing page describes five Parquet families: raw NSE/BSE bhavcopy, classified corporate actions, back-adjusted prices, symbol/ISIN history and derived metrics. It reports NSE coverage from 2010-01-04, BSE from 2024-07, ~6:30 PM IST EOD availability, and a stated 89% match within ±1% on 25k Yahoo close comparisons. Its schema has 14 columns: date, symbol, series, ISIN, name, OHLC, last, previous close, volume, turnover and trades. Source: https://tejhq.dev/ (sections 02–04).
- The same page says adjusted close is calculated by reverse cumulative corporate-action factors for splits, bonuses and dividends, per ISIN. This needs independent checks: confirm whether the adjustment convention matches Northgate's target definition (total-return-like dividend adjustment versus split-only price adjustment), whether the full adjusted OHLC is consistent, how demergers/mergers are treated, and whether historical values are revised when new actions arrive. Do not replace the current target until this is understood.
- TejHQ advertises a point-in-time monthly liquid universe (top 500 by trailing 63-day turnover, delisted names retained in the months they qualified). This could help reduce survivorship bias for a broader research panel, but it is not official index membership. Validate rebalance effective dates, whether ranking uses only information available at that date, tie handling, listing/suspension filters, and historical completeness before use.
- Important provider-terms conflict: the landing page says the Parquet data is MIT-licensed/open, while its dedicated data-terms page (updated 2026-11-08) says MIT applies only to pipeline/SDK code, not market data; it says TejHQ has no NSE/BSE/NSE Indices licence or written clarification, permits personal research/model training/local storage, prohibits raw-data publication/redistribution, and says exchange terms apply independently. Treat the dedicated data-terms page as the more specific statement, preserve the conflict, and do not treat the dataset as rights-cleared for redistribution or commercial deployment. Sources: https://tejhq.dev/ and https://tejhq.dev/data-terms.
- The dataset's current Hugging Face root search snapshot reported 1.25 GB / ~8.33M rows and an 11-Nov-2026 actions/adjusted/symbol-history/metrics update; individual subtree views returned older August snapshots. The landing page separately reports 8.11M rows and 89% Yahoo reconciliation. These snapshots are not perfectly synchronized. Pin a repository commit and inspect its actual file manifest before download/reconciliation; record commit hash, file sizes and retrieval time.
- TejHQ's own 89% within-±1% Yahoo reconciliation is a provider-reported metric, not independent validation. The remaining 11% outside tolerance may be material and must be investigated rather than ignored. Compare raw exchange close first (should match source bhavcopy), then adjusted close under explicitly matched corporate-action definitions; separate legitimate convention differences from errors.
- No TejHQ files have been downloaded or compared with Northgate in this pass.

### NSE historical reports: VIX and index route cross-check
- NSE's public All Reports page is indexed with a historical India VIX date-range example and fields Date, Open, High, Low, Close, Previous Close, Change and % Change. The sample rendered for a requested 01–05 Jan 2019 period shows 03-Sep-2018, and a duplicate row appears in the indexed preview. Treat this as a preview/indexing anomaly until a real bounded CSV is acquired; do not infer that the VIX archive begins in 2018 or that rows are duplicated in the source file. Source: https://www.nseindia.com/all-reports.
- The dedicated India VIX historical page confirms custom range controls and CSV download but its indexed result says No Records. Combined, these establish that the route is exposed but do not establish reliable export/coverage. The official index archive page also lists historical index data, P/E/P/B/dividend yield, TRI and advances/declines downloads. Sources: https://www.nseindia.com/reports-indices-historical-vix and https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives.
- NSE defines India VIX as annualised implied volatility for the next 30 calendar days derived from NIFTY option bid/ask prices. It is forward-looking implied volatility, not realised volatility. Source: https://www.nseindia.com/static/products-services/indices-indiavix-index.

### MoSPI PLFS MCP: exact metadata constraints reconfirmed
- The current official server source explicitly documents PLFS frequency_code=1 annual, 2 quarterly, 3 monthly; monthly coverage Apr-2025–Sep-2026, All India only, indicators 1–3; quarterly calendar years 2018–2026, indicators 1–4. It warns indicator_code accepts a single integer only; comma-separated values cause HTTP 500. The workflow must use list_datasets → get_indicators → get_metadata → get_data, passing metadata-returned filters verbatim. Sources: https://github.com/nso-india/esankhyiki-mcp/blob/main/mospi_server.py and https://github.com/nso-india/esankhyiki-mcp/blob/main/README.md.
- The MCP server repository code is MIT-licensed, but that licences the connector implementation, not MoSPI's underlying statistical data. No PLFS rows were retrieved in this web research pass.

### BigQuery cost control for GDELT pilot
- Google documents that BigQuery public datasets are hosted for users and the first 1 TB of query processing per month is free; usage beyond free allowance is chargeable and requires billing. A GDELT GKG pilot can therefore be run with a strict bytes-scanned cap and partition/date filters, but only after confirming the exact GDELT public table and schema. Do not scan the full archive or assume unlimited free usage. Source: https://docs.cloud.google.com/bigquery/public-data.


## Official NSE bhavcopy format and MoSPI PLFS release-calendar check — 2026-11-14

### NSE daily cash-market source
- The official NSE All Reports page currently exposes the final CM-UDiFF Common Bhavcopy as a ZIP/CSV (example listed for 11-Nov-2026: `BhavCopy_NSE_CM_0_0_0_20261111_F_0000.csv.zip`). The page explicitly says the older CM Bhavcopy CSV and CM Common Bhavcopy CSV were discontinued from 08-Jul-2024 and directs users to the CM-UDiFF final format. It also lists a separate Full Bhavcopy and Security Deliverable data CSV.
- The NSE historical reports page separately lists archives for daily/monthly equity reports, historical index data, India VIX, P/E/P/B/dividend yield, and Total Returns Index values. This is a stronger official-source map than relying on the stale indexed VIX preview alone.
- Research implication: use CM-UDiFF as the post-08-Jul-2024 raw EOD source candidate and identify the matching pre-transition official archive/format before stitching. Parse the official readme/schema and compare overlapping dates around the transition if available. Do not silently mix the legacy and UDiFF schemas.
- The page is an interactive download portal; the search result establishes that the download is listed, not that a complete historical archive has been acquired or that automated collection is permitted. Respect NSE terms and use the intended export route. No bhavcopy/VIX file was downloaded in this pass.
- Sources: https://www.nseindia.com/all-reports ; https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives ; https://www.nseindia.com/reports-indices-historical-vix.

### India VIX route qualification
- NSE's official historical reports directory lists Historical Data - India VIX. The dedicated VIX page exposes 1D/1W/1M/3M/6M/1Y/custom ranges and CSV download. Its unfiltered indexed view returns “No Records”; that is not evidence that historical coverage is absent. The prior all-reports preview had a mismatched sample date and duplicated row, so no coverage or duplicate conclusion is drawn from that preview.
- Next validation should be a small manually selected date-range export (e.g. one calendar month), followed by header, row-count, date continuity and spot-check validation against official index publications. Do not infer an API or automate undocumented endpoints.

### PLFS release-calendar update
- The official MoSPI 2026-27 advance release calendar updated through October 2026 schedules the Monthly Bulletin of PLFS for October 2026 on 15-Nov-2026. As of this 14-Nov research pass, this is a scheduled future release, not an observed publication. The July-Sep 2026 quarterly bulletin was separately scheduled for 10-Nov and must remain a distinct product/frequency.
- Current PLFS MCP source code documents monthly frequency_code=3 coverage Apr-2025–Sep-2026 (All India; indicators 1–3) and quarterly frequency_code=2 coverage for calendar years 2018–2026 (indicators 1–4). The four-step metadata workflow remains mandatory; one indicator_code per request. Connector source code is MIT-licensed, but this does not license MoSPI data.
- Keep monthly bulletin, quarterly bulletin and API extracts in separate source tables with their own reference period and actual publication/retrieval timestamps. Calendar dates are schedules, not proof of publication.
- Sources: https://www.mospi.gov.in/uploads/documents/releaseCalender/1793948871564-ARC%202026-27%20updated%20till%20October%202026.pdf ; https://github.com/nso-india/esankhyiki-mcp/blob/main/mospi_server.py ; https://github.com/nso-india/esankhyiki-mcp/blob/main/README.md.

### Acquisition status
- No raw NSE, VIX or PLFS observations were downloaded, validated or merged in this pass. This update records source route and format findings only.


## TejHQ Hugging Face dataset card and current data-terms reconciliation — 2026-11-14

A further inspection of the Hugging Face dataset page exposed material version/documentation drift; do not treat the viewer's top-level licence badge or stale card as sufficient rights or schema evidence.

- Current search-indexed Hugging Face dataset page identifies `tejhq/indian-markets`, Parquet format, and a 7.36M-row NSE subset. The current dataset card describes seven trees: raw prices, corporate actions, back-adjusted prices, symbol history, derived metrics, a survivorship-bias-free liquidity universe, and NSE/BSE delivery quantity and delivery percentage. It claims daily refresh for raw/action/adjusted/symbol/delivery trees, while metrics/universe are month-end snapshots. These claims need a pinned revision and tree-by-tree manifest before use.
- A search-indexed commit `408bab9d85371d333cc18572a428934f4fad0112` is titled “daily: 2026-11-09 NSE+BSE prices” and changes the 2026 NSE and BSE Parquet objects. It provides a useful revision pin for investigating that snapshot, not proof that all seven trees or all dates are present in that commit.
- The opened Hugging Face viewer is internally stale: its top badge says MIT; its preview shows 8.33M rows of corporate-action records; the card body says a much older layout with NSE/BSE from 2024-01 and no corporate actions yet; it also shows a separate 7.36M NSE price split in the current search result. These disagree with the newer card text in search, which claims NSE from 2010-01-04 and BSE from 2024-07-08 and seven data trees. Treat these as different revisions/auto-generated viewer snapshots, not one consistent dataset manifest.
- TejHQ's dedicated data terms updated 2026-11-08 are more specific than the HF MIT badge/card: MIT covers the pipeline/SDK code only, not exchange data; TejHQ states it has no NSE/BSE/NSE Indices licence or written clarification; personal research, backtesting, private model training and local retention are allowed under TejHQ's terms; raw data publication/redistribution is prohibited; exchange terms independently apply. The HF card's redistribution claim therefore conflicts with the provider's dedicated terms. Follow the specific terms and do not publish raw data.
- The dataset card's raw-price schema includes date, symbol, series, ISIN, name, OHLC, last, previous close, volume, turnover and trades. It says pre-2012 NSE rows lack ISIN/trade count. These fields are candidates only until verified against a pinned Parquet file and exchange source.
- A key QA warning from the current dataset card: symbol/ISIN continuity and corporate-action factors may be chained across new ISINs around face-value splits/re-listings. The provider's own caveat says exchange files can contain errors and adjusted data is supplied without warranty. Independently test ticker/ISIN transitions, duplicate keys, non-positive/zero-volume rows, OHLC bounds, corporate actions, and adjusted-vs-raw returns. Do not use current adjusted history as a point-in-time price vintage without understanding retrospective factor updates.
- No Parquet object was downloaded or independently inspected in this pass. The 2026-11-09 commit is a candidate pin for a future bounded file inspection, not a validated source approval.
- Sources: https://huggingface.co/datasets/tejhq/indian-markets ; https://huggingface.co/datasets/tejhq/indian-markets/commit/408bab9d85371d333cc18572a428934f4fad0112 ; https://tejhq.dev/data-terms.


## TejHQ current partition and pipeline audit — 2026-11-14 (continued)

- The live Hugging Face dataset tree now reports a verified daily revision labelled `daily: 2026-11-11 actions + adjusted + symbol-history + metrics` (short commit `10bd698`), total repository size about 1.25 GB. The `prices_adjusted/` tree exposes annual NSE Parquet files for 2010–2026 and BSE files for 2024–2026; the 2026 NSE adjusted file is listed at about 19.3 MB. This is a materially newer and more complete visible tree than the earlier 2026-11-09 snapshot. Pin the full commit hash before any actual acquisition; the short hash alone is not a sufficient reproducibility identifier.
- The provider's public `tej-bazaar` GitHub README currently describes an older pipeline state: five trees, Hive partitioning by year/month/date, and coverage beginning 2024-01-01 with legacy pre-cutover data not yet supported. This conflicts with the live HF tree's 2010–2026 annual NSE partitions and seven-tree card. Treat README/docs as stale relative to the live dataset until repository code and revision history are reconciled; do not infer the actual raw-price path from the stale README example.
- The public pipeline README documents raw schema candidates (date, symbol, series, ISIN, name, OHLC, last, previous close, volume, turnover, trades), and adjusted fields `adj_factor_cumulative` and `adj_close`. It says adjustment factors incorporate later corporate actions (including dividends), and documents Yahoo adjusted-close comparison at 89% within ±1% for top-50 rows in 2024–2026. This is provider-reported QA, not independent exchange reconciliation and not proof of point-in-time adjusted prices.
- Important design implication: the provider explicitly rebuilds historical adjusted data when future actions arrive. These adjusted histories are retrospective; for a historical forecast at date t, use only information/action factors knowable by t or compute a PIT-adjustment convention. Never feed today's fully back-adjusted historical prices into a leakage-sensitive backtest without auditing this.
- Official NSE All Reports page confirms the current CM-UDiFF Common Bhavcopy Final ZIP and a separate “New Bhavcopy Format readme.xlsx”; legacy CM Bhavcopy CSV formats are discontinued from 2024-07-08. The official NSE UDiFF guidance confirms CSV with comma separators, ISO 8601 dates/times, ASCII encoding and ZIP/GZ compression. The readme workbook itself and a UDiFF sample were not downloaded or inspected; exact CM column mapping and pre/post-cutover stitching remain open.
- No TejHQ Parquet or NSE bhavcopy was downloaded, no raw values compared, and no dataset approved. Next acquisition test should first resolve current raw tree path + full HF commit SHA, then fetch only one target-year partition or one bounded day and compare selected target symbols against an official NSE CM-UDiFF sample.
- Sources: https://huggingface.co/datasets/tejhq/indian-markets/tree/main ; https://huggingface.co/datasets/tejhq/indian-markets/tree/main/prices_adjusted ; https://github.com/tejhq/tej-bazaar ; https://www.nseindia.com/all-reports ; https://www.nseindia.com/static/resources/forms-formats-members ; https://nsearchives.nseindia.com/web/sites/default/files/inline-files/UDiFF%20guidance%20document_Ver1.0.pdf .


## TejHQ pipeline code audit — raw layout, parser and adjustment caveats (2026-11-14)

- The live dataset card and current public pipeline README now agree on seven published trees and NSE equity coverage from 2010-01-04 to current; BSE starts 2024-07-08. The raw NSE path is annual rollup `nse/year=YYYY/nse_YYYY.parquet`, sorted by (symbol,date). The raw schema includes date, symbol, series, ISIN, name, OHLC, last, previous close, volume, turnover and trades. Pre-2012 NSE ISIN and trade count are null by source design. This replaces the older stale five-tree/2024-only description seen in earlier README snapshots.
- The repository parser code (blob `643310359347d22f83298a0dc480e9ac4bbd43a8`) documents separate CMTS and legacy NSE parsing. Modern CMTS compact columns map to the normalized 14-field schema; legacy `SYMBOL/SERIES/TIMESTAMP` is parsed separately, optional ISIN/trade-count columns are null-filled, and mixed-case/two-digit-year dates are normalized. This is code inspection only; no parser test was run by Northgate.
- The pipeline's instrument-chain code (blob `038950ced664e3472633ecfa9900c8f7b8d358db`) links same-symbol ISIN intervals separated by at most 30 calendar days. This is a heuristic; independently audit false merges caused by ticker reuse, demergers, relistings and symbol reuse, especially around the target universe's corporate events. The raw ISIN is retained separately.
- Adjustment code (blob `bc10e5783f45da03ee3f8c413cf87adcfacb0f04`) applies factors only to dates strictly before an action's ex-date. Split and bonus factors are formulaic; dividend factor is (prior close - cash) / prior close. Rights, buyback, demerger, merger, AGM and other actions currently receive factor 1.0. Missing dividend inputs also return 1.0, leaving the raw action subject for review. Therefore adjusted close is not a fully economically total-return-adjusted series for every corporate event; demerger treatment in particular differs from some vendors. Audit action classifications and all factor-1 cases before using adjusted close as target.
- Back-adjustment is recomputed from full history when later corporate actions arrive. This retrospectively changes older absolute adjusted price levels. For next-session price ratios/returns, common factors from actions later than both dates cancel, but an absolute adjusted-close target can be on a subsequently revised scale. Preserve the PRD target as a requirement for now; before model training compare the prescribed absolute target against a return/ratio representation as an explicitly labelled experiment, not a silent target change. A point-in-time adjustment snapshot would be needed to claim historical as-known adjusted-price levels.
- The provider's 2026-09-08 Yahoo reconciliation reports 96.88% of 25,329 daily comparisons within ±1% for 48/50 selected liquid NSE names over 2024-01-01 to 2026-05-06. It identifies Yahoo convention differences for TRENT bonus timing and ITC demerger treatment. This is vendor-vs-vendor adjusted-close QA, not independent raw NSE bhavcopy reconciliation, and it does not cover Northgate's full target universe / 2016–2023 period.
- The current README's legal statement is more nuanced than the generic HF MIT badge: code is MIT; data is not covered by MIT; the repository says it holds no exchange licence and says free personal/research use while exchange terms still govern. Continue following the provider's dedicated terms and exchange restrictions; no raw redistribution.
- No raw parquet acquired, no official exchange sample compared, no parser or tests run, and no Northgate dataset approved. Exact full HF commit SHA for the current raw tree remains to be pinned (the visible tree shows short commit `d6f1912`; do not treat a short hash as a complete reproducibility pin).
- Sources: https://huggingface.co/datasets/tejhq/indian-markets ; https://huggingface.co/datasets/tejhq/indian-markets/tree/main/nse ; https://github.com/tejhq/tej-bazaar/blob/master/README.md ; https://github.com/tejhq/tej-bazaar/blob/master/pipeline/parse.py ; https://github.com/tejhq/tej-bazaar/blob/master/pipeline/instrument.py ; https://github.com/tejhq/tej-bazaar/blob/master/pipeline/actions/back_adjust.py ; https://github.com/tejhq/tej-bazaar/blob/master/pipeline/actions/factors.py ; https://github.com/tejhq/tej-bazaar/blob/master/reconcile_report.md .


### Dataset freshness correction — 2026-11-14
A further live-tree check found a newer 2026-11-12 dataset publication than the 2026-11-11 revision noted above. The raw `nse/` tree shows commit short hash `d6f1912`; the adjusted `prices_adjusted/nse_2024.parquet` history shows 2026-11-12 commit short hash `8b77c06`. Hugging Face's public page exposes only short hashes in the indexed view; the full immutable commit SHA was not obtained. Therefore the 2026-11-11 note above is superseded for freshness, and no full revision pin is yet recorded. The documented raw annual path remains `nse/year=YYYY/nse_YYYY.parquet`.


### TejHQ raw ingestion and transform QA review — 2026-11-14
- Inspected public `pipeline/fetch.py`, `pipeline/parse.py`, `pipeline/transform.py`, plus parser/transform tests. Fetcher selects legacy NSE URL before 2024-07-08 and CMTS/UDiFF-style URL from cutover; parser maps modern compact fields and legacy `SYMBOL/SERIES/TIMESTAMP` separately. Tests include synthetic examples for 2010 legacy rows and modern 2025 values. These are provider tests; Northgate has not run them and they do not replace independent file reconciliation.
- Transform defaults to NSE `EQ/BE/BZ` and BSE `A/B/T`, drops null OHLC/volume, drops zero-volume rows by default, and filters invalid price relationships. For Northgate's 10 mainboard tickers, we should explicitly decide whether to use `EQ` only or preserve BE/BZ; do not silently mix series. Zero-volume removal may create missing target rows and needs a documented policy.
- Code-level QA gaps worth testing: transform deduplicates on `(date, symbol)` (not series or ISIN) and silently keeps the first row; it does not explicitly require positive `low` or non-negative turnover/trades; dropped rows are not emitted as a rejection/audit table. These may be acceptable for the provider's broad equity dataset but must be checked against raw source records and Northgate's target symbols before adoption.
- Fetcher uses browser-like headers, retries and direct NSE archive URLs. This describes the provider's implementation, not a recommendation for Northgate to automate NSE collection; Northgate must still respect exchange terms and prefer official permitted downloads or licensed access.
- Source blobs reviewed: fetch.py `40b7daf0c2c52ff94a079efa13e0b766fcd751ec`; parse.py `643310359347d22f83298a0dc480e9ac4bbd43a8`; transform.py `495be2ddaab322550f43a0f57c68d19d7dd51109`; tests/test_parse.py `56cc6d24d11ff993be3e92a7024e15d63af8655c`; tests/test_transform.py `d60e345eb8a1dca91f8abccbb64f34ea640c5433`.
- No Northgate execution, raw data download, validation or model training occurred.

## TejHQ target-universe coverage and rights/format cross-check — 2026-11-14

### Provider-published per-symbol coverage
Individual TejHQ stock pages report the following first NSE observations for Northgate's ten provisional equities:

| Symbol | Provider-reported first date | Page's latest date observed in this research |
|---|---:|---:|
| BHARTIARTL | 2010-01-04 | 2026-11-11 |
| HDFCBANK | 2010-01-04 | 2026-11-12 |
| HINDUNILVR | 2010-01-04 | 2026-11-11 |
| ICICIBANK | 2010-01-04 | 2026-11-12 |
| INFY | 2011-06-29 | 2026-11-12 |
| ITC | 2010-01-04 | 2026-11-12 |
| LT | 2010-01-04 | 2026-11-11 |
| RELIANCE | 2010-01-04 | 2026-11-12 |
| SUNPHARMA | 2010-01-04 | 2026-11-12 |
| TCS | 2010-01-04 | 2026-11-12 |

All ten provider-reported histories begin before Northgate's 2016 start date. These pages are provider-generated summaries and are not a row-level completeness or correctness audit. The three pages showing 2026-11-11 rather than 2026-11-12 are not assumed missing the 12th; they may reflect page refresh/cache lag. Verify from raw/API data.

### API acquisition path and terms
- TejHQ documents keyless raw OHLCV via GET /v1/ohlcv/nse/{symbol}; its free API key is needed for adjusted prices and delivery, not raw OHLCV. The provider terms permit personal research, backtesting, paper trading, local storage and private dashboards; keyless limits are 120 requests/minute. Use only documented OpenAPI endpoints. No API request or dataset download was completed in this review.
- Provider terms explicitly say TejHQ holds no NSE/BSE/NSE Indices licence or written clarification; MIT covers pipeline/SDK code only, not market data; exchange terms apply independently; raw-data publication/redistribution is prohibited. This supersedes any casual interpretation of the HF metadata badge. The current indexed HF search result shows exchange-public-data, while a cached rendered HF page still shows mit; treat the mismatch as metadata/cache drift and follow the specific data terms, not the badge.

### Official NSE UDiFF references
- NSE Forms & Formats page currently lists UDiFF Catalogue versions 1.0–4.0, a CM Bhavcopy File Format document, and a sample test file. The page was updated 30-Jun-2026. NSE All Reports lists the daily CM-UDiFF Common Bhavcopy Final ZIP and a separate “New Bhavcopy Format readme.xlsx”; legacy CM Bhavcopy CSV is discontinued effective 08-Jul-2024.
- NSE Circular NSE/MSD/62424 dated 12-Jun-2024 states legacy and UDiFF bhavcopy formats would be available in parallel through 05-Jul-2024 and old bhavcopy formats discontinued from 08-Jul-2024. This supports the pipeline's cutover date. The actual XLSX/ZIP binary sample could not be retrieved/inspected in this research session, so exact CM field mapping still needs inspection.
- Current public HF search metadata lists a custom exchange-public-data label; cached rendered page still displays MIT and stale older content. Current GitHub README + TejHQ terms are more internally consistent: pipeline code MIT, data not MIT, no exchange licence, personal/research use allowed by TejHQ terms subject to exchange terms.

### Current disposition
TejHQ has sufficient claimed symbol coverage to justify a bounded raw-data pilot for 2016–2026. It is not approved as Northgate's source yet. Next validation: obtain a single-year raw Parquet file (prefer 2025) or small API range for two or three symbols, inspect dtypes/series/date gaps/duplicates/zero-volume rows, and compare one or more exact dates to a permitted official NSE UDiFF export. Keep raw data private. No file, API response or exchange sample has been acquired in this review.

Sources: https://tejhq.dev/stocks/bhartiartl ; https://tejhq.dev/stocks/hdfcbank ; https://tejhq.dev/stocks/hindunilvr ; https://tejhq.dev/stocks/icicibank ; https://tejhq.dev/stocks/infy ; https://tejhq.dev/stocks/itc ; https://tejhq.dev/stocks/lt ; https://tejhq.dev/stocks/reliance ; https://tejhq.dev/stocks/sunpharma ; https://tejhq.dev/stocks/tcs ; https://tejhq.dev/data-terms ; https://tejhq.dev/keys ; https://www.nseindia.com/static/resources/forms-formats-members ; https://www.nseindia.com/all-reports ; https://avantiscdnprodstorage.blob.core.windows.net/legalupdatedocs/32584/NSE_issued_a_circular_regarding_the_Standardization_of_Exchange_to_Member_Interface_files_in_Unified_Distilled_File_Formats_UDiFF_June122024.pdf .
