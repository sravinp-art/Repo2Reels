# Contributing

Thanks for helping. Repo2Reels is small on purpose: one HTML page draws the picture, and a few Python
modules do everything else.

## Set up
```bash
./setup.sh --listen
python3 make.py projects/starter      # ends with "Done:" and the path of the MP4
```

## Before you open a pull request
- Make the starter reel and open `build/starter/qa/r1.jpg`. Every frame on that sheet should be clean.
- If you changed the engine (`engine/engine.html` or `engine/world-*.js`), check that the Keyva reels look
  the same as before. Run `python3 make.py projects/keyva --steps voice,timing,page,events`, then compare
  stills before and after: `python3 -m r2r.page stills projects/keyva r11 1.0 4.0 8.0`.
- Keep the page deterministic: `render(t)` must draw the same frame for the same `t`, whatever order the
  frames are rendered in. Use `rng(seed)` instead of `Math.random()`, and no `Date.now()` or CSS animations.
- Every pull request makes the starter reel on macOS and Linux (`.github/workflows/ci.yml`).

## Good first contributions
- A new world, `engine/world-<name>.js`. [docs/writing-scenes.md](docs/writing-scenes.md) says what it defines.
- New building blocks for the scene kit, with a reel that uses them.
- Another language: the pronunciation dictionary is American English for now.
- Windows support without WSL.

## Reporting a problem
Open an issue with the command you ran, the last lines of its output, your operating system and
`python3 --version`.
