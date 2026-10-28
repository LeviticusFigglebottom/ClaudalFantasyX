#!/usr/bin/env python3
"""env-art's walk-through pass over the Prologue–Ch4 zones (the Lead's 10-28 ask): each zone's critical path as
legs of waypoints (x, z) on the ground, sampled every WALK_STEP_M (closer on a short zone, so each zone gets at
least MIN_POINTS), a camera at the player's eye at each sample looking on along the leg. The Prologue has no player
(its camera is the cinematic's); it is walked at a player's eye anyway.

    python3 tools/act1/walkthrough.py --out DIR [--zone ID ...]

writes DIR/<zone>/walk.json for game/levels/_tests/walkthrough/walk_render.tscn, and prints the godot-render line
that renders it (frames to DIR/<zone>/). A waypoint with three numbers is an eye height given outright (x, y, z): an
interior whose roof would catch the renderer's ground ray.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

WALK_STEP_M = 30.0
MIN_POINTS = 6
LOOK_AHEAD_M = 12.0

# zone id -> (level, spawn, flags, legs). The legs follow each chapter's beats (spawns and triggers in order); a new
# leg is a cut in the walk (a drop, a door, a boat).
ZONES: dict[str, tuple[str, str, list[str], list[list[tuple[float, ...]]]]] = {
    # The Prologue has no player (its camera is the cinematic's); walked anyway at a player's eye through Iskarra:
    # the arrival line to the gate, the plaza across, the vigil line.
    "prologue": ("res://game/levels/prologue/prologue.tscn", "Start", [], [
        [(1.5, 21.0), (1.0, 6.0), (-4.0, -20.0), (-4.0, -45.0)], [(8.0, 6.5), (24.0, -6.0)],
        [(-12.0, 1.5), (9.5, -5.5)]]),
    "ch01_oruvel": ("res://game/levels/ch01/oruvel/oruvel.tscn", "ScaleHull", [], [
        [(0.0, 13.0), (0.0, 2.0), (0.0, -6.0), (-12.0, -6.0), (-12.0, -16.5), (0.0, -20.0), (0.0, -34.0)],
        [(0.0, -6.0), (12.5, -7.0), (23.0, -6.0), (35.0, -6.0), (45.0, -5.0), (45.0, -11.5)],
        [(45.0, -14.0), (41.5, -17.0), (35.0, -17.5), (30.0, -21.0)]]),
    "ch01_underway": ("res://game/levels/ch01/oruvel_underway/oruvel_underway.tscn", "Drop", ["ch01_started"], [
        [(0.0, 15.0), (0.0, 5.0), (0.0, -2.0)],
        [(40.0, 12.0), (42.0, 6.0), (44.0, 3.0)],
        [(80.0, 17.0), (80.0, 9.0), (80.0, -2.0), (80.0, -20.0), (80.0, -31.0)],
        [(80.0, -26.0), (88.0, -26.0), (96.0, -31.0), (97.0, -36.0)]]),
    "ch02_haluna": ("res://game/levels/ch02/haluna/haluna.tscn", "Beach", ["prologue_seen", "ch02_met_asha"], [
        [(-1.0, 8.0), (-13.0, 6.5), (-24.0, 6.5), (-40.0, 3.0), (-52.0, -2.6)],
        [(-52.0, -2.6), (-60.0, 20.0), (-67.0, 44.3)],
        [(-52.0, -2.6), (-30.0, -40.0), (-10.0, -80.0), (4.0, -118.0)],
        [(-24.0, 6.5), (0.0, 30.0), (13.7, 46.2)]]),
    # What the player touches in Haluna (the shop, the smith, the inn, the save shrine), each from the customer's side.
    "ch02_haluna_touch": ("res://game/levels/ch02/haluna/haluna.tscn", "Beach", ["prologue_seen", "ch02_met_asha"], [
        [(-40.0, 0.4), (-34.0, -1.0)], [(-7.0, 48.0), (-13.5, 51.0)], [(-24.5, 55.5), (-30.0, 59.5)],
        [(-67.0, 41.0), (-67.0, 46.6)]]),
    "ch03_causeway": ("res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn", "FromHaluna",
                      ["prologue_seen", "ch02_met_asha", "ch02_tideline_won", "ch02_ate_at_nemes"], [
        [(1.35, -0.65), (28.6, -14.4), (58.7, -37.7), (76.0, -47.4), (111.0, -70.1), (170.0, -125.0),
         (231.2, -177.5)]]),
    "ch03_shell_shrine": ("res://game/levels/ch03/shell_shrine/shell_shrine.tscn", "Entry", ["ch02_met_asha"], [
        [(-20.0, 1.65, 0.0), (-12.5, 1.7, 0.0), (-4.0, 1.7, 0.0), (4.0, 1.7, 0.0), (12.3, 1.7, 0.0)]]),
    "ch04_ferry": ("res://game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn", "Landing", [], [
        [(13.0, 7.9), (1.5, 7.9), (2.8, 10.4), (0.0, 16.6), (0.0, 4.0), (0.0, -1.5)],
        [(-7.8, 18.3), (-8.1, 15.1), (-9.24, 12.3), (-9.24, 8.6), (-9.24, 3.5)]]),
    "ch04_wake": ("res://game/levels/ch04/haluna_wake/haluna_wake.tscn", "DockShore", [], [
        [(23.5, 39.35), (10.0, 50.0), (-2.7, 57.7), (-30.0, 57.5)],
        [(-30.0, 57.5), (-50.0, 20.0), (-58.0, -3.6)],
        [(-58.0, -3.6), (-40.0, -50.0), (-4.0, -100.0), (5.0, -110.0), (-12.5, -118.0)]]),
}


def _sample(leg: list[tuple[float, ...]], step: float) -> list[tuple[tuple[float, ...], tuple[float, ...]]]:
    """(at, look) every `step` along a polyline; the look LOOK_AHEAD_M on along it (or past its end)."""
    pts = [tuple(float(c) for c in p) for p in leg]

    def xz(p: tuple[float, ...]) -> tuple[float, float]:
        return (p[0], p[-1])

    segs = [(pts[i], pts[i + 1], math.dist(xz(pts[i]), xz(pts[i + 1]))) for i in range(len(pts) - 1)]
    total = sum(s[2] for s in segs)

    def at(d: float) -> tuple[float, ...]:
        d = max(0.0, d)
        for a, b, n in segs:
            if d <= n or (a, b, n) == segs[-1]:
                t = d / n if n > 0 else 0.0
                return tuple(a[k] + (b[k] - a[k]) * t for k in range(len(a)))
            d -= n
        return pts[-1]

    out = []
    count = max(1, round(total / step))
    for i in range(count + 1):
        d = total * i / count
        here = at(min(d, total - 0.01))
        ahead = at(min(d + LOOK_AHEAD_M, total)) if d + 1.0 < total else None
        if ahead is None or math.dist(xz(ahead), xz(here)) < 0.5:
            a, b, _ = segs[-1]
            ahead = tuple(b[k] + (b[k] - a[k]) for k in range(len(b)))
        out.append((here, ahead))
    return out


def walk(zone: str) -> dict:
    level, spawn, flags, legs = ZONES[zone]
    length = sum(math.dist((p[0], p[-1]), (q[0], q[-1])) for leg in legs for p, q in zip(leg, leg[1:]))
    step = min(WALK_STEP_M, length / MIN_POINTS)
    points = []
    for li, leg in enumerate(legs):
        for k, (here, ahead) in enumerate(_sample(leg, step)):
            look = list(ahead) if len(here) == 3 else [ahead[0], ahead[-1]]
            if len(here) == 3 and len(look) == 2:
                look = [look[0], here[1], look[1]]
            points.append({"id": f"{zone}_l{li + 1}_{k:02d}", "at": [round(c, 3) for c in here],
                           "look": [round(c, 3) for c in look]})
    return {"level_path": level, "spawn": spawn, "flags": flags, "points": points}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--zone", action="append", choices=sorted(ZONES))
    args = ap.parse_args()
    for zone in args.zone or sorted(ZONES):
        d = Path(args.out) / zone
        d.mkdir(parents=True, exist_ok=True)
        w = walk(zone)
        (d / "walk.json").write_text(json.dumps(w, indent=1) + "\n", encoding="utf-8")
        print(f"{zone}: {len(w['points'])} points\n  godot-render --path . --audio-driver Dummy --fixed-fps 60 "
              f"--disable-vsync --rendering-driver vulkan res://game/levels/_tests/walkthrough/walk_render.tscn -- "
              f"--walk={d / 'walk.json'} --out={d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
