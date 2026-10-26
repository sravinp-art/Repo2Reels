# Third-party notices

## Ideas and adapted work
- **brag** by Shunit Haviv Hakimi, https://github.com/latent-spaces/brag (MIT). Repo2Reels adapts brag's
  creative rules for launch videos (hook first, show the real thing, every frame postable, cover as frame 0,
  share copy). The brag licence:

  > MIT License. Copyright (c) 2026 Shunit Haviv Hakimi. Permission is hereby granted, free of charge, to any
  > person obtaining a copy of this software and associated documentation files (the "Software"), to deal in
  > the Software without restriction, including without limitation the rights to use, copy, modify, merge,
  > publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
  > Software is furnished to do so, subject to the following conditions: The above copyright notice and this
  > permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS
  > PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
  > WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  > AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
  > CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
  > DEALINGS IN THE SOFTWARE.

- **Remotion**, https://www.remotion.dev. Repo2Reels reimplements ideas from Remotion (frame-driven rendering,
  interpolate, springs, easing, transitions, motion blur, light leaks, fitText, captions) in its own code. It
  contains no Remotion code and is not affiliated with or endorsed by Remotion. Remotion itself has its own
  licence, under which companies above a small size need a company licence.

- **sherpa-onnx** by k2-fsa, https://github.com/k2-fsa/sherpa-onnx (Apache-2.0). `r2r/listen.py` adapts the
  greedy Whisper decoding of `scripts/whisper/test.py` (log-mel features rewritten in numpy).

- **kokoro-onnx** by thewh1teagle, https://github.com/thewh1teagle/kokoro-onnx (MIT).
  `r2r/kokoro_vocab.json` is the phoneme vocabulary from its `config.json` (which comes from Kokoro-82M, Apache-2.0).

## Bundled
- **Sora** (Copyright 2019 The Sora Project Authors), **Space Mono** (Copyright 2016 The Space Mono Project
  Authors) and **Inter** (Copyright 2020 The Inter Project Authors), all under the SIL Open Font License 1.1.
  The full licences are in `engine/fonts/OFL-*.txt`.

## Downloaded by setup.sh (not in this repository)
- **Kokoro v1.0** text-to-speech model and voices by hexgrad (Apache-2.0), ONNX files published by kokoro-onnx.
- **misaki** pronunciation lexicon by hexgrad (Apache-2.0). Its licence is copied to `models/misaki/LICENSE`.
- **Whisper base.en** by OpenAI (MIT), the ONNX export published by sherpa-onnx (Apache-2.0).
