"""Fen leech, Ch10 Ossa Fen (M3-CRE-628): docs/kb/art/creatures/act2/variants.md.

blender --background --factory-startup --python assets_src/creatures/fen_leech/build_fen_leech.py -- \
    --out assets/creatures/fen_leech/fen_leech.glb

A variant of the sail leech: a ribbon-flat leech of the fen's dark water. The sail leech's rig and clips, rebuilt
through the base build's parameters (so the sail leech's own output is unchanged): longer (2.36 m nose to rear, 2.74 m
with the tail) and narrower, half as thick, and without the canvas frill along its edge. Its back is wet
lacquer_black ringed with faint annuli, its underside a faint tannin-amber (dusk_gold darkened), and the spawn_wound
slits run down its back with the eyes at the front. The base build is imported, not copied, so a fix to the sail
leech reaches the fen leech on its next rebuild.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "sail_leech"))
import build_sail_leech as base  # noqa: E402
import creature_kit as ck  # noqa: E402

SEED = 8273
SW = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "tortoiseshell": "#6B3A1E", "dusk_gold": "#F2A64A",
}.items()}
TANNIN = ck.mix(SW["dusk_gold"] * 0.42, SW["tortoiseshell"], 0.25)  # the underside: dusk_gold darkened, faint

base.SEED = SEED
base.HALF_W = 0.44  # ribbon-narrow (sail leech 0.7)
base.HALF_L = 0.95  # and long (0.5)
base.THICK = 0.035  # flat (0.07)
base.KO_DROP = 0.85  # its fall from its 0.85 m hover: hung low, under the battle camera, so its face reads, not its
# edge (the Act I audit found the sail leech at eye height a row of glowing dashes; its attack dips 0.70 m)
base.DOME = 0.05  # a raised back (was 0.025): edge-on from a low battle camera the flat ribbon read as a branch
base.FRILL = 0.006  # no canvas: only a slight ripple at the edge (0.022)
base.FRILL_WAVES = 22.0
base.SLIT_Z = (0.55, 0.22)  # the four slits spread down the longer back
base.EYE = (0.07, 0.245, 0.86)
base.TAIL_Z0, base.TAIL_STEP = -0.75, 0.25
base.TAIL_PATH = ((0, 0.2, -0.75), (0, 0.19, -1.0), (0.04, 0.15, -1.25), (0.0, 0.13, -1.5))
base.TAIL_R = (0.05, 0.012)
base.TAIL_CHAIN = ((0, 0.2, -0.75), (0, 0.2, -1.0), (0, 0.2, -1.25), (0, 0.2, -1.5))
# M3-CRE-654 gave the sail leech a leech's own body and suckers: here the body is lower than the sail leech's so the
# eyes sit on it.
base.BODY_W = 0.1
base.BODY_H = (0.085, 0.045)  # a muscular back, not a strap (was 0.06, 0.035)
# its edges drape down like a ray's (the sail leech hangs its sails 0.11): edge-on it is an arch with height, not a
# line (the Ossa Fen arena check, 2026-10-30)
base.DROOP = 0.1
base.PAL = dict(base.PAL)
base.PAL.update({
    "abyss_navy": ck.mix(SW["lacquer_black"], SW["tortoiseshell"], 0.18),  # the back: lacquer black, a hint of brown
    "storm_slate": TANNIN,
    "deep_teal_shadow": TANNIN,
})
ANNULI = 40.0  # rings per metre down the back
# The as-played pass (ch10_fen_leeches in the ossa_fen arena, 2026-10-30): side-on under the battle camera the flat
# 2.4 m ribbon still read as a plank hung over the mud. A leech humps its body lengthwise, so the whole mesh is bowed:
# the middle raised ARCH over the nose and the rear (a parabola over the body's length, flat along the tail), and
# side-on it is a living curve. The body is one bone, so the bow is in the mesh; the nose and rear keep the hover.
ARCH = 0.28
SET_DOWN_CLEAR = 0.01  # the lowest point 1 cm over the model's floor: the KO tips it 8 deg nose-down as it lands


def annuli(mesh: ck.Mesh) -> None:
    """A leech's faint rings across the back and the tail (lacquer black, darker in the grooves)."""
    for k, P in enumerate(mesh.pos):
        if mesh.uv2[k][:, 1].max() >= 0.99 and len(P) < 200:  # the glowing eyes
            continue
        ring = 0.5 + 0.5 * np.cos(P[:, 2] * ANNULI * np.pi)
        groove = ck.smoothstep(0.8, 1.0, ring) * (1.0 - mesh.uv2[k][:, 1])
        mesh.col[k][:, :3] = mesh.col[k][:, :3] * (1.0 - 0.18 * groove)[:, None]
        mesh.col[k][:, :3] = np.maximum(mesh.col[k][:, :3], SW["lacquer_black"])  # never under the albedo floor
        mesh.uv2[k][:, 0] = np.clip(mesh.uv2[k][:, 0] + 0.35 * groove, 0.0, 1.0)


def arch(mesh: ck.Mesh) -> None:
    """Bows every part lengthwise: y += ARCH x (1 - (z / HALF_L)^2), z clamped to the body (the tail stays level),
    its normals sheared to match."""
    for P, N in zip(mesh.pos, mesh.nrm):
        u = np.clip(P[:, 2] / base.HALF_L, -1.0, 1.0)
        slope = np.where(np.abs(P[:, 2]) < base.HALF_L, -2.0 * ARCH * u / base.HALF_L, 0.0)  # d y / d z
        P[:, 1] += ARCH * (1.0 - u * u)
        N[:, 2] -= slope * N[:, 1]  # normals by the shear's inverse transpose
        N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    # set down so its lowest point rests at the model's floor: its KO (a fall of exactly its hover) then lays it on the
    # ground (the animation polish pass, 2026-10-30: bowed, it ended 6 cm up)
    low = min(float(P[:, 1].min()) for P in mesh.pos) - SET_DOWN_CLEAR
    for P in mesh.pos:
        P[:, 1] -= low


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = base.build_mesh(rig, "fen_leech")
    annuli(mesh)
    arch(mesh)
    return mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = base.build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, base.build_clips(), args.out, extras={"hymn_creature": "fen_leech"})
    print(f"fen_leech: {info}")


if __name__ == "__main__":
    main()
