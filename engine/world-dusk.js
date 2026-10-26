// Repo2Reels world: "dusk skyline".
// The night scene behind the hook (canvas #sky: skyline at dusk, lit windows, water reflections, bokeh)
// and the day scene's line-art skyline (svg #dayart) that draws itself in after the iris.
// A world must define: drawNight(t), cv (the night canvas), SKY + SKYLEN (the day line art path and its
// length), ART.hz (the day horizon), and #sunGrp / #sunDisc / #sunHalo in #dayart. See docs/writing-scenes.md.
const eo = EO, eio = EIO, ei = EI, back = x => { const c = 1.5; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2) };
// ---------------- skyline world
const HZ = Math.round(V ? H * 0.60 : H * 0.665);
function layer(seed, hMin, hMax, wMin, wMax, gap) {
  const r = rng(seed), out = []; let x = -80;
  while (x < W + 80) {
    const w = wMin + r() * (wMax - wMin), h = hMin + Math.pow(r(), 1.4) * (hMax - hMin);
    const kind = r() < .18 ? 'spire' : (r() < .35 ? 'step' : 'flat');
    const win = []; const r2 = rng(Math.floor(r() * 1e9));
    for (let wy = 14; wy < h - 10; wy += 13) for (let wx = 7; wx < w - 9; wx += 10) {
      if (r2() < .42) win.push([wx, wy, .2 + r2() * 3.4, r2() < .06 ? r2() * 6.28 : -1]);
    }
    out.push({ x, w, h, kind, win, sw: .45 + r() * .3 });
    x += w + r() * gap;
  }
  return out;
}
const S = V ? 1.0 : 1.0;
const FAR = layer(11, 40, V ? 190 : 170, 40, 120, 14);
const MID = layer(23, 70, V ? 330 : 300, 34, 92, 22);
const NEAR = layer(37, 30, V ? 170 : 150, 60, 150, 8);
const HEROX = V ? W * 0.68 : W * 0.64;
const HEROSEG = (V ? [[104, 200], [86, 150], [68, 110], [52, 80], [38, 56], [24, 34], [10, 22]] : [[92, 160], [76, 118], [60, 86], [46, 62], [32, 42], [20, 26], [8, 18]]);
const HEROH = HEROSEG.reduce((a, s) => a + s[1], 0);

function drawBuildings(c, L, col, winCol, winA, t, lightsOn) {
  c.fillStyle = col;
  for (const b of L) {
    c.beginPath();
    if (b.kind === 'step') { const sw = b.w * b.sw; c.rect(b.x, HZ - b.h * .78, b.w, b.h * .78); c.rect(b.x + (b.w - sw) / 2, HZ - b.h, sw, b.h * .22 + 1); }
    else c.rect(b.x, HZ - b.h, b.w, b.h);
    c.fill();
    if (b.kind === 'spire') { c.fillRect(b.x + b.w / 2 - 1.5, HZ - b.h - 34, 3, 34); }
  }
  if (!winCol) return;
  for (const b of L) {
    for (const w of b.win) {
      if (t < w[2] || !lightsOn) continue;
      let a = winA * Math.min(1, (t - w[2]) / .35);
      if (w[3] >= 0) a *= .55 + .45 * Math.sin(t * 3.1 + w[3]);
      if (b.kind === 'step' && w[1] > b.h * .78) continue;
      c.globalAlpha = a; c.fillStyle = winCol; c.fillRect(b.x + w[0], HZ - b.h + w[1], 4, 6);
    }
  }
  c.globalAlpha = 1;
}
function drawHero(c, col, t, withWin) {
  let y = HZ; c.fillStyle = col;
  for (const [w, h] of HEROSEG) { c.fillRect(HEROX - w / 2, y - h, w, h); y -= h; }
  c.fillRect(HEROX - 1.5, y - 70, 3, 70);
  if (!withWin) return;
  y = HZ; const r = rng(99);
  for (const [w, h] of HEROSEG) {
    for (let wy = 10; wy < h - 6; wy += 11) for (let wx = 6; wx < w - 8; wx += 9) {
      const th = .4 + r() * 3.0; if (r() < .5 || t < th) continue;
      c.globalAlpha = .75 * Math.min(1, (t - th) / .35); c.fillStyle = '#f6cf86'; c.fillRect(HEROX - w / 2 + wx, y - h + wy, 3, 5);
    }
    y -= h;
  }
  c.globalAlpha = 1;
}

const cv = $('sky'); cv.width = W; cv.height = H; const ctx = cv.getContext('2d');
const off = document.createElement('canvas'); off.width = W; off.height = HZ + 2; const oc = off.getContext('2d');
const SUNX = V ? W * 0.36 : W * 0.42;

function drawNight(t) {
  const c = p(t, 0, 8.4);
  const s = 1 + .055 * eio(c);
  const ox = W * .55;
  // sky
  const g = ctx.createLinearGradient(0, 0, 0, HZ);
  g.addColorStop(0, '#021412'); g.addColorStop(.42, '#05302b'); g.addColorStop(.74, '#0c4f48');
  g.addColorStop(.9, '#5f6b45'); g.addColorStop(.97, '#c08a4a'); g.addColorStop(1, '#f0c579');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, HZ + 1);
  // sun
  const sunY = HZ - 26 + 46 * c;
  const sg = ctx.createRadialGradient(SUNX, sunY, 10, SUNX, sunY, V ? 620 : 560);
  sg.addColorStop(0, 'rgba(246,208,138,.55)'); sg.addColorStop(.25, 'rgba(212,160,83,.22)'); sg.addColorStop(1, 'rgba(212,160,83,0)');
  ctx.fillStyle = sg; ctx.fillRect(0, 0, W, HZ);
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, HZ); ctx.clip();
  ctx.fillStyle = '#fbe0a4'; ctx.beginPath(); ctx.arc(SUNX, sunY, V ? 50 : 46, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  // skyline into offscreen, with camera + parallax
  oc.setTransform(1, 0, 0, 1, 0, 0); oc.clearRect(0, 0, W, HZ + 2);
  const cam = (k) => { const dx = -t * k; oc.setTransform(s, 0, 0, s, ox - ox * s + dx * s, HZ - HZ * s); };
  cam(3); drawBuildings(oc, FAR, '#1d564d', null, 0, t, false);
  // haze over far layer
  oc.setTransform(1, 0, 0, 1, 0, 0);
  const hz = oc.createLinearGradient(0, HZ - 220, 0, HZ); hz.addColorStop(0, 'rgba(192,138,74,0)'); hz.addColorStop(1, 'rgba(192,138,74,.28)');
  oc.globalCompositeOperation = 'source-atop'; oc.fillStyle = hz; oc.fillRect(0, HZ - 220, W, 222); oc.globalCompositeOperation = 'source-over';
  cam(8); drawBuildings(oc, MID, '#0a3a35', '#f2c77c', .55, t, true); drawHero(oc, '#0a3a35', t, true);
  cam(15); drawBuildings(oc, NEAR, '#052824', '#f6cf86', .8, t, true);
  ctx.drawImage(off, 0, 0);
  // water
  const wg = ctx.createLinearGradient(0, HZ, 0, H);
  wg.addColorStop(0, '#0b3f39'); wg.addColorStop(.25, '#062c28'); wg.addColorStop(1, '#021412');
  ctx.fillStyle = wg; ctx.fillRect(0, HZ, W, H - HZ);
  const gl = ctx.createLinearGradient(0, HZ, 0, HZ + 160); gl.addColorStop(0, 'rgba(240,197,121,.35)'); gl.addColorStop(1, 'rgba(240,197,121,0)');
  ctx.fillStyle = gl; ctx.fillRect(0, HZ, W, 160);
  // reflection strips
  const D = H - HZ;
  for (let y = 0; y < D; y += 2) {
    const sy = HZ - 1 - y * 0.92; if (sy < 0) break;
    const amp = 1.5 + y * .045;
    const dx = Math.sin(y * .11 + t * 2.4) * amp + Math.sin(y * .043 - t * 1.3) * amp * .6;
    ctx.globalAlpha = .5 * Math.pow(1 - y / D, 1.3);
    ctx.drawImage(off, 0, sy, W, 2, dx, HZ + y, W, 2);
  }
  ctx.globalAlpha = 1;
  // sun glitter
  const r = rng(Math.floor(t * 12));
  for (let k = 0; k < 34; k++) {
    const yy = HZ + 6 + k * (V ? 9 : 7); if (yy > H) break;
    const w = (V ? 90 : 80) * (1 - k / 40) * (.5 + r());
    ctx.globalAlpha = (.55 - k * .014) * (.4 + .6 * r());
    ctx.fillStyle = '#f6d396'; ctx.fillRect(SUNX - w / 2 + Math.sin(k + t * 3) * 6, yy, w, 2);
  }
  ctx.globalAlpha = 1;
  // bokeh
  for (const b of BOKEH) {
    const x = b.x + Math.sin(t * .35 + b.ph) * 30 - t * b.vx, y = b.y - t * b.vy;
    const g2 = ctx.createRadialGradient(x, y, 0, x, y, b.r);
    g2.addColorStop(0, `rgba(246,208,138,${b.a})`); g2.addColorStop(.6, `rgba(246,208,138,${b.a * .55})`); g2.addColorStop(1, 'rgba(246,208,138,0)');
    ctx.fillStyle = g2; ctx.beginPath(); ctx.arc(x, y, b.r, 0, Math.PI * 2); ctx.fill();
  }
}
const BOKEH = []; { const r = rng(77); for (let i = 0; i < (V ? 12 : 14); i++) BOKEH.push({ x: r() * W, y: (V ? .25 : .15) * H + r() * H * .7, r: 18 + r() * 46, a: .05 + r() * .09, vx: 2 + r() * 5, vy: 3 + r() * 6, ph: r() * 6.28 }); }


const ART = { sc: V ? .55 : .5, hz: V ? 1840 : 1050 };
{
  const step = 3; let d = `M0 ${ART.hz}`;
  const prof = x => { let m = 0; for (const b of MID) if (x >= b.x && x <= b.x + b.w) m = Math.max(m, b.kind === 'step' && Math.abs(x - (b.x + b.w / 2)) > b.w * b.sw / 2 ? b.h * .78 : b.h);
    let y = 0; for (const [w, h] of HEROSEG) { if (Math.abs(x - HEROX) <= w / 2) m = Math.max(m, y + h); y += h; } return m; };
  let last = -1;
  for (let x = 0; x <= W; x += step) { const h = prof(x) * ART.sc; const y = (ART.hz - h).toFixed(1); if (y !== last) { d += ` L${x} ${last === -1 ? ART.hz : last} L${x} ${y}`; last = y; } }
  d += ` L${W} ${last} L${W} ${ART.hz}`;
  const svg = $('dayart'); svg.setAttribute('width', W); svg.setAttribute('height', H); svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.innerHTML = `<defs><radialGradient id="sunG"><stop offset="0" stop-color="#f6d08a" stop-opacity=".9"/><stop offset=".35" stop-color="#f0c579" stop-opacity=".35"/><stop offset="1" stop-color="#f0c579" stop-opacity="0"/></radialGradient></defs>
    <g id="sunGrp"><circle id="sunHalo" cx="${SUNX}" cy="${ART.hz}" r="${V ? 380 : 300}" fill="url(#sunG)"/><circle id="sunDisc" cx="${SUNX}" cy="${ART.hz}" r="${V ? 58 : 46}" fill="#e7b35f"/></g>
    <rect x="0" y="${ART.hz}" width="${W}" height="${H - ART.hz}" fill="#f0efea"/>
    <path id="skyline" d="${d}" fill="#f0efea" stroke="#0b4f4a" stroke-width="3" stroke-linejoin="round" opacity=".55"/>
    <line x1="0" y1="${ART.hz}" x2="${W}" y2="${ART.hz}" stroke="#d4a053" stroke-width="3"/>`;
}
const SKY = $('skyline'); const SKYLEN = SKY.getTotalLength(); SKY.style.strokeDasharray = SKYLEN;
