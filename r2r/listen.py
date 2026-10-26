"""Listen back: transcribe audio with Whisper (base.en, ONNX export from sherpa-onnx) and compare with the script.

Every voice line is heard back before it is used, and so is each final mix, because a TTS voice that sounds
right to its author can still say "to buy" for "Dubai". A line whose transcript drifts from its text is
flagged; reword it or add a pronunciation to "lexicon" in project.json.

Adapted from scripts/whisper/test.py in k2-fsa/sherpa-onnx (Apache-2.0): greedy decoding, with the
log-mel features computed in numpy the way OpenAI Whisper does.

    python3 -m r2r.listen projects/keyva [r11 ...]        # each voice line against its text
    python3 -m r2r.listen --file out/keyva/some.mp4        # any audio or video file
"""
import base64
import difflib
import json
import re
import subprocess
import sys
import tempfile

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

from .common import MODELS, all_lines, load_project

def mel_filters(sr=16000, n_fft=400, n_mels=80):
    def hz_to_mel(f):
        f = np.asarray(f, dtype=float)
        m = 3.0 * f / 200.0
        logstep = np.log(6.4) / 27.0
        return np.where(f >= 1000, 15.0 + np.log(np.maximum(f, 1e-9) / 1000.0) / logstep, m)
    def mel_to_hz(m):
        m = np.asarray(m, dtype=float)
        f = 200.0 * m / 3.0
        logstep = np.log(6.4) / 27.0
        return np.where(m >= 15.0, 1000.0 * np.exp(logstep * (m - 15.0)), f)
    fftfreqs = np.linspace(0, sr / 2, n_fft // 2 + 1)
    mels = np.linspace(hz_to_mel(0), hz_to_mel(sr / 2), n_mels + 2)
    hz = mel_to_hz(mels)
    fdiff = np.diff(hz)
    ramps = hz[:, None] - fftfreqs[None, :]
    w = np.zeros((n_mels, len(fftfreqs)))
    for i in range(n_mels):
        lower = -ramps[i] / fdiff[i]
        upper = ramps[i + 2] / fdiff[i + 1]
        w[i] = np.maximum(0, np.minimum(lower, upper))
    enorm = 2.0 / (hz[2:n_mels + 2] - hz[:n_mels])
    return w * enorm[:, None]

def features(path, n_mels):
    sr, x = wavfile.read(path)
    x = x.astype(np.float32) / 32768.0
    if x.ndim > 1: x = x[:, 0]
    if sr != 16000:
        from math import gcd
        g = gcd(sr, 16000); x = resample_poly(x, 16000 // g, sr // g).astype(np.float32)
    n_fft, hop = 400, 160
    win = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(n_fft) / n_fft)  # periodic hann
    xp = np.pad(x, (n_fft // 2, n_fft // 2), mode='reflect')
    n_frames = 1 + (len(xp) - n_fft) // hop
    frames = np.stack([xp[i * hop:i * hop + n_fft] * win for i in range(n_frames)])
    mag = np.abs(np.fft.rfft(frames, axis=1)) ** 2
    mag = mag[:-1]  # whisper drops the last frame
    mel = mag @ mel_filters(n_mels=n_mels).T  # (T, n_mels)
    log_spec = np.log10(np.maximum(mel, 1e-10))
    log_spec = np.maximum(log_spec, log_spec.max() - 8.0)
    m = (log_spec + 4.0) / 4.0
    m = np.pad(m, ((0, 1500), (0, 0)))
    if m.shape[0] > 3000:
        m = np.pad(m[:2950], ((0, 50), (0, 0)))
    return m.T[None].astype(np.float32)


class Whisper:
    def __init__(self, d=None):
        import onnxruntime as ort
        d = d or (MODELS / 'whisper')
        so = ort.SessionOptions(); so.inter_op_num_threads = 1; so.intra_op_num_threads = 4
        self.enc = ort.InferenceSession(str(d / 'base.en-encoder.int8.onnx'), so, providers=['CPUExecutionProvider'])
        self.dec = ort.InferenceSession(str(d / 'base.en-decoder.int8.onnx'), so, providers=['CPUExecutionProvider'])
        meta = self.enc.get_modelmeta().custom_metadata_map
        self.n_layer, self.n_ctx, self.n_state, self.n_mels = (int(meta[k]) for k in ('n_text_layer', 'n_text_ctx', 'n_text_state', 'n_mels'))
        self.sot, self.eot, self.no_ts, self.no_speech, self.translate, self.blank = (int(meta[k]) for k in ('sot', 'eot', 'no_timestamps', 'no_speech', 'translate', 'blank_id'))
        self.sot_seq = list(map(int, meta['sot_sequence'].split(','))) + [self.no_ts]
        self.table = {}
        for line in open(d / 'base.en-tokens.txt'):
            t, i = line.split(); self.table[int(i)] = t
        self.din = [i.name for i in self.dec.get_inputs()]; self.dout = [o.name for o in self.dec.get_outputs()][:3]

    def _suppress(self, logits, initial):
        if initial:
            logits[self.eot] = -np.inf; logits[self.blank] = -np.inf
        for k in (self.no_ts, self.sot, self.no_speech, self.translate): logits[k] = -np.inf

    def __call__(self, path):
        mel = features(str(path), self.n_mels)
        ck, cv = self.enc.run([o.name for o in self.enc.get_outputs()][:2], {self.enc.get_inputs()[0].name: mel})
        kc = np.zeros((self.n_layer, 1, self.n_ctx, self.n_state), np.float32); vc = np.zeros_like(kc)
        toks = np.array([self.sot_seq], np.int64); off = np.zeros(1, np.int64)
        logits, kc, vc = self.dec.run(self.dout, dict(zip(self.din, [toks, kc, vc, ck, cv, off])))
        off += len(self.sot_seq)
        lg = logits[0, -1].copy(); self._suppress(lg, True); best = int(lg.argmax())
        out = []
        for _ in range(self.n_ctx):
            if best == self.eot: break
            out.append(best)
            logits, kc, vc = self.dec.run(self.dout, dict(zip(self.din, [np.array([[best]], np.int64), kc, vc, ck, cv, off])))
            off += 1
            lg = logits[0, -1].copy(); self._suppress(lg, False); best = int(lg.argmax())
        return b''.join(base64.b64decode(self.table[i]) for i in out if i in self.table).decode(errors='replace').strip()


SPOKEN = {'1st': 'first', '2nd': 'second', '3rd': 'third', '4th': 'fourth', '5th': 'fifth', '6th': 'sixth', '7th': 'seventh',
          '8th': 'eighth', '9th': 'ninth', '10th': 'tenth', '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
          '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine', '10': 'ten', '11': 'eleven', '12': 'twelve',
          '20': 'twenty', '22': 'twenty two', '30': 'thirty', '90': 'ninety'}


def words(s):
    """Lower-case words with digits and ordinals spelled out, so "5th" and "fifth" match."""
    toks = re.findall(r"[a-z0-9']+", s.lower().replace('’', "'").replace('-', ' '))
    return ' '.join(SPOKEN.get(t, t) for t in toks).split()


def similarity(a, b):
    return difflib.SequenceMatcher(None, words(a), words(b)).ratio()


def transcribe_file(path, w=None):
    """Any audio or video: decoded to 16 kHz mono first (needs ffmpeg)."""
    w = w or Whisper()
    with tempfile.NamedTemporaryFile(suffix='.wav') as f:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(path), '-vn', '-ac', '1', '-ar', '16000', f.name], check=True)
        return w(f.name)


def run(project_dir, reels=None, threshold=.75):
    proj, pdir, build, out = load_project(project_dir)
    w = Whisper(); flagged = []
    for line in all_lines(proj, reels):
        heard = w(build / 'vo' / f"{line['id']}.wav")
        s = similarity(line['text'], heard)
        mark = 'ok ' if s >= threshold else 'CHECK'
        if s < threshold: flagged.append(line['id'])
        print(f"  {mark} {line['id']} {s:.2f}  heard: {heard}")
    if flagged:
        print('  Lines to listen to (names are often heard approximately, which is fine):', flagged)
    return flagged


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--file':
        w = Whisper()
        for p in a[1:]: print(f'{p}: {transcribe_file(p, w)}')
    else:
        run(a[0], a[1:] or None)
