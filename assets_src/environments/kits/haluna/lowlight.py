"""Lowlight's engine hall (lowlight.md §1-§2; M3-ENV-716): the Lamp Engine's arena and the hall's kit pieces. Pure numpy.

Built in the Haluna kit (its import kind and materials directory, as iskarra.py and keth.py), with `kit_lowlight_*`.

  engine_hall      (arena frame) the hall below the sanctum, 24 x 24 m and 9 m to its vault: the flooded floor at
                   -0.6 (the arena's water at -0.15 over it), a dry stone dais 10.8 x 8.2 m with its top at y 0 (the
                   battle floor), two steps down into the water on every side; eight Lit Age ceramic piers
                   carrying the vault's ribs; the walls (grey stone to the tide line, ceramic above) with tiers of
                   empty lamp niches; the Engine's copper trimming rail round the walls at 3.5 m; the conduit along
                   the cornice; the vault with one bay fallen in behind the enemy line (the grey shaft of daylight)
                   and its rubble in the water; the stair from the sanctum behind the camera.
  conduit_run      a 4 m copper-and-salt-glass light line on brackets, the bound light steady (lowlight.md §0)
  lamp_niche_tier  a tier of six empty glass lamp niches with bronze trim-arms, 4 m (the Engine's work)
  conduit_housing  a copper junction housing on a conduit run (0.56 x 0.4 x 0.26 m), a salt-glass window on the bound
                   light inside, the two runs entering through bolted collars, and stamped in its face the **Saltwright
                   housing-mark** Liss reads (L03): the Saltwrights' circle crossed by three fine lines (their
                   camp-sign, bs_story's chalk_mark) over two small round seats side by side, "pair-built". Rhen's
                   lantern carries the same mark (Character's request). Origin at the back plate's centre, face +Z.

Nothing here is frozen (ADR 0015/0016).
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_CERAMIC = "kit_lowlight_ceramic"
M_STONE = "kit_lowlight_stone"
M_COPPER = "kit_lowlight_copper"
M_CONDUIT = "kit_lowlight_conduit"
M_GLASS = "kit_salt_glass"
M_DARK = "kit_interior_dark"

TRI_BUDGET = {"engine_hall": (34000, 2400), "conduit_run": (1500, 120), "lamp_niche_tier": (3000, 200),
              "conduit_housing": (3000, 120)}

HALL_HALF = 12.0
HALL_H = 9.0
FLOOR_Y = -0.6  # the flooded floor
WATER_Y = -0.15  # the arena's sea in the hall
DAIS = (-4.6, 6.2, -3.4, 4.8)  # x0, x1, z0, z1 of the battle floor's top: the slots' metre clear, off-centre so the
#                               enemy side's steps go down into the water where the Engine stands (ENGINE_AT)
DAIS_STEPS = ((0.9, -0.4), (0.45, -0.2))  # (how far each step runs out from the dais, its top)
ENGINE_AT = (-6.4, FLOOR_Y, -2.6)  # the boss anchor: on the flooded floor past the steps, knee-deep
PIER_AT = ((-8.5, -8.5), (0.0, -9.0), (8.5, -8.5), (-9.0, 0.0), (9.0, 0.0), (-8.5, 8.5), (8.5, 8.5), (0.0, 9.5))
FALLEN_BAY = (-6.0, 0.0, -10.5, -4.5)  # x0, x1, z0, z1 of the vault opening (behind the foes)
RAIL_Y = 3.5
CONDUIT_Y = 8.4
STONE = kc.Weathering(moss=0.2, salt=0.3, wet=0.4, erosion=0.6, noise_scale_m=0.8)
CERAMIC = kc.Weathering(moss=0.25, salt=0.35, wet=0.2, erosion=0.75, noise_scale_m=1.2)


def _slab(mb, x0, x1, z0, z1, y_top, thick, mat, rng, noise, *, flag=None, lod=False):
    """A slab top at y_top; `flag` (min, max) lays it as flags."""
    if flag is None or lod:
        kc.rounded_block(mb, ((x0 + x1) * 0.5, y_top - thick * 0.5, (z0 + z1) * 0.5),
                         ((x1 - x0) * 0.5, thick * 0.5, (z1 - z0) * 0.5), mb.material(mat), radius=0.04, seg=1,
                         weather=STONE, variation=float(rng.random()))
        return
    # The bedding under the flags: the joints read as shallow grooves, never as holes down to the step below.
    kc.rounded_block(mb, ((x0 + x1) * 0.5, y_top - 0.015 - thick * 0.5, (z0 + z1) * 0.5),
                     ((x1 - x0) * 0.5, thick * 0.5, (z1 - z0) * 0.5), mb.material(mat), radius=0.01, seg=1)
    z = z0
    while z < z1 - 0.05:
        w = min(rng.uniform(0.6, 0.9), z1 - z)
        x = x0 + rng.uniform(0.0, 0.4)
        kc.rounded_block(mb, ((x0 + x) * 0.5, y_top - thick * 0.5, z + w * 0.5), (max((x - x0) * 0.5 - 0.01, 0.02),
                         thick * 0.5, w * 0.5 - 0.012), mb.material(mat), radius=0.015, seg=1, weather=STONE)
        while x < x1 - 0.05:
            ln = min(rng.uniform(*flag), x1 - x)
            kc.rounded_block(mb, (x + ln * 0.5, y_top - thick * 0.5 + rng.uniform(-0.006, 0.004), z + w * 0.5),
                             (ln * 0.5 - 0.012, thick * 0.5, w * 0.5 - 0.012), mb.material(mat),
                             rot=kc.rot_y(rng.normal(0.0, 0.006)), radius=0.015, seg=1, noise=noise, disp_m=0.005,
                             weather=STONE, variation=float(rng.random()))
            x += ln
        z += w


def _pier(mb, x, z, rng, noise, lod):
    kc.rounded_block(mb, (x, FLOOR_Y + 0.45, z), (0.85, 0.45, 0.85), mb.material(M_STONE), radius=0.06, seg=1,
                     weather=STONE, variation=float(rng.random()))
    kc.rounded_block(mb, (x, (FLOOR_Y + 0.9 + 7.2) * 0.5, z), (0.62, (7.2 - FLOOR_Y - 0.9) * 0.5, 0.62),
                     mb.material(M_CERAMIC), radius=0.08, seg=1 if lod else 2, noise=None if lod else noise,
                     disp_m=0.02, weather=CERAMIC, variation=float(rng.random()))
    kc.rounded_block(mb, (x, 7.4, z), (0.85, 0.2, 0.85), mb.material(M_STONE), radius=0.05, seg=1, weather=STONE)


def _walls(mb, rng, noise, lod):
    """Four walls: grey stone to 1.2 m over the water (the tide line's algae), ceramic panels above to the cornice."""
    h = HALL_HALF
    for (cx, cz, hx, hz) in ((0.0, -h - 0.4, h + 0.8, 0.4), (0.0, h + 0.4, h + 0.8, 0.4),
                             (-h - 0.4, 0.0, 0.4, h), (h + 0.4, 0.0, 0.4, h)):
        kc.rounded_block(mb, (cx, (FLOOR_Y + 1.2) * 0.5, cz), (hx, (1.2 - FLOOR_Y) * 0.5, hz), mb.material(M_STONE),
                         radius=0.04, seg=1, weather=STONE, variation=float(rng.random()))
        if lod:
            kc.rounded_block(mb, (cx, (1.2 + HALL_H) * 0.5, cz), (hx, (HALL_H - 1.2) * 0.5, hz), mb.material(M_CERAMIC),
                             radius=0.04, seg=1)
            continue
        # Ceramic panels in courses of 1.95 m, each a block a little proud or sunk.
        along_x = hx > hz
        n = int(2 * (hx if along_x else hz) / 2.4)
        for i in range(n):
            for j, y0 in enumerate(np.arange(1.2, HALL_H, 1.95)):
                y1 = min(y0 + 1.95, HALL_H)
                t = -1.0 + (i + 0.5) * 2.0 / n
                px = cx + (t * hx if along_x else 0.0)
                pz = cz + (0.0 if along_x else t * hz)
                half = (hx / n - 0.02, (y1 - y0) * 0.5 - 0.02, hz) if along_x else (hx, (y1 - y0) * 0.5 - 0.02, hz / n - 0.02)
                kc.rounded_block(mb, (px, (y0 + y1) * 0.5, pz), half, mb.material(M_CERAMIC), radius=0.04, seg=1,
                                 noise=noise, disp_m=0.01, weather=CERAMIC, variation=float(rng.random()))


def _niche_tiers(mb, rng, lod):
    """Three tiers of empty lamp niches up the back wall: dark recesses, a clouded glass globe in each, a bronze
    trim-arm over it."""
    if lod:
        return
    face = -HALL_HALF + 0.02
    for y in (2.2, 4.6, 6.6):
        for x in np.arange(-10.0, 10.5, 1.6):
            if FALLEN_BAY[0] - 0.5 < x < FALLEN_BAY[1] + 0.5 and y > 6:
                continue
            kc.rounded_block(mb, (x, y, face + 0.02), (0.32, 0.42, 0.05), mb.material(M_DARK), radius=0.02, seg=1)
            kc.rounded_block(mb, (x, y - 0.12, face + 0.12), (0.13, 0.15, 0.13), mb.material(M_GLASS), radius=0.12, seg=2)
            kc.tube(mb, np.array([[x - 0.3, y + 0.38, face + 0.05], [x, y + 0.32, face + 0.32]]), 0.02, 4,
                    mb.material(M_COPPER))


def build_hall(seed: int = 1601) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("engine_hall", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("engine_hall" + ("-lod1" if lod else ""))
        # The flooded floor, the dais and its steps.
        _slab(mb, -HALL_HALF, HALL_HALF, -HALL_HALF, HALL_HALF, FLOOR_Y, 0.3, M_STONE, rng, noise, lod=True)
        x0, x1, z0, z1 = DAIS
        for grow, top in DAIS_STEPS:
            _slab(mb, x0 - grow, x1 + grow, z0 - grow, z1 + grow, top, top - FLOOR_Y, M_STONE, rng, noise, lod=True)
        _slab(mb, x0, x1, z0, z1, 0.0, 0.6, M_STONE, rng, noise, flag=(0.8, 1.4), lod=lod)
        for x, z in PIER_AT:
            _pier(mb, x, z, rng, noise, lod)
        _walls(mb, rng, noise, lod)
        _niche_tiers(mb, rng, lod)
        # The vault: a ceiling slab with ribs, open over the fallen bay; the fallen ribs' rubble in the water below.
        h = HALL_HALF
        x0, x1, z0, z1 = FALLEN_BAY
        for (a, b, c, d) in ((-h, h, -h, z0), (-h, h, z1, h), (-h, x0, z0, z1), (x1, h, z0, z1)):
            kc.rounded_block(mb, ((a + b) * 0.5, HALL_H + 0.2, (c + d) * 0.5), ((b - a) * 0.5, 0.2, (d - c) * 0.5),
                             mb.material(M_CERAMIC), radius=0.05, seg=1, weather=CERAMIC)
        if not lod:
            for zz in np.arange(-h + 3.0, h, 4.0):  # transverse ribs
                if not (z0 < zz < z1):
                    kc.rounded_block(mb, (0.0, HALL_H - 0.25, zz), (h, 0.25, 0.3), mb.material(M_STONE), radius=0.06,
                                     seg=1, weather=STONE)
                else:  # the broken rib: two stubs either side of the hole
                    for (ra, rb) in ((-h, x0 - 0.3 - rng.uniform(0, 1.0)), (x1 + 0.3 + rng.uniform(0, 1.0), h)):
                        kc.rounded_block(mb, ((ra + rb) * 0.5, HALL_H - 0.25, zz), ((rb - ra) * 0.5, 0.25, 0.3),
                                         mb.material(M_STONE), radius=0.06, seg=1, weather=STONE)
            for k in range(14):
                s = rng.uniform(0.3, 0.9)
                kc.rounded_block(mb, (rng.uniform(x0, x1), FLOOR_Y + s * 0.4, rng.uniform(z0 - 1.0, z1 - 1.5)),
                                 (s, s * 0.5, s * 0.8), mb.material(M_CERAMIC if k % 3 else M_STONE),
                                 rot=kc.rot_y(rng.uniform(0, 3)) @ kc.rot_x(rng.normal(0, 0.3)), radius=s * 0.15,
                                 seg=1, noise=noise, disp_m=0.04, weather=CERAMIC, variation=float(rng.random()))
            # The trimming rail round the walls on its brackets, and the conduit along the cornice.
            for (a, b) in (((-h + 0.5, -h + 0.5), (h - 0.5, -h + 0.5)), ((-h + 0.5, -h + 0.5), (-h + 0.5, h - 2.0)),
                           ((h - 0.5, -h + 0.5), (h - 0.5, h - 2.0))):
                pa = np.array([a[0], RAIL_Y, a[1]])
                pb = np.array([b[0], RAIL_Y, b[1]])
                kc.tube(mb, np.stack([pa, pb]), 0.06, 6, mb.material(M_COPPER))
                n = int(np.linalg.norm(pb - pa) / 2.4)
                for t in np.linspace(0.0, 1.0, n + 1):
                    p = pa + (pb - pa) * t
                    w = np.array([np.sign(p[0]) * 0.5 if abs(abs(p[0]) - (h - 0.5)) < 0.01 else 0.0, 0.0,
                                  -0.5 if abs(p[2] + h - 0.5) < 0.01 else 0.0])
                    kc.tube(mb, np.stack([p, p + w]), 0.04, 4, mb.material(M_COPPER))
                kc.tube(mb, np.stack([pa + [0, CONDUIT_Y - RAIL_Y, 0], pb + [0, CONDUIT_Y - RAIL_Y, 0]]), 0.05, 6,
                        mb.material(M_CONDUIT))
            # The stair from the sanctum, behind the camera, rising south.
            for k in range(8):
                kc.rounded_block(mb, (6.5, -0.4 + 0.2 * (k + 1) - 0.1, 9.0 + 0.32 * k), (1.2, 0.1 + 0.1 * k, 0.17),
                                 mb.material(M_STONE), radius=0.02, seg=1, weather=STONE)
        out.append(mb)
    return out


def build_conduit(seed: int = 1602) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("conduit_run", seed)
        mb = kc.MeshBuilder("conduit_run" + ("-lod1" if lod else ""))
        kc.tube(mb, np.array([[-2.0, 0.0, 0.1], [2.0, 0.0, 0.1]]), 0.06, 4 if lod else 8, mb.material(M_CONDUIT))
        kc.tube(mb, np.array([[-2.0, 0.0, 0.1], [2.0, 0.0, 0.1]]), 0.085, 4 if lod else 8, mb.material(M_GLASS))
        if not lod:
            for x in (-1.6, 0.0, 1.6):
                kc.rounded_block(mb, (x, 0.0, 0.05), (0.06, 0.1, 0.07), mb.material(M_COPPER), radius=0.02, seg=1)
        del rng
        out.append(mb)
    return out


def build_niche_tier(seed: int = 1603) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lamp_niche_tier", seed)
        mb = kc.MeshBuilder("lamp_niche_tier" + ("-lod1" if lod else ""))
        kc.rounded_block(mb, (0.0, 0.6, -0.15), (2.0, 0.6, 0.15), mb.material(M_CERAMIC), radius=0.03, seg=1,
                         weather=CERAMIC, variation=float(rng.random()))
        for x in np.linspace(-1.6, 1.6, 6):
            kc.rounded_block(mb, (x, 0.6, 0.01), (0.22, 0.38, 0.03), mb.material(M_DARK), radius=0.02, seg=1)
            if not lod:
                kc.rounded_block(mb, (x, 0.5, 0.08), (0.11, 0.13, 0.11), mb.material(M_GLASS), radius=0.1, seg=2)
                kc.tube(mb, np.array([[x - 0.22, 0.95, 0.02], [x, 0.9, 0.24]]), 0.015, 4, mb.material(M_COPPER))
        out.append(mb)
    return out


MARK_R = 0.075  # the housing-mark's circle
MARK_RELIEF = 0.003  # stamped proud of the face


def _mark(mb, centre, face_z, lod) -> None:
    """The Saltwright housing-mark, stamped in relief: a circle crossed by three fine parallel lines, and below it
    two small round seats side by side (pair-built)."""
    if lod:
        return
    copper = mb.material(M_COPPER)
    cx, cy = centre
    a = np.linspace(0.0, 2 * math.pi, 33)
    kc.tube(mb, np.stack([cx + np.cos(a) * MARK_R, cy + np.sin(a) * MARK_R, np.full_like(a, face_z + MARK_RELIEF)], -1),
            0.005, 4, copper)
    for k in (-1, 0, 1):  # the lines run corner to corner, slanted 30 degrees, clipped by the circle
        off = k * 0.03
        d = np.array([math.cos(math.radians(30.0)), math.sin(math.radians(30.0))])
        n = np.array([-d[1], d[0]])
        half = math.sqrt(max(MARK_R ** 2 - off ** 2, 0.0)) * 0.96
        p0 = np.array([cx, cy]) + n * off - d * half
        p1 = np.array([cx, cy]) + n * off + d * half
        kc.tube(mb, np.array([[p0[0], p0[1], face_z + MARK_RELIEF], [p1[0], p1[1], face_z + MARK_RELIEF]]), 0.0045, 4,
                copper)
    for sx in (-1.0, 1.0):  # the two seats
        kc.tube(mb, np.array([[cx + sx * 0.03, cy - MARK_R - 0.035, face_z], [cx + sx * 0.03, cy - MARK_R - 0.035,
                                                                             face_z + MARK_RELIEF * 2.0]]),
                0.012, 8, copper, cap_end=True)


def build_housing(seed: int = 1604) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("conduit_housing", seed)
        mb = kc.MeshBuilder("conduit_housing" + ("-lod1" if lod else ""))
        copper = mb.material(M_COPPER)
        hx, hy, hz = 0.28, 0.2, 0.13
        kc.rounded_block(mb, (0.0, 0.0, hz), (hx, hy, hz), copper, radius=0.03, seg=1 if lod else 2,
                         weather=CERAMIC, variation=float(rng.random()))
        face = hz * 2.0
        # The window on the bound light: a salt-glass pane over the conduit's glow, in a copper frame.
        kc.rounded_block(mb, (0.1, 0.02, face - 0.02), (0.1, 0.12, 0.02), mb.material(M_CONDUIT), radius=0.01, seg=1)
        kc.rounded_block(mb, (0.1, 0.02, face + 0.004), (0.11, 0.13, 0.006), mb.material(M_GLASS), radius=0.01, seg=1)
        if not lod:
            for x in (-0.01, 0.21):
                kc.tube(mb, np.array([[x, -0.12, face + 0.01], [x, 0.16, face + 0.01]]), 0.008, 4, copper)
            # Bolted collars where the two runs enter, left and right.
            for sx in (-1.0, 1.0):
                x = sx * (hx + 0.03)
                kc.tube(mb, np.array([[x - sx * 0.03, 0.0, 0.1], [x + sx * 0.03, 0.0, 0.1]]), 0.09, 12, copper,
                        cap_start=True, cap_end=True)
                for k in range(6):
                    a = 2 * math.pi * k / 6
                    kc.rounded_block(mb, (x + sx * 0.035, math.cos(a) * 0.07, 0.1 + math.sin(a) * 0.07),
                                     (0.008, 0.01, 0.01), copper, radius=0.004, seg=1)
        _mark(mb, (-0.14, 0.04), face, lod)
        out.append(mb)
    return out


TARGETS = {"engine_hall": build_hall, "conduit_run": build_conduit, "lamp_niche_tier": build_niche_tier,
           "conduit_housing": build_housing}
