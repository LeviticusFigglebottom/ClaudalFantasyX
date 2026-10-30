"""The Sunken Vey's walks and lagoon bed (M4-A2P-041; lowlight.md §5), built from act1-chapters' greybox
(game/levels/ch11/sunken_vey/sunken_vey_layout.json), read here so the stone follows the greybox if it moves. Pure numpy.

The kit's 6 m `vey_gallery_walk_6m` carries its balustrade along its whole length, but the greybox's rails stop 3.6 m
short of every strip's end (the junctions stay open) and its strips are not whole multiples of 6 m. So each walk is built
here at its block's own length, its balustrade exactly on its rail blocks, in the gallery walk's language (lowlight.py):
ceramic slabs flat-shaded on the arcade's top course, a cornice with the bound-light conduit along it, the upper arches
of the drowned arcade dropping into the lagoon on each side.

  sunken_vey_walks_w  the landing (paved, its west parapet on LandingBoundW) and the inbound galleries (GalleryIn0-2)
  sunken_vey_court    the conduit court (paved; its parapets on the CourtWall* blocks; the conduit stand on `Conduit`,
                      the housing itself is the kit's `conduit_housing`), the side gallery and the fig end (paved)
  sunken_vey_walks_e  the outbound galleries (GalleryOut0-1) and Lowlight's gate on GateBound: a ceramic facade with a
                      pointed doorway into the dark
  sunken_vey_ground   the lagoon's bed under the turquoise water: silt and drowned paving 2-3 m down, the drowned
                      street conduits still lit along it ("conduit light lies on the drowned floor")

Origin at the zone's origin (the greybox's frame); the walks' tops at y 0 as the greybox's.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import kit_common as kc
import lowlight as ll

ROOT = Path(__file__).resolve().parents[4]
LAYOUT = ROOT / "game" / "levels" / "ch11" / "sunken_vey" / "sunken_vey_layout.json"
TRI_BUDGET = {"sunken_vey_walks_w": (90000, 6000), "sunken_vey_court": (90000, 6000),
              "sunken_vey_walks_e": (90000, 6000), "sunken_vey_ground": (40000, 2500)}

WATER_Y = -0.3  # the greybox's Water block top
SLAB_M = 1.2
M_SILT = "kit_vey_silt"
ARCH_BAY_M = 6.0
BED_Y = -2.6
BED_VARY_M = 0.35
PARAPET_H = 0.95
COURSE_FOOT_Y = -2.4  # a paved block's stone body reaches the bed
CONDUIT_Y = -0.32  # the conduit along a walk's cornice, under the slabs' edge
FLAG_PAVED = ("Landing", "Court", "FigEnd")
# The order the surfaces are laid in: a later surface leaves out its slabs over an earlier one (no two decks in one place).
ORDER = ("Landing", "Court", "FigEnd", "GalleryIn0", "GalleryIn1", "GalleryIn2", "GallerySide", "GalleryOut0",
         "GalleryOut1")
GROUPS = {"sunken_vey_walks_w": ("Landing", "GalleryIn0", "GalleryIn1", "GalleryIn2"),
          "sunken_vey_court": ("Court", "FigEnd", "GallerySide"),
          "sunken_vey_walks_e": ("GalleryOut0", "GalleryOut1")}
GATE_W = 4.2  # Lowlight's doorway
GATE_H = 6.4
FACADE_HALF = 11.0
FACADE_H = 13.0


def layout() -> dict:
    return json.loads(LAYOUT.read_text(encoding="utf-8"))


def blocks() -> dict:
    return {b["id"]: b for b in layout()["blocks"]}


def _xform(b: dict):
    return kc.rot_y(math.radians(float(b.get("yaw", 0.0)))), (b["pos"][0], 0.0, b["pos"][2])


def _to_local(b: dict, x: float, z: float) -> tuple[float, float]:
    a = math.radians(float(b.get("yaw", 0.0)))
    dx, dz = x - b["pos"][0], z - b["pos"][2]
    return dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)


def _covers(b: dict, x: float, z: float, pad: float = 0.0) -> bool:
    lx, lz = _to_local(b, x, z)
    return abs(lx) <= b["size"][0] / 2 + pad and abs(lz) <= b["size"][2] / 2 + pad


def _earlier(bid: str, bl: dict) -> list[dict]:
    return [bl[i] for i in ORDER[:ORDER.index(bid)] if i in bl]


def _world(b: dict, lx: float, lz: float) -> tuple[float, float]:
    a = math.radians(float(b.get("yaw", 0.0)))
    return b["pos"][0] + lx * math.cos(a) + lz * math.sin(a), b["pos"][2] - lx * math.sin(a) + lz * math.cos(a)


def _flat_top(mb, v0: int) -> None:
    n = np.asarray(mb.nrm[v0:])
    n[n[:, 1] > 0.85] = (0.0, 1.0, 0.0)  # flat-shaded tops (no pillows)
    mb.nrm[v0:] = n.tolist()


def _rails(b: dict, bl: dict) -> list[tuple[float, float, float]]:
    """The block's rail blocks in its own frame: (side z, from x, to x)."""
    out = []
    for r in bl.values():
        if not r["id"].startswith(b["id"] + "Rail"):
            continue
        lx, lz = _to_local(b, r["pos"][0], r["pos"][2])
        out.append((math.copysign(ll.WALK_RAIL_Z, lz), lx - r["size"][0] / 2, lx + r["size"][0] / 2))
    return out


def _balustrade(mb, rng, x0: float, x1: float, z: float, h: float, lod: bool, *, thick: float = 0.16) -> None:
    cer = mb.material(ll.M_CERAMIC)
    hl, cx = (x1 - x0) / 2, (x0 + x1) / 2
    if lod:
        kc.rounded_block(mb, (cx, h * 0.5, z), (hl, h * 0.5, thick * 0.9), cer, radius=0.03, seg=1)
        return
    kc.rounded_block(mb, (cx, 0.05, z), (hl, 0.05, thick), cer, radius=0.015, seg=1, weather=ll.CERAMIC)
    kc.rounded_block(mb, (cx, h - 0.05, z), (hl + 0.02, 0.05, thick + 0.02), cer, radius=0.02, seg=1,
                     weather=ll.CERAMIC)
    n = max(1, int(round((x1 - x0) / 0.4)))
    for k in range(n):
        x = x0 + (k + 0.5) * (x1 - x0) / n
        if rng.random() < 0.08:
            continue  # a baluster lost
        kc.tube(mb, np.array([[x, 0.1, z], [x, h - 0.1, z]]), np.array([0.05, 0.035]) * (thick / 0.16) ** 0.5, 6, cer,
                weather=ll.CERAMIC)
    for x in (x0 + 0.12, x1 - 0.12):  # a newel at each end
        kc.rounded_block(mb, (x, h * 0.5, z), (0.12, h * 0.5, thick + 0.03), cer, radius=0.02, seg=1,
                         weather=ll.CERAMIC)


def _conduit(mb, a, b, lod: bool) -> None:
    """The bound light in its salt-glass sheath on copper brackets (the kit's conduit_run, any length)."""
    pts = np.array([a, b], float)
    kc.tube(mb, pts, 0.05, 4 if lod else 8, mb.material(ll.M_CONDUIT))
    if lod:
        return
    kc.tube(mb, pts, 0.075, 8, mb.material(ll.M_GLASS))
    d = pts[1] - pts[0]
    n = max(2, int(np.linalg.norm(d) / 1.6) + 1)
    for t in np.linspace(0.04, 0.96, n):
        p = pts[0] + d * t
        kc.rounded_block(mb, tuple(p), (0.06, 0.09, 0.06), mb.material(ll.M_COPPER), radius=0.02, seg=1)


def _slabs(mb, rng, noise, b: dict, earlier: list[dict], hx: float, hz: float, mat: str, *, rows_z=None) -> None:
    """Flags over the block's top, 1.2 m-ish, flat-shaded; none where an earlier surface already lies."""
    nx = max(1, int(round(2 * hx / SLAB_M)))
    zs = rows_z if rows_z is not None else [(-hz + (k + 0.5) * 2 * hz / max(1, int(round(2 * hz / SLAB_M))))
                                           for k in range(max(1, int(round(2 * hz / SLAB_M))))]
    dz = (2 * hz / len(zs)) * 0.5
    sx = hx / nx
    for i in range(nx):
        x = -hx + (2 * i + 1) * sx
        for z in zs:
            wx, wz = _world(b, x, z)
            if any(_covers(e, wx, wz) for e in earlier):
                continue
            dy = rng.normal(0.0, 0.005) + (0.012 if rng.random() < 0.07 else 0.0)
            v0 = mb.vertex_count
            kc.rounded_block(mb, (x, -0.06 + dy, z), (sx - 0.015, 0.06, dz - 0.015), mb.material(mat),
                             rot=kc.rot_y(rng.normal(0, 0.005)), radius=0.015, seg=1, noise=noise, disp_m=0.003,
                             weather=ll.CERAMIC if mat == ll.M_CERAMIC else ll.STONE, variation=float(rng.random()))
            _flat_top(mb, v0)


def _gallery(mb, rng, noise, b: dict, bl: dict, lod: bool) -> None:
    """One gallery walk at its block's length, in its own frame (axis X)."""
    hl, hw = b["size"][0] / 2, ll.WALK_HALF_W
    cer, stone = mb.material(ll.M_CERAMIC), mb.material(ll.M_STONE)
    rails = _rails(b, bl)
    if lod:
        kc.rounded_block(mb, (0.0, -0.15, 0.0), (hl, 0.15, hw + 0.2), cer, radius=0.03, seg=1)
        kc.rounded_block(mb, (0.0, -1.3, 0.0), (hl, 1.0, hw), stone, radius=0.05, seg=1)
        for z, x0, x1 in rails:
            _balustrade(mb, rng, x0, x1, z, ll.WALK_RAIL_H, True)
        return
    # The bedding under the slabs (the joints read as grooves, never as slits onto the water), then the slabs.
    kc.rounded_block(mb, (0.0, -0.14, 0.0), (hl, 0.02, hw), stone, radius=0.01, seg=1)
    _slabs(mb, rng, noise, b, _earlier(b["id"], bl), hl, hw, ll.M_CERAMIC, rows_z=(-0.9, 0.9))
    for sz in (-1.0, 1.0):  # the cornice and the arcade's top course, the conduit along the cornice
        kc.rounded_block(mb, (0.0, -0.18, sz * (hw + 0.1)), (hl, 0.08, 0.16), cer, radius=0.02, seg=1,
                         weather=ll.CERAMIC)
        kc.rounded_block(mb, (0.0, -0.45, sz * (hw - 0.05)), (hl, 0.2, 0.22), stone, radius=0.03, seg=1, noise=noise,
                         disp_m=0.01, weather=ll.STONE)
        _conduit(mb, (-hl + 0.3, CONDUIT_Y, sz * (hw + 0.34)), (hl - 0.3, CONDUIT_Y, sz * (hw + 0.34)), lod)
    for z, x0, x1 in rails:
        _balustrade(mb, rng, x0, x1, z, ll.WALK_RAIL_H, lod)
    # The drowned arcade's upper arches on each side, a bay every ~6 m, its piers into the water.
    n = max(1, int(round(2 * hl / ARCH_BAY_M)))
    w = 2 * hl / n
    r = w / 2 - 0.8
    t = np.linspace(0.0, math.pi, 13)
    for sz in (-1.0, 1.0):
        zf = sz * (hw + 0.05)
        for k in range(n):
            cx = -hl + (k + 0.5) * w
            arch = np.stack([cx + np.cos(t) * r, -0.65 - (1.0 - np.sin(t)) * 1.35, np.full_like(t, zf)], -1)
            kc.tube(mb, arch, 0.14, 6, cer, weather=ll.CERAMIC)
            for sx in (-1.0, 1.0):
                kc.rounded_block(mb, (cx + sx * (r + 0.1), -0.75, zf), (0.6, 0.12, 0.22), cer, radius=0.02, seg=1,
                                 weather=ll.CERAMIC)
        for k in range(n + 1):
            kc.rounded_block(mb, (-hl + k * w, -1.4, zf), (0.35, 0.9, 0.25), stone, radius=0.04, seg=1, noise=noise,
                             disp_m=0.01, weather=ll.STONE)


def _paved(mb, rng, noise, b: dict, bl: dict, lod: bool) -> None:
    """A paved block (the landing, the court, the fig end): stone flags inside a ceramic border, the stone body down to
    the bed with a cornice round it, the conduit along the cornice."""
    hx, hz = b["size"][0] / 2, b["size"][2] / 2
    cer, stone = mb.material(ll.M_CERAMIC), mb.material(ll.M_STONE)
    body_h = (0.0 - COURSE_FOOT_Y) / 2
    kc.rounded_block(mb, (0.0, -0.12 - body_h, 0.0), (hx - 0.05, body_h - 0.12, hz - 0.05), stone, radius=0.05, seg=1,
                     noise=None if lod else noise, disp_m=0.015, weather=ll.STONE, variation=float(rng.random()))
    if lod:
        kc.rounded_block(mb, (0.0, -0.06, 0.0), (hx, 0.06, hz), stone, radius=0.02, seg=1)
        return
    border = 0.6
    for sx, sz in ((1, 0), (-1, 0), (0, 1), (0, -1)):  # the ceramic border course and the cornice under it
        c = (sx * (hx - border / 2), -0.06, sz * (hz - border / 2))
        h = (border / 2 - 0.01, 0.06, hz - 0.01) if sx else (hx - border - 0.01, 0.06, border / 2 - 0.01)
        v0 = mb.vertex_count
        kc.rounded_block(mb, c, h, cer, radius=0.015, seg=1, weather=ll.CERAMIC, variation=float(rng.random()))
        _flat_top(mb, v0)
        cc = (sx * (hx + 0.08), -0.2, sz * (hz + 0.08))
        ch = (0.14, 0.08, hz + 0.2) if sx else (hx + 0.2, 0.08, 0.14)
        kc.rounded_block(mb, cc, ch, cer, radius=0.02, seg=1, weather=ll.CERAMIC)
    earlier = _earlier(b["id"], bl)
    sub = dict(b, size=[b["size"][0] - 2 * border, b["size"][1], b["size"][2] - 2 * border])
    _slabs(mb, rng, noise, sub, earlier, hx - border, hz - border, ll.M_STONE)
    # The conduit along the cornice, on the sides no gallery leaves from.
    for sx, sz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if sx:
            a, c = (sx * (hx + 0.32), CONDUIT_Y, -hz + 0.3), (sx * (hx + 0.32), CONDUIT_Y, hz - 0.3)
        else:
            a, c = (-hx + 0.3, CONDUIT_Y, sz * (hz + 0.32)), (hx - 0.3, CONDUIT_Y, sz * (hz + 0.32))
        _conduit(mb, a, c, lod)


def _parapet(mb, rng, w: dict, lod: bool) -> None:
    """A court wall (or the landing's bound) as a balustrade on its block, in the block's frame."""
    hx, hz = w["size"][0] / 2, w["size"][2] / 2
    if hz > hx:  # run it along its long side
        rot = kc.rot_y(math.pi / 2)
        sub = kc.MeshBuilder("p")
        _balustrade(sub, rng, -hz, hz, 0.0, PARAPET_H, lod, thick=min(0.22, hx * 0.5))
        mb.merge(sub, rot)
        return
    _balustrade(mb, rng, -hx, hx, 0.0, PARAPET_H, lod, thick=min(0.22, hz * 0.5))


def _conduit_stand(mb, rng, noise, c: dict, lod: bool) -> None:
    """The court's conduit stand (the greybox's Conduit, 3 x 3 x 0.8): a ceramic pier-wall on a stone foot, three conduit
    lines rising out of the lagoon behind it and over its top into the court's north cornice; the kit's
    `conduit_housing` (the mark) is set on its face at chest height by the zone's dressing."""
    hx, hy, hz = c["size"][0] / 2, c["size"][1] / 2, c["size"][2] / 2
    cer, stone = mb.material(ll.M_CERAMIC), mb.material(ll.M_STONE)
    kc.rounded_block(mb, (0.0, 0.35, 0.0), (hx, 0.35, hz), stone, radius=0.04, seg=1, noise=None if lod else noise,
                     disp_m=0.01, weather=ll.STONE, variation=float(rng.random()))
    kc.rounded_block(mb, (0.0, 0.7 + (2 * hy - 0.7) / 2, -0.05), (hx - 0.12, (2 * hy - 0.7) / 2, hz - 0.12), cer,
                     radius=0.05, seg=1, noise=None if lod else noise, disp_m=0.01, weather=ll.CERAMIC,
                     variation=float(rng.random()))
    kc.rounded_block(mb, (0.0, 2 * hy + 0.08, 0.0), (hx + 0.1, 0.08, hz + 0.08), stone, radius=0.02, seg=1,
                     weather=ll.STONE)
    if lod:
        return
    # The sunk panel the housing sits in, the conduits up the back and over the top, down into the housing's collars.
    kc.rounded_block(mb, (0.0, 1.35, hz - 0.1), (0.62, 0.5, 0.02), mb.material(ll.M_DARK), radius=0.0, seg=1)
    for x in (-0.9, 0.0, 0.9):
        _conduit(mb, (x, -1.2, -hz - 0.18), (x, 2 * hy + 0.25, -hz - 0.18), lod)
    _conduit(mb, (-0.9, 2 * hy + 0.25, -hz - 0.18), (0.9, 2 * hy + 0.25, -hz - 0.18), lod)
    for x in (-0.28, 0.28):  # into the housing's two collars from above
        _conduit(mb, (x, 2 * hy + 0.25, -hz - 0.1), (x, 2 * hy + 0.25, hz - 0.05), lod)
        _conduit(mb, (x, 2 * hy + 0.25, hz - 0.05), (x, 1.62, hz - 0.05), lod)


def _gate(mb, rng, noise, g: dict, lod: bool) -> None:
    """Lowlight's gate on GateBound, in the bound's frame turned so the facade faces -X (the walk): a ceramic facade over
    a stone foot, 2 x FACADE_HALF wide, a pointed doorway onto the dark (the temple inside), the conduit over it."""
    cer, stone, dark = mb.material(ll.M_CERAMIC), mb.material(ll.M_STONE), mb.material(ll.M_DARK)
    x_face = g["size"][0] / 2 + 0.6  # the facade's face, past the bound
    t = 1.6
    xc = x_face + t / 2
    hw = GATE_W / 2
    # Stone to 1.6 over the water, ceramic above; the doorway cut by building the wall either side and above.
    for z0, z1 in ((-FACADE_HALF, -hw), (hw, FACADE_HALF)):
        zc, zh = (z0 + z1) / 2, (z1 - z0) / 2
        kc.rounded_block(mb, (xc, (WATER_Y - 1.0 + 1.6) / 2, zc), (t / 2, (1.6 - WATER_Y + 1.0) / 2, zh), stone,
                         radius=0.05, seg=1, noise=None if lod else noise, disp_m=0.015, weather=ll.STONE)
        kc.rounded_block(mb, (xc, (1.6 + FACADE_H) / 2, zc), (t / 2, (FACADE_H - 1.6) / 2, zh), cer, radius=0.05,
                         seg=1, noise=None if lod else noise, disp_m=0.01, weather=ll.CERAMIC)
    kc.rounded_block(mb, (xc, (GATE_H + FACADE_H) / 2, 0.0), (t / 2, (FACADE_H - GATE_H) / 2, hw), cer, radius=0.05,
                     seg=1, weather=ll.CERAMIC)
    # The doorway's dark (the temple's unlit inside) and its threshold.
    kc.rounded_block(mb, (xc + t / 2 + 1.5, GATE_H / 2, 0.0), (1.5, GATE_H / 2 + 0.2, hw + 0.4), dark, radius=0.0,
                     seg=1)
    kc.rounded_block(mb, (x_face - 0.3, -0.06, 0.0), (0.9, 0.06, hw + 0.3), stone, radius=0.02, seg=1,
                     weather=ll.STONE)
    if lod:
        return
    # The pointed arch's moulding and its jambs, the conduit along the facade's string course, the niche tier over it.
    prof = ll._pointed_arch(hw + 0.15, GATE_H - 1.8, GATE_H + 0.6, 17)
    arch = np.stack([np.full(len(prof), x_face - 0.08), prof[:, 1], prof[:, 0]], -1)
    kc.tube(mb, arch, 0.18, 6, stone, weather=ll.STONE)
    for sz in (-1.0, 1.0):
        kc.rounded_block(mb, (x_face - 0.1, (GATE_H - 1.8) / 2, sz * (hw + 0.15)), (0.2, (GATE_H - 1.8) / 2, 0.22),
                         stone, radius=0.03, seg=1, weather=ll.STONE)
        for zz in np.arange(3.2, FACADE_HALF - 0.8, 2.4):  # blind arcading on the facade
            p = ll._pointed_arch(0.8, 4.0, 6.2, 9)
            kc.tube(mb, np.stack([np.full(len(p), x_face - 0.04), p[:, 1], sz * zz + p[:, 0]], -1), 0.07, 5, cer,
                    weather=ll.CERAMIC)
            kc.rounded_block(mb, (x_face - 0.01, 3.2, sz * zz), (0.02, 1.6, 0.62), dark, radius=0.0, seg=1)
    kc.rounded_block(mb, (x_face - 0.15, 7.6, 0.0), (0.25, 0.14, FACADE_HALF), stone, radius=0.03, seg=1,
                     weather=ll.STONE)
    _conduit(mb, (x_face - 0.45, 7.35, -FACADE_HALF + 0.3), (x_face - 0.45, 7.35, FACADE_HALF - 0.3), lod)
    kc.rounded_block(mb, (x_face - 0.15, FACADE_H + 0.1, 0.0), (0.4, 0.2, FACADE_HALF + 0.1), stone, radius=0.03, seg=1,
                     weather=ll.STONE)


def build_group(name: str, seed: int) -> list[kc.MeshBuilder]:
    bl = blocks()
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        for bid in GROUPS[name]:
            b = bl[bid]
            sub = kc.MeshBuilder(bid)
            (_paved if bid in FLAG_PAVED else _gallery)(sub, rng, noise, b, bl, lod)
            rot, off = _xform(b)
            mb.merge(sub, rot, off)
        walls = [w for w in bl.values() if w["id"].startswith(("CourtWall", "LandingBound"))]
        for w in walls:
            if (name == "sunken_vey_walks_w") != w["id"].startswith("LandingBound"):
                continue
            sub = kc.MeshBuilder(w["id"])
            _parapet(sub, rng, w, lod)
            rot, off = _xform(w)
            mb.merge(sub, rot, off)
        if name == "sunken_vey_court":
            c = bl["Conduit"]
            sub = kc.MeshBuilder("conduit")
            _conduit_stand(sub, rng, noise, c, lod)
            mb.merge(sub, None, (c["pos"][0], 0.0, c["pos"][2]))
        if name == "sunken_vey_walks_e":
            g = bl["GateBound"]
            sub = kc.MeshBuilder("gate")
            _gate(sub, rng, noise, g, lod)
            mb.merge(sub, None, (g["pos"][0], 0.0, g["pos"][2]))
        out.append(mb)
    return out


def bed_height(noise: kc.Noise3):
    """The lagoon's bed: silt at BED_Y with soft swells, rising under every walk and court to the drowned arcades'
    footings (-2.2), so the stone stands on it."""
    bl = blocks()
    walks = [bl[i] for i in ORDER]

    def h(X, Z):
        X, Z = np.asarray(X, float), np.asarray(Z, float)
        n = noise.fbm(np.stack([X / 9.0, np.zeros_like(X), Z / 9.0], -1), 4) - 0.5
        y = BED_Y + n * BED_VARY_M * 2.0
        for b in walks:
            a = math.radians(float(b.get("yaw", 0.0)))
            dx, dz = X - b["pos"][0], Z - b["pos"][2]
            lx, lz = dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)
            d = np.hypot(np.maximum(np.abs(lx) - b["size"][0] / 2, 0.0), np.maximum(np.abs(lz) - b["size"][2] / 2, 0.0))
            y = np.maximum(y, -2.25 + n * 0.1 - 0.5 * kc.smoothstep(0.0, 3.0, d))
        return y

    return h


def build_ground(seed: int = 1830) -> list[kc.MeshBuilder]:
    lay = layout()
    wb = {b["id"]: b for b in lay["blocks"]}["Water"]
    x0, x1 = wb["pos"][0] - wb["size"][0] / 2, wb["pos"][0] + wb["size"][0] / 2
    z0, z1 = wb["pos"][2] - wb["size"][2] / 2, wb["pos"][2] + wb["size"][2] / 2
    out = []
    for lod in (False, True):
        rng = kc.rng_for("sunken_vey_ground", seed)
        noise = kc.Noise3(rng)
        h = bed_height(noise)
        mb = kc.MeshBuilder("sunken_vey_ground" + ("-lod1" if lod else ""))
        cell = 1.5 * (4.0 if lod else 1.0)
        xs = np.linspace(x0, x1, int(round((x1 - x0) / cell)) + 1)
        zs = np.linspace(z0, z1, int(round((z1 - z0) / cell)) + 1)
        X, Z = np.meshgrid(xs, zs)
        Y = h(X, Z)
        P = np.stack([X, Y, Z], -1)
        brk = noise.fbm(P / 2.5, 2)
        col = np.stack([np.full_like(Y, 0.25), np.full_like(Y, 0.15), np.full_like(Y, 1.0), 0.3 + 0.4 * brk], -1)
        kc.quad_strip(mb, P, mb.material(M_SILT), uv=np.stack([X, Z], -1) / 4.0, col=col,
                      uv2=np.array([0.85, 0.5]), flip=True)
        if not lod:
            _drowned_streets(mb, rng, noise, h, (x0, x1, z0, z1))
        out.append(mb)
    return out


def _drowned_streets(mb, rng, noise, h, ext) -> None:
    """The drowned town's floor: patches of the old paving tilted on the silt, and the street conduits still running
    along it, lit (lowlight.md §0: bound light still in every line)."""
    x0, x1, z0, z1 = ext
    stone = mb.material(ll.M_STONE)
    for _ in range(46):  # paving patches
        cx, cz = rng.uniform(x0 + 4, x1 - 4), rng.uniform(z0 + 4, z1 - 4)
        n = int(rng.integers(3, 8))
        for _k in range(n):
            x, z = cx + rng.uniform(-2.0, 2.0), cz + rng.uniform(-2.0, 2.0)
            y = float(h([x], [z])[0])
            kc.rounded_block(mb, (x, y + 0.02, z), (0.58, 0.07, 0.58), stone,
                             rot=kc.rot_y(rng.uniform(0, 0.2)) @ kc.rot_x(rng.normal(0, 0.06)), radius=0.02, seg=1,
                             weather=ll.STONE, variation=float(rng.random()))
    for k in range(7):  # the street conduits, east-west lines on the floor, broken into runs
        z = z0 + (k + 0.5) * (z1 - z0) / 7 + rng.uniform(-3.0, 3.0)
        x = x0 + rng.uniform(0, 8)
        while x < x1 - 6:
            ln = rng.uniform(5.0, 14.0)
            xa, xb = x, min(x + ln, x1 - 2)
            ya, yb = float(h([xa], [z])[0]) + 0.12, float(h([xb], [z])[0]) + 0.12
            _conduit(mb, (xa, ya, z), (xb, yb, z), False)
            x = xb + rng.uniform(3.0, 10.0)


TARGETS = {
    "sunken_vey_walks_w": lambda: build_group("sunken_vey_walks_w", 1831),
    "sunken_vey_court": lambda: build_group("sunken_vey_court", 1832),
    "sunken_vey_walks_e": lambda: build_group("sunken_vey_walks_e", 1833),
    "sunken_vey_ground": build_ground,
}
