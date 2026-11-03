"""Ch4's derelict_deck_night arena with a night fill for the fighters (env-art-b, the PC's battle-UI pass row 71).
At battle distance the Spar-Wraith read as a black silhouette against the night sea: the table's moon (0.28) and
ambient (0.2) leave a dark body nothing to separate it from the dark water behind. env-art's table (`ARENAS
["derelict_deck_night"]` in `assets_src/environments/kits/haluna/arena_scenes.py`, read-only) is written through the
same `write_arena`, then two shadowless lights are added, both kept in the arena in battle (only Sun moves):

  MoonRim   the moon's light off the sea from behind the foes' side, low, edging every figure against the water
  NightFill a faint cool fill from behind the battle camera, so the side of a body the camera sees isn't black

and the ambient is lifted a little. Re-run after the table changes, instead of `arena_scenes.py`'s own write of this
arena:

    python3 assets_src/environments/kits/brine_shoals/b_derelict_arena.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ARENA = "derelict_deck_night"
FILL = {"color": "#3A5E86", "energy": 0.32}  # the table's 0.2 ambient, lifted
# (name, elevation deg, azimuth deg clockwise from north = -Z, colour, energy, specular)
LIGHTS = (
    ("MoonRim", 18.0, 340.0, "#A9C6EC", 0.6, 0.2),
    ("NightFill", 30.0, 170.0, "#6283AA", 0.45, 0.0),
)


def _load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def add_lights(text: str, sa) -> str:
    out = text.rstrip("\n")
    for name, elev, az, color, energy, spec in LIGHTS:
        out += (f'\n\n[node name="{name}" type="DirectionalLight3D" parent="."]\n'
                f"transform = {sa._dir_xform(elev, az)}\n"
                f"light_color = {sa._color(color)}\n"
                f"light_energy = {energy}\n"
                f"light_specular = {spec}\n"
                "shadow_enabled = false")
    return out + "\n"


def main(out_dir: Path | None = None) -> int:
    AS = _load("arena_scenes_derelict", HERE.parent / "haluna" / "arena_scenes.py")
    sa = _load("storm_arenas", ROOT / "tools" / "act1" / "storm_arenas.py")
    if out_dir is not None:  # tools/tests/test_b_arenas.py writes to a scratch dir
        AS.OUT_DIR = out_dir
    out = AS.write_arena({**AS.ARENAS[ARENA], "fill": dict(FILL)})
    out.write_text(add_lights(out.read_text(encoding="utf-8"), sa), encoding="utf-8")
    print(f"ARENA {out.name} (+ {', '.join(n for n, *_ in LIGHTS)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
