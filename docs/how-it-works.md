# How Repo2Reels mixes brag and Remotion

Repo2Reels started as a question: what if the creative rules of
[brag](https://github.com/latent-spaces/brag) met the motion craft of [Remotion](https://www.remotion.dev)?
brag knows *what* a good launch video says and *when*. Remotion knows *how* video made in code can move like
it was cut by hand. Repo2Reels keeps the good part of each, in a plain HTML page and a small Python pipeline
that runs on your machine.

## What came from brag
brag is an agent skill that turns a project into a short launch video. Repo2Reels keeps its rules:

- **The hook lands in the first two seconds.** Nobody waits to find out what a reel is about.
- **Show the real thing.** The cards are the product's own screens and wording, with its real numbers.
- **Be specific.** One fact per reel, from the product's own code and docs.
- **Every frame is postable.** Any moment should work as a still, including mid-transition.
- **Write the voice first, cut on the beat.** Lines sit on a 120 bpm grid, and the cuts and cues land on their words.
- **Music and sound effects share a key.** The music ducks under the voice.
- **The cover is frame 0**, so the thumbnail and the opening agree.
- **Share copy ships with the video**: a caption, hashtags and any disclaimer.

## What came from Remotion
Remotion makes videos with React, one frame at a time. Repo2Reels reimplements these ideas from scratch in
vanilla JavaScript. None of Remotion's code is used, and Repo2Reels is not affiliated with Remotion.

- **Frames are a function of time.** `render(t)` poses everything for that instant, the way a Remotion
  composition does for `useCurrentFrame()`. That makes rendering deterministic and lets frames come out in any order.
- **`interpolate`, springs and easing.** Keyframe interpolation, a physical spring with real overshoot,
  bezier easings and a scale that grows evenly to the eye.
- **Transitions.** An iris from the night scene into the day scene, cards that push each other out, 3D flips.
- **Motion blur.** Frames during fast moves are rendered four times across a 180° shutter and averaged.
- **Light leaks** at the cuts.
- **`fitText`.** Hook lines are sized to fill the width, measured on the line as it is really set.
- **Word-by-word captions**, TikTok style, with the spoken word lit.

## What Repo2Reels adds
- **Facts with sources.** Each reel's fact comes from the product repo with its source file. Anything made up
  for the picture is tagged "Illustrative" on screen.
- **A voice you can trust.** Kokoro speaks the script from phonemes, with a lexicon for local names. Whisper
  then listens to every line and every final mix and flags anything misheard.
- **Hand-drawn annotations**: circles, underlines, cross-outs and marker highlights that draw themselves on the
  word, and follow it onto a second line if it wraps.
- **Cards that grow** as their rows arrive, like a receipt printing, so no frame shows a half-empty card.
- **Readable captions.** Any chunk that would flash past in under 0.4 s is re-cut with its phrase, and the
  plate never wraps.
- **Sound made from scratch.** Pad, pluck, bass and drums in one key, one effect per cue, the voice compressed
  and the music ducked under it. There are no music licences to clear.
- **Loudness for phones**: two-pass normalisation to −14 LUFS, then a limiter.
- **A check before you post.** A contact sheet per reel (a frame a second plus every transition), plus
  automatic checks for hook width and caption timing.

## The pipeline

```
project.json ──► voice ──► listen ──► timing ──► page ──► events ──► score ──► posters ──► render ──► encode ──► qa
 (lines, brand)   Kokoro    Whisper    beat grid  engine+   cues,     music+    frame 0    frames,    cover +    sheets,
                  phonemes  check      word times scenes    blur      SFX+VO              blur       sound,     checks
                                                            windows   mix                            −14 LUFS
```

Each step writes into `build/<project>/` and can be re-run on its own (`--steps`), for just some reels.
Only lines whose words or voice changed are spoken again.

## Lessons from the first batch
The Keyva reels were checked frame by frame before they shipped, and these fixes are now built in:
- Letter-spacing set in `em` on a parent resolves at the parent's font size, so hook lines came out wider
  than measured. Tracking now sits on the line itself, and the fit is measured from the real line.
- An inline element that wraps has one box per line. Underlines now draw per line instead of off the card.
- Annotations with a z-index escaped the night layer and showed through the iris. The night layer is isolated now.
- Counters now stay hidden until they start, so "0 recorded sales" never sits on screen.
- A payoff number (a total) must land at least 0.6 s before the end card.
- Captions in quick speech are re-cut so that nothing flashes past, and they always fit on one line.
