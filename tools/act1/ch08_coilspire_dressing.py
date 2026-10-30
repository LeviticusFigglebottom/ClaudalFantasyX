#!/usr/bin/env python3
"""Ch8 Coilspire: env-art's Coilspire kit (M3-ENV-10) on ch08/coilspire, upright (M3-C08-1210, ADR 0200).

The greybox laid the spire's tiers out flat northward; the kit stands them up: the base hall (tier 1, the spire's
floor), landings at 9, 18 and 27 m (tiers 2-4), the crown floor at 35 m and the gallery ring at 42.6 m, joined by
stone flights that wind up the inner wall (cs_common.plan()), on the headland at the end of the path from the
wall. The zone takes the kit preview's frame, which is Corrow's world (cs_common.world_from_spire).

Writes next to the zone (game/levels/ch08/coilspire/):
  coilspire_dressing.json   the kit: ground, path, scrub, shell, flues, tiers, hut, beacon basket, the flue-keys (their
                            wheels spin with the trial's Key_<id> blocks), the tier braziers (on the Flame_<tier>
                            blocks), the hearth and grate lights, and Corrow's wall and far ground as the backdrop.
  coilspire_collision.json  trimesh on the shell, tiers, ground and hut (from the dressing), plus: ramps over every
                            flight and the path's flags (the controller has no step-up), the gates across each
                            flight's foot (Gate_t1-t4: the trial hides them as the flame climbs), the path's
                            verges, and the well's fall guards.
With --relayout it also moves the layout's story points into the frame once (relayout()).

    python3 tools/act1/ch08_coilspire_dressing.py [--relayout]
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "coilspire"
sys.path.insert(0, str(KIT_SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ch05_09_zone_looks as zl  # noqa: E402
import cs_common as cs  # noqa: E402
import cs_headland as ch  # noqa: E402
import cs_preview_layout as cpl  # noqa: E402
import cs_tiers  # noqa: E402
import numpy as np  # noqa: E402

ZONE = ROOT / "game" / "levels" / "ch08" / "coilspire"
LAYOUT = ZONE / "coilspire_layout.json"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "coilspire_kit"
RES_ZONE = "res://game/levels/ch08/coilspire/"
KIT = "res://assets/environments/kits/coilspire/"
FLIGHTS, LANDINGS = cs.plan()
SEG_TREADS = 4  # treads per straight ramp along a winding flight (its chord sags < 0.15 m)
GATE_TREAD = 3  # the gate across each flight stands over its third tread
THRESHOLD_IN_M = 0.35  # the gallery threshold starts this far past the crown stair's top (its corners clear the stair)
GUARD_CLEAR_M = 1.2  # a well guard stops this far short of the wall at each end
VERGE_M = 1.6  # the path's verges, out from its edge
PATH_STEP_M = 3.0
HUT_SIDE_OPEN = 1  # path segments at its top with no verge on the hut's side
# The trial's keys (game/data/flow/ch08_field.json) on the kit's flue-keys: the kit's angle where it has one,
# else a free angle on the same landing's arc (deg). The side flue's niche stands beside its key.
KEY_ANGLES = {"t1_a": 0.0, "t1_b": 88.0, "t1_c": 240.0, "t2_a": 204.0, "t2_b": 260.0, "t2_c": 285.0,
              "t2_side": 180.0, "t3_a": 106.0, "t3_seized": 188.0, "t3_b": 140.0, "t4_a": 291.0, "t4_b": 17.0,
              "t4_c": 320.0, "t4_d": 345.0}  # t4_d clear of flight 3's head (55)
TIER_FLOOR = {"t1": cs.TIER_Y[0], "t2": cs.TIER_Y[1], "t3": cs.TIER_Y[2], "t4": cs.TIER_Y[3]}
NICHE_DA = 9.0


def r3(v: float) -> float:
    return round(float(v), 3)


def world(p) -> list[float]:
    return [r3(v) for v in cs.world_from_spire(float(p[0]), float(p[1]), float(p[2]))]


def spire_point(a_deg: float, r: float, y: float) -> np.ndarray:
    return cs.dir_of(a_deg) * r + np.array([0.0, y, 0.0])


def ramp(rid: str, a, b, width: float) -> dict:
    return {"id": rid, "from": world(a), "to": world(b), "width": width}


def flight_ramps() -> list[dict]:
    """Every flight as straight ramps along its treads' nosing line, SEG_TREADS at a time (flight 5: the crown stair)."""
    out = []
    for f in FLIGHTS:
        rmid = float(cs.inner_r((f.y0 + f.y1) * 0.5)) - 0.5 * f.width
        pts = [spire_point(f.a0, rmid, f.y0)]
        for i in range(SEG_TREADS, f.count + 1, SEG_TREADS):
            a, top = f.tread(i)
            pts.append(spire_point(a + f.step * 0.5, rmid, top))
        if f.count % SEG_TREADS:
            a, top = f.tread(f.count)
            pts.append(spire_point(a + f.step * 0.5, rmid, top))
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            out.append(ramp(f"Flight{f.index}_{k}", a, b, f.width))
    return out


def gates() -> list[dict]:
    """Gate_t1-t4 across flights 1-4 at their GATE_TREAD (the trial hides a tier's gate when its flame is lit)."""
    out = []
    for f in FLIGHTS[:4]:
        a, top = f.tread(GATE_TREAD)
        rmid = float(cs.inner_r(top)) - 0.5 * f.width
        p = world(spire_point(a, rmid, top + 1.4))
        yaw = cpl.wall_yaw(a, inward=True)  # the gate's local x lies along the flight, local z across it
        out.append({"id": f"Gate_t{f.index}", "pos": p, "size": [0.3, 2.8, f.width + 0.6], "yaw": yaw,
                    "color": "#6b3a2a"})
    return out


def path_ramps_and_verges() -> tuple[list[dict], list[dict]]:
    """The path's flags as ramps between PATH_STEP_M samples of its walking height, and verges either side."""
    ramps, blocks = [], []
    total = float(cs.PATH.s[-1])
    s_list = list(np.arange(0.0, total, PATH_STEP_M)) + [total]
    for k, (s0, s1) in enumerate(zip(s_list, s_list[1:])):
        p0, y0, t0 = cs.PATH.at(s0)
        p1, y1, _t1 = cs.PATH.at(s1)
        a = cs.world_from_headland(p0[0], y0, p0[1])
        b = cs.world_from_headland(p1[0], y1, p1[1])
        ramps.append({"id": f"Path{k}", "from": [r3(v) for v in a], "to": [r3(v) for v in b], "width": cs.PATH_W + 0.4})
        n = np.array([-t0[1], t0[0]])
        for side in (-1.0, 1.0):
            if side < 0 and k >= len(s_list) - 1 - HUT_SIDE_OPEN:
                continue  # the path's top opens on to the forecourt toward the keeper's hut (B03)
            off = n * side * (cs.PATH_W * 0.5 + VERGE_M)
            c0 = cs.world_from_headland(p0[0] + off[0], 0.0, p0[1] + off[1])
            c1 = cs.world_from_headland(p1[0] + off[0], 0.0, p1[1] + off[1])
            mid = [(c0[0] + c1[0]) * 0.5, (y0 + y1) * 0.5 + 1.0, (c0[2] + c1[2]) * 0.5]
            length = math.hypot(c1[0] - c0[0], c1[2] - c0[2]) + 0.4
            yaw = math.degrees(math.atan2(c1[0] - c0[0], c1[2] - c0[2]))
            blocks.append({"id": f"Verge{'LR'[side > 0]}{k}", "pos": [r3(v) for v in mid],
                           "size": [0.4, abs(y1 - y0) + 3.0, r3(length)], "yaw": r3(yaw)})
    return ramps, blocks


def well_guards() -> list[dict]:
    """A low wall along each landing's chord, so nobody walks off into the well (the crown's grate is floor)."""
    out = []
    for ln in LANDINGS:
        r = float(cs.inner_r(ln.y))
        d = cs.dir_of(ln.centre)
        c = d * (-cs.LANDING_CHORD * r)
        # short of the wall at each end by a flight's width: the flights arrive and leave there (the kit's balustrade
        # keeps the well's edge along their treads)
        half = math.sqrt(max(r * r - (cs.LANDING_CHORD * r) ** 2, 0.0)) - GUARD_CLEAR_M
        p = world(c + np.array([0.0, ln.y + 0.5, 0.0]))
        out.append({"id": f"WellGuard_t{ln.tier}", "pos": p, "size": [r3(2 * half), 1.0, 0.25],
                    "yaw": cpl.wall_yaw(ln.centre, inward=True)})
    return out


def gallery_threshold() -> dict:
    """The crown stair tops out inside the spire's wall: a level slab from its last tread out through the gallery door
    on to the gallery deck (the kit's trimesh has no floor in the doorway)."""
    top = np.array(flight_ramps_of(5)[-1]["to"])  # already in the world frame
    out = np.array(world(spire_point(cs.gallery_door_a(), float(cs.outer_r(cs.GALLERY_Y)) + 0.4, cs.GALLERY_Y)))
    start = top + (out - top) / np.linalg.norm(out - top) * THRESHOLD_IN_M
    return {"id": "GalleryThreshold", "from": [r3(v) for v in start], "to": [r3(v) for v in out], "width": 0.9}


def door_sill() -> dict:
    """The spire's door: the hall floor stands 0.35 m above the forecourt at the sill (the controller has no step-up),
    so a short ramp runs over it from the forecourt into the doorway."""
    ro = float(cs.outer_r(0.0))
    return ramp("DoorSill", spire_point(cs.DOOR_A, ro + 1.9, cs.FORECOURT_DY), spire_point(cs.DOOR_A, ro + 0.1, 0.0), 1.4)


def door_reveal() -> dict:
    """The door's reveal through the wall: the ground runs on under it at the forecourt's height, and the hall's floor
    stops at the wall's inner face with a riser, so a level slab carries the sill's height through into the hall."""
    ro, ri = float(cs.outer_r(0.0)), float(cs.inner_r(0.0))
    return ramp("DoorReveal", spire_point(cs.DOOR_A, ro + 0.1, 0.0), spire_point(cs.DOOR_A, ri - 0.3, 0.0), 1.4)


HUT_SILL_DY = (-0.885, -0.235, -0.295)  # the ground outside the hut's door, its sill, its floor (from the spire's base;
# measured on the kit's meshes): the floor is raised 0.6 m above the ground, so a ramp runs up through the door


def hut_point(x: float, z: float, y: float) -> list[float]:
    """A point in the keeper's hut's frame (cs_hut): x along the spire's wall (+x toward the spire's door), z out."""
    return world(spire_point(cs.HEARTH_A - math.degrees(math.atan2(x, z)), math.hypot(x, z), y))


def hut_door_sill() -> list[dict]:
    import cs_hut
    z = cs_hut.DOOR[0]
    out, sill, floor = HUT_SILL_DY
    a, b, c = hut_point(cs_hut.HALF_X + 1.8, z, out), hut_point(cs_hut.HALF_X, z, sill), hut_point(cs_hut.HALF_X - 0.8, z, floor)
    return [{"id": "HutSillOut", "from": a, "to": b, "width": 0.8}, {"id": "HutSillIn", "from": b, "to": c, "width": 0.8}]


def flight_ramps_of(index: int) -> list[dict]:
    rows = [r for r in flight_ramps() if r["id"].startswith(f"Flight{index}_")]
    return sorted(rows, key=lambda r: int(r["id"].split("_")[1]))


def collision() -> dict:
    pr, pv = path_ramps_and_verges()
    return {"_about": "Generated by tools/act1/ch08_coilspire_dressing.py (ADR 0200); do not edit by hand. The kit's "
            "trimesh is in the dressing (collide: trimesh); these are the ramps, gates, verges and guards.",
            "blocks": gates() + pv + well_guards(), "ramps": flight_ramps() + pr + [gallery_threshold(), door_sill(), door_reveal()] + hut_door_sill()}


# --- dressing ----------------------------------------------------------------------------------------------------

def key_pieces() -> list[dict]:
    out = []
    for key, a in KEY_ANGLES.items():
        y = TIER_FLOOR[key.split("_")[0]] + 1.25
        r = float(cs.inner_r(y))
        d = cs.dir_of(a)
        yaw = cpl.wall_yaw(a, inward=True)
        x, yy, z = cs.world_from_spire(*(d * r + [0.0, y, 0.0]))
        out.append({"piece": "flue_key", "at": [r3(x), r3(z)], "y": r3(yy), "yaw_deg": yaw})
        wx, wy, wz = cs.world_from_spire(*(d * (r - cs_tiers.KEY_STUB) + [0.0, y, 0.0]))
        out.append({"piece": "flue_key_wheel", "at": [r3(wx), r3(wz)], "y": r3(wy), "yaw_deg": yaw,
                    "spin_with": f"Key_{key}"})
    return out


DOOR_BOX_SILL_M = 0.15  # a doorway's box starts this far above its sill, so the floor's triangles stay LOD1
DOOR_BOX_REACH_M = 0.4  # and reaches this far past the wall's faces, in and out


def door_boxes() -> list[dict]:
    """The spire's door and the gallery door, which the shell's and the tiers' LOD1 (closed shells) seal: boxes in the
    world frame where their trimesh collides from LOD0 (ZoneKitDressing "collide_lod0_in")."""
    import cs_spire
    out = []
    for a, half, y0, y1 in (cs_spire.DOOR, (cs.gallery_door_a(), cs_spire.GALLERY_DOOR_HALF, cs.GALLERY_Y,
                                            cs.GALLERY_Y + cs_spire.GALLERY_DOOR_H)):
        y = (y0 + DOOR_BOX_SILL_M + y1) * 0.5
        ro, wt = float(cs.outer_r(y)), float(cs.wall_t(y))
        out.append({"pos": world(spire_point(a, ro - wt * 0.5, y)),
                    "size": [r3(2 * half), r3(y1 - y0 - DOOR_BOX_SILL_M), r3(wt + 2 * DOOR_BOX_REACH_M)],
                    "yaw": cpl.wall_yaw(a, inward=True)})
    return out


# The Undertow seen from the beacon gallery (B07, "the storm against the wind"): Rendering's UndertowStorm at the
# beacon, from the south (corrow.md §0: it comes in from the south-east; from the headland that is south), on the
# StormWall block (shown when Virel is bound).
STORM = {"name": "Undertow", "at": [308.745, 77.285, 159.418], "preset": "ch08_seawall", "azimuth_deg": 170.0,
         "block": "StormWall"}
# env-art-b's flue-trial pieces (the Coilspire kit's b_spire_trial.py, M3-ENV-1222; renamed from b_trial.py so it never shadows Ashcrown's) on their blocks: (block, piece, origin)
TRIAL_PIECES = (("Gate_t1", "flue_gate", "foot"), ("Gate_t2", "flue_gate", "foot"), ("Gate_t3", "flue_gate", "foot"),
                ("Gate_t4", "flue_gate", "foot"), ("NicheSeal", "niche_seal", "foot"), ("Niche", "lamp_niche", "foot"),
                ("WrightMark", "wright_mark", "centre"))


# Virel in the crown chamber is act1-chapters' ZoneCast actor on her coil (M3-CRE-700), which owns her state after the
# binding (the Lead, 2026-10-29: Coilspire showed her twice). This dressing places no model of her (it did, as
# M3-ENV-1320's still piece, until then).


# The interior on the GPU (M3-ENV-1322, the PC's QA rows 6 and 27): the kit's cs_laterite_inner gathers its green
# verdigris into every mortar joint, so the well's walls read as a thin green grid, and the well was near-black away
# from the four braziers. The zone's own copy keeps a little verdigris off the joints, and each tier gets a ring of
# low, shadowless wall-wash lights at the keepers' wall lamps (wash_lamps), so the stonework reads.
INNER_SLOT = "cs_laterite_inner"
INNER_MAT = "coilspire_inner_material"
INNER_OVERRIDES = {"salt_coverage": "Vector2(0.0, 0.16)", "salt_cavity_gather": "0.3"}
WASH_PER_TIER = 4
WASH = {"lift_m": 2.2, "energy": 1.7, "range": 7.5}
LAMP_TRIES = 12
LAMP_MIN_GAP_DEG = 60.0
LAMP_TREAD_CLEAR_DEG = 14.0
LAMP_BLOCK_CLEAR_M = 1.8


def write_inner_material() -> None:
    src = (ROOT / "assets" / "environments" / "kits" / "coilspire" / "materials" / f"{INNER_SLOT}.tres")
    text = src.read_text(encoding="utf-8").replace(f'resource_name = "{INNER_SLOT}"', f'resource_name = "{INNER_MAT}"')
    for key, value in INNER_OVERRIDES.items():
        text = re.sub(rf"^shader_parameter/{key} = .*$", f"shader_parameter/{key} = {value}", text, flags=re.M)
    (ZONE / f"{INNER_MAT}.tres").write_text(text, encoding="utf-8")


def wash_lamps() -> tuple[list[dict], list[dict]]:
    """The keepers' lamps (the 10-29 audit: the wash lights had no source): b_spire_trial's wall_lamp on the well's
    wall WASH["lift_m"] over each tier's floor, facing the well's centre, its light at the dish. Each tier tries
    LAMP_TRIES angles and keeps up to WASH_PER_TIER of them, at least LAMP_MIN_GAP_DEG apart, clear of every flight's
    treads (with headroom) and of the trial's blocks."""
    flights, _landings = cs.plan()
    treads = [f.tread(i) for f in flights for i in range(1, f.count + 1)]
    blocks = [b for b in json.loads(LAYOUT.read_text(encoding="utf-8"))["blocks"]]
    pieces, lights = [], []
    for k, ty in enumerate(cs.TIER_Y):
        y = ty + WASH["lift_m"]
        r = float(cs.inner_r(y))
        kept: list[float] = []
        for n in range(LAMP_TRIES):
            a = 360.0 * (n + 0.5 * (k % 2)) / LAMP_TRIES
            if any(abs((a - b + 180.0) % 360.0 - 180.0) < LAMP_MIN_GAP_DEG for b in kept):
                continue
            if any(abs((a - ta + 180.0) % 360.0 - 180.0) < LAMP_TREAD_CLEAR_DEG and y - 2.1 < top < y + 0.4
                   for ta, top in treads):
                continue
            ar = math.radians(a)
            wx, wy, wz = cs.world_from_spire(r * math.cos(ar), y, r * math.sin(ar))
            if any(math.dist((wx, wy, wz), b["pos"]) < LAMP_BLOCK_CLEAR_M for b in blocks):
                continue
            kept.append(a)
            if len(kept) == WASH_PER_TIER:
                break
        for a in kept:
            ar = math.radians(a)
            wall = cs.world_from_spire(r * math.cos(ar), y, r * math.sin(ar))
            inner = cs.world_from_spire((r - 1.0) * math.cos(ar), y, (r - 1.0) * math.sin(ar))
            yaw = math.degrees(math.atan2(inner[0] - wall[0], inner[2] - wall[2]))
            pieces.append({"piece": "wall_lamp", "at": [r3(wall[0]), r3(wall[2])], "y": r3(wall[1]), "yaw_deg": r3(yaw)})
            reach = b_lamp_reach()
            d = ((inner[0] - wall[0]), (inner[2] - wall[2]))
            lights.append({"at": [r3(wall[0] + d[0] * reach[0]), r3(wall[1] - reach[1] + 0.06), r3(wall[2] + d[1] * reach[0])],
                           "energy": WASH["energy"], "range": WASH["range"]})
    return pieces, lights


def b_lamp_reach() -> tuple[float, float]:
    import b_spire_trial  # noqa: PLC0415  (the kit's own lamp dimensions)

    return b_spire_trial.LAMP_REACH, b_spire_trial.LAMP_DROP


def trial_pieces() -> list[dict]:
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    rows = {b["id"]: b for b in layout["blocks"]}
    rows.update({b["id"]: b for b in json.loads((ZONE / "coilspire_collision.json").read_text(encoding="utf-8"))["blocks"]})
    out = []
    for bid, piece, origin in TRIAL_PIECES:
        b = rows[bid]
        y = b["pos"][1] - (b["size"][1] * 0.5 if origin == "foot" else 0.0)
        out.append({"piece": piece, "at": [b["pos"][0], b["pos"][2]], "y": round(y, 3), "yaw_deg": b.get("yaw", 0.0),
                    "block": bid})
    return out


# The kit's metals at player height (M3-ENV-1326): `cs_copper`'s patina covered almost all of it, so the flue pipes,
# key housings and the roof read pale flat mint; the wheels' worn copper and the gates' iron are flat StandardMaterials.
# Swapped on every Coilspire piece (`kit_material_paths`).
KIT_LOOKS = {
    "cs_copper": ("coilspire_copper_material.tres", dict(zl.VERDIGRIS, patina_coverage=(0.1, 0.7))),
    "cs_copper_worn": ("coilspire_copper_worn_material.tres", {
        "col_bronze": (0.5020, 0.2706, 0.1255), "col_worn": (0.8000, 0.4784, 0.2706),
        "col_patina": (0.2706, 0.3804, 0.3373), "col_patina_pale": (0.4314, 0.5137, 0.4706),
        "metallic_bronze": 1.0, "roughness_bronze": 0.42, "roughness_worn": 0.25, "patina_coverage": (0.0, 0.25),
        "patina_roughness": 0.85, "streak_strength": 0.3, "wear_strength": 0.9, "detail_scale_m": 0.5,
        "normal_strength": 0.4, "normal_tile_m": 1.6}),
    "cs_iron": ("coilspire_iron_material.tres", dict(zl.SEA_IRON)),
}


def dressing() -> dict:
    preview = json.loads((PREVIEW / "coilspire_layout.json").read_text(encoding="utf-8"))
    pieces = []
    for p in preview["pieces"]:
        if p["piece"] in ("flue_key", "flue_key_wheel"):
            if p.get("tag") == "great_key":  # the trial's keys are placed by key_pieces(); the great key as built
                pieces.append(p)
            continue
        if p["piece"] == "tier_brazier":
            pieces.append(dict(p, block=f"Flame_t{p['tag'][-1]}"))
            continue
        if p["piece"] in ("coilspire_ground", "keepers_hut"):
            # LOD0: the hut's LOD1 is a closed shell (no door, no room) and would seal the hearth away
            pieces.append(dict(p, collide="trimesh_lod0"))
            continue
        if p["piece"] in ("coilspire_shell", "coilspire_tiers"):
            # LOD1 (LOD0's stonework grazes a body on the flights' treads), with the doorways from LOD0
            pieces.append(dict(p, collide="trimesh", collide_lod0_in=door_boxes()))
            continue
        pieces.append(p)
    pieces += key_pieces() + trial_pieces()
    backdrop = json.loads((PREVIEW / "coilspire_backdrop.json").read_text(encoding="utf-8"))
    corrow = "res://assets/environments/kits/corrow/"
    for p in backdrop.get("pieces", []):
        pieces.append(dict(p, kit_dir=corrow))
    lights = [{"at": l[:3], "energy": l[3], "range": l[4]} for l in preview.get("hearth_lights", [])]
    for i, light in enumerate(lights[:4]):  # the tier braziers' lights burn with their braziers (Flame_t1-t4)
        light["block"] = f"Flame_t{i + 1}"
    lights += [{"at": l[:3], "energy": l[3], "range": l[4]} for l in preview.get("fire_lights", [])]
    lamps, lamp_lights = wash_lamps()
    pieces += lamps
    lights += lamp_lights
    for p in pieces:
        if p["piece"] in ("coilspire_shell", "coilspire_tiers"):
            p["material_paths"] = {INNER_SLOT: RES_ZONE + INNER_MAT + ".tres"}
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act1/ch08_coilspire_dressing.py from env-art's Coilspire kit (M3-ENV-10); do "
        "not edit by hand. Corrow's world frame.",
        "seed": 10,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": float(preview.get("lod1_from_m", 70.0)),
        "lod_end_m": float(preview.get("lod_end_m", 4000.0)),
        "lod_margin_m": float(preview.get("lod_margin_m", 2.0)),
        "environment": RES_ZONE + "coilspire_ch08_environment.tres",
        "time_of_day_h": 12.0,
        "greybox": {"hide_all": True, "keep": []},
        "storms": [STORM],
        "fire_light_color": preview.get("hearth_light_color", "#FFB16E"),
        "fire_lights": lights,
        "kit_material_paths": {slot: RES_ZONE + name for slot, (name, _) in KIT_LOOKS.items()},
        "pieces": pieces,
    }


# --- the one-time move of the story points ----------------------------------------------------------------------

GB_BANDS = (("t1", -12.0, -34.0), ("t2", -34.0, -54.0), ("t3", -54.0, -74.0), ("t4", -74.0, -94.0),
            ("crown", -94.0, -110.5))
GB_PATH_Z = (62.0, 3.0)  # the greybox path, from the wall-gate to the plaza
GB_DOOR_Z = -12.0
SPREAD_DEG = 60.0
GB_HALF_W = 22.0


def _local(name: str, x: float, y: float, z: float) -> tuple[np.ndarray, float] | None:
    """A greybox point inside the spire, in the spire's frame (point, the spire angle it stands at), or None."""
    if name.startswith(("Key_", "key_")):
        key = name.split("_", 1)[1]
        a = KEY_ANGLES[key]
        fy = TIER_FLOOR[key.split("_")[0]]
        back = 0.3 if name.startswith("Key_") else 0.9
        return spire_point(a, float(cs.inner_r(fy + 1.25)) - back, fy + (y if name.startswith("Key_") else 0.0)), a
    for tier, z0, z1 in GB_BANDS:
        if z1 <= z <= z0:
            frac = (z0 - z) / (z0 - z1)
            u = max(-1.0, min(1.0, x / GB_HALF_W))
            if tier == "t1":
                a, fy, r = 15.0 + u * 90.0, cs.TIER_Y[0], float(cs.inner_r(0.0)) * (0.25 + 0.55 * frac)
            elif tier == "crown":
                a, fy, r = 54.0 + u * SPREAD_DEG, cs.CROWN_Y, float(cs.inner_r(cs.CROWN_Y)) * (0.2 + 0.5 * frac)
            else:
                ln = LANDINGS[int(tier[1]) - 2]
                ri = float(cs.inner_r(ln.y))
                a, fy, r = ln.centre + u * SPREAD_DEG, ln.y, ri * (0.45 + 0.4 * frac)
            return spire_point(a, r, fy + y), a
    if z < GB_BANDS[-1][2]:  # the gallery ring, outside at 42.6 m
        a = cs.gallery_door_a() + max(-1.0, min(1.0, x / GB_HALF_W)) * SPREAD_DEG
        return spire_point(a, float(cs.outer_r(cs.GALLERY_Y)) + 0.7, cs.GALLERY_Y + y), a
    return None


def to_kit(name: str, x: float, y: float, z: float, yaw: float) -> tuple[list[float], float]:
    """A greybox point (and its facing) in Corrow's world: the path, the forecourt, or inside the spire."""
    inside = _local(name, x, y, z)
    if inside is not None:
        p, a = inside
        return world(p), yaw + cpl.wall_yaw(a, inward=True) - cpl.YAW
    if z >= GB_PATH_Z[1]:  # the path
        total = float(cs.PATH.s[-1])
        s = (GB_PATH_Z[0] - min(z, GB_PATH_Z[0])) / (GB_PATH_Z[0] - GB_PATH_Z[1]) * total
        p, py, t = cs.PATH.at(s)
        n = np.array([-t[1], t[0]])
        q = p + n * max(-1.0, min(1.0, x * 0.3))
        w = cs.world_from_headland(q[0], py + y, q[1])
        return [r3(v) for v in w], yaw + math.degrees(math.atan2(-t[0], -t[1])) + cpl.YAW
    # the forecourt: greybox +z (toward the path) is out of the door, +x along the spire's face
    d, tang = cs.dir_of(cs.DOOR_A), cs.dir_of(cs.DOOR_A + 90.0)
    p = d * (float(cs.outer_r(0.0)) + 0.8 + (z - GB_DOOR_Z) * 0.6) + tang * (x * 0.6)
    return world(p + np.array([0.0, cs.FORECOURT_DY + y, 0.0])), yaw + cpl.wall_yaw(cs.DOOR_A, inward=True) - cpl.YAW


SPECIAL = {  # (spire angle, radius, height) in the spire's frame
    "SpireBase": (cs.DOOR_A, 2.6, 0.0), "hearth": (cs.HEARTH_A, float(cs.outer_r(0.0)) + 1.4, cs.FORECOURT_DY),
    "Gallery": (cs.gallery_door_a(), float(cs.outer_r(cs.GALLERY_Y)) + 0.8, cs.GALLERY_Y),
    "great_key": (cpl.GREAT_KEY[1], float(cs.outer_r(cs.GALLERY_Y)) + 1.0, cs.GALLERY_Y),
}
GEOMETRY = {"Ground", "BoundW", "BoundE", "BoundS", "BoundN", "Path", "ScrubW", "ScrubE", "Plaza", "Hut", "Hearth",
            "SpireS_W", "SpireS_E", "SpireW", "SpireE", "FluesW", "FluesE", "CrownFloor", "GalleryRail",
            "Gate_t1", "Gate_t2", "Gate_t3", "Gate_t4", "Beacon"}


def relayout() -> None:
    from ch08_corrow_relayout import dump
    g = json.loads(LAYOUT.read_text(encoding="utf-8"))

    def place(name: str, p: list) -> tuple[list[float], float]:
        if name in SPECIAL:
            a, r, y = SPECIAL[name]
            return world(spire_point(a, r, y)), cpl.wall_yaw(a, inward=False) - cpl.YAW
        if name in ("PathFoot", "PathMid"):
            s = 1.5 if name == "PathFoot" else float(cs.PATH.s[-1]) * 0.5
            q, py, t = cs.PATH.at(s)
            return [r3(v) for v in cs.world_from_headland(q[0], py, q[1])], math.degrees(math.atan2(-t[0], -t[1])) + cpl.YAW
        return to_kit(name, p[0], p[1], p[2], p[3] if len(p) > 3 else 0.0)

    def m(name: str, p: list) -> list:
        w, yaw = place(name, p)
        return w + [round(yaw % 360.0, 2)] if len(p) > 3 else w

    blocks = []
    for b in g["blocks"]:
        if b["id"] in GEOMETRY:
            continue
        w, _yaw = place(b["id"], [b["pos"][0], b["pos"][1] - b["size"][1] * 0.5, b["pos"][2]])
        row = dict(b, pos=[w[0], r3(w[1] + b["size"][1] * 0.5), w[2]])
        if b["id"] == "StormWall":
            x, y, z = cs.world_from_spire(*(cs.dir_of(70.0) * 400.0 + np.array([0.0, 20.0, 0.0])))
            row.update(pos=[r3(x), r3(y), r3(z)], yaw=r3(cpl.wall_yaw(70.0, inward=False)))
        if b["id"] == "GreatKey":
            gk = [p for p in cpl.keys() if p.get("tag") == "great_key"][0]
            row.update(pos=[gk["at"][0], r3(gk["y"]), gk["at"][1]], solid=False)
        if b["id"].startswith("Key_"):
            row["yaw"] = r3(cpl.wall_yaw(KEY_ANGLES[b["id"][4:]], inward=True))
        if b["id"] in ("NicheSeal", "Niche"):
            a = KEY_ANGLES["t2_side"] + NICHE_DA
            row["pos"] = world(spire_point(a, float(cs.inner_r(cs.TIER_Y[1] + 1.5)) - (0.2 if b["id"] == "NicheSeal" else 0.05),
                                           cs.TIER_Y[1] + 1.5))
            row["yaw"] = r3(cpl.wall_yaw(a, inward=True))
        if b["id"] == "WrightMark":
            a = KEY_ANGLES["t3_seized"] + 3.0
            row["pos"] = world(spire_point(a, float(cs.inner_r(cs.TIER_Y[2] + 1.25)) - 0.03, cs.TIER_Y[2] + 1.25))
            row["yaw"] = r3(cpl.wall_yaw(a, inward=True))
        if b["id"].startswith("Flame_") or b["id"] == "HearthFlame":
            tier = 1 if b["id"] == "HearthFlame" else int(b["id"][-1])
            br = [p for p in cpl.braziers()[0] if p["tag"] == f"tier{tier}"][0]
            row.update(pos=[br["at"][0], r3(br["y"] + 0.6), br["at"][1]], solid=False)
            if b["id"] == "HearthFlame":
                row["pos"] = world(spire_point(cs.HEARTH_A, float(cs.inner_r(0.0)), 0.5))
        blocks.append(row)
    g["blocks"] = blocks
    g["spawns"] = {k: m(k, v) for k, v in g["spawns"].items()}
    g["marks"] = {k: m(k, v) for k, v in g["marks"].items()}
    g["actors"] = {k: dict(v, at=m(k, v["at"])) for k, v in g["actors"].items()}
    g["shots"] = {k: dict(v, pos=place(k, v["pos"])[0], look_at=place(k, v["look_at"])[0]) for k, v in g["shots"].items()}
    for t in g["triggers"]:
        w, yaw = place(t["id"], t["at"])
        t["at"] = w
        t["yaw"] = r3(yaw)
    g["collision_path"] = RES_ZONE + "coilspire_collision.json"
    LAYOUT.write_text(dump(g), encoding="utf-8")


def copy_grades() -> None:
    import re
    import shutil
    for name in ("coilspire_ch08_environment.tres", "coilspire_int_environment.tres"):
        text = (PREVIEW / name).read_text(encoding="utf-8").replace("res://game/levels/_tests/coilspire_kit/", RES_ZONE)
        text = text.replace("res://game/levels/_tests/corrow_kit/", "res://game/levels/ch08/corrow/")
        (ZONE / name).write_text(text, encoding="utf-8")
    lut = "lut_ch08_coilspire_int.png"
    shutil.copyfile(PREVIEW / lut, ZONE / lut)
    if not (ZONE / f"{lut}.import").exists():
        imp = re.sub(r"^(uid|path|dest_files)=.*\n", "", (PREVIEW / f"{lut}.import").read_text(encoding="utf-8"),
                     flags=re.M)
        (ZONE / f"{lut}.import").write_text(imp.replace("res://game/levels/_tests/coilspire_kit/", RES_ZONE),
                                            encoding="utf-8")


def main() -> None:
    copy_grades()
    write_inner_material()
    for name, params in KIT_LOOKS.values():
        (ZONE / name).write_text(zl.bronze_material(name, params), encoding="utf-8")
    if "--relayout" in sys.argv:
        relayout()
    (ZONE / "coilspire_collision.json").write_text(json.dumps(collision(), indent=1) + "\n", encoding="utf-8")
    (ZONE / "coilspire_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
