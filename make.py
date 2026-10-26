#!/usr/bin/env python3
"""Repo2Reels: make the reels of a project, start to finish.

    python3 make.py projects/starter                   every reel, every step
    python3 make.py new acme                           start projects/acme from the starter
    python3 make.py projects/keyva r11 r18             just these reels
    python3 make.py projects/keyva --steps page,events,posters,render,encode
    python3 make.py projects/keyva --workers 2         render two reels at a time
    python3 make.py projects/keyva --listen            also hear every voice line back (needs the Whisper model)

Steps, in order:
  voice    words -> phonemes -> speech, one WAV per line            (build/<p>/vo/)
  listen   transcribe each line and flag drift from the script      (optional, --listen)
  timing   lines on a 120 bpm grid, every word timed                (build/<p>/timing.json)
  page     engine + world + your scenes -> one HTML page            (build/<p>/reel.html)
  events   sound cues, motion-blur windows, cover time from the page (build/<p>/events.json)
  score    music + sound effects + voice, mixed                     (build/<p>/audio/)
  posters  the cover frame of each reel                             (build/<p>/posters/)
  render   every frame, motion-blurred where it moves fast          (build/<p>/pic/)
  encode   cover + picture + sound, loudness for phones             (out/<p>/*.mp4, *.jpg)
  qa       contact sheets and layout/caption checks                 (build/<p>/qa/)
"""
import os
import sys
import time

from r2r import build, encode, page, qa, render, score, timing, voice
from r2r.common import ROOT

STEPS = ['voice', 'listen', 'timing', 'page', 'events', 'score', 'posters', 'render', 'encode', 'qa']


def new_project(name):
    """projects/<name>: a copy of the starter with the brand renamed, ready to edit."""
    import json
    import re
    import shutil
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    if not slug:
        raise SystemExit('Give the new project a name, like: python3 make.py new acme')
    dst = ROOT / 'projects' / slug
    if dst.exists():
        raise SystemExit(f'projects/{slug} already exists.')
    shutil.copytree(ROOT / 'projects' / 'starter', dst)
    pj = dst / 'project.json'
    proj = json.loads(pj.read_text())
    proj['name'] = name
    proj['about'] = f'Reels for {name}.'
    proj['brand'].update(name=name, url=f'{slug}.com')
    pj.write_text(json.dumps(proj, ensure_ascii=False, indent=2) + '\n')
    print(f"""Made projects/{slug}, a copy of the starter. Next:
  1. projects/{slug}/project.json   your brand (name, url), and the lines of each reel
  2. projects/{slug}/scenes.js      what is on screen while each line is said (docs/writing-scenes.md)
  3. projects/{slug}/logo.svg       your logo
  4. python3 make.py projects/{slug}""")


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__); return 0
    if argv[0] == 'new':
        new_project(' '.join(argv[1:])); return 0
    project = argv[0]; reels = []; steps = None; workers = 1; listen = False; force = False
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == '--steps': steps = argv[i + 1].split(','); i += 2; continue
        if a == '--workers': workers = int(argv[i + 1]); i += 2; continue
        if a == '--listen': listen = True
        elif a == '--force': force = True
        else: reels.append(a)
        i += 1
    steps = steps or [s for s in STEPS if s != 'listen' or listen]
    unknown = [s for s in steps if s not in STEPS]
    if unknown: raise SystemExit(f'unknown step(s): {unknown}; steps are {STEPS}')
    import json
    from pathlib import Path
    if not (Path(project) / 'project.json').is_file():
        have = ', '.join(sorted('projects/' + p.parent.name for p in (ROOT / 'projects').glob('*/project.json')))
        raise SystemExit(f'No project.json in {project}. The projects here: {have}')
    ids = list(json.loads((Path(project) / 'project.json').read_text())['reels'])
    missing = [r for r in reels if r not in ids]
    if missing: raise SystemExit(f'No reel {", ".join(missing)} in {project}. Its reels: {", ".join(ids)}')
    reels = reels or None
    ok = True
    for s in STEPS:
        if s not in steps: continue
        t0 = time.time(); print(f'== {s}', flush=True)
        if s == 'voice': voice.run(project, reels, force=force)
        elif s == 'listen':
            from r2r import listen as lis
            lis.run(project, reels)
        elif s == 'timing': timing.run(project, reels)
        elif s == 'page': build.run(project)
        elif s == 'events': page.events(project, reels)
        elif s == 'score': score.run(project, reels)
        elif s == 'posters': page.posters(project, reels)
        elif s == 'render': render.run(project, reels, workers)
        elif s == 'encode': encode.run(project, reels)
        elif s == 'qa': ok = qa.run(project, reels)
        print(f'   ({time.time() - t0:.0f}s)', flush=True)
    if ok and 'encode' in steps:
        from r2r.common import load_project, out_name
        proj, _, _, outdir = load_project(project)
        made = [outdir / (out_name(proj, r) + '.mp4') for r in (reels or ids)]
        print('\nDone:\n' + '\n'.join(f'  {os.path.relpath(m)}' for m in made if m.exists()))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
