# Northgate Stock Predictor

Northgate is an India-focused stock-market research project exploring how machine learning, market indicators and portfolio analysis can support more informed investment decisions.

The project brings together historical market-data processing, exploratory data analysis, financial calculations, model comparison, portfolio analytics and an interactive Streamlit dashboard.

## What the project includes

- **Market analysis:** historical price trends, technical indicators, returns, volatility and market context.
- **Exploratory data analysis:** stationarity, return distributions, correlation, volatility clustering and seasonality.
- **Forecasting research:** comparison of classical machine-learning and deep-learning model families against simple benchmarks.
- **Portfolio analytics:** portfolio optimisation, risk measures and historical strategy analysis.
- **Decision support:** transparent BUY / HOLD / SELL logic designed to allow a no-action decision.
- **Interactive dashboard:** seven sections covering the market overview, prices and predictions, recommendations, portfolio analytics, risk, sentiment and model comparison.
- **Research verification:** notebooks documenting the EDA and independent checks of financial calculations and gradient descent.

## Technology

Python, pandas, NumPy, scikit-learn, XGBoost, PyTorch, Streamlit, Plotly and Jupyter.

## Run locally

Create and activate a virtual environment, then install the project dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dashboard.txt -r requirements-dl.txt
```

Run the automated checks:

```bash
pytest
```

Launch the dashboard:

```bash
streamlit run dashboard/app.py
```

The data and trained model artefacts are not included in the repository. The research workflow and analysis are documented in the source code, notebooks and report.

## Project structure

- `src/northgate/` — features, models, financial calculations, portfolio and recommendation logic
- `dashboard/` — Streamlit application
- `scripts/` — data processing and model workflows
- `notebooks/` — exploratory analysis and financial-mathematics verification
- `tests/` — automated checks
- `config/` — project configuration
- `docs/RESEARCH_REPORT.md` — research methodology, results and interpretation

## Research report

See [the Northgate research report](docs/RESEARCH_REPORT.md) for the methodology, experiments, findings and interpretation.

## Disclaimer

Northgate is an educational research and decision-support project. It is not investment advice or an automated trading system. Historical analysis does not guarantee future performance.
