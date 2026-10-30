"""The Pale Rim's shallows arena (env-art-b; M4-A2P-046, ch16.md's encounter table: `ch16_rim_skates` and
`ch16_rim_crawlers` fight in `pale_rim_shallows`), written by env-art's arena writer (`arena_scenes.py`, read-only: its
`write_arena` and table format), as the Ch14 arenas are (ansedra_arenas.py):

  pale_rim_shallows  the wade south along the Rim: ankle-deep still water over white sand, a cairn line into the white,
                     the marker poles. The Rim's own white overcast noon (colour script ch16; the zone's sky, fog,
                     water and lut_ch16_rim), the battle camera looking down the wade toward the Choir.

The arena is the zone's own dressing (tools/act2/ch16_pale_rim_dressing.py) moved into the arena frame about RIM_AT
(between two cairns on the wade's line, so no cairn stands on the fight floor). Re-run after the kit or the Rim changes:

    python3 assets_src/environments/kits/haluna/rim_arenas.py
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import arena_scenes as AS  # noqa: E402


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RIM = _load(ROOT / "tools" / "act2" / "ch16_pale_rim_dressing.py", "ch16_pale_rim_dressing_arena")
KIT = "res://assets/environments/kits/haluna/"
RIM_AT = (81.0, 0.0, 0.0)  # on the wade, halfway between Cairn2 (67) and Cairn3 (96): both 14 m off the fight's centre
# The battle camera looks along the arena's -Z. A quarter turn puts the wade's +X (south, toward the Choir) there: the
# cairn line runs away into the white behind the enemy line, and the way back to the ship is behind the party.
TURN_DEG = 90.0
GROUND = "pale_rim_strand"
REACH_M = 160.0  # the zone's pieces this far from the fight are kept (the cairn line fades into the fog by then)
# The arena's water: a still film over the sand (the zone's 12 cm would hide the feet of every slot), in the zone's
# water look (water_looks.json `pale_rim`)
SEA_Y = 0.05
STILL_WAVES = [(40.0, 1.0, 0.003, 0.05), (23.0, 0.7, 0.002, 0.04)]


def to_arena(x: float, y: float, z: float) -> tuple[float, float, float]:
    """A Rim point in the arena frame: about RIM_AT, turned TURN_DEG about +Y (Godot's yaw)."""
    dx, dz = x - RIM_AT[0], z - RIM_AT[2]
    a = math.radians(TURN_DEG)
    return (round(dx * math.cos(a) + dz * math.sin(a), 3), round(y - RIM_AT[1], 3),
            round(-dx * math.sin(a) + dz * math.cos(a), 3))


def _hex(godot_color: str) -> str:
    r, g, b = (float(v) for v in godot_color[godot_color.index("(") + 1:].split(",")[:3])
    return "#" + "".join(f"{round(c * 255):02X}" for c in (r, g, b))


def shallows() -> dict:
    rows = RIM.dressing()
    pieces = []
    for r in rows["pieces"]:
        if r["piece"] == GROUND:
            continue
        x, z = r["at"]
        if math.hypot(x - RIM_AT[0], z - RIM_AT[2]) > REACH_M:
            continue
        pieces.append({"glb": KIT + r["piece"] + ".glb", "at": to_arena(x, r.get("y", 0.0), z),
                       "yaw": round(TURN_DEG + r.get("yaw_deg", 0.0), 3), "structure": True})
    layout_sun = RIM.json.loads(RIM.LAYOUT.read_text(encoding="utf-8"))["sun"]
    choir = to_arena(205.0, 1.0, 0.0)
    ship = to_arena(-30.0, 1.5, 0.0)
    return {
        "id": "pale_rim_shallows",
        "sub_frame": "ch16",
        "ground": "deck",
        "ground_glb": KIT + GROUND + ".glb",
        "ground_at": to_arena(RIM.STRAND_AT[0], 0.0, RIM.STRAND_AT[1]),
        "ground_yaw": TURN_DEG,
        "lut": RIM.RES_ZONE + RIM.LUT_NAME,
        # The Rim's white overcast noon (the zone's layout sun and environment): a high soft key, a pale fill, the fog
        # taking the horizon.
        "sun": {"elev": -layout_sun["pitch_deg"], "az": 180.0, "color": layout_sun["color"].upper(),
                "energy": layout_sun["energy"], "max_distance": 80.0},
        "fill": {"color": "#D8DEE4", "energy": 0.9},
        "exposure": RIM.EXPOSURE,
        "glow": (0.3, 0.04, 1.2),
        "fog": {"color": _hex(RIM.FOG["color"]), "aerial": RIM.FOG["aerial"], "density": RIM.FOG["density"],
                "sky_affect": RIM.FOG["sky_affect"], "height": 0.0, "height_density": 0.0},
        "sky_shader": RIM.ans.SKY_SHADER,
        "sky": dict(RIM.SKY),
        "sea": {"y": SEA_Y, "tide_line_y": SEA_Y, "sea_glow": 0.0,
                "material": {"name": "arena_pale_rim_shallows", "shader": "res://game/shaders/water/water_ocean.gdshader",
                             "params": [("col_deep", RIM.WATER["col_deep"]),
                                        ("col_scatter_shallow", RIM.WATER["col_scatter_shallow"]),
                                        ("absorption_per_m", "Vector3(2, 0.5, 0.42)"),
                                        ("absorption_scale", float(RIM.WATER["absorption_scale"])),
                                        ("scatter_energy", 0.2), ("caustic_strength", float(RIM.WATER["caustic_strength"])),
                                        ("col_foam", "#F2F2EE"), ("col_sss", RIM.WATER["col_sss"]),
                                        ("foam_crest_threshold", 0.95), ("use_ssr", "true")]},
                "waves": STILL_WAVES},
        "pieces": pieces,
        "extra_glbs": [],
        "scatters": [],
        "hints": {
            "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.3, -3.0)),
            "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
            "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
            "the_cairns": ((1.0, 1.2, 6.0), choir),
            "the_way_back": ((-1.0, 1.4, -4.0), ship),
        },
    }


ARENAS = {"pale_rim_shallows": shallows}


def main(out_dir: Path | None = None) -> int:
    if out_dir is not None:
        AS.OUT_DIR = out_dir
    for _aid, fn in ARENAS.items():
        path = AS.write_arena(fn())
        print(f"ARENA {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
