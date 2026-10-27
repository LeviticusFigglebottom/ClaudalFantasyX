"""Root crab, Ch10 Ossa Fen (M3-CRE-628): docs/kb/art/creatures/act2/variants.md.

blender --background --factory-startup --python assets_src/creatures/root_crab/build_root_crab.py -- \
    --out assets/creatures/root_crab/root_crab.glb

A variant of the reef crab: a mangrove tree-crab that lives in the fen's roots and drags prey into them. The reef
crab's rig and clips, on longer climbing legs (the base build's LEG_KNEE and LEG_FOOT parameters, so the reef crab's
own output is unchanged), re-coloured from house-coral to mangrove bark: a bark-brown carapace (timber_weathered,
laterite) with dark fissures for the mortar seams, spotted with grey lichen (overcast_slate). Where the reef crab
carries its red roof tile, a knot of mangrove roots grips the back and trails off the rim. The base build is
imported, not copied, so a fix to the reef crab reaches the root crab on its next rebuild.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "reef_crab"))
import build_reef_crab as base  # noqa: E402
import creature_kit as ck  # noqa: E402

SEED = 8261
SW = {k: ck.hexrgb(v) for k, v in {
    "timber_weathered": "#7E6A55", "laterite": "#A8573A", "overcast_slate": "#6F7E8E", "tortoiseshell": "#6B3A1E",
    "lacquer_black": "#1D1916",
}.items()}

# Longer climbing legs: the knee higher and further out, the foot planted wider (reef crab: (0.62, 0.47, 1.7), (0.80, 2.3))
base.LEG_KNEE = (0.70, 0.62, 1.85)
base.LEG_FOOT = (0.96, 2.5)
base.SEED = SEED
_orig = dict(base.PAL)
BARK = SW["timber_weathered"]
BARK_DARK = ck.mix(SW["timber_weathered"], SW["tortoiseshell"], 0.55)
base.PAL.update({
    "coral_stone": BARK,  # the plates: mangrove bark
    "coral_stone_weathered": ck.mix(SW["timber_weathered"], SW["laterite"], 0.35),
    "mortar_white": ck.mix(SW["tortoiseshell"], SW["lacquer_black"], 0.35),  # the seams: the bark's dark fissures
    "roof_clay": ck.mix(SW["laterite"], SW["tortoiseshell"], 0.4),  # the plate under the root knot
    "laterite": ck.mix(_orig["laterite"], SW["timber_weathered"], 0.65),  # legs and claws: bark-brown
    "sand_wet": BARK_DARK,  # the rim's fen mud
})
LICHEN = SW["overcast_slate"]

# The knot of roots over the back (where the reef crab's tile plate is): each root runs from one rim, over the knot,
# and off another rim, where it trails down as an aerial root. (start, end) as unit directions on the dome.
KNOT_AT = np.array([0.30, 0.80, -0.30])
ROOTS = (((0.95, 0.15, 0.25), (-0.55, 0.2, -0.85)), ((0.9, 0.2, -0.45), (-0.75, 0.25, 0.65)),
         ((0.55, 0.2, -0.85), (0.75, 0.25, 0.65)), ((-0.85, 0.2, -0.3), (0.98, 0.1, -0.15)))  # clear of the weak point's crack at the back (x 0) and the eyes
ROOT_R = (0.034, 0.028, 0.03, 0.026)
ROOT_N = 18  # rings per root, over the dome
ROOT_SEGS = 6


def _unit(v) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def _slerp(a: np.ndarray, b: np.ndarray, u: np.ndarray) -> np.ndarray:
    om = math.acos(float(np.clip(a @ b, -1.0, 1.0)))
    if om < 1e-6:
        return np.tile(a, (len(u), 1))
    s = math.sin(om)
    return (np.sin((1.0 - u) * om)[:, None] * a + np.sin(u * om)[:, None] * b) / s


def _on_dome(d: np.ndarray, lift: float) -> np.ndarray:
    """A point `lift` metres over the carapace dome along unit directions d (the plates' mean height)."""
    P = d * (np.asarray(base.SHELL_R) + 0.03 + np.asarray(lift, dtype=np.float64).reshape(-1, 1))
    P[:, 2] += 0.04 * d[:, 2] * (d[:, 2] > 0)
    P[:, 1] += base.BODY_Y
    return P


def lichen(mesh: ck.Mesh) -> None:
    """Grey lichen spotted over the carapace plates (the first shell part, the dome)."""
    P = mesh.pos[0]
    n = ck.fbm(P * 9.0, SEED + 3)
    spots = ck.smoothstep(0.0, 0.15, n) * ck.smoothstep(0.45, 0.55, ck.value_noise(P * 23.0, SEED + 4) * 0.5 + 0.5)
    spots = np.maximum(spots, ck.smoothstep(0.1, 0.25, n) * 0.8)
    top = ck.smoothstep(base.BODY_Y + 0.05, base.BODY_Y + 0.15, P[:, 1])
    k = (0.85 * spots * top * (1.0 - mesh.uv2[0][:, 1]))[:, None]  # never over the weak point's crack
    C = mesh.col[0]
    C[:, :3] = ck.mix(C[:, :3], LICHEN * (0.92 + 0.12 * ck.fbm(P * 30.0, SEED + 5))[:, None], k)
    mesh.uv2[0][:, 0] = np.maximum(mesh.uv2[0][:, 0] - 0.3 * k[:, 0], 0.0)  # lichen fills the fissures it covers


def roots(mesh: ck.Mesh, rig: ck.Rig) -> None:
    knot = _unit(KNOT_AT)
    body = rig.rigid("body")
    for i, ((a, b), r) in enumerate(zip(ROOTS, ROOT_R)):
        a, b = _unit(a), _unit(b)
        u = np.linspace(0.0, 1.0, ROOT_N)
        half = ROOT_N // 2
        d = np.vstack([_slerp(a, knot, u[: half + 1] * 2.0)[:-1], _slerp(knot, b, u[half:] * 2.0 - 1.0)])
        d = _unit(d)
        # the roots twist round each other where they cross at the knot, and rise over it
        near = np.exp(-((u - 0.5) / 0.16) ** 2)
        ph = i * 2.0 * math.pi / len(ROOTS) + u * 5.0 * math.pi
        side = _unit(np.cross(d, np.gradient(d, axis=0)))
        up = d
        path = _on_dome(d, 0.012 + 0.05 * near)
        path = path + (0.035 * near * np.cos(ph))[:, None] * side + (0.025 * near * np.sin(ph))[:, None] * up
        # an aerial root: off the rim it bends down toward the water
        tail = path[-1] + np.array([0.0, -0.02, 0.0])
        drop = np.array([tail + np.array([b[0] * 0.03, -0.07, b[2] * 0.03]),
                         tail + np.array([b[0] * 0.04, -0.15, b[2] * 0.04])])
        path = np.vstack([path, drop])
        k = len(path)
        rad = r * np.interp(np.linspace(0, 1, k), [0.0, 0.1, 0.5, 0.85, 1.0], [0.55, 1.0, 1.15, 0.8, 0.35])
        P, T = ck.tube(path, rad, ROOT_SEGS, squash=0.85)
        grain = 0.5 + 0.5 * np.sin(np.linalg.norm(P - path[0], axis=1) * 70.0 + ck.fbm(P * 12.0, SEED + 10 + i) * 4.0)
        col = ck.mix(BARK_DARK, BARK, (0.35 + 0.45 * grain)[:, None])
        col = ck.mix(col, SW["laterite"] * 0.8, ck.smoothstep(base.BODY_Y + 0.05, base.BODY_Y - 0.15, P[:, 1])[:, None]
                     * 0.5)
        ck.finish(mesh, P, T, "shell", col, body, wet=ck.smoothstep(base.BODY_Y, base.BODY_Y - 0.15, P[:, 1]) * 0.6,
                  cavity=0.35 * (1.0 - grain))


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = base.build_mesh(rig)
    mesh.name = "root_crab"
    lichen(mesh)
    roots(mesh, rig)
    return mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = base.build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, base.build_clips(), args.out, extras={"hymn_creature": "root_crab"})
    print(f"root_crab: {info}")


if __name__ == "__main__":
    main()
