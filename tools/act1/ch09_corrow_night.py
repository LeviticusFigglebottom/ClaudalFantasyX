#!/usr/bin/env python3
"""Ch9 'The Ebbing': ch09/corrow_night on the Corrow kit, the night after the wall fell (M3-C09-1209, ADR 0200).

The zone shares Ch8's frame (tools/act1/corrow_frame.py) and the kit's fallen state (M3-ENV-04B): the stair breach
open (s -36 .. -24), the broken stair, the cut hoist, the lake in the low town. Ch9's own ground:
  - the strand of the drowned: shingle banks (the Brine Shoals kit's `camp_hard`, sunk) along the wall's sea foot
    either side of the breach, s -69 .. +1, wall-frame z 19 .. 30, top y 0.6, the ebb's water at y -0.55;
  - the landing out from the strand's middle (s -30) and the raft mid-harbour; the harbour floor 1.1 m down;
  - a bridge from the strand's east end to Ch8's mole (s 15), whose ramp climbs to the walk: Liss on her cut rope at
    the hoist (s -16.5) and the coast road (the walk east of the wall-gate, s 36 .. 100, the milestone at s 65);
  - the rocks Pell comes down at the strand's east end (s 2 .. 10), fallen Watchers' heads on them;
  - Iskarra's plaza, a separate set far east (greybox x + ISKARRA_DX), for the cut inside one scene.
Derived from Ch8's generated files (re-run tools/act1/ch08_corrow_dressing.py first):

    python3 tools/act1/ch09_corrow_night.py [--relayout]

--relayout moves the greybox layout's story points into the frame once (see relayout()).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ch08_corrow_dressing as c8  # noqa: E402
import corrow_frame as cf  # noqa: E402

ROOT = cf.ROOT
ZONE = ROOT / "game" / "levels" / "ch09" / "corrow_night"
LAYOUT = ZONE / "corrow_night_layout.json"
C8 = ROOT / "game" / "levels" / "ch08" / "corrow"
RES_C8 = "res://game/levels/ch08/corrow/"
BRINE = "res://assets/environments/kits/brine_shoals/"
BREACH_S = -30.0  # greybox x 0, the breach
STRAND_S = (-69.0, 1.0)
STRAND_Z = (19.0, 30.0)
STRAND_Y = 0.6
WATER_Y = -0.55
HARBOUR_Y = -0.7  # the harbour floor's top, just under the ebb's water ("no swimming")
LAKE_Y = 3.5  # the low town drowned to the eaves (the houses are 4 m)
ROAD_S = (36.0, 100.0)
ROCKS_S = (2.0, 10.0)
ROCKS_PATH = (2.0, 4.0, 22.4)  # the path down the rocks' west face: its top (s, y, wall-frame z)
ROCKS_PATH_RUN_M = 5.8  # its run west (about 30 deg)
ROCKS_COLOR = "#3e3a36"
BRIDGE_Z = 28.0  # the bridge to the mole: along the strand's south edge onto the pier's first metres
ISKARRA_DX = 1700.0
ISKARRA_SCENE = cf.ROOT / "assets/environments/zones/iskarra/iskarra_city.tscn"
ISKARRA_AT = (2000.0, -0.4, -2.0)  # env-art's city's origin in the zone: its plaza's top meets the vigil's (y 0, z 0)
# Ch8's state pieces: the intact wall, the rigged hoist and the whole stair are gone, and so are the noon's kites,
# the trader and what the flood took (Marra's step, the net racks, the hoist's basket); the breach, the cut hoist and
# its pins, the Bastion's houses, the wall-gate and the shrine on the walk always stand.
DROP_BLOCKS = {"WallSection", "WatchersSection", "StairFlight2", "HoistRope", "Trader", "Kites", "KitesHigh",
               "MarraStep", "NetRacks", "Basket"}
ALWAYS_BLOCKS = {"Breach", "RopeCoil", "Barracks", "Chapel", "Chandler", "WallGate", "HoistPins", "Shrine"}
DROP_COLLISION = {"WallSection", "WallSectionParapet", "WallSectionKerb", "StairFlight1Upper", "StairLanding",
                  "StairFlight2", "MoleRailW", "WalkEndE", "TownBoundN", "TownBoundW", "TownBoundE"}


def collision() -> dict:
    src = json.loads((C8 / "corrow_collision.json").read_text(encoding="utf-8"))
    saved = c8.SEGMENTS
    c8.SEGMENTS = range(-10, 9)  # the walk runs on east as the coast road
    walls = [b for b in c8.wall_collision() if b["id"] not in DROP_COLLISION]
    c8.SEGMENTS = saved
    wall_ids = {b["id"] for b in walls}
    blocks = [b for b in src["blocks"] if b["id"] not in DROP_COLLISION and b["id"] not in wall_ids]
    blocks = [b for b in blocks if not (b["id"].startswith(("Wall", "Parapet", "Kerb")) and b["id"] not in wall_ids)]
    blocks += walls
    ramps = [r for r in src["ramps"] if r["id"] not in DROP_COLLISION]
    s0, s1 = STRAND_S
    z0, z1 = STRAND_Z
    blocks += [c8.arc_box("StrandFloor", s0, s1, STRAND_Y - 1.0, STRAND_Y, z0, z1),
               c8.arc_box("StrandBoundN", s0, s1 + 12.0, STRAND_Y, STRAND_Y + 2.0, z0 - 0.5, z0),
               c8.arc_box("StrandBoundW", s0 - 0.5, s0, STRAND_Y, STRAND_Y + 2.0, z0, z1),
               c8.arc_box("StrandBoundE", s1, s1 + 0.5, STRAND_Y, STRAND_Y + 2.0, z0, BRIDGE_Z - 2.0),
               c8.arc_box("StrandBoundSW", s0, BREACH_S - 3.0, STRAND_Y, STRAND_Y + 2.0, z1, z1 + 0.5),
               c8.arc_box("StrandBoundSE", BREACH_S + 3.0, s1, STRAND_Y, STRAND_Y + 2.0, z1, z1 + 0.5),
               c8.arc_box("Harbour", -110.0, 60.0, HARBOUR_Y - 1.0, HARBOUR_Y, z1 + 0.5, 110.0)]
    # the bridge to the mole: a ramp from the strand's east end up to the pier's top, railed; the pier's west rail
    # keeps a gap where it lands
    bz = BRIDGE_Z
    pier_w = cf.MOLE_S - 2.2
    ramps.append(c8.arc_ramp("MoleBridge", s1 - 1.0, STRAND_Y, bz, pier_w + 0.3, cf.PIER_Y, bz, 4.0))
    blocks += [c8.arc_box("MoleBridgeRailN", s1, pier_w, STRAND_Y - 0.5, cf.PIER_Y + 1.0, bz - 2.5, bz - 2.0),
               c8.arc_box("MoleBridgeRailS", s1, pier_w, STRAND_Y - 0.5, cf.PIER_Y + 1.0, bz + 2.0, bz + 2.5)]
    p0, p1 = cf.PIER_Z
    blocks += [c8.arc_box("MoleRailWa", cf.MOLE_S - 2.7, pier_w, -2.0, cf.HEAD_Y + 1.5, cf.RAMP_TOP_Z, bz - 2.0),
               c8.arc_box("MoleRailWb", cf.MOLE_S - 2.7, pier_w, -2.0, cf.HEAD_Y + 1.5, bz + 2.0, p1)]
    blocks.append(c8.arc_box("RoadEnd", ROAD_S[1], ROAD_S[1] + 1.0, cf.WALK_Y, c8.PARAPET_TOP, -4.0, 7.2))
    # the path Pell comes down: off the rocks' west face to the strand (a greybox slab, kept with the Rocks)
    s_top, y_top, z = ROCKS_PATH
    ramps.append(dict(c8.arc_ramp("RocksDown", s_top, y_top, z, s_top - ROCKS_PATH_RUN_M, STRAND_Y, z, 1.2),
                      color=ROCKS_COLOR))
    return {"_about": "Generated by tools/act1/ch09_corrow_night.py from Ch8's collision (ADR 0200); do not edit by "
            "hand.", "blocks": blocks, "ramps": ramps}


def dressing() -> dict:
    src = json.loads((C8 / "corrow_dressing.json").read_text(encoding="utf-8"))
    pieces = []
    for p in src["pieces"]:
        b = p.get("block")
        if b in DROP_BLOCKS:
            continue
        if b in ALWAYS_BLOCKS:
            p = {k: v for k, v in p.items() if k != "block"}
        pieces.append(p)
    for i, s in enumerate((-62.0, -48.0, -34.0, -20.0, -6.0)):  # the strand's shingle: the cores meet
        x, _y, z, a = cf.arc(s, 0.0, sum(STRAND_Z) * 0.5 - 1.0)
        pieces.append({"piece": "camp_hard", "kit_dir": BRINE, "at": [cf.r3(x), cf.r3(z)], "y": STRAND_Y - 1.13,
                       "yaw_deg": cf.yaw_norm(a + (180.0 if i % 2 else 0.0))})
    for k, (s, zl, dyaw) in enumerate(((4.0, 17.5, 30.0), (7.0, 19.5, -70.0), (5.5, 21.5, 140.0))):
        x, _y, z, a = cf.arc(s, 0.0, zl)
        pieces.append({"piece": "watcher_head_fallen", "at": [cf.r3(x), cf.r3(z)], "y": 1.2 + 0.7 * k,
                       "yaw_deg": cf.yaw_norm(a + dyaw), "block": "Rocks"})
    pieces += strand_pieces() + iskarra_pieces() + stand_in_pieces()
    src.update(pieces=pieces, environment=RES_C8 + "corrow_ch09_environment.tres", time_of_day_h=22.0,
               _about="Generated by tools/act1/ch09_corrow_night.py from Ch8's dressing (ADR 0200); do not edit by hand.")
    # ADR 0041: no greybox left on the played path. The lake is the scene's own WaterSurface (Lake); Iskarra's water
    # lies under the sea's surface, which reaches the set.
    src["greybox"] = {"hide_all": True, "keep": []}
    src["fire_lights"] = [{"at": l["at"], "energy": l["energy"], "range": l["range"]} for l in src.get("fire_lights", [])]
    src["fire_lights"] += vigil_lights()
    return src


VIGIL_ROWS = ("ShroudRow1", "ShroudRow2", "ShroudRow3", "ShroudRow4", "StillguardRow")
VIGIL = {"step_m": 4.0, "out_m": 1.1, "y": 1.5, "energy": 0.9, "range": 8.0, "color": "#FFB46B"}


def vigil_lights() -> list[dict]:
    """The vigil lamps along the rows of the drowned, every VIGIL step_m, each going out with the nearest Lamp block
    (the dawn variant hides them): the strand reads at night by its own small fires."""
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    rows = {b["id"]: b for b in layout["blocks"]}
    lamps = [b for b in layout["blocks"] if b["id"].startswith("Lamp")]
    out = []
    for rid in VIGIL_ROWS:
        b = rows[rid]
        a = math.radians(b.get("yaw", 0.0))
        ux, uz = math.cos(a), -math.sin(a)  # the row's length (local x)
        n = int(b["size"][0] // VIGIL["step_m"])
        for i in range(n):
            u = (i + 0.5) * VIGIL["step_m"] - b["size"][0] * 0.5
            x = b["pos"][0] + ux * u + uz * VIGIL["out_m"]
            z = b["pos"][2] + uz * u - ux * VIGIL["out_m"]
            near = min(lamps, key=lambda m: (m["pos"][0] - x) ** 2 + (m["pos"][2] - z) ** 2)
            out.append({"at": [cf.r3(x), VIGIL["y"], cf.r3(z)], "energy": VIGIL["energy"], "range": VIGIL["range"],
                        "color": VIGIL["color"], "block": near["id"]})
    return out


SHROUD_PITCH_M = 2.4  # the drowned lie head to foot along each row (shroud_a/b are 2.1 m)
SHROUD_SMALL_EVERY = 5  # every fifth in a row of the town's dead is a child (shroud_small)
SHROUD_JITTER = (3.0, 0.08)  # yaw (deg) and across-row (m) jitter, so the rows were laid by hand
STILLGUARD_ROWS = ("StillguardRow",)
HALUNA = "res://assets/environments/kits/haluna/"


def _along(b: dict, u: float, v: float = 0.0) -> tuple[float, float]:
    """The point u m along block b's local x and v m along its local z (Godot's Basis(UP, yaw))."""
    a = math.radians(b.get("yaw", 0.0))
    return b["pos"][0] + math.cos(a) * u + math.sin(a) * v, b["pos"][2] - math.sin(a) * u + math.cos(a) * v


def iskarra_pieces() -> list[dict]:
    """The act break's vigil (B10) stands in env-art's Iskarra (M3-ENV-710): the pieces of its drop-in scene, each at
    its transform from the scene (yaw, the uniform horizontal scale and the vertical one) moved to ISKARRA_AT."""
    import re
    text = ISKARRA_SCENE.read_text(encoding="utf-8")
    res = dict(re.findall(r'path="res://assets/environments/kits/haluna/([a-z_]+)\.glb" id="([^"]+)"', text))
    ids = {v: k for k, v in res.items()}
    out = []
    for rid, xf in re.findall(r'instance=ExtResource\("([^"]+)"\)\]\ntransform = Transform3D\(([^)]+)\)', text):
        m = [float(v) for v in xf.split(",")]
        sh, sy = math.hypot(m[0], m[2]), m[4]
        row = {"piece": ids[rid], "kit_dir": HALUNA, "at": [cf.r3(m[9] + ISKARRA_AT[0]), cf.r3(m[11] + ISKARRA_AT[2])],
               "y": cf.r3(m[10] + ISKARRA_AT[1]), "yaw_deg": cf.r3(math.degrees(math.atan2(m[2], m[0]))),
               "block": "IskarraPlaza"}
        if abs(sh - 1.0) > 1e-3:
            row["scale"] = cf.r3(sh)
        if abs(sy - sh) > 1e-3:
            row["scale_y"] = cf.r3(sy)
        out.append(row)
    return out


def strand_pieces() -> list[dict]:
    """M3-ENV-708's pieces on Ch9's story blocks: the drowned in their rows (heads to the row's -x), the Stillguard's
    shields at their feet, a clay lamp under each vigil light and on each Lamp block, the Ebbing raft, Ivo's shroud,
    the cut hoist's coil and the dawn road's milestone. Each follows its block."""
    import random
    rng = random.Random(9)
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    rows = {b["id"]: b for b in layout["blocks"]}
    out = []
    for rid in VIGIL_ROWS:
        b = rows[rid]
        n = int(b["size"][0] // SHROUD_PITCH_M)
        for i in range(n):
            u = (i + 0.5) * SHROUD_PITCH_M - n * SHROUD_PITCH_M * 0.5
            x, z = _along(b, u, rng.uniform(-SHROUD_JITTER[1], SHROUD_JITTER[1]))
            soldier = rid in STILLGUARD_ROWS
            piece = "shroud_small" if not soldier and i % SHROUD_SMALL_EVERY == 2 else ("shroud_a", "shroud_b")[i % 2]
            out.append({"piece": piece, "at": [cf.r3(x), cf.r3(z)], "y": STRAND_Y,
                        "yaw_deg": cf.yaw_norm(b.get("yaw", 0.0) + 90.0 + rng.uniform(-SHROUD_JITTER[0], SHROUD_JITTER[0])),
                        "block": rid})
            if soldier:
                s = rows["StillguardShields"]
                sx, sz = _along(s, u)
                out.append({"piece": "round_shield", "at": [cf.r3(sx), cf.r3(sz)], "y": STRAND_Y,
                            "yaw_deg": cf.yaw_norm(rng.uniform(0.0, 360.0)), "block": "StillguardShields"})
    for light in vigil_lights():
        out.append({"piece": "strand_lamp", "at": [light["at"][0], light["at"][2]], "y": STRAND_Y, "yaw_deg": 0.0,
                    "block": light["block"]})
    for lid in ("LampA", "LampB", "LampC", "LampD"):
        b = rows[lid]
        out.append({"piece": "strand_lamp", "at": [b["pos"][0], b["pos"][2]], "y": STRAND_Y, "yaw_deg": 0.0, "block": lid})
    for bid, piece, kit in (("Raft", "ebbing_raft", ""), ("IvoShroud", "shroud_a", ""), ("HoistCoil", "rope_coil", HALUNA),
                            ("Milestone", "milestone", "")):
        b = rows[bid]
        y = b["pos"][1] if bid == "Raft" else b["pos"][1] - b["size"][1] * 0.5
        row = {"piece": piece, "at": [b["pos"][0], b["pos"][2]], "y": cf.r3(y), "yaw_deg": b.get("yaw", 0.0), "block": bid}
        if kit:
            row["kit_dir"] = kit
        out.append(row)
    return out


ORUVEL = "res://assets/environments/kits/oruvel/"
COILSPIRE = "res://assets/environments/kits/coilspire/"
DECK = ("timber_deck_2m", 2.09, 1.88)  # Haluna's decking: across (x), along (z), its top at the origin
PILE_STEP_M = 3.0  # the mole bridge's piles (Oruvel's mooring_post, 1.5 m above its origin) along each edge
BOULDER_B_TOP = 0.9  # coral_boulder_b's top above its origin (m)


def deck_run(a: tuple[float, float, float], b: tuple[float, float, float], width: float) -> list[dict]:
    """Haluna's decking laid from a to b (world x, y of the top, z), `width` across, tilted with the slope: the walk's
    own surface, so the collision under it is unchanged."""
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    run = math.hypot(dx, dz)
    yaw = math.atan2(dx, dz)
    pitch = -math.degrees(math.atan2(dy, run))
    n_along = math.ceil(run / (DECK[2] - 0.05))
    n_across = math.ceil(width / (DECK[1] - 0.05))
    scale = max(run / n_along / DECK[2], width / n_across / DECK[1], 1.0)
    out = []
    for i in range(n_along):
        t = (i + 0.5) / n_along
        for j in range(n_across):
            v = (j + 0.5) * width / n_across - width * 0.5
            x = a[0] + dx * t + math.cos(yaw) * v
            z = a[2] + dz * t - math.sin(yaw) * v
            out.append({"piece": DECK[0], "kit_dir": HALUNA, "at": [cf.r3(x), cf.r3(z)], "y": cf.r3(a[1] + dy * t),
                        "yaw_deg": cf.r3(math.degrees(yaw)), "tilt_deg": [cf.r3(pitch), 0.0], "scale": cf.r3(scale)})
    return out


def stand_in_pieces() -> list[dict]:
    """ADR 0041: the last story blocks Ch9 drew as greybox, in kit pieces (M3-ENV-1222 may replace them with bespoke
    ones): the landing and the bridge to the mole decked in Haluna's timber, the bridge on Oruvel's piles, the rocks Pell
    comes down as coral boulders with stepping stones down their path, and the vigil's burner as Coilspire's brazier."""
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    rows = {b["id"]: b for b in layout["blocks"]}
    ramps = {r["id"]: r for r in collision()["ramps"]}
    out = []
    land = rows["Landing"]
    top = land["pos"][1] + land["size"][1] * 0.5
    half = land["size"][2] * 0.5
    a, b = _along(land, 0.0, -half), _along(land, 0.0, half)
    out += [dict(p, block="Landing") for p in deck_run((a[0], top, a[1]), (b[0], top, b[1]), land["size"][0])]
    br = ramps["MoleBridge"]
    out += deck_run(tuple(br["from"]), tuple(br["to"]), br["width"])
    dx, dz = br["to"][0] - br["from"][0], br["to"][2] - br["from"][2]
    run = math.hypot(dx, dz)
    ux, uz = dx / run, dz / run
    for k in range(int(run // PILE_STEP_M) + 1):
        t = min(k * PILE_STEP_M, run) / run
        for side in (-1.0, 1.0):
            x = br["from"][0] + dx * t + uz * side * br["width"] * 0.5
            z = br["from"][2] + dz * t - ux * side * br["width"] * 0.5
            y = br["from"][1] + (br["to"][1] - br["from"][1]) * t
            out.append({"piece": "mooring_post", "kit_dir": "res://assets/environments/kits/tamsule_bell/",
                        "at": [cf.r3(x), cf.r3(z)], "y": cf.r3(y - 0.5), "yaw_deg": 0.0})
    rocks = rows["Rocks"]
    rx, rz = rocks["pos"][0], rocks["pos"][2]
    out.append({"piece": "coral_boulder_c", "kit_dir": HALUNA, "at": [rx, rz], "y": -0.12, "scale": 2.1,
                "yaw_deg": cf.r3(rocks.get("yaw", 0.0) + 90.0), "block": "Rocks"})
    ex, ez = _along(rocks, 3.2, 2.4)
    out.append({"piece": "coral_boulder_b", "kit_dir": HALUNA, "at": [cf.r3(ex), cf.r3(ez)], "y": 0.4, "scale": 1.5,
                "yaw_deg": 40.0, "block": "Rocks"})
    path = ramps["RocksDown"]
    n = 5
    for k in range(n):
        t = (k + 0.5) / n
        x = path["from"][0] + (path["to"][0] - path["from"][0]) * t
        z = path["from"][2] + (path["to"][2] - path["from"][2]) * t
        y = path["from"][1] + (path["to"][1] - path["from"][1]) * t
        out.append({"piece": "coral_boulder_b", "kit_dir": HALUNA, "at": [cf.r3(x), cf.r3(z)],
                    "y": cf.r3(y - BOULDER_B_TOP * 0.8 - 0.05), "scale": 0.8, "yaw_deg": cf.r3(k * 67.0),
                    "block": "Rocks"})
    burner = rows["VigilBurner"]
    out.append({"piece": "tier_brazier", "kit_dir": COILSPIRE, "at": [burner["pos"][0], burner["pos"][2]],
                "y": cf.r3(burner["pos"][1] - burner["size"][1] * 0.5), "scale": 0.5, "yaw_deg": 0.0,
                "block": "VigilBurner"})
    return out


# --- the one-time move of the story points ----------------------------------------------------------------------

GB_STRAND_Z = (-8.0, 8.0)
GB_SEA_Y = 0.6  # the greybox strand's top (0) is the kit strand's (STRAND_Y)
GB_STAIR_FOOT = (20.0, -28.0)


def to_kit(name: str, x: float, y: float, z: float, yaw: float) -> tuple[float, float, float, float]:
    if x > 250.0:  # Iskarra, a separate set
        return x + ISKARRA_DX, y, z, yaw
    if name in ANCHORS:
        s, yy, zl, dyaw = ANCHORS[name]
        wx, wy, wz, a = cf.arc(s, yy, zl)
        return wx, wy, wz, yaw + dyaw + a
    if x < -32.0:  # the wall-head where Liss waits: the walk at her cut hoist
        wx, wy, wz, a = cf.arc(cf.HOIST_S + (x + 40.0) * 0.4, cf.WALK_Y + y, max(-2.2, min(2.7, (z + 2.0) * 0.25)))
        return wx, wy, wz, yaw + a
    if x > 45.0 and z < -8.0:  # the coast road
        wx, wy, wz, a = cf.arc(x - 15.0, cf.WALK_Y + y, max(-2.2, min(2.7, (z + 14.0) * 0.5)))
        return wx, wy, wz, yaw + a
    if z < -10.0:  # the drowned low town behind the wall
        fx, _fy, fz, _a = cf.arc(cf.STAIR_S, 0.0, cf.stair_z(cf.TOWN_Y))
        return fx + (x - GB_STAIR_FOOT[0]), max(LAKE_Y, cf.TOWN_Y + y), fz + (z - GB_STAIR_FOOT[1]) * 0.6 - 4.0, yaw
    zl = STRAND_Z[0] + (min(z, GB_STRAND_Z[1]) - GB_STRAND_Z[0]) * 0.5 + max(0.0, z - GB_STRAND_Z[1])
    wx, wy, wz, a = cf.arc(x + BREACH_S, y + GB_SEA_Y, zl)
    return wx, wy, wz, yaw + a


# Story points the regions can't place: Kerrid on the broken stair's lower flight above the lake, the climb, Liss's
# NPC spot, the dawn road's gate. Values: (s, y, wall-frame z, yaw offset).
ANCHORS = {
    "kerrid_stair": (cf.STAIR_S + 12 * cf.cw_stair.GOING_M - 0.2, cf.TOWN_Y + 12 * 0.2, cf.stair_z(3.4), 90.0),
    "stair_climb": (cf.STAIR_S + 9 * cf.cw_stair.GOING_M, cf.TOWN_Y + 9 * 0.2, cf.stair_z(2.8), 90.0),
    "RoadGate": (37.0, cf.WALK_Y, 0.0, 0.0),
    "wallhead_motes": (BREACH_S, 8.0, 0.0, 0.0),
}


def relayout() -> None:
    from ch08_corrow_relayout import dump
    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    geometry = {"Harbour", "Strand", "KerbW", "KerbE", "MoleW", "MoleE", "WallHead", "WallHeadParapetN",
                "WallHeadParapetW", "WallHeadParapetS", "SeaWallW", "SeaWallE", "BreachRubble", "RoofA", "RoofB",
                "RoofC", "RoofD", "WatcherFallenA", "WatcherFallenB", "CoastRoad", "RoadKerbN", "RoadKerbS",
                "LandwardGate", "RoadEnd"} | {f"FisherStair{i}" for i in range(7)}

    def m(name: str, p: list) -> list:
        x, y, z, yaw = to_kit(name, p[0], p[1], p[2], p[3] if len(p) > 3 else 0.0)
        return [cf.r3(x), cf.r3(y), cf.r3(z), cf.yaw_norm(yaw)] if len(p) > 3 else [cf.r3(x), cf.r3(y), cf.r3(z)]

    blocks = []
    for b in g["blocks"]:
        if b["id"] in geometry:
            continue
        x, y, z, a = to_kit(b["id"], b["pos"][0], b["pos"][1], b["pos"][2], 0.0)
        row = dict(b, pos=[cf.r3(x), cf.r3(y), cf.r3(z)])
        if b["pos"][0] < 250.0:
            row["yaw"] = cf.yaw_norm(float(b.get("yaw", 0.0)) + a)
        blocks.append(row)
    for b in blocks:
        if b["id"] == "LowTownLake":
            x, _y, z, _a = cf.arc(-45.0, 0.0, -28.0)
            b.update(pos=[cf.r3(x), LAKE_Y - 0.5, cf.r3(z)], size=[120.0, 1.0, 56.0], solid=False)
        if b["id"] == "Rocks":
            x, _y, z, a = cf.arc(sum(ROCKS_S) * 0.5, 0.0, 20.0)
            b.update(pos=[cf.r3(x), 2.0, cf.r3(z)], size=[8.0, 4.0, 7.0], yaw=cf.yaw_norm(a))
    g["blocks"] = blocks
    g["spawns"] = {k: m(k, v) for k, v in g["spawns"].items()}
    g["marks"] = {k: m(k, v) for k, v in g["marks"].items()}
    g["actors"] = {k: dict(v, at=m(k, v["at"])) for k, v in g["actors"].items()}
    g["shots"] = {k: dict(v, pos=m(k, v["pos"]), look_at=m(k, v["look_at"])) for k, v in g["shots"].items()}
    for t in g["triggers"]:
        x, y, z, a = to_kit(t["id"], t["at"][0], t["at"][1], t["at"][2], 0.0)
        t["at"] = [cf.r3(x), cf.r3(y), cf.r3(z)]
        t["yaw"] = cf.yaw_norm(float(t.get("yaw", 0.0)) + a)
    g["collision_path"] = "res://game/levels/ch09/corrow_night/corrow_night_collision.json"
    LAYOUT.write_text(dump(g), encoding="utf-8")


def main() -> None:
    if "--relayout" in sys.argv:
        relayout()
    (ZONE / "corrow_night_collision.json").write_text(json.dumps(collision(), indent=1) + "\n", encoding="utf-8")
    (ZONE / "corrow_night_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
