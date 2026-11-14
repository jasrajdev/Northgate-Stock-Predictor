"""Transparent BUY / HOLD / SELL engine (PRD section 12, DECISIONS.md 2026-11-12).

composite = w_f * forecast_signal + w_s * sentiment_signal - w_r * max(risk_signal, 0)

* forecast_signal: next-session forecast return divided by the stock's recent daily
  volatility, clipped to [-3, 3]; set to 0 if the forecast is smaller than round-trip cost.
  If `require_validated_edge` is true and the selected model did not beat the naive forecast
  on validation, the forecast weight is 0 (the forecast is still displayed).
* sentiment_signal: mean headline polarity over recent sessions in [-1, 1]; weight 0 when
  fewer than the minimum number of articles is available.
* risk_signal: cross-sectional z-score of recent volatility (positive = riskier); it can
  only reduce conviction, never create a SELL on its own.
Rules: BUY needs composite >= buy_threshold, a positive forecast/sentiment contribution and
room under the weight cap. SELL needs composite <= sell_threshold, a negative contribution and
a holding. REDUCE applies only when a holding exceeds the cap by more than the band.
Otherwise HOLD. A stock is never sold because another stock has a higher forecast.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd


@dataclass
class Decision:
    ticker: str
    action: str
    composite: float
    forecast_return: float | None
    forecast_signal: float
    sentiment_signal: float | None
    risk_signal: float
    weight: float
    reasons: list

    def row(self):
        d = asdict(self); d["reasons"] = " · ".join(self.reasons); return d


def decide(tickers, forecasts: dict, vol_daily: pd.Series, sentiment: dict, weights: pd.Series,
           cfg: dict, validated_edge: bool) -> list[Decision]:
    w_cfg = cfg["signal_weights"]; cost = 2 * cfg["transaction_cost_bps_one_way"] / 1e4
    use_forecast = validated_edge or not cfg["require_validated_edge"]
    vz = (vol_daily - vol_daily.median()) / (vol_daily.std(ddof=0) or 1)
    out = []
    for t in tickers:
        reasons = []
        f_ret = forecasts.get(t)
        if f_ret is None or not np.isfinite(f_ret):
            f_sig = 0.0; reasons.append("no forecast available")
        elif abs(f_ret) < cost:
            f_sig = 0.0; reasons.append(f"forecast {f_ret*100:+.2f}% is below round-trip cost {cost*100:.2f}%")
        else:
            f_sig = float(np.clip(f_ret / vol_daily[t], -3, 3)); reasons.append(f"forecast {f_ret*100:+.2f}% ({f_sig:+.2f} vol units)")
        if not use_forecast and f_ret is not None:
            reasons.append("forecast not used: model has no validated edge over the naive forecast")
        wf = w_cfg["forecast"] if use_forecast else 0.0
        s = sentiment.get(t)
        if s is None:
            ws, s_sig = 0.0, None; reasons.append("sentiment unavailable")
        else:
            ws, s_sig = w_cfg["sentiment"], float(s); reasons.append(f"sentiment {s_sig:+.2f}")
        r_sig = float(np.clip(vz.get(t, 0.0), -2, 2))
        if r_sig > 0.5:
            reasons.append(f"volatility above universe median ({r_sig:+.1f} sd)")
        drive = wf * f_sig + ws * (s_sig or 0.0)
        comp = drive - w_cfg["risk"] * max(r_sig, 0.0)
        wt = float(weights.get(t, 0.0))
        if wt > cfg["max_weight"] + cfg["rebalance_band"]:
            action = "REDUCE"; reasons.insert(0, f"weight {wt:.0%} exceeds the {cfg['max_weight']:.0%} cap")
        elif comp >= cfg["buy_threshold"] and drive > 0 and wt < cfg["max_weight"]:
            action = "BUY"
        elif comp <= cfg["sell_threshold"] and drive < 0 and wt > 0:
            action = "SELL"
        else:
            action = "HOLD"
        out.append(Decision(t, action, float(comp), f_ret, f_sig, s_sig, r_sig, wt, reasons))
    return out


def portfolio_action(decisions: list[Decision]) -> str:
    acts = [d.action for d in decisions if d.action != "HOLD"]
    return "No action recommended" if not acts else f"{len(acts)} action(s): " + ", ".join(f"{d.action} {d.ticker.replace('.NS','')}" for d in decisions if d.action != "HOLD")


def rebalance(current: pd.Series, target: pd.Series, band: float) -> pd.DataFrame:
    """PRD listing 12.1: act only where drift exceeds the band."""
    df = pd.DataFrame({"current": current, "target": target}).fillna(0.0)
    df["drift"] = df.target - df.current
    df["action"] = np.where(df.drift.abs() > band, np.where(df.drift > 0, "INCREASE", "DECREASE"), "within band")
    return df
