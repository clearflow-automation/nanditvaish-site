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
  var ctx=cv.getContext('2d'), N=2000, START=100, BINS=54, XMAX=600;
  var m=new Float64Array(N), seed=20260825, frame=0, MAXF=620, tx=0, raf=null, ran=false;
  var $g=document.getElementById('sim-gini'), $t=document.getElementById('sim-tx'),
      $b=document.getElementById('sim-replay'), $l=document.getElementById('sim-label');
  var ENERGY=false;

  /* Equilibrium occupancy per bin: Boltzmann-Gibbs with mean START, drawn as a
     fixed dashed target so the histogram can be seen walking into it. The x-axis
     is fixed at [0, XMAX] for the same reason: a domain that rescales each frame
     turns convergence into wobble. */
  var EXP=new Array(BINS), bw=XMAX/BINS, expMax=0;
  for(var q=0;q<BINS;q++){
    EXP[q]=N*(Math.exp(-(q*bw)/START)-Math.exp(-((q+1)*bw)/START));
    if(EXP[q]>expMax) expMax=EXP[q];
  }

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
    var r=size(), W=r.width, H=r.height, pad=1, AX=20, PH=H-AX;
    ctx.clearRect(0,0,W,H);
    var hist=new Array(BINS).fill(0);
    for(var i=0;i<N;i++){ var b=Math.min(BINS-1,Math.floor(m[i]/XMAX*BINS)); hist[b]++; }
    var hmax=expMax; for(i=0;i<BINS;i++) if(hist[i]>hmax) hmax=hist[i];
    var bwpx=(W-pad*(BINS-1))/BINS;
    ctx.fillStyle = ENERGY ? 'rgba(242,180,92,.85)' : 'rgba(79,214,200,.85)';
    for(i=0;i<BINS;i++){
      var h=(hist[i]/hmax)*(PH-14);
      ctx.fillRect(i*(bwpx+pad), PH-h, bwpx, h);
    }
    /* everyone starts here */
    var sx=(START/XMAX)*W;
    ctx.strokeStyle='rgba(139,144,152,.35)'; ctx.lineWidth=1;
    ctx.setLineDash([2,4]); ctx.beginPath(); ctx.moveTo(sx,6); ctx.lineTo(sx,PH); ctx.stroke();
    /* the prediction */
    ctx.strokeStyle='#8b9098'; ctx.setLineDash([4,4]);
    ctx.beginPath();
    for(i=0;i<BINS;i++){
      var x=i*(bwpx+pad)+bwpx/2, y=PH-(EXP[i]/hmax)*(PH-14);
      if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle='#8b9098'; ctx.font='10px "IBM Plex Mono",monospace';
    ctx.textAlign='right';
    ctx.fillText('Boltzmann\\u2013Gibbs, the prediction', W-6, PH-16);
    /* axis */
    ctx.strokeStyle='#23262c'; ctx.beginPath();
    ctx.moveTo(0,PH+.5); ctx.lineTo(W,PH+.5); ctx.stroke();
    ctx.textAlign='left'; ctx.fillText('0', 2, H-6);
    ctx.textAlign='center';
    ctx.fillText('100 \\u00b7 start', sx, H-6);
    ctx.fillText('300', (300/XMAX)*W, H-6);
    ctx.textAlign='right'; ctx.fillText('600', W-2, H-6);
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

  function run(){ if(raf) cancelAnimationFrame(raf); seed=20260825; reset(); ran=true; $b.textContent='Running'; step(); }
  $b.addEventListener('click',run);
  $l.addEventListener('click',function(ev){
    ev.preventDefault();
    ENERGY=!ENERGY;
    $l.textContent = ENERGY ? 'energy among gas molecules' : 'money among people';
    draw();
  });
  window.addEventListener('resize',function(){ draw(); });
  reset(); draw();
  /* Start only when the viewer arrives, from the visible all-equal spike, so the
     collapse is witnessed rather than already over. Honour reduced motion. */
  var still=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(!still && 'IntersectionObserver' in window){
    var io=new IntersectionObserver(function(en){
      en.forEach(function(e){ if(e.isIntersecting&&!ran){ run(); io.disconnect(); } });
    },{threshold:.35});
    io.observe(cv);
  }
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
       desc="A four-month research programme over 252 million rows of Indian equity and "
            "index-option history, industrialising the part everyone skips: proving "
            "yourself wrong quickly, cheaply, and on the record.",
       media='<img src="/assets/generated/market-topography.webp" width="1683" height="935" alt="A sculptural field of market data rising into peaks and troughs" loading="lazy">',
       go="Open the notebook"),
  dict(no="02", href="/research-os/", when="July \u2013 August 2026",
       title="India from orbit, on one join key",
       desc="A mapping study of India from orbit: satellite embeddings over 318,706 "
            "five-kilometre cells, every year since 2017, joined to rainfall, land cover, "
            "districts, elevation and population. Nineteen terabytes reduced to 242 megabytes.",
       media='<img src="/assets/generated/india-grid.webp" width="1122" height="1402" alt="India rendered as a dark field of geospatial cells and red points" loading="lazy">',
       go="Open the notebook"),
  dict(no="03", href="/research-os/#referee", when="July \u2013 August 2026",
       title="A research system with its own referee",
       desc="Sixty threads carried from question to verdict, with external checks, trivial "
            "baselines and failed findings kept visible instead of polished away.",
       media='<img src="/assets/generated/research-threads.webp" width="1677" height="938" alt="Fine research threads converging on a restrained red evidence point" loading="lazy">',
       go="Meet the referee"),
  dict(no="04", href="/film/", when="July \u2013 August 2026",
       title="A street of six shapes, and a film about robots",
       desc="A finished three-minute film, watchable inside, and the notebook of its making: "
            "every number in a bank\u2019s humanoid-robot projection given its own scene, in a "
            "neon city built from six primitive shapes inside Unreal Engine.",
       media='<img src="/assets/generated/film-strips.webp" width="1536" height="1024" alt="Monochrome film strips carrying frames of a city and one figure" loading="lazy">',
       go="Open the notebook"),
  dict(no='05', href='/operations/', when='June 2026 – present',
       title='From websites to process systems',
       desc='Lantern evolved from a website studio into a systems practice: mapping how '
            'owner-run businesses actually work, putting numbers on the process, and '
            'building the small systems that keep it running. Websites remain a secondary line.',
       media='<img src="/assets/generated/operations-table.webp" width="1536" height="1024" alt="Ledgers, process cards and a restrained dashboard arranged into an operating system" loading="lazy">',
       go='See the evolution'),
]

cards_html = "".join(
  '<a class="card rv" href="%s"><div class="card__fig">%s</div>'
  '<div class="card__meta"><span class="card__no">%s</span><span class="card__when">%s</span></div>'
  '<h2>%s</h2><p>%s</p><span class="card__go">%s</span></a>'
  % (c["href"], c["media"], c["no"], c["when"], c["title"], c["desc"], c["go"])
  for c in CARDS)

SCALE=[("252 M","rows of market data, 188k parquet parts"),
       ("60","research threads run to a verdict"),
       ("318,706","cells of India, nine years, one join key"),
       ("1,158","frames rendered across six passes")]
scale_html="".join(
    '<div><p class="scale__n">'+n+'</p><p class="scale__l">'+l+'</p></div>' for n,l in SCALE)

HEAD_PROD = """<link rel="canonical" href="https://nanditvaish.com/">
  <meta property="og:title" content="Nandit Vaish">
  <meta property="og:description" content="Business analytics, operational systems, applied AI and independent research — work built to argue back.">
  <meta property="og:type" content="website">"""

HOME_CSS = """
/* ---------- cinematic intelligence homepage ---------- */
:root{--home-bg:#080909;--home-panel:#0d0e0e;--home-ink:#f0ede7;
  --home-muted:#a6a29d;--home-rule:#343434;--home-red:#b41419}
body{background:var(--home-bg);color:var(--home-ink);overflow-x:hidden}
a{border-color:#555}.home-shell{width:min(74rem,100% - 2.5rem);margin-inline:auto}
.mast{position:absolute;z-index:20;inset:0 0 auto;border:0;color:var(--home-ink)}
.mast__in{width:min(78rem,100% - 2.5rem);padding-top:1.6rem}
.mast__name{font-size:.82rem;letter-spacing:.34em;color:#fff;text-shadow:0 2px 12px #000}
.mast__nav{color:#d8d6d1}.mast__nav a:hover{color:#fff;border-color:#fff}
.menu{display:none;position:relative}.menu summary{list-style:none;cursor:pointer;width:2.75rem;height:2.75rem;
  border:1px solid rgba(255,255,255,.44);display:grid;place-items:center;font-family:var(--mono);
  font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;background:rgba(7,8,8,.38)}
.menu summary::-webkit-details-marker{display:none}.menu nav{position:absolute;right:0;top:3.1rem;
  min-width:13rem;background:#0b0c0c;border:1px solid #454545;padding:.65rem;display:grid}
.menu nav a{font-family:var(--mono);font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;
  padding:.8rem;border-bottom:1px solid #292929}.menu nav a:last-child{border-bottom:0}
.hero{min-height:100svh;border:0;display:grid;align-items:end;isolation:isolate}
.hero__media{position:absolute;inset:0;width:100%;height:100%;max-height:none;aspect-ratio:auto;z-index:-2}
.hero__media video,.hero__media img{object-position:center}
.hero__scrim{background:rgba(5,6,6,.47);box-shadow:inset 0 -14rem 10rem -6rem #080909}
.hero__copy{padding:11rem 0 4.25rem;width:min(78rem,100% - 2.5rem);margin-inline:auto}
.hero__eyebrow,.section-label,.chapters__head,.evolution__trail,.home-fact__label{
  font-family:var(--mono);font-size:.68rem;letter-spacing:.23em;text-transform:uppercase;color:#bbb7b2}
.hero h1{font-size:clamp(3.25rem,7.6vw,7.35rem);line-height:.87;letter-spacing:-.052em;
  max-width:9.2ch;margin-top:1rem;color:#f4f1eb;text-shadow:0 5px 26px #000}
.hero h1 em{color:#f4f1eb;font-weight:400}.hero__sub{margin-top:1.8rem;max-width:39rem;
  color:#d3d0ca;font-size:clamp(1.08rem,1rem + .35vw,1.3rem);line-height:1.52}
.hero__cta{display:inline-flex;align-items:center;justify-content:space-between;gap:4rem;
  margin-top:2rem;padding:1rem 1.35rem;min-width:19rem;background:var(--home-red);
  color:#fff;border:0;font-family:var(--mono);font-size:.7rem;letter-spacing:.25em;text-transform:uppercase}
.hero__cta:hover{filter:brightness(1.12)}
.signal{position:absolute;top:33%;padding:.9rem .9rem 1rem;background:rgba(8,9,9,.72);
  border:1px solid rgba(255,255,255,.12);font-family:var(--mono);font-size:.67rem;
  line-height:1.75;letter-spacing:.18em;text-transform:uppercase;color:#e7e4de;box-shadow:0 10px 35px #000}
.signal::after{content:"";display:block;width:1.4rem;height:2px;background:var(--home-red);margin-top:.75rem}
.signal--left{left:3.5vw}.signal--right{right:3.5vw}
.chapters{padding:1rem 0 5.5rem}.chapters__head{display:flex;justify-content:space-between;
  padding:1.25rem 0;border-top:1px solid var(--home-rule)}
.chapter{display:grid;grid-template-columns:3rem minmax(0,1fr) minmax(11rem,auto) 1.25rem;
  align-items:center;gap:1rem;padding:1rem 0;border-top:1px solid var(--home-rule);border-bottom:0}
.chapter:last-child{border-bottom:1px solid var(--home-rule)}.chapter:hover{padding-left:.45rem;background:#0d0e0e}
.chapter__no,.chapter__measure{font-family:var(--mono);font-size:.72rem;color:#aaa6a1}
.chapter__title{font-size:clamp(1.4rem,1.1rem + .9vw,2rem);line-height:1.1}
.chapter__measure{text-align:right}.chapter__arrow{font-size:1.5rem;color:#eee}
.home-section{padding:6rem 0;border-top:1px solid var(--home-rule)}
.section-head{display:grid;grid-template-columns:10rem minmax(0,1fr);gap:2rem;margin-bottom:3.5rem}
.section-head h2{font-size:clamp(2.7rem,5vw,5.1rem);line-height:.94;letter-spacing:-.045em;max-width:12ch}
.section-head p{max-width:38rem;color:var(--home-muted);align-self:end}
.cards{padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4rem 1.25rem}
.card{color:var(--home-ink)}.card__fig{border-color:#313131;aspect-ratio:16/10}
.card:nth-child(2) .card__fig{aspect-ratio:4/5}.card:nth-child(3){margin-top:-7rem}
.card:nth-child(4){margin-top:2rem}.card:nth-child(5){grid-column:1/-1;margin-top:1rem}
.card:nth-child(5) .card__fig{aspect-ratio:16/7}.card__meta{color:#8f8b87;margin-top:1rem}
.card__no{color:var(--home-red)}.card h2{font-size:clamp(1.65rem,1.25rem + 1.3vw,2.6rem)}
.card p{color:var(--home-muted);font-size:1rem}.card__go{color:#e7e3dd;border-color:#575757}
.scale{border:0;padding:0}.scale__grid{grid-template-columns:repeat(4,1fr);gap:0;border-top:1px solid var(--home-rule)}
.scale__grid>div{padding:2rem 1.35rem 2rem 0;border-right:1px solid var(--home-rule)}
.scale__grid>div+div{padding-left:1.35rem}.scale__grid>div:last-child{border-right:0}
.scale__n{font-size:clamp(2.1rem,4vw,4.5rem);color:var(--home-ink)}
.scale__l{color:var(--home-muted);font-size:.64rem}
.evidence-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(18rem,.62fr);gap:1.5rem;margin-top:2rem}
.plate{margin:0;background:#0b0c0c;border:1px solid #2d2e2e;color:var(--home-ink)}
.plate__in{width:auto;padding:2rem}.sim__head h2{color:var(--home-ink);font-size:2rem}
.sim__head p{color:var(--home-muted);font-size:1rem}.sim__canvas{aspect-ratio:16/8}
.sim__bar{gap:1rem}.sim__stat b{color:var(--home-ink)}.plate__cap{color:#999590}
.sim__switch{background:none;border:0;border-bottom:1px solid #555;color:#e8e4de;padding:0;
  font:inherit;cursor:pointer}.ledger{border:1px solid #2d2e2e;padding:2rem;display:flex;flex-direction:column}
.ledger h3{font-size:2rem;margin-bottom:1rem}.ledger p{color:var(--home-muted);font-size:1rem}
.ledger__rows{margin-top:auto}.ledger__row{display:flex;justify-content:space-between;gap:1rem;
  padding:.9rem 0;border-top:1px solid var(--home-rule);font-family:var(--mono);font-size:.68rem;color:#a9a5a0}
.ledger__row b{color:#ece8e2;font-weight:400}.method{display:grid;grid-template-columns:repeat(5,1fr);border-top:1px solid var(--home-rule)}
.method__step{padding:1.7rem 1rem 1.7rem 0;border-right:1px solid var(--home-rule)}
.method__step+.method__step{padding-left:1rem}.method__step:last-child{border-right:0}
.method__no{font-family:var(--mono);font-size:.67rem;color:var(--home-red)}
.method__step h3{margin-top:2.2rem;font-size:1.5rem}.method__step p{margin-top:.55rem;color:var(--home-muted);font-size:.92rem}
.evolution{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(18rem,.95fr);gap:4rem;align-items:center}
.evolution__media{position:relative}.evolution__media img{width:100%;display:block;border:1px solid #333}
.evolution__copy h2{font-size:clamp(2.8rem,5vw,5rem);line-height:.92;letter-spacing:-.045em;margin:1.2rem 0}
.evolution__copy>p{color:var(--home-muted);max-width:35rem}.evolution__trail{display:flex;flex-wrap:wrap;gap:.6rem 1rem;color:#e6e2dc}
.evolution__trail span{color:var(--home-red)}.evolution__line{width:2rem;height:2px;background:var(--home-red);margin:1.8rem 0}
.evolution__link{display:inline-block;margin-top:1.6rem;font-family:var(--mono);font-size:.68rem;
  letter-spacing:.16em;text-transform:uppercase;color:#fff}.about{display:grid;grid-template-columns:minmax(0,.7fr) minmax(0,1.3fr);gap:5rem}
.about h2{font-size:clamp(3rem,6vw,6.4rem);line-height:.86;letter-spacing:-.05em}
.about__body{padding-top:.5rem}.about__lede{font-size:clamp(1.5rem,2.6vw,2.5rem);line-height:1.15;max-width:18ch}
.about__text{margin-top:1.5rem;color:var(--home-muted);max-width:38rem}.about__facts{display:flex;flex-wrap:wrap;gap:.65rem;margin-top:2rem}
.about__fact{border:1px solid #393939;padding:.55rem .75rem;font-family:var(--mono);font-size:.62rem;
  letter-spacing:.1em;text-transform:uppercase;color:#ccc8c2}.about__fact:first-child{border-color:var(--home-red);color:#eee}
.contact{padding:7rem 0 4rem;border-top:1px solid var(--home-rule)}
.contact__head{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(18rem,.8fr);gap:4rem;align-items:end}
.contact h2{font-size:clamp(3rem,7vw,7.2rem);line-height:.88;letter-spacing:-.055em;max-width:9ch}
.contact__side>p{color:var(--home-muted);max-width:29rem}.contact__mail{display:inline-block;margin-top:1.3rem;
  font-size:1.3rem;color:var(--home-ink)}.note{border-top:1px solid var(--home-rule);margin-top:4rem;padding-top:2rem}
.note__form{max-width:none;grid-template-columns:minmax(0,1fr) minmax(12rem,.45fr) auto;align-items:end}
.note__field{display:grid;gap:.45rem}.note__field label{font-family:var(--mono);font-size:.62rem;
  letter-spacing:.15em;text-transform:uppercase;color:#8d8985}.note__form textarea,.note__form input{
  color:var(--home-ink);border:0;border-bottom:1px solid #525252;padding:.7rem 0;background:transparent;border-radius:0}
.note__form textarea{min-height:3.1rem;height:3.1rem}.note__form button{background:var(--home-red);padding:.85rem 1.6rem;color:#fff}
.note__hint{grid-column:1/-1;color:#8e8a86}.colophon{border-top:1px solid var(--home-rule);color:#8f8b87;background:#080909}
.colophon dt{color:#696663}.colophon a{border-color:#444}.home-red{color:var(--home-red)}
@media(max-width:56rem){
  .mast__nav{display:none}.menu{display:block}.signal{display:none}.hero__copy{padding-bottom:3rem}
  .section-head{grid-template-columns:1fr}.section-head p{align-self:auto}.evidence-grid,.evolution,.about,.contact__head{grid-template-columns:1fr}
  .evolution__media{order:2}.about{gap:2rem}.method{grid-template-columns:repeat(2,1fr)}
  .method__step:nth-child(2){border-right:0}.method__step:nth-child(n+3){border-top:1px solid var(--home-rule)}
  .method__step:last-child{grid-column:1/-1}.note__form{grid-template-columns:1fr}
}
@media(max-width:40rem){
  .home-shell,.mast__in,.hero__copy{width:min(100% - 1.5rem,74rem)}.hero{min-height:39rem}
  .hero__media{height:100%}.hero__media video,.hero__media img{object-position:58% center}.hero h1{font-size:2.65rem;max-width:100%}
  .hero__sub{font-size:1.02rem}.hero__cta{min-width:0;width:100%}.chapters{padding-bottom:4rem}
  .chapter{grid-template-columns:1.7rem minmax(0,1fr) auto 1rem;gap:.45rem;padding:.62rem 0}
  .chapter__title{font-size:1.16rem}.chapter__measure{font-size:.56rem;max-width:7.5rem}.chapter__arrow{font-size:1rem}
  .home-section{padding:4.5rem 0}.cards{grid-template-columns:1fr;gap:3.5rem}
  .card:nth-child(3),.card:nth-child(4),.card:nth-child(5){margin-top:0}.card:nth-child(2) .card__fig{aspect-ratio:16/10}
  .card:nth-child(5){grid-column:auto}.card:nth-child(5) .card__fig{aspect-ratio:16/10}
  .scale__grid{grid-template-columns:repeat(2,1fr)}.scale__grid>div:nth-child(2){border-right:0}
  .scale__grid>div:nth-child(n+3){border-top:1px solid var(--home-rule)}.plate__in,.ledger{padding:1.25rem}
  .sim__canvas{aspect-ratio:1.25}.sim__btn{margin-left:0}.method{grid-template-columns:1fr}
  .method__step,.method__step+.method__step{padding:1.35rem 0;border-right:0;border-top:1px solid var(--home-rule)}
  .method__step:first-child{border-top:0}.method__step:last-child{grid-column:auto}.method__step h3{margin-top:.8rem}
  .evolution{gap:2rem}.about__facts{display:grid}.contact{padding-top:5rem}.colophon dt{float:none;width:auto}
  .colophon dd{margin:0 0 1rem}.note__form textarea{height:5rem}
}
"""

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nandit Vaish</title>
<meta name="description" content="Business analytics, operational systems, applied AI and independent research by Nandit Vaish.">
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
  <div class="mast__in">
    <a class="mast__name" href="/">Nandit Vaish</a>
    <nav class="mast__nav">
      <a href="/market/">Market</a>
      <a href="/research-os/">Research OS</a>
      <a href="/film/">Film</a>
      <a href="/operations/">Operations</a>
    </nav>
    <details class="menu">
      <summary aria-label="Open navigation">Menu</summary>
      <nav aria-label="Mobile navigation">
        <a href="/market/">Market</a><a href="/research-os/">Research OS</a>
        <a href="/film/">Film</a><a href="/operations/">Operations</a>
        <a href="#meet">Meet Nandit</a><a href="#contact">Contact</a>
      </nav>
    </details>
  </div>
</header>

<main>
  <section class="hero">
    <div class="hero__media">
      <img src="/assets/generated/city-hero.webp" width="1672" height="941" fetchpriority="high" alt="A rain-soaked elevated road crossing a monochrome city at night">
      <div class="hero__scrim"></div>
    </div>
    <div class="hero__copy">
      <p class="hero__eyebrow">Data &middot; systems &middot; people &middot; outcomes</p>
      <h1>I build instruments that <em>argue back.</em></h1>
      <p class="hero__sub">Business analytics &middot; Operational systems &middot;
        Applied AI &middot; Independent research</p>
      <a class="hero__cta" href="#work"><span>Enter the work</span><span aria-hidden="true">&rarr;</span></a>
    </div>
  </section>

  <section class="chapters" id="work">
    <div class="home-shell">
      <div class="chapters__head"><span>Select a chapter</span><span>/ 01&ndash;05</span></div>
      <a class="chapter" href="/market/"><span class="chapter__no">01</span><span class="chapter__title">Market research</span><span class="chapter__measure">252M rows</span><span class="chapter__arrow" aria-hidden="true">&rarr;</span></a>
      <a class="chapter" href="/research-os/"><span class="chapter__no">02</span><span class="chapter__title">India from orbit</span><span class="chapter__measure">318,706 cells</span><span class="chapter__arrow" aria-hidden="true">&rarr;</span></a>
      <a class="chapter" href="/research-os/#referee"><span class="chapter__no">03</span><span class="chapter__title">Research OS</span><span class="chapter__measure">60 threads</span><span class="chapter__arrow" aria-hidden="true">&rarr;</span></a>
      <a class="chapter" href="/film/"><span class="chapter__no">04</span><span class="chapter__title">Film</span><span class="chapter__measure">1,158 frames</span><span class="chapter__arrow" aria-hidden="true">&rarr;</span></a>
      <a class="chapter" href="/operations/"><span class="chapter__no">05</span><span class="chapter__title">Operations</span><span class="chapter__measure">Websites &rarr; process systems</span><span class="chapter__arrow" aria-hidden="true">&rarr;</span></a>
    </div>
  </section>

  <section class="home-section">
    <div class="home-shell">
      <div class="section-head rv">
        <p class="section-label">Selected work / 01</p>
        <div><h2>Questions, made inspectable.</h2><p>Four rooms, one method: build an instrument, let it try to kill the idea, and keep every verdict it returns &mdash; the dead ones especially.</p></div>
      </div>
      <div class="cards">__CARDS__</div>
    </div>
  </section>

  <section class="home-section">
    <div class="home-shell">
      <div class="section-head rv">
        <p class="section-label">Evidence ledger / 02</p>
        <div><h2>What the instruments returned.</h2><p>The numbers are not decoration. They are the scale of the evidence, the record of what survived, and the open questions that remain.</p></div>
      </div>
      <div class="scale"><div class="scale__grid rv">__SCALE__</div></div>
      <div class="evidence-grid">
        <div class="plate rv">
          <div class="plate__in"><div class="sim">
            <div class="sim__head"><h2>Money behaves like a gas</h2><p>Two thousand agents start equal. They exchange at random; the dashed line is the distribution statistical physics predicts.</p></div>
            <canvas id="sim" class="sim__canvas" aria-label="Simulation of two thousand agents exchanging money at random"></canvas>
            <div class="sim__bar"><span class="sim__stat">Gini<b id="sim-gini">0.000</b></span><span class="sim__stat">Exchanges<b id="sim-tx">0</b></span><span class="sim__stat">Agents<b>2,000</b></span><button class="sim__btn" id="sim-replay" type="button">Run</button></div>
            <p class="plate__cap"><b>Nobody is smarter. Nobody cheats. The total never changes.</b> Inequality arrives anyway. Compare <button type="button" class="sim__switch" id="sim-label">money among people</button>.</p>
          </div></div>
        </div>
        <aside class="ledger rv">
          <h3>The ledger stays open.</h3>
          <p>Verified facts, observed behaviour, inference and open questions are labelled differently. A polished answer is never allowed to erase uncertainty.</p>
          <div class="ledger__rows">
            <div class="ledger__row"><span>Market hypotheses</span><b>41 dead &middot; 4 trusted</b></div>
            <div class="ledger__row"><span>Satellite referee</span><b>AUC 0.486</b></div>
            <div class="ledger__row"><span>Research record</span><b>Every verdict kept</b></div>
            <div class="ledger__row"><span>Current state</span><b>Open by design</b></div>
          </div>
        </aside>
      </div>
    </div>
  </section>

  <section class="home-section">
    <div class="home-shell">
      <div class="section-head rv"><p class="section-label">Method / 03</p><div><h2>One method, across different worlds.</h2><p>Markets, satellite data, film and business operations look unrelated. The work underneath them follows the same five moves.</p></div></div>
      <div class="method rv">
        <div class="method__step"><span class="method__no">01</span><h3>Observe</h3><p>Start with what is actually there.</p></div>
        <div class="method__step"><span class="method__no">02</span><h3>Structure</h3><p>Turn the mess into a system.</p></div>
        <div class="method__step"><span class="method__no">03</span><h3>Measure</h3><p>Put numbers on the important parts.</p></div>
        <div class="method__step"><span class="method__no">04</span><h3>Challenge</h3><p>Try to break the first answer.</p></div>
        <div class="method__step"><span class="method__no">05</span><h3>Document</h3><p>Keep the evidence and the unknowns.</p></div>
      </div>
    </div>
  </section>

  <section class="home-section">
    <div class="home-shell evolution rv">
      <div class="evolution__media"><img src="/assets/generated/operations-table.webp" width="1536" height="1024" alt="Ledgers, process cards and a dashboard made into a visible operating system" loading="lazy"></div>
      <div class="evolution__copy">
        <p class="section-label">Operations / 04</p>
        <h2>From websites to process systems.</h2>
        <p class="evolution__trail">ClearFlow experiment <span>/</span> Lantern websites <span>&rarr;</span> process and business transformation</p>
        <p>ClearFlow tested automation. Lantern began with websites. The work evolved into mapping how owner-run businesses actually run, putting numbers on their processes, and building the small systems that keep working when the owner is not in the room. Websites remain a secondary line.</p>
        <a class="evolution__link" href="/operations/">Read the operations ledger &rarr;</a>
      </div>
    </div>
  </section>

  <section class="home-section" id="meet">
    <div class="home-shell about rv">
      <div><p class="section-label">Meet Nandit / 05</p><h2>Nandit Vaish.</h2></div>
      <div class="about__body">
        <p class="about__lede">Business analytics, finance transformation, and practical systems.</p>
        <p class="about__text">I work where messy operations meet evidence: understanding how a process really runs, structuring the data around it, and building tools that make better decisions possible. The research on this site is the same method under different conditions.</p>
        <div class="about__facts"><span class="about__fact">Big 4 &middot; finance transformation</span><span class="about__fact">Business analytics</span><span class="about__fact">Independent research &middot; built in public</span></div>
      </div>
    </div>
  </section>

  <section class="contact" id="contact">
    <div class="home-shell">
      <div class="contact__head rv">
        <h2>Bring me a problem worth measuring.</h2>
        <div class="contact__side"><p>A difficult dataset, a process held together by memory, or an idea that needs a proper referee.</p><a class="contact__mail" href="mailto:__MAIL__">__MAIL__</a></div>
      </div>
      <div class="note rv">
        <p class="note__t">Start a conversation</p>
        <form class="note__form">
          <div class="note__field"><label for="note-body">Your note</label><textarea id="note-body" name="body" required placeholder="A question, a correction, or something worth investigating."></textarea></div>
          <div class="note__field"><label for="note-from">How to reach you</label><input id="note-from" type="text" name="from" placeholder="Email or phone (optional)"></div>
          <button type="submit">Send</button>
          <p class="note__hint">Goes to Nandit only. Not published or shared.</p>
        </form>
      </div>
    </div>
  </section>
</main>

<footer class="colophon">
  <div class="col-wide">
    <dl>
      <dt>Contact</dt><dd><a href="mailto:__MAIL__">__MAIL__</a></dd>
      <dt>Lantern</dt><dd><a href="https://airlantern.com">airlantern.com</a> &mdash; process and business transformation; websites remain a secondary line</dd>
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
            .replace("__CSS__", CSS + HOME_CSS)
            .replace("__SCALE__", scale_html)
            .replace("__CARDS__", cards_html)
            .replace("__REVEAL__", REVEAL_JS)
            .replace("__NOTE__", NOTE_JS)
            .replace("__SIM__", SIM_JS)
            .replace("__MAIL__", MAIL))

(OUT/"index.html").write_text(HTML, encoding="utf-8")
print("built index.html  (%s)  %s bytes" % ("PROD" if PROD else "preview, noindex", f"{len(HTML):,}"))
