# Decisions Log

Record only decisions explicitly agreed by the user or required by the project brief. Keep unapproved options out of this log.

## 2026-10-19 — Project workflow
- Decision: use Mac, VS Code, Python, and GitHub as the main development workflow.
- Reason: keep the project reproducible and minimise cost.
- Reversible: yes.

## 2026-10-19 — Evaluation standard
- Decision: chronological out-of-sample evaluation and simple baselines are mandatory.
- Reason: prevent look-ahead bias and test whether complexity adds genuine value.
- Reversible: only with a documented methodological reason.

## 2026-10-19 — Project boundary
- Decision: build a research/decision-support system, not live brokerage execution software.
- Reason: matches the stated project scope.
- Reversible: only as a separately approved extension.

## 2026-10-19 — Initial market focus
- Decision: begin with Indian equities.
- Reason: the system should be relevant to the user's market context.
- Status: confirmed. Specific stocks, benchmark, target, horizon, and data sources remain open.
- Reversible: yes, with a documented reason.

## 2026-10-19 — Research before bulk collection
- Decision: review relevant research and verify data-source feasibility before downloading the full history or training models.
- Reason: avoid committing to unreliable sources or arbitrary modelling choices.
- Status: confirmed process decision.

## Not decisions
The following have appeared in earlier planning notes but are not confirmed design decisions:
- A fixed five-session holding period or mandatory day-five exit.
- A fixed take-profit, stop-loss, or return threshold (including 5% or 10%).
- A fixed BUY score/probability threshold.
- A fixed weighting for news versus price/volume signals.
- A final news API provider, Make workflow, deployment host, or model architecture.
- Expanding beyond the PRD's 8–15 equities.
- Omitting any of the PRD's required model comparisons.

The earlier 70% profitable-BUY figure is an aspiration discussed by the user, not a proven result and not a PRD acceptance criterion. Confirm whether it remains a secondary research objective before using it to define experiments.
