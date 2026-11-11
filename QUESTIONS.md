# Open Questions

Only unresolved questions belong here. Do not treat a question or candidate option as a decision.

## Data
- Which 8–15 Indian equities and benchmark satisfy the PRD with reproducible selection rules?
- Which source provides the required historical OHLCV and corporate-action-adjusted prices with acceptable coverage, cost, and terms?
- Is point-in-time index membership available? If not, how will survivorship limitations be documented?
- Which macroeconomic series are required, and can their release dates/revisions be aligned correctly?

## Forecasting and evaluation
- What is the primary forecast target and horizon?
- What chronological train/validation/test periods and walk-forward folds will be used?
- How will overlapping forward labels be purged at split boundaries?
- What exactly constitutes a BUY recommendation and a successful trade?
- What signal time, entry/exit convention, holding horizon, transaction-cost assumptions, and capital/position constraints are appropriate?
- Should the earlier 70% profitable-BUY aspiration remain a secondary research objective, and if so, how should it be measured without replacing portfolio-level evaluation?

## News and event intelligence
- Which official company-announcement sources and licensed news APIs provide reliable coverage, timestamps, and historical access?
- What company/sector/competitor context is genuinely relevant to each announcement?
- How will duplicate reports, after-close publication, corrections, and already-known information be handled?
- Does news add measurable out-of-sample value beyond price/volume features?

## Delivery
- What can be completed to a correct standard by the recorded 15 November 2026 deadline?
- Which PRD requirements, if any, need an explicitly approved scope adjustment?
