#!/usr/bin/env python3
"""Three charts for /market, computed from the historical_data store itself.

Nothing here is drawn from a claim; every number is recomputed from the parquet at
render time and written to assets/charts/charts.json so the page's captions quote
what THIS run measured, not what the notebook remembers.

  1. store.png    — symbols with data, per year (the ground-truth store)
  2. gap.png      — the confirmation gap that killed the breakout book, recomputed
                    with the repo's own Camarilla formula (H4 = C + range*1.1/2)
  3. regimes.png  — equal-weight index of the whole universe, 2021 to date,
                    split at the regime boundary the notebook quotes

Style matches the site's plates: near-black ground, mono labels, the kill red and
the live green doing the talking.
"""
import glob
import json
import os
import pathlib
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd

STORE = pathlib.Path(os.path.expanduser("~/Desktop/historical_data/data/daily_clean"))
OUT = pathlib.Path(__file__).parent / "assets/charts"
OUT.mkdir(parents=True, exist_ok=True)

# ---- plate style ------------------------------------------------------------
BG, GRID, INK, DIM = "#07090c", "#1d2127", "#e9e7e4", "#8b9098"
KILL, LIVE, AMBER = "#e0705f", "#2f9e83", "#f2b45c"

mono = next((f.name for f in font_manager.fontManager.ttflist
             if "IBM Plex Mono" in f.name), None) or \
       next((n for n in ("Menlo", "DejaVu Sans Mono")
             for f in font_manager.fontManager.ttflist if f.name == n), "monospace")
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "font.family": mono, "text.color": INK, "axes.edgecolor": GRID,
    "axes.labelcolor": DIM, "xtick.color": DIM, "ytick.color": DIM,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": .6,
    "axes.spines.top": False, "axes.spines.right": False,
})


def frame(w=13.5, h=7.2):
    fig, ax = plt.subplots(figsize=(w, h), dpi=160)
    fig.subplots_adjust(left=.07, right=.97, top=.9, bottom=.1)
    return fig, ax


def save(fig, name):
    p = OUT / name
    fig.savefig(p)
    plt.close(fig)
    print(f"  {name:14} {p.stat().st_size // 1024:>4} KB")


stats = {}

# ---- load the store once, deduplicated per symbol ---------------------------
print("reading daily_clean ...")
def load_symbol(sdir):
    # Store schema: ts at a constant 18:30 UTC, so the UTC calendar date IS the
    # trading date (verified: 249 sessions in 2024, zero duplicates).
    fs = glob.glob(str(sdir / "year=*/*.parquet"))
    if not fs:
        return None
    df = pd.concat([pd.read_parquet(f, columns=["ts", "open", "high", "low", "close"])
                    for f in fs], ignore_index=True)
    df["date"] = pd.to_datetime(df["ts"], utc=True).dt.tz_localize(None).dt.normalize()
    df = df.drop(columns=["ts"])
    return (df.drop_duplicates("date", keep="last")
              .sort_values("date").reset_index(drop=True))

symbols = sorted(d for d in STORE.iterdir() if d.name.startswith("symbol="))
data = {}
for sdir in symbols:
    df = load_symbol(sdir)
    if df is not None and len(df):
        data[sdir.name.split("=", 1)[1]] = df
rows = sum(len(d) for d in data.values())
print(f"  {len(data)} symbols, {rows:,} deduplicated rows")
stats["symbols"] = len(data)
stats["rows"] = rows

# ============================ 1. the store ===================================
per_year = {}
for df in data.values():
    for y in df["date"].dt.year.unique():
        per_year[int(y)] = per_year.get(int(y), 0) + 1
years = sorted(y for y in per_year if 2000 <= y <= 2026)
counts = [per_year[y] for y in years]
stats["store_first_year"] = years[0]
stats["store_peak"] = max(counts)

fig, ax = frame()
ax.bar(years, counts, width=.72, color="#3a4048", edgecolor="none", zorder=2)
ax.bar([y for y, c in zip(years, counts) if c < max(counts) * .2],
       [c for c in counts if c < max(counts) * .2],
       width=.72, color=KILL, edgecolor="none", zorder=3)
ax.axhline(max(counts) * .2, color=KILL, lw=.9, ls=(0, (4, 4)), zorder=1)
ax.text(years[0] - .4, max(counts) * .2, "20% of peak ", color=KILL,
        va="bottom", ha="left", fontsize=9)
ax.set_title("SYMBOLS WITH DATA, BY YEAR", loc="left", fontsize=11,
             color=INK, pad=14)
ax.set_xticks(range(2000, 2027, 2))
ax.margins(x=.01)
save(fig, "store.png")

# ============================ 2. the gap =====================================
# cam_daily_long, by the repo's own formula: H4 = prev_close + (prev_h - prev_l)*1.1/2
# a confirmation day is close > H4; the gap is how far past the level that close is.
gaps = []
for df in data.values():
    if len(df) < 30:
        continue
    h4 = df["close"].shift(1) + (df["high"].shift(1) - df["low"].shift(1)) * 1.1 / 2
    m = df["close"] > h4
    g = (df.loc[m, "close"] - h4[m]) / h4[m]
    gaps.append(g[np.isfinite(g)])
gaps = pd.concat(gaps)
gaps = gaps[(gaps > 0) & (gaps < .25)] * 100          # percent, tail-trimmed for the plot
med = float(gaps.median())
stats["gap_n"] = int(len(gaps))
stats["gap_median"] = round(med, 2)

fig, ax = frame()
counts, edges = np.histogram(gaps[gaps <= 8], bins=120)
cols = [KILL if edges[i] >= med else "#3a4048" for i in range(len(counts))]
ax.bar(edges[:-1], counts, width=np.diff(edges), align="edge", color=cols, zorder=2)
ax.axvline(med, color=KILL, lw=1.4, zorder=4)
ax.text(med + .12, ax.get_ylim()[1] * .93,
        f"median {med:.2f}%\nthe close is already this far past the level",
        color=KILL, fontsize=9.5, va="top")
ax.set_title("CAM_DAILY_LONG · HOW FAR PAST H4 THE CONFIRMING CLOSE SITS",
             loc="left", fontsize=11, color=INK, pad=14)
ax.set_xlabel("distance beyond the level at confirmation, %")
ax.margins(x=.01)
save(fig, "gap.png")

# ============================ 3. two regimes =================================
# Equal-weight daily return of the whole universe, compounded from Jan 2021.
rets = []
for sym, df in data.items():
    d = df[df["date"] >= "2020-12-25"].set_index("date")["close"]
    if len(d) < 100:
        continue
    rets.append(d.pct_change().rename(sym))
R = pd.concat(rets, axis=1).sort_index()
R = R[R.index >= "2021-01-01"]
R = R.where(R.abs() < .5)                               # guard against split glitches
daily = R.mean(axis=1, skipna=True)
curve = (1 + daily.fillna(0)).cumprod() * 100

split = pd.Timestamp("2024-01-01")
def cagr(seg):
    yrs = (seg.index[-1] - seg.index[0]).days / 365.25
    return (seg.iloc[-1] / seg.iloc[0]) ** (1 / yrs) - 1
c1, c2 = cagr(curve[curve.index < split]), cagr(curve[curve.index >= split])
stats["regime1_cagr"] = round(c1 * 100, 1)
stats["regime2_cagr"] = round(c2 * 100, 1)
stats["curve_end"] = round(float(curve.iloc[-1]), 1)

fig, ax = frame()
ax.axvspan(curve.index[0], split, color=LIVE, alpha=.06)
ax.axvspan(split, curve.index[-1], color=KILL, alpha=.05)
ax.plot(curve.index, curve.values, color=INK, lw=1.5, zorder=3)
ax.axvline(split, color=DIM, lw=.9, ls=(0, (4, 4)))
ax.text(curve.index[180], ax.get_ylim()[1], f"2021–23 · +{c1*100:.1f}%/yr",
        color=LIVE, fontsize=10.5, va="top")
ax.text(split + pd.Timedelta(days=40), ax.get_ylim()[1],
        f"2024–26 · {c2*100:+.1f}%/yr", color=KILL, fontsize=10.5, va="top")
ax.set_title("THE UNIVERSE, EQUAL-WEIGHT · JAN 2021 = 100", loc="left",
             fontsize=11, color=INK, pad=14)
ax.margins(x=.01)
save(fig, "regimes.png")

(OUT / "charts.json").write_text(json.dumps(stats, indent=1))
print(json.dumps(stats))
