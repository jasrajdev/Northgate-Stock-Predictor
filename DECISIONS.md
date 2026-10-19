# Decisions Log

Record each important choice with date, decision, reason, alternatives, and whether reversible.

## 2026-10-19 — Project workflow
- Decision: use Mac + VS Code + GitHub as the main workflow; use free services when useful.
- Reason: minimize cost and keep code reproducible.
- Reversible: yes.

## 2026-10-19 — Evaluation standard
- Decision: chronological out-of-sample evaluation and simple baselines are mandatory.
- Reason: avoid look-ahead bias and measure whether complexity adds genuine value.
- Reversible: no, unless a documented research reason requires a change.

## 2026-10-19 — Scope boundary
- Decision: treat the system as research/decision support, not live trading or guaranteed-profit software.
- Reason: matches the PRD.
- Reversible: only as a separately approved extension.

## 2026-10-19 — Initial market focus
- Decision: begin research with Indian equities rather than US equities.
- Reason: the user wants the system to be relevant to their own market use.
- Status: market focus chosen; specific stocks, benchmark, target, horizon, and sources are not yet finalized.
- Reversible: yes, but any later change should be documented.

## 2026-10-19 — Research before data collection
- Decision: review relevant papers and source documentation before committing to the dataset and downloading the full history.
- Reason: avoid arbitrary feature selection and design choices.
- Initial research direction: investigate company-specific news, government/policy events, RBI/economic releases, global events, broader market news, and price/volume features. Treat these as candidate feature groups, not proven predictors.
- Reversible: yes.

## 2026-10-19 — News-analysis architecture hypothesis
- Idea: explore a research pipeline that classifies news by event/topic, affected company or sector, sentiment, and publication time; later test whether these features add value beyond price/volume and macro data.
- Important limitation: co-occurrence does not prove that a news item caused a price move. Start with a simple, testable pipeline rather than committing to a multi-agent system or training a language model from scratch.
- Status: hypothesis for research, not an implementation decision.
