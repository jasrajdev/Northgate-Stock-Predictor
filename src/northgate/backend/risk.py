"""Historical risk statistics computed directly from the price panel.

All figures are descriptive statistics of past adjusted-close returns. They are not
forecasts, model results or backtests.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import market

TRADING_DAYS = 252


def returns_wide(start=None, end=None) -> pd.DataFrame:
    """Daily simple returns of Adj Close, one column per instrument."""
    p = market.load_panel()
    wide = p.pivot(index="Date", columns="Ticker", values="Adj Close").sort_index()
    r = wide.pct_change(fill_method=None)
    if start is not None:
        r = r[r.index >= pd.Timestamp(start)]
    if end is not None:
        r = r[r.index <= pd.Timestamp(end)]
    return r


def drawdown(series: pd.Series) -> pd.Series:
    level = (1 + series.fillna(0)).cumprod()
    return level / level.cummax() - 1


def summary(start=None, end=None) -> pd.DataFrame:
    r = returns_wide(start, end)
    bench = r[market.BENCHMARK]
    rows = []
    for t in r.columns:
        x = r[t].dropna()
        if len(x) < 30:
            continue
        both = pd.concat([x, bench], axis=1, join="inner").dropna()
        beta = np.nan if t == market.BENCHMARK else both.iloc[:, 0].cov(both.iloc[:, 1]) / both.iloc[:, 1].var()
        years = len(x) / TRADING_DAYS
        rows.append({
            "Ticker": t,
            "Sessions": len(x),
            "Annualised return": (1 + x).prod() ** (1 / years) - 1,
            "Annualised volatility": x.std() * np.sqrt(TRADING_DAYS),
            "Maximum drawdown": drawdown(x).min(),
            "1-day VaR 95% (historical)": x.quantile(0.05),
            "Worst day": x.min(),
            "Beta vs NIFTY 50": beta,
        })
    return pd.DataFrame(rows).set_index("Ticker")


def rolling_volatility(ticker: str, window: int = 20) -> pd.Series:
    return returns_wide()[ticker].rolling(window, min_periods=window).std() * np.sqrt(TRADING_DAYS)


def correlation(start=None, end=None) -> pd.DataFrame:
    r = returns_wide(start, end).drop(columns=[market.BENCHMARK])
    return r.corr()
