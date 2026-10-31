"""The Cage, the Ch20 boss frame (M5-A3P-1851): docs/kb/art/creatures/act3/the_cage.md, as amended to seats by
act3_roster.md ("Reconciled with the Act III beat sheets", U07) and docs/kb/art/creatures/act3/the_cage_seats.md.

blender --background --factory-startup --python assets_src/creatures/the_cage/build_the_cage.py -- \
    --out assets/creatures/the_cage/the_cage.glb

Four Lit Age lamp bays on a shallow arc, moored by anchor chains: brass frames gone to patina, posts and arches of
salt-glass chimney tubes lit with bound light, a gimballed crown lamp over each and a keystone clasp (the weak point)
at each arch's top. In each bay a brass seat with armrests: the founder sits chained at the wrists and ankles (the
founders' figures are the characters track's; the frame gives them `q<n>_seat`). Each quarter is two meshes,
`Q<n>Whole` (lit, chained) and `Q<n>Broken` (dark, cracked, the chains parted, modelled open), swapped by the
`break_q<n>` phase. Every other part is the frame's and is rigid on one bone.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 9203
PAL = {k: ck.hexrgb(v) for k, v in {
    "brass": "#B08D57", "bronze_patina": "#5F8A78", "lacquer_black": "#1D1916", "salt_glass": "#BFE6E0",
    "gold_leaf": "#D4A437", "spawn_wound": "#3FE0C8",
}.items()}
FLOOR = PAL["lacquer_black"]

# The plan (the sheet): four bays on an arc of chord 4.0 m, 0.35 m deep, convex toward the party (+z)
ARC_DEPTH, HALF_CHORD = 0.35, 2.0
BAYS = [(-1.5, 2.9), (-0.5, 3.3), (0.5, 3.3), (1.5, 2.9)]  # bay centre x, crown height
SILL_Y = 0.30
POST_X, POST_R = 0.45, 0.045       # the side posts (salt-glass tubes)
ARCH_DROP = 0.28                   # the arch's apex below the crown (the crown lamp sits above it)
SPRING_DROP = 0.9                  # where the arch springs, below the crown
SEAT = (0.48, 0.56, 0.42)          # the seat: height over the sill, width, depth
ARM_Y, ARM_X = 0.92, 0.34          # the armrests (the wrist rings ride on their fronts)
WRIST = (0.34, 0.97, 0.1)          # the wrist rings (x mirrored), over the armrests' fronts
ANKLE = (0.14, 0.37, 0.2)          # the ankle shackles on the sill
RING_R, RING_T = 0.06, 0.012
LINK = (0.05, 0.028, 0.008)        # a shackle chain's link: length, width, wire radius
MOORING = (0.12, 0.07, 0.016)      # the anchor chain's heavier links
ANCHOR_BACK, ANCHOR_RING = 1.2, 0.14  # the anchor chain's floor ring: behind the rail, its radius
CLASP_OPEN = 35.0                  # the broken clasp's sprung half (deg about z)
RING_OPEN = 40.0                   # a broken wrist/ankle ring's swing (deg about z)
CROWN_R = 0.11


def arc_z(x: float) -> float:
    return ARC_DEPTH * (1.0 - (x / HALF_CHORD) ** 2)


def bay_yaw(x: float) -> float:
    """Outer bays turn 15 degrees outward, inner ones 5 (toward their own side)."""
    return math.copysign(15.0 if abs(x) > 1.0 else 5.0, x)


class Bay:
    """One quarter's frame of reference: bay-local (x across, y up, z out of the bay) to model space."""

    def __init__(self, n: int) -> None:
        self.n = n
        self.x, self.crown = BAYS[n - 1]
        self.R = ck.rot_y(bay_yaw(self.x))
        self.o = np.array([self.x, 0.0, arc_z(self.x)])
        self.apex = self.crown - ARCH_DROP
        self.spring = self.crown - SPRING_DROP

    def p(self, P) -> np.ndarray:
        P = np.asarray(P, dtype=np.float64)
        return P @ self.R.T + self.o

    def b(self, name: str) -> str:
        return f"q{self.n}_{name}"


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("frame", (0, 0.15, 0), (0, 0.15, 0.4), "root")
    for n in range(1, 5):
        q = Bay(n)
        rig.add(q.b("bay"), q.p((0, SILL_Y, 0)), q.p((0, q.spring, 0)), "frame")
        rig.add(q.b("seat"), q.p((0, SILL_Y + SEAT[0], -0.02)), q.p((0, SILL_Y + SEAT[0], 0.2)), q.b("bay"))
        for s, tag in ((1.0, "l"), (-1.0, "r")):
            w = q.p((s * WRIST[0], WRIST[1], WRIST[2]))
            rig.add(q.b(f"wrist_{tag}"), w, w + q.R @ np.array([0.0, 0.0, 0.1]), q.b("bay"))
            a = q.p((s * ANKLE[0], ANKLE[1], ANKLE[2]))
            rig.add(q.b(f"ankle_{tag}"), a, a + q.R @ np.array([0.0, 0.0, 0.1]), q.b("bay"))
        rig.add(q.b("crown"), q.p((0, q.apex + 0.06, 0)), q.p((0, q.crown, 0)), q.b("bay"))
        rig.add(q.b("clasp"), q.p((0, q.apex, 0.02)), q.p((0, q.apex, 0.12)), q.b("bay"))
        pts = anchor_points(q)
        for k in range(3):
            rig.add(q.b(f"chain_{k}"), pts[k], pts[k + 1], "frame" if k == 0 else q.b(f"chain_{k - 1}"))
    rig.add("vfx_core", (0.0, 2.6, 0.3), (0.0, 2.6, 0.5), "frame")  # the row of clasps: hits land on the frame
    return rig


# ---------------------------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------------------------
def box(c, size) -> tuple[np.ndarray, np.ndarray]:
    sx, sy, sz = (0.5 * float(v) for v in size)
    P = np.array([[x, y, z] for x in (-sx, sx) for y in (-sy, sy) for z in (-sz, sz)]) + np.asarray(c, float)
    T = np.array([(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1), (2, 3, 7), (2, 7, 6),
                  (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)])
    return P, T


def aged_brass(P: np.ndarray, seed: int, bright: float = 0.0) -> np.ndarray:
    """Brass going to patina with a thousand years under water; `bright` where it is worn (the rings)."""
    green = ck.smoothstep(-0.25, 0.45, ck.fbm(P * 4.0, seed)) * (1.0 - bright)
    col = ck.mix(PAL["brass"] * 0.8, PAL["bronze_patina"] * 0.85, (0.25 + 0.6 * green)[:, None])
    return np.maximum(col * (0.9 + 0.1 * ck.fbm(P * 11.0, seed + 1))[:, None], FLOOR)


def ring(c, axis_frame: np.ndarray, r: float, t: float, gap: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """A torus (or a C, with `gap` radians open) in the plane of axis_frame's x and y columns, centred at c."""
    a0 = gap * 0.5
    n = 10
    th = np.linspace(a0, 2.0 * math.pi - a0, n + (0 if gap else 1))
    if not gap:
        th = th[:-1]
    path = np.column_stack([np.cos(th), np.sin(th), np.zeros_like(th)]) * r
    path = path @ axis_frame.T + np.asarray(c, float)
    if gap:
        return ck.tube(path, t, 4)
    P, T = ck.tube(np.vstack([path, path[:1]]), t, 4, cap_start=False, cap_end=False)
    return P, T


def chain(mesh: ck.Mesh, path: np.ndarray, skin, seed: int, wet: float = 0.6, link=LINK) -> None:
    """Links along a polyline, each turned 90 degrees to the last: wet black iron with a patina bloom."""
    seg = np.diff(path, axis=0)
    cum = np.concatenate([[0.0], np.cumsum(np.linalg.norm(seg, axis=1))])
    count = max(int(cum[-1] / (link[0] * 0.8)), 1)
    for k in range(count):
        s = (k + 0.5) * cum[-1] / count
        i = min(int(np.searchsorted(cum, s)) - 1, len(seg) - 1)
        i = max(i, 0)
        f = (s - cum[i]) / max(cum[i + 1] - cum[i], 1e-9)
        c = path[i] + f * seg[i]
        d = seg[i] / np.linalg.norm(seg[i])
        side = np.cross(d, [0.0, 1.0, 0.0] if abs(d[1]) < 0.9 else [1.0, 0.0, 0.0])
        side /= np.linalg.norm(side)
        if k % 2:
            side = np.cross(d, side)
        th = np.linspace(0.0, 2.0 * math.pi, 7)[:-1]
        loop = np.outer(np.cos(th) * link[0] * 0.5, d) + np.outer(np.sin(th) * link[1] * 0.5, side) + c
        P, T = ck.tube(np.vstack([loop, loop[:1]]), link[2], 3, cap_start=False, cap_end=False)
        col = ck.mix(FLOOR * 1.25, PAL["bronze_patina"] * 0.6, 0.25 + 0.3 * float(ck.fbm(c[None] * 9.0, seed + k)[0]))
        ck.finish(mesh, P, T, "chain", np.maximum(col, FLOOR), skin, wet=wet,
                  cavity=0.3)


def anchor_points(q: Bay) -> list[np.ndarray]:
    """The anchor chain's bone points: from the back of the base rail down and back to its floor ring."""
    a = q.p((0.0, 0.2, -0.4))
    b = q.p((0.0, ANCHOR_RING * 0.35, -0.4 - ANCHOR_BACK))
    return [a + (b - a) * t + np.array([0.0, -0.05 * math.sin(math.pi * t), 0.0]) for t in (0.0, 1 / 3, 2 / 3, 1.0)]


def base_rail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The arc's base rail (0-0.3 m), brass plates over lacquer-black joints, with a moulding along its top."""
    xs = np.linspace(-HALF_CHORD - 0.05, HALF_CHORD + 0.05, 41)
    rows = []
    for x in xs:
        z = arc_z(x)
        dz = -2.0 * ARC_DEPTH * x / HALF_CHORD ** 2
        nrm = np.array([-dz, 0.0, 1.0]) / math.hypot(dz, 1.0)
        for y, off in ((0.0, 0.32), (0.3, 0.3), (0.3, -0.48), (0.0, -0.5)):
            rows.append(np.array([x, y, z]) + nrm * off)
    P = np.array(rows)
    T = ck.grid_tris(len(xs), 4, True)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    if float(fn[:, 1].sum()) < 0:
        T = ck.flip(T)
    joint = (np.abs(np.repeat(xs, 4) % 1.0 - 0.5) > 0.47).astype(float)  # a dark joint under each bay's edge
    col = ck.mix(aged_brass(P, SEED + 1), FLOOR, (0.8 * joint)[:, None])
    ck.finish(mesh, P, T, "frame", col, rig.rigid("frame"), cavity=0.3 + 0.4 * joint, flat=True)
    for side in (-1.0, 1.0):  # end caps
        x = side * (HALF_CHORD + 0.05)
        Pc, Tc = box((x, 0.15, arc_z(x) - 0.09), (0.04, 0.3, 0.82))
        ck.finish(mesh, Pc, Tc, "frame", FLOOR * 1.3, rig.rigid("frame"), flat=True)


def bay_frame(mesh: ck.Mesh, rig: ck.Rig, q: Bay) -> None:
    """The bay's brass: the sill, the seat with its armrests, collars at the posts' feet and the arch's spring,
    the wrist rings and ankle shackles (closed), and the anchor's floor ring. (The lit glass is Q<n>Whole's.)"""
    bb = rig.rigid(q.b("bay"))
    seed = SEED + 10 * q.n
    parts = [box((0, SILL_Y - 0.02, -0.05), (1.04, 0.04, 0.6)),            # the sill plate
             box((0, SILL_Y + SEAT[0] * 0.5, -0.06), (SEAT[1], SEAT[0], SEAT[2])),   # the seat
             box((0, SILL_Y + SEAT[0] + 0.03, -0.04), (SEAT[1] + 0.06, 0.05, SEAT[2] + 0.06))]  # its cushion plate
    for s in (-1.0, 1.0):
        parts.append(box((s * ARM_X, ARM_Y, -0.06), (0.07, 0.05, 0.42)))           # armrest
        parts.append(box((s * ARM_X, (ARM_Y + SILL_Y + SEAT[0]) * 0.5, 0.12), (0.05, ARM_Y - SILL_Y - SEAT[0], 0.05)))
        for y in (SILL_Y + 0.04, q.spring):                                          # post collars
            parts.append(box((s * POST_X, y, -0.05), (0.13, 0.08, 0.13)))
    for P, T in parts:
        P = q.p(P)
        ck.finish(mesh, P, T, "frame", aged_brass(P, seed), bb, cavity=0.25, flat=True)
    fr = q.R @ np.column_stack([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]])  # a ring lying flat
    P, T = ring(q.p((0.0, 0.03, -0.4 - ANCHOR_BACK)), fr, ANCHOR_RING, 0.025)
    ck.finish(mesh, P, T, "chain", np.maximum(FLOOR * 1.3, FLOOR), rig.rigid("root"), wet=0.6, cavity=0.3)
    pts = anchor_points(q)
    names = [q.b(f"chain_{k}") for k in range(3)]
    chain(mesh, np.array(pts), rig.chain(names, pts), seed + 5, link=MOORING)


def ring_frame(q: Bay) -> np.ndarray:
    """A shackle ring's plane: upright, facing out of the bay."""
    return q.R @ np.column_stack([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])


def lamp_bars(mesh: ck.Mesh, q: Bay, bb: int, lit: bool, seed: int) -> None:
    """The posts, the spine bar behind the seat and the arch: salt-glass chimney tubes, lit with bound light when
    whole; dark and cracked through (gaps in the tubes, a few shards) when broken."""
    rng = np.random.default_rng(seed)
    a, sp = q.apex, q.spring
    runs = []
    for s in (-1.0, 1.0):
        runs.append(np.array([[s * POST_X, SILL_Y, -0.05], [s * POST_X, sp, -0.05]]))
        runs.append(ck.bezier([np.array([s * POST_X, sp, -0.05]), np.array([s * POST_X, a - 0.05, -0.05]),
                               np.array([s * 0.05, a, -0.05])], 10))
    runs.append(np.array([[0.0, SILL_Y + SEAT[0], -0.29], [0.0, SILL_Y + SEAT[0] + 1.05, -0.29]]))  # the backrest
    for path in runs:
        path = q.p(path)
        if not lit:  # cracked through: the run breaks into pieces with gaps
            crack = rng.uniform(0.35, 0.65)
            pieces = [(0.0, crack - rng.uniform(0.02, 0.05)), (crack + rng.uniform(0.02, 0.05), 1.0)]
        else:
            pieces = [(0.0, 1.0)]
        for t0, t1 in pieces:
            sub = _resample(path, t0, t1, 2 if len(path) == 2 else 8)
            P, T = ck.tube(sub, POST_R, 6)
            glow = 1.0 if lit else 0.0
            col = PAL["salt_glass"] * (0.95 if lit else 0.45) * (0.9 + 0.1 * ck.fbm(P * 8.0, seed + 3))[:, None]
            ck.finish(mesh, P, T, "lampbar", np.maximum(col, FLOOR), bb, wet=0.8, emission=glow)


def _resample(path: np.ndarray, t0: float, t1: float, n: int) -> np.ndarray:
    seg = np.diff(path, axis=0)
    cum = np.concatenate([[0.0], np.cumsum(np.linalg.norm(seg, axis=1))])
    s = np.linspace(t0, t1, n) * cum[-1]
    return np.column_stack([np.interp(s, cum, path[:, k]) for k in range(3)])


def crown(mesh: ck.Mesh, rig: ck.Rig, q: Bay, lit: bool, seed: int) -> None:
    """The crown lamp: a salt-glass globe in a brass gimbal with a thin gold-leaf rim."""
    cb = rig.rigid(q.b("crown"))
    c = q.p((0.0, q.crown - CROWN_R - 0.02, 0.0))
    P, T = ck.ellipsoid(c, (CROWN_R, CROWN_R * 1.15, CROWN_R), 6, 10)
    col = PAL["salt_glass"] * (0.95 if lit else 0.4)
    ck.finish(mesh, P, T, "crown", col, cb, wet=0.8, emission=1.0 if lit else 0.0)
    fr = ring_frame(q)
    P, T = ring(c, fr, CROWN_R + 0.03, 0.012)
    ck.finish(mesh, P, T, "frame", aged_brass(P, seed), cb, cavity=0.2)
    eq = q.R @ np.column_stack([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
    P, T = ring(c, eq, CROWN_R + 0.004, 0.005)
    ck.finish(mesh, P, T, "frame", PAL["gold_leaf"], cb, wet=0.3)


def clasp(mesh: ck.Mesh, rig: ck.Rig, q: Bay, whole: bool, seed: int) -> None:
    """The keystone clasp at the arch's top. Whole: one brass block with the weak point, a 6 cm hairline seam in
    spawn_wound across its face. Broken: split down the seam, its left half sprung open (on the clasp bone, modelled
    open; `break_q<n>` keys it from shut), no mark."""
    c = np.array([0.0, q.apex, 0.0])
    if whole:
        P, T = ck.ellipsoid(c, (0.09, 0.07, 0.07), 6, 10)
        P = q.p(P)
        local = (P - q.p(c)) @ q.R
        seam = ck.smoothstep(0.006, 0.0, np.abs(local[:, 0])) * (local[:, 2] > 0.02) * (np.abs(local[:, 1]) < 0.03)
        col = ck.mix(aged_brass(P, seed, 0.3), PAL["spawn_wound"], seam[:, None])
        ck.finish(mesh, P, T, "clasp", col, rig.rigid(q.b("clasp")), cavity=0.2, emission=seam)
        return
    for s, bone in ((1.0, q.b("clasp")), (-1.0, q.b("bay"))):
        P, T = ck.ellipsoid(c + np.array([s * 0.045, 0.0, 0.0]), (0.045, 0.07, 0.07), 6, 6)
        P = q.p(P)
        if s > 0:  # sprung: turned about the clasp bone's head
            head = np.asarray(rig.bones[rig.index(bone)].head)
            P = (P - head) @ ck.rot_z(CLASP_OPEN).T + head
        ck.finish(mesh, P, T, "clasp", aged_brass(P, seed, 0.3), rig.rigid(bone), cavity=0.3)


def shackles(mesh: ck.Mesh, rig: ck.Rig, q: Bay, whole: bool, seed: int) -> None:
    """The wrist rings and ankle shackles with their chains. Whole: closed, chained to the posts' feet and the sill.
    Broken: each ring open (a C, swung on its bone, modelled open) with two links hanging off it, and a stub of
    chain left hanging at the post."""
    fr = ring_frame(q)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for kind, (x, y, z), to in (("wrist", WRIST, (POST_X - 0.04, SILL_Y + 0.12, -0.02)),
                                    ("ankle", ANKLE, (0.3, SILL_Y + 0.02, 0.12))):
            bone = q.b(f"{kind}_{tag}")
            bi = rig.rigid(bone)
            c = q.p((s * x, y, z))
            anchor = q.p((s * to[0], to[1], to[2]))
            r = RING_R if kind == "wrist" else RING_R * 0.9
            if whole:
                P, T = ring(c, fr, r, RING_T)
                ck.finish(mesh, P, T, "frame", aged_brass(P, seed, 0.6), bi, cavity=0.2)
                start = c + (anchor - c) / np.linalg.norm(anchor - c) * r
                chain(mesh, np.array([start, 0.5 * (start + anchor) + np.array([0.0, -0.03, 0.0]), anchor]),
                      rig.rigid(q.b("bay")), seed + 7)
                continue
            head = np.asarray(rig.bones[rig.index(bone)].head)
            turn = ck.rot_z(s * RING_OPEN).T
            P, T = ring(c, fr, r, RING_T, gap=0.9)
            P = (P - head) @ turn + head
            ck.finish(mesh, P, T, "frame", aged_brass(P, seed, 0.6), bi, cavity=0.2)
            low = c + np.array([0.0, -r, 0.0])
            dangle = np.array([low, low + np.array([0.0, -0.07, 0.01])])
            chain(mesh, (dangle - head) @ turn + head, bi, seed + 8)
            stub = np.array([anchor, anchor + np.array([0.0, -0.06, 0.0]) + (c - anchor) * 0.15])
            chain(mesh, stub, rig.rigid(q.b("bay")), seed + 9)


def quarter(rig: ck.Rig, q: Bay, whole: bool) -> ck.Mesh:
    mesh = ck.Mesh(f"Q{q.n}{'Whole' if whole else 'Broken'}")
    seed = SEED + 100 * q.n + (0 if whole else 50)
    lamp_bars(mesh, q, rig.rigid(q.b("bay")), whole, seed)
    crown(mesh, rig, q, whole, seed + 1)
    clasp(mesh, rig, q, whole, seed + 2)
    shackles(mesh, rig, q, whole, seed + 3)
    return mesh


def build_meshes(rig: ck.Rig) -> tuple[ck.Mesh, list[ck.Mesh]]:
    frame = ck.Mesh("the_cage")
    base_rail(frame, rig)
    quarters = []
    for n in range(1, 5):
        q = Bay(n)
        bay_frame(frame, rig, q)
        quarters += [quarter(rig, q, True), quarter(rig, q, False)]
    return frame, quarters


# ---------------------------------------------------------------------------------------------
# Clips (the sheet's table; nothing travels)
# ---------------------------------------------------------------------------------------------
BACK_EDGE = np.array([0.0, -0.15, -0.5])  # the rail's back edge, from the frame bone's head


def lean(rx: float) -> tuple[tuple, tuple]:
    """(rot, loc) of the frame leaning back by -rx about the rail's back edge, so its front lifts, never sinks."""
    R = ck.euler(rx, 0.0, 0.0)
    return (rx, 0.0, 0.0), tuple(BACK_EDGE - R @ BACK_EDGE)


def keyrows(c: ck.Clip, bone: str, table) -> None:
    for r in table:
        c.key(bone, r[0], r[1], r[2] if len(r) > 2 else (0.0, 0.0, 0.0))


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 6.0, loop=True)  # the lattice flexes as if water moved through it; the chains ease
    for n in range(1, 5):
        idle.wave(f"q{n}_bay", amp_rot=(0.0, 0.0, 0.8), cycles=1, phase=0.9 * n)
        idle.wave(f"q{n}_crown", amp_rot=(2.5, 0.0, 1.5), cycles=1, phase=1.3 * n + 0.4)
        idle.wave(f"q{n}_chain_0", amp_rot=(1.5, 0.0, 0.0), cycles=1, phase=0.7 * n)
        idle.wave(f"q{n}_chain_1", amp_rot=(1.0, 0.0, 0.0), cycles=1, phase=0.7 * n + 0.5)

    attack = ck.Clip("attack", 1.4)  # the drag (contact 0.6 s): the chains snap taut, the frame leans back 4 deg
    for t, s in ((0.0, 0.0), (0.4, 0.4), (0.6, 1.0), (0.85, 0.9), (1.4, 0.0)):
        rot, loc = lean(-4.0 * s)
        attack.key("frame", t, rot, loc)
        for n in range(1, 5):
            attack.key(f"q{n}_chain_0", t, (-5.0 * s, 0, 0))
            attack.key(f"q{n}_chain_1", t, (-3.0 * s, 0, 0))
            attack.key(f"q{n}_crown", t, (-8.0 * s, 0, 0))

    cast = ck.Clip("cast", 1.8)  # the tightening (contact 1.0 s): the bays draw in a notch, a held breath; it eases
    for t, s in ((0.0, 0.0), (0.6, 0.6), (1.0, 1.0), (1.3, 1.0), (1.8, 0.0)):
        for n in range(1, 5):
            side = -1.0 if BAYS[n - 1][0] < 0 else 1.0
            cast.key(f"q{n}_bay", t, (2.5 * s, 0, 1.5 * side * s))
            for tag, sx in (("l", 1.0), ("r", -1.0)):
                cast.key(f"q{n}_wrist_{tag}", t, (0, 0, -6.0 * sx * s))

    hit = ck.Clip("hit", 0.6)  # the struck side jolts back on its rail, the crown lamps swing, the chains snap
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.22, -0.4), (0.36, 0.15), (0.6, 0.0)):
        rot, loc = lean(-1.5 * s)
        hit.key("frame", t, (rot[0], 0, 1.2 * s), (loc[0], loc[1], loc[2] - 0.03 * s))
        for n in range(1, 5):
            hit.key(f"q{n}_crown", t, (-10.0 * s, 0, 5.0 * s))
            hit.key(f"q{n}_chain_0", t, (-3.0 * s, 0, 0))

    out = [idle, attack, cast, hit]
    for n in range(1, 5):
        out.append(break_clip(n))
    out.append(ko_clip())
    return out


def break_clip(n: int) -> ck.Clip:
    """A quarter breaks (4.0 s; the phase swaps Q<n>Whole for Q<n>Broken at 0): the clasp springs apart (0-0.3 s),
    the rings spring open (0.3-0.6 s; 0.5 s is the founder's cue), the bay jolts and its dark crown lamp swings
    (1.5-3.0 s), then it stills. Keyed from shut to rest, which is open."""
    c = ck.Clip(f"break_q{n}", 4.0)
    keyrows(c, f"q{n}_clasp", ((0.0, (0, 0, -CLASP_OPEN)), (0.05, (0, 0, -CLASP_OPEN)), (0.3, (0, 0, 0)),
                               (4.0, (0, 0, 0))))
    for tag, s in (("l", 1.0), ("r", -1.0)):
        for kind in ("wrist", "ankle"):
            keyrows(c, f"q{n}_{kind}_{tag}", ((0.0, (0, 0, -s * RING_OPEN)), (0.3, (0, 0, -s * RING_OPEN)),
                                              (0.6, (0, 0, 0)), (4.0, (0, 0, 0))))
    keyrows(c, f"q{n}_bay", ((0.0, (0, 0, 0)), (0.15, (-2.0, 0, 1.0)), (0.5, (0.8, 0, -0.4)), (1.0, (0, 0, 0)),
                             (4.0, (0, 0, 0))))
    keyrows(c, f"q{n}_crown", ((0.0, (0, 0, 0)), (1.5, (0, 0, 0)), (1.8, (12, 0, 4)), (2.2, (-8, 0, -3)),
                               (2.6, (4, 0, 1.5)), (3.0, (-1.5, 0, 0)), (3.4, (0, 0, 0)), (4.0, (0, 0, 0))))
    keyrows(c, f"q{n}_chain_0", ((0.0, (0, 0, 0)), (1.0, (0, 0, 0)), (1.2, (4, 0, 0)), (1.6, (2, 0, 0)),
                                 (4.0, (2, 0, 0))))
    return c


def ko_clip() -> ck.Clip:
    """The empty frame lets go (5.0 s): every anchor chain falls slack and the arches lean outward; the crown lamps
    swing and still. It ends on the floor, open. (The last quarter breaks by its phase, not here: the KO can't swap
    meshes.)"""
    c = ck.Clip("ko", 5.0)
    for n in range(1, 5):
        side = -1.0 if BAYS[n - 1][0] < 0 else 1.0
        keyrows(c, f"q{n}_bay", ((0.0, (0, 0, 0)), (1.0 + 0.3 * n, (0, 0, 0)), (2.5 + 0.3 * n, (0, 0, 5.0 * side)),
                                 (5.0, (0, 0, 5.0 * side))))
        keyrows(c, f"q{n}_crown", ((0.0, (0, 0, 0)), (2.5 + 0.3 * n, (10, 0, 4 * side)), (3.4 + 0.3 * n, (-5, 0, -2)),
                                   (5.0, (0, 0, 0))))
        for k, amp in ((0, 6.0), (1, 4.0), (2, 3.0)):
            keyrows(c, f"q{n}_chain_{k}", ((0.0, (0, 0, 0)), (0.6 + 0.2 * n, (amp, 0, 0)), (5.0, (amp, 0, 0))))
    return c


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    frame, quarters = build_meshes(rig)
    info = ck.export_creature(frame, rig, build_clips(), args.out, extra_meshes=quarters,
                              extras={"hymn_creature": "the_cage"})
    print(f"the_cage: {info} frame_tris={frame.triangle_count} "
          f"quarters={[m.triangle_count for m in quarters]}")


if __name__ == "__main__":
    main()
