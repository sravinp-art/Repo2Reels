"""Check before you post: contact sheets of the finished reels, plus layout and caption checks on the page.

- Contact sheet per reel: the cover, a frame every second, the middle of every transition, the first
  moment of the day scene and of the end card. Look at every frame: text off the edge, overlaps,
  a half-empty card, a "0" before a count starts, anything left over from the previous scene.
- Hook lines must end by x = 970 px (safe from the right-hand buttons).
- Every caption chunk must stay on screen long enough to read (0.4 s or more) and fit on one line.

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
  return { hooks, caps };
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
