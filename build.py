#!/usr/bin/env python3
"""nanditvaish.com — a research portfolio, built as a lab notebook.

DIRECTION (locked 25 Aug 2026): "The Lab Notebook". Paper-white editorial page,
one red reserved for kills, artifacts dropped in as full-bleed dark plates.
VOICE: first person plural. The collaboration with Claude is named, not implied.
THESIS: we build instruments designed to disprove us.

Motion law is Nandit's own, from channel/CLAUDE.md §5:
  simulation motion is NEVER eased · interface motion is ALWAYS eased
  a beat after a reveal — never stack two animations

  python3 build.py           preview, noindex
  python3 build.py --prod    the head nanditvaish.com ships
"""
import pathlib, sys

OUT = pathlib.Path(__file__).parent
PROD = "--prod" in sys.argv
ROBOTS = "" if PROD else '<meta name="robots" content="noindex">'
MAIL = "vaishnandit@gmail.com"

# ---------------------------------------------------------------------------
from shared import BASE_CSS as CSS

# ---------------------------------------------------------------------------
SIM_JS = """
/* Fig. 1 — kinetic exchange (Dragulescu & Yakovenko, EPJ B, 2000).
   N agents all start equal. Repeatedly pick two at random, pool their money and
   split the pool at random. Nobody is smarter. Nobody cheats. Money is conserved
   exactly. Per the motion law this is SIMULATION motion: never eased, never
   interpolated — every frame is the true state of the model. */
(function(){
  var cv=document.getElementById('sim'); if(!cv) return;
  var ctx=cv.getContext('2d'), N=2000, START=100, BINS=54;
  var m=new Float64Array(N), seed=20260825, frame=0, MAXF=620, tx=0, raf=null;
  var $g=document.getElementById('sim-gini'), $t=document.getElementById('sim-tx'),
      $b=document.getElementById('sim-replay'), $l=document.getElementById('sim-label');
  var ENERGY=false;

  function rnd(){ seed^=seed<<13; seed^=seed>>>17; seed^=seed<<5; return ((seed>>>0)%1e6)/1e6; }
  function reset(){ for(var i=0;i<N;i++) m[i]=START; frame=0; tx=0; }

  function gini(a){
    var s=Array.prototype.slice.call(a).sort(function(x,y){return x-y}), n=s.length,
        c=0, tot=0;
    for(var i=0;i<n;i++){ c+=(i+1)*s[i]; tot+=s[i]; }
    if(tot<=0) return 0;
    return (2*c)/(n*tot) - (n+1)/n;
  }

  function size(){
    var r=cv.getBoundingClientRect(), d=window.devicePixelRatio||1;
    cv.width=Math.round(r.width*d); cv.height=Math.round(r.height*d);
    ctx.setTransform(d,0,0,d,0,0); return r;
  }

  function draw(){
    var r=size(), W=r.width, H=r.height, pad=1;
    ctx.clearRect(0,0,W,H);
    var max=0; for(var i=0;i<N;i++) if(m[i]>max) max=m[i];
    var top=Math.max(max,1), hist=new Array(BINS).fill(0);
    for(i=0;i<N;i++){ var b=Math.min(BINS-1,Math.floor(m[i]/top*BINS)); hist[b]++; }
    var hmax=1; for(i=0;i<BINS;i++) if(hist[i]>hmax) hmax=hist[i];
    var bw=(W-pad*(BINS-1))/BINS;
    for(i=0;i<BINS;i++){
      var h=(hist[i]/hmax)*(H-2);
      ctx.fillStyle = ENERGY ? 'rgba(242,180,92,'+(0.35+0.65*(hist[i]/hmax))+')'
                             : 'rgba(79,214,200,'+(0.35+0.65*(hist[i]/hmax))+')';
      ctx.fillRect(i*(bw+pad), H-h, bw, h);
    }
  }

  function step(){
    /* 1200 pairings per frame; front-loaded pacing is unnecessary here because
       the histogram itself shows the early collapse clearly. */
    for(var k=0;k<1200;k++){
      var i=(rnd()*N)|0, j=(rnd()*N)|0; if(i===j) continue;
      var pool=m[i]+m[j], share=rnd();
      m[i]=pool*share; m[j]=pool-m[i]; tx++;
    }
    frame++;
    draw();
    $g.textContent=gini(m).toFixed(3);
    $t.textContent=tx.toLocaleString('en-US');
    if(frame<MAXF){ raf=requestAnimationFrame(step); }
    else { raf=null; $b.textContent='Run it again'; }
  }

  function run(){ if(raf) cancelAnimationFrame(raf); seed=20260825; reset(); $b.textContent='Running'; step(); }
  $b.addEventListener('click',run);
  $l.addEventListener('click',function(){
    ENERGY=!ENERGY;
    $l.textContent = ENERGY ? 'energy among gas molecules' : 'money among people';
    document.getElementById('sim-unit').textContent = ENERGY ? 'energy' : 'money';
    draw();
  });
  window.addEventListener('resize',function(){ draw(); });
  reset(); draw(); run();
})();
"""

REVEAL_JS = """
document.documentElement.classList.add('js');
(function(){
  var els=[].slice.call(document.querySelectorAll('.rv'));
  var show=function(e){e.classList.add('in')};
  if(!('IntersectionObserver' in window)){els.forEach(show);return}
  var io=new IntersectionObserver(function(en){
    en.forEach(function(x){if(x.isIntersecting){show(x.target);io.unobserve(x.target)}})
  },{rootMargin:'0px 0px -6% 0px',threshold:.05});
  els.forEach(function(e){io.observe(e)});
  /* Content must never be able to stay invisible. A tab that never renders never
     ticks a transition, so the class alone would leave it at opacity 0 forever. */
  setTimeout(function(){
    if(document.querySelectorAll('.rv.in').length===0){
      io.disconnect();
      els.forEach(function(e){ e.classList.add('in');
        e.style.transition='none'; e.style.opacity='1'; e.style.transform='none'; });
    }
  },3000);
})();
"""

NOTE_JS = """
document.querySelectorAll('.note__form').forEach(function(f){
  f.addEventListener('submit',function(ev){
    ev.preventDefault();
    var btn=f.querySelector('button'), hint=f.querySelector('.note__hint');
    var body=f.body.value.trim(); if(!body) return;
    btn.disabled=true; btn.textContent='Sending';
    fetch('https://formsubmit.co/ajax/da68bdf022916e7f4771c192cd673f08',{method:'POST',
      headers:{'Content-Type':'application/json','Accept':'application/json'},
      body:JSON.stringify({_subject:'nanditvaish.com \u2014 note',
        page:document.title,body:body,from:f.from.value.trim()})})
    .then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); })
    .then(function(j){ if(j.success!=='true') throw new Error('rejected'); return j; })
    .then(function(){ f.innerHTML='<p class="note__state">Received. It came straight to Nandit \\u2014 nobody else sees it.</p>'; })
    .catch(function(){
      btn.disabled=false; btn.textContent='Send';
      hint.textContent='That did not send. Email __MAIL__ instead.';
      hint.style.color='var(--kill)';
    });
  });
});
""".replace("__MAIL__", MAIL)

# ---------------------------------------------------------------------------
import json as _json
CAT = _json.loads((OUT/"assets/research_catalog.json").read_text())
THREADS = CAT if isinstance(CAT,list) else next(v for v in CAT.values() if isinstance(v,list))
_CLS = {"DEAD":"d","TRUST":"t","OPEN":"o"}
grave = "".join('<i class="%s"></i>' % _CLS.get(t.get("verdict"),"x") for t in THREADS)

CARDS = [
  dict(no="01", href="/market/", when="April \u2013 August 2026",
       title="Sixty ideas, run until they broke",
       desc="Four months of market research on 252 million rows of Indian equity and index-option "
            "history. A research programme that industrialised the part everyone skips: proving "
            "yourself wrong quickly, cheaply, and on the record.",
       media='<div class="graveWrap"><div class="grave">%s</div><div class="graveKey"><span><s style="background:#ae2f22"></s><b>41</b> dead</span><span><s style="background:#2f9e83"></s><b>4</b> trusted</span><span><s style="background:#f2b45c"></s><b>3</b> open</span><span><s style="background:#4a4f57"></s><b>12</b> other</span></div></div>' % grave,
       go="Open the notebook"),
  dict(no="02", href="/research-os/", when="July \u2013 August 2026",
       title="India from orbit, on one join key",
       desc="Satellite embeddings over 318,706 five-kilometre cells, every year since 2017, joined "
            "to rainfall, land cover, districts, elevation and population. Nineteen terabytes of "
            "source reduced to 242 megabytes by choosing the right resolution.",
       media='<img src="/assets/plates/grid-poster.jpg" alt="India rendered as 318,706 cells, coloured by how much each changed" loading="lazy">',
       go="Open the notebook"),
  dict(no="03", href="/film/", when="July \u2013 August 2026",
       title="A street of six shapes, and a film about robots",
       desc="Twenty-five days inside Unreal Engine. A neon city built entirely from primitives, and "
            "a three-minute film that gives every number in a bank\u2019s humanoid-robot projection "
            "its own scene \u2014 narrated, timed and shipped.",
       media='<img src="/assets/plates/film-poster.jpg" alt="A frame from the film: the hands alone cost $9,315" loading="lazy">',
       go="Open the notebook"),
  dict(no='04', href='/operations/', when='June 2026 – present',
       title='The machinery behind the studio',
       desc='The back room of a one-person web studio: engines that find the leads, a pipeline that builds a personalised demo in twenty minutes, automated site audits — and the parked Canadian venture that taught it all.',
       media='<img src="/assets/ops/card.jpg" alt="Eight of the sixteen demo sites on the shelf" loading="lazy">',
       go='Open the back room'),
]

cards_html = "".join(
  '<a class="card rv" href="%s"><div class="card__fig">%s</div>'
  '<div class="card__meta"><span class="card__when">%s</span></div>'
  '<h2>%s</h2><p>%s</p><span class="card__go">%s</span></a>'
  % (c["href"], c["media"], c["when"], c["title"], c["desc"], c["go"])
  for c in CARDS)

SCALE=[("252 M","rows of market data, 188k parquet parts"),
       ("60","research threads run to a verdict"),
       ("318,706","cells of India, nine years, one join key"),
       ("1,158","frames rendered across six passes")]
scale_html="".join(
    '<div><p class="scale__n">'+n+'</p><p class="scale__l">'+l+'</p></div>' for n,l in SCALE)

HEAD_PROD = """<link rel="canonical" href="https://nanditvaish.com/">
  <meta property="og:title" content="Nandit Vaish">
  <meta property="og:description" content="Market research over 252 million rows, India from orbit, and a city made of six shapes and light.">
  <meta property="og:type" content="website">"""

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nandit Vaish</title>
<meta name="description" content="Selected work by Nandit Vaish \u2014 market-structure research over 252 million rows, India mapped from orbit, and a neon city built entirely from primitive shapes.">
<meta property="og:image" content="https://nanditvaish.com/assets/plates/street-poster.jpg">
<meta name="twitter:card" content="summary_large_image">
__ROBOTS__
__HEADP__
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=IBM+Plex+Mono:wght@400;600&display=swap">
<style>__CSS__</style>
</head>
<body>

<header class="mast">
  <div class="col-wide mast__in">
    <a class="mast__name" href="/">Nandit Vaish</a>
    <nav class="mast__nav">
      <a href="/market/">Market</a>
      <a href="/research-os/">Research OS</a>
      <a href="/film/">Film</a>
      <a href="/operations/">Operations</a>
    </nav>
  </div>
</header>

<main>

  <section class="hero">
    <div class="hero__media">
      <video src="/assets/plates/street.mp4" poster="/assets/plates/street-poster.jpg"
             autoplay muted loop playsinline preload="metadata"></video>
      <div class="hero__scrim"></div>
    </div>
    <div class="hero__text">
      <div class="col-wide">
        <h1>I build instruments that <em>argue back.</em></h1>
        <p class="hero__deck">A market engine that killed forty-one of its own trading
          ideas. A satellite study that failed its own referee, and said so.
          A city made of six shapes and light.</p>
      </div>
    </div>
  </section>

  <section class="scale">
    <div class="col-wide"><div class="scale__grid rv">__SCALE__</div></div>
  </section>

  <section class="col-wide">
    <div class="cards">__CARDS__</div>
  </section>

  <section class="plate rv">
    <div class="plate__in">
      <div class="sim">
        <canvas id="sim" class="sim__canvas" aria-label="Live simulation of the distribution of money across 2,000 agents"></canvas>
        <div class="sim__bar">
          <span class="sim__stat">Gini<b id="sim-gini">0.000</b></span>
          <span class="sim__stat">Exchanges<b id="sim-tx">0</b></span>
          <span class="sim__stat">Agents<b>2,000</b></span>
          <button class="sim__btn" id="sim-replay">Running</button>
        </div>
        <p class="plate__cap"><b>One you can play with: the distribution of <span id="sim-unit">money</span>, live.</b>
          Two thousand agents start with exactly one hundred each. Two are picked at random,
          their holdings pooled, the pool split at random. Nobody is smarter, nobody cheats,
          and the total never changes. It settles into the same curve that describes
          <a href="#" id="sim-label" style="border-color:#3a3f47">money among people</a>.
          Inequality out of nothing but fair trades. From Episode 1 of the channel.</p>
      </div>
    </div>
  </section>

  <section class="col">
    <div class="note rv">
      <p class="note__t">Leave a note</p>
      <form class="note__form">
        <textarea name="body" required placeholder="A question, a correction, or something you think is wrong."></textarea>
        <input type="text" name="from" placeholder="How to reach you (optional)">
        <button type="submit">Send</button>
        <p class="note__hint">Goes to Nandit only. Not published, not shown to anyone else.</p>
      </form>
    </div>
  </section>

</main>

<footer class="colophon">
  <div class="col-wide">
    <dl>
      <dt>Contact</dt><dd><a href="mailto:__MAIL__">__MAIL__</a></dd>
      <dt>Studio</dt><dd><a href="https://airlantern.com">airlantern.com</a> &mdash; websites for local businesses</dd>
      <dt>Verdicts</dt><dd>Verified &middot; observed &middot; inferred &middot; flagged. Anything flagged is known-open and deliberately not smoothed over.</dd>
      <dt>Set in</dt><dd>Newsreader and IBM Plex Mono. Figures are tabular throughout.</dd>
    </dl>
  </div>
</footer>

<script>__REVEAL____NOTE____SIM__</script>
</body>
</html>"""

HTML = (HTML.replace("__ROBOTS__", ROBOTS)
            .replace("__HEADP__", HEAD_PROD if PROD else "")
            .replace("__CSS__", CSS)
            .replace("__SCALE__", scale_html)
            .replace("__CARDS__", cards_html)
            .replace("__REVEAL__", REVEAL_JS)
            .replace("__NOTE__", NOTE_JS)
            .replace("__SIM__", SIM_JS)
            .replace("__MAIL__", MAIL))

(OUT/"index.html").write_text(HTML, encoding="utf-8")
print("built index.html  (%s)  %s bytes" % ("PROD" if PROD else "preview, noindex", f"{len(HTML):,}"))
