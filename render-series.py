#!/usr/bin/env python3
"""Render the grid's time series as frames, so the page can play them.

Two series, both real: built-up area across six epochs from 1990, and year-on-year
change for every year the embedding covers. Same binning as render-maps.py so the
frames sit in register with the single-layer plates.
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA = pathlib.Path(__file__).parent / "work/india-grid/data"
DEST = pathlib.Path(__file__).parent / "assets/maps"
DEST.mkdir(parents=True, exist_ok=True)

meta = json.loads((DATA / "meta.json").read_text())
X0, Y0, X1, Y1 = meta["bbox"]
lat = np.fromfile(DATA / "lat.f32", dtype="<f4")
lon = np.fromfile(DATA / "lon.f32", dtype="<f4")
R = 0.05
W = int(np.ceil((X1 - X0) / R))
H = int(np.ceil((Y1 - Y0) / R))
GX = np.clip(((lon - X0) / R).astype(int), 0, W - 1)
GY = np.clip(((Y1 - lat) / R).astype(int), 0, H - 1)


def grid(v):
    ok = np.isfinite(v)
    s = np.zeros((H, W)); c = np.zeros((H, W))
    np.add.at(s, (GY[ok], GX[ok]), v[ok])
    np.add.at(c, (GY[ok], GX[ok]), 1)
    return np.where(c > 0, s / np.maximum(c, 1), np.nan)


def draw(g, out, cmap, vmin, vmax):
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=170)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    fig.patch.set_facecolor("#07090c"); ax.set_facecolor("#07090c")
    ax.imshow(g, cmap=cmap, vmin=vmin, vmax=vmax, interpolation="bilinear")
    fig.savefig(out, facecolor="#07090c", pil_kwargs={"quality": 80, "optimize": True})
    plt.close(fig)


def series(prefix, cmap, out_prefix):
    files = sorted(DATA.glob(f"{prefix}_*.f32"))
    if not files:
        print(f"  no {prefix}_*.f32"); return []
    grids, years = [], []
    for f in files:
        y = f.stem.split("_")[-1]
        if not y.isdigit():
            continue
        grids.append(grid(np.fromfile(f, dtype="<f4")))
        years.append(y)
    # One scale across the whole series, or the animation lies about growth.
    allv = np.concatenate([g[np.isfinite(g)] for g in grids])
    lo, hi = np.nanpercentile(allv, [2, 99.5])
    for g, y in zip(grids, years):
        out = DEST / f"{out_prefix}-{y}.jpg"
        draw(g, out, cmap, lo, hi)
        print(f"  {out.name:22} {out.stat().st_size // 1024:>4} KB")
    return years


print("built-up, 1990 -> 2025")
b = series("built", "inferno", "built")
print("year-on-year change")
d = series("drift", "magma", "drift")
(DEST / "series.json").write_text(json.dumps({"built": b, "drift": d}))
print(f"\nseries.json: {len(b)} built epochs, {len(d)} drift years")
