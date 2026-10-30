"""Ansedra, the holy city on its mirror lagoon (M4-A2P-043; ansedra.md §3), built from act1-chapters' greybox
(game/levels/ch13/ansedra/ansedra_layout.json), read here so the stone follows the greybox if it moves. Pure numpy.

The city's greybox is the Sunken Vey's grammar: 3.6 m causeways railed at +-2 m (the rails stopping short of the
isles), paved isles walled low, the water at -0.3. So the walks are vey_zones.py's builders (each causeway at its own
length, its balustrade on its rail blocks, the isles paved, their walls balustrades) re-dressed in the Order's white
marble and gilt (`_ORDER_SKIN`: the Lit Age ceramic and stone go to order marble, the conduits and their copper to a gilt
moulding). On them, built on their greybox blocks:

  ansedra_walks_n    the outer moorings, the north causeway, the central island, the Sanctum causeway and its isle,
                     their balustrades and lamp posts (white marble shafts, red-lacquer collars, a salt-glass lantern
                     round a bound core, gilt cap: the Order's lamps never flicker)
  ansedra_walks_we   the west causeway and Corran's isle, the east causeway and the Archive's isle, and theirs
  ansedra_buildings  Sefir's house (white walls, red-lacquer door and shutters, a gilt bowl-dome on its roof), Corran's
                     old house, the Lamp Archive's and the Sanctum's domes (a square white base storey on the greybox's
                     footprint with the door on the trigger's side, the kit's lacquer drums and gilt bowl over it), the
                     polers' two barges at the moorings
  ansedra_ground     the lagoon's bed (vey_zones' bed, round this greybox's walks)

Origin at the zone's origin (the greybox's frame); the walks' tops at y 0 as the greybox's.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ansedra as an
import kit_common as kc
import lowlight as ll
import vey_zones as vz

ROOT = Path(__file__).resolve().parents[4]
LAYOUT = ROOT / "game" / "levels" / "ch13" / "ansedra" / "ansedra_layout.json"
TRI_BUDGET = {"ansedra_walks_n": (90000, 6000), "ansedra_walks_we": (90000, 6000), "ansedra_buildings": (60000, 4000),
              "ansedra_ground": (40000, 2500)}

WATER_Y = -0.3
ORDER = ("Moorings", "Centre", "CorranIsle", "ArchiveIsle", "SanctumIsle", "CausewayN", "CausewayW", "CausewayE",
         "CausewaySanctum")
PAVED = ("Moorings", "Centre", "CorranIsle", "ArchiveIsle", "SanctumIsle")
GROUPS = {"ansedra_walks_n": ("Moorings", "CausewayN", "Centre", "CausewaySanctum", "SanctumIsle"),
          "ansedra_walks_we": ("CausewayW", "CorranIsle", "CausewayE", "ArchiveIsle")}
# The Vey's materials to the Order's: Lit Age ceramic and grey stone go to order marble; the bound-light conduit, its
# salt-glass sheath and its copper brackets to one gilt moulding (no conduits in Ansedra's causeways: its lamps hold it).
_ORDER_SKIN = {ll.M_CERAMIC: an.M_STONE, ll.M_STONE: an.M_STONE, ll.M_CONDUIT: an.M_GILT, ll.M_GLASS: an.M_GILT,
               ll.M_COPPER: an.M_GILT}
M_WALL = "kit_whitewash"
DOME_BASE_H = 3.6  # a dome's square base storey over its isle (the door in it)
DOOR_W = 2.4
DOOR_H = 3.0
LAMP_TOP = 2.9
HOUSE_DOME_S = 0.48


def layout() -> dict:
    return json.loads(LAYOUT.read_text(encoding="utf-8"))


def blocks() -> dict:
    return {b["id"]: b for b in layout()["blocks"]}


def _box(b: dict):
    (x, y, z), (sx, sy, sz) = b["pos"], b["size"]
    return x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z - sz / 2, z + sz / 2


def _skin(mb: kc.MeshBuilder) -> kc.MeshBuilder:
    """The Vey's slots renamed to the Order's (a merge maps materials by name)."""
    mb.materials = [_ORDER_SKIN.get(m, m) for m in mb.materials]
    return mb


def _lamp(mb, rng, b: dict, lod: bool) -> None:
    """An Order lamp post on its greybox block: a white marble shaft on a stepped base, a red-lacquer collar, a
    salt-glass lantern round a bound core (still light), a gilt cap and finial."""
    x, z = b["pos"][0], b["pos"][2]
    y0 = _box(b)[2]
    marble, gilt = mb.material(an.M_STONE), mb.material(an.M_GILT)
    kc.rounded_block(mb, (x, y0 + 0.35, z), (0.24, 0.35, 0.24), marble, radius=0.03, seg=1)
    kc.tube(mb, np.array([[x, y0 + 0.7, z], [x, LAMP_TOP - 0.45, z]]), np.array([0.1, 0.08]), 5 if lod else 10,
            marble, weather=an.STONE_W)
    if lod:
        kc.rounded_block(mb, (x, LAMP_TOP - 0.2, z), (0.15, 0.2, 0.15), gilt, radius=0.05, seg=1)
        return
    kc.tube(mb, np.array([[x, LAMP_TOP - 0.62, z], [x, LAMP_TOP - 0.48, z]]), 0.11, 10, mb.material(an.M_LACQUER))
    kc.rounded_block(mb, (x, LAMP_TOP - 0.2, z), (0.14, 0.2, 0.14), mb.material(an.M_GLASS), radius=0.12, seg=2)
    kc.rounded_block(mb, (x, LAMP_TOP - 0.22, z), (0.05, 0.08, 0.05), mb.material(an.M_CORE), radius=0.04, seg=1)
    for dx, dz in ((1, 1), (1, -1), (-1, 1), (-1, -1)):  # the lantern's gilt frame
        kc.tube(mb, np.array([[x + dx * 0.13, LAMP_TOP - 0.42, z + dz * 0.13],
                              [x + dx * 0.13, LAMP_TOP + 0.0, z + dz * 0.13]]), 0.012, 4, gilt)
    kc.tube(mb, np.array([[x, LAMP_TOP - 0.02, z], [x, LAMP_TOP + 0.12, z]]), np.array([0.19, 0.02]), 10, gilt,
            cap_end=True)
    kc.tube(mb, np.array([[x, LAMP_TOP + 0.12, z], [x, LAMP_TOP + 0.38, z]]), np.array([0.025, 0.006]), 6, gilt)


def build_walks(name: str, seed: int) -> list[kc.MeshBuilder]:
    bl = blocks()
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        for bid in GROUPS[name]:
            b = bl[bid]
            sub = kc.MeshBuilder(bid)
            (vz._paved if bid in PAVED else vz._gallery)(sub, rng, noise, b, bl, lod, ORDER)
            rot, off = vz._xform(b)
            mb.merge(_skin(sub), rot, off)
            for w in bl.values():  # its walls (balustrades) and its lamps
                if w["id"].startswith(bid + "Wall"):
                    sub = kc.MeshBuilder(w["id"])
                    vz._parapet(sub, rng, w, lod)
                    rot, off = vz._xform(w)
                    mb.merge(_skin(sub), rot, off)
                elif w["id"].startswith(bid + "Lamp"):
                    _lamp(mb, rng, w, lod)
        out.append(mb)
    return out


# ---- the buildings -------------------------------------------------------------------------------------------------
def _door(mb, x: float, z: float, nx: float, nz: float, lod: bool, *, w: float = DOOR_W, h: float = DOOR_H) -> None:
    """A red-lacquer double door in a white marble frame with a gilt lintel, its face at (x, z) facing (nx, nz)."""
    sx, sz = -nz, nx  # along the face
    lac, gilt, marble = mb.material(an.M_LACQUER), mb.material(an.M_GILT), mb.material(an.M_STONE)

    def blk(a, y, out, half, mat):
        c = (x + sx * a + nx * out, y, z + sz * a + nz * out)
        hh = (half[0] * abs(sx) + half[2] * abs(nx), half[1], half[0] * abs(sz) + half[2] * abs(nz))
        kc.rounded_block(mb, c, hh, mat, radius=0.02, seg=1)

    blk(0.0, h / 2, 0.02, (w / 2, h / 2, 0.04), lac)
    if lod:
        return
    for a in (-1.0, 1.0):
        blk(a * (w / 2 + 0.15), h / 2, 0.08, (0.15, h / 2 + 0.1, 0.1), marble)
        blk(a * w / 4, h * 0.55, 0.07, (0.06, 0.06, 0.02), gilt)  # the door rings
    blk(0.0, h + 0.2, 0.1, (w / 2 + 0.35, 0.2, 0.12), marble)
    blk(0.0, h + 0.45, 0.12, (w / 2 + 0.4, 0.05, 0.12), gilt)
    blk(0.0, h / 2, 0.065, (0.01, h / 2 - 0.05, 0.01), gilt)  # the meeting stile


def _base_storey(mb, rng, noise, b: dict, door_side: tuple[float, float], lod: bool, height: float) -> None:
    """A square white base storey on the greybox's footprint: dressed courses, a marble plinth and cornice with a gilt
    band, pilasters at the corners and the door on `door_side` (a unit x/z out of the block)."""
    x0, x1, y0, _, z0, z1 = _box(b)
    cx, cz, hx, hz = (x0 + x1) / 2, (z0 + z1) / 2, (x1 - x0) / 2, (z1 - z0) / 2
    wall, marble, gilt = mb.material(M_WALL), mb.material(an.M_STONE), mb.material(an.M_GILT)
    kc.rounded_block(mb, (cx, 0.25, cz), (hx + 0.1, 0.25, hz + 0.1), marble, radius=0.03, seg=1, weather=an.STONE_W)
    kc.rounded_block(mb, (cx, (0.5 + height) / 2, cz), (hx, (height - 0.5) / 2, hz), wall, radius=0.04, seg=1,
                     noise=None if lod else noise, disp_m=0.005, weather=an.STONE_W)
    kc.rounded_block(mb, (cx, height + 0.15, cz), (hx + 0.25, 0.15, hz + 0.25), marble, radius=0.03, seg=1)
    if lod:
        return
    kc.rounded_block(mb, (cx, height - 0.05, cz), (hx + 0.06, 0.06, hz + 0.06), gilt, radius=0.01, seg=1)
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            kc.rounded_block(mb, (cx + sx * (hx - 0.2), (0.5 + height) / 2, cz + sz * (hz - 0.2)),
                             (0.28, (height - 0.5) / 2, 0.28), marble, radius=0.03, seg=1)
    nx, nz = door_side
    _door(mb, cx + nx * hx, cz + nz * hz, nx, nz, lod)


def _dome_over(mb, rng, b: dict, base_h: float, lod: bool) -> None:
    """The kit's bowl-dome (lacquer drums, gilt bowl and spire) over a square base, its bottom drum inside the base's
    top (scale from the footprint)."""
    x0, x1, _, _, z0, z1 = _box(b)
    s = (min(x1 - x0, z1 - z0) / 2 - 0.4) / an.DRUMS[0][0]
    sub = kc.MeshBuilder("dome")
    an._dome(sub, 0.0, 0.0, s, lod, rng, sides=12 if lod else 32, windows=False, island=False)
    mb.merge(sub, None, ((x0 + x1) / 2, base_h + 0.3 - an.PLINTH_TOP * s, (z0 + z1) / 2))


def _house(mb, rng, noise, b: dict, door_at: tuple[float, float], lod: bool, *, dome: dict | None = None) -> None:
    """A white city house on its block: whitewashed walls over a marble plinth, a gilt band at the cornice, red-lacquer
    shutters on dark windows, the door toward its mark, a flat roof (a small gilt bowl-dome on it for Sefir's)."""
    x0, x1, y0, y1, z0, z1 = _box(b)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    dx, dz = door_at[0] - cx, door_at[1] - cz
    side = (0.0, math.copysign(1.0, dz)) if abs(dz) / (z1 - z0) >= abs(dx) / (x1 - x0) else (math.copysign(1.0, dx), 0.0)
    sub_b = dict(b)
    _base_storey(mb, rng, noise, sub_b, side, lod, y1 - 0.3)
    if not lod:  # windows in the long walls, with red-lacquer shutters
        lac, dark = mb.material(an.M_LACQUER), mb.material("kit_interior_dark")
        for (nx, nz) in ((0.0, 1.0), (0.0, -1.0), (1.0, 0.0), (-1.0, 0.0)):
            length = (x1 - x0) if nx == 0.0 else (z1 - z0)
            for k in range(max(1, int(length // 3.0))):
                t = -length / 2 + (k + 0.5) * length / max(1, int(length // 3.0))
                if (nx, nz) == side and abs(t) < DOOR_W:
                    continue
                for y in ((2.0, 4.2) if y1 > 5.5 else (2.4,)):
                    px = cx + (t if nx == 0.0 else nx * (x1 - x0) / 2)
                    pz = cz + (t if nz == 0.0 else nz * (z1 - z0) / 2)
                    hw = (0.4, 0.55, 0.03) if nx == 0.0 else (0.03, 0.55, 0.4)
                    kc.rounded_block(mb, (px + nx * 0.01, y, pz + nz * 0.01), hw, dark, radius=0.0, seg=1)
                    for a in (-1.0, 1.0):
                        o = (a * 0.62, 0.0) if nx == 0.0 else (0.0, a * 0.62)
                        sh = (0.2, 0.58, 0.03) if nx == 0.0 else (0.03, 0.58, 0.2)
                        kc.rounded_block(mb, (px + o[0] + nx * 0.06, y, pz + o[1] + nz * 0.06), sh, lac, radius=0.01,
                                         seg=1)
    if dome is not None:
        dx0, dx1, dy0, _, dz0, dz1 = _box(dome)
        sub = kc.MeshBuilder("hdome")
        an._dome(sub, 0.0, 0.0, HOUSE_DOME_S, lod, rng, sides=12 if lod else 28, windows=False, island=False)
        mb.merge(sub, None, ((dx0 + dx1) / 2, y1 - an.PLINTH_TOP * HOUSE_DOME_S, (dz0 + dz1) / 2))


def _barge(mb, rng, noise, b: dict, lod: bool) -> None:
    """A poler's barge on its greybox block: a black-lacquer hull with a gilt sheer line, timber deck at the block's top,
    the bow and stern swept up, a mooring pole and a dark bow lantern (the polers work by day)."""
    x0, x1, y0, y1, z0, z1 = _box(b)
    cx, cz, hx, hz = (x0 + x1) / 2, (z0 + z1) / 2, (x1 - x0) / 2, (z1 - z0) / 2
    black, gilt, deck = mb.material(an.M_BLACK), mb.material(an.M_GILT), mb.material(an.M_DECK)
    # The hull: a lofted U section along Z, narrowing and sweeping up at bow and stern (both faces: seen from the deck
    # and from the water).
    n = 7 if lod else 21
    rows = []
    for k in range(n):
        t = -1.0 + 2.0 * k / (n - 1)
        lift = 0.5 * max(0.0, abs(t) - 0.6) ** 2 / 0.16
        w = hx * (1.0 - 0.55 * max(0.0, abs(t) - 0.5) ** 1.5 / 0.35)
        top, bot = y1 + lift, y0 + lift * 0.8
        z = cz + t * hz
        rows.append([(cx - w, top, z), (cx - w * 0.97, bot + 0.18, z), (cx - w * 0.6, bot, z), (cx + w * 0.6, bot, z),
                     (cx + w * 0.97, bot + 0.18, z), (cx + w, top, z)])
    grid = np.array(rows, float)
    for flip in (False, True):
        kc.quad_strip(mb, grid, black, uv=grid[..., [2, 1]] / 1.5, col=(0, 0, 0, 0.2), uv2=(0.9, 0.5), flip=flip)
    kc.rounded_block(mb, (cx, y1 + 0.02, cz), (hx * 0.85, 0.03, hz * 0.62), deck, radius=0.01, seg=1)
    if lod:
        return
    for sxs in (-1.0, 1.0):
        kc.tube(mb, np.array([[cx + sxs * (hx + 0.01), y1 - 0.05, cz - hz * 0.7], [cx + sxs * (hx + 0.01), y1 - 0.05,
                                                                                   cz + hz * 0.7]]), 0.025, 4, gilt)
    pole = np.array([[cx + hx * 0.5, y1 - 0.2, cz + hz * 0.3], [cx + hx * 0.2, y1 + 3.6, cz + hz * 0.1]])
    kc.tube(mb, pole, 0.035, 6, deck)
    kc.rounded_block(mb, (cx, y1 + 0.75, cz - hz * 0.92), (0.1, 0.14, 0.1), mb.material(an.M_GLASS), radius=0.08,
                     seg=1)


def build_buildings(seed: int = 1860) -> list[kc.MeshBuilder]:
    lay = layout()
    bl = {b["id"]: b for b in lay["blocks"]}
    marks = lay["marks"]
    trig = {t["id"]: t["at"] for t in lay["triggers"]}
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ansedra_buildings", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("ansedra_buildings" + ("-lod1" if lod else ""))
        _house(mb, rng, noise, bl["SefirHouse"], (marks["sefir_door"][0], marks["sefir_door"][2]), lod,
               dome=bl["SefirHouseDome"])
        _house(mb, rng, noise, bl["CorranHouse"], (marks["corran_house"][0], marks["corran_house"][2]), lod)
        for dome_id, trig_id in (("ArchiveIsleDome", "to_archive"), ("SanctumIsleDome", "to_sanctum")):
            d = bl[dome_id]
            tx, tz = trig[trig_id][0] - d["pos"][0], trig[trig_id][2] - d["pos"][2]
            side = (math.copysign(1.0, tx), 0.0) if abs(tx) > abs(tz) else (0.0, math.copysign(1.0, tz))
            _base_storey(mb, rng, noise, d, side, lod, DOME_BASE_H)
            _dome_over(mb, rng, d, DOME_BASE_H, lod)
        for bid in ("BargeA", "BargeB"):
            _barge(mb, rng, noise, bl[bid], lod)
        out.append(mb)
    return out


def build_ground(seed: int = 1861) -> list[kc.MeshBuilder]:
    bl = blocks()
    wb = bl["Water"]
    x0, x1 = wb["pos"][0] - wb["size"][0] / 2, wb["pos"][0] + wb["size"][0] / 2
    z0, z1 = wb["pos"][2] - wb["size"][2] / 2, wb["pos"][2] + wb["size"][2] / 2
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ansedra_ground", seed)
        noise = kc.Noise3(rng)
        h = vz.bed_height(noise, bl, ORDER)
        mb = kc.MeshBuilder("ansedra_ground" + ("-lod1" if lod else ""))
        cell = 1.5 * (4.0 if lod else 1.0)
        xs = np.linspace(x0, x1, int(round((x1 - x0) / cell)) + 1)
        zs = np.linspace(z0, z1, int(round((z1 - z0) / cell)) + 1)
        X, Z = np.meshgrid(xs, zs)
        Y = h(X, Z)
        P = np.stack([X, Y, Z], -1)
        brk = noise.fbm(P / 2.5, 2)
        col = np.stack([np.full_like(Y, 0.15), np.full_like(Y, 0.1), np.full_like(Y, 1.0), 0.3 + 0.4 * brk], -1)
        kc.quad_strip(mb, P, mb.material(vz.M_SILT), uv=np.stack([X, Z], -1) / 4.0, col=col, uv2=np.array([0.85, 0.5]),
                      flip=True)
        out.append(mb)
    return out


TARGETS = {
    "ansedra_walks_n": lambda: build_walks("ansedra_walks_n", 1862),
    "ansedra_walks_we": lambda: build_walks("ansedra_walks_we", 1863),
    "ansedra_buildings": build_buildings,
    "ansedra_ground": build_ground,
}
