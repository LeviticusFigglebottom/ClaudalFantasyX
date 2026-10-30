"""Held shoal, Ch20 the Undertow layers (M5-A3P-1803): docs/kb/art/creatures/act3/held_shoal.md.

blender --background --factory-startup --python assets_src/creatures/held_shoal/build_held_shoal.py -- \
    --out assets/creatures/held_shoal/held_shoal.glb
python3 assets_src/creatures/held_shoal/build_held_shoal.py --report   # numpy checks (the rise rule), no Blender

The sea's memory of fish: a school of 24 fish made of held light (glimmer_held, steady) in three rings of eight at 0.75,
1.0 and 1.25 m, slowly counter-turning round a fisher's glass net float that hangs still at 1.0 m in the middle, wrapped
in a scrap of net and crusted with the spawn's wet black. The float is what holds them; its crust carries the spawn's
one short open seam, lipped and lit spawn_wound: the weak point (ADR 0151). Each fish is ~26 small flattened beads
(Nhoa's bipyramids) scattered over a mackerel's narrow outline round a dark abyss_navy inner body, skinned to its
body and its tail. Held light never rises (color_script.md rule 1): every clip moves the fish sideways, their tails
beat side to side, and only the KO goes down; `--report` checks no vertex ever steps upward between baked frames.
Built hovering with its origin on the floor (as Nhoa and the chain lamp), so it needs no stand_in hover.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402
import grounding as gr  # noqa: E402

SEED = 1803
PAL = {k: ck.hexrgb(v) for k, v in {
    "salt_glass": "#BFE6E0", "abyss_navy": "#061A2B", "lacquer_black": "#1D1916", "sand_cloth": "#C9B48E",
    "spawn_wound": "#3FE0C8",
}.items()}

RINGS = ((0.75, 0.9, 1.0, 0.32), (1.0, 1.0, -1.0, 0.42), (1.25, 0.85, 1.0, 0.36))  # (height, radius, turn, fish length)
PER_RING = 8
BEADS = 26
BEAD_R = (0.015, 0.035)
MOTE_FLAT = (0.3, 0.2)
MOTE_GLOW = (0.4, 1.0)
TAIL_AT = -0.15  # a fish's tail starts this far back of its middle (a share of its length)
FLOAT_Y, FLOAT_R = 1.0, 0.15
SEAM_LEN = 0.08

BEAD_RANGES: list[tuple[int, int]] = []  # the light's vertices (the report's rise rule)


def fish_frame(r: int, k: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Fish k of ring r: its middle, its swimming direction (the way its ring turns), its outward side, its length."""
    y, rad, turn, ln = RINGS[r]
    a = (k + 0.5 * r) * 2.0 * math.pi / PER_RING
    mid = np.array([rad * math.sin(a), y, rad * math.cos(a)])
    t = turn * np.array([math.cos(a), 0.0, -math.sin(a)])
    out = np.array([math.sin(a), 0.0, math.cos(a)])
    return mid, t, out, ln


# ---------------------------------------------------------------------------------------------
# Rig: root; the float; three rings (each turns about the vertical); 24 fish of two (body, tail), each fish's bones
# lying level along its swimming direction, so every turn of them is about the vertical; `seam` on the float.
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.15, 0))
    rig.add("float", (0, FLOAT_Y, 0), (0, FLOAT_Y + 0.1, 0), "root")
    for r, (y, _rad, _turn, _ln) in enumerate(RINGS):
        rig.add(f"ring{r}", (0, y, 0), (0, y + 0.1, 0), "root")
        for k in range(PER_RING):
            mid, t, _out, ln = fish_frame(r, k)
            root = mid + t * TAIL_AT * ln
            rig.add(f"fish{r}_{k}", root, mid + t * 0.5 * ln, f"ring{r}")
            rig.add(f"tail{r}_{k}", root, mid - t * 0.5 * ln, f"fish{r}_{k}")
    rig.add("seam", seam_at(), seam_at() + np.array([0.0, 0.0, 0.08]), "float")
    return rig


def seam_at() -> np.ndarray:
    """The seam faces the party (+z) on the float's crust, a little below its equator."""
    return np.array([0.0, FLOAT_Y - 0.03, FLOAT_R + 0.012])


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def bead(c: np.ndarray, nrm: np.ndarray, r: float, phi: float) -> tuple[np.ndarray, np.ndarray]:
    """A flattened triangular bipyramid at c, its poles on nrm (Nhoa's mote)."""
    e1 = np.cross(nrm, (0.0, 1.0, 0.0) if abs(nrm[1]) < 0.9 else (1.0, 0.0, 0.0))
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(nrm, e1)
    V = [c + r * (math.cos(phi + k * 2.0 * math.pi / 3.0) * e1 + math.sin(phi + k * 2.0 * math.pi / 3.0) * e2)
         for k in range(3)]
    V += [c + nrm * r * MOTE_FLAT[0], c - nrm * r * MOTE_FLAT[1]]
    T = [(k, (k + 1) % 3, 3) for k in range(3)] + [((k + 1) % 3, k, 4) for k in range(3)]
    return np.array(V), np.array(T)


def profile(s: np.ndarray) -> np.ndarray:
    """A mackerel's side outline: deepest a little ahead of its middle, tapering to a narrow tail stalk, s in -0.5..0.5."""
    return np.clip(np.sin((s + 0.5) * math.pi) ** 0.8 * (1.0 - 0.35 * ck.smoothstep(-0.1, -0.5, s)), 0.08, 1.0)


def fish(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Each fish: its beads (the same scatter for every fish in a ring, so the ring's fish are identical and its idle
    loops by symmetry) over a dark inner body."""
    for r in range(len(RINGS)):
        rng = np.random.default_rng(SEED + r)
        s = rng.uniform(-0.48, 0.48, BEADS)
        phi = rng.uniform(0.0, 2.0 * math.pi, BEADS)
        rr = rng.uniform(*BEAD_R, BEADS) * (0.75 + 0.5 * RINGS[r][3] / 0.42)
        spin = rng.uniform(0.0, 2.0 * math.pi, BEADS)
        glow = rng.uniform(*MOTE_GLOW, BEADS)
        for k in range(PER_RING):
            mid, t, out, ln = fish_frame(r, k)
            up = np.array([0.0, 1.0, 0.0])
            h, w = 0.11 * ln, 0.045 * ln  # half depth (vertical) and half width: laterally pressed
            for j in range(BEADS):
                p = profile(np.array([s[j]]))[0]
                nrm = up * math.sin(phi[j]) * 0.6 + out * math.cos(phi[j])
                nrm /= np.linalg.norm(nrm)
                c = mid + t * s[j] * ln + up * h * p * math.sin(phi[j]) + out * w * p * math.cos(phi[j])
                P, T = bead(c, nrm, rr[j], spin[j])
                bone = f"tail{r}_{k}" if s[j] < TAIL_AT else f"fish{r}_{k}"
                start = mesh.count
                ck.finish(mesh, P, T, "beads", PAL["salt_glass"], rig.rigid(bone), wet=0.0, emission=glow[j])
                BEAD_RANGES.append((start, mesh.count))
            Pb, Tb = ck.ellipsoid((0.0, 0.0, 0.0), (w * 0.7, h * 0.7, 0.42 * ln), 4, 6)
            R = np.column_stack([out, up, t])
            Pb = Pb @ R.T + mid + t * 0.04 * ln
            ck.finish(mesh, Pb, Tb, "fishbody", PAL["abyss_navy"], rig.rigid(f"fish{r}_{k}"), wet=0.2)


def drowned_float(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The glass float, its crust of spawn carapace in patches (the glass bare between), a scrap of net round it, and
    the crust's one short open seam (lipped, lit) facing the party."""
    c = np.array([0.0, FLOAT_Y, 0.0])
    P, T = ck.ellipsoid(c, (FLOAT_R,) * 3, 9, 14)
    ck.finish(mesh, P, T, "float", PAL["salt_glass"] * 0.8, rig.rigid("float"), wet=0.6)
    Pc, Tc = ck.ellipsoid(c, (FLOAT_R + 0.008,) * 3, 9, 14)
    n = ck.fbm(Pc * 9.0, SEED + 10)
    keep = (n[Tc].mean(axis=1) > -0.08) | (Pc[Tc][:, :, 1].mean(axis=1) < FLOAT_Y - 0.06)  # crusted, thickest below
    to_seam = np.linalg.norm(Pc[Tc].mean(axis=1) - seam_at(), axis=1) < 0.06  # the crust is whole round the seam
    Tc = Tc[keep | to_seam]
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.3, n)[:, None])
    ck.finish(mesh, Pc, Tc, "crust", col, rig.rigid("float"), wet=1.0, cavity=0.4)
    for a0, tilt in ((0.0, 0.5), (1.9, -0.4), (3.6, 0.2)):  # a scrap of net: a few cords wrapped round it
        a = np.linspace(a0, a0 + 2.4, 12)
        rad = FLOAT_R + 0.014
        pts = np.column_stack([rad * np.sin(a), FLOAT_Y + rad * np.cos(a) * math.sin(tilt) * 0.6 + 0.02 * np.sin(3 * a),
                               rad * np.cos(a) * math.cos(tilt)])
        pts = c + (pts - c) * (rad / np.maximum(np.linalg.norm(pts - c, axis=1, keepdims=True), 1e-6))
        Pn, Tn = ck.tube(pts, np.full(len(pts), 0.004), 4)
        ck.finish(mesh, Pn, Tn, "crust", PAL["sand_cloth"] * 0.45, rig.rigid("float"), wet=0.9)
    # the seam: a short split through the crust, its lips raised either side and its depth lit
    sc = seam_at()
    along = np.array([1.0, 0.25, 0.0])
    along /= np.linalg.norm(along)
    for off, rad, lit in ((0.008, 0.006, 0.0), (-0.008, 0.006, 0.0), (0.0, 0.004, 1.0)):
        lip_dir = np.array([0.0, 1.0, 0.0]) - along * along[1]
        lip_dir /= np.linalg.norm(lip_dir)
        pts = np.array([sc + along * u + lip_dir * off for u in np.linspace(-SEAM_LEN / 2, SEAM_LEN / 2, 6)])
        pts = c + (pts - c) * ((FLOAT_R + 0.01 + (0.004 if lit == 0.0 else 0.0)) /
                               np.linalg.norm(pts - c, axis=1, keepdims=True))
        Ps, Ts = ck.tube(pts, np.full(len(pts), rad) * np.sin(np.linspace(0.3, math.pi - 0.3, len(pts))), 5)
        col = PAL["spawn_wound"] * 0.7 if lit else PAL["lacquer_black"] * 1.3
        ck.finish(mesh, Ps, Ts, "crust", col, rig.rigid("float"), wet=1.0, emission=lit)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("held_shoal")
    fish(mesh, rig)
    drowned_float(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips: every motion level or downward; the rings turn, the fish slide in and out along their rings' radii, the tails
# beat about the vertical
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 6.0
TURNED_SEC = 4.0
ATTACK_SEC, ATTACK_CONTACT = 1.2, 0.55
CAST_SEC, CAST_CONTACT = 1.6, 0.9
HIT_SEC = 0.5
KO_SEC = 2.0
SPACING = 360.0 / PER_RING
TAIL_DEG = 16.0
TURNED_IN = 0.5  # idle_turned: the rings drawn in to 1.0 m across


def tails(c: ck.Clip, length: float, beats: int, amp: float = TAIL_DEG) -> None:
    for r in range(len(RINGS)):
        for k in range(PER_RING):
            c.wave(f"tail{r}_{k}", amp_rot=(0, amp, 0), cycles=beats, phase=0.7 * r + 0.0 * k)
            c.wave(f"fish{r}_{k}", amp_rot=(0, amp * 0.25, 0), cycles=beats, phase=0.7 * r + math.pi)


def slide(c: ck.Clip, t: float, r: int, d: float) -> None:
    """Every fish of ring r slid d metres along its ring's radius (out positive), level."""
    for k in range(PER_RING):
        _mid, _t, out, _ln = fish_frame(r, k)
        c.key(f"fish{r}_{k}", t, (0, 0, 0), tuple(float(v) for v in out * d))


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # each ring turns one fish-spacing: the picture loops, the bones don't
    for r, (_y, _rad, turn, _ln) in enumerate(RINGS):
        for i in range(9):
            t = IDLE_SEC * i / 8
            c.key(f"ring{r}", t, (0, turn * SPACING * i / 8, 0))
    tails(c, IDLE_SEC, 6)
    c.key("float", 0.0)
    c.key("float", IDLE_SEC)
    return c


def build_turned() -> ck.Clip:
    c = ck.Clip("idle_turned", TURNED_SEC, loop=True)  # the targetable look: drawn in tight round the float
    for r, (_y, rad, turn, _ln) in enumerate(RINGS):
        for i in range(9):
            t = TURNED_SEC * i / 8
            c.key(f"ring{r}", t, (0, turn * SPACING * i / 8, 0))
        for k in range(PER_RING):
            _mid, _t, out, _ln2 = fish_frame(r, k)
            for t in (0.0, TURNED_SEC):
                c.key(f"fish{r}_{k}", t, (0, 0, 0), tuple(float(v) for v in out * (TURNED_IN - rad)))
        for k in range(PER_RING):
            c.wave(f"tail{r}_{k}", amp_rot=(0, TAIL_DEG * 0.7, 0), cycles=4, phase=0.7 * r)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # the turn: the three rings swing forward together toward the target, and back
    for r in range(len(RINGS)):
        for t, s in ((0.0, 0.0), (0.3, 0.3), (ATTACK_CONTACT, 1.0), (0.8, 0.5), (ATTACK_SEC, 0.0)):
            c.key(f"ring{r}", t, (0, 20.0 * s * RINGS[r][2], 0), (0, 0, 0.75 * s * (1.0 - 0.15 * abs(r - 1))))
        slide(c, 0.0, r, 0.0)
        slide(c, ATTACK_CONTACT, r, -0.25)
        slide(c, ATTACK_SEC, r, 0.0)
    tails(c, ATTACK_SEC, 3, TAIL_DEG * 1.4)
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # the rings spin up and tighten, then flare outward: the room's memory turning
    for r in range(len(RINGS)):
        turn = RINGS[r][2]
        for t, a in ((0.0, 0.0), (0.5, 50.0), (CAST_CONTACT, 140.0), (1.25, 170.0), (CAST_SEC, 180.0)):
            c.key(f"ring{r}", t, (0, turn * a, 0))
        for t, d in ((0.0, 0.0), (0.5, -0.3), (CAST_CONTACT, 0.45), (1.3, 0.15), (CAST_SEC, 0.0)):
            slide(c, t, r, d)
    tails(c, CAST_SEC, 4, TAIL_DEG * 1.3)
    return c


def build_hit() -> ck.Clip:
    c = ck.Clip("hit", HIT_SEC)  # pushed sideways away from the blow, the rings scatter out and gather back
    for r in range(len(RINGS)):
        for t, s in ((0.0, 0.0), (0.1, 1.0), (0.26, 0.45), (HIT_SEC, 0.0)):
            c.key(f"ring{r}", t, (0, -8.0 * s * RINGS[r][2], 0), (0, 0, -0.22 * s))
        for t, d in ((0.0, 0.0), (0.1, 0.18), (0.3, 0.06), (HIT_SEC, 0.0)):
            slide(c, t, r, d)
    return c


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # the float drops first; the fish lose their rings and sink, falling apart as they go
    for t, s in ((0.0, 0.0), (0.45, 1.0), (KO_SEC, 1.0)):
        c.key("float", t, (0, 0, 0), (0, -(FLOAT_Y - FLOAT_R - 0.01) * s, 0))
    for r, (y, _rad, turn, ln) in enumerate(RINGS):
        land = -(y - 0.11 * ln - 0.02)
        for t, s in ((0.0, 0.0), (0.3, 0.0), (1.0 + 0.15 * r, 0.75), (1.6 + 0.1 * r, 1.0), (KO_SEC, 1.0)):
            c.key(f"ring{r}", t, (0, turn * 12.0 * s, 0), (0, land * s, 0))
        for t, d in ((0.0, 0.0), (0.3, 0.0), (1.4, 0.25), (KO_SEC, 0.32)):
            slide(c, t, r, d)
    tails(c, KO_SEC, 3, TAIL_DEG * 0.6)
    return c


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_turned(), build_attack(), build_cast(), build_hit(), build_ko()]


# The KO sinks it onto the floor: the float and each ring lift the least it takes to lie on the floor, not through it.
GROUNDED_LIMBS = [("float", gr.LIFT, 1.0, 0.3, ("ko",))] + [(f"ring{r}", gr.LIFT, 1.0, 0.3, ("ko",)) for r in range(3)]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def report(rig: ck.Rig, mesh: ck.Mesh) -> None:
    """The triangle count, each clip's lowest point, and the rise rule: the largest upward step any light vertex (the
    beads) takes between consecutive baked frames (held light never rises; tolerance 1 mm)."""
    arrays = mesh.arrays()
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    poser = gr.Poser(rig, mesh)
    beads = np.zeros(len(arrays["pos"]), dtype=bool)
    for a, b in BEAD_RANGES:
        beads[a:b] = True
    for c in export_clips(rig, mesh):
        prev, rise, low = None, 0.0, np.inf
        for t in gr.frame_times(c):
            V = poser.vertices(poser.matrices(gr.pose_at(c, poser.names, t)))
            low = min(low, float(V[:, 1].min()))
            if prev is not None:
                rise = max(rise, float((V[beads, 1] - prev[beads, 1]).max()))
            prev = V
        print(f"{c.name:12s} {c.length:.2f}s: lowest {low:+.4f}; largest rise of the light {rise * 1000:.3f} mm")


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and the clip checks; no export")
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    if args.report or not args.out:
        report(rig, mesh)
        return
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "held_shoal"})
    print(f"held_shoal: {info}")


if __name__ == "__main__":
    main()
