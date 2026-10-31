"""Hull rasp, Ch17 Hollowmere's outer moorings (M5-A3P-1806): docs/kb/art/creatures/act3_roster.md (reconciled).

blender --background --factory-startup --python assets_src/creatures/hull_rasp/build_hull_rasp.py -- \
    --out assets/creatures/hull_rasp/hull_rasp.glb

A variant of the hullgnaw (Ch1): a rasping hull-borer in the flotilla's keels, an echo of Oruvel at Dace's yard. The
hullgnaw's rig, clips and breach (it bores up through the hull it was eating), with a new shell and palette:
- its body sunk darker and salt-crusted where it dried between tides, the crust scabbed over its back;
- its seams bored rather than split: many small round bore-holes glowing spawn_wound along every gap between the
  frames, round the one large seam the hullgnaw's weak point keeps (`vfx_wound`);
- the frames that ring it are keel timbers gone white with salt, crusted thick, the rust bled pale (`Ribs`, its part:
  the `breaking` phase throws them off, the Ch1 lesson grown up).
The battle scene sets it at 0.62 times the hullgnaw's size: a single optional foe, not a boss. The base build is
imported, not copied, so a fix to the hullgnaw's rig, clips or breach reaches the hull rasp on its next rebuild.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "hullgnaw"))
import build_hullgnaw as base  # noqa: E402
import creature_kit as ck  # noqa: E402

SEED = 1806
SALT = ck.mix(base.PAL["coral_stone_weathered"], base.PAL["bone"], 0.5)
DARK = 0.8  # the body's lacquer sinks darker than the hullgnaw's
CRUST_BODY = (0.18, 0.34)  # the fbm band over which salt scabs the body's back
CRUST_RIB = (-0.1, 0.25)  # the fbm band over which salt crusts the keel timbers (most of them)
BORE_WIDTH = 0.055  # metres: a bore-hole's width across its gap
# Bore-holes (gap, phi from, phi to): short spans of each gap, so each opens as a small round hole, not a split
BORES = (
    (0, 0.3, 0.55), (0, 1.5, 1.75), (0, 2.9, 3.15),
    (1, -0.5, -0.25), (1, 1.0, 1.25), (1, 2.3, 2.55), (1, 3.7, 3.95),
    (2, 0.2, 0.45), (2, 1.6, 1.85), (2, 3.0, 3.25),
    (3, 4.4, 4.65),
)

base.SEED = SEED
base.PAL = dict(base.PAL)
base.PAL.update({
    "lacquer_black": base.PAL["lacquer_black"] * DARK,
    "abyss_navy": base.PAL["abyss_navy"] * DARK,
    "timber_weathered": ck.mix(base.PAL["timber_weathered"], SALT, 0.55),  # the keel timbers bleached
    "laterite": ck.mix(base.PAL["laterite"], SALT, 0.6),  # their rust bled pale
})
# the main seam (gap 3, `vfx_wound`) stays the hullgnaw's; the rest are bored
base.WOUNDS = tuple(w for w in base.WOUNDS if w[0] == 3) + tuple((g, p0, p1, BORE_WIDTH) for g, p0, p1 in BORES)


def salt(mesh: ck.Mesh, frames: ck.Mesh) -> None:
    """Salt dried on between tides: scabbed over the body's back (never in the glowing wounds, the eyes or the breach's
    water), crusted thick over the keel timbers. Dry salt is rough: the crust loses its wetness."""
    for k, P in enumerate(mesh.pos):
        C, E = mesh.col[k], mesh.uv2[k]
        glow = E[:, 1]
        up = ck.smoothstep(0.8, 2.4, P[:, 1])  # the arch's upper body, out of the water longest
        crust = ck.smoothstep(*CRUST_BODY, ck.fbm(P * 7.0, SEED + 1)) * up * (1.0 - ck.smoothstep(0.05, 0.3, glow))
        C[:, :3] = ck.mix(C[:, :3], SALT * 0.82, (0.85 * crust)[:, None])
        C[:, 3] = C[:, 3] * (1.0 - 0.8 * crust)
    for k, P in enumerate(frames.pos):
        C = frames.col[k]
        crust = ck.smoothstep(*CRUST_RIB, ck.fbm(P * 5.0, SEED + 2))
        C[:, :3] = ck.mix(C[:, :3], SALT * 0.9, (0.75 * crust)[:, None])
        C[:, 3] = C[:, 3] * (1.0 - 0.7 * crust)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, joints = base.build_rig()
    mesh, frames = base.build(rig, joints)
    mesh.name = "hull_rasp"
    salt(mesh, frames)
    info = ck.export_creature(mesh, rig, base.build_clips(rig), args.out, extra_meshes=[frames],
                              extras={"hymn_creature": "hull_rasp"})
    print(f"hull_rasp: {info} (body {mesh.triangle_count}, frames {frames.triangle_count})")


if __name__ == "__main__":
    main()
