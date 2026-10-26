"""Shared paths and helpers for the Repo2Reels pipeline."""
import json
import os
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINE = ROOT / 'engine'
MODELS = Path(os.environ.get('R2R_MODELS', ROOT / 'models'))
FPS = 30
W, H = 1080, 1920


def load_project(project_dir):
    """project.json plus resolved paths. A project is a folder: project.json, scenes.js, scenes.css, logo.svg."""
    pdir = Path(project_dir).resolve()
    proj = json.loads((pdir / 'project.json').read_text())
    name = proj.get('id') or pdir.name
    build = Path(os.environ.get('R2R_BUILD', ROOT / 'build')) / name
    out = Path(os.environ.get('R2R_OUT', ROOT / 'out')) / name
    return proj, pdir, build, out


def all_lines(proj, reels=None):
    """Every voice-over line of the project, in reel order, as dicts with id/text/say/pauseBefore/captions."""
    out = []
    for rid, reel in proj['reels'].items():
        if reels and rid not in reels:
            continue
        out.extend(reel['lines'])
    return out


def reel_ids(proj, reels=None):
    return [r for r in proj['reels'] if not reels or r in reels]


def seed_of(rid):
    """A stable number per reel id: the digits in it ("r11" -> 11), else a checksum."""
    d = re.sub(r'\D', '', rid)
    return int(d) if d else zlib.crc32(rid.encode()) % 100000


def out_name(proj, rid):
    brand = re.sub(r'[^a-z0-9]+', '-', proj.get('brand', {}).get('name', 'reel').lower()).strip('-')
    num = re.sub(r'\D', '', rid) or rid
    slug = proj['reels'][rid].get('slug', rid)
    return f'{brand}-reel-{num}-{slug}'


def chromium_args():
    """Launch options for Playwright's Chromium. R2R_CHROME points at a specific browser binary if needed."""
    opts = {'args': ['--allow-file-access-from-files']}
    if os.environ.get('R2R_CHROME'):
        opts['executable_path'] = os.environ['R2R_CHROME']
    return opts
