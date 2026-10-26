#!/usr/bin/env python3
"""Repo2Reels: make the reels of a project, start to finish.

    python3 make.py projects/keyva                     every reel, every step
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
import sys
import time

from r2r import build, encode, page, qa, render, score, timing, voice

STEPS = ['voice', 'listen', 'timing', 'page', 'events', 'score', 'posters', 'render', 'encode', 'qa']


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__); return 0
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
    reels = reels or None
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
        elif s == 'qa': qa.run(project, reels)
        print(f'   ({time.time() - t0:.0f}s)', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
