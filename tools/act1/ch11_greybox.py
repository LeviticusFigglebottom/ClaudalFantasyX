#!/usr/bin/env python3
"""Ch11 "Lowlight" greybox (M4-C11-02): the geography of ch11/sunken_vey and ch11/lowlight, before the beat sheet
(M4-C11-01) adds the story. From act_outline.md (Ch11) and the colour script's `ch11` (overcast midday, a still
turquoise lagoon under a grey sky, Lit Age light bleeding teal from every conduit; the sanctum underwater).

  ch11/sunken_vey the drowned galleries: a Lit Age city's arcades half under the lagoon, their roofs the walks (level,
                  railed), drowned pillars along them; from the landing (west) through the conduit court, where Liss
                  reads the Saltwright housing-mark on a conduit (`conduit_mark`), a side gallery north to a fig-choked
                  end (a rest point), and east to Lowlight's gate.
  ch11/lowlight   the temple, half underwater: the atrium at the gate (the lamp bench for Rhen and Liss's side scene),
                  the Lamp Engine's hall north of it (the boss's arena), and east the well-shaft: two flights down
                  (ramps; the controller has no step-up) past the waterline to the drowned sanctum at the shaft's foot
                  (Nhoa's binding), where the deep's cold wells up.

Shares Ch10's builders (tools/act1/ch10_greybox.py). x is east, north is -Z.

    python3 tools/act1/ch11_greybox.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch10_greybox import WALK_T, WALK_W, box, follow_volumes, r3, walk, water  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ZONES = ROOT / "game" / "levels" / "ch11"
COL_STONE = "#8a9a98"
COL_PARAPET = "#5e6a6a"
COL_PILLAR = "#a8b4b0"
COL_LAGOON = "#0e4a55"
COL_CONDUIT = "#1c3a3e"
GLOW_BOUND = "#2fb8c8"  # glimmer_bound: the conduits keep their teal
COL_FIG = "#4a5a3e"
PILLARS = ("Pillar", 0.9, 6.0, COL_PILLAR)
SUN = {"pitch_deg": -65.0, "yaw_deg": 160.0, "energy": 1.4, "color": "#f3f2ff"}  # overcast midday
ENV = {"background": "#a8b4b8", "ambient_color": "#7fa3a8", "ambient_energy": 0.7}


def gallery(bid: str, a: tuple[float, float], b: tuple[float, float], **kw) -> list[dict]:
    return walk(bid, a, b, trim=WALK_W * 0.5, posts=PILLARS, colors=(COL_STONE, COL_PARAPET), **kw)


def walls(bid: str, cx: float, cz: float, hx: float, hz: float, y0: float, h: float,
          gaps: dict[str, tuple[float, float]]) -> list[dict]:
    """A room's four walls round (cx, cz) with half sizes (hx, hz), floor at y0; `gaps` opens a side ("n", "s", "e",
    "w") between two along-wall offsets from the side's middle."""
    out = []
    for side, (ax, az, length, along_x) in {"n": (0.0, -hz, 2 * hx, True), "s": (0.0, hz, 2 * hx, True),
                                            "w": (-hx, 0.0, 2 * hz, False), "e": (hx, 0.0, 2 * hz, False)}.items():
        pieces = [(-length * 0.5, length * 0.5)]
        if side in gaps:
            g0, g1 = gaps[side]
            pieces = [(-length * 0.5, g0), (g1, length * 0.5)]
        for k, (u0, u1) in enumerate(pieces):
            if u1 - u0 < 0.1:
                continue
            um = (u0 + u1) * 0.5
            x, z = (cx + ax + um, cz + az) if along_x else (cx + ax, cz + az + um)
            sx, sz = (u1 - u0, 0.5) if along_x else (0.5, u1 - u0)
            out.append(box(f"{bid}Wall{side.upper()}{k}", x, y0 + h * 0.5, z, sx, h, sz, color=COL_PARAPET))
    return out


def floor(bid: str, cx: float, cz: float, hx: float, hz: float, y: float, color: str = COL_STONE) -> dict:
    return box(bid, cx, y - WALK_T * 0.5, cz, 2 * hx, WALK_T, 2 * hz, color=color)


# --- Sunken Vey -------------------------------------------------------------------------------------------------------

VEY_IN = [(0.0, 0.0), (22.0, 0.0), (33.0, -8.0), (33.0, -16.0)]  # out along the first gallery, into the court
COURT = (38.0, -22.0, 8.0)  # the conduit court: centre x, z and half size
VEY_SIDE = [(38.0, -30.0), (38.0, -50.0)]  # the side gallery north to the fig-choked end
VEY_OUT = [(46.0, -22.0), (70.0, -16.0), (92.0, -16.0)]  # east to Lowlight's gate


def sunken_vey() -> dict:
    blocks = water(-10.0, 110.0, -70.0, 25.0, color=COL_LAGOON)
    blocks.append(floor("Landing", -6.0, 0.0, 6.0, 6.0, 0.0))
    blocks.append(box("LandingBoundW", -12.5, 1.0, 0.0, 1.0, 2.0, 12.0, color=COL_PARAPET))
    for i, (a, b) in enumerate(zip(VEY_IN, VEY_IN[1:])):
        blocks += gallery(f"GalleryIn{i}", a, b)
    cx, cz, h = COURT
    blocks.append(floor("Court", cx, cz, h, h, 0.0))
    blocks += walls("Court", cx, cz, h, h, 0.0, 1.0, {"s": (-h, -h + WALK_W + 2.0), "n": (-2.5, 2.5),
                                                      "e": (-2.5, 2.5)})
    blocks.append(box("Conduit", cx - 4.0, 1.5, cz - h + 0.6, 3.0, 3.0, 0.8, color=COL_CONDUIT, emission=GLOW_BOUND,
                      emission_energy=0.8))
    blocks += gallery("GallerySide", (cx, cz - h), VEY_SIDE[1])
    blocks.append(floor("FigEnd", VEY_SIDE[1][0], VEY_SIDE[1][1] - 4.0, 4.0, 4.0, 0.0))
    blocks.append(box("Fig", VEY_SIDE[1][0], 3.0, VEY_SIDE[1][1] - 7.5, 7.0, 6.0, 1.5, color=COL_FIG))
    for i, (a, b) in enumerate(zip([(cx + h, cz)] + VEY_OUT[1:], VEY_OUT[1:])):
        blocks += gallery(f"GalleryOut{i}", a, b)
    blocks.append(box("GateBound", 94.5, 1.0, -16.0, 1.0, 2.0, WALK_W + 1.0, color=COL_PARAPET))
    return {
        "doc": "M4-C11-02 greybox (tools/act1/ch11_greybox.py; do not edit by hand): Sunken Vey, the drowned galleries, "
        "at an overcast midday (colour script ch11). A Lit Age city's arcades half under a still turquoise lagoon, "
        "their roofs the walks. From the landing (west) to the conduit court, where a conduit bleeds bound teal and "
        "Liss reads the Saltwright housing-mark (conduit_mark); a side gallery north to a fig-choked end; east to "
        "Lowlight's gate (to_lowlight). The story waits on the beat sheet (M4-C11-01).",
        "sun": SUN,
        "environment": ENV,
        "block_color": COL_STONE,
        "blocks": blocks,
        "spawns": {"Landing": [-4.0, 0.0, 0.0, 270.0], "FromLowlight": [88.0, 0.0, -16.0, 90.0]},
        "marks": {"conduit_mark": [r3(cx - 4.0), 0.0, r3(cz - h + 2.2), 0.0], "fig_end": [38.0, 0.0, -54.0, 0.0]},
        "actors": {},
        "shots": {"V01": {"pos": [-8.0, 3.0, 4.0], "look_at": [30.0, 1.0, -14.0], "fov": 45},
                  # M4-A2P-011 (docs/kb/plan/act2/chapters/ch11.md): C1 the housing-mark insert and the court's
                  # two-shot; Wenna's mark at the fig end
                  "V02": {"pos": [35.5, 1.4, -25.5], "look_at": [r3(cx - 4.0), 1.3, r3(cz - h + 0.8)], "fov": 35},
                  "V03": {"pos": [42.0, 1.7, -20.0], "look_at": [35.5, 1.4, -26.5], "fov": 45},
                  "V04": {"pos": [40.5, 1.6, -49.0], "look_at": [38.0, 1.5, -55.5], "fov": 45}},
        "camera_volumes": follow_volumes("GalleryIn", VEY_IN) + follow_volumes("GallerySide", [(cx, cz - h), VEY_SIDE[1]])
        + follow_volumes("GalleryOut", [(cx + h, cz)] + VEY_OUT[1:])
        + [{"id": "Court", "mode": "pan_follow", "at": [cx, 1.5, cz], "size": [2 * h, 4.0, 2 * h],
            "pos": [r3(cx + h - 1.0), 5.0, r3(cz + h - 1.0)], "look_at": [cx, 0.5, cz], "fov": 55, "priority": 2}],
        "triggers": [{"id": "to_lowlight", "activation": "touch", "at": [92.0, 0.0, -16.0], "size": [2.0, 0, WALK_W],
                      "payload": {"beat": "to_lowlight"}, "yaw": 0.0}],
        # M4-C11-03: the galleries' random fights (act2_roster.md Ch11); none in Lowlight
        "encounters": {"table": [{"encounter": "ch11_vey_rays", "weight": 1}, {"encounter": "ch11_vey_urchins", "weight": 1}],
                       "min_m": 30, "max_m": 50, "when": {"set": ["ch11_started"]}, "seed": 11},
    }


# --- Lowlight ---------------------------------------------------------------------------------------------------------

ATRIUM = (10.0, 0.0, 10.0)  # centre x, z and half size; floor y 0
HALL = (10.0, -26.0, 9.0)  # the Lamp Engine's hall, north of the atrium
LANDING_Y = -4.0
SANCTUM_Y = -8.0
WATERLINE_Y = -2.0  # the temple is drowned below this: the lower flight goes under, the sanctum is underwater
FLIGHTS = (((20.0, 4.0), (36.0, 4.0)), ((40.0, 4.0), (56.0, 4.0)))  # x runs; flight 1 y 0 -> -4, flight 2 -4 -> -8
SANCTUM = (64.0, 4.0, 8.0)
WELL_R = 3.1  # M4-A2P-0411: the collision ring round the well's mouth (env-art's r 3.0)
WELL_SIDES = 10


def lowlight() -> dict:
    blocks = []
    cx, cz, h = ATRIUM
    blocks.append(floor("Atrium", cx, cz, h, h, 0.0))
    blocks += walls("Atrium", cx, cz, h, h, 0.0, 4.0, {"w": (-2.5, 2.5), "n": (-2.5, 2.5), "e": (2.0, 6.0)})
    blocks.append(floor("GateStep", -1.5, 0.0, 1.5, 2.5, 0.0))
    blocks.append(box("GateStepBound", -3.25, 1.0, 0.0, 0.5, 2.0, 5.0, color=COL_PARAPET))
    for side in (-1.0, 1.0):  # the step's sides: walking along the gate must not step off into the water
        blocks.append(box(f"GateStepBound{'NS'[side > 0]}", -1.75, 1.0, side * 2.75, 3.5, 2.0, 0.5, color=COL_PARAPET))
    blocks.append(box("LampBench", cx - 6.0, 0.45, cz + 7.5, 2.4, 0.9, 1.0, color=COL_CONDUIT))
    blocks.append(floor("HallWay", cx, -14.0, 2.5, 4.5, 0.0))
    for s in (-1.0, 1.0):
        blocks.append(box(f"HallWayWall{'WE'[s > 0]}", cx + s * 2.75, 2.0, -14.0, 0.5, 4.0, 9.0, color=COL_PARAPET))
    hx, hz, hh = HALL
    blocks.append(floor("Hall", hx, hz, hh, hh, 0.0))
    blocks += walls("Hall", hx, hz, hh, hh, 0.0, 6.0, {"s": (-2.5, 2.5)})
    blocks.append(box("LampEngine", hx, 3.0, hz - 4.0, 6.0, 6.0, 4.0, color=COL_CONDUIT, emission=GLOW_BOUND,
                      emission_energy=1.2))
    ramps = []
    ys = ((0.0, LANDING_Y), (LANDING_Y, SANCTUM_Y))
    for i, ((a, b), (y0, y1)) in enumerate(zip(FLIGHTS, ys)):
        ramps.append({"id": f"Flight{i + 1}", "from": [a[0], y0, a[1]], "to": [b[0], y1, b[1]], "width": 3.0,
                      "color": COL_STONE})
        for s in (-1.0, 1.0):  # the shaft's walls either side of each flight
            blocks.append(box(f"Flight{i + 1}Wall{'NS'[s > 0]}", (a[0] + b[0]) * 0.5, (y0 + y1) * 0.5 + 1.5,
                              a[1] + s * 1.75, b[0] - a[0], abs(y1 - y0) + 4.0, 0.5, color=COL_PARAPET))
    blocks.append(floor("ShaftLanding", 38.0, 4.0, 2.0, 1.5, LANDING_Y))
    for s in (-1.0, 1.0):
        blocks.append(box(f"ShaftLandingWall{'NS'[s > 0]}", 38.0, LANDING_Y + 2.0, 4.0 + s * 1.75, 4.0, 4.0, 0.5,
                          color=COL_PARAPET))
    sx, sz, sh = SANCTUM
    blocks.append(floor("Sanctum", sx, sz, sh, sh, SANCTUM_Y))
    blocks += walls("Sanctum", sx, sz, sh, sh, SANCTUM_Y, 10.0, {"w": (-1.5, 1.5)})
    blocks.append(box("WellShaft", sx, SANCTUM_Y + 14.0, sz, 6.0, 0.2, 6.0, color=COL_LAGOON, solid=False))
    # M4-A2P-0411: the well's mouth is open in the sanctum's floor (env-art's well_shaft, r 3.0); a low collision ring
    # (r 3.1, hidden under the dressing like the rest) keeps the party round it, never over it
    for k in range(WELL_SIDES):
        a = 2 * math.pi * (k + 0.5) / WELL_SIDES
        blocks.append(box(f"WellRim{k}", r3(sx + WELL_R * math.cos(a)), SANCTUM_Y + 0.3, r3(sz + WELL_R * math.sin(a)),
                          r3(2 * WELL_R * math.tan(math.pi / WELL_SIDES) + 0.3), 0.6, 0.4, r3(-math.degrees(a) + 90.0),
                          color=COL_PARAPET))
    blocks.append(box("Waterline", 52.0, WATERLINE_Y - 0.05, 4.0, 40.0, 0.1, 20.0, color=COL_LAGOON, solid=False))
    return {
        "doc": "M4-C11-02 greybox (tools/act1/ch11_greybox.py; do not edit by hand): Lowlight, the temple half "
        "underwater (colour script ch11). The atrium at the gate (Gate; the lamp bench for Rhen and Liss's side scene, "
        "lamp_bench), the Lamp Engine's hall north of it (EngineHall: the boss's arena, its conduits bleeding bound "
        "teal), and east the well-shaft: two flights down (ramps) past the waterline (y -2: the temple is drowned "
        "below it) to the drowned sanctum at the shaft's foot (Sanctum, nhoa: Nhoa's binding; the light from the "
        "well-shaft above). Back to Sunken Vey at to_vey. The story, and whether the lower temple is swum or walked, "
        "wait on the beat sheet (M4-C11-01).",
        "sun": SUN,
        "environment": ENV,
        "block_color": COL_STONE,
        "blocks": blocks,
        "ramps": ramps,
        "spawns": {"Gate": [2.0, 0.0, 0.0, 270.0], "EngineHall": [10.0, 0.0, -20.0, 180.0],
                   "Sanctum": [r3(sx - 4.0), SANCTUM_Y, r3(sz), 270.0]},
        "marks": {"lamp_bench": [r3(cx - 6.0), 0.0, r3(cz + 6.4), 0.0], "nhoa": [r3(sx + 4.0), SANCTUM_Y, r3(sz), 90.0],
                  "pell_kneel": [r3(sx + 3.2), SANCTUM_Y, r3(sz + 1.6), 90.0]},  # M4-A2P-011: C3, before his sister
        # M4-A2P-0411: the Lamp Engine stands in its hall as creatures' model (the dressing hides the block)
        "actors": {"lamp_engine": {"at": [hx, 0.0, r3(hz - 4.0), 180.0], "cast": "creature:lamp_engine",
                                   "color": COL_CONDUIT, "radius": 2.0, "height": 3.4}},
        "shots": {"L01": {"pos": [r3(sx - 6.0), SANCTUM_Y + 1.8, r3(sz + 5.0)], "look_at": [r3(sx + 4.0), SANCTUM_Y + 3.0,
                                                                                         r3(sz)], "fov": 50},
                  # M4-A2P-011: C2 the Engine hall and its bared core; C3 down the shaft, the sanctum, Pell kneeling;
                  # C4 the lamp bench
                  "L02": {"pos": [16.0, 4.0, -19.0], "look_at": [hx, 2.5, r3(hz - 1.5)], "fov": 55},
                  "L03": {"pos": [12.0, 0.8, -25.0], "look_at": [hx, 4.0, r3(hz - 1.8)], "fov": 55},
                  "L04": {"pos": [17.0, 2.5, 4.0], "look_at": [34.0, -3.0, 4.0], "fov": 50},
                  "L05": {"pos": [r3(sx - 6.0), SANCTUM_Y + 2.5, r3(sz - 4.0)], "look_at": [r3(sx + 4.0), SANCTUM_Y + 1.5,
                                                                                          r3(sz)], "fov": 45},
                  "L06": {"pos": [r3(sx + 3.2), SANCTUM_Y + 1.2, r3(sz - 3.5)], "look_at": [r3(sx + 3.2), SANCTUM_Y + 1.0,
                                                                                            r3(sz + 1.6)], "fov": 40},
                  "L07": {"pos": [r3(cx - 4.5), 1.3, r3(cz + 5.8)], "look_at": [r3(cx - 6.0), 0.9, r3(cz + 7.5)], "fov": 35}},
        "camera_volumes": [
            {"id": "Atrium", "mode": "pan_follow", "at": [cx, 1.5, cz], "size": [2 * h, 4.0, 2 * h],
             "pos": [r3(cx + h - 1.5), 5.0, r3(cz + h - 1.5)], "look_at": [cx, 0.5, cz], "fov": 55, "priority": 1},
            {"id": "Hall", "mode": "pan_follow", "at": [hx, 1.5, r3(hz + 3.0)], "size": [2 * hh, 4.0, r3(2 * hh + 10.0)],
             "pos": [11.88, 5.0, -13.61], "look_at": [hx, 1.0, hz], "fov": 55, "priority": 1},
            {"id": "Flight1", "mode": "pan_follow", "at": [28.0, -2.0, 4.0], "size": [18.0, 6.0, 3.5],
             "pos": [17.0, 3.0, 4.0], "look_at": [30.0, -2.0, 4.0], "fov": 50, "priority": 1},
            {"id": "Flight2", "mode": "pan_follow", "at": [47.0, -6.0, 4.0], "size": [20.0, 6.0, 3.5],
             "pos": [37.0, -1.0, 4.0], "look_at": [50.0, -6.0, 4.0], "fov": 50, "priority": 1},
            {"id": "Sanctum", "mode": "pan_follow", "at": [sx, SANCTUM_Y + 1.5, sz], "size": [2 * sh, 4.0, 2 * sh],
             "pos": [r3(sx - sh + 1.5), SANCTUM_Y + 4.0, r3(sz + sh - 1.5)], "look_at": [sx, SANCTUM_Y + 0.5, sz], "fov": 55,
             "priority": 2}],
        "triggers": [{"id": "to_vey", "activation": "touch", "at": [-0.5, 0.0, 0.0], "size": [1.0, 0, 4.0],
                      "payload": {"beat": "to_vey"}, "yaw": 0.0}],
    }


def main() -> None:
    for name, layout in (("sunken_vey", sunken_vey()), ("lowlight", lowlight())):
        out = ZONES / name / f"{name}_layout.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
