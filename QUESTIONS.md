# Open Questions

Resolve these through research or implementation; record answers and sources here.

## First phase: price/volume baseline
- Which Indian equities and benchmark should we use, and what reproducible rule selects them?
- Which source provides enough historical daily OHLCV and corporate-action-adjusted prices at acceptable cost and with clear terms?
- What primary target and horizon will we predict: next-session return, direction, or volatility?
- What chronological train/validation/test periods and simple baselines should we use?
- How do we account for survivorship bias (only studying companies that survived or are prominent today)?

## Later phase: macro/news/events
- Which reliable, free source will provide Indian macroeconomic series and timestamped financial news?
- Which event/topic categories add useful information beyond price/volume?
- How will publication time, after-market news, revised economic data, duplicate stories, and historical availability be handled to avoid look-ahead bias?
- Can news be collected at sufficient historical depth and with trustworthy timestamps under free source terms?

## Portfolio evaluation and implementation
- What realistic transaction-cost and slippage assumptions can be documented?
- Which local Python/deep-learning setup is practical on the available Mac, and when should Colab be used?
- What are the exact acceptance criteria and final deliverables in the original PRD?
