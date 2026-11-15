# Post-Submission Backlog

Outstanding work after the 15 November 2026 submission. Priority: P1 = needed for full PRD acceptance; P2 = strengthens the research; P3 = extension. Detailed task history: `reports/claude_dataset_audit_2026-11-14/REMAINING_TASKS.csv`.

| # | Item | Why it is outstanding | Priority | Depends on |
|---|---|---|---|---|
| 1 | Freeze the evaluation protocol (absolute split dates, metrics, direction convention) and run the single held-out test evaluation of the selected model and portfolio | PRD §14 acceptance is defined on a held-out window; only validation results exist | P1 | Owner decisions D-04, D-17; items 2–3 if they change the data |
| 2 | Repair data defects: 10 phantom rows (15 Jan 2026), 9 stale rows (18 Mar 2025), missing special sessions; flag the ITC and HUL demerger labels | Distort labels and features | P1 | Owner decisions D-05, D-06, D-03; official NSE files |
| 3 | Remove the adjusted-close *level* from model inputs and retrain all eight models on one pipeline | Level is restated by later dividends; deep checkpoints currently use a different 32-input set | P1 | Item 2 |
| 4 | Retrain the four deep models on the 25-input pipeline (or a revised one) so they can be deployed | Installed Kaggle checkpoints expect 32 inputs and are refused by the loader | P1 | Item 3; GPU session |
| 5 | Hyper-parameter tuning with expanding-window CV, several seeds, and bootstrap / Diebold-Mariano intervals | PRD asks for tuned models; current differences are untested | P1 | Item 3 |
| 6 | Historical timestamped news and the with/without-sentiment experiment | PRD §10; free GDELT API returned no data and only covers a recent window | P1 | Data access (GDELT BigQuery pilot or a licensed source); owner decision D-11 |
| 7 | NIFTY 50 Total Returns Index as the portfolio benchmark | Price index excludes dividends and flatters the portfolios | P2 | Manual NSE Indices export |
| 8 | Point-in-time macro features (repo-rate events, CPI release history back to 2015, lagged US series) and an ablation | Macro series are displayed but not modelled | P2 | Owner decisions D-09, D-10 |
| 9 | Multi-day forecast horizons with purge/embargo | PRD asks for multi-day forecasts; horizons not chosen | P2 | Owner decision D-13 |
| 10 | Approve the risk-free rate, transaction costs and recommendation thresholds in `config/recommendation.json` | Currently documented assumptions | P2 | Owner decision D-18 |
| 11 | Survivorship-aware universe statement or point-in-time membership | Universe is ten stocks chosen in 2026 | P3 | Owner decision D-07 |
| 12 | Fresh-machine end-to-end rebuild test (one command) | Individual steps verified; full rebuild on a clean machine not yet run | P2 | None |
