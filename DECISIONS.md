# Decisions Log

Record only decisions explicitly agreed by the user or required by the project brief. Keep unapproved options out of this log.

## 2026-11-12 — Recommendation system must allow no action

- Decision: Northgate must not force a BUY, SELL, portfolio rotation, or other trade every day. It must be valid for the system to recommend no new trade across the entire portfolio on a given day.
- Decision: recommendations must follow pre-defined, consistently applied criteria. Do not weaken thresholds or manufacture a trade merely because another asset has a more attractive forecast.
- Decision: a holding should not be sold solely because another stock has a higher predicted return; any sale/rebalance must satisfy the agreed exit, risk, allocation-drift, or other explicit rule.
- Decision: preserve the PRD's benchmark and baseline comparisons; do not change them opportunistically to make results look better.
- Reason: avoiding unnecessary turnover and preserving honest, risk-aware decisions matter more than producing a daily action.
- Scope: this clarifies the recommendation layer; it does not yet define numerical thresholds, holding periods, confidence cut-offs, or exit rules.

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
- Reversible: yes.

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
- Expanding beyond the PRD's 8–15 equities or choosing a final train-vs-prediction universe.
- Omitting any of the PRD's required model comparisons.

The earlier 70% profitable-BUY figure is an aspiration discussed by the user, not a proven result and not a PRD acceptance criterion. Confirm whether it remains a secondary research objective before using it to define experiments.
