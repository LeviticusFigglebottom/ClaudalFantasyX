"""Rim rays (Ch16 the Pale Rim, M4-A2P-056): docs/kb/plan/act2/creatures/rim_ray.md, docs/kb/art/wildlife.md.

blender --background --factory-startup --python-exit-code 1 --threads 4 --python \
    assets_src/wildlife/rim_ray/build_rim_ray.py -- --out assets/wildlife/rim_ray/rim_ray.glb

A small pale ray, 0.4 m across, gliding in loose groups over the white sand in the ankle-deep water of the Rim: a
flat rounded diamond with a short whip tail, a pale sand back (sand_dry toward coral_stone_weathered) freckled a shade
darker, a faint darker margin (sand_wet) so its edge holds against the sand, two small dark eyes, a bone belly. Fish-
sized and always moving in groups, so it is never mistaken for the glass skate (a 2 m buried foe). Nothing spawn-
touched: no wound light, no glimmer.
  rim_ray   flat, swimming (+z forward). TEXCOORD_1.y = the fin's span (0 at the body's edge .. 1 at the wingtip),
            which the wildlife shader flaps about the body's edge (materials.json `wing_pivot`, the shader's mode 1:
            the fins beat up and down as a ray swims; the stroke lags toward the tip).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import wildlife_kit as wk  # noqa: E402

ck = wk.ck

SEED = 6160
PAL = {k: ck.hexrgb(v) for k, v in {
    "sand_dry": "#EFDDB4", "coral_stone_weathered": "#B9AE98", "sand_wet": "#B59D74", "bone": "#E6DAC0",
    "lacquer_black": "#1D1916",
}.items()}
BACK = ck.mix(PAL["sand_dry"], PAL["coral_stone_weathered"], 0.35)
FRECKLE = ck.mix(BACK, PAL["sand_wet"], 0.55)
MARGIN = ck.mix(PAL["sand_wet"], PAL["coral_stone_weathered"], 0.3)
SLOT = "skin"

SPAN_HALF = 0.20  # the wingtip's x
BODY_X = 0.045  # the body's half-width, where the fins begin (the shader's wing pivot)
NOSE_Z = 0.13
REAR_Z = -0.11
TIP_Z = -0.01  # the wingtips sit a little behind the middle
THICK = 0.018  # the body's thickness at its centre
TAIL_Z = -0.34


def half_span(z: np.ndarray) -> np.ndarray:
    """The disc's half-width at z: a rounded diamond, widest at TIP_Z."""
    front = SPAN_HALF * np.clip((NOSE_Z - z) / (NOSE_Z - TIP_Z), 0.0, 1.0) ** 0.75
    back = SPAN_HALF * np.clip((z - REAR_Z) / (TIP_Z - REAR_Z), 0.0, 1.0) ** 1.2
    return np.maximum(np.where(z >= TIP_Z, front, back), 0.004)


def build() -> ck.Mesh:
    mesh = ck.Mesh("rim_ray")
    nz, nx = 16, 13
    zz = np.linspace(NOSE_Z, REAR_Z, nz)
    uu = np.linspace(-1.0, 1.0, nx)
    Z, U = np.meshgrid(zz, uu, indexing="ij")
    X = U * half_span(Z)
    dome = np.clip(1.0 - (np.abs(X) / SPAN_HALF) ** 1.5, 0.0, 1.0) * np.clip(1.0 - ((Z - 0.0) / 0.14) ** 2, 0.15, 1.0)
    top = np.column_stack([X.ravel(), (0.35 * THICK + 0.65 * THICK * dome).ravel(), Z.ravel()])
    bot = np.column_stack([X.ravel(), (-0.15 * THICK * dome).ravel(), Z.ravel()])
    span = np.clip((np.abs(X.ravel()) - BODY_X) / (SPAN_HALF - BODY_X), 0.0, 1.0)  # the flap mask
    edge = ck.smoothstep(0.75, 1.0, np.abs(U.ravel()))
    freckle = ck.smoothstep(0.55, 0.75, ck.value_noise(top * 60.0, SEED))
    col = ck.mix(BACK, FRECKLE, (0.7 * freckle * (1.0 - edge))[:, None])
    col = ck.mix(col, MARGIN, (0.6 * edge)[:, None])
    eye = np.zeros(len(top))
    for side in (1.0, -1.0):
        d = np.linalg.norm(top[:, [0, 2]] - np.array([side * 0.022, 0.07]), axis=1)
        eye = np.maximum(eye, 1.0 - ck.smoothstep(0.004, 0.008, d))
    col = ck.mix(col, PAL["lacquer_black"], eye[:, None])
    T = ck.grid_tris(nz, nx, False)
    ck.finish(mesh, top, ck.flip(T), SLOT, col, 0, wet=0.4, cavity=0.1 * eye, emission=span)
    ck.finish(mesh, bot, T, SLOT, ck.mix(PAL["bone"], BACK, 0.3), 0, wet=0.4, cavity=0.1, emission=span)
    # the rim joining top and bottom round the disc's outline, so the edge is closed
    ring = np.concatenate([np.arange(nx) * 1, (np.arange(1, nz) * nx + nx - 1), (nz - 1) * nx + np.arange(nx - 2, -1, -1),
                           (np.arange(nz - 2, 0, -1) * nx)])
    n = len(ring)
    P = np.vstack([top[ring], bot[ring]])
    Tr = np.array([[k, (k + 1) % n, n + k] for k in range(n)] + [[(k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)])
    ck.finish(mesh, P, Tr, SLOT, np.tile(MARGIN, (len(P), 1)), 0, wet=0.4, cavity=0.2,
              emission=np.concatenate([span[ring], span[ring]]))
    # the tail: a thin whip from the rear of the disc
    path = ck.bezier([(0.0, 0.008, REAR_Z + 0.01), (0.0, 0.007, (REAR_Z + TAIL_Z) / 2), (0.0, 0.006, TAIL_Z)], 5)
    Pt, Tt = ck.tube(path, np.array([0.006, 0.004, 0.003, 0.002, 0.0006]), 4)
    ck.finish(mesh, Pt, Tt, SLOT, ck.mix(BACK, MARGIN, 0.5), 0, wet=0.4, cavity=0.1)
    return mesh


def main() -> None:
    out = wk.out_arg()
    info = wk.export_static([build()], out, extras={"hymn_wildlife": "rim_ray"})
    print(f"rim_ray: {info}")


if __name__ == "__main__":
    main()
