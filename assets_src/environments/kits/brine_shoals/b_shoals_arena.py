"""Ch6's brine_shoals_afternoon arena with its smoke as Rendering's volumetric columns (env-art-b, M3-RND-21).
env-art's table (`SHOALS` in `assets_src/environments/kits/haluna/arena_scenes.py`, read-only) is written through the
same `write_arena`, unchanged, then b_smoke_columns.py swaps its two smoke_plume shells (the burning camp seen across
the flats) for SmokeColumn nodes. Re-run after the table changes, instead of `arena_scenes.py`'s own write of this
arena:

    python3 assets_src/environments/kits/brine_shoals/b_shoals_arena.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _arena_scenes():
    path = HERE.parent / "haluna" / "arena_scenes.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("arena_scenes_shoals", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(out_dir: Path | None = None) -> int:
    sys.path.insert(0, str(HERE))
    import b_smoke_columns

    AS = _arena_scenes()
    if out_dir is not None:  # tools/tests/test_b_arenas.py writes to a scratch dir
        AS.OUT_DIR = out_dir
    out = AS.write_arena(AS.SHOALS)
    print(f"ARENA {out.name} ({b_smoke_columns.swap(out)} smoke columns)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
