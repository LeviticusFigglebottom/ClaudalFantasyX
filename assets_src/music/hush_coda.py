"""`hush_coda`: the slice end card's piano coda (M2-AUD-03; vertical_slice.md B12). The music is in
hush_first_verse.py (render_coda); this module is its render_all.py job.

Render:  python3 assets_src/music/hush_coda.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("hush_first_verse", os.path.join(HERE, "hush_first_verse.py"))
_hfv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_hfv)

OUT = _hfv.OUT_CODA


def render(out_path: str = OUT, verbose: bool = True) -> dict:
    return _hfv.render_coda(out_path, verbose=verbose)


if __name__ == "__main__":
    render()
