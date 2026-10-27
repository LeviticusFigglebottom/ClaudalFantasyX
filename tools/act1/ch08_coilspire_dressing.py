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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "coilspire"
sys.path.insert(0, str(KIT_SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))
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
VERGE_M = 1.6  # the path's verges, out from its edge
PATH_STEP_M = 3.0
# The trial's keys (game/data/flow/ch08_field.json) on the kit's flue-keys: the kit's angle where it has one,
# else a free angle on the same landing's arc (deg). The side flue's niche stands beside its key.
KEY_ANGLES = {"t1_a": 0.0, "t1_b": 88.0, "t1_c": 240.0, "t2_a": 204.0, "t2_b": 260.0, "t2_c": 285.0,
              "t2_side": 180.0, "t3_a": 106.0, "t3_seized": 188.0, "t3_b": 140.0, "t4_a": 291.0, "t4_b": 17.0,
              "t4_c": 320.0, "t4_d": 40.0}
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
        half = math.sqrt(max(r * r - (cs.LANDING_CHORD * r) ** 2, 0.0))
        p = world(c + np.array([0.0, ln.y + 0.5, 0.0]))
        out.append({"id": f"WellGuard_t{ln.tier}", "pos": p, "size": [r3(2 * half), 1.0, 0.25],
                    "yaw": cpl.wall_yaw(ln.centre, inward=True)})
    return out


def collision() -> dict:
    pr, pv = path_ramps_and_verges()
    return {"_about": "Generated by tools/act1/ch08_coilspire_dressing.py (ADR 0200); do not edit by hand. The kit's "
            "trimesh is in the dressing (collide: trimesh); these are the ramps, gates, verges and guards.",
            "blocks": gates() + pv + well_guards(), "ramps": flight_ramps() + pr}


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
        if p["piece"] in ("coilspire_shell", "coilspire_tiers", "coilspire_ground", "keepers_hut"):
            pieces.append(dict(p, collide="trimesh"))
            continue
        pieces.append(p)
    pieces += key_pieces()
    backdrop = json.loads((PREVIEW / "coilspire_backdrop.json").read_text(encoding="utf-8"))
    corrow = "res://assets/environments/kits/corrow/"
    for p in backdrop.get("pieces", []):
        pieces.append(dict(p, kit_dir=corrow))
    lights = [{"at": l[:3], "energy": l[3], "range": l[4]} for l in preview.get("hearth_lights", [])]
    for i, light in enumerate(lights[:4]):  # the tier braziers' lights burn with their braziers (Flame_t1-t4)
        light["block"] = f"Flame_t{i + 1}"
    lights += [{"at": l[:3], "energy": l[3], "range": l[4]} for l in preview.get("fire_lights", [])]
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
        "greybox": {"hide_all": True, "keep": ["Gate_t1", "Gate_t2", "Gate_t3", "Gate_t4", "NicheSeal", "WrightMark",
                                               "Virel", "StormWall"]},
        "fire_light_color": preview.get("hearth_light_color", "#FFB16E"),
        "fire_lights": lights,
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
    if "--relayout" in sys.argv:
        relayout()
    (ZONE / "coilspire_collision.json").write_text(json.dumps(collision(), indent=1) + "\n", encoding="utf-8")
    (ZONE / "coilspire_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
