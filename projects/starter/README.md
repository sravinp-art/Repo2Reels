# The starter project

One 20-second reel, about Repo2Reels itself. It is the quickest way to check your setup, and the place to
start your own:

```bash
python3 make.py projects/starter      # makes out/starter/repo2reels-reel-1-your-repo-reels.mp4
python3 make.py new yourproduct       # copies this folder to projects/yourproduct
```

| File | What it holds |
|---|---|
| `project.json` | The brand (name, address, logo), the voice, words the voice needs help with (`lexicon`), and each reel's lines |
| `scenes.js` | What is on screen while each line is said: the hook, a card for the night scene, the cards of the day scene |
| `scenes.css` | Styles for those cards |
| `logo.svg` | The logo on the corner chip and the end card |

## Writing the lines
- Five lines make a 20-second reel. Line 1 is the hook: say the surprising thing first.
- Write numbers as words, the way they are said, and show them as figures in the captions:
  `{"text": "Save twenty percent.", "captions": [["twenty percent", "20%"]]}`. The voice reads words only,
  so `make.py` stops on a line with digits or symbols and shows you which.
- Names the voice doesn't know stop the run too, with a list. Add each to `lexicon`, written the way it
  sounds with ordinary words: `"lexicon": {"github": "git hub"}`. Acronyms like API and GPU are spelled out
  by themselves.
- `"pauseBefore": 0.4` on a line leaves room for a card to land before it is said.

## Changing what is on screen
`scenes.js` is commented line by line. Every helper it uses is in [docs/writing-scenes.md](../../docs/writing-scenes.md),
and `projects/keyva` has ten more reels to borrow from: flip cards, receipts, timelines, counters.
