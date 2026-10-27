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

Origins: towers at their foot centre on the sea bed datum (the sea is at y 3 above it: their waterline band sits
there), the plaza pieces at their top's centre (y 0 = the paving), the rest at their foot. Front +Z.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_CERAMIC = "kit_iskarra_ceramic"
M_PAVING = "kit_iskarra_paving"
M_BRONZE = "kit_iskarra_bronze"
M_GLASS = "kit_salt_glass"
M_DARK = "kit_interior_dark"

WATERLINE_M = 3.0  # the tower's foot is this far under the sea (the Prologue's water is at y 0, feet at -3)
FLUTES = 18

TRI_BUDGET = {
    "iskarra_tower": (16000, 1200),
    "iskarra_crown_fallen": (4000, 300),
    "iskarra_plaza": (14000, 600),
    "iskarra_plaza_rise": (3000, 120),
    "iskarra_arch": (4000, 200),
    "iskarra_lamp_column": (1500, 100),
}
BUDGET_KEY = {name: "iskarra_tower" for name in ("iskarra_tower_spire", "iskarra_tower_stepped", "iskarra_tower_broken",
                                                 "iskarra_tower_small", "iskarra_tower_small_broken")}
BUDGET_KEY["iskarra_arch_fallen"] = "iskarra_arch"

WORN = kc.Weathering(moss=0.0, salt=0.6, wet=0.0, erosion=0.6)  # dry above the tide: the shaft paints its own band


def _shaft(mb: kc.MeshBuilder, y0: float, y1: float, r0: float, r1: float, rng, noise, *, lod: bool,
           top_jagged: float = 0.0, waterline: float | None = None) -> None:
    """A fluted ceramic shaft from y0 (radius r0) to y1 (r1), its vertex colours carrying the waterline band
    (salt and wet below `waterline`+1 m) and wear; `top_jagged` > 0 breaks the top rim into a ragged edge."""
    na = (FLUTES * 4 if not lod else 12) + 1
    ny = max(2, int((y1 - y0) / (1.5 if not lod else 8.0)) + 1)
    a = np.linspace(0.0, 2 * math.pi, na)
    t = np.linspace(0.0, 1.0, ny)
    A, T = np.meshgrid(a, t)
    Y = y0 + T * (y1 - y0)
    R = r0 + (r1 - r0) * T
    if not lod:
        R = R * (1.0 + 0.018 * np.cos(A * FLUTES))  # flutes
    if top_jagged > 0.0:
        jag = (noise.fbm(np.stack([np.cos(a) * 3.0, np.zeros_like(a), np.sin(a) * 3.0], -1), 3) - 0.5) * 2.0
        Y[-1] = y1 - top_jagged * (0.5 + 0.5 * np.abs(jag)) - top_jagged * 0.6 * (np.sin(a * 2.0 + 1.0) > 0.4)
        if ny > 2:
            Y[-2] = np.minimum(Y[-2], Y[-1] - 0.2)
    P = np.stack([np.cos(A) * R, Y, np.sin(A) * R], axis=-1)
    if waterline is not None:
        wet = 1.0 - kc.smoothstep(waterline, waterline + 1.2, Y)
        salt = np.clip(1.0 - kc.smoothstep(waterline + 0.5, waterline + 4.0, Y), 0.0, 1.0) * 0.8
    else:
        wet = np.zeros_like(Y)
        salt = np.zeros_like(Y)
    breakup = noise.fbm(P / 4.0, 2) if not lod else np.full(Y.shape, 0.5)
    col = np.stack([np.zeros_like(Y), np.clip(salt + 0.15 * breakup, 0, 1), wet, 0.35 + 0.4 * breakup], axis=-1)
    uv = np.stack([A / (2 * math.pi) * (2 * math.pi * r0) / 2.0, Y / 2.0], axis=-1)
    uv2 = np.stack([np.full(Y.shape, 0.9), np.full(Y.shape, float(rng.random()))], axis=-1)
    kc.quad_strip(mb, P, mb.material(M_CERAMIC), uv=uv, col=col, uv2=uv2)
    if top_jagged > 0.0:
        # The broken wall's inside, so the open top reads as a hollow shell from above and through the breaks.
        inner = P[-2:].copy()
        inner[..., 0] *= 0.9
        inner[..., 2] *= 0.9
        kc.quad_strip(mb, np.stack([P[-1], inner[-1]]), mb.material(M_CERAMIC), uv=uv[-2:], col=col[-2:],
                      uv2=uv2[-2:])
        down = inner[-1:].copy()
        down[..., 1] -= min(6.0, (y1 - y0) * 0.6)
        kc.quad_strip(mb, np.concatenate([inner[-1:], down]), mb.material(M_DARK), uv=uv[-2:], col=col[-2:],
                      uv2=uv2[-2:], flip=True)


def _gallery(mb: kc.MeshBuilder, y: float, r: float, rng, lod: bool) -> None:
    """A gallery ring: a projecting ledge with its coping, and a band of dark window slits just below it."""
    a = np.linspace(0.0, 2 * math.pi, (48 if not lod else 12) + 1)
    ring = np.stack([np.cos(a) * (r + 0.35), np.full_like(a, y), np.sin(a) * (r + 0.35)], axis=-1)
    kc.tube(mb, ring, 0.32, 6 if not lod else 3, mb.material(M_CERAMIC), weather=WORN,
            variation=float(rng.random()))
    if lod:
        return
    n = max(8, int(2 * math.pi * r / 2.2))
    for k in range(n):
        th = 2 * math.pi * (k + 0.5) / n
        c = np.array([math.cos(th) * (r + 0.02), y - 1.6, math.sin(th) * (r + 0.02)])
        kc.rounded_block(mb, c, (0.03, 0.9, 0.22), mb.material(M_DARK), rot=kc.rot_y(-th), radius=0.01, seg=1)


def _dome(mb: kc.MeshBuilder, y: float, r: float, h: float, rng, noise, lod: bool, finial: bool = True) -> None:
    """A domed cap from radius r at y, rising h, with a ribbed surface and a bronze finial."""
    n = 9 if not lod else 3
    t = np.linspace(0.0, 1.0, n)
    prof = [(max(r * math.cos(tt * math.pi * 0.5) ** 0.8, 0.05), y + h * math.sin(tt * math.pi * 0.5)) for tt in t]
    tmp = kc.MeshBuilder("dome")
    import props  # noqa: PLC0415

    props.lathe(tmp, prof, M_CERAMIC, rng, sides=36 if not lod else 10, noise=None if lod else noise, disp_m=0.04,
                cap_start=False, weather=WORN)
    mb.merge(tmp)
    if finial and not lod:
        kc.tube(mb, np.array([[0.0, y + h - 0.1, 0.0], [0.0, y + h + 3.2, 0.0]]),
                np.array([0.22, 0.05]), 8, mb.material(M_BRONZE), cap_end=True)
        a = np.linspace(0.0, 2 * math.pi, 13)
        ring = np.stack([np.cos(a) * 0.5, np.full_like(a, y + h + 1.4), np.sin(a) * 0.5], axis=-1)
        kc.tube(mb, ring, 0.06, 5, mb.material(M_BRONZE))


def build_tower(kind: str, seed: int) -> list[kc.MeshBuilder]:
    name = "iskarra_tower_" + kind
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        if kind == "spire":
            _shaft(mb, 0.0, 52.0, 6.0, 5.16, rng, noise, lod=lod, waterline=WATERLINE_M)
            for y in np.arange(12.0, 52.0, 9.0):
                _gallery(mb, y, 6.0 - 0.84 * y / 52.0, rng, lod)
            _dome(mb, 52.0, 5.3, 7.0, rng, noise, lod)
        elif kind == "stepped":
            tiers = ((0.0, 20.0, 5.5, 5.2), (20.0, 33.0, 4.4, 4.1), (33.0, 42.0, 3.3, 3.0))
            for y0, y1, r0, r1 in tiers:
                _shaft(mb, y0, y1, r0, r1, rng, noise, lod=lod, waterline=WATERLINE_M if y0 == 0.0 else None)
                _gallery(mb, y1, r1 + 0.2, rng, lod)
                if not lod and y1 < 42.0:
                    # The set-back's flat roof between tiers.
                    a = np.linspace(0.0, 2 * math.pi, 37)
                    grid = np.stack([np.stack([np.cos(a) * r1, np.full_like(a, y1), np.sin(a) * r1], -1),
                                     np.stack([np.cos(a) * (r1 - 1.1), np.full_like(a, y1), np.sin(a) * (r1 - 1.1)], -1)])
                    kc.quad_strip(mb, grid, mb.material(M_CERAMIC), uv=grid[..., [0, 2]], col=np.array([0, 0.3, 0, 0.5]),
                                  uv2=np.array([0.9, 0.5]))
            _dome(mb, 42.0, 3.1, 4.0, rng, noise, lod)
        elif kind == "broken":
            _shaft(mb, 0.0, 40.0, 5.0, 4.3, rng, noise, lod=lod, top_jagged=3.5, waterline=WATERLINE_M)
            for y in (13.0, 24.0):
                _gallery(mb, y, 5.0 - 0.7 * y / 40.0, rng, lod)
        elif kind == "small":
            _shaft(mb, 0.0, 17.0, 3.5, 3.1, rng, noise, lod=lod, waterline=WATERLINE_M)
            _gallery(mb, 10.0, 3.26, rng, lod)
            _gallery(mb, 17.0, 3.1, rng, lod)
            _dome(mb, 17.0, 3.2, 3.6, rng, noise, lod)
        else:  # small_broken
            _shaft(mb, 0.0, 14.0, 3.0, 2.7, rng, noise, lod=lod, top_jagged=1.8, waterline=WATERLINE_M)
            _gallery(mb, 8.5, 2.82, rng, lod)
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


def _paving(mb: kc.MeshBuilder, x0: float, x1: float, z0: float, z1: float, y: float, rng, noise, lod: bool,
            keep=None, slab: float = 1.5) -> None:
    """Paving slabs on a grid, each a separate block with a joint around it, a few sunk or lifted; `keep(x, z)`
    drops slabs (the broken corner). Every fourth row an inlaid ceramic channel."""
    if lod:
        return  # the podium's top stands in for the slabs
    for i, x in enumerate(np.arange(x0 + slab * 0.5, x1, slab)):
        for j, z in enumerate(np.arange(z0 + slab * 0.5, z1, slab)):
            if keep is not None and not keep(x, z):
                continue
            dy = rng.normal(0.0, 0.02) - (0.08 if rng.random() < 0.06 else 0.0)
            mat = mb.material(M_CERAMIC) if j % 4 == 1 and i % 2 == 0 else mb.material(M_PAVING)
            kc.rounded_block(mb, (x, y - 0.15 + dy, z), (slab * 0.5 - 0.03, 0.15, slab * 0.5 - 0.03), mat,
                             rot=kc.rot_y(rng.normal(0.0, 0.01)), radius=0.03, seg=1, noise=noise, disp_m=0.008,
                             weather=WORN, variation=float(rng.random()))


def build_plaza(seed: int = 722, *, w: float = 34.0, d: float = 18.0) -> list[kc.MeshBuilder]:
    hx, hz = w * 0.5, d * 0.5
    out = []
    for lod in (False, True):
        rng = kc.rng_for("iskarra_plaza", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("iskarra_plaza" + ("-lod1" if lod else ""))

        def keep(x, z):  # the back-right corner has fallen into the sea along a ragged line
            return (x - hx * 0.25) * 0.55 + (-z - hz * 0.2) < 6.0 + 1.5 * math.sin(x * 0.9)

        _paving(mb, -hx, hx, -hz, hz - 2.4, 0.0, rng, noise, lod, keep=keep)
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
        out.append(mb)
    return out


def build_plaza_rise(seed: int = 723) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("iskarra_plaza_rise", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("iskarra_plaza_rise" + ("-lod1" if lod else ""))
        kc.rounded_block(mb, (0.0, 0.4, -0.4), (5.0, 0.4, 2.6), mb.material(M_PAVING), radius=0.06,
                         seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.01, weather=WORN)
        for k in range(3 if not lod else 1):
            kc.rounded_block(mb, (0.0, 0.8 - (k + 1) * 0.27 + 0.135, 2.2 + 0.27 * k + 0.135),
                             (4.2, 0.135, 0.15), mb.material(M_PAVING), radius=0.03, seg=1, variation=float(rng.random()))
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
        # The cold head: a bronze cage round a clouded glass globe (dead since the Lit Age).
        import props  # noqa: PLC0415

        ang = np.linspace(-math.pi * 0.5, math.pi * 0.5, 7 if not lod else 3)
        props.lathe(mb, np.stack([np.maximum(np.cos(ang) * 0.36, 0.01), np.sin(ang) * 0.36], -1), M_GLASS, rng,
                    sides=14 if not lod else 6, at=(0.0, 5.85, 0.0), cap_start=False)
        if not lod:
            for k in range(4):
                a = k * math.pi * 0.5
                arc = np.stack([np.cos(a) * np.cos(ang) * 0.39, 5.85 + np.sin(ang) * 0.39, np.sin(a) * np.cos(ang) * 0.39],
                               axis=-1)
                kc.tube(mb, arc, 0.018, 4, mb.material(M_BRONZE))
            kc.tube(mb, np.array([[0.0, 6.2, 0.0], [0.0, 6.55, 0.0]]), np.array([0.06, 0.02]), 6,
                    mb.material(M_BRONZE), cap_end=True)
        out.append(mb)
    return out


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
}
