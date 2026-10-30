"""Lowlight, the temple half under the water (M4-A2P-041; lowlight.md §5), built from act1-chapters' greybox
(game/levels/ch11/lowlight/lowlight_layout.json), read here so the stone follows the greybox if it moves. Pure numpy.

The kit's `lowlight_nave_bay` and `engine_hall` stand their piers in the middle of the floor and close their walls,
where the greybox's rooms are open floors with doorways through their walls. So the rooms are built here in the kit's
language (lowlight.py) on the greybox's own walls: grey stone to the tide line and white Lit Age ceramic panels above,
engaged piers, tiers of empty lamp niches with their bronze trim-arms, the cornice conduit with its bound light, a
pointed vault; every doorway the greybox leaves between two walls a pointed arch through the wall. Nothing stands in the
walked floor (the greybox's collision is the floor), bar the flooded hall's water film.

  lowlight_atrium     the atrium at the gate (the lamp bench's room), its gate threshold, the hallway north to the hall
  lowlight_hall       the Lamp Engine's hall: its floor flooded, the trimming rail round the walls with the twelve trimmed
                      lamps, the vault fallen in over the Engine (the grey shaft of daylight)
  lowlight_well       the well-stair east: two flights down past the waterline between their walls, under a sloped vault,
                      the landing between; the drowned sanctum at the foot, a square chamber under a dome on pendentives
                      whose oculus opens on the shaft up to the light, the well's mouth in its floor (the kit's
                      `well_shaft` drops from it into the deep)

Origin at the zone's origin (the greybox's frame).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import kit_common as kc
import lowlight as ll

ROOT = Path(__file__).resolve().parents[4]
LAYOUT = ROOT / "game" / "levels" / "ch11" / "lowlight" / "lowlight_layout.json"
TRI_BUDGET = {"lowlight_atrium": (90000, 6000), "lowlight_hall": (70000, 5000), "lowlight_well": (90000, 6000)}

TIDE_BAND_M = 1.2  # grey stone to here over a floor, ceramic above (the tide line's algae)
PANEL_M = 2.4
COURSE_M = 1.95
PILASTER_EVERY_M = 4.0
PILASTER_PROUD = 0.12  # engaged piers stand no further into the room than this (the walker's capsule keeps off them)
NICHE_PITCH_M = 1.6
NICHE_TIERS_M = (2.4, 4.2, 6.0)  # three tiers (a fourth read as a filing cabinet)
CORNICE_DROP = 0.5
DOOR_SPRING_M = 3.0  # a doorway's arch springs here over its floor
ATRIUM_H = 9.0  # the walls' tops over the floor
ATRIUM_CROWN = 14.0
HALLWAY_H = 6.5
HALLWAY_CROWN = 8.5
HALL_H = 9.0
HALL_FALLEN = (5.0, 11.5, -33.5, -28.0)  # x0, x1, z0, z1: the vault's fallen bay, over the Engine (LampEngine)
HALL_RAIL_Y = 3.5
ATRIUM_BROKEN = (13.0, 17.5, -3.0, 2.5)  # x0, x1, z0, z1: the atrium vault's broken bay
FLIGHT_VAULT_M = 3.4  # a flight's vault springs this far over its treads
WELL_MOUTH_R = 3.0
SANCTUM_SPRING = -2.0  # the drowned sanctum's dome springs here; its oculus at the walls' top
SHAFT_TOP = 6.0  # the greybox's WellShaft: the shaft's mouth to the light above
FLOOD_Y = 0.03  # the hall's water film over its flags


def layout() -> dict:
    return json.loads(LAYOUT.read_text(encoding="utf-8"))


def blocks() -> dict:
    return {b["id"]: b for b in layout()["blocks"]}


def _box(b: dict) -> tuple[float, float, float, float, float, float]:
    (x, y, z), (sx, sy, sz) = b["pos"], b["size"]
    return x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z - sz / 2, z + sz / 2


def _flat_top(mb, v0: int) -> None:
    n = np.asarray(mb.nrm[v0:])
    n[n[:, 1] > 0.85] = (0.0, 1.0, 0.0)
    mb.nrm[v0:] = n.tolist()


def _flags(mb, rng, noise, x0, x1, z0, z1, top, lod, *, wet: bool = False, skip=None) -> None:
    """Laid stone flags over a floor, the bedding under them (the joints read as grooves)."""
    stone = mb.material(ll.M_STONE)
    w = kc.Weathering(moss=0.1, salt=0.25, wet=0.85 if wet else 0.45, erosion=0.5, noise_scale_m=0.8)
    if skip is None:
        kc.rounded_block(mb, ((x0 + x1) / 2, top - 0.25, (z0 + z1) / 2), ((x1 - x0) / 2, 0.2, (z1 - z0) / 2), stone,
                         radius=0.02, seg=1)
    if lod:
        kc.rounded_block(mb, ((x0 + x1) / 2, top - 0.03, (z0 + z1) / 2), ((x1 - x0) / 2, 0.03, (z1 - z0) / 2), stone,
                         radius=0.01, seg=1)
        return
    z = z0
    while z < z1 - 0.05:
        dz = min(rng.uniform(0.7, 1.0), z1 - z)
        x = x0 - rng.uniform(0.0, 0.6)
        while x < x1 - 0.05:
            dx = min(rng.uniform(0.9, 1.5), x1 - max(x, x0))
            a = max(x, x0)
            if skip is not None and skip(a + dx / 2, z + dz / 2):
                x = a + dx
                continue
            v0 = mb.vertex_count
            kc.rounded_block(mb, (a + dx / 2, top - 0.04 + rng.normal(0, 0.004), z + dz / 2),
                             (dx / 2 - 0.012, 0.04, dz / 2 - 0.012), stone, rot=kc.rot_y(rng.normal(0, 0.004)),
                             radius=0.012, seg=1, noise=noise, disp_m=0.003, weather=w, variation=float(rng.random()))
            _flat_top(mb, v0)
            x = a + dx
        z += dz


def _wall(mb, rng, noise, b: dict, top: float, inward: tuple[float, float], lod: bool, *, floor_y: float | None = None,
          niches: bool = True) -> None:
    """A greybox wall block raised to `top`: stone to the tide band, ceramic panels in courses above; on its room face
    (`inward`, a unit x/z) engaged piers, two tiers of empty lamp niches and the cornice conduit."""
    x0, x1, y0, _y1, z0, z1 = _box(b)
    base = y0 if floor_y is None else floor_y
    stone, cer = mb.material(ll.M_STONE), mb.material(ll.M_CERAMIC)
    along_x = (x1 - x0) >= (z1 - z0)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    hx, hz = (x1 - x0) / 2, (z1 - z0) / 2
    band = base + TIDE_BAND_M
    kc.rounded_block(mb, (cx, (y0 + band) / 2, cz), (hx, (band - y0) / 2, hz), stone, radius=0.04, seg=1,
                     noise=None if lod else noise, disp_m=0.01, weather=ll.STONE, variation=float(rng.random()))
    if lod:
        kc.rounded_block(mb, (cx, (band + top) / 2, cz), (hx, (top - band) / 2, hz), cer, radius=0.04, seg=1)
        return
    # The wall's core behind the panels (their joints are grooves onto it, never slits onto the sky).
    core = (hx - 0.01, (top - band) / 2, hz * 0.6) if along_x else (hx * 0.6, (top - band) / 2, hz - 0.01)
    kc.rounded_block(mb, (cx, (band + top) / 2, cz), core, stone, radius=0.01, seg=1)
    length = 2 * (hx if along_x else hz)
    n = max(1, int(round(length / PANEL_M)))
    for i in range(n):
        t = -1.0 + (i + 0.5) * 2.0 / n
        for y in np.arange(band, top - 0.01, COURSE_M):
            yy = min(y + COURSE_M, top)
            px, pz = (cx + t * hx, cz) if along_x else (cx, cz + t * hz)
            half = ((hx / n - 0.02, (yy - y) / 2 - 0.02, hz) if along_x else (hx, (yy - y) / 2 - 0.02, hz / n - 0.02))
            kc.rounded_block(mb, (px, (y + yy) / 2, pz), half, cer, radius=0.04, seg=1, noise=noise, disp_m=0.01,
                             weather=ll.CERAMIC, variation=float(rng.random()))
    ix, iz = inward
    face = (cx + ix * hx, cz + iz * hz)  # the room face's centre line
    copper, dark, glass = mb.material(ll.M_COPPER), mb.material(ll.M_DARK), mb.material(ll.M_GLASS)

    def at(s: float, out: float) -> tuple[float, float]:
        return (face[0] + s, face[1] + iz * out) if along_x else (face[0] + ix * out, face[1] + s)

    # Engaged piers (shallow), the niche tiers between them, the cornice and its conduit.
    k = max(1, int(round(length / PILASTER_EVERY_M)))
    step = length / k
    for j in range(k + 1):
        s = -length / 2 + j * step
        if abs(s) > length / 2 - 0.3:
            continue
        px, pz = at(s, PILASTER_PROUD / 2)
        half = (0.3, (top - CORNICE_DROP - base) / 2, PILASTER_PROUD / 2) if along_x else (
            PILASTER_PROUD / 2, (top - CORNICE_DROP - base) / 2, 0.3)
        kc.rounded_block(mb, (px, (base + top - CORNICE_DROP) / 2, pz), half, cer, radius=0.03, seg=1,
                         weather=ll.CERAMIC, variation=float(rng.random()))
        kc.rounded_block(mb, (px, base + 0.35, pz), (half[0] + 0.03, 0.35, half[2] + 0.03), stone, radius=0.03,
                         seg=1, weather=ll.STONE)
    if niches and top - base > 4.0:
        tiers = [y for y in NICHE_TIERS_M if base + y + 0.6 < top - CORNICE_DROP]
        for y in tiers:
            for s in np.arange(-length / 2 + 0.9, length / 2 - 0.8, NICHE_PITCH_M):
                if any(abs(s - (-length / 2 + j * step)) < 0.5 for j in range(k + 1)):
                    continue  # not on a pier
                px, pz = at(s, 0.0)
                d = (0.32, 0.42, 0.05) if along_x else (0.05, 0.42, 0.32)
                kc.rounded_block(mb, (px, base + y, pz), d, dark, radius=0.02, seg=1)
                gx, gz = at(s, 0.12)
                kc.rounded_block(mb, (gx, base + y - 0.12, gz), (0.13, 0.15, 0.13), glass, radius=0.12, seg=2)
                a0 = at(s - 0.3, 0.03)
                a1 = at(s, 0.3)
                kc.tube(mb, np.array([[a0[0], base + y + 0.38, a0[1]], [a1[0], base + y + 0.32, a1[1]]]), 0.02, 4,
                        copper)
    cy = top - CORNICE_DROP
    c0, c1 = at(-length / 2, 0.1), at(length / 2, 0.1)
    kc.rounded_block(mb, ((c0[0] + c1[0]) / 2, cy, (c0[1] + c1[1]) / 2),
                     (length / 2, 0.1, 0.12) if along_x else (0.12, 0.1, length / 2), stone, radius=0.02, seg=1,
                     weather=ll.STONE)
    k0, k1 = at(-length / 2 + 0.1, 0.24), at(length / 2 - 0.1, 0.24)
    kc.tube(mb, np.array([[k0[0], cy - 0.22, k0[1]], [k1[0], cy - 0.22, k1[1]]]), 0.05, 6, mb.material(ll.M_CONDUIT))


def _door(mb, rng, line: str, at: float, a: float, b: float, floor_y: float, top: float, thick: float,
          lod: bool) -> None:
    """The wall over a doorway the greybox leaves between two walls: from the arch's crown to `top`, with the pointed
    arch's moulded ring under it and the spandrels filled. `line` 'x' (the wall runs along X at z=at) or 'z'."""
    cer, stone = mb.material(ll.M_CERAMIC), mb.material(ll.M_STONE)
    hw = (b - a) / 2
    mid = (a + b) / 2
    crown = floor_y + DOOR_SPRING_M + hw * 1.1
    prof = ll._pointed_arch(hw, floor_y + DOOR_SPRING_M, crown, 7 if lod else 15)

    def p(s, y, o=0.0):
        return (mid + s, y, at + o) if line == "x" else (at + o, y, mid + s)

    # Spandrel and lintel: a slab per profile segment from the arch's line up to the top.
    for k in range(len(prof) - 1):
        s0, s1 = prof[k][0], prof[k + 1][0]
        ylo = min(prof[k][1], prof[k + 1][1])
        cs, hs = (s0 + s1) / 2, abs(s1 - s0) / 2 + 0.01
        c = p(cs, (ylo + top) / 2)
        half = (hs, (top - ylo) / 2, thick / 2) if line == "x" else (thick / 2, (top - ylo) / 2, hs)
        kc.rounded_block(mb, c, half, cer, radius=0.02, seg=1, weather=ll.CERAMIC, variation=float(rng.random()))
    if lod:
        return
    for o in (-thick / 2 - 0.06, thick / 2 + 0.06):
        ring = np.array([p(s, y, o) for s, y in prof])
        kc.tube(mb, ring, 0.12, 6, stone, weather=ll.STONE)
        for sgn in (-1.0, 1.0):  # the jambs' mouldings down to the floor
            kc.tube(mb, np.array([p(sgn * hw, floor_y + 0.05, o), p(sgn * hw, floor_y + DOOR_SPRING_M, o)]), 0.12, 6,
                    stone, weather=ll.STONE)


def _vault(mb, rng, x0, x1, z0, z1, spring: float, crown: float, axis: str, lod: bool, *, hole=None,
           ribs_every: float = 4.0, ends: bool = True) -> None:
    """A pointed barrel over a rectangle (its axis along `axis`), its end walls (tympana) closed, transverse ribs; the
    triangles over `hole` (x0, x1, z0, z1) left out (a broken bay)."""
    cer, stone = mb.material(ll.M_CERAMIC), mb.material(ll.M_STONE)
    span_half = (z1 - z0) / 2 if axis == "x" else (x1 - x0) / 2
    mid = (z0 + z1) / 2 if axis == "x" else (x0 + x1) / 2
    n = 9 if lod else 21
    prof = ll._pointed_arch(span_half, spring, crown, n)
    a0, a1 = (x0, x1) if axis == "x" else (z0, z1)
    m = max(2, int(round((a1 - a0) / (2.0 if lod else 0.8))) + 1)
    along = np.linspace(a0, a1, m)
    if axis == "x":
        grid = np.stack([np.stack([np.full(n, t), prof[:, 1], mid + prof[:, 0]], -1) for t in along], 0)
    else:
        grid = np.stack([np.stack([mid + prof[:, 0], prof[:, 1], np.full(n, t)], -1) for t in along], 0)
    t0 = mb.triangle_count
    for flip in (False, True):  # both faces: the vault is seen from below, and from above through its broken bay
        kc.quad_strip(mb, grid, cer, uv=grid[..., [0, 2]] / 2.0, col=(0, 0, 0, 0.6), uv2=(0.7, 0.5), flip=flip)
    if hole is not None:
        hx0, hx1, hz0, hz1 = hole
        pos = np.asarray(mb.pos)
        tris = np.asarray(mb.tris[t0:])
        cen = pos[tris].mean(axis=1)
        keep = ~((cen[:, 0] > hx0) & (cen[:, 0] < hx1) & (cen[:, 2] > hz0) & (cen[:, 2] < hz1))
        mb.tris = mb.tris[:t0] + [t for t, k in zip(mb.tris[t0:], keep) if k]
        mb.tri_mat = mb.tri_mat[:t0] + [mm for mm, k in zip(mb.tri_mat[t0:], keep) if k]
    # The tympana at the ends: from the springing line up to the arch.
    for t in (a0, a1) if ends else ():
        rows = np.stack([np.stack([prof[:, 0], np.full(n, spring), np.zeros(n)], -1),
                         np.stack([prof[:, 0], prof[:, 1], np.zeros(n)], -1)], 0)
        if axis == "x":
            g = np.stack([np.full_like(rows[..., 0], t), rows[..., 1], mid + rows[..., 0]], -1)
        else:
            g = np.stack([mid + rows[..., 0], rows[..., 1], np.full_like(rows[..., 0], t)], -1)
        uvs = g[..., [2, 1]] if axis == "x" else g[..., [0, 1]]  # across the end wall, never along the barrel
        ax = np.array([1.0, 0.0, 0.0]) if axis == "x" else np.array([0.0, 0.0, 1.0])
        for flip in (False, True):
            v0, t0 = mb.vertex_count, mb.triangle_count
            kc.quad_strip(mb, g, cer, uv=uvs / 2.0, col=(0, 0, 0, 0.6), uv2=(0.7, 0.5), flip=flip, smooth=False)
            # The end wall is flat: every normal is the wall's own (the springing's degenerate quads gave stray ones,
            # and the ceramic's triplanar streaked along them).
            pos = np.asarray(mb.pos)
            geo = sum(np.cross(pos[b] - pos[a], pos[c] - pos[a]) for a, b, c in mb.tris[t0:])
            sign = 1.0 if float(np.dot(geo, ax)) >= 0.0 else -1.0
            nrm = np.asarray(mb.nrm)
            nrm[v0:] = ax * sign
            mb.nrm = nrm.tolist()
    if lod:
        return
    for t in np.arange(a0 + ribs_every / 2, a1, ribs_every):
        if hole is not None:
            hx0, hx1, hz0, hz1 = hole
            if (axis == "x" and hx0 < t < hx1) or (axis == "z" and hz0 < t < hz1):
                continue  # the broken bay's rib fell
        if axis == "x":
            pts = np.stack([np.full(n, t), prof[:, 1] - 0.08, mid + prof[:, 0] * 0.99], -1)
        else:
            pts = np.stack([mid + prof[:, 0] * 0.99, prof[:, 1] - 0.08, np.full(n, t)], -1)
        kc.tube(mb, pts, 0.22, 6, stone, weather=ll.STONE)


def _rubble(mb, rng, noise, x0, x1, z0, z1, y: float, n: int, top_m: float) -> None:
    """Fallen vault shards lying flat in a corner or under a broken bay, none taller than `top_m` (they lie under the
    water film or the walker steps over them)."""
    for k in range(n):
        s = rng.uniform(0.25, 0.6)
        h = min(s * 0.35, top_m)
        kc.rounded_block(mb, (rng.uniform(x0, x1), y + h * 0.5, rng.uniform(z0, z1)), (s, h * 0.5, s * 0.8),
                         mb.material(ll.M_CERAMIC if k % 3 else ll.M_STONE),
                         rot=kc.rot_y(rng.uniform(0, 3)) @ kc.rot_x(rng.normal(0, 0.05)), radius=0.03, seg=1,
                         noise=noise, disp_m=0.02, weather=ll.CERAMIC, variation=float(rng.random()))


def _ragged_edge(mb, rng, noise, hole, y: float) -> None:
    """A fallen bay's broken rim: shards of the ceiling still hanging into the hole, the rubble core showing."""
    x0, x1, z0, z1 = hole
    cer, stone = mb.material(ll.M_CERAMIC), mb.material(ll.M_STONE)
    per = [(x, z0) for x in np.arange(x0, x1, 0.7)] + [(x, z1) for x in np.arange(x0, x1, 0.7)]
    per += [(x0, z) for z in np.arange(z0, z1, 0.7)] + [(x1, z) for z in np.arange(z0, z1, 0.7)]
    for x, z in per:
        s = rng.uniform(0.3, 0.75)
        kc.rounded_block(mb, (x + rng.uniform(-0.2, 0.2), y + rng.uniform(-0.15, 0.05), z + rng.uniform(-0.2, 0.2)),
                         (s, rng.uniform(0.12, 0.28), s * 0.8), cer if rng.random() < 0.6 else stone,
                         rot=kc.rot_y(rng.uniform(0, 3)) @ kc.rot_x(rng.normal(0, 0.25)), radius=0.03, seg=1,
                         noise=noise, disp_m=0.04, weather=ll.CERAMIC, variation=float(rng.random()))


def _inward(b: dict, room: dict) -> tuple[float, float]:
    x0, x1, _, _, z0, z1 = _box(b)
    rx0, rx1, _, _, rz0, rz1 = _box(room)
    if (x1 - x0) >= (z1 - z0):
        return (0.0, 1.0 if (z0 + z1) / 2 < (rz0 + rz1) / 2 else -1.0)
    return (1.0 if (x0 + x1) / 2 < (rx0 + rx1) / 2 else -1.0, 0.0)


def _doors(bl: dict, room: str, walls: list[str]) -> list[tuple[str, float, float, float, float]]:
    """The doorways of a room: on each side, the gaps the greybox leaves between that side's wall blocks.
    -> (line, at, a, b, thick)."""
    r = bl[room]
    rx0, rx1, _, _, rz0, rz1 = _box(r)
    out = []
    for line, lo, hi in (("x", rx0, rx1), ("z", rz0, rz1)):
        sides: dict[float, list] = {}
        for wid in walls:
            x0, x1, _, _, z0, z1 = _box(bl[wid])
            if line == "x" and (x1 - x0) >= (z1 - z0):
                sides.setdefault(round((z0 + z1) / 2, 2), []).append((x0, x1, z1 - z0))
            elif line == "z" and (z1 - z0) > (x1 - x0):
                sides.setdefault(round((x0 + x1) / 2, 2), []).append((z0, z1, x1 - x0))
        for at, segs in sides.items():
            segs.sort()
            thick = segs[0][2]
            edge = lo
            for a, b, _t in segs + [(hi, hi, thick)]:
                if a - edge > 1.0:
                    out.append((line, at, edge, a, thick))
                edge = max(edge, b)
    return out


def _room(mb, rng, noise, bl: dict, room: str, walls: list[str], top: float, lod: bool, *, niches: bool = True,
          wet: bool = False, clip_z: tuple[float, float] | None = None, skip=None) -> None:
    """A room on its floor block: flags (over `clip_z` of it only, where it overlaps the rooms it joins), its walls
    raised to `top` over the floor, a pointed arch over every doorway the greybox leaves."""
    r = bl[room]
    x0, x1, _y0, y1, z0, z1 = _box(r)
    fz0, fz1 = clip_z if clip_z is not None else (z0, z1)
    _flags(mb, rng, noise, x0, x1, fz0, fz1, y1, lod, wet=wet, skip=skip)
    for wid in walls:
        _wall(mb, rng, noise, bl[wid], y1 + top, _inward(bl[wid], r), lod, floor_y=y1, niches=niches)
    for line, at, a, b, thick in _doors(bl, room, walls):
        _door(mb, rng, line, at, a, b, y1, y1 + top, thick, lod)


def build_atrium(seed: int = 1840) -> list[kc.MeshBuilder]:
    bl = blocks()
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lowlight_atrium", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("lowlight_atrium" + ("-lod1" if lod else ""))
        walls = [i for i in bl if i.startswith("AtriumWall")]
        _room(mb, rng, noise, bl, "Atrium", walls, ATRIUM_H, lod)
        ax0, ax1, _, _, az0, az1 = _box(bl["Atrium"])
        _vault(mb, rng, ax0 - 0.25, ax1 + 0.25, az0 - 0.25, az1 + 0.25, ATRIUM_H, ATRIUM_CROWN, "x", lod,
               hole=ATRIUM_BROKEN)
        if not lod:  # the broken bay's shards, fallen to the floor under it, flat
            hx0, hx1, hz0, hz1 = ATRIUM_BROKEN
            _rubble(mb, rng, noise, hx0, hx1, hz0, hz1, 0.0, 9, 0.12)
            _ragged_edge(mb, rng, noise, (hx0 + 0.3, hx1 - 0.3, hz0 + 0.3, hz1 - 0.3), ATRIUM_CROWN - 0.3)
        # The gate's threshold (GateStep) and its jambs out to the Vey.
        g = bl["GateStep"]
        gx0, gx1, _, gy1, gz0, gz1 = _box(g)
        _flags(mb, rng, noise, gx0, gx1, gz0, gz1, gy1, lod, wet=True)
        kc.rounded_block(mb, ((gx0 + gx1) / 2, -1.3, (gz0 + gz1) / 2), ((gx1 - gx0) / 2, 1.1, (gz1 - gz0) / 2),
                         mb.material(ll.M_STONE), radius=0.04, seg=1, weather=ll.STONE)
        # The hallway north to the hall: its walls raised and vaulted along Z.
        # (Its floor and vault run between the two rooms' walls: the greybox's block overlaps both floors.)
        hz0 = _box(bl["HallWallS0"])[5]
        hz1 = _box(bl["AtriumWallN0"])[4]
        _room(mb, rng, noise, bl, "HallWay", ["HallWayWallW", "HallWayWallE"], HALLWAY_H, lod, niches=True,
              clip_z=(hz0, hz1))
        hx0, hx1, _, _, _, _ = _box(bl["HallWay"])
        _vault(mb, rng, hx0 - 0.25, hx1 + 0.25, hz0, hz1, HALLWAY_H, HALLWAY_CROWN, "z", lod, ends=False)
        out.append(mb)
    return out


def build_hall(seed: int = 1841) -> list[kc.MeshBuilder]:
    bl = blocks()
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lowlight_hall", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("lowlight_hall" + ("-lod1" if lod else ""))
        walls = [i for i in bl if i.startswith("HallWall")]
        _room(mb, rng, noise, bl, "Hall", walls, HALL_H, lod, wet=True)
        x0, x1, _, y1, z0, z1 = _box(bl["Hall"])
        # The ceiling: a slab with ribs, open over the fallen bay; its shards in the water film under it.
        fx0, fx1, fz0, fz1 = HALL_FALLEN
        cer, stone = mb.material(ll.M_CERAMIC), mb.material(ll.M_STONE)
        for (a, b, c, d) in ((x0, x1, z0, fz0), (x0, x1, fz1, z1), (x0, fx0, fz0, fz1), (fx1, x1, fz0, fz1)):
            kc.rounded_block(mb, ((a + b) / 2, HALL_H + 0.25, (c + d) / 2), ((b - a) / 2 + 0.25, 0.25, (d - c) / 2),
                             cer, radius=0.05, seg=1, weather=ll.CERAMIC)
        if not lod:
            for zz in np.arange(z0 + 2.0, z1, 3.0):
                if fz0 < zz < fz1:
                    for (ra, rb) in ((x0, fx0 - 0.3 - rng.uniform(0, 0.8)), (fx1 + 0.3 + rng.uniform(0, 0.8), x1)):
                        kc.rounded_block(mb, ((ra + rb) / 2, HALL_H - 0.25, zz), ((rb - ra) / 2, 0.25, 0.3), stone,
                                         radius=0.06, seg=1, weather=ll.STONE)
                    continue
                kc.rounded_block(mb, ((x0 + x1) / 2, HALL_H - 0.25, zz), ((x1 - x0) / 2, 0.25, 0.3), stone,
                                 radius=0.06, seg=1, weather=ll.STONE)
            _rubble(mb, rng, noise, fx0, fx1, fz0, z0 + 1.5, y1, 16, 0.1)
            _ragged_edge(mb, rng, noise, HALL_FALLEN, HALL_H + 0.25)
            # The trimming rail round the walls on its brackets, the twelve trimmed lamps on it (lowlight.md §0: the
            # Engine's work, bound teal, steady): a salt-glass globe round a bound core, a bronze trim-arm over it.
            ring = [(x0 + 0.5, z0 + 0.5), (x1 - 0.5, z0 + 0.5), (x1 - 0.5, z1 - 0.5), (x0 + 0.5, z1 - 0.5)]
            for k in range(4):
                (ax, az), (bx, bz) = ring[k], ring[(k + 1) % 4]
                if k == 2:
                    continue  # not across the hallway's wall (the doorway)
                pa, pb = np.array([ax, HALL_RAIL_Y, az]), np.array([bx, HALL_RAIL_Y, bz])
                kc.tube(mb, np.stack([pa, pb]), 0.06, 6, mb.material(ll.M_COPPER))
                for t in np.linspace(0.0, 1.0, int(np.linalg.norm(pb - pa) / 2.4) + 1):
                    p = pa + (pb - pa) * t
                    w = np.array([-0.5 if abs(p[0] - (x0 + 0.5)) < 0.01 else (0.5 if abs(p[0] - (x1 - 0.5)) < 0.01
                                                                              else 0.0), 0.0,
                                  -0.5 if abs(p[2] - (z0 + 0.5)) < 0.01 else 0.0])
                    kc.tube(mb, np.stack([p, p + w]), 0.04, 4, mb.material(ll.M_COPPER))
            for p in lamp_points(bl):
                c = np.array(p)
                kc.rounded_block(mb, tuple(c), (0.16, 0.2, 0.16), mb.material(ll.M_GLASS), radius=0.15, seg=2)
                kc.rounded_block(mb, tuple(c + [0, -0.02, 0]), (0.06, 0.08, 0.06), mb.material("kit_bound_core"),
                                 radius=0.05, seg=1)
                kc.tube(mb, np.stack([c + [0, -0.45, 0], c + [0, -0.22, 0]]), 0.025, 4, mb.material(ll.M_COPPER))
        out.append(mb)
    return out


def lamp_points(bl: dict | None = None) -> list[tuple[float, float, float]]:
    """The twelve trimmed lamps on the hall's rail: six along the north wall, three down each side."""
    bl = bl or blocks()
    x0, x1, _, _, z0, z1 = _box(bl["Hall"])
    y = HALL_RAIL_Y + 0.45
    pts = [(x, y, z0 + 0.5) for x in np.linspace(x0 + 2.0, x1 - 2.0, 6)]
    pts += [(sx, y, z) for sx in (x0 + 0.5, x1 - 0.5) for z in np.linspace(z0 + 4.0, z1 - 3.0, 3)]
    return [(round(float(a), 3), round(float(b), 3), round(float(c), 3)) for a, b, c in pts]


def _flight(mb, rng, noise, ramp: dict, lod: bool) -> None:
    """A flight down: treads on the ramp's line (each tread's middle on the ramp), the fill under them, a sloped
    pointed vault over, the conduit down the wall at hand height."""
    a, b, w = np.array(ramp["from"], float), np.array(ramp["to"], float), float(ramp["width"])
    d = b - a
    length = float(np.hypot(d[0], d[2]))
    ux = d[0] / length
    stone, cer = mb.material(ll.M_STONE), mb.material(ll.M_STONE if lod else ll.M_CERAMIC)
    n = max(4, int(round(length / 0.34)))
    run = length / n
    for k in range(n):
        t = (k + 0.5) / n
        p = a + d * t
        rise = abs(d[1]) / n
        kc.rounded_block(mb, (p[0], p[1] - 0.6, p[2]), (run / 2 + 0.01, 0.6 - rise * 0.0, w / 2 + 0.2), stone,
                         radius=0.01 if lod else 0.015, seg=1, weather=ll.STONE, variation=float(rng.random()))
        if not lod:  # the tread's nosing, ceramic edged
            kc.rounded_block(mb, (p[0] - ux * (run / 2 - 0.04), p[1] + 0.005, p[2]), (0.04, 0.02, w / 2 + 0.2), cer,
                             radius=0.01, seg=1)
    # The vault: a pointed barrel sloped with the flight.
    nprof = 7 if lod else 15
    prof = ll._pointed_arch(w / 2 + 0.25, FLIGHT_VAULT_M, FLIGHT_VAULT_M + 1.2, nprof)
    rows = []
    for t in np.linspace(-0.04, 1.04, 4 if lod else 18):
        p = a + d * t
        rows.append(np.stack([np.full(nprof, p[0]), p[1] + prof[:, 1], p[2] + prof[:, 0]], -1))
    grid = np.stack(rows, 0)
    for flip in (False, True):
        kc.quad_strip(mb, grid, mb.material(ll.M_CERAMIC), uv=grid[..., [0, 2]] / 2.0, col=(0, 0, 0, 0.6),
                      uv2=(0.7, 0.5), flip=flip)
    if lod:
        return
    for t in np.linspace(0.08, 0.92, 6):  # transverse ribs
        p = a + d * t
        kc.tube(mb, np.stack([np.full(nprof, p[0]), p[1] + prof[:, 1] - 0.06, p[2] + prof[:, 0] * 0.98], -1), 0.14, 6,
                stone, weather=ll.STONE)
    for sz in (-1.0, 1.0):  # the conduit down each wall at hand height, the bound light leading down
        z = a[2] + sz * (w / 2 + 0.15)
        _conduit(mb, (a[0], a[1] + 1.0, z), (b[0], b[1] + 1.0, z))


def _conduit(mb, a, b) -> None:
    pts = np.array([a, b], float)
    kc.tube(mb, pts, 0.05, 8, mb.material(ll.M_CONDUIT))
    kc.tube(mb, pts, 0.075, 8, mb.material(ll.M_GLASS))
    dd = pts[1] - pts[0]
    for t in np.linspace(0.04, 0.96, max(2, int(np.linalg.norm(dd) / 1.6) + 1)):
        kc.rounded_block(mb, tuple(pts[0] + dd * t), (0.06, 0.09, 0.06), mb.material(ll.M_COPPER), radius=0.02, seg=1)


def _sanctum(mb, rng, noise, bl: dict, lod: bool) -> None:
    """The drowned sanctum at the shaft's foot: its square walls to the dome's springing, a dome on pendentives with
    the oculus at the walls' top opening on the shaft up to the light (the greybox's WellShaft), the well's mouth open
    in its floor (the kit's well_shaft below it)."""
    s = bl["Sanctum"]
    x0, x1, _, y1, z0, z1 = _box(s)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    walls = [i for i in bl if i.startswith("SanctumWall")]
    for wid in walls:
        _wall(mb, rng, noise, bl[wid], SANCTUM_SPRING + 0.4, _inward(bl[wid], s), lod, floor_y=y1)
    for line, at, a, b, thick in _doors(bl, "Sanctum", walls):
        _door(mb, rng, line, at, a, b, y1, SANCTUM_SPRING + 0.4, thick, lod)
    # The floor: flags round the mouth (the mouth's ring left open), the bronze rim round it.
    stone, cer, copper = mb.material(ll.M_STONE), mb.material(ll.M_CERAMIC), mb.material(ll.M_COPPER)
    na = 24 if lod else 72
    ang = np.linspace(0.0, 2 * math.pi, na + 1)
    r_out = (x1 - x0) / 2
    sq = r_out / np.maximum(np.abs(np.cos(ang)), np.abs(np.sin(ang)))
    inner = np.stack([cx + np.cos(ang) * WELL_MOUTH_R, np.full(na + 1, y1), cz + np.sin(ang) * WELL_MOUTH_R], -1)
    outer = np.stack([cx + np.cos(ang) * sq, np.full(na + 1, y1), cz + np.sin(ang) * sq], -1)
    collar_r = WELL_MOUTH_R + 0.9
    collar = np.stack([cx + np.cos(ang) * collar_r, np.full(na + 1, y1), cz + np.sin(ang) * collar_r], -1)
    if lod:
        rings = np.stack([inner, (inner + outer) / 2, outer], 0)
        kc.quad_strip(mb, rings, stone, uv=rings[..., [0, 2]] / 1.5, col=(0.15, 0.2, 0.9, 0.5), uv2=(0.7, 0.5),
                      flip=True)
    else:  # flags out to the walls, the mouth's collar a ring of dressed stone, the bronze rim at its lip
        _flags(mb, rng, noise, x0, x1, z0, z1, y1, lod, wet=True,
               skip=lambda x, z: math.hypot(x - cx, z - cz) < collar_r + 0.5)
        band = np.stack([inner, collar], 0)
        kc.quad_strip(mb, band, stone, uv=band[..., [0, 2]] / 1.2, col=(0.1, 0.2, 0.7, 0.4), uv2=(0.7, 0.5), flip=True)
        out_band = np.stack([collar, np.stack([cx + np.cos(ang) * (collar_r + 0.9), np.full(na + 1, y1 - 0.01),
                                               cz + np.sin(ang) * (collar_r + 0.9)], -1)], 0)
        kc.quad_strip(mb, out_band, stone, uv=out_band[..., [0, 2]] / 1.2, col=(0.1, 0.2, 0.8, 0.5), uv2=(0.7, 0.5),
                      flip=True)
        for k in range(24):  # the collar's joints
            th = 2 * math.pi * k / 24
            kc.tube(mb, np.array([[cx + math.cos(th) * (WELL_MOUTH_R + 0.05), y1 + 0.004, cz + math.sin(th) * (WELL_MOUTH_R + 0.05)],
                                  [cx + math.cos(th) * collar_r, y1 + 0.004, cz + math.sin(th) * collar_r]]), 0.012, 3,
                    mb.material(ll.M_DARK))
    kc.tube(mb, inner + [0, 0.06, 0], 0.1, 6 if lod else 8, copper)
    # The dome: a hemisphere on the inscribed circle, springing at SANCTUM_SPRING, its oculus at the walls' top; the
    # pendentives (the corners between the square and the dome's foot) as a flat ring of ceiling.
    rd = r_out
    oc = 3.0
    rise = (bl["SanctumWallN0"]["pos"][1] + bl["SanctumWallN0"]["size"][1] / 2) - SANCTUM_SPRING
    el = np.linspace(0.0, math.asin(min(1.0, (1.0 - (oc / rd) ** 2) ** 0.5)), 5 if lod else 14)
    rows = [np.stack([cx + np.cos(ang) * rd * math.cos(e), np.full(na + 1, SANCTUM_SPRING + rise * math.sin(e)),
                      cz + np.sin(ang) * rd * math.cos(e)], -1) for e in el]
    dome = np.stack(rows, 0)
    for flip in (False, True):
        kc.quad_strip(mb, dome, cer, uv=dome[..., [0, 2]] / 2.0, col=(0, 0, 0, 0.6), uv2=(0.7, 0.5), flip=flip)
    corner = np.stack([np.stack([cx + np.cos(ang) * rd, np.full(na + 1, SANCTUM_SPRING), cz + np.sin(ang) * rd], -1),
                       np.stack([cx + np.cos(ang) * sq * 1.03, np.full(na + 1, SANCTUM_SPRING),
                                 cz + np.sin(ang) * sq * 1.03], -1)], 0)
    for flip in (False, True):
        kc.quad_strip(mb, corner, cer, uv=corner[..., [0, 2]] / 2.0, col=(0, 0, 0, 0.6), uv2=(0.7, 0.5), flip=flip)
    # The shaft over the oculus up to the light: a ribbed drum to SHAFT_TOP, the bronze rim at its lip.
    top_y = SANCTUM_SPRING + rise * (oc / rd and math.sin(el[-1]))
    ys = np.linspace(top_y, SHAFT_TOP, 3 if lod else 9)
    A, Y = np.meshgrid(ang, ys)
    drum = np.stack([cx + np.cos(A) * oc, Y, cz + np.sin(A) * oc], -1)
    for flip in (False, True):
        kc.quad_strip(mb, drum, cer, uv=np.stack([A * oc, Y], -1) / 2.0, col=(0, 0, 0, 0.6), uv2=(0.7, 0.5), flip=flip)
    kc.tube(mb, np.stack([cx + np.cos(ang) * (oc + 0.05), np.full(na + 1, SHAFT_TOP), cz + np.sin(ang) * (oc + 0.05)],
                         -1), 0.12, 6, copper)
    if lod:
        return
    for k in range(12):  # the shaft's ribs
        th = 2 * math.pi * k / 12
        kc.tube(mb, np.array([[cx + math.cos(th) * (oc - 0.05), y, cz + math.sin(th) * (oc - 0.05)]
                              for y in (top_y, SHAFT_TOP)]), 0.1, 5, stone)
    for k in range(16):  # the dome's ribs, springing to the oculus
        th = 2 * math.pi * k / 16
        pts = np.array([[cx + math.cos(th) * rd * math.cos(e) * 0.99, SANCTUM_SPRING + rise * math.sin(e) - 0.05,
                         cz + math.sin(th) * rd * math.cos(e) * 0.99] for e in el])
        kc.tube(mb, pts, 0.14, 5, stone, weather=ll.STONE)


def build_well(seed: int = 1842) -> list[kc.MeshBuilder]:
    lay = layout()
    bl = {b["id"]: b for b in lay["blocks"]}
    ramps = {r["id"]: r for r in lay.get("ramps", [])}
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lowlight_well", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("lowlight_well" + ("-lod1" if lod else ""))
        for fid in ("Flight1", "Flight2"):
            r = ramps[fid]
            _flight(mb, rng, noise, r, lod)
            hi = max(r["from"][1], r["to"][1])
            for side in ("N", "S"):
                w = bl[f"{fid}Wall{side}"]
                top = hi + FLIGHT_VAULT_M + 1.6
                inward = (0.0, 1.0 if side == "N" else -1.0)
                _wall(mb, rng, noise, w, top, inward, lod, floor_y=min(r["from"][1], r["to"][1]), niches=False)
        # The landing between the flights, its walls and a short vault over it.
        ld = bl["ShaftLanding"]
        x0, x1, _, y1, z0, z1 = _box(ld)
        _flags(mb, rng, noise, x0, x1, z0, z1, y1, lod, wet=True)
        for side in ("N", "S"):
            w = bl[f"ShaftLandingWall{side}"]
            _wall(mb, rng, noise, w, y1 + FLIGHT_VAULT_M + 1.6, (0.0, 1.0 if side == "N" else -1.0), lod, floor_y=y1,
                  niches=False)
        _vault(mb, rng, x0, x1, z0 - 0.5, z1 + 0.5, y1 + FLIGHT_VAULT_M, y1 + FLIGHT_VAULT_M + 1.2, "x", lod,
               ribs_every=2.0)
        _sanctum(mb, rng, noise, bl, lod)
        # The threshold at the flight's foot (over the sanctum's west doorway): flags at the floor's level.
        s = bl["Sanctum"]
        sx0, _, _, sy1, _, _ = _box(s)
        _flags(mb, rng, noise, sx0 - 0.3, sx0 + 1.2, 2.25, 5.75, sy1, lod, wet=True)
        out.append(mb)
    return out


TARGETS = {"lowlight_atrium": build_atrium, "lowlight_hall": build_hall, "lowlight_well": build_well}
