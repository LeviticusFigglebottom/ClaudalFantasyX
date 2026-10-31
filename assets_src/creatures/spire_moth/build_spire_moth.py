"""Spire moth, Ch19 the Iskarra Lamp Spire (M5-A3P-1802): docs/kb/art/creatures/act3/spire_moth.md.

blender --background --factory-startup --python assets_src/creatures/spire_moth/build_spire_moth.py -- \
    --out assets/creatures/spire_moth/spire_moth.glb

A variant of the flue moth (Ch8): moths that have lived for centuries on the Lamp Spire's warm lamp-glass, pale and
glassy, with no soot and no embers. The flue moth's rig, mesh, clips and weak point (the seared seam across its brow,
ADR 0151), imported, with its colouring swapped: fur `bone` into `lit_ceramic` with `coral_stone_weathered` in the
cavities, no embers; forewings `salt_glass` with fine `cold_blue_stone` veins where the soot zig-zags were (glossy
in the materials, so they read as glass); hindwings `gauze_white` paling from `salt_glass` at the root, edged `brass`,
not emissive (the flare reads by catching the light; the glint is battle VFX); antennae `brass`-tinted `bone`; legs a
pale `coral_stone_weathered`; the eyes stay black. The base is untouched, so the flue moth still builds identical.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "flue_moth"))
import build_flue_moth as base  # noqa: E402
import creature_kit as ck  # noqa: E402

SW = {k: ck.hexrgb(v) for k, v in {
    "bone": "#E6DAC0", "lit_ceramic": "#DCE3E0", "coral_stone_weathered": "#B9AE98", "salt_glass": "#BFE6E0",
    "cold_blue_stone": "#5E6E80", "gauze_white": "#EBE7DF", "brass": "#B08D57",
}.items()}

base.PAL = dict(base.PAL)
base.PAL.update({
    "bone": ck.mix(SW["bone"], SW["brass"], 0.35) / 0.55,  # the antennae (the base darkens its bone by 0.55)
    "volcanic_stone": ck.mix(SW["coral_stone_weathered"], SW["bone"], 0.4) / 0.8,  # the legs (darkened by 0.8)
    "overcast_slate": SW["coral_stone_weathered"],  # the abdomen's segment rings, a shade darker than the fur
})


def spire_fur(P: np.ndarray, seed: int, ember: float) -> tuple[np.ndarray, np.ndarray]:
    """The pale fur: bone into lit_ceramic, coral_stone_weathered in the hollows, and no embers (`ember` is ignored)."""
    n = ck.fbm(P * 30.0, seed)
    col = ck.mix(SW["bone"], SW["lit_ceramic"], ck.smoothstep(-0.2, 0.4, n)[:, None])
    col = ck.mix(col, SW["coral_stone_weathered"], (0.6 * ck.smoothstep(0.0, -0.4, n))[:, None])
    return col, np.zeros(len(P))


def spire_wings(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The base's wing sheets, coloured glass: salt_glass forewings veined cold_blue_stone where the soot zig-zags were;
    gauze_white hindwings paling from salt_glass at the root and edged brass. Nothing glows."""
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for hind, wn in ((True, "hind"), (False, "fore")):
            span, chord, ln, wd = base.wing_frame(s, hind)
            b = rig.bones[rig.index(f"{wn}wing_{tag}")]
            root = np.asarray(b.head)
            ns, nc = 14, 6
            su, cu = np.meshgrid(np.linspace(0, 1, ns), np.linspace(0, 1, nc), indexing="ij")
            prof = wd * np.sin(np.clip(su, 0.02, 1.0) * np.pi * 0.85) ** 0.6 * (1.0 + 0.25 * su)
            lead = 0.06 * su
            P = (root + (su * ln)[..., None] * span + ((cu * prof) - lead)[..., None] * chord).reshape(-1, 3)
            T = ck.grid_tris(ns, nc, False)
            normal = np.cross(span, chord)
            if hind:
                out = ck.smoothstep(0.1, 0.5, su.ravel())
                col = ck.mix(np.tile(SW["salt_glass"], (len(P), 1)), np.tile(SW["gauze_white"], (len(P), 1)),
                             out[:, None])
                col = ck.mix(col, SW["brass"], (0.6 * ck.smoothstep(0.85, 1.0, cu.ravel()))[:, None])
            else:
                n = ck.fbm(P * 14.0, base.SEED + 30)
                vein = ck.smoothstep(0.88, 1.0, np.abs(np.sin(su.ravel() * 18.0 + cu.ravel() * 5.0 + n * 2.0)))
                col = ck.mix(SW["salt_glass"], SW["gauze_white"], ck.smoothstep(0.0, 0.5, n)[:, None] * 0.3)
                col = ck.mix(col, SW["cold_blue_stone"], (0.55 * vein)[:, None])
            for fl in (False, True):
                off = normal * (0.003 if fl else -0.003) * s
                ck.finish(mesh, P + off, ck.flip(T) if fl else T, "wing", col, rig.rigid(f"{wn}wing_{tag}"),
                          cavity=0.1, emission=np.zeros(len(P)))


base.fur = spire_fur
base.wings = spire_wings


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, mesh = base.build_mesh()
    mesh.name = "spire_moth"
    info = ck.export_creature(mesh, rig, base.export_clips(rig, mesh), args.out, extras={"hymn_creature": "spire_moth"})
    print(f"spire_moth: {info}")


if __name__ == "__main__":
    main()
