# Dataset Inventory and Acquisition Plan

Updated: 2026-11-13

## Current verified price dataset

The user-uploaded `market_panel.csv` was inspected from the conversation upload:
- 29,484 rows; 11 tickers.
- Ten provisional Indian equities: BHARTIARTL.NS, HDFCBANK.NS, HINDUNILVR.NS, ICICIBANK.NS, INFY.NS, ITC.NS, LT.NS, RELIANCE.NS, SUNPHARMA.NS, TCS.NS.
- Benchmark: ^NSEI.
- Columns: Date, Ticker, Name, Adj Close, Close, Dividends, High, Low, Open, Stock Splits, Volume.
- Date coverage begins 2016-01-01; exact per-ticker end dates should be rechecked by the GPU rebuild.
- The file is a Yahoo Finance/yfinance download. It is not an official exchange archive and adjusted historical values may be revised.
- The Mac-generated `feature_panel.csv` (about 17 MB), `modeling_dataset_next_day.csv` (about 18 MB), and split files were reported locally but are not in GitHub. The repo's rebuild script recreates them on the GPU laptop.

## Required source plan

| Data family | Candidate source | Coverage / access | Use and caveat |
|---|---|---|---|
| Daily equity OHLCV | Yahoo Finance via yfinance for provisional research; NSE historical reports for official exchange records | yfinance is easy to reproduce; NSE provides official historical reports and price-volume archives | Adjusted series and redistribution terms need scrutiny; NSE historical downloads/data sharing may have conditions |
| Broad-market benchmark | NIFTY 50 (^NSEI); prefer NIFTY 50 TRI for total-return portfolio benchmark if reliably accessible | Yahoo price index is currently in the local panel; NSE historical index archives are available | Price index excludes reinvested dividends; benchmark definition must be consistent |
| Volatility index | CBOE VIX (^VIX) as PRD example; India VIX may be added as a local-market proxy | Yahoo candidate; validate coverage and definitions | VIX is US-market volatility and not a substitute for India VIX |
| Interest rates/yields | FRED DGS3MO, DGS10; RBI DBIE for Indian rates | FRED public series; RBI DBIE offers downloadable Indian time series | Observation date is not necessarily publication date; use release/vintage timestamps before merging |
| Inflation | MoSPI e-Sankhyiki CPI API (base years 2010, 2012, 2024) | Open API with pagination; base-2024 back series for All-India Rural/Urban/Combined Jan 2013–Dec 2024 was announced for 12 Feb 2026 | Keep base-year/series metadata. Do not splice current and linked back-series naively. Historical publication-vintage dates matter |
| Unemployment | FRED UNRATE per PRD; consider PLFS for India-specific context | FRED public series; MoSPI PLFS releases | Low frequency and delayed publication; release-time alignment required |
| Financial news | GDELT 2.0 archives / DOC API; company-specific publisher archives | GDELT raw archives cover English-stream data since Feb 2015; DOC API's date search is rolling/limited (up to one year per published docs) | GDELT is broad news metadata, not a complete Indian financial-news archive; article text availability and entity matching vary |
| India financial-news research corpus | IN-FINews (Zenodo) | 3,348 Indian e-news articles, Feb–Aug 2025 | Useful small validation corpus only; six months is insufficient for the full 8–10-year history |

## CPI findings

MoSPI's current e-Sankhyiki CPI API documentation lists base years 2010, 2012 and 2024, with Current/Back series and paginated endpoints. The user's earlier working request fetched base-2012 General-Overall All India Combined monthly records for 2019–2023.

The uploaded `cpi_33.xlsx` was inspected: 31,460 rows and 15 columns, all base_year=2024 and series=Current in the inspected rows; it contains granular state/sector/division-level records from January 2025 through October 2026. It is not a complete 2013–2026 monthly headline CPI time series by itself.

MoSPI's CPI 2024 FAQ states the linked back series is base 2024=100 and includes All-India Rural, Urban and Combined indices for Jan 2013–Dec 2024, with annual inflation rates from Jan 2014–Dec 2024. This linked series is calculated using linking factors and is not the same as the contemporaneous 2012-base release history. Preserve both series and their vintage/availability metadata rather than pretending they are one unchanged series.

## News findings

GDELT DOC 2.0 supports timestamped article search, but its documented query window is limited to the recent rolling period (up to one year). The GDELT project also publishes historical 15-minute archives from 2015; GKG records can provide entities/themes/tone, but are not a guaranteed substitute for full article text needed by FinBERT. The Zenodo IN-FINews dataset has 3,348 Indian e-news articles across roughly six months in 2025, useful as a small benchmark but not enough to satisfy the PRD's long-history request.

## Recommended staged completeness definition

1. **Baseline-trainable:** daily adjusted price/volume, features, next-session labels, chronological train/validation/test, leakage checks. This is achievable with the current ten equities + NIFTY 50 panel.
2. **Macro-enriched:** CPI, rates/yields, unemployment and volatility/breadth indicators with actual release timestamps and explicit source/base-year metadata.
3. **Sentiment-enriched:** historical timestamped ticker/market news, FinBERT and VADER scores, after-close mapping to next eligible session.
4. **PRD-complete:** at least 8 years per ticker, 8–15 equities + benchmark, documented cleaning/EDA/stationarity, four classical + four DL models, portfolio optimisation/backtest, recommendation logic, dashboard and report.

The current panel meets a baseline starting point, not the full PRD data contract. Historical constituent/survivorship bias and official adjusted-price validation remain limitations.


## MoSPI CPI extraction — verified from supplied workbooks (2026-11-13)

A reproducible extractor is now available at `scripts/extract_mospi_cpi.py`. It reads the monthly MoSPI Annex-I Excel releases and the supplied `cpi_33.xlsx` workbook, extracts only the All-India headline General CPI row, and keeps the CPI base years separate.

### Base-2012 monthly release vintages
- 18 supplied monthly workbooks, from July 2024 through December 2025.
- Extracted 108 rows: 19 reference months (June 2024–December 2025) × 3 sectors (Rural, Urban, Combined) × 2 vintage observations per monthly release.
- Preserves prior-month Final and current-month Provisional values, with release-month and source-file provenance.
- No missing headline index values and no duplicate reference-month/sector/release-month/status keys in the extracted rows.
- The earliest supplied release is July 2024, so coverage starts with June 2024. Earlier months are not present in these supplied Annex-I files.

### Base-2024 current headline series
- Extracted 66 rows from `cpi_33.xlsx`: 22 months (January 2025–October 2026) × Rural, Urban and Combined.
- All headline index values are present. The source workbook has 36 missing year-on-year inflation values in these selected rows; preserve them as missing rather than filling them.
- This is a separate base-2024 Current series. Do not concatenate or splice it to the base-2012 series without a documented linking methodology.

### Point-in-time limitation
The supplied tables do not provide exact publication date/time in the extracted rows. The extractor leaves `release_date_exact` blank deliberately. Do not merge CPI into daily stock features by reference month alone: a CPI value may be used only after its actual publication timestamp is known and is no later than the simulated prediction timestamp. The `latest_available` CSV is a convenience snapshot, not a leakage-safe historical panel.

### Generated outputs
- `india_cpi_base2012_release_vintages.csv`
- `india_cpi_base2012_latest_available.csv`
- `india_cpi_base2024_current_headline.csv`
- `india_cpi_dataset_qa.json`

These outputs were generated from the conversation's supplied workbooks and are not committed as model-ready repository data. Rebuild them using the script and local raw input files.


### Full historical base-2012 headline series recovered (2026-11-13)
- The December 2025 workbook's Annex-VI and Annex-VII contain the full All-India Combined headline CPI index and year-on-year inflation series: January 2013–December 2025.
- Extracted 156 monthly index rows. The latest row (December 2025) is explicitly marked provisional with an asterisk in the source; the prior rows are historical/final in that snapshot. Fourteen year-on-year inflation cells are missing in the sheet and remain missing.
- The snapshot was released with the December 2025 CPI press release on 12 January 2026. This timestamp applies to the downloaded historical snapshot, not to the original release date of each historical monthly observation. Do not back-assign the snapshot's availability to earlier dates.
- The full historical file is Combined only. The Annex-I vintages retain Rural, Urban and Combined for the more recent supplied release period.
- This closes the raw historical-coverage gap for base-2012 Combined CPI, but point-in-time feature construction still needs the actual monthly publication dates (official schedule: 12th of the following month, shifted to next working day when needed) or archived press-release dates.


## Daily market-context acquisition scaffold (2026-11-13)
- Added `scripts/download_market_context.py` to download India VIX and NIFTY sector-index proxies (Bank, IT, Pharma, Auto, FMCG, Metal, Realty, Energy and PSU Bank) from Yahoo Finance into a separate daily panel, with per-series coverage and missing-close QA.
- This is an acquisition scaffold only; it has not yet been executed in this session. Yahoo Finance is secondary-vendor data. NSE provides official historical India VIX downloads and describes India VIX as the options-implied expected volatility over the next 30 calendar days. Prefer validating the downloaded series against NSE before model use.
- RBI DBIE's Key Rates table provides historical policy-rate event data (repo, reverse repo, SDF, MSF, bank rate and CRR, among others) with downloadable CSV/JSON; it is the preferred source for Indian policy rates. The RBI policy-rate history is irregular/event-based, so it must be converted to a daily effective-rate panel using forward-fill only after each effective date.
- No macro/context data has been merged into the stock modelling dataset yet.


### CPI cross-validation result (2026-11-13)
- Compared the latest supplied Annex-I Combined index values against the December 2025 workbook's Annex-VI full time-series values for all 19 overlapping reference months (June 2024–December 2025): 19/19 exact matches; maximum absolute difference 0.0.
- Annex-VI/Annex-VII base-2012 Combined history contains 156 monthly index values from January 2013–December 2025. Fourteen YoY inflation values are missing: all 12 months of 2013 (no prior-year comparison in the sheet) and April–May 2020.
- The base-2024 current workbook contains 66 headline rows from January 2025–October 2026; 36 YoY inflation values are missing in the supplied workbook rows.
- The committed extractor now reports missingness and the Annex-I vs Annex-VI overlap check in its QA JSON.


## Macro context source audit — FRED/OECD (2026-11-13)

A reproducible downloader is now committed as `scripts/download_macro_context.py`. It requests seven series from FRED's public graph CSV endpoint and writes a separate observation-date panel plus QA report. It has not yet been executed locally; successful downloads and row counts are therefore not claimed.

| Series ID | Indicator | Frequency | Role / limitation |
|---|---|---|---|
| DGS3MO | US 3-month Treasury constant-maturity rate | Daily | PRD-specified global short-rate reference |
| DGS10 | US 10-year Treasury constant-maturity rate | Daily | PRD-specified global long-yield reference |
| CPIAUCSL | US CPI, all urban consumers | Monthly | PRD-specified global inflation reference; US, not India |
| UNRATE | US civilian unemployment rate | Monthly | PRD-specified global labour reference; US, not India |
| INDIRLTLT01STM | India 10-year government bond yield | Monthly | OECD via FRED; monthly, not daily RBI benchmark yield |
| INDIR3TIB01STM | India 3-month interbank rate | Monthly | OECD via FRED; not identical to RBI repo rate |
| IRSTCB01INM156N | India central bank rate | Monthly | OECD via FRED; historical monthly series ends December 2023 in the currently indexed FRED metadata |

FRED's currently indexed metadata reports India 10-year monthly yield through September 2026 and India 3-month interbank monthly rate through September 2026. The 10-year series is OECD-sourced and subject to citation/copyright requirements. Standard FRED graph CSV returns a current snapshot, not ALFRED vintage data; it must not be treated as point-in-time truth for historical backtests. Preserve observation dates and separately obtain release/vintage dates before joining to daily stock data.

Official NSE exposes a historical India VIX download page and describes India VIX as NIFTY-options-implied expected volatility over the next 30 calendar days. The existing Yahoo Finance market-context script is only a secondary-vendor fallback; validate against NSE before treating it as an authoritative series.

India PLFS is the preferred domestic unemployment source. Its monthly series under the revised survey framework begins in 2025; do not splice it seamlessly with older annual/quarterly PLFS estimates without a methodology-break flag. For now, unemployment remains pending until the monthly/annual source files and release dates are captured.

RBI DBIE Key Rates is the preferred source for Indian policy-rate events (repo, SDF, MSF, bank rate and CRR). Preserve its event/effective-date structure; create daily features by forward-filling only after each effective date, never backward.

No macro or market-context series has yet been downloaded by the committed scripts or merged into the modelling dataset.


## Official release-time and India labour/policy source confirmation (2026-11-13)

- MoSPI confirms CPI is disseminated at **16:00 IST on the 12th of the following month**, moving to the next working day if the 12th is a holiday. MoSPI also publishes an advance release calendar with precise scheduled dates. The CPI observation's reference month must never be treated as its availability date. Source: MoSPI FAQ and PIB release-time revision (5 Nov 2024).
- RBI DBIE's official **Key Rates** table provides repo, reverse repo, SDF, MSF, bank rate and CRR (among other columns), effective-date observations, and CSV/JSON downloads. The indexed table covers 1935-07-06 through 2026-10-07 (271 rows). Preserve the irregular event table as source data; only then derive a daily effective-rate panel by forward-fill from each effective date. RBI's own RTI responses direct users to DBIE → Statistics → Financial Sector → Key Rates → Major Monetary Policy Measures.
- MoSPI PLFS monthly bulletins under the revised methodology begin April 2025. The current advance calendar lists monthly bulletins through September 2026 and October 2026 scheduled for 15 November 2026. The methodology changed from January 2025; flag this break and do not splice earlier annual/quarterly PLFS measures as if definitionally identical.
- The committed FRED macro downloader passed a Python syntax compilation check in this session. Network execution has not been run here; dataset row counts remain unverified until the script is run on a connected machine.


## RBI policy rates and PLFS — source access audit (2026-11-13)

### RBI DBIE Key Rates
- The official DBIE Key Rates table is indexed as `financial_sector.r531_key_rates`; the public table page reports 271 effective-date rows spanning 1935-07-06 to 2026-10-07. Displayed variables include Fix Range LAF Rates, Bank Rate, Repo, Reverse Repo, SDF, MSF and CRR. The table page advertises CSV and JSON downloads.
- RBI's own RTI responses repeatedly direct users to DBIE → Statistics → Financial Sector → Key Rates → Major Monetary Policy Measures – Bank Rate, CRR & SLR for historical repo/bank-rate changes. This confirms DBIE as the authoritative source.
- Automated extraction is **not yet implemented**. The table page could not be opened through the research browser, and the public RBI Innovation Hub DBIE data mirror explicitly says Key Rates are among the datasets not included in its guest-accessible SDMX CSV collection (they sit behind SAP authentication in that mirror). Do not substitute the mirror or third-party mirrors without a separate validation step. Next step is to obtain the official DBIE CSV/JSON export through its UI or discover a documented public download route, then validate row count, dates and values before committing data.
- Model treatment: preserve the effective date and each rate-change event; create daily features by carrying values forward from the effective date only. Do not backfill earlier dates or use the date the dataset was downloaded as an availability timestamp.

### PLFS monthly labour indicators
- MoSPI's revised PLFS methodology began in January 2025. The monthly series reports all-India LFPR, WPR and unemployment rate (UR) under Current Weekly Status (CWS), including age, gender and rural/urban breakdowns. Monthly bulletins start with April 2025; the September 2026 bulletin is the eighteenth monthly bulletin in the series.
- MoSPI's e-Sankhyiki catalogue exposes PLFS monthly indicator entries with reference month, frequency, release date and table identifier. The official API contract is now identified from the NSO India's public eSankhyiki MCP repository: `GET https://api.mospi.gov.in/api/plfs/getData`. Monthly UR uses `frequency_code=3`, `indicator_code=3`; All India is `state_code=99`, Person is `gender_code=3`, age 15+ is `age_code=1`, and Rural+Urban combined is `sector_code=3`. Monthly year uses calendar `YYYY` and `month_code`; monthly data is documented from 2025 onward. Important: the API specification says `weekly_status_code` (including CWS) is only valid for annual data, not monthly/quarterly. Do not label monthly API records as CWS unless the returned metadata explicitly establishes that definition. The direct API Swagger specification declares bearer-token authentication. However, MoSPI also operates a public hosted MCP service at `https://mcp.mospi.gov.in/`, and its official portal FAQ says registration is not required for public e-Sankhyiki data. This MCP service wraps the API and exposes a documented sequence (`list_datasets` → `get_indicators` → `get_metadata` → `get_data`); it is the preferred no-token route to test before requesting credentials. The direct API and MCP calls have not yet been executed in this project, so no response data or row counts are claimed.
- Preserve the January 2025 methodology break. Do not splice pre-2025 annual/quarterly PLFS values into the post-2025 monthly CWS series as if they were directly comparable. Keep publication date separate from reference month and map each release to the next eligible NSE session.
- No PLFS or RBI policy-rate rows have been downloaded or merged into Northgate's market panel yet.


### Access-route correction (2026-11-13)
- The previous PLFS note overstated the authentication blocker by considering only the direct REST endpoint. MoSPI's public e-Sankhyiki portal says registration is not required for public datasets, and the official NSO India MCP repository documents the hosted service at `https://mcp.mospi.gov.in/` with a four-step data retrieval workflow. Test this public route before treating authentication as a blocker; direct REST Swagger still declares bearer-token security.
- The PLFS Swagger also clarifies that `weekly_status_code` (CWS) is not available for monthly/quarterly API frequencies. For monthly indicator 3, preserve the official indicator metadata and do not infer the exact status definition from the annual CWS filter.
- RBI's new DBIE domain is `https://data.rbi.org.in`; RBI confirms DBIE supports reusable downloads. The Key Rates table is official and downloadable, but no documented public machine API has been verified. UI export remains the reliable fallback.


## Official-source follow-up — PLFS, CPI release timing, India VIX and RBI (2026-11-13)

### PLFS: public MoSPI MCP route identified; monthly CWS assumption corrected
- NSO India's public `nso-india/esankhyiki-mcp` repository documents the hosted MoSPI MCP endpoint `https://mcp.mospi.gov.in/` and a sequential workflow: `list_datasets → get_indicators → get_metadata → get_data`. The README describes this as access to official open e-Sankhyiki data; the PIB announcement confirms the MCP pilot launch on 6 February 2026. This is a better first retrieval route than attempting the bearer-token REST endpoint directly. The live MCP calls have not yet been executed in this project.
- The official PLFS Swagger specification clarifies monthly filter codes: `frequency_code=3` means monthly (calendar years 2025 onward); `indicator_code=3` means unemployment rate; `state_code=99` All India; `gender_code=3` Person; `age_code=1` 15 years and above; `sector_code=3` Rural+Urban combined. Use `limit=50` or higher and paginate as needed.
- Important correction: the Swagger explicitly says `weekly_status_code` is available only for annual frequency (`frequency_code=1`), not quarterly or monthly. Therefore monthly PLFS unemployment must **not** be labelled CWS based on the API filters. Keep the monthly indicator's official definition/metadata from `get_indicators` and `get_metadata`; do not claim a CWS basis unless the retrieved metadata itself establishes it. Monthly UR, LFPR and WPR are the only monthly indicator set documented.
- Monthly PLFS starts in 2025 and has a January 2025 methodology break. Preserve the release date separately from the reference month. No PLFS observations have yet been retrieved or merged.

### CPI release timestamp: conflicting official references
- MoSPI's FAQ currently says CPI is released at 5:30 PM on the 12th (next working day if holiday). Recent CPI press releases carry a 4:00 PM embargo time, and the 2026-27 advance release calendar records scheduled dates that can differ from actual release dates. These sources are not fully consistent as a timestamp rule. Do not hard-code a universal 16:00 or 17:30 availability time. Prefer the actual timestamp/publication record for each archived release; where only a date is known, use a conservative next-session availability convention and mark the time as unknown.

### India VIX and RBI
- NSE provides an official Historical Data – India VIX page with date-range selection and CSV download. This should be the preferred source for the India VIX panel; the current yfinance downloader remains a fallback pending comparison against NSE. NSE also exposes historical index data and Total Returns Index values through its historical reports portal.
- RBI DBIE Key Rates remains the authoritative effective-date event table, with CSV/JSON downloads and 271 rows reported through 2026-10-07. Preserve effective-date events and derive daily rates only by forward-filling from each effective date; do not interpolate or backfill earlier sessions. No official file has yet been downloaded into the project.


## PLFS current-coverage correction — official MCP and latest bulletin (2026-11-13)
- The current public NSO India e-Sankhyiki MCP server source describes PLFS monthly API coverage as **April 2025–September 2026**, All India only, with indicators 1–3. It describes quarterly bulletin coverage through 2026 and says frequency_code=2 is quarterly, frequency_code=3 monthly. This is server/API coverage metadata, not proof that every monthly series has identical definitions or release dates.
- A newer official MoSPI Quarterly Bulletin for **July–September 2026**, published **10 November 2026**, is available. It presents LFPR, WPR, UR and worker distributions under Current Weekly Status (CWS), with rural, urban and combined estimates. The press note says April–June 2025 was the first quarterly bulletin to extend these estimates to both rural and urban India; pre-January-2025 quarterly bulletins covered urban areas only.
- Correction to earlier shorthand in project notes: do not describe the September 2026 PLFS publication as a “monthly bulletin”. It is the July–September 2026 **quarterly bulletin**. Monthly API observations and quarterly bulletin estimates are distinct products/frequencies and must be kept separately.
- The MCP source says frequency_code=3 monthly indicators 1–3 cover Apr 2025–Sep 2026; frequency_code=2 quarterly indicators 1–4 cover calendar years 2018–2026, but availability by quarter is uneven. Quarterly CWS results have a documented methodology/coverage change from April–June 2025 when rural estimates were added. Retain frequency, status concept, geography, publication date, and source release as separate fields.
- No PLFS rows have been retrieved through MCP yet. This is source/coverage verification only; actual retrieval and row-level QA remain pending.


## 2026-11-13 — PLFS release-calendar correction; NSE VIX and RBI export paths rechecked

### PLFS: monthly bulletins and quarterly bulletins are separate products
- The official MoSPI 2026–27 Advance Release Calendar (updated through October 2026) explicitly lists Monthly Bulletin of PLFS – September 2026, released 15 October 2026 (PIB PRID 2323828). Therefore the earlier wording that treated September 2026 only as the endpoint of monthly API coverage and described the July–September quarterly bulletin as the latest PLFS publication was incomplete.
- The same calendar separately lists the Quarterly Bulletin for July–September 2026, dated 10 November 2026, and the Monthly Bulletin of PLFS – October 2026, scheduled for 15 November 2026. As of this review (13 November 2026), October's monthly bulletin is scheduled but not yet due.
- Keep three distinct artefacts: (1) monthly PLFS API observations, (2) monthly PLFS bulletin/release PDFs, and (3) quarterly CWS bulletin tables. Do not infer one product's definitions or availability from another.
- The calendar documents that scheduled and actual release dates can differ. Store actual publication date from the linked PIB/MoSPI release separately from the advance scheduled date. It does not provide exact intraday release timestamps.

### India VIX: official interface confirmed, export requires date selection
- NSE's official Historical Data – India VIX page exposes date presets/custom range and a Download (.csv) control. Its unfiltered page may show No Records; this is not evidence that the historical archive is empty. Select a date range, submit/view the results, then download the CSV.
- NSE's Historical Reports navigation separately links Historical Data – India VIX, Historical Index Data, Total Returns Index Values, and daily/monthly index reports. Use official NSE downloads as the preferred VIX source; compare coverage and values with the existing yfinance fallback before replacing it.
- No VIX CSV has been downloaded into Northgate yet. Browser evidence establishes the official UI/export path only.

### RBI DBIE Key Rates: direct table and export controls re-confirmed
- Official RBI DBIE table financial_sector.r531_key_rates is indexed at https://dbie.rbihub.in/tables?table=financial_sector.r531_key_rates. It reports 271 rows, period 06-07-1935 to 07-10-2026, frequency As and When, and visible Download CSV / JSON controls.
- Fields include Effective Date, Fix Range LAF Rates, Bank Rate, Repo, Reverse Repo, SDF, MSF and CRR. This is an event-based table, not daily. Download CSV or JSON from the table controls; preserve effective date and original missing/change markers. Create daily session-aligned values only by forward-filling from the effective date, never backward or interpolated.
- The source is considered download-path identified / export ready, not downloaded. Remaining uncertainty concerns automated export, not whether an official export control exists.

### Company news / announcements: candidate data contract
- NSE corporate filings dashboard and public filing pages expose company filings/announcements. A third-party scraper description reports separate filing and dissemination timestamps, but this is not an official API specification and does not establish a free, supported bulk API.
- Treat exchange corporate announcements as a separate regulatory-disclosure/event stream, not a complete substitute for editorial financial news. Store exchange, symbol/ISIN, subject, summary, attachment URL, filing timestamp, dissemination timestamp, retrieval timestamp and source ID where actually available.
- Do not commit to third-party paid scraping. Continue investigating official NSE/BSE public access, licensing/terms and timestamp coverage. Apply FinBERT/VADER only after text eligibility and event-availability mapping are validated.
- No announcement corpus has been downloaded.

### Retrieval status
No new PLFS, VIX, RBI or news rows were downloaded in this research pass. These updates correct the source map and manual export procedure only.


## 2026-11-13 — PLFS CWS definition correction, 2027 survey transition, and NSE timestamp evidence

### Correction: monthly PLFS is explicitly CWS
- The official e-Sankhyiki catalogue lists September 2026 monthly PLFS LFPR, WPR and UR records. Each catalogue entry explicitly defines the monthly estimates as **Current Weekly Status (CWS)**, All India, disaggregated by gender, sector and broad age group, with release date 15 October 2026 and table IDs PLFSFY26001SEP / 002SEP / 003SEP.
- This supersedes the earlier caution in this inventory and older notes suggesting that the monthly series must not be labelled CWS. That caution arose because the MCP Swagger parameter `weekly_status_code` is annual-only; the monthly CWS definition is supplied by the official catalogue/product metadata and does not require passing that annual filter to the monthly API.
- Use the official catalogue as the semantic authority for monthly bulletin tables. Keep monthly frequency and CWS status explicitly recorded. For MCP data retrieval, call `get_metadata` for each single indicator code with `frequency_code=3`, then pass the returned `filter_values` to `get_data`; do not guess or pass annual-only `weekly_status_code` filters into monthly calls.
- The official e-Sankhyiki catalogue currently displays monthly September 2026 reference-period records and release date. The API implementation docs identify frequency_code=3 as monthly and indicators 1–3. Capture the actual metadata and returned data schema before designing the final raw table.

### New structural break / transition: January 2027 PLFS changes
- PIB's 23 October 2026 note announces proposed PLFS sampling-design and schedule changes from January 2027. It describes a new second-stage stratum for digital-platform workers; a refreshed sampling frame for Panel 6 (2027–28); refinements to allocation/stratification; and additional questions on digital platform work and unpaid activities.
- During the first three months from January 2027, the sample will combine FSUs from Panel 5 and updated Panel 6 frames. Monthly bulletins are expected to publish pooled estimates and omit RSE estimates for those three months.
- Treat January 2027 onward as a documented methodology/sample-frame transition. Store release version, panel/frame, and transition flag if available; do not blindly stitch the 2027 series to the 2025–26 series. The PIB item was an invitation for comments on proposed changes, so verify the final implementation note before treating every proposal as final.

### NSE announcements: stronger timestamp evidence
- NSE's official Corporate Filings Summary Documents page provides filters for company/symbol, subject and date range, CSV export, and a `BROADCAST DATE/TIME` field. Its rendered example shows 19-Sep-2026 14:47:29, plus an exchange dissemination time 14:47:34 and time taken 00:00:05.
- This is direct official evidence that at least this NSE filing product exposes broadcast and dissemination timestamps to second-level precision. It materially strengthens NSE corporate filings as a free/manual candidate event source. It is still necessary to test the main Corporate Announcements archive for historical date-range depth, category coverage, downloadable CSV fields and attachment retrieval. Do not assume the summary-documents page is a complete editorial news archive.
- Proposed raw fields: exchange, symbol, company, filing category, subject, attachment URL, broadcast timestamp, dissemination timestamp, time taken, submission type, exchange record ID, retrieval timestamp. Keep original timestamp strings and timezone assumption documented; verify timezone from NSE documentation or sample responses before normalizing.

### Source links
- e-Sankhyiki PLFS catalogue: https://esankhyiki.mospi.gov.in/catalogue-main/catalogue?page=1&product=PLFS
- Official NSO MCP implementation: https://github.com/nso-india/esankhyiki-mcp/blob/main/mospi_server.py
- PIB PLFS 2027 change note: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2327153&lang=1&reg=3
- NSE Corporate Filings Summary Documents: https://www.nseindia.com/companies-listing/corporate-filings-summary-documents

No raw PLFS API response, RBI export, VIX CSV or NSE filings CSV was downloaded in this pass. This is metadata/source-contract verification only.


## 2026-11-13 — MoSPI CPI API contract verified from user's terminal

The user retrieved the official OpenAPI YAML successfully (HTTP 200) from https://esankhyiki.mospi.gov.in/layout/swagger_user_cpi.yaml. This is the CPI API, not the PLFS API. Official e-Sankhyiki CPI page documents the same endpoint.

- Production endpoint: https://api.mospi.gov.in/api/cpi/getCPIData (GET); bearer token optional for guest access; rate-limited per IP.
- Base years 2010, 2012 and 2024. level=Group|Item is required for base 2010/2012; not used for 2024.
- Filters differ by base year/level. For 2024, filters include series, year, month, state, sector, division, group, class, subclass, item and imputation. Codes can be comma-separated but are not validated; discover valid values via getCpiFilterByLevelAndBaseYear first.
- Page numbering starts at 1; limit is 10–100. viz_req=true asks for the full filtered result. API responses use a JSON envelope with statusCode, msg, data and pagination metadata.
- The OpenAPI example shows 1,445,316 records / 144,532 pages for a broad 2024 request. This is an example, not retrieved project data. Never run unbounded requests.

The API spec does not document historical vintage/as-of queries. Its current response must not replace the existing point-in-time 2012-base vintage/event archive. Use the API for a current/expanded dataset only unless historical vintages can be independently obtained. No API observation pages have been downloaded or merged yet. Existing point-in-time workbook pipeline remains the reliable CPI backtest path.


### Additional official CPI 2024 methodological finding (MoSPI FAQ)
MoSPI's CPI 2024 FAQ states that the base-2024 back series for All-India Rural, Urban and Combined covers Jan 2013–Dec 2024 and is linked using the 2025 overlap between old (2012) and new (2024) series. The general-level linking factors listed are Rural 0.5222, Urban 0.5320 and Combined 0.5267; the FAQ defines the factor as the ratio of annual-average (geometric-mean) new-series CPI to old-series CPI for the overlap year. This creates a comparable historical index scale; it does not make those linked historical values contemporaneous release vintages. Do not use the back series as point-in-time investor information for 2013–2024. Preserve source series and vintage separately. MoSPI FAQ: https://mospi.gov.in/uploads/documents/documents/1770891066052-Annexure_V.pdf (questions 36–38, pp. 4–5).
