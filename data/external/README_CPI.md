# MoSPI CPI 2012-base research data

## Files
- `cpi_mospi_2012_release_vintages_2024-07_to_2025-12.csv`: headline rural/urban/combined index and current-month provisional inflation extracted from 18 monthly release workbooks.
- `cpi_mospi_2012_historical_table_snapshots_2024-07_to_2025-12.csv`: historical All-India general CPI index and YoY inflation snapshots, preserving release vintage and provisional markers.
- `cpi_mospi_2012_release_availability_map_2024-07_to_2025-12.csv`: actual release date/time, source link and first eligible NSE session for each workbook.
- `cpi_mospi_2012base_point_in_time_vintages_part1_2024-11_to_2025-05.csv` and `...part2_2025-06_to_2025-12.csv`: timestamp-enriched historical snapshot rows split into two files for reliable repository storage. Concatenate rows (keep one header) to reconstruct the full 3,990-row point-in-time vintage table.
- `cpi_mospi_2012base_release_events_2024-07_to_2025-12.csv`: compact 18-row event table for the latest published monthly combined CPI index and YoY inflation. This is the intended input for a daily market-panel as-of join.

## Point-in-time rule
All listed releases in this sample were published after NSE's 15:30 cash-market close. Do not use a release on its publication date. Use it from `next_nse_session` onward. For a market-panel row dated (d), select the latest event with `next_nse_session <= d), using a backward as-of join. Never join on `reference_month` or month-end alone.

## Vintage and base-year handling
- Preserve `release_workbook_month`, `reference_month`, `vintage_status`, `provisional_marker`, raw source value, base year and source link.
- The historical snapshots contain 14 releases (November 2024–December 2025); the first four supplied 2024 workbooks do not include the cumulative time-series sheets.
- MoSPI changed annexure numbering. The historical CPI index and inflation tables were Annex-V/VI in some workbooks and Annex-VI/VII in later workbooks. Use title/content detection, not fixed sheet numbers.
- These files cover the CPI 2012=100 series only. Keep the 2024=100 series separate; do not backfill it into 2025 decision dates.

## Rebuild
Run `scripts/build_cpi_vintages.py` against the original monthly Excel workbooks and the release availability map. The script identifies historical tables by title and validates unique (release vintage, reference month, series) keys. The original workbooks are retained in the Project source files; keep them alongside this repository-derived data as source evidence.
