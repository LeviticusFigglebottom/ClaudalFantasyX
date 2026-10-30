"""The Iskarra ruins for the Prologue (prologue/iskarra_dusk; reused in Ch19). M3-ENV-710. Pure numpy.

"Gold dusk light over drowned white towers ... a broken plaza that juts above the water" (act_outline.md,
Prologue). The Lit Age capital's towers are glazed white ceramic, fluted, banded with galleries and rows of dark
window slits, their feet in the sea with a weed and barnacle band at the waterline; some keep their domed caps and
finials, some end in a broken, jagged rim, one has lost its crown into the water. Replaces the Prologue's primitive
city one piece for one primitive (iskarra_city.tscn), so its shots keep their composition.

  iskarra_tower_spire    a fluted tower, galleries every 9 m, a domed cap and finial (60 m with the cap, r 6 at the foot)
  iskarra_tower_stepped  three tiers narrowing upward, each with its gallery, a low dome (46 m, r 5.5)
  iskarra_tower_broken   a fluted shaft ending in a jagged broken rim, open to the sky (40 m, r 5)
  iskarra_tower_small    a short domed tower, two galleries (21 m with the cap, r 3.5)
  iskarra_tower_small_broken  a short shaft broken off at 14 m (r 3)
  iskarra_crown_fallen   a tower's toppled crown, half sunk: a dome ring and its finial, on its side (r 3.4)
  iskarra_plaza          the broken plaza 34 x 18 m: ceramic-inlaid paving, a broken back corner fallen away, steps
                         down to the water at the front (+Z), balustrade stumps along the sides
  iskarra_plaza_rise     the raised dais on the plaza (10 x 6 m, 0.8 m): three steps on its +Z face
  iskarra_arch           a standing gate: two fluted pillars and a carved lintel (9 m wide, 10.9 m)
  iskarra_arch_fallen    the same gate fallen: one pillar standing, a stump, the lintel broken across the ground
  iskarra_lamp_column    a dead Lit Age lamp column (5.5 m): a fluted ceramic shaft and a cold glass head in bronze
  iskarra_drowned_block  (M3-ENV-724) a drowned building's top storeys out of the sea (14 x 10 m, 4.5 m over the
                         water): tiled walls with arched windows, a blue-glazed band under the cornice, a parapet,
                         its roof terrace fallen in at one end
  iskarra_drowned_dome   (M3-ENV-724) a smaller drowned block (9 x 9 m, 3.6 m over the water) carrying a blue dome
  iskarra_far_towers     (M3-ENV-724) the drowned city to the horizon: low-poly towers (domed, stepped, broken) with
                         galleries and a glazed band, out of the sea at 180-520 m behind the plaza (the -Z half and
                         the flanks), so the skyline is a city, not an empty sea
  iskarra_arcade_sunk    (M3-ENV-724) five bays of a drowned arcade along X (23 m): square piers, round arches,
                         the entablature with its glazed band; the fourth bay's arch and lintel fallen

M3-ENV-724 (the fast-track pass for the Prologue's first frames): the shafts are clad in Iskarra's glazed tile
(kit_iskarra_cladding, mesh UV in metres), every storey has its row of arched windows (dark openings in cast
frames, a sill), the galleries are real ledges (a slab, its edge and soffit, a parapet rail on posts) with a band of
reef-blue glazed tile under each (kit_iskarra_glaze, the city's one colour); the stepped towers' domes are glazed.
The plaza's inlaid channels are the blue glaze, and a Lit Age sunburst is inlaid in its middle.

Origins: towers at their foot centre on the sea bed datum (the sea is at y 3 above it: their waterline band sits
there), the plaza pieces at their top's centre (y 0 = the paving), the drowned pieces at the sea level (y 0) over
their centre, the rest at their foot. Front +Z.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_CERAMIC = "kit_iskarra_ceramic"
M_CLAD = "kit_iskarra_cladding"
M_GLAZE = "kit_iskarra_glaze"
M_CORE_EXPOSED = "kit_coral_concrete"
M_GRASS = "kit_keth_grass"  # pale salt-grass, two-sided (the Keth seep's; read-only)  # the cast core where the cladding has spalled (M3-ENV-724)
M_PAVING = "kit_iskarra_paving"
M_BRONZE = "kit_iskarra_bronze"
M_GILT = "kit_gold_leaf"  # the white towers' domes and finials (the human's playtest: "greyscale"; M3-ENV-752)
M_GLASS = "kit_salt_glass"
M_DARK = "kit_interior_dark"

WATERLINE_M = 3.0  # the tower's foot is this far under the sea (the Prologue's water is at y 0, feet at -3)
FLUTES = 18

CHANNEL_HALF_W = 0.11  # the paving's inlaid ceramic channel strips

TRI_BUDGET = {
    "iskarra_tower": (36000, 2400),
    "iskarra_drowned": (9000, 400),
    "iskarra_arcade_sunk": (5000, 300),
    "iskarra_far_towers": (14000, 1300),
    "iskarra_vigil_dressing": (9000, 500),
    "iskarra_crown_fallen": (4000, 300),
    "iskarra_plaza": (14000, 600),
    "iskarra_plaza_rise": (3000, 120),
    "iskarra_arch": (4000, 200),
    "iskarra_lamp_column": (1500, 100),
}
BUDGET_KEY = {name: "iskarra_tower" for name in ("iskarra_tower_spire", "iskarra_tower_stepped", "iskarra_tower_broken",
                                                 "iskarra_tower_small", "iskarra_tower_small_broken")}
BUDGET_KEY["iskarra_arch_fallen"] = "iskarra_arch"
BUDGET_KEY["iskarra_drowned_block"] = "iskarra_drowned"
BUDGET_KEY["iskarra_drowned_dome"] = "iskarra_drowned"
WINDOW_PITCH_M = 2.6  # arc length between a storey's windows
STOREY_ROWS = (3.4, 6.6)  # window-row centres below each gallery

# The Prologue dressing pass (the Lead, 10-30): the shafts' decline read from P01's 70-100 m. The tide band stands
# 2.4 m up the foot (it was 1.2 m, lost under the swell), a fainter old high-water ring 5-7 m up, and the rain streaks
# under each ledge run darker and longer (9 m, was 5 m at 0.55).
TIDE_BAND_M = 2.4
HIGH_WATER_M = (5.0, 7.0)
HIGH_WATER_WET = 0.5
STAIN_WET = 0.75
STAIN_RUN_M = 9.0
STAIN_FREQ = 10.0  # the streaks' breakup round the shaft (was 4: broad patches, not runs)
# The shaft's vertex rows carry the streaks and bands: 1 m at LOD0 (was 2), and LOD1 (P01's towers stand 60-110 m off,
# past the 70 m switch) 24 sides at 3 m (was 12 at 8 m: no streak survived), the galleries' LOD1 rings matching.
SHAFT_ROW_M = 1.0
LOD1_SIDES = 24
LOD1_ROW_M = 3.0
WORN = kc.Weathering(moss=0.0, salt=0.6, wet=0.0, erosion=0.6)  # dry above the tide: the shaft paints its own band


def _shaft(mb: kc.MeshBuilder, y0: float, y1: float, r0: float, r1: float, rng, noise, *, lod: bool,
           top_jagged: float = 0.0, waterline: float | None = None, stains=()) -> None:
    """A fluted ceramic shaft from y0 (radius r0) to y1 (r1), its vertex colours carrying the waterline band
    (salt and wet below `waterline`+1 m) and wear; `top_jagged` > 0 breaks the top rim into a ragged edge.
    `stains` (gallery heights, M3-ENV-724): a thousand years of rain run off each ledge in dark streaks, wet in the
    vertex colour, fading over the 5 m below it, broken round the shaft by noise."""
    marked = waterline is not None or bool(stains)  # a tower's shaft: its rows carry the bands and streaks
    na = (FLUTES * 4 if not lod else (LOD1_SIDES if marked else 12)) + 1
    ny = max(2, int((y1 - y0) / ((SHAFT_ROW_M if marked else 2.0) if not lod else (LOD1_ROW_M if marked else 8.0))) + 1)
    a = np.linspace(0.0, 2 * math.pi, na)
    t = np.linspace(0.0, 1.0, ny)
    A, T = np.meshgrid(a, t)
    Y = y0 + T * (y1 - y0)
    R = r0 + (r1 - r0) * T
    if not lod:
        R = R * (1.0 + 0.03 * np.cos(A * FLUTES))  # flutes
    if top_jagged > 0.0:
        jag = (noise.fbm(np.stack([np.cos(a) * 3.0, np.zeros_like(a), np.sin(a) * 3.0], -1), 3) - 0.5) * 2.0
        Y[-1] = y1 - top_jagged * (0.5 + 0.5 * np.abs(jag)) - top_jagged * 0.6 * (np.sin(a * 2.0 + 1.0) > 0.4)
        if ny > 2:
            Y[-2] = np.minimum(Y[-2], Y[-1] - 0.2)
    P = np.stack([np.cos(A) * R, Y, np.sin(A) * R], axis=-1)
    if waterline is not None:
        wet = 1.0 - kc.smoothstep(waterline, waterline + TIDE_BAND_M, Y)
        salt = np.clip(1.0 - kc.smoothstep(waterline + 0.5, waterline + 4.0, Y), 0.0, 1.0) * 0.8
        # The Prologue dressing pass (the Lead, 10-30: beautiful and doomed at dusk): an older, higher sea's mark, a
        # faint dark ring round every drowned shaft, broken by noise: the water has stood higher, and will again.
        ring = (kc.smoothstep(waterline + HIGH_WATER_M[0], waterline + HIGH_WATER_M[0] + 0.4, Y)
                * (1.0 - kc.smoothstep(waterline + HIGH_WATER_M[1] - 0.6, waterline + HIGH_WATER_M[1], Y)))
        ring_breakup = noise.fbm(np.stack([np.cos(A) * 2.0, Y * 0.3, np.sin(A) * 2.0], -1), 2)
        wet = np.maximum(wet, HIGH_WATER_WET * ring * np.clip(ring_breakup * 1.6 - 0.2, 0.0, 1.0))
    else:
        wet = np.zeros_like(Y)
        salt = np.zeros_like(Y)
    breakup = noise.fbm(P / 4.0, 2) if not lod else np.full(Y.shape, 0.5)
    for g in stains:
        runs = np.clip((noise.fbm(np.stack([np.cos(A) * STAIN_FREQ, np.full_like(A, g * 0.1), np.sin(A) * STAIN_FREQ],
                                           -1), 2) - 0.45) * 4.0, 0.0, 1.0)
        below = (Y < g - 0.3) * np.clip(1.0 - (g - 0.3 - Y) / STAIN_RUN_M, 0.0, 1.0)
        wet = np.maximum(wet, STAIN_WET * runs * below)
    col = np.stack([np.zeros_like(Y), np.clip(salt + 0.15 * breakup, 0, 1), wet, 0.35 + 0.5 * breakup], axis=-1)
    uv = np.stack([A * (r0 + r1) * 0.5, Y], axis=-1)  # metres: the cladding's tile runs level round the shaft
    uv2 = np.stack([np.full(Y.shape, 0.9), np.full(Y.shape, float(rng.random()))], axis=-1)
    kc.quad_strip(mb, P, mb.material(M_CLAD), uv=uv, col=col, uv2=uv2, flip=True)  # faces out (M3-ENV-724 fix)
    if top_jagged > 0.0:
        # The broken wall's inside, so the open top reads as a hollow shell from above and through the breaks.
        inner = P[-2:].copy()
        inner[..., 0] *= 0.9
        inner[..., 2] *= 0.9
        kc.quad_strip(mb, np.stack([P[-1], inner[-1]]), mb.material(M_CLAD), uv=uv[-2:], col=col[-2:],
                      uv2=uv2[-2:], flip=True)
        down = inner[-1:].copy()
        down[..., 1] -= min(6.0, (y1 - y0) * 0.6)
        kc.quad_strip(mb, np.concatenate([inner[-1:], down]), mb.material(M_DARK), uv=uv[-2:], col=col[-2:],
                      uv2=uv2[-2:], flip=True)


def _strip(mb: kc.MeshBuilder, grid: np.ndarray, mat: int, want, **kw) -> None:
    """quad_strip with its faces turned toward `want` (a vector, or a callable of the first quad's centre)."""
    n = np.cross(grid[0, 1] - grid[0, 0], grid[1, 0] - grid[0, 0])
    c = (grid[0, 0] + grid[1, 1]) * 0.5
    w = want(c) if callable(want) else np.asarray(want, float)
    kc.quad_strip(mb, grid, mat, flip=bool(np.dot(n, w) < 0.0), **kw)


def _ring(rad: float, y: float, a: np.ndarray) -> np.ndarray:
    return np.stack([np.cos(a) * rad, np.full_like(a, y), np.sin(a) * rad], axis=-1)


def _gallery(mb: kc.MeshBuilder, y: float, r: float, rng, lod: bool, *, sides1: int = 12) -> None:
    """A gallery: a ledge projecting 0.9 m (its top, edge and soffit), a parapet rail on posts, and under it a band
    of reef-blue glazed tile."""
    a = np.linspace(0.0, 2 * math.pi, (48 if not lod else sides1) + 1)  # a tower's LOD1: its shaft's sides
    ro = r + 0.9
    cer, glaze = mb.material(M_CERAMIC), mb.material(M_GLAZE)
    out = lambda c: np.array([c[0], 0.0, c[2]])  # noqa: E731
    kw = dict(col=np.array([0.0, 0.3, 0.0, 0.5]), uv2=np.array([0.9, float(rng.random())]))
    for grid, want in ((np.stack([_ring(r, y, a), _ring(ro, y, a)]), (0.0, 1.0, 0.0)),
                       (np.stack([_ring(ro, y, a), _ring(ro, y - 0.35, a)]), out),
                       (np.stack([_ring(ro, y - 0.35, a), _ring(r, y - 0.35, a)]), (0.0, -1.0, 0.0))):
        _strip(mb, grid, cer, want, uv=grid[..., [0, 2]] + grid[..., [1, 1]], smooth=False, **kw)
    band = np.stack([_ring(r * 1.03 + 0.01, y - 0.45, a), _ring(r * 1.03 + 0.01, y - 1.55, a)])
    _strip(mb, band, glaze, out, uv=np.stack([np.broadcast_to(a * r, band.shape[:2]), band[..., 1]], -1), **kw)
    if lod:
        return
    kc.tube(mb, _ring(ro - 0.12, y + 0.95, a), 0.06, 4, cer)
    n = max(12, int(2 * math.pi * ro / 1.6))
    for k in range(n):
        th = 2 * math.pi * k / n
        p = np.array([math.cos(th) * (ro - 0.12), 0.0, math.sin(th) * (ro - 0.12)])
        kc.tube(mb, np.array([p + [0.0, y, 0.0], p + [0.0, y + 0.92, 0.0]]), 0.05, 4, cer)


def _window(mb: kc.MeshBuilder, th: float, y: float, r: float, *, w: float = 0.9, h: float = 2.0) -> None:
    """An arched window on a wall whose outward normal is (cos th, 0, sin th) at radius r: the dark opening, a cast
    frame (jambs and arch) standing proud of the wall, and a sill. y is the window's centre."""
    dark, cer = mb.material(M_DARK), mb.material(M_CERAMIC)
    n = np.array([math.cos(th), 0.0, math.sin(th)])
    t = np.array([-math.sin(th), 0.0, math.cos(th)])
    spring = y + h * 0.5 - w * 0.5
    base = n * r
    kc.rounded_block(mb, base + n * 0.02 + [0.0, (y - h * 0.5 + spring) * 0.5, 0.0],
                     (0.04, (spring - (y - h * 0.5)) * 0.5, w * 0.5), dark, rot=kc.rot_y(-th), radius=0.0, seg=1)
    kc.rounded_block(mb, base + n * 0.02 + [0.0, spring + w * 0.22, 0.0], (0.04, w * 0.22, w * 0.32), dark,
                     rot=kc.rot_y(-th), radius=0.0, seg=1)
    arc = np.linspace(0.0, math.pi, 7)
    fr = w * 0.5 + 0.08
    pts = [base + n * 0.1 + t * fr + [0.0, y - h * 0.5, 0.0]]
    pts += [base + n * 0.1 + t * (math.cos(ang) * fr) + [0.0, spring + math.sin(ang) * fr, 0.0] for ang in arc]
    pts += [base + n * 0.1 - t * fr + [0.0, y - h * 0.5, 0.0]]
    kc.tube(mb, np.array(pts), 0.08, 3, cer)
    kc.rounded_block(mb, base + n * 0.12 + [0.0, y - h * 0.5 - 0.06, 0.0], (0.14, 0.06, w * 0.5 + 0.18), cer,
                     rot=kc.rot_y(-th), radius=0.0, seg=1)


def _storeys(mb: kc.MeshBuilder, galleries, r_at, lod: bool, *, y_top: float = 1e9, y_min: float = 4.0) -> None:
    """Rows of windows round a shaft: two storeys under each gallery, none in the sea or above a broken top."""
    if lod:
        return
    for gy in galleries:
        for dy in STOREY_ROWS:
            y = gy - dy
            if y - 1.0 < y_min or y + 1.0 > y_top:
                continue
            r = r_at(y)
            n = max(6, int(2 * math.pi * r / WINDOW_PITCH_M))
            off = 0.5 if dy == STOREY_ROWS[1] else 0.0
            for k in range(n):
                _window(mb, 2 * math.pi * (k + off) / n, y, r * 1.03)


def _damage(mb: kc.MeshBuilder, rng, y_lo: float, y_hi: float, r_at, n: int, lod: bool) -> None:
    """Spalled cladding (M3-ENV-724): patches where the glazed tile has fallen and the grey cast core shows, set
    flush on the shaft (a decal with depth: a thin block, its edges catching the light)."""
    if lod:
        return
    core = mb.material(M_CORE_EXPOSED)
    for _ in range(n):
        th = float(rng.uniform(0.0, 2 * math.pi))
        y = float(rng.uniform(y_lo, y_hi))
        r = r_at(y) * 1.03 + 0.012
        w, h = float(rng.uniform(0.35, 1.3)), float(rng.uniform(0.25, 0.9))
        c = np.array([math.cos(th) * r, y, math.sin(th) * r])
        kc.rounded_block(mb, c, (0.015, h * 0.5, w * 0.5), core, rot=kc.rot_y(-th) @ kc.rot_x(rng.normal(0, 0.2)),
                         radius=0.0, seg=1, weather=WORN, variation=float(rng.random()))


def _dome(mb: kc.MeshBuilder, y: float, r: float, h: float, rng, noise, lod: bool, finial: bool = True,
          mat: str = M_GILT) -> None:
    """A domed cap from radius r at y, rising h, with a ribbed surface and a gilt finial (gold leaf, or reef-blue
    glaze on the stepped towers): "white and gold at dusk" (iskarra.md §1)."""
    n = 9 if not lod else 3
    t = np.linspace(0.0, 1.0, n)
    prof = [(max(r * math.cos(tt * math.pi * 0.5) ** 0.8, 0.05), y + h * math.sin(tt * math.pi * 0.5)) for tt in t]
    tmp = kc.MeshBuilder("dome")
    import props  # noqa: PLC0415

    props.lathe(tmp, prof, mat, rng, sides=36 if not lod else 10, noise=None if lod else noise, disp_m=0.04,
                cap_start=False, weather=WORN)
    mb.merge(tmp)
    if finial and not lod:
        kc.tube(mb, np.array([[0.0, y + h - 0.1, 0.0], [0.0, y + h + 3.2, 0.0]]),
                np.array([0.22, 0.05]), 8, mb.material(M_GILT), cap_end=True)
        a = np.linspace(0.0, 2 * math.pi, 13)
        ring = np.stack([np.cos(a) * 0.5, np.full_like(a, y + h + 1.4), np.sin(a) * 0.5], axis=-1)
        kc.tube(mb, ring, 0.06, 5, mb.material(M_GILT))


def build_tower(kind: str, seed: int) -> list[kc.MeshBuilder]:
    name = "iskarra_tower_" + kind
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        if kind == "spire":
            gal = list(np.arange(12.0, 52.0, 9.0)) + [52.0]
            _shaft(mb, 0.0, 52.0, 6.0, 5.16, rng, noise, lod=lod, waterline=WATERLINE_M, stains=gal)
            _damage(mb, rng, 5.0, 50.0, lambda y: 6.0 - 0.84 * y / 52.0, 26, lod)
            for y in gal[:-1]:
                _gallery(mb, y, 6.0 - 0.84 * y / 52.0, rng, lod, sides1=LOD1_SIDES)
            _storeys(mb, gal, lambda y: 6.0 - 0.84 * y / 52.0, lod)
            _dome(mb, 52.0, 5.3, 7.0, rng, noise, lod)
        elif kind == "stepped":
            tiers = ((0.0, 20.0, 5.5, 5.2), (20.0, 33.0, 4.4, 4.1), (33.0, 42.0, 3.3, 3.0))
            for y0, y1, r0, r1 in tiers:
                _shaft(mb, y0, y1, r0, r1, rng, noise, lod=lod, waterline=WATERLINE_M if y0 == 0.0 else None,
                       stains=(y1,))
                _damage(mb, rng, max(y0, 4.0) + 0.5, y1 - 1.5, lambda y, a=r0, b=r1, c=y0, d=y1: a + (b - a) * (y - c) /
                        (d - c), 8, lod)
                _gallery(mb, y1, r1 + 0.2, rng, lod, sides1=LOD1_SIDES)
                if not lod and y1 < 42.0:
                    # The set-back's flat roof between tiers.
                    a = np.linspace(0.0, 2 * math.pi, 37)
                    grid = np.stack([np.stack([np.cos(a) * r1, np.full_like(a, y1), np.sin(a) * r1], -1),
                                     np.stack([np.cos(a) * (r1 - 1.1), np.full_like(a, y1), np.sin(a) * (r1 - 1.1)], -1)])
                    kc.quad_strip(mb, grid, mb.material(M_CERAMIC), uv=grid[..., [0, 2]], col=np.array([0, 0.3, 0, 0.5]),
                                  uv2=np.array([0.9, 0.5]))
            _storeys(mb, (20.0,), lambda y: 5.5 - 0.3 * y / 20.0, lod)
            _storeys(mb, (33.0,), lambda y: 4.4 - 0.3 * (y - 20.0) / 13.0, lod)
            _storeys(mb, (42.0,), lambda y: 3.3 - 0.3 * (y - 33.0) / 9.0, lod, y_min=33.5)
            _dome(mb, 42.0, 3.1, 4.0, rng, noise, lod, mat=M_GLAZE)
        elif kind == "broken":
            _shaft(mb, 0.0, 40.0, 5.0, 4.3, rng, noise, lod=lod, top_jagged=3.5, waterline=WATERLINE_M,
                   stains=(13.0, 24.0, 36.0))
            _damage(mb, rng, 5.0, 34.0, lambda y: 5.0 - 0.7 * y / 40.0, 30, lod)
            for y in (13.0, 24.0):
                _gallery(mb, y, 5.0 - 0.7 * y / 40.0, rng, lod, sides1=LOD1_SIDES)
            _storeys(mb, (13.0, 24.0, 33.0), lambda y: 5.0 - 0.7 * y / 40.0, lod, y_top=34.5)
        elif kind == "small":
            _shaft(mb, 0.0, 17.0, 3.5, 3.1, rng, noise, lod=lod, waterline=WATERLINE_M, stains=(10.0, 17.0))
            _damage(mb, rng, 4.5, 15.5, lambda y: 3.5 - 0.4 * y / 17.0, 8, lod)
            _gallery(mb, 10.0, 3.26, rng, lod, sides1=LOD1_SIDES)
            _gallery(mb, 17.0, 3.1, rng, lod, sides1=LOD1_SIDES)
            _storeys(mb, (10.0, 17.0), lambda y: 3.5 - 0.4 * y / 17.0, lod)
            _dome(mb, 17.0, 3.2, 3.6, rng, noise, lod)
        else:  # small_broken
            _shaft(mb, 0.0, 14.0, 3.0, 2.7, rng, noise, lod=lod, top_jagged=1.8, waterline=WATERLINE_M,
                   stains=(8.5, 12.0))
            _damage(mb, rng, 4.5, 11.0, lambda y: 3.0 - 0.3 * y / 14.0, 10, lod)
            _gallery(mb, 8.5, 2.82, rng, lod, sides1=LOD1_SIDES)
            _storeys(mb, (13.0,), lambda y: 3.0 - 0.3 * y / 14.0, lod, y_top=11.5)
        out.append(mb)
    return out


def build_crown_fallen(seed: int = 721) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("iskarra_crown_fallen", seed)
        noise = kc.Noise3(rng)
        tmp = kc.MeshBuilder("crown")
        _shaft(tmp, 0.0, 4.0, 3.4, 3.1, rng, noise, lod=lod, top_jagged=0.0)
        _gallery(tmp, 4.0, 3.2, rng, lod)
        _dome(tmp, 4.0, 3.0, 3.5, rng, noise, lod)
        mb = kc.MeshBuilder("iskarra_crown_fallen" + ("-lod1" if lod else ""))
        # On its side, half sunk: rolled 80 degrees about Z, its broken base toward -X.
        mb.merge(tmp, kc.rot_z(math.radians(80.0)) @ kc.rot_y(0.4), (2.0, -0.8, 0.0))
        out.append(mb)
    return out



def _flat_top(mb: kc.MeshBuilder, v0: int) -> None:
    """A slab's top shades flat (M3-ENV-724 render: a one-segment block's corner normals tilt up to 23 deg outward, so
    each 1.5 m slab read as a pillow): its upward vertex normals are set straight up."""
    n = np.asarray(mb.nrm[v0:])
    up = n[:, 1] > 0.85
    n[up] = (0.0, 1.0, 0.0)
    mb.nrm[v0:] = n.tolist()

# The Prologue dressing pass: the low and sunk flags hold the last rain or the spray, standing water that mirrors the
# dusk (the shader's wet layer: darker, glossy, its normal flattened). Chosen by noise (no rng draw, so the slab layout
# is unchanged): a puddle field over PUDDLE_NOISE, or any slab sunk deeper than PUDDLE_SUNK_M.
PUDDLED = kc.Weathering(moss=0.0, salt=0.3, wet=1.0, erosion=0.6)
PUDDLE_NOISE = 0.6
PUDDLE_PERIOD_M = 5.0
PUDDLE_SUNK_M = 0.03


def _puddled(noise, x: float, z: float, dy: float) -> bool:
    field = float(noise.fbm(np.array([[x / PUDDLE_PERIOD_M, 0.37, z / PUDDLE_PERIOD_M]]), 2)[0])
    return field > PUDDLE_NOISE or dy < -PUDDLE_SUNK_M


def _paving(mb: kc.MeshBuilder, x0: float, x1: float, z0: float, z1: float, y: float, rng, noise, lod: bool,
            keep=None, slab: float = 1.5, tufts: bool = True) -> None:
    """Paving slabs on a grid, each a separate block with a joint around it, a few sunk or lifted; `keep(x, z)`
    drops slabs (the broken corner). Every fourth row carries an inlaid ceramic channel: a narrow strip along the
    middle of each slab, flush with it, so the rows read as lines across the plaza (not a checkerboard)."""
    if lod:
        return  # the podium's top stands in for the slabs
    for i, x in enumerate(np.arange(x0 + slab * 0.5, x1, slab)):
        for j, z in enumerate(np.arange(z0 + slab * 0.5, z1, slab)):
            if keep is not None and not keep(x, z):
                continue
            dy = rng.normal(0.0, 0.02) - (0.08 if rng.random() < 0.06 else 0.0)
            yaw = rng.normal(0.0, 0.01)
            v0 = mb.vertex_count
            wear = PUDDLED if _puddled(noise, x, z, dy) else WORN
            if rng.random() < 0.12:  # M3-ENV-724: a slab cracked across, its halves settled apart
                tilt = rng.normal(0.0, 0.02)
                for sgn in (-1.0, 1.0):
                    kc.rounded_block(mb, (x + sgn * slab * 0.25, y - 0.15 + dy - (0.02 if sgn > 0 else 0.0), z),
                                     (slab * 0.25 - 0.035, 0.15, slab * 0.5 - 0.03), mb.material(M_PAVING),
                                     rot=kc.rot_y(yaw + sgn * 0.02) @ kc.rot_z(tilt * sgn), radius=0.03, seg=1,
                                     noise=noise, disp_m=0.008, weather=wear, variation=float(rng.random()))
            else:
                kc.rounded_block(mb, (x, y - 0.15 + dy, z), (slab * 0.5 - 0.03, 0.15, slab * 0.5 - 0.03),
                                 mb.material(M_PAVING), rot=kc.rot_y(yaw), radius=0.03, seg=1, noise=noise,
                                 disp_m=0.008, weather=wear, variation=float(rng.random()))
            _flat_top(mb, v0)
            if rng.random() < 0.18 and tufts:  # sea-grass grown in the joint at the slab's corner
                _tuft(mb, rng, (x + slab * 0.5, y, z + slab * 0.5), float(rng.uniform(0.15, 0.4)))
            if j % 4 == 1:
                kc.rounded_block(mb, (x, y - 0.02 + dy + 0.003, z), (slab * 0.5 - 0.03, 0.02, CHANNEL_HALF_W),
                                 mb.material(M_GLAZE), rot=kc.rot_y(yaw), radius=0.01, seg=1,
                                 weather=WORN, variation=float(rng.random()))


# The Prologue's cast marks in the plaza's frame (prologue.tscn: the plaza at (0, 0.4, 2)): Kerrid, Liss, Pell, Toma,
# Ysolde. The paving keeps every slab within CAST_CLEAR_M of them (M3-ENV-724, the vigil gap).
CAST_MARKS_LOCAL = ((9.5, -7.5), (4.5, -8.5), (-12.0, -0.5), (-12.0, 1.5), (7.5, -1.0))
CAST_CLEAR_M = 2.2
MEDALLION_AT = (3.5, 2.5)  # plaza-local x, z: clear of the dais, the steps and the vigils


def _sunburst(mb: kc.MeshBuilder, at, rng) -> None:
    """The Lit Age sunburst inlaid flush in the paving: a glazed ring, a white ring inside it, sixteen rays."""
    cx, cz = at
    glaze, cer = mb.material(M_GLAZE), mb.material(M_CERAMIC)
    a = np.linspace(0.0, 2 * math.pi, 49)
    for rad, mat, w in ((2.2, glaze, 0.09), (1.0, cer, 0.06), (0.35, glaze, 0.05)):
        ring = np.stack([cx + np.cos(a) * rad, np.full_like(a, 0.004), cz + np.sin(a) * rad], -1)
        kc.tube(mb, ring, w, 4, mat)
    for k in range(16):
        th = 2 * math.pi * k / 16
        ln = 0.55 if k % 2 else 0.95
        mid = 1.0 + 0.1 + ln * 0.5
        kc.rounded_block(mb, (cx + math.cos(th) * mid, 0.002, cz + math.sin(th) * mid), (ln * 0.5, 0.012, 0.05),
                         glaze if k % 2 == 0 else cer, rot=kc.rot_y(-th), radius=0.0, seg=1)


def _tuft(mb: kc.MeshBuilder, rng, at, h: float, blades: int = 7) -> None:
    """A tuft of salt-grass in a joint: crossed two-sided blade cards, bent by the wind off the sea."""
    grass = mb.material(M_GRASS)
    x, y, z = at
    for k in range(blades):
        th = 2 * math.pi * k / blades + float(rng.uniform(-0.3, 0.3))
        lean = np.array([math.cos(th), 0.0, math.sin(th)]) * float(rng.uniform(0.1, 0.35)) + np.array([0.08, 0, 0])
        hh = h * float(rng.uniform(0.6, 1.0))
        side = np.array([-math.sin(th), 0.0, math.cos(th)]) * 0.02
        base = np.array([x, y, z])
        top = base + np.array([0.0, hh, 0.0]) + lean * hh
        grid = np.array([[base - side, base + side], [top - side * 0.2, top + side * 0.2]])
        kc.quad_strip(mb, grid, grass, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]), col=(0.6, 0.3, 0.5, 0.4),
                      uv2=(0.9, float(rng.random())), smooth=False)


def build_plaza(seed: int = 722, *, w: float = 34.0, d: float = 18.0) -> list[kc.MeshBuilder]:
    hx, hz = w * 0.5, d * 0.5
    out = []
    for lod in (False, True):
        rng = kc.rng_for("iskarra_plaza", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("iskarra_plaza" + ("-lod1" if lod else ""))

        def keep(x, z):  # the back-right corner has fallen into the sea along a ragged line (clear of Kerrid's vigil)
            if any(math.hypot(x - mx, z - mz) < CAST_CLEAR_M for mx, mz in CAST_MARKS_LOCAL):
                return True  # M3-ENV-724: stone under every cast mark, whatever the broken edge does
            return (x - hx * 0.25) * 0.55 + (-z - hz * 0.2) < 7.5 + 1.5 * math.sin(x * 0.9)

        _paving(mb, -hx, hx, -hz, hz - 2.4, 0.0, rng, noise, lod, keep=keep)
        if not lod:
            _sunburst(mb, MEDALLION_AT, rng)
        # The plaza's body: a massive ceramic-faced podium down into the water, in 3 m bays whose back ends follow
        # the fallen corner's ragged line (so the break goes right down into the sea). At LOD1 its top is the paving.
        top = 0.0 if lod else -0.2
        for x in np.arange(-hx + 1.5, hx, 3.0):
            z0 = next((z for z in np.arange(-hz + 0.75, hz, 0.75) if keep(x - 0.75, z) and keep(x + 0.75, z)), -hz)
            z0 = max(-hz + 0.05, z0 - 0.75 + rng.uniform(-0.3, 0.3))
            z1 = hz - 2.3
            kc.rounded_block(mb, (x, top - 2.0, (z0 + z1) * 0.5), (1.5, 2.0, (z1 - z0) * 0.5), mb.material(M_CERAMIC),
                             radius=0.15, seg=1 if lod else 2, weather=WORN, variation=float(rng.random()))
        # Steps down to the water at the front (+Z), across the middle two thirds.
        for k in range(5 if not lod else 1):
            z = hz - 2.4 + 0.48 * k + 0.24
            y = -0.3 - 0.3 * k
            kc.rounded_block(mb, (0.0, y - 0.15 + 0.15, z), (hx * 0.66, 0.15 if not lod else 0.8, 0.26 if not lod else 1.2),
                             mb.material(M_PAVING), radius=0.03, seg=1, noise=None if lod else noise, disp_m=0.01,
                             weather=WORN, variation=float(rng.random()))
        if not lod:
            # Balustrade stumps along the two sides: a coping run broken into pieces, a few balusters standing.
            for sx in (-1.0, 1.0):
                for k, z in enumerate(np.arange(-hz + 1.5, hz - 3.0, 2.2)):
                    if rng.random() < 0.35:
                        continue
                    h = rng.uniform(0.35, 1.0)
                    kc.tube(mb, np.array([[sx * (hx - 0.4), 0.0, z], [sx * (hx - 0.4), h, z]]),
                            np.array([0.16, 0.11]), 10, mb.material(M_CERAMIC), cap_end=True, weather=WORN,
                            variation=float(rng.random()))
            # Rubble from the fallen corner lying on the paving's broken edge.
            for k in range(14):
                x = rng.uniform(hx * 0.1, hx)
                z = rng.uniform(-hz, -hz * 0.1)
                if keep(x, z):
                    s = rng.uniform(0.15, 0.5)
                    kc.rounded_block(mb, (x, s * 0.4, z), (s, s * 0.5, s * 0.8), mb.material(M_PAVING),
                                     rot=kc.rot_y(rng.uniform(0, 3)), radius=s * 0.2, seg=1, noise=noise, disp_m=0.02,
                                     variation=float(rng.random()))
            # Glazed tiles fallen from the towers' bands, lying where the sea left them.
            for k in range(40):
                x, z = rng.uniform(-hx + 1.0, hx - 1.0), rng.uniform(-hz + 1.0, hz - 3.0)
                if not keep(x, z) or math.hypot(x - MEDALLION_AT[0], z - MEDALLION_AT[1]) < 2.6:
                    continue
                kc.rounded_block(mb, (x, 0.012, z), (0.2, 0.012, 0.1), mb.material(M_GLAZE if k % 3 else M_CLAD),
                                 rot=kc.rot_y(rng.uniform(0, 3.2)) @ kc.rot_x(rng.normal(0, 0.05)), radius=0.0, seg=1)
        out.append(mb)
    return out


RISE_TOP_Y = 0.8
RISE_FLAG_M = 1.02
RISE_FLAGS_HX = 4.08  # eight flags across, inside the glazed border (x 4.34)
RISE_FLAGS_Z = (-2.44, 1.64)  # four rows, border to border
RISE_FLAGS_UP_M = 0.0
RISE_FLAG_DEPTH_M = 0.05  # the core stops this far under the flags' top: shallow dark joints (each flag beds into it)


def build_plaza_rise(seed: int = 723) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("iskarra_plaza_rise", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("iskarra_plaza_rise" + ("-lod1" if lod else ""))
        # LOD0: the dais's core stops a flag's depth under its top (the flags drawn on it below are the top).
        core = RISE_TOP_Y if lod else RISE_TOP_Y - RISE_FLAG_DEPTH_M
        kc.rounded_block(mb, (0.0, core * 0.5, -0.4), (5.0, core * 0.5, 2.6), mb.material(M_PAVING), radius=0.06,
                         seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.01, weather=WORN)
        for k in range(3 if not lod else 1):
            kc.rounded_block(mb, (0.0, 0.8 - (k + 1) * 0.27 + 0.135, 2.2 + 0.27 * k + 0.135),
                             (4.2, 0.135, 0.15), mb.material(M_PAVING), radius=0.03, seg=1, variation=float(rng.random()))
        if not lod:  # M3-ENV-724: a cast coping round the dais, a flush glazed border inside it, glazed riser bands
            cer, glaze = mb.material(M_CERAMIC), mb.material(M_GLAZE)
            for (cx, cz, sx, sz) in ((0.0, -3.0, 5.05, 0.12), (0.0, 2.2, 5.05, 0.12), (-5.0, -0.4, 0.12, 2.6),
                                     (5.0, -0.4, 0.12, 2.6)):
                kc.rounded_block(mb, (cx, 0.805, cz), (sx, 0.025, sz), cer, radius=0.01, seg=1, weather=WORN)
            for (cx, cz, sx, sz) in ((0.0, -2.5, 4.4, 0.06), (0.0, 1.7, 4.4, 0.06), (-4.4, -0.4, 0.06, 2.1),
                                     (4.4, -0.4, 0.06, 2.1)):
                kc.rounded_block(mb, (cx, 0.8, cz), (sx, 0.006, sz), glaze, radius=0.0, seg=1)
            for k in range(3):
                kc.rounded_block(mb, (0.0, 0.8 - (k + 1) * 0.27 + 0.135, 2.2 + 0.27 * k + 0.282),
                                 (4.1, 0.05, 0.006), glaze, radius=0.0, seg=1)
            # The Prologue dressing pass: the dais top was one blank slab filling P02's lower half (the two-shot where
            # Rhen's line lands). The plaza's own flags inside the glazed border, cracked and settled, the low ones
            # holding water; drawn last, so the rng above is unchanged.
            _paving(mb, -RISE_FLAGS_HX, RISE_FLAGS_HX, RISE_FLAGS_Z[0], RISE_FLAGS_Z[1], RISE_TOP_Y + RISE_FLAGS_UP_M,
                    rng, noise, lod, slab=RISE_FLAG_M, tufts=False)  # no grass round the cast's feet
        out.append(mb)
    return out


def _pillar(mb: kc.MeshBuilder, x: float, h: float, rng, noise, lod: bool, *, broken: bool = False) -> None:
    tmp = kc.MeshBuilder("p")
    _shaft(tmp, 0.4, h, 0.62, 0.55, rng, noise, lod=lod, top_jagged=0.4 if broken else 0.0)
    mb.merge(tmp, None, (x, 0.0, 0.0))
    kc.rounded_block(mb, (x, 0.2, 0.0), (0.85, 0.2, 0.85), mb.material(M_CERAMIC), radius=0.05, seg=1)
    if not broken:
        kc.rounded_block(mb, (x, h + 0.2, 0.0), (0.82, 0.2, 0.82), mb.material(M_CERAMIC), radius=0.05, seg=1)


def build_arch(seed: int = 724, *, fallen: bool = False) -> list[kc.MeshBuilder]:
    name = "iskarra_arch_fallen" if fallen else "iskarra_arch"
    out = []
    for lod in (False, True):
        rng = kc.rng_for("iskarra_arch", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        h = 9.5
        if not fallen:
            _pillar(mb, -3.8, h, rng, noise, lod)
            _pillar(mb, 3.8, h, rng, noise, lod)
            kc.rounded_block(mb, (0.0, h + 1.1, 0.0), (4.5, 0.7, 0.8), mb.material(M_CERAMIC), radius=0.08,
                             seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.01, weather=WORN)
            if not lod:
                # The lintel's carved band: a row of fan-shell bosses.
                for k in range(7):
                    x = -3.0 + k
                    kc.rounded_block(mb, (x, h + 1.1, 0.82), (0.3, 0.3, 0.06), mb.material(M_CERAMIC), radius=0.1,
                                     seg=2, variation=0.6)
            # Two torn banners from the lintel's front (M3-ENV-724), the gate's last colour.
            for x0 in (-2.6, 1.0):
                _banner(mb, rng, (x0, h + 0.45, 0.86), (x0 + 1.6, h + 0.45, 0.86), 4.2, lod)
        else:
            _pillar(mb, -3.8, h, rng, noise, lod)
            _pillar(mb, 3.8, 3.1, rng, noise, lod, broken=True)
            # The lintel broken in two on the ground, the fallen pillar's drum lying beside it.
            for (x, z, a, ln) in ((-1.0, 2.2, 0.21, 2.6), (3.2, 2.9, -0.35, 1.8)):
                kc.rounded_block(mb, (x, 0.55, z), (ln, 0.55, 0.75), mb.material(M_CERAMIC), rot=kc.rot_y(a) @ kc.rot_z(0.05),
                                 radius=0.08, seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.015,
                                 weather=WORN)
            if not lod:
                tmp = kc.MeshBuilder("drum")
                _shaft(tmp, 0.0, 5.5, 0.6, 0.57, rng, noise, lod=False, top_jagged=0.3)
                mb.merge(tmp, kc.rot_y(0.7) @ kc.rot_z(math.pi * 0.5), (7.5, 0.6, -0.5))
        out.append(mb)
    return out


LAMP_FLAME_R = 0.07  # the flame in a lamp column's globe (its base at LAMP_FLAME_Y)
LAMP_FLAME_Y = 5.68
OFFERING_SHELLS_X = tuple(-4.5 + 1.5 * k for k in range(7))  # the seven shells on the front step's lip
OFFERING_Z_FROM_BACK = 2.55
OFFERING_LAMP_DX = 0.24  # each shell's oil saucer beside it
OFFERING_FLAME_R = 0.025


def build_lamp_column(seed: int = 725) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("iskarra_lamp_column", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("iskarra_lamp_column" + ("-lod1" if lod else ""))
        tmp = kc.MeshBuilder("s")
        _shaft(tmp, 0.0, 5.4, 0.22, 0.15, rng, noise, lod=lod)
        mb.merge(tmp)
        kc.rounded_block(mb, (0.0, 0.15, 0.0), (0.38, 0.15, 0.38), mb.material(M_CERAMIC), radius=0.04, seg=1)
        # The head: a bronze cage round a clouded glass globe, an oil flame set in it for the vigil (the Lead, 10-28:
        # the Prologue's lamps are lit; the city's light is the mourners').
        import props  # noqa: PLC0415

        flame = [(r * LAMP_FLAME_R / 0.85, LAMP_FLAME_Y + y * LAMP_FLAME_R * 2.4) for r, y in props.FLAME_PROFILE]
        props.lathe(mb, flame if not lod else flame[::2], "kit_lamp_flame_hot", rng, sides=10 if not lod else 5,
                    weather=kc.Weathering(0, 0, 0, 0))

        ang = np.linspace(-math.pi * 0.5, math.pi * 0.5, 7 if not lod else 3)
        globe = np.stack([np.maximum(np.cos(ang) * 0.36, 0.01), np.sin(ang) * 0.36], -1)
        props.lathe(mb, globe, "kit_lamp_glass_lit", rng,
                    sides=14 if not lod else 6, at=(0.0, 5.85, 0.0), cap_start=False)
        if not lod:
            for k in range(4):
                a = k * math.pi * 0.5
                arc = np.stack([np.cos(a) * np.cos(ang) * 0.39, 5.85 + np.sin(ang) * 0.39, np.sin(a) * np.cos(ang) * 0.39],
                               axis=-1)
                kc.tube(mb, arc, 0.018, 4, mb.material(M_BRONZE))
            kc.tube(mb, np.array([[0.0, 6.2, 0.0], [0.0, 6.55, 0.0]]), np.array([0.06, 0.02]), 6,
                    mb.material(M_BRONZE), cap_end=True)
            # A strip of mourning cloth knotted under the head (M3-ENV-724).
            _banner(mb, rng, (0.12, 5.5, 0.0), (0.12, 5.5, 0.24), 1.6, False)
        out.append(mb)
    return out


def build_drowned_block(name: str, seed: int, *, w: float, d: float, h: float, dome: bool) -> list[kc.MeshBuilder]:
    """A drowned building's top storeys: tiled walls from under the sea to h, arched windows on every face, the glazed
    band under a cast cornice, a parapet, the roof terrace (fallen in at its +X end unless it carries a dome)."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        clad, cer, glaze = mb.material(M_CLAD), mb.material(M_CERAMIC), mb.material(M_GLAZE)
        hx, hz, t = w * 0.5, d * 0.5, 0.35
        y0 = -WATERLINE_M
        for (cx, cz, sx, sz) in ((0.0, hz - t, hx, t), (0.0, -hz + t, hx, t), (hx - t, 0.0, t, hz - 2 * t),
                                 (-hx + t, 0.0, t, hz - 2 * t)):
            kc.rounded_block(mb, (cx, (y0 + h) * 0.5, cz), (sx, (h - y0) * 0.5, sz), clad, radius=0.04, seg=1,
                             weather=WORN, variation=float(rng.random()))
        # The cornice, the glazed band under it, and the parapet's coping.
        kc.rounded_block(mb, (0.0, h + 0.15, 0.0), (hx + 0.3, 0.15, hz + 0.3), cer, radius=0.05, seg=1, weather=WORN)
        kc.rounded_block(mb, (0.0, h - 0.55, 0.0), (hx + 0.04, 0.45, hz + 0.04), glaze, radius=0.02, seg=1)
        for (cx, cz, sx, sz) in ((0.0, hz, hx + 0.3, 0.15), (0.0, -hz, hx + 0.3, 0.15), (hx, 0.0, 0.15, hz),
                                 (-hx, 0.0, 0.15, hz)):
            kc.rounded_block(mb, (cx, h + 0.75, cz), (sx, 0.45, sz), cer, radius=0.04, seg=1, weather=WORN)
        # The roof terrace, its +X end fallen in (rubble on the slab's broken edge) unless a dome stands on it.
        if dome:
            kc.rounded_block(mb, (0.0, h - 0.1, 0.0), (hx - t, 0.1, hz - t), cer, radius=0.02, seg=1)
            _dome(mb, h, min(hx, hz) * 0.62, min(hx, hz) * 0.5, rng, noise, lod, mat=M_GLAZE)
        else:
            kc.rounded_block(mb, (-hx * 0.3, h - 0.1, 0.0), (hx * 0.7 - t, 0.1, hz - t), cer, radius=0.02, seg=1)
            if not lod:
                for k in range(8):
                    s_ = rng.uniform(0.25, 0.6)
                    kc.rounded_block(mb, (hx * 0.4 + rng.uniform(-0.3, 0.6), h - 0.1 + s_ * 0.3,
                                          rng.uniform(-hz + 1.0, hz - 1.0)), (s_, s_ * 0.4, s_ * 0.7), cer,
                                     rot=kc.rot_y(rng.uniform(0, 3)) @ kc.rot_z(rng.normal(0, 0.3)), radius=0.05,
                                     seg=1, weather=WORN)
        if not lod:  # windows: one row just over the water, one under the band
            for y in (1.3, 4.6):  # a second storey of windows only where the walls rise high enough under the band
                if y + 1.0 > h - 1.1:
                    continue
                for th, half, fx in ((0.0, hz, hx), (math.pi, hz, -hx), (math.pi * 0.5, hx, hz), (-math.pi * 0.5, hx, -hz)):
                    n = max(2, int(half * 2 / WINDOW_PITCH_M))
                    for k in range(n):
                        along = -half + (k + 0.5) * 2 * half / n
                        tmp = kc.MeshBuilder("w")
                        _window(tmp, 0.0, y, 0.0)  # built facing +X, then turned to the face's outward normal
                        R = kc.rot_y(-th)
                        mb.merge(tmp, R, tuple(R @ np.array([abs(fx), 0.0, along])))
        out.append(mb)
    return out


def build_arcade_sunk(seed: int = 727) -> list[kc.MeshBuilder]:
    out = []
    bays, pitch = 5, 4.6
    for lod in (False, True):
        rng = kc.rng_for("iskarra_arcade_sunk", seed)
        mb = kc.MeshBuilder("iskarra_arcade_sunk" + ("-lod1" if lod else ""))
        clad, cer, glaze = mb.material(M_CLAD), mb.material(M_CERAMIC), mb.material(M_GLAZE)
        x0 = -bays * pitch * 0.5
        spring, top = 2.2, 4.4
        fallen = 3
        for k in range(bays + 1):
            x = x0 + k * pitch
            h = spring if k != fallen + 1 else 1.1  # the pier beyond the fallen bay broke
            kc.rounded_block(mb, (x, (h - WATERLINE_M) * 0.5, 0.0), (0.38, (h + WATERLINE_M) * 0.5, 0.38), clad,
                             radius=0.03, seg=1, weather=WORN, variation=float(rng.random()))
            if k != fallen + 1:
                kc.rounded_block(mb, (x, h + 0.1, 0.0), (0.48, 0.1, 0.48), cer, radius=0.02, seg=1)
        a = np.linspace(0.0, math.pi, 5 if lod else 13)
        rad = pitch * 0.5 - 0.38
        for k in range(bays):
            if k in (fallen, fallen + 1):  # the two bays either side of the broken pier are down
                continue
            cx = x0 + (k + 0.5) * pitch
            arc = np.stack([cx + np.cos(a) * rad, spring + 0.2 + np.sin(a) * rad, np.zeros_like(a)], -1)
            kc.tube(mb, arc, 0.3, 3 if lod else 6, cer)
            kc.rounded_block(mb, (cx, (top + spring + rad * 0.5) * 0.5 + 0.2, 0.0), (pitch * 0.5,
                             (top - spring - rad * 0.5) * 0.5, 0.36), clad, radius=0.02, seg=1)
            kc.rounded_block(mb, (cx, top + 0.35, 0.0), (pitch * 0.5 + 0.02, 0.25, 0.44), glaze, radius=0.02, seg=1)
            if not lod:
                kc.rounded_block(mb, (cx, top + 0.75, 0.0), (pitch * 0.5 + 0.05, 0.15, 0.5), cer, radius=0.03, seg=1)
        if not lod:  # the fallen arch's voussoirs and lintel in the water by the broken pier
            for j in range(5):
                kc.rounded_block(mb, (x0 + (fallen + 0.5) * pitch + rng.uniform(-1.5, 1.5), rng.uniform(-0.4, 0.2),
                                      rng.uniform(-1.2, 1.4)), (rng.uniform(0.4, 0.9), 0.3, 0.35), cer,
                                 rot=kc.rot_y(rng.uniform(0, 3)) @ kc.rot_z(rng.normal(0, 0.4)), radius=0.04, seg=1,
                                 weather=WORN)
        out.append(mb)
    return out


FAR_RANGE_M = (180.0, 520.0)


def build_far_towers(seed: int = 729) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("iskarra_far_towers", seed)
        mb = kc.MeshBuilder("iskarra_far_towers" + ("-lod1" if lod else ""))
        clad, cer, glaze, dark = (mb.material(M_CLAD), mb.material(M_CERAMIC), mb.material(M_GLAZE),
                                  mb.material(M_DARK))
        n = 44
        sides = 4 if lod else 10
        for k in range(n):
            # Behind the plaza (-Z) and round the flanks: bearings from -110 to +110 degrees off -Z.
            bearing = math.radians(-110.0 + 220.0 * (k + rng.uniform(0.1, 0.9)) / n)
            r = rng.uniform(*FAR_RANGE_M)
            x, z = math.sin(bearing) * r, -math.cos(bearing) * r
            rad = rng.uniform(3.0, 7.5)
            h = rng.uniform(18.0, 70.0) * (0.7 if r < 260.0 else 1.0)
            kind = rng.integers(0, 3)  # 0 domed, 1 stepped, 2 broken
            top = h * (0.6 if kind == 2 else 1.0)
            kc.tube(mb, np.array([[x, -WATERLINE_M, z], [x, top, z]]), np.array([rad, rad * 0.88]), sides, clad,
                    cap_end=kind != 0)
            for g in () if lod else np.arange(12.0, top - 3.0, 10.0):  # the galleries and their glazed band
                rr = rad - 0.12 * rad * g / h
                ring = np.array([[x, g, z], [x, g + 0.5, z]])
                kc.tube(mb, ring, rr + 0.6, sides, cer, cap_start=True, cap_end=True)
                kc.tube(mb, np.array([[x, g - 1.4, z], [x, g - 0.4, z]]), rr * 1.02 + 0.03, sides, glaze)
                kc.tube(mb, np.array([[x, g - 4.2, z], [x, g - 2.4, z]]), rr * 1.01 + 0.02, sides, dark)
            if kind == 0:
                dome = np.array([[x, top, z], [x, top + rad * 0.6, z], [x, top + rad * 0.95, z]])
                kc.tube(mb, dome, np.array([rad * 0.9, rad * 0.62, 0.05]), sides,
                        glaze if rng.random() < 0.3 else cer)
            elif kind == 1:
                kc.tube(mb, np.array([[x, top, z], [x, top + h * 0.25, z]]), np.array([rad * 0.6, rad * 0.5]), sides,
                        clad, cap_end=True)
        out.append(mb)
    return out


def _pack(mb, rng, at, yaw: float) -> None:
    """A traveller's pack and a rolled bedroll beside it (the party's gear: no fire, ADR 0017)."""
    sand, indigo, lash = mb.material("kit_cloth_sand"), mb.material("kit_cloth_indigo"), mb.material("kit_lashing")
    x, y, z = at
    R = kc.rot_y(yaw)
    lean = R @ kc.rot_z(rng.normal(0, 0.08))
    d = R @ np.array([0.0, 0.0, 1.0])
    e = R @ np.array([1.0, 0.0, 0.0])
    base = np.array([x, y, z])
    # M3-ENV-724 render (I02 has one by the lens): the body slumped and creased, not a smooth capsule.
    v0, t0 = mb.vertex_count, mb.triangle_count
    kc.rounded_block(mb, (x, y + 0.24, z), (0.2, 0.24, 0.14), sand, rot=lean, radius=0.08, seg=3,
                     noise=kc.Noise3(rng), disp_m=0.025, disp_period_m=0.12)
    p = np.asarray(mb.pos[v0:])
    h = np.clip((p[:, 1] - y) / 0.48, 0.0, 1.0)
    p[:, [0, 2]] += (p[:, [0, 2]] - base[[0, 2]]) * (0.12 * np.sin(np.pi * h))[:, None]  # it bellies, full of gear
    mb.pos[v0:] = p.tolist()
    kc.recompute_normals(mb, v0, t0)
    # The lid flap over the drawn top, hanging down the front; two straps over it to buckles; a front pocket.
    kc.rounded_block(mb, base + [0, 0.5, 0] + d * 0.02, (0.19, 0.035, 0.15), sand, rot=R @ kc.rot_x(0.1), radius=0.03,
                     seg=2)
    kc.rounded_block(mb, base + [0, 0.42, 0] + d * 0.16, (0.17, 0.08, 0.02), sand, rot=R @ kc.rot_x(-0.12),
                     radius=0.015, seg=1)
    kc.rounded_block(mb, base + [0, 0.2, 0] + d * 0.165, (0.13, 0.09, 0.035), sand, rot=R, radius=0.03, seg=2)
    for s_ in (-0.09, 0.09):
        strap = np.array([base + e * s_ + [0, 0.53, 0] - d * 0.12, base + e * s_ + [0, 0.54, 0] + d * 0.06,
                          base + e * s_ + [0, 0.42, 0] + d * 0.185, base + e * s_ + [0, 0.3, 0] + d * 0.2])
        kc.tube(mb, strap, 0.012, 4, lash)
        kc.rounded_block(mb, base + e * s_ + [0, 0.3, 0] + d * 0.205, (0.02, 0.02, 0.006), mb.material("kit_brass"),
                         rot=R, radius=0.004, seg=1)
    roll = np.array([x, y + 0.1, z]) + d * 0.45
    kc.tube(mb, np.array([roll - e * 0.35, roll + e * 0.35]), 0.1, 10, indigo, cap_start=True, cap_end=True)
    for s_ in (-0.2, 0.2):
        a = np.linspace(0.0, 2 * math.pi, 9)
        c = roll + e * s_
        ring = np.stack([np.full_like(a, 0.0), np.cos(a) * 0.105, np.sin(a) * 0.105], -1) @ np.array([e, [0, 1, 0], d])
        kc.tube(mb, ring + c, 0.012, 3, lash)


def build_vigil_dressing(seed: int = 730) -> list[kc.MeshBuilder]:
    """The vigil on the plaza (M3-ENV-724), in the plaza's frame: each member's gear by their mark, seven shells laid
    along the front step's lip (one for each who keeps the vigil), a broken jar, salt-grass along the edges and
    creepers down the podium's sides. Each shell has a lit oil saucer beside it (the Lead overruled ADR 0017's "only
    Rhen's lantern burns" for the Prologue, 10-28)."""
    out = []
    hx, hz = 17.0, 9.0
    for lod in (False, True):
        rng = kc.rng_for("iskarra_vigil_dressing", seed)
        mb = kc.MeshBuilder("iskarra_vigil_dressing" + ("-lod1" if lod else ""))
        for (mx, mz), yaw in zip(CAST_MARKS_LOCAL, (0.3, -0.5, 1.2, 1.9, 2.6)):
            if lod:
                kc.rounded_block(mb, (mx + 0.7, 0.2, mz + 0.4), (0.2, 0.2, 0.15), mb.material("kit_cloth_sand"),
                                 radius=0.05, seg=1)
                continue
            _pack(mb, rng, (mx + 0.75 * math.cos(yaw), 0.0, mz + 0.75 * math.sin(yaw)), yaw)
        if not lod:
            _pack(mb, rng, (-1.2, 0.8, -1.1), 0.4)  # Rhen's and Asha's, on the dais
            # Seven shells along the lip of the front steps' top, evenly spaced, mouths to the sea.
            shell = mb.material("kit_wake_shell")
            import props  # noqa: PLC0415

            for x in OFFERING_SHELLS_X:
                kc.rounded_block(mb, (x, 0.03, hz - OFFERING_Z_FROM_BACK), (0.09, 0.03, 0.07), shell,
                                 rot=kc.rot_y(rng.normal(0, 0.2)), radius=0.03, seg=2)
                # A clay oil saucer lit beside each shell (the Lead, 10-28: the vigil's offerings burn).
                at = (x + OFFERING_LAMP_DX, 0.0, hz - OFFERING_Z_FROM_BACK)
                props.lathe(mb, [(0.0, 0.0), (0.05, 0.0), (0.07, 0.025), (0.065, 0.03), (0.0, 0.018)],
                            "kit_earthenware", rng, sides=10, at=at)
                flame = [(r * OFFERING_FLAME_R / 0.85, 0.02 + y * OFFERING_FLAME_R * 2.4) for r, y in props.FLAME_PROFILE]
                props.lathe(mb, flame, "kit_lamp_flame_hot", rng, sides=8, at=at, weather=kc.Weathering(0, 0, 0, 0))
            # A broken water jar by the lamp row, its sherds.
            clay = "kit_earthenware"
            import props  # noqa: PLC0415

            props.lathe(mb, [(0.18, 0.0), (0.26, 0.2), (0.22, 0.42), (0.12, 0.5)], clay, rng, sides=12,
                        at=(-9.0, 0.0, -7.6))
            for j in range(5):
                kc.rounded_block(mb, (-8.4 + rng.uniform(-0.4, 0.4), 0.02, -7.2 + rng.uniform(-0.4, 0.4)),
                                 (0.08, 0.015, 0.05), mb.material(clay), rot=kc.rot_y(rng.uniform(0, 3)), radius=0.01,
                                 seg=1)
            # Salt-grass along the paving's edges and the balustrade stumps.
            for j in range(60):
                side = rng.integers(0, 3)
                if side == 0:
                    x, z = rng.uniform(-hx + 0.3, hx - 0.3), -hz + rng.uniform(0.2, 1.5)
                elif side == 1:
                    x, z = -hx + rng.uniform(0.3, 1.2), rng.uniform(-hz, hz - 3.0)
                else:
                    x, z = hx - rng.uniform(0.3, 1.2), rng.uniform(-hz * 0.2, hz - 3.0)
                if any(math.hypot(x - mx, z - mz) < 1.2 for mx, mz in CAST_MARKS_LOCAL):
                    continue
                _tuft(mb, rng, (x, 0.0, z), float(rng.uniform(0.2, 0.55)), blades=6)
            # Creepers hanging down the podium's two sides into the sea, salt-burned at their tips.
            leaf = mb.material("kit_canopy_leaf_dark")
            for sx in (-1.0, 1.0):
                for j in range(9):
                    z = rng.uniform(-hz + 1.0, hz - 3.5)
                    n = 6
                    t = np.linspace(0.0, 1.0, n)
                    path = np.stack([np.full(n, sx * (hx + 0.05)) + sx * 0.12 * np.sin(t * 3.0),
                                     -t * rng.uniform(1.5, 3.5), z + 0.3 * np.sin(t * 5.0 + j)], -1)
                    kc.tube(mb, path, 0.015, 3, mb.material("kit_banyan_root"))
                    for p in path[1:]:
                        g = np.array([[p + [0, 0.12, -0.1], p + [0, 0.12, 0.1]], [p + [sx * 0.08, -0.1, -0.1],
                                                                                   p + [sx * 0.08, -0.1, 0.1]]])
                        kc.quad_strip(mb, g, leaf, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]),
                                      col=(0.4, 0.2, 0.5, 0.6), uv2=(0.8, float(rng.random())), smooth=False)
        out.append(mb)
    return out


def _banner(mb, rng, top_a, top_b, drop: float, lod: bool) -> None:
    """A torn Lit Age banner hung from two points: sea-blue cloth faded, its lower edge ragged; both faces."""
    cloth = mb.material("kit_cloth_sea_blue")
    nu, nv = (3, 3) if lod else (6, 8)
    u = np.linspace(0.0, 1.0, nu)
    v = np.linspace(0.0, 1.0, nv)
    U, V = np.meshgrid(u, v, indexing="ij")
    top = np.asarray(top_a) + (np.asarray(top_b) - np.asarray(top_a)) * U[..., None]
    rag = 1.0 - 0.35 * (np.abs(np.sin(U * 9.0 + 1.7)) ** 3) * (V ** 4)
    sway = np.stack([np.zeros_like(U), np.zeros_like(U), 0.12 * np.sin(V * 2.5 + U)], -1) * V[..., None]
    pts = top + np.stack([np.zeros_like(U), -drop * V * rag, np.zeros_like(U)], -1) + sway
    for f in (False, True):
        kc.quad_strip(mb, pts, cloth, uv=np.stack([U, V], -1), col=(0.0, 0.2, 0.0, 0.5), uv2=(0.85, 0.5), flip=f,
                      smooth=not lod)


TARGETS = {
    "iskarra_tower_spire": lambda: build_tower("spire", 731),
    "iskarra_tower_stepped": lambda: build_tower("stepped", 732),
    "iskarra_tower_broken": lambda: build_tower("broken", 733),
    "iskarra_tower_small": lambda: build_tower("small", 734),
    "iskarra_tower_small_broken": lambda: build_tower("small_broken", 735),
    "iskarra_crown_fallen": build_crown_fallen,
    "iskarra_plaza": build_plaza,
    "iskarra_plaza_rise": build_plaza_rise,
    "iskarra_arch": build_arch,
    "iskarra_arch_fallen": lambda: build_arch(fallen=True),
    "iskarra_lamp_column": build_lamp_column,
    "iskarra_drowned_block": lambda: build_drowned_block("iskarra_drowned_block", 726, w=14.0, d=10.0, h=4.5,
                                                         dome=False),
    "iskarra_drowned_dome": lambda: build_drowned_block("iskarra_drowned_dome", 728, w=9.0, d=9.0, h=3.6,
                                                        dome=True),
    "iskarra_arcade_sunk": build_arcade_sunk,
    "iskarra_far_towers": build_far_towers,
    "iskarra_vigil_dressing": build_vigil_dressing,
}
