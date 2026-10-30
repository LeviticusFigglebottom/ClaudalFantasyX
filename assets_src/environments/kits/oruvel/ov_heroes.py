"""Oruvel's hero pieces (oruvel.md §2). Pure numpy; see ov_common.py. Every hull runs along local +Z (bow at -Z);
the origin is at the waterline amidships.

  keel_hull   the town's oldest and biggest hull and its meeting place: 22 m x 6.4 m, deck +1.0; a deckhouse aft with
              a railed deck on its roof (+3.6), an aft house on that under a keel-roof (ridge KEEL_HULL_RIDGE), the
              meeting awning slung from the old mast over the fore deck, benches, ladders, the carved stern post
  chandlery   Kell's: an 8 m hull with a keel-roof cabin, its +X side open as a counter under a striped awning; lamp
              racks of unlit lanterns, tall oil jars, the wick board, the post shelf, a stool, the beacon lamp on
              the roof (unlit; the drill lights it, C1-12)
  scale_hull  a 7 m hull with a booth: the counter facing +X, the brass beam scale, the chit stamp and its ink, a
              stack of chits, the small brass Level plaque on the booth post (the Order's only mark in the town)
  cookboat    a 7.5 m open hull with a clay stove amidships, a tin smoke hood, pots, a bowl shelf and the cook's knot
              tally (nine knots) hanging from the hood
  dive_raft   7 x 6 m deck on two 9 m hulls, deck top +0.75, the 1.6 m dive well between them (centred on the origin:
              place it over the Underway's tether), the A-frame and block over it, the tether winch, the ladder down
              to -2.4, a rack of unlit diver lanterns, lead weights, coiled tethers
"""

from __future__ import annotations

import math

import numpy as np

import ov_common as oc

kc = oc.kc

TRI_BUDGET = {
    "keel_hull": (28000, 1500),
    "chandlery": (24000, 1200),
    "scale_hull": (14000, 700),
    "cookboat": (11000, 600),
    "dive_raft": (18000, 900),
}

KEEL_HULL = (22.0, 6.4, 2.2, 1.25)  # length, beam, depth, gunwale height above the water
KEEL_DECK_Y = 1.0
KEEL_HOUSE = (2.3, 0.6, 8.6, 3.6)  # half width, z from, z to, roof-deck height
KEEL_AFT = (1.55, 5.1, 8.3, 2.0)  # half width, z from, z to, wall height above the roof deck
KEEL_AFT_ROOF = (5.6, 4.1, 0.95, 0.26)  # length, beam, depth, sheer
KEEL_HULL_RIDGE = KEEL_HOUSE[3] + KEEL_AFT[3] + 0.06 + KEEL_AFT_ROOF[2] + 0.08
CHANDLERY_HULL = (8.0, 3.4, 1.3, 0.6)
CHANDLERY_DECK_Y = 0.5
CHANDLERY_ROOF = (6.6, 3.9, 0.95, 0.24)  # length, beam, depth, sheer; its eave at deck + 2.22
DIVE_DECK_Y = 0.75
DIVE_WELL = 0.8  # half side of the dive well


def _ladder(mb: kc.MeshBuilder, base, top, width: float, rungs: int, rng, *, weather=oc.SUN) -> None:
    timber = mb.material(oc.M_TIMBER)
    base, top = np.asarray(base, float), np.asarray(top, float)
    side = np.array([width * 0.5, 0.0, 0.0])
    for sgn in (-1.0, 1.0):
        kc.plank(mb, base + side * sgn, top + side * sgn, 0.06, 0.05, timber, weather=weather,
                 variation=float(rng.random()))
    for k in range(rungs):
        f = (k + 0.6) / rungs
        p = base + (top - base) * f
        kc.plank(mb, p - side, p + side, 0.045, 0.035, timber, weather=weather, variation=float(rng.random()))


def _rope_rail(mb: kc.MeshBuilder, pts, y: float, rng, noise, *, h: float = 0.95, skip=()) -> None:
    """Posts at each (x, z) and a rope rail between consecutive posts (gaps listed in `skip` by segment index)."""
    rope = mb.material(oc.M_ROPE)
    for x, z in pts:
        oc.village.post(mb, (x, y - 0.1, z), (x, y + h, z), 0.045, rng, noise, sides=6, weather=oc.SUN)
    for k in range(len(pts) - 1):
        if k in skip:
            continue
        a = np.array([pts[k][0], y + h - 0.06, pts[k][1]])
        b = np.array([pts[k + 1][0], y + h - 0.06, pts[k + 1][1]])
        oc.rope(mb, a, b, 0.05, 0.016, rope, n=6)


def _lamp_rail(mb: kc.MeshBuilder, a, b, n: int, rng, *, drop=(0.32, 0.5), lanterns: bool = True) -> None:
    """An iron rail from a to b with n hooks, an unlit lantern on each (their chains at varied lengths)."""
    iron = mb.material(oc.M_IRON)
    a, b = np.asarray(a, float), np.asarray(b, float)
    kc.tube(mb, np.array([a, b]), 0.013, 4, iron, cap_start=True, cap_end=True)
    for k in range(n):
        p = a + (b - a) * ((k + 0.5) / n)
        dl = float(rng.uniform(*drop))
        kc.tube(mb, np.array([p, p - np.array([0.0, dl, 0.0])]), 0.005, 3, iron)
        if lanterns:
            oc.lantern(mb, p - np.array([0.0, dl + 0.3, 0.0]), rng)


def build_keel_hull(seed: int = 741) -> list[kc.MeshBuilder]:
    out = []
    L, B, D, gun = KEEL_HULL
    hw, z0, z1, roof_y = KEEL_HOUSE
    ahw, az0, az1, awall = KEEL_AFT
    rl, rb, rd, rs = KEEL_AFT_ROOF
    house_walls = (oc.M_TIMBER, oc.M_PAINT_WHITE, oc.M_PAINT_OCHRE)
    for lod in (False, True):
        rng = kc.rng_for("keel_hull", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("keel_hull" + (oc.LOD if lod else ""))
        timber = mb.material(oc.M_TIMBER)
        h = oc.hull("h", L, B, D, rng, noise, waterline=-gun, lod=lod, paint=oc.M_PAINT_RED, sheer=0.75,
                    open_top=True, frames=False, wear=0.24)
        oc.place(mb, h, 0.0, gun, 0.0)
        oc.hull_deck(mb, L, B, KEEL_DECK_Y, rng, noise, inset=0.14, lod=lod)
        # The deckhouse aft, its roof a railed deck; a door forward, windows on both sides.
        y0 = KEEL_DECK_Y
        oc.plank_wall(mb, (-hw, z0), (hw, z0), y0, roof_y, (0.0, -1.0), rng, noise, slots=house_walls,
                      openings=[(1.7, 2.6, y0, y0 + 1.95)], lod=lod)
        oc.plank_wall(mb, (hw, z0), (hw, z1), y0, roof_y, (1.0, 0.0), rng, noise, slots=house_walls,
                      openings=[(1.6, 2.5, y0 + 1.0, y0 + 1.7), (5.0, 5.9, y0 + 1.0, y0 + 1.7)], lod=lod)
        oc.plank_wall(mb, (-hw, z1), (-hw, z0), y0, roof_y, (-1.0, 0.0), rng, noise, slots=house_walls,
                      openings=[(2.2, 3.1, y0 + 1.0, y0 + 1.7), (5.6, 6.5, y0 + 1.0, y0 + 1.7)], lod=lod)
        oc.plank_wall(mb, (hw, z1), (-hw, z1), y0, roof_y, (0.0, 1.0), rng, noise, slots=house_walls, lod=lod)
        kc.polygon_prism(mb, np.array([[-hw + 0.08, z0 + 0.08], [hw - 0.08, z0 + 0.08], [hw - 0.08, z1 - 0.08],
                                       [-hw + 0.08, z1 - 0.08]]), y0, roof_y - 0.06, mb.material(oc.M_DARK),
                         col=np.array([0.0, 0.0, 0.0, 0.3]), uv2=np.array([0.3, 0.5]))
        oc.deck(mb, -hw - 0.2, hw + 0.2, z0 - 0.2, z1 + 0.2, roof_y + 0.05, rng, noise, along_x=True, lod=lod)
        # The aft house on the roof deck, under its keel-roof; the gull perches on its keel (placed by the layout).
        ay = roof_y + 0.05
        aeave = ay + awall + 0.06
        mid_z = (az0 + az1) * 0.5
        oc.plank_wall(mb, (-ahw, az0), (ahw, az0), ay, ay + awall, (0.0, -1.0), rng, noise, slots=house_walls,
                      openings=[(1.0, 1.85, ay, ay + 1.85)], lod=lod)
        oc.plank_wall(mb, (ahw, az0), (ahw, az1), ay, ay + awall, (1.0, 0.0), rng, noise, slots=house_walls, lod=lod)
        oc.plank_wall(mb, (-ahw, az1), (-ahw, az0), ay, ay + awall, (-1.0, 0.0), rng, noise, slots=house_walls,
                      openings=[(1.2, 1.9, ay + 0.9, ay + 1.5)], lod=lod)
        oc.plank_wall(mb, (ahw, az1), (-ahw, az1), ay, aeave + rd, (0.0, 1.0), rng, noise, slots=house_walls,
                      top_fn=lambda s: oc.keel_roof_underside(ahw - s, az1 - mid_z, rl, rb, rd, aeave, rs), lod=lod)
        oc.plank_wall(mb, (-ahw, az0), (ahw, az0), ay + awall, aeave + rd, (0.0, -1.0), rng, noise, slots=house_walls,
                      top_fn=lambda s: oc.keel_roof_underside(-ahw + s, az0 - mid_z, rl, rb, rd, aeave, rs),
                      lod=lod)
        kc.polygon_prism(mb, np.array([[-ahw + 0.08, az0 + 0.08], [ahw - 0.08, az0 + 0.08], [ahw - 0.08, az1 - 0.08],
                                       [-ahw + 0.08, az1 - 0.08]]), ay, ay + awall, mb.material(oc.M_DARK),
                         col=np.array([0.0, 0.0, 0.0, 0.3]), uv2=np.array([0.3, 0.5]))
        oc.keel_roof(mb, rl, rb, rd, aeave, rng, noise, lod=lod, paint=oc.M_PAINT, sheer=rs, at=(0.0, mid_z))
        # The old mast, stepped forward, and its stays; the meeting awning slung from it over the fore deck.
        mast_z = -3.2
        kc.tube(mb, np.array([[0.0, KEEL_DECK_Y - 0.2, mast_z], [0.0, KEEL_DECK_Y + 7.8, mast_z + 0.15]]),
                np.array([0.16, 0.11]), 5 if lod else 9, timber, cap_end=True, variation=0.3,
                noise=None if lod else noise, disp_m=0.01)
        if lod:
            oc.canvas(mb, [(-2.6, 2.9, -8.0), (2.6, 2.9, -8.0), (2.6, 2.9, -0.5), (-2.6, 2.9, -0.5)], 0.1, oc.M_CANVAS,
                      nu=2, nv=2, double=False)
        else:
            rope, tar = mb.material(oc.M_ROPE), mb.material(oc.M_ROPE_TAR)
            top = np.array([0.0, KEEL_DECK_Y + 7.6, mast_z + 0.14])
            for p in ((0.0, 2.0, -L * 0.5 - 0.1), (2.9, 1.6, mast_z + 1.0), (-2.9, 1.6, mast_z + 1.0),
                      (2.6, 1.7, 2.5), (-2.6, 1.7, 2.5)):
                oc.rope(mb, top, np.asarray(p), 0.12, 0.014, tar, n=8)
            yard_y = KEEL_DECK_Y + 3.3
            kc.tube(mb, np.array([[-3.0, yard_y, mast_z], [3.0, yard_y, mast_z]]), 0.06, 6, timber, cap_start=True,
                    cap_end=True)
            for x, z in ((-2.55, -8.2), (2.55, -8.2), (-2.75, -0.4), (2.75, -0.4)):
                oc.village.post(mb, (x, KEEL_DECK_Y - 0.05, z), (x, KEEL_DECK_Y + 2.15, z), 0.06, rng, noise,
                                weather=oc.SUN)
            oc.canvas(mb, [(-2.6, KEEL_DECK_Y + 2.15, -8.2), (2.6, KEEL_DECK_Y + 2.15, -8.2), (2.9, yard_y, mast_z),
                           (-2.9, yard_y, mast_z)], 0.12, oc.M_CANVAS, nu=7, nv=5, stripes=oc.M_CANVAS_RED, stripe_n=9)
            oc.canvas(mb, [(-2.9, yard_y, mast_z), (2.9, yard_y, mast_z), (2.8, KEEL_DECK_Y + 2.15, -0.4),
                           (-2.8, KEEL_DECK_Y + 2.15, -0.4)], 0.1, oc.M_CANVAS, nu=7, nv=4, stripes=oc.M_CANVAS_RED,
                      stripe_n=9)
            # Benches along both bulwarks under the awning; a long table board on trestles in the middle.
            for sgn in (-1.0, 1.0):
                x = sgn * 2.45
                kc.plank(mb, (x, KEEL_DECK_Y + 0.42, -7.6), (x, KEEL_DECK_Y + 0.42, -0.9), 0.34, 0.05, timber,
                         variation=float(rng.random()), noise=noise, seg=2)
                for z in (-7.2, -4.2, -1.3):
                    kc.rounded_block(mb, (x, KEEL_DECK_Y + 0.2, z), (0.14, 0.2, 0.06), timber, radius=0.01, seg=1)
            kc.plank(mb, (0.0, KEEL_DECK_Y + 0.74, -6.8), (0.0, KEEL_DECK_Y + 0.74, -1.6), 0.9, 0.05, timber,
                     variation=0.6, noise=noise, seg=2)
            for z in (-6.3, -2.1):
                for sgn in (-1.0, 1.0):
                    kc.plank(mb, (sgn * 0.35, KEEL_DECK_Y, z - 0.25), (sgn * 0.3, KEEL_DECK_Y + 0.72, z), 0.06, 0.05,
                             timber, variation=0.5)
            # Ladders: main deck to the roof deck (starboard, forward), roof deck to the aft house's door.
            _ladder(mb, (1.5, KEEL_DECK_Y, z0 - 0.7), (1.5, roof_y + 0.9, z0 - 0.05), 0.5, 9, rng)
            # The roof deck's rope rail (open at the ladder head).
            rail = [(-hw - 0.1, z0 - 0.1), (-hw - 0.1, z1 + 0.1), (hw + 0.1, z1 + 0.1), (hw + 0.1, z0 - 0.1),
                    (0.9, z0 - 0.1), (-hw - 0.1, z0 - 0.1)]
            _rope_rail(mb, rail, roof_y + 0.05, rng, noise, skip=(3,))
            # The carved stern post, rising over the stern with a knob carved as a coiled rope; a bowsprit stub.
            carved = mb.material(oc.M_CARVED)
            sz = L * 0.5
            kc.tube(mb, np.array([[0.0, gun + 0.5, sz - 0.2], [0.0, gun + 1.6, sz + 0.1], [0.0, gun + 2.6, sz + 0.05]]),
                    np.array([0.14, 0.12, 0.1]), 8, carved, cap_end=True, variation=0.4)
            for k in range(3):
                oc.ring(mb, (0.0, gun + 2.45 + 0.07 * k, sz + 0.05), (0.0, 1.0, 0.0), 0.1 - 0.02 * k, 0.035, carved)
            kc.tube(mb, np.array([[0.0, gun + 0.85, -sz + 0.6], [0.0, gun + 1.15, -sz - 1.4]]), np.array([0.13, 0.08]),
                    8, timber, cap_end=True)
            # Lamp rails on the deckhouse's eaves; a hook by the door.
            _lamp_rail(mb, (hw + 0.12, roof_y - 0.2, z0 + 0.6), (hw + 0.12, roof_y - 0.2, z1 - 0.6), 5, rng)
            _lamp_rail(mb, (-hw - 0.12, roof_y - 0.2, z0 + 0.6), (-hw - 0.12, roof_y - 0.2, z1 - 0.6), 4, rng)
            # Coils, a water jar, baskets; floats lashed outboard amidships as fenders.
            oc.coil(mb, (-1.5, KEEL_DECK_Y, -9.0), 0.3, rope)
            oc.coil(mb, (1.9, roof_y + 0.05, z1 - 0.6), 0.25, rope)
            oc.jar(mb, (-1.7, KEEL_DECK_Y, z0 - 0.5), 0.8, rng)
            oc.basket(mb, (1.9, KEEL_DECK_Y, -9.6), 0.25, 0.3, rng)
            for sgn in (-1.0, 1.0):
                for z in (-4.0, 1.0, 5.5):
                    oc.lashing(mb, (sgn * (B * 0.5 + 0.12), gun - 0.5, z), (0.0, 0.0, 1.0), 0.1, rope, turns=5,
                               rope_r=0.035, pitch=0.06)
                    kc.tube(mb, np.array([[sgn * (B * 0.5 + 0.1), gun - 0.4, z], [sgn * B * 0.5, gun + 0.02, z]]),
                            0.013, 4, rope)
        out.append(mb)
    return out


def build_chandlery(seed: int = 742) -> list[kc.MeshBuilder]:
    out = []
    L, B, D, gun = CHANDLERY_HULL
    dy = CHANDLERY_DECK_Y
    cw, cz0, cz1 = 1.5, -2.3, 2.3  # cabin half width (x), z extent
    rl, rb, rd, rs = CHANDLERY_ROOF
    eave = dy + 2.22
    walls = (oc.M_TIMBER, oc.M_PAINT_OCHRE, oc.M_PAINT_RED)
    counter_y = dy + 1.05
    for lod in (False, True):
        rng = kc.rng_for("chandlery", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("chandlery" + (oc.LOD if lod else ""))
        timber, iron = mb.material(oc.M_TIMBER), mb.material(oc.M_IRON)
        h = oc.hull("h", L, B, D, rng, noise, waterline=-gun, lod=lod, paint=oc.M_PAINT_OCHRE, sheer=0.35,
                    open_top=True, frames=False)
        oc.place(mb, h, 0.0, gun, 0.0)
        oc.hull_deck(mb, L, B, dy, rng, noise, inset=0.12, lod=lod)
        # The cabin: back wall, gables to the keel-roof, the street side (+X) a counter with the shop open above it.
        oc.plank_wall(mb, (-cw, cz1), (-cw, cz0), dy, eave - 0.06, (-1.0, 0.0), rng, noise, slots=walls, lod=lod)
        oc.plank_wall(mb, (cw, cz0), (cw, cz1), dy, counter_y - 0.03, (1.0, 0.0), rng, noise, slots=walls, lod=lod)
        for zw, sgn in ((cz0, -1.0), (cz1, 1.0)):
            oc.plank_wall(mb, (-cw, zw), (cw, zw), dy, eave + rd, (0.0, sgn), rng, noise, slots=walls,
                          top_fn=lambda s, zw=zw: oc.keel_roof_underside(-cw + s, zw, rl, rb, rd, eave, rs),
                          openings=[(0.9, 1.7, dy, dy + 1.9)] if sgn < 0 else [], lod=lod)
        oc.keel_roof(mb, rl, rb, rd, eave, rng, noise, lod=lod, paint=oc.M_PAINT_RED, sheer=rs)
        kc.plank(mb, (cw + 0.12, counter_y, cz0 + 0.05), (cw + 0.12, counter_y, cz1 - 0.05), 0.5, 0.06, timber,
                 variation=0.7, noise=None if lod else noise, seg=1 if lod else 3)
        # The striped awning over the counter, held out over the walkway by two spars from the gunwale.
        ax = cw + 0.5  # short, so the high sun reaches the counter under it (C1-10: her hands and the wick in focus)
        oc.canvas(mb, [(cw + 0.05, eave - 0.05, cz0 - 0.2), (cw + 0.05, eave - 0.05, cz1 + 0.2),
                       (ax + 0.1, eave - 0.3, cz1 + 0.2), (ax + 0.1, eave - 0.3, cz0 - 0.2)], 0.04, oc.M_CANVAS,
                  nu=3 if lod else 11, nv=2 if lod else 4, stripes=None if lod else oc.M_CANVAS_RED, stripe_n=11,
                  double=not lod)
        if lod:
            kc.polygon_prism(mb, np.array([[-cw + 0.1, cz0 + 0.1], [cw - 0.1, cz0 + 0.1], [cw - 0.1, cz1 - 0.1],
                                           [-cw + 0.1, cz1 - 0.1]]), counter_y, eave - 0.1, mb.material(oc.M_DARK),
                             col=np.array([0.0, 0.0, 0.0, 0.3]), uv2=np.array([0.3, 0.5]))
            out.append(mb)
            continue
        for z in (cz0 - 0.15, cz1 + 0.15):
            kc.tube(mb, np.array([[1.55, gun - 0.05, z], [ax, eave - 0.33, z]]), 0.035, 6, timber, cap_start=True,
                    cap_end=True)
            oc.lashing(mb, (1.6, gun + 0.1, z), (0.6, 1.0, 0.0), 0.04, mb.material(oc.M_ROPE), turns=3)
        for cx in (-cw, cw):
            for cz in (cz0, cz1):
                oc.village.post(mb, (cx, dy - 0.05, cz), (cx, eave + 0.02, cz), 0.07, rng, noise, weather=oc.SUN)
        # Lamp racks: one rail at the awning's edge, one under the eave; lanterns by the dozen, all unlit.
        _lamp_rail(mb, (ax - 0.05, eave - 0.36, cz0 + 0.1), (ax - 0.05, eave - 0.36, cz1 - 0.1), 6, rng, drop=(0.05, 0.25))
        _lamp_rail(mb, (cw + 0.3, eave - 0.12, cz0 + 0.3), (cw + 0.3, eave - 0.12, cz1 - 0.3), 5, rng, drop=(0.2, 0.4))
        # Oil jars: four tall ones on the fore deck, two behind the counter.
        for (x, z, hh) in ((0.9, -3.05, 1.05), (0.25, -3.25, 0.95), (-0.45, -3.1, 1.1), (-1.05, -2.85, 0.85),
                           (-1.0, 1.7, 0.8), (-1.05, -1.5, 0.75)):
            oc.jar(mb, (x, dy, z), hh, rng)
        # The wick board on the back wall: twelve spools on pegs.
        kc.rounded_block(mb, (-cw + 0.08, dy + 1.65, 0.3), (0.025, 0.42, 0.75), timber, radius=0.01, seg=1,
                         variation=0.4)
        wick = mb.material(oc.M_WICK)
        for r in range(3):
            for c in range(4):
                p = np.array([-cw + 0.11, dy + 1.38 + r * 0.26, -0.22 + c * 0.35])
                kc.tube(mb, np.array([p, p + np.array([0.16, 0.02, 0.0])]), 0.01, 4, timber, cap_end=True)
                oc.lathe(mb, [(0.035, 0.0), (0.035, 0.012), (0.026, 0.014), (0.026, 0.07), (0.035, 0.072),
                              (0.035, 0.084)], wick, sides=8, at=p + np.array([0.04, 0.0, 0.0]),
                         rot=kc.rot_z(-math.pi * 0.5))
        # The post shelf: a 4 x 3 box of pigeonholes on the -Z gable's inner face (empty: no letter is shown).
        sx0, sx1, sy0, sy1, sz = -1.1, 0.1, dy + 1.2, dy + 1.95, cz0 + 0.2
        kc.rounded_block(mb, ((sx0 + sx1) * 0.5, (sy0 + sy1) * 0.5, sz - 0.1), ((sx1 - sx0) * 0.5, (sy1 - sy0) * 0.5,
                                                                             0.012), timber, radius=0.005, seg=1)
        for k in range(5):
            x = sx0 + (sx1 - sx0) * k / 4
            kc.rounded_block(mb, (x, (sy0 + sy1) * 0.5, sz), (0.012, (sy1 - sy0) * 0.5, 0.11), timber, radius=0.004,
                             seg=1)
        for k in range(4):
            y = sy0 + (sy1 - sy0) * k / 3
            kc.rounded_block(mb, ((sx0 + sx1) * 0.5, y, sz), ((sx1 - sx0) * 0.5, 0.012, 0.11), timber, radius=0.004,
                             seg=1)
        # On the counter: a spool, a tray of wicks, a lantern; a stool behind it.
        for zs, ys in ((0.4, 0.0), (0.55, 0.0), (0.47, 0.096)):  # spools on the counter, one stacked
            oc.lathe(mb, [(0.04, 0.0), (0.04, 0.014), (0.03, 0.016), (0.03, 0.08), (0.04, 0.082), (0.04, 0.096)], wick,
                     sides=10, at=(cw + 0.05, counter_y + 0.03 + ys, zs))
        kc.rounded_block(mb, (cw + 0.1, counter_y + 0.05, -0.5), (0.14, 0.02, 0.22), timber, radius=0.01, seg=1)
        for k in range(6):
            kc.tube(mb, np.array([[cw + 0.0 + 0.04 * k, counter_y + 0.075, -0.68], [cw + 0.0 + 0.04 * k,
                                                                                  counter_y + 0.075, -0.3]]),
                    0.006, 3, wick)
        oc.lantern(mb, (cw + 0.12, counter_y + 0.03, 1.4), rng)
        kc.rounded_block(mb, (0.4, dy + 0.62, -0.2), (0.2, 0.025, 0.2), timber, radius=0.01, seg=1)
        for sx in (-1, 1):
            for sz2 in (-1, 1):
                kc.tube(mb, np.array([[0.4 + 0.15 * sx, dy, -0.2 + 0.15 * sz2], [0.4 + 0.13 * sx, dy + 0.6,
                                                                                 -0.2 + 0.13 * sz2]]),
                        0.018, 4, timber)
        # The beacon lamp on the roof's fore end: a post off the keel, a big brass lantern under a cowl.
        ridge_y = eave + rd + 0.04
        bz = -1.8
        ridge_here = oc.keel_roof_underside(0.0, bz, rl, rb, rd, eave, rs) + 0.12
        del ridge_y
        oc.village.post(mb, (0.0, ridge_here - 0.1, bz), (0.0, ridge_here + 1.2, bz), 0.07, rng, noise, weather=oc.SUN)
        oc.lantern(mb, (0.0, ridge_here + 1.2, bz), rng, scale=2.1, bail=False)
        oc.lathe(mb, [(0.26, 0.0), (0.2, 0.08), (0.05, 0.2), (0.0, 0.22)], mb.material(oc.M_BRASS), sides=12,
                 at=(0.0, ridge_here + 1.2 + 0.64, bz))
        for sgn in (-1.0, 1.0):
            oc.rope(mb, (0.0, ridge_here + 0.9, bz), (sgn * 1.6, eave - 0.05, bz - 0.3), 0.04, 0.01,
                    mb.material(oc.M_ROPE_TAR), n=5)
        del iron
        out.append(mb)
    return out


def build_scale_hull(seed: int = 743) -> list[kc.MeshBuilder]:
    out = []
    L, B, D, gun = 7.0, 2.8, 1.1, 0.5
    dy = 0.4
    bx0, bx1, bz0, bz1 = -1.0, 1.0, -1.2, 1.2  # the booth (its counter on +X)
    y_hi, y_lo = dy + 2.4, dy + 2.05
    counter_y = dy + 1.0
    for lod in (False, True):
        rng = kc.rng_for("scale_hull", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("scale_hull" + (oc.LOD if lod else ""))
        timber, brass = mb.material(oc.M_TIMBER), mb.material(oc.M_BRASS)
        h = oc.hull("h", L, B, D, rng, noise, waterline=-gun, lod=lod, paint=oc.M_PAINT_WHITE, sheer=0.3,
                    open_top=True, frames=False)
        oc.place(mb, h, 0.0, gun, 0.0)
        oc.hull_deck(mb, L, B, dy, rng, noise, inset=0.12, lod=lod)

        def roof_y(x: float) -> float:
            return y_hi + (y_lo - y_hi) * (x - bx0) / (bx1 - bx0)

        walls = (oc.M_TIMBER, oc.M_PAINT)
        oc.plank_wall(mb, (bx0, bz1), (bx0, bz0), dy, y_hi, (-1.0, 0.0), rng, noise, slots=walls, lod=lod)
        for zw, sgn in ((bz0, -1.0), (bz1, 1.0)):
            oc.plank_wall(mb, (bx0, zw), (bx1, zw), dy, y_hi, (0.0, sgn), rng, noise, slots=walls,
                          top_fn=lambda s: roof_y(bx0 + s) - 0.03, lod=lod)
        oc.plank_wall(mb, (bx1, bz0), (bx1, bz1), dy, counter_y - 0.03, (1.0, 0.0), rng, noise, slots=walls, lod=lod)
        up = kc.normalize(np.array([(y_hi - y_lo) / (bx1 - bx0), 1.0, 0.0]))
        rx0, rx1 = bx0 - 0.15, bx1 + 0.45
        if lod:
            kc.plank(mb, (rx0, roof_y(rx0) + 0.05, 0.0), (rx1, roof_y(rx1) + 0.05, 0.0), bz1 - bz0 + 0.5, 0.06, timber,
                     up=up)
        else:
            nb = 12
            for k in range(nb):  # roof boards down the slope, alternately lapped, one an old painted board
                z = bz0 - 0.25 + (k + 0.5) * (bz1 - bz0 + 0.5) / nb
                slot = mb.material(oc.M_PAINT_RED) if k == 7 else timber
                kc.plank(mb, (rx0, roof_y(rx0) + 0.05 + 0.018 * (k % 2), z), (rx1, roof_y(rx1) + 0.05 + 0.018 * (k % 2), z),
                         (bz1 - bz0 + 0.5) / nb + 0.02, 0.03, slot, up=up, variation=float(rng.random()), noise=noise)
        kc.plank(mb, (bx1 + 0.1, counter_y, bz0 + 0.05), (bx1 + 0.1, counter_y, bz1 - 0.05), 0.45, 0.06, timber,
                 variation=0.8, noise=None if lod else noise)
        if lod:
            out.append(mb)
            continue
        for cx in (bx0, bx1):
            for cz in (bz0, bz1):
                oc.village.post(mb, (cx, dy - 0.05, cz), (cx, roof_y(cx), cz), 0.06, rng, noise, weather=oc.SUN)
        # The brass beam scale: a post on the counter, a 1.2 m beam, two pans on three chains each, a pointer.
        base = np.array([bx1 + 0.12, counter_y + 0.03, 0.0])
        kc.rounded_block(mb, base + np.array([0.0, 0.03, 0.0]), (0.12, 0.03, 0.12), brass, radius=0.01, seg=1)
        kc.tube(mb, np.array([base, base + np.array([0.0, 0.85, 0.0])]), 0.02, 8, brass, cap_end=True)
        top = base + np.array([0.0, 0.85, 0.0])
        kc.tube(mb, np.array([top + np.array([0.0, 0.0, -0.6]), top + np.array([0.0, 0.0, 0.6])]), 0.014, 6, brass,
                cap_start=True, cap_end=True)
        kc.tube(mb, np.array([top + np.array([0.0, 0.02, 0.0]), top + np.array([0.0, 0.2, 0.0])]),
                np.array([0.008, 0.002]), 4, brass)
        for zc in (-0.58, 0.58):
            pan = top + np.array([0.0, -0.62, zc])
            oc.lathe(mb, [(0.0, -0.03), (0.13, -0.01), (0.16, 0.02)], brass, sides=12, at=pan)
            for k in range(3):
                a = k * 2.0 * math.pi / 3.0
                kc.tube(mb, np.array([top + np.array([0.0, -0.01, zc]), pan + np.array([math.cos(a) * 0.14, 0.02,
                                                                                         math.sin(a) * 0.14])]),
                        0.003, 3, brass)
        # The chit stamp, its ink tin, a stack of chits; scrap brass in a crate below the counter.
        st = np.array([bx1 + 0.2, counter_y + 0.03, -0.75])
        kc.rounded_block(mb, st + np.array([0.0, 0.025, 0.0]), (0.04, 0.025, 0.05), brass, radius=0.005, seg=1)
        kc.tube(mb, np.array([st + np.array([0.0, 0.05, 0.0]), st + np.array([0.0, 0.16, 0.0])]),
                np.array([0.015, 0.022]), 6, timber, cap_end=True)
        oc.lathe(mb, [(0.0, 0.0), (0.04, 0.0), (0.04, 0.02), (0.0, 0.02)], mb.material(oc.M_IRON), sides=10,
                 at=st + np.array([0.0, 0.0, 0.16]))
        kc.rounded_block(mb, st + np.array([0.04, 0.02, 0.36]), (0.07, 0.02, 0.1), mb.material(oc.M_WICK),
                         radius=0.004, seg=1, rot=kc.rot_y(0.2))
        oc.crate(mb, (bx1 + 0.6, dy + 0.25, 0.9), (0.25, 0.25, 0.3), rng, noise)
        for k in range(4):
            p = np.array([bx1 + 0.55, dy + 0.5, 0.75 + 0.08 * k])
            kc.tube(mb, np.array([p, p + np.array([0.2 * math.cos(k), 0.08, 0.2 * math.sin(k)])]), 0.02, 6, brass,
                    cap_start=True, cap_end=True)
        # The Level plaque: a small brass plate on the booth's front post, a bar over a plumb drop in relief.
        pp = np.array([bx1 + 0.075, dy + 1.62, bz1 - 0.02])
        kc.rounded_block(mb, pp, (0.008, 0.12, 0.1), brass, radius=0.004, seg=1)
        kc.rounded_block(mb, pp + np.array([0.012, 0.05, 0.0]), (0.006, 0.01, 0.075), brass, radius=0.003, seg=1)
        kc.tube(mb, np.array([pp + np.array([0.012, 0.04, 0.0]), pp + np.array([0.012, -0.05, 0.0])]), 0.003, 4,
                brass)
        oc.lathe(mb, [(0.0, -0.09), (0.014, -0.07), (0.0, -0.05)], brass, sides=6, at=pp + np.array([0.012, 0.0, 0.0]))
        # A coil and a stool.
        oc.coil(mb, (-1.6, dy, -1.9), 0.22, mb.material(oc.M_ROPE))
        kc.rounded_block(mb, (0.3, dy + 0.55, -0.4), (0.17, 0.025, 0.17), timber, radius=0.01, seg=1)
        for sx in (-1, 1):
            for sz in (-1, 1):
                kc.tube(mb, np.array([[0.3 + 0.13 * sx, dy, -0.4 + 0.13 * sz], [0.3 + 0.11 * sx, dy + 0.53,
                                                                                -0.4 + 0.11 * sz]]), 0.016, 4, timber)
        out.append(mb)
    return out


def build_cookboat(seed: int = 744) -> list[kc.MeshBuilder]:
    out = []
    L, B, D, gun = 7.5, 2.4, 1.0, 0.45
    floor_y = gun - 0.62
    for lod in (False, True):
        rng = kc.rng_for("cookboat", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("cookboat" + (oc.LOD if lod else ""))
        timber, clay, iron = mb.material(oc.M_TIMBER), mb.material(oc.M_CLAY), mb.material(oc.M_IRON)
        h = oc.hull("h", L, B, D, rng, noise, waterline=-gun, lod=lod, paint=oc.M_PAINT_TEAL, sheer=0.3,
                    open_top=True, frames=not lod)
        oc.place(mb, h, 0.0, gun, 0.0)
        oc.hull_deck(mb, L, B, floor_y, rng, noise, inset=0.32, lod=lod, z_clip=(-2.6, 2.8))
        # The stove: a clay firebox amidships, its mouth to +X, a pot on it; the smoke hood on four posts.
        kc.rounded_block(mb, (0.0, floor_y + 0.32, 0.0), (0.42, 0.32, 0.32), clay, radius=0.06, seg=1 if lod else 3,
                         noise=None if lod else noise, disp_m=0.015, weather=oc.DRY, variation=0.4)
        hood_y = floor_y + 2.0
        if lod:
            oc.lathe(mb, [(0.85, 0.0), (0.12, 0.45), (0.12, 0.9)], iron, sides=4, at=(0.0, hood_y, 0.0),
                     rot=kc.rot_y(math.pi * 0.25))
            out.append(mb)
            continue
        kc.rounded_block(mb, (0.43, floor_y + 0.25, 0.0), (0.02, 0.13, 0.15), mb.material(oc.M_DARK), radius=0.02,
                         seg=1)
        oc.lathe(mb, [(0.0, 0.0), (0.2, 0.0), (0.24, 0.12), (0.22, 0.2), (0.24, 0.22)], iron, sides=12,
                 at=(0.0, floor_y + 0.64, 0.05))
        oc.lathe(mb, [(0.0, 0.0), (0.14, 0.0), (0.16, 0.1), (0.15, 0.13)], iron, sides=10,
                 at=(0.25, floor_y + 0.64, -0.6))
        for sx in (-1, 1):
            for sz in (-1, 1):
                oc.village.post(mb, (sx * 0.62, floor_y, sz * 0.62), (sx * 0.62, hood_y + 0.02, sz * 0.62), 0.04, rng,
                                noise, sides=6, weather=oc.SUN)
        oc.lathe(mb, [(0.88, 0.0), (0.84, 0.04), (0.15, 0.42), (0.11, 0.44)], iron, sides=4,
                 at=(0.0, hood_y, 0.0), rot=kc.rot_y(math.pi * 0.25))
        oc.lathe(mb, [(0.1, 0.4), (0.1, 1.05), (0.13, 1.08), (0.13, 1.14)], iron, sides=8, at=(0.0, hood_y, 0.0))
        # The knot tally: a cord from the hood's corner, nine knots (the cook's credit).
        p0 = np.array([0.66, hood_y - 0.05, 0.66])
        ss = np.linspace(0.0, 1.0, 46)
        pts = p0 + np.stack([0.01 * np.sin(ss * 7.0), -1.05 * ss, 0.01 * np.cos(ss * 5.0)], axis=-1)
        radii = np.full(len(ss), 0.006)
        for k in range(9):
            radii[4 + k * 4] = 0.016
        kc.tube(mb, pts, radii, 5, mb.material(oc.M_ROPE), cap_end=True)
        # A shelf of bowls on the fore thwart, stools, a water jar, firewood.
        kc.plank(mb, (-0.85, floor_y + 0.75, -1.5), (0.85, floor_y + 0.75, -1.5), 0.3, 0.04, timber, variation=0.5)
        for k in range(5):
            oc.lathe(mb, [(0.0, 0.0), (0.05, 0.0), (0.08, 0.05), (0.075, 0.055)], clay, sides=8,
                     at=(-0.6 + 0.3 * k, floor_y + 0.77, -1.5))
        oc.jar(mb, (-0.55, floor_y, 1.3), 0.65, rng)
        for k in range(6):
            a = 0.15 * k
            kc.tube(mb, np.array([[-0.75 + 0.05 * k, floor_y + 0.05 + 0.04 * (k % 2), 0.6],
                                  [-0.7 + 0.05 * k, floor_y + 0.05 + 0.04 * (k % 2), 1.0 + a * 0.1]]), 0.035, 5,
                    timber, cap_start=True, cap_end=True)
        for z in (2.0, -2.2):
            kc.rounded_block(mb, (0.4, floor_y + 0.3, z), (0.15, 0.3, 0.15), timber, radius=0.02, seg=1)
        out.append(mb)
    return out


def build_dive_raft(seed: int = 745) -> list[kc.MeshBuilder]:
    out = []
    w, d = 7.0, 6.0
    x0, x1, z0, z1 = -w * 0.5, w * 0.5, -d * 0.5, d * 0.5
    y = DIVE_DECK_Y
    hw = DIVE_WELL
    for lod in (False, True):
        rng = kc.rng_for("dive_raft", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("dive_raft" + (oc.LOD if lod else ""))
        timber, rope, tar, iron = (mb.material(oc.M_TIMBER), mb.material(oc.M_ROPE), mb.material(oc.M_ROPE_TAR),
                                   mb.material(oc.M_IRON))
        if lod:
            for a0, a1, b0, b1 in ((x0, x1, z0, -hw), (x0, x1, hw, z1), (x0, -hw, -hw, hw), (hw, x1, -hw, hw)):
                kc.rounded_block(mb, ((a0 + a1) * 0.5, y - 0.04, (b0 + b1) * 0.5), ((a1 - a0) * 0.5, 0.04,
                                                                                   (b1 - b0) * 0.5), timber, seg=1,
                                 radius=0.01)
        else:
            oc.deck(mb, x0, x1, z0, z1, y, rng, noise, along_x=False, holes=[(-hw, hw, -hw, hw)], missing_p=0.01,
                    weather=oc.SOAK)
        gun = y - 0.21
        for hx, paint in ((-2.25, oc.M_PAINT), (2.25, oc.M_PAINT_WHITE)):
            hh = oc.hull("h", 9.0, 1.9, 0.95, rng, noise, waterline=-gun, lod=lod, paint=paint, sheer=0.3,
                         open_top=True, frames=False)
            oc.place(mb, hh, hx, gun, 0.0)
            if not lod:
                for zb in (-2.4, -0.9, 0.9, 2.4):
                    oc.cross_lash(mb, (hx, gun + 0.07, zb), 0.16, rope)
        # The A-frame over the well (legs either side, a back leg aft), the block hanging from its head.
        apex = np.array([0.0, y + 3.25, 0.1])
        legs = [np.array([-1.35, y, -0.2]), np.array([1.35, y, -0.2])]
        for p in legs:
            if lod:
                kc.tube(mb, np.array([p, apex]), 0.07, 4, timber)
            else:
                oc.village.post(mb, p - np.array([0.0, 0.05, 0.0]), apex, 0.075, rng, noise, weather=oc.SUN)
        kc.tube(mb, np.array([[0.0, y, 2.6], apex]), 0.065, 4 if lod else 7, timber, cap_start=True,
                variation=0.4)
        if lod:
            out.append(mb)
            continue
        oc.lashing(mb, apex - np.array([0.0, 0.12, 0.0]), (1.0, 0.0, 0.0), 0.12, rope, turns=6, pitch=0.03)
        block = apex - np.array([0.0, 0.42, 0.0])
        kc.tube(mb, np.array([apex - np.array([0.0, 0.15, 0.0]), block + np.array([0.0, 0.12, 0.0])]), 0.014, 4, rope)
        kc.rounded_block(mb, block, (0.05, 0.13, 0.1), timber, radius=0.03, seg=2, variation=0.5)
        oc.ring(mb, block, (1.0, 0.0, 0.0), 0.075, 0.012, mb.material(oc.M_BRASS), segs=10)
        # The well's coaming: four boards on edge round the hole.
        for a, b, up in (((-hw, y + 0.06, -hw - 0.04), (hw, y + 0.06, -hw - 0.04), (0, 0, 1)),
                         ((-hw, y + 0.06, hw + 0.04), (hw, y + 0.06, hw + 0.04), (0, 0, 1)),
                         ((-hw - 0.04, y + 0.06, -hw), (-hw - 0.04, y + 0.06, hw), (1, 0, 0)),
                         ((hw + 0.04, y + 0.06, -hw), (hw + 0.04, y + 0.06, hw), (1, 0, 0))):
            kc.plank(mb, a, b, 0.14, 0.05, timber, up=up, variation=float(rng.random()), noise=noise)
        # The tether winch aft of the well: cheeks, a drum wound with tether, a crank and a brass pawl.
        wz, wy = 1.75, y + 0.55
        for sx in (-0.48, 0.48):
            kc.rounded_block(mb, (sx, y + 0.3, wz), (0.04, 0.32, 0.32), timber, radius=0.02, seg=1,
                             noise=noise, disp_m=0.005, variation=float(rng.random()))
            kc.plank(mb, (sx, y + 0.02, wz - 0.55), (sx, y + 0.02, wz + 0.55), 0.12, 0.08, timber,
                     variation=float(rng.random()))
        oc.lathe(mb, [(0.0, -0.44), (0.24, -0.44), (0.24, -0.4), (0.17, -0.38), (0.17, 0.38), (0.24, 0.4),
                      (0.24, 0.44), (0.0, 0.44)], timber, sides=12, at=(0.0, wy, wz), rot=kc.rot_z(math.pi * 0.5))
        for k in range(9):
            oc.ring(mb, (-0.32 + 0.08 * k, wy, wz), (1.0, 0.0, 0.0), 0.19, 0.017, tar, segs=12)
        kc.tube(mb, np.array([[-0.6, wy, wz], [0.62, wy, wz]]), 0.025, 6, iron, cap_start=True, cap_end=True)
        crank = np.array([[0.62, wy, wz], [0.62, wy + 0.32, wz - 0.05], [0.8, wy + 0.32, wz - 0.05]])
        kc.tube(mb, crank, 0.016, 5, iron, cap_end=True)
        kc.tube(mb, np.array([[0.8, wy + 0.32, wz - 0.05], [0.95, wy + 0.32, wz - 0.05]]), 0.022, 6, timber,
                cap_start=True, cap_end=True)
        oc.ring(mb, (-0.56, wy, wz), (1.0, 0.0, 0.0), 0.12, 0.018, iron, segs=14)
        kc.rounded_block(mb, (-0.56, wy + 0.16, wz - 0.06), (0.018, 0.07, 0.025), mb.material(oc.M_BRASS),
                         rot=kc.rot_x(0.5), radius=0.008, seg=1)
        # The tether: off the drum, up over the block and down through the well into the water.
        top_drum = np.array([0.0, wy + 0.19, wz - 0.05])
        sheave = block + np.array([0.0, 0.05, 0.08])
        oc.rope(mb, top_drum, sheave, 0.03, 0.012, tar, n=6)
        kc.tube(mb, np.array([block + np.array([0.0, -0.05, -0.07]), np.array([0.05, y - 0.5, -0.1]),
                              np.array([0.12, -3.0, -0.15])]), 0.012, 5, tar)
        # The ladder down from the well's fore edge into the water.
        _ladder(mb, (0.0, -2.4, -hw + 0.08), (0.0, y + 0.55, -hw - 0.02), 0.5, 10, rng, weather=oc.SOAK)
        # A rack of four diver lanterns (unlit) on two posts to port, a lamp hook by the well.
        for z in (-1.2, 1.0):
            oc.village.post(mb, (-3.0, y - 0.05, z), (-3.0, y + 1.5, z), 0.05, rng, noise, sides=6, weather=oc.SUN)
        _lamp_rail(mb, (-3.0, y + 1.42, -1.2), (-3.0, y + 1.42, 1.0), 4, rng, drop=(0.12, 0.2))
        oc.village.post(mb, (0.95, y - 0.05, -1.05), (0.95, y + 1.25, -1.05), 0.035, rng, noise, sides=6,
                        lash=False, weather=oc.SUN)
        kc.tube(mb, np.array([[0.95, y + 1.2, -1.05], [0.85, y + 1.2, -1.05], [0.83, y + 1.12, -1.05]]), 0.007, 4,
                iron)
        # Lead weights in a basket, two coiled tethers, a crate of salvage, cleats.
        oc.basket(mb, (2.6, y, -2.2), 0.24, 0.26, rng)
        lead = mb.material(oc.M_LEAD)
        for k in range(5):
            a = k * 1.3
            kc.rounded_block(mb, (2.6 + 0.1 * math.cos(a), y + 0.24 + 0.03 * (k % 2), -2.2 + 0.1 * math.sin(a)),
                             (0.06, 0.035, 0.04), lead, rot=kc.rot_y(a), radius=0.015, seg=1)
        oc.coil(mb, (1.9, y, 2.3), 0.3, tar, turns=6, rope_r=0.014)
        oc.coil(mb, (-1.9, y, -2.3), 0.26, tar, turns=5, rope_r=0.014)
        oc.crate(mb, (2.5, y + 0.25, 0.6), (0.3, 0.25, 0.35), rng, noise, yaw=0.2)
        for cx, cz in ((x0 + 0.2, z0 + 0.2), (x1 - 0.2, z0 + 0.2), (x0 + 0.2, z1 - 0.2), (x1 - 0.2, z1 - 0.2)):
            oc.village.post(mb, (cx, y - 0.25, cz), (cx, y + 0.4, cz), 0.07, rng, noise, weather=oc.SUN)
        _dive_mark(mb)
        out.append(mb)
    return out


# The Ch1 Underway dressing pass (the Lead, 10-30: the dive's readability): seen from the deck, the well was flat dark
# water, the tether and ladder tarred black and lost under it. A rope hoop of white floats rides the well's water
# (Oruvel's water at the dressing's y and scale: local +0.15) and a pale shot-line, white-tagged every 0.6 m, drops
# from it to a lead sinker: the way down reads before the prompt does.
DIVE_WATER_LOCAL_Y = 0.15
DIVE_HOOP_R = 0.5
DIVE_FLOATS = 6
DIVE_FLOAT_PROFILE = [(0.0, -0.09), (0.08, -0.08), (0.11, -0.03), (0.11, 0.03), (0.08, 0.08), (0.0, 0.09)]
DIVE_LINE_TO_Y = -4.0
DIVE_TAG_STEP_M = 0.6


def _dive_mark(mb: kc.MeshBuilder) -> None:
    wy = DIVE_WATER_LOCAL_Y
    rope, white, lead = mb.material(oc.M_ROPE), mb.material(oc.M_PAINT_WHITE), mb.material(oc.M_LEAD)
    oc.ring(mb, (0.0, wy, 0.0), (0.0, 1.0, 0.0), DIVE_HOOP_R, 0.02, rope, segs=24, sides=5)
    for k in range(DIVE_FLOATS):
        a = 2.0 * math.pi * (k + 0.5) / DIVE_FLOATS
        oc.lathe(mb, DIVE_FLOAT_PROFILE, white, sides=10, at=(math.cos(a) * DIVE_HOOP_R, wy, math.sin(a) * DIVE_HOOP_R),
                 rot=kc.rot_y(-a) @ kc.rot_x(math.pi * 0.5), weather=oc.SOAK)
    for k in range(3):  # the bridle from the hoop to the line's head
        a = 2.0 * math.pi * k / 3
        kc.tube(mb, np.array([[math.cos(a) * DIVE_HOOP_R, wy, math.sin(a) * DIVE_HOOP_R], [0.0, wy - 0.35, 0.0]]),
                0.01, 4, rope)
    kc.tube(mb, np.array([[0.0, wy - 0.35, 0.0], [0.04, (wy + DIVE_LINE_TO_Y) * 0.5, 0.03],
                          [0.06, DIVE_LINE_TO_Y, 0.05]]), 0.016, 5, rope)
    for ty in np.arange(wy - 0.35 - DIVE_TAG_STEP_M, DIVE_LINE_TO_Y, -DIVE_TAG_STEP_M):
        t = (wy - 0.35 - ty) / (wy - 0.35 - DIVE_LINE_TO_Y)
        kc.rounded_block(mb, (0.06 * t + 0.03, ty, 0.05 * t), (0.035, 0.05, 0.005), white, radius=0.0, seg=1)
    oc.lathe(mb, [(0.0, -0.12), (0.07, -0.1), (0.08, 0.0), (0.05, 0.1), (0.0, 0.12)], lead, sides=8,
             at=(0.06, DIVE_LINE_TO_Y - 0.1, 0.05))


TARGETS = {
    "keel_hull": build_keel_hull,
    "chandlery": build_chandlery,
    "scale_hull": build_scale_hull,
    "cookboat": build_cookboat,
    "dive_raft": build_dive_raft,
}
