"""The Cinder Matron, the Ch5 boss (M3-CRE-04): docs/kb/art/creatures/act1/cinder_matron.md.

blender --background --factory-startup --python assets_src/creatures/cinder_matron/build_cinder_matron.py -- \
    --out assets/creatures/cinder_matron/cinder_matron.glb

Ashcrown's temple guardian: a seated matron of laterite blocks, eyes closed and mouth open, long arms ending in flat
stone hands on her knees, under a crust of cooled magma (`Crust`, its own mesh: phase 2 bursts it off and the
ember-lit seams of the blocks show). A construct: every part is a rigid block on a bone.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 5307
PAL = {k: ck.hexrgb(v) for k, v in {
    "laterite": "#A8573A", "volcanic_stone": "#3A3A3F", "ember_orange": "#E0702E", "lacquer_black": "#1D1916",
    "sand_dry": "#EFDDB4", "coral_stone_weathered": "#B9AE98",
}.items()}


def block(center, size, rings: int = 18, segs: int = 28, round_: float = 0.25, R=None) -> tuple[np.ndarray, np.ndarray]:
    """A rounded stone block: a sphere pushed toward a cube (`round_` 0 = sharp box .. 1 = ellipsoid)."""
    P, T = ck.ellipsoid((0, 0, 0), (1, 1, 1), rings, segs)
    cube = P / np.maximum(np.abs(P).max(axis=1, keepdims=True), 1e-6)
    P = cube * (1.0 - round_) + P * round_
    P = P * (np.asarray(size, dtype=np.float64) / 2.0)
    return ck.transform(P, R, center), T


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("torso", (0, 1.0, -0.2), (0, 2.3, -0.15), "root")
    rig.add("head", (0, 2.35, -0.1), (0, 3.0, -0.05), "torso")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"arm_{tag}", (s * 0.72, 2.1, -0.15), (s * 0.9, 1.25, 0.05), "torso")
        rig.add(f"fore_{tag}", (s * 0.9, 1.25, 0.05), (s * 0.75, 0.9, 0.6), f"arm_{tag}")
        rig.add(f"hand_{tag}", (s * 0.75, 0.9, 0.6), (s * 0.72, 0.85, 0.95), f"fore_{tag}")
    return rig


def stone(P: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray]:
    n = ck.fbm(P * 5.0, seed)
    col = ck.mix(PAL["laterite"] * 0.62, PAL["laterite"] * 0.9, (0.5 + 0.5 * n)[:, None])
    col = ck.mix(col, PAL["volcanic_stone"], (0.25 * ck.smoothstep(0.2, 0.5, n))[:, None])
    seams = ck.smoothstep(0.9, 0.98, np.abs(np.sin(P[:, 1] * 9.0)))  # coursed joints between blocks
    vert = ck.smoothstep(0.93, 0.99, np.abs(np.sin((P[:, 0] + 0.37 * np.floor(P[:, 1] * 9.0 / math.pi)) * 6.0)))
    seams = np.maximum(seams, vert * 0.8)
    return col * (1.0 - 0.45 * seams)[:, None], seams


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    parts = [
        ("root", (0, 0.35, 0.05), (1.6, 0.7, 1.3)),      # the seat and lap
        ("root", (0, 0.75, 0.35), (1.3, 0.25, 0.8)),     # thighs
        ("torso", (0, 1.25, -0.2), (1.2, 0.6, 0.8)),     # belly
        ("torso", (0, 1.8, -0.18), (1.35, 0.6, 0.75)),   # chest
        ("torso", (0, 2.2, -0.15), (1.5, 0.3, 0.65)),    # shoulders
        ("head", (0, 2.45, -0.1), (0.35, 0.25, 0.35)),   # neck
    ]
    for k, (bone, c, size) in enumerate(parts):
        P, T = block(c, size, round_=0.3)
        col, seams = stone(P, SEED + k)
        ember = np.zeros(len(P))  # the stone itself does not glow; the crust's cracks and the mouth do
        ck.finish(mesh, P, T, "stone", col, rig.rigid(bone), cavity=0.6 * seams, emission=ember)
    # the head: a calm mask, eyes closed, mouth open (the Watchers' language)
    Ph, Th = block((0, 2.78, -0.05), (0.62, 0.72, 0.55), 16, 22, round_=0.4)
    col, seams = stone(Ph, SEED + 20)
    face = Ph[:, 2] > 0.1
    lid = face & (np.abs(Ph[:, 1] - (2.9 - 0.03 * np.abs(Ph[:, 0]) / 0.2)) < 0.025) & (np.abs(np.abs(Ph[:, 0]) - 0.14) < 0.09)
    mouth_d = ((Ph[:, 0] / 0.11) ** 2 + ((Ph[:, 1] - 2.6) / 0.08) ** 2)
    mouth = face & (mouth_d < 1.0)
    Ph = Ph - np.array([0, 0, 1.0]) * (0.05 * np.clip(1.0 - mouth_d, 0, 1) * face)[:, None]  # the open mouth is a hollow
    col = np.where(lid[:, None], PAL["lacquer_black"], col)
    col = np.where(mouth[:, None], PAL["lacquer_black"] * 0.5 + PAL["ember_orange"] * 0.45, col)
    ck.finish(mesh, Ph, Th, "stone", col, rig.rigid("head"), cavity=np.where(mouth | lid, 1.0, 0.2 * seams),
              emission=np.where(mouth, 0.8 * np.clip(1.0 - mouth_d, 0, 1), 0.0))
    for k, (y, w, h, d) in enumerate(((3.16, 0.7, 0.12, 0.6), (3.28, 0.5, 0.12, 0.45), (3.4, 0.3, 0.14, 0.3))):
        P, T = block((0, y, -0.08), (w, h, d), round_=0.2)  # the stepped crown: a temple's tiers on her head
        col, seams = stone(P, SEED + 80 + k)
        ck.finish(mesh, P, T, "stone", col, rig.rigid("head"), cavity=0.4 * seams)
    P, T = block((0, 2.75, -0.42), (0.9, 0.95, 0.25), round_=0.3)  # a hood-slab behind the head
    col, seams = stone(P, SEED + 85)
    ck.finish(mesh, P, T, "stone", col, rig.rigid("torso"), cavity=0.4 * seams)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for bone, (a, b), w in ((f"arm_{tag}", ((s * 0.72, 2.1, -0.15), (s * 0.9, 1.25, 0.05)), 0.32),
                                (f"fore_{tag}", ((s * 0.9, 1.25, 0.05), (s * 0.75, 0.9, 0.6)), 0.28)):
            a, b = np.asarray(a), np.asarray(b)
            d = b - a
            L = np.linalg.norm(d)
            yaw = math.degrees(math.atan2(d[0], d[2]))
            pitch = -math.degrees(math.asin(d[1] / L))
            R = ck.rot_y(yaw) @ ck.rot_x(pitch)
            P, T = block((a + b) / 2, (w, w, L + 0.1), round_=0.3, R=R)
            col, seams = stone(P, SEED + 30)
            ck.finish(mesh, P, T, "stone", col, rig.rigid(bone), cavity=0.5 * seams)
        P, T = block((s * 0.74, 0.86, 0.8), (0.42, 0.12, 0.5), round_=0.25)  # the flat hand on the knee
        col, seams = stone(P, SEED + 31)
        ck.finish(mesh, P, T, "stone", col, rig.rigid(f"hand_{tag}"), cavity=0.4)


CRUST_PARTS = [  # (bone, centre, size, rounding) of the blocks the crust grows over
    ("torso", (0, 1.8, -0.18), (1.35, 0.6, 0.75), 0.3), ("torso", (0, 2.2, -0.15), (1.5, 0.3, 0.65), 0.3),
    ("torso", (0, 1.25, -0.2), (1.2, 0.6, 0.8), 0.3), ("root", (0, 0.75, 0.35), (1.3, 0.25, 0.8), 0.3),
    ("head", (0, 2.78, -0.05), (0.62, 0.72, 0.55), 0.45),
]


def crust(rig: ck.Rig) -> ck.Mesh:
    """Cooled magma grown over the blocks in thick patches, cracked with ember light (phase 1 only): a shell a few
    centimetres proud of each block, kept where noise says the flow pooled, thickest on top."""
    mesh = ck.Mesh("Crust")
    for k, (bone, c, size, rnd) in enumerate(CRUST_PARTS):
        P, T = block(c, size, 22, 34, round_=rnd)
        n = ck.fbm(P * 2.6, SEED + 60 + k)
        up = (P[:, 1] - c[1]) / (size[1] / 2)
        keep_v = n + 0.45 * up > (-0.15 if bone != "head" else 0.2)
        keep = keep_v[T].all(axis=1)
        cc = np.asarray(c)
        out = (P - cc) / np.maximum(np.linalg.norm(P - cc, axis=1, keepdims=True), 1e-6)
        thick = 0.045 + 0.07 * np.clip(n + 0.45 * up + 0.2, 0, 1)
        P = P + out * (thick + 0.015 * ck.fbm(P * 12.0, SEED + 70 + k))[:, None]
        vein = np.abs(ck.fbm(P * 4.5, SEED + 90 + k))
        crack = ck.smoothstep(0.035, 0.0, vein)  # thin veins along the noise's zero contour
        col = ck.mix(PAL["lacquer_black"], PAL["volcanic_stone"], (0.4 + 0.4 * ck.fbm(P * 6.0, 7 + k))[:, None])
        col = ck.mix(col, PAL["ember_orange"] * 0.75, crack[:, None])
        T2 = T[keep]
        used = np.unique(T2.reshape(-1))
        remap = np.full(len(P), -1, dtype=np.int64)
        remap[used] = np.arange(len(used))
        ck.finish(mesh, P[used], remap[T2], "crust", col[used], rig.rigid(bone), cavity=0.3 * (1 - crack[used]),
                  emission=crack[used])
    for s, tag in ((1.0, "l"), (-1.0, "r")):  # drips down the upper arms
        P, T = block((s * 0.82, 1.75, -0.08), (0.36, 0.5, 0.36), 10, 14, round_=0.5)
        crack = ck.smoothstep(0.88, 0.97, np.abs(np.sin(P[:, 1] * 20.0 + P[:, 0] * 9.0)))
        col = ck.mix(PAL["lacquer_black"], PAL["ember_orange"] * 0.7, crack[:, None])
        ck.finish(mesh, P, T, "crust", col, rig.rigid(f"arm_{tag}"), cavity=0.3, emission=crack)
    return mesh


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 4.0, loop=True)
    idle.wave("torso", amp_rot=(1.2, 0.0, 0.0), amp_loc=(0.0, 0.025, 0.0), cycles=1)
    idle.wave("head", amp_rot=(1.5, 2.0, 0.0), cycles=1, phase=0.8)
    attack = ck.Clip("attack", 1.6)  # a hand slam
    for t, raise_, lean in ((0.0, 0, 0), (0.6, 1.0, -0.4), (0.85, -0.3, 1.0), (1.05, -0.2, 0.8), (1.6, 0, 0)):
        attack.key("arm_r", t, (-70.0 * raise_ + 20.0 * max(-raise_, 0), 0, -15.0 * raise_))
        attack.key("fore_r", t, (-30.0 * raise_, 0, 0))
        attack.key("torso", t, (8.0 * lean, 0, 0))
    cast = ck.Clip("cast", 1.8)  # both hands rise, the seams flare
    for t, s in ((0.0, 0.0), (0.7, 1.0), (1.2, 1.0), (1.8, 0.0)):
        for tag, sg in (("l", 1), ("r", -1)):
            cast.key(f"arm_{tag}", t, (-55.0 * s, 0, 18.0 * s * sg))
            cast.key(f"fore_{tag}", t, (-40.0 * s, 0, 0))
        cast.key("head", t, (-12.0 * s, 0, 0))
    hit = ck.Clip("hit", 0.6)
    for k, t in enumerate(np.linspace(0, 0.6, 7)):
        s = 0.0 if k in (0, 6) else (1.0 if k % 2 else -1.0) * (1 - t / 0.6)
        hit.key("torso", float(t), (0, 0, 2.0 * s))
    phase = ck.Clip("phase_change", 2.0)  # the crust bursts off (the part swap is in creatures.json)
    for t, s in ((0.0, 0.0), (0.5, -1.0), (0.8, 1.0), (1.3, 0.3), (2.0, 0.0)):
        phase.key("torso", t, (6.0 * s, 0, 0), (0, 0.06 * abs(s), 0))
        for tag, sg in (("l", 1), ("r", -1)):
            phase.key(f"arm_{tag}", t, (0, 0, 20.0 * max(s, 0) * sg))
        phase.key("head", t, (-15.0 * max(s, 0), 0, 0))
    ko = ck.Clip("ko", 2.4)  # she settles forward, the head bowing; the glow goes out (the fade)
    for t, s in ((0.0, 0.0), (1.0, 0.6), (2.0, 1.0), (2.4, 1.0)):
        ko.key("torso", t, (18.0 * s, 0, 0), (0, -0.08 * s, 0.1 * s))
        ko.key("head", t, (30.0 * s, 0, 0))
        for tag in ("l", "r"):
            ko.key(f"arm_{tag}", t, (10.0 * s, 0, 0))
    return [idle, attack, cast, hit, ko, phase]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = ck.Mesh("cinder_matron")
    body(mesh, rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extra_meshes=[crust(rig)],
                              extras={"hymn_creature": "cinder_matron"})
    print(f"cinder_matron: {info}")


if __name__ == "__main__":
    main()
