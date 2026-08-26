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

.go{display:inline-block;margin:1.75rem 0;font-family:var(--mono);font-size:.6875rem;
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

/* ---------- interactive: sector rotation ---------- */
.rrg{margin:2.5rem 0}
.rrg__stage{position:relative;background:var(--plate);border:1px solid var(--rule-2)}
.rrg__stage canvas{width:100%;display:block}
.rrg__ctl{display:flex;align-items:center;gap:.9rem;margin-top:.9rem;flex-wrap:wrap}
.rrg__ctl input{flex:1;min-width:10rem;accent-color:var(--kill)}
.rrg__date{font-family:var(--mono);font-size:.6875rem;letter-spacing:.1em;
  color:var(--ink-2);min-width:7rem}

/* ---------- interactive: verdict timeline ---------- */
.tl{margin:2.25rem 0;overflow-x:auto}
.tl svg{width:100%;min-width:40rem;height:auto;display:block;overflow:visible}
.tl__dot{cursor:pointer;transition:r .15s ease}
.tl__dot:hover{r:6}
.tl__read{font-family:var(--mono);font-size:.75rem;color:var(--ink-2);margin-top:1rem;
  min-height:3.4em;max-width:46rem}
.tl__read b{color:var(--ink);font-weight:500}

/* ---------- operations ---------- */
.bound{margin:2.25rem 0;padding:1.1rem 1.25rem;border:1px solid var(--rule-2);
  max-width:var(--measure);font-size:.9375rem;color:var(--ink-2)}
.bound b{color:var(--ink);font-weight:500}
.wall{margin:2.5rem 0;display:grid;gap:6px;grid-template-columns:repeat(2,1fr)}
@media (min-width:40rem){.wall{grid-template-columns:repeat(4,1fr)}}
.wall img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block;
  background:var(--plate);border:1px solid var(--rule-2)}

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


_cf = OUT / "assets/charts/charts.json"
CH = json.loads(_cf.read_text()) if _cf.exists() else {}

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
    return ('<figure class="vid" id="watch"><video controls preload="metadata" '
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


def breadth_widget():
    cap = (f"Today it reads {CH.get('breadth_now_50',0)}% above the 50-day and "
           f"{CH.get('breadth_now_200',0)}% above the 200-day, drawn day by day "
           "across five and a half years.")
    return ('<div class="rrg"><div class="rrg__stage">'
            '<canvas id="brdc" width="1240" height="640" '
            'aria-label="Breadth of the universe above its own moving averages, animated weekly"></canvas></div>'
            '<div class="rrg__ctl"><button class="play__btn" id="brdb">Play</button>'
            '<input type="range" id="brdr" min="0" max="10" value="10" step="1" '
            'aria-label="Week"><span class="rrg__date" id="brdd"></span></div>'
            f'<p class="mapx__cap">{cap}</p></div>')


def rrg():
    return ('<div class="rrg"><div class="rrg__stage">'
            '<canvas id="rrgc" width="1240" height="780" '
            'aria-label="Sector rotation: relative strength against its own momentum, animated weekly"></canvas></div>'
            '<div class="rrg__ctl"><button class="play__btn" id="rrgb">Play</button>'
            '<input type="range" id="rrgr" min="8" max="10" value="8" step="1" '
            'aria-label="Week"><span class="rrg__date" id="rrgd"></span></div></div>')


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


def entry(no, when, title, blocks, eid=None):
    aid = f' id="{eid}"' if eid else ""
    return (f'<section class="ent"{aid}><div class="col-wide">'
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
        for s, n in [("market", "Market"), ("research-os", "Research OS"), ("film", "Film"), ("operations", "Operations")])
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

/* breadth, playable */
(function(){{
  var cv=document.getElementById('brdc'); if(!cv)return;
  var btn=document.getElementById('brdb'), rng=document.getElementById('brdr'),
      dt=document.getElementById('brdd'), ctx=cv.getContext('2d'), D=null, t=null;
  var W=cv.width,H=cv.height,L=58,R=16,T=40,B=36;
  function X(i){{return L+(W-L-R)*i/(D.dates.length-1)}}
  function Y(v){{return T+(H-T-B)*(1-v/100)}}
  function draw(i){{
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#0a0b0d';ctx.fillRect(0,0,W,H);
    ctx.strokeStyle='#1d2127';ctx.lineWidth=1;
    ctx.font='11px "IBM Plex Mono",monospace';
    for(var g=0;g<=100;g+=20){{
      ctx.beginPath();ctx.moveTo(L,Y(g));ctx.lineTo(W-R,Y(g));ctx.stroke();
      ctx.fillStyle='#8b9098';ctx.fillText(String(g),L-30,Y(g)+4);
    }}
    ctx.setLineDash([4,4]);ctx.strokeStyle='#8b9098';
    ctx.beginPath();ctx.moveTo(L,Y(50));ctx.lineTo(W-R,Y(50));ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle='#e9e7e4';
    ctx.fillText('BREADTH \u00b7 SHARE OF THE UNIVERSE ABOVE ITS OWN MOVING AVERAGE',L,22);
    for(var j=1;j<=i;j++){{
      var v0=D.b50[j-1],v1=D.b50[j]; if(v0==null||v1==null)continue;
      ctx.fillStyle=(v1>=50)?'rgba(47,158,131,.12)':'rgba(174,47,34,.16)';
      ctx.beginPath();
      ctx.moveTo(X(j-1),Y(50));ctx.lineTo(X(j-1),Y(v0));
      ctx.lineTo(X(j),Y(v1));ctx.lineTo(X(j),Y(50));ctx.closePath();ctx.fill();
    }}
    function series(arr,col,lw){{
      ctx.strokeStyle=col;ctx.lineWidth=lw;ctx.beginPath();var m=false;
      for(var j=0;j<=i;j++){{var v=arr[j];if(v==null){{m=false;continue}}
        var x=X(j),y=Y(v); if(!m){{ctx.moveTo(x,y);m=true}}else ctx.lineTo(x,y);}}
      ctx.stroke();
    }}
    series(D.b200,'#6b7280',1.1);
    series(D.b50,'#e9e7e4',1.6);
    var v=D.b50[i];
    if(v!=null){{ctx.fillStyle='#e0705f';ctx.beginPath();
      ctx.arc(X(i),Y(v),4,0,7);ctx.fill();}}
    dt.textContent=D.dates[i]+' \u00b7 '+(D.b50[i]==null?'\u2014':D.b50[i]+'%');
    rng.value=i;
  }}
  function stop(){{clearInterval(t);t=null;btn.textContent='Play'}}
  fetch('/assets/charts/breadth.json').then(function(r){{return r.json()}})
  .then(function(d){{
    D=d;rng.max=d.dates.length-1;rng.value=d.dates.length-1;
    draw(d.dates.length-1);
    btn.addEventListener('click',function(){{
      if(t)return stop();
      btn.textContent='Pause';
      var i=+rng.value; if(i>=d.dates.length-1)i=0;
      t=setInterval(function(){{
        i=Math.min(i+5,D.dates.length-1);if(i>=d.dates.length){{stop();return}}
        draw(i);
      }},45);
    }});
    rng.addEventListener('input',function(){{stop();draw(+rng.value)}});
  }});
}})();

/* sector rotation */
(function(){{
  var cv=document.getElementById('rrgc'); if(!cv)return;
  var btn=document.getElementById('rrgb'), rng=document.getElementById('rrgr'),
      dt=document.getElementById('rrgd'), ctx=cv.getContext('2d'), D=null, t=null;
  var PAL=['#e0705f','#2f9e83','#f2b45c','#7aa2f7','#c792ea','#8fbf6d','#e39fc2',
           '#5fb4c9','#d0885f','#9aa5ce','#c9c05f','#6fcf97','#bf6f8f'];
  var W=cv.width,H=cv.height,CX=W/2,CY=H/2,S=34;   // px per unit around 100,100
  function px(v){{return CX+(v-100)*S}}
  function py(v){{return CY-(v-100)*S}}
  function draw(i){{
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#0a0b0d';ctx.fillRect(0,0,W,H);
    ctx.fillStyle='rgba(47,158,131,.05)';ctx.fillRect(CX,0,W-CX,CY);
    ctx.fillStyle='rgba(174,47,34,.05)';ctx.fillRect(0,CY,CX,H-CY);
    ctx.strokeStyle='#23262c';ctx.lineWidth=1;
    ctx.beginPath();ctx.moveTo(CX,0);ctx.lineTo(CX,H);ctx.moveTo(0,CY);ctx.lineTo(W,CY);ctx.stroke();
    ctx.font='11px "IBM Plex Mono",monospace';ctx.fillStyle='#5c636d';
    ctx.fillText('IMPROVING',14,20);ctx.fillText('LEADING',W-76,20);
    ctx.fillText('LAGGING',14,H-12);ctx.fillText('WEAKENING',W-86,H-12);
    D.sectors.forEach(function(sec,k){{
      var col=PAL[k%PAL.length];
      ctx.strokeStyle=col;ctx.globalAlpha=.55;ctx.lineWidth=1.4;ctx.beginPath();
      var moved=false;
      for(var j=Math.max(0,i-8);j<=i;j++){{
        var x=sec.x[j],y=sec.y[j];
        if(x==null||y==null)continue;
        var X=px(x),Y=py(y);
        if(!moved){{ctx.moveTo(X,Y);moved=true}}else ctx.lineTo(X,Y);
      }}
      ctx.stroke();ctx.globalAlpha=1;
      var x=sec.x[i],y=sec.y[i]; if(x==null||y==null)return;
      var X=px(x),Y=py(y);
      ctx.fillStyle=col;ctx.beginPath();ctx.arc(X,Y,5,0,7);ctx.fill();
      ctx.fillText(sec.code,X+8,Y+4);
    }});
    dt.textContent=D.weeks[i];rng.value=i;
  }}
  function stop(){{clearInterval(t);t=null;btn.textContent='Play'}}
  fetch('/assets/charts/sectors.json').then(function(r){{return r.json()}})
  .then(function(d){{
    D=d;rng.max=d.weeks.length-1;rng.value=d.weeks.length-1;
    draw(d.weeks.length-1);
    btn.addEventListener('click',function(){{
      if(t)return stop();
      btn.textContent='Pause';
      var i=+rng.value; if(i>=d.weeks.length-1)i=8;
      t=setInterval(function(){{
        i++;if(i>=d.weeks.length){{stop();return}}
        draw(i);
      }},110);
    }});
    rng.addEventListener('input',function(){{stop();draw(+rng.value)}});
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
    "instrument that can prove, cheaply and repeatedly, that a signal is not there. "
    "What cleared the bar instead is not a prediction: discretionary selection, and "
    "the management of the trade after the fill.",
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
        plate("/assets/charts/store.png",
              f"The store itself: symbols with data, per year, {CH.get('rows',0):,} "
              "deduplicated daily rows across "
              f"{CH.get('symbols',502)} names. The early years sit far below today&rsquo;s "
              "coverage, which is exactly why the cleaner judges each date against "
              "<i>its own year&rsquo;s</i> active names rather than 2025&rsquo;s.",
              "Bar chart of symbols with data per year, 2000 to 2026"),
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
        plate("/assets/charts/gap.png",
              f"The gap, recomputed from the store for this page: every close beyond "
              f"the previous day&rsquo;s H4 across all {CH.get('symbols',502)} names and "
              f"twenty-six years &mdash; {CH.get('gap_n',0):,} confirmations, median "
              f"{CH.get('gap_median',0)}% past the level, using the repository&rsquo;s own "
              "formula. The notebook&rsquo;s ~1.95% was measured on its filtered signal "
              "population; unconditionally the median is smaller and the argument is the "
              "same. Everything red was never fillable at the level.",
              "Histogram of how far beyond the level the confirming close sits"),
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
        p("Here is the dial itself, computed from the store and playable. Press play "
          "and watch five and a half years of participation breathe: the share of all "
          "502 names above their own 50-day average (bright) and 200-day average "
          "(faint). Green when the majority is participating, red when it is not."),
        breadth_widget(),
        p("And the rotation the hub&rsquo;s sector tab watches, running on the real "
          "data. Each dot is a sector&rsquo;s relative strength against the universe, "
          "plotted against the momentum of that strength; the tail is its last eight "
          "weeks. Press play and watch " + str(CH.get('rrg_weeks', 270)) + " weeks of "
          "money moving between sectors:"),
        rrg(),
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
    entry("11", "standing since 8 July 2026", "The second brain", [
        p("The research corpus is hundreds of documents, and the reason it stays "
          "usable is a rule, not a tool: an Obsidian vault sits over the whole "
          "repository, and a standing instruction requires every new diagnostic, "
          "spec or finding to join the graph <i>connected</i>, never as an orphan "
          "node. One hundred and fifty-eight notes, one hundred and ninety links "
          "between them."),
        plate("/assets/ops/brain.png",
              "The vault, drawn from its own wikilinks: one continent and two "
              "satellites. The named hubs are the same objects as the graveyard "
              "above (CPR-Camarilla, Nifty-Scalp, RS-Rotation) because the verdict "
              "pages and the knowledge graph are one system, not two.",
              "Force-directed graph of the research vault's notes and links"),
        rule("A finding you cannot find again will be paid for twice. The graph is "
             "cheaper than the second discovery."),
    ]),
    entry("12", "July 2026", "The live book, and the placebo", [
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
        plate("/assets/charts/regimes.png",
              f"The tape the book traded into, computed from the store: the universe, "
              f"equal-weight, indexed to 100 at January 2021. It compounds at "
              f"+{CH.get('regime1_cagr',0)}% a year through 2021&ndash;23 and "
              f"+{CH.get('regime2_cagr',0)}% after &mdash; the same regime split, in the "
              "market itself. One caveat this page has already taught: this is "
              "today&rsquo;s 502-name list projected backwards, so the early segment "
              "carries survivorship shine.",
              "Equal-weight index of the universe from 2021, split at the 2024 regime boundary"),
        rule("Quote the regime numbers, never the headline. A single figure spanning "
             "two regimes is an average of two different businesses."),
    ]),
    entry("13", "August 2026", "The sweep, and what the literature actually offers", [
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
    entry("14", "August 2026", "Kabaddi: turning the machine on the person", [
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
        plate("/assets/charts/kabaddi.png",
              "The table above, drawn. Each bar spans from what the book earns each "
              "year (top cap) down to the worst drawdown it takes on the way (bottom "
              "cap). De-sizing on the left of each pair, off on the right. At "
              "10&times; without de-sizing the median outcome is &minus;94.9% and the "
              "fifth percentile is &minus;99.7 &mdash; ruin, on a book with positive "
              "expectancy. These are the notebook&rsquo;s simulation results, drawn "
              "as published, not recomputed.",
              "Leverage against survival: CAGR versus maximum drawdown per configuration"),
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
<section class="bar"><div class="col-wide">
  <h2>What cleared the bar</h2>
  <p class="yard__intro">The signal layer proved nothing. Across sixty threads, a
  hundred pre-registered hypotheses and 104 pre-registered kabaddi cells, not one
  entry pattern carried strength that survived the list above: not levels, not
  machine-learned policies, not fitted geometry, not folklore. That result is the
  product, not the casualty. The instrument exists so this sentence could be said
  with evidence rather than exhaustion.</p>
  <p class="pull">Where to enter never cleared the bar. How much to carry, and
  when to cut, did.</p>
  <p class="yard__intro">Two things survived, and both were measured rather than
  believed. Discretionary selection is real: a trader&rsquo;s stated rule died
  under the machine while the selection underneath it tested at
  p&nbsp;&asymp;&nbsp;0.000 (entry 09), and the kabaddi book, written down as a
  specification, carries positive expectancy (entry 14). And trade management is
  where outcomes are actually decided: the identical book at option-like leverage
  lands at +9.2% a year with de-sizing against a median of &minus;94.9% without it
  (entry 14), and the single result the literature sweep left standing was a
  drawdown stop, not an entry (entry 13). The returns are not the claim. The
  asymmetry is: every attempt to time an entry died, and what survived is
  selection, sizing, and the exit.</p>
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
    "A month inside Unreal Engine, which began as &ldquo;make me a simple "
    "movie&rdquo; and turned into an argument about which parts of a creative process "
    "can be automated and which absolutely cannot.",
    [("6", "primitive shapes, one city"), ("~95", "hand-built materials"),
     ("1,158", "frames across six render passes"), ("3:00", "finished film, shipped")],
) + ('<section class="col-wide">'
     + go("#watch", "The film is real and three minutes long. Watch it first")
     + "</section>") + "".join([
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
    entry("02", "early August 2026", "The cyberpunk street: forty scripts, six renders", [
        p("The street went up in layers, and the layers are still legible in the script names, right down to the marathon session where most of it landed: "
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
        p("The first film the whole machine shipped end to end: research, twenty-five "
          "scenes, voice, sound and nine builds. It takes a bank&rsquo;s "
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
table(["#", "Line, as shaped", "Window", "Measured", "wpm", "Fits"], [['01', 'Two hundred thousand dollars.', '3.2s', '3.16s', '76', '&#10003;'], ['06', 'It is shaped like us because the world is al&hellip;', '3.8s', '3.68s', '228', '&#10003;'], ['12', 'None of this scales until it gets cheap. So &hellip;', '5.0s', '4.93s', '134', '&#10003;'], ['18', 'Then in the late 2030s the line stops behavi&hellip;', '4.2s', '4.17s', '173', '&#10003;'], ['24', 'Five trillion dollars a year in revenue.', '3.6s', '0.70s', '600', '&#10003;'], ['30', 'China, mostly. Three hundred and two million&hellip;', '8.0s', '8.00s', '142', '&#10003;'], ['35', "Morgan Stanley's billion is … the conservati&hellip;", '3.4s', '0.81s', '519', '&#10003;']], "Seven of the thirty-five lines. Every line carries its hard limit, its measured read, the words-per-minute that implies, and a fits flag; after shaping, all thirty-five fit, at paces from 76 to 600 words a minute. Pacing became arithmetic, not feel."),
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

WALL = ["punyas-kriti","poshak-boutique","queen-madonna","beauty-life-salon",
        "dr-mona-prabhakar","peaches-and-cream","beast-mode-gym","asha-clinic",
        "british-unisex-salon","modern-looks-salon","empire-of-fitness","anagh-routes",
        "bodyline-gym","rd-creations","v-sachdeva-associates","queen-madonna-premium"][:16]


def wall():
    seen, imgs = set(), ""
    for w in WALL:
        if w in seen:
            continue
        seen.add(w)
        imgs += (f'<img src="/assets/ops/work/{w}.webp" alt="Demo site: '
                 f'{w.replace("-", " ")}" loading="lazy" decoding="async">')
    return f'<div class="wall">{imgs}</div>'


operations = head(
    "May 2026 &ndash; present",
    "The machinery behind the studio",
    "Lantern, the website studio, is the storefront. This page is the back room: the "
    "agent that ran a company&rsquo;s socials under human approval, the engines that "
    "find the work, the pipeline that personalises a website in twenty minutes, and "
    "the generators that write the paperwork. One venture here is parked and listed "
    "anyway, because a ledger that only shows what worked is marketing. If you are "
    "reading this page wondering whom any of it is for, "
    '<a href="#for-you">the last entry answers exactly that</a>.',
    [("16", "demo sites on the shelf"), ("381", "leads in the master book"),
     ("13", "agent drafts awaiting approval, on disk today"),
     ("18", "document generators, zero hand-made paperwork")],
) + ('<section class="col-wide"><div class="bound"><b>What this page shows and '
     'withholds.</b> Volumes are real and current. Rates, conversion numbers, client '
     'economics and lead sources are deliberately absent: the same boundary the '
     'trading hub draws, for the same reason.</div></section>') + "".join([
    entry("01", "May &ndash; June 2026", "ClearFlow, the first venture", [
        p("Before Lantern there was ClearFlow: a spreadsheet-automation consultancy, "
          "born from a KPMG observation: almost every small business runs on a "
          "spreadsheet built by one employee years ago that the whole company depends "
          "on and nobody dares touch."),
        p("It was built like a real company. A brand with a written voice guide "
          "(fourteen kilobytes of it before a single client). Worked case studies. A "
          "lead scraper and calling lists. And the site doubled as a design "
          "laboratory: each section tried a different visual language "
          "(claymorphism among them) to find out, cheaply, what converts and what "
          "merely looks clever. That habit of testing looks on a live page became "
          "the mood system Lantern runs on today."),
        plate("/assets/ops/clearflow.jpg",
              "The studio&rsquo;s permanent record of its first swing.",
              "The ClearFlow marketing site's headline"),
        go("https://clearflow-automation.github.io/clearflow/",
           "Visit the ClearFlow site, still live"),
        p("It is parked, and not because the machinery failed: selling hands-on "
          "automation from half a world away never found its footing, while the same "
          "machinery pointed at shops twenty minutes from the desk worked "
          "immediately. Everything below is its direct descendant. "
          "<i>The fossil is in the address bar: the GitHub organisation serving this "
          "very site is still named clearflow-automation.</i>"),
        rule("A parked venture that taught the next one is not a failure; it is "
             "tuition. It stays on the ledger."),
    ]),
    entry("02", "June 2026", "The growth agent, human in the loop", [
        p("ClearFlow&rsquo;s social presence was not run by hand. It was run by an "
          "agent with a twenty-six-kilobyte system brain: six numbered sub-routines "
          "(researcher, content creator, prospector, outreach manager, engagement "
          "monitor, dashboard updater) plus a warm-engagement pass that must run "
          "before any cold message is even drafted."),
        pull("You are not a generic social media bot."),
        p("The engineering is in the constraints, not the generation. Every post, "
          "DM and reply lands in an approvals queue and nothing touches a platform "
          "until a human clears it; only then does Composio execute the actual "
          "publish. The guardrails are written like laws: never more than ten DMs a "
          "day, never more than five posts, client names always anonymised, and "
          "claims capped in the voice guide itself: always &ldquo;up to 95%&rdquo;, "
          "never &ldquo;95%&rdquo;. State lives in a file, so the agent resumes "
          "mid-campaign across sessions instead of starting over."),
        plate("/assets/ops/agent-dashboard.jpg",
              "The agent&rsquo;s control panel, captured running today: thirteen "
              "drafts waiting for approval (seven posts, six DMs), each with its "
              "generated image, its pain-point citation and its source, and an "
              "Approve &amp; Post button a human has to press. Six industries "
              "tracked; nothing published without a click.",
              "The ClearFlow growth agent dashboard with a pending approvals queue"),
        rule("Automate the drafting, never the judgment. The film notebook reached "
             "the same law from the other direction: slop is automated judgment."),
    ]),
    entry("03", "July 2026 &ndash; present", "The twenty-minute demo", [
        p("The product is not a website; it is a system that turns a prospect&rsquo;s "
          "name into a personalised demo site in about twenty minutes, sent over "
          "WhatsApp to open the conversation. If they like it, the demo becomes the "
          "delivered site."),
        p("The personalisation is engineered, not improvised. The niche picks a "
          "default mood from a written design system: editorial for boutiques, "
          "minimal-luxe for spas, warm-boutique for bridal, clinical-trust for "
          "dentists, bold-modern for gyms, prestige-luxe for the elite end. Two or "
          "three colours are pulled from the shop&rsquo;s own logo and photos and "
          "declared as CSS custom properties, the type pairing comes from the "
          "mood&rsquo;s shortlist, and testimonials are real Google reviews or "
          "nothing. Every demo deploys under a noindex path so a sample site can "
          "never outrank the real shop in search."),
        wall(),
        p("Sixteen on the shelf; two became live client sites; the studio&rsquo;s "
          "own airlantern.com runs on the same machinery. Nothing personalised is "
          "built before an advance clears: a rule that exists because its absence "
          "was tried first."),
        rule("Personalisation is a data change, not a build. That is the whole "
             "economics of the studio in one sentence."),
    ]),
    entry("04", "August 2026", "Three lead engines, and a call sheet that "
          "respects the caller", [
        p("Finding the shops got automated three ways: an engine that reads public "
          "map listings for a locality and scores which businesses have weak or "
          "missing websites; one that sweeps direct-to-consumer brands and enriches "
          "each with its domain&rsquo;s registration age over RDAP; and one that "
          "walks business-association directories. Together they feed a master book "
          "of 381 leads across five regions, each row carrying the business, its "
          "category, rating and review count, a fit score, and an opening hook "
          "written in Hinglish, because that is the language the call actually "
          "happens in."),
        p("The detail that matters is in what the engines refuse to do: the call "
          "sheets are additions-only. A regenerated sheet would overwrite the "
          "caller&rsquo;s own record (who answered, who said no, what was promised), "
          "so the machinery only ever appends. The human&rsquo;s handwriting wins "
          "over the machine&rsquo;s output, by design."),
        rule("The phone call is the expensive part. Everything before it should "
             "cost nothing, and everything the caller writes down is sacred."),
    ]),
    entry("05", "June 2026 &ndash; present", "Paperwork as a build artifact", [
        p("Every document the studio sends is generated: the offer catalogue, the "
          "price card, the sales ladder, the one-pager, the partner brief, both "
          "scopes of work, the invoices, the health-check sheets, the handover "
          "document, the client setup guide, the call sheets, the outreach "
          "messages. Even the logo is built by a script. Eighteen generators share "
          "one Word-furniture module, so a pricing change is edited once, in a "
          "constant, and every document that mentions money is rebuilt to match."),
        rule("If it goes to a client twice, it gets a generator. Hand-edited "
             "paperwork is where version drift goes to hide."),
    ]),
    entry("06", "August 2026", "The health check", [
        p("More than half the lead list already has a website, and most of those "
          "sites are quietly broken. For them the door is an automated audit: a "
          "scanner crawls the site, scores what is actually wrong (speed, search "
          "visibility, broken contact paths) and a generator turns the findings "
          "into a written review the owner keeps, free."),
        p("Three of those scorecards are published on airlantern.com&rsquo;s "
          "reviews ledger, findings and all. The review earns the fix; the fix "
          "earns the retainer. It is the only door in the studio that ends in "
          "recurring revenue."),
        go("https://airlantern.com/#tuneup", "See the published scorecards"),
    ]),
    entry("07", "&mdash;", "The open ledger", [
        p("What the back room is looking into right now, updated as it changes:"),
        p("<b>Conversion experiments on the demo funnel.</b> Which opening message, "
          "which demo mood, which follow-up interval actually gets a reply. Volumes "
          "are small enough that honesty matters more than statistics here."),
        p("<b>An automation engagement with a chartered-accountancy firm.</b> "
          "Scoping in September. What it becomes is not yet known, which is why "
          "this line says nothing else."),
        rule("Dead ideas cost nothing to publish. Live ones cost everything. The "
             "ledger stays one step behind the work on purpose."),
    ]),
    entry("08", "&mdash;", "If some of this is for you", eid="for-you", blocks=[
        p("The machinery is for hire in one specific form: fast, honest websites "
          "for local businesses, and tune-ups for the ones whose site is quietly "
          "failing them. That storefront is "
          '<a href="https://airlantern.com">airlantern.com</a>: prices on the '
          "page, a WhatsApp button that reaches an actual person, and a form that, "
          "as of this week, verifiably delivers."),
    ]),
])

# ------------------------------------------------------------------ write ---
PAGES = [
    ("operations", "The machinery behind the studio",
     "The engines behind a one-person web studio: lead finding, twenty-minute demos, "
     "automated site audits, and the agent-run venture that came first and taught it all.",
     operations, "/assets/ops/card.jpg"),
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
