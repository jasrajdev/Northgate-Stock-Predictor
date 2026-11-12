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
