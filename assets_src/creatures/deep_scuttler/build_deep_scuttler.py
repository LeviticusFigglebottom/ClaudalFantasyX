"""Deep scuttler, Ch17 Hollowmere's outer moorings (M5-A3P-1805): docs/kb/art/creatures/act3_roster.md (reconciled).

blender --background --factory-startup --python assets_src/creatures/deep_scuttler/build_deep_scuttler.py -- \
    --out assets/creatures/deep_scuttler/deep_scuttler.glb

The Act I scuttler grown dangerous: spawn that has crawled up the flotilla's hull-lines as the Calm fails. The
scuttler's rig and clips, with its plates rebuilt darker (lacquer black sunk toward abyss navy) and more wounded:
every seam opened wide, raw wounds broken through the plates themselves, and a ridge of short barbs grown along the
spine, so its silhouette is the scuttler's arch with a saw-edge. The battle scene sets it at 1.3 times the
scuttler's size (it has grown, not changed kind). The base build is imported, not copied, so a fix to the scuttler's
rig or clips reaches the deep scuttler on its next rebuild.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "scuttler"))
import build_scuttler as base  # noqa: E402
import creature_kit as ck  # noqa: E402

SEED = 1817
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "spawn_wound": "#3FE0C8", "storm_slate": "#3E4A57",
    "bone": "#E6DAC0",
}.items()}
DARK = 0.72  # the plates sink darker than the scuttler's
SEAM_OPEN = 0.5  # where on a plate's rear face the seam wound starts (the scuttler's: 0.75)
RAW = (0.33, 0.4)  # the fbm band in which a raw wound breaks through a plate (small, sharp openings)
RAW_SCALE = 30.0  # the raw wounds' noise frequency (per metre): a scatter of small wounds, not patches
BARB_LEN = (0.07, 0.12)  # metres, the spine barbs' length range
BARB_RADIUS = 0.022
BARB_RAKE = 0.6  # how far back a barb leans, as a fraction of its length


def plates(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rng = np.random.default_rng(SEED)
    for i in range(base.NSEG):
        z = base.seg_z(i)
        w = 0.24 * math.sin((i + 0.6) / (base.NSEG + 0.2) * math.pi) ** 0.5 + 0.05
        h = 0.18 * math.sin((i + 0.6) / (base.NSEG + 0.2) * math.pi) ** 0.6 + 0.03
        depth = base.LENGTH / base.NSEG * 0.75
        P, T = ck.ellipsoid((0, 0.06, z), (w, h, depth), 8, 18)
        P[:, 1] = np.maximum(P[:, 1], 0.06)
        rear = ck.smoothstep(0.0, -1.0, (P[:, 2] - z) / depth)
        n = ck.fbm(P * 9.0, SEED + i)
        col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.4, n)[:, None]) * DARK
        seam = ck.smoothstep(SEAM_OPEN, 1.0, rear) * ck.smoothstep(0.07, 0.12, P[:, 1])
        raw = ck.smoothstep(RAW[0], RAW[1], ck.fbm(P * RAW_SCALE, SEED + 40 + i)) * ck.smoothstep(0.1, 0.16, P[:, 1])
        wound = np.maximum(seam, raw)
        col = ck.mix(col, PAL["spawn_wound"] * 0.55, wound[:, None])
        ck.finish(mesh, P, T, "carapace", col, rig.rigid(base.bone_for(z)), wet=1.0, cavity=0.3, emission=wound)
        top = np.array([0.0, 0.06 + h, z])
        for k in range(2 if 0 < i < base.NSEG - 1 else 1):
            ln = rng.uniform(*BARB_LEN)
            root = top + np.array([0.0, -0.01, (k - 0.5) * depth * 0.6 if i else 0.0])
            tip = root + np.array([rng.uniform(-0.01, 0.01), ln, -ln * BARB_RAKE])
            Pb, Tb = ck.tube(ck.bezier([root, (root + tip) / 2 + np.array([0, 0, -0.01]), tip], 4),
                             np.linspace(BARB_RADIUS, 0.002, 4), 6)
            tipw = ck.smoothstep(0.5, 1.0, (Pb[:, 1] - root[1]) / ln)
            colb = ck.mix(PAL["lacquer_black"] * DARK, PAL["bone"] * 0.55, tipw[:, None])
            ck.finish(mesh, Pb, Tb, "carapace", colb, rig.rigid(base.bone_for(z)), wet=0.6, cavity=0.2)
        for s in (-1.0, 1.0):
            hip = np.array([s * w * 0.8, 0.07, z])
            tip = np.array([s * (w + 0.12), 0.0, z + rng.uniform(-0.02, 0.04)])
            Pl, Tl = ck.tube(ck.bezier([hip, (hip + tip) / 2 + np.array([s * 0.02, 0.05, 0]), tip], 5),
                             np.linspace(0.016, 0.004, 5), 5)
            ck.finish(mesh, Pl, Tl, "carapace", PAL["storm_slate"] * 0.5, rig.rigid(base.bone_for(z)), wet=1.0)
    Ph, Th = ck.ellipsoid((0, 0.08, base.LENGTH / 2 + 0.02), (0.1, 0.07, 0.07), 6, 10)
    ck.finish(mesh, Ph, Th, "carapace", PAL["lacquer_black"] * DARK, rig.rigid("front"), wet=1.0)
    for s in (-1.0, 1.0):
        for dy, r in ((0.11, 0.017), (0.085, 0.011)):  # a second, smaller pair of eyes opened below the first
            Pe, Te = ck.ellipsoid((s * 0.06, dy, base.LENGTH / 2 + 0.06), (r,) * 3, 4, 6)
            ck.finish(mesh, Pe, Te, "carapace", PAL["spawn_wound"], rig.rigid("front"), wet=1.0, emission=1.0)
    for tag in ("l", "r"):
        b = rig.bones[rig.index(f"feeler_{tag}")]
        h0, h1 = np.asarray(b.head), np.asarray(b.tail)
        P, T = ck.tube(ck.bezier([h0, (h0 + h1) / 2 + np.array([0, 0.08, 0]), h1], 8), np.linspace(0.01, 0.002, 8), 4)
        ck.finish(mesh, P, T, "carapace", PAL["storm_slate"] * 0.6, rig.rigid(f"feeler_{tag}"), wet=1.0)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = base.build_rig()
    mesh = ck.Mesh("deep_scuttler")
    plates(mesh, rig)
    info = ck.export_creature(mesh, rig, base.export_clips(rig, mesh), args.out,
                              extras={"hymn_creature": "deep_scuttler"})
    print(f"deep_scuttler: {info}")


if __name__ == "__main__":
    main()
