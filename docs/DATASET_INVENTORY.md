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
