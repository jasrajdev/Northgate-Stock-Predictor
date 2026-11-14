"""Visual language for the dashboard: paper background, ink text, one restrained palette.

Palette validated for colour-vision separation and contrast on the page background
(dataviz validator, light mode): blue, burnt orange, violet, green, in fixed order.
"""
import plotly.graph_objects as go

PAPER, PANEL, INK, MUTED, RULE, GRID = "#FAF8F4", "#F1EDE4", "#1C1B19", "#6B665C", "#1C1B19", "#E4DFD5"
BLUE, ORANGE, VIOLET, GREEN = "#2B6CB0", "#C2571A", "#7B4FA6", "#2F8F6B"
SERIES = [BLUE, ORANGE, VIOLET, GREEN]
NEUTRAL = "#8C867A"
DIVERGING = [[0.0, BLUE], [0.5, "#EDE9E0"], [1.0, ORANGE]]
SEQUENTIAL = [[0.0, "#E9EEF4"], [1.0, "#1F4E86"]]
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
SERIF = "'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif"

CSS = f"""
<style>
.block-container {{ padding-top: 3.4rem; max-width: 1180px; }}
h1, h2, h3 {{ font-family: {SERIF}; font-weight: 600; letter-spacing: -0.01em; color: {INK}; }}
h1 {{ font-size: 2.0rem; border-top: 3px solid {RULE}; padding-top: .7rem; margin-bottom: .1rem; }}
h3 {{ font-size: 1.08rem; border-bottom: 1px solid {RULE}; padding-bottom: .25rem; margin-top: 1.6rem; }}
.ng-kicker {{ font-family: {MONO}; font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: {MUTED}; }}
.ng-lede {{ font-size: 1.02rem; color: #3A3832; max-width: 62rem; margin: .2rem 0 1.1rem 0; }}
.ng-tag {{ display: inline-block; font-family: {MONO}; font-size: .68rem; letter-spacing: .1em; text-transform: uppercase;
          border: 1px solid {INK}; padding: .08rem .45rem; margin-right: .4rem; color: {INK}; background: transparent; }}
.ng-tag.off {{ border-style: dashed; color: {MUTED}; border-color: {MUTED}; }}
.ng-figs {{ display: flex; flex-wrap: wrap; border-top: 1px solid {RULE}; border-bottom: 1px solid {RULE}; margin: .6rem 0 1rem 0; }}
.ng-fig {{ flex: 1 1 150px; padding: .7rem .9rem .6rem 0; margin-right: .9rem; border-right: 1px solid {GRID}; }}
.ng-fig:last-child {{ border-right: 0; }}
.ng-fig .v {{ font-family: {MONO}; font-size: 1.45rem; font-variant-numeric: tabular-nums; color: {INK}; line-height: 1.15; }}
.ng-fig .l {{ font-family: {MONO}; font-size: .66rem; letter-spacing: .1em; text-transform: uppercase; color: {MUTED}; }}
.ng-fig .s {{ font-size: .8rem; color: {MUTED}; }}
.ng-note {{ border-left: 3px solid {INK}; background: {PANEL}; padding: .7rem 1rem; margin: .8rem 0; font-size: .95rem; }}
.ng-note b {{ font-family: {MONO}; font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; }}
.ng-foot {{ font-family: {MONO}; font-size: .68rem; color: {MUTED}; border-top: 1px solid {GRID}; margin-top: 2.5rem; padding-top: .6rem; }}
[data-testid="stSidebar"] {{ border-right: 1px solid {RULE}; }}
[data-testid="stSidebar"] label p {{ font-size: .95rem; }}
[data-testid="stDataFrame"] * {{ font-variant-numeric: tabular-nums; }}
</style>
"""


def style(fig: go.Figure, height: int = 360, y_title: str | None = None, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height, paper_bgcolor=PAPER, plot_bgcolor=PAPER, margin=dict(l=8, r=16, t=34 if legend else 12, b=8),
        font=dict(family="Georgia, serif", size=13, color=INK), hovermode="x unified", showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=PAPER, bordercolor=INK, font=dict(family="Menlo, monospace", size=12, color=INK)),
    )
    axis = dict(showgrid=True, gridcolor=GRID, gridwidth=1, zeroline=False, linecolor=NEUTRAL, ticks="outside",
                tickcolor=NEUTRAL, ticklen=4, tickfont=dict(family="Menlo, monospace", size=11, color=MUTED))
    fig.update_xaxes(**{**axis, "showgrid": False})
    fig.update_yaxes(**axis, title=dict(text=y_title or "", font=dict(size=12, color=MUTED)))
    return fig


def figures(items) -> str:
    """items: (label, value, sub) tuples -> HTML strip of headline figures."""
    cells = "".join(f'<div class="ng-fig"><div class="l">{l}</div><div class="v">{v}</div><div class="s">{s}</div></div>' for l, v, s in items)
    return f'<div class="ng-figs">{cells}</div>'


def tag(text: str, off: bool = False) -> str:
    return f'<span class="ng-tag{" off" if off else ""}">{text}</span>'
