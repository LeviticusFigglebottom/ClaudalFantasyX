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

    python3 tools/act1/ch09_corrow_night.py [--relayout] [--moon-relayout]

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


# The Corrow kit's pieces with a cw_rubble slot (the rip-rap, the breach, the strand's rocks, the milestone's cairn)
RUBBLE_PIECES = ("wall_apron", "seawall_breach_a", "seawall_breach_b", "seawall_breach_end_e", "seawall_breach_end_w",
                 "lowtown_rubble", "strand_rocks", "milestone")
APRON_NIGHT = {"cw_rubble": "res://assets/environments/kits/corrow/materials/cw_laterite_broken.tres"}
# The strand's boulders (env-art-b's beauty pass, 10-30): their cw_headland face tiles the coral stone every 18 m (the
# headland's cliff scale), so on a boulder 3 m from the Rocks view its pores magnify into coarse pixel blocks. The
# boulders take a copy at a boulder's scale, with a quieter normal; the cliffs keep the kit's.
ROCKS_NAME = "corrow_strand_rocks_material.tres"
ROCKS_SRC = "res://assets/environments/kits/corrow/materials/cw_headland.tres"
ROCKS_OVERRIDES = {"tile_m": "Vector2(3, 3)", "detail_scale_m": "0.8", "normal_strength": "0.8"}
ROCKS_NIGHT = dict(APRON_NIGHT, cw_headland="res://game/levels/ch09/corrow_night/" + ROCKS_NAME)
# The shrouds (the PC's pass 3, row 51: from the field camera the rows read as blurred orange rectangles): the trader's
# tan canvas took the vigil lamps as flat orange and its fine weave mipmapped away. The dead lie under grey, damp
# sailcloth: darker and cooler, a coarser weave that holds at field distance, the creases darkened over the bodies.
SHROUD_NAME = "corrow_shroud_canvas_material.tres"
# The PC's pass 5 (row 51): the sand ground through the canvas read as soft orange under the lamps; the cloth is
# cooler and covers more of the base now, and the woven normal is soft and coarser: at 0.2 m and 1.7 its weave shaded
# the cloth into dark stripes that read as spiky ridges from the field camera.
SHROUD_OVERRIDES = {"col_paint": "Color(0.6, 0.62, 0.63, 1)", "paint_cover": "0.8", "tile_m": "Vector2(0.45, 0.45)",
                    "normal_strength": "0.45", "variation_value": "0.18", "salt_coverage": "Vector2(0.05, 0.3)"}
SHROUD_ADDED = {"cavity_darken": "0.55"}
SHROUD_PIECES = ("shroud_bound_a", "shroud_bound_b", "shroud_bound_small")  # b_strand.py's crisper shrouds
SHROUD_SLOTS = {"cw_sail": "res://game/levels/ch09/corrow_night/" + SHROUD_NAME}


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
    pieces += strand_pieces() + iskarra_pieces() + strand_kit_pieces()
    pieces += flood_debris_pieces(pieces)
    for p in pieces:  # the night's rubble: dry broken laterite, not the wet black cw_rubble (GPU QA row 28's spheres)
        if p["piece"] in SHROUD_PIECES and not p.get("kit_dir"):
            p["material_paths"] = dict(SHROUD_SLOTS)
        if p["piece"] in RUBBLE_PIECES and not p.get("kit_dir"):
            p["material_paths"] = dict(ROCKS_NIGHT if p["piece"] == "strand_rocks" else APRON_NIGHT)
    src.update(pieces=pieces, environment=RES_C8 + "corrow_ch09_environment.tres", time_of_day_h=22.0,
               _about="Generated by tools/act1/ch09_corrow_night.py from Ch8's dressing (ADR 0200); do not edit by hand.")
    src["greybox"] = {"hide_all": True, "keep": []}
    src["waters"] = c8.story_waters(LAYOUT, ("LowTownLake", "IskarraWater"))
    src["storms"] = []  # the night after: the storm has gone
    src["fire_lights"] = [{"at": l["at"], "energy": l["energy"], "range": l["range"]} for l in src.get("fire_lights", [])]
    src["fire_lights"] += vigil_lights() + [ROCKS_LAMP]
    src["ebbing"] = {}  # the Ebbing's held fields (EbbingMotes, game/data/vfx/ebbing.json; M3-C09-03)
    return src


# The vigil's last lamp at the strand's east end, at the foot of the path Pell comes down (the rocks stood in the
# wall's moon-shadow before M3-ENV-1309, and it still warms the path); it goes out at dawn with the nearest Lamp block.
_PATH_FOOT = cf.arc(ROCKS_PATH[0] - ROCKS_PATH_RUN_M - 0.8, 0.0, ROCKS_PATH[2] + 1.4)
ROCKS_LAMP = {"at": [cf.r3(_PATH_FOOT[0]), 1.5, cf.r3(_PATH_FOOT[2])], "energy": 1.1, "range": 9.0,
              "color": "#FFB46B", "block": "LampD"}
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
            piece = ("shroud_bound_small" if not soldier and i % SHROUD_SMALL_EVERY == 2
                     else ("shroud_bound_a", "shroud_bound_b")[i % 2])
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
    out.append({"piece": "strand_lamp", "at": [ROCKS_LAMP["at"][0], ROCKS_LAMP["at"][2]], "y": STRAND_Y, "yaw_deg": 0.0,
                "block": "LampD"})
    for lid in ("LampA", "LampB", "LampC", "LampD"):
        b = rows[lid]
        out.append({"piece": "strand_lamp", "at": [b["pos"][0], b["pos"][2]], "y": STRAND_Y, "yaw_deg": 0.0, "block": lid})
    for bid, piece, kit in (("Raft", "ebbing_raft", ""), ("IvoShroud", "shroud_bound_a", ""), ("HoistCoil", "rope_coil", HALUNA),
                            ("Milestone", "milestone", "")):
        b = rows[bid]
        y = b["pos"][1] if bid == "Raft" else b["pos"][1] - b["size"][1] * 0.5
        row = {"piece": piece, "at": [b["pos"][0], b["pos"][2]], "y": cf.r3(y), "yaw_deg": b.get("yaw", 0.0), "block": bid}
        if kit:
            row["kit_dir"] = kit
        out.append(row)
    return out


def strand_kit_pieces() -> list[dict]:
    """env-art-b's strand pieces (the Corrow kit's b_strand.py) on the blocks and ramps the greybox stood in with: the
    landing on its block's top, Pell's rocks on the Rocks block's base (the path down its west face is the RocksDown
    ramp), the gangway along the MoleBridge ramp, and the vigil's burner (the Haluna kit's clay ground lamp)."""
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    rows = {b["id"]: b for b in layout["blocks"]}
    ramps = {r["id"]: r for r in collision()["ramps"]}
    out = []
    for bid, piece, kit, top in (("Landing", "strand_landing", "", True), ("Rocks", "strand_rocks", "", False),
                                 ("VigilBurner", "ground_lamp", HALUNA, False)):
        b = rows[bid]
        y = b["pos"][1] + b["size"][1] * (0.5 if top else -0.5)
        row = {"piece": piece, "at": [b["pos"][0], b["pos"][2]], "y": cf.r3(y), "yaw_deg": b.get("yaw", 0.0), "block": bid}
        if kit:
            row["kit_dir"] = kit
        out.append(row)
    r = ramps["MoleBridge"]
    (x0, y0, z0), (x1, _y1, z1) = r["from"], r["to"]
    out.append({"piece": "mole_bridge", "at": [x0, z0], "y": y0,
                "yaw_deg": cf.r3(-math.degrees(math.atan2(z1 - z0, x1 - x0)))})
    return out


# The low town flooded to the eaves (act1_ch09.md §9 Environment 1): the Corrow kit's flood_debris (M3-ENV-708: planks,
# a door, a shutter, a basket, a cloth) adrift on the lake between the drowned houses: HOUSE_CLEAR_M to HOUSE_NEAR_M
# from the nearest house's centre (their roofs stand out of the water). Seeded, so the dressing is reproducible.
DEBRIS_COUNT = 12
DEBRIS_SEED = 909
HOUSE_CLEAR_M = 5.0
HOUSE_NEAR_M = 12.0
DEBRIS_EDGE_M = 6.0  # in from the lake's edges (the wall's apron on one side, the town's rise on the others)


def flood_debris_pieces(pieces: list[dict]) -> list[dict]:
    import random  # noqa: PLC0415

    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    lake = next(b for b in layout["blocks"] if b["id"] == "LowTownLake")
    (cx, cy, cz), (sx, _sy, sz) = lake["pos"], lake["size"]
    water_y = next(w["pos"][1] for w in c8.story_waters(LAYOUT, ("LowTownLake",)))
    houses = [p["at"] for p in pieces if p["piece"].startswith("lowtown_house")]
    rng = random.Random(DEBRIS_SEED)
    out: list[dict] = []
    for _ in range(DEBRIS_COUNT * 50):
        if len(out) == DEBRIS_COUNT:
            break
        x = cx + rng.uniform(-sx * 0.5 + DEBRIS_EDGE_M, sx * 0.5 - DEBRIS_EDGE_M)
        z = cz + rng.uniform(-sz * 0.5 + DEBRIS_EDGE_M, sz * 0.5 - DEBRIS_EDGE_M)
        near = min(math.hypot(x - hx, z - hz) for hx, hz in houses)
        if not HOUSE_CLEAR_M <= near <= HOUSE_NEAR_M:  # in the open water among the houses (the plane runs on under
            continue  # the bastion and the wall's apron, where nothing shows)
        if any(math.hypot(x - o["at"][0], z - o["at"][1]) < HOUSE_CLEAR_M for o in out):
            continue
        out.append({"piece": "flood_debris", "at": [cf.r3(x), cf.r3(z)], "y": cf.r3(water_y),
                     "yaw_deg": cf.r3(rng.uniform(0.0, 360.0)), "block": "LowTownLake"})
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


# --moon-relayout (once, M3-ENV-1309): the moon stood over the town (yaw 200), so the wall's sea face, Pell's rocks and
# the strand's west end were one black plane in the wall's moon-shadow. From the sea's east (yaw 60) it rakes the
# sea face's coursing and the Watchers' reliefs, and lays the shadows of the vigil across the shingle; the dawn
# variant keeps its own sun.
MOON_YAW_DEG = 60.0


def moon_relayout() -> None:
    import re
    text = LAYOUT.read_text(encoding="utf-8")
    text, n = re.subn(r'^(  "sun": \{"pitch_deg": -25\.0, "yaw_deg": )[-0-9.]+', rf"\g<1>{MOON_YAW_DEG}", text, count=1,
                      flags=re.M)
    assert n == 1, "the night sun row has moved"
    LAYOUT.write_text(text, encoding="utf-8")


# The `ch09_dawn` frame (M3-C09-10, act1_ch09.md §9; the colour script's ch09_dawn): B09 at 05:50, a washed low gold
# dawn after the storm, the last warm light of Act I. The zone's own grade, derived from the Ch8 day grade (the same
# sky shader and warm-laterite LUT) with the storm cleared: a pale clearing zenith over a gold eastern horizon, broken
# cloud lit gold from beneath, warm ambient, a lighter exposure. The layout's dawn variant (ch09_pell_joined) loads it.
DAWN_GRADE = "corrow_ch09_dawn_environment.tres"
DAWN_SET = {
    "resource_name": '"corrow_ch09_dawn"',
    "shader_parameter/col_zenith": "Color(0.4706, 0.5569, 0.6353, 1)",
    "shader_parameter/col_horizon_sun": "Color(1, 0.7843, 0.5216, 1)",
    "shader_parameter/col_horizon_away": "Color(0.6431, 0.6314, 0.6392, 1)",
    "shader_parameter/col_ground": "Color(0.2588, 0.2706, 0.2941, 1)",
    "shader_parameter/col_cloud_lit": "Color(1, 0.8, 0.6, 1)",
    "shader_parameter/col_cloud_shadow": "Color(0.4392, 0.4392, 0.502, 1)",
    "shader_parameter/cloud_coverage": "0.45",
    "ambient_light_color": "Color(0.7216, 0.6588, 0.6, 1)",
    "ambient_light_energy": "0.9",
    "tonemap_exposure": "0.9",
    "fog_light_color": "Color(0.7843, 0.6784, 0.5804, 1)",
    "volumetric_fog_albedo": "Color(0.7843, 0.6784, 0.5804, 1)",
}


def write_dawn_grade() -> None:
    import re
    text = (c8.ZONE / "corrow_ch08_environment.tres").read_text(encoding="utf-8")
    for key, value in DAWN_SET.items():
        text, n = re.subn(rf"^{re.escape(key)} = .*$", f"{key} = {value}", text, flags=re.M)
        assert n == 1, key
    (c8.ZONE / DAWN_GRADE).write_text(text, encoding="utf-8")
    layout = LAYOUT.read_text(encoding="utf-8")
    layout, n = re.subn(r'"environment_res": "res://game/levels/ch08/corrow/[a-z0-9_]+\.tres"',
                        f'"environment_res": "{RES_C8}{DAWN_GRADE}"', layout)
    assert n == 1, "the dawn variant's grade row"
    LAYOUT.write_text(layout, encoding="utf-8")


def main() -> None:
    if "--relayout" in sys.argv:
        relayout()
    if "--moon-relayout" in sys.argv:
        moon_relayout()
    write_dawn_grade()
    (ZONE / SHROUD_NAME).write_text(c8.zl.copy_material(c8.RES_ZONE + c8.CANVAS_NAME, SHROUD_NAME, SHROUD_OVERRIDES,
                                                        SHROUD_ADDED), encoding="utf-8")
    (ZONE / ROCKS_NAME).write_text(c8.zl.copy_material(ROCKS_SRC, ROCKS_NAME, ROCKS_OVERRIDES), encoding="utf-8")
    (ZONE / "corrow_night_collision.json").write_text(json.dumps(collision(), indent=1) + "\n", encoding="utf-8")
    (ZONE / "corrow_night_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
