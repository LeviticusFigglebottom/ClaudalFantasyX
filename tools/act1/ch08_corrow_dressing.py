#!/usr/bin/env python3
"""Ch8 Corrow: env-art's seawall kit (M3-ENV-04, 04B) dressing ch08/corrow, and the collision the kit's heights need
(M3-C08-1202, ADR 0200). The zone's frame is the kit's (tools/act1/corrow_frame.py).

Writes, next to the zone (game/levels/ch08/corrow/):
  corrow_dressing.json   ZoneKitDressing's layout: the wall, its Watchers and reliefs, the Fisher Stair and Liss's
                         hoist, the low town's ground and houses (houses that would cover the story's lanes, marks
                         or the Bastion are left out), the far ground and the Coilspire headland, the stair breach
                         (M3-ENV-04B: its pieces follow the Breach block, the intact ones WallSection).
  corrow_collision.json  Ch04Zone's "collision_path": the wall's body, kerb and parapet per 12 m segment (the gap
                         segment is WallSection, which the fall hides), the town's floor, the Bastion's platform, the
                         stair's flights as ramps, the mole's pier and ramp, and the bounds.
and copies the kit preview's grades (ch08, fallen) and water look beside them, since shipped scenes never load
game/levels/_tests/. Re-run after the kit's generators change:

    python3 tools/act1/ch08_corrow_dressing.py
"""
from __future__ import annotations

import json
import math
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corrow_frame as cf  # noqa: E402

cwl = cf.cwl
ZONE = cf.ROOT / "game" / "levels" / "ch08" / "corrow"
PREVIEW = cf.ROOT / "game" / "levels" / "_tests" / "corrow_kit"
RES_ZONE = "res://game/levels/ch08/corrow/"
SEGMENTS = range(-10, 4)  # the zone's wall: s -114 .. +42 (the dressing runs on into the headland)
GAP_K = -3  # the stair breach's gap segment (s -36 .. -24)
BREACH_KS = (-4, -3, -2)
MOLE_GAP_S = (13.0, 17.0)  # no Watchers' heads where the mole's ramp crosses the parapet
HEAD_GAP_S = (-18.4, -14.2)  # the kerb opens onto the stair's head landing
BASTION_S = (-100.0, -58.0)
BASTION_Z = (-2.5, -27.0)  # inner overlaps the walk (no crack at the curve); outer is its revetment's parapet edge
WALL_Z = (-3.9, 4.2)  # the body, inner face to the parapet's sea edge (the sea batter is art: the mole climbs it)
KERB_Z = (cf.cw.KERB[0], cf.cw.KERB[1])
PARAPET_Z = (cf.cw.PARAPET[0], cf.cw.PARAPET[1])
PARAPET_TOP = 14.5  # the parapet and the Watchers' heads: nobody climbs them
TOWN = (-118.0, 8.0, -70.0)  # the town floor: x from, x to, z north edge (south edge is under the wall)
LAYOUT = ZONE / "corrow_layout.json"
STORY_CLEAR_M = 4.5  # no house within this of a town mark, spawn or actor


def arc_box(bid: str, s0: float, s1: float, y0: float, y1: float, z0: float, z1: float, **kw) -> dict:
    sm, zm = (s0 + s1) * 0.5, (z0 + z1) * 0.5
    x, y, z, yaw = cf.arc(sm, (y0 + y1) * 0.5, zm)
    row = {"id": bid, "pos": [cf.r3(x), cf.r3(y), cf.r3(z)], "size": [cf.r3(abs(s1 - s0)), cf.r3(y1 - y0),
           cf.r3(abs(z1 - z0))], "yaw": cf.yaw_norm(yaw)}
    row.update(kw)
    return row


def arc_ramp(rid: str, s0: float, y0: float, z0: float, s1: float, y1: float, z1: float, width: float) -> dict:
    a = cf.arc(s0, y0, z0)
    b = cf.arc(s1, y1, z1)
    return {"id": rid, "from": [cf.r3(a[0]), cf.r3(a[1]), cf.r3(a[2])], "to": [cf.r3(b[0]), cf.r3(b[1]), cf.r3(b[2])],
            "width": width}


def split(s0: float, s1: float, gaps: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """[s0, s1] less the gaps."""
    out = [(s0, s1)]
    for g0, g1 in gaps:
        nxt = []
        for a, b in out:
            if b <= g0 or a >= g1:
                nxt.append((a, b))
                continue
            if a < g0:
                nxt.append((a, g0))
            if b > g1:
                nxt.append((g1, b))
        out = nxt
    return out


def wall_collision() -> list[dict]:
    rows = []
    for k in SEGMENTS:
        s = 6.0 + 12.0 * k
        s0, s1 = s - 6.0, s + 6.0
        gap = k == GAP_K
        rows.append(arc_box("WallSection" if gap else f"Wall{k:+d}", s0, s1, -1.0, cf.WALK_Y, *WALL_Z))
        for i, (a, b) in enumerate(split(s0, s1, [MOLE_GAP_S])):
            rows.append(arc_box("WallSectionParapet" if gap else f"Parapet{k:+d}{'ab'[i]}", a, b, cf.WALK_Y,
                                PARAPET_TOP, *PARAPET_Z))
        for i, (a, b) in enumerate(split(s0, s1, [HEAD_GAP_S, BASTION_S])):
            rows.append(arc_box("WallSectionKerb" if gap else f"Kerb{k:+d}{'ab'[i]}", a, b, cf.WALK_Y,
                                cf.WALK_Y + cf.cw.KERB[2], *KERB_Z))
    s_west, s_east = 6.0 + 12.0 * SEGMENTS[0] - 6.0, 6.0 + 12.0 * SEGMENTS[-1] + 6.0
    rows.append(arc_box("WalkEndW", s_west - 1.0, s_west, cf.WALK_Y, PARAPET_TOP, -4.0, 7.2))
    rows.append(arc_box("WalkEndE", s_east - 2.0, s_east, cf.WALK_Y, PARAPET_TOP, -4.0, 7.2))
    # the story's three "WallSection" dressing hooks the fall hides (WatchersSection, PaleBlocks: no collision)
    rows.append(arc_box("WatchersSection", -36.0, -24.0, cf.HEAD_Y, cf.HEAD_Y + 2.4, *PARAPET_Z, solid=False))
    rows.append(arc_box("PaleBlocks", -36.0, -24.0, 1.0, cf.WALK_Y, -3.9, -3.7, solid=False))
    return rows


def town_collision() -> list[dict]:
    x0, x1, zn = TOWN
    zs = 12.0
    rows = [{"id": "TownFloor", "pos": [(x0 + x1) * 0.5, cf.TOWN_Y - 0.5, (zn + zs) * 0.5],
             "size": [x1 - x0, 1.0, zs - zn]}]
    rows.append({"id": "TownBoundN", "pos": [(x0 + x1) * 0.5, 3.0, zn - 0.5], "size": [x1 - x0, 6.0, 1.0]})
    rows.append({"id": "TownBoundW", "pos": [x0 - 0.5, 3.0, (zn + zs) * 0.5], "size": [1.0, 6.0, zs - zn]})
    rows.append({"id": "TownBoundE", "pos": [x1 + 0.5, 3.0, (zn + zs) * 0.5], "size": [1.0, 6.0, zs - zn]})
    return rows


def bastion_collision() -> list[dict]:
    """The platform at walk height, and its revetments' parapet courses as rims (on the town side and both ends)."""
    s0, s1 = BASTION_S
    zi, zo = BASTION_Z
    par = cf.cw.PARAPET[1] - cf.cw.PARAPET[0]
    top = cf.WALK_Y + cf.cw.PARAPET[2]
    return [arc_box("BastionPlatform", s0, s1, cf.TOWN_Y, cf.WALK_Y, zo, zi),
            arc_box("BastionRimN", s0, s1, cf.WALK_Y, top, zo, zo + par),
            arc_box("BastionRimE", s1 - par, s1, cf.WALK_Y, top, zo, zi - 1.0),
            arc_box("BastionRimW", s0, s0 + par, cf.WALK_Y, top, zo, zi - 1.0)]


def bastion_pieces() -> list[dict]:
    """The Bastion dressed from the kit: seawall segments turned outward as its revetments (their parapet course on
    the platform's edge, their Watcher-faced sea face to the town), and town ground cells on its top."""
    s0, s1 = BASTION_S
    zi, zo = BASTION_Z
    out = []

    def seg(s: float, zl: float, dyaw: float) -> dict:
        x, _y, z, a = cf.arc(s, 0.0, zl)
        return {"piece": "seawall_curve", "at": [cf.r3(x), cf.r3(z)], "y": 0.0, "yaw_deg": cf.yaw_norm(a + dyaw)}

    edge = cf.cw.PARAPET[1]  # the parapet's outer edge, local z
    for sc in (s0 + 6.0, s0 + 18.0, s0 + 30.0, s1 - 6.0):
        out.append(seg(sc, zo + edge, 180.0))  # the town side: local +z faces inland
    for zc in (zi - 6.0, zo + 6.0):  # two 12 m segments from the walk's edge to the town-side edge
        out.append(seg(s1 - edge, zc, 90.0))  # the east end faces +s
        out.append(seg(s0 + edge, zc, -90.0))  # the west end faces -s
    for sc in (s0 + 12.0, s1 - 12.0):
        x, _y, z, a = cf.arc(sc, 0.0, (zi + zo) * 0.5)
        out.append({"piece": "lowtown_ground", "at": [cf.r3(x), cf.r3(z)], "y": cf.WALK_Y + 0.02,
                    "yaw_deg": cf.yaw_norm(a)})
    return out


def stair_ramps() -> list[dict]:
    st = cf.STAIR_S
    land, head = cf.LANDING, cf.HEAD_LANDING
    u12 = 12 * cf.cw_stair.GOING_M  # the broken stair stands to its 12th step

    def r(rid: str, u0: float, u1: float, width: float = 3.0) -> dict:
        y0, y1 = cf.stair_y(u0), cf.stair_y(u1 - 1e-6) if u1 > u0 else cf.stair_y(u1)
        return arc_ramp(rid, st + u0, y0, cf.stair_z(y0), st + u1, y1, cf.stair_z(y1), width)

    rows = [r("StairFoot", 0.0, u12), r("StairFlight1Upper", u12, land[0]), r("StairLanding", land[0], land[1]),
            r("StairFlight2", land[1], head[0])]
    hz = (cf.cw.KERB[1] + cf.inner_z(cf.STAIR_TOP_Y) - 3.2) * 0.5
    rows.append(arc_ramp("StairHeadLanding", st + head[0], cf.STAIR_TOP_Y, hz, st + head[1], cf.STAIR_TOP_Y, hz, 3.8))
    sm = st + (head[0] + head[1]) * 0.5
    rows.append(arc_ramp("StairApproach", sm, cf.WALK_Y, 0.6, sm, cf.STAIR_TOP_Y, cf.cw.KERB[1], 3.4))
    return rows


def mole() -> tuple[list[dict], list[dict]]:
    s = cf.MOLE_S
    p0, p1 = cf.PIER_Z
    blocks = [arc_box("MolePier", s - 2.2, s + 2.2, -2.0, cf.PIER_Y, p0, p1, color="#7d746a"),
              arc_box("MoleRailW", s - 2.7, s - 2.2, -2.0, cf.HEAD_Y + 1.5, cf.RAMP_TOP_Z, p1, solid=True),
              arc_box("MoleRailE", s + 2.2, s + 2.7, -2.0, cf.HEAD_Y + 1.5, cf.RAMP_TOP_Z, p1, solid=True),
              arc_box("MoleEnd", s - 2.7, s + 2.7, -2.0, 4.0, p1, p1 + 0.5)]
    ramps = [arc_ramp("MoleRamp", s, cf.PIER_Y, p0, s, cf.HEAD_Y, cf.RAMP_TOP_Z, 4.0),
             arc_ramp("MoleOverParapet", s, cf.HEAD_Y, cf.RAMP_TOP_Z, s, cf.HEAD_Y, cf.cw.PARAPET[0], 4.0),
             arc_ramp("MoleDown", s, cf.HEAD_Y, cf.cw.PARAPET[0], s, cf.WALK_Y, 1.0, 4.0)]
    return blocks, ramps


def collision() -> dict:
    blocks = wall_collision() + town_collision() + bastion_collision()
    mb, mr = mole()
    return {"_about": "Generated by tools/act1/ch08_corrow_dressing.py (ADR 0200); do not edit by hand. Ch04Zone's "
            "collision_path: blocks and ramps in the Corrow kit's frame.", "blocks": blocks + mb,
            "ramps": stair_ramps() + mr}


# --- dressing ----------------------------------------------------------------------------------------------------

def story_points() -> list[tuple[float, float]]:
    """Every town-level mark, spawn and actor of the zone's layout (houses keep clear of them)."""
    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    pts = list(g["marks"].values()) + list(g["spawns"].values()) + [a["at"] for a in g["actors"].values()]
    pts += [t["at"] for t in g["triggers"]]
    pts += [b["pos"] for b in g["blocks"] if b["id"] in ("NetRacks", "MarraStep")]
    return [(p[0], p[2]) for p in pts if p[1] < cf.TOWN_Y + 2.5]


def in_bastion(x: float, z: float, pad: float) -> bool:
    for s in (BASTION_S[0] - pad, (BASTION_S[0] + BASTION_S[1]) * 0.5, BASTION_S[1] + pad):
        bx, _y, bz, _a = cf.arc(s, 0.0, (BASTION_Z[0] + BASTION_Z[1]) * 0.5)
        if abs(x - bx) < 22.0 + pad and abs(z - bz) < 14.0 + pad:
            return True
    return False


def near_stair(x: float, z: float) -> bool:
    for u in (0.0, 6.0, 12.0, 18.0, 24.0):
        sx, _y, sz, _a = cf.arc(cf.STAIR_S + u, 0.0, cf.stair_z(cf.TOWN_Y))
        if math.hypot(x - sx, z - sz) < 7.0:
            return True
    return False


def town_pieces() -> list[dict]:
    pts = story_points()
    out = []
    for d in cwl.town():
        x, z = d["at"]
        if d["piece"] == "lowtown_ground":
            out.append(d)
            continue
        if in_bastion(x, z, 4.0) or near_stair(x, z):
            continue
        if any(math.hypot(x - px, z - pz) < STORY_CLEAR_M + 3.5 for px, pz in pts):
            continue
        out.append(dict(d, collide=True))
    return out


def wall_pieces() -> list[dict]:
    out = []
    for k in cwl.SEGMENTS:
        s = 6.0 + 12.0 * k
        breach = k in BREACH_KS
        out.append(cwl.put_arc("seawall_curve", s, **({"block": "WallSection"} if breach else {})))
        out.append(cwl.put_arc("wall_apron", s))
        for dh in (-4.5, -1.5, 1.5, 4.5):
            sh = s + dh
            if MOLE_GAP_S[0] <= sh <= MOLE_GAP_S[1]:
                continue
            row = cwl.put_arc("watcher_head", sh, cwl.HEAD_Y, cwl.HEAD_Z)
            cracked = (k, dh) in ((-4, 4.5), (-2, -4.5))
            if k == GAP_K or cracked:
                row["block"] = "WatchersSection"
            out.append(row)
            if cracked:
                out.append(dict(cwl.put_arc("watcher_head_cracked", sh, cwl.HEAD_Y, cwl.HEAD_Z), block="Breach"))
        for ds, y0 in cwl.RELIEF_ROWS:
            row = cwl.put_arc("watcher_relief", s + ds, y0, float(cf.cw_wall.sea_z(y0)))
            torn = k == GAP_K or (k == -4 and ds > 0) or (k == -2 and ds < 0)
            if torn:
                row["block"] = "WallSection"
            out.append(row)
    return out


def breach_pieces() -> list[dict]:
    """The stair breach (M3-ENV-04B): its ends and gap, the fallen heads, the broken stair, the cut hoist and the
    stair lane's rubble; all follow the Breach block (shown when the wall falls)."""
    out = []
    for piece, k in cwl.BREACHES[0]:
        out.append(dict(cwl.put_arc(piece, 6.0 + 12.0 * k), block="Breach"))
    for s, z, dyaw, where in cwl.FALLEN:
        if not -40.0 <= s <= -20.0:
            continue
        y = float(cwl.cw_breach.floor_base(cwl.np.array(z))) if where == "floor" else (
            cf.TOWN_Y if where == "town" else 0.9)
        d = cwl.put_arc("watcher_head_fallen", s, y, z)
        d["yaw_deg"] = round(d["yaw_deg"] + dyaw, 3)
        out.append(dict(d, block="Breach"))
    out.append(dict(cwl.put_arc("fisher_stair_broken", cf.STAIR_S), block="Breach"))
    foot_x, _y, foot_z, _yaw = cwl.arc_pose(cf.STAIR_S, 0.0, -cf.cw_stair.WIDTH_M - 4.0)
    out.append({"piece": "lowtown_rubble", "at": [cf.r3(foot_x - 1.0), cf.r3(foot_z - cwl.cw_breach.RUBBLE_HALF + 4.0)],
                "y": cf.TOWN_Y, "yaw_deg": 0.0, "block": "Breach"})
    return out


def stand_ins() -> list[dict]:
    """Kit stand-ins on story blocks until M3-ENV-1203's pieces: the chandler's stall is crates."""
    blocks = {r["id"]: r for r in json.loads(LAYOUT.read_text(encoding="utf-8"))["blocks"]}
    b = blocks["Chandler"]
    return [{"piece": "crate_stack", "kit_dir": "res://assets/environments/kits/brine_shoals/",
             "at": [b["pos"][0], b["pos"][2]], "y": cf.WALK_Y, "yaw_deg": b["yaw"], "block": "Chandler"}]


def trader() -> list[dict]:
    """The trader the party comes in on (B01), on the Trader block: the Brightwater ferry kit's hull, rig and cargo at
    half scale, no name board (a coaster, not the ferry). A stand-in until a trader is built (M3-ENV-1203)."""
    b = next(r for r in json.loads(LAYOUT.read_text(encoding="utf-8"))["blocks"] if r["id"] == "Trader")
    kit = "res://assets/environments/kits/brightwater_ferry/"
    return [{"piece": piece, "kit_dir": kit, "at": [b["pos"][0], b["pos"][2]], "y": cf.SEA_Y, "yaw_deg": b["yaw"],
             "scale": 0.5, "block": "Trader"} for piece in ("ferry_hull", "ferry_rig", "ferry_cargo")]


def dressing() -> dict:
    head, _beacon = cwl.headland()
    pieces = [{"piece": "corrow_far", "at": [0.0, 0.0], "y": 0.0, "yaw_deg": 0.0, "lod1_from_m": 5000.0}] + head
    pieces += wall_pieces()
    pieces.append(dict(cwl.put_arc("fisher_stair", cf.STAIR_S), block="StairFlight2"))
    pieces.append(dict(cwl.put_arc("liss_hoist", cf.HOIST_S, cwl.HEAD_Y, cwl.HEAD_Z), block="HoistRope"))
    pieces.append(dict(cwl.put_arc("liss_hoist_cut", cf.HOIST_S, cwl.HEAD_Y, cwl.HEAD_Z), block="RopeCoil"))
    pieces += breach_pieces()
    pieces += town_pieces()
    pieces += bastion_pieces()
    for bid, piece, ds, dz in (("Barracks", "lowtown_house_a", -3.4, 0.0), ("Barracks", "lowtown_house_b", 3.2, 0.0),
                               ("Chapel", "lowtown_house_b", 0.0, 0.0)):
        b = next(r for r in json.loads(LAYOUT.read_text(encoding="utf-8"))["blocks"] if r["id"] == bid)
        yaw = math.radians(b["yaw"])
        x = b["pos"][0] + ds * math.cos(yaw) + dz * math.sin(yaw)
        z = b["pos"][2] - ds * math.sin(yaw) + dz * math.cos(yaw)
        pieces.append({"piece": piece, "at": [cf.r3(x), cf.r3(z)], "y": cf.WALK_Y, "yaw_deg": cf.yaw_norm(b["yaw"] + 90.0),
                       "block": bid})
    pieces += trader()
    pieces += stand_ins()
    preview = json.loads((PREVIEW / "corrow_layout.json").read_text(encoding="utf-8"))
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act1/ch08_corrow_dressing.py from env-art's Corrow kit (M3-ENV-04, 04B); do not "
        "edit by hand. The kit's own frame (tools/act1/corrow_frame.py).",
        "seed": 8,
        "kit_dir": "res://assets/environments/kits/corrow/",
        "materials_dir": "res://assets/environments/kits/corrow/materials/",
        "lod1_from_m": float(preview.get("lod1_from_m", 70.0)),
        "lod_end_m": float(preview.get("lod_end_m", 4000.0)),
        "lod_margin_m": float(preview.get("lod_margin_m", 2.0)),
        "environment": RES_ZONE + "corrow_ch08_environment.tres",
        "time_of_day_h": 16.0,
        "greybox": {"hide_all": True, "keep": ["NetRacks", "MarraStep", "HoistPins", "HoistRope",
                                               "Basket", "RopeCoil", "Flood", "Lake", "Shrine",
                                               "WallGate", "MolePier", "MoleRamp",
                                               "MoleOverParapet", "MoleDown"]},
        "fire_light_color": preview.get("fire_light_color", "#E0702E"),
        "fire_lights": [{"at": f[:3], "energy": f[3], "range": f[4]} for f in preview.get("fire_lights", [])],
        "pieces": pieces,
    }


def copy_grades() -> None:
    for name in ("corrow_ch08_environment.tres", "corrow_fallen_environment.tres", "corrow_ch09_environment.tres",
                 "corrow_water_material.tres"):
        text = (PREVIEW / name).read_text(encoding="utf-8").replace("res://game/levels/_tests/corrow_kit/", RES_ZONE)
        text = re.sub(r' uid="uid://[a-z0-9]+"(?= path="res://game/levels/ch08/)', "", text)
        (ZONE / name).write_text(text, encoding="utf-8")
    for lut in ("lut_ch08_storm.png", "lut_ch09_ebbing.png"):
        shutil.copyfile(PREVIEW / lut, ZONE / lut)
        if (ZONE / f"{lut}.import").exists():
            continue  # Godot owns the copy's import file once it has imported it (its uid and cache path)
        imp = (PREVIEW / f"{lut}.import").read_text(encoding="utf-8")
        imp = re.sub(r"^(uid|path|dest_files)=.*\n", "", imp, flags=re.M)
        (ZONE / f"{lut}.import").write_text(imp.replace("res://game/levels/_tests/corrow_kit/", RES_ZONE),
                                            encoding="utf-8")


def main() -> None:
    (ZONE / "corrow_collision.json").write_text(json.dumps(collision(), indent=1) + "\n", encoding="utf-8")
    (ZONE / "corrow_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")
    copy_grades()


if __name__ == "__main__":
    main()
