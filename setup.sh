#!/usr/bin/env bash
# Repo2Reels setup: Python packages, a headless Chromium, and the voice models (downloaded once into models/).
#   ./setup.sh               voice + render
#   ./setup.sh --listen      also the Whisper model, to hear every line back (about 160 MB more)
set -euo pipefail
cd "$(dirname "$0")"
MODELS="${R2R_MODELS:-models}"
LISTEN=0; [ "${1:-}" = "--listen" ] && LISTEN=1

say() { printf '\n== %s\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing: $1. $2"; exit 1; }; }

need python3 "Install Python 3.10 or newer."
need ffmpeg "Install ffmpeg (macOS: brew install ffmpeg; Ubuntu: sudo apt install ffmpeg)."
need git "Install git."

say "Python packages"
if python3 -c "import numpy, scipy, onnxruntime, playwright, PIL" 2>/dev/null; then
  echo "already installed"
else
  python3 -m pip install -r requirements.txt || python3 -m pip install --break-system-packages -r requirements.txt
fi

say "Headless Chromium (for rendering)"
if python3 - <<'EOF' 2>/dev/null
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); await b.close()
asyncio.run(main())
EOF
then echo "ready"; else python3 -m playwright install chromium; fi

mkdir -p "$MODELS"
fetch() {  # url dest
  if [ -s "$2" ]; then echo "have $(basename "$2")"; return; fi
  echo "downloading $(basename "$2") ..."
  curl -fL --retry 3 -o "$2.part" "$1" && mv "$2.part" "$2"
}

say "Voice: Kokoro v1.0 (Apache-2.0)"
fetch https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx "$MODELS/kokoro-v1.0.onnx"
fetch https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin "$MODELS/voices-v1.0.bin"

say "Pronunciation lexicon: misaki (Apache-2.0)"
if [ -s "$MODELS/misaki/us_gold.json" ] && [ -s "$MODELS/misaki/us_silver.json" ]; then echo "have it"; else
  tmp="$(mktemp -d)"
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/hexgrad/misaki "$tmp/misaki"
  git -C "$tmp/misaki" sparse-checkout set misaki/data
  mkdir -p "$MODELS/misaki"
  cp "$tmp/misaki/misaki/data/us_gold.json" "$tmp/misaki/misaki/data/us_silver.json" "$tmp/misaki/LICENSE" "$MODELS/misaki/"
  rm -rf "$tmp"
fi

if [ "$LISTEN" = 1 ]; then
  say "Listening: Whisper base.en, ONNX export from sherpa-onnx (MIT / Apache-2.0)"
  if [ -s "$MODELS/whisper/base.en-encoder.int8.onnx" ]; then echo "have it"; else
    tmp="$(mktemp -d)"
    curl -fL --retry 3 -o "$tmp/w.tar.bz2" https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-base.en.tar.bz2
    tar -xjf "$tmp/w.tar.bz2" -C "$tmp"
    mkdir -p "$MODELS/whisper"
    cp "$tmp"/sherpa-onnx-whisper-base.en/base.en-{encoder.int8.onnx,decoder.int8.onnx,tokens.txt} "$MODELS/whisper/"
    rm -rf "$tmp"
  fi
fi

say "Done"
echo "Try:  python3 make.py projects/keyva r11"
