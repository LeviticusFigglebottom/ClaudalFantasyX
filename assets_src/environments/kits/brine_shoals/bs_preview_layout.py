"""Writes the Brine Shoals preview layout (M3-ENV-02): game/levels/_tests/brine_shoals_kit/brine_shoals_layout.json.

    python3 assets_src/environments/kits/brine_shoals/bs_preview_layout.py

The layout is HalunaDresser's format (hymn-zone-layout/1, no terrain: every piece carries its own "y"),
plus "fire_lights" for BrineShoalsPreview. It composes the design notes' key shots (brine_shoals.md §4):
a 6 x 8 block of 24 m ground cells with the shoal channel down x = 0 (cells alternating a and b, so it
meanders), the camp on its hard on the east bank, the plank walk in from the east past the wrecks, the
tideline on the hard's west and south flanks, the barge in the channel to the south, and a kit row of
intact / burned pairs on a second hard to the north-east for review (B11).

Heights come from the kit's own height functions with each piece's seed (bs_ground), so props sit on the
generated ground exactly. m2-slice copies the pieces it wants (docs/kb/handoffs/live/env-art.md).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import bs_ground as bg  # noqa: E402
from bs_common import kc  # noqa: E402

OUT = ROOT / "game" / "levels" / "_tests" / "brine_shoals_kit" / "brine_shoals_layout.json"
COL_X = (-48.0, -24.0, 0.0, 24.0, 48.0, 72.0)  # x = 0 is the channel column
ROW_Z = tuple(-84.0 + 24.0 * k for k in range(8))
HARD = (20.0, 0.0, 90.0)  # x, z, yaw (deg): long axis north-south along the channel's east bank
SHEET_HARD = (150.0, -150.0, 0.0)
WIND_TO_AZ = 240.0  # an offshore breeze from the east-north-east lays the smoke south-west, across the channel


def _noise(name: str, seed: int) -> kc.Noise3:
    return kc.Noise3(kc.rng_for(name, seed))


NOISE = {
    "mudflat_patch_a": _noise("mudflat_patch_a", 201),
    "mudflat_patch_b": _noise("mudflat_patch_b", 202),
    "channel_straight_a": _noise("channel_straight_a", 211),
    "channel_straight_b": _noise("channel_straight_b", 212),
    "camp_hard": _noise("camp_hard", 311),
    "mudflat_far": _noise("mudflat_far", 301),
}


def to_local(x: float, z: float, cx: float, cz: float, yaw_deg: float) -> tuple[float, float]:
    """World (x, z) -> a piece's local (x, z) for Godot's Basis(UP, yaw) placement."""
    a = math.radians(yaw_deg)
    dx, dz = x - cx, z - cz
    return dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)


def yaw_toward(dx: float, dz: float) -> float:
    """Yaw (deg) that turns a piece's local +X toward world direction (dx, dz)."""
    return math.degrees(math.atan2(-dz, dx))


def cells() -> list[dict]:
    out = []
    for i, x in enumerate(COL_X):
        for j, z in enumerate(ROW_Z):
            if x == 0.0:
                piece = "channel_straight_a" if j % 2 == 0 else "channel_straight_b"
                yaw = 0.0
            else:
                piece = "mudflat_patch_a" if (i + j) % 2 == 0 else "mudflat_patch_b"
                yaw = 90.0 * ((i * 3 + j * 7) % 4)
            out.append({"piece": piece, "at": [x, z], "y": 0.0, "yaw_deg": yaw})
    return out


CELLS = cells()


def cell_y(x: float, z: float) -> float:
    for c in CELLS:
        cx, cz = c["at"]
        if abs(x - cx) <= bg.HALF and abs(z - cz) <= bg.HALF:
            lx, lz = to_local(x, z, cx, cz, c["yaw_deg"])
            X, Z = np.array([[lx]]), np.array([[lz]])
            n = NOISE[c["piece"]]
            if c["piece"].startswith("channel"):
                amp = bg.CHANNEL_AMP_M if c["piece"].endswith("_a") else -bg.CHANNEL_AMP_M
                return float(bg.channel_height(n, X, Z, amp)[0, 0])
            return float(bg._mud_height(n, X, Z)[0, 0])
    return float(bg.apron_height(NOISE["mudflat_far"], np.array([[x]]), np.array([[z]]))[0, 0])


def hard_y(x: float, z: float, hard=HARD) -> float:
    lx, lz = to_local(x, z, hard[0], hard[1], hard[2])
    return float(bg.hard_height(NOISE["camp_hard"], np.array([[lx]]), np.array([[lz]]))[0, 0])


def sheet_base() -> float:
    """The review hard sits on the apron: its origin goes at the apron's height there."""
    return float(bg.apron_height(NOISE["mudflat_far"], np.array([[SHEET_HARD[0]]]), np.array([[SHEET_HARD[1]]]))[0, 0])


def ground_y(x: float, z: float) -> float:
    if abs(x - SHEET_HARD[0]) < 20 and abs(z - SHEET_HARD[1]) < 20:
        return max(cell_y(x, z), hard_y(x, z, SHEET_HARD) + sheet_base())
    return max(cell_y(x, z), hard_y(x, z))


def channel_x(z: float) -> float:
    for j, cz in enumerate(ROW_Z):
        if abs(z - cz) <= bg.HALF:
            amp = bg.CHANNEL_AMP_M if j % 2 == 0 else -bg.CHANNEL_AMP_M
            return float(bg.channel_offset(z - cz, amp))
    return 0.0


def put(piece: str, x: float, z: float, yaw: float = 0.0, dy: float = 0.0, **kw) -> dict:
    d = {"piece": piece, "at": [round(x, 3), round(z, 3)], "y": round(ground_y(x, z) + dy, 3), "yaw_deg": round(yaw, 2)}
    d.update(kw)
    return d


def flank_x(z: float, level: float, x_from: float, x_to: float) -> float:
    """Where the hard's surface crosses `level` between x_from (low) and x_to (high), at z."""
    xs = np.linspace(x_from, x_to, 200)
    ys = np.array([hard_y(x, z) for x in xs])
    k = int(np.argmax(ys >= level))
    return float(xs[k])


def flank_z(x: float, level: float, z_from: float, z_to: float) -> float:
    zs = np.linspace(z_from, z_to, 200)
    ys = np.array([hard_y(x, z) for z in zs])
    k = int(np.argmax(ys >= level))
    return float(zs[k])


def camp() -> tuple[list[dict], list[list[float]]]:
    plume_yaw = yaw_toward(math.sin(math.radians(WIND_TO_AZ)), -math.cos(math.radians(WIND_TO_AZ)))
    p = [put("camp_hard", HARD[0], HARD[1], HARD[2], 0.0)]
    p[0]["y"] = 0.0
    p += [
        put("camp_tent_burned", 18.2, -3.4, 15.0),
        put("camp_tent_burned", 22.6, 2.6, 100.0),
        put("camp_tent", 22.9, -4.8, 85.0),
        put("salvage_pile_burned", 18.9, 1.6, 30.0),
        put("salvage_rack_burned", 16.9, 5.4, 90.0),
        put("crate_stack", 17.2, -7.0, 30.0),
        put("crate_stack_burned", 25.2, 5.0, -20.0),
        put("brine_vat", 24.3, -1.2, 0.0),
        put("brine_vat_burned", 15.9, -1.2, 40.0),
        put("branding_brazier", 19.2, -0.6, 0.0),
        put("liss_crate", 16.0, 2.4, 12.0),
    ]
    # Smoke: plumes off the three fires and the tent that is catching, leaning downwind (south-west).
    for x, z, s in ((18.3, -2.8, 1.0), (19.0, 1.7, 1.15), (22.6, 2.9, 0.9), (22.9, -4.6, 0.55)):
        p.append(put("smoke_plume", x, z, plume_yaw + (z * 3.0) % 20 - 10, 0.0, scale=s))
    # Two bands of smoke laid across the channel downwind of the camp (B05: the barge comes up through them).
    for x, z, h, s in ((11.5, 7.0, 1.2, 0.8), (12.5, 11.5, 2.2, 0.65)):
        d = put("smoke_plume", x, z, plume_yaw, h, scale=s, tilt_deg=[0.0, -74.0])
        p.append(d)
    lights = [  # x, y, z, energy, range (BrineShoalsPreview: ember_orange, no shadows)
        [18.2, ground_y(18.2, -3.0) + 1.3, -3.0, 1.6, 8.0],
        [18.9, ground_y(18.9, 1.6) + 1.5, 1.6, 2.0, 9.0],
        [22.6, ground_y(22.6, 2.8) + 1.3, 2.8, 1.4, 7.0],
        [19.2, ground_y(19.2, -0.6) + 1.1, -0.6, 0.6, 3.0],
    ]
    return p, lights


def tideline() -> list[dict]:
    out = []
    for z in (-6.5, 1.0, 8.0):  # the west flank, strips running north-south
        x = flank_x(z, 0.9, 11.0, 17.0)
        out.append(put("tideline_wrack", x, z, 90.0 + (z % 7) - 3, -0.02))
    for x in (17.5, 24.5):  # the south flank, east-west
        z = flank_z(x, 0.9, 11.0, 6.0)
        out.append(put("tideline_wrack", x, z, (x % 5) - 2.0, -0.02))
    zb = flank_z(21.0, 0.88, 11.0, 6.0)
    out.append(put("lamp_burial", 21.0, zb, 20.0, -0.03))
    return out


def plank_walk() -> list[dict]:
    pts = np.array([[27.8, 1.2], [36.0, 2.6], [48.0, 1.4], [60.0, 3.2], [72.0, 2.4], [84.0, 3.6]])
    out = []
    seg = 4.05
    dist = 0.0
    total = float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))
    k = 0
    while dist + seg <= total:
        a = _along(pts, dist)
        b = _along(pts, dist + seg)
        m = (a + b) * 0.5
        d = b - a
        yaw = math.degrees(math.atan2(d[0], d[1]))  # the walk's long axis is local +Z
        y = max(ground_y(*a), ground_y(*b), ground_y(*m))
        e = put("plank_walk", float(m[0]), float(m[1]), yaw + ((k * 37) % 7 - 3) * 0.5)
        e["y"] = round(y - 0.06, 3)
        out.append(e)
        dist += seg
        k += 1
    return out


def _along(pts: np.ndarray, dist: float) -> np.ndarray:
    left = dist
    for a, b in zip(pts[:-1], pts[1:]):
        L = float(np.linalg.norm(b - a))
        if left <= L:
            return a + (b - a) * (left / max(L, 1e-9))
        left -= L
    return pts[-1]


def wrecks() -> list[dict]:
    return [
        put("wreck_hull_section", 46.0, -12.0, 30.0),
        put("wreck_bow", 62.0, 19.0, 205.0),
        put("wreck_mast_standing", 53.0, 15.5, 160.0),
        put("wreck_mast_fallen", 67.0, -15.0, 20.0, -0.05),
        put("wreck_ribs_large", 33.5, 14.0, 75.0, -0.1),
        put("wreck_ribs_large", -34.0, -30.0, 10.0, -0.1),
        put("wreck_ribs_large", 78.0, -38.0, 140.0, -0.1),
        put("wreck_ribs_large", 40.0, 30.0, -30.0, -0.1),
    ]


def barge() -> list[dict]:
    """The barge in the channel south of the camp, heading north (its bow is local +X) along the channel."""
    z = 30.0
    slope = (channel_x(z + 0.5) - channel_x(z - 0.5))  # dx per metre of z
    e = {"piece": "white_barge", "at": [round(channel_x(z), 3), z], "y": bg.WATER_Y,
         "yaw_deg": round(yaw_toward(-slope, -1.0), 2)}
    return [e]


def kit_sheet() -> list[dict]:
    """B11: every camp piece intact beside its burned variant, on a second hard to the north-east."""
    sx, sz, _ = SHEET_HARD
    out = [{"piece": "camp_hard", "at": [sx, sz], "y": round(sheet_base(), 3), "yaw_deg": 0.0}]
    pairs = ["camp_tent", "salvage_rack", "crate_stack", "salvage_pile", "brine_vat"]
    for k, name in enumerate(pairs):
        x = sx - 6.0 + 3.0 * k
        for z, suffix in ((sz - 2.6, ""), (sz + 2.6, "_burned")):
            out.append(put(name + suffix, x, z, 90.0 if name == "camp_tent" else 0.0))
    return out


def main() -> int:
    camp_pieces, lights = camp()
    pieces = CELLS + camp_pieces + tideline() + plank_walk() + wrecks() + barge() + kit_sheet()
    pieces.insert(0, {"piece": "mudflat_far", "at": [0.0, 0.0], "y": 0.0, "yaw_deg": 0.0})
    layout = {
        "schema": "hymn-zone-layout/1",
        "zone": "ch06/brine_shoals preview (M3-ENV-02): the kit composed for the design notes' key shots",
        "_about": "Generated by assets_src/environments/kits/brine_shoals/bs_preview_layout.py; do not edit by hand. "
                  "Coordinates: x east, z south (north = -Z), y explicit per piece (no terrain). The channel runs down "
                  "x = 0; the camp's hard is centred at (20, 0); the barge lies in the channel at z = 30.",
        "seed": 6,
        "kit_dir": "res://assets/environments/kits/brine_shoals/",
        "materials_dir": "res://assets/environments/kits/brine_shoals/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "fire_lights": [[round(v, 3) for v in L] for L in lights],
        "fire_light_color": "#E0702E",
        "pieces": pieces,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")
    print(f"LAYOUT {OUT.relative_to(ROOT)}: {len(pieces)} pieces, {len(lights)} fire lights")
    return 0


if __name__ == "__main__":
    sys.exit(main())
