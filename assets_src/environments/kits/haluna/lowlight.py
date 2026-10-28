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

  lowlight_nave_bay         one 8 m bay of the temple's nave (lowlight.md §1), the nave axis along Z: the floor 0.45 m
                            under the lagoon's datum (knee-deep), ceramic piers at x +-6.5, the aisle walls at x +-9
                            with three lamp-niche tiers each, the dry gallery walks at +5.6 and +11.2, the conduit along
                            the cornice, a pointed ribbed vault to 16 m; origin at the bay's centre on the datum (y 0)
  lowlight_nave_bay_broken  the same bay with its vault broken open (the grey sky through it) and the rubble fallen
  well_shaft                the Lit Age well-shaft: a ribbed ceramic drum r 3.5 m dropping 24 m from the sanctum's
                            floor, a spiral stair round its wall, the bronze rim at the mouth; origin at the mouth's
                            centre (y 0 = the sanctum's floor)
  vey_arcade_bay            one bay of a two-storey Lit Age arcade in the Sunken Vey, 6 m along X: grey stone to the
                            first storey's springing (drowned to it), white ceramic above, the arch open on +Z and -Z,
                            a lamp gallery's corbels at +5.6; origin at the bay's centre on the lagoon's datum
  vey_gallery_bridge        a lamp-gallery walk spanning 6 m between two arcades at +5.6: an iron frame, ceramic
                            treads, a rail with a conduit along it; origin at its centre, deck at y 0
  lowlight_sanctum          the sanctum (r 7): a semicircular apse on -Z with a half-dome, three niche tiers and the
                            cornice conduit; the dry floor at y 0 with the well-shaft's mouth (r 3.65) open in its
                            middle; three steps down to the nave (+Z) to its knee-deep floor; origin at the mouth
  strangler_fig             a strangler fig on a 1.2 m square ceramic pier: root strands spiralling down and fusing
                            round the pier from its top (9 m) into the water, a crown of banyan-spray leaf cards (the
                            Haluna banyan's bark and leaf materials; the vegetation wind contract); origin at the pier's
                            foot centre on the datum. The pier itself is the arcade's or the nave's.

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
              "conduit_housing": (3000, 120), "lowlight_nave_bay": (24000, 1500), "well_shaft": (14000, 900),
              "vey_arcade_bay": (12000, 900), "vey_gallery_bridge": (4000, 300), "lowlight_sanctum": (18000, 1200),
              "strangler_fig": (8000, 600), "vey_gallery_walk_6m": (6000, 300), "lowlight_lamp_bench": (2500, 150)}
BUDGET_KEY = {"lowlight_nave_bay_broken": "lowlight_nave_bay"}

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


def _pier_trim(mb, x, z, y0: float, y1: float, half: float, lod: bool) -> None:
    """A pier's articulation (M3-ENV-705 audit: the hall's piers read as plain blocks): a sunk panel on each face
    (a dark reveal in a ceramic frame), a copper conduit band a third of the way up, and a stepped capital."""
    if lod:
        return
    dark, copper, cer = mb.material(M_DARK), mb.material(M_COPPER), mb.material(M_CERAMIC)
    h = y1 - y0
    for nx, nz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        c = (x + nx * (half + 0.004), y0 + h * 0.55, z + nz * (half + 0.004))
        hs = (0.006, h * 0.28, half * 0.55) if nx else (half * 0.55, h * 0.28, 0.006)
        kc.rounded_block(mb, c, hs, dark, radius=0.0, seg=1)
    band_y = y0 + h * 0.3
    kc.rounded_block(mb, (x, band_y, z), (half + 0.05, 0.09, half + 0.05), copper, radius=0.02, seg=1)
    for k, (dy, grow) in enumerate(((0.0, 0.08), (0.16, 0.16))):
        kc.rounded_block(mb, (x, y1 - 0.1 + dy, z), (half + grow, 0.08, half + grow), cer, radius=0.02, seg=1)


def _pier(mb, x, z, rng, noise, lod):
    kc.rounded_block(mb, (x, FLOOR_Y + 0.45, z), (0.85, 0.45, 0.85), mb.material(M_STONE), radius=0.06, seg=1,
                     weather=STONE, variation=float(rng.random()))
    kc.rounded_block(mb, (x, (FLOOR_Y + 0.9 + 7.2) * 0.5, z), (0.62, (7.2 - FLOOR_Y - 0.9) * 0.5, 0.62),
                     mb.material(M_CERAMIC), radius=0.08, seg=1 if lod else 2, noise=None if lod else noise,
                     disp_m=0.02, weather=CERAMIC, variation=float(rng.random()))
    kc.rounded_block(mb, (x, 7.4, z), (0.85, 0.2, 0.85), mb.material(M_STONE), radius=0.05, seg=1, weather=STONE)
    _pier_trim(mb, x, z, FLOOR_Y + 0.9, 7.2, 0.62, lod)


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


# ---------------------------------------------------------------------------------------------
# The temple and the Vey (lowlight.md §1)
# ---------------------------------------------------------------------------------------------
NAVE_FLOOR_Y = -0.45
GALLERY_Y = (5.6, 11.2)
NAVE_BAY = 8.0
NAVE_HALF_W = 9.0
NAVE_PIER_X = 6.5
NAVE_VAULT_Y = (11.8, 16.0)  # springing, crown


def _pointed_arch(half_w: float, y0: float, y1: float, n: int) -> np.ndarray:
    """(x, y) points of a pointed (two-centred) arch from -half_w to +half_w, springing at y0, crown at y1."""
    t = np.linspace(-1.0, 1.0, n)
    return np.stack([t * half_w, y0 + (y1 - y0) * (1.0 - np.abs(t) ** 1.6) ** 0.62], -1)


def build_nave_bay(seed: int = 1605, *, broken: bool = False) -> list[kc.MeshBuilder]:
    out = []
    hz = NAVE_BAY * 0.5
    for lod in (False, True):
        rng = kc.rng_for("lowlight_nave_bay", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(("lowlight_nave_bay_broken" if broken else "lowlight_nave_bay") + ("-lod1" if lod else ""))
        stone, ceramic = mb.material(M_STONE), mb.material(M_CERAMIC)
        # The floor (under the water) and the aisle walls.
        _slab(mb, -NAVE_HALF_W, NAVE_HALF_W, -hz, hz, NAVE_FLOOR_Y, 0.4, M_STONE, rng, noise, lod=True)
        for sx in (-1.0, 1.0):
            x = sx * (NAVE_HALF_W + 0.4)
            kc.rounded_block(mb, (x, (NAVE_FLOOR_Y + 1.0) * 0.5, 0.0), (0.4, (1.0 - NAVE_FLOOR_Y) * 0.5, hz), stone,
                             radius=0.04, seg=1, weather=STONE, variation=float(rng.random()))
            kc.rounded_block(mb, (x, (1.0 + NAVE_VAULT_Y[0]) * 0.5, 0.0), (0.4, (NAVE_VAULT_Y[0] - 1.0) * 0.5, hz),
                             ceramic, radius=0.04, seg=1, noise=None if lod else noise, disp_m=0.01, weather=CERAMIC,
                             variation=float(rng.random()))
            # The two gallery walks (ledges on corbels) and the niche tiers between them.
            for gy in GALLERY_Y:
                kc.rounded_block(mb, (sx * (NAVE_HALF_W - 0.75), gy - 0.12, 0.0), (0.75, 0.12, hz), stone, radius=0.03,
                                 seg=1, weather=STONE)
                if not lod:
                    for z in np.linspace(-hz + 0.6, hz - 0.6, 5):
                        kc.rounded_block(mb, (sx * (NAVE_HALF_W - 0.3), gy - 0.45, z), (0.3, 0.2, 0.18), stone,
                                         radius=0.04, seg=1, weather=STONE)
                    kc.tube(mb, np.array([[sx * (NAVE_HALF_W - 1.45), gy + 0.9, -hz], [sx * (NAVE_HALF_W - 1.45),
                                                                                      gy + 0.9, hz]]),
                            0.03, 5, mb.material(M_COPPER))  # the gallery's rail
            if not lod:
                for gy in (2.2, 3.8, 7.4, 9.0):
                    for z in np.arange(-hz + 0.8, hz, 1.6):
                        face = sx * NAVE_HALF_W
                        kc.rounded_block(mb, (face, gy, z), (0.05, 0.42, 0.32), mb.material(M_DARK), radius=0.02,
                                         seg=1)
                        kc.rounded_block(mb, (face - sx * 0.1, gy - 0.12, z), (0.13, 0.15, 0.13), mb.material(M_GLASS),
                                         radius=0.12, seg=2)
                        kc.tube(mb, np.array([[face, gy + 0.38, z - 0.3], [face - sx * 0.32, gy + 0.32, z]]), 0.02, 4,
                                mb.material(M_COPPER))
                kc.tube(mb, np.array([[sx * (NAVE_HALF_W - 0.1), NAVE_VAULT_Y[0] - 0.3, -hz],
                                      [sx * (NAVE_HALF_W - 0.1), NAVE_VAULT_Y[0] - 0.3, hz]]), 0.06, 6,
                        mb.material(M_CONDUIT))
        # The piers (ceramic over a stone base, standing in the water).
        for sx in (-1.0, 1.0):
            for z in (-hz, hz):
                _pier_at(mb, sx * NAVE_PIER_X, z, rng, noise, lod)
        # The vault: transverse ribs at the bay's ends, the pointed barrel between them (broken open on variant b).
        n = 9 if lod else 25
        prof = _pointed_arch(NAVE_HALF_W + 0.4, NAVE_VAULT_Y[0], NAVE_VAULT_Y[1], n)
        zs = np.linspace(-hz, hz, 3 if lod else 9)
        hole = (lambda x, z: (abs(x) < 3.2) & (abs(z) < 2.6)) if broken else (lambda x, z: False)
        grid = np.stack([np.stack([prof[:, 0], prof[:, 1] + 0.3, np.full(n, z)], -1) for z in zs], 1)
        keep_tris_from = mb.triangle_count
        kc.quad_strip(mb, grid, ceramic, uv=grid[..., [0, 2]] / 2.0, col=(0, 0, 0, 0.6), uv2=(0.7, 0.5), flip=True)
        if broken:
            pos = np.asarray(mb.pos)
            tris = np.asarray(mb.tris[keep_tris_from:])
            cen = pos[tris].mean(axis=1)
            keep = ~hole(cen[:, 0], cen[:, 2]) | (cen[:, 1] < NAVE_VAULT_Y[1] - 1.6)
            mb.tris = mb.tris[:keep_tris_from] + [t for t, k in zip(mb.tris[keep_tris_from:], keep) if k]
            mb.tri_mat = mb.tri_mat[:keep_tris_from] + [m for m, k in zip(mb.tri_mat[keep_tris_from:], keep) if k]
        for z in (-hz, hz):
            pts = np.stack([prof[:, 0] * 0.98, prof[:, 1], np.full(n, z)], -1)
            kc.tube(mb, pts, 0.28, 4 if lod else 6, stone)
        if broken and not lod:
            for _k in range(10):
                sc = rng.uniform(0.3, 0.8)
                kc.rounded_block(mb, (rng.uniform(-3.0, 3.0), NAVE_FLOOR_Y + sc * 0.4, rng.uniform(-2.5, 2.5)),
                                 (sc, sc * 0.4, sc * 0.7), ceramic,
                                 rot=kc.rot_y(rng.uniform(0, 3)) @ kc.rot_x(rng.normal(0, 0.3)), radius=sc * 0.15, seg=1,
                                 noise=noise, disp_m=0.03, weather=CERAMIC, variation=float(rng.random()))
        out.append(mb)
    return out


def _pier_at(mb, x, z, rng, noise, lod) -> None:
    kc.rounded_block(mb, (x, NAVE_FLOOR_Y + 0.55, z), (0.8, 0.55, 0.8), mb.material(M_STONE), radius=0.06, seg=1,
                     weather=STONE, variation=float(rng.random()))
    top = NAVE_VAULT_Y[0]
    kc.rounded_block(mb, (x, (NAVE_FLOOR_Y + 1.1 + top) * 0.5, z), (0.58, (top - NAVE_FLOOR_Y - 1.1) * 0.5, 0.58),
                     mb.material(M_CERAMIC), radius=0.08, seg=1 if lod else 2, noise=None if lod else noise,
                     disp_m=0.02, weather=CERAMIC, variation=float(rng.random()))
    kc.rounded_block(mb, (x, top + 0.18, z), (0.8, 0.18, 0.8), mb.material(M_STONE), radius=0.05, seg=1, weather=STONE)
    _pier_trim(mb, x, z, NAVE_FLOOR_Y + 1.1, top, 0.58, lod)


WELL_R = 3.5
WELL_DEPTH = 24.0


def build_well_shaft(seed: int = 1606) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("well_shaft", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("well_shaft" + ("-lod1" if lod else ""))
        ceramic, stone, copper = mb.material(M_CERAMIC), mb.material(M_STONE), mb.material(M_COPPER)
        # The drum (inside faces), ribbed every 30 degrees.
        sides = 16 if lod else 48
        a = np.linspace(0.0, 2 * math.pi, sides + 1)
        ys = np.linspace(-WELL_DEPTH, 0.0, 5 if lod else 25)
        A, Y = np.meshgrid(a, ys)
        R = WELL_R + 0.05 * np.sin(A * 12.0) * (0.0 if lod else 1.0)
        grid = np.stack([np.cos(A) * R, Y, np.sin(A) * R], -1)
        kc.quad_strip(mb, grid, ceramic, uv=np.stack([A * WELL_R, Y], -1) / 2.0, col=(0, 0, 0, 0.6), uv2=(0.6, 0.5))
        if not lod:
            for k in range(12):
                th = 2 * math.pi * k / 12
                kc.tube(mb, np.array([[math.cos(th) * (WELL_R - 0.1), y, math.sin(th) * (WELL_R - 0.1)]
                                      for y in (-WELL_DEPTH, 0.0)]), 0.12, 5, stone)
        # The spiral stair: treads cantilevered from the wall, 4 turns over the depth, a copper rail on the open side.
        n_steps = 40 if lod else 120
        rail = []
        for k in range(n_steps):
            t = k / n_steps
            th = t * 4.0 * 2 * math.pi
            y = -t * WELL_DEPTH
            d = np.array([math.cos(th), 0.0, math.sin(th)])
            side = np.array([-d[2], 0.0, d[0]])
            c = d * (WELL_R - 0.7) + np.array([0.0, y, 0.0])
            kc.rounded_block(mb, c, (0.6, 0.06, 0.3), stone, rot=kc.rot_y(-th), radius=0.02, seg=1,
                             weather=STONE, variation=float(rng.random()))
            rail.append(d * (WELL_R - 1.35) + np.array([0.0, y + 0.95, 0.0]))
            del side
        if not lod:
            kc.tube(mb, np.array(rail), 0.025, 5, copper)
        # The bronze rim at the mouth, and the deep's upwelling at the foot (the bound light sifting down is VFX).
        a = np.linspace(0.0, 2 * math.pi, 49 if not lod else 17)
        kc.tube(mb, np.stack([np.cos(a) * (WELL_R + 0.15), np.full_like(a, 0.06), np.sin(a) * (WELL_R + 0.15)], -1), 0.12,
                6 if not lod else 4, copper)
        kc.tube(mb, np.array([[0.0, -WELL_DEPTH - 0.2, 0.0], [0.0, -WELL_DEPTH, 0.0]]), WELL_R, 24 if not lod else 8,
                mb.material(M_DARK), cap_end=True)
        del noise
        out.append(mb)
    return out


ARCADE_BAY = 6.0
ARCADE_SPRING_Y = 3.4  # the first storey's springing: the lagoon drowns the bay to here
ARCADE_TOP_Y = 12.0


def build_arcade_bay(seed: int = 1607) -> list[kc.MeshBuilder]:
    out = []
    hx, hz = ARCADE_BAY * 0.5, 2.0
    for lod in (False, True):
        rng = kc.rng_for("vey_arcade_bay", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("vey_arcade_bay" + ("-lod1" if lod else ""))
        stone, ceramic = mb.material(M_STONE), mb.material(M_CERAMIC)
        # Two piers (one per bay end), grey stone under the water and to the first springing, ceramic above.
        for sx in (-1.0, 1.0):
            x = sx * (hx - 0.55)
            kc.rounded_block(mb, (x, (-4.0 + ARCADE_SPRING_Y) * 0.5, 0.0), (0.55, (ARCADE_SPRING_Y + 4.0) * 0.5, hz),
                             stone, radius=0.05, seg=1, noise=None if lod else noise, disp_m=0.02, weather=STONE,
                             variation=float(rng.random()))
            kc.rounded_block(mb, (x, (ARCADE_SPRING_Y + ARCADE_TOP_Y) * 0.5, 0.0),
                             (0.55, (ARCADE_TOP_Y - ARCADE_SPRING_Y) * 0.5, hz), ceramic, radius=0.05, seg=1,
                             noise=None if lod else noise, disp_m=0.015, weather=CERAMIC, variation=float(rng.random()))
        # The two storeys' arches, open through the bay (+Z and -Z faces), and the spandrel walls over them.
        for y0, y1, w in ((ARCADE_SPRING_Y, 5.4, hx - 1.1), (7.2, 10.2, hx - 1.1)):
            prof = _pointed_arch(w, y0, y1, 7 if lod else 17)
            for z in (-hz, hz):
                kc.tube(mb, np.stack([prof[:, 0], prof[:, 1], np.full(len(prof), z)], -1), 0.18, 4 if lod else 6,
                        ceramic)
                # the spandrel: a slab from the arch's line up to the next storey's floor
                top = y1 + 0.3 if y1 < 6 else ARCADE_TOP_Y
                for k in range(len(prof) - 1):
                    a, b = prof[k], prof[k + 1]
                    grid = np.array([[[a[0], a[1], z], [b[0], b[1], z]], [[a[0], top, z], [b[0], top, z]]])
                    kc.quad_strip(mb, grid, ceramic, uv=grid[..., [0, 1]] / 2.0, col=(0, 0, 0, 0.6), uv2=(0.8, 0.5),
                                  flip=z > 0, smooth=False)
            # the storey's floor (the vault over the arch, flat-topped)
            kc.rounded_block(mb, (0.0, y1 + 0.5, 0.0), (hx - 1.1, 0.2, hz), stone, radius=0.03, seg=1, weather=STONE)
        # The lamp gallery's corbels at +5.6 on the +Z face, and the cornice with its conduit.
        if not lod:
            for x in np.linspace(-hx + 1.4, hx - 1.4, 4):
                kc.rounded_block(mb, (x, GALLERY_Y[0] - 0.3, hz + 0.3), (0.18, 0.25, 0.3), stone, radius=0.04, seg=1,
                                 weather=STONE)
            kc.tube(mb, np.array([[-hx, ARCADE_TOP_Y - 0.35, hz + 0.12], [hx, ARCADE_TOP_Y - 0.35, hz + 0.12]]), 0.06, 6,
                    mb.material(M_CONDUIT))
        kc.rounded_block(mb, (0.0, ARCADE_TOP_Y + 0.2, 0.0), (hx, 0.2, hz + 0.2), stone, radius=0.04, seg=1,
                         weather=STONE)
        out.append(mb)
    return out


def build_gallery_bridge(seed: int = 1608) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("vey_gallery_bridge", seed)
        mb = kc.MeshBuilder("vey_gallery_bridge" + ("-lod1" if lod else ""))
        iron, ceramic = mb.material(M_COPPER), mb.material(M_CERAMIC)
        hw = 0.9
        for sz in (-1.0, 1.0):  # the two stringers, a shallow arch
            t = np.linspace(-1.0, 1.0, 5 if lod else 13)
            kc.tube(mb, np.stack([t * 3.0, -0.12 + 0.18 * (1.0 - t ** 2), np.full_like(t, sz * hw)], -1), 0.06,
                    4 if lod else 6, iron)
            if not lod:
                kc.tube(mb, np.stack([t * 3.0, 1.0 + 0.18 * (1.0 - t ** 2), np.full_like(t, sz * hw)], -1), 0.025, 5,
                        iron)
                for x in np.linspace(-3.0, 3.0, 9):
                    y = 0.18 * (1.0 - (x / 3.0) ** 2)
                    kc.tube(mb, np.array([[x, y - 0.1, sz * hw], [x, y + 1.0, sz * hw]]), 0.02, 4, iron)
        n = 6 if lod else 18
        for k in range(n):  # the treads
            x = -3.0 + 6.0 * (k + 0.5) / n
            y = 0.18 * (1.0 - (x / 3.0) ** 2)
            kc.rounded_block(mb, (x, y - 0.03, 0.0), (3.0 / n - 0.015, 0.03, hw - 0.05), ceramic, radius=0.01, seg=1,
                             weather=CERAMIC, variation=float(rng.random()))
        if not lod:
            t = np.linspace(-1.0, 1.0, 13)
            kc.tube(mb, np.stack([t * 3.0, 1.06 + 0.18 * (1.0 - t ** 2), np.full_like(t, hw)], -1), 0.03, 6,
                    mb.material(M_CONDUIT))
        out.append(mb)
    return out


SANCTUM_R = 7.0
SANCTUM_H = 9.0


def build_sanctum(seed: int = 1609) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lowlight_sanctum", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("lowlight_sanctum" + ("-lod1" if lod else ""))
        stone, ceramic = mb.material(M_STONE), mb.material(M_CERAMIC)
        # The floor: an annulus of laid stone round the well's mouth, out to the apse wall (and square on +Z).
        n_a = 24 if lod else 64
        a = np.linspace(0.0, 2 * math.pi, n_a + 1)
        r_in, r_out = WELL_R + 0.15, SANCTUM_R
        inner = np.stack([np.cos(a) * r_in, np.zeros_like(a), np.sin(a) * r_in], -1)
        outer = np.stack([np.cos(a) * r_out, np.zeros_like(a), np.sin(a) * r_out], -1)
        front = np.sin(a) > 0.0  # the +Z half meets the square front, out to its corners
        sq = r_out / np.maximum(np.abs(np.cos(a)), np.abs(np.sin(a)))
        outer[front] = np.stack([np.cos(a) * sq, np.zeros_like(a), np.sin(a) * sq], -1)[front]
        ring = np.stack([inner, outer], 1)
        kc.quad_strip(mb, ring, stone, uv=ring[..., [0, 2]] / 1.2, col=(0, 0, 0, 0.5), uv2=(0.8, 0.5), flip=True)
        # The apse: a half-cylinder wall on -Z to the springing, and a half-dome over it.
        half = np.linspace(math.pi, 2 * math.pi, (12 if lod else 33))
        ys = np.linspace(0.0, SANCTUM_H * 0.6, 3 if lod else 9)
        A, Y = np.meshgrid(half, ys)
        wall = np.stack([np.cos(A) * SANCTUM_R, Y, np.sin(A) * SANCTUM_R], -1)
        kc.quad_strip(mb, wall, ceramic, uv=np.stack([A * SANCTUM_R, Y], -1) / 2.0, col=(0, 0, 0, 0.6), uv2=(0.7, 0.5))
        el = np.linspace(0.0, math.pi * 0.5, 5 if lod else 13)
        A, E = np.meshgrid(half, el)
        y0 = SANCTUM_H * 0.6
        dome = np.stack([np.cos(A) * np.cos(E) * SANCTUM_R, y0 + np.sin(E) * SANCTUM_H * 0.4,
                         np.sin(A) * np.cos(E) * SANCTUM_R], -1)
        kc.quad_strip(mb, dome, ceramic, uv=np.stack([A * SANCTUM_R, E * SANCTUM_R], -1) / 2.0, col=(0, 0, 0, 0.6),
                      uv2=(0.6, 0.5))
        # The apse's arch toward the nave, and the side walls closing the square front (+Z).
        prof = _pointed_arch(SANCTUM_R, y0, SANCTUM_H + 0.6, 7 if lod else 17)
        kc.tube(mb, np.stack([prof[:, 0], prof[:, 1], np.zeros(len(prof))], -1), 0.35, 4 if lod else 6, stone)
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * (SANCTUM_R + 0.4), SANCTUM_H * 0.5, SANCTUM_R * 0.5),
                             (0.4, SANCTUM_H * 0.5, SANCTUM_R * 0.5), ceramic, radius=0.05, seg=1,
                             noise=None if lod else noise, disp_m=0.01, weather=CERAMIC, variation=float(rng.random()))
        # Three steps down from the sanctum's floor to the nave's knee-deep floor (+Z edge).
        for k in range(3):
            y = -(k + 1) * 0.15
            kc.rounded_block(mb, (0.0, y - 0.15, SANCTUM_R + 0.25 + 0.4 * k), (SANCTUM_R - 0.6, 0.15, 0.2), stone,
                             radius=0.02, seg=1, weather=STONE, variation=float(rng.random()))
        if not lod:
            # The niche tiers round the apse, and the cornice's conduit.
            for gy in (1.8, 3.4, 5.0):
                for th in np.linspace(math.pi + 0.25, 2 * math.pi - 0.25, 11):
                    d = np.array([math.cos(th), 0.0, math.sin(th)])
                    c = d * (SANCTUM_R - 0.03) + np.array([0.0, gy, 0.0])
                    kc.rounded_block(mb, c, (0.3, 0.4, 0.05), mb.material(M_DARK), rot=kc.rot_y(-th - math.pi * 0.5),
                                     radius=0.02, seg=1)
                    kc.rounded_block(mb, c - d * 0.12 + np.array([0.0, -0.12, 0.0]), (0.12, 0.14, 0.12),
                                     mb.material(M_GLASS), radius=0.11, seg=2)
            cor = np.stack([np.cos(half) * (SANCTUM_R - 0.12), np.full_like(half, y0 - 0.3),
                            np.sin(half) * (SANCTUM_R - 0.12)], -1)
            kc.tube(mb, cor, 0.06, 6, mb.material(M_CONDUIT))
        out.append(mb)
    return out


FIG_TOP = 9.0
FIG_HALF = 0.62  # the pier's half width plus the roots' clearance


def _square_ring(t: np.ndarray, half: float) -> np.ndarray:
    """A point at parameter t (0..4 round) on a square of half-size `half` with rounded corners, in (x, z)."""
    t = t % 4.0
    side = np.floor(t).astype(int)
    f = t - side
    pts = np.zeros((len(t), 2))
    corners = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], float) * half
    for k in range(4):
        m = side == k
        pts[m] = corners[k] + (corners[(k + 1) % 4] - corners[k]) * f[m, None]
    r = np.linalg.norm(pts, axis=1, keepdims=True)
    return pts / r * (0.55 * r + 0.45 * half * 1.25)  # rounded toward a circle


def build_strangler_fig(seed: int = 1610) -> list[kc.MeshBuilder]:
    import ossa_fen  # noqa: PLC0415  (the tree helpers: wind weights, leaf clusters)

    out = []
    for lod in (False, True):
        rng = kc.rng_for("strangler_fig", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("strangler_fig" + ("-lod1" if lod else ""))
        root, bark = mb.material("kit_banyan_root"), mb.material("kit_banyan_bark")
        start = mb.vertex_count
        # Root strands: each starts at the pier's top and spirals down round it, fusing with its neighbours.
        n_strands = 7 if lod else 16
        for k in range(n_strands):
            t0 = 4.0 * k / n_strands + rng.uniform(0.0, 0.2)
            turns = rng.uniform(0.3, 0.9) * (1 if rng.random() < 0.6 else -1)
            ys = np.linspace(FIG_TOP, -0.4, 6 if lod else 18)
            tt = t0 + turns * 4.0 * (FIG_TOP - ys) / FIG_TOP
            xz = _square_ring(tt, FIG_HALF + rng.uniform(0.0, 0.08))
            pts = np.stack([xz[:, 0], ys, xz[:, 1]], -1)
            radii = np.linspace(0.05, 0.12, len(ys)) * rng.uniform(0.7, 1.3)
            kc.tube(mb, pts, radii, 4 if lod else 6, root, noise=None if lod else noise, disp_m=0.01,
                    v_scale=1.0 / 1.4, u_repeat=2.0)
        # A few cross-ties fusing the strands (the lattice a strangler makes).
        if not lod:
            for _k in range(10):
                y = rng.uniform(1.0, FIG_TOP - 1.0)
                t = rng.uniform(0.0, 4.0)
                xz = _square_ring(np.array([t, t + rng.uniform(0.4, 0.9)]), FIG_HALF + 0.03)
                kc.tube(mb, np.array([[xz[0, 0], y, xz[0, 1]], [xz[1, 0], y + rng.normal(0, 0.3), xz[1, 1]]]), 0.05, 5,
                        root)
        ossa_fen._wind(mb, start, FIG_TOP + 3.0, sway=False)
        # The crown: limbs leaving the pier's top, leaf clusters at their ends.
        start = mb.vertex_count
        ends: list = []
        top = np.array([0.0, FIG_TOP, 0.0])
        for k in range(4):
            th = 2 * math.pi * (k + rng.uniform(0.0, 0.5)) / 4
            ossa_fen._bough(mb, rng, noise, top, np.array([math.cos(th), 0.7, math.sin(th)]), rng.uniform(1.2, 1.8), 0.12,
                            1, bark, ends, lod=lod, bare=False)
        ossa_fen._wind(mb, start, FIG_TOP + 3.0, phase=0.2)
        for k, (e, d) in enumerate(ends):
            ossa_fen._leaf_cluster(mb, rng, e + d * 0.15, 5 if lod else 12, 0.7, FIG_TOP + 3.0, phase=k * 0.11)
        # The cluster cards use the fen's leaf material; the fig takes the banyan's.
        leaf_fen = mb.materials.index(ossa_fen.M_LEAF)
        mb.materials[leaf_fen] = "kit_banyan_leaf"
        out.append(mb)
    return out



# ---------------------------------------------------------------------------------------------
# M3-ENV-735: the Sunken Vey's gallery walks and Lowlight's lamp bench (act1-chapters' Ch11 greybox, M4-C11-02)
# ---------------------------------------------------------------------------------------------
WALK_HALF_W = 1.8
WALK_RAIL_Z = 2.0
WALK_RAIL_H = 0.5


def build_gallery_walk(seed: int = 1611) -> list[kc.MeshBuilder]:
    """A gallery walk on the drowned arcades' roofs (the greybox's GalleryIn*, GalleryOut*, GallerySide: 3.6 m, its
    top at y 0, rails 0.5 m at z +-2.0), 6 m along X: ceramic slabs on the arcade's top course, a cornice under them,
    a ceramic balustrade along each side, and on each side the arcade's upper arch dropping into the lagoon (its
    spandrels white ceramic, its piers grey stone, drowned at -2). The greybox's pillars beside it are
    `ruin_column_broken`."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("vey_gallery_walk_6m", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("vey_gallery_walk_6m" + ("-lod1" if lod else ""))
        cer, stone = mb.material(M_CERAMIC), mb.material(M_STONE)
        hl = 3.0
        if lod:
            kc.rounded_block(mb, (0.0, -0.15, 0.0), (hl, 0.15, WALK_HALF_W + 0.2), cer, radius=0.03, seg=1)
            kc.rounded_block(mb, (0.0, -1.3, 0.0), (hl, 1.0, WALK_HALF_W), stone, radius=0.05, seg=1)
            for sz in (-1.0, 1.0):
                kc.rounded_block(mb, (0.0, WALK_RAIL_H * 0.5, sz * WALK_RAIL_Z), (hl, WALK_RAIL_H * 0.5, 0.15), cer,
                                 radius=0.03, seg=1)
            out.append(mb)
            continue
        # The slabs: 1.2 m squares in two rows, a joint round each, a few lifted or cracked.
        for x in np.arange(-hl + 0.6, hl, 1.2):
            for z in (-0.9, 0.9):
                dy = rng.normal(0.0, 0.006) + (0.015 if rng.random() < 0.08 else 0.0)
                v0 = mb.vertex_count
                kc.rounded_block(mb, (x, -0.06 + dy, z), (0.585, 0.06, 0.885), cer, rot=kc.rot_y(rng.normal(0, 0.006)),
                                 radius=0.015, seg=1, noise=noise, disp_m=0.003, weather=CERAMIC,
                                 variation=float(rng.random()))
                n = np.asarray(mb.nrm[v0:])
                n[n[:, 1] > 0.85] = (0.0, 1.0, 0.0)  # flat-shaded tops (no pillows)
                mb.nrm[v0:] = n.tolist()
        # The cornice under the slabs and the arcade's top course.
        for sz in (-1.0, 1.0):
            kc.rounded_block(mb, (0.0, -0.18, sz * (WALK_HALF_W + 0.1)), (hl, 0.08, 0.16), cer, radius=0.02, seg=1,
                             weather=CERAMIC)
            kc.rounded_block(mb, (0.0, -0.45, sz * (WALK_HALF_W - 0.05)), (hl, 0.2, 0.22), stone, radius=0.03, seg=1,
                             noise=noise, disp_m=0.01, weather=STONE)
        # The balustrade: a plinth, balusters and a coping rail at z +-2.0.
        for sz in (-1.0, 1.0):
            zr = sz * WALK_RAIL_Z
            kc.rounded_block(mb, (0.0, 0.05, zr), (hl, 0.05, 0.16), cer, radius=0.015, seg=1, weather=CERAMIC)
            kc.rounded_block(mb, (0.0, WALK_RAIL_H - 0.05, zr), (hl, 0.05, 0.18), cer, radius=0.02, seg=1,
                             weather=CERAMIC)
            for x in np.arange(-hl + 0.2, hl, 0.4):
                if rng.random() < 0.08:
                    continue  # a baluster lost
                kc.tube(mb, np.array([[x, 0.1, zr], [x, WALK_RAIL_H - 0.1, zr]]), np.array([0.05, 0.035]), 6, cer,
                        weather=CERAMIC)
        # The arcade's upper arch on each side, its crown under the walk, its piers into the water at -2.
        for sz in (-1.0, 1.0):
            zf = sz * (WALK_HALF_W + 0.05)
            t = np.linspace(0.0, math.pi, 13)
            arch = np.stack([np.cos(t) * 2.2, -0.65 - (1.0 - np.sin(t)) * 1.35, np.full_like(t, zf)], -1)
            kc.tube(mb, arch, 0.14, 6, cer, weather=CERAMIC)  # the arch's moulded ring
            for sx in (-1.0, 1.0):
                kc.rounded_block(mb, (sx * 2.65, -1.4, zf), (0.35, 0.9, 0.25), stone, radius=0.04, seg=1, noise=noise,
                                 disp_m=0.01, weather=STONE)  # the piers, drowned
                # the spandrel between the arch's ring and the top course
                kc.rounded_block(mb, (sx * 2.3, -0.75, zf), (0.6, 0.12, 0.22), cer, radius=0.02, seg=1,
                                 weather=CERAMIC)
        out.append(mb)
    return out


def build_lamp_bench(seed: int = 1612) -> list[kc.MeshBuilder]:
    """Lowlight's lamp bench in the atrium (the greybox's LampBench, 2.4 x 0.9 x 1.0: Rhen and Liss's side scene): a
    ceramic bench on two stone ends against the wall, a row of three empty glass lamp housings on its back ledge with
    bronze trim-arms, the conduit's copper running under it."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lowlight_lamp_bench", seed)
        mb = kc.MeshBuilder("lowlight_lamp_bench" + ("-lod1" if lod else ""))
        cer, stone, cu = mb.material(M_CERAMIC), mb.material(M_STONE), mb.material(M_COPPER)
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * 1.05, 0.22, 0.0), (0.15, 0.22, 0.35), stone, radius=0.03, seg=1, weather=STONE)
        kc.rounded_block(mb, (0.0, 0.47, 0.0), (1.2, 0.05, 0.4), cer, radius=0.02, seg=1, weather=CERAMIC)
        kc.rounded_block(mb, (0.0, 0.75, -0.4), (1.2, 0.3, 0.08), cer, radius=0.02, seg=1, weather=CERAMIC)  # the back
        kc.rounded_block(mb, (0.0, 1.08, -0.38), (1.2, 0.03, 0.12), cer, radius=0.01, seg=1)  # the ledge
        if not lod:
            for x in (-0.7, 0.0, 0.7):
                kc.tube(mb, np.array([[x, 1.11, -0.38], [x, 1.3, -0.38]]), np.array([0.07, 0.06]), 8,
                        mb.material(M_GLASS), cap_end=True)
                kc.tube(mb, np.array([[x - 0.09, 1.11, -0.38], [x - 0.09, 1.34, -0.38], [x + 0.09, 1.34, -0.38],
                                      [x + 0.09, 1.11, -0.38]]), 0.008, 4, cu)
            kc.tube(mb, np.array([[-1.2, 0.3, -0.42], [1.2, 0.3, -0.42]]), 0.03, 6, cu)
        del rng
        out.append(mb)
    return out

TARGETS = {"engine_hall": build_hall, "conduit_run": build_conduit, "lamp_niche_tier": build_niche_tier,
           "conduit_housing": build_housing, "lowlight_nave_bay": build_nave_bay,
           "lowlight_nave_bay_broken": lambda: build_nave_bay(broken=True), "well_shaft": build_well_shaft,
           "vey_arcade_bay": build_arcade_bay, "vey_gallery_bridge": build_gallery_bridge,
           "lowlight_sanctum": build_sanctum, "strangler_fig": build_strangler_fig,
           "vey_gallery_walk_6m": build_gallery_walk, "lowlight_lamp_bench": build_lamp_bench}
