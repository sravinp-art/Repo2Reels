"""Read things out of the reel page with a headless browser: sound cues, covers, stills, layout checks.

    python3 -m r2r.page events  projects/keyva [r11 ...]   -> build/<p>/events.json (cues, motion-blur windows, cover time)
    python3 -m r2r.page posters projects/keyva [r11 ...]   -> build/<p>/posters/<rid>.png (frame 0 of the reel)
    python3 -m r2r.page stills  projects/keyva r11 3.2 4.5 -> build/<p>/stills/r11_03.20.png ...
"""
import asyncio
import json
import sys

from .common import H, W, chromium_args, load_project, reel_ids


async def _open(browser, html, rid, errors=None):
    pg = await browser.new_page(viewport={'width': W, 'height': H})
    if errors is not None:
        pg.on('pageerror', lambda e: errors.append(str(e)))
        pg.on('console', lambda m: errors.append(m.text) if 'mismatch' in m.text else None)
    await pg.goto(f'file://{html}#{rid}')
    await pg.evaluate('loadFonts()')
    return pg


async def _events(build, rids):
    from playwright.async_api import async_playwright
    path = build / 'events.json'
    res = json.loads(path.read_text()) if path.exists() else {}
    async with async_playwright() as pw:
        b = await pw.chromium.launch(**chromium_args())
        for rid in rids:
            errs = []
            pg = await _open(b, build / 'reel.html', rid, errs)
            res[rid] = {k: await pg.evaluate(v) for k, v in
                        {'dur': 'window.DUR', 'events': 'window.EVENTS', 'mb': 'window.MB', 'paperAt': 'PAPER_AT', 'endAt': 'END_AT', 'posterAt': 'window.POSTER_AT'}.items()}
            print(f"  {rid}: {res[rid]['dur']}s, {len(res[rid]['events'])} cues, {len(res[rid]['mb'])} blur windows, cover at {res[rid]['posterAt']:.2f}s" + (f'  PAGE ERRORS: {errs[:3]}' if errs else ''))
            if errs: raise SystemExit(f'page errors in {rid}: {errs[:3]}')
            await pg.close()
        await b.close()
    path.write_text(json.dumps(res, indent=1))


async def _posters(build, rids):
    from playwright.async_api import async_playwright
    ev = json.loads((build / 'events.json').read_text())
    (build / 'posters').mkdir(exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(**chromium_args())
        for rid in rids:
            pg = await _open(b, build / 'reel.html', rid)
            t = ev[rid]['posterAt']
            await pg.evaluate(f'render({t}); document.getElementById("cap").style.opacity = 0')   # no caption on the cover
            await pg.screenshot(path=str(build / 'posters' / f'{rid}.png'))
            print(f'  {rid}: cover from {t:.2f}s'); await pg.close()
        await b.close()


async def _stills(build, rid, times):
    from playwright.async_api import async_playwright
    (build / 'stills').mkdir(exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(**chromium_args())
        pg = await _open(b, build / 'reel.html', rid)
        for t in times:
            await pg.evaluate(f'render({t})')
            p = build / 'stills' / f'{rid}_{t:05.2f}.png'
            await pg.screenshot(path=str(p)); print(' ', p)
        await b.close()


def events(project_dir, reels=None):
    proj, pdir, build, out = load_project(project_dir)
    asyncio.run(_events(build, reel_ids(proj, reels)))


def posters(project_dir, reels=None):
    proj, pdir, build, out = load_project(project_dir)
    asyncio.run(_posters(build, reel_ids(proj, reels)))


def stills(project_dir, rid, times):
    proj, pdir, build, out = load_project(project_dir)
    asyncio.run(_stills(build, rid, times))


if __name__ == '__main__':
    cmd, pdir, *rest = sys.argv[1:]
    if cmd == 'events': events(pdir, rest or None)
    elif cmd == 'posters': posters(pdir, rest or None)
    elif cmd == 'stills': stills(pdir, rest[0], [float(x) for x in rest[1:]])
    else: raise SystemExit(__doc__)
