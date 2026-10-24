"""Generates the Pemakar kit preview layout (M3-ENV-03): the town's ten tiers dressed from the kit, the
Lanternfall leaf-boats and lights, the skyline. Plain python3 + numpy, deterministic.

    python3 assets_src/environments/kits/pemakar/pemakar_layout.py [--out game/levels/_tests/pemakar_kit/pemakar_preview_layout.json]

The JSON is what game/levels/_tests/pemakar_kit/pemakar_kit_preview.gd places (explicit transforms, so
m2-slice can copy pieces straight into the zone layout, as with the Haluna route layout). Geometry rules
(pemakar.md §0): tier t's tread front is an arc of radius TOWN_R0_M - 7 t about TOWN_CENTRE at height
TOWN_Y0_M + 2.4 t; a module's yaw turns its local +Z outward (downhill) and its local +X along the
contour toward the east. Every tier's channel runs from an inlet at one end to a spill at the other,
alternating ends, so the water (and the boats) zig-zag down the mountain:
    tier 9 flows east, spills into tier 8's east end; tier 8 flows west ... tier 0 spills to the sea road.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import pemakar_common as pc  # noqa: E402
import pemakar_skyline as sky  # noqa: E402
import pemakar_terraces as pt  # noqa: E402

kc = pc.kc
OUT_DEFAULT = ROOT / "game" / "levels" / "_tests" / "pemakar_kit" / "pemakar_preview_layout.json"
SEED = 5
TIER_KINDS = ["market", "house", "house", "paddy", "cemetery", "cemetery", "paddy", "cemetery", "cemetery", "cemetery"]
X_HALF_M = 44.0  # each tier spans x in [-X_HALF_M, X_HALF_M]
CHANNEL_END_MARGIN_M = 3.0  # channels stop this far inside a tier's end
STAIR_CLEAR_M = 3.4  # nothing but the stair, gate and lamps within this of x = 0
COPPER_X_M = 14.0  # the Lit Age vein runs down the tiers here
GAP_X_M = 1.70  # inlet gap centre from the inlet module's centre (pemakar_terraces.channel)
SPILL_X_M = pc.CHANNEL_IN_M * 0.5  # cross channel centre in the spill's frame
LAMP = "#FFA757"  # ch05 lamp key (color script)
BOAT_SPACING_M = (0.45, 1.5)
CHANNEL_LIGHT_STEP_M = 4.5
GRAVE_ROWS_Z = (-3.3, -5.1)
GRAVE_STEP_M = (1.5, 2.6)
GRAVE_LIGHT_EVERY = 3
TREE_STEP_M = 11.0
FAR_LIGHT_LEVELS = (40.0, 262.0, 9.6)  # massif band contours that carry far lights: from, to, step (m)


def anchor(t: int, theta: float, local=(0.0, 0.0, 0.0)) -> np.ndarray:
    """World position of a point given in the tier-t anchor frame at arc angle theta."""
    r = pc.TOWN_R0_M - pc.TREAD_D_M * t
    base = np.array([pc.TOWN_CENTRE[0] + r * math.sin(theta), float(pc.tier_tread_y(t)),
                     pc.TOWN_CENTRE[1] + r * math.cos(theta)])
    lx, ly, lz = local
    return base + np.array([lx * math.cos(theta) + lz * math.sin(theta), ly, -lx * math.sin(theta) + lz * math.cos(theta)])


def tread_rise(z: float) -> float:
    """How far a tread stands above its front edge at local z (it rises TREAD_FALL_M to its back)."""
    return pt.TREAD_FALL_M * min(max((-z - 0.25) / (pc.TREAD_D_M - 0.25), 0.0), 1.0)


def radius(t: int) -> float:
    return pc.TOWN_R0_M - pc.TREAD_D_M * t


def angle_of(p: np.ndarray) -> float:
    return math.atan2(p[0] - pc.TOWN_CENTRE[0], p[2] - pc.TOWN_CENTRE[1])


def piece(name: str, at: np.ndarray, yaw: float, **extra) -> dict:
    d = {"piece": name, "at": [round(float(v), 3) for v in at], "yaw_deg": round(math.degrees(yaw), 3)}
    d.update(extra)
    return d


def light(at: np.ndarray, energy: float, rng_m: float, **extra) -> dict:
    d = {"at": [round(float(v), 3) for v in at], "color": LAMP, "energy": energy, "range": rng_m}
    d.update(extra)
    return d


def module_angles(t: int) -> list[float]:
    r = radius(t)
    step = 2.0 * math.asin(pc.MODULE_M * 0.5 / r)
    n = int(2.0 * math.asin(X_HALF_M / r) / step)
    n -= 1 - n % 2  # odd, so one module is centred on x = 0 (the stair)
    return [(k - (n - 1) * 0.5) * step for k in range(n)]


def build(seed: int = SEED) -> dict:
    rng = np.random.default_rng(np.random.SeedSequence([seed, 2026]))
    pieces: list[dict] = []
    lights: list[dict] = []
    boats: list[list[float]] = []
    plants: list[dict] = []
    channels: list[dict] = []  # per tier: the channel run (for tests and the swap-in note)
    cross_angles: dict[int, float] = {}  # tier -> arc angle where the cross channel from above crosses it

    # --- walls, treads, stairs, gates, lamps -------------------------------------------------------
    for t in range(pc.TOWN_TIERS):
        angles = module_angles(t)
        copper_k = int(np.argmin([abs(radius(t) * math.sin(a) - COPPER_X_M) for a in angles]))
        for k, a in enumerate(angles):
            centre = len(angles) // 2
            wall = "stair_flight" if k == centre else ("terrace_wall_copper" if k == copper_k else "terrace_wall_4m")
            pieces.append(piece(wall, anchor(t, a), a))
            tread = "paddy_tread_4m" if TIER_KINDS[t] == "paddy" else "terrace_tread_4m"
            pieces.append(piece(tread, anchor(t, a), a))
        # Lamp pillars at the stair head (on this tread) and at its foot (on the tread below).
        for sx in (-1.0, 1.0):
            head = anchor(t, 0.0, (sx * 2.3, 0.0, -1.55))
            pieces.append(piece("lamp_pillar", head, 0.0))
            lights.append(light(head + [0, 1.35, 0], 1.6, 6.0))
            foot = anchor(t, 0.0, (sx * 1.55, -pc.WALL_H_M, 4.75))
            pieces.append(piece("lamp_pillar", foot, 0.0))
            lights.append(light(foot + [0, 1.35, 0], 1.6, 6.0))
        if TIER_KINDS[t] == "cemetery":
            pieces.append(piece("open_hand_gate", anchor(t, 0.0, (0.0, 0.02, -2.05)), 0.0))

    # --- channels, spills, boats, channel lights: top tier first ------------------------------------
    flow = 1  # tier 9 flows east
    inlet_theta = None
    for t in reversed(range(pc.TOWN_TIERS)):
        r = radius(t)
        step = 2.0 * math.asin(pc.MODULE_M * 0.5 / r)
        side = "r" if flow > 0 else "l"
        if inlet_theta is None:  # the top tier's water comes from a culvert at its west end
            first = math.asin((-X_HALF_M + CHANNEL_END_MARGIN_M + 2.0) / r)
        else:
            first = inlet_theta - flow * GAP_X_M / r
        mods = [first]
        while True:
            nxt = mods[-1] + flow * step
            x_edge = r * math.sin(nxt + flow * step * 0.5)
            if abs(x_edge) > X_HALF_M - CHANNEL_END_MARGIN_M:
                break
            mods.append(nxt)
        for i, a in enumerate(mods):
            name = f"terrace_channel_inlet_{side}" if i == 0 else "terrace_channel_4m"
            pieces.append(piece(name, anchor(t, a, (0.0, 0.0, -pc.CHANNEL_Z_M)), a))
        end = mods[-1] + flow * step * 0.5
        pieces.append(piece(f"terrace_spill_{side}", anchor(t, end), end))
        gap = first - flow * GAP_X_M / r
        channels.append({"tier": t, "flow": "east" if flow > 0 else "west", "modules": len(mods),
                         "from_deg": round(math.degrees(gap), 3), "to_deg": round(math.degrees(end), 3)})
        # Boats along the channel (the water centre line at radius r - CHANNEL_Z_M), lights above them.
        rc = r - pc.CHANNEL_Z_M
        length = abs(end - gap) * rc
        s = float(rng.uniform(0.0, 1.0))
        y_water = float(pc.tier_tread_y(t)) + pc.CHANNEL_WATER_M + 0.004
        while s < length - 0.3:
            a = gap + flow * s / rc
            lat = float(rng.uniform(-0.07, 0.07))
            p = np.array([rc * math.sin(a) + pc.TOWN_CENTRE[0], y_water, rc * math.cos(a) + pc.TOWN_CENTRE[1]])
            p += np.array([math.sin(a), 0.0, math.cos(a)]) * lat
            yaw = math.pi * 0.5 - a + float(rng.normal(0.0, 0.4))
            boats.append([round(float(p[0]), 3), round(float(p[1]), 3), round(float(p[2]), 3), round(yaw, 3)])
            s += float(rng.uniform(*BOAT_SPACING_M))
        s = CHANNEL_LIGHT_STEP_M * 0.5
        while s < length:
            a = gap + flow * s / rc
            p = np.array([rc * math.sin(a) + pc.TOWN_CENTRE[0], y_water + 0.3, rc * math.cos(a) + pc.TOWN_CENTRE[1]])
            lights.append(light(p, 1.4, 4.0))
            s += CHANNEL_LIGHT_STEP_M
        # The spill's basin and cross channel (on the tier below): boats drifting, one light.
        spill_frame = lambda lx, ly, lz, end=end, t=t: anchor(t, end, (lx, ly, lz))  # noqa: E731
        sx = SPILL_X_M if side == "r" else -SPILL_X_M
        basin = spill_frame(sx, -pc.WALL_H_M + 0.27 + 0.004, pc.SPILL_BASIN_Z_M)
        for _ in range(2):
            q = basin + np.array([rng.uniform(-0.25, 0.25), 0.0, 0.0]) + np.array([0.0, 0.0, rng.uniform(-0.1, 0.1)])
            boats.append([round(float(q[0]), 3), round(float(q[1]), 3), round(float(q[2]), 3),
                          round(float(rng.uniform(0, math.pi)), 3)])
        lights.append(light(basin + [0, 0.35, 0], 0.7, 3.2))
        lip = spill_frame(sx, pc.CHANNEL_WATER_M + 0.004, 0.3)
        boats.append([round(float(lip[0]), 3), round(float(lip[1]), 3), round(float(lip[2]), 3), round(-end, 3)])
        z0, z1 = pc.SPILL_BASIN_Z_M + 0.6, pc.TREAD_D_M - pc.CHANNEL_Z_M - 0.4
        zz = z0 + float(rng.uniform(0.0, 0.6))
        while zz < z1:
            y = -pc.WALL_H_M + tread_rise(zz - pc.TREAD_D_M) + 0.02 + pc.CHANNEL_WATER_M
            q = spill_frame(sx + float(rng.uniform(-0.05, 0.05)), y, zz)
            boats.append([round(float(q[0]), 3), round(float(q[1]), 3), round(float(q[2]), 3),
                          round(float(-end + rng.normal(0, 0.3)), 3)])
            zz += float(rng.uniform(*BOAT_SPACING_M))
        if t > 0:
            cross = spill_frame(sx, 0.0, 3.0)
            cross_angles[t - 1] = angle_of(cross)
            inlet_theta = angle_of(spill_frame(sx, 0.0, pc.TREAD_D_M - pc.CHANNEL_Z_M))
        flow = -flow

    # --- graves, trees, houses, the smithy, the outcrop ---------------------------------------------
    for t in range(pc.TOWN_TIERS):
        r = radius(t)
        a_max = math.asin((X_HALF_M - 1.5) / r)
        cross = cross_angles.get(t)
        kind = TIER_KINDS[t]
        if kind == "cemetery":
            for row, z in enumerate(GRAVE_ROWS_Z):
                a = -a_max + float(rng.uniform(0.0, 1.0)) / r
                n = 0
                while a < a_max:
                    x = (r + z) * math.sin(a)
                    clear = abs(x) > STAIR_CLEAR_M and (cross is None or abs(a - cross) * r > 1.3)
                    if clear:
                        roll = float(rng.random())
                        name = ("grave_stele_a" if roll < 0.55 else "grave_stele_b" if roll < 0.72 else
                                "grave_cairn" if roll < 0.88 else "grave_curb")
                        jitter = (float(rng.uniform(-0.15, 0.15)), 0.0, z + float(rng.uniform(-0.25, 0.25)))
                        pos = anchor(t, a, jitter)
                        pos[1] += tread_rise(jitter[2])
                        yaw = a + float(rng.normal(0.0, 0.08))
                        pieces.append(piece(name, pos, yaw))
                        if name != "grave_curb" and n % GRAVE_LIGHT_EVERY == row % GRAVE_LIGHT_EVERY:
                            lights.append(light(anchor(t, a, (jitter[0], 1.05 + pos[1] - pc.tier_tread_y(t), z + 0.45)),
                                                0.7, 3.0))
                        n += 1
                    a += float(rng.uniform(*GRAVE_STEP_M)) / (r + z)
            a = -a_max + 2.0 / r
            while a < a_max:
                x = r * math.sin(a)
                if abs(x) > STAIR_CLEAR_M + 1.5 and (cross is None or abs(a - cross) * r > 2.5):
                    plants.append({"plant": "frangipani_a" if rng.random() < 0.5 else "frangipani_b",
                                   "at": [round(float(v), 3) for v in anchor(t, a, (0.0, 0.13, -6.1))],
                                   "yaw_deg": round(float(rng.uniform(0, 360)), 1),
                                   "scale": round(float(rng.uniform(0.75, 1.05)), 3)})
                a += (TREE_STEP_M + float(rng.uniform(-2.0, 2.0))) / r
        elif kind in ("house", "market"):
            a = -a_max + 3.5 / r
            k = 0
            smithy_done = kind != "market"
            while a < a_max - 3.0 / r:
                x = r * math.sin(a)
                near_ore = t == 1 and abs(x - COPPER_X_M - 1.5) < 5.0
                if abs(x) < STAIR_CLEAR_M + 2.5 or near_ore or (cross is not None and abs(a - cross) * r < 4.0):
                    a += 2.0 / r
                    continue
                if not smithy_done and x > 18.0:
                    name, z, half_w = "smithy", -3.8, 3.7
                    smithy_done = True
                    pieces.append(piece(name, anchor(t, a, (0.0, tread_rise(z + 2.5), z)), a))
                    lights.append(light(anchor(t, a, (-1.4, 1.2, z - 0.8)), 2.2, 6.0, color="#E0702E", shadow=True))
                else:
                    name = "house_pemakar_a" if k % 2 == 0 else "house_pemakar_b"
                    z, half_w = (-4.3, 2.6) if name == "house_pemakar_a" else (-4.55, 2.1)
                    yaw = a + float(rng.normal(0.0, 0.03))
                    pieces.append(piece(name, anchor(t, a, (0.0, tread_rise(z + 3.0), z)), yaw,
                                        materials={"kit_interior_dark": "kit_interior_lit"}))
                    front = 3.0 if name == "house_pemakar_a" else 3.25
                    pieces.append(piece("shrine_box", anchor(t, a, (-half_w - 0.35, 0.07, z + front + 0.2)), yaw))
                    lights.append(light(anchor(t, a, (0.0, 2.2, z + front + 0.7)), 0.7, 3.8))
                    k += 1
                a += (2.0 * half_w + float(rng.uniform(2.5, 5.0))) / r
        if t == 1:
            a = math.asin((COPPER_X_M + 1.5) / r)
            pieces.append(piece("copper_outcrop", anchor(t, a, (0.0, 0.05, -5.6)), a + 0.2))

    # --- skyline and far lights -------------------------------------------------------------------
    pieces.append(piece("mountain_massif", np.zeros(3), 0.0))
    rim = np.array(sky.massif_rim_point())
    pieces.append(piece("ashcrown_silhouette", rim, 0.0))
    vent_noise = kc.Noise3(kc.rng_for("mountain_massif", 801))
    vent_y = float(sky.massif_height(np.array([pc.CROWN[0]]), np.array([pc.CROWN[1]]), vent_noise)[0])
    pieces.append(piece("ash_plume", np.array([pc.CROWN[0], vent_y - 10.0, pc.CROWN[1]]), 0.0))
    far = far_lights(rng)
    return {
        "schema": "hymn-zone-layout/1",
        "zone": "ch05/pemakar kit preview (M3-ENV-03)",
        "_about": ("Generated by assets_src/environments/kits/pemakar/pemakar_layout.py; do not hand-edit. "
                   "Coordinates are the town's (origin at its foot at sea level; x east, z south). Placed by "
                   "pemakar_kit_preview.gd. Pieces, plants and lights copy straight into the ch05/pemakar zone layout."),
        "seed": seed,
        "kit_dir": "res://assets/environments/kits/pemakar/",
        "materials_dir": "res://assets/environments/kits/pemakar/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 4000.0,
        "lod_margin_m": 2.0,
        "pieces": pieces,
        "channels": channels,
        "boats": {"piece": "leaf_boat_lit", "transforms": boats},
        "lights": lights,
        "far_lights": far,
        "plants": plants,
        "plant_kinds": {
            name: {"glb": f"res://assets/environments/vegetation/{name}.glb",
                   "materials": {"frangipani_bark": "res://assets/environments/vegetation/materials/frangipani_bark.tres",
                                 "frangipani_leaf": "res://assets/environments/vegetation/materials/frangipani_leaf.tres"}}
            for name in ("frangipani_a", "frangipani_b")
        },
    }


def far_lights(rng: np.random.Generator) -> dict:
    """Leaf-boat lights on the massif's far terrace bands: lit segments along contours of the south face,
    with a short drop between bands at alternating ends (the zig-zag continued up the mountain)."""
    noise = kc.Noise3(kc.rng_for("mountain_massif", 801))
    pts: list[list[float]] = []
    lo, hi, stepm = FAR_LIGHT_LEVELS
    angles = np.arange(-0.95, 0.95, 0.0045)
    for level in np.arange(lo, hi, stepm):
        gate = noise.fbm(np.stack([np.cos(angles) * 9.0, np.full(angles.shape, level / 20.0), np.sin(angles) * 9.0],
                                  axis=-1), 2)
        a = angles[gate >= 0.5]
        # Bisect along each radial line from the crown for where the massif reaches this band.
        r0 = np.full(a.shape, pc.CALDERA_R_M + 30.0)
        r1 = np.full(a.shape, pc.CROWN_FOOT_R_M)
        for _ in range(22):
            rm = 0.5 * (r0 + r1)
            h = sky.massif_height(pc.CROWN[0] + rm * np.sin(a), pc.CROWN[1] + rm * np.cos(a), noise)
            above = h > level
            r0 = np.where(above, rm, r0)
            r1 = np.where(above, r1, rm)
        x = pc.CROWN[0] + r1 * np.sin(a)
        z = pc.CROWN[1] + r1 * np.cos(a)
        h = sky.massif_height(x, z, noise)
        keep = ~((np.abs(x) < 70.0) & (z > -110.0))  # not in the town itself
        for xi, hi_, zi in zip(x[keep], h[keep], z[keep]):
            pts.append([round(float(xi), 2), round(float(hi_) + 0.4, 2), round(float(zi), 2)])
    return {"color": LAMP, "energy": 3.0, "size_m": [0.9, 2.6], "points": pts}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args(argv)
    data = build()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(f"PEMAKAR_LAYOUT {len(data['pieces'])} pieces, {len(data['boats']['transforms'])} boats, "
          f"{len(data['lights'])} lights, {len(data['far_lights']['points'])} far lights, {len(data['plants'])} plants")
    return 0


if __name__ == "__main__":
    sys.exit(main())
