#!/usr/bin/env python3
"""The three project notebooks: /market, /research-os, /film.

Register: the home page is a showcase, these are notebooks. Someone reading this far
has already decided to take the work seriously, so the rigour lives here.

Voice: first person plural, and the collaboration is named rather than implied.
Nothing is invented — every number traces to a file on the Desktop.

  python3 build-pages.py           preview, noindex
  python3 build-pages.py --prod    the head the live site ships
"""
import html
import re
import json
import pathlib
import sys

from shared import BASE_CSS

OUT = pathlib.Path(__file__).parent
PROD = "--prod" in sys.argv
ROBOTS = "" if PROD else '<meta name="robots" content="noindex">'

PAGE_CSS = """
/* ---------- notebook ---------- */
.head{padding:4.5rem 0 3rem;border-bottom:1px solid var(--ink)}
.head__eyebrow{font-family:var(--mono);font-size:.6875rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--ink-3);margin-bottom:1.5rem}
.head h1{font-size:clamp(2rem,1.2rem + 3.4vw,3.5rem);letter-spacing:-.03em;max-width:19ch;
  text-wrap:balance}
.head__stand{margin-top:1.6rem;max-width:46ch;color:var(--ink-2);font-size:1.125rem}
.head__facts{display:flex;flex-wrap:wrap;gap:2.25rem;margin-top:2.5rem;
  font-family:var(--mono);font-size:.75rem;color:var(--ink-3)}
.head__facts b{display:block;font-size:1.375rem;color:var(--ink);font-weight:400;
  margin-bottom:.2rem;font-family:var(--serif)}

.ent{padding:3.5rem 0;border-bottom:1px solid var(--rule)}
.ent__top{display:flex;gap:1.25rem;align-items:baseline;
  font-family:var(--mono);font-size:.6875rem;letter-spacing:.12em;text-transform:uppercase;
  color:var(--ink-3);margin-bottom:1rem}
.ent__no{color:var(--ink)}
.ent__when{margin-left:auto;letter-spacing:.06em;text-transform:none}
.ent h2{font-size:clamp(1.375rem,1.1rem + 1.2vw,2rem);letter-spacing:-.022em;
  max-width:24ch;margin-bottom:1.25rem}
.ent p+p{margin-top:1rem}
.ent p{max-width:var(--measure)}
.ent i{color:var(--ink-2)}

.rule{margin:2.25rem 0;max-width:var(--measure)}
.rule span{display:inline-block;font-family:var(--mono);font-size:.625rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--kill);margin-bottom:.55rem;
  padding-bottom:.3rem;border-bottom:1px solid var(--kill)}
.rule p{font-size:1.0625rem}

.pull{margin:1.75rem 0;font-size:clamp(1.25rem,1.05rem + .9vw,1.625rem);line-height:1.35;
  letter-spacing:-.02em;max-width:26ch;color:var(--ink)}
.pull::before{content:"\\201C"} .pull::after{content:"\\201D"}

figure.t{margin:2.25rem 0;overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.9375rem;
  font-family:var(--mono);font-variant-numeric:tabular-nums}
th{text-align:left;font-size:.625rem;letter-spacing:.13em;text-transform:uppercase;
  color:var(--ink-3);font-weight:400;padding:.5rem .75rem .5rem 0;
  border-bottom:1px solid var(--ink)}
td{padding:.5rem .75rem .5rem 0;border-bottom:1px solid var(--rule)}
td.neg{color:var(--kill)} td.pos{color:var(--live)}
th.num,td.num{text-align:right}
figcaption{font-family:var(--serif);font-style:italic;font-size:.9688rem;line-height:1.6;
  color:var(--ink-2);margin-top:.9rem;max-width:44rem}

.figplate{margin:2.5rem 0;background:var(--plate);border:1px solid var(--rule-2)}
.figplate img{width:100%;display:block}
.figplate figcaption{padding:.9rem 1.1rem;margin:0;color:#b9c0c9;
  border-top:1px solid #23262c;background:var(--plate)}

.go{display:inline-block;margin-top:1.75rem;font-family:var(--mono);font-size:.6875rem;
  letter-spacing:.12em;text-transform:uppercase;border-bottom:1px solid var(--rule-2);
  padding-bottom:.15rem}
.go:hover{border-color:var(--ink)}

/* ---------- graveyard ---------- */
.yard{padding:3.5rem 0}
.yard h2{font-size:clamp(1.5rem,1.15rem + 1.4vw,2.25rem);margin-bottom:.9rem}
.yard__intro{max-width:var(--measure);color:var(--ink-2);margin-bottom:2rem}
.yard__filter{display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:1.5rem}
.yard__filter button{font-family:var(--mono);font-size:.6875rem;letter-spacing:.1em;
  text-transform:uppercase;background:none;border:1px solid var(--rule-2);border-radius:2px;
  padding:.35rem .7rem;cursor:pointer;color:var(--ink-2);font-weight:400}
.yard__filter button.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.th{padding:1.1rem 0;border-bottom:1px solid var(--rule);display:grid;gap:.35rem}
.th__top{display:flex;gap:.75rem;align-items:baseline;flex-wrap:wrap}
.th__n{font-family:var(--mono);font-size:.6875rem;color:var(--ink-3);min-width:2.25rem}
.th__name{font-size:1.0625rem}
.th__meta{margin-left:auto;font-family:var(--mono);font-size:.625rem;
  letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3)}
.th__find{font-size:.9375rem;color:var(--ink-2);padding-left:3rem;max-width:60rem}
.vd{font-family:var(--mono);font-size:.5625rem;letter-spacing:.12em;padding:.12rem .4rem;
  border-radius:2px;border:1px solid}
.vd-dead{color:var(--kill);border-color:var(--kill)}
.vd-trust{color:var(--live);border-color:var(--live)}
.vd-open{color:#8a6a1f;border-color:#8a6a1f}
.vd-discount,.vd-tool,.vd-retired{color:var(--ink-3);border-color:var(--rule-2)}

/* ---------- interactive: layer switcher ---------- */
.mapx{margin:2.5rem 0}
.mapx__keys{display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:.9rem}
.mapx__keys button{font-family:var(--mono);font-size:.6875rem;letter-spacing:.1em;
  text-transform:uppercase;background:none;border:1px solid var(--rule-2);border-radius:2px;
  padding:.35rem .7rem;cursor:pointer;color:var(--ink-2)}
.mapx__keys button:hover{border-color:var(--ink)}
.mapx__keys button.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.mapx__stage{position:relative;background:var(--plate);border:1px solid var(--rule-2);
  overflow:hidden}
.mapx__stage img{position:absolute;inset:0;width:100%;height:100%;
  opacity:0;transition:opacity .45s ease}
.mapx__stage img:first-child{position:relative;height:auto}
.mapx__stage img.on{opacity:1}
.mapx__cap{font-family:var(--serif);font-style:italic;font-size:.9688rem;line-height:1.6;
  color:var(--ink-2);margin-top:.9rem;max-width:44rem;min-height:3.2em}

/* ---------- interactive: render ladder ---------- */
.ladder{margin:2.5rem 0}
.ladder__stage{position:relative;background:var(--plate);border:1px solid var(--rule-2);
  aspect-ratio:16/9;overflow:hidden}
.ladder__stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  opacity:0;transition:opacity .4s ease}
.ladder__stage img.on{opacity:1}
.ladder__ctl{display:flex;align-items:center;gap:1rem;margin-top:.9rem;flex-wrap:wrap}
.ladder__ctl input{flex:1;min-width:12rem;accent-color:var(--kill)}
.ladder__n{font-family:var(--mono);font-size:.6875rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--ink-2);min-width:9rem}
.ladder__cap{font-family:var(--serif);font-style:italic;font-size:.9688rem;line-height:1.6;
  color:var(--ink-2);margin-top:.6rem;max-width:44rem;min-height:3.2em}

/* ---------- interactive: fill chart ---------- */
.fillc{margin:2.25rem 0;max-width:46rem}
.fillc__row{display:grid;grid-template-columns:9.5rem 1fr;gap:1rem;align-items:center;
  padding:.55rem 0;border-bottom:1px solid var(--rule)}
.fillc__lab{font-family:var(--mono);font-size:.75rem;color:var(--ink-2)}
.fillc__track{position:relative;height:1.4rem;background:linear-gradient(
  90deg,transparent calc(50% - .5px),var(--rule-2) calc(50% - .5px),
  var(--rule-2) calc(50% + .5px),transparent calc(50% + .5px))}
.fillc__bar{position:absolute;top:.25rem;height:.9rem;
  transition:left .6s cubic-bezier(.2,.7,.3,1),width .6s cubic-bezier(.2,.7,.3,1),
  background .6s ease}
.fillc__val{position:absolute;top:0;font-family:var(--mono);font-size:.6875rem;
  line-height:1.4rem;color:var(--ink-2);transition:left .6s cubic-bezier(.2,.7,.3,1)}
.fillc__toggle{display:flex;gap:.4rem;margin-bottom:1rem}
.fillc__toggle button{font-family:var(--mono);font-size:.6875rem;letter-spacing:.1em;
  text-transform:uppercase;background:none;border:1px solid var(--rule-2);border-radius:2px;
  padding:.35rem .7rem;cursor:pointer;color:var(--ink-2)}
.fillc__toggle button.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}

/* ---------- film: player + scene grid ---------- */
.vid{margin:2.5rem 0;background:var(--plate);border:1px solid var(--rule-2)}
.vid video{width:100%;display:block;background:var(--plate)}
.vid figcaption{padding:.85rem 1rem;margin:0;color:var(--ink-3);
  border-top:1px solid #23262c;background:var(--plate)}
.scenes{margin:2.5rem 0;display:grid;gap:.5rem;
  grid-template-columns:repeat(auto-fit,minmax(15rem,1fr))}
.scenes figure{margin:0;background:var(--plate);border:1px solid var(--rule-2);
  overflow:hidden;cursor:zoom-in}
.scenes img{width:100%;display:block;transition:transform .6s cubic-bezier(.2,.7,.3,1)}
.scenes figure:hover img{transform:scale(1.03)}
.scenes figcaption{font-family:var(--mono);font-size:.6875rem;color:var(--ink-3);
  padding:.5rem .7rem;margin:0;border-top:1px solid #23262c;line-height:1.5}
.lb{position:fixed;inset:0;background:rgba(7,9,12,.94);display:none;z-index:50;
  align-items:center;justify-content:center;padding:2rem;cursor:zoom-out}
.lb.on{display:flex}
.lb img{max-width:100%;max-height:100%;object-fit:contain}

/* ---------- interactive: time player ---------- */
.play{margin:2.5rem 0}
.play__stage{position:relative;background:var(--plate);border:1px solid var(--rule-2);
  overflow:hidden}
.play__stage img{position:absolute;inset:0;width:100%;height:100%;opacity:0}
.play__stage img:first-child{position:relative;height:auto}
.play__stage img.on{opacity:1}
.play__yr{position:absolute;left:1rem;top:.85rem;font-family:var(--mono);
  font-size:1.5rem;color:#f2f4f7;letter-spacing:.04em;
  text-shadow:0 2px 14px rgba(7,9,12,.9)}
.play__ctl{display:flex;align-items:center;gap:.9rem;margin-top:.9rem;flex-wrap:wrap}
.play__btn{font-family:var(--mono);font-size:.6875rem;letter-spacing:.12em;
  text-transform:uppercase;background:var(--ink);color:var(--paper);border:1px solid var(--ink);
  border-radius:2px;padding:.4rem .85rem;cursor:pointer;min-width:5.5rem}
.play__ctl input{flex:1;min-width:10rem;accent-color:var(--kill)}

/* ---------- interactive: verdict timeline ---------- */
.tl{margin:2.25rem 0;overflow-x:auto}
.tl svg{width:100%;min-width:40rem;height:auto;display:block;overflow:visible}
.tl__dot{cursor:pointer;transition:r .15s ease}
.tl__dot:hover{r:6}
.tl__read{font-family:var(--mono);font-size:.75rem;color:var(--ink-2);margin-top:1rem;
  min-height:3.4em;max-width:46rem}
.tl__read b{color:var(--ink);font-weight:500}

/* ---------- rising bar ---------- */
.bar{padding:3.5rem 0;border-top:1px solid var(--ink)}
.bar ol{list-style:none;margin:1.75rem 0 0;padding:0;counter-reset:b}
.bar li{counter-increment:b;padding:.85rem 0 .85rem 3.25rem;position:relative;
  border-bottom:1px solid var(--rule);max-width:52rem}
.bar li::before{content:counter(b,decimal-leading-zero);position:absolute;left:0;
  font-family:var(--mono);font-size:.6875rem;color:var(--ink-3);top:1.05rem}
.bar li b{font-weight:500}
.bar li span{display:block;font-size:.9375rem;color:var(--ink-2);margin-top:.2rem}
"""


def e(t):
    return html.escape(str(t), quote=False)


# ------------------------------------------------------------------ blocks --
def p(t):            return f"<p>{t}</p>"
def pull(t):         return f'<p class="pull">{t}</p>'
def rule(t):         return f'<div class="rule"><span>The rule</span><p>{t}</p></div>'
def go(href, label): return f'<a class="go" href="{href}">{label} &rarr;</a>'


def _numeric(cell):
    txt = re.sub(r"<[^>]+>", "", str(cell))
    txt = txt.replace("&minus;", "-").replace("&times;", "x").strip()
    return bool(re.fullmatch(r"[+\-\u2212]?[\d.,%x\s]+", txt))


def table(headers, rows, caption=""):
    # A column is numeric only if every body cell in it is; those columns right-align.
    numcols = [all(_numeric(r[i]) for r in rows) for i in range(len(headers))]
    th = ""
    for i, h in enumerate(headers):
        cls = ' class="num"' if numcols[i] else ''
        th += f"<th{cls}>{h}</th>"
    tr = ""
    for r in rows:
        tds = ""
        for i, c in enumerate(r):
            cls = []
            s = str(c)
            if s.startswith("−") or (s.startswith("-") and any(ch.isdigit() for ch in s)):
                cls.append("neg")
            elif s.startswith("+"):
                cls.append("pos")
            if numcols[i]:
                cls.append("num")
            a = f' class="{" ".join(cls)}"' if cls else ""
            tds += f"<td{a}>{c}</td>"
        tr += f"<tr>{tds}</tr>"
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return (f'<figure class="t"><table><thead><tr>{th}</tr></thead>'
            f"<tbody>{tr}</tbody></table>{cap}</figure>")


def plate(src, caption, alt=""):
    return (f'<figure class="figplate"><img src="{src}" alt="{e(alt or caption)}" '
            f'loading="lazy" decoding="async"><figcaption>{caption}</figcaption></figure>')


_sf = OUT / "assets/maps/series.json"
SERIES = json.loads(_sf.read_text()) if _sf.exists() else {}

MAPS = [
    ("drift", "Change", "Cosine distance between each cell&rsquo;s fingerprint this year "
     "and last. Bright means the surface changed. This is the layer we built the whole "
     "instrument to produce, and the one the referee later showed measures "
     "volatility rather than development."),
    ("built", "Built-up", "Share of each cell that is built. Nobody drew these cities; "
     "they are the layer reading itself out. The road corridors between them are visible "
     "without being labelled."),
    ("cluster", "Land types", "Twelve clusters over the 64-dimensional embedding. Land "
     "cover was joined in specifically so a cluster could be given a real name instead "
     "of a number."),
    ("pop", "Population", "2020, which is where the free data stops. Reading this layer "
     "correctly took two attempts: a negative window offset had Delhi at 263 "
     "people per square kilometre instead of 23,452."),
    ("rain", "Rainfall", "Annual total. Rainfall <i>level</i> turned out not to move the "
     "land surface at all. Rainfall <i>volatility</i> does, at a rank correlation of "
     "0.357 against a null of zero."),
    ("elev", "Elevation", "The Himalaya, the Western Ghats and the Deccan plateau, drawn "
     "only from cell elevation. Useful mostly as a sanity check that the joins land where "
     "the geography says they should."),
]


def mapswitch():
    keys = "".join(
        f'<button class="{"on" if i == 0 else ""}" data-m="{k}" data-cap="{e(c)}">{lbl}</button>'
        for i, (k, lbl, c) in enumerate(MAPS))
    imgs = "".join(
        f'<img class="{"on" if i == 0 else ""}" data-m="{k}" src="/assets/maps/{k}.jpg" '
        f'alt="India rendered by {lbl.lower()}" loading="lazy" decoding="async">'
        for i, (k, lbl, _) in enumerate(MAPS))
    return (f'<div class="mapx"><div class="mapx__keys">{keys}</div>'
            f'<div class="mapx__stage">{imgs}</div>'
            f'<p class="mapx__cap">{MAPS[0][2]}</p></div>')


LADDER = [
    ("The empty street, wide", "The finished set with nobody in it. The camera sits well "
     "back and takes in the whole block: magenta on the left, the diner sign on "
     "the right, everything already reflecting in the wet road."),
    ("Camera moved in", "The same street from a different position, with a warmer read "
     "on the signage. No new geometry, no new materials. Just a second opinion about "
     "where to stand."),
    ("A walker, crossing", "The first figure, moving across the frame at a distance. It "
     "immediately changes what the street is for: the reflections now have "
     "something to be near."),
    ("Turned toward the lens", "Same camera, the walk redirected. The street stops being "
     "a backdrop and becomes somewhere a person is going."),
    ("Rain, and far too much of it", "The particle system goes in and flattens "
     "everything. The neon is washed out, the figure is a smudge, the road is gone. This "
     "pass is kept because the overshoot is the useful part: you cannot tune a "
     "thing you have not yet pushed past."),
    ("Rain, pulled back", "Density down, figure forward, the signage readable again. "
     "This is the frame the site opens on."),
]


def ladder():
    imgs = "".join(
        f'<img class="{"on" if i == 0 else ""}" data-l="{i}" '
        f'src="/assets/plates/ladder-pass{i+1}.jpg" alt="Render pass {i+1}: {t}" '
        f'loading="lazy" decoding="async">' for i, (t, _) in enumerate(LADDER))
    caps = json.dumps([[t, c] for t, c in LADDER])
    return (f'<div class="ladder" data-caps=\'{caps}\'>'
            f'<div class="ladder__stage">{imgs}</div>'
            f'<div class="ladder__ctl"><span class="ladder__n" id="ladn">Pass 1 &middot; '
            f'{LADDER[0][0]}</span>'
            f'<input type="range" min="0" max="{len(LADDER)-1}" value="0" step="1" '
            f'id="ladr" aria-label="Render pass"></div>'
            f'<p class="ladder__cap" id="ladc">{LADDER[0][1]}</p></div>')


SCENES = [
    ("f01", "The price, cold open"), ("f02", "A human, and a humanoid, to scale"),
    ("f03", "Fifty degrees of freedom, twenty-two of them in the hand"),
    ("f04", "The comparison the whole film keeps returning to"),
    ("f05", "Sensors are 37% of the bill of materials. The battery is 0.5%"),
    ("f06", "The hands alone: $9,315"),
    ("f07", "Question card: none of this scales until it gets cheap"),
    ("f08", "The timeline opens"), ("f09", "Ten years of almost nothing"),
    ("f10", "Six models unveiled in 2022. Fifty-one in 2024"),
    ("f11", "Price falls, capability lands, adoption goes vertical"),
    ("f12", "One becomes a hundred, a hundred becomes a million"),
    ("f13", "A billion in use by 2050"),
    ("f14", "$5 trillion a year: twice the global auto industry"),
    ("f15", "The crowd, at scale"),
    ("f16", "930 million at work. 80 million in homes"),
    ("f17", "One household in ten, and the last place they arrive"),
    ("f18", "China 302m against America&rsquo;s 78m. Patents, 5,688 against 1,483"),
]


def filmplayer():
    return ('<figure class="vid"><video controls preload="metadata" '
            'poster="/assets/plates/film-poster.jpg" '
            'src="/assets/film/humanoids-2050.mp4"></video>'
            '<figcaption>Humanoids 2050: three minutes, twenty-five scenes, '
            'narrated by Nandit. This is the compressed build; the master is 80 MB.'
            '</figcaption></figure>')


def scenes():
    figs = "".join(
        f'<figure data-full="/assets/film/frames/{k}.jpg">'
        f'<img src="/assets/film/frames/{k}.jpg" alt="{e(c)}" loading="lazy" '
        f'decoding="async"><figcaption>{c}</figcaption></figure>'
        for k, c in SCENES)
    return f'<div class="scenes">{figs}</div><div class="lb" id="lb"><img alt=""></div>'


def player(prefix, years, label, caption):
    imgs = "".join(
        f'<img class="{"on" if i == 0 else ""}" data-i="{i}" '
        f'src="/assets/maps/{prefix}-{y}.jpg" alt="India, {label}, {y}" '
        f'loading="lazy" decoding="async">' for i, y in enumerate(years))
    ys = json.dumps(years)
    return (f'<div class="play" data-years=\'{ys}\'>'
            f'<div class="play__stage">{imgs}'
            f'<span class="play__yr">{years[0]}</span></div>'
            f'<div class="play__ctl"><button class="play__btn">Play</button>'
            f'<input type="range" min="0" max="{len(years)-1}" value="0" step="1" '
            f'aria-label="{label} year"></div>'
            f'<p class="mapx__cap">{caption}</p></div>')


FILL = [("cam_daily_long", 1.64, -0.30), ("cpr_daily_long", 1.72, -0.23),
        ("cam_1H_short", 0.50, -0.13), ("cpr_1H_short", 0.51, -0.14)]


def fillchart():
    rows = ""
    for name, modelled, honest in FILL:
        rows += (f'<div class="fillc__row" data-m="{modelled}" data-h="{honest}">'
                 f'<span class="fillc__lab">{name}</span>'
                 f'<span class="fillc__track"><i class="fillc__bar"></i>'
                 f'<span class="fillc__val"></span></span></div>')
    return ('<div class="fillc">'
            '<div class="fillc__toggle">'
            '<button class="on" data-f="m">What we modelled</button>'
            '<button data-f="h">What we could actually fill</button></div>'
            f"{rows}</div>")


def timeline(threads):
    """Every thread on a real date axis, coloured by verdict."""
    months = sorted({t.get("date", "")[:7] for t in threads if t.get("date")})
    if not months:
        return ""
    idx = {m: i for i, m in enumerate(months)}
    W_, H_, PAD = 1000, 250, 34
    step = (W_ - PAD * 2) / max(len(months) - 1, 1)
    lanes = {}
    dots = ""
    COL = {"DEAD": "#ae2f22", "TRUST": "#1c6553", "OPEN": "#8a6a1f"}
    for t in threads:
        d = t.get("date", "")[:7]
        if d not in idx:
            continue
        x = PAD + idx[d] * step
        lanes[d] = lanes.get(d, 0) + 1
        y = H_ - PAD - (lanes[d] - 1) * 11
        c = COL.get(t.get("verdict"), "#8b9098")
        dots += (f'<circle class="tl__dot" cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{c}" '
                 f'data-n="{e(t["name"])}" data-v="{t.get("verdict","")}" '
                 f'data-f="{e(t.get("finding",""))[:190]}"></circle>')
    ticks = "".join(
        f'<text x="{PAD + i*step:.1f}" y="{H_-10}" text-anchor="middle" '
        f'font-family="IBM Plex Mono,monospace" font-size="11" fill="#8b9098">{m[5:]}/{m[2:4]}</text>'
        for i, m in enumerate(months))
    return (f'<div class="tl"><svg viewBox="0 0 {W_} {H_}" role="img" '
            f'aria-label="Every research thread plotted by the month it concluded">'
            f'<line x1="{PAD}" y1="{H_-PAD+8}" x2="{W_-PAD}" y2="{H_-PAD+8}" '
            f'stroke="#c9c0ad"></line>{ticks}{dots}</svg>'
            f'<p class="tl__read" id="tlread">Hover any dot. Each one is a hypothesis, '
            f'placed on the month it was concluded and coloured by its verdict.</p></div>')


def entry(no, when, title, blocks):
    return (f'<section class="ent"><div class="col-wide">'
            f'<div class="ent__top"><span class="ent__no">{no}</span>'
            f'<span class="ent__when">{when}</span></div>'
            f"<h2>{title}</h2>{''.join(blocks)}</div></section>")


# ------------------------------------------------------------- the yard ----
def load_threads():
    cat = json.loads((OUT / "assets/research_catalog.json").read_text())
    return cat if isinstance(cat, list) else next(
        v for v in cat.values() if isinstance(v, list))


def graveyard():
    th = load_threads()
    order = {"DEAD": 0, "DISCOUNT": 1, "RETIRED": 2, "TOOL": 3, "OPEN": 4, "TRUST": 5}
    th = sorted(th, key=lambda t: (order.get(t.get("verdict"), 9), t.get("date", "")))
    items = ""
    for i, t in enumerate(th, 1):
        v = t.get("verdict", "")
        items += (
            f'<article class="th" data-v="{v}">'
            f'<div class="th__top"><span class="th__n">{i:02d}</span>'
            f'<span class="th__name">{e(t["name"])}</span>'
            f'<span class="th__meta">{e(t.get("family",""))} &middot; {e(t.get("date",""))} '
            f'&middot; <span class="vd vd-{v.lower()}">{v}</span></span></div>'
            f'<p class="th__find">{e(t.get("finding",""))}</p></article>')
    counts = {}
    for t in th:
        counts[t.get("verdict")] = counts.get(t.get("verdict"), 0) + 1
    btns = '<button class="on" data-f="ALL">All ' + str(len(th)) + "</button>"
    for k in ["DEAD", "DISCOUNT", "TOOL", "TRUST", "OPEN", "RETIRED"]:
        if k in counts:
            btns += f'<button data-f="{k}">{k.title()} {counts[k]}</button>'
    return (f'<section class="yard" id="graveyard"><div class="col-wide"><h2>The graveyard</h2>'
            f'<p class="yard__intro">Every hypothesis we ran to a conclusion, with the '
            f'finding that ended it. Forty-one are dead. We are naming all of them, '
            f'because a list of what did not work is the only honest way to read a list '
            f'of what did.</p>'
            f'{timeline(th)}'
            f'<div class="yard__filter">{btns}</div>{items}</div></section>')


# ----------------------------------------------------------------- shell ----
def shell(slug, title, desc, body, og=""):
    here = ' aria-current="page"'
    nav = "".join(
        f'<a href="/{s}/"{here if s == slug else ""}>{n}</a>'
        for s, n in [("market", "Market"), ("research-os", "Research OS"), ("film", "Film")])
    head_prod = (f'<link rel="canonical" href="https://nanditvaish.com/{slug}/">'
                 f'<meta property="og:title" content="{e(title)}">'
                 f'<meta property="og:description" content="{e(desc)}">'
                 f'<meta property="og:image" content="https://nanditvaish.com{og}">'
                 f'<meta name="twitter:card" content="summary_large_image">') if PROD else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} &mdash; Nandit Vaish</title>
<meta name="description" content="{e(desc)}">
{ROBOTS}{head_prod}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap">
<style>{BASE_CSS}{PAGE_CSS}</style></head><body>
<header class="mast"><div class="mast__in col-wide">
  <a class="mast__name" href="/">Nandit Vaish</a>
  <nav class="mast__nav">{nav}</nav>
</div></header>
{body}
<footer class="colophon"><div class="col-wide">
  <p>Built with Claude. The research, the mistakes and the decisions are Nandit's;
  a great deal of the code and the writing was done in conversation with it, and
  saying so is more interesting than pretending otherwise.</p>
  <p><a href="/">All work</a> &middot; <a href="mailto:vaishnandit@gmail.com">vaishnandit@gmail.com</a></p>
</div></footer>
<script>
/* graveyard filter */
(function(){{
  var bs=[].slice.call(document.querySelectorAll('.yard__filter button'));
  if(!bs.length)return;
  var cards=[].slice.call(document.querySelectorAll('.th'));
  bs.forEach(function(b){{b.addEventListener('click',function(){{
    bs.forEach(function(x){{x.classList.toggle('on',x===b)}});
    var f=b.dataset.f;
    cards.forEach(function(c){{
      c.style.display=(f==='ALL'||c.dataset.v===f)?'':'none';}});
  }})}});
}})();

/* layer switcher */
(function(){{
  var keys=[].slice.call(document.querySelectorAll('.mapx__keys button'));
  if(!keys.length)return;
  var imgs=[].slice.call(document.querySelectorAll('.mapx__stage img')),
      cap=document.querySelector('.mapx__cap');
  keys.forEach(function(b){{b.addEventListener('click',function(){{
    keys.forEach(function(x){{x.classList.toggle('on',x===b)}});
    imgs.forEach(function(i){{i.classList.toggle('on',i.dataset.m===b.dataset.m)}});
    cap.innerHTML=b.dataset.cap;
  }})}});
}})();

/* render ladder */
(function(){{
  var wrap=document.querySelector('.ladder'); if(!wrap)return;
  var caps=JSON.parse(wrap.dataset.caps),
      imgs=[].slice.call(wrap.querySelectorAll('img')),
      r=document.getElementById('ladr'),
      n=document.getElementById('ladn'),
      c=document.getElementById('ladc');
  function set(i){{
    imgs.forEach(function(im){{im.classList.toggle('on',+im.dataset.l===i)}});
    n.innerHTML='Pass '+(i+1)+' &middot; '+caps[i][0];
    c.innerHTML=caps[i][1];
  }}
  r.addEventListener('input',function(){{set(+r.value)}});
}})();

/* fill chart */
(function(){{
  var wrap=document.querySelector('.fillc'); if(!wrap)return;
  var rows=[].slice.call(wrap.querySelectorAll('.fillc__row')),
      bts=[].slice.call(wrap.querySelectorAll('.fillc__toggle button')),
      MAX=2.0;
  function draw(which){{
    rows.forEach(function(row){{
      var v=parseFloat(row.dataset[which==='m'?'m':'h']),
          bar=row.querySelector('.fillc__bar'),
          val=row.querySelector('.fillc__val'),
          w=Math.abs(v)/MAX*50;
      bar.style.width=w+'%';
      bar.style.left=(v>=0?50:50-w)+'%';
      bar.style.background=v>=0?'var(--live)':'var(--kill)';
      val.textContent=(v>0?'+':'')+v.toFixed(2)+'%';
      val.style.left=(v>=0?50+w+1.5:50-w-7)+'%';
      val.style.color=v>=0?'var(--live)':'var(--kill)';
    }});
  }}
  bts.forEach(function(b){{b.addEventListener('click',function(){{
    bts.forEach(function(x){{x.classList.toggle('on',x===b)}});
    draw(b.dataset.f);
  }})}});
  draw('m');
}})();

/* time player */
[].slice.call(document.querySelectorAll('.play')).forEach(function(w){{
  var years=JSON.parse(w.dataset.years),
      imgs=[].slice.call(w.querySelectorAll('img')),
      yr=w.querySelector('.play__yr'),
      btn=w.querySelector('.play__btn'),
      rng=w.querySelector('input'), t=null;
  function set(i){{
    imgs.forEach(function(im){{im.classList.toggle('on',+im.dataset.i===i)}});
    yr.textContent=years[i]; rng.value=i;
  }}
  function stop(){{clearInterval(t); t=null; btn.textContent='Play';}}
  btn.addEventListener('click',function(){{
    if(t) return stop();
    btn.textContent='Pause';
    t=setInterval(function(){{
      var i=(+rng.value+1)%years.length; set(i);
      if(i===years.length-1){{setTimeout(stop,900);}}
    }},900);
  }});
  rng.addEventListener('input',function(){{stop(); set(+rng.value)}});
}});

/* film scene lightbox */
(function(){{
  var lb=document.getElementById('lb'); if(!lb)return;
  var img=lb.querySelector('img');
  document.querySelectorAll('.scenes figure').forEach(function(f){{
    f.addEventListener('click',function(){{
      img.src=f.dataset.full; lb.classList.add('on');
    }});
  }});
  lb.addEventListener('click',function(){{lb.classList.remove('on')}});
  document.addEventListener('keydown',function(e){{
    if(e.key==='Escape') lb.classList.remove('on');
  }});
}})();

/* verdict timeline */
(function(){{
  var read=document.getElementById('tlread'); if(!read)return;
  var base=read.innerHTML;
  [].slice.call(document.querySelectorAll('.tl__dot')).forEach(function(d){{
    function show(){{
      read.innerHTML='<b>'+d.dataset.n+'</b> &middot; '+d.dataset.v+'<br>'+d.dataset.f;
    }}
    d.addEventListener('mouseenter',show);
    d.addEventListener('focus',show);
    d.setAttribute('tabindex','0');
  }});
  document.querySelector('.tl svg').addEventListener('mouseleave',function(){{
    read.innerHTML=base;
  }});
}})();
</script></body></html>"""


def head(when, h1, stand, facts):
    facts = [(when, "the working window")] + list(facts)
    f = "".join(f"<span><b>{n}</b>{l}</span>" for n, l in facts)
    return (f'<section class="head"><div class="col-wide">'
            f'<h1>{h1}</h1>'
            f'<p class="head__stand">{stand}</p>'
            f'<div class="head__facts">{f}</div></div></section>')


# =============================================================== MARKET =====
market = head(
    "Apr &ndash; Aug 2026",
    "Sixty ideas, run until they broke",
    "Four months of market research on 252 million rows of Indian equity and "
    "index-option history. It set out to find a signal and ended up building an "
    "instrument that can prove, cheaply and repeatedly, that a signal is not there.",
    [("252 M", "rows &middot; 188k parquet parts"), ("60", "threads run to a verdict"),
     ("41", "dead"), ("242,764", "lines of Python")],
) + ('<section class="ent"><div class="col-wide">' + plate(
    "/assets/hub/today.png",
    "Where four months of it ended up: the hub, on an ordinary Tuesday morning. Feed "
    "ages along the top, a choppiness reading with its percentile for each index, and a "
    "playbook line that turns all of that into one instruction. The table is headed in "
    "Hinglish because the thing was built for one person rather than for a market: <i>abhi kahan dekhna hai</i>, where to look right now.",
    "The trading hub's Today tab during market hours") + "</div></section>") + "".join([
    entry("01", "18 April 2026", "A chart, on a screen", [
        p("It started as a Flask dashboard scanning NSE equities for CPR, Camarilla, "
          "relative strength, reversals and fractal coils. The organising idea was a "
          "timeframe ladder: weekly reads yearly levels, daily reads monthly, "
          "four-hour reads weekly, and everything intraday reads the day."),
        p("The first data came from Yahoo Finance, and nine of those first 512 files "
          "were not Indian equities at all: crude, gold, copper, natural gas, palladium, "
          "platinum, silver, corn, wheat. There was a multi-asset scope, and it got "
          "dropped. Narrowing to NSE equity and index options was a deliberate early "
          "call, and the abandoned commodity leg is the evidence of it."),
        rule("The timeframe ladder survived the entire project as a way of looking. "
             "It died as an edge."),
    ]),
    entry("02", "May 2026", "Building the ground truth", [
        p("Upstox OAuth, the Nifty 500 matched against the instrument master, and a "
          "hive-partitioned parquet store: daily candles back to 2000, minute "
          "candles from 2022."),
        p("The detail that mattered was in the cleaner. Session detection became "
          "coverage-based and <i>era-relative</i>: a date counts as a real trading day "
          "only if at least a fifth of that year&rsquo;s active symbols traded. Before "
          "that fix it had been silently discarding pre-2010 days, because it was "
          "judging 2004 by how many symbols trade in 2025. Rows are removed; values are "
          "never touched."),
        rule("Clean by a rule that assumes today&rsquo;s market and you will quietly "
             "delete the past."),
    ]),
    entry("03", "June 2026", "Four strategies, three engine generations", [
        p("Camarilla long and short, CPR long and short, confluence long and short, "
          "across six timeframes, through three generations of engine."),
        p("The acceptance checklist was written down <i>before</i> anything ran: "
          "expectancy-per-risk at or above 0.10, at least 300 trades, profit factor "
          "1.25, at least 40% of symbols profitable, drawdown no worse than 20R. "
          "Settled design decisions were logged as &ldquo;do not revert&rdquo; with the "
          "reason attached to each."),
        rule("This is the point where it stopped being scripts and became a discipline."),
    ]),
    entry("04", "mid-June 2026", "The deployable", [
        p("Walk-forward logistic scoring ranked trades by win probability, and it "
          "worked: out-of-sample, the top quartile hit 75&ndash;92% win rate against "
          "42&ndash;44% for the bottom. Futures were modelled with real lot sizes and "
          "margin. Options were priced off actual bhavcopy premium rather than a "
          "formula. A live scanner ran on the Upstox REST API."),
        p("The headline was a Sharpe of 3.88, a maximum drawdown of &minus;5.7%, and a "
          "book that survived 2008 down only 4%."),
        p("<i>Every number in that paragraph is wrong. The next entry is why.</i>"),
    ]),
    entry("05", "17 June 2026", "The teardown", [
        p("Entry was booked at the level. But the signal only confirms once a bar "
          "<i>closes</i> beyond that level: on daily data, about 1.95% beyond it. "
          "You cannot fill at a price the bar has already left. The entire modelled edge "
          "was living inside that gap."),
        table(["Sleeve", "Modelled @ level", "Enter at close", "Retrace limit", "Verdict"],
              [["cam_daily_long", "+1.64%", "−0.30%", "−0.29%", "DEAD"],
               ["cpr_daily_long", "+1.72%", "−0.23%", "−0.14%", "DEAD"],
               ["cam_1H_short", "+0.50%", "−0.13%", "−0.04%", "DEAD"],
               ["cpr_1H_short", "+0.51%", "−0.14%", "−0.06%", "DEAD"]],
              "All four sleeves, gross, before costs. Only about 37% of trades ever "
              "reach an exit that beats the confirming close; for the other 63% "
              "the move is finished before you can act."),
        p("Flip between the two and watch every sleeve cross the line:"),
        fillchart(),
        pull("The signal is a lagging report that the move already happened."),
        p("Then we tried to rescue it. A stop order resting at the level fills on the "
          "touch, in real time, but it drags in exactly the fakeouts the closing "
          "confirmation had been screening out, roughly half of all touches, each losing "
          "between 0.6% and 2.7%. Three leading filters were pre-committed before "
          "testing: volume on approach, ADX primed, higher-timeframe trend. None "
          "of them clears cost. ADX made the daily book actively worse."),
        p("Four more biases fell out of the same audit. Survivorship inverted the trust "
          "ordering: the universe is the 2024 F&amp;O list projected backwards, so the "
          "long history is the <i>most</i> contaminated, and that famous &minus;4% in "
          "2008 is the book largely sitting the year out: thirteen trades against "
          "a normal fifty-four to sixty-nine. Capacity was fiction, arithmetic over tens "
          "of thousands of signals. Slippage was uncalibrated and charged nothing on "
          "entry. And the structure itself (which family, how many sleeves, which "
          "exits) had been chosen in-sample."),
        rule("Out of this came an audit lens: eight failure classes, ordered not by "
             "theory but by how often each one has actually killed an edge in this "
             "repository. Every later idea was run through it before it was believed."),
        p("One thing did survive the teardown, and not as a strategy. If the breakout "
          "side is dead because half of all touches fail, then the failures themselves "
          "are a population worth watching. That became a tab, and the tab argues "
          "with whoever opens it:"),
        plate("/assets/hub/failed_breaks.png",
              "Breaks classified <b>broke &rarr; failing &rarr; failed / reclaimed</b>, "
              "with live counters. The box at the top is a warning rather than a pitch: "
              "the fade tilt on choppy days is real and monotonic, <i>and</i> the "
              "mechanical average is about one basis point before costs. "
              "&ldquo;Trending &rarr; trade breakouts&rdquo; found no support at all.",
              "The Failed Breaks tab, showing its own caveat above the table"),
    ]),
    entry("06", "June &ndash; July 2026", "Honest costs, honest gates", [
        p("Brokerage is close to zero through the API, so the real costs are securities "
          "transaction tax and slippage. We rebuilt the round trip per vehicle from its "
          "components: 0.238% for cash delivery, 0.035% for cash intraday, 0.026% for "
          "futures. Spread was estimated with Corwin&ndash;Schultz, market impact with a "
          "square-root law."),
        rule("Relative strength, index regime and breadth are a risk dial, not a return "
             "booster. Tested both ways, they work as gates and add approximately "
             "nothing as scoring features."),
    ]),
    entry("07", "June &ndash; July 2026", "The options detour", [
        p("Two gigabytes of one-minute option chains across twelve underlyings, "
          "including expired contracts pulled through the expired-instruments API. We "
          "built the scalp book and ran it forward on paper."),
        p("Buying short-dated premium intraday is negative carry. It loses on average, "
          "always. What had looked like a momentum fade was entirely expiry-day theta, "
          "and cutting by days-to-expiry proved it."),
        rule("This programme was retired by decision rather than by statistics, and the repository records which of the two it was. They are not the "
             "same thing and should not be filed together."),
    ]),
    entry("08", "July 2026", "The kill factory", [
        p("Instead of hand-coding hypotheses one at a time, we built engines whose "
          "purpose is to reject them."),
        p("A <b>describer that cannot p-hack</b>: ten low-redundancy gauges per "
          "minute, z-scored using only the past, with outcomes measured from an entry "
          "you could actually have got, feeding a <b>judge</b> that demands a "
          "chronological split, trains at or before 2025, tests on held-out 2026, nets "
          "off costs, and uses robust statistics rather than means."),
        p("Alongside it: a hundred pre-registered hypotheses, none testable without "
          "approval. A factor zoo of 462 factors that collapsed to roughly two "
          "independent bets: size, and momentum, which turned out to be relative "
          "strength wearing a different name at a correlation of +0.98. A reinforcement "
          "learner trained on real level geometry against an identical agent trained on "
          "placebo twins, where <i>the profitable placebo was the alarm</i>."),
        p("Machine learning, astrology, Gann geometry and a TradingView indicator all "
          "went through the same bar and all died. The astrology engine was verified "
          "against Solar Fire to within 1.4 arcseconds first."),
        rule("Refusing to kill something for the wrong reason is part of killing it "
             "properly. A wrong result and a broken implementation look identical from "
             "the outside."),
    ]),
    entry("09", "July 2026", "Forensics on four real traders", [
        p("We took the machine and pointed it at actual trading records. Two thousand "
          "two hundred and fifty-eight trades decomposed: skill lands at p = 0.45, and "
          "the profit is one name. Another book&rsquo;s stated rule is dead, while its "
          "discretionary selection is real at p &asymp; 0.000: the trader was "
          "good at something other than the thing they believed they were doing. A "
          "+68.3% run over ten days turned out to have an entry that fails four "
          "different ways. A VCP playbook sign-flips on every lever when you move it "
          "from the F&amp;O list to a wide universe, which is survivorship."),
        rule("Traders cannot tell you what they actually do. The stated rule and the "
             "executed rule are different objects, and only one of them is in the data."),
    ]),
    entry("10", "10 July 2026", "The steward crisis", [
        p("The integrity checker had gone fifteen days without an update and was "
          "covering three of seven stores, because it <i>enumerated</i> what to "
          "check. Adding a store broke nothing; it simply went unchecked, forever. "
          "Meanwhile it was globbing one filename pattern while 499 symbols carried "
          "55,457 duplicate rows under a different one, and it reported clean. Three "
          "orphaned dashboard processes were squatting on ports, one of them twenty-five "
          "hours old."),
        pull("A checker that names what it checks can only find bugs in what it names."),
        p("The fix was architectural rather than diligent. A registry file became the "
          "declared desired state: every store, every service, every port. The "
          "session manager discovers what is actually on disk and running, and fails if "
          "anything is not declared. Add a directory and preflight goes red until you "
          "declare it."),
        rule("Drift is a failure, not a silent skip."),
        plate("/assets/hub/system.png",
              "The System tab today. Last night&rsquo;s refresh failed and it says so in "
              "red at the top rather than degrading quietly; every scheduled run carries "
              "a chip per step so a failure points at its own cause. The doctor reports "
              "0 fail, 1 warn, 58 pass. The single covered line is the broker "
              "account holder&rsquo;s name.",
              "The hub's System tab showing a failed end-of-day refresh"),
        go("/market/hub/", "All ten tabs"),
    ]),
    entry("11", "July 2026", "The live book, and the placebo", [
        p("A positional momentum book on relative strength went to forward paper "
          "trading. Then we tested it against a thousand dart-throwing placebos."),
        p("The selection is real: it beats random name-picking. But its Sharpe "
          "lands at roughly equal-weight buy-and-hold, which is a much less interesting "
          "claim. And the 48% compound headline splits into 85% across 2021&ndash;23 "
          "against 13.7% across 2024&ndash;26."),
        plate("/assets/hub/gati_paper.png",
              "The book as it runs. The fill assumptions are printed under the chart "
              "where they can be argued with: next-open entry, full costs, ten "
              "basis points of slippage, idle cash at six percent. The regime gate is "
              "off, so the watchlist is what the rules <i>would</i> buy and the position "
              "count is zero out of ten. The rupee figures are simulated capital.",
              "The GATI paper book, showing equity, watchlist and fill assumptions"),
        rule("Quote the regime numbers, never the headline. A single figure spanning "
             "two regimes is an average of two different businesses."),
    ]),
    entry("12", "August 2026", "The sweep, and what the literature actually offers", [
        p("We swept the public internet across six lanes looking for mechanical systems "
          "and found the same thing everywhere: there is no undiscovered entry signal "
          "out there. What the literature genuinely offers is the risk layer."),
        p("Ding&rsquo;s generalisation of Grinold gives the frame: information "
          "ratio is capped at IC divided by the volatility of IC, regardless of how much "
          "breadth you add. More bets cannot rescue an unstable signal."),
        table(["Pre-test", "Result", "Consequence"],
              [["AR(1) on monthly realised variance", "+0.114 <span style='color:#8b9098'>(US momentum: +0.578)</span>",
                "Volatility scaling discounted"],
               ["Effective number of bets", "10 names = 1.3 bets", "No sizing scheme can fix it"],
               ["Autocorrelation of own returns", "+0.126 <span style='color:#8b9098'>(universe: +0.004)</span>",
                "Drawdown stops back on the table"]],
              "The third result survived four adversarial controls: clean-mark "
              "repricing, fully-invested days only, market residual with beta removed, "
              "and a fixed sixty-day hold. A placebo of ten random names showed +0.009. "
              "It overturns the textbook dismissal of stops for this particular book."),
    ]),
    entry("13", "August 2026", "Kabaddi: turning the machine on the person", [
        p("The last thread pointed the instrument at its own operator. Four rounds of "
          "interviews: one spoken, twenty-two minutes, transcribed rather than "
          "translated so the Hinglish trading vocabulary survived intact; three typed, "
          "verbatim. The goal was to write down the discretionary system that actually "
          "gets traded, as a specification."),
        p("The specification surfaced a reframe that invalidates every mechanical test "
          "that came before it. The target is 0.7&ndash;0.8% in the underlying, which "
          "becomes roughly 10% on the premium, and then the position is closed. The "
          "daily level everyone was testing against sits 5&ndash;6% away, and is "
          "deliberately not the target."),
        pull("The system never needed the entry to predict direction. It needed the "
             "position to visit a small favourable excursion."),
        p("That is a question about the <i>path</i> a trade takes, not about where it "
          "ends. Every test in the repository up to this point had measured endpoints."),
        p("So we pre-registered 104 cells, split train at or before 2023, test across "
          "2024&ndash;25, holdout 2026. Cells clearing the null at p95, after cost, "
          "after a red-team pass: <b>zero</b>. Best net expectancy: &minus;12.95 basis "
          "points per trade. Random entry on the same stock-days beat the best signal by "
          "about ten points of compound annual return. Two candidates survived the first "
          "pass, were independently re-derived from raw data by separately written code, "
          "reproduced exactly &mdash; and were then destroyed by attacks that reversed "
          "their sign. A clean null, not an inconclusive one."),
        p("The durable output is not a signal. It is this, measured on a real account&rsquo;s "
          "actual behaviour:"),
        table(["Leverage", "With de-sizing", "Without de-sizing"],
              [["1&times;", "+4.7% CAGR &middot; −15.7% DD", "+6.9% &middot; −19.3%"],
               ["3&times;", "+7.8% &middot; −28.4%", "+16.8% &middot; −49.9%"],
               ["10&times; <span style='color:#8b9098'>(ATM-call proxy)</span>",
                "+9.2% &middot; −53.6%", "−0.6% &middot; −94.9% (p5: −99.7)"]],
              "At option-like leverage, without de-sizing, the median outcome is close to "
              "total ruin on a book that has positive expectancy. Of 9,955 signals only "
              "3,619 were taken and 6,444 were skipped for want of a slot. The "
              "account still loses. Capital was never the binding constraint. The edge was."),
        rule("Positive expectancy and survival are different properties. A book can have "
             "the first and still reliably destroy the account that trades it."),
    ]),
]) + graveyard() + """
<section class="bar"><div class="col-wide">
  <h2>The bar kept rising</h2>
  <p class="yard__intro">The most underrated thing in four months of work is not any
  single result. It is that the standard an idea had to clear went up, visibly, month after month, and several ideas that passed the early bar are dead at the
  late one.</p>
  <ol>
    <li><b>Expectancy &ge; 0.10R, at least 300 trades</b><span>The opening checklist,
      written before anything ran.</span></li>
    <li><b>Re-priced at a fill you could actually get</b><span>After the teardown.
      This one alone killed the entire first book.</span></li>
    <li><b>Net of a real cost floor</b><span>Rebuilt per vehicle from STT, spread
      and impact rather than assumed.</span></li>
    <li><b>Chronological held-out split</b><span>Train on the past, test on a period
      the search never saw.</span></li>
    <li><b>Measured against a calibrated null</b><span>Not against zero. Against what
      random entry does on the same days.</span></li>
    <li><b>Survives an adversarial red team</b><span>Someone actively trying to reverse
      the sign, using independently written code.</span></li>
    <li><b>t &gt; 3, for multiple testing</b><span>The Harvey&ndash;Liu&ndash;Zhu bar,
      because by now we had run hundreds of tests.</span></li>
  </ol>
</div></section>
"""

# ========================================================== RESEARCH OS =====
research = head(
    "Jul &ndash; Aug 2026",
    "A machine for finding the question",
    "Most research tooling helps you test a hypothesis. Almost none of it helps you "
    "find one worth testing. This is an attempt at the second thing, pointed at India "
    "from orbit, and then pointed at itself.",
    [("2.85 M", "rows &middot; 318,706 cells"), ("8", "layers on one join key"),
     ("4", "bugs caught before they became findings"), ("19 TB", "reduced to 242 MB")],
) + "".join([
    entry("01", "25 July 2026, 21:01", "Hour zero: one pixel, three formulas", [
        p("Before any data was pulled, one tile over Delhi was read and three "
          "de-quantisation formulas were tested against it. The obvious one, linear, produces vectors with a norm of about 2.5. The square law "
          "produces 1.0001, which is what a unit-sphere embedding is supposed to give."),
        rule("The discipline arrived before the data did. Had we scaled first and "
             "checked later, every number downstream would have been wrong and "
             "plausible."),
    ]),
    entry("02", "25 July 2026, 21:25", "The national pull", [
        p("Eleven thousand seven hundred and forty-nine tiles, nine years, fifty-one "
          "minutes. Read directly from cloud storage rather than downloaded, and sampled "
          "from the overview pyramid rather than at full resolution: nineteen "
          "terabytes of source becomes 242 megabytes by choosing the right level."),
        rule("Resolution is a decision, not a constraint. Most of the cost of a large "
             "dataset is spent before anyone asks how much detail the question needs."),
        p("Every layer below is drawn from the same 318,706 cells. Switch between them: the country is the same, only the question changes:"),
        mapswitch(),
        p("<i>The faint curved seams across the north are a known-open bug in the UTM "
          "zone joins. They are disclosed in the data dictionary and left visible here "
          "rather than retouched out.</i>"),
    ]),
    entry("03", "26 July 2026, 00:17", "A second domain, the same night", [
        p("Three hours after the first grid finished, we pointed the same method at "
          "something with nothing in common with satellites: NASA&rsquo;s battery "
          "ageing corpus. Thirty-six gigabytes from public storage, not the "
          "convenient mirror, which silently drops the impedance cycles. A MATLAB "
          "struct-array became five normalised tables and 7.28 million rows, and the "
          "data dictionary was written before any analysis ran."),
        rule("A research OS that only works on one dataset is a project. Proving it on "
             "an alien domain is what makes it an OS."),
    ]),
    entry("04", "27 July 2026", "Four connectors, two bugs", [
        p("Population, elevation, districts and built-up area were joined onto the grid. "
          "Two bugs came out of it, and both are the dangerous kind, because both "
          "produce numbers that look entirely reasonable."),
        p("A negative window offset shifted the whole population raster by 239 rows. "
          "Delhi came back at 263 people per square kilometre instead of 23,452, wrong by two orders of magnitude, and still a number you could put in a table "
          "without anyone blinking."),
        p("Summing counts over overlapping sample boxes gave India 1.75 billion people "
          "instead of 1.34 billion. Correct arithmetic on a wrong assumption: with "
          "overlapping windows you must take the mean, not the sum."),
        plate("/assets/maps/pop.jpg",
              "The population layer, read correctly. This is the plate that came back "
              "with Delhi at 263 people per square kilometre the first time, and "
              "it looked fine. Nothing about a shifted raster announces itself; the "
              "coastline still traces, the Gangetic plain is still bright. Only the "
              "cross-check against the census caught it.",
              "India rendered by population density"),
        rule("The bugs that matter do not crash. They return a plausible number, and the "
             "only defence is an external cross-check: total land area against "
             "the published figure, total population against the census."),
    ]),
    entry("05", "29 July 2026", "The dashboard, and its danger", [
        p("A hundred and thirty-two megabytes of binary layers, twelve views, a year "
          "slider with playback. It is the prettiest thing in the project and the least "
          "load-bearing. It looks like an answer."),
        plate("/assets/maps/cluster.jpg",
              "Twelve land types, clustered over the embedding. This is the view that "
              "does the most damage: it is beautiful, it is obviously "
              "<i>structured</i>, and structure is exactly what a person goes looking "
              "for. Six weeks later the referee showed that the layer underneath it "
              "cannot detect the thing we built it to detect.",
              "India rendered as twelve land-type clusters"),
        rule("A dashboard is a claim with the evidence removed. Everything on this one "
             "was true and none of it had been tested, and for a month nobody noticed "
             "the difference, including us."),
        go("/work/india-grid/", "Open the explorer"),
    ]),
    entry("06", "21 August 2026, 01:18", "The referee night", [
        p("A month after the instrument was finished, we turned it on our own results. "
          "Three hypotheses, three kills, each one chained to the last."),
        p("<b>Rainfall drives land-surface change.</b> Dead: a calendar artifact. "
          "A national year effect swings mean drift by 2.3&times;, and the two dry years "
          "happen to be the two lowest-drift years."),
        p("<b>Fine, but the swing itself is real.</b> Dead: the ordering is "
          "inverted. Water drifts 2.11&times; and desert 1.88&times; against cropland, "
          "while built-up land drifts 0.74&times;. Construction makes land <i>stiller</i>."),
        p("<b>Fine, but it still detects real change.</b> Dead: matched against "
          "an independent forest-loss dataset, the detector scores an AUC of 0.486. "
          "That is worse than a coin."),
        rule("Each kill was the referee check on the previous one. Three rounds of "
             "&ldquo;fine, but&rdquo; is what an honest retreat looks like written down."),
    ]),
    entry("07", "21 August 2026, 02:14", "Five pre-registered questions", [
        p("Predictions written in code before the test ran. Two killed, two partial, "
          "one answered."),
        p("The humiliating one: a baseline of &ldquo;where it grew before, it grows "
          "again&rdquo; predicts construction at an AUC of 0.977. The satellite "
          "embedding manages 0.60. A single lag of the target beats the entire "
          "sixty-four-dimensional apparatus by a distance."),
        rule("A trivial baseline is not a formality. Run it first, or you will spend a "
             "month measuring something a single lagged variable already knew."),
    ]),
    entry("08", "&mdash;", "What survived", [
        p("Rainfall <i>volatility</i> moves the land surface at a rank correlation of "
          "0.357 against a null of 0.000. Rainfall <i>level</i> does not. Those are "
          "different claims and only one of them holds."),
        p("India&rsquo;s built-up growth is a fringe phenomenon: 74.6% of "
          "2015&ndash;20 growth landed on cells that were already between 0.5% and 5% "
          "built, up from 60.2% in the 1990s. It is the one clean positive result in "
          "the project, and it uses no embeddings at all."),
        p("Press play. Thirty-five years of building, on one fixed colour scale so the "
          "growth is real rather than a rescaling artifact:"),
        player("built", SERIES.get("built", []), "built-up area",
               "Built-up fraction, 1990 to 2025. Watch the corridors thicken between "
               "the cities rather than the city centres themselves getting brighter: that is the fringe result, visible without a single statistic."),
        rule("The reframe worth the month: the instrument measures surface volatility, "
             "not development. That is a real thing to have built. It is simply not the "
             "thing we set out to build, and saying so is cheaper than defending it."),
    ]),
]) + """
<section class="bar"><div class="col-wide">
  <h2>Flagged, not resolved</h2>
  <p class="yard__intro">The repository has a verbal tic that turned out to be its best
  quality. It appears on duplicate archives, on an unreadable weights file, on the UTM
  seams, on a licence question. It is worth making explicit, because it is the thing
  that lets one document serve a peer and a client without lying to either.</p>
  <ol>
    <li><b>Verified</b><span>Measured, with the measurement shown.</span></li>
    <li><b>Observed</b><span>Read directly off the artifact.</span></li>
    <li><b>Inferred</b><span>Deduced but not confirmed. Treat as a hypothesis.</span></li>
    <li><b>Flagged</b><span>Known-open, not fixed, and deliberately not smoothed
      over.</span></li>
  </ol>
</div></section>
"""

# ================================================================= FILM =====
film = head(
    "Jul &ndash; Aug 2026",
    "A city of six shapes, and a film about robots",
    "Twenty-five days inside Unreal Engine, which began as &ldquo;make me a simple "
    "movie&rdquo; and turned into an argument about which parts of a creative process "
    "can be automated and which absolutely cannot.",
    [("6", "primitive shapes, one city"), ("~95", "hand-built materials"),
     ("1,158", "frames across six render passes"), ("3:00", "finished film, shipped")],
) + "".join([
    entry("01", "31 July 2026", "The GUI era, and why it had to die", [
        p("Day one ran two things in parallel, and the tension between them turned out "
          "to be the whole project. One was screen automation: taking over the "
          "editor and clicking through it. The other was a scripting bridge over the "
          "engine&rsquo;s own remote-execution protocol, written the same morning."),
        p("The screen approach broke on its own terms within hours: it stops responding, "
          "the view does not move, the camera is unfathomable. But the fatal objection "
          "was not fragility."),
        pull("We are stuck with what the agent can do. We never really explore "
             "what&rsquo;s possible, all options come out of that same number "
             "of combinations."),
        rule("Screen control is non-deterministic, and an options system depends on "
             "reproducibility. You cannot generate three comparable variants if the same "
             "input gives a different output. Scripting was not a convenience; it was "
             "the precondition for having choices at all."),
    ]),
    entry("02", "5 August 2026", "The cyberpunk street, in one very long day", [
        p("Around forty scripts, in an order you can read straight off the filenames: "
          "build the street, fix the street, rebuild it curved, make it cyberpunk, "
          "detail the buildings, a second detail pass, props, street furniture: bins, newspaper stands, stop signs, zebra crossings, hydrants. Then neon "
          "signage generated from scratch, then night, then blue hour, then sky, then "
          "three grading passes to land on &ldquo;just about sunset, street lights just "
          "coming on&rdquo;. Then rain textures, then a Niagara particle system. Then "
          "navigation, a walker, a camera move, and six render passes."),
        p("The geometry underneath all of it is six primitive shapes. No models, no "
          "asset packs. A whole noir street out of boxes, cylinders and light."),
        p("The method that produced the detail has a name now, though it did not then: comparison against reality, deliberately: <i>the wires are straight, "
          "and in reality wires are tangled, they have smaller wires wrapped around "
          "them, they are never this straight, they sag in the middle.</i>"),
        p("Drag through the six render passes. The set never changes across them: what changes is where the camera stands, who is in the shot, and how "
          "hard it is raining:"),
        ladder(),
        rule("The bottleneck was never the engine. It was review latency: &ldquo;do I have to render it every time to see what&rsquo;s happening?&rdquo; "
             "Everything good that came later descends from that question."),
    ]),
    entry("03", "6 August 2026", "Don&rsquo;t jump the gun", [
        p("The morning after the street, the work stopped: no scene, nothing built, "
          "because none of the specifications existed yet. What came out of that was a "
          "twenty-thousand-word operating contract, and it is the single most valuable "
          "artifact in the whole body of work: more than the street, more than "
          "the film."),
        p("<b>The operator model.</b> It describes the human as &ldquo;merely a taste "
          "factor&rdquo;, and takes that literally: no editing skill, no engine "
          "knowledge. You can run a command, paste an error, record your voice, judge an "
          "image, and pick one of three. Every interaction is designed inside that "
          "envelope. The corollary is the useful half: you can reliably detect "
          "that something is wrong but rarely say why, so producing the signal is your "
          "job and translating it into a rule is the machine&rsquo;s."),
        p("<b>The render ladder.</b> A one-minute contact sheet for a whole video is the "
          "primary review surface. Cheap regeneration is what makes &ldquo;none of "
          "these, do it again&rdquo; a rule you actually keep rather than one you "
          "abandon under time pressure."),
        p("<b>The closed rejection menu.</b> Nine permitted complaints: too fast, "
          "too busy, can&rsquo;t read it, doesn&rsquo;t sound like me, looks generic, I "
          "don&rsquo;t believe it, nothing happened, saw it coming, lost me at a "
          "timestamp. A closed vocabulary is what makes taste into data."),
        p("<b>Audio is the master clock.</b> Voice first, all timing derived from it, which converts pacing from an editing skill nobody has into a "
          "performance decision anyone can make at a microphone."),
        pull("The slop feeling does not come from using AI. It comes from automating "
             "judgement."),
        rule("Agents do not learn; documents do. The compounding asset across a month "
             "of work was a single markdown file."),
    ]),
    entry("04", "August 2026", "Money behaves like a gas", [
        p("The first episode takes a 2000 paper on kinetic exchange and builds it. Two "
          "thousand agents each start with exactly one hundred. Two are picked at "
          "random, their holdings pooled, the pool split at random. Nobody is smarter, "
          "nobody cheats, and the total is conserved: asserted in the code, not "
          "assumed."),
        p("It converges to the Boltzmann&ndash;Gibbs distribution: the same law that "
          "describes how energy distributes among molecules in a gas. Inequality rises "
          "from nothing but fair trades."),
        p("<b>And then the break</b>, which is the part that makes it honest rather than "
          "a party trick. The exponential fits roughly the bottom 90% of real income "
          "data. The top 1% follows a power law that random exchange cannot produce at "
          "any runtime. The physics explains the unremarkable part of the distribution "
          "and fails exactly where the argument actually is."),
        rule("The break is non-negotiable. Without it, a channel about hidden structure "
             "becomes a channel about everything being connected, which is the same "
             "genre as astrology."),
        go("/#sim", "Run the simulation on the home page"),
    ]),
    entry("05", "20&ndash;22 August 2026", "Humanoids 2050", [
        p("A detour that became the only finished film. It takes a bank&rsquo;s "
          "humanoid-robot projection and gives every number in it a scene: the hands "
          "alone at $9,315 against a human hand&rsquo;s 27 degrees of freedom; sensors "
          "at 37% of the bill of materials; six models unveiled in 2022 against "
          "fifty-one in 2024; China at 5,688 patents in five years against "
          "America&rsquo;s 1,483."),
        p("Three structural inventions hold it together. <b>Every chapter opens on a "
          "question card</b>, which doubles as a valid start point for a short-form cut. "
          "<b>A two-tone system</b> where warm is always cost, China, acceleration and "
          "the uncomfortable side of any comparison, and cool is cheap, America and the conservative number; the room itself is cool, so warm reads as "
          "intrusion. And <b>one time axis</b>: the entire video is a single element "
          "tree rendered as a pure function of time, so nothing mounts or unmounts at a "
          "scene boundary and editing one duration re-times everything downstream."),
        filmplayer(),
        p("Every scene, in order. Watch the two-tone rule hold across all of them: cost, China and acceleration are always warm; the machine, America "
          "and the conservative number are always cool:"),
        scenes(),
        rule("The story was never the billion units. It was the flat decade: the "
             "ten years in the middle where nothing visible happens."),
    ]),
    entry("06", "August 2026", "The voice problem, which is not solved", [
        p("Several synthesis models were tried and rejected in the same words each time: "
          "shrill, mechanical, sounds like it came from a machine. A self-recorded take "
          "was rejected too, and then the honest objection arrived: the delivery "
          "is monotonous, not the timbre."),
        p("The response was not a better model. It was measurement. A delivery plan "
          "fits every line to its scene window and records, per line: the hard limit, "
          "the designed duration, the word count, the measured duration, the resulting "
          "words per minute, whether it fits, a speed multiplier, padding, and a shaped "
          "rewrite. Alongside it, a cue sheet with continuous room tone across the full "
          "three minutes, ticks while a counter runs, and an impact when a reveal lands."),
        p("Nine voices were auditioned as an options system. Nine builds shipped, "
          "including one in Nandit&rsquo;s own voice."),
        rule("When the generative approach fails, the fallback is not a better generator. "
             "It is measuring the thing you were hoping the generator would intuit."),
    ]),
    entry("07", "&mdash;", "The open ledger", [
        p("Several directories the contract refers to are still empty. Three documents "
          "it cites do not exist. The scene-kit module is a zero-byte file. The style "
          "decision is still open, which is precisely why the only renderer is named "
          "<i>scratch</i>. And the Unreal craft work and the channel system have never actually met: the first episode is drawn with a plotting library, not "
          "the engine."),
        rule("A recap that hides this is a brochure. One that shows it is a research "
             "log, and it is far more convincing."),
    ]),
])

# ------------------------------------------------------------------ write ---
PAGES = [
    ("market", "Sixty ideas, run until they broke",
     "Four months of market research over 252 million rows: the teardown, the "
     "graveyard of 41 dead hypotheses, and the acceptance bar that kept rising.",
     market, "/assets/hub/today.png"),
    ("research-os", "A machine for finding the question",
     "India from orbit on a five-kilometre grid, four bugs caught before they became "
     "findings, and the night we turned the referee on our own results.",
     research, "/assets/plates/grid-poster.jpg"),
    ("film", "A city of six shapes, and a film about robots",
     "Twenty-five days in Unreal Engine: a neon street built from primitives, an "
     "operating contract, and a three-minute film shipped in nine builds.",
     film, "/assets/plates/street-poster.jpg"),
]

for slug, title, desc, body, og in PAGES:
    d = OUT / slug
    d.mkdir(exist_ok=True)
    h = shell(slug, title, desc, body, og)
    (d / "index.html").write_text(h, encoding="utf-8")
    print(f"built {slug}/index.html  {len(h):>7,} bytes")
print(f"\n{'PROD' if PROD else 'preview, noindex'}")
