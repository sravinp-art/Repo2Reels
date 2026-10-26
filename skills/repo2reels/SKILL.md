---
name: repo2reels
description: Turn the product in this repo into short vertical reels (20–30 s, TikTok and Instagram) with a strong hook, a checked voice-over, beat-synced motion and a mastered mix, checked frame by frame. Use when asked for reels, shorts, a launch video or social videos about a product or codebase.
---

# Repo2Reels

You are making a batch of 1080×1920 reels about the product in the current repo. Each reel has one fact, a hook in the first two seconds, the real product on screen, captions word by word, and a cover that works as a still.

## 0. The toolkit
Find the Repo2Reels folder: a clone at `~/Repo2Reels`, or two levels up from this skill's base directory (the plugin root). If there's none, run `git clone https://github.com/sravinp-art/Repo2Reels ~/Repo2Reels`. Run `./setup.sh --listen` there once; it installs the Python packages (into `.venv` when the system Python can't take them), a headless Chromium and the voice models, and says what to install if anything is missing. Check the setup with `python3 make.py projects/starter` (one 20-second reel). Every command below runs from that folder.

## 1. Facts first (from the product's repo)
- Read the product's code, docs, copy and data. List every fact you might use with its source file and, for laws, fees or rates, the date the source says it was read.
- One fact per reel. Facts that surprise people make the best hooks: something people assume that isn't so, a number they don't know, a rule with a catch.
- Invent no figures. Anything made up for the picture (a search box, an ad, a cheque, an income) gets an on-screen "Illustrative" tag. A real figure shows its count and dates.
- Follow the product's own rules on wording and disclosure (banned words, which price is which, "not advice" lines, full cost lists). Put disclosures in the end-card footnote and in the caption.
- Don't cross out or mock a feature the product itself offers. Contrast it instead.

## 2. Hooks and scripts
- Hook formats that work: myth-bust ("That 10% deposit? It's not a law."), absence ("There's no JVC in Dubai's rent records."), number ("You can send USD 250,000 a year."), warning ("No permit number? That's the red flag."), contrarian ("Most price tools always give a number. Keyva sometimes won't.").
- 4–6 voice-over lines per reel, 20–30 s in all. Line 1 is the hook, the middle lines are the proof, and the last line is the product plus the name of its feature or page.
- Write numbers as they are spoken in the line text ("two hundred and fifty thousand dollars"). In `captions`, map them back to figures (`["two hundred and fifty thousand dollars", "USD 250,000"]`).

## 3. The project folder
Run `python3 make.py new <product>`: it copies `projects/starter` (one commented reel) to `projects/<product>`. Then edit:
- `project.json`: the brand (name, url, logo), the voice, a `lexicon` for names the dictionary lacks, and the reels (`slug`, `lines` with `id`, `text`, optional `say`, `pauseBefore`, `captions`).
- `scenes.js`: one `REELS.<id>` entry per reel, with `bug`, `label`, `foot`, `setup()` and `scene(t)`, and `this.posterAt` for the cover. Read `docs/writing-scenes.md` first; `projects/keyva` has ten finished reels to borrow patterns from (flip cards, receipts, timelines, counters).
- `scenes.css`: the card styles your scenes use.
- `logo.svg`: the brand mark.

The voice reads words only. A line with digits or symbols stops the `voice` step, so write numbers as they are said and map them back in `captions`. A word the dictionary lacks stops it too: add it to `lexicon` as a respelling in ordinary words (`"github": "git hub"`) or as misaki phonemes. Acronyms (API, GPU) are spelled out on their own.

## 4. Make
```
python3 make.py projects/<product> --steps voice,listen     # hear every line back; reword any hook that is misheard
python3 make.py projects/<product> --steps timing,page,events
python3 -m r2r.page stills projects/<product> r1 1.0 3.6 5.2   # look at key moments before rendering
python3 make.py projects/<product> --steps score,posters,render,encode,qa --workers 2
```
If a word comes out wrong, add it to `lexicon` (a respelling or misaki phonemes) and run `voice` again. Only changed lines are re-spoken.

## 5. Check every frame (don't skip this)
`qa` writes a contact sheet per reel (`build/<p>/qa/<rid>.jpg`) and checks hook width and captions. Open every sheet and look for:
- text off an edge or overlapping, a card that sits half-empty, a "0" before a count starts
- an annotation in the wrong place (it should follow its words), anything left over from the previous scene
- a payoff number still moving when the end card arrives, a caption that flashes past
Fix the cause in `scenes.js` or the engine, rebuild the page, and render again only the reels that changed. Then run `python3 -m r2r.listen --file out/<p>/<reel>.mp4` on the finished files.

## 6. Deliver
Deliver `out/<p>/*.mp4` and their `.jpg` covers, plus a share copy per reel (a caption, 5 hashtags and any disclaimer). Also deliver a short plan: a table of hook, fact and source per reel, what is illustrative, and which reels to post first.
