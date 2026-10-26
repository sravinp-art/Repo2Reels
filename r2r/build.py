"""Assemble a project's reel page: engine + world + the project's scenes, brand and caption fixes.

The page holds every reel of the project; #r11 in the URL picks one. It is deterministic: render(t) poses
the whole frame for time t, so the renderer can ask for any frame in any order.

    python3 -m r2r.build projects/keyva
"""
import json
import os
import shutil
import sys

from .common import ENGINE, load_project


def run(project_dir, reels=None):
    proj, pdir, build, out = load_project(project_dir)
    build.mkdir(parents=True, exist_ok=True)
    page = (ENGINE / 'engine.html').read_text()
    world = (ENGINE / f"world-{proj.get('world', 'dusk')}.js").read_text()
    brand = dict(proj.get('brand', {}))
    if brand.get('logo'):
        brand['logoSvg'] = (pdir / brand.pop('logo')).read_text().strip()
    capfix = {l['id']: l['captions'] for r in proj['reels'].values() for l in r['lines'] if l.get('captions')}
    inject = ('window.BRAND=' + json.dumps(brand, ensure_ascii=False) + ';\nwindow.CAPFIX=' + json.dumps(capfix, ensure_ascii=False) + ';\n')
    page = (page.replace('/*WORLD*/', world)
                .replace('/*SCENE_CSS*/', (pdir / 'scenes.css').read_text())
                .replace('/*SCENES*/', (pdir / 'scenes.js').read_text())
                .replace('<script src="timing.js"></script>', '<script src="timing.js"></script>\n<script>\n' + inject + '</script>'))
    tmp = build / 'reel.tmp.html'
    tmp.write_text(page); os.replace(tmp, build / 'reel.html')     # atomic: a render in progress never reads half a page
    # fonts and the grain texture sit next to the page (it loads them by relative path)
    shutil.copytree(ENGINE / 'fonts', build / 'fonts', dirs_exist_ok=True)
    shutil.copy2(ENGINE / 'grain.png', build / 'grain.png')
    print(f'  page: {build / "reel.html"} ({len(page) // 1024} KB)')


if __name__ == '__main__':
    run(sys.argv[1])
