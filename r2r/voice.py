"""Voice-over: words -> phonemes -> speech, one WAV per line.

Phonemes come from the misaki US lexicon (gold, then silver) plus the project's own "lexicon" for names
the dictionary lacks or gets wrong. A line can override any word with "say": {"word": "phonemes"}.
Speech is Kokoro v1.0 (ONNX) run with onnxruntime, phonemes in directly, so nothing is guessed twice.

    python3 -m r2r.voice projects/keyva [--reels r11 r12] [--force]
"""
import hashlib
import json
import re
import sys

import numpy as np

from .common import MODELS, ROOT, all_lines, load_project

VOWELS = set('AIOQWYaeiouæɑɒɔəɛɜɪʊʌᵻ')
PUNCT_RE = r"[.,!?;:…—]"


class Lexicon:
    def __init__(self, extra=None):
        d = MODELS / 'misaki'
        self.gold = json.loads((d / 'us_gold.json').read_text())
        self.silver = json.loads((d / 'us_silver.json').read_text())
        self.extra = {k.lower(): v for k, v in (extra or {}).items()}

    def look(self, w):
        for k in (w, w.lower(), w.capitalize()):
            for lex in (self.gold, self.silver):
                if k in lex:
                    v = lex[k]
                    if isinstance(v, dict):
                        v = v.get('DEFAULT') or v.get('None') or next(iter(v.values()))
                    return v
        return None

    def word(self, w, nxt, override):
        lw = w.lower()
        if lw in override: return override[lw]
        if lw in self.extra: return self.extra[lw]
        if lw == 'the': return 'ði' if nxt and nxt[0] in VOWELS else 'ðə'
        if lw == 'a': return 'ɐ'
        if lw == 'an': return 'ɐn'
        if lw == 'to': return 'tʊ' if nxt and nxt[0] in VOWELS else 'tə'
        if lw == 'in': return 'ɪn'
        if lw == 'by': return 'bI'
        look = self.look
        v = look(w)
        if v is None and "'" in w:                      # possessives
            base, _, tail = w.partition("'")
            b = look(base)
            if b is not None and tail == 's':
                v = b + ('ɪz' if b[-1] in 'szʃʒʧʤ' else ('s' if b[-1] in 'ptkfθ' else 'z'))
        if v is None and lw.endswith('s') and not lw.endswith("'s"):
            b = look(w[:-1])
            if b is not None:
                v = b + ('ɪz' if b[-1] in 'szʃʒʧʤ' else ('s' if b[-1] in 'ptkfθ' else 'z'))
        if v is None and lw.endswith('ed'):
            for base in (w[:-1], w[:-2]):
                b = look(base)
                if b is not None:
                    v = b + ('ɪd' if b[-1] in 'td' else ('t' if b[-1] in 'pkfsʃʧθ' else 'd')); break
        if v is None and w.endswith("'"):
            v = look(w.rstrip("'"))
        if v is None and '-' in w:
            parts = [look(p) for p in w.split('-')]
            if all(parts): v = ' '.join(parts)
        return v

    def line(self, text, say=None):
        """Phoneme string for a line, plus [word, phonemes] pairs, plus words it could not find."""
        override = {k.lower(): v for k, v in (say or {}).items()}
        words = re.findall(r"[A-Za-z][A-Za-z'\-]*|" + PUNCT_RE, text)
        raw = [None] * len(words); missing = []
        for i in range(len(words) - 1, -1, -1):        # right to left: "the"/"to" depend on the next sound
            t = words[i]
            if re.match(PUNCT_RE, t):
                raw[i] = t; continue
            nxt = None
            for j in range(i + 1, len(words)):
                if raw[j] and not re.match(PUNCT_RE, raw[j]): nxt = raw[j]; break
                if raw[j]: break
            p = self.word(t, nxt.lstrip('ˈˌ') if nxt else None, override)
            if p is None:
                missing.append(t); p = '?'
            raw[i] = p
        s = ''
        for t in raw:
            if re.match(PUNCT_RE, t): s = s.rstrip() + t + ' '
            else: s += t + ' '
        return s.strip(), [[w, p] for w, p in zip(words, raw)], missing


class Kokoro:
    def __init__(self, voice='af_heart', speed=1.0, model='kokoro-v1.0.onnx'):
        import onnxruntime as ort
        self.vocab = json.loads((ROOT / 'r2r' / 'kokoro_vocab.json').read_text())
        voices = np.load(MODELS / 'voices-v1.0.bin', allow_pickle=False)
        self.voice = voices[voice]                    # (510, 1, 256)
        self.speed = speed
        self.sess = ort.InferenceSession(str(MODELS / model), providers=['CPUExecutionProvider'])
        ins = {i.name: i for i in self.sess.get_inputs()}
        self.tok_name = 'input_ids' if 'input_ids' in ins else 'tokens'
        self.speed_int = 'int' in ins['speed'].type

    def say(self, ph):
        unknown = sorted({c for c in ph if c not in self.vocab})
        toks = [self.vocab[c] for c in ph if c in self.vocab]
        style = self.voice[min(len(toks), len(self.voice)) - 1]
        feed = {self.tok_name: np.array([[0, *toks, 0]], dtype=np.int64), 'style': np.asarray(style, dtype=np.float32),
                'speed': np.array([round(self.speed) if self.speed_int else self.speed], dtype=np.int32 if self.speed_int else np.float32)}
        audio = self.sess.run(None, feed)[0].squeeze()
        return audio, unknown


def run(project_dir, reels=None, force=False):
    from scipy.io import wavfile
    proj, pdir, build, out = load_project(project_dir)
    vo = build / 'vo'; vo.mkdir(parents=True, exist_ok=True)
    lex = Lexicon(proj.get('lexicon'))
    v = proj.get('voice', {})
    tts = None
    lines_path = build / 'lines.json'
    known = {l['id']: l for l in json.loads(lines_path.read_text())} if lines_path.exists() else {}
    missing_all = set()
    for line in all_lines(proj, reels):
        ph, words, missing = lex.line(line['text'], line.get('say'))
        missing_all.update(missing)
        key = hashlib.sha1(json.dumps([ph, v.get('voice', 'af_heart'), v.get('speed', 1.0)]).encode()).hexdigest()[:12]
        rec = {'id': line['id'], 'text': line['text'], 'ph': ph, 'words': words, 'key': key}
        wav = vo / f"{line['id']}.wav"
        if not force and wav.exists() and known.get(line['id'], {}).get('key') == key:
            known[line['id']] = rec; continue
        if tts is None:
            tts = Kokoro(v.get('voice', 'af_heart'), v.get('speed', 1.0), v.get('model', 'kokoro-v1.0.onnx'))
        audio, unknown = tts.say(ph)
        if unknown: print('  unknown phoneme symbols in', line['id'], unknown)
        wavfile.write(wav, 24000, (np.clip(audio, -1, 1) * 32767).astype(np.int16))
        known[line['id']] = rec
        print(f"  {line['id']}: {len(audio) / 24000:.2f}s  {ph}")
    lines_path.write_text(json.dumps(list(known.values()), ensure_ascii=False, indent=1))
    if missing_all:
        print('  NOT IN THE LEXICON (add them to "lexicon" in project.json):', sorted(missing_all))
    return not missing_all


if __name__ == '__main__':
    a = sys.argv[1:]
    run(a[0], [x for x in a[1:] if not x.startswith('--')] or None, force='--force' in a)
