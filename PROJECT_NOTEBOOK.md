

## Follow-up on official market-data coverage (2026-11-14)

- NSE Indices' official NIFTY 50 whitepaper states NIFTY 50 Total Return values are available from 30-Jun-1999. The historical UI exposes both TR and Net TR with date-range CSV. Since a total-return benchmark includes reinvested dividends, it is the stronger candidate for portfolio-performance comparison than the current price-only ^NSEI series. Do not replace the existing benchmark until the CSV, definition, availability and terms are checked.
- NSE's 19-Jul-2010 press release establishes India VIX dissemination before Northgate's 2016 start. The historical page exposes Custom/CSV, but daily coverage has not been downloaded or verified. India VIX is implied expected volatility over the next 30 calendar days, not realised volatility.
- An official NSE ITC Corporate Actions result contains 20 records reaching 2015, including a bonus and dividends, plus the 06-Jan-2025 demerger. This is useful evidence for one ticker only. Ex-date is not the announcement publication time; retain filing/dissemination timestamps for point-in-time event features.
- NSE labels FII/FPI flow as provisional and subject to custodial confirmation/modification. The report is aggregate category-level flow, not stock-level activity. Historical vintages should not be overwritten if the series becomes a feature.
- NSE discontinued legacy CM Bhavcopy CSV formats effective 08-Jul-2024 and directs users to CM-UDiFF Common Bhavcopy Final ZIP. Any stitched history must document schema transition and validate comparable fields across the boundary.
- No official files were downloaded; no additional data was ingested or validated. The model-training and backtesting state is unchanged.
