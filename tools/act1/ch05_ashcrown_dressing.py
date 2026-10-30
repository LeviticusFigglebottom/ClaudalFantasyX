#!/usr/bin/env python3
"""Ch5 Ashcrown: env-art's Ashcrown kit (M3-ENV-09) dresses ch05/ashcrown, and the zone moves into the kit's frame
(M3-ENV-1303, which takes up act1-chapters' blocked M3-C05-1215; ADR 0200; the steep flights are walked by
hero-integration's HeroStairs, M3-ARC-1216 / ADR 0193).

The kit's frame (ashcrown.md §0; assets_src/environments/kits/ashcrown/ac_common.py): x east, north -Z, the temple
facing south (+Z) down to Pemakar. The forecourt at y -4 (z 19..45, x +-32), the pilgrims' causeway climbing to it from
z 146 (11 flights of 32 risers, 43.7°, with 1.8 m landings), the flying stair (48°) from the forecourt (z 39.8) to the
top tier's front edge (y 42), the seven tiers (tier k's top at y 6 + 6k; the "tierK" floors of ashcrown_flights.json),
the vein stairs (60°) down each tier's front face, the anvil hall inside tiers 0 and 1 (floor y -4, x +-7, the anvil at
z -8.4, the crater loggia at the north end).

The story's places:
  the pilgrim stair (B07)  the Tenders' gate (Pemakar's open-hand gate) at the causeway's foot, the tortoises on its
                           second landing, the grave banter at a mid landing (Pemakar's graves on the slope beside it),
                           the copper banter on the forecourt under tier 0's veins; then the flying stair to the crown
  the trial (B08)          t1 the crown (tier 6, east of the pavilion), t2..t4 the east side ambulatories of tiers 5, 4,
                           3: each a line of release, gates, bowl and catch-rod running north from where the vein stair
                           from the tier above lands; the way down is the east vein stair, chained (Stair_t<k>) until
                           the strike reaches the tier below. The ash drift on tier 5, the quench seal and its trough at
                           tier 4's north end, the Tenders' graves and the floor plates on tier 3.
  the anvil court (B09-10) the anvil hall: the anvil (the kit's altar), the Matron's alcove on the west wall, Kahre's
                           door at the loggia (his chamber is the loggia over the crater), the hall door to the sea.
After the last release the walk ends at tier 3's east vein stair: its head is the anvil_court trigger (the matron beat
places the party in the court), and the way on down is chained for good.

Writes next to the zone (game/levels/ch05/ashcrown/):
  ashcrown_dressing.json   the kit (the preview's pieces and borrowed Pemakar pieces and lights) and the story pieces
  ashcrown_collision.json  the tiers (boxes, hollowed for the hall), their coping rails, the forecourt and its parapet,
                           the causeway (ramps, landings, cheeks), the hall's walls and pillars, the flights' blocking
                           slabs, the chains, and the "stairs" rows HeroStairs walks
and takes env-art's Ch5 day grade (assets/environments/zones/ch05/). --relayout (once) moves the layout's story points into the frame.

    python3 tools/act1/ch05_ashcrown_dressing.py [--relayout]
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "ashcrown"
sys.path.insert(0, str(KIT_SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ac_approach  # noqa: E402
import ch05_09_zone_looks as zl  # noqa: E402
import ac_common as ac  # noqa: E402

ZONE = ROOT / "game" / "levels" / "ch05" / "ashcrown"
LAYOUT = ZONE / "ashcrown_layout.json"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "ashcrown_kit"
RES_ZONE = "res://game/levels/ch05/ashcrown/"
KIT = "res://assets/environments/kits/ashcrown/"
PEM = "res://assets/environments/kits/pemakar/"
# env-art's Ch5 grades (M3-C05-03, assets/environments/zones/ch05/ch05_grades.json): ashcrown.md's `ch05_temple`
GRADE = "res://assets/environments/zones/ch05/ch05_ashcrown_day_environment.tres"
FLIGHTS = json.loads((ROOT / "assets" / "environments" / "kits" / "ashcrown" / "ashcrown_flights.json").read_text())

FLOOR_Y = ac.FLOOR_Y
RAIL_H = 1.1
RAIL_T = 0.3
SLAB_T = 0.4
SLAB_DROP = 0.3  # a flight's blocking slab lies this far under its nosing line (HeroStairs carries the body above it)
HALL_X = ac.HALL_HALF_W
HALL_TOP = ac.HALL_CEIL_Y + 0.6
LOGGIA_END_Z = ac.tier(0)["back"] - 0.5
BAND_MARGIN_IN = 0.75  # off the tier above's plinth
BAND_MARGIN_OUT = 0.7  # off the coping
TRIAL_TIERS = {"t1": 6, "t2": 5, "t3": 4, "t4": 3}  # the trial's tier ids -> the kit's tiers


def r3(v: float) -> float:
    return round(float(v), 3)


def tier(k: int) -> dict:
    return ac.tier(k)


def flight(fid: str) -> dict:
    return next(f for f in FLIGHTS["flights"] if f["id"] == fid)


def box(bid: str, x0: float, x1: float, y0: float, y1: float, z0: float, z1: float, **extra: object) -> dict:
    row = {"id": bid, "pos": [r3((x0 + x1) * 0.5), r3((y0 + y1) * 0.5), r3((z0 + z1) * 0.5)],
           "size": [r3(abs(x1 - x0)), r3(abs(y1 - y0)), r3(abs(z1 - z0))]}
    row.update(extra)
    return row


def slab(fid: str, foot: list, head: list, width: float) -> dict:
    """A flight's blocking slab: a ramp SLAB_DROP under its nosing line (a 48°/60° slope is a wall to the controller)."""
    return {"id": fid, "from": [foot[0], r3(foot[1] - SLAB_DROP), foot[2]],
            "to": [head[0], r3(head[1] - SLAB_DROP), head[2]], "width": width, "thick": SLAB_T}


# --- the trial's places -------------------------------------------------------------------------------------------
def band_x(k: int) -> float:
    """The centre line of tier k's east side ambulatory (tier 6: between the pavilion's plinth and the edge)."""
    inner = 5.0 + 0.12 if k == 6 else tier(k + 1)["w"] * 0.5 + 0.12
    outer = tier(k)["w"] * 0.5
    return r3((inner + BAND_MARGIN_IN + outer - BAND_MARGIN_OUT) * 0.5)


def band_z0(k: int) -> float:
    """Where a tier's line of pieces starts: just north of where the vein stair from the tier above lands (tier 6: the
    flying stair's head)."""
    return r3(-3.0 if k == 6 else tier(k + 1)["front"] - 1.4)


# Each trial tier: (piece id, kind, metres north of band_z0). Kinds: release, gate, bowl, rod, drift, plate, seal,
# trough, graves.
TRIAL_LINES = {
    "t1": [("release_t1", "release", 0.0), ("g1", "gate", 2.4), ("Bowl_t1", "bowl", 5.4), ("rod_t1", "rod", 7.8)],
    "t2": [("release_t2", "release", 0.0), ("g2a", "gate", 2.2), ("g2b", "gate", 4.4), ("Bowl_t2", "bowl", 7.0),
           ("rod_t2", "rod", 9.0), ("AshDrift", "drift", 10.8)],
    "t3": [("release_t3", "release", 0.0), ("g3a", "gate", 2.0), ("g3b", "gate", 4.0), ("g3c", "gate", 6.0),
           ("Bowl_t3", "bowl", 8.8), ("rod_t3", "rod", 10.8), ("QuenchSeal", "seal", 12.6),
           ("QuenchTrough", "trough", 14.2)],
    "t4": [("release_t4", "release", 0.0), ("g4a", "gate", 2.0), ("PlateA", "plate", 4.2), ("PlateB", "plate", 6.4),
           ("g4b", "gate", 8.6), ("Bowl_t4", "bowl", 11.0), ("rod_t4", "rod", 13.0)],
}
PIECE_OF = {"release": "release_lever", "gate": "vein_gate", "bowl": "strike_bowl", "rod": "catch_rod",
            "drift": "ash_drift", "plate": "floor_plate", "seal": "quench_seal", "trough": "quench_trough"}


# The standing pieces (the bowl, the rod, the lever, the trough) keep to the band's inner side, against the tier's
# wall, so the band's outer side is a clear walk past them; the flush ones (gates, plates) lie on its centre line.
STANDING = {"release", "bowl", "rod", "trough"}
INNER_SHIFT_M = 0.85


def trial_points() -> dict[str, list[float]]:
    """Every trial piece's floor point [x, y, z] by id."""
    out = {}
    for tid, line in TRIAL_LINES.items():
        k = TRIAL_TIERS[tid]
        x, z0, y = band_x(k), band_z0(k), tier(k)["top"]
        for pid, kind, d in line:
            out[pid] = [r3(x - INNER_SHIFT_M) if kind in STANDING else x, r3(y), r3(z0 - d)]
    return out


# The vein stairs down from each trial tier (east), and the chains on their heads (Stair_t<k> opens the way down to
# trial tier t<k>; tier 3's stays chained: below it the walk is over).
DOWN = {"t1": "vein_stair_t6_e", "t2": "vein_stair_t5_e", "t3": "vein_stair_t4_e", "t4": "vein_stair_t3_e"}
STAIR_BLOCKS = {"vein_stair_t6_e": "Stair_t2", "vein_stair_t5_e": "Stair_t3", "vein_stair_t4_e": "Stair_t4",
                "vein_stair_t3_e": "StairDownChained"}


def chain_at(fid: str) -> tuple[list[float], float]:
    """A chain across a vein stair's head: [x, y, z] at the head landing's edge, and its yaw (across the flight)."""
    f = flight(fid)
    hx, hy, hz = f["head"]
    fx = f["foot"][0]
    step = 0.6 if fx > hx else -0.6  # the flight descends along +x (east) or -x (west)
    return [r3(hx - step), r3(hy), r3(hz)], 90.0


# --- hall ----------------------------------------------------------------------------------------------------------
HALL = {  # the anvil court's story points, kit frame [x, y, z, yaw]
    "AnvilCourt": [0.0, FLOOR_Y, 1.6, 0.0],
    "court_front": [0.0, FLOOR_Y, -2.4, 0.0],
    "court_asha_in": [3.2, FLOOR_Y, -11.6, 180.0],  # north of the anvil: her walk to the chamber passes it clear
    "court_kerrid_in": [-2.5, FLOOR_Y, 0.1, 180.0],
    "matron_heart": [-5.3, FLOOR_Y + 1.4, -10.4, 270.0],
    "kahre_heart": [0.0, FLOOR_Y + 1.8, -18.4, 0.0],
    "chamber_in": [0.0, FLOOR_Y, -16.6, 180.0],
    "chamber_door": [0.0, FLOOR_Y, -14.6, 0.0],
    "sea": [0.0, FLOOR_Y + 1.0, 30.0, 0.0],
}
MATRON_ALCOVE = (-HALL_X + 1.45, -10.4, 90.0)  # origin x, z, yaw: its back on the west wall, open to the hall
CHAMBER_DOOR = (0.0, -15.6, 0.0)  # across the loggia's threshold: Kahre's chamber is the loggia over the crater


# --- collision -----------------------------------------------------------------------------------------------------
def tier_boxes() -> list[dict]:
    """Each tier as solid stone from its base to its top, tiers 0 and 1 hollowed for the anvil hall (the nave and the
    loggia, x +-HALL_X, up to HALL_TOP); tier 0's front wall either side of the hall door."""
    out = []
    for k in range(ac.TIERS):
        t = tier(k)
        hw = t["w"] * 0.5
        if k > 1:
            out.append(box(f"Tier{k}", -hw, hw, t["base"], t["top"], t["back"], t["front"]))
            continue
        y_cut = min(t["top"], HALL_TOP)
        out.append(box(f"Tier{k}W", -hw, -HALL_X, t["base"], y_cut, t["back"], t["front"]))
        out.append(box(f"Tier{k}E", HALL_X, hw, t["base"], y_cut, t["back"], t["front"]))
        if t["top"] > HALL_TOP:
            out.append(box(f"Tier{k}Over", -HALL_X, HALL_X, HALL_TOP, t["top"], t["back"], t["front"]))
        if k == 1:  # tier 0's top floor round tier 1, over the hall's sides (tier 0 is only its sides here)
            continue
    t0 = tier(0)
    out.append(box("Tier0Roof", -HALL_X, HALL_X, ac.HALL_CEIL_Y - 0.4, t0["top"] + 2.6, t0["back"], t0["front"]))
    d = ac.DOOR_HALF_W
    for side, (a, b) in (("W", (-HALL_X, -d)), ("E", (d, HALL_X))):
        out.append(box(f"HallFront{side}", a, b, FLOOR_Y, ac.DOOR_TOP_Y, t0["front"] - 4.0, t0["front"]))
    out.append(box("HallFrontLintel", -d, d, ac.DOOR_TOP_Y, ac.HALL_CEIL_Y, t0["front"] - 0.6, t0["front"]))
    return out


def hall_boxes() -> list[dict]:
    out = [box("HallFloor", -HALL_X, HALL_X, FLOOR_Y - 1.0, FLOOR_Y, LOGGIA_END_Z, tier(0)["front"])]
    ph = 0.5
    for i, z in enumerate((12.0, 7.0, 2.0, -3.0, -13.0)):
        for sx in (-1.0, 1.0):
            x = sx * ac.PILLAR_X
            out.append(box(f"Pillar{i}{'WE'[sx > 0]}", x - ph, x + ph, FLOOR_Y, ac.HALL_CEIL_Y, z - ph, z + ph))
    out.append(box("Anvil", -2.5, 2.5, FLOOR_Y, FLOOR_Y + 1.6, ac.PAVILION_Z - 1.8, ac.PAVILION_Z + 1.8))
    out.append(box("LoggiaBalustrade", -HALL_X, HALL_X, FLOOR_Y, FLOOR_Y + RAIL_H, LOGGIA_END_Z - 0.3, LOGGIA_END_Z))
    mx, mz, _yaw = MATRON_ALCOVE
    out.append(box("MatronAlcoveBody", -HALL_X, mx + 1.5, FLOOR_Y, FLOOR_Y + 3.2, mz - 1.0, mz + 1.0))
    return out


def rails() -> list[dict]:
    """Coping rails round every tier's top edge, open where the flying stair lands on tier 6 and at every vein stair's
    head; the forecourt's parapet open for the gate."""
    gaps: dict[int, list[tuple[float, float]]] = {k: [] for k in range(ac.TIERS)}
    gaps[6].append((-ac.STAIR_HALF_W, ac.STAIR_HALF_W))
    for f in FLIGHTS["flights"]:
        if f["id"].startswith("vein_stair_t"):
            k = int(f["id"].split("_t")[1][0])
            hx = f["head"][0]
            gaps[k].append((hx - 1.2, hx + 1.2) if hx > 0 else (hx - 1.2, hx + 1.2))
    out = []
    for k in range(ac.TIERS):
        t = tier(k)
        hw, y = t["w"] * 0.5, t["top"]
        segs = [(-hw, hw)]
        for g0, g1 in sorted(gaps[k]):
            nxt = []
            for a, b in segs:
                if g1 <= a or g0 >= b:
                    nxt.append((a, b))
                    continue
                if g0 > a:
                    nxt.append((a, g0))
                if g1 < b:
                    nxt.append((g1, b))
            segs = nxt
        for i, (a, b) in enumerate(segs):
            out.append(box(f"Coping{k}F{i}", a, b, y, y + RAIL_H, t["front"] - RAIL_T, t["front"]))
        out.append(box(f"Coping{k}B", -hw, hw, y, y + RAIL_H, t["back"], t["back"] + RAIL_T))
        for sx in (-1.0, 1.0):
            x = sx * hw
            out.append(box(f"Coping{k}{'WE'[sx > 0]}", min(x, x - sx * RAIL_T), max(x, x - sx * RAIL_T), y,
                           y + RAIL_H, t["back"], t["front"]))
    z0, z1 = ac.COURT_Z
    out.append(box("Forecourt", -ac.COURT_HALF_W, ac.COURT_HALF_W, FLOOR_Y - 1.0, FLOOR_Y, z0, z1))
    for sx in (-1.0, 1.0):
        x = sx * ac.COURT_HALF_W
        out.append(box(f"Parapet{'WE'[sx > 0]}", min(x, x - sx * RAIL_T), max(x, x - sx * RAIL_T), FLOOR_Y,
                       FLOOR_Y + RAIL_H, z0, z1))
        a, b = (-ac.COURT_HALF_W, -ac.CAUSEWAY_HALF_W) if sx < 0 else (ac.CAUSEWAY_HALF_W, ac.COURT_HALF_W)
        out.append(box(f"ParapetFront{'WE'[sx > 0]}", a, b, FLOOR_Y, FLOOR_Y + RAIL_H, z1 - RAIL_T, z1))
    return out


def causeway() -> tuple[list[dict], list[dict], list[dict]]:
    """The causeway's flights (walkable ramps, also HeroStairs rows for the step-by-step climb), its landings and its
    cheek walls; and the pad at its foot."""
    zs, ys, steps = ac_approach.causeway_profile()
    n = ac.CAUSEWAY_FLIGHT
    hw = ac.CAUSEWAY_HALF_W - 0.5
    blocks, ramps, stairs = [], [], []
    for i in range(0, len(steps), n):
        flight_steps = steps[i:i + n]
        (z_top, y_top), (z_last, y_last) = flight_steps[0], flight_steps[-1]
        z_bot, y_bot = z_last + ac.CAUSEWAY_GOING_M, y_last - ac.CAUSEWAY_RISE_M
        fid = f"Causeway{i // n}"
        ramps.append({"id": fid, "from": [0.0, r3(y_bot), r3(z_bot)], "to": [0.0, r3(y_top), r3(z_top)],
                      "width": r3(2 * hw)})
        stairs.append({"id": fid, "foot": [0.0, r3(y_bot), r3(z_bot)], "head": [0.0, r3(y_top), r3(z_top)],
                       "width_m": r3(2 * hw), "step_rise_m": ac.CAUSEWAY_RISE_M})
        land_z1 = z_bot + ac.CAUSEWAY_LANDING_M
        blocks.append(box(f"{fid}Landing", -hw, hw, y_bot - 1.0, y_bot, z_bot, land_z1))
    blocks.append(box("CausewayTop", -hw, hw, FLOOR_Y - 1.0, FLOOR_Y, ac.COURT_Z[1] - 0.2,
                      ac.COURT_Z[1] + ac.CAUSEWAY_LANDING_M))
    z_end, y_end = float(zs[-1]), float(ys[-1])
    blocks.append(box("CausewayFoot", -6.0, 6.0, y_end - 1.0, y_end, z_end - 0.1, z_end + 8.0))
    for sx in (-1.0, 1.0):  # the cheeks, as stepped boxes over each flight and landing
        for j, r in enumerate(ramps):
            (_, yb, zb), (_, yt, zt) = r["from"], r["to"]
            x = sx * (hw + 0.25)
            blocks.append(box(f"Cheek{'WE'[sx > 0]}{j}", x - 0.25, x + 0.25, yb - 0.5, yt + RAIL_H, zt, zb + 1.8))
        x = sx * 6.0
        blocks.append(box(f"FootBound{'WE'[sx > 0]}", x - 0.25, x + 0.25, y_end, y_end + 2.0, z_end, z_end + 8.0))
    blocks.append(box("FootBoundS", -6.0, 6.0, y_end, y_end + 2.0, z_end + 8.0, z_end + 8.5))
    return blocks, ramps, stairs


def flights() -> tuple[list[dict], list[dict]]:
    """The flying stair and the vein stairs: blocking slabs and HeroStairs rows; chains on the heads not walked."""
    ramps, stairs = [], []
    for f in FLIGHTS["flights"]:
        w = f["clear_width_m"]
        ramps.append(slab(f"Slab_{f['id']}", f["foot"], f["head"], w + 0.3))
        stairs.append({"id": f["id"], "foot": f["foot"], "head": f["head"], "width_m": w})
    return ramps, stairs


def chains() -> list[dict]:
    """Chains (solid) on the heads of every west vein stair and of the east ones below the trial."""
    out = []
    for f in FLIGHTS["flights"]:
        fid = f["id"]
        if not fid.startswith("vein_stair_t"):
            continue
        if fid.endswith("_w") or int(fid.split("_t")[1][0]) <= 2:
            (x, y, z), _yaw = chain_at(fid)
            out.append(box(f"Chain_{fid}", x - 0.6, x + 0.6, y, y + 2.0, z - 0.7, z + 0.7))
    return out


def collision() -> dict:
    blocks = tier_boxes() + hall_boxes() + rails() + chains()
    cb, cr, cs = causeway()
    fr, fs = flights()
    return {"_about": "Generated by tools/act1/ch05_ashcrown_dressing.py (ADR 0200, ADR 0193); do not edit by hand.",
            "blocks": blocks + cb, "ramps": cr + fr, "stairs": cs + fs}


# --- dressing ------------------------------------------------------------------------------------------------------
def _ground(x: float, z: float) -> float:
    return float(ac.massif_local([x], [z])[0])


GRAVE_LANDINGS = (4, 5, 6, 7, 8)  # Pemakar buries its dead where the way passes (B07's grave banter, landing 6)
GRAVE_X = (4.2, 5.6)  # off the causeway's battered side, on the slope
GRAVE_SINK_M = -0.2  # set level into the slope: on its steep fall a shallower sink left the curb's downhill edge in the air


def road_graves() -> list[dict]:
    """Graves on the slope beside the causeway's mid landings: a curb and a stele each side, facing the stair."""
    out = []
    for i, landing in enumerate(GRAVE_LANDINGS):
        _x, _y, z = causeway_point(landing)
        for sx in (-1.0, 1.0):
            for j, gx in enumerate(GRAVE_X):
                x = sx * (gx + 0.9 * ((i + j) % 2))
                zz = z + 1.4 * j - 0.7
                y = r3(_ground(x, zz) - 0.05)
                yaw = 90.0 if sx < 0 else 270.0
                # snapped to the built crest: its coarse rings lie up to 2 m under the analytic massif out here, and
                # the graves floated over the slope (the eye-height pass, 10-30)
                out.append({"piece": "grave_curb", "kit_dir": PEM, "at": [r3(x), r3(zz)], "y": y, "yaw_deg": yaw,
                            "snap": GRAVE_SINK_M})
                out.append({"piece": ("grave_stele_a", "grave_stele_b")[(i + j) % 2], "kit_dir": PEM,
                            "at": [r3(x + sx * 0.6), r3(zz)], "y": y, "yaw_deg": yaw, "collide": True,
                            "snap": GRAVE_SINK_M})
    return out


def flank_rocks() -> list[dict]:
    """Pemakar's flank rock patches (boulders half sunk in the ash, scree, dry scrub) over the crest round the causeway,
    so the slope it climbs is not one smooth sheet of ash; kept 8 m off its centre line."""
    import random

    rng = random.Random(5)
    out = []
    for _k in range(34):
        z = rng.uniform(52.0, 150.0)
        x = rng.choice((-1.0, 1.0)) * rng.uniform(9.0, 60.0)
        out.append({"piece": "flank_rocks", "kit_dir": PEM, "at": [r3(x), r3(z)], "y": r3(_ground(x, z) - 0.3),
                    "yaw_deg": r3(rng.uniform(0.0, 360.0)), "snap": -0.3})
    return out


def story_pieces() -> list[dict]:
    pts = trial_points()
    out = []
    for tid, line in TRIAL_LINES.items():
        for pid, kind, _d in line:
            x, y, z = pts[pid]
            row = {"piece": PIECE_OF[kind], "at": [x, z], "y": y, "yaw_deg": 0.0}
            if kind in ("bowl", "drift", "plate", "seal", "trough"):
                row["block"] = pid
            if kind in ("release", "rod"):  # no greybox block stood for them: their own box colliders
                row["collide"] = True
            if kind == "gate":
                row["block"] = pid
                row["turn_with"] = pid
            if kind in ("seal", "drift"):
                row["yaw_deg"] = 90.0  # across the band
            out.append(row)
    for fid, bid in STAIR_BLOCKS.items():
        (x, y, z), yaw = chain_at(fid)
        out.append({"piece": "stair_chain", "at": [x, z], "y": y, "yaw_deg": yaw, "block": bid})
    for f in FLIGHTS["flights"]:  # the permanent chains
        fid = f["id"]
        if fid.startswith("vein_stair_t") and (fid.endswith("_w") or int(fid.split("_t")[1][0]) <= 2):
            (x, y, z), yaw = chain_at(fid)
            out.append({"piece": "stair_chain", "at": [x, z], "y": y, "yaw_deg": yaw})
    # The Tenders' graves on tier 3, under the plates (Pemakar's grave curbs and steles along the band's outer side).
    pa, pb = pts["PlateA"], pts["PlateB"]
    gx = r3(tier(3)["w"] * 0.5 - BAND_MARGIN_OUT - 0.4)
    for i, z in enumerate((pa[2] + 1.0, pa[2], pb[2], pb[2] - 1.0)):
        out.append({"piece": "grave_curb", "kit_dir": PEM, "at": [gx, z], "y": pa[1], "yaw_deg": 270.0,
                    "block": "TenderGraves" if i == 0 else ""})
        out.append({"piece": ("grave_stele_a", "grave_stele_b")[i % 2], "kit_dir": PEM, "at": [r3(gx + 0.5), z],
                    "y": pa[1], "yaw_deg": 270.0})
    mx, mz, myaw = MATRON_ALCOVE
    out.append({"piece": "matron_alcove", "at": [r3(mx), mz], "y": FLOOR_Y, "yaw_deg": myaw, "block": "MatronAlcove"})
    cx, cz, cyaw = CHAMBER_DOOR
    out.append({"piece": "chamber_door", "at": [cx, cz], "y": FLOOR_Y, "yaw_deg": cyaw, "block": "ChamberDoor"})
    # The pilgrim stair's places: the Tenders' gate at the causeway's foot; graves on the slope by the mid landing.
    zs, ys, _steps = ac_approach.causeway_profile()
    out.append({"piece": "open_hand_gate", "kit_dir": PEM, "at": [0.0, r3(float(zs[-1]) + 1.0)], "y": r3(float(ys[-1])),
                "yaw_deg": 0.0, "scale": 1.3, "block": "TendersGate"})
    out += road_graves() + flank_rocks()
    for row in out:
        if row.get("block") == "":
            del row["block"]
    return out


# The crater loggia (A08, M3-ENV-1310): at the preview's size the near plume's billows reach the loggia's rail, so
# Kahre's chamber looked into a flat grey wall of ash. Narrowed to 0.75 across (its height kept), the plume stands
# back over the vent with the crater's far rim and the sky round it, and the vent's glow lights it from below.
PLUME_SCALE_XZ = 0.75
VENT_GLOW = {"at": [0.0, -40.0, -70.0], "energy": 8.0, "range": 110.0, "color": "#FF7A3A"}
# The plume's day look as played (the beauty pass, 10-30): the kit's ac_plume_day read as a cold blue-grey, lumpy wall
# (a rock face, not ash) against the overcast. The zone's copy is a warm ash grey-brown, its billows softer and
# feathered at the edges, the sun catching its rim.
PLUME_SLOT = "kit_plume"
PLUME_NAME = "ashcrown_plume_day_material.tres"
RES_ZONE_PLUME = "res://game/levels/ch05/ashcrown/" + PLUME_NAME
PLUME_LOOK = {"col_body": "Color(0.52, 0.49, 0.46, 1)", "col_body_top": "Color(0.62, 0.59, 0.55, 1)",
              "col_shade": "Color(0.63, 0.61, 0.6, 1)", "detail_bump": "0.55", "near_detail": "0.6", "mottle": "0.3",
              "edge_soft": "0.75", "alpha_mottle": "0.12", "back_scatter": "0.7", "rim_energy": "0.35"}


def preview_pieces() -> tuple[list[dict], list[dict]]:
    pv = json.loads((PREVIEW / "ashcrown_layout.json").read_text(encoding="utf-8"))
    pieces = []
    for p in pv["pieces"]:
        row = dict(p)
        if p["piece"] == "crest_ground":
            row["collide"] = "trimesh"  # the slope round the causeway's foot and the crest beyond the parapets
        pieces.append(row)
    for b in pv["borrowed"]:
        glb = b["glb"]
        kit_dir, piece = glb.rsplit("/", 1)
        row = {"piece": piece.removesuffix(".glb"), "kit_dir": kit_dir + "/", "at": [b["at"][0], b["at"][2]],
               "y": b["at"][1], "yaw_deg": b.get("yaw_deg", 0.0)}
        for key in ("scale", "lod1_from_m"):
            if key in b:
                row[key] = b[key]
        if "materials" in b:  # an override from this kit's materials (the plume's day look): by slot name, from here
            row["materials"] = {slot: Path(path).stem for slot, path in b["materials"].items()}
            row["materials_dir"] = KIT + "materials/"
        if row["piece"] == "ash_plume_near":
            row.update(scale=PLUME_SCALE_XZ * float(row.get("scale", 1.0)), scale_y=1.0)
        if row.get("materials", {}).get(PLUME_SLOT) == "ac_plume_day":  # the zone's warmer, softer day plume
            row.pop("materials")
            row.pop("materials_dir")
            row["material_paths"] = {PLUME_SLOT: RES_ZONE_PLUME}
        if row["piece"] == "open_hand_gate":
            row["block"] = "CrownGate"  # the causeway head's gate (not the Tenders' gate)
            del row["block"]
        pieces.append(row)
    return pieces, pv["lights"] + [VENT_GLOW]


# --- the zone's own metal and lacquer looks and its grade (M3-ENV-1325) ---------------------------------------------
# The kit's copper, gold and lacquer slots are flat StandardMaterials: at player height the trial's bowls, rods and
# veins read as mint plastic and its posts as red plastic (GPU QA row 26, the 10-29 walk). The zone swaps those slots
# (ZoneKitDressing `material_paths`) for env_bronze looks with patina, streaks and edge wear, written here.
# slot -> (zone material file, env_bronze parameters). Colours are the kit's own (ac_materials.py) unless noted.
ZONE_METALS = {
    # the veins: old copper gone to verdigris (the kit's #5F8A78) over a dark copper body showing at the edges
    "ac_copper_vein": ("ashcrown_copper_vein_material.tres", {
        "col_bronze": (0.3529, 0.2039, 0.1412), "col_worn": (0.6510, 0.3529, 0.1647),
        "col_patina": (0.2706, 0.3804, 0.3373), "col_patina_pale": (0.4314, 0.5137, 0.4706),
        "metallic_bronze": 0.8, "roughness_bronze": 0.5, "roughness_worn": 0.3, "patina_coverage": (0.0, 0.55),
        "patina_roughness": 0.88, "streak_strength": 0.6, "wear_strength": 0.7, "detail_scale_m": 0.6,
        "normal_strength": 0.5, "normal_tile_m": 2.0}),
    # the tiers' long veins (the per-tier slots and the hall's floor vein): weathered far longer and out in the ash
    # rain, so verdigris runs down them in streaks over a dark body; the copper shows where hands and feet wear it
    "ac_vein_t0": ("ashcrown_vein_material.tres", {
        "col_bronze": (0.2706, 0.1569, 0.1098), "col_worn": (0.5490, 0.3020, 0.1569),
        "col_patina": (0.2902, 0.4392, 0.3804), "col_patina_pale": (0.4471, 0.5882, 0.5216),
        "metallic_bronze": 0.7, "roughness_bronze": 0.55, "roughness_worn": 0.35, "patina_coverage": (0.35, 1.0),
        "patina_roughness": 0.9, "streak_strength": 0.85, "wear_strength": 0.5, "detail_scale_m": 0.6,
        "normal_strength": 0.5, "normal_tile_m": 2.0, "variation_value": 0.12}),
    # the Tenders' new copper (the rods, studs and leads they keep bright): a little bloom in the cavities only
    "ac_copper_new": ("ashcrown_copper_new_material.tres", {
        "col_bronze": (0.5020, 0.2706, 0.1255), "col_worn": (0.8000, 0.4784, 0.2706),
        "col_patina": (0.3725, 0.5412, 0.4706), "col_patina_pale": (0.5216, 0.6588, 0.5843),
        "metallic_bronze": 1.0, "roughness_bronze": 0.4, "roughness_worn": 0.24, "patina_coverage": (0.0, 0.18),
        "patina_roughness": 0.8, "streak_strength": 0.25, "wear_strength": 0.9, "detail_scale_m": 0.5,
        "normal_strength": 0.4, "normal_tile_m": 1.6}),
    # gold leaf: worn through to the bronze under it at the edges, ash-dulled in the hollows
    "ac_gold_leaf": ("ashcrown_gold_leaf_material.tres", {
        "col_bronze": (0.7020, 0.5294, 0.2275), "col_worn": (0.4784, 0.3608, 0.2196),
        "col_patina": (0.3608, 0.3451, 0.3255), "col_patina_pale": (0.5020, 0.4824, 0.4549),
        "metallic_bronze": 1.0, "roughness_bronze": 0.3, "roughness_worn": 0.45, "patina_coverage": (0.0, 0.3),
        "patina_roughness": 0.9, "streak_strength": 0.2, "wear_strength": 0.6, "detail_scale_m": 0.5,
        "normal_strength": 0.3, "normal_tile_m": 1.6}),
    # the lacquers: the hollows dull to an aged lacquer of the same hue and the edges chip to the undercoat (the shared
    # look, ch05_09_zone_looks.lacquer(): a grey dust in the hollows read as camouflage on Kahre's door leaves)
    "ac_lacquer_red": ("ashcrown_lacquer_red_material.tres", zl.lacquer((0.6, 0.1294, 0.1020))),
    "ac_lacquer_black": ("ashcrown_lacquer_black_material.tres",
                         zl.lacquer((0.0627, 0.0588, 0.0588), undercoat=(0.3216, 0.1176, 0.0863))),
}
# The trial's per-tier vein slots (ac_common: the kit gives each tier its own so a strike could light one; the zone
# lights a strike with ZoneKitDressing.glow's overlay instead) and the anvil hall's floor vein: the same flat verdigris.
VEIN_SLOTS = tuple("ac_vein_t%d" % k for k in range(7)) + ("ac_vein_floor",)
# The zone's grade: env-art's Ch5 temple grade with more sky fill. Under the ash overcast the tiers' shaded faces
# (tens of metres of ashlar, the flying stair's flanks) fell to near black at player height; this lifts them so
# their coursing reads while the sunlit faces keep their contrast.
ZONE_GRADE_NAME = "ashcrown_day_environment.tres"
ZONE_AMBIENT_ENERGY = 1.8
ZONE_GRADE_OVERRIDES = {"ambient_light_energy": str(ZONE_AMBIENT_ENERGY)}


# The PC's pass 3 (10-30): the crown's benches and steps streaked on the GPU. Short rounded risers interpolate their
# vertex normals toward +Y, so the triplanar base and the salt detail took the top-down projection on near-vertical
# faces. The dressed stone uses the mesh's metre UVs (as ac_ashlar does), and neither copy takes salt: no salt
# reaches a volcano's crown.
# The kit's stone slots bake an occlusion (UV2) that keeps the tiers' faces in near-total shadow once the sun leaves
# them: with the kit's ao_strength the sky's fill hardly reaches tens of metres of ashlar. The zone's copies keep
# everything else and take the occlusion lighter.
ZONE_STONES = {"ac_ashlar": ("ashcrown_ashlar_material.tres", {"ao_strength": "0.3", "salt_coverage": "Vector2(0, 0)"}),
               "ac_dressed": ("ashcrown_dressed_material.tres", {"ao_strength": "0.35", "base_triplanar": "false",
                                                                "salt_coverage": "Vector2(0, 0)"})}


def zone_grade() -> str:
    src = (ROOT / GRADE.removeprefix("res://")).read_text(encoding="utf-8")
    for key, value in ZONE_GRADE_OVERRIDES.items():
        src, n = re.subn(r"(?m)^%s = .*$" % key, "%s = %s" % (key, value), src)
        assert n == 1, key
    return src.replace('resource_name = "ch05_ashcrown_day"', 'resource_name = "ashcrown_day"')


def metal_paths() -> dict:
    paths = {slot: RES_ZONE + f for slot, (f, _) in (ZONE_METALS | ZONE_STONES).items()}
    for slot in VEIN_SLOTS:  # every tier's veins and the hall's floor vein take tier 0's look
        paths[slot] = paths["ac_vein_t0"]
    return paths


def dressing() -> dict:
    pieces, lights = preview_pieces()
    pieces += story_pieces()
    pem = zl.load_generator("ch05_pemakar_dressing").PEMAKAR_SLOTS
    for row in pieces:  # every Ashcrown kit piece; the borrowed Pemakar ones take Pemakar's own looks
        if row.get("kit_dir", KIT) == KIT:
            row["material_paths"] = metal_paths()
        elif row.get("kit_dir") == PEM:
            row["material_paths"] = dict(pem, **row.get("material_paths", {}))  # keeps the plume's own look
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act1/ch05_ashcrown_dressing.py from env-art's Ashcrown kit (M3-ENV-09); do not "
        "edit by hand. The kit's frame.",
        "seed": 55,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 4000.0,
        "lod_margin_m": 2.0,
        "environment": RES_ZONE + ZONE_GRADE_NAME,
        "time_of_day_h": 13.0,
        "greybox": {"hide_all": True, "keep": []},
        "fire_light_color": "#FFB16E",
        "fire_lights": [{"at": l["at"], "energy": l["energy"], "range": l["range"], "color": l["color"]} for l in lights],
        "pieces": pieces,
    }


# --- the one-time move of the story points --------------------------------------------------------------------------
def causeway_point(landing: int, dx: float = 0.0, dz: float = 0.0) -> list[float]:
    """A point on the causeway's landing `landing` counted from its foot (0 = the foot pad)."""
    zs, ys, steps = ac_approach.causeway_profile()
    n = ac.CAUSEWAY_FLIGHT
    flights_ = [steps[i:i + n] for i in range(0, len(steps), n)]
    if landing == 0:
        return [dx, r3(float(ys[-1])), r3(float(zs[-1]) + 3.0 + dz)]
    f = flights_[-landing]
    z_bot = f[-1][0] + ac.CAUSEWAY_GOING_M
    y_bot = f[-1][1] - ac.CAUSEWAY_RISE_M
    return [dx, r3(y_bot), r3(z_bot + ac.CAUSEWAY_LANDING_M * 0.5 + dz)]


def relayout() -> None:
    from ch08_corrow_relayout import dump

    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    pts = trial_points()
    t6 = tier(6)
    crown_y = t6["top"]
    sp = {
        "StairFoot": causeway_point(0, 0.0, 2.0) + [0.0],
        "AfterTortoises": causeway_point(2) + [0.0],
        "Crown": [3.2, crown_y, -3.2, 270.0],
        "AnvilCourt": HALL["AnvilCourt"],
    }
    marks = {
        "stair_front": causeway_point(0, 0.0, -2.6) + [0.0],  # the causeway's foot: Kerrid steps up to the first flight
        "plate_p4a": pts["PlateA"] + [0.0],
        "plate_p4b": pts["PlateB"] + [0.0],
    }
    for k in ("court_front", "matron_heart", "kahre_heart", "chamber_in", "chamber_door", "court_asha_in",
              "court_kerrid_in", "sea"):
        marks[k] = HALL[k]
    actors = dict(g["actors"])
    party = causeway_point(0, 0.0, 1.0)
    for k, (dx, dz) in {"asha": (1.5, -1.5), "toma": (-1.5, -1.5), "ysolde": (1.5, 1.0), "kerrid": (0.0, 2.5)}.items():
        actors[k] = dict(actors[k], at=[r3(party[0] + dx), party[1], r3(party[2] + dz), 0.0])
    actors["tender"] = dict(actors["tender"], at=[-1.6, r3(crown_y), -3.6, 180.0])
    actors["matron"] = dict(actors["matron"], at=[-5.3, FLOOR_Y, -10.4, 270.0])
    trig = {t["id"]: t for t in g["triggers"]}
    foot = causeway_point(0)
    places = {
        "banter_tenders_gate": ([0.0, foot[1], r3(foot[2] - 4.0)], [4.0, 0.0, 1.5]),
        "tortoises": (causeway_point(2), [4.0, 0.0, 1.2]),
        "banter_grave_tier": (causeway_point(6), [4.0, 0.0, 1.2]),
        "banter_copper_tier": ([0.0, FLOOR_Y, 30.0], [20.0, 0.0, 1.5]),
        "crown": ([0.0, crown_y, -2.4], [5.0, 0.0, 1.4]),
        "anvil_court": (list(flight(DOWN["t4"])["head_landing"]), [2.0, 0.0, 2.0]),
    }
    for pid, (x, y, z) in pts.items():
        for tid in ("rod_t", "release_t"):
            if pid.startswith(tid):
                places[pid] = ([x, y, z], [2.0, 0.0, 2.0])
        if re.fullmatch(r"g\d[a-c]?", pid):
            places[f"gate_{pid}"] = ([x, y, z], [2.0, 0.0, 2.0])
        if pid in ("PlateA", "PlateB"):
            places["plate_p4" + pid[-1].lower()] = ([x, y, z], [1.4, 0.0, 1.4])
        if pid == "QuenchTrough":
            places["quench_charm"] = ([x, y, z + 1.0], [2.0, 0.0, 1.4])
    for tid, (at, size) in places.items():
        if tid in trig:
            trig[tid]["at"] = [r3(v) for v in at]
            trig[tid]["size"] = size
            trig[tid]["yaw"] = 0.0
    blocks = []
    for b in g["blocks"]:
        bid = b["id"]
        if bid in pts:
            x, y, z = pts[bid]
            size = b["size"]
            row = dict(b, pos=[x, r3(y + size[1] * 0.5), z])
            if bid in ("QuenchSeal",):
                row["size"] = [r3(tier(4)["w"] * 0.5 - tier(5)["w"] * 0.5), 2.0, 1.2]
                row["pos"] = [r3((tier(4)["w"] * 0.5 + tier(5)["w"] * 0.5) * 0.5), r3(y + 1.0), z]
            blocks.append(row)
        elif bid.startswith("Stair_t"):
            fid = next(f for f, s in STAIR_BLOCKS.items() if s == bid)
            (x, y, z), _yaw = chain_at(fid)
            blocks.append(dict(b, pos=[x, r3(y + 1.0), z], size=[1.2, 2.0, 1.4]))
        elif bid in ("TendersGate", "TenderGraves", "MatronAlcove", "ChamberDoor"):
            at = {"TendersGate": [0.0, r3(foot[1] + 1.0), r3(foot[2] - 2.0)],
                  "TenderGraves": [r3(tier(3)["w"] * 0.5 - 1.1), r3(tier(3)["top"] + 0.15), pts["PlateA"][2]],
                  "MatronAlcove": [-HALL_X + 1.0, FLOOR_Y + 1.6, -10.4], "ChamberDoor": [0.0, FLOOR_Y + 1.4, -15.6]}[bid]
            row = dict(b, pos=at, solid=False)
            if bid == "TenderGraves":
                row["size"] = [1.2, 0.3, 4.0]
            blocks.append(row)
    (cx, cy, cz), _yaw = chain_at(DOWN["t4"])
    blocks.append({"id": "StairDownChained", "pos": [cx, r3(cy + 1.0), cz], "size": [1.2, 2.0, 1.4],
                   "color": "#6b5a3a"})  # for good: below tier 3 the walk is over (the matron beat moves the party)
    g["blocks"] = blocks  # the rest (the ground, the paths, the walls, the court) is the kit's collision now
    g["spawns"] = sp
    g["marks"] = marks
    g["actors"] = actors
    g["shots"] = SHOTS
    g["sun"] = {"pitch_deg": -58.0, "yaw_deg": -45.0, "energy": 2.8, "color": "#fff0dc"}
    g["environment"] = {"background": "#8c8882", "ambient_color": "#8e959c", "ambient_energy": 0.45}
    g["collision_path"] = RES_ZONE + "ashcrown_collision.json"
    g["doc"] = ("M3-C05-02 story (act1_ch05.md B07-B10) on env-art's Ashcrown kit in its own frame since M3-ENV-1303 "
                "(ADR 0200; tools/act1/ch05_ashcrown_dressing.py, which wrote these points once and writes the "
                "collision and the dressing): the pilgrims' causeway from StairFoot up to the forecourt, the flying "
                "stair (48°, HeroStairs: ADR 0193) to the crown (tier 6, y 42), the trial down the east ambulatories "
                "of tiers 6 to 3 (t1-t4: release, gates, bowl, catch-rod running north; the east vein stairs (60°) "
                "down, chained by Stair_t<k> until the strike reaches the tier below), and the anvil court in the "
                "anvil hall (floor y -4: the anvil at z -8.4, the Matron's alcove on the west wall, Kahre's door at "
                "the crater loggia). The walk down ends at tier 3's east vein stair, whose head is the anvil_court "
                "trigger. " + g["doc"].split(". ", 1)[1] if ". " in g["doc"] else g["doc"])
    LAYOUT.write_text(dump(g), encoding="utf-8")


SHOTS = {
    "A01": {"pos": [3.0, -79.4, 154.0], "look_at": [0.0, -76.0, 140.0], "fov": 46},
    "A02": {"pos": [5.0, -62.5, 122.0], "look_at": [0.0, -50.0, 102.0], "fov": 40},
    "A03": {"pos": [12.0, -2.2, 40.0], "look_at": [17.0, 4.0, 19.0], "fov": 46},
    "A04": {"pos": [3.5, 43.8, -1.0], "look_at": [0.0, 52.0, -8.4], "fov": 50},
    "A05": {"pos": [26.0, 52.0, 18.0], "look_at": [9.0, 30.0, -4.0], "fov": 55},
    "A06": {"pos": [14.0, 31.5, 8.0], "look_at": [8.5, 33.5, 1.8], "fov": 44},
    "A07": {"pos": [0.0, 3.6, 10.0], "look_at": [0.0, -4.0, -8.4], "fov": 55},
    "A08": {"pos": [2.0, -2.0, 4.5], "look_at": [-2.5, -2.4, -9.0], "fov": 50},
    "A09": {"pos": [-1.0, -2.4, -6.0], "look_at": [-5.3, -2.4, -10.4], "fov": 40},
    "A10": {"pos": [2.6, -2.4, -11.0], "look_at": [0.0, -2.6, -15.6], "fov": 40},
    "A11": {"pos": [0.0, -2.4, -19.0], "look_at": [0.0, -2.2, -16.6], "fov": 32},
    "A12": {"pos": [0.0, -3.0, -11.4], "look_at": [0.0, 2.0, -15.6], "fov": 55},
}


def main() -> None:
    if "--relayout" in sys.argv:
        relayout()
    (ZONE / "ashcrown_collision.json").write_text(json.dumps(collision(), indent=1) + "\n", encoding="utf-8")
    (ZONE / "ashcrown_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")
    for name, params in ZONE_METALS.values():
        (ZONE / name).write_text(zl.bronze_material(name, params), encoding="utf-8")
    for slot, (name, overrides) in ZONE_STONES.items():
        (ZONE / name).write_text(zl.copy_material(KIT + "materials/" + slot + ".tres", name, overrides), encoding="utf-8")
    (ZONE / PLUME_NAME).write_text(zl.copy_material(KIT + "materials/ac_plume_day.tres", PLUME_NAME, PLUME_LOOK),
                                   encoding="utf-8")
    (ZONE / ZONE_GRADE_NAME).write_text(zone_grade(), encoding="utf-8")
    # Ch05Zone.apply_variant writes the layout's `environment` row over the grade, so the fill goes there too
    # (a one-key text edit: the layout is hand-formatted and act1-chapters edits it too)
    text = LAYOUT.read_text(encoding="utf-8")
    env = json.loads(text)["environment"]
    old = '"ambient_color": "%s", "ambient_energy": %s}' % (env["ambient_color"], json.dumps(env["ambient_energy"]))
    if env["ambient_energy"] != ZONE_AMBIENT_ENERGY:
        assert text.count(old) == 1, old
        LAYOUT.write_text(text.replace(old, old.rsplit(":", 1)[0] + ": %s}" % ZONE_AMBIENT_ENERGY), encoding="utf-8")


if __name__ == "__main__":
    main()
