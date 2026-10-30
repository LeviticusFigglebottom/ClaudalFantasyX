"""The Lacquer Court's step-hold arena (env-art-b; M4-A2P-044, arenas_ch13_16.md), written by env-art's arena writer
(`arena_scenes.py`, read-only: its `write_arena` and table format), as Act I's Ashcrown arenas are (ashcrown/b_arenas.py):

  lacquer_court_steps  Ch14's step-hold: the party holds the top of the court's water-steps while Merel cuts the barge
                       loose; the bridal barge and the water-gate behind the party, the lit dais and the Conclave's
                       gallery behind the enemy line (the Stillguard come up from the court). `ch14` dusk at peak
                       contrast, the ceremony's lamp-stands lit.

The arena is the court zone's own dressing (tools/act2/ch14_lacquer_court_dressing.py) moved into the arena frame
about COURT_AT (the fight's centre on the court's paving, near the steps' head). Re-run after the
kit or the court changes:

    python3 assets_src/environments/kits/haluna/ansedra_arenas.py
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


COURT = _load(ROOT / "tools" / "act2" / "ch14_lacquer_court_dressing.py", "ch14_lacquer_court_dressing_arena")
KIT = "res://assets/environments/kits/haluna/"
COURT_AT = (0.0, 0.0, -4.5)  # the fight's centre on the court, 4.5 m in from the steps' head (the slots stay on the paving)
# The battle camera looks along the arena's -Z: unturned, it looks north over the court to the lit dais and the halls,
# with the Conclave's gallery (court -X) on the enemy's side (-X). The water-steps, the barge and the gate are behind it
# (the hints `the_steps` and `the_gate` turn to them). A quarter turn put the side gallery and the open sea behind
# the fight instead (the first render).
TURN_DEG = 0.0
SKIP = ("court_ground",)  # the arena's ground
LAMP_FLAME_Y = COURT.FLAME_Y + 0.1


def to_arena(x: float, y: float, z: float) -> tuple[float, float, float]:
    """A court point in the arena frame: about COURT_AT, turned TURN_DEG about +Y (Godot's yaw)."""
    dx, dz = x - COURT_AT[0], z - COURT_AT[2]
    a = math.radians(TURN_DEG)
    return (round(dx * math.cos(a) + dz * math.sin(a), 3), round(y - COURT_AT[1], 3),
            round(-dx * math.sin(a) + dz * math.cos(a), 3))


def steps() -> dict:
    esc = AS.ANSEDRA_ESCAPE
    rows = COURT.dressing()
    pieces = []
    for r in rows["pieces"]:
        if r["piece"] in SKIP:
            continue
        pieces.append({"glb": KIT + r["piece"] + ".glb", "at": to_arena(r["at"][0], r.get("y", 0.0), r["at"][1]),
                       "yaw": round(TURN_DEG + r.get("yaw_deg", 0.0), 3), **({"scale": r["scale"]} if "scale" in r else {}),
                       "structure": True})
    lamps = [{"at": to_arena(*fl["at"]), "color": COURT.LAMP_COLOR, "energy": COURT.LAMP_ENERGY,
              "range": COURT.LAMP_RANGE_M, "own": True, "shadow": False} for fl in rows["fire_lights"]]
    gate = to_arena(0.0, 3.0, 18.0)
    conclave = to_arena(-12.0, 3.0, -21.5)
    return {
        "id": "lacquer_court_steps",
        "sub_frame": "ch14",
        "ground": "deck",
        "ground_glb": KIT + "court_ground.glb",
        "ground_at": to_arena(0.0, 0.0, 0.0),
        "ground_yaw": TURN_DEG,
        "lut": esc["lut"],
        # The escape arena's ch14 dusk (its sun at 5 deg so the rails' shadows don't black out the floor), here over the
        # court: the low sun from the west lights the dais's side.
        "sun": dict(esc["sun"]),
        "fill": dict(esc["fill"]),
        "exposure": 1.1,
        "glow": esc["glow"],
        "fog": dict(esc["fog"]),
        "sky_shader": esc["sky_shader"],
        "sky": dict(esc["sky"]),
        "sea": {"y": COURT.WATER_Y, "tide_line_y": COURT.WATER_Y, "sea_glow": 0.04, "material": esc["sea"]["material"],
                "waves": esc["sea"]["waves"]},
        "pieces": pieces,
        "extra_glbs": [],
        "scatters": [],
        "lamp_spec": {"color": COURT.LAMP_COLOR, "energy": COURT.LAMP_ENERGY, "range_m": COURT.LAMP_RANGE_M,
                      "attenuation": 1.2, "flame_radius_m": 0.05, "flame_energy": 6.0},
        "lamps": lamps,
        "hints": {
            "wide_high": ((-1.0, 6.5, 12.0), (0.0, 0.3, -3.0)),
            "party_side": ((5.0, 1.6, 4.5), (-1.5, 1.0, -0.5)),
            "foe_side": ((-5.0, 1.6, 4.0), (1.5, 1.0, 0.0)),
            "the_steps": ((-4.0, 1.6, 2.0), (gate[0], 1.0, gate[2])),
            "the_gate": ((1.0, 1.2, 2.5), gate),
            "the_conclave": ((3.0, 1.6, -2.0), conclave),
        },
    }


ARENAS = {"lacquer_court_steps": steps}


def main(out_dir: Path | None = None) -> int:
    if out_dir is not None:
        AS.OUT_DIR = out_dir
    zl = _load(ROOT / "tools" / "act1" / "ch05_09_zone_looks.py", "ch05_09_zone_looks_arena")
    looks = {slot: COURT.ans.RES_ZONE + name for slot, (name, _) in COURT.ans.LOOKS.items()}
    looks["kit_order_marble"] = COURT.ans.RES_ZONE + COURT.ans.MARBLE_NAME
    for _aid, fn in ARENAS.items():
        path = AS.write_arena(fn())
        path.write_text(zl.add_kit_slot_swaps(path.read_text(encoding="utf-8"), looks), encoding="utf-8")
        print(f"ARENA {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
