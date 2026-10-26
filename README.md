# Repo2Reels

**Turn the product in a repo into short vertical reels: a hook in the first two seconds, a voice-over that has been heard back, motion that feels cut by hand, and a mix mastered for phones.**

![Three reels made with Repo2Reels: the hook, then the iris into the day scene, then the first card](media/showcase.gif)

Made with Repo2Reels for [keyva.ae](https://keyva.ae). Watch three in full; press play, then turn the sound on:

<table>
<tr>
<td align="center" width="33%"><video src="https://github.com/user-attachments/assets/2aed93e7-8370-4d9b-b934-60bed5622a4b" controls playsinline width="240"></video><br><sub>There's no JVC in Dubai's rent records</sub></td>
<td align="center" width="33%"><video src="https://github.com/user-attachments/assets/05890fd8-7f2f-4a9f-8eb6-aea6608b6f1e" controls playsinline width="240"></video><br><sub>That 10% deposit? It's not a law</sub></td>
<td align="center" width="33%"><video src="https://github.com/user-attachments/assets/cb3b43d4-320a-4c5a-8446-bb038ae68913" controls playsinline width="240"></video><br><sub>Keyva sometimes won't</sub></td>
</tr>
</table>

The same three are in [media/reels](media/reels) to download.

![The covers of all ten reels in the Keyva example](media/covers.jpg)

## brag × Remotion

Repo2Reels mixes two projects. [brag](https://github.com/latent-spaces/brag) is an agent skill with sharp creative rules for launch videos. [Remotion](https://www.remotion.dev) makes video with code, frame by frame, with springs, transitions and motion blur. Repo2Reels keeps brag's rules and rebuilds Remotion's motion ideas in one plain HTML page. A small Python pipeline then handles the voice, the music, the render and the checks. There's no React, no Node and no paid API: once setup is done, everything runs on your own machine.

| From brag | From Remotion | Added by Repo2Reels |
|---|---|---|
| The hook lands in the first 2 seconds | Each frame is a function of time: `render(t)` | Facts taken from the product's repo, each with its source |
| One real fact per reel, with the real product on screen | Springs, easing, `interpolate` | A voice-over spoken from phonemes and heard back by Whisper |
| Every frame works as a still | Iris, push and flip transitions | Hand-drawn circles, underlines and highlights |
| Voice written first, cuts on the beat | Motion blur, light leaks | Cards that grow as their rows arrive |
| Music and effects in one key | `fitText`, word-by-word captions | Captions that never flash past or wrap |
| Cover as frame 0, share copy included | | −14 LUFS mastering, contact-sheet checks |

The full story, and what the first batch taught us, is in [docs/how-it-works.md](docs/how-it-works.md).

## Quick start

```bash
git clone https://github.com/sravinp-art/Repo2Reels
cd Repo2Reels
./setup.sh                            # Python packages, a headless Chromium, voice models (about 350 MB, once)
python3 make.py projects/keyva r11    # -> out/keyva/keyva-reel-11-no-jvc-on-record.mp4
```

You need Python 3.10+, ffmpeg and git. A 25-second reel takes about 5 minutes on two CPU cores. `./setup.sh --listen` also fetches the Whisper model, which hears every line back.

## Make reels for your own product

**With Claude Code.** Add the plugin, then ask for reels from inside your product's repo:

```
/plugin marketplace add sravinp-art/Repo2Reels
/plugin install repo2reels@repo2reels
```

> make 5 reels about this product with repo2reels

The skill reads your code for facts and writes the hooks and scripts. It then builds the scenes, runs the pipeline, listens to every line and checks every frame.

**By hand.**
1. Copy `projects/keyva` to `projects/yourproduct`.
2. In `project.json`, set your brand and write the lines of each reel. Add a `lexicon` entry for any name the voice gets wrong.
3. In `scenes.js`, write one `REELS` entry per reel. [docs/writing-scenes.md](docs/writing-scenes.md) has the building blocks.
4. Run `python3 make.py projects/yourproduct --workers 2`, then look at every contact sheet in `build/yourproduct/qa/`.

## The pipeline

| Step | What happens | Output |
|---|---|---|
| `voice` | Words to phonemes (misaki lexicon plus yours), then Kokoro speaks each line | `build/<p>/vo/*.wav` |
| `listen` | Whisper transcribes each line and flags any drift from the script (`--listen`) | report |
| `timing` | Lines placed on a 120 bpm grid, every word timed | `build/<p>/timing.json` |
| `page` | Engine, world, your scenes and brand assembled into one page | `build/<p>/reel.html` |
| `events` | Sound cues, motion-blur windows and the cover time, read from the page | `build/<p>/events.json` |
| `score` | Music, sound effects and voice mixed, with the music ducked under the voice | `build/<p>/audio/*.wav` |
| `posters` | The cover frame of each reel | `build/<p>/posters/*.png` |
| `render` | Every frame, motion-blurred where things move fast | `build/<p>/pic/*.mp4` |
| `encode` | Cover, picture and sound, set to −14 LUFS | `out/<p>/*.mp4`, `*.jpg` |
| `qa` | Contact sheets, plus checks on hook width and caption timing | `build/<p>/qa/*.jpg` |

Run any steps on their own with `--steps page,events,render`, and for some reels only: `python3 make.py projects/keyva r11 r18`. A line is only spoken again if its words or the voice changed.

## What's inside

```
engine/      the reel page: motion toolkit, scene kit, captions, end card, the dusk-skyline world, fonts
r2r/         the pipeline: voice, listen, timing, build, page, score, render, encode, qa
projects/    one folder per product; keyva is the worked example (ten reels)
skills/      the Claude Code skill
docs/        how it works, and how to write scenes
```

## Credits

- [brag](https://github.com/latent-spaces/brag) by Shunit Haviv Hakimi (MIT): the creative rules.
- [Remotion](https://www.remotion.dev): the motion ideas, reimplemented here. Repo2Reels contains no Remotion code and is not affiliated with Remotion.
- Voice: [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) through [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx), and the [misaki](https://github.com/hexgrad/misaki) lexicon. Listening: Whisper through [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx). Fonts: Sora, Space Mono and Inter (SIL OFL).

The code is MIT-licensed. The Keyva name, logo and reels in `projects/keyva` and `media/` belong to Keyva. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
