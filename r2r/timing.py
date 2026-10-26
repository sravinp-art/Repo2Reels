"""Place each reel's voice-over lines on a beat grid and time every word (for captions and cues).

Line 1 starts at 0.25 s. Each later line starts on the next beat after the previous one ends plus a short
gap, plus any "pauseBefore" the line asks for (room for a visual to land). Words are timed by splitting
each spoken stretch (found from the audio's energy) in proportion to the word's phoneme count.

    python3 -m r2r.timing projects/keyva [--reels r11 r12]
"""
import json
import math
import sys

import numpy as np

from .common import load_project, reel_ids

PUNCT = set('.,!?;:…—')
STRIP = str.maketrans('', '', 'ˈˌ ')


def analyse(path):
    from scipy.io import wavfile
    sr, x = wavfile.read(path); x = x.astype(float) / 32768
    fr = int(sr * .01); n = len(x) // fr
    e = np.array([np.sqrt(np.mean(x[k * fr:(k + 1) * fr] ** 2)) for k in range(n)])
    on = np.where(e > e.max() * .04)[0]
    segs = []; s0 = on[0]; prev = on[0]
    for k in on[1:]:
        if k - prev > 11:
            segs.append([s0 * .01, (prev + 1) * .01]); s0 = k
        prev = k
    segs.append([s0 * .01, (prev + 1) * .01])
    return len(x) / sr, segs


def word_times(words, segs):
    chunks = [[]]
    for w, p in words:
        if w in PUNCT:
            if chunks[-1]: chunks.append([])
        else:
            chunks[-1].append((w, p))
    chunks = [c for c in chunks if c]
    segs = [list(s) for s in segs]
    while len(segs) > len(chunks):          # merge the closest segments
        gaps = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]
        i = int(np.argmin(gaps)); segs[i][1] = segs[i + 1][1]; del segs[i + 1]
    while len(chunks) > len(segs):          # merge chunks (fewest phonemes first)
        w = [sum(len(p.translate(STRIP)) for _, p in c) for c in chunks]
        i = int(np.argmin([w[k] + w[k + 1] for k in range(len(chunks) - 1)]))
        chunks[i] = chunks[i] + chunks[i + 1]; del chunks[i + 1]
    out = []
    for c, (a, b) in zip(chunks, segs):
        wts = [len(p.translate(STRIP)) + 1.2 for _, p in c]
        tot = sum(wts); t = a
        for (w, _), wt in zip(c, wts):
            d = (b - a) * wt / tot
            out.append([w, round(t, 3), round(t + d, 3)]); t += d
    return out


def run(project_dir, reels=None):
    proj, pdir, build, out = load_project(project_dir)
    cfg = proj.get('timing', {})
    beat = 60.0 / cfg.get('bpm', 120); first_on = cfg.get('firstOn', .25)
    min_gap = cfg.get('minGap', .22); end_hold = cfg.get('endHold', 1.7)
    L = {l['id']: l for l in json.loads((build / 'lines.json').read_text())}
    tpath = build / 'timing.json'
    timing = json.loads(tpath.read_text()) if tpath.exists() else {}
    for rid in reel_ids(proj, reels):
        t = None; placed = []
        for line in proj['reels'][rid]['lines']:
            lid = line['id']
            total, segs = analyse(build / 'vo' / f'{lid}.wav')
            sp0, sp1 = segs[0][0], segs[-1][1]
            on = first_on if t is None else math.ceil((t + min_gap + line.get('pauseBefore', 0)) / beat) * beat + .05
            start = on - sp0
            wt = word_times(L[lid]['words'], segs)
            placed.append({'id': lid, 'text': line['text'], 'clipStart': round(start, 3), 'on': round(on, 3), 'off': round(start + sp1, 3),
                           'words': [[w, round(start + a, 3), round(start + b, 3)] for w, a, b in wt]})
            t = start + sp1
        dur = math.ceil((t + end_hold) / beat) * beat
        timing[rid] = {'bpm': round(60 / beat), 'dur': dur, 'lines': placed}
        print(f'  {rid}: {dur:.1f}s  ' + ' '.join(f"{p['id']}@{p['on']:.2f}" for p in placed))
    tpath.write_text(json.dumps(timing, ensure_ascii=False, indent=1))
    (build / 'timing.js').write_text('window.TIMING=' + json.dumps(timing, ensure_ascii=False) + ';\n')


if __name__ == '__main__':
    a = sys.argv[1:]
    run(a[0], [x for x in a[1:] if not x.startswith('--')] or None)
