"""The Shell Shrine's inner pool filling (M2-AUD-01): a 6 s seamless stereo loop. The model is in shrine_sfx.py
(render_fill); this module is its render_all.py job, so the loop gets the music_loop checks and its import settings.

Render:  python3 assets_src/sfx/shrine_pool_fill.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("shrine_sfx", os.path.join(HERE, "shrine_sfx.py"))
_sfx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sfx)

OUT = os.path.join(_sfx.OUT_DIR, "shrine_pool_fill.ogg")


def render(out_path: str = OUT, verbose: bool = True) -> dict:
    return _sfx.render_fill(out_path, verbose=verbose)


if __name__ == "__main__":
    render()
