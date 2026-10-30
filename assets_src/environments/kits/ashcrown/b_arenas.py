"""Ch5 Ashcrown's two battle arenas (env-art-b; ADR 0041), from the Ashcrown kit, written by the arena writer of
docs/kb/tech/battle_arenas.md (`assets_src/environments/kits/haluna/arena_scenes.py`, read-only: its `write_arena`
and table format). Every Ch5 fight played on the Pemakar terrace at night (`ash_terrace_lanternfall`), but the stair
fights and the Cinder Matron are Ashcrown's, by day (act1_ch05.md B07, B09):

  ashcrown_forecourt_day  the stair fights (ch05_stair_*): the forecourt at the top of the pilgrims' causeway, its
                          paving the floor, the fight east of the flying stair's foot, the tiers, the stair and the
                          pavilion rising beyond the enemy line, the plume over the crest; `ch05_temple` (13:00).
  ashcrown_anvil_court    the Cinder Matron (ch05_cinder_matron): the anvil hall's nave between its pillars, the anvil
                          under the shaft beyond the enemy line, the Matron's alcove on the west wall, the crater
                          loggia's light at the end; `ch05_temple_int` (the hall lamps, the forge trough, the shaft and
                          door daylight stand-ins, interior ambient).

Each arena is the kit's frame moved so its floor point is the arena origin (FORECOURT_AT, COURT_AT). Re-run after the
kit changes:

    python3 assets_src/environments/kits/ashcrown/b_arenas.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import ac_common as ac  # noqa: E402


def _arena_scenes():
    path = HERE.parent / "haluna" / "arena_scenes.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("arena_scenes_ashcrown", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


AS = _arena_scenes()
KIT = "res://assets/environments/kits/ashcrown/"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "ashcrown_kit"
LUT = "res://assets/environments/zones/ch05/lut_ch05_ashcrown.png"
GRADE = ROOT / "assets" / "environments" / "zones" / "ch05" / "ch05_ashcrown_day_environment.tres"
SEA_Y_KIT = -ac.RIM_WORLD[1]  # Pemakar's sea, 306.7 m under the kit's origin
FORECOURT_AT = (12.0, ac.FLOOR_Y, 30.0)  # the fight east of the stair's foot, its camera on the court's south half
COURT_AT = (0.0, ac.FLOOR_Y, 1.0)  # the nave between the pillar pairs at z 2 and -3, the anvil 9.4 m beyond
EXTERIOR = ("ashcrown_tiers", "flying_stair", "crown_pavilion", "pilgrim_causeway", "crest_ground", "plume_vent")


def _sky() -> dict:
    """env-art's Ch5 day sky (its env_sky_low_sun parameters), as the arena table's sky row."""
    text = GRADE.read_text(encoding="utf-8")
    return {k: v for k, v in re.findall(r"^shader_parameter/(\w+) = (.+)$", text, flags=re.M)}


def _at(kit_xyz, origin) -> tuple[float, float, float]:
    return tuple(round(float(kit_xyz[i]) - origin[i], 3) for i in range(3))


def _preview() -> dict:
    return json.loads((PREVIEW / "ashcrown_layout.json").read_text(encoding="utf-8"))


TEMPLE_LIGHT = {  # ashcrown.md §0 `ch05_temple` (13:00): the sun through the ash veil, ash haze
    "sub_frame": "ch05_temple",
    "sun": {"elev": 58.0, "az": 225.0, "color": "#FFF0DC", "energy": 2.8},
    # the fill is the zone's (tools/act1/ch05_ashcrown_dressing.py ZONE_AMBIENT_ENERGY, M3-ENV-1325): at 0.45 the tiers'
    # shaded faces behind the enemy line were black planes
    "fill": {"color": "#8E959C", "energy": 1.8},
    "exposure": 0.72,
    "glow": (0.35, 0.03, 1.1),
    "fog": {"color": "#8C8882", "aerial": 0.5, "density": 0.0018, "sky_affect": 0.25, "height": 0.0,
            "height_density": 0.0},
    "sky_shader": AS.LOW_SUN_SKY,
    "lut": LUT,
}


def forecourt() -> dict:
    o = FORECOURT_AT
    pieces = [{"glb": KIT + p + ".glb", "at": _at((0, 0, 0), o), "yaw": 0.0, "structure": True} for p in EXTERIOR]
    for b in _preview()["borrowed"]:
        if "materials" in b:  # the plume's day look is a material override the arena writer has no row for
            continue
        pieces.append({"glb": b["glb"], "at": _at(b["at"], o), "yaw": b.get("yaw_deg", 0.0), "scale": b.get("scale", 1.0),
                       "structure": True})
    pieces.append({"glb": "res://assets/environments/kits/pemakar/ash_plume_near.glb", "at": _at((0.0, -56.717, -78.0), o),
                   "yaw": 0.0, "structure": True})
    return {
        "id": "ashcrown_forecourt_day",
        **TEMPLE_LIGHT,
        "sky": _sky(),
        "ground": "deck",
        "ground_glb": KIT + "forecourt.glb",
        "ground_at": _at((0, 0, 0), o),
        "sea": {"y": round(SEA_Y_KIT - o[1], 3), "tide_line_y": round(SEA_Y_KIT - o[1], 3), "sea_glow": 0.0},
        "pieces": pieces,
        "scatters": [],
        "hints": {
            "wide_high": ((-1.5, 8.0, 14.0), (0.0, 0.3, -3.0)),
            "party_side": ((7.0, 1.6, 5.0), (-1.5, 1.0, -0.5)),
            "foe_side": ((-7.5, 1.6, 5.0), (1.5, 1.0, 0.0)),
            "to_the_crown": ((4.0, 1.2, 7.0), (-12.0, 30.0, -36.0)),
        },
    }


INTERIOR_FIRE = "#FFB16E"
LOGGIA_SCREEN_IN_M = 0.25  # the lattice stands this far out from the nave into the loggia


def court() -> dict:
    o = COURT_AT
    pieces = [{"glb": KIT + p + ".glb", "at": _at((0, 0, 0), o), "yaw": 0.0, "structure": True}
              for p in ("anvil_altar", "ashcrown_tiers", "crest_ground", "plume_vent")]
    pieces.append({"glb": KIT + "matron_alcove.glb", "at": _at((-ac.HALL_HALF_W + 1.45, ac.FLOOR_Y, -10.4), o),
                   "yaw": 90.0, "structure": True})
    # The Tenders' wind lattice across the loggia (the PC's pass 5, row 63: the open loggia still read as a flat bright
    # panel behind the Matron's shoulder); just inside the opening, between its reveals.
    pieces.append({"glb": KIT + "loggia_screen.glb", "at": _at((0.0, ac.FLOOR_Y, ac.HALL_LOGGIA_Z - LOGGIA_SCREEN_IN_M), o),
                   "yaw": 0.0, "structure": True})
    # No plume here (the PC's pass 3, row 63): seen through the loggia door behind the Matron it filled the opening as
    # a flat grey panel. From inside the hall the loggia shows the crater rim and the sky.
    lamps = [{"at": _at(lp["at"], o), "color": lp["color"], "energy": lp["energy"], "range": lp["range"], "own": True,
              "shadow": k == 0} for k, lp in enumerate(_preview()["lights"])]
    # the forge trough's spill over the fight floor, so the battle camera's near half is not a black pool
    lamps.append({"at": (0.6, 3.2, 0.4), "color": INTERIOR_FIRE, "energy": 1.6, "range": 9.0, "own": True,
                  "shadow": False})
    return {
        "id": "ashcrown_anvil_court",
        **TEMPLE_LIGHT,
        "sub_frame": "ch05_temple_int",
        # ashcrown.md `ch05_temple_int`: interior ambient #2B2622 (raised to 1.4, exposure 1.35, so the party's floor
        # half reads in the battle camera); the sun reaches the floor only
        # down the shaft and through the door and the loggia (the stand-in lights are the preview's).
        "fill": {"color": "#2B2622", "energy": 1.4},
        "exposure": 1.35,
        "fog": {"color": "#3A3330", "aerial": 0.2, "density": 0.004, "sky_affect": 0.0, "height": 0.0,
                "height_density": 0.0},
        "sky": _sky(),
        "ground": "deck",
        "ground_glb": KIT + "anvil_hall.glb",
        "ground_at": _at((0, 0, 0), o),
        "sea": {"y": round(SEA_Y_KIT - o[1], 3), "tide_line_y": round(SEA_Y_KIT - o[1], 3), "sea_glow": 0.0},
        "pieces": pieces,
        "scatters": [],
        "lamp_spec": {"color": INTERIOR_FIRE, "energy": 2.4, "range_m": 6.0, "attenuation": 1.2,
                      "flame_radius_m": 0.05, "flame_energy": 6.0},
        "lamps": lamps,
        "anchors": {"BossAnchor": (-2.4, 0.0, 0.9)},
        "hints": {
            "wide_high": ((-1.0, 6.5, 12.0), (0.0, 0.3, -3.0)),
            "party_side": ((5.0, 1.6, 4.5), (-1.5, 1.0, -0.5)),
            "foe_side": ((-5.0, 1.6, 4.0), (1.5, 1.0, 0.0)),
            "to_the_shaft": ((1.0, 0.8, 5.0), (0.0, 9.0, -9.4)),
        },
    }


ARENAS = {"ashcrown_forecourt_day": forecourt, "ashcrown_anvil_court": court}
# The near plume's day look (M3-ENV-1314): the arena writer has no material override, so the plume drew in its own
# glb material (flat and red against the noon sky); the written scene gets the override on both LOD meshes.
PLUME_GLB = "res://assets/environments/kits/pemakar/ash_plume_near.glb"
PLUME_DAY = KIT + "materials/ac_plume_day.tres"
PLUME_MESHES = ("ash_plume_near", "ash_plume_near-lod1")
# The big17 gate review (10-30): at the forecourt's ~110 m the Pemakar kit's LOD chain (LOD1 from 70 m) drew the
# plume's coarse LOD1, a flat faceted slab across the battle camera's top left. The zone keeps LOD0 to 900 m
# (the Ashcrown preview's plume row) and narrows it to 0.75 across; the arenas do the same.
PLUME_LOD1_FROM_M = 900.0
PLUME_SCALE_XZ = 0.75


def plume_day(text: str) -> str:
    rid = re.search(rf'\[ext_resource type="PackedScene" path="{re.escape(PLUME_GLB)}" id="([^"]+)"\]', text)
    if rid is None:
        return text
    node = re.search(rf'\[node name="([^"]+)" parent="([^"]+)" instance=ExtResource\("{re.escape(rid.group(1))}"\)\]',
                     text)
    head = re.match(r"\[gd_scene load_steps=(\d+) format=3\]", text)
    text = text.replace(head.group(0), f"[gd_scene load_steps={int(head.group(1)) + 1} format=3]", 1)
    last = list(re.finditer(r"^\[ext_resource [^\n]*\]$", text, flags=re.M))[-1]
    text = text[:last.end()] + f'\n[ext_resource type="Material" path="{PLUME_DAY}" id="plume_day"]' + text[last.end():]
    path = f"{node.group(2)}/{node.group(1)}"
    for k, mesh in enumerate(PLUME_MESHES):
        rng = "visibility_range_end" if k == 0 else "visibility_range_begin"
        text = text.rstrip("\n") + (f'\n\n[node name="{mesh}" parent="{path}" index="{k}"]\n'
                                    'surface_material_override/0 = ExtResource("plume_day")\n'
                                    f'{rng} = {PLUME_LOD1_FROM_M}\n')
    # The zone's narrowing (ch05_ashcrown_dressing.PLUME_SCALE_XZ): the column stands back over its vent
    old = re.search(rf'(\[node name="{re.escape(node.group(1))}" parent="{re.escape(node.group(2))}" instance=[^\n]*\]\n)'
                    r"transform = Transform3D\(1, 0, 0, 0, 1, 0, -?0, 0, 1, ", text)
    if old is not None:
        sx = f"{PLUME_SCALE_XZ:g}"
        text = text.replace(old.group(0), old.group(1) + f"transform = Transform3D({sx}, 0, 0, 0, 1, 0, 0, 0, {sx}, ", 1)
    return text


# The zone's slot swaps (M3-ENV-1325: weathered copper, gold and lacquer, the stone's lighter baked occlusion), applied
# to the written scene by a KitSlotSwaps node (tools/act1/ch05_09_zone_looks.py).
def _zone_looks():
    spec = importlib.util.spec_from_file_location("ch05_09_zone_looks", ROOT / "tools" / "act1" / "ch05_09_zone_looks.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(out_dir: Path | None = None) -> int:
    if out_dir is not None:  # tools/tests/test_b_arenas.py writes to a scratch dir
        AS.OUT_DIR = out_dir
    zl = _zone_looks()
    paths = zl.load_generator("ch05_ashcrown_dressing").metal_paths()
    for aid, fn in ARENAS.items():
        path = AS.write_arena(fn())
        path.write_text(zl.add_kit_slot_swaps(plume_day(path.read_text(encoding="utf-8")), paths), encoding="utf-8")
        print(f"ARENA {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
