#!/usr/bin/env python3
"""Trading Hub — the real thing, captured and annotated.

Replaces the earlier synthetic mock. Every tab here is a screenshot of the live hub
taken on 25 Aug 2026 during market hours. Nothing is staged and nothing is recreated.

Two decisions worth stating, because the page states them too:
  · Rupee figures stay. GATI is an explicitly-labelled PAPER book — started 2026-07-16,
    equity equals cash, no trades taken. Simulated capital, not an account.
  · One redaction, and it is not about markets. The doctor's env/auth check prints the
    broker token's account holder by name. Signals go stale in a day; a third party's
    identity does not.
"""
import pathlib

OUT = pathlib.Path(__file__).parent

TABS = [
    dict(slug="today", label="Today", shot="today.png",
         head="The morning read",
         body="The strip along the top is feed health, not decoration — tick feed age, "
              "equity LTP age, how much of the universe the scanner has covered "
              "(117 of 208), and the day’s regime call. Each index card carries a "
              "choppiness score <i>and its percentile</i>, so 0.125 is legible as p25 "
              "rather than as a bare number. The playbook row then collapses all of it "
              "into one instruction: <b>choppy tape → fade-wind on → hunt failed "
              "breaks</b>. The main table is titled in Hinglish because the tool was "
              "built for one person rather than for a market: <i>abhi kahan dekhna "
              "hai</i> — where to look right now."),
    dict(slug="scanner", label="Levels & Scanner", shot="scanner.png",
         head="The full scan behind the summary",
         body="Today shows the shortlist; this is the whole population the scanner "
              "tracks, across every timeframe on the fractal ladder — weekly reading "
              "yearly levels, daily reading monthly, intraday reading daily."),
    dict(slug="failed_breaks", label="Failed Breaks", shot="failed_breaks.png",
         head="A tool that argues with its own user",
         body="Breaks that got trapped, classified <b>broke → failing → failed / "
              "reclaimed</b>, with live counters and a timeframe filter. The important "
              "part is the box at the top, which is a warning rather than a pitch: the "
              "fade tilt on choppy days is real and monotonic, <i>and</i> the mechanical "
              "average is about one basis point before costs. “Trending → trade "
              "breakouts” found no support at all. A dashboard that tells you not to "
              "trade its own list mechanically is doing the job properly."),
    dict(slug="gati_paper", label="GATI", shot="gati_paper.png",
         head="A paper book, priced honestly",
         body="Positional momentum on relative strength, running forward on paper since "
              "16 July. The fill assumptions are printed under the chart where they can "
              "be checked — <b>next-open entry, full costs, ten basis points of "
              "slippage, idle cash at six percent</b>. The regime gate is off, so the "
              "watchlist is what the rules <i>would</i> buy and the position count is "
              "zero out of ten. The rupee figures are simulated capital."),
    dict(slug="breadth", label="Breadth", shot="breadth.png",
         head="Breadth as a risk dial",
         body="Tested both ways and kept as a gate rather than a scoring feature, "
              "because as a feature it added approximately nothing."),
    dict(slug="rs_quadrant", label="Sector Rotation", shot="rs_quadrant.png",
         head="Relative strength, by sector",
         body="Ratio against momentum on the same universe the scanner runs on."),
    dict(slug="vcp", label="VCP", shot="vcp.png",
         head="Volatility contraction",
         body="Tightest coils first, ranked by percentile rather than by a raw number "
              "so that today is comparable with last month."),
    dict(slug="research", label="Research", shot="research.png",
         head="Every thread, with its verdict",
         body="The catalogue of concluded research — sixty threads, each carrying the "
              "finding that ended it and a path to the evidence. Forty-one are dead."),
    dict(slug="system", label="System", shot="system.png",
         head="The tab that admits it is broken",
         body="Last night’s end-of-day refresh failed, and the page says so in red at "
              "the top rather than degrading quietly. Every scheduled run is listed with "
              "its mode, its result, and a chip per step, so a failure points at the step "
              "that caused it. Underneath, the doctor reports <b>0 fail, 1 warn, 58 "
              "pass</b> — freshness per store, known option-chain gaps kept as known "
              "gaps, and delisted names excluded with the reason and the date. This is "
              "the tab that exists because a checker once reported clean while 499 "
              "symbols carried 55,457 duplicate rows. The account holder’s name is the "
              "one thing covered on this page."),
    dict(slug="journal", label="Journal", shot="journal.png",
         head="The discretion journal",
         body="Where a discretionary decision gets written down at the time it is taken, "
              "so it can be argued with later."),
]

CAP = ("Captured live on 25 August 2026 during market hours. Real data, real state, "
       "nothing staged. The only thing covered anywhere is the broker account "
       "holder’s name on the System tab.")

nav = "".join(
    f'<button class="tab{" on" if i == 0 else ""}" data-i="{i}" data-s="{t["slug"]}">'
    f'{t["label"]}</button>' for i, t in enumerate(TABS))

panes = "".join(
    f'''<section class="pane{" on" if i == 0 else ""}" data-i="{i}">
      <div class="note"><h2>{t["head"]}</h2><p>{t["body"]}</p></div>
      <figure><img src="/assets/hub/{t["shot"]}" alt="{t["label"]} tab of the trading hub"
        loading="{"eager" if i == 0 else "lazy"}" decoding="async"></figure>
    </section>''' for i, t in enumerate(TABS))

HTML = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Trading Hub &mdash; the real thing</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap">
<style>
*,*::before,*::after{{box-sizing:border-box}}
:root{{--bg:#0b0d10;--pan:#12151a;--rule:#232830;--ink:#e6e9ee;--dim:#878e98;--acc:#c2683a;
--mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;--sans:'Inter',system-ui,sans-serif}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}}
.top{{display:flex;align-items:center;gap:.9rem;padding:.75rem 1.1rem;
border-bottom:1px solid var(--rule);flex-wrap:wrap;position:sticky;top:0;
background:rgba(11,13,16,.94);backdrop-filter:blur(8px);z-index:5}}
.brand{{font-family:var(--mono);font-size:.72rem;letter-spacing:.22em;text-transform:uppercase}}
.brand b{{color:var(--acc);font-weight:400}}
.live{{font-family:var(--mono);font-size:.6rem;letter-spacing:.13em;text-transform:uppercase;
color:#0b0d10;background:var(--acc);padding:.2rem .5rem;border-radius:2px}}
.back{{margin-left:auto;font-family:var(--mono);font-size:.68rem;letter-spacing:.1em;
text-transform:uppercase;color:var(--dim);text-decoration:none}}
.back:hover{{color:var(--ink)}}
.tabs{{display:flex;overflow-x:auto;border-bottom:1px solid var(--rule);scrollbar-width:none;
position:sticky;top:3.05rem;background:rgba(11,13,16,.94);backdrop-filter:blur(8px);z-index:4}}
.tabs::-webkit-scrollbar{{display:none}}
.tab{{flex:none;background:none;border:0;border-bottom:2px solid transparent;color:var(--dim);
font:inherit;font-size:.82rem;padding:.7rem 1rem;cursor:pointer;white-space:nowrap}}
.tab:hover{{color:var(--ink)}}
.tab.on{{color:var(--ink);border-bottom-color:var(--acc)}}
.wrap{{padding:2rem 1.1rem 4rem;max-width:78rem;margin:0 auto}}
.pane{{display:none}} .pane.on{{display:block}}
.note{{max-width:64ch;margin:0 0 1.6rem}}
.note h2{{font-size:1.35rem;letter-spacing:-.02em;margin:0 0 .6rem;font-weight:600}}
.note p{{margin:0;color:var(--dim)}}
.note b{{color:var(--ink);font-weight:500}} .note i{{color:#b9c0c9;font-style:italic}}
figure{{margin:0;border:1px solid var(--rule);border-radius:4px;overflow:hidden;
background:var(--pan)}}
figure img{{width:100%;display:block}}
.foot{{border-top:1px solid var(--rule);padding:1.2rem 1.1rem;color:var(--dim);
font-size:.78rem;max-width:78rem;margin:0 auto}}
</style></head><body>
<div class="top">
  <span class="brand">Trading<b>Hub</b></span>
  <span class="live">Captured live</span>
  <a class="back" href="/market/">&larr; notebook</a>
</div>
<nav class="tabs">{nav}</nav>
<main class="wrap">{panes}</main>
<footer class="foot">{CAP}</footer>
<script>
var tabs=[].slice.call(document.querySelectorAll('.tab')),
    panes=[].slice.call(document.querySelectorAll('.pane'));
tabs.forEach(function(t){{t.addEventListener('click',function(){{
  var i=t.dataset.i;
  tabs.forEach(function(x){{x.classList.toggle('on',x===t)}});
  panes.forEach(function(p){{p.classList.toggle('on',p.dataset.i===i)}});
  history.replaceState(null,'','#'+t.dataset.s);
  window.scrollTo(0,0);
}})}});
(function(){{var h=location.hash.slice(1);if(!h)return;
  var t=tabs.filter(function(x){{return x.dataset.s===h}})[0];if(t)t.click();}})();
</script></body></html>'''

(OUT / "index.html").write_text(HTML, encoding="utf-8")
print(f"built market/hub/index.html  {len(HTML):,} bytes  {len(TABS)} tabs, real captures")
