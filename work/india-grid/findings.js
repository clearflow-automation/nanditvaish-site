/* Animated storyboard for the land & people findings.
   Every chart shows WHAT WE EXPECTED as a dashed ghost, then animates in WHAT WE GOT. */
(function () {
  const EASE = k => 1 - Math.pow(1 - k, 3);
  const clamp = (v, a, b) => v < a ? a : v > b ? b : v;
  const uid = (() => { let i = 0; return () => "g" + (++i); })();

  function anim(dur, fn) {
    const t0 = performance.now(); let done = false;
    const finish = () => { if (done) return; done = true; fn(1); };
    const step = t => {
      if (done) return;
      const k = clamp((t - t0) / dur, 0, 1);
      if (k >= 1) return finish();
      fn(EASE(k)); requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
    setTimeout(finish, dur + 150);          // rAF is paused in a background tab — never strand a number
  }
  const T = (x, y, t, o = {}) => `<text x="${x}" y="${y}" fill="${o.f || "#8b97a5"}" font-size="${o.s || 9.5}"` +
    ` text-anchor="${o.a || "start"}" font-family="ui-sans-serif"${o.w ? ' font-weight="600"' : ""}` +
    `${o.id ? ` id="${o.id}"` : ""}${o.op != null ? ` opacity="${o.op}"` : ""}>${t}</text>`;
  const R = (x, y, w, h, f, o = {}) => `<rect x="${x}" y="${y}" width="${Math.max(w, 0)}" height="${Math.max(h, 0)}"` +
    ` fill="${f}" rx="${o.r != null ? o.r : 2}"${o.id ? ` id="${o.id}"` : ""}${o.op != null ? ` opacity="${o.op}"` : ""}` +
    `${o.stroke ? ` stroke="${o.stroke}" stroke-width="1" stroke-dasharray="${o.dash || "3 3"}"` : ""}/>`;
  const SVG = (w, h, b) => `<svg viewBox="0 0 ${w} ${h}" width="100%" style="display:block">${b}</svg>`;
  const GHOST = "#6f7d8c", GOT = "#5eead4", BAD = "#c2603f", NEU = "#4a5560";

  /* ---------- Q3 reservoir ---------- */
  function chartReservoir(q) {
    const r = q.result, W = 740, x0 = 176, w = W - x0 - 96, H = 168;
    const sc = v => v / 0.62 * w;
    const rows = [
      ["Reservoir cells", r.coupling_water, GOT, "predicted to tower over cropland"],
      ["Cropland, matched", r.coupling_land, NEU, "the control"],
      ["Shuffled-year null", r.null_water, "#3a444f", "what pure noise scores"]];
    const ids = rows.map(() => uid());
    let b = R(0, 0, W, H, "#0e1216", { r: 0 });
    b += `<line x1="${x0 + sc(0.60)}" y1="30" x2="${x0 + sc(0.60)}" y2="${H - 18}" stroke="${GHOST}" stroke-width="1.6" stroke-dasharray="5 4" opacity=".75"/>`;
    b += T(x0 + sc(0.60) - 6, 24, "expected ≈0.60 for reservoirs", { a: "end", s: 9, f: GHOST });
    rows.forEach((rw, i) => {
      const y = 44 + i * 34;
      b += T(x0 - 9, y + 13, rw[0], { a: "end", s: 10.6, f: "#c3cdd8", w: i === 0 });
      b += T(x0 - 9, y + 24, rw[3], { a: "end", s: 8.4, f: "#5b6672" });
      b += R(x0, y, 0, 17, rw[2], { id: ids[i] });
      b += T(0, y + 13, "", { id: ids[i] + "t", s: 10.4, f: rw[2], w: 1 });
    });
    b += `<line x1="${x0}" y1="38" x2="${x0}" y2="${H - 16}" stroke="#242b33"/>`;
    b += T(x0, H - 4, "0", { s: 9 }) + T(x0 + sc(0.6), H - 4, "0.60  Spearman ρ", { a: "middle", s: 9 });
    return {
      html: SVG(W, H, b), play: () => anim(1100, p => rows.forEach((rw, i) => {
        const v = rw[1] * p, e = document.getElementById(ids[i]), t = document.getElementById(ids[i] + "t");
        if (!e) return; e.setAttribute("width", Math.max(sc(v), 0));
        t.setAttribute("x", x0 + Math.max(sc(v), 0) + 8); t.textContent = v.toFixed(3);
      }))
    };
  }

  /* ---------- Q4 building ---------- */
  function chartBuilding(q) {
    const ts = q.result.tests, W = 740, x0 = 52, H = 220, bw = (W - x0 - 24) / ts.length;
    const lo = 0.30, hi = 1.0, y = v => 176 - (clamp(v, lo, hi) - lo) / (hi - lo) * 140;
    let b = R(0, 0, W, H, "#0e1216", { r: 0 });
    b += R(x0, y(0.75), W - x0 - 24, y(0.65) - y(0.75), GHOST, { op: .16, r: 3 });
    b += T(W - 28, y(0.70) + 3, "expected band", { a: "end", s: 9, f: GHOST });
    b += `<line x1="${x0}" y1="${y(0.5)}" x2="${W - 24}" y2="${y(0.5)}" stroke="#e6ebf1" stroke-dasharray="3 3" opacity=".5"/>`;
    b += T(x0 - 6, y(0.5) + 3, "0.50", { a: "end", s: 9, f: "#e6ebf1" });
    b += T(x0 - 6, y(1.0) + 3, "1.00", { a: "end", s: 9 }) + T(x0 - 6, y(0.30) + 3, "0.30", { a: "end", s: 9 });
    const ids = ts.map(() => uid());
    ts.forEach((t, i) => {
      const cx = x0 + i * bw + bw * 0.5, isB = t.timing === "baseline";
      b += R(cx - bw * 0.24, y(0.5), bw * 0.48, 0, isB ? "#f5c77e" : BAD, { id: ids[i] });
      b += T(cx, 0, "", { id: ids[i] + "t", a: "middle", s: 10.2, f: isB ? "#f5c77e" : BAD, w: 1 });
      const lab = isB ? "trivial baseline" : t.timing;
      b += T(cx, 194, lab, { a: "middle", s: 9.4, f: isB ? "#f5c77e" : "#c3cdd8", w: isB });
      b += T(cx, 205, t.predictor, { a: "middle", s: 8.3, f: "#5b6672" });
      b += T(cx, 215, "n=" + t.n.toLocaleString(), { a: "middle", s: 8.3, f: "#5b6672" });
    });
    return {
      html: SVG(W, H, b), play: () => anim(1300, p => ts.forEach((t, i) => {
        const v = 0.5 + (t.auc - 0.5) * p, e = document.getElementById(ids[i]), tx = document.getElementById(ids[i] + "t");
        if (!e) return;
        const yt = Math.min(y(v), y(0.5)), h = Math.abs(y(v) - y(0.5));
        e.setAttribute("y", yt); e.setAttribute("height", h);
        tx.setAttribute("y", (v >= 0.5 ? yt - 5 : yt + h + 12)); tx.textContent = v.toFixed(3);
      }))
    };
  }

  /* ---------- Q5 sprawl ---------- */
  function chartSprawl(q) {
    const st = q.result.steps, W = 740, x0 = 92, w = W - x0 - 130, H = 40 + st.length * 40;
    const COL = { "core (>5% built)": "#f5c77e", "fringe (0.5–5%)": GOT, "rural (<0.5%)": "#4a5560" };
    let b = R(0, 0, W, H, "#0e1216", { r: 0 });
    const ids = st.map(() => uid());
    st.forEach((s, i) => {
      const y = 26 + i * 40;
      b += T(x0 - 10, y + 15, s.from + "→" + s.to, { a: "end", s: 10.4, f: "#c3cdd8", w: 1 });
      s.strata.forEach((x, j) => { b += R(x0, y, 0, 21, COL[x.stratum] || NEU, { id: ids[i] + "_" + j, r: 0 }); });
      b += T(0, y + 15, "", { id: ids[i] + "f", s: 10, f: GOT, w: 1 });
    });
    let lx = x0;
    Object.keys(COL).forEach(k => { b += R(lx, 6, 9, 9, COL[k]); b += T(lx + 13, 14, k, { s: 9, f: "#c3cdd8" }); lx += k.length * 5.6 + 34; });
    return {
      html: SVG(W, H, b), play: () => anim(1500, p => st.forEach((s, i) => {
        const k = clamp(p * st.length - i, 0, 1); let acc = 0;
        s.strata.forEach((x, j) => {
          const e = document.getElementById(ids[i] + "_" + j); if (!e) return;
          const ww = x.share * w * k; e.setAttribute("x", x0 + acc); e.setAttribute("width", ww); acc += ww;
        });
        const t = document.getElementById(ids[i] + "f");
        if (t) { t.setAttribute("x", x0 + acc + 9); t.textContent = (s.strata[1].share * 100 * k).toFixed(1) + "% fringe"; }
      }))
    };
  }

  /* ---------- Q6 fringe ---------- */
  function chartFringe(q) {
    const g = q.result.groups, W = 740, x0 = 168, mid = x0 + 150, H = 34 + g.length * 30;
    const mx = Math.max(...g.map(d => Math.abs(d.driftz))) * 1.25, sc = v => v / mx * 140;
    let b = R(0, 0, W, H, "#0e1216", { r: 0 });
    b += `<line x1="${mid}" y1="18" x2="${mid}" y2="${H - 14}" stroke="#3a444f"/>`;
    b += T(mid, 12, "0 = typical for its land cover", { a: "middle", s: 9, f: "#8b97a5" });
    const ids = g.map(() => uid());
    g.forEach((d, i) => {
      const y = 24 + i * 30, hot = d.group.indexOf("→") >= 0;
      b += T(x0 - 10, y + 13, d.group, { a: "end", s: 10.4, f: hot ? GOT : "#c3cdd8", w: hot });
      b += T(x0 - 10, y + 23, "n=" + d.n.toLocaleString() + " · built +" + d.built_gain_pp.toFixed(2) + "pp", { a: "end", s: 8.3, f: "#5b6672" });
      b += R(mid, y, 0, 17, hot ? GOT : NEU, { id: ids[i] });
      b += T(0, y + 13, "", { id: ids[i] + "t", s: 10, f: hot ? GOT : "#8b97a5", w: 1 });
    });
    b += R(mid + sc(mx * 0.62), 22, 3, H - 40, GHOST, { op: .5, r: 1 });
    b += T(mid + sc(mx * 0.62) + 8, 16, "expected the arrows here", { s: 9, f: GHOST });
    return {
      html: SVG(W, H, b), play: () => anim(1100, p => g.forEach((d, i) => {
        const v = d.driftz * p, e = document.getElementById(ids[i]), t = document.getElementById(ids[i] + "t");
        if (!e) return; const ww = Math.abs(sc(v));
        e.setAttribute("x", v < 0 ? mid - ww : mid); e.setAttribute("width", ww);
        t.setAttribute("x", v < 0 ? mid - ww - 8 : mid + ww + 8);
        t.setAttribute("text-anchor", v < 0 ? "end" : "start");
        t.textContent = (v >= 0 ? "+" : "") + v.toFixed(3);
      }))
    };
  }

  /* ---------- Q7 people: the U ---------- */
  function chartPeople(q) {
    const d = q.result.deciles, W = 740, L = 62, Rg = 28, TP = 26, BT = 44, H = 250;
    const xs = d.map(p => p.pop_growth_pct), ys = d.map(p => p.driftz);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = 0.15, y1 = Math.max(...ys) * 1.15;
    const X = v => L + (v - x0) / (x1 - x0) * (W - L - Rg);
    const Y = v => H - BT - (clamp(v, y0, y1) - y0) / (y1 - y0) * (H - TP - BT);
    let b = R(0, 0, W, H, "#0e1216", { r: 0 });
    for (let i = 0; i <= 4; i++) { const v = y0 + (y1 - y0) * i / 4; b += `<line x1="${L}" y1="${Y(v)}" x2="${W - Rg}" y2="${Y(v)}" stroke="#1b212a"/>` + T(L - 7, Y(v) + 3, v.toFixed(2), { a: "end", s: 8.8 }); }
    b += `<line x1="${X(0)}" y1="${TP}" x2="${X(0)}" y2="${H - BT}" stroke="#3a444f" stroke-dasharray="2 3"/>`;
    b += T(X(0), H - BT + 25, "no change", { a: "middle", s: 8.6, f: "#5b6672" });
    b += `<line x1="${L}" y1="${Y(ys[0])}" x2="${W - Rg}" y2="${Y(Math.max(...ys))}" stroke="${GHOST}" stroke-width="1.6" stroke-dasharray="5 4" opacity=".6"/>`;
    b += T(W - Rg, Y(Math.max(...ys)) - 8, "what we expected: a straight rise", { a: "end", s: 9, f: GHOST });
    b += `<path id="upath" d="" fill="none" stroke="${GOT}" stroke-width="2.2" stroke-linejoin="round"/>`;
    d.forEach((p, i) => { b += `<circle id="uc${i}" cx="${X(p.pop_growth_pct)}" cy="${Y(p.driftz)}" r="0" fill="${GOT}"/>`; });
    b += T(L, H - 8, "← population shrinking", { s: 9.4, f: "#8b97a5" });
    b += T(W - Rg, H - 8, "population booming →", { a: "end", s: 9.4, f: "#8b97a5" });
    b += T(L - 7, TP - 10, "corrected drift", { s: 9.4, f: "#8b97a5" });
    d.forEach(p => { b += T(X(p.pop_growth_pct), H - BT + 14, (p.pop_growth_pct > 0 ? "+" : "") + p.pop_growth_pct.toFixed(0) + "%", { a: "middle", s: 8.4, f: "#5b6672" }); });
    return {
      html: SVG(W, H, b), play: () => anim(1700, p => {
        const n = clamp(p * d.length, 0, d.length); let path = "";
        d.forEach((q2, i) => {
          const c = document.getElementById("uc" + i); if (!c) return;
          const on = i < n; c.setAttribute("r", on ? (i === 0 || i === d.length - 1 ? 5 : 3.4) : 0);
          if (on) path += (path ? "L" : "M") + X(q2.pop_growth_pct) + " " + Y(q2.driftz);
        });
        const pe = document.getElementById("upath"); if (pe) pe.setAttribute("d", path);
      })
    };
  }

  const BUILDERS = { reservoir: chartReservoir, building: chartBuilding, sprawl: chartSprawl, fringe: chartFringe, people: chartPeople };

  window.renderLandReport = function (data) {
    if (!data) return { html: '<p class="meta">Run <code>python3 src/q3_landvalue.py</code> to generate this report.</p>', play: () => { } };
    const parts = [], plays = [];
    data.questions.forEach((q, i) => {
      const c = (BUILDERS[q.id] || (() => ({ html: "", play: () => { } })))(q);
      const vid = uid(); plays.push({ id: vid, play: c.play });
      parts.push(`
      <div class="find">
        <h3><span class="badge ${q.verdict_class}">${q.verdict}</span> Q${i + 3} · ${q.title}</h3>
        <p class="whytag">${q.tag}</p>
        <p>${q.why}</p>
        <div class="pred"><span class="plab">What we expected</span>${q.expected}</div>
        <div class="chart">${c.html}
          <button class="replay" data-play="${vid}">↻ replay</button></div>
        <div class="pred got"><span class="plab">What we got</span>${q.got}</div>
        <p class="cap2"><b>How:</b> ${q.method}</p>
      </div>`);
    });
    return {
      html: `<div class="q">Report 2 · land, people and the limits of the signal</div>
        <h2>Can this grid say anything about where land gets valuable?</h2>
        <div class="meta">${data.n_cells.toLocaleString()} cells · five questions, each with its prediction
        written before the test · <code>python3 src/q3_landvalue.py</code></div>
        <div class="warn">${data.note_prices}</div>
        ${parts.join("")}
        <div class="sofar">${data.verdict_html || ""}</div>`,
      play: () => plays.forEach((p, i) => setTimeout(p.play, 120 + i * 90)),
      plays
    };
  };
})();
