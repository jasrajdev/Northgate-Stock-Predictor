

## Follow-up official archive checks — 2026-11-14

- **NIFTY 50 TRI:** Official NSE Indices whitepaper says daily TR values are available from 30-Jun-1999; the official UI provides TR and Net TR date-range CSV. This covers the 2016-onward project window in principle. No CSV acquired; current endpoint date and completeness remain untested. Candidate portfolio benchmark should be TRI rather than price-only ^NSEI if the comparison includes dividend-reinvesting holdings.
- **India VIX:** NSE says dissemination began 19-Jul-2010, before the project's 2016 start. Historical UI offers Custom/CSV, but no daily archive export acquired or coverage validated.
- **ITC corporate actions:** Official NSE symbol-filtered result shows 20 records including bonus/dividend actions back to 2015 and ITC demerger ex-date 06-Jan-2025. This validates the UI for one ticker only; do not generalise to the other nine.
- **FII/FPI/DII:** NSE explicitly labels FII/FPI activity provisional and revisable; data is aggregate market flow, not stock-specific. Preserve publication/vintage status if used; final FPI data is directed to NSDL/CDSL.
- **CM UDiFF:** Current ZIP format is the successor to legacy CM Bhavcopy CSV formats discontinued 08-Jul-2024. The format transition needs schema mapping; full archive coverage and delivery-file alignment remain open.
- **No files downloaded or ingested.** These are official-source coverage clues, not acquired data.
