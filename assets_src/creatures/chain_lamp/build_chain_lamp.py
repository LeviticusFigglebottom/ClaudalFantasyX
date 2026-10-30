"""Chain lamp, Ch19 the Iskarra Lamp Spire (M5-A3P-1801): docs/kb/art/creatures/act3/chain_lamp.md.

blender --background --factory-startup --python assets_src/creatures/chain_lamp/build_chain_lamp.py -- \
    --out assets/creatures/chain_lamp/chain_lamp.glb
python3 assets_src/creatures/chain_lamp/build_chain_lamp.py --report   # numpy checks, no Blender

A Lit Age signal lamp that keeps its own time: an eight-sided brass lamp-cage 0.9 m tall and 0.55 m across, hung on a
heavy iron chain from a ring 5.0 m up, its base at 0.9 m (the party's chest is where its beam meets them). Inside, a
salt-glass core holds its bound light (glimmer_bound, steady: the light never changes, the louvres do). Eight tall
brass louvres on vertical hinges close its sides, their inner faces lit_ceramic reflectors. A domed cap with a finial,
a drip cone under the base, and a shackle on the cap whose pin carries a hairline spawn_wound crack: the weak point
(ADR 0151), closed, a construct's; the KO is the shackle parting. Built hanging with its origin on the floor (as Nhoa is
built hovering), so it needs no stand_in hover; the chain's top never moves.
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

SEED = 1801
PAL = {k: ck.hexrgb(v) for k, v in {
    "brass": "#B08D57", "bronze_patina": "#5F8A78", "lacquer_black": "#1D1916", "salt_glass": "#BFE6E0",
    "glimmer_bound": "#4FB3B0", "spawn_wound": "#3FE0C8", "lit_ceramic": "#DCE3E0",
}.items()}

TOP = 5.0  # the chain's fixed ring
BASE_Y, CAP_Y = 0.9, 1.72  # the cage's base and the cap's rim
CAP_TOP = 1.84  # the cap's crown, where the shackle sits
SHACKLE_TOP = 1.95
R = 0.275  # the octagon's corner radius (0.55 m across)
SIDES = 8
N_CHAIN = 8  # chain bones
N_LINKS = 26
LINK = (0.13, 0.07, 0.013)  # a link's length, width and bar radius
LOUVRE_T = 0.008  # a louvre leaf's thickness
SLIT = 0.03  # the gap a shut leaf leaves at its free edge: the light shows through in slits (the sheet's battle read)

PARTS: dict[str, tuple[int, int]] = {}


def corner(k: int, r: float = R) -> np.ndarray:
    a = (k + 0.5) * 2.0 * math.pi / SIDES
    return np.array([r * math.sin(a), 0.0, r * math.cos(a)])


def mark(name: str, mesh: ck.Mesh, start: int) -> None:
    lo, _hi = PARTS.get(name, (start, start))
    PARTS[name] = (min(lo, start), mesh.count)


# ---------------------------------------------------------------------------------------------
# Rig: root on the floor; a chain of eight hanging from the ring (the first swings everything below it); the shackle;
# the cage on the root (its head at the cap's crown, so it turns from there; while it hangs, its keys follow the chain's
# swing as a pendulum from the ring, `swing`; when the shackle parts it falls on its own); eight louvres hinged on the cage's corners
# (louvre k's hinge is corner k, its leaf closing side k toward corner k+1); and `beam`, an attach bone at the cage's
# centre pointing out of side 0 (+z, the louvres the cast opens), for battle VFX's cone.
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.15, 0))
    ys = np.linspace(TOP, SHACKLE_TOP, N_CHAIN + 1)
    parent = "root"
    for i in range(N_CHAIN):
        rig.add(f"chain{i}", (0, ys[i], 0), (0, ys[i + 1], 0), parent)
        parent = f"chain{i}"
    rig.add("shackle", (0, SHACKLE_TOP, 0), (0, CAP_TOP, 0), parent)
    rig.add("cage", (0, CAP_TOP, 0), (0, BASE_Y, 0), "root")
    for k in range(SIDES):
        c = corner(k)
        rig.add(f"louvre{k}", (c[0], BASE_Y + 0.06, c[2]), (c[0], CAP_Y - 0.03, c[2]), "cage")
    mid = (BASE_Y + CAP_Y) / 2
    rig.add("beam", (0, mid, 0), (0, mid, 0.3), "cage")
    return rig


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def aged_brass(P: np.ndarray, seed: int, patina: float = 0.0) -> np.ndarray:
    n = ck.fbm(P * 12.0, seed)
    p = np.clip(0.1 + 0.45 * ck.smoothstep(0.0, 0.35, n) + patina, 0.0, 0.85)
    return ck.mix(PAL["brass"], PAL["bronze_patina"], p[:, None])


def ring(mesh: ck.Mesh, rig: ck.Rig, y: float, r: float, rad: float, seed: int) -> None:
    pts = np.array([corner(k, r) + np.array([0.0, y, 0.0]) for k in range(SIDES + 1)])
    P, T = ck.tube(pts, np.full(len(pts), rad), 6, cap_start=False, cap_end=False)
    ck.finish(mesh, P, T, "cage", aged_brass(P, seed), rig.rigid("cage"), wet=0.1, cavity=0.3)


def cage(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The frame: eight corner posts, the top and base rings, the domed cap with its finial, the drip cone."""
    for k in range(SIDES):
        c = corner(k)
        P, T = ck.tube(np.array([c + [0, BASE_Y + 0.03, 0], c + [0, CAP_Y, 0]]), np.array([0.012, 0.012]), 6)
        ck.finish(mesh, P, T, "cage", aged_brass(P, SEED + k), rig.rigid("cage"), wet=0.1, cavity=0.3)
    ring(mesh, rig, BASE_Y + 0.04, R + 0.008, 0.016, SEED + 10)
    ring(mesh, rig, CAP_Y, R + 0.01, 0.018, SEED + 11)
    # the base plate the louvres close on
    Pb, Tb = ck.lathe([(0.0, BASE_Y + 0.045), (R, BASE_Y + 0.045), (R, BASE_Y + 0.03), (0.0, BASE_Y + 0.03)], SIDES)
    ck.finish(mesh, Pb, Tb, "cage", aged_brass(Pb, SEED + 12, 0.15), rig.rigid("cage"), wet=0.1, cavity=0.4)
    # the domed cap, going bronze_patina toward its crown, and the finial
    cap = [(R + 0.03, CAP_Y), (R + 0.02, CAP_Y + 0.025), (R * 0.75, CAP_Y + 0.07), (R * 0.4, CAP_Y + 0.105),
           (0.04, CAP_TOP - 0.005), (0.0, CAP_TOP)]
    Pc, Tc = ck.lathe(cap[::-1], SIDES * 2)  # crown first: ck.lathe's outward faces run top to bottom
    up = ck.smoothstep(CAP_Y, CAP_TOP, Pc[:, 1])
    ck.finish(mesh, Pc, Tc, "cage", aged_brass(Pc, SEED + 13, 0.35 * up), rig.rigid("cage"), wet=0.1, cavity=0.4)
    # the drip cone under the base, its tip at the base height
    cone = [(0.0, BASE_Y - 0.0), (0.03, BASE_Y + 0.008), (0.1, BASE_Y + 0.025), (0.16, BASE_Y + 0.03)]
    Pd, Td = ck.lathe(cone[::-1], SIDES * 2)
    ck.finish(mesh, Pd, Td, "cage", aged_brass(Pd, SEED + 14, 0.2), rig.rigid("cage"), wet=0.1, cavity=0.4)


def louvres(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Eight tall brass leaves, each hinged on corner k and closing side k toward corner k+1: brass outside, worn
    bright on its free edge, its inner face a lit_ceramic reflector."""
    y0, y1 = BASE_Y + 0.06, CAP_Y - 0.03
    for k in range(SIDES):
        a, b = corner(k, R - 0.004), corner(k + 1, R - 0.004)
        along = b - a
        w = float(np.linalg.norm(along)) - 0.008 - SLIT
        u = along / np.linalg.norm(along)
        n = np.array([u[2], 0.0, -u[0]])  # outward, away from the centre
        if n @ ((a + b) / 2) < 0:
            n = -n
        h0 = a + u * 0.008
        P, T = _box(h0 + u * (w / 2) + np.array([0.0, (y0 + y1) / 2, 0.0]), u, n, w / 2, (y1 - y0) / 2, LOUVRE_T / 2)
        inner = ((P - (h0 + u * (w / 2))) @ n) < 0
        free = ck.smoothstep(w * 0.75, w, (P - h0) @ u)
        col = ck.mix(aged_brass(P, SEED + 20 + k), PAL["brass"] * 1.2, (0.7 * free)[:, None])
        col = np.where(inner[:, None], PAL["lit_ceramic"] * 0.9, col)
        ck.finish(mesh, P, T, "louvre", col, rig.rigid(f"louvre{k}"), wet=0.1, cavity=0.2)


def _box(c, u, n, hu, hy, hn) -> tuple[np.ndarray, np.ndarray]:
    """A box centred at c with half-extents along u (width), y (height) and n (thickness), flat-shaded by faces."""
    v = np.array([0.0, 1.0, 0.0])
    faces = []
    for ax, s, e1, e2, h1, h2, hd in ((n, 1, u, v, hu, hy, hn), (n, -1, v, u, hy, hu, hn), (u, 1, v, n, hy, hn, hu),
                                       (u, -1, n, v, hn, hy, hu), (v, 1, n, u, hn, hu, hy), (v, -1, u, n, hu, hn, hy)):
        o = c + ax * s * hd
        q = [o - e1 * h1 - e2 * h2, o + e1 * h1 - e2 * h2, o + e1 * h1 + e2 * h2, o - e1 * h1 + e2 * h2]
        faces.append(np.array(q))
    P = np.vstack(faces)
    T = np.array([[4 * f, 4 * f + 1, 4 * f + 2] for f in range(6)] + [[4 * f, 4 * f + 2, 4 * f + 3] for f in range(6)])
    return P, T


def lamp(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The salt-glass core and the bound light in it (one emissive shape: the glass glows with it, steady)."""
    mid = (BASE_Y + CAP_Y) / 2
    core = [(0.0, mid - 0.24), (0.09, mid - 0.2), (0.14, mid - 0.07), (0.14, mid + 0.09), (0.09, mid + 0.22),
            (0.0, mid + 0.25)]
    P, T = ck.lathe(core[::-1], 14)
    ck.finish(mesh, P, T, "lamp", ck.mix(PAL["salt_glass"], PAL["glimmer_bound"], 0.55), rig.rigid("cage"),
              wet=0.4, emission=1.0)
    Ps, Ts = ck.tube(np.array([[0.0, mid - 0.37, 0.0], [0.0, mid - 0.24, 0.0]]), np.array([0.02, 0.016]), 8)
    ck.finish(mesh, Ps, Ts, "cage", aged_brass(Ps, SEED + 30), rig.rigid("cage"), wet=0.1, cavity=0.3)


def chain(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Twenty-six heavy iron links from the ring down to the shackle, alternating their planes, each riding the chain
    bone it hangs in; the ring at the top; the shackle and its pin (the weak point's hairline crack round it)."""
    L, W, rad = LINK
    step = (TOP - SHACKLE_TOP) / N_LINKS
    for j in range(N_LINKS):
        yc = TOP - (j + 0.5) * step
        b = min(int((TOP - yc) / ((TOP - SHACKLE_TOP) / N_CHAIN)), N_CHAIN - 1)
        a = np.linspace(0.0, 2.0 * math.pi, 13)
        loop = np.column_stack([W / 2 * np.sin(a), (L / 2) * np.cos(a), np.zeros_like(a)])
        if j % 2:
            loop = loop[:, [2, 1, 0]]
        loop = loop + np.array([0.0, yc, 0.0])
        P, T = ck.tube(loop, np.full(len(loop), rad), 5, cap_start=False, cap_end=False)
        rust = ck.smoothstep(0.1, 0.4, ck.fbm(P * 20.0, SEED + 40 + j))
        col = ck.mix(PAL["lacquer_black"] * 1.3, PAL["bronze_patina"] * 0.5, (0.3 * rust)[:, None])
        ck.finish(mesh, P, T, "chain", col, rig.rigid(f"chain{b}"), wet=0.0, cavity=0.3)
    a = np.linspace(0.0, 2.0 * math.pi, 17)
    ring_pts = np.column_stack([0.07 * np.sin(a), TOP + 0.07 * np.cos(a) + 0.05, np.zeros_like(a)])
    P, T = ck.tube(ring_pts, np.full(len(ring_pts), 0.016), 6, cap_start=False, cap_end=False)
    ck.finish(mesh, P, T, "chain", PAL["lacquer_black"] * 1.2, rig.rigid("root"), wet=0.0, cavity=0.3)
    # the shackle: a bow over the cap's eye, its pin across the bottom of it
    a = np.linspace(-0.15 * math.pi, 1.15 * math.pi, 11)
    bow = np.column_stack([0.045 * np.cos(a), CAP_TOP + 0.03 + 0.07 * np.sin(a), np.zeros_like(a)])
    P, T = ck.tube(bow, np.full(len(bow), 0.012), 6)
    ck.finish(mesh, P, T, "chain", PAL["lacquer_black"] * 1.2, rig.rigid("shackle"), wet=0.0, cavity=0.3)
    pin = np.array([[-0.065, CAP_TOP + 0.02, 0.0], [0.065, CAP_TOP + 0.02, 0.0]])
    P, T = ck.tube(pin, np.array([0.009, 0.009]), 8)
    crack = ck.smoothstep(0.012, 0.0, np.abs(P[:, 0] - 0.018))  # the hairline crack round the pin, near one end
    col = ck.mix(PAL["lacquer_black"], PAL["spawn_wound"] * 0.65, crack[:, None])
    ck.finish(mesh, P, T, "pin", col, rig.rigid("shackle"), wet=0.1, emission=crack)
    # the cap's eye the shackle passes through
    a = np.linspace(0.0, 2.0 * math.pi, 13)
    eye = np.column_stack([0.025 * np.sin(a), CAP_TOP + 0.02 + 0.025 * np.cos(a), np.zeros_like(a)])[:, [0, 1, 2]]
    eye = np.column_stack([np.zeros(len(a)), eye[:, 1], eye[:, 0]])
    P, T = ck.tube(eye, np.full(len(eye), 0.008), 5, cap_start=False, cap_end=False)
    ck.finish(mesh, P, T, "cage", aged_brass(P, SEED + 50, 0.3), rig.rigid("cage"), wet=0.1)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("chain_lamp")
    cage(mesh, rig)
    louvres(mesh, rig)
    lamp(mesh, rig)
    chain(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips (the sheet's table): the light never changes; the louvres open on the beat
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 4.0
BEATS = (1.0, 3.0)
BEAT_SEC = 0.3
BEAT_DEG = 25.0
ATTACK_SEC = 1.0
ATTACK_CONTACT = 0.45
CAST_SEC = 2.6
CAST_CONTACT = 1.3
TURN = (0.4, 2.2)  # the cast's one full turn
HIT_SEC = 0.6
KO_SEC = 1.8
KO_PART, KO_LAND = 0.3, 0.75
OPEN_DEG = 80.0
FRONT = (7, 0)  # the louvres on the +z side (the target's): their sides face the beam
SWEEP = (6, 7, 0)  # the side the sweep opens


OPEN_SIGN = -1.0  # the hinge turn (about the vertical) that swings a leaf out about its corner


def open_louvre(c: ck.Clip, k: int, t: float, deg: float) -> None:
    c.key(f"louvre{k}", t, (0, OPEN_SIGN * deg, 0))


PIVOT = np.array([0.0, TOP, 0.0])
CAGE_HEAD = np.array([0.0, CAP_TOP, 0.0])


def swing(c: ck.Clip, t: float, ax: float, az: float, own=(0.0, 0.0, 0.0)) -> None:
    """The chain swung (ax, 0, az) degrees from its ring, and the hanging cage with it: the cage's head carried round the
    ring as a pendulum's bob, turned with the chain, plus its own turn `own`."""
    W = ck.euler(ax, 0.0, az)
    loc = W @ (CAGE_HEAD - PIVOT) + PIVOT - CAGE_HEAD
    c.key("chain0", t, (ax, 0.0, az))
    c.key("cage", t, (ax + own[0], own[1], az + own[2]), tuple(float(v) for v in loc))


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)
    for i in range(17):  # a 2 degree sway at the cage over the chain's length, and a slow turn on it
        t = IDLE_SEC * i / 16
        w = 2.0 * math.pi * t / IDLE_SEC
        swing(c, t, 0.8 * math.sin(w), 0.6 * math.sin(w), (0.0, 1.5 * math.sin(w + 0.7), 0.0))
    for k in range(SIDES):
        open_louvre(c, k, 0.0, 0.0)
        for b in BEATS:
            open_louvre(c, k, b, 0.0)
            open_louvre(c, k, b + BEAT_SEC * 0.45, BEAT_DEG)
            open_louvre(c, k, b + BEAT_SEC, 0.0)
        open_louvre(c, k, IDLE_SEC, 0.0)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # the flash: the louvres facing the target snap open and shut
    for k in range(SIDES):
        open_louvre(c, k, 0.0, 0.0)
        open_louvre(c, k, ATTACK_SEC, 0.0)
    for k in FRONT:
        for t, d in ((0.3, 0.0), (ATTACK_CONTACT, OPEN_DEG), (0.62, OPEN_DEG * 0.8), (0.8, 0.0)):
            open_louvre(c, k, t, d)
    for t, s in ((0.0, 0.0), (ATTACK_CONTACT, 1.0), (ATTACK_SEC, 0.0)):
        swing(c, t, -0.6 * s, 0.0)
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # the sweep: one side opens, the cage turns once, the beam crosses the field
    for k in range(SIDES):
        open_louvre(c, k, 0.0, 0.0)
        open_louvre(c, k, CAST_SEC, 0.0)
    for k in SWEEP:
        for t, d in ((0.15, 0.0), (0.35, OPEN_DEG), (2.3, OPEN_DEG), (2.5, 0.0)):
            open_louvre(c, k, t, d)
    c.key("cage", 0.0, (0, 0, 0))
    c.key("cage", TURN[0], (0, 0, 0))
    n = 12
    for i in range(1, n + 1):
        u = i / n
        e = u * u * (3.0 - 2.0 * u)
        c.key("cage", TURN[0] + (TURN[1] - TURN[0]) * u, (0, 360.0 * e, 0))
    c.key("cage", CAST_SEC, (0, 360.0, 0))
    return c


def build_hit() -> ck.Clip:
    c = ck.Clip("hit", HIT_SEC)  # knocked back on its chain, a decaying swing; the louvres rattle half open
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.24, -0.55), (0.38, 0.28), (0.5, -0.1), (HIT_SEC, 0.0)):
        swing(c, t, -2.4 * s, 0.6 * s, (-3.0 * s, 0.0, 0.0))
    for k in range(SIDES):
        for t, d in ((0.0, 0.0), (0.1, 40.0 if k % 2 else 28.0), (0.24, 10.0), (0.36, 16.0), (HIT_SEC, 0.0)):
            open_louvre(c, k, t, d)
    return c


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # the shackle parts; the cage falls to the floor, tips onto its side and rocks still
    drop = CAP_TOP  # the pivot (the cap's crown) comes down by the cage's whole height as it tips onto its side
    for t, dy, rz, dx in ((0.0, 0.0, 0.0, 0.0), (KO_PART, 0.0, 0.0, 0.0), (KO_LAND, -BASE_Y, 0.0, 0.0),
                          (1.1, -BASE_Y - 0.35, 60.0, 0.12), (1.3, -drop + R + 0.02, 92.0, 0.42),
                          (1.48, -drop + R + 0.02, 84.0, 0.42), (1.62, -drop + R + 0.02, 90.0, 0.42),
                          (KO_SEC, -drop + R + 0.02, 89.0, 0.42)):
        c.key("cage", t, (0, 0, rz), (dx, dy, 0))
    for k in range(SIDES):  # every louvre shuts as it lands: its light is shut in
        for t, d in ((0.0, 12.0), (KO_PART, 30.0), (KO_LAND - 0.05, 18.0), (KO_LAND + 0.1, 0.0), (KO_SEC, 0.0)):
            open_louvre(c, k, t, d)
    for t, s in ((0.0, 0.0), (KO_PART, 0.0), (0.55, 1.0), (0.9, 0.6), (KO_SEC, 0.75)):  # the broken end whips up
        c.key(f"chain{N_CHAIN - 1}", t, (0, 0, 70.0 * s))
        c.key(f"chain{N_CHAIN - 2}", t, (0, 0, 45.0 * s))
        c.key("shackle", t, (0, 0, 40.0 * s))
    return c


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_attack(), build_cast(), build_hit(), build_ko()]


# The KO lands it: the cage lifts the least it takes to lie on the floor, not through it.
GROUNDED_LIMBS = [("cage", gr.LIFT, 1.0, 0.6, ("ko",))]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def report(rig: ck.Rig, mesh: ck.Mesh) -> None:
    arrays = mesh.arrays()
    rest = arrays["pos"]
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    poser = gr.Poser(rig, mesh)
    for c in export_clips(rig, mesh):
        low = gr.lowest(poser, c)
        print(f"{c.name:7s} {c.length:.2f}s: lowest {min(low):+.4f}, at the end {low[-1]:+.4f}")


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
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "chain_lamp"})
    print(f"chain_lamp: {info}")


if __name__ == "__main__":
    main()
