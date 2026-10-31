"""Writes the Ashcrown preview layout (M3-ENV-09): game/levels/_tests/ashcrown_kit/ashcrown_layout.json.

    python3 assets_src/environments/kits/ashcrown/ac_preview_layout.py

The layout is HalunaDresser's format (hymn-zone-layout/1, no terrain: every piece carries its own "y"),
plus two lists AshcrownPreview reads: "borrowed" (pieces of another kit, by .glb path, already slotted by
that kit's import: the Pemakar kit's ash_plume, open-hand gate and lamp pillars, read-only) and "lights"
(OmniLight3Ds: the hall's lamps, the forge trough, the vent's glow). Every kit piece is modelled in the
kit's frame (ashcrown.md §0) and stands at the origin; the borrowed pieces are placed from the kit's own
numbers. m2-slice copies what it wants (swap-in note in the task file); nothing shipped may read this file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import ac_approach  # noqa: E402
import ac_common as ac  # noqa: E402
import ac_hall  # noqa: E402
import build  # noqa: E402

OUT = ROOT / "game" / "levels" / "_tests" / "ashcrown_kit" / "ashcrown_layout.json"
PEMAKAR = "res://assets/environments/kits/pemakar/"
MATERIALS = "res://assets/environments/kits/ashcrown/materials/"
LAMP = "#FFB16E"  # oil_lamp
EMBER = "#E0702E"  # ember_orange
SKY = "#C9D2DA"  # the ash-veiled noon sky (ch05_temple fill, lightened)
BOUNCE = "#D9CBB8"  # sunlight off the ash-dusted court
GATE_SCALE = 1.6
GATE_FILL = "#E8D2B8"  # a warm sky-and-lamplight fill on the gate's hands (row 79)
# The big pieces draw LOD0 out to this distance (their origin is the temple's, not their middle).
FAR_LOD1_M = {"crest_ground": 3000.0, "ashcrown_tiers": 600.0, "flying_stair": 600.0, "forecourt": 600.0,
              "pilgrim_causeway": 600.0, "crown_pavilion": 600.0, "anvil_hall": 200.0, "anvil_altar": 200.0,
              "plume_vent": 600.0}
COURT_LAMP_ZS = (22.0, 28.0, 34.0, 40.0)
PLUME_LOD1_M = 900.0  # the near plume's dense LOD0 out to here (measured from the plume's foot)


def r3(v) -> list[float]:
    return [round(float(x), 3) for x in v]


def build_layout() -> dict:
    pieces = [{"piece": name, "at": [0.0, 0.0], "y": 0.0, "yaw_deg": 0.0, "lod1_from_m": FAR_LOD1_M[name]}
              for name in sorted(build.targets()) if name in FAR_LOD1_M]  # a kit piece the preview doesn't stand
                                                                                 # (ash_drift, M3-ENV-1310) is skipped
    borrowed = [
        # The plume where the Pemakar layout stands it (pemakar_layout: the vent's floor minus 10 m), with
        # this kit's noon material. The near plume (M3-ENV-11): ash_plume's own surface, dense, out to
        # PLUME_LOD1_M (O2's 660 m included); beyond, its LOD1 is ash_plume's LOD0.
        {"glb": PEMAKAR + "ash_plume_near.glb", "at": r3((0.0, ac.vent_y(), ac.VENT_Z)), "yaw_deg": 0.0,
         "materials": {"kit_plume": MATERIALS + "ac_plume_day.tres"}, "lod1_from_m": PLUME_LOD1_M},
        # The open-hand gate at the causeway's head (1.6x: 5.1 m forearms over the 4 m stair).
        {"glb": PEMAKAR + "open_hand_gate.glb", "at": r3((0.0, ac.FLOOR_Y, ac.GATE_Z)), "yaw_deg": 0.0,
         "scale": GATE_SCALE},
    ]
    for sx in (-1.0, 1.0):
        for z in COURT_LAMP_ZS:
            borrowed.append({"glb": PEMAKAR + "lamp_pillar.glb", "at": r3((sx * (ac.COURT_HALF_W - 1.4), ac.FLOOR_Y, z)),
                             "yaw_deg": 0.0})
    zs, ys, _steps = ac_approach.causeway_profile()
    for i in range(1, len(zs) - 1):
        if abs(ys[i] - ys[i + 1]) < 1e-9 and zs[i + 1] - zs[i] > 1.0:  # a landing
            for sx in (-1.0, 1.0):
                borrowed.append({"glb": PEMAKAR + "lamp_pillar.glb",
                                 "at": r3((sx * (ac.CAUSEWAY_HALF_W - 0.95), ys[i], 0.5 * (zs[i] + zs[i + 1]))),
                                 "yaw_deg": 0.0})
    lights = [{"at": r3(p), "color": LAMP, "energy": 2.4, "range": 6.0} for p in ac_hall.lamp_points()]
    # The PC's pass 7, row 79 (env-art-b with the Lead's leave): from the approach (A01, under the gate, looking up)
    # the hands' undersides stand against the bright overcast and read as flat black cut-outs. A soft fill low between
    # the forearms (the sun off the causeway's pale stone) models the palms and fingers from below.
    lights.append({"at": r3((0.0, ac.FLOOR_Y + 1.2, ac.GATE_Z)), "color": GATE_FILL, "energy": 3.5, "range": 14.0})
    lights.append({"at": r3((0.0, ac.FLOOR_Y + 0.55, ac.PAVILION_Z + ac_hall.TROUGH_Z)), "color": EMBER,
                   "energy": 1.6, "range": 7.0})
    # Daylight stand-ins inside the hall until Rendering's GI (ashcrown.md §0): the sky down the shaft onto the
    # anvil, and the sunlit court's bounce through the door into the vestibule. Pale, shadowless, soft.
    pz = ac.PAVILION_Z
    lights.append({"at": r3((0.0, ac.HALL_CEIL_Y - 0.8, pz)), "color": SKY, "energy": 5.0, "range": 14.0})
    lights.append({"at": r3((0.0, ac.FLOOR_Y + 3.5, ac.tier(0)["front"] - 2.0)), "color": BOUNCE, "energy": 3.0,
                   "range": 18.0})
    vy = float(ac.massif_local(np.array([0.0]), np.array([ac.VENT_Z + 36.0]))[0])
    lights.append({"at": r3((0.0, vy + 6.0, ac.VENT_Z + 36.0)), "color": EMBER, "energy": 6.0, "range": 40.0})
    return {
        "schema": "hymn-zone-layout/1",
        "zone": "ch05/ashcrown kit preview (M3-ENV-09)",
        "_about": ("Generated by assets_src/environments/kits/ashcrown/ac_preview_layout.py; do not hand-edit. "
                   "Coordinates are the kit's frame (ashcrown.md §0: the Pemakar layout's ashcrown_silhouette origin; "
                   "add (0, 306.72, -682) for the Pemakar town's). Placed by HalunaDresser and AshcrownPreview."),
        "seed": 9,
        "kit_dir": "res://assets/environments/kits/ashcrown/",
        "materials_dir": MATERIALS,
        "lod1_from_m": 70.0,
        "lod_end_m": 4000.0,
        "lod_margin_m": 2.0,
        "pieces": pieces,
        "borrowed": borrowed,
        "lights": lights,
    }


def main() -> int:
    data = build_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"ASHCROWN_LAYOUT {len(data['pieces'])} pieces, {len(data['borrowed'])} borrowed, {len(data['lights'])} lights")
    return 0


if __name__ == "__main__":
    sys.exit(main())
