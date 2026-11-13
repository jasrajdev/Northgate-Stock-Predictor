

## Follow-up verification of official NSE archives — 2026-11-14

### Security-wise archive: actual page evidence
The current NSE Security-wise Archives page explicitly states that a company symbol is mandatory for multi-day retrieval, offers 1D/1W/1M/3M/6M/1Y/5Y/Custom filters and CSV export, and lists OHLC, VWAP, traded quantity, turnover, trade count, deliverable quantity and delivery percentage. The inspected live snapshot had no rows because no symbol was selected. It therefore confirms the interface and schema labels, not any target-stock date coverage or a 2016–2026 export. Do not claim ten-stock coverage until each ticker is checked in the UI.

### Corporate-action coverage sample
The NSE Corporate Actions search result for ITC exposes 20 records, including a 2016 bonus, dividends back to 2015, and the ITC demerger with ex-date 06-Jan-2025. This is direct evidence that at least one target ticker's UI history reaches earlier than the recent 1Y presets. It does not establish complete history for the other nine tickers. The page provides ex-date/record-date/book-closure fields, not the original announcement timestamp. The ITC result is useful for event-window validation; announcement-time/news alignment still requires the exchange filing/dissemination timestamp.

### NIFTY 50 total-return benchmark
NSE Indices' official NIFTY 50 whitepaper states that NIFTY 50 TR values are available from 30-Jun-1999 and that TR assumes dividends are reinvested. The official historical-data UI separately exposes Total Returns Index and Net Total Return Index values with date-range selection and CSV. This is enough to establish that an official NIFTY 50 TR history exists with ample nominal coverage for Northgate's 2016 onward window. Actual CSV retrieval, current end date, exact daily completeness and licence/usage terms remain unverified. Keep price-return ^NSEI and total-return TRI distinct; for a portfolio benchmark that includes reinvested dividends, TRI is the economically consistent comparison.

### India VIX history
NSE's 2010-07-19 press release says real-time India VIX dissemination began on that date. This establishes a plausible inception before the 2016 Northgate start date. The current historical UI offers Custom and CSV, but no historical rows or download were obtained; exact daily archive coverage remains unverified. India VIX measures expected volatility over the next 30 calendar days and is based on NIFTY option prices, so it is a market-risk feature, not a realised-volatility measure.

### FII/FPI and DII: provisional-data warning confirmed
The NSE page displays separate CSVs for NSE-only and combined NSE+BSE+MSEI activity, with category/date/buy/sell/net values. Its own note explicitly says FII/FPI data is provisional and subject to change, including custodial confirmation and modifications; it points to NSDL/CDSL for final FPI data. The sample is aggregate daily category flow, not company-specific. If used, preserve source type and provisional/final status, and do not silently overwrite a historical provisional value with a later final value without retaining vintage timestamps.

### UDiFF transition and archive
The All Reports page confirms the current CM-UDiFF Common Bhavcopy Final ZIP and states that legacy CM Bhavcopy CSV and CM Common Bhavcopy CSV were discontinued effective 08-Jul-2024. It also lists security-wise delivery positions and full Bhavcopy/security-deliverable reports. A current dated UDiFF filename is visible, but the full historic daily archive range and field-level mapping to the legacy schema remain unverified. Treat the 08-Jul-2024 format transition as a potential data-schema break that needs a documented mapping and overlap/cross-check if both sides are combined.

### Access boundary
These checks used publicly rendered NSE/NSE Indices pages and search-indexed official content. No data file was downloaded, no protected endpoint was called, and no scripted collection was performed. UI visibility does not itself grant bulk-retrieval or automated-scraping rights. Continue with manual UI checks or the formal NSE research-data route until terms/permissions are confirmed.

Sources:
- NSE Security-wise Archives: https://www.nseindia.com/report-detail/eq_security
- NSE ITC Corporate Actions result: https://www.nseindia.com/companies-listing/corporate-filings-actions?symbol=ITC
- NSE FII/FPI & DII: https://www.nseindia.com/reports/fii-dii
- NSE All Reports: https://www.nseindia.com/all-reports
- NSE India VIX launch release (19-Jul-2010): https://nsearchives.nseindia.com/content/press/19072010.htm
- NSE India VIX methodology overview: https://www.nseindia.com/static/products-services/indices-indiavix-index
- NIFTY Indices historical data: https://www.niftyindices.com/reports/historical-data
- NIFTY 50 whitepaper 2024: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/nifty-50-whitepaper-2024_0.pdf
- NSE Total Returns Index explanation: https://www.nseindia.com/static/products-services/indices-total-returns-index
