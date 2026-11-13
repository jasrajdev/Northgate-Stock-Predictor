# CPI–Market Panel Merge Validation

**Run date:** 2026-11-13  
**Input:** User-provided `market_panel.csv`  
**CPI source:** MoSPI 2012-base monthly release-event table, July 2024–December 2025  
**Output artifact:** `/mnt/data/market_panel_with_cpi.csv` (local generated file; not committed)

## Method
A backward as-of join assigns each market row the most recent CPI release whose `next_nse_session` is on or before the market `Date`. CPI is not assigned on its publication date because all supplied release times are after the NSE cash-market close. The market input uses `Date` (capital D), so that column was used explicitly.

## Results

| Check | Result |
|---|---:|
| Input market rows | 29,484 |
| Output rows | 29,484 |
| Output columns | 22 |
| Instruments | 11 (10 equities + NIFTY 50) |
| Duplicate Date–Ticker keys | 0 |
| Rows with a matched CPI event | 6,115 |
| Rows before first available CPI event | 23,369 |
| Distinct CPI release months used | 18 |
| First CPI-eligible market date | 2024-08-13 |
| Latest market date | 2026-11-09 |
| Latest CPI reference month in source | 2025-12 |
| Maximum age of carried-forward CPI event | 300 calendar days |

All 18 event rows had the required fields populated, were 2012-base observations, and had unique next-session availability dates. Original market row count and order were preserved. Each date receives one consistent CPI vintage across instruments.

## Boundary checks
- 2024-08-12: July 2024 CPI is not yet available.
- 2024-08-13: July 2024 CPI becomes available.
- 2025-05-13: March 2025 CPI remains in force; April 2025 CPI is not yet available.
- 2025-05-14: April 2025 CPI becomes available.

All matched CPI availability sessions and actual release dates are on or before their market dates.

## Limitations and modelling implications
1. CPI event coverage starts only on 2024-08-13, leaving 2016–2024 market rows unmatched.
2. The event table ends with December 2025 CPI, first available 2026-01-13. The same value is carried forward to 2026-11-09, reaching 300 calendar days of age. This is stale and must not be presented as a current macro feed.
3. The 2024-base CPI series is not merged or spliced into this 2012-base series.
4. This joined panel is a data-engineering artifact, not a modelling dataset. Before training, choose whether to extend point-in-time historical CPI coverage, restrict the CPI experiment to a defensible date range, or use a documented missingness strategy.
5. The join logic was exercised and validated in the analysis environment. The repository pytest suite was not run, and no model or backtest was run.

## Reproducibility
The repository script is `scripts/merge_cpi_release_events.py`. Run it with `--date-column Date` for this market panel. Preserve the original market panel; do not overwrite it.
