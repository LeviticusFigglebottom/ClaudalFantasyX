"""The drowned hulls on the strait's reef edge and the reef itself (M3-ENV-08; brightwater_ferry.md §0, §2). Pure
numpy; see bf_common.py.

  derelict_hulk_a   a trader of the ferry's own kind (bf_common.hull_shell's vocabulary, so the two read as kin),
                    22 m, grounded with an 8 deg list to starboard and settled until her deck is barely above the
                    sea: dismasted (a 4 m mainmast stump with a sprung top, the foremast a stub), the starboard
                    bulwark stove in along half its length, her deck silvered with planks gone, the main yard fallen
                    across the deck and over the side.
  derelict_hulk_b   the fore half of another hull, bow up at 14 deg, the broken stern under water: the planking's
                    inside showing at the break, a raked foremast with its yard hanging from one end, a rag of sail.
  reef_awash        a 40 x 16 m patch of the reef edge: dark coral heads just breaking the surface.

Each piece's origin is at the sea's datum (the preview's water at y 0), so the hulls sit where they grounded.
Nothing on them emits light: the drowned carry no lamp.
"""

from __future__ import annotations

import math

import numpy as np

import bf_common as bf
from bf_common import kc

TRI_BUDGET = {"derelict_hulk_a": (16000, 1600), "derelict_hulk_b": (12000, 1200), "reef_awash": (8000, 800)}

FORM_A = bf.HullForm(stem_z=-11.5, transom_z=10.5, half_beam=3.0, taper_fwd_z=-4.0, taper_aft_z=6.0, transom_half=2.4,
                     poop_z=6.0, poop_y=0.8, bow_rise=0.5, gangways=())
LIST_A_DEG = 8.0  # to starboard
DECK_A_Y = 0.35  # the deck's height amidships above the sea, settled on the reef
STUMP_A = (1.0, 3.6)  # mainmast z, stump height above the deck
FORE_A_Z = -6.5
FORM_B = bf.HullForm(stem_z=-10.0, transom_z=0.0, half_beam=2.8, taper_fwd_z=-3.5, taper_aft_z=-0.5, transom_half=2.75,
                     poop_z=None, bow_rise=0.6, gangways=())
PITCH_B_DEG = 14.0  # bow up
DECK_B_Y = -0.9  # the broken end's deck, under the sea
FORE_B = (-6.2, 7.6, 10.0)  # mast z, height, extra rake aft (deg)
REEF_HALF = (20.0, 8.0)


def _jagged_top(mb: kc.MeshBuilder, rng, base, r: float, mat: str) -> None:
    """A sprung, splintered mast top: a ring of spikes of different heights."""
    base = np.asarray(base, float)
    i = mb.material(mat)
    n = 7
    for k in range(n):
        a = 2.0 * math.pi * k / n
        d = np.array([math.cos(a), 0.0, math.sin(a)]) * r * 0.6
        h = float(rng.uniform(0.15, 0.7))
        kc.tube(mb, np.array([base + d, base + d * 0.7 + np.array([0.0, h, 0.0])]), [r * 0.45, 0.01], 3, i,
                weather=bf.WRECK_W, cap_end=True)


def _transform(mb: kc.MeshBuilder, start: int, rot: np.ndarray, offset) -> None:
    p = np.asarray(mb.pos[start:], float) @ rot.T + np.asarray(offset, float)
    n = np.asarray(mb.nrm[start:], float) @ rot.T
    mb.pos[start:] = p.tolist()
    mb.nrm[start:] = n.tolist()


def build_hulk_a(seed: int = 881) -> list[kc.MeshBuilder]:
    out = []
    f = FORM_A
    for lod in (False, True):
        rng = kc.rng_for("derelict_hulk_a", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("derelict_hulk_a" + (bf.LOD if lod else ""))

        def ragged(z: float, side: float) -> float:
            if side > 0 and -7.0 < z < 2.0:  # stove in to the deck's edge
                return f.rail_h - 0.05 + 0.25 * float(noise.fbm(np.array([z * 0.7, 0.0, 3.0]), 2))
            return 0.12 * float(noise.fbm(np.array([z * 0.5, side, 0.0]), 2))

        bf.hull_sides(mb, f, lod=lod, tar=bf.M_WRECK_TAR, paint=bf.M_WRECK, ragged=ragged, noise=noise,
                      weather=bf.WRECK_W)
        bf.transom(mb, f, bf.M_WRECK_TAR, lod=lod)
        if lod:
            for z0, z1, y in ((f.stem_z + 0.8, f.poop_z, 0.0), (f.poop_z, f.transom_z - 0.1, f.poop_y)):
                zs = bf.rows_between(z0, z1, 2.5)
                grid = np.asarray([[[x, y, float(z)] for x in np.linspace(-float(f.half_beam_at(float(z))),
                                                                        float(f.half_beam_at(float(z))), 3)] for z in zs])
                kc.quad_strip(mb, grid, mb.material(bf.M_WRECK), uv=grid[..., [0, 2]], col=(0.0, 0.8, 0.4, 0.9),
                              uv2=(0.8, 0.5), flip=True, smooth=False)
        else:
            bf.sub_deck(mb, f, f.stem_z + 0.8, f.poop_z, -0.3, bf.M_DARK)
            bf.sub_deck(mb, f, f.poop_z, f.transom_z - 0.05, f.poop_y - 0.3, bf.M_DARK)
            keep = [(-1.0, 1.0, -1.6, -0.1)]  # the main hatch, open
            bf.deck_planks(mb, f, rng, noise, f.stem_z + 0.9, f.poop_z, 0.0, mat=bf.M_WRECK, holes=0.16, keep_out=keep,
                           weather=bf.WRECK_W)
            bf.deck_planks(mb, f, rng, noise, f.poop_z + 0.05, f.transom_z - 0.1, f.poop_y, mat=bf.M_WRECK, holes=0.22,
                           weather=bf.WRECK_W)
            for side in (-1.0, 1.0):
                bf.covering_board(mb, f, rng, noise, side, f.stem_z + 1.4, f.poop_z - 0.05, mat=bf.M_WRECK,
                                  weather=bf.WRECK_W)
            # The open main hatch's coaming.
            for cx, cz, sx, sz in ((0.0, -1.6, 1.1, 0.1), (0.0, -0.1, 1.1, 0.1), (-1.0, -0.85, 0.1, 0.75),
                                   (1.0, -0.85, 0.1, 0.75)):
                kc.rounded_block(mb, (cx, 0.15, cz), (sx, 0.2, sz), mb.material(bf.M_WRECK_TAR), radius=0.03, seg=1,
                                 weather=bf.WRECK_W, variation=float(rng.random()))
        for side in (-1.0, 1.0):
            gone = (lambda z: -7.0 < z < 2.0) if side > 0 else (lambda z: 3.2 < z < 4.6)
            bf.bulwark(mb, f, rng, noise, side, f.stem_z + 1.2, f.poop_z - 0.02, lod=lod, timber=bf.M_WRECK,
                       lining=bf.M_WRECK, gone=gone, weather=bf.WRECK_W)
            bf.bulwark(mb, f, rng, noise, side, f.poop_z + 0.02, f.transom_z - 0.12, lod=lod, timber=bf.M_WRECK,
                       lining=bf.M_WRECK, weather=bf.WRECK_W)
        # The masts: the main a stump, sprung at the top; the foremast a stub.
        mz, mh = STUMP_A
        kc.tube(mb, np.array([[0.0, -0.4, mz], [0.0, mh, mz]]), [0.27, 0.24], 6 if lod else 10, mb.material(bf.M_WRECK),
                weather=bf.WRECK_W, noise=None if lod else noise, disp_m=0.01)
        kc.tube(mb, np.array([[0.0, -0.4, FORE_A_Z], [0.0, 0.7, FORE_A_Z]]), [0.24, 0.23], 6 if lod else 10,
                mb.material(bf.M_WRECK), weather=bf.WRECK_W)
        if not lod:
            _jagged_top(mb, rng, (0.0, mh, mz), 0.24, bf.M_WRECK)
            _jagged_top(mb, rng, (0.0, 0.7, FORE_A_Z), 0.23, bf.M_WRECK)
        # The main yard, fallen across the deck from the stump's foot and out over the stove-in side.
        a = np.array([-2.1, 0.55, mz - 1.4])
        b = np.array([4.6, -0.6, mz - 6.8])
        kc.tube(mb, np.array([a, b]), [0.11, 0.08], 5 if lod else 8, mb.material(bf.M_WRECK), weather=bf.WRECK_W,
                cap_start=True, cap_end=True)
        if not lod:
            bf.rope(mb, (0.0, mh - 0.4, mz), a + np.array([0.3, 0.05, 0.1]), 0.02, bf.M_ROPE, sag=0.4, segs=6, sides=4)
            bf.rope(mb, b - np.array([0.4, -0.05, -0.3]), b + np.array([1.2, -1.2, 0.8]), 0.02, bf.M_ROPE, sag=0.2, segs=4,
                    sides=4)
            # The bowsprit, broken short.
            sz = f.stem_z
            hy = float(f.sheer_y(sz + 0.1))
            kc.tube(mb, np.array([[0.0, hy - 0.05, sz + 1.4], [0.0, hy + 0.35, sz - 1.0]]), [0.15, 0.13], 8,
                    mb.material(bf.M_WRECK), weather=bf.WRECK_W)
            _jagged_top(mb, rng, (0.0, hy + 0.35, sz - 1.0), 0.13, bf.M_WRECK)
        _transform(mb, 0, kc.rot_z(-math.radians(LIST_A_DEG)), (0.0, DECK_A_Y, 0.0))
        out.append(mb)
    return out


def build_hulk_b(seed: int = 891) -> list[kc.MeshBuilder]:
    out = []
    f = FORM_B
    for lod in (False, True):
        rng = kc.rng_for("derelict_hulk_b", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("derelict_hulk_b" + (bf.LOD if lod else ""))

        def ragged(z: float, side: float) -> float:
            # The break: the planking torn away raggedly over the last 2.5 m.
            t = float(kc.smoothstep(-2.5, 0.0, z))
            return t * (1.6 + 0.8 * float(noise.fbm(np.array([z * 1.3, side, 1.0]), 2))) + 0.1 * float(
                noise.fbm(np.array([z * 0.4, side, 0.0]), 2))

        bf.hull_sides(mb, f, lod=lod, tar=bf.M_WRECK_TAR, paint=bf.M_WRECK, ragged=ragged, noise=noise,
                      weather=bf.WRECK_W, inner=bf.M_WRECK_TAR)
        if lod:
            zs = bf.rows_between(f.stem_z + 0.8, -1.5, 2.5)
            grid = np.asarray([[[x, 0.0, float(z)] for x in np.linspace(-float(f.half_beam_at(float(z))),
                                                                      float(f.half_beam_at(float(z))), 3)] for z in zs])
            kc.quad_strip(mb, grid, mb.material(bf.M_WRECK), uv=grid[..., [0, 2]], col=(0.0, 0.8, 0.4, 0.9),
                          uv2=(0.8, 0.5), flip=True, smooth=False)
        else:
            bf.sub_deck(mb, f, f.stem_z + 0.8, -0.4, -0.3, bf.M_DARK)
            bf.deck_planks(mb, f, rng, noise, f.stem_z + 0.9, -0.3, 0.0, mat=bf.M_WRECK, holes=0.25, weather=bf.WRECK_W,
                           ragged_end=True)
        for side in (-1.0, 1.0):
            bf.bulwark(mb, f, rng, noise, side, f.stem_z + 1.2, -2.6, lod=lod, timber=bf.M_WRECK, lining=bf.M_WRECK,
                       gone=lambda z: -5.2 < z < -4.1, weather=bf.WRECK_W)
        # The foremast, raked further aft than the hull's pitch, its yard hanging from the masthead by one end.
        mz, mh, rake = FORE_B
        r = math.radians(rake)
        top = np.array([0.0, mh * math.cos(r), mz + mh * math.sin(r)])
        kc.tube(mb, np.array([[0.0, -0.4, mz], top]), [0.22, 0.14], 6 if lod else 10, mb.material(bf.M_WRECK),
                weather=bf.WRECK_W, noise=None if lod else noise, disp_m=0.01, cap_end=True)
        ya = top + np.array([-0.35, -0.4, 0.15])
        yb = np.array([-2.6, 1.0, mz - 2.2])
        kc.tube(mb, np.array([ya, yb]), [0.09, 0.07], 5 if lod else 8, mb.material(bf.M_WRECK), weather=bf.WRECK_W,
                cap_start=True, cap_end=True)
        # A rag of sail hanging from the yard, torn short.
        nu, nv = (3, 3) if lod else (12, 9)
        u = np.linspace(0.0, 1.0, nu)
        v = np.linspace(0.0, 1.0, nv)
        U, V = np.meshgrid(u, v)
        line = ya[None, None, :] + (yb - ya)[None, None, :] * U[..., None]
        tear = 0.35 + 0.65 * (noise.fbm(np.stack([U * 4.0, np.zeros_like(U), np.full_like(U, 2.0)], -1), 2))
        length = (2.6 - 1.8 * U) * tear
        g = line + np.stack([0.25 * np.sin(np.pi * V) * (1.0 - U) - 0.2 * V, -V * length, 0.15 * V], -1)
        if not lod:
            g = g + (noise.fbm(g / 0.4, 2)[..., None] - 0.5) * 0.08
        bf.cloth(mb, g, bf.M_WRECK_CANVAS, uv=np.stack([U * 4.0, V * 3.0], -1), noise=None if lod else noise,
                 weather=bf.WRECK_W, variation=0.4)
        if not lod:
            bf.rope(mb, top, np.array([2.2, 0.9, mz + 0.9]), 0.018, bf.M_ROPE, sag=0.25, segs=6, sides=4)
            sz = f.stem_z
            hy = float(f.sheer_y(sz + 0.1))
            kc.tube(mb, np.array([[0.0, hy - 0.05, sz + 1.4], [0.0, hy + 0.9, sz - 2.6]]), [0.15, 0.11], 8,
                    mb.material(bf.M_WRECK), weather=bf.WRECK_W, cap_end=True)
        _transform(mb, 0, kc.rot_x(math.radians(PITCH_B_DEG)), (0.0, DECK_B_Y, 0.0))
        out.append(mb)
    return out


def reef_height(noise: kc.Noise3, X: np.ndarray, Z: np.ndarray) -> np.ndarray:
    """The reef crest: a ridge along x just under the surface, coral heads breaking it, falling away at the edges."""
    hx, hz = REEF_HALF
    ridge = -0.55 - 1.4 * (Z / hz) ** 2
    p = np.stack([X / 3.0, np.zeros_like(X), Z / 3.0], -1)
    heads = np.clip(noise.fbm(p, 3) - 0.5, 0.0, None) * 2.6
    fine = (noise.fbm(p * 3.1 + 7.0, 2) - 0.5) * 0.25
    edge = kc.smoothstep(0.0, 4.0, hx - np.abs(X)) * kc.smoothstep(0.0, 2.5, hz - np.abs(Z))
    return (ridge + heads + fine) * edge + (-2.2) * (1.0 - edge)


def build_reef(seed: int = 901) -> list[kc.MeshBuilder]:
    out = []
    hx, hz = REEF_HALF
    for lod in (False, True):
        rng = kc.rng_for("reef_awash", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("reef_awash" + (bf.LOD if lod else ""))
        nx, nz = (21, 9) if lod else (71, 29)
        xs = np.linspace(-hx, hx, nx)
        zs = np.linspace(-hz, hz, nz)
        bf.bsc.heightfield(mb, xs, zs, lambda X, Z: reef_height(noise, X, Z), mb.material(bf.M_REEF),
                           wet=lambda X, Z, Y: np.clip(0.9 - Y * 0.8, 0.0, 1.0),
                           salt=lambda X, Z, Y: np.clip(Y * 1.5, 0.0, 0.6), erosion=0.7, variation=0.5,
                           ao=lambda X, Z, Y: 0.6 + 0.4 * np.clip(Y + 0.8, 0.0, 1.0))
        out.append(mb)
    return out


TARGETS = {"derelict_hulk_a": build_hulk_a, "derelict_hulk_b": build_hulk_b, "reef_awash": build_reef}
