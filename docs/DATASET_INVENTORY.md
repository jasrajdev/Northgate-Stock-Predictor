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
