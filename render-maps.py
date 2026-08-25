#!/usr/bin/env python3
"""Render the grid's layers as plates for the research notebook.

These are the same binaries the explorer reads, drawn server-side so the page can show
six real views of India without shipping 132 MB to every visitor. Binned slightly
coarser than the source raster so the 5 km cells tile without leaving a mesh of gaps.
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

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


def grid(vals, mode="mean"):
    ok = np.isfinite(vals)
    if mode == "mode":                       # categorical: take the most common class
        out = np.full((H, W), np.nan)
        order = np.lexsort((vals[ok], GY[ok] * W + GX[ok]))
        gy, gx, v = GY[ok][order], GX[ok][order], vals[ok][order]
        out[gy, gx] = v                      # last wins; fine for a coarse plate
        return out
    s = np.zeros((H, W))
    c = np.zeros((H, W))
    np.add.at(s, (GY[ok], GX[ok]), vals[ok])
    np.add.at(c, (GY[ok], GX[ok]), 1)
    return np.where(c > 0, s / np.maximum(c, 1), np.nan)


# 12 land clusters need a categorical palette, not a ramp.
CLUSTER = ListedColormap([
    "#1b2a4a", "#2f6f8f", "#3fa08a", "#7ec46b", "#c3d94e", "#e8c34a",
    "#e08b3c", "#c95b3c", "#9e3b52", "#6b2f5e", "#8a8f98", "#e9edf2"])

LAYERS = [
    ("drift", "drift_2025.f32", "magma", (2, 98), "mean",
     "How much each cell changed against last year"),
    ("built", "built_2025.f32", "inferno", (1, 99.5), "mean",
     "Built-up fraction, 2025 — the cities draw themselves"),
    ("cluster", "cluster.u8", CLUSTER, None, "mode",
     "Twelve land types, k-means over the embedding"),
    ("pop", "pop_2020.f32", "cividis", (2, 99.5), "mean",
     "Population, 2020 — the last free year"),
    ("rain", "precip_2024.f32", "YlGnBu", (2, 98), "mean",
     "Annual rainfall, 2024"),
    ("elev", "elev_mean.f32", "terrain", (1, 99), "mean",
     "Elevation — the Himalaya, the Ghats, the Deccan"),
]

for name, fn, cmap, pct, mode, note in LAYERS:
    f = DATA / fn
    if not f.exists():
        cands = sorted(DATA.glob(fn.split("_")[0] + "_*"))
        if not cands:
            print(f"  skip {name}: no {fn}")
            continue
        f = cands[-1]
    dt = "<u1" if f.suffix == ".u8" else "<f4"
    v = np.fromfile(f, dtype=dt).astype("f4")
    if dt == "<u1":
        v[v == 255] = np.nan
    g = grid(v, mode)
    kw = {}
    if pct:
        lo, hi = np.nanpercentile(g, pct)
        kw = dict(vmin=lo, vmax=hi)
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=190)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    fig.patch.set_facecolor("#07090c")
    ax.set_facecolor("#07090c")
    ax.imshow(g, cmap=cmap, interpolation="nearest" if mode == "mode" else "bilinear", **kw)
    out = DEST / f"{name}.jpg"
    fig.savefig(out, facecolor="#07090c", pil_kwargs={"quality": 84, "optimize": True})
    plt.close(fig)
    print(f"  {name:9} {f.name:20} {out.stat().st_size // 1024:>4} KB   {note}")

print(f"\n{len(list(DEST.glob('*.jpg')))} plates -> assets/maps/")
