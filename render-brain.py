#!/usr/bin/env python3
"""Draw the trading repository's Obsidian vault as the graph it actually is.

Nodes are markdown notes under historical_data/claude; edges are the [[wikilinks]]
between them, resolved by basename the way Obsidian resolves them. Nothing is
staged: if the graph looks connected, it is because the vault's standing rule
(no finding lands as an orphan) was actually followed.
"""
import glob
import json
import os
import pathlib
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

VAULT = pathlib.Path(os.path.expanduser("~/Desktop/historical_data/claude"))
OUT = pathlib.Path(__file__).parent / "assets/ops"

BG, INK, DIM, EDGE = "#07090c", "#e9e7e4", "#8b9098", "#252a31"
PAL = {"wiki": "#f2b45c", "intel": "#7aa2f7", "strategy": "#2f9e83",
       "kabaddi": "#e0705f", "root": "#c792ea", "other": "#8b9098"}


def bucket(rel):
    top = rel.split("/")[0] if "/" in rel else "root"
    if top in PAL:
        return top
    if "kabaddi" in rel.lower():
        return "kabaddi"
    return "other" if "/" in rel else "root"


files = {}
for f in glob.glob(str(VAULT / "**/*.md"), recursive=True):
    rel = os.path.relpath(f, VAULT)
    files[pathlib.Path(f).stem.lower()] = rel

G = nx.Graph()
for f in glob.glob(str(VAULT / "**/*.md"), recursive=True):
    rel = os.path.relpath(f, VAULT)
    try:
        text = open(f, encoding="utf-8", errors="ignore").read()
    except OSError:
        continue
    src = pathlib.Path(f).stem
    for m in re.findall(r"\[\[([^\]|#]+)", text):
        tgt = m.strip()
        hit = files.get(tgt.lower()) or files.get(tgt.replace(" ", "-").lower())
        if hit:
            G.add_edge(rel, hit)

deg = dict(G.degree)
n, e = G.number_of_nodes(), G.number_of_edges()
comps = nx.number_connected_components(G)
print(f"graph: {n} linked notes, {e} edges, {comps} components "
      f"(vault holds {len(files)} notes total)")

# Lay out the dominant component to fill the frame; park the satellites in an
# inset so the picture is the graph, not the empty space between its islands.
comps_sorted = sorted(nx.connected_components(G), key=len, reverse=True)
main = G.subgraph(comps_sorted[0])
import numpy as np
pos = nx.spring_layout(main, k=2.4 / max(len(main), 2) ** 0.5,
                       iterations=320, seed=31)
xs = np.array([p_[0] for p_ in pos.values()])
ys = np.array([p_[1] for p_ in pos.values()])
for node in pos:
    x, y = pos[node]
    pos[node] = (0.05 + 0.90 * (x - xs.min()) / (float(np.ptp(xs)) or 1),
                 0.12 + 0.76 * (y - ys.min()) / (float(np.ptp(ys)) or 1))
for ci, comp in enumerate(comps_sorted[1:3]):
    sub = G.subgraph(comp)
    sp = nx.spring_layout(sub, seed=7 + ci)
    sxs = np.array([q[0] for q in sp.values()]); sys_ = np.array([q[1] for q in sp.values()])
    ox = 0.80 + ci * 0.11
    for node in sp:
        x, y = sp[node]
        pos[node] = (ox + 0.08 * (x - sxs.min()) / (float(np.ptp(sxs)) or 1),
                     0.90 + 0.06 * (y - sys_.min()) / (float(np.ptp(sys_)) or 1))

fig, ax = plt.subplots(figsize=(13.5, 9), dpi=160)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_axis_off()

for a, b in G.edges:
    xa, ya = pos[a]; xb, yb = pos[b]
    ax.plot([xa, xb], [ya, yb], color=EDGE, lw=0.7, alpha=0.7, zorder=1)
for node, (x, y) in pos.items():
    c = PAL[bucket(node)]
    ax.scatter([x], [y], s=26 + deg[node] * 16, color=c, zorder=3,
               edgecolors=BG, linewidths=0.6)
for node, d in sorted(deg.items(), key=lambda kv: -kv[1])[:9]:
    x, y = pos[node]
    ax.annotate(pathlib.Path(node).stem, (x, y), xytext=(7, 6),
                textcoords="offset points", fontsize=7.5,
                fontfamily="monospace", color=INK, zorder=4)

ax.set_title(f"THE VAULT \u00b7 {len(files)} NOTES, {e} LINKS \u00b7 "
             f"ONE CONTINENT, {comps - 1} SATELLITES", loc="left", fontsize=11, color=INK,
             fontfamily="monospace", pad=16)
legend_y = 0.02
for i, (k, c) in enumerate(PAL.items()):
    if k == "other":
        continue
    ax.text(0.01 + i * 0.11, legend_y, f"● {k}", transform=ax.transAxes,
            color=c, fontsize=8.5, fontfamily="monospace")
fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.05)
out = OUT / "brain.png"
fig.savefig(out, facecolor=BG)
print(f"brain.png {out.stat().st_size // 1024} KB")

(OUT / "brain.json").write_text(json.dumps(
    {"notes": len(files), "linked": n, "edges": e, "components": comps}))
