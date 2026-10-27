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


RATE_W = 4.0          # how much a group's speaking rate may stray from the line's own
CUT_NO_PUNCT = .15    # a pause between two words with no punctuation between them
RUN_ON = {'.': .2, '?': .2, '!': .2}   # punctuation the voice ran straight through (others: RUN_ON_SOFT)
RUN_ON_SOFT = .05
GAP_KEPT = (.1, 1.5)  # a pause left inside one group: fixed + per second (a quiet consonant, or a breath mid-phrase)


def word_times(words, segs):
    """Time every word of a line from the stretches of speech found in its audio.

    The voice does not pause at every comma, and now and then it pauses where there is no punctuation, or a
    quiet consonant splits one word in two, so the stretches of speech and the punctuation rarely line up one
    to one. Every way of pairing consecutive groups of words with consecutive stretches is scored, and the
    cheapest wins: each pair should be spoken near the line's own pace (phonemes a second), a cut between
    words with no punctuation costs a little, punctuation the voice ran through costs a little, and a pause
    left inside a group costs more the longer it is. Inside a pair, words share the speech in proportion to
    their phonemes, skipping the pauses."""
    toks = []                                   # [word, weight, punctuation after it]
    for w, p in words:
        if w in PUNCT:
            if toks and not toks[-1][2]: toks[-1][2] = w
        else:
            toks.append([w, len(p.translate(STRIP)) + 1.2, ''])
    n, S = len(toks), len(segs)
    if not n: return []
    cw = np.concatenate([[0], np.cumsum([t[1] for t in toks])])
    sd = np.concatenate([[0], np.cumsum([b - a for a, b in segs])])
    gap = [segs[k + 1][0] - segs[k][1] for k in range(S - 1)]
    gc = np.concatenate([[0], np.cumsum([GAP_KEPT[0] + GAP_KEPT[1] * g for g in gap])])
    run = np.concatenate([[0], np.cumsum([(RUN_ON.get(t[2], RUN_ON_SOFT) if t[2] else 0) for t in toks])])
    Wt, Dt = cw[-1], sd[-1]; r0 = Wt / Dt
    INF = float('inf'); f = np.full((n + 1, S + 1), INF); back = {}
    f[0][0] = 0
    for i in range(1, n + 1):
        for j in range(1, S + 1):
            for i0 in range(i):
                cut = 0 if i0 == 0 or toks[i0 - 1][2] else CUT_NO_PUNCT
                wg = cw[i] - cw[i0]; inside = run[i - 1] - run[i0]
                for j0 in range(j):
                    if f[i0][j0] == INF: continue
                    dg = sd[j] - sd[j0]
                    c = (f[i0][j0] + cut + inside + (gc[j - 1] - gc[j0])
                         + RATE_W * (wg / Wt + dg / Dt) / 2 * math.log(wg / dg / r0) ** 2)
                    if c < f[i][j]: f[i][j] = c; back[i, j] = (i0, j0)
    pairs = []; i, j = n, S
    while i:
        i0, j0 = back[i, j]; pairs.append((i0, i, j0, j)); i, j = i0, j0
    out = []
    for i0, i1, j0, j1 in reversed(pairs):
        sg = segs[j0:j1]; dur = sum(b - a for a, b in sg); wg = cw[i1] - cw[i0]

        def at(x, start):                       # speech time -> clock time (a start never sits on a pause)
            for a, b in sg:
                if x < b - a - 1e-9 or (not start and x <= b - a + 1e-9): return a + x
                x -= b - a
            return sg[-1][1]
        for k in range(i0, i1):
            x0 = (cw[k] - cw[i0]) / wg * dur; x1 = (cw[k + 1] - cw[i0]) / wg * dur
            out.append([toks[k][0], round(float(at(x0, True)), 3), round(float(at(x1, False)), 3)])
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
