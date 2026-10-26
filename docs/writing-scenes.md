# Writing scenes

A project's `scenes.js` adds one entry to `REELS` per reel. The engine (`engine/engine.html`) runs the rest:
the night scene with the hook, the iris into the day scene, captions, the corner bug, light leaks at the cuts
and the end card. The page is deterministic: `render(t)` poses every element for time `t`, so frames can be
rendered in any order, and motion blur can sample between frames.

## The shape of a reel

```js
REELS.r1 = {
  bug: 'Check an asking price',          // corner chip in the day scene
  label: 'Prices with their count and dates',   // end card headline
  foot: 'Sources, dates, "not advice" lines.',  // end card footnote
  setup() {
    std(this, 4);                        // iris at line 2, end card at line 4 (set this.paperAt / this.endAt yourself if you like)
    hookSetup(this, ['Most price tools', 'always give a number.', 'Keyva sometimes <g>won’t.</g>'], { max: 130, top: 300, extra: `
      <div class="glass ncard" id="np" style="top:930px">...</div>` });   // the hook, plus cards for the night scene
    $('pscene').innerHTML = `<div class="card dcard" id="s1">...</div>`;  // day-scene cards
    this.cards = [{ id: 's1', at: this.paperAt + .1 }]; deckSetup(this.cards);
    this.tst = wt(1, "won't"); ev(this.tst, 'stamp');                   // a word's start time, and a sound cue on it
    this.posterAt = this.tst + .45;                                        // the cover frame
  },
  scene(t) {
    hookIn(this.hw, t); nightCard($('np'), t, .25);
    deck(t, this.cards);
  },
};
```

`<g>…</g>` in a hook line sets those words in the accent colour. Hook lines are fitted to 900 px, measured as
they are really set, up to `max` px tall.

## Timing helpers
| | |
|---|---|
| `LN(i)` | voice line `i` (1-based): `.on`, `.off`, `.words` (`[word, start, end]`) |
| `wt(i, 'word', n=0)` / `we(...)` | start / end of the n-th "word" in line i. A word that isn't in the line throws, so typos fail loudly |
| `ev(t, kind)` | queue a sound effect: `pop` `chime` `soft` `hit` `print` `tick` `key` `click` `rise` `strike` `whip` `flip` `stamp` `scribble` (`open`, `iris`, `end` are automatic) |
| `mbWindow(a, b)` | motion-blur frames between a and b (fast moves: pushes, whips) |
| `std(this, n)` | iris just before line 2, end card just before line n |

## Motion
| | |
|---|---|
| `p(t, a, b)` | progress 0→1 between a and b, clamped |
| `iv(t, [t0, t1, ...], [v0, v1, ...], ease)` | interpolate across keyframes |
| `spr(t - t0, {damping, stiffness, mass})` | a physical spring from t0 (overshoots when underdamped) |
| `EO`, `EIO`, `EI`, `SMOOTH`, `Easing.bezier(...)`, `Easing.spring(...)` | easings |
| `pscale(k, s0, s1)` | scale that grows evenly to the eye (log space) |
| `enter(el, t, t0, {dy, dx, s0})` | fade, slide and spring in at t0 |
| `stamp(el, t, t0, rot)` | rubber stamp landing |
| `counter(t, t0, dur, a, b)` + `fmt(n)` | count up, formatted. Hide the element until the count starts: never show a "0" |
| `typeIn(el, 'text', t, a, b)` | typing with a caret |
| `flipCard(el, t, t0)` | 3D card flip (front/back faces) |
| `deckSetup(cards)` / `deck(t, cards)` | full-width cards: the first springs in, each next one pushes the last one out (motion-blurred, with a whip) |
| `revealSetup(card, [[rowId, t], ...])` / `reveal(card, rv, t)` | a card that grows as its rows arrive, like a receipt printing. Call it before any annotation on that card |
| `nightCard(el, t, t0)`, `chips(t, [[id, t0], ...])` | the night card's entrance; chips popping in |

## Hand-drawn annotations
`RN.circle(el)`, `RN.underline(el)`, `RN.strike(el)`, `RN.cross(el)`, `RN.highlight(el)`, each with optional
`{color, width, pad, seed}`. Make them in `setup()` and drive them in `scene(t)` with `.set(progress)`:
`this.c = RN.circle($('total'))` and then `this.c.set(p(t, t0, t0 + .5))`. An underline or highlight follows
its words onto a second line when they wrap.

## The stage
- 1080×1920 at 30 fps. The night scene is `#night` (the hook and its card). The day scene is `#pscene`, inside the iris.
- Hook lines run from x = 70 and end by x = 970, between y ≈ 290 and 720. Cards span x 100–940 (`.dcard`, `.ncard`).
- The caption plate sits at y = 1290. Keep everything important above y ≈ 1440, where TikTok and Instagram put their own text.
- Styles you can use: `.glass` (night card), `.card` (day card), `.eb` (eyebrow), `.tag` ("Illustrative"), `.chip` (`.ok` `.warn` `.gold` `.tint`), `.stamp`, `.big` (mono figure), `.h` (Sora heading), `.row`, `.blur`. The Keyva example's `scenes.css` has more: decks, timelines, receipts, flip cards.

## The world
`engine/world-dusk.js` draws the night skyline and the day line art. Another world is a file
`engine/world-<name>.js` that defines `drawNight(t)`, `cv` (the night canvas), `SKY` and `SKYLEN` (the day line
art path and its length), `ART.hz` (the day horizon) and `#sunGrp`, `#sunDisc` and `#sunHalo` inside `#dayart`.
Choose it with `"world": "<name>"` in `project.json`.

## Brand
`project.json` → `brand`: `name` (wordmark), `url` (end card), `logo` (an SVG file in the project folder) and an
optional `palette` that overrides the CSS colour variables: `teal`, `teal2`, `gold`, `goldlight`, `goldtxt`,
`goldsoft`, `ink`, `paper`, `muted`, `rust`, `rustsoft`, `tint`, `line`, `green`, `greensoft`.
