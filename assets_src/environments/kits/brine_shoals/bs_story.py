"""Ch6's story pieces (act1_ch06.md; M3-ENV-703 for act1-chapters' request M3-ENV-1201). Pure numpy.

Each fits the greybox block it replaces in game/levels/ch06/brine_shoals/brine_shoals_layout.json:

  tide_wheel          the Saltwrights' undershot tide-wheel, 4 m across on a trestle (block 0.4 x 4 x 4); the
                      axle runs along X, the wheel turns in the YZ plane
  tide_wheel_burned   the same wheel burning and collapsing (B03-B06): charred, paddles gone, the rim broken and
                      slumped off its axle, embers in the trestle's foot
  ridge_fire          the party's small fire on the high hull at dusk (W15; block 0.6 x 0.4 x 0.6): a ring of shingle
                      stones, a driftwood cross-lay, an ember bed (the flames are VFX)
  level_stone_shrine  the wayside save shrine (B08; block 1 x 1.6 x 0.6): an Order Level-stone, chipped and still
                      tended, set into a wreck's bow-stem, its level line glowing faintly; front +Z
  vendor_boat         the travelling purser's small boat at the dusk camp (block 2 x 0.8 x 4): a beached clinker
                      skiff with an awning hoop, crates, jars and a hanging lamp; bow -Z
  hatch               the hold hatch in the hull's side (B03; block 0.1 x 1.2 x 1.4): a planked, iron-strapped
                      door in its frame, facing +X; origin at the panel's centre
  chalk_mark          the Saltwright camp-sign (B02): a chalk circle crossed by fine parallel lines, 0.8 m,
                      drawn on a hull side facing +X (origin at its centre, 4 mm proud of the plank)
  chalk_mark_heavy    the same sign nearer the camp: drawn over twice, thicker, with a tally of strokes

Origins: on the ground at the block's foot centre, except hatch and the chalk marks (their centre).
"""

from __future__ import annotations

import math

import numpy as np

import bs_common as bc
from bs_common import kc

M_CHALK = "bs_chalk"
M_LEVEL_STONE = "bs_level_stone"
M_LEVEL_GLOW = "bs_level_glow"

TRI_BUDGET = {
    "tide_wheel": (9000, 700),
    "ridge_fire": (2500, 200),
    "level_stone_shrine": (5000, 400),
    "vendor_boat": (9000, 800),
    "hatch": (2000, 120),
    "chalk_mark": (600, 60),
}
BUDGET_KEY = {"tide_wheel_burned": "tide_wheel", "chalk_mark_heavy": "chalk_mark"}

WHEEL_R = 1.62  # the paddles reach 2.0 m: the block is 4 m across
WHEEL_HUB_Y = 2.0
PADDLES = 12


def _spar(mb: kc.MeshBuilder, a, b, r: float, rng, noise, mat: str = bc.M_TIMBER, sides: int = 6) -> None:
    a, b = np.asarray(a, float), np.asarray(b, float)
    n = max(2, int(np.linalg.norm(b - a) / 0.5) + 1)
    kc.tube(mb, np.linspace(a, b, n), r, sides, mb.material(mat), weather=bc.CAMP, noise=noise, disp_m=r * 0.15,
            disp_period_m=0.3, variation=float(rng.random()), cap_start=True, cap_end=True, u_repeat=r * 6.3)


def _wheel(mb: kc.MeshBuilder, rng, noise, lod: bool, *, burned: bool) -> None:
    hub = np.array([0.0, WHEEL_HUB_Y, 0.0])
    tm = bc.M_TIMBER
    # The trestle: an A-frame each side of the wheel, a cross-tie, the axle through bronze bearings.
    for sx in (-0.16, 0.16):
        for sz in (-1.0, 1.0):
            _spar(mb, (sx, 0.0, sz * 1.1), (sx, WHEEL_HUB_Y + 0.12, 0.0), 0.06, rng, noise, sides=5 if lod else 6)
        if not lod:
            _spar(mb, (sx, 0.5, -0.86), (sx, 0.5, 0.86), 0.04, rng, noise)
            kc.tube(mb, np.array([[sx - 0.04, WHEEL_HUB_Y, 0.0], [sx + 0.04, WHEEL_HUB_Y, 0.0]]), 0.09, 10,
                    mb.material(bc.M_BRASS), cap_start=True, cap_end=True)
    _spar(mb, (-0.26, WHEEL_HUB_Y, 0.0), (0.26, WHEEL_HUB_Y, 0.0), 0.05, rng, noise, mat=bc.M_IRON)
    # The wheel. Burned: it has slumped off the axle (centre dropped and leaning), paddles burned away.
    slump = np.array([0.0, -0.55, 0.25]) if burned else np.zeros(3)
    tilt = kc.rot_x(0.18) @ kc.rot_z(0.12) if burned else np.eye(3)
    c = hub + slump
    seg = 24 if not lod else 10
    for sx in (-0.1, 0.1):
        a = np.linspace(0.0, 2 * math.pi, seg + 1)
        if burned:
            a = a[: int(seg * 0.72) + 1] + 0.9  # a quarter of the rim has burned through and fallen
        ring = np.stack([np.full_like(a, sx), np.cos(a) * WHEEL_R, np.sin(a) * WHEEL_R], axis=-1) @ tilt.T + c
        kc.tube(mb, ring, 0.045, 5 if not lod else 3, mb.material(tm), weather=bc.CAMP, variation=float(rng.random()))
    keep = [k for k in range(PADDLES) if not burned or k % 3 != 1]
    for k in keep:
        a = 2 * math.pi * k / PADDLES
        d = np.array([0.0, math.cos(a), math.sin(a)])
        spoke_end = d * (WHEEL_R - 0.05)
        if burned and not (0.9 <= (a - 0.9) % (2 * math.pi) <= 0.9 + 2 * math.pi * 0.72):
            spoke_end = spoke_end * 0.55  # the spokes of the fallen quarter end in charred stubs
        kc.tube(mb, (np.array([np.zeros(3), spoke_end]) @ tilt.T) + c, 0.035, 5 if not lod else 3, mb.material(tm),
                weather=bc.CAMP, variation=float(rng.random()), cap_end=True)
        if spoke_end is not None and np.linalg.norm(spoke_end) > WHEEL_R * 0.9:
            # The paddle: a board across both rims at the spoke's end, set radially.
            pc = d * (WHEEL_R + 0.12)
            rot = np.column_stack([np.array([1.0, 0.0, 0.0]), d, np.cross(np.array([1.0, 0.0, 0.0]), d)])
            kc.rounded_block(mb, tilt @ pc + c, (0.17, 0.28, 0.018), mb.material(tm), rot=tilt @ rot, radius=0.008,
                             seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.003, weather=bc.CAMP,
                             variation=float(rng.random()))
    if burned and not lod:
        # Embers where the fallen boards burn on in the trestle's foot.
        for k in range(18):
            p = np.array([rng.uniform(-0.4, 0.4), 0.04, rng.uniform(-0.9, 0.9)])
            s = rng.uniform(0.04, 0.09)
            slot = bc.M_EMBER if rng.random() < 0.5 else bc.M_CHAR
            kc.rounded_block(mb, p, (s, s * 0.5, s * 1.6), mb.material(slot), rot=kc.rot_y(rng.uniform(0, 3)),
                             radius=s * 0.3, seg=1, variation=float(rng.random()))


def build_tide_wheel(seed: int = 731, *, burned: bool = False) -> list[kc.MeshBuilder]:
    name = "tide_wheel_burned" if burned else "tide_wheel"
    out = []
    for lod in (False, True):
        rng = kc.rng_for("tide_wheel", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (bc.LOD if lod else ""))
        _wheel(mb, rng, noise, lod, burned=burned)
        if burned:
            field = bc.CharField((0.0, 0.3, 0.2), 3.2, kc.rng_for("tide_wheel_char", seed), climb=0.25)
            bc.apply_char(mb, field, char_at=0.45, scorch_at=0.12)
        out.append(mb)
    return out


def build_ridge_fire(seed: int = 732) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ridge_fire", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("ridge_fire" + (bc.LOD if lod else ""))
        n = 11 if not lod else 6
        for k in range(n):
            a = 2 * math.pi * k / n + rng.uniform(-0.1, 0.1)
            r = rng.uniform(0.05, 0.075)
            p = np.array([math.cos(a) * 0.26, r * 0.55, math.sin(a) * 0.26])
            kc.rounded_block(mb, p, (r, r * 0.7, r * 0.85), mb.material(bc.M_GRIT), rot=kc.rot_y(a), radius=r * 0.5,
                             seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.008, weather=bc.CAMP,
                             variation=float(rng.random()))
        kc.rounded_block(mb, (0.0, 0.025, 0.0), (0.2, 0.025, 0.2), mb.material(bc.M_ASH), radius=0.02, seg=1)
        if lod:
            kc.rounded_block(mb, (0.0, 0.08, 0.0), (0.14, 0.05, 0.14), mb.material(bc.M_EMBER), radius=0.03, seg=1)
            out.append(mb)
            continue
        # Driftwood laid in a star, the ends charred where they meet over the coals.
        for k in range(5):
            a = 2 * math.pi * k / 5 + 0.3
            d = np.array([math.cos(a), 0.0, math.sin(a)])
            inner = d * 0.04 + np.array([0.0, 0.11, 0.0])
            outer = d * 0.3 + np.array([0.0, 0.05, 0.0])
            kc.tube(mb, np.array([outer, inner]), np.array([0.028, 0.022]), 6, mb.material(bc.M_TIMBER),
                    weather=bc.CAMP, cap_start=True, cap_end=True, variation=float(rng.random()))
            kc.tube(mb, np.array([d * 0.1 + [0, 0.1, 0], inner]), 0.024, 6, mb.material(bc.M_CHAR), cap_end=True)
        for k in range(14):
            a, r = rng.uniform(0, 2 * math.pi), 0.16 * math.sqrt(rng.random())
            s = rng.uniform(0.025, 0.045)
            p = np.array([math.cos(a) * r, 0.05 + 0.03 * (1 - r / 0.16), math.sin(a) * r])
            slot = bc.M_EMBER if rng.random() < 0.6 else bc.M_CHAR
            kc.rounded_block(mb, p, (s, s * 0.6, s * 0.8), mb.material(slot), rot=kc.rot_y(rng.uniform(0, 3)),
                             radius=s * 0.4, seg=1, variation=float(rng.random()))
        out.append(mb)
    return out


def build_level_stone_shrine(seed: int = 733) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("level_stone_shrine", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("level_stone_shrine" + (bc.LOD if lod else ""))
        # The wreck's bow-stem, cut off and set upright: two strakes curving in to a stem post behind the stone.
        for sx in (-1.0, 1.0):
            t = np.linspace(0.0, 1.0, 7 if not lod else 3)
            for k in range(4 if not lod else 2):
                y = 0.15 + k * (0.36 if not lod else 0.72)
                x = sx * (0.48 - 0.3 * t ** 1.6)
                z = -0.28 * t + 0.1
                pts = np.stack([x, np.full_like(t, y) + 0.08 * t, z], axis=-1)
                kc.tube(mb, pts, 0.06, 4, mb.material(bc.M_TAR), weather=bc.WRECK, variation=float(rng.random()),
                        cap_start=True, cap_end=True)
        _spar(mb, (0.0, 0.0, -0.2), (0.02, 1.6, -0.24), 0.07, rng, noise, mat=bc.M_TAR)
        # The Level-stone: a dressed slab on a plinth, its top chipped at one corner, the level line across it.
        kc.rounded_block(mb, (0.0, 0.1, 0.02), (0.36, 0.1, 0.24), mb.material(M_LEVEL_STONE), radius=0.03,
                         seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.006, weather=bc.CAMP)
        kc.rounded_block(mb, (0.0, 0.72, 0.0), (0.26, 0.52, 0.09), mb.material(M_LEVEL_STONE), radius=0.04,
                         seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.01, weather=bc.CAMP,
                         variation=0.4)
        kc.rounded_block(mb, (0.0, 0.88, 0.093), (0.2, 0.012, 0.004), mb.material(M_LEVEL_GLOW), radius=0.003, seg=1)
        if not lod:
            # The chip: a dark scar on the top corner (a faceted block of the same stone, set in).
            kc.rounded_block(mb, (0.2, 1.2, 0.02), (0.07, 0.05, 0.1), mb.material(bc.M_GRIT),
                             rot=kc.rot_z(0.6), radius=0.01, seg=1)
            # Still tended: a clay bowl, two shells and a strip of teal cloth tied round the stem.
            ys = np.linspace(0.0, 1.0, 6)
            bowl = np.stack([0.06 + 0.06 * np.sin(ys * math.pi * 0.5), 0.2 + ys * 0.06], axis=-1)
            kc.tube(mb, np.stack([np.zeros(6) - 0.2, bowl[:, 1], np.zeros(6) + 0.15], axis=-1), bowl[:, 0], 12,
                    mb.material(bc.M_CERAMIC), cap_start=True)
            for (x, z) in ((0.16, 0.18), (0.25, 0.12)):
                kc.rounded_block(mb, (x, 0.215, z), (0.03, 0.015, 0.02), mb.material(bc.M_SALT), radius=0.012, seg=2)
            a = np.linspace(0.0, 2 * math.pi, 9)
            ring = np.stack([np.cos(a) * 0.085 + 0.02, np.full(9, 1.35), np.sin(a) * 0.085 - 0.24], axis=-1)
            kc.tube(mb, ring, 0.02, 4, mb.material(bc.M_CANVAS_TEAL), variation=0.4)
            tail = np.array([[0.1, 1.35, -0.18], [0.16, 1.15, -0.12], [0.2, 0.98, -0.1]])
            kc.tube(mb, tail, 0.012, 4, mb.material(bc.M_CANVAS_TEAL), variation=0.6, cap_end=True)
        out.append(mb)
    return out


def build_vendor_boat(seed: int = 734) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("vendor_boat", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("vendor_boat" + (bc.LOD if lod else ""))
        tm = mb.material(bc.M_TAR)
        # A clinker skiff: each side a lofted surface (keel to sheer over the stations, both faces, so the
        # inside reads from above), the strakes' lap edges as thin battens, beached with a slight list.
        lst = kc.rot_z(0.06)
        stations = np.linspace(-1.95, 1.95, 13 if not lod else 5)
        levels = np.linspace(0.0, 1.0, 7 if not lod else 3)
        T = stations / 1.95

        def hull_pt(f, t, side):
            half = 0.92 * (1 - t ** 2) ** 0.55 + 0.02
            y = 0.06 + f * 0.62 + 0.2 * t ** 2  # the sheer rises to bow and stern
            x = side * half * (0.25 + 0.75 * math.sin(f * math.pi * 0.5))
            return np.array([x, y, t * 1.95])

        for side in (-1.0, 1.0):
            grid = np.array([[hull_pt(f, t, side) for t in T] for f in levels]) @ lst.T
            uv = np.stack(np.meshgrid(stations, levels * 0.9), axis=-1)
            for flip in (False, True):
                kc.quad_strip(mb, grid, tm, uv=uv, col=np.array([0.0, 0.5, 0.25, 0.6]),
                              uv2=np.array([0.85 if flip else 1.0, float(rng.random())]), flip=(side > 0) != flip)
            if not lod:
                for f in levels[1:]:
                    lap = np.array([hull_pt(f, t, side * 1.01) for t in T]) @ lst.T
                    kc.tube(mb, lap, 0.014, 4, tm, weather=bc.WRECK, variation=float(rng.random()))
        kc.tube(mb, np.array([[0.0, 0.0, -1.85], [0.0, 0.9, -2.0]]) @ lst.T, 0.05, 5, tm, cap_end=True)
        kc.rounded_block(mb, np.array([0.0, 0.08, 0.0]), (0.3, 0.05, 1.5), tm, rot=lst, radius=0.02, seg=1)
        if lod:
            kc.rounded_block(mb, (0.0, 0.5, 0.4), (0.4, 0.25, 0.4), mb.material(bc.M_TIMBER), radius=0.04, seg=1)
            out.append(mb)
            continue
        # Thwarts, the awning hoop and its sail-cloth, the purser's goods and a lamp on the hoop.
        for z in (-0.9, 0.2, 1.1):
            kc.plank(mb, np.array([-0.8, 0.5, z]) @ lst.T, np.array([0.8, 0.5, z]) @ lst.T, 0.18, 0.04,
                     mb.material(bc.M_TIMBER), variation=float(rng.random()), noise=noise)
        a = np.linspace(0.0, math.pi, 11)
        hoops = []
        for z in (0.4, 1.4):
            hoop = np.stack([np.cos(a) * 0.82, 0.55 + np.sin(a) * 0.95, np.full_like(a, z)], axis=-1) @ lst.T
            kc.tube(mb, hoop, 0.025, 5, mb.material(bc.M_TIMBER), variation=float(rng.random()))
            hoops.append(hoop)
        grid = np.stack([hoops[0], hoops[1]], axis=0)
        uv = np.stack([np.tile(np.linspace(0, 2.8, 11), (2, 1)), np.array([[0.0] * 11, [1.0] * 11])], axis=-1)
        for flip in (False, True):
            kc.quad_strip(mb, grid + (np.array([0.0, 0.01, 0.0]) if flip else 0.0), mb.material(bc.M_CANVAS_TEAL),
                          uv=uv, col=np.array([0.0, 0.2, 0.0, 0.3]), uv2=np.array([0.9, 0.5]), flip=flip)
        for (x, z, s) in ((-0.35, 0.6, 0.22), (0.3, 0.7, 0.18), (-0.1, 1.2, 0.2)):
            kc.rounded_block(mb, np.array([x, 0.13 + s, z]) @ lst.T, (s, s, s * 0.9), mb.material(bc.M_TIMBER),
                             rot=kc.rot_y(rng.uniform(-0.4, 0.4)), radius=0.015, seg=2, noise=noise, disp_m=0.003,
                             variation=float(rng.random()))
        for (x, z) in ((0.25, 1.2), (0.42, 0.9)):
            ys = np.linspace(0.0, 1.0, 7)
            r = 0.08 + 0.07 * np.sin(np.clip(ys / 0.8, 0, 1) * math.pi)
            kc.tube(mb, np.stack([np.full(7, x), 0.13 + ys * 0.4, np.full(7, z)], axis=-1) @ lst.T, r, 12,
                    mb.material(bc.M_CERAMIC), cap_start=True)
        top = np.array([0.0, 1.5, 1.4]) @ lst.T
        kc.tube(mb, np.array([top, top - [0, 0.2, 0]]), 0.006, 3, mb.material(bc.M_ROPE))
        kc.rounded_block(mb, top - [0, 0.32, 0], (0.06, 0.1, 0.06), mb.material(bc.M_GLASS), radius=0.01, seg=1)
        kc.rounded_block(mb, top - [0, 0.2, 0], (0.07, 0.015, 0.07), mb.material(bc.M_BRASS), radius=0.005, seg=1)
        out.append(mb)
    return out


def build_hatch(seed: int = 735) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hatch", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("hatch" + (bc.LOD if lod else ""))
        rot = np.column_stack([[0.0, 0.0, -1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]])  # local +Z -> world +X
        if lod:
            kc.rounded_block(mb, (0.0, 0.0, 0.0), (0.05, 0.6, 0.7), mb.material(bc.M_TAR), radius=0.02, seg=1)
            out.append(mb)
            continue
        # The frame (coaming) and five vertical planks, two iron straps and a ring pull.
        for (a, b) in (((-0.65, -0.55), (0.65, -0.55)), ((-0.65, 0.55), (0.65, 0.55)),
                       ((-0.65, -0.55), (-0.65, 0.55)), ((0.65, -0.55), (0.65, 0.55))):
            kc.plank(mb, rot @ np.array([a[0], a[1], 0.0]), rot @ np.array([b[0], b[1], 0.0]), 0.1, 0.08,
                     mb.material(bc.M_TAR), up=rot @ np.array([0.0, 0.0, 1.0]), variation=float(rng.random()))
        for k in range(5):
            z = -0.5 + k * 0.25
            kc.plank(mb, rot @ np.array([z, -0.5, 0.01]), rot @ np.array([z, 0.5, 0.01]), 0.23, 0.04,
                     mb.material(bc.M_TIMBER), up=rot @ np.array([0.0, 0.0, 1.0]), variation=float(rng.random()),
                     noise=noise)
        for y in (-0.35, 0.35):
            kc.plank(mb, rot @ np.array([-0.62, y, 0.04]), rot @ np.array([0.5, y, 0.04]), 0.06, 0.01,
                     mb.material(bc.M_IRON), up=rot @ np.array([0.0, 0.0, 1.0]))
        a = np.linspace(0.0, 2 * math.pi, 11)
        ring = np.stack([0.45 + np.cos(a) * 0.05, np.sin(a) * 0.05 - 0.05, np.full(11, 0.06)], axis=-1) @ rot.T
        kc.tube(mb, ring, 0.008, 4, mb.material(bc.M_IRON))
        out.append(mb)
    return out


def _stroke(mb: kc.MeshBuilder, pts: np.ndarray, width: float, mat: int) -> None:
    """A chalk stroke along a polyline in the local YZ plane (x = proud of the plank), facing +X."""
    pts = np.asarray(pts, float)
    d = np.gradient(pts, axis=0)
    d = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    side = np.cross(np.array([1.0, 0.0, 0.0]), d) * width * 0.5
    grid = np.stack([pts - side, pts + side], axis=1)
    n = len(pts)
    uv = np.stack([np.tile([0.0, 1.0], (n, 1)), np.tile(np.linspace(0, 1, n)[:, None], (1, 2))], axis=-1)
    base = mb.add_vertices(grid.reshape(-1, 3), np.tile([1.0, 0.0, 0.0], (2 * n, 1)), uv.reshape(-1, 2),
                           np.tile([0.9, 0.5], (2 * n, 1)), np.tile([0.0, 0.0, 0.0, 0.0], (2 * n, 1)))
    for k in range(n - 1):
        a, b, c, e = base + 2 * k, base + 2 * k + 1, base + 2 * k + 2, base + 2 * k + 3
        # Wound to face +X (the normals above).
        for tri in ((a, c, b), (b, c, e)):
            p = np.asarray(mb.pos)[list(tri)]
            if np.dot(np.cross(p[1] - p[0], p[2] - p[0]), [1.0, 0.0, 0.0]) < 0:
                tri = (tri[0], tri[2], tri[1])
            mb.add_tri(*tri, mat)


def build_chalk_mark(seed: int = 736, *, heavy: bool = False) -> list[kc.MeshBuilder]:
    name = "chalk_mark_heavy" if heavy else "chalk_mark"
    out = []
    for lod in (False, True):
        rng = kc.rng_for("chalk_mark", seed)
        mb = kc.MeshBuilder(name + (bc.LOD if lod else ""))
        m = mb.material(M_CHALK)
        w = (0.035 if heavy else 0.022) * (1.6 if lod else 1.0)
        x = 0.004
        passes = 2 if heavy and not lod else 1
        for p in range(passes):
            a = np.linspace(0.0, 2 * math.pi * 1.04, 33 if not lod else 12) + p * 0.2
            r = 0.3 + rng.normal(0, 0.006, len(a)) + p * 0.012
            _stroke(mb, np.stack([np.full_like(a, x + p * 0.0015), np.sin(a) * r, np.cos(a) * r], axis=-1), w, m)
        # The fine parallel lines through the circle (the "wrights work here" sign), slightly slanted.
        for k in range(5 if not lod else 3):
            off = -0.2 + k * (0.1 if not lod else 0.2)
            t = np.linspace(-1.0, 1.0, 5 if not lod else 2)
            ys = np.full_like(t, off) + t * 0.04
            zs = t * math.sqrt(max(0.3 ** 2 - off ** 2, 0.01)) * 1.1
            # Crossing strokes sit a little prouder than the circle, so they don't z-fight where they cross.
            _stroke(mb, np.stack([np.full_like(t, x + 0.003), ys, zs], axis=-1), w * 0.7, m)
        if heavy and not lod:
            for k in range(4):  # a tally under the sign
                z = -0.12 + k * 0.08
                _stroke(mb, np.array([[x + 0.003, -0.36, z], [x + 0.003, -0.46, z + 0.01]]), w * 0.7, m)
        out.append(mb)
    return out


TARGETS = {
    "tide_wheel": build_tide_wheel,
    "tide_wheel_burned": lambda: build_tide_wheel(burned=True),
    "ridge_fire": build_ridge_fire,
    "level_stone_shrine": build_level_stone_shrine,
    "vendor_boat": build_vendor_boat,
    "hatch": build_hatch,
    "chalk_mark": build_chalk_mark,
    "chalk_mark_heavy": lambda: build_chalk_mark(heavy=True),
}
