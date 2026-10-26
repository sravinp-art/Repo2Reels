"""Render a reel's picture: every frame from the page, straight into ffmpeg, with motion blur where things move fast.

Frames inside the page's motion-blur windows (card pushes, the iris) are rendered at 4 moments across a
180-degree shutter and averaged, the way a camera smears fast motion. Other frames are rendered once.
Output is a high-quality intermediate (x264 crf 14); encode adds the cover, the sound and the final squeeze.

    python3 -m r2r.render projects/keyva [r11 ...] [--workers 2]
"""
import asyncio
import io
import json
import subprocess
import sys

from .common import FPS, H, ROOT, W, chromium_args, load_project, reel_ids

SAMPLES, SHUTTER = 4, .5


async def _render(build, rids):
    import numpy as np
    from PIL import Image
    from playwright.async_api import async_playwright
    E = json.loads((build / 'events.json').read_text())
    (build / 'pic').mkdir(exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(**chromium_args())
        for rid in rids:
            n = int(round(E[rid]['dur'] * FPS)); mb = E[rid]['mb']
            pg = await b.new_page(viewport={'width': W, 'height': H})
            await pg.goto(f'file://{build / "reel.html"}#{rid}'); await pg.evaluate('loadFonts()')
            out = build / 'pic' / f'{rid}.mp4'
            ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                                   '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', str(out)], stdin=subprocess.PIPE)
            blurred = 0
            for i in range(n):
                t = i / FPS
                if any(a - 1 / FPS <= t <= z + 1 / FPS for a, z in mb):
                    acc = None
                    for k in range(SAMPLES):
                        tk = t + ((k + .5) / SAMPLES - .5) * SHUTTER / FPS
                        await pg.evaluate(f'render({tk:.5f})')
                        arr = np.asarray(Image.open(io.BytesIO(await pg.screenshot(type='jpeg', quality=94))), dtype=np.float32)
                        acc = arr if acc is None else acc + arr
                    bio = io.BytesIO(); Image.fromarray(np.clip(acc / SAMPLES + .5, 0, 255).astype(np.uint8)).save(bio, 'JPEG', quality=94)
                    data = bio.getvalue(); blurred += 1
                else:
                    await pg.evaluate(f'render({t:.5f})')
                    data = await pg.screenshot(type='jpeg', quality=94)
                ff.stdin.write(data)
            ff.stdin.close(); ff.wait()
            if ff.returncode: raise SystemExit(f'ffmpeg failed on {rid}')
            print(f'  {rid}: {n} frames, {blurred} motion-blurred', flush=True)
            await pg.close()
        await b.close()


def run(project_dir, reels=None, workers=1):
    proj, pdir, build, out = load_project(project_dir)
    rids = reel_ids(proj, reels)
    if workers <= 1 or len(rids) == 1:
        asyncio.run(_render(build, rids)); return
    # balance the reels over the workers by length, longest first
    E = json.loads((build / 'events.json').read_text())
    groups = [[] for _ in range(workers)]; load = [0.0] * workers
    for rid in sorted(rids, key=lambda r: -E[r]['dur']):
        k = load.index(min(load)); groups[k].append(rid); load[k] += E[rid]['dur']
    procs = [subprocess.Popen([sys.executable, '-m', 'r2r.render', str(pdir), *g], cwd=str(ROOT)) for g in groups if g]
    codes = [p.wait() for p in procs]
    if any(codes): raise SystemExit('a render worker failed')


if __name__ == '__main__':
    a = sys.argv[1:]
    workers = int(a[a.index('--workers') + 1]) if '--workers' in a else 1
    rest = [x for i, x in enumerate(a[1:], 1) if not x.startswith('--') and (i == 0 or a[i - 1] != '--workers')]
    run(a[0], rest or None, workers)
