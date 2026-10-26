# Privacy

Repo2Reels collects no data and sends none. It has no accounts, no analytics and no telemetry.

**What it downloads.** `setup.sh` downloads, once:
- the Python packages in `requirements.txt`, from PyPI;
- a headless Chromium, from Playwright's download server;
- the voice model and voices (Kokoro), the pronunciation dictionary (misaki) and, with `--listen`, the
  listening model (Whisper), from GitHub.

These are ordinary downloads: none of your project's content is sent with them. After setup, Repo2Reels
makes no network requests at all.

**What stays on your computer.** Your scripts, the voice-over, the frames, the music and the finished
reels. Nothing is uploaded anywhere.

**The Claude Code plugin.** The skill asks Claude to read your product's files to find facts for the
reels, and to run Repo2Reels on your computer. Claude Code handles those files as it handles any other work
in your repository, under Anthropic's terms. Repo2Reels itself sends them nowhere.

Questions: open an issue at https://github.com/sravinp-art/Repo2Reels/issues.
