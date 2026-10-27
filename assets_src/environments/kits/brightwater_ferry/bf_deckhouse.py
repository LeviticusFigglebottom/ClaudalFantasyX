"""The ferry's deckhouse and the passengers' awning (M3-ENV-08; brightwater_ferry.md §0, §2). Pure numpy; see
bf_common.py.

  ferry_deckhouse   3.8 x 4.0 m on the main deck aft of the mainmast: lime-washed boards over a sea-blue dado,
                    corner posts, a cambered tarred-canvas roof with grab rails, the open door in the fore face,
                    four lamp-lit windows, and inside on the after wall the Order niche (the save point): a marble
                    basin on a plinth in an arched recess.
  ferry_awning      the passengers' awning between the foremast and the gangways: two ridge posts and four side
                    posts, the ridge spar and side spars, faded teal cloth sagging between them with a scalloped
                    valance, lashed to the posts.

Both in the hull's frame (bf_hull.ferry_hull).
"""

from __future__ import annotations

import math

import numpy as np

import bf_common as bf
from bf_common import kc

TRI_BUDGET = {"ferry_deckhouse": (16000, 1600), "ferry_awning": (6000, 600)}
X0, X1, Z0, Z1, WALL_H = bf.DECKHOUSE
WALL_T = 0.08
DADO_H = 0.8
DOOR = (-0.4, 0.4, 1.85)  # x0, x1, height (fore wall)
WINDOW_Z = (4.4, 6.4)
WINDOW = (0.5, 1.15, 1.6)  # width along z, sill, head
ROOF_CAMBER = 0.14
ROOF_EAVE = 0.14
NICHE = (0.0, 0.62, 1.55)  # x centre, half width, arch springing height (on the after wall, inside)
AWNING_Z = (-7.2, -3.2)
AWNING_RIDGE_Y = 2.45
AWNING_SIDE_X = 2.3
AWNING_SIDE_Y = 1.9
WALL_W = kc.Weathering(moss=0.0, salt=0.2, wet=0.0, erosion=0.12)  # the lime-wash is kept up: little edge wear


def roof_y(x) -> np.ndarray:
    half = (X1 - X0) * 0.5 + ROOF_EAVE
    return WALL_H + ROOF_CAMBER * (1.0 - (np.asarray(x, float) / half) ** 2)


def _panel(mb: kc.MeshBuilder, rng, axis: str, fixed: float, a0: float, a1: float, y0: float, y1: float, mat: str) -> None:
    """A wall panel: along x (axis "x", at z = fixed) or along z (axis "z", at x = fixed)."""
    if a1 - a0 < 0.02 or y1 - y0 < 0.02:
        return
    c = 0.5 * (a0 + a1)
    h = 0.5 * (a1 - a0)
    if axis == "x":
        center, half = (c, 0.5 * (y0 + y1), fixed), (h, 0.5 * (y1 - y0), WALL_T * 0.5)
    else:
        center, half = (fixed, 0.5 * (y0 + y1), c), (WALL_T * 0.5, 0.5 * (y1 - y0), h)
    kc.rounded_block(mb, center, half, mb.material(mat), radius=0.008, seg=1, weather=WALL_W,
                     variation=float(rng.random()))


def _wall(mb: kc.MeshBuilder, rng, axis: str, fixed: float, a0: float, a1: float, holes, *, lod: bool) -> None:
    """A wall from a0 to a1 with rectangular holes [(h0, h1, y0, y1)]: dado below DADO_H, lime-wash above, a chair
    rail between; panels are cut around each hole."""
    for y0, y1, mat in ((0.0, DADO_H, bf.M_BLUE), (DADO_H, WALL_H, bf.M_LIME)):
        cuts = sorted({a0, a1} | {h for hole in holes for h in hole[:2]})
        for s0, s1 in zip(cuts[:-1], cuts[1:]):
            inside = [hole for hole in holes if hole[0] <= s0 and s1 <= hole[1]]
            if not inside:
                _panel(mb, rng, axis, fixed, s0, s1, y0, y1, mat)
                continue
            hy0, hy1 = inside[0][2], inside[0][3]
            _panel(mb, rng, axis, fixed, s0, s1, y0, min(y1, hy0), mat)
            _panel(mb, rng, axis, fixed, s0, s1, max(y0, hy1), y1, mat)
    if lod:
        return
    # The chair rail and the board joints (thin battens on the lime-wash, every 0.3 m).
    i_t = mb.material(bf.M_TIMBER)
    off = WALL_T * 0.5 + 0.012
    for s in (-1.0, 1.0):
        if axis == "x":
            kc.plank(mb, (a0, DADO_H, fixed + s * off), (a1, DADO_H, fixed + s * off), 0.06, 0.03, i_t, up=(0.0, 0.0, s),
                     weather=bf.RAIL_W, variation=float(rng.random()))
        else:
            kc.plank(mb, (fixed + s * off, DADO_H, a0), (fixed + s * off, DADO_H, a1), 0.06, 0.03, i_t, up=(s, 0.0, 0.0),
                     weather=bf.RAIL_W, variation=float(rng.random()))


def _window(mb: kc.MeshBuilder, side: float, z: float, *, lod: bool) -> None:
    w, sill, head = WINDOW
    x = side * X1
    i_t = mb.material(bf.M_TIMBER)
    # The glow: a pane set in the wall's thickness (lamp light from inside), and a dark frame.
    kc.rounded_block(mb, (x, 0.5 * (sill + head), z), (0.012, 0.5 * (head - sill), w * 0.5), mb.material(bf.M_WINDOW),
                     radius=0.004, seg=1)
    if lod:
        return
    for dz in (-w * 0.5 - 0.03, w * 0.5 + 0.03):
        kc.rounded_block(mb, (x, 0.5 * (sill + head), z + dz), (0.06, 0.5 * (head - sill) + 0.04, 0.03), i_t, radius=0.01,
                         seg=1)
    for y in (sill - 0.02, head + 0.02, 0.5 * (sill + head)):
        kc.rounded_block(mb, (x, y, z), (0.06 if y != 0.5 * (sill + head) else 0.03, 0.025, w * 0.5 + 0.05), i_t,
                         radius=0.008, seg=1)
    kc.rounded_block(mb, (x, 0.5 * (sill + head), z), (0.03, 0.5 * (head - sill), 0.015), i_t, radius=0.005, seg=1)


def _roof(mb: kc.MeshBuilder, rng, noise, *, lod: bool) -> None:
    half = (X1 - X0) * 0.5 + ROOF_EAVE
    xs = np.linspace(-half, half, 3 if lod else 13)
    zs = np.linspace(Z0 - ROOF_EAVE, Z1 + ROOF_EAVE, 2 if lod else 9)
    X, Z = np.meshgrid(xs, zs)
    top = np.stack([X, roof_y(X) + 0.06, Z], -1)
    if not lod:
        top[..., 1] += (noise.fbm(top / 0.4, 2) - 0.5) * 0.01
    bf.cloth(mb, top, bf.M_TARP, uv=np.stack([X, Z], -1), noise=None if lod else noise, thick=0.06, back=bf.M_LIME,
             variation=0.5)
    i_t = mb.material(bf.M_TIMBER)
    # Fascia boards round the eave, and the grab rails along both sides.
    for z in (Z0 - ROOF_EAVE, Z1 + ROOF_EAVE):
        pts = np.stack([xs, roof_y(xs) + 0.02, np.full_like(xs, z)], -1)
        kc.tube(mb, pts, 0.05, 4, i_t, weather=bf.RAIL_W)
    for s in (-1.0, 1.0):
        x = s * half
        kc.plank(mb, (x, roof_y(x) + 0.02, Z0 - ROOF_EAVE), (x, roof_y(x) + 0.02, Z1 + ROOF_EAVE), 0.12, 0.05, i_t,
                 up=(s * 0.4, 1.0, 0.0), weather=bf.RAIL_W, variation=float(rng.random()))
        if lod:
            continue
        xr = s * (half - 0.25)
        yr = float(roof_y(xr)) + 0.06
        kc.tube(mb, np.array([[xr, yr + 0.18, Z0 + 0.2], [xr, yr + 0.18, Z1 - 0.2]]), 0.025, 5, mb.material(bf.M_IRON),
                cap_start=True, cap_end=True)
        for z in (Z0 + 0.25, 0.5 * (Z0 + Z1), Z1 - 0.25):
            kc.tube(mb, np.array([[xr, yr, z], [xr, yr + 0.19, z]]), 0.02, 4, mb.material(bf.M_IRON))


def _posts(mb: kc.MeshBuilder, rng, *, lod: bool) -> None:
    i_t = mb.material(bf.M_TIMBER)
    for x in (X0, X1):
        for z in (Z0, Z1):
            kc.rounded_block(mb, (x, WALL_H * 0.5, z), (0.07, WALL_H * 0.5 + 0.03, 0.07), i_t, radius=0.015,
                             seg=1 if lod else 2, weather=bf.RAIL_W, variation=float(rng.random()))
    if lod:
        return
    # The door's posts, lintel and sill, and the leaf standing open against the fore wall (hinged at the door's starboard post).
    d0, d1, dh = DOOR
    for x in (d0 - 0.04, d1 + 0.04):
        kc.rounded_block(mb, (x, dh * 0.5, Z0), (0.04, dh * 0.5, 0.07), i_t, radius=0.01, seg=1)
    kc.rounded_block(mb, (0.5 * (d0 + d1), dh + 0.04, Z0), (0.5 * (d1 - d0) + 0.08, 0.04, 0.07), i_t, radius=0.01, seg=1)
    kc.rounded_block(mb, (0.5 * (d0 + d1), 0.04, Z0), (0.5 * (d1 - d0), 0.04, 0.08), i_t, radius=0.01, seg=1)
    w = d1 - d0
    ang = math.radians(15.0)  # the leaf stands open, back against the fore wall
    hinge = np.array([d1 + 0.02, 0.0, Z0 - 0.06])
    c = hinge + np.array([math.cos(ang) * w * 0.5, dh * 0.5, -math.sin(ang) * w * 0.5])
    kc.rounded_block(mb, c, (w * 0.5, dh * 0.5 - 0.02, 0.025), mb.material(bf.M_BLUE), rot=kc.rot_y(ang), radius=0.006,
                     seg=1, weather=bf.RAIL_W, variation=0.6)


def _niche(mb: kc.MeshBuilder, rng, *, lod: bool) -> None:
    """The Order niche on the after wall, inside: lime pilasters and an arch round a recess, a marble plinth and
    basin. Plain: no symbol, no lamp of its own (the cabin lantern lights it)."""
    cx, hw, spring = NICHE
    z = Z1 - WALL_T * 0.5 - 0.01
    i_lime, i_m = mb.material(bf.M_LIME), mb.material(bf.M_MARBLE)
    for s in (-1.0, 1.0):
        kc.rounded_block(mb, (cx + s * (hw + 0.07), spring * 0.5, z - 0.08), (0.07, spring * 0.5, 0.08), i_lime,
                         radius=0.012, seg=1, variation=0.4)
    n = 4 if lod else 9
    ang = np.linspace(math.pi, 0.0, n)
    arch = np.stack([cx + np.cos(ang) * (hw + 0.07), spring + np.sin(ang) * (hw + 0.07), np.full(n, z - 0.08)], -1)
    kc.tube(mb, arch, 0.075, 4 if lod else 6, i_lime, weather=bf.RAIL_W, variation=0.4)
    # The recess's back (darker in the shade of the arch) and the plinth with the basin.
    kc.rounded_block(mb, (cx, spring * 0.75, z - 0.005), (hw, spring * 0.75, 0.01), mb.material(bf.M_DARK), radius=0.003,
                     seg=1)
    kc.rounded_block(mb, (cx, 0.42, z - 0.22), (0.3, 0.42, 0.2), i_m, radius=0.02, seg=1 if lod else 2, variation=0.5)
    bf.lathe(mb, (cx, 0.84, z - 0.22), [(0.12, 0.0), (0.2, 0.05), (0.27, 0.14), (0.28, 0.17), (0.24, 0.17), (0.0, 0.12)],
             8 if lod else 18, bf.M_MARBLE, weather=kc.FRESH)
    del rng


def _bench(mb: kc.MeshBuilder, rng) -> None:
    """A bench along the port wall inside."""
    i_t = mb.material(bf.M_TIMBER)
    x = X0 + WALL_T * 0.5 + 0.22
    kc.rounded_block(mb, (x, 0.44, 0.5 * (Z0 + Z1) + 0.2), (0.2, 0.03, 1.2), i_t, radius=0.01, seg=1, weather=bf.RAIL_W,
                     variation=float(rng.random()))
    for z in (Z0 + 0.9, Z1 - 0.5):
        kc.rounded_block(mb, (x, 0.21, z), (0.18, 0.21, 0.03), i_t, radius=0.01, seg=1)


def build_deckhouse(seed: int = 821) -> list[kc.MeshBuilder]:
    out = []
    w, sill, head = WINDOW
    d0, d1, dh = DOOR
    for lod in (False, True):
        rng = kc.rng_for("ferry_deckhouse", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("ferry_deckhouse" + (bf.LOD if lod else ""))
        _wall(mb, rng, "x", Z0, X0, X1, [(d0, d1, 0.0, dh)], lod=lod)
        _wall(mb, rng, "x", Z1, X0, X1, [], lod=lod)
        for side in (-1.0, 1.0):
            holes = [(z - w * 0.5, z + w * 0.5, sill, head) for z in WINDOW_Z]
            _wall(mb, rng, "z", side * X1, Z0, Z1, holes, lod=lod)
            for z in WINDOW_Z:
                _window(mb, side, z, lod=lod)
        _posts(mb, rng, lod=lod)
        _roof(mb, rng, noise, lod=lod)
        _niche(mb, rng, lod=lod)
        if not lod:
            _bench(mb, rng)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The awning
# ---------------------------------------------------------------------------------------------
def awning_y(x, z) -> np.ndarray:
    """The cloth's height: straight-ish from the ridge to the side spars, sagging between the posts."""
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    f = np.clip(np.abs(x) / AWNING_SIDE_X, 0.0, 1.0)
    y = AWNING_RIDGE_Y + (AWNING_SIDE_Y - AWNING_RIDGE_Y) * f
    y = y - 0.08 * np.sin(np.pi * f)  # the cloth bags between the ridge and the side spar
    t = (z - AWNING_Z[0]) / (AWNING_Z[1] - AWNING_Z[0])
    return y - 0.1 * np.sin(np.pi * np.clip(t, 0, 1)) * (0.3 + 0.7 * np.sin(np.pi * f))


def build_awning(seed: int = 831) -> list[kc.MeshBuilder]:
    out = []
    za, zb = AWNING_Z
    for lod in (False, True):
        rng = kc.rng_for("ferry_awning", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("ferry_awning" + (bf.LOD if lod else ""))
        i_t = mb.material(bf.M_TIMBER)
        # Posts: two at the ridge's ends, four at the side spars' ends.
        for x, top in ((0.0, AWNING_RIDGE_Y), (-AWNING_SIDE_X, AWNING_SIDE_Y), (AWNING_SIDE_X, AWNING_SIDE_Y)):
            for z in (za, zb):
                kc.tube(mb, np.array([[x, 0.0, z], [x, top + 0.08, z]]), 0.05, 4 if lod else 7, i_t, weather=bf.RAIL_W,
                        variation=float(rng.random()), cap_end=True)
        for x, top in ((0.0, AWNING_RIDGE_Y), (-AWNING_SIDE_X, AWNING_SIDE_Y), (AWNING_SIDE_X, AWNING_SIDE_Y)):
            kc.tube(mb, np.array([[x, top + 0.02, za - 0.15], [x, top + 0.02, zb + 0.15]]), 0.045, 4 if lod else 7, i_t,
                    weather=bf.RAIL_W, cap_start=True, cap_end=True)
        # The cloth, both slopes, and the valance.
        nx, nz = (3, 3) if lod else (9, 13)
        for s in (-1.0, 1.0):
            xs = s * np.linspace(0.0, AWNING_SIDE_X + 0.04, nx)
            zs = np.linspace(za - 0.1, zb + 0.1, nz)
            X, Z = np.meshgrid(xs, zs)
            g = np.stack([X, awning_y(X, Z) + 0.06, Z], -1)
            if not lod:
                g[..., 1] += (noise.fbm(g / 0.5, 2) - 0.5) * 0.02
            bf.cloth(mb, g, bf.M_AWNING, uv=np.stack([X, Z], -1) * 0.8, noise=None if lod else noise,
                     variation=float(rng.uniform(0.3, 0.7)))
            if lod:
                continue
            # The scalloped valance hanging from the side spar.
            zv = np.linspace(za - 0.1, zb + 0.1, 41)
            top = np.stack([np.full_like(zv, s * (AWNING_SIDE_X + 0.05)), np.full_like(zv, AWNING_SIDE_Y + 0.03), zv], -1)
            drop = 0.16 + 0.07 * np.abs(np.sin(np.pi * (zv - za) / 0.5))
            bot = top - np.stack([np.zeros_like(zv), drop, np.zeros_like(zv)], -1)
            g = np.stack([top, bot], axis=1)
            bf.cloth(mb, g, bf.M_AWNING, uv=np.stack([g[..., 2], g[..., 1]], -1), variation=0.55)
        if not lod:
            # Lashings from the side spars down to the cap rail (the awning is lashed against the wind).
            for s in (-1.0, 1.0):
                for z in (za + 0.6, zb - 0.6):
                    hb = float(bf.FERRY.half_beam_at(z))
                    bf.rope(mb, (s * AWNING_SIDE_X, AWNING_SIDE_Y, z), (s * (hb + 0.05), bf.RAIL_H + 0.04, z), 0.012,
                            bf.M_ROPE, sag=0.03, segs=3, sides=4)
        out.append(mb)
    return out


TARGETS = {"ferry_deckhouse": build_deckhouse, "ferry_awning": build_awning}
