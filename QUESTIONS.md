# Open Questions

Only unresolved questions belong here. Do not treat a question or candidate option as a decision.

## Data and universe
- The PRD specifies 8–15 liquid large-cap equities plus a benchmark. Is this only the initial project research universe, or is the intended eventual prediction/coverage universe also limited to those tickers?
- Can a shared model trained on a set of companies generalise to additional, previously unseen Indian equities? What evidence and minimum history would be needed to support that claim?
- Should we test a broader historical training universe (potentially dozens or hundreds of equities) while separately defining the assets eligible for live-style predictions and portfolio selection?
- How will sector/category information be represented without assuming that two companies in the same sector must behave alike?
- Which 8–15 Indian equities and benchmark satisfy the PRD if its stated universe is retained for the baseline submission?
- Which source provides the required historical OHLCV and corporate-action-adjusted prices with acceptable coverage, cost, and terms?
- Is point-in-time index membership available? If not, how will survivorship limitations be documented?
- Which macroeconomic series are required, and can their release dates/revisions be aligned correctly?

## Forecasting and evaluation
- Multi-day forward-price horizons are not specified in the PRD. Which additional horizons should be implemented after the next-session dataset?
- What chronological train/validation/test periods and walk-forward folds will be used?
- How will overlapping forward labels be purged at split boundaries?
- What exactly constitutes a BUY recommendation and a successful trade?
- What signal time, entry/exit convention, holding horizon, transaction-cost assumptions, and capital/position constraints are appropriate?
- How should the system express uncertainty and decide to abstain when no asset clears the pre-defined action criteria?
- How should portfolio-level HOLD/no-trade be distinguished from an asset-level HOLD?
- What exit/rebalance rules prevent a higher forecast for another stock from automatically forcing a sale of a current holding?
- Should the earlier 70% profitable-BUY aspiration remain a secondary research objective, and if so, how should it be measured without replacing portfolio-level evaluation?

## News and event intelligence
- Which official company-announcement sources and licensed news APIs provide reliable coverage, timestamps, and historical access?
- What company/sector/competitor context is genuinely relevant to each announcement?
- How will duplicate reports, after-close publication, corrections, and already-known information be handled?
- Does news add measurable out-of-sample value beyond price/volume features?

## Delivery
- What can be completed to a correct standard by the recorded 15 November 2026 deadline?
- Which PRD requirements, if any, need an explicitly approved scope adjustment?


## MoSPI CPI API integration
- The portal OpenAPI fetched by the user documents /api/cpi/getCPIData, while the current official NSO India MCP server source maps CPI Group/Item retrieval to /api/cpi/getCPIIndex and /api/cpi/getItemIndex. Are these parallel/legacy API routes, or does the direct portal spec differ from the MCP server's bundled specification? Compare identical bounded filters and sample months before choosing the automated route.
- Does the direct CPI endpoint's status=F field mean final, or something else? Verify against the official data dictionary/release PDFs rather than infer from the label.
- Does the direct CPI API expose revisions or vintage snapshots? The currently reviewed specification does not document as-of retrieval; contemporaneous release-vintage records remain the safer backtest source.

## Data access rights and acquisition
- Can Northgate's research be submitted through an accredited academic institution under SEBI Circular SEBI/HO/DEPA-II/DEPA-II_SRG/P/CIR/2024/178? The circular's up-to-2-GB/researcher/year free access route is limited to research/research publications undertaken by accredited academic institutions; eligibility and exchange-specific request procedures need confirmation.
- What written permission/licence, if any, is required for persistent storage and backtesting/simulation using NSE-origin data, given NSE website terms restricting automated collection and simulation?
- If academic access is unavailable, which source can provide licensed OHLCV, VIX, sector indices and historical corporate disclosures within the zero/low budget?
- Does the user have an institutional supervisor/contact who can submit a research-data request and confirm the institution's accreditation?

### NSE academic data request
- Which institution should be named on the NSE Data Seeking Request Form, and can an academic supervisor/department support the application?
- What date range and exact fields should the request prioritize (daily EOD OHLCV, corporate actions, historical indices, VIX, company announcements, FII/DII activity)?
