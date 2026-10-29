#!/usr/bin/env python3
"""Ch4 the Brightwater ferry: env-art's ferry kit (M3-ENV-08) and the Seventh Terrace (M3-ENV-08B) on ch04/brightwater_ferry
(M3-C04-1204, ADR 0200).

The zone keeps its greybox frame (north -Z, deck height y 0). The ferry's origin is at FERRY_AT (bow north, main deck
y 0), the derelict's at FERRY_AT + bf_terrace.DERELICT_IN_FERRY (an oar's length to port, both bows north, never
joined: ADR 0017 (d)). The islet's seaward landing lies off her starboard gangway (the kit boards midships), so the
gangplank crosses from the islet to the gangway.

Writes next to the zone (game/levels/ch04/brightwater_ferry/):
  brightwater_ferry_dressing.json   ZoneKitDressing's layout: both ships and their states (the sails, the name
                                    board), the alongside gear, the passengers' bundles, the reef awash.
  brightwater_ferry_collision.json  Ch04Zone's collision_path: the decks in slices inside the bulwarks, the bulwarks
                                    to their rail height (the starboard gangway open), the poops and their ladders as
                                    ramps, the hatch coamings, the deckhouse with its door, the masts, the cargo, the
                                    derelict's galley with its door, the islet and the gangplank.
With --relayout it also moves the layout's story points onto the kit (once; see relayout()).

    python3 tools/act1/ch04_ferry_dressing.py [--relayout]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "brightwater_ferry"
sys.path.insert(0, str(KIT_SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bf_common as bf  # noqa: E402
import bf_terrace as bt  # noqa: E402

ZONE = ROOT / "game" / "levels" / "ch04" / "brightwater_ferry"
LAYOUT = ZONE / "brightwater_ferry_layout.json"
KIT = "res://assets/environments/kits/brightwater_ferry/"
RES_ZONE = "res://game/levels/ch04/brightwater_ferry/"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "brightwater_ferry_kit"
PREVIEW_LAYOUT = PREVIEW / "brightwater_ferry_layout.json"
DROWNED = ("derelict_hulk_a", "derelict_hulk_b", "reef_awash")
SEA_Y = bf.WATERLINE_Y  # the ship's waterline in her frame (bf_common.WATERLINE_Y), main deck at y 0
FERRY_AT = (0.0, 0.0, 10.0)
DERELICT_AT = tuple(FERRY_AT[i] + bt.DERELICT_IN_FERRY[i] for i in range(3))
SLICE_M = 1.0
DECK_T = 1.0
WALL_T = 0.22
ISLET_AT = (12.0, 0.0, FERRY_AT[2] + sum(bf.GANGWAY_Z) * 0.5)  # the islet's rock, east of the starboard gangway
ISLET_HALF = (5.0, 9.0)  # x, z: the 10 x 18 m rock of the greybox, turned to lie along the ferry
PLANK_W = 1.6


def r3(v: float) -> float:
    return round(float(v), 3)


def box(bid: str, x0: float, x1: float, y0: float, y1: float, z0: float, z1: float, **kw) -> dict:
    row = {"id": bid, "pos": [r3((x0 + x1) / 2), r3((y0 + y1) / 2), r3((z0 + z1) / 2)],
           "size": [r3(abs(x1 - x0)), r3(abs(y1 - y0)), r3(abs(z1 - z0))]}
    row.update(kw)
    return row


def ramp(rid: str, a: tuple, b: tuple, width: float) -> dict:
    return {"id": rid, "from": [r3(v) for v in a], "to": [r3(v) for v in b], "width": width}


def hull_collision(tag: str, form: bf.HullForm, at: tuple, deck_z: tuple, poop: tuple, open_starboard: tuple | None,
                   ladders_x: float) -> tuple[list[dict], list[dict]]:
    """A ship's walkable decks and its bulwarks, in slices along her length (her frame + `at`)."""
    ox, oy, oz = at
    blocks: list[dict] = []
    cuts = {round(deck_z[0] + SLICE_M * i, 3) for i in range(int((poop[1] - deck_z[0]) / SLICE_M) + 1)}
    cuts |= {poop[0], poop[1]} | (set(open_starboard) if open_starboard else set())
    cuts = sorted(c for c in cuts if deck_z[0] <= c <= poop[1])
    for k, (z, z1) in enumerate(zip(cuts, cuts[1:])):
        if z1 - z < 0.05:
            continue
        zm = (z + z1) * 0.5
        hb = float(min(form.half_beam_at(z), form.half_beam_at(z1)))
        top = poop[2] if zm >= poop[0] else 0.0
        blocks.append(box(f"{tag}Deck{k}", ox - hb + 0.05, ox + hb - 0.05, oy + top - DECK_T, oy + top, oz + z, oz + z1))
        rail = float(max(form.rail_y(z), form.rail_y(z1)))
        hbo = float(max(form.half_beam_at(z), form.half_beam_at(z1)))
        blocks.append(box(f"{tag}RailP{k}", ox - hbo - WALL_T, ox - hbo + 0.05, oy - 0.5, oy + max(rail, top + 0.95),
                          oz + z, oz + z1))
        gap = open_starboard is not None and z >= open_starboard[0] - 1e-6 and z1 <= open_starboard[1] + 1e-6
        if not gap:
            blocks.append(box(f"{tag}RailS{k}", ox + hbo - 0.05, ox + hbo + WALL_T, oy - 0.5,
                              oy + max(rail, top + 0.95), oz + z, oz + z1))
    bow_hb = float(form.half_beam_at(deck_z[0]))
    blocks.append(box(f"{tag}RailBow", ox - bow_hb, ox + bow_hb, oy - 0.5, oy + 1.5, oz + deck_z[0] - 0.3,
                      oz + deck_z[0]))
    stern_hb = float(form.half_beam_at(poop[1]))
    blocks.append(box(f"{tag}RailStern", ox - stern_hb, ox + stern_hb, oy + poop[2] - 0.5, oy + poop[2] + 1.0,
                      oz + poop[1], oz + poop[1] + 0.3))
    # the poop's break: a wall across her but for the two ladders (ramps, lengthened forward to a walkable pitch)
    hb = float(form.half_beam_at(poop[0]))
    lw = 0.9
    edges = [-hb, -ladders_x - lw / 2, -ladders_x + lw / 2, ladders_x - lw / 2, ladders_x + lw / 2, hb]
    for i, (a, b) in enumerate(((edges[0], edges[1]), (edges[2], edges[3]), (edges[4], edges[5]))):
        blocks.append(box(f"{tag}PoopBreak{i}", ox + a, ox + b, oy - 0.5, oy + poop[2] + 0.4, oz + poop[0] - 0.1,
                          oz + poop[0]))
    run = poop[2] / math.tan(math.radians(30.0))
    ramps = [ramp(f"{tag}Ladder{s}", (ox + sx, oy, oz + poop[0] - run), (ox + sx, oy + poop[2], oz + poop[0]), lw)
             for s, sx in (("P", -ladders_x), ("S", ladders_x))]
    return blocks, ramps


def ferry_fittings() -> list[dict]:
    ox, oy, oz = FERRY_AT
    out = []
    hx, hz, hhx, hhz, hh = bf.MAIN_HATCH
    out.append(box("FerryMainHatch", ox + hx - hhx, ox + hx + hhx, oy, oy + hh, oz + hz - hhz, oz + hz + hhz))
    fx, fz, fhx, fhz, fh = bf.FORE_HATCH
    out.append(box("FerryForeHatch", ox + fx - fhx, ox + fx + fhx, oy, oy + fh, oz + fz - fhz, oz + fz + fhz))
    x0, x1, z0, z1, h = bf.DECKHOUSE
    door = 0.5
    out += [box("FerryHouseW", ox + x0, ox + x0 + 0.15, oy, oy + h, oz + z0, oz + z1),
            box("FerryHouseE", ox + x1 - 0.15, ox + x1, oy, oy + h, oz + z0, oz + z1),
            box("FerryHouseAft", ox + x0, ox + x1, oy, oy + h, oz + z1 - 0.15, oz + z1),
            box("FerryHouseFwdW", ox + x0, ox - door, oy, oy + h, oz + z0, oz + z0 + 0.15),
            box("FerryHouseFwdE", ox + door, ox + x1, oy, oy + h, oz + z0, oz + z0 + 0.15),
            box("FerryHouseRoof", ox + x0, ox + x1, oy + h, oy + h + 0.2, oz + z0, oz + z1)]
    for name, mz in (("FerryForemast", bf.FOREMAST_Z), ("FerryMainmast", bf.MAINMAST_Z)):
        out.append(box(name, ox - 0.25, ox + 0.25, oy, oy + 4.0, oz + mz - 0.25, oz + mz + 0.25))
    for side, (a, b) in (("P", (-2.2, -1.3)), ("S", (1.3, 2.2))):
        out.append(box(f"FerryCargo{side}", ox + a, ox + b, oy, oy + 1.4, oz - 0.9, oz + 1.7))
    return out


def derelict_fittings() -> list[dict]:
    ox, oy, oz = DERELICT_AT
    out = []
    hx, hz, hhx, hhz, hh = bt.MAIN_HATCH
    out.append(box("DerelictHatch", ox + hx - hhx, ox + hx + hhx, oy, oy + hh, oz + hz - hhz, oz + hz + hhz))
    x0, x1, z0, z1, h = bt.GALLEY
    d0, d1, _dh = bt.GALLEY_DOOR
    out += [box("DerelictGalleyW", ox + x0, ox + x0 + 0.12, oy, oy + h, oz + z0, oz + z1),
            box("DerelictGalleyE", ox + x1 - 0.12, ox + x1, oy, oy + h, oz + z0, oz + z1),
            box("DerelictGalleyAft", ox + x0, ox + x1, oy, oy + h, oz + z1 - 0.12, oz + z1),
            box("DerelictGalleyFwdW", ox + x0, ox + d0, oy, oy + h, oz + z0, oz + z0 + 0.12),
            box("DerelictGalleyFwdE", ox + d1, ox + x1, oy, oy + h, oz + z0, oz + z0 + 0.12)]
    tx, tz, thx, thz, th = bt.TABLE
    out.append(box("DerelictTable", ox + tx - thx, ox + tx + thx, oy, oy + th, oz + tz - thz, oz + tz + thz))
    out.append(box("DerelictMainmast", ox - 0.25, ox + 0.25, oy, oy + 4.0, oz + bt.MAINMAST_Z - 0.25,
                   oz + bt.MAINMAST_Z + 0.25))
    out.append(box("DerelictForemast", ox - 0.25, ox + 0.25, oy, oy + 4.0, oz + bt.FOREMAST_Z - 0.25,
                   oz + bt.FOREMAST_Z + 0.25))
    return out


def islet() -> tuple[list[dict], list[dict]]:
    ix, _iy, iz = ISLET_AT
    hx, hz = ISLET_HALF
    blocks = [box("IsletRock", ix - hx, ix + hx, -1.0, 0.0, iz - hz, iz + hz, color="#6f6a60"),
              box("IsletRailN", ix - hx, ix + hx, 0.0, 1.0, iz - hz - 0.6, iz - hz),
              box("IsletRailS", ix - hx, ix + hx, 0.0, 1.0, iz + hz, iz + hz + 0.6),
              box("IsletRailE", ix + hx, ix + hx + 0.6, 0.0, 1.0, iz - hz, iz + hz)]
    gz = FERRY_AT[2] + sum(bf.GANGWAY_Z) * 0.5
    blocks += [box("IsletRailWN", ix - hx - 0.6, ix - hx, 0.0, 1.0, iz - hz, gz - PLANK_W / 2),
               box("IsletRailWS", ix - hx - 0.6, ix - hx, 0.0, 1.0, gz + PLANK_W / 2, iz + hz)]
    hb = float(bf.FERRY.half_beam_at(sum(bf.GANGWAY_Z) * 0.5))
    plank = [ramp("Gangplank", (ix - hx, 0.0, gz), (FERRY_AT[0] + hb - 0.05, 0.0, gz), PLANK_W)]
    blocks += [box("GangplankRailN", FERRY_AT[0] + hb, ix - hx, 0.0, 1.0, gz - PLANK_W / 2 - 0.3, gz - PLANK_W / 2),
               box("GangplankRailS", FERRY_AT[0] + hb, ix - hx, 0.0, 1.0, gz + PLANK_W / 2, gz + PLANK_W / 2 + 0.3)]
    return blocks, plank


def collision() -> dict:
    fb, fr = hull_collision("Ferry", bf.FERRY, FERRY_AT, (bf.FERRY.stem_z + 1.0, 0.0), (bf.POOP_Z, bf.FERRY.transom_z - 0.2,
                            bf.POOP_Y), bf.GANGWAY_Z, 2.62)
    db, dr = hull_collision("Derelict", bt.FORM, DERELICT_AT, (bt.WALK[0][4], 0.0), (bt.POOP_Z, bt.WALK[1][5], bt.POOP_Y),
                            None, bt.LADDER_X)
    ib, ir = islet()
    sea = box("Sea", -40.0, 40.0, -3.0, -2.0, -30.0, 50.0)
    return {"_about": "Generated by tools/act1/ch04_ferry_dressing.py (ADR 0200); do not edit by hand. Ch04Zone's "
            "collision_path for ch04/brightwater_ferry.", "blocks": [sea] + fb + ferry_fittings() + db +
            derelict_fittings() + ib, "ramps": fr + dr + ir}


HALUNA = "res://assets/environments/kits/haluna/"
BRINE = "res://assets/environments/kits/brine_shoals/"
# the islet's rock: Haluna's largest coral boulder, flattened, two across and three along its 10 x 18 m, so the walk
# (y 0) is rock from edge to edge (x offset, z offset, yaw)
ISLET_BOULDERS = ((-2.4, -5.8, 10.0), (2.6, -5.2, 200.0), (-2.6, 0.3, 130.0), (2.3, 0.0, 300.0), (-2.2, 5.9, 250.0),
                  (2.7, 5.6, 70.0))
ISLET_BOULDER = {"scale": 2.2, "scale_y": 1.1, "y": -1.9}  # half height (scale_y is absolute); crown 0.25 m over the walk
PLANK_WALK = {"length": 4.0, "top": 0.12}  # the Brine kit's plank_walk, along its z
GATE = {"scale": 0.75, "half_h": 0.6}  # the Brine kit's hatch (1.4 x 1.2 m, centred) across the 1 m gangway


def stand_in_pieces() -> list[dict]:
    """ADR 0041: the islet landing's story blocks in other kits' pieces until env-art's own land (M3-ENV-1222): the
    islet's rock in Haluna's coral, the gangplank as the Brine kit's plank walk, the stern gate as its hatch board
    and the name board laid flat on the deck. Each follows its block."""
    ix, _iy, iz = ISLET_AT
    out = [{"piece": "coral_boulder_c", "kit_dir": HALUNA, "at": [r3(ix + ox), r3(iz + oz)], "yaw_deg": yaw,
            "block": "IsletRock", **ISLET_BOULDER} for ox, oz, yaw in ISLET_BOULDERS]
    gz = FERRY_AT[2] + sum(bf.GANGWAY_Z) * 0.5
    hb = float(bf.FERRY.half_beam_at(sum(bf.GANGWAY_Z) * 0.5))
    mid = (ix - ISLET_HALF[0] + FERRY_AT[0] + hb) * 0.5
    out.append({"piece": "plank_walk", "kit_dir": BRINE, "at": [r3(mid), r3(gz)], "y": -PLANK_WALK["top"],
                "yaw_deg": 90.0, "block": "Gangplank"})
    layout = {b["id"]: b for b in json.loads(LAYOUT.read_text(encoding="utf-8"))["blocks"]}
    gate = layout["SternGate"]
    out.append({"piece": "hatch", "kit_dir": BRINE, "at": [gate["pos"][0], gate["pos"][2]],
                "y": r3(gate["pos"][1] - gate["size"][1] * 0.5 + GATE["half_h"] * GATE["scale"]), "yaw_deg": 0.0,
                "scale": GATE["scale"], "block": "SternGate"})
    board = layout["NameBoardWrapped"]
    out.append({"piece": "terrace_name_board", "at": [board["pos"][0], board["pos"][2]],
                "y": r3(board["pos"][1] - board["size"][1] * 0.5), "yaw_deg": 0.0, "tilt_deg": [-90.0, 0.0],
                "scale": r3(board["size"][0] / 2.59), "block": "NameBoardWrapped"})
    return out


def ship(pieces: tuple, at: tuple, **kw) -> list[dict]:
    return [dict({"piece": p, "at": [r3(at[0]), r3(at[2])], "y": r3(at[1]), "yaw_deg": 0.0}, **kw) for p in pieces]


def dressing() -> dict:
    fx, fy, fz = FERRY_AT
    dx, dy, dz = DERELICT_AT
    pieces = ship(("ferry_hull", "ferry_rig", "ferry_deckhouse", "ferry_awning", "ferry_cargo", "ferry_skiff",
                   "alongside_gear"), FERRY_AT)
    preview = json.loads(PREVIEW_LAYOUT.read_text(encoding="utf-8"))
    off = [FERRY_AT[i] - preview["ship_origin"][i] for i in range(3)]
    for p in preview["pieces"]:
        x, z = p["at"][0] + off[0], p["at"][1] + off[2]
        near = abs(x - DERELICT_AT[0]) < 12.0 and abs(z - DERELICT_AT[2]) < 20.0 or abs(x - ISLET_AT[0]) < 8.0
        if p["piece"] in ("ferry_lantern", "passenger_bundles") or (p["piece"] in DROWNED and not near):
            pieces.append(dict(p, at=[r3(x), r3(z)], y=r3(p["y"] + off[1])))
    pieces += ship(("terrace_hull", "terrace_galley", "terrace_hold", "terrace_rig", "terrace_derelict"), DERELICT_AT)
    pieces += ship(("terrace_sails_set", "terrace_membrane"), DERELICT_AT, block="SailsSet")
    pieces += ship(("terrace_sails_lowered",), DERELICT_AT, block="SailsLowered")
    wx, wy, wz = bt.WHEEL_AT
    pieces += ship(("terrace_wheel",), (dx + wx, dy + wy, dz + wz))
    nx, ny, nz = bt.NAME_BOARD_AT
    pieces += ship(("terrace_name_board",), (dx + nx, dy + ny, dz + nz), block="NameBoard")
    pieces += landing()
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act1/ch04_ferry_dressing.py from env-art's ferry kit (M3-ENV-08, 08B); do not "
        "edit by hand.",
        "seed": 4,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "time_of_day_h": 5.83,
        "environment": RES_ZONE + "brightwater_ferry_ch04_environment.tres",
        "fire_light_color": preview["lamp_color"],
        "fire_lights": [{"at": [r3(l[0] + off[0]), r3(l[1] + off[1]), r3(l[2] + off[2])], "energy": l[3], "range": l[4],
                         "shadow": bool(l[5]), "attenuation": preview["lamp_attenuation"]} for l in preview["lamps"]]
        + derelict_fill() + ferry_fill(),
        "greybox": {"hide_all": True, "keep": []},
        "pieces": pieces,
    }


# The derelict's deck has no lamp of its own (a dead ship), and at player height under the pre-dawn grade its fights
# (the leeches, the hermit, the wraith) read near black (the walk-through pass): the sky's cold fill off her pale
# salt-bleached timber, a few shadowless omnis along her waist and poop, in the moon's colour, not a lamp's.
DERELICT_FILL = {"color": "#9DB4D6", "energy": 1.4, "range": 7.0, "attenuation": 1.2}
DERELICT_FILL_AT = ((0.0, 2.5, 6.5), (0.0, 2.5, 1.0), (0.0, 2.5, -5.0))  # in the derelict's frame, as bt's points
# Her topsides and transom read black from the ferry (M3-ENV-1228: F05, D01 and D06; the low moon is behind them), so the
# same fill, weaker, stands just outboard of her ferry side (+x, the half beam is 3.0) and astern of her transom (z 10),
# where the name-board hangs: the hull reads as pale dead timber, still unlit by any lamp.
DERELICT_HULL_FILL_AT = ((3.8, 1.1, -6.0, 0.9), (3.8, 1.1, 1.0, 0.9), (3.8, 1.1, 7.0, 0.9), (1.4, 1.1, 14.5, 1.6))


# The ferry's own deck between its lamps read near black on a real GPU too (the GPU QA's row 4, ch04_ferry_deck): the
# same cold sky fill, weaker (her lamps are the key), along her waist and poop.
FERRY_FILL = {"color": "#9DB4D6", "range": 8.0, "attenuation": 1.2}
# In the ferry's frame, with each one's energy: the waist, amidships, and the poop (where the shots stand), lower and
# stronger there.
FERRY_FILL_AT = ((0.0, 3.2, -8.0, 0.9), (0.0, 3.2, 0.0, 0.9), (0.0, 2.7, 8.5, 1.5))


def ferry_fill() -> list[dict]:
    fx, fy, fz = FERRY_AT
    return [{"at": [r3(fx + x), r3(fy + y), r3(fz + z)], "energy": e, "range": FERRY_FILL["range"],
             "shadow": False, "attenuation": FERRY_FILL["attenuation"], "color": FERRY_FILL["color"]}
            for x, y, z, e in FERRY_FILL_AT]


def derelict_fill() -> list[dict]:
    dx, dy, dz = DERELICT_AT
    return [{"at": [r3(dx + x), r3(dy + y), r3(dz + z)], "energy": DERELICT_FILL["energy"],
             "range": DERELICT_FILL["range"], "shadow": False, "attenuation": DERELICT_FILL["attenuation"],
             "color": DERELICT_FILL["color"]} for x, y, z in DERELICT_FILL_AT] + [
        {"at": [r3(dx + x), r3(dy + y), r3(dz + z)], "energy": e, "range": DERELICT_FILL["range"], "shadow": False,
         "attenuation": DERELICT_FILL["attenuation"], "color": DERELICT_FILL["color"]}
        for x, y, z, e in DERELICT_HULL_FILL_AT]


def landing() -> list[dict]:
    """The islet's landing and the boarding gear (env-art's bf_landing, M3-ENV-746) on the blocks they replace: the
    islet's rock (its walk at y 0), the gangplank from the islet's edge to the gangway, the stern gate on the deck at
    the gangway and the wrapped name-board on the deck, each following its block (the story's states)."""
    blocks = {b["id"]: b for b in json.loads(LAYOUT.read_text(encoding="utf-8"))["blocks"]}
    gz = FERRY_AT[2] + sum(bf.GANGWAY_Z) * 0.5
    out = [{"piece": "islet_landing", "at": [r3(ISLET_AT[0]), r3(ISLET_AT[2])], "y": 0.0, "yaw_deg": 0.0,
            "block": "IsletRock"},
           {"piece": "gangplank", "at": [r3(ISLET_AT[0] - ISLET_HALF[0]), r3(gz)], "y": 0.0, "yaw_deg": 0.0,
            "block": "Gangplank"}]
    for piece, bid in (("stern_gate", "SternGate"), ("terrace_name_board_wrapped", "NameBoardWrapped")):
        b = blocks[bid]
        out.append({"piece": piece, "at": [r3(b["pos"][0]), r3(b["pos"][2])], "y": r3(b["pos"][1] - b["size"][1] / 2),
                    "yaw_deg": 0.0, "block": bid})
    return out


# --- the one-time move of the story points onto the kit -----------------------------------------------------------

GB_FERRY = (-6.0, 24.0)  # the greybox ferry deck's z
GB_DERELICT = (-13.0, 4.0, -8.0, 16.0)  # its centre x, centre z and z range
ANCHORS = {  # story points the kit names (M3-ENV-08 swap-in note), in the zone
    "purser": (2.8, 0.0, FERRY_AT[2] + 0.4, 270.0),
    "ferrymaster": (0.0, bf.POOP_Y, FERRY_AT[2] + 11.0, 0.0),
    "shrine": (0.0, 0.0, FERRY_AT[2] + 6.6, 0.0),
    "bow": (0.0, 0.0, FERRY_AT[2] - 11.5, 0.0),
    "rail_ysolde": (2.9, 0.0, FERRY_AT[2] + 0.2, 90.0),
    "asha": (2.9, 0.0, FERRY_AT[2] + 1.3, 90.0),
    "gangplank_top": (3.0, 0.0, FERRY_AT[2] + sum(bf.GANGWAY_Z) * 0.5, 270.0),
    "ysolde": (ISLET_AT[0] - ISLET_HALF[0] + 0.8, 0.0, FERRY_AT[2] + sum(bf.GANGWAY_Z) * 0.5, 270.0),
    "Landing": (ISLET_AT[0] + 1.0, 0.0, ISLET_AT[2], 270.0),
    "Deck": (1.5, 0.0, FERRY_AT[2] - 2.1, 0.0),
    "FerryAft": (-1.0, 0.0, FERRY_AT[2] + 6.2, 90.0),
}


def to_kit(name: str, x: float, y: float, z: float, yaw: float) -> tuple[float, float, float, float]:
    if name in ANCHORS:
        return ANCHORS[name]
    if x < -7.0:  # the derelict
        cx, cz, z0, z1 = GB_DERELICT
        w = bt.WALK
        zl = w[0][4] + (z - z0) / (z1 - z0) * (w[1][5] - w[0][4])
        top = bt.POOP_Y if zl >= bt.POOP_Z else 0.0
        hb = float(bt.FORM.half_beam_at(zl)) - 0.5
        xl = max(-hb, min(hb, (x - cx) * 0.8))
        return DERELICT_AT[0] + xl, DERELICT_AT[1] + top + y, DERELICT_AT[2] + zl, yaw
    if z > GB_FERRY[1] + 0.5:  # the islet: turned so its north edge (the gangplank) faces the ferry's starboard side
        gx, gz = 0.0, 25.5
        d = (x - gx, z - gz)
        return ISLET_AT[0] - ISLET_HALF[0] + d[1], y, FERRY_AT[2] + sum(bf.GANGWAY_Z) * 0.5 - d[0], yaw - 90.0
    zl = bf.FERRY.stem_z + 2.0 + (z - GB_FERRY[0]) / (GB_FERRY[1] - GB_FERRY[0]) * (bf.FERRY.transom_z - 1.0 - bf.FERRY.stem_z - 2.0)
    top = bf.POOP_Y if zl >= bf.POOP_Z else 0.0
    hb = float(bf.FERRY.half_beam_at(zl)) - 0.5
    return FERRY_AT[0] + max(-hb, min(hb, x * 0.85)), FERRY_AT[1] + top + y, FERRY_AT[2] + zl, yaw


def relayout() -> None:
    from ch08_corrow_relayout import dump
    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    geometry = {"Sea", "IsletRock", "IsletRailW", "IsletRailE", "IsletRailS", "IsletRailNW", "IsletRailNE", "Gangplank",
                "FerryDeck", "FerryRailW", "FerryRailE", "FerryRailBow", "FerryRailSternW", "FerryRailSternE",
                "Deckhouse", "Awning", "Cargo", "MastFore", "MastMain", "Skiff", "Wheel", "DerelictDeck",
                "DerelictRailE", "DerelictRailW", "DerelictRailBow", "DerelictRailStern", "Sheathing", "Galley",
                "Mainmast"}

    def m(name: str, p: list) -> list:
        x, y, z, yaw = to_kit(name, p[0], p[1], p[2], p[3] if len(p) > 3 else 0.0)
        return [r3(x), r3(y), r3(z), round(yaw, 2)]

    blocks = []
    for b in g["blocks"]:
        if b["id"] in geometry:
            continue
        x, y, z, _yaw = to_kit(b["id"], b["pos"][0], b["pos"][1], b["pos"][2], 0.0)
        blocks.append(dict(b, pos=[r3(x), r3(y), r3(z)]))
    g["blocks"] = blocks
    g["spawns"] = {k: m(k, v) for k, v in g["spawns"].items()}
    g["marks"] = {k: m(k, v) for k, v in g["marks"].items()}
    g["actors"] = {k: dict(v, at=m(k, v["at"])) for k, v in g["actors"].items()}
    g["shots"] = {k: dict(v, pos=m(k, v["pos"])[:3], look_at=m(k, v["look_at"])[:3]) for k, v in g["shots"].items()}
    for t in g["triggers"]:
        x, y, z, _yaw = to_kit(t["id"], t["at"][0], t["at"][1], t["at"][2], 0.0)
        t["at"] = [r3(x), r3(y), r3(z)]
    g["collision_path"] = "res://game/levels/ch04/brightwater_ferry/brightwater_ferry_collision.json"
    LAYOUT.write_text(dump(g), encoding="utf-8")


def copy_grades() -> None:
    for name in ("brightwater_ferry_ch04_environment.tres", "brightwater_ferry_water_material.tres"):
        text = (PREVIEW / name).read_text(encoding="utf-8").replace("res://game/levels/_tests/brightwater_ferry_kit/",
                                                                     RES_ZONE)
        (ZONE / name).write_text(text, encoding="utf-8")


def main() -> None:
    copy_grades()
    if "--relayout" in sys.argv:
        relayout()
    (ZONE / "brightwater_ferry_collision.json").write_text(json.dumps(collision(), indent=1) + "\n", encoding="utf-8")
    (ZONE / "brightwater_ferry_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
