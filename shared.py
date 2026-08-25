"""Shared stylesheet for nanditvaish.com.

Single source of truth for the design tokens. The home page and the three project
notebooks all render from this; project pages append their own block on top.
"""

BASE_CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
  --paper:#f6f3ec; --paper-2:#efeade; --plate:#0a0b0d;
  --ink:#16181c; --ink-2:#4a4f57; --ink-3:#8b9098;
  --rule:#ddd6c8; --rule-2:#c9c0ad;
  --kill:#ae2f22; --live:#1c6553;
  --serif:'Newsreader',Georgia,'Times New Roman',serif;
  --mono:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
  --measure:38rem; --wide:64rem;
}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);
  font-size:clamp(1.0625rem,1rem + .25vw,1.1875rem);line-height:1.62;
  font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased}
h1,h2,h3{font-weight:500;line-height:1.16;margin:0;letter-spacing:-.012em;text-wrap:balance}
p{margin:0}
a{color:inherit;text-decoration:none;border-bottom:1px solid var(--rule-2)}
a:hover{border-color:var(--ink)}
::selection{background:var(--kill);color:var(--paper)}
:focus-visible{outline:2px solid var(--kill);outline-offset:3px;border-radius:1px}

.col{width:min(var(--measure),100% - 2.5rem);margin-inline:auto}
.col-wide{width:min(var(--wide),100% - 2.5rem);margin-inline:auto}

/* ---------- masthead ---------- */
.mast{border-bottom:1px solid var(--ink);margin-bottom:0}
.mast__in{display:flex;flex-wrap:wrap;gap:.75rem 1.5rem;align-items:baseline;
  justify-content:space-between;padding:1.1rem 0 .9rem}
.mast__name{font-family:var(--mono);font-size:.75rem;letter-spacing:.2em;
  text-transform:uppercase;border:0}
.mast__nav{display:flex;gap:1.25rem;font-family:var(--mono);font-size:.6875rem;
  letter-spacing:.14em;text-transform:uppercase;color:var(--ink-2)}
.mast__nav a{border:0}
.mast__nav a:hover{color:var(--ink);border-bottom:1px solid var(--ink)}
.mast__nav a[aria-current="page"]{color:var(--ink);border-bottom:1px solid var(--ink)}

/* ---------- abstract ---------- */
.abstract{padding:5rem 0 3.5rem;border-bottom:1px solid var(--rule)}
.abstract__eyebrow{font-family:var(--mono);font-size:.6875rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--ink-3);margin-bottom:1.75rem}
.abstract h1{font-size:clamp(2rem,1.3rem + 3vw,3.5rem);letter-spacing:-.025em;
  margin-bottom:1.75rem;text-wrap:balance}
.abstract h1 em{font-style:italic}
.abstract p+p{margin-top:1.1rem}
.abstract .lede{font-size:1.125em}
.drop::first-letter{float:left;font-size:3.6em;line-height:.84;padding:.06em .09em 0 0;
  font-weight:500}

/* ---------- plate (full-bleed dark) ---------- */
.plate{background:var(--plate);color:#e9edf2;margin:3.5rem 0;padding:0;
  border-top:1px solid var(--ink);border-bottom:1px solid var(--ink)}
.plate__in{width:min(var(--wide),100% - 2.5rem);margin-inline:auto;padding:2.5rem 0}
.plate__cap{font-family:var(--mono);font-size:.6875rem;letter-spacing:.1em;
  color:#8b9098;margin-top:1.25rem;line-height:1.6}
.plate__cap b{color:#e9edf2;font-weight:400}
.plate video,.plate img{display:block;width:100%;height:auto;border:1px solid #23262c}

/* ---------- figure (on paper) ---------- */
figure{margin:3.25rem 0}
figcaption{font-family:var(--mono);font-size:.6875rem;line-height:1.65;
  letter-spacing:.02em;color:var(--ink-2);margin-top:.9rem;
  padding-top:.7rem;border-top:1px solid var(--rule)}
figcaption b{font-weight:600;color:var(--ink)}

/* ---------- simulation canvas ---------- */
.sim{display:grid;gap:1.25rem}
.sim__head{max-width:58ch}
.sim__head h2{font-family:var(--serif);font-weight:400;font-size:clamp(1.375rem,1.2rem + .8vw,1.75rem);
  line-height:1.2;letter-spacing:-.02em;color:#e9edf2;margin:0 0 .6rem}
.sim__head p{font-family:var(--serif);font-size:1.0313rem;line-height:1.6;color:#b9c0c9;margin:0}
.sim a{color:#e9edf2;border-bottom:1px solid #3a3f47}
.sim a:hover{border-color:#e9edf2}
.sim__canvas{width:100%;aspect-ratio:16/7;background:#0a0b0d;display:block;
  border:1px solid #23262c}
.sim__bar{display:flex;flex-wrap:wrap;gap:1.5rem 2.25rem;align-items:baseline;
  font-family:var(--mono);font-size:.75rem;letter-spacing:.06em;color:#8b9098}
.sim__stat b{display:block;font-size:1.5rem;color:#e9edf2;font-weight:400;
  letter-spacing:0;margin-top:.2rem}
.sim__btn{margin-left:auto;background:none;border:1px solid #3a3f47;color:#e9edf2;
  font:inherit;font-family:var(--mono);font-size:.6875rem;letter-spacing:.12em;
  text-transform:uppercase;padding:.5rem 1rem;cursor:pointer}
.sim__btn:hover{border-color:#e9edf2}

/* ---------- scale band ---------- */
.scale{border-bottom:1px solid var(--rule);padding:3rem 0}
.scale__grid{display:grid;gap:2rem 1.5rem;grid-template-columns:repeat(2,minmax(0,1fr))}
@media(min-width:48rem){.scale__grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
.scale__n{font-size:1.875rem;line-height:1;letter-spacing:-.02em}
.scale__l{font-family:var(--mono);font-size:.6875rem;line-height:1.55;
  letter-spacing:.06em;color:var(--ink-2);margin-top:.55rem}

/* ---------- contents ---------- */
.contents{padding:3.5rem 0}
.contents__label{font-family:var(--mono);font-size:.6875rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--ink-3);margin-bottom:2rem}
.entry{display:block;border:0;border-top:1px solid var(--rule);padding:1.9rem 0;
  transition:background .18s ease}
.entry:last-of-type{border-bottom:1px solid var(--rule)}
.entry:hover{background:var(--paper-2)}
.entry__top{display:flex;gap:1rem;align-items:baseline;flex-wrap:wrap;
  font-family:var(--mono);font-size:.6875rem;letter-spacing:.1em;color:var(--ink-3)}
.entry__no{color:var(--ink)}
.entry__when{margin-left:auto}
.entry__t{font-size:1.5rem;margin:.7rem 0 .5rem;letter-spacing:-.018em}
.entry__d{color:var(--ink-2);font-size:.9688em}
.entry__verdicts{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.9rem}

/* ---------- verdict chips ---------- */
.chip{font-family:var(--mono);font-size:.625rem;letter-spacing:.1em;
  text-transform:uppercase;padding:.2rem .5rem;border:1px solid var(--rule-2);
  color:var(--ink-2);white-space:nowrap}
.chip--kill{border-color:var(--kill);color:var(--kill)}
.chip--live{border-color:var(--live);color:var(--live)}
.chip--flag{border-style:dashed}

/* ---------- note ---------- */
.note{border-top:1px solid var(--ink);padding:3rem 0 1rem}
.note__t{font-family:var(--mono);font-size:.6875rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--ink-3);margin-bottom:1rem}
.note__form{display:grid;gap:.85rem;max-width:32rem}
.note__form textarea,.note__form input{width:100%;background:transparent;
  border:1px solid var(--rule-2);padding:.7rem .85rem;color:var(--ink);
  font:inherit;font-size:.9375rem;font-family:var(--serif);resize:vertical}
.note__form textarea{min-height:5.5rem}
.note__form textarea:focus,.note__form input:focus{outline:none;border-color:var(--ink)}
.note__form button{justify-self:start;background:var(--ink);color:var(--paper);
  border:0;padding:.6rem 1.3rem;font-family:var(--mono);font-size:.6875rem;
  letter-spacing:.12em;text-transform:uppercase;cursor:pointer}
.note__form button[disabled]{opacity:.5}
.note__hint{font-family:var(--mono);font-size:.6875rem;color:var(--ink-3);line-height:1.6}
.note__state{font-family:var(--mono);font-size:.75rem;color:var(--live)}

/* ---------- colophon ---------- */
.colophon{border-top:1px solid var(--ink);padding:2.5rem 0 4rem;
  font-family:var(--mono);font-size:.6875rem;line-height:1.9;
  letter-spacing:.04em;color:var(--ink-2)}
.colophon dt{float:left;width:6.5rem;color:var(--ink-3)}
.colophon dd{margin:0 0 .1rem 6.5rem}
.colophon a{border-color:var(--rule-2)}

/* ---------- hero (showcase register) ---------- */
.hero{position:relative;background:var(--plate);border-bottom:1px solid var(--ink)}
.hero__media{position:relative;width:100%;aspect-ratio:16/9;max-height:78svh;overflow:hidden}
@media (max-width:40rem){.hero__media{aspect-ratio:auto;height:76svh;min-height:30rem}}
.hero__media video,.hero__media img{width:100%;height:100%;object-fit:cover;display:block}
.hero__scrim{position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(7,9,12,.50) 0%,rgba(7,9,12,.08) 30%,rgba(7,9,12,.55) 52%,rgba(7,9,12,.90) 76%,rgba(7,9,12,.97) 100%)}
.hero__text{position:absolute;inset:auto 0 0 0;padding:0 0 clamp(2.25rem,4.5vw,3.75rem)}
.hero__deck{margin-top:1.3rem;max-width:54ch;color:rgba(236,240,244,.92);
  font-size:clamp(.9688rem,.9rem + .45vw,1.1875rem);line-height:1.6;
  text-shadow:0 1px 14px rgba(7,9,12,.85)}
.hero__kicker{font-family:var(--mono);font-size:.6875rem;letter-spacing:.18em;
  text-transform:uppercase;color:rgba(233,237,242,.88);margin-bottom:1rem;text-shadow:0 1px 12px rgba(7,9,12,.9)}
.hero h1{color:#f7f8fa;text-shadow:0 2px 24px rgba(7,9,12,.75);font-size:clamp(1.75rem,1rem + 3.2vw,3.25rem);letter-spacing:-.028em;
  max-width:24ch;text-wrap:balance}
.hero h1 em{font-style:italic;color:#c9cfd6}

/* ---------- project cards ---------- */
.cards{padding:4.5rem 0 1rem;display:grid;gap:4.5rem}
.card{display:block;border:0;text-decoration:none}
.card__fig{background:var(--plate);border:1px solid var(--rule-2);overflow:hidden;
  aspect-ratio:16/9}
.card__fig img,.card__fig video{width:100%;height:100%;object-fit:cover;display:block;
  transition:transform .8s cubic-bezier(.2,.7,.3,1)}
.card:hover .card__fig img,.card:hover .card__fig video{transform:scale(1.02)}
.card__meta{display:flex;gap:1rem;align-items:baseline;flex-wrap:wrap;margin-top:1.1rem;
  font-family:var(--mono);font-size:.6875rem;letter-spacing:.12em;text-transform:uppercase;
  color:var(--ink-3)}
.card__no{color:var(--ink)}
.card__when{margin-left:auto;text-transform:none;letter-spacing:.06em}
.card h2{font-size:clamp(1.5rem,1.1rem + 1.5vw,2.25rem);margin:.6rem 0 .6rem;
  letter-spacing:-.022em}
.card p{color:var(--ink-2);max-width:52ch}
.card__go{display:inline-block;margin-top:1rem;font-family:var(--mono);font-size:.6875rem;
  letter-spacing:.12em;text-transform:uppercase;border-bottom:1px solid var(--rule-2);
  padding-bottom:.15rem}
.card:hover .card__go{border-color:var(--ink)}

/* ---------- graveyard swatch (market card) ---------- */
.graveWrap{position:relative;width:100%;height:100%;background:var(--plate);
  display:flex;align-items:center;justify-content:center}
.grave{display:grid;grid-template-columns:repeat(15,1fr);gap:6px;
  width:min(88%,40rem)}
.graveKey{position:absolute;left:clamp(1rem,4vw,2rem);bottom:clamp(1rem,4vw,2rem);
  display:flex;gap:1.15rem;font-family:var(--mono);font-size:.625rem;letter-spacing:.1em;
  text-transform:uppercase;color:#8b9098}
.graveKey b{color:#e9edf2;font-weight:400}
.graveKey s{display:inline-block;width:.55rem;height:.55rem;margin-right:.4rem;
  text-decoration:none;vertical-align:middle}
.grave i{display:block;aspect-ratio:1;background:#2a2d33}
.grave i.d{background:#ae2f22}
.grave i.t{background:#2f9e83}
.grave i.o{background:#f2b45c}
.grave i.x{background:#4a4f57}

/* ---------- reveal ---------- */
.js .rv{opacity:0;transform:translateY(10px);
  transition:opacity .6s cubic-bezier(.2,.7,.3,1),transform .6s cubic-bezier(.2,.7,.3,1)}
.js .rv.in{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.js .rv{opacity:1;transform:none;transition:none}}
"""
