"""The Kite (kite.md; M3-ENV-725): Dace's hull finished at Hollowmere and flown as the party's hub from Ch18 to the
Ending. Pure numpy.

Built in the Haluna kit (its import kind and materials), on hollowmere.py's lines for Dace's hull: the frame Rhen
finds in Ch17 (dace_hull_frame) is this hull before its planking. Origins: the deck's centre at y 0, the bow +X.

  kite_hull    the hull, planked both sides now and decked: the keel 3.3 m under the deck, the stem rising at +X and
               the sternpost at -X; a rail on posts round the deck, the hatch amidships, the tiller at the stern,
               Dace's ledger chest lashed by the hatch, a lamp post at bow and stern with a bound-light lantern.
  kite_rig     the rig, after Virel (vowbound.md §3: a ribbon of sailcloth panels): the mast (11 m over the deck)
               and two kite wings spread from it, each a delta of five battened sailcloth panels in sand and red with
               timber spars; from the sternpost, the ribbon tail of small panels streaming aft on a cord.
  kite_engine  one bound-light lift engine on its outrigger: a bronze drum along X under a ring of vanes, salt-glass
               bands showing the bound core, and the two arms that carry it out from the hull (built on the +Z side;
               the zone mirrors it for -Z). At H09 every bound light goes out: the core and the lanterns are
               `kit_bound_core`, so one material swap darkens them all (act3_ending.md).
"""

from __future__ import annotations

import math

import numpy as np

import hollowmere as hm
import kit_common as kc

M_TIMBER = "kit_timber"
M_DRIFT = "kit_driftwood"
M_TAR = "kit_interior_dark"
M_SAIL = "kit_cloth_sand"
M_SAIL_RED = "kit_keth_red"
M_LASH = "kit_lashing"
M_BRONZE = "kit_iskarra_bronze"
M_COPPER = hm.M_COPPER
M_GLASS = "kit_salt_glass"
M_CORE = "kit_bound_core"

TRI_BUDGET = {"kite_hull": (16000, 1200), "kite_rig": (10000, 800), "kite_engine": (4000, 300)}

DECK_DROP = hm.SHEER_Y  # Dace's sheer height over his keel datum: the deck is at y 0 here
MAST_X = 1.0
MAST_H = 11.0
ENGINE_Z = hm.DACE_HALF_BEAM + 1.6
ENGINE_Y = -1.6
WOOD = hm.WOOD


def _oriented(mb, grid, mat, want, **kw) -> None:
    """quad_strip turned so the first quad's face points along `want` (a vector, or a callable of its centre)."""
    n = np.cross(grid[0, 1] - grid[0, 0], grid[1, 0] - grid[0, 0])
    c = (grid[0, 0] + grid[1, 1]) * 0.5
    w = want(c) if callable(want) else np.asarray(want, float)
    kc.quad_strip(mb, grid, mat, flip=bool(np.dot(n, w) < 0.0), **kw)


def _rib(x: float, t: float) -> tuple[float, float]:
    y, z = hm._rib_point(x, t)
    return y - DECK_DROP, z


def build_hull(seed: int = 2501) -> list[kc.MeshBuilder]:
    out = []
    half = hm.DACE_LEN * 0.5
    for lod in (False, True):
        rng = kc.rng_for("kite_hull", seed)
        mb = kc.MeshBuilder("kite_hull" + ("-lod1" if lod else ""))
        timber, tar = mb.material(M_TIMBER), mb.material(M_TAR)
        nx, nt = (9, 4) if lod else (25, 9)
        xs = np.linspace(-half, half, nx)
        ts = np.linspace(0.0, 1.0, nt)
        kw = dict(col=(0.0, 0.15, 0.2, 0.5), uv2=(0.8, 0.5))
        for side in (-1.0, 1.0):  # the planking, keel to sheer, each side
            grid = np.array([[[x, _rib(x, t)[0], side * _rib(x, t)[1]] for x in xs] for t in ts])
            _oriented(mb, grid, timber, (0.0, 0.0, side), uv=grid[..., [0, 1]], **kw)
        # The deck at y 0 between the sheer lines, and the tarred keel under it all.
        across = np.linspace(-1.0, 1.0, 3 if lod else 7)
        hw = np.array([_rib(x, 1.0)[1] for x in xs])
        deck = np.stack([np.stack([xs, np.zeros(nx), a * hw], -1) for a in across])
        _oriented(mb, deck, timber, (0.0, 1.0, 0.0), uv=deck[..., [0, 2]], **kw)
        kc.rounded_block(mb, (0.0, hm.KEEL_Y - DECK_DROP - 0.06, 0.0), (half, 0.14, 0.12), tar, radius=0.02, seg=1)
        t = np.linspace(0.0, 1.0, 4 if lod else 9)
        stem = np.stack([half + 0.9 * t ** 1.6, hm.KEEL_Y - DECK_DROP + (DECK_DROP + 0.9 - hm.KEEL_Y) * t,
                         np.zeros_like(t)], -1)
        kc.tube(mb, stem, 0.12, 4 if lod else 6, timber)
        kc.tube(mb, np.array([[-half, hm.KEEL_Y - DECK_DROP, 0.0], [-half - 0.4, 1.4, 0.0]]), 0.12, 4 if lod else 6,
                timber)
        if lod:
            out.append(mb)
            continue
        # The rail on posts round the deck, open at the bow for the stem.
        for side in (-1.0, 1.0):
            rx = np.linspace(-half + 0.6, half - 0.9, 14)
            top = np.stack([rx, np.full_like(rx, 0.9), side * (np.array([_rib(x, 1.0)[1] for x in rx]) - 0.08)], -1)
            kc.tube(mb, top, 0.04, 6, timber)
            for p in top:
                kc.tube(mb, np.array([[p[0], 0.0, p[2]], [p[0], 0.9, p[2]]]), 0.035, 5, timber)
        # Deck seams, the hatch, the tiller, the ledger chest lashed by the hatch.
        for z in np.arange(-1.6, 1.61, 0.22):
            inside = np.array([_rib(x, 1.0)[1] for x in xs]) > abs(z) + 0.05
            if inside.sum() < 2:
                continue
            xa, xb = xs[inside][0], xs[inside][-1]
            g = np.array([[[xa, 0.002, z - 0.005], [xb, 0.002, z - 0.005]], [[xa, 0.002, z + 0.005], [xb, 0.002, z + 0.005]]])
            _oriented(mb, g, tar, (0.0, 1.0, 0.0), uv=np.zeros((2, 2, 2)), col=(0, 0, 0, 0), uv2=(0.9, 0.5), smooth=False)
        kc.rounded_block(mb, (-1.0, 0.15, 0.0), (0.8, 0.15, 0.6), timber, radius=0.04, seg=1, weather=WOOD)
        kc.rounded_block(mb, (-1.0, 0.32, 0.0), (0.7, 0.02, 0.5), tar, radius=0.01, seg=1)
        kc.tube(mb, np.array([[-half + 0.2, 0.6, 0.0], [-half + 1.6, 1.0, 0.0]]), np.array([0.07, 0.04]), 6, timber)
        kc.tube(mb, np.array([[-half + 0.2, 0.0, 0.0], [-half + 0.2, 0.6, 0.0]]), 0.09, 6, timber)
        kc.rounded_block(mb, (-1.0, 0.22, 1.0), (0.4, 0.22, 0.26), mb.material(M_DRIFT), radius=0.03, seg=1,
                         weather=WOOD)
        for dx in (-0.25, 0.25):
            a = np.linspace(0.0, math.pi, 7)
            loop = np.stack([np.full_like(a, -1.0 + dx), 0.22 + np.sin(a) * 0.25, 1.0 + np.cos(a) * 0.3], -1)
            kc.tube(mb, loop, 0.02, 4, mb.material(M_LASH))
        # The lamp posts at bow and stern, each with its lantern of bound light.
        for x, h in ((half - 0.5, 1.9), (-half + 0.5, 2.2)):
            kc.tube(mb, np.array([[x, 0.0, 0.0], [x, h, 0.0]]), np.array([0.06, 0.045]), 6, timber, cap_end=True)
            hm._lantern(mb, (x + (0.35 if x > 0 else -0.35), h - 0.35, 0.0), False)
            kc.tube(mb, np.array([[x, h - 0.05, 0.0], [x + (0.35 if x > 0 else -0.35), h - 0.05, 0.0]]), 0.025, 4,
                    timber)
        del rng
        out.append(mb)
    return out


def _sail(mb, a, b, c, d, n: int, lod: bool, rng) -> None:
    """A battened sail between edges a-b (inner) and c-d (outer, a->c and b->d running out along the spars): n
    panels, sand and red in turn, battens of timber between them; both faces built."""
    sand, red, timber = mb.material(M_SAIL), mb.material(M_SAIL_RED), mb.material(M_TIMBER)
    for k in range(n):
        u0, u1 = k / n, (k + 1) / n
        p0, p1 = a + (c - a) * u0, a + (c - a) * u1
        q0, q1 = b + (d - b) * u0, b + (d - b) * u1
        sag = np.array([0.0, -0.08, 0.0]) * (0.6 + 0.4 * rng.random())
        mid0, mid1 = (p0 + q0) * 0.5 + sag, (p1 + q1) * 0.5 + sag
        grid = np.array([[p0, p1], [mid0, mid1], [q0, q1]])
        mat = red if k % 2 else sand
        uv = np.array([[[u0, 0.0], [u1, 0.0]], [[u0, 0.5], [u1, 0.5]], [[u0, 1.0], [u1, 1.0]]]) * 2.0
        for flip in (False, True):
            kc.quad_strip(mb, grid, mat, uv=uv, col=(0.0, 0.0, 0.0, 0.3), uv2=(0.9, 0.5), flip=flip, smooth=False)
        if not lod and k > 0:
            kc.tube(mb, np.array([p0, mid0, q0]), 0.03, 4, timber)


def build_rig(seed: int = 2502) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("kite_rig", seed)
        mb = kc.MeshBuilder("kite_rig" + ("-lod1" if lod else ""))
        timber, lash = mb.material(M_TIMBER), mb.material(M_LASH)
        sides = 6 if lod else 10
        kc.tube(mb, np.array([[MAST_X, 0.0, 0.0], [MAST_X, MAST_H, 0.0]]), np.array([0.16, 0.09]), sides, timber,
                cap_end=True)
        head = np.array([MAST_X, MAST_H - 0.6, 0.0])
        foot = np.array([MAST_X - 0.4, 5.0, 0.0])
        for side in (-1.0, 1.0):
            tip = np.array([MAST_X - 2.4, 7.8, side * 8.5])  # a little dihedral, clear over the deck
            root_aft = np.array([MAST_X - 3.8, 5.2, side * 0.4])
            # The spars: masthead to tip (the leading edge), the foot to the tip, the aft root to the tip.
            for a in (head, foot, root_aft):
                kc.tube(mb, np.array([a, tip]), 0.06, 4 if lod else 6, timber)
            # Two sails per wing: forward (head-foot to tip) and aft (foot-root to tip), five panels in all.
            _sail(mb, head, foot, tip, tip, 3, lod, rng)
            _sail(mb, foot, root_aft, tip, tip, 2, lod, rng)
            if not lod:  # stays from the tip to the deck edge, and from the masthead
                kc.tube(mb, np.array([tip, [MAST_X - 1.0, 0.9, side * 1.8]]), 0.012, 3, lash)
                kc.tube(mb, np.array([head + [0.0, 0.5, 0.0], tip]), 0.012, 3, lash)
        # The ribbon tail: small panels on a cord from the sternpost top, streaming aft and down in an easy S.
        n = 6 if lod else 14
        t = np.linspace(0.0, 1.0, n + 1)
        stern = np.array([-hm.DACE_LEN * 0.5 - 0.4, 1.4, 0.0])
        path = np.stack([stern[0] - 9.0 * t, stern[1] - 1.6 * t + 0.4 * np.sin(t * 2 * math.pi), 0.9 * np.sin(t * 3.0)], -1)
        if not lod:
            kc.tube(mb, path, 0.012, 3, lash)
        for k in range(n):
            c = (path[k] + path[k + 1]) * 0.5
            w = 0.45 * (1.0 - 0.5 * t[k])
            p0 = c + np.array([0.3, 0.0, 0.0])
            p1 = c - np.array([0.3, 0.0, 0.0])
            g = np.array([[p0 + [0.0, w, 0.0], p1 + [0.0, w, 0.0]], [p0 - [0.0, w * 0.2, 0.0], p1 - [0.0, w * 0.2, 0.0]]])
            mat = mb.material(M_SAIL_RED if k % 2 else M_SAIL)
            for flip in (False, True):
                kc.quad_strip(mb, g, mat, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]), col=(0, 0, 0, 0.3),
                              uv2=(0.9, 0.5), flip=flip, smooth=False)
        out.append(mb)
    return out


def build_engine(seed: int = 2503) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("kite_engine" + ("-lod1" if lod else ""))
        bronze, glass, core, timber = (mb.material(M_BRONZE), mb.material(M_GLASS), mb.material(M_CORE),
                                       mb.material(M_TIMBER))
        sides = 8 if lod else 16
        c = np.array([0.0, ENGINE_Y, ENGINE_Z])
        # The drum: bronze ends and a salt-glass middle over the bound core.
        kc.tube(mb, np.array([c - [1.0, 0, 0], c - [0.45, 0, 0]]), np.array([0.5, 0.62]), sides, bronze, cap_start=True)
        kc.tube(mb, np.array([c + [0.45, 0, 0], c + [1.0, 0, 0]]), np.array([0.62, 0.5]), sides, bronze, cap_end=True)
        kc.tube(mb, np.array([c - [0.45, 0, 0], c + [0.45, 0, 0]]), 0.6, sides, glass)
        kc.tube(mb, np.array([c - [0.4, 0, 0], c + [0.4, 0, 0]]), 0.3, sides // 2, core, cap_start=True, cap_end=True)
        if not lod:  # the vane ring round the drum's aft end
            for k in range(10):
                a = 2 * math.pi * k / 10
                d = np.array([0.0, math.cos(a), math.sin(a)])
                kc.rounded_block(mb, c - [0.75, 0, 0] + d * 0.82, (0.18, 0.02, 0.16), bronze,
                                 rot=kc.rot_x(-a), radius=0.0, seg=1)
            ring = np.stack([np.full(25, c[0] - 0.75), c[1] + np.cos(np.linspace(0, 2 * math.pi, 25)) * 1.0,
                             c[2] + np.sin(np.linspace(0, 2 * math.pi, 25)) * 1.0], -1)
            kc.tube(mb, ring, 0.035, 4, bronze)
        # The outrigger arms from the hull side (the turn of the bilge) to the drum.
        for dx in (-0.7, 0.7):
            y_b, z_b = _rib(dx, 0.55)
            kc.tube(mb, np.array([[dx, y_b, z_b], c + [dx, 0.45, -0.3]]), 0.08, 4 if lod else 6, timber)
        out.append(mb)
    return out


TARGETS = {"kite_hull": build_hull, "kite_rig": build_rig, "kite_engine": build_engine}
