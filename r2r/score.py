"""Music, sound effects and the voice-over mixed into one track per reel (48 kHz stereo, on the beat grid).

Everything is synthesised here, so there are no music licences to worry about: a four-chord pad, a plucked
arpeggio, bass and light drums (a lighter pulse under the hook, a groove after it), a resolving chord on the
end card, and one sound effect for every cue the page queued with ev(t, kind). The voice is compressed,
the music ducks under it, and the result is soft-limited. Final loudness is set later, in encode.

    python3 -m r2r.score projects/keyva [r11 ...]
"""
import json
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, resample_poly, sosfilt

from .common import load_project, reel_ids, seed_of

# Four chords (MIDI notes) and their bass roots; the end card resolves to chord 3. A reel can name its own
# in project.json ("harmony"); otherwise one of these is picked from the reel id.
HARMONIES = [
    {"chords": [[54, 57, 61], [50, 54, 57], [57, 61, 64], [52, 56, 59]], "bass": [42, 38, 45, 40]},
    {"chords": [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]], "bass": [38, 34, 41, 36]},
    {"chords": [[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]], "bass": [40, 36, 43, 38]},
    {"chords": [[47, 50, 54], [43, 47, 50], [50, 54, 57], [45, 49, 52]], "bass": [35, 31, 38, 33]},
    {"chords": [[49, 52, 56], [45, 49, 52], [52, 56, 59], [47, 51, 54]], "bass": [37, 33, 40, 35]},
    {"chords": [[45, 48, 52], [41, 45, 48], [48, 52, 55], [43, 47, 50]], "bass": [33, 29, 36, 31]},
    {"chords": [[56, 59, 63], [52, 56, 59], [47, 51, 54], [54, 58, 61]], "bass": [44, 40, 35, 42]},
    {"chords": [[55, 58, 62], [51, 55, 58], [46, 50, 53], [53, 57, 60]], "bass": [43, 39, 34, 41]},
]


def make(rid, TM, EV, vo_dir, outp, harmony):
    SR = 48000; BEAT = .5; BAR = 2.0
    DUR = float(EV['dur']); N = int(SR * DUR)
    PAPER, END = EV['paperAt'], EV['endAt']
    seed = seed_of(rid)
    rng = np.random.default_rng(100 + seed)

    def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
    def tt(d): return np.arange(int(SR * d)) / SR
    def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x, axis=-1)
    def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x, axis=-1)
    def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x, axis=-1)
    def stereo(): return np.zeros((2, N))
    def place(buf, sig, at, gain=1.0, pan=0.0):
        i = int(round(at * SR))
        if i >= N: return
        if sig.ndim == 1:
            l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            sig = np.stack([sig * l * 1.414, sig * r * 1.414])
        if i < 0: sig = sig[:, -i:]; i = 0
        j = min(N, i + sig.shape[1]); buf[:, i:j] += sig[:, :j - i] * gain

    # ---------------------------------------------------------------- instruments
    def bell(m, d=1.2, g=1.0):
        t = tt(d); f = mtof(m)
        x = np.sin(2*np.pi*f*t) + .45*np.sin(2*np.pi*f*2*t)*np.exp(-t*5) + .2*np.sin(2*np.pi*f*3.01*t)*np.exp(-t*8)
        return x * np.exp(-t*3.0) * np.minimum(1, t/.003) * .11 * g
    def pluck(m, d=.45, g=1.0):
        t = tt(d); f = mtof(m)
        x = sum((1/k**1.4)*np.sin(2*np.pi*f*k*t) * np.exp(-t*(6+3*k)) for k in range(1, 6))
        return lp(x * np.minimum(1, t/.002), 5000) * .12 * g
    def pad(chord, d, cutoff=1600, g=1.0):
        t = tt(d); L = np.zeros(len(t)); R = np.zeros(len(t))
        for m in chord:
            f = mtof(m)
            for det, side in ((-.1, 0), (0., 2), (.1, 1)):
                ff = f*(1+det/100); ph = rng.random()*6.28
                s = .3*(2*((ff*t + ph/6.28) % 1) - 1) + .7*np.sin(2*np.pi*ff*t + ph)
                if side == 0: L += s
                elif side == 1: R += s
                else: L += .7*s; R += .7*s
        env = np.minimum(1, t/.5) * np.minimum(1, (d-t)/.4)
        return np.stack([lp(L, cutoff), lp(R, cutoff)]) * env * .02 * g
    def bass(m, d, g=1.0):
        t = tt(d); f = mtof(m)
        x = np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*2*f*t)
        env = np.minimum(1, t/.01) * np.minimum(1, (d-t)/.05) * np.exp(-t*2.2)
        return lp(x*env, 700) * .30 * g
    def kick(g=1.0):
        t = tt(.4); f = 48 + 80*np.exp(-t*30)
        return lp(np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*8) * np.minimum(1, t/.003), 800) * .6 * g
    def snap(g=1.0):
        t = tt(.2); n = bp(rng.standard_normal(len(t)), 1300, 4500) * (np.exp(-t*32) + .5*np.exp(-np.maximum(0, t-.011)*28)*(t > .011))
        return n * .075 * g
    def hat(g=1.0):
        t = tt(.07); return bp(rng.standard_normal(len(t)), 6000, 12000) * np.exp(-t*65) * .055 * g
    def tick(f=2600, g=1.0):
        t = tt(.03); return (np.sin(2*np.pi*f*t) + .4*np.sin(2*np.pi*f*2.1*t)) * np.exp(-t*220) * .045 * g
    def key(g=1.0):
        t = tt(.035); n = bp(rng.standard_normal(len(t)), 2500, 7000) * np.exp(-t*160)
        return (n * .05 + np.sin(2*np.pi*1800*t)*np.exp(-t*300)*.02) * g
    def boom(g=1.0, d=2.4):
        t = tt(d); f = 52*np.exp(-t*.25)
        x = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*1.6) * np.minimum(1, t/.01)
        return lp(x + lp(rng.standard_normal(len(t)), 140)*np.exp(-t*2.4)*.6, 400) * .45 * g
    def whoosh(d=.45, g=1.0):
        t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros(len(t)); blk = 512
        for s in range(0, len(t), blk):
            c = 300 + 3800*(s/len(t))**2; seg = n[max(0, s-2048):s+blk]
            y = bp(seg, max(60, c*.55), min(c*1.7, 20000))[-min(blk, len(t)-s):]; out[s:s+len(y)] = y
        return out * (t/d)**2 * np.minimum(1, (d-t)/.03) * .11 * g
    def sweep_up(d=.6, g=1.0, m0=60):
        t = tt(d); f = mtof(m0) * 2**(1.5*t/d)
        return np.sin(2*np.pi*np.cumsum(f)/SR) * np.sin(np.pi*t/d)**1.5 * .05 * g
    def whip(g=1.0):
        t = tt(.28); n = rng.standard_normal(len(t)); out = np.zeros(len(t)); blk = 256
        for s0 in range(0, len(t), blk):
            c = 6000 - 5200 * (s0 / len(t)) ** .6; seg = n[max(0, s0 - 1024):s0 + blk]
            y = bp(seg, max(80, c * .5), min(c * 1.6, 20000))[-min(blk, len(t) - s0):]; out[s0:s0 + len(y)] = y
        return out * np.sin(np.pi * np.minimum(1, t / .28)) ** 1.5 * .09 * g
    def flip(g=1.0):
        t = tt(.32); n = bp(rng.standard_normal(len(t)), 1500, 6500)
        env = np.exp(-((t - .06) / .03) ** 2) + .7 * np.exp(-((t - .17) / .04) ** 2)
        return n * env * .07 * g
    def thud(g=1.0):
        t = tt(.35); f = 90 * np.exp(-t * 10) + 45
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) + .5 * lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 40)
        return lp(x, 1400) * .42 * g
    def scribble(d=.42, g=1.0):
        t = tt(d); n = bp(rng.standard_normal(len(t)), 2200, 7500)
        am = .55 + .45 * np.sin(2 * np.pi * 14 * t + 1.3) * np.sin(2 * np.pi * 3 * t)
        return n * am * np.sin(np.pi * t / d) ** .8 * .028 * g
    def revcym(d=.5, g=1.0):
        t = tt(d); return hp(rng.standard_normal(len(t)), 4500) * (t/d)**3 * np.minimum(1, (d-t)/.01) * .06 * g

    # ---------------------------------------------------------------- harmony per reel
    PROG = (harmony["chords"], harmony["bass"])
    CH, BS = PROG
    music = stereo(); fx = stereo()
    nbars = int(np.ceil(DUR / BAR))
    for b in range(nbars):
        t0 = b * BAR
        if t0 >= END: break
        i = b % 4
        place(music, pad([m + 12 for m in CH[i]], BAR + .4, 1300 if t0 < PAPER else 2000), t0)
        for k in range(4):                       # bass on beats, octave hop on 4
            tb = t0 + k * BEAT
            if tb < END: place(music, bass(BS[i] + (12 if k == 3 else 0), BEAT * .9, .8 if tb < PAPER else 1.0), tb)
        for k in range(8 if t0 >= PAPER else 4):   # pluck arpeggio: 8ths in the day, quarters in the hook
            step = BEAT / 2 if t0 >= PAPER else BEAT
            tp = t0 + k * step
            if tp >= END: break
            arp = [CH[i][0] + 24, CH[i][1] + 24, CH[i][2] + 24, CH[i][1] + 36]
            place(music, pluck(arp[k % 4], .5, .8 if t0 >= PAPER else .6), tp, pan=(-.35 if k % 2 else .35))
    # drums: light pulse in the hook, groove in the day
    nbeats = int(DUR / BEAT)
    for k in range(nbeats):
        tb = k * BEAT
        if tb >= END: break
        if tb < PAPER:
            if k % 2 == 0: place(music, kick(.55), tb)
            place(music, tick(2600 if k % 2 == 0 else 2150, .8), tb, pan=.2 if k % 2 else -.2)
        else:
            if k % 2 == 0: place(music, kick(.9), tb)
            else: place(music, snap(1.0), tb, pan=.08)
            place(music, hat(1.0), tb + BEAT / 2, pan=.3); place(music, hat(.55), tb, pan=-.3)
    # build into the end card: 16th hats over the last bar
    for k in range(8):
        tb = END - 1.0 + k * BEAT / 4
        if tb > PAPER: place(music, hat(.5 + .06 * k), tb, pan=(-.4 if k % 2 else .4))
    # end card: resolve to chord 3 (relative major) with a held chord
    fin = CH[2]
    place(music, pad([m + 12 for m in fin] + [fin[0] + 24], DUR - END + .2, 2400, 1.2), END)
    place(music, bass(BS[2], DUR - END, 1.1), END)
    for k, m in enumerate([fin[0] + 24, fin[1] + 24, fin[2] + 24, fin[0] + 36]):
        place(music, bell(m, 2.0, .8 - .1 * k), END + k * BEAT / 4, pan=(-.4 + .27 * k))

    # ---------------------------------------------------------------- SFX from the page's cues
    q16 = lambda x: round(x / (BEAT / 4)) * (BEAT / 4)
    top = CH[0][0] + 36
    for t, kind in EV['events']:
        if kind == 'open': place(fx, boom(.7, 2.0), 0.0)
        elif kind == 'iris': place(fx, whoosh(.45, 1.0), PAPER - .45, pan=-.15); place(fx, boom(.45, 1.4), PAPER)
        elif kind == 'end': place(fx, revcym(.5, 1.0), END - .5); place(fx, boom(.9, 2.4), END)
        elif kind == 'key': place(fx, key(1.0), t, pan=.15)
        elif kind == 'click': place(fx, tick(1600, 2.2), t); place(fx, kick(.25), t)
        elif kind == 'pop': place(fx, bell(top + 7, .8, .5), q16(t), pan=.2); place(fx, tick(2400, 1.0), q16(t))
        elif kind == 'chime': place(fx, bell(top + 4, 1.4, .6), q16(t), pan=-.15); place(fx, bell(top + 11, 1.4, .35), q16(t) + BEAT / 4, pan=.15)
        elif kind == 'soft': place(fx, bell(top + 7, 1.2, .35), q16(t))
        elif kind == 'hit': place(fx, boom(.5, 1.6), q16(t)); place(fx, bell(top, 1.4, .5), q16(t))
        elif kind == 'print': place(fx, tick(2100, 1.3), t, pan=.25); place(fx, key(.8), t + .03)
        elif kind == 'tick': place(fx, tick(2400, 1.0), t, pan=-.1)
        elif kind == 'rise': place(fx, sweep_up(.8, 1.0, CH[0][0] + 12), t)
        elif kind == 'strike': place(fx, bell(top - 5, .6, .4), q16(t)); place(fx, whoosh(.25, .5), t - .25)
        elif kind == 'whip': place(fx, whip(1.0), t - .06, pan=-.2)
        elif kind == 'flip': place(fx, flip(1.0), t, pan=.15); place(fx, bell(top + 7, .7, .25), q16(t + .25))
        elif kind == 'stamp': place(fx, thud(1.0), t); place(fx, bell(top - 12, 1.0, .35), q16(t))
        elif kind == 'scribble': place(fx, scribble(.42, 1.0), t, pan=.1)

    # ---------------------------------------------------------------- voiceover
    vo = stereo(); spans = []
    for line in TM['lines']:
        sr, x = wavfile.read(f"{vo_dir}/{line['id']}.wav"); x = x.astype(float) / 32768
        x = resample_poly(x, 2, 1); x = hp(x, 90, 2)
        x = x + .22 * bp(x, 2400, 5200, 2) - .12 * bp(x, 180, 350, 1)
        place(vo, x, line['clipStart']); spans.append((line['on'], line['off']))
    env = np.sqrt(np.maximum(lp(np.mean(vo ** 2, axis=0), 12), 0) + 1e-12)
    thr, ratio = .06, 3.0
    vo = vo * np.where(env > thr, (thr * (env / thr) ** (1 / ratio)) / env, 1.0) * 1.8

    # ---------------------------------------------------------------- duck, reverb, master
    t = np.arange(N) / SR
    target = np.ones(N)
    for s, e in spans: target[(t >= s - .15) & (t <= e + .2)] = .25
    duck = np.empty(N); g = 1.0
    a_dn = 1 - np.exp(-1 / (SR * .09)); a_up = 1 - np.exp(-1 / (SR * .45))
    for i in range(N):
        tg = target[i]; g += (tg - g) * (a_dn if tg < g else a_up); duck[i] = g
    def reverb(x, secs, wet, damp, sd):
        r = np.random.default_rng(sd); out = np.zeros_like(x)
        for c in range(2):
            tr = np.arange(int(SR * secs)) / SR; ir = lp(r.standard_normal(len(tr)) * np.exp(-tr * 3.4), damp); ir /= np.sqrt(np.sum(ir ** 2))
            out[c] = fftconvolve(x[c], ir)[:x.shape[1]]
        return x + wet * out
    music = reverb(music, 1.8, .22, 4000, 1); fx = reverb(fx, 2.0, .3, 5000, 2); vo = reverb(vo, .8, .04, 5000, 3)
    mix = vo + music * duck * .62 + fx * .7
    mix = hp(mix, 28, 2)
    mix *= np.minimum(1, t / .02) * np.minimum(1, (DUR - t) / .9)
    pk = np.max(np.abs(mix)); mix = np.tanh(mix / pk * 1.15) / np.tanh(1.15) * .95
    wavfile.write(outp, SR, (mix.T * 32767).astype(np.int16))
    inv = np.zeros(N, bool)
    for s, e in spans: inv |= (t >= s) & (t <= e)
    db = lambda x, m: 10 * np.log10(np.mean(x[:, m] ** 2) + 1e-20)
    print(' ', rid, f'VO {db(vo, inv):.1f} | music under VO {db(music * duck * .62, inv):.1f} | music in gaps {db(music * duck * .62, ~inv & (t < END)):.1f}')


def run(project_dir, reels=None):
    proj, pdir, build, out = load_project(project_dir)
    timing = json.loads((build / 'timing.json').read_text())
    events = json.loads((build / 'events.json').read_text())
    (build / 'audio').mkdir(exist_ok=True)
    for rid in reel_ids(proj, reels):
        harmony = proj['reels'][rid].get('harmony') or HARMONIES[seed_of(rid) % len(HARMONIES)]
        make(rid, timing[rid], events[rid], build / 'vo', build / 'audio' / f'{rid}.wav', harmony)


if __name__ == '__main__':
    a = sys.argv[1:]
    run(a[0], a[1:] or None)
