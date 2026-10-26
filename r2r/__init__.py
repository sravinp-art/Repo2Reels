"""Repo2Reels pipeline.

setup.sh installs the Python packages into a private environment, .venv, when the system Python doesn't
already have them (macOS Homebrew and recent Ubuntu refuse to install into the system Python). Every entry
point, `python3 make.py ...` and `python3 -m r2r.<step> ...`, then re-runs itself inside .venv, so the
commands in the README work whichever python3 comes first on the PATH. Set R2R_NO_VENV=1 to skip this.
"""
import os as _os
import sys as _sys
from pathlib import Path as _Path


def _run_in_venv():
    root = _Path(__file__).resolve().parent.parent
    venv = root / '.venv'
    py = venv / 'bin' / 'python3'
    if _os.environ.get('R2R_NO_VENV') or not py.exists():
        return
    if _Path(_sys.prefix).resolve() == venv.resolve():
        return                                          # already inside it
    # The command line exactly as typed (python3 make.py ..., python3 -m r2r.page ...). sys.argv can't be used:
    # under -m it still reads ['-m'] while this package is being imported.
    argv = getattr(_sys, 'orig_argv', None)
    if not argv or len(argv) < 2 or _sys.flags.interactive or hasattr(_sys, 'ps1'):
        return                                          # an interactive session: leave it alone
    _os.execv(str(py), [str(py), *argv[1:]])


_run_in_venv()
