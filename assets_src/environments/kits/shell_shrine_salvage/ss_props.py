"""Shell Shrine door, charm and exterior (haluna.md §3.2 Inner pool and chamber door, Side pool, Exterior).

  chamber_door_valve   the carved shell-valve door, 3.0 m wide, 3.4 m tall, 0.6 m thick: a stone leaf with a
                       great scallop in relief (hinge at the foot, ribs fanning up), its rim inlaid with
                       nacre. Origin at the centre of its base; it faces local -X (into the room from the
                       east wall) and sinks in -Y.
  net_float_charm      a 6 cm salt-glass float in a knotted twine net, with a hanging loop
  exterior_steps       outside the west entrance (local +X runs outward from the wall's outer face): the
                       porch landing, six steps to a lower landing, three steps to the tidepool, low cheek
                       walls with mortar copings, all on coursed foundations
  sea_stones           stepping stones across the last tidepool and wave-rounded boulders (local +X outward)
  offering_shelf       a low ledge with a fan-shell back, for leaf-boats and flowers (front faces local +X)
  leaf_boat            a folded green leaf boat with a frangipani flower (0.28 m long, along local X)
"""

from __future__ import annotations

import math

import numpy as np

import ss_common as sc
from ss_common import kc

M = sc.METRICS

TRI_BUDGET = {
    "chamber_door_valve": (9000, 200),
    "net_float_charm": (1200, 80),
    "exterior_steps": (16000, 600),
    "sea_stones": (9000, 500),
    "offering_shelf": (4000, 200),
    "leaf_boat": (500, 60),
}


# ---------------------------------------------------------------------------------------------
# The chamber door
# ---------------------------------------------------------------------------------------------
def _valve_relief(z: np.ndarray, y: np.ndarray, w: float, h: float):
    """Relief depth (m, towards the viewer) and a rim mask for the scallop on the door's face."""
    hz, hy = 0.0, 0.12  # the hinge, at the foot
    dz, dy = z - hz, y - hy
    r = np.hypot(dz, dy)
    th = np.arctan2(dz, np.maximum(dy, 1e-6))  # 0 = straight up
    span = math.radians(78.0)
    ribs = 15
    edge = (h - 0.25) * (1.0 - 0.04 * (0.5 - 0.5 * np.cos(th * ribs * math.pi / span)))
    edge = np.minimum(edge, (w * 0.5 - 0.1) / np.maximum(np.abs(np.sin(th)), 1e-3))
    inside = (np.abs(th) < span) & (r < edge) & (dy > -0.05)
    f = np.clip(r / np.maximum(edge, 1e-6), 0.0, 1.0)
    dome = 0.11 * np.sqrt(np.clip(1.0 - f * f, 0.0, 1.0)) * kc.smoothstep(0.0, 0.25, f + 0.05)
    rib = 0.028 * (0.5 + 0.5 * np.cos(th * ribs * math.pi / span * 2.0)) * kc.smoothstep(0.08, 0.35, f)
    depth = np.where(inside, dome + rib, 0.0)
    # The two "ears" of a scallop at the hinge, as low square bosses.
    ears = (np.abs(np.abs(dz) - 0.42) < 0.3) & (dy < 0.55) & (dy > 0.0)
    depth = np.where(ears & ~inside, 0.05, depth)
    rim = inside & (r > edge - 0.07)
    return depth, rim, inside


def build_door(seed: int = 501) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("chamber_door_valve", seed)
    noise = kc.Noise3(rng)
    w, h, t = M["door_w_m"], M["door_h_m"], M["door_t_m"]
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("chamber_door_valve" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        # Core leaf (its front 1 cm behind the relief sheet).
        kc.rounded_block(mb, (0.03, h * 0.5, 0.0), (t * 0.5 - 0.03, h * 0.5, w * 0.5), stone, radius=0.04,
                         seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.008, weather=sc.TENDED,
                         variation=0.4)
        if lod:
            out.append(mb)
            continue
        nz, ny = 60, 70
        zs = np.linspace(-w * 0.5 + 0.02, w * 0.5 - 0.02, nz)
        ys = np.linspace(0.02, h - 0.02, ny)
        Z, Y = np.meshgrid(zs, ys)
        depth, rim, inside = _valve_relief(Z, Y, w, h)
        X = -t * 0.5 + 0.01 - depth
        grid = np.stack([X, Y, Z], axis=-1)
        breakup = noise.fbm(grid / 0.35, 2)
        col = sc.col4(0.02 * breakup, 0.25 + 0.4 * (depth < 0.02) * inside * breakup, 0.0,
                      0.2 + 0.5 * rim + 0.2 * breakup)
        uv2 = np.stack([0.6 + 0.4 * np.clip(depth / 0.12, 0, 1), np.full(depth.shape, 0.4)], axis=-1)
        # Rows ascend (+Y), columns run +Z: +Z x +Y = -X, the door's front. No flip.
        kc.quad_strip(mb, grid, stone, uv=np.stack([Z, Y], axis=-1), col=col, uv2=uv2, flip=False)
        # Nacre along the scallop's rim.
        span = math.radians(76.0)
        th = np.linspace(-span, span, 61)
        ribs = 15
        edge = (h - 0.25) * (1.0 - 0.04 * (0.5 - 0.5 * np.cos(th * ribs * math.pi / math.radians(78.0))))
        edge = np.minimum(edge, (w * 0.5 - 0.1) / np.maximum(np.abs(np.sin(th)), 1e-3)) - 0.035
        pz, py = np.sin(th) * edge, 0.12 + np.cos(th) * edge
        d, _, _ = _valve_relief(pz, py, w, h)
        pts = np.stack([-t * 0.5 + 0.01 - d - 0.004, py, pz], axis=-1)
        sc.nacre_band(mb, pts, (-1.0, 0.0, 0.0), 0.04, mb.material(sc.M_NACRE))
        out.append(mb)
    col = kc.MeshBuilder("chamber_door_valve-col")
    sc.box_proxy(col, (0.0, h * 0.5, 0.0), (t * 0.5, h * 0.5, w * 0.5))
    return out + [col]


# ---------------------------------------------------------------------------------------------
# Net-float charm
# ---------------------------------------------------------------------------------------------
def build_charm(seed: int = 502) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("net_float_charm", seed)
    r = M["charm_d_m"] * 0.5
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("net_float_charm" + ("-lod1" if lod else ""))
        glass = mb.material(sc.M_GLASS)
        rows, sides = (4, 8) if lod else (12, 20)
        el = np.linspace(math.pi * 0.5, -math.pi * 0.5, rows + 1)
        prof = [(max(r * math.cos(e), 1e-4), r + r * math.sin(e)) for e in el]  # top -> bottom: outward
        sc.lathe(mb, prof, sides, glass, weather=kc.Weathering(moss=0, salt=0.1, wet=0.3, erosion=0.05),
                 variation=0.5)
        if not lod:
            lash = mb.material(sc.M_LASHING)
            c = np.array([0.0, r, 0.0])
            ro = r + 0.0015
            for k in range(5):  # meridian cords, knotted at the poles
                a = 2 * math.pi * k / 5 + 0.2
                e = np.linspace(-math.pi * 0.5 + 0.15, math.pi * 0.5 - 0.15, 9)
                pts = c + np.stack([np.cos(e) * math.cos(a) * ro, np.sin(e) * ro, np.cos(e) * math.sin(a) * ro], axis=-1)
                kc.tube(mb, pts, 0.0012, 3, lash, variation=float(rng.random()))
            for e0 in (-0.35, 0.35):  # two rings of mesh
                a = np.linspace(0, 2 * math.pi, 17)
                rr = math.cos(e0) * ro
                pts = c + np.stack([np.cos(a) * rr, np.full_like(a, math.sin(e0) * ro), np.sin(a) * rr], axis=-1)
                kc.tube(mb, pts, 0.0012, 3, lash, variation=0.3)
            loop_a = np.linspace(0.0, math.pi, 9)
            loop = c + np.stack([np.cos(loop_a) * 0.008, ro + np.sin(loop_a) * 0.012, np.zeros(9)], axis=-1)
            kc.tube(mb, loop, 0.0013, 3, lash, variation=0.6)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Exterior: west steps and landings
# ---------------------------------------------------------------------------------------------
def _foundation(mb, rng, noise, x0: float, x1: float, z0: float, z1: float, y_top: float, *, lod: bool) -> None:
    """A coursed block mass from the foundation line up to y_top (the sides show; the top is paved)."""
    stone = mb.material(sc.M_STONE)
    y_f = M["foundation_y_m"]
    if lod:
        kc.rounded_block(mb, (0.5 * (x0 + x1), 0.5 * (y_f + y_top), 0.5 * (z0 + z1)),
                         (0.5 * (x1 - x0), 0.5 * (y_top - y_f), 0.5 * (z1 - z0)), stone, radius=0.02, seg=1)
        return
    # Three exposed faces (+X front, +-Z sides) as ashlar skins 0.4 m thick.
    for frame, length, thick, s_rng in (
        (lambda s: (np.array([x1 - 0.2, 0.0, s]), kc.rot_y(math.pi * 0.5)), z1 - z0, 0.4, (z0, z1)),
        (lambda s: (np.array([s, 0.0, z1 - 0.2]), np.eye(3)), x1 - x0, 0.4, (x0, x1 - 0.4)),
        (lambda s: (np.array([s, 0.0, z0 + 0.2]), np.eye(3)), x1 - x0, 0.4, (x0, x1 - 0.4)),
    ):
        sc.wall_blocks(mb, frame, length, thick, y_f, y_top - 0.1, rng, noise, mat=stone, seg=2, block_mean=0.75,
                       course_mean=0.38, s_range=s_rng, weather=sc.SEAWORN if y_top < -0.6 else sc.TENDED,
                       low_seg_below=-1.2)


def _flags(mb, rng, noise, x0: float, x1: float, z0: float, z1: float, y: float, *, lod: bool, row_w: float = 0.55,
           weather=None) -> None:
    """Flagstones paving a rectangle (top at y)."""
    pav = mb.material(sc.M_PAVING)
    wz = weather or kc.Weathering(moss=0.05, salt=0.35, wet=0.0, erosion=0.45)
    if lod:
        kc.rounded_block(mb, (0.5 * (x0 + x1), y - 0.06, 0.5 * (z0 + z1)), (0.5 * (x1 - x0), 0.06, 0.5 * (z1 - z0)),
                         pav, radius=0.01, seg=1)
        return
    rows = max(1, int(round((z1 - z0) / row_w)))
    rw = (z1 - z0) / rows
    for r in range(rows):
        for b0, b1 in sc.split_run(x1 - x0, rng, mean=0.7, spread=0.2, offset=0.3 * (r % 2) + 0.1):
            kc.rounded_block(mb, (x0 + 0.5 * (b0 + b1), y - 0.06, z0 + rw * (r + 0.5)),
                             (0.5 * (b1 - b0) - 0.008, 0.06, rw * 0.5 - 0.008), pav, radius=0.02, seg=2, noise=noise,
                             disp_m=0.004, weather=wz, variation=float(rng.random()))


STEP_SPECS = {"porch": (0.0, 2.2, 2.8), "upper_steps": 6, "steps_w": 2.0, "landing": (2.0, 2.3),
              "lower_steps": 3}


def exterior_layout() -> dict:
    """Step and landing extents (local +X outward); also used to place leaf-boats (manifest metrics)."""
    rise, run = M["step_rise_m"], M["step_run_m"]
    p0, p1, pw = STEP_SPECS["porch"]
    x = p1
    y = 0.0
    steps = []
    for _ in range(STEP_SPECS["upper_steps"]):
        steps.append((x, x + run, y - rise))
        x += run
        y -= rise
    land = (x, x + STEP_SPECS["landing"][0], y, STEP_SPECS["landing"][1])
    x += STEP_SPECS["landing"][0]
    for _ in range(STEP_SPECS["lower_steps"]):
        steps.append((x, x + run, y - rise))
        x += run
        y -= rise
    return {"porch": (p0, p1, pw), "steps": steps, "landing": land, "end_x": x, "end_y": y,
            "steps_w": STEP_SPECS["steps_w"]}


def build_exterior_steps(seed: int = 511) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("exterior_steps", seed)
    noise = kc.Noise3(rng)
    lay = exterior_layout()
    p0, p1, pw = lay["porch"]
    sw = lay["steps_w"]
    rise = M["step_rise_m"]
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("exterior_steps" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        mor = mb.material(sc.M_MORTAR)
        # Porch: paved, on its foundation, flanked by low parapets.
        _foundation(mb, rng, noise, p0 - 0.6, p1, -pw, pw, 0.0, lod=lod)
        _flags(mb, rng, noise, p0 - 0.3, p1, -pw, pw, 0.0, lod=lod)
        # Steps (each a long tread stone over a riser), worn in the middle where feet go.
        for k, (x0, x1, y) in enumerate(lay["steps"]):
            wear = kc.Weathering(moss=0.04, salt=0.4, wet=0.25 if y < -1.2 else 0.0, erosion=0.6)
            if lod:
                kc.rounded_block(mb, (0.5 * (x0 + x1), 0.5 * (y + M["foundation_y_m"]), 0.0),
                                 (0.5 * (x1 - x0) + 0.02, 0.5 * (y - M["foundation_y_m"]), sw), stone, radius=0.01,
                                 seg=1)
                continue
            n_st = 3
            for j in range(n_st):
                z0 = -sw + 2 * sw * j / n_st
                z1 = -sw + 2 * sw * (j + 1) / n_st
                kc.rounded_block(mb, (0.5 * (x0 + x1) + 0.02, y - rise * 0.5, 0.5 * (z0 + z1)),
                                 (0.5 * (x1 - x0) + 0.03, rise * 0.5 - 0.006, 0.5 * (z1 - z0) - 0.008), stone,
                                 radius=0.035, seg=3, noise=noise, disp_m=0.008, weather=wear,
                                 variation=float(rng.random()))
            kc.rounded_block(mb, (0.5 * (x0 + x1), 0.5 * (y - rise + M["foundation_y_m"]), 0.0),
                             (0.5 * (x1 - x0), 0.5 * (y - rise - M["foundation_y_m"]), sw - 0.01), stone, radius=0.02,
                             seg=1, weather=sc.SEAWORN, variation=0.5)
        lx0, lx1, ly, lw = lay["landing"]
        _foundation(mb, rng, noise, lx0, lx1, -lw, lw, ly, lod=lod)
        _flags(mb, rng, noise, lx0, lx1, -lw, lw, ly, lod=lod)
        # Cheek walls beside the upper flight: coursed, with sloping mortar copings.
        sx0, sx1 = lay["steps"][0][0], lay["steps"][STEP_SPECS["upper_steps"] - 1][1]
        for sgn in (-1.0, 1.0):
            zc = sgn * (sw + 0.22)
            if lod:
                kc.rounded_block(mb, (0.5 * (sx0 + sx1), -0.5, zc), (0.5 * (sx1 - sx0), 0.9, 0.22), stone,
                                 radius=0.01, seg=1)
                continue

            def cheek(s: float, zc=zc):
                return np.array([s, 0.0, zc]), np.eye(3)

            sc.wall_blocks(mb, cheek, sx1 - sx0, 0.44, M["foundation_y_m"], -0.9, rng, noise, mat=stone, seg=2,
                           s_range=(sx0, sx1), course_mean=0.36, block_mean=0.7, low_seg_below=-1.2)
            # The stepped upper courses follow the flight down.
            for k in range(STEP_SPECS["upper_steps"]):
                x0, x1, y = lay["steps"][k]
                top = y + 0.45
                kc.rounded_block(mb, (0.5 * (x0 + x1), 0.5 * (-0.9 + top), zc), (0.5 * (x1 - x0) - 0.01,
                                 0.5 * (top + 0.9), 0.22), stone, radius=0.03, seg=2, noise=noise, disp_m=0.008,
                                 weather=sc.TENDED, variation=float(rng.random()))
                kc.rounded_block(mb, (0.5 * (x0 + x1), top + 0.05, zc), (0.5 * (x1 - x0) + 0.005, 0.05, 0.25), mor,
                                 radius=0.025, seg=2, weather=sc.TENDED, variation=0.2)
        out.append(mb)
    col = kc.MeshBuilder("exterior_steps-col")
    sc.box_proxy(col, (0.5 * (p0 - 0.6 + p1), -1.0, 0.0), (0.5 * (p1 - p0 + 0.6), 1.0, pw))
    for x0, x1, y in lay["steps"]:
        sc.box_proxy(col, (0.5 * (x0 + x1), 0.5 * (y + M["foundation_y_m"]), 0.0),
                     (0.5 * (x1 - x0), 0.5 * (y - M["foundation_y_m"]), sw))
    lx0, lx1, ly, lw = lay["landing"]
    sc.box_proxy(col, (0.5 * (lx0 + lx1), 0.5 * (ly + M["foundation_y_m"]), 0.0),
                 (0.5 * (lx1 - lx0), 0.5 * (ly - M["foundation_y_m"]), lw))
    return out + [col]


def build_sea_stones(seed: int = 512) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("sea_stones", seed)
    noise = kc.Noise3(rng)
    lay = exterior_layout()
    x_start = 0.15
    water = M["foundation_y_m"] + 0.2  # mean water at the islet (the preview's tidepool level)
    stones = []
    # Stepping stones: flat-topped, a stride apart, wandering a little.
    x = x_start
    for k in range(9):
        z = 0.35 * math.sin(k * 1.3) + 0.15 * (float(rng.random()) - 0.5)
        stones.append(((x, water + 0.14 + 0.03 * float(rng.random()), z), (0.32, 0.12, 0.27), 0.25, True))
        x += 0.72 + 0.12 * float(rng.random())
    # Boulders either side, larger towards the islet.
    for k in range(16):
        side = -1.0 if k % 2 else 1.0
        bx = x_start + float(rng.random()) * (x - x_start) * 0.9
        bz = side * (1.0 + float(rng.random()) * 2.4 + 0.8 * (1.0 - bx / x))
        s = 0.25 + 0.55 * float(rng.random()) * (1.2 - bx / x)
        stones.append(((bx, water + s * 0.15, bz), (s * 1.2, s * 0.7, s), 0.6, False))
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("sea_stones" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        for c, half, rnd, step in stones:
            kc.rounded_block(mb, c, half, stone, rot=kc.rot_y(float(np.sum(c)) * 1.7), radius=min(half) * rnd,
                             seg=1 if lod else (3 if step else 4), noise=None if lod else noise,
                             disp_m=0.05 * min(half) / 0.3, disp_period_m=0.35, weather=sc.SEAWORN,
                             variation=float((c[0] * 7.3) % 1.0))
        out.append(mb)
    col = kc.MeshBuilder("sea_stones-col")
    for c, half, _rnd, step in stones:
        if step:
            sc.box_proxy(col, c, half)
    del lay
    return out + [col]


def build_offering_shelf(seed: int = 513) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("offering_shelf", seed)
    noise = kc.Noise3(rng)
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("offering_shelf" + ("-lod1" if lod else ""))
        stone = mb.material(sc.M_STONE)
        seg = 1 if lod else 3
        # Ledge on two short legs, back slab against the wall (x = 0), the front facing +X.
        kc.rounded_block(mb, (0.25, 0.5, 0.0), (0.24, 0.06, 0.85), stone, radius=0.03, seg=seg,
                         noise=None if lod else noise, disp_m=0.006, weather=sc.TENDED, variation=0.3)
        for z in (-0.6, 0.6):
            kc.rounded_block(mb, (0.24, 0.22, z), (0.16, 0.22, 0.12), stone, radius=0.03, seg=seg, weather=sc.TENDED,
                             variation=float(rng.random()))
        kc.rounded_block(mb, (0.06, 0.82, 0.0), (0.06, 0.32, 0.8), stone, radius=0.03, seg=seg, weather=sc.TENDED,
                         variation=0.6)
        if not lod:
            import shrine  # noqa: PLC0415

            tmp = kc.MeshBuilder("shelf_fan")
            shrine.fan_shell(tmp, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 0.55, rng, noise, span_deg=150.0, ribs=9,
                             lift=0.12, droop_deg=0.0, weather=sc.TENDED)
            n = np.array([1.0, 0.0, 0.0])
            mb.merge(tmp, np.column_stack([kc.UP, n, np.cross(kc.UP, n)]), (0.13, 0.6, 0.0))
            sc.nacre_band(mb, np.linspace([0.495, 0.565, -0.8], [0.495, 0.565, 0.8], 6), (1.0, 0.0, 0.0), 0.03,
                          mb.material(sc.M_NACRE))
        out.append(mb)
    return out


def build_leaf_boat(seed: int = 514) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("leaf_boat", seed)
    length, beam, depth = 0.28, 0.09, 0.045
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("leaf_boat" + ("-lod1" if lod else ""))
        leaf = mb.material(sc.M_LEAF)
        nu, nv = (4, 3) if lod else (13, 7)
        grid = np.zeros((nv + 1, nu + 1, 3))
        for i in range(nv + 1):
            v = -1.0 + 2.0 * i / nv  # across: -1 port gunwale, 0 keel, +1 starboard
            for j in range(nu + 1):
                u = -1.0 + 2.0 * j / nu  # along: bow -1 .. stern +1
                taper = math.sqrt(max(0.0, 1.0 - u * u)) ** 0.8
                sheer = 0.012 * u * u  # the folded ends rise
                grid[i, j] = (u * length * 0.5, depth * (abs(v) ** 1.6) * (0.4 + 0.6 * taper) + sheer + 0.004,
                              v * beam * 0.5 * taper)
        col = sc.col4(0, 0, 0, 0)
        uv = np.stack([grid[..., 0] / length + 0.5, grid[..., 2] / beam + 0.5], axis=-1)
        # Rows run across (+Z), columns along (+X): X x Z = -Y, so the inside (up) needs the flip.
        kc.quad_strip(mb, grid, leaf, uv=uv, col=col, uv2=(1.0, float(rng.random())), flip=True)
        kc.quad_strip(mb, grid - np.array([0.0, 0.002, 0.0]), leaf, uv=uv, col=col, uv2=(0.8, 0.5), flip=False)
        if not lod:
            petal = mb.material(sc.M_FLOWER)
            throat = mb.material(sc.M_FLOWER_THROAT)
            c = np.array([0.01, depth * 0.55, 0.0])
            for k in range(5):
                a = 2 * math.pi * k / 5 + 0.3
                d = np.array([math.cos(a), 0.0, math.sin(a)])
                side = np.cross(kc.UP, d)
                pts = np.array([c, c + d * 0.02 + side * 0.012 + kc.UP * 0.006, c + d * 0.035 + kc.UP * 0.012,
                                c + d * 0.02 - side * 0.006 + kc.UP * 0.004])
                base = mb.add_vertices(pts, np.tile(kc.UP, (4, 1)), np.array([[0, 0], [1, 0], [1, 1], [0, 1]]),
                                       np.tile([1.0, 0.5], (4, 1)), np.zeros((4, 4)))
                mb.add_tri(base, base + 2, base + 1, petal)
                mb.add_tri(base, base + 3, base + 2, petal)
            kc.tube(mb, np.array([c - kc.UP * 0.004, c + kc.UP * 0.008]), 0.006, 5, throat, cap_end=True)
        out.append(mb)
    return out


TARGETS = {
    "chamber_door_valve": build_door,
    "net_float_charm": build_charm,
    "exterior_steps": build_exterior_steps,
    "sea_stones": build_sea_stones,
    "offering_shelf": build_offering_shelf,
    "leaf_boat": build_leaf_boat,
}
