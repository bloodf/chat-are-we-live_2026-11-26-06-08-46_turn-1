#!/bin/bash
# Full asset rebuild. Needs: python 3.11 venv at ~/.cache/forge/py with `bpy==4.5.* numpy scipy pillow xatlas fonttools brotli`,
# and ~/.cache/forge/dl holding the unpacked `anny` wheel (PyPI) and `makehuman-data` tarball (npm). See CREDITS.md.
set -e; cd "$(dirname "$0")"; PY=~/.cache/forge/py/bin/python
node art.mjs; $PY textures_env.py; $PY characters.py; $PY props.py all; $PY backdrops.py; $PY envs.py; node compress.mjs
