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

# ============================ 4. kabaddi (notebook numbers) ==================
# These are the notebook's simulation results, NOT recomputed here — the ruin
# distribution needs the full Kabaddi harness. Drawn honestly, labelled honestly.
KAB = [  # (label, de-size, cagr %, max dd %, p5 %)
    ("1x",  "on",  4.7, -15.7, None), ("1x",  "off", 6.9, -19.3, None),
    ("3x",  "on",  7.8, -28.4, None), ("3x",  "off", 16.8, -49.9, None),
    ("10x", "on",  9.2, -53.6, None), ("10x", "off", -0.6, -94.9, -99.7),
]
fig, ax = frame()
xs = np.arange(len(KAB), dtype=float)
xs += (xs // 2) * .5                                   # gap between leverage groups
for x, (lev, ds, cagr, dd, p5) in zip(xs, KAB):
    body = "#3a4048" if ds == "on" else "#4a3a3d"
    ax.bar([x], [cagr - dd], bottom=dd, width=.62, color=body, zorder=2)
    ax.plot([x - .31, x + .31], [cagr, cagr], color=LIVE if cagr > 0 else KILL,
            lw=2.4, zorder=4)
    ax.plot([x - .31, x + .31], [dd, dd], color=KILL, lw=2.4, zorder=4)
    ax.text(x - .42 if p5 is not None else x, dd - 3.5, f"{dd:.1f}%", color=KILL,
            ha="right" if p5 is not None else "center", va="top", fontsize=9)
    ax.text(x, cagr + 3.5, f"{cagr:+.1f}%", color=LIVE if cagr > 0 else KILL,
            ha="center", va="bottom", fontsize=9)
    if p5 is not None:
        ax.scatter([x], [p5], color=KILL, s=26, zorder=5)
        ax.text(x + .42, p5, f"p5: {p5}%", color=KILL, fontsize=9, va="center")
ax.axhline(0, color=DIM, lw=.8)
for x, (lev, ds, *_ ) in zip(xs, KAB):
    ax.text(x, -118, f"{lev}\n{ds}", color=DIM, ha="center", va="top", fontsize=9)
ax.set_xticks([]); ax.set_ylim(-125, 30)
ax.set_title("KABADDI · WHAT LEVERAGE DOES TO A POSITIVE-EXPECTANCY BOOK",
             loc="left", fontsize=11, color=INK, pad=14)
ax.text(.995, .975, "from the notebook's simulation · not recomputed here",
        transform=ax.transAxes, color=DIM, fontsize=8.5, ha="right", va="top")
save(fig, "kabaddi.png")

# ============================ 5. real breadth ================================
print("computing breadth ...")
above50, above200 = [], []
for sym, df in data.items():
    c = df.set_index("date")["close"]
    if len(c) < 260:
        continue
    above50.append((c > c.rolling(50).mean()).rename(sym))
    above200.append((c > c.rolling(200).mean()).rename(sym))
B50 = pd.concat(above50, axis=1).sort_index()
B200 = pd.concat(above200, axis=1).sort_index()
b50 = B50.mean(axis=1) * 100
b200 = B200.mean(axis=1) * 100
b50, b200 = b50[b50.index >= "2021-01-01"], b200[b200.index >= "2021-01-01"]
stats["breadth_now_50"] = round(float(b50.iloc[-1]), 1)
stats["breadth_now_200"] = round(float(b200.iloc[-1]), 1)

# playable version: the same two series, daily, as JSON for the canvas widget
bj = {"dates": [d.strftime("%Y-%m-%d") for d in b50.index],
      "b50": [round(float(v), 1) for v in b50.values],
      "b200": [round(float(v), 1) for v in b200.reindex(b50.index).values]}
(OUT / "breadth.json").write_text(json.dumps(bj, separators=(",", ":")))
print(f"  breadth.json    {len(bj['dates'])} days, "
      f"{(OUT / 'breadth.json').stat().st_size // 1024} KB")

fig, ax = frame()
ax.axhline(50, color=DIM, lw=.8, ls=(0, (4, 4)))
from matplotlib.dates import date2num
xb = date2num(b50.index.to_pydatetime())
ax.plot(b200.index, b200.values, color="#6b7280", lw=1.1, label="above 200-day")
ax.plot(b50.index, b50.values, color=INK, lw=1.3, label="above 50-day")
v = b50.values.astype(float)
ax.fill_between(xb, 50, v, where=v < 50, color=KILL, alpha=.14, lw=0)
ax.fill_between(xb, 50, v, where=v >= 50, color=LIVE, alpha=.10, lw=0)
ax.set_ylim(0, 100)
ax.set_title("BREADTH · SHARE OF THE UNIVERSE ABOVE ITS OWN MOVING AVERAGE",
             loc="left", fontsize=11, color=INK, pad=14)
leg = ax.legend(loc="lower left", frameon=False, fontsize=9)
for t in leg.get_texts():
    t.set_color(DIM)
ax.margins(x=.01)
save(fig, "breadth.png")

# ============================ 6. sector rotation trails ======================
print("computing sector rotation ...")
import sys
sys.path.insert(0, os.path.expanduser("~/Desktop/historical_data/claude/strategy"))
from rs import INDUSTRY_TO_SECTOR                          # the repo's own mapping
master = pd.read_parquet(os.path.expanduser(
    "~/Desktop/historical_data/claude/strategy/reference/symbols_master.parquet"))
sec_of = {r.symbol: INDUSTRY_TO_SECTOR.get(r.industry, "Other")
          for r in master.itertuples()}

closes = pd.concat(
    {s: df.set_index("date")["close"] for s, df in data.items()}, axis=1).sort_index()
closes = closes[closes.index >= "2020-06-01"]
rets = closes.pct_change()
rets = rets.where(rets.abs() < .5)
uni = (1 + rets.mean(axis=1, skipna=True).fillna(0)).cumprod()

sectors = {}
for sec in sorted(set(sec_of.values())):
    cols = [s for s in closes.columns if sec_of.get(s) == sec]
    if len(cols) < 8 or sec == "Other":
        continue
    idx = (1 + rets[cols].mean(axis=1, skipna=True).fillna(0)).cumprod()
    sectors[sec] = idx / uni                               # RS ratio vs the universe

wk = pd.concat(sectors, axis=1).resample("W-FRI").last().dropna(how="all")
ratio = wk / wk.rolling(13).mean() * 100                   # JdK-style RS-ratio
mom = ratio / ratio.shift(1) * 100                         # and its momentum
ratio, mom = ratio.dropna(), mom.dropna()
common = ratio.index.intersection(mom.index)
common = common[common >= "2021-06-01"]
ratio, mom = ratio.loc[common], mom.loc[common]

CODES = {"Financial Services": "FIN", "Information Technology": "IT",
         "Automobile and Auto Components": "AUTO", "Healthcare": "HLTH",
         "Fast Moving Consumer Goods": "FMCG", "Metals & Mining": "METL",
         "Oil Gas & Consumable Fuels": "ENGY", "Capital Goods": "CAPG",
         "Consumer Durables": "CDUR", "Power": "PWR", "Realty": "RLTY",
         "Chemicals": "CHEM", "Construction": "CNST", "Services": "SVCS",
         "Telecommunication": "TCOM", "Construction Materials": "CMAT",
         "Consumer Services": "CSVC", "Textiles": "TXTL",
         "Media Entertainment & Publication": "MDIA", "Diversified": "DIV"}
payload = {
    "weeks": [d.strftime("%Y-%m-%d") for d in ratio.index],
    "sectors": [
        {"name": sec, "code": CODES.get(sec, sec[:4].upper()),
         "n": sum(1 for s in sec_of.values() if s == sec),
         "x": [round(float(v), 2) if np.isfinite(v) else None for v in ratio[sec]],
         "y": [round(float(v), 2) if np.isfinite(v) else None for v in mom[sec]]}
        for sec in sectors if sec in ratio.columns],
}
(OUT / "sectors.json").write_text(json.dumps(payload, separators=(",", ":")))
stats["rrg_sectors"] = len(payload["sectors"])
stats["rrg_weeks"] = len(payload["weeks"])
print(f"  sectors.json    {len(payload['sectors'])} sectors x {len(payload['weeks'])} weeks, "
      f"{(OUT/'sectors.json').stat().st_size // 1024} KB")

(OUT / "charts.json").write_text(json.dumps(stats, indent=1))
print(json.dumps(stats))
