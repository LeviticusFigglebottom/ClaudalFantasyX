"""Writes the Coilspire preview layouts (M3-ENV-10): game/levels/_tests/coilspire_kit/coilspire_layout.json and
coilspire_backdrop.json.

    python3 assets_src/environments/kits/coilspire/cs_preview_layout.py

Both are HalunaDresser's format (hymn-zone-layout/1, no terrain: every piece carries its own "y"), in the Corrow
preview's world frame, so the temple stands exactly where Corrow's skyline piece stands:
* coilspire_layout.json: this kit. The headland pieces at the headland's transform (cs_common.HEADLAND), the
  spire pieces at the spire's (its base on the headland at cs_common.SPIRE_BASE_Y), the flue-keys and braziers
  where cs_common's plan puts them, the scrub along the path; plus "fire_lights" (the beacon) and
  "hearth_lights" (the braziers and the keeping flame) for CoilspirePreview.
* coilspire_backdrop.json: Corrow's kit as Corrow's preview places it (cw_preview_layout's wall, stair, town and
  far ground, read-only), without its `coilspire_headland`, which this kit replaces: what the gallery looks
  back at.

m2-slice copies the placement helpers it wants (swap-in note in the task file); nothing shipped reads these.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import cs_common as cs  # noqa: E402
import cs_tiers  # noqa: E402
from cs_common import kc  # noqa: E402

sys.path.insert(0, str(HERE.parent / "corrow"))
import cw_preview_layout as cwl  # noqa: E402  (Corrow's preview placements, read-only)

OUT_DIR = ROOT / "game" / "levels" / "_tests" / "coilspire_kit"
YAW = cs.HEADLAND[2]
BRAZIER_LIGHT = (2.0, 8.0, 1.15)  # energy, range (m), height above the brazier's floor
HALL_BRAZIER_LIGHT = (3.2, 10.0)  # the base hall's brazier lights the whole hall and the landing undersides
HEARTH_LIGHT = (1.6, 5.0)
GRATE_LIGHT = (1.4, 10.0, 0.8)  # energy, range, below the beacon grate
BEACON_LIGHT = (6.0, 60.0, 1.6)  # energy, range, height above the top (cw_preview_layout.headland's)
GREAT_KEY = (cs.GALLERY_Y + 1.15, 70.0, 1.6)  # axle height, spire angle (deg: facing the storm), scale
SCRUB_N = 70


def r3(v) -> list[float]:
    return [round(float(x), 3) for x in v]


def spire_piece(piece: str, y: float = 0.0, **kw) -> dict:
    x, yy, z = cs.world_from_spire(0.0, y, 0.0)
    d = {"piece": piece, "at": r3([x, z]), "y": round(yy, 3), "yaw_deg": YAW}
    d.update(kw)
    return d


def headland_piece(piece: str, **kw) -> dict:
    d = {"piece": piece, "at": [cs.HEADLAND[0], cs.HEADLAND[1]], "y": 0.0, "yaw_deg": YAW}
    d.update(kw)
    return d


def wall_yaw(a_deg: float, inward: bool) -> float:
    """World yaw (deg) of a fitting whose local +Z faces into the room (inward) or out of the wall at spire
    angle a. Godot's Basis(UP, yaw) sends +Z to (sin yaw, 0, cos yaw); spire angle a points at (cos a, sin a)."""
    a = a_deg + (180.0 if inward else 0.0)
    local_yaw = math.degrees(math.atan2(math.cos(math.radians(a)), math.sin(math.radians(a))))
    return round(local_yaw + YAW, 3)


def keys() -> list[dict]:
    out = []
    for tier, a, y, kind in cs.key_list():
        d = cs.dir_of(a)
        r = float(cs.inner_r(y))
        x, yy, z = cs.world_from_spire(*(d * r + [0.0, y, 0.0]))
        yaw = wall_yaw(a, inward=True)
        tag = f"tier{tier}_{kind}_{int(round(a))}"
        out.append({"piece": "flue_key", "at": r3([x, z]), "y": round(yy, 3), "yaw_deg": yaw, "tag": tag})
        wx, wy, wz = cs.world_from_spire(*(d * (r - cs_tiers.KEY_STUB) + [0.0, y, 0.0]))
        out.append({"piece": "flue_key_wheel", "at": r3([wx, wz]), "y": round(wy, 3), "yaw_deg": yaw, "tag": tag})
    # The great key on the gallery, facing out toward the storm (B07: the player opens the beacon).
    y, da, s = GREAT_KEY
    a = da
    d = cs.dir_of(a)
    r = float(cs.outer_r(y))
    yaw = wall_yaw(a, inward=False)
    x, yy, z = cs.world_from_spire(*(d * r + [0.0, y, 0.0]))
    out.append({"piece": "flue_key", "at": r3([x, z]), "y": round(yy, 3), "yaw_deg": yaw, "scale": s,
                "tag": "great_key"})
    wx, wy, wz = cs.world_from_spire(*(d * (r + cs_tiers.KEY_STUB * s) + [0.0, y, 0.0]))
    out.append({"piece": "flue_key_wheel", "at": r3([wx, wz]), "y": round(wy, 3), "yaw_deg": yaw, "scale": s,
                "tag": "great_key"})
    return out


def braziers() -> tuple[list[dict], list[list[float]]]:
    pieces, lights = [], []
    e, rng_m, h = BRAZIER_LIGHT
    for tier, a, rad, fy in cs.brazier_list():
        p = cs.dir_of(a) * rad + np.array([0.0, fy, 0.0])
        x, y, z = cs.world_from_spire(*p)
        pieces.append({"piece": "tier_brazier", "at": r3([x, z]), "y": round(y, 3), "yaw_deg": YAW + 37.0 * tier,
                       "tag": f"tier{tier}"})
        lights.append(r3([x, y + h, z]) + (list(HALL_BRAZIER_LIGHT) if tier == 1 else [e, rng_m]))
    # The keeping flame in the hearth arch (keeper's hut side and hall side both see it).
    ri, ro = float(cs.inner_r(0.0)), float(cs.outer_r(0.0))
    p = cs.dir_of(cs.HEARTH_A) * (0.5 * (ri + ro)) + np.array([0.0, 0.55, 0.0])
    lights.append(r3(cs.world_from_spire(*p)) + list(HEARTH_LIGHT))
    # The beacon's glow coming down through its grate into the crown chamber.
    lights.append(r3(cs.world_from_spire(0.0, cs.GRATE_Y - GRATE_LIGHT[2], 0.0)) + list(GRATE_LIGHT[:2]))
    return pieces, lights


def scrub() -> list[dict]:
    rng = kc.rng_for("coilspire_preview_scrub", 10)
    out = []
    tries = 0
    noise = cs.headland_noise()
    while len(out) < SCRUB_N and tries < 4000:
        tries += 1
        s = rng.uniform(2.0, cs.PATH.s[-1] - 4.0)
        p, _y, t = cs.PATH.at(s)
        side = np.array([-t[1], t[0]]) * rng.choice([-1.0, 1.0])
        q = p + side * rng.uniform(2.4, 11.0) + t * rng.uniform(-1.0, 1.0)
        d, _yp = cs.path_distance(np.array([q[0]]), np.array([q[1]]))
        if d[0] < 2.3 or math.hypot(q[0] - cs.SPIRE_AT[0], q[1] - cs.SPIRE_AT[1]) < 10.0:
            continue
        if any(math.hypot(q[0] - o[0], q[1] - o[1]) < 2.2 for o in [e["_l"] for e in out]):
            continue
        y = float(cs.ground_height(np.array(q[0]), np.array(q[1]), noise))
        if y < 8.0:
            continue
        x, yy, z = cs.world_from_headland(q[0], y - 0.06, q[1])
        piece = "scrub_clump_b" if rng.random() < 0.4 else "scrub_clump_a"
        out.append({"piece": piece, "at": r3([x, z]), "y": round(yy, 3), "yaw_deg": round(YAW + rng.uniform(-18, 18), 2),
                    "scale": round(float(rng.uniform(0.8, 1.25)), 3), "_l": (q[0], q[1])})
    for e in out:
        del e["_l"]
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bx, by, bz = cs.world_from_spire(0.0, cs.SPIRE_H + BEACON_LIGHT[2], 0.0)
    brz, hearth_lights = braziers()
    pieces = [headland_piece("coilspire_ground", lod1_from_m=2500.0), headland_piece("headland_path", lod1_from_m=2500.0)]
    pieces += [spire_piece(p, lod1_from_m=300.0) for p in ("coilspire_shell", "coilspire_flues")]
    pieces += [spire_piece("coilspire_tiers", lod1_from_m=120.0), spire_piece("keepers_hut", lod1_from_m=150.0),
               spire_piece("beacon_basket", cs.SPIRE_H, lod1_from_m=300.0)]
    pieces += keys() + brz + scrub()
    layout = {
        "schema": "hymn-zone-layout/1",
        "zone": "ch08/coilspire preview (M3-ENV-10): the kit composed for the design notes' key shots",
        "_about": "Generated by assets_src/environments/kits/coilspire/cs_preview_layout.py; do not edit by hand. "
                  "Coordinates: Corrow's preview world (x east, z south, y explicit per piece). The headland frame is "
                  "placed at (318, 178) yaw -30 deg; the spire's base is at its local (-18, -12), y "
                  f"{cs.SPIRE_BASE_Y:.3f}. Pieces with a tag are the trial's fittings (tier, kind, spire angle).",
        "seed": 10,
        "kit_dir": "res://assets/environments/kits/coilspire/",
        "materials_dir": "res://assets/environments/kits/coilspire/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "fire_lights": [r3([bx, by, bz]) + [BEACON_LIGHT[0], BEACON_LIGHT[1]]],
        "fire_light_color": "#E0702E",
        "hearth_lights": hearth_lights,
        "hearth_light_color": "#FFB16E",
        "pieces": pieces,
    }
    (OUT_DIR / "coilspire_layout.json").write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")
    back = [{"piece": "corrow_far", "at": [0.0, 0.0], "y": 0.0, "yaw_deg": 0.0, "lod1_from_m": 5000.0}]
    back += cwl.wall() + cwl.stair() + cwl.town()
    backdrop = {
        "schema": "hymn-zone-layout/1",
        "zone": "ch08/coilspire preview backdrop: Corrow as its own preview places it, without its skyline headland",
        "_about": "Generated by assets_src/environments/kits/coilspire/cs_preview_layout.py from Corrow's "
                  "cw_preview_layout (read-only); do not edit by hand.",
        "seed": 8,
        "kit_dir": "res://assets/environments/kits/corrow/",
        "materials_dir": "res://assets/environments/kits/corrow/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "pieces": back,
    }
    (OUT_DIR / "coilspire_backdrop.json").write_text(json.dumps(backdrop, indent=1) + "\n", encoding="utf-8")
    print(f"LAYOUT {len(pieces)} pieces, backdrop {len(back)} pieces -> {OUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
