"""Ambient shoal fish (M3-CRE-611): docs/kb/art/wildlife.md.

blender --background --factory-startup --python-exit-code 1 --threads 4 --python \
    assets_src/wildlife/shoal_fish/build_shoal_fish.py -- --out assets/wildlife/shoal_fish/shoal_fish.glb

A small lagoon silverside (14 cm), drawn many at a time through one MultiMesh: a slim, laterally flattened body with
a dark blue-teal back, a bright silver flank stripe and a white belly, a forked tail and a small dorsal fin. One
mesh, one material slot, about two hundred triangles. No motion mask: the wildlife shader's swim bends the body by
its distance behind the snout (VERTEX.z), so the tail sweeps most.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import wildlife_kit as wk  # noqa: E402

ck = wk.ck

PAL = {k: ck.hexrgb(v) for k, v in {
    "reef_blue": "#1569A0", "deep_teal_shadow": "#0E4A55", "foam_white": "#EEF6F4", "gauze_white": "#EBE7DF",
    "lit_ceramic": "#DCE3E0", "lacquer_black": "#1D1916",
}.items()}
BACK = ck.mix(PAL["deep_teal_shadow"], PAL["reef_blue"], 0.45)
FLANK = PAL["lit_ceramic"] * 0.82
BELLY = PAL["gauze_white"]
SLOT = "scales"

SNOUT_Z = 0.075
TAIL_Z = -0.065


def body(mesh: ck.Mesh) -> None:
    n = 11
    path = ck.bezier([(0, 0.0, SNOUT_Z), (0, 0.002, 0.03), (0, 0.001, -0.02), (0, 0.0, TAIL_Z + 0.012)], n)
    s = np.linspace(0.0, 1.0, n)
    rad = 0.002 + 0.0155 * np.sin(np.clip(s * 1.15 + 0.04, 0, 1) * math.pi) ** 0.75
    rad[-1] = 0.0035
    # deep and slim: the tube's binormal (x with up_hint +y... see ck.tube) is squashed to the fish's width
    P, T = ck.tube(path, rad, 8, squash=0.48, up_hint=(1.0, 0.0, 0.0))
    P = P[:, [1, 0, 2]] * np.array([1.0, 1.0, 1.0])  # swap so the squashed axis is x (width), the deep axis y
    P[:, 0] *= 1.0
    T = ck.flip(T)
    h = P[:, 1] / np.maximum(np.interp(P[:, 2], path[::-1, 2], rad[::-1]), 1e-4)  # -1 belly .. +1 back
    col = ck.mix(BELLY, FLANK, ck.smoothstep(-0.7, -0.1, h)[:, None])
    stripe = 1.0 - ck.smoothstep(0.04, 0.16, np.abs(h - 0.12))
    col = ck.mix(col, PAL["foam_white"] * 0.95, (0.8 * stripe)[:, None])
    col = ck.mix(col, BACK, ck.smoothstep(0.25, 0.55, h)[:, None])
    eye = np.zeros(len(P))
    for side in (1.0, -1.0):
        d = np.linalg.norm(P - np.array([side * 0.006, 0.003, SNOUT_Z - 0.014]), axis=1)
        eye = np.maximum(eye, 1.0 - ck.smoothstep(0.0025, 0.004, d))
    col = ck.mix(col, PAL["lacquer_black"], eye[:, None])
    ck.finish(mesh, P, T, SLOT, col, 0, wet=1.0, cavity=0.05 + 0.3 * eye)


def fins(mesh: ck.Mesh) -> None:
    # forked tail: two thin swept lobes, two-sided
    root = np.array([0.0, 0.0, TAIL_Z + 0.014])
    for lobe in (1.0, -1.0):
        P = np.array([root + np.array([0, 0.004 * lobe, 0]), root + np.array([0, 0.0, -0.006]),
                      root + np.array([0, 0.022 * lobe, -0.030]), root + np.array([0, 0.008 * lobe, -0.020])])
        T = np.array([[0, 2, 1], [1, 2, 3]]) if lobe > 0 else np.array([[0, 1, 2], [1, 3, 2]])
        col = ck.mix(BACK, FLANK, 0.35)
        ck.finish(mesh, P, T, SLOT, col, 0, wet=1.0, flat=True)
        ck.finish(mesh, P, ck.flip(T), SLOT, col, 0, wet=1.0, flat=True)
    # dorsal fin: one small triangle on the back
    P = np.array([(0, 0.014, 0.012), (0, 0.024, -0.004), (0, 0.012, -0.012)])
    ck.finish(mesh, P, np.array([[0, 1, 2]]), SLOT, BACK, 0, wet=1.0, flat=True)
    ck.finish(mesh, P, np.array([[0, 2, 1]]), SLOT, BACK, 0, wet=1.0, flat=True)


def build_mesh() -> ck.Mesh:
    mesh = ck.Mesh("shoal_fish")
    body(mesh)
    fins(mesh)
    return mesh


def main() -> None:
    out = wk.out_arg()
    info = wk.export_static([build_mesh()], out, extras={"hymn_wildlife": "shoal_fish"})
    print(f"shoal_fish: {info}")


if __name__ == "__main__":
    main()
