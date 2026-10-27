"""Check before you post: contact sheets of the finished reels, plus layout and caption checks on the page.

- Contact sheet per reel: the cover, a frame every second, the middle of every transition, the first
  moment of the day scene and of the end card. Look at every frame: text off the edge, overlaps,
  a half-empty card, a "0" before a count starts, anything left over from the previous scene.
- Hook lines must end by x = 970 px (safe from the right-hand buttons).
- Every caption chunk must stay on screen long enough to read (0.4 s or more) and fit on one line.
- Captions and the topic label must actually be visible (a scene stylesheet can hide them by reusing a class
  name such as .plate or .lb), and no card or end-card note may reach down into the captions (y 1270 and below).
- Nothing should arrive in the last second before a cut: it is gone before anyone can read it.

    python3 -m r2r.qa projects/keyva [r11 ...]       -> build/<p>/qa/<rid>.jpg and a printed report
"""
import asyncio
import io
import json
import subprocess
import sys

from .common import H, W, chromium_args, load_project, out_name, reel_ids

HOOK_RIGHT = 970

PAGE_CHECK = '''() => {
  const hooks = [...document.querySelectorAll('.hook .ln')].map(d => { const ws = d.querySelectorAll('.w'), z = ws[ws.length - 1];
    return { text: d.textContent, right: d.parentElement.offsetLeft + z.offsetLeft + z.offsetWidth }; });
  const caps = CHUNKS.map(c => { render((c.show + c.hide) / 2); const p = document.getElementById('plate');
    return { text: c.items.map(i => i.txt).join(' '), up: c.hide - c.show, size: p.style.fontSize, h: p.offsetHeight }; });
  const opa = el => { let o = 1; for (let x = el; x && x !== document.documentElement; x = x.parentElement) {
    const cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= +cs.opacity; } return o; };
  let hidden = 0;
  for (const c of CHUNKS) { render((c.show + c.hide) / 2); const pl = document.getElementById('plate'), r = pl.getBoundingClientRect();
    if (opa(pl) < .5 || r.width < 10 || r.height < 10) hidden++; }
  const R = REELS[RID]; render(R.paperAt + 1); const bl = document.getElementById('buglb');
  const bug = !R.bug || (opa(bl) > .5 && bl.getBoundingClientRect().width > 10);
  const ats = (R.cards || []).map(c => c.at).concat([R.endAt]), low = [], late = [];
  const seen = t => { render(t); const m = new Map(); for (const e of document.querySelectorAll('#pscene [id], #pscene svg.ann')) m.set(e, opa(e)); return m; };
  for (let k = 1; k < ats.length; k++) {
    render(ats[k] - .12); let bot = 0, who = '';
    for (const c of document.querySelectorAll('#pscene .card')) { if (opa(c) < .5) continue;
      for (const e of [c, ...c.querySelectorAll('*')]) { if (opa(e) < .05) continue; const r = e.getBoundingClientRect(); if (r.height > 0 && r.bottom > bot) { bot = r.bottom; who = c.id; } } }
    low.push([who, Math.round(bot)]);
    const a = seen(ats[k] - 1.0), b = seen(ats[k] - .06);
    for (const [e, o] of b) if (o > .6 && (a.get(e) ?? 0) < .3 && !e.classList.contains('card')) late.push([e.id || 'an annotation', +ats[k].toFixed(2)]);
  }
  render(R.endAt + 1.2); const foot = Math.round(document.getElementById('efoot').getBoundingClientRect().bottom);
  return { hooks, caps, n: CHUNKS.length, hidden, bug, low, late, foot };
}'''


async def _page_checks(build, rids):
    from playwright.async_api import async_playwright
    problems = {}
    async with async_playwright() as pw:
        b = await pw.chromium.launch(**chromium_args())
        for rid in rids:
            pg = await b.new_page(viewport={'width': W, 'height': H})
            await pg.goto(f'file://{build / "reel.html"}#{rid}'); await pg.evaluate('loadFonts()')
            r = await pg.evaluate(PAGE_CHECK); await pg.close()
            p = [f'hook line "{h["text"]}" ends at {h["right"]} px' for h in r['hooks'] if h['right'] > HOOK_RIGHT]
            one = min(c['h'] for c in r['caps']) if r['caps'] else 0
            p += [f'caption "{c["text"]}" is up for only {c["up"]:.2f} s' for c in r['caps'] if c['up'] < .4]
            p += [f'caption "{c["text"]}" wraps to two lines' for c in r['caps'] if c['h'] > one + 20]
            if r['hidden']: p.append(f'captions are not visible in {r["hidden"]} of {r["n"]} chunks (does a scene style reuse .plate?)')
            if not r['bug']: p.append('the topic label is not visible (does a scene style reuse .lb?)')
            p += [f'card {who} reaches down to y {bot}, into the captions (keep cards above 1270)' for who, bot in r['low'] if bot > 1270]
            p += [f'"{e}" arrives less than a second before the cut at {t:.2f} s' for e, t in r['late']]
            if r['foot'] > 1282: p.append(f'the end-card note reaches down to y {r["foot"]}, into the captions')
            problems[rid] = p
        await b.close()
    return problems


def sheet(ev, video, dst):
    from PIL import Image, ImageDraw, ImageFont
    dur = ev['dur']; mids = {round((a + z) / 2, 3) for a, z in ev['mb']}
    times = {0.0, round(ev['paperAt'] + .2, 3), round(ev['endAt'] + .5, 3), round(dur - .1, 3)} | mids
    t = .5
    while t < dur - .05: times.add(round(t, 3)); t += 1.0
    times = sorted(x for x in times if x < dur)
    w, h, cols = 270, 480, 8
    rows = (len(times) + cols - 1) // cols
    im = Image.new('RGB', (cols * w, rows * (h + 26)), (18, 18, 18)); d = ImageDraw.Draw(im)
    try: font = ImageFont.truetype('DejaVuSans.ttf', 17)
    except OSError: font = ImageFont.load_default()
    for i, tt in enumerate(times):
        sel = ['-vf', 'select=eq(n\\,0)'] if tt == 0 else []
        cmd = ['ffmpeg', '-v', 'error'] + ([] if tt == 0 else ['-ss', f'{tt:.3f}']) + ['-i', str(video)] + sel + ['-frames:v', '1', '-f', 'image2pipe', '-c:v', 'png', '-']
        fr = Image.open(io.BytesIO(subprocess.run(cmd, capture_output=True).stdout)).convert('RGB').resize((w, h))
        x, y = (i % cols) * w, (i // cols) * (h + 26)
        im.paste(fr, (x, y + 26))
        d.text((x + 6, y + 4), f'{tt:.2f}s' + ('  cut' if tt in mids else '') + ('  cover' if tt == 0 else ''), fill=(240, 200, 90) if tt in mids else (220, 220, 220), font=font)
    im.save(dst, quality=88)


def run(project_dir, reels=None):
    proj, pdir, build, out = load_project(project_dir)
    rids = reel_ids(proj, reels)
    E = json.loads((build / 'events.json').read_text())
    (build / 'qa').mkdir(exist_ok=True)
    problems = asyncio.run(_page_checks(build, rids))
    bad = 0
    for rid in rids:
        video = out / (out_name(proj, rid) + '.mp4')
        if video.exists():
            sheet(E[rid], video, build / 'qa' / f'{rid}.jpg')
        p = problems[rid]; bad += len(p)
        print(f'  {rid}: ' + ('layout and captions ok' if not p else '; '.join(p)) + (f'  sheet: {build / "qa" / (rid + ".jpg")}' if video.exists() else ''))
    print('  Now look at every contact sheet. The checks above cannot see a half-empty card or a misleading "0".')
    return bad == 0


if __name__ == '__main__':
    a = sys.argv[1:]
    run(a[0], a[1:] or None)
