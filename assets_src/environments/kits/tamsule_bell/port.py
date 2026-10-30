"""Tamsule port's edge around the Bell Reach (tamsule_bell.md §2; M3-ENV-01).

  shophouse_a      an 8 x 10 m stilt shophouse, front (+Z) to the river: piles, a shop deck, an open
                   front with propped shutter-boards, a timber upper floor with windows, a two-tier
                   shingle hip roof with flared eaves, gilded ridge finials, and a vertical gilded
                   signboard hung out from the front corner
  shophouse_b      a 7 x 9 m variant with an upper balcony and a horizontal gilded board on its rail
  boardwalk_8m     a boardwalk module along X on piles, deck y 1.6, rail on the river side (+Z)
  signboard_gilded a free-standing gilded side-board on a lacquered post frame (gallery ends, boat lanes)

Origins: at the footprint centre (shophouses, boardwalk) or the frame's foot (signboard), on the river
datum y 0. The port's water is the datum too; piles go to the riverbed at y -3.5.
"""

from __future__ import annotations

import math

import numpy as np

import tb_common as tb
from tb_common import kc, village

M_TIMBER = "tb_timber"
M_PILE = "tb_pile_timber"
M_BLACK = "tb_lacquer_black"
M_RED = "tb_lacquer_red"
M_WOVEN = "tb_woven"
M_DARK = "tb_interior_dark"
ROOF_SLOTS = {"kit_thatch": "tb_roof_nipa", "kit_timber": "tb_timber", "kit_mortar_white": "tb_lacquer_black"}

TRI_BUDGET = {
    "shophouse": (20000, 2000),
    "boardwalk_8m": (3000, 300),
    "signboard_gilded": (1600, 200),
}
BUDGET_KEY = {"shophouse_a": "shophouse", "shophouse_b": "shophouse"}

DECK_Y = 1.6
RIVERBED_Y = -3.5
UPPER_FLOOR_Y = 4.4
WALL_TOP_Y = 7.2
EAVE_M = 1.2

SHOPHOUSES = {
    # name: (width x, depth z, lower pitch, upper pitch, balcony, seed)
    "shophouse_a": (8.0, 10.0, 28.0, 34.0, False, 741),
    "shophouse_b": (7.0, 9.0, 30.0, 36.0, True, 742),
}


def _box(mb, center, half, mat, rng, *, rot=None, weather=tb.TIMBER):
    kc.rounded_block(mb, center, half, mb.material(mat), rot=rot, radius=min(0.02, min(half) * 0.5), seg=1,
                     weather=weather, variation=float(rng.random()))


def _roof(mb, w, d, y_eave, pitch, rng, noise, *, lod):
    start = mb.vertex_count
    village.hip_roof(mb, w, d, y_eave, rng, noise, kind="thatch", pitch_deg=pitch, weather=tb.TIMBER, lod=lod)
    tb.lift_flare(mb, start, (0.0, 0.0), w * 0.5 - EAVE_M, d * 0.5 - EAVE_M, y_eave, 0.45, EAVE_M)
    tan_p = math.tan(math.radians(pitch))
    return y_eave + min(w, d) * 0.5 * tan_p, (max(w, d) - min(w, d)) * 0.5


STOCK_DYES = ("tb_cloth_red", "tb_cloth_indigo", "tb_cloth_sand", "tb_cloth_sea_blue", "tb_cloth_faded_teal")


def _shop_stock(mb, name: str, seed: int, hw: float, hd: float) -> None:
    """The shop's goods in the open front (M3-ENV-1327: the ground floors read as empty black voids from the lane): a
    lacquered counter across the front, shelves on the back panel with jars, cloth bolts and baskets, and cloth lengths
    hung from a pole. Its own rng, so the rest of the house is as it was."""
    rng = kc.rng_for(name + "_stock", seed)
    zc, zb = hd - 0.55, hd - 2.1  # the counter's line, the back panel's face
    _box(mb, (0.0, DECK_Y + 0.42, zc), (hw - 0.9, 0.42, 0.22), M_TIMBER, rng)
    _box(mb, (0.0, DECK_Y + 0.86, zc), (hw - 0.85, 0.03, 0.26), M_BLACK, rng, weather=tb.LACQUER)
    for y in (DECK_Y + 0.95, DECK_Y + 1.6):  # two shelves on brackets
        _box(mb, (0.0, y, zb + 0.18), (hw - 0.5, 0.025, 0.17), M_TIMBER, rng)
        x = -hw + 0.7
        while x < hw - 0.7:
            kind = rng.integers(3)
            if kind == 0:  # a lidded jar
                r = float(rng.uniform(0.09, 0.13))
                kc.tube(mb, np.array([[x, y + 0.025, zb + 0.18], [x, y + 0.025 + r * 2.4, zb + 0.18]]),
                        [r, r * 0.8], 8, mb.material(M_RED), weather=tb.LACQUER, cap_end=True,
                        variation=float(rng.random()))
                x += r * 2 + 0.08
            elif kind == 1:  # a bolt of cloth on its side
                dye = STOCK_DYES[int(rng.integers(len(STOCK_DYES)))]
                kc.tube(mb, np.array([[x, y + 0.11, zb + 0.06], [x, y + 0.11, zb + 0.32]]), 0.085, 8, mb.material(dye),
                        weather=tb.TIMBER, cap_start=True, cap_end=True)
                x += 0.22
            else:  # a lidded basket
                _box(mb, (x + 0.12, y + 0.13, zb + 0.18), (0.12, 0.11, 0.12), M_WOVEN, rng)
                x += 0.32
    # Goods on the counter: a tray of small jars and a folded cloth.
    for k in range(int(rng.integers(3, 6))):
        xk = float(rng.uniform(-hw + 1.2, hw - 1.2))
        kc.tube(mb, np.array([[xk, DECK_Y + 0.89, zc], [xk, DECK_Y + 1.05, zc]]), 0.05, 6, mb.material(M_RED),
                weather=tb.LACQUER, cap_end=True)
    _box(mb, (float(rng.uniform(-hw + 1.4, hw - 1.4)), DECK_Y + 0.93, zc), (0.22, 0.04, 0.16),
         STOCK_DYES[int(rng.integers(len(STOCK_DYES)))], rng)
    # Cloth lengths hung from a pole under the upper floor, in the dyes.
    pole_y = UPPER_FLOOR_Y - 0.25
    kc.tube(mb, np.array([[-hw + 0.3, pole_y, zc - 0.5], [hw - 0.3, pole_y, zc - 0.5]]), 0.025, 5, mb.material(M_TIMBER))
    for k in range(int(rng.integers(3, 5))):
        xk = float(rng.uniform(-hw + 0.6, hw - 0.6))
        drop = float(rng.uniform(0.9, 1.5))
        _box(mb, (xk, pole_y - drop * 0.5, zc - 0.5), (0.22, drop * 0.5, 0.012),
             STOCK_DYES[int(rng.integers(len(STOCK_DYES)))], rng)


def build_shophouse(name: str, *, lod: bool = False) -> kc.MeshBuilder:
    w, d, pitch_lo, pitch_up, balcony, seed = SHOPHOUSES[name]
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
    hw, hd = w * 0.5, d * 0.5
    # Piles, deck and the shop deck in front.
    for x in np.linspace(-hw + 0.2, hw - 0.2, 3 if lod else 4):
        for z in np.linspace(-hd + 0.2, hd + 1.3, 3 if lod else 5):
            if lod:
                kc.tube(mb, np.array([[x, RIVERBED_Y, z], [x, DECK_Y - 0.2, z]]), 0.16, 4, mb.material(M_PILE))
            else:
                kc.tube(mb, np.linspace([x, RIVERBED_Y, z], [x, DECK_Y - 0.2, z], 4), 0.16, 7, mb.material(M_PILE),
                        weather=tb.PILE, noise=noise, disp_m=0.03, disp_period_m=0.4, variation=float(rng.random()),
                        cap_end=True)
    if lod:
        _box(mb, (0, DECK_Y - 0.1, 0.75), (hw, 0.1, hd + 0.75), M_TIMBER, rng)
    else:
        village.deck(mb, -hw, hw, -hd, hd + 1.5, DECK_Y, rng, noise, weather=tb.TIMBER)
    # Ground floor: woven back and sides between lacquered corner posts; the front open.
    for x, z in ((-hw, -hd), (hw, -hd), (-hw, hd), (hw, hd), (-hw / 3, hd), (hw / 3, hd)):
        _box(mb, (x, (DECK_Y + WALL_TOP_Y) * 0.5, z), (0.11, (WALL_TOP_Y - DECK_Y) * 0.5, 0.11), M_BLACK, rng,
             weather=tb.LACQUER)
    for a, b in (((-hw, -hd), (hw, -hd)), ((-hw, -hd), (-hw, hd)), ((hw, -hd), (hw, hd))):
        village.panel(mb, a, b, DECK_Y, UPPER_FLOOR_Y, "kit_woven_panel", rng, thick=0.05)
    # The dark shop interior seen through the open front, and propped shutter-boards as awnings.
    village.panel(mb, (-hw + 0.15, hd - 2.2), (hw - 0.15, hd - 2.2), DECK_Y, UPPER_FLOOR_Y, "kit_interior_dark", rng,
                  thick=0.04)
    if not lod:
        _shop_stock(mb, name, seed, hw, hd)
        for k in range(3):
            xc = -hw + w / 6 + k * w / 3
            hinge = np.array([xc, UPPER_FLOOR_Y - 0.15, hd + 0.05])
            ang = math.radians(62.0 + rng.uniform(-6, 6))
            rot = kc.rot_x(-ang)
            c = hinge + rot @ np.array([0.0, -0.6, 0.0])
            _box(mb, c, (w / 6 - 0.1, 0.6, 0.03), M_TIMBER, rng, rot=rot)
            for sx in (-1.0, 1.0):  # prop sticks
                tip = hinge + rot @ np.array([sx * (w / 6 - 0.25), -1.15, 0.0])
                kc.tube(mb, np.array([[tip[0], DECK_Y + 1.0, hd + 0.05], tip]), 0.025, 4, mb.material(M_TIMBER))
    # Upper floor: the floor slab with a lacquered edge beam, timber walls, dark windows.
    _box(mb, (0, UPPER_FLOOR_Y + 0.1, 0.2), (hw + 0.2, 0.1, hd + 0.2), M_TIMBER, rng)
    _box(mb, (0, UPPER_FLOOR_Y - 0.05, hd + 0.4), (hw + 0.25, 0.16, 0.08), M_BLACK, rng, weather=tb.LACQUER)
    yu0, yu1 = UPPER_FLOOR_Y + 0.2, WALL_TOP_Y
    for a, b in (((-hw, -hd), (hw, -hd)), ((-hw, -hd), (-hw, hd)), ((hw, -hd), (hw, hd)), ((-hw, hd), (hw, hd))):
        village.panel(mb, a, b, yu0, yu1, "kit_timber", rng, thick=0.06)
    n_win = 1 if lod else 3
    for k in range(n_win):
        xc = -hw + w * (k + 0.5) / n_win
        _box(mb, (xc, (yu0 + yu1) * 0.5 + 0.1, hd + 0.04), (0.55, 0.6, 0.02), M_DARK, rng)
        if not lod:
            _box(mb, (xc, (yu0 + yu1) * 0.5 - 0.55, hd + 0.08), (0.7, 0.05, 0.08), M_BLACK, rng, weather=tb.LACQUER)
    if balcony:
        if lod:
            _box(mb, (0, UPPER_FLOOR_Y + 0.1, hd + 0.9), (hw - 0.3, 0.08, 0.7), M_TIMBER, rng)
        else:
            village.deck(mb, -hw + 0.3, hw - 0.3, hd + 0.2, hd + 1.6, UPPER_FLOOR_Y + 0.2, rng, noise, plank_w=0.22,
                         weather=tb.TIMBER, bearers=True)
            village.railing(mb, (-hw + 0.3, hd + 1.55), (hw - 0.3, hd + 1.55), UPPER_FLOOR_Y + 0.2, rng, noise,
                            weather=tb.TIMBER)
            tb.signboard(mb, (0.0, UPPER_FLOOR_Y + 0.75, hd + 1.65), 3.6, 0.8, 0.0, rng, strokes=8)
    else:
        if not lod:
            arm0 = np.array([hw + 0.1, UPPER_FLOOR_Y + 0.9, hd - 0.3])
            kc.tube(mb, np.array([arm0, arm0 + [1.2, 0, 0]]), 0.05, 6, mb.material(M_BLACK), weather=tb.LACQUER,
                    cap_end=True)
        tb.signboard(mb, (hw + 0.75, UPPER_FLOOR_Y - 0.9, hd - 0.3), 0.9, 3.2, 90.0, rng, lod=lod)
    tb.rename(mb, {"kit_woven_panel": M_WOVEN, "kit_interior_dark": M_DARK, "kit_timber": M_TIMBER})
    # Two-tier roof: the lower hip with flared eaves, a lacquered frieze, the upper hip above it.
    wl, dl = w + 2 * EAVE_M, d + 2 * EAVE_M
    _roof(mb, wl, dl, WALL_TOP_Y, pitch_lo, rng, noise, lod=lod)
    wu, du = w * 0.62, d * 0.68
    tan_lo = math.tan(math.radians(pitch_lo))
    y_gap = WALL_TOP_Y + (min(wl, dl) * 0.5 - wu * 0.5) * tan_lo
    y_up = y_gap + 0.7
    frieze_h = (y_up - y_gap + 0.25) * 0.5
    for sx, sz, hx, hz in ((0, 1, wu * 0.5 - 0.35, 0.05), (0, -1, wu * 0.5 - 0.35, 0.05),
                           (1, 0, 0.05, du * 0.5 - 0.35), (-1, 0, 0.05, du * 0.5 - 0.35)):
        c = (sx * (wu * 0.5 - 0.4), y_gap + frieze_h - 0.2, sz * (du * 0.5 - 0.4))
        _box(mb, c, (hx, frieze_h, hz), M_BLACK, rng, weather=tb.LACQUER)
    apex, ridge_half = _roof(mb, wu + 1.0, du + 1.0, y_up, pitch_up, rng, noise, lod=lod)
    tb.rename(mb, ROOF_SLOTS)
    if not lod:
        gold = mb.material("tb_gold_leaf")
        along_x = (wu + 1.0) >= (du + 1.0)
        for s in (-1.0, 1.0):
            p = np.array([s * ridge_half if along_x else 0.0, apex + 0.12, 0.0 if along_x else s * ridge_half])
            tb.revolve(mb, np.array([(0.12, 0.0), (0.16, 0.18), (0.08, 0.38), (0.0, 0.62)]), 0, 360, 10, gold,
                       weather=tb.LACQUER, outward=1.0)
            start = mb.vertex_count - 4 * 11
            mb.pos[start:] = (np.asarray(mb.pos[start:]) + p).tolist()
    return mb


def build_shophouse_pair(name: str) -> list[kc.MeshBuilder]:
    return [build_shophouse(name), build_shophouse(name, lod=True)]


def build_boardwalk(seed: int = 743) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("boardwalk_8m", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("boardwalk_8m" + ("-lod1" if lod else ""))
        for x in (-3.6, 0.0, 3.6):
            for z in (-1.3, 1.3):
                kc.tube(mb, np.linspace([x, RIVERBED_Y, z], [x, DECK_Y - 0.2, z], 2 if lod else 4), 0.15,
                        4 if lod else 7, mb.material(M_PILE), weather=tb.PILE, noise=None if lod else noise,
                        disp_m=0.03, variation=float(rng.random()), cap_end=True)
        if lod:
            _box(mb, (0, DECK_Y - 0.08, 0), (4.0, 0.08, 1.5), M_TIMBER, rng)
            _box(mb, (0, DECK_Y + 0.9, 1.45), (4.0, 0.04, 0.04), M_TIMBER, rng)
        else:
            village.deck(mb, -4.0, 4.0, -1.5, 1.5, DECK_Y, rng, noise, plank_w=0.26, weather=tb.TIMBER)
            village.railing(mb, (-4.0, 1.45), (4.0, 1.45), DECK_Y, rng, noise, weather=tb.TIMBER)
        out.append(tb.rename(mb))
    return out


def build_signboard_gilded(seed: int = 744) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("signboard_gilded", seed)
        mb = kc.MeshBuilder("signboard_gilded" + ("-lod1" if lod else ""))
        for x in (-0.58, 0.58):
            kc.tube(mb, np.array([[x, 0.0, 0.0], [x, 4.5, 0.0]]), 0.07, 4 if lod else 8, mb.material(M_BLACK),
                    weather=tb.LACQUER, cap_end=True)
        kc.rounded_block(mb, (0.0, 4.35, 0.0), (0.75, 0.06, 0.09), mb.material(M_RED), radius=0.02, seg=1,
                         weather=tb.LACQUER)
        tb.signboard(mb, (0.0, 2.65, 0.0), 0.9, 3.2, 0.0, rng, lod=lod)
        out.append(mb)
    return out


TARGETS = {
    "boardwalk_8m": build_boardwalk,
    "signboard_gilded": build_signboard_gilded,
    **{name: (lambda name=name: build_shophouse_pair(name)) for name in SHOPHOUSES},
}
