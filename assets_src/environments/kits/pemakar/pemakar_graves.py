"""Pemakar graves, gates, lamps and offerings (pemakar.md §2.2). Pure numpy.

  grave_stele_a     an ash-stone: a dark stele on a two-step plinth, a shouldered top, a lamp niche cut
                    through near the top (its wick lit), a carved tide-line band, the names in a framed panel of
                    terrace script cut in and sooted, and an offering ledge
  grave_stele_b     a family stone: wider, three niches in a row, older, one top corner broken off
  grave_cairn       a poor grave: rounded stones under a flat capstone, one niche stone with a wick
  grave_curb        a low kerb round a family plot, pale ash gravel inside
  open_hand_gate    two carved stone forearms rising from a plinth, palms cupped towards each other over
                    the walkway, fingertips just short of touching (bible §5.2; an original design)
  lamp_pillar       a squared stone lamp pillar with an oil dish and a wick flame
  leaf_boat_lit     a folded palm-leaf tray (the Haluna leaf_boat hull), a pinch of rice, a lit wick
  shrine_box        a household lacquer shrine-box on a post: black, red panels, a thin gold-leaf band

Pieces stand on their origin (y = 0 the ground), facing +Z. Flames are part of the mesh (slot
`kit_wick_flame`); the scene adds the lights.
"""

from __future__ import annotations

import math

import numpy as np

import pemakar_common as pc
import shrine_interior as si  # Haluna's Shell Shrine kit, read-only: the leaf_boat hull and lathe
from pemakar_common import kc

TRI_BUDGET = {
    "grave_stele_a": (1600, 220),
    "grave_stele_b": (2000, 260),
    "grave_cairn": (1400, 200),
    "grave_curb": (900, 140),
    "open_hand_gate": (9000, 1300),
    "lamp_pillar": (900, 140),
    "leaf_boat_lit": (260, 40),
    "shrine_box": (900, 140),
}

NICHE_M = 0.14
LEAF_BOAT_M = 0.22


def _plinth(mb: kc.MeshBuilder, w: float, d: float, rng, noise, *, steps: int = 2, step_h: float = 0.1, lod: bool,
            weather=pc.DRESSED) -> float:
    """Stepped plinth; returns its top height."""
    y = 0.0
    for k in range(steps):
        ww, dd = w + 0.12 * (steps - k), d + 0.12 * (steps - k)
        kc.rounded_block(mb, (rng.uniform(-0.01, 0.01), y + step_h * 0.5, rng.uniform(-0.01, 0.01)),
                         (ww * 0.5, step_h * 0.5, dd * 0.5), mb.material(pc.M_DRESSED),
                         rot=kc.rot_y(rng.normal(0, 0.02)), radius=0.02, seg=1 if lod else 2,
                         noise=None if lod else noise, disp_m=0.012, weather=weather, variation=float(rng.random()))
        y += step_h
    return y


def _slab_with_niches(mb: kc.MeshBuilder, x_half: float, y0: float, y1: float, thick: float, niches: list[float],
                      niche_y: float, rng, noise, *, lod: bool, weather, broken: bool = False) -> None:
    """A stele body from y0 to y1 with square niches cut through at x in `niches`, centred at niche_y:
    built as the stones around each opening, so a lamp in the niche shows through both faces."""
    stone = pc.M_DRESSED
    seg = 1 if lod else 2
    n = NICHE_M * 0.5
    kw = dict(radius=0.02, seg=seg, noise=None if lod else noise, disp_m=0.008, disp_period_m=0.2, weather=weather)
    # Below and above the niche band.
    kc.rounded_block(mb, (0.0, (y0 + niche_y - n) * 0.5, 0.0), (x_half, (niche_y - n - y0) * 0.5, thick * 0.5),
                     mb.material(stone), variation=float(rng.random()), **kw)
    top_h = y1 - (niche_y + n)
    if broken:
        kc.rounded_block(mb, (-x_half * 0.18, niche_y + n + top_h * 0.5, 0.0), (x_half * 0.82, top_h * 0.5, thick * 0.5),
                         mb.material(stone), rot=kc.rot_z(0.04), variation=float(rng.random()), **kw)
    else:
        kc.rounded_block(mb, (0.0, niche_y + n + top_h * 0.5, 0.0), (x_half, top_h * 0.5, thick * 0.5),
                         mb.material(stone), variation=float(rng.random()), **kw)
        # The shouldered top: a rounded cap.
        kc.rounded_block(mb, (0.0, y1 + 0.02, 0.0), (x_half * 0.97, 0.075, thick * 0.5 * 0.98), mb.material(stone),
                         radius=0.074, seg=seg + 2, noise=None if lod else noise, disp_m=0.006, weather=weather,
                         variation=float(rng.random()))
    # Posts between and beside the niches.
    edges = [-x_half] + [e for x in niches for e in (x - n, x + n)] + [x_half]
    for a, b in zip(edges[0::2], edges[1::2]):
        if b - a > 0.01:
            kc.rounded_block(mb, ((a + b) * 0.5, niche_y, 0.0), ((b - a) * 0.5 + 0.004, n + 0.004, thick * 0.5),
                             mb.material(stone), variation=float(rng.random()), **kw)
    for x in niches:
        pc.flame(mb, (x, niche_y - n + 0.012, 0.0), 0.08, 0.016)
        # A soot shadow on the niche's lintel underside.
        kc.rounded_block(mb, (x, niche_y + n - 0.004, 0.0), (n * 0.9, 0.004, thick * 0.45), mb.material(pc.M_SOOT),
                         seg=1, radius=0.002)



def _inscription(mb: kc.MeshBuilder, x_half: float, y0: float, y1: float, z: float, rng, weather) -> None:
    """The dead's names on the front face (M3-ENV-705: P03 read the stones as plain blocks): a framed panel, and in it
    rows of Pemakar terrace script, short stepped bars cut in and darkened with lamp soot."""
    stone, soot = mb.material(pc.M_DRESSED), mb.material(pc.M_SOOT)
    px = x_half - 0.06
    if y1 - y0 < 0.1 or px < 0.08:
        return
    for c, half in (((0.0, y1, z), (px + 0.012, 0.01, 0.006)), ((0.0, y0, z), (px + 0.012, 0.01, 0.006)),
                    ((-px, (y0 + y1) * 0.5, z), (0.01, (y1 - y0) * 0.5, 0.006)),
                    ((px, (y0 + y1) * 0.5, z), (0.01, (y1 - y0) * 0.5, 0.006))):
        kc.rounded_block(mb, c, half, stone, radius=0.004, seg=1, weather=weather)
    rows = max(1, int((y1 - y0 - 0.04) / 0.07))
    for r in range(rows):
        yy = y1 - 0.045 - r * 0.07
        x = -px + 0.035
        while x < px - 0.06:
            bw = float(rng.uniform(0.025, 0.07))
            step = 0.012 if rng.random() < 0.3 else 0.0  # the script's stepped bars
            kc.rounded_block(mb, (x + bw * 0.5, yy + step, z + 0.001), (bw * 0.5, 0.007, 0.002), soot, radius=0.002,
                             seg=1)
            x += bw + float(rng.uniform(0.012, 0.03))

def stele(name: str, seed: int, *, lod: bool = False, kind: str = "a") -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    if kind == "a":
        w, h, t = 0.54, 0.9, 0.15
        weather, niches, broken = pc.DRESSED, [0.0], False
    else:
        w, h, t = 0.9, 0.75, 0.2
        weather, niches, broken = pc.OLD, [-0.27, 0.0, 0.27], True
    if lod:
        # LOD1: plinth and body as two blocks, the niche lamps kept (they are what reads at range).
        kc.rounded_block(mb, (0.0, 0.1, 0.0), ((w + 0.22) * 0.5, 0.1, (t + 0.37) * 0.5), mb.material(pc.M_DRESSED),
                         seg=1, radius=0.02)
        kc.rounded_block(mb, (0.0, 0.2 + h * 0.5, 0.0), (w * 0.5, h * 0.5, t * 0.5), mb.material(pc.M_DRESSED), seg=1,
                         radius=0.03)
        for x in niches:
            pc.flame(mb, (x, 0.2 + h - 0.2 - NICHE_M * 0.5, t * 0.5 + 0.01), 0.06, 0.012, sides=4)
        return mb
    y = _plinth(mb, w + 0.1, t + 0.25, rng, noise, lod=lod, weather=weather)
    _slab_with_niches(mb, w * 0.5, y, y + h, t, niches, y + h - 0.2, rng, noise, lod=lod, weather=weather, broken=broken)
    if not lod:
        _inscription(mb, w * 0.5, y + h * 0.35 + 0.05, y + h - 0.2 - NICHE_M * 0.5 - 0.05, t * 0.5, rng, weather)
        # The carved tide-line band (a shallow proud ring) and the offering ledge in front.
        kc.rounded_block(mb, (0.0, y + h * 0.35, 0.0), (w * 0.5 + 0.012, 0.022, t * 0.5 + 0.012),
                         mb.material(pc.M_DRESSED), radius=0.01, seg=2, weather=weather)
        kc.rounded_block(mb, (0.0, y - 0.03, t * 0.5 + 0.13), (w * 0.42, 0.03, 0.1), mb.material(pc.M_DRESSED),
                         radius=0.012, seg=2, noise=noise, disp_m=0.005, weather=weather)
        # Lichen on the sun side and moss at the foot (old stones more).
        pos = np.asarray(mb.pos, float)
        col = np.asarray(mb.col, float)
        col[:, 0] = np.clip(col[:, 0] + weather.moss * kc.smoothstep(0.35, 0.0, pos[:, 1]) * noise.fbm(pos / 0.15, 2), 0, 1)
        mb.col = col.tolist()
        pc.ash_pass(mb, 0, noise, 0.9, period_m=0.25)
    return mb


def cairn(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    stones = 4 if lod else 11
    for k in range(stones):
        layer = 0 if k < stones * 0.55 else 1
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0.12, 0.3) * (1.0 - 0.45 * layer)
        s = rng.uniform(0.11, 0.17) * (1.0 - 0.2 * layer)
        c = (math.cos(a) * r, s * 0.8 + layer * 0.2, math.sin(a) * r)
        kc.rounded_block(mb, c, (s, s * 0.75, s * 0.9), mb.material(pc.M_STONE), rot=kc.rot_y(a), radius=s * 0.6,
                         seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.03, disp_period_m=0.2,
                         weather=pc.OLD, variation=float(rng.random()))
    kc.rounded_block(mb, (0.0, 0.47, 0.0), (0.24, 0.04, 0.2), mb.material(pc.M_STONE), rot=kc.rot_y(0.3),
                     radius=0.03, seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.015, weather=pc.OLD)
    # The niche stone on the cap, its wick lit.
    for sx in (-1.0, 1.0):
        kc.rounded_block(mb, (sx * 0.085, 0.58, 0.0), (0.025, 0.07, 0.07), mb.material(pc.M_DRESSED), radius=0.01,
                         seg=1, weather=pc.OLD)
    kc.rounded_block(mb, (0.0, 0.665, 0.0), (0.11, 0.018, 0.075), mb.material(pc.M_DRESSED), radius=0.01, seg=1,
                     weather=pc.OLD)
    pc.flame(mb, (0.0, 0.512, 0.0), 0.06, 0.012)
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.9, period_m=0.2)
    return mb


def curb(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    w, d, h, k = 2.0, 1.2, 0.18, 0.12
    for c, half in (((0.0, h * 0.5, d * 0.5), (w * 0.5, h * 0.5, k * 0.5)), ((0.0, h * 0.5, -d * 0.5), (w * 0.5, h * 0.5, k * 0.5)),
                    ((w * 0.5, h * 0.5, 0.0), (k * 0.5, h * 0.5, d * 0.5 - k * 0.5)),
                    ((-w * 0.5, h * 0.5, 0.0), (k * 0.5, h * 0.5, d * 0.5 - k * 0.5))):
        kc.rounded_block(mb, c, half, mb.material(pc.M_DRESSED), rot=kc.rot_y(rng.normal(0, 0.01)), radius=0.02,
                         seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.01, weather=pc.OLD,
                         variation=float(rng.random()))
    # Ash gravel inside: a low displaced mound.
    nx, nz = (2, 2) if lod else (9, 6)
    xs = np.linspace(-w * 0.5 + k, w * 0.5 - k, nx)
    zs = np.linspace(d * 0.5 - k, -d * 0.5 + k, nz)
    X, Z = np.meshgrid(xs, zs)
    Y = 0.1 + 0.03 * np.cos(X / w * math.pi) * np.cos(Z / d * math.pi)
    if not lod:
        Y = Y + (noise.fbm(np.stack([X, Y, Z], -1) / 0.08, 2) - 0.5) * 0.02
    g = np.stack([X, Y, Z], axis=-1)
    kc.quad_strip(mb, g, mb.material(pc.M_SOIL), uv=np.stack([X, Z], -1), col=(0.0, 0.9, 0.0, 0.2), uv2=(0.9, 0.5),
                  flip=False)
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.95, period_m=0.2, floor=0.2)
    return mb


# ---------------------------------------------------------------------------------------------
# The open-hand gate
# ---------------------------------------------------------------------------------------------
def _limb(mb: kc.MeshBuilder, spine: np.ndarray, radii: np.ndarray, sides: int, mat: str, noise, *, flat=None,
          up_hint=(0.0, 0.0, 1.0)) -> None:
    """A tube along `spine` whose section can be flattened (flat[i] scales one axis, toward up_hint)."""
    start_v, start_t = mb.vertex_count, mb.triangle_count
    kc.tube(mb, spine, radii, sides, mb.material(mat), weather=pc.DRESSED, noise=noise, disp_m=0.01,
            disp_period_m=0.15, cap_end=True, first_normal=np.asarray(up_hint, float))
    if flat is not None:
        p = np.asarray(mb.pos[start_v:], float)
        rings = len(spine)
        per = sides + 1
        hint = kc.normalize(np.asarray(up_hint, float))
        for i in range(rings):
            sl = slice(i * per, (i + 1) * per)
            c = spine[i]
            d = p[sl] - c
            along = d @ hint
            p[sl] = p[sl] - np.outer(along * (1.0 - flat[i]), hint)
        mb.pos[start_v:] = p.tolist()
        kc.recompute_normals(mb, start_v, start_t)


def _arm(mb: kc.MeshBuilder, sx: float, rng, noise, *, lod: bool) -> None:
    """One forearm rising at x = sx * 1.2, its hand opening upward and inward over the walkway (-sx)."""
    sides = 8 if lod else 16
    x0 = sx * 1.25
    inward = -sx
    t = np.linspace(0.0, 1.0, 5 if lod else 14)
    base_y = 0.42
    wrist_y = 2.35
    spine = np.stack([x0 + inward * 0.12 * t ** 2, base_y + (wrist_y - base_y) * t, 0.03 * np.sin(t * math.pi)], -1)
    radii = 0.31 - 0.08 * t + 0.03 * np.exp(-((t - 0.12) / 0.07) ** 2)
    if not lod:
        # Two carved bracelet bands near the wrist.
        radii = radii + 0.025 * (np.exp(-((t - 0.84) / 0.025) ** 2) + np.exp(-((t - 0.9) / 0.025) ** 2))
    _limb(mb, spine, radii, sides, pc.M_DRESSED, None if lod else noise, flat=0.82 + 0.18 * (1 - t))
    # The palm: a thick, slightly cupped plate tilted inward 40 deg, its face toward the other hand.
    wrist = spine[-1]
    tilt = math.radians(40.0) * inward
    palm_c = wrist + np.array([inward * 0.18, 0.36, 0.0])
    kc.rounded_block(mb, palm_c, (0.13, 0.38, 0.34), mb.material(pc.M_DRESSED), rot=kc.rot_z(-tilt),
                     radius=0.1, seg=2 if lod else 4, noise=None if lod else noise, disp_m=0.01, weather=pc.DRESSED)
    if lod:
        # The fingers as one curled plate.
        tip = palm_c + np.array([inward * 0.7, 0.5, 0.0])
        kc.tube(mb, np.array([palm_c + [0, 0.3, 0], tip]), np.array([0.2, 0.1]), 6, mb.material(pc.M_DRESSED),
                cap_end=True)
        return
    # Four fingers curling from the palm's top edge over toward the walkway, and the thumb forward.
    up = kc.normalize(np.array([math.sin(tilt), math.cos(tilt), 0.0]))
    side = kc.normalize(np.array([inward, 0.0, 0.0]) - up * up[0] * inward)
    top = palm_c + up * 0.34
    n = 9
    for zoff, ln, r in ((-0.24, 0.62, 0.075), (-0.08, 0.72, 0.08), (0.08, 0.7, 0.08), (0.23, 0.58, 0.07)):
        bend = np.linspace(0.0, math.radians(100.0), n)  # the curl toward the walkway
        pts = [top + np.array([0.0, 0.0, zoff])]
        for b in bend[1:]:
            pts.append(pts[-1] + (math.cos(b) * up + math.sin(b) * side) * (ln / (n - 1)))
        pts = np.asarray(pts)
        rr = r * (1.0 - 0.35 * np.linspace(0.0, 1.0, n))
        kc.tube(mb, pts, rr, 8, mb.material(pc.M_DRESSED), weather=pc.DRESSED, noise=noise, disp_m=0.004,
                disp_period_m=0.1, cap_end=True, cap_start=True)
    th = np.linspace(0.0, 1.0, 7)
    thumb = palm_c + np.array([inward * 0.05, -0.1, 0.32]) + np.stack(
        [inward * 0.32 * th, 0.3 * th, 0.18 * np.sin(th * 2.0)], -1)
    kc.tube(mb, thumb, 0.085 * (1.0 - 0.3 * th), 8, mb.material(pc.M_DRESSED), noise=noise, disp_m=0.004,
            cap_end=True, cap_start=True)


def gate(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    for sx in (-1.0, 1.0):
        # A two-step plinth under each forearm, carved as one stone with the ground course.
        kc.rounded_block(mb, (sx * 1.25, 0.12, 0.0), (0.55, 0.12, 0.6), mb.material(pc.M_STONE), radius=0.04,
                         seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.02, weather=pc.TERRACE,
                         variation=float(rng.random()))
        kc.rounded_block(mb, (sx * 1.25, 0.33, 0.0), (0.42, 0.1, 0.46), mb.material(pc.M_DRESSED), radius=0.03,
                         seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.01, weather=pc.DRESSED,
                         variation=float(rng.random()))
        _arm(mb, sx, rng, noise, lod=lod)
    # The threshold stone between them, worn hollow in the middle.
    kc.rounded_block(mb, (0.0, 0.04, 0.0), (0.7, 0.05, 0.45), mb.material(pc.M_DRESSED), radius=0.03,
                     seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.01,
                     weather=kc.Weathering(moss=0.1, salt=0, wet=0, erosion=0.9))
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.9, period_m=0.3, vertical=0.1)
    return mb


# ---------------------------------------------------------------------------------------------
# Lamps and offerings
# ---------------------------------------------------------------------------------------------
def lamp_pillar(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    seg = 1 if lod else 2
    kc.rounded_block(mb, (0.0, 0.06, 0.0), (0.2, 0.06, 0.2), mb.material(pc.M_DRESSED), radius=0.02, seg=seg,
                     noise=None if lod else noise, disp_m=0.008, weather=pc.DRESSED)
    kc.rounded_block(mb, (0.0, 0.58, 0.0), (0.11, 0.48, 0.11), mb.material(pc.M_DRESSED), radius=0.02, seg=seg,
                     noise=None if lod else noise, disp_m=0.006, weather=pc.DRESSED, variation=float(rng.random()))
    kc.rounded_block(mb, (0.0, 1.09, 0.0), (0.17, 0.04, 0.17), mb.material(pc.M_DRESSED), radius=0.015, seg=seg,
                     weather=pc.DRESSED)
    # The oil dish: a shallow bowl, sooted underneath, and the wick.
    prof = [(0.05, 1.13), (0.13, 1.15), (0.155, 1.19), (0.14, 1.2), (0.11, 1.17)]
    if not lod:
        si.lathe(mb, prof, 12, mb.material(pc.M_SOOT), center=(0.0, 0.0, 0.0), weather=pc.DRESSED)
    pc.flame(mb, (0.0, 1.17, 0.0), 0.1, 0.02, sides=4 if lod else 6)
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.8, period_m=0.2)
    return mb


def leaf_boat_lit(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    """A leaf-boat for MultiMesh instancing, centred on its origin (the water line at y = 0)."""
    rng = kc.rng_for(name, seed)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    L = LEAF_BOAT_M
    if lod:
        leaf = mb.material(pc.M_LEAF)
        p = np.array([[0.0, 0.012, -L * 0.5], [L * 0.17, 0.012, 0.0], [0.0, 0.012, L * 0.5], [-L * 0.17, 0.012, 0.0]])
        base = mb.add_vertices(p, kc.UP, np.zeros((4, 2)), (1.0, 0.5), (0, 0, 0, 0))
        mb.add_tri(base, base + 2, base + 1, leaf)
        mb.add_tri(base, base + 3, base + 2, leaf)
        pc.flame(mb, (0.0, 0.03, 0.0), 0.05, 0.012, sides=3)
        return pc.remap_slots(mb)
    si.leaf_boat(mb, (0.0, 0.0, 0.0), 0.0, L, rng, flower=False)
    # The pinch of rice (a low mound) and the wick standing in it.
    kc.rounded_block(mb, (0.0, 0.022, 0.012), (0.022, 0.01, 0.02), mb.material(pc.M_RICE), radius=0.009, seg=2)
    kc.tube(mb, np.array([[0.0, 0.025, 0.0], [0.0, 0.04, 0.0]]), 0.0025, 4, mb.material(pc.M_SOOT), cap_end=True)
    pc.flame(mb, (0.0, 0.038, 0.0), 0.05, 0.011)
    return pc.remap_slots(mb)


def shrine_box(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    seg = 1 if lod else 2
    kc.rounded_block(mb, (0.0, 0.42, 0.0), (0.05, 0.42, 0.05), mb.material(pc.M_TIMBER), radius=0.01, seg=1)
    kc.rounded_block(mb, (0.0, 0.86, 0.0), (0.16, 0.025, 0.14), mb.material(pc.M_TIMBER), radius=0.01, seg=1)
    # The box: black lacquer, red panels on three faces, a gold band under the lid.
    kc.rounded_block(mb, (0.0, 0.99, 0.0), (0.13, 0.11, 0.11), mb.material(pc.M_LACQUER_BLACK), radius=0.012, seg=seg)
    if not lod:
        for rot in (0.0, math.pi * 0.5, -math.pi * 0.5):
            R = kc.rot_y(rot)
            kc.rounded_block(mb, R @ np.array([0.0, 0.98, 0.112]), (0.085, 0.07, 0.004) if rot == 0.0 else
                             (0.07, 0.07, 0.004), mb.material(pc.M_LACQUER_RED), rot=R, radius=0.003, seg=1)
        kc.rounded_block(mb, (0.0, 1.085, 0.0), (0.134, 0.008, 0.114), mb.material(pc.M_GOLD), radius=0.003, seg=1)
        # A small open front with an offering lamp.
        pc.flame(mb, (0.0, 1.0, 0.13), 0.04, 0.01)
    # The lid: a little hipped cap.
    kc.rounded_block(mb, (0.0, 1.13, 0.0), (0.16, 0.03, 0.14), mb.material(pc.M_LACQUER_BLACK), radius=0.02, seg=seg)
    kc.rounded_block(mb, (0.0, 1.175, 0.0), (0.09, 0.025, 0.07), mb.material(pc.M_LACQUER_RED), radius=0.02, seg=seg)
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.5, period_m=0.1)
    return mb


TARGETS = {
    "grave_stele_a": lambda: [stele("grave_stele_a", 601), stele("grave_stele_a", 601, lod=True)],
    "grave_stele_b": lambda: [stele("grave_stele_b", 602, kind="b"), stele("grave_stele_b", 602, lod=True, kind="b")],
    "grave_cairn": lambda: [cairn("grave_cairn", 603), cairn("grave_cairn", 603, lod=True)],
    "grave_curb": lambda: [curb("grave_curb", 604), curb("grave_curb", 604, lod=True)],
    "open_hand_gate": lambda: [gate("open_hand_gate", 605), gate("open_hand_gate", 605, lod=True)],
    "lamp_pillar": lambda: [lamp_pillar("lamp_pillar", 606), lamp_pillar("lamp_pillar", 606, lod=True)],
    "leaf_boat_lit": lambda: [leaf_boat_lit("leaf_boat_lit", 607), leaf_boat_lit("leaf_boat_lit", 607, lod=True)],
    "shrine_box": lambda: [shrine_box("shrine_box", 608), shrine_box("shrine_box", 608, lod=True)],
}
