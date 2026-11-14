# Implementation Roadmap

Task IDs refer to `REMAINING_TASKS.csv` (52 tasks: 22 P0, 17 P1, 7 P2, 6 P3). Effort figures are my estimates for one person who already knows the codebase, ±30 %, in working days (8 h). Gates are pass/fail conditions; do not start a phase before the previous gate passes (P2/P3 must not start while any P0 blocker remains open).

## Immediately doable, no approval, no external data
Nothing in the repository changes without approval, but these need no decision and no new data:
* T-007 build the NSE trading-calendar table (needs only public holiday pages).
* T-016 test scaffolding design, T-019 dependency pins, T-021 PRD traceability matrix (documents only).
* T-117 data-quality report design.

## Needs your approval only (code/doc/git changes)
T-001 (git pull), T-003 (doc corrections), T-004 (immutable snapshots), T-013/T-014/T-015 (feature and pipeline repair), T-017 (.gitignore), T-018 (repair CPI files), T-002 (rescue Kaggle files, needs your Kaggle access).

## Needs a decision first
D-15, D-02, D-03, D-04, D-05, D-06, D-17 → see `USER_DECISIONS_REQUIRED.md`.

## Needs external data, accounts or time
Manual NSE exports (T-010, T-011, T-012, T-101, T-102), RBI DBIE exports (T-103, T-104), FRED key (T-105), MoSPI PDFs (T-106), Google Cloud account (T-108), possible paid news (not recommended).

---

## Phase 0: Secure what exists (≈ 1 day)
T-001, T-002, T-003, T-017.
**Gate 0:** local repo equals GitHub; Kaggle outputs and the notebook's code are in Git or their loss is recorded; `git status` shows no data files; documents corrected.

## Phase 1: Make the data trustworthy (≈ 6–8 days)
T-004, T-005 (after D-04), T-007, T-008/T-009 (after D-05/D-06), T-010, T-011, T-012 (after D-14), T-018, T-117.
**Gate 1:** hashed immutable snapshot with manifest; calendar table; every panel row is a calendar session or documented exclusion; the 19 bad rows resolved; ledger complete and primary-sourced; ≥ 99.9 % of rows within 0.05 % of official after factors, exceptions listed; CPI CSVs readable.

## Phase 2: Make the pipeline reproducible and leak-proof (≈ 4–5 days)
T-013, T-014, T-015, T-016, T-019, T-020 (after D-17), T-006 (after D-02/D-03), T-021.
**Gate 2:** one command rebuilds `data/processed/<version>/` from the raw snapshot, bit-identically twice; pytest from a clean clone passes, including a test that deliberately injected look-ahead fails; evaluation protocol committed *before* Experiment 02.

## Phase 3: Complete the PRD dataset (≈ 8–10 days, partly parallel)
Context block: T-101, T-102, T-103, T-104, T-105, T-107. CPI: T-106 (after D-10). News: T-108 → go/no-go → T-109, T-110, T-111 (after D-11/D-12). Universe: T-112 (D-07). Features/labels: T-113, T-114 (D-13). EDA/maths: T-115, T-116.
**Gate 3:** every external series passes the join test (no value before its availability time); news table schema-validated with first-available session; feature dictionary in the repo; EDA notebook has the six PRD analyses on training data only.

## Phase 4: Experiments (≈ 8–9 days)
T-201 → T-202 → T-203 → T-204 → T-205 → T-207, then T-206.
**Gate 4a (before T-206):** model, features and hyper-parameters frozen in a tagged commit; written sign-off.
**Gate 4b:** the single test run is reported in full regardless of outcome. Expected honest outcomes include "no model beats the naive predictor"; that is an acceptable PRD outcome if reported.

## Phase 5: Decision-support product (≈ 7–8 days)
T-301 → T-302 → T-303 → T-304 → T-305 → T-306.
**Gate 5:** backtest on identical dates for optimised, equal-weight and TRI-benchmark portfolios with costs; dashboard imports no training code; report 10–15 pages; fresh-clone rebuild succeeds.

## Critical path and parallelism
Decisions D-02/D-03/D-04/D-05/D-06 → T-005/T-008/T-009 → T-014 → T-201. Everything in Phase 3 except T-114 can run in parallel with Phase 2 once Gate 1 passes. News (T-108) is the longest-lead uncertainty: start the pilot early, because a "no-go" changes the report scope.

## Totals (estimates)
| Phase | Working days |
|---|---|
| 0 | 1 |
| 1 | 6–8 |
| 2 | 4–5 |
| 3 | 8–10 |
| 4 | 8–9 |
| 5 | 7–8 |
| **Total** | **≈ 34–41** (≈ 7–8 calendar weeks), more if news is paid or manual exports are slower than assumed |

## Recommended first task
**T-001 + T-003 + T-017 (Phase 0, about half a day)**: sync the clone, correct the four inaccurate statements and ignore data files. They are low-risk, unblock every later task, and prevent accidental publication of vendor data. The first *data* task is then T-007 (calendar), because the bad-row, special-session and label decisions all depend on it.
