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
    main = _sys.modules.get('__main__')
    spec = getattr(main, '__spec__', None)
    if spec is not None and spec.name:
        head = ['-m', spec.name]                        # python3 -m r2r.page ...
    elif _sys.argv and _sys.argv[0] and _os.path.isfile(_sys.argv[0]):
        head = [_sys.argv[0]]                           # python3 make.py ...
    else:
        return                                          # python3 -c / an interactive session: leave it alone
    _os.execv(str(py), [str(py), *head, *_sys.argv[1:]])


_run_in_venv()
