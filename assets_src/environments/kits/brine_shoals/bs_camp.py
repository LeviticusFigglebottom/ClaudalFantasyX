"""The Saltwright salvage camp and the raid (brine_shoals.md §2). Pure numpy; see bs_common.py.

Every camp piece has an intact and a burned variant from the same seed: the burned one collapses part
of its structure, re-slots its timber and rope to bs_char / bs_scorch and its cloth to bs_canvas_scorched
by a seeded char field (bs_common.CharField, deepest at the fire's seat and low on the piece), burns
holes through the canvas, and lays an ember bed (bs_ember coals in bs_ash) at the seat.

  camp_tent(_burned)          3 x 4 m ridge tent of sail-cloth over crossed oars, ridge 2.1 m
  salvage_rack(_burned)       a 3.6 m lashed spar rack hung with rope coils, brass and net-floats
  crate_stack(_burned)        four rope-bound salvage crates
  salvage_pile(_burned)       hull plating, brass pipe, a Lit Age conduit shard, rope, on a grit mound
  brine_vat(_burned)          a 1.4 m coopered brine vat with a salt rime, and its evaporation pan
  branding_brazier            the Order's iron brazier with live coals and three branding irons
  liss_crate                  Liss's small iron-cornered crate, its seams leaking bound light
  smoke_plume                 a 14 m leaning smoke column for env_smoke_plume.gdshader (UV.y = height 0..1)
"""

from __future__ import annotations

import math

import numpy as np

import bs_common as bc
from bs_common import kc

TRI_BUDGET = {
    "camp_tent": (9000, 900),
    "salvage_rack": (9000, 900),
    "crate_stack": (6000, 600),
    "salvage_pile": (7000, 700),
    "brine_vat": (7000, 700),
    "branding_brazier": (3500, 350),
    "liss_crate": (2500, 250),
    "smoke_plume": (1200, 200),
}
BUDGET_KEY = {"camp_tent_burned": "camp_tent", "salvage_rack_burned": "salvage_rack",
              "crate_stack_burned": "crate_stack", "salvage_pile_burned": "salvage_pile",
              "brine_vat_burned": "brine_vat"}


def _rings(mb: kc.MeshBuilder, c, axis, r: float, rng, n: int = 2) -> None:
    """A rope lashing: n thin rings around a joint."""
    axis = kc.normalize(np.asarray(axis, float))
    c = np.asarray(c, float)
    for k in range(n):
        p = c + axis * (k - (n - 1) * 0.5) * 0.04
        kc.tube(mb, np.array([p - axis * 0.015, p + axis * 0.015]), r, 6, mb.material(bc.M_ROPE),
                variation=float(rng.random()))


def _spar(mb: kc.MeshBuilder, a, b, r: float, rng, noise, *, mat: str = bc.M_TIMBER, sides: int = 6) -> None:
    a, b = np.asarray(a, float), np.asarray(b, float)
    n = max(2, int(np.linalg.norm(b - a) / 0.5) + 1)
    kc.tube(mb, np.linspace(a, b, n), r, sides, mb.material(mat), weather=bc.CAMP, noise=noise, disp_m=r * 0.15,
            disp_period_m=0.3, variation=float(rng.random()), cap_start=True, cap_end=True, u_repeat=r * 6.3)


def _oar(mb: kc.MeshBuilder, grip, tip, rng, noise) -> None:
    """A salvaged oar used as a tent pole: shaft from `grip` to `tip`, the blade at the tip end."""
    grip, tip = np.asarray(grip, float), np.asarray(tip, float)
    axis = kc.normalize(tip - grip)
    neck = tip - axis * 0.7
    _spar(mb, grip, neck, 0.032, rng, noise)
    side = kc.normalize(np.cross(axis, kc.UP)) if abs(axis[1]) < 0.99 else np.array([1.0, 0.0, 0.0])
    rot = np.column_stack([side, axis, np.cross(side, axis)])
    kc.rounded_block(mb, neck + axis * 0.35, (0.075, 0.36, 0.012), mb.material(bc.M_TIMBER), rot=rot, radius=0.01,
                     seg=2, noise=noise, disp_m=0.004, weather=bc.CAMP, variation=float(rng.random()))


def _cloth(mb: kc.MeshBuilder, grid: np.ndarray, rng, slot: str = bc.M_CANVAS) -> None:
    """A double-sided cloth sheet from a (rows, cols, 3) grid."""
    rows, cols = grid.shape[:2]
    across = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(grid[0], axis=0), axis=1))])
    along = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(grid[:, 0], axis=0), axis=1))])
    uv = np.stack([np.broadcast_to(across[None, :], (rows, cols)), np.broadcast_to(along[:, None], (rows, cols))],
                  axis=-1)
    var = float(rng.random())
    # The hem is damp and dirtied where it lies near the ground (VC.B), salt dried into the upper cloth.
    y = grid[..., 1] - float(grid[..., 1].min())
    col = np.stack([np.zeros((rows, cols)), np.full((rows, cols), 0.25), 0.55 * (1.0 - kc.smoothstep(0.1, 0.55, y)),
                    np.full((rows, cols), 0.35)], axis=-1)
    kc.quad_strip(mb, grid, mb.material(slot), uv=uv, col=col, uv2=np.array([0.95, var]))
    kc.quad_strip(mb, grid, mb.material(slot), uv=uv, col=col, uv2=np.array([0.75, var]), flip=True)


def _stake_and_guy(mb: kc.MeshBuilder, top, ground, rng, noise) -> None:
    top, ground = np.asarray(top, float), np.asarray(ground, float)
    t = np.linspace(0, 1, 4)
    sag = np.array([0.0, -0.06, 0.0])
    pts = top[None] + (ground - top)[None] * t[:, None] + sag[None] * np.sin(t * math.pi)[:, None]
    kc.tube(mb, pts, 0.006, 3, mb.material(bc.M_ROPE), variation=float(rng.random()))
    _spar(mb, ground - np.array([0, 0.1, 0]), ground + np.array([0.02, 0.28, 0.0]), 0.025, rng, noise, sides=5)


# ---------------------------------------------------------------------------------------------
# Tent
# ---------------------------------------------------------------------------------------------
TENT_W, TENT_L, TENT_RIDGE = 3.0, 4.0, 2.1
TENT_SAG_M = 0.26  # the canvas between the frames (M3-ENV-1316, GPU QA row 5: the slopes read as one flat box)


def tent(name: str, seed: int, *, burned: bool, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for("camp_tent", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (bc.LOD if lod else ""))
    hw, hl = TENT_W * 0.5, TENT_L * 0.5
    zf, zr = hl - 0.2, -hl + 0.2  # front and rear A-frames

    # Ridge height along z: intact level; burned, the front frame has gone and the ridge lies on the ground.
    def ridge_y(z):
        if not burned:
            return np.full_like(np.asarray(z, float), TENT_RIDGE)
        t = np.clip((np.asarray(z, float) - zr) / (zf - zr), 0, 1)
        return TENT_RIDGE * (1.0 - t) + 0.22 * t

    if lod:
        for s in (-1.0, 1.0):
            zs = np.array([-hl, hl])
            grid = np.array([[[0.0, float(ridge_y(z)), z], [s * (hw + 0.05), 0.2, z]] for z in zs])
            _cloth(mb, grid, rng, bc.M_CANVAS_SCORCHED if burned else bc.M_CANVAS)
        return mb
    # A-frames of crossed oars (blades up past the ridge).
    for z, standing in ((zr, True), (zf, not burned)):
        for s in (-1.0, 1.0):
            foot = np.array([s * (hw - 0.05), -0.05, z])
            if standing:
                tip = np.array([-s * 0.45, TENT_RIDGE + 0.55, z])
            else:  # fallen outward, lying across the ground
                tip = np.array([s * (hw + 1.6), 0.08, z + s * 0.9 + 0.4])
            _oar(mb, foot, tip, rng, noise)
        if standing:
            _rings(mb, (0.0, TENT_RIDGE, z), (0, 0, 1), 0.06, rng)
    _spar(mb, (0.0, float(ridge_y(zr - 0.3)) + 0.04, zr - 0.3), (0.0, float(ridge_y(zf + 0.3)) + 0.04, zf + 0.3),
          0.045, rng, noise)
    # Canvas slopes with a sag between the frames, folds running down the slope, and a little billow.
    start = mb.triangle_count

    def canvas_pt(s: float, z: float, g: float, lift: float = 0.0) -> np.ndarray:
        ry = float(ridge_y(z))
        sag = TENT_SAG_M * math.sin(math.pi * (z - zr) / (zf - zr)) if zr <= z <= zf else 0.0
        x = s * (0.03 + (hw + 0.08) * g)
        y = ry + (0.18 - ry) * g
        inward = sag * math.sin(math.pi * min(g * 1.15, 1.0)) + 0.06 * math.sin(z * 5.5 + g * 2.0) * g
        bil = (noise.fbm(np.array([x * 2.5, y * 2.5, z * 2.5]), 2) - 0.5) * 0.1
        return np.array([x - s * inward * 0.5 + s * bil + s * lift, y - inward + bil + lift, z])

    # Burned canvas needs a finer grid, so its holes and scorch edges are ragged, not triangular.
    zs = np.linspace(-hl, hl, 15 if not burned else 31)
    gs = np.linspace(0.0, 1.0, 9 if not burned else 15)
    step = 2 if not burned else 4  # grid rows per sewn sail-cloth panel (about 0.55 m)
    for s in (-1.0, 1.0):
        grid = np.array([[canvas_pt(s, z, g) for g in gs] for z in zs])
        for k in range(0, len(zs) - 1, step):  # each panel its own UV2.y, so the material's value spread
            _cloth(mb, grid[k:k + step + 1], rng)  # reads the seams
        if not burned:  # the sewn seams themselves, a doubled hem standing off the cloth down each panel edge
            for k in range(step, len(zs) - 1, step):
                seam = np.array([canvas_pt(s, zs[k], g, 0.015) for g in gs])
                kc.tube(mb, seam, 0.012, 3, mb.material(bc.M_ROPE), variation=0.2)
    # The rear gable, closed; the front flaps tied back.
    rows = np.linspace(0.0, 1.0, 5 if not burned else 10)
    cols = np.linspace(-1.0, 1.0, 7 if not burned else 13)
    gable = np.zeros((len(rows), len(cols), 3))
    ry = float(ridge_y(-hl))
    for i, v in enumerate(rows):
        for j, u in enumerate(cols):
            y = ry * (1 - v) + 0.18 * v
            gable[i, j] = (u * (0.03 + (hw + 0.08) * v), y, -hl + 0.02 + 0.03 * v)
    _cloth(mb, gable, rng)
    if not burned:
        for s in (-1.0, 1.0):
            roll = np.array([[s * 0.6, 1.6, hl], [s * 1.05, 0.9, hl + 0.05], [s * 1.45, 0.25, hl + 0.02]])
            kc.tube(mb, roll, 0.07, 6, mb.material(bc.M_CANVAS), variation=float(rng.random()))
    # The Saltwright patch: a panel of faded teal sewn onto the west slope.
    patch = np.array([[canvas_pt(-1.0, z, g, 0.012) for g in np.linspace(0.3, 0.62, 3)]
                      for z in np.linspace(0.15, 1.15, 4)])
    _cloth(mb, patch, rng, bc.M_CANVAS_TEAL)
    # Guy lines to driftwood stakes.
    for z, sgn in ((zr, -1.0), (zf, 1.0)):
        if burned and sgn > 0:
            continue
        _stake_and_guy(mb, (0.0, TENT_RIDGE + 0.05, z), (0.25 * sgn, 0.0, z + sgn * 1.4), rng, noise)
    # Contents: a teal bedroll and a small crate.
    kc.tube(mb, np.array([[-0.95, 0.12, -0.6], [-0.05, 0.12, -0.55]]), 0.12, 8, mb.material(bc.M_CANVAS_TEAL),
            cap_start=True, cap_end=True)
    kc.rounded_block(mb, (0.7, 0.2, -1.1), (0.3, 0.2, 0.22), mb.material(bc.M_TIMBER), rot=kc.rot_y(0.2), radius=0.02,
                     seg=2, noise=noise, disp_m=0.005, weather=bc.CAMP, variation=float(rng.random()))
    if burned:
        field = bc.CharField((0.1, 0.0, 1.0), 4.2, rng, climb=0.25, breakup=0.14)
        bc.burn_holes(mb, field, 0.22, start_tri=start)
        bc.scorch_cloth(mb, field, (0.15, 0.22), start_tri=start)
        bc.apply_char(mb, field)
        bc.ember_bed(mb, (0.1, 0.0, 0.7), 0.95, 22, rng, noise)
        # Burned canvas fallen on the ground, its edges eaten.
        scrap_start = mb.triangle_count
        xs = np.linspace(0.3, 1.9, 14)
        zz = np.linspace(0.6, 2.2, 14)
        X, Z = np.meshgrid(xs, zz)
        grid = np.stack([X, 0.03 + 0.03 * np.sin(X * 4 + Z * 3), Z], axis=-1)
        _cloth(mb, grid, rng, bc.M_CANVAS_SCORCHED)
        scrap_field = bc.CharField((1.6, 0.0, 2.0), 1.6, rng)
        bc.burn_holes(mb, scrap_field, 0.6, start_tri=scrap_start)
        bc.scorch_cloth(mb, scrap_field, (0.48, 0.6), start_tri=scrap_start, cloth=(bc.M_CANVAS_SCORCHED,))
    return mb


def build_tent(burned: bool) -> list[kc.MeshBuilder]:
    name = "camp_tent_burned" if burned else "camp_tent"
    return [tent(name, 501, burned=burned, lod=False), tent(name, 501, burned=burned, lod=True)]


# ---------------------------------------------------------------------------------------------
# Salvage rack
# ---------------------------------------------------------------------------------------------
def _coil(mb: kc.MeshBuilder, hang, r: float, rng, *, lying: bool = False) -> None:
    hang = np.asarray(hang, float)
    a = np.linspace(0, 2 * math.pi, 13)
    for k in range(3):
        rr = r * (1.0 - 0.08 * k)
        if lying:
            pts = hang + np.stack([np.cos(a) * rr, np.full_like(a, 0.03 + 0.03 * k), np.sin(a) * rr], axis=-1)
        else:
            pts = hang + np.stack([np.sin(a) * rr * 0.9, -rr + np.cos(a) * rr, np.full_like(a, 0.025 * k)], axis=-1)
        kc.tube(mb, pts, 0.016, 4, mb.material(bc.M_ROPE), variation=float(rng.random()))


def _hanging(mb: kc.MeshBuilder, top, drop: float, item: str, rng) -> np.ndarray:
    top = np.asarray(top, float)
    bot = top - np.array([0.0, drop, 0.0])
    kc.tube(mb, np.array([top, bot]), 0.005, 3, mb.material(bc.M_ROPE))
    if item == "brass":
        kc.tube(mb, np.array([bot, bot - np.array([0.0, 0.22, 0.0])]), 0.045, 8, mb.material(bc.M_BRASS),
                cap_start=True, cap_end=True)
    elif item == "float":
        kc.rounded_block(mb, bot - np.array([0.0, 0.1, 0.0]), (0.1, 0.1, 0.1), mb.material(bc.M_GLASS), radius=0.099,
                         seg=4)
    return bot


def rack(name: str, seed: int, *, burned: bool, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for("salvage_rack", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (bc.LOD if lod else ""))
    hx, top_y, low_y = 1.5, 1.9, 0.95
    # Burned, the east trestle has gone and the bar's east end lies on the ground.
    east_top = np.array([hx + 0.3, top_y, 0.0]) if not burned else np.array([hx + 0.5, 0.12, 0.35])
    if lod:
        _spar(mb, (-hx - 0.3, top_y, 0.0), east_top, 0.05, rng, None, sides=4)
        for x in (-hx,) + ((hx,) if not burned else ()):
            for s in (-1.0, 1.0):
                _spar(mb, (x, 0.0, s * 0.55), (x, top_y + 0.1, 0.0), 0.04, rng, None, sides=4)
        return mb
    for x, standing in ((-hx, True), (hx, not burned)):
        for s in (-1.0, 1.0):
            foot = np.array([x + rng.normal(0, 0.03), -0.05, s * 0.55])
            head = np.array([x, top_y + 0.15, -s * 0.06])
            if not standing:  # splayed and down
                head = foot + np.array([0.9 * s, 0.25, 1.1 + 0.3 * s])
            _spar(mb, foot, head, 0.042, rng, noise)
        if standing:
            _rings(mb, (x, top_y, 0.0), (1, 0, 0), 0.06, rng)
    _spar(mb, (-hx - 0.3, top_y, 0.0), east_top, 0.05, rng, noise)
    low_east = np.array([hx + 0.1, low_y, 0.32]) if not burned else np.array([hx + 0.2, 0.08, 0.55])
    _spar(mb, (-hx - 0.1, low_y, 0.32), low_east, 0.035, rng, noise)
    # Hung salvage: rope coils, brass fittings, net-floats; Lit Age ceramic plates leaning on the low bar.
    items = ["coil", "brass", "float", "brass", "coil", "float", "brass", "float"]
    for k, item in enumerate(items):
        x = -hx + 0.25 + (2 * hx - 0.5) * k / (len(items) - 1)
        on_bar = (not burned) or x < 0.2
        if on_bar:
            t = (x + hx + 0.3) / (east_top[0] + hx + 0.3)
            top = np.array([x, top_y + (east_top[1] - top_y) * t - 0.04, east_top[2] * t])
            if item == "coil":
                _coil(mb, top, 0.2, rng)
            else:
                _hanging(mb, top, rng.uniform(0.25, 0.6), item, rng)
        else:  # fallen on the ground below
            g = np.array([x + rng.normal(0, 0.2), 0.0, rng.uniform(0.0, 0.9)])
            if item == "coil":
                _coil(mb, g, 0.2, rng, lying=True)
            elif item == "brass":
                kc.tube(mb, np.array([g + (0, 0.04, 0), g + (0.2, 0.04, 0.08)]), 0.045, 8, mb.material(bc.M_BRASS),
                        cap_start=True, cap_end=True)
            elif rng.random() < 0.5:
                kc.rounded_block(mb, g + (0, 0.1, 0), (0.1, 0.1, 0.1), mb.material(bc.M_GLASS), radius=0.099, seg=4)
            else:  # shattered: a few glass shards
                for _s in range(4):
                    p = g + np.array([rng.normal(0, 0.12), 0.01, rng.normal(0, 0.12)])
                    kc.rounded_block(mb, p, (0.03, 0.006, 0.02), mb.material(bc.M_GLASS), rot=kc.rot_y(rng.uniform(0, 3)),
                                     radius=0.004, seg=1)
    for k in range(3):
        x = -1.1 + 0.85 * k
        lean = math.radians(18 + rng.normal(0, 4))
        if burned and k == 2:
            # cracked in two and down
            for j, (dx, rz) in enumerate(((0.0, 0.1), (0.45, -0.25))):
                kc.rounded_block(mb, (x + dx, 0.03 + 0.01 * j, 0.9 + 0.1 * j), (0.22, 0.015, 0.3), mb.material(bc.M_CERAMIC),
                                 rot=kc.rot_y(rz), radius=0.01, seg=2, noise=noise, disp_m=0.01, weather=kc.DROWNED)
            continue
        c = np.array([x, 0.5, 0.32 + 0.16])
        kc.rounded_block(mb, c, (0.24, 0.5, 0.018), mb.material(bc.M_CERAMIC), rot=kc.rot_x(-lean), radius=0.012, seg=2,
                         noise=noise, disp_m=0.01, weather=kc.DROWNED, variation=float(rng.random()))
    if burned:
        field = bc.CharField((1.0, 0.0, 0.3), 2.4, rng, climb=0.5)
        bc.apply_char(mb, field)
        bc.ember_bed(mb, (1.2, 0.0, 0.5), 0.7, 14, rng, noise)
    return mb


def build_rack(burned: bool) -> list[kc.MeshBuilder]:
    name = "salvage_rack_burned" if burned else "salvage_rack"
    return [rack(name, 511, burned=burned, lod=False), rack(name, 511, burned=burned, lod=True)]


# ---------------------------------------------------------------------------------------------
# Crates
# ---------------------------------------------------------------------------------------------
def crate(mb: kc.MeshBuilder, center, half, yaw: float, rng, noise, *, lid: bool = True, missing=(), tilt=None,
          slot: str = bc.M_TIMBER) -> None:
    """A salvage crate of boards (three per side, horizontal) on four corner battens. `missing` lists
    (face, board) pairs to leave out; faces 0..3 are the sides (+X, -X, +Z, -Z), 4 the lid."""
    hx, hy, hz = half
    rot = kc.rot_y(yaw) if tilt is None else tilt
    center = np.asarray(center, float)
    tm = mb.material(slot)

    def P(p):
        return np.asarray(p, float) @ rot.T + center

    up = kc.UP @ rot.T
    t = 0.022
    for face, (n, u, span_u, span_n) in enumerate(((0, 2, hz, hx), (0, 2, hz, -hx), (2, 0, hx, hz), (2, 0, hx, -hz))):
        for k in range(3):
            if (face, k) in missing:
                continue
            y = -hy + hy * 2 * (k + 0.5) / 3
            a = np.zeros(3)
            b = np.zeros(3)
            a[n] = b[n] = span_n + np.sign(span_n) * t * 0.5
            a[u], b[u] = -span_u, span_u
            a[1] = b[1] = y
            bw = hy * 2 / 3 - 0.012
            normal = np.zeros(3)
            normal[n] = np.sign(span_n)
            kc.plank(mb, P(a), P(b), bw, t, tm, up=normal @ rot.T, weather=bc.CAMP, variation=float(rng.random()),
                     noise=noise)
    if lid:
        for k in range(3):
            if (4, k) in missing:
                continue
            x = -hx + hx * 2 * (k + 0.5) / 3
            kc.plank(mb, P((x, hy + t * 0.5, -hz - t)), P((x, hy + t * 0.5, hz + t)), hx * 2 / 3 - 0.012, t, tm,
                     up=up, weather=bc.CAMP, variation=float(rng.random()), noise=noise)
    for sx in (-1, 1):
        for sz in (-1, 1):
            c = P((sx * (hx + t * 0.6), 0.0, sz * (hz + t * 0.6)))
            kc.rounded_block(mb, c, (0.03, hy, 0.03), tm, rot=rot, radius=0.008, seg=1, weather=bc.CAMP,
                             variation=float(rng.random()))


def crate_stack(name: str, seed: int, *, burned: bool, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for("crate_stack", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (bc.LOD if lod else ""))
    specs = [  # center, half, yaw
        ((0.0, 0.35, 0.0), (0.5, 0.35, 0.3), 0.05),
        ((0.05, 0.98, 0.02), (0.4, 0.28, 0.25), 0.22),
        ((1.05, 0.25, 0.15), (0.3, 0.25, 0.22), -0.3),
        ((-0.9, 0.18, 0.35), (0.25, 0.18, 0.2), 0.7),
    ]
    if lod:
        for k, (c, h, y) in enumerate(specs):
            if burned and k == 1:
                c, y = (0.6, 0.25, 0.85), 1.2
            kc.rounded_block(mb, c, h, mb.material(bc.M_TIMBER), rot=kc.rot_y(y), radius=0.02, seg=1)
        return mb
    for k, (c, h, y) in enumerate(specs):
        if burned and k == 1:
            # Knocked off the stack: on its side on the ground, lid boards gone, contents spilled.
            tilt = kc.rot_y(1.2) @ kc.rot_z(math.pi * 0.5 - 0.08)
            crate(mb, (0.75, h[0] * 0.95, 0.9), h, 0.0, rng, noise, lid=False, missing=((0, 1), (2, 2)), tilt=tilt)
            for b in range(2):
                p0 = np.array([1.4 + 0.3 * b, 0.02, 0.4 + 0.25 * b])
                kc.plank(mb, p0, p0 + np.array([0.75, 0.0, 0.18 * (b - 0.5)]), 0.24, 0.022, mb.material(bc.M_TIMBER),
                         weather=bc.CAMP, variation=float(rng.random()), noise=noise)
            for _s in range(5):
                p = np.array([1.2 + rng.normal(0, 0.25), 0.04, 1.1 + rng.normal(0, 0.2)])
                kc.tube(mb, np.array([p, p + np.array([rng.normal(0, 0.1), 0.0, 0.12])]), 0.03, 6,
                        mb.material(bc.M_BRASS), cap_start=True, cap_end=True)
            continue
        missing = ((1, 0), (1, 1), (4, 2)) if (burned and k == 0) else ()
        crate(mb, c, h, y, rng, noise, missing=missing)
        if k == 0:  # rope binding
            for x in (-0.25, 0.25):
                loop = np.array([[x, -0.01, -0.33], [x, 0.71, -0.33], [x, 0.71, 0.33], [x, -0.01, 0.33]])
                loop = loop @ kc.rot_y(0.05).T
                kc.tube(mb, np.vstack([loop, loop[:1]]), 0.012, 4, mb.material(bc.M_ROPE))
    if burned:
        field = bc.CharField((-0.6, 0.0, 0.5), 1.7, rng, climb=0.8)
        bc.apply_char(mb, field, char_at=0.62, scorch_at=0.25)
    return mb


def build_crates(burned: bool) -> list[kc.MeshBuilder]:
    name = "crate_stack_burned" if burned else "crate_stack"
    return [crate_stack(name, 521, burned=burned, lod=False), crate_stack(name, 521, burned=burned, lod=True)]


# ---------------------------------------------------------------------------------------------
# Salvage pile
# ---------------------------------------------------------------------------------------------
def salvage_pile(name: str, seed: int, *, burned: bool, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for("salvage_pile", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (bc.LOD if lod else ""))
    R = 1.6
    n = 15 if not lod else 6
    xs = np.linspace(-R, R, n)

    def mound(X, Z):
        r = np.sqrt((X / R) ** 2 + (Z / (R * 0.75)) ** 2)
        return 0.35 * np.clip(1 - r ** 2, 0, 1) - 0.03

    bc.heightfield(mb, xs, xs * 0.8, mound, mb.material(bc.M_GRIT), keep=lambda X, Z: (X / R) ** 2 + (Z / (R * 0.78)) ** 2 < 1.05,
                   salt=lambda X, Z, Y: 0.3 + 0 * X, erosion=0.6, variation=0.3)
    if lod:
        kc.rounded_block(mb, (0.0, 0.35, 0.0), (1.1, 0.25, 0.7), mb.material(bc.M_TAR), radius=0.1, seg=1)
        return mb
    plate_slot = bc.M_SOOT if burned else bc.M_IRON
    for k in range(6):  # hull plating: tarred planks and riveted iron plates, leaning into the heap
        a = k * 2 * math.pi / 6 + rng.normal(0, 0.2)
        c = np.array([math.cos(a) * 0.65, 0.4, math.sin(a) * 0.45])
        rot = kc.rot_y(-a) @ kc.rot_z(math.radians(rng.uniform(25, 55)))
        slot = plate_slot if k % 2 else bc.M_TAR
        kc.rounded_block(mb, c, (0.55, 0.02, rng.uniform(0.25, 0.4)), mb.material(slot), rot=rot, radius=0.012, seg=3,
                         noise=noise, disp_m=0.03, disp_period_m=0.4, weather=bc.WRECK, variation=float(rng.random()))
    for k in range(4):  # brass pipe lengths
        a = rng.uniform(0, 2 * math.pi)
        p0 = np.array([math.cos(a) * 0.3, 0.45, math.sin(a) * 0.2])
        p1 = p0 + np.array([math.cos(a + 1.0) * 0.9, rng.uniform(-0.3, 0.05), math.sin(a + 1.0) * 0.6])
        kc.tube(mb, np.array([p0, p1]), rng.uniform(0.03, 0.05), 8, mb.material(bc.M_BRASS), cap_start=True,
                cap_end=True)
    # A Lit Age conduit shard (a quarter of a ring 1.2 m across), pale and greyed.
    ang = np.linspace(0.2, 1.7, 9)
    ring = np.stack([np.cos(ang) * 0.6 - 0.2, np.sin(ang) * 0.6 * 0.7 + 0.15, np.full_like(ang, -0.5)], axis=-1)
    kc.tube(mb, ring @ kc.rot_y(0.5).T, 0.13, 10, mb.material(bc.M_CERAMIC), weather=kc.DROWNED, noise=noise,
            disp_m=0.015, cap_start=True, cap_end=True, u_repeat=1.0)
    _coil(mb, (0.95, 0.12, 0.55), 0.28, rng, lying=True)
    _spar(mb, (-1.3, 0.05, 0.9), (0.2, 0.55, 0.1), 0.03, rng, noise)  # a broken oar shaft
    for k in range(3):  # loose planks
        p0 = np.array([rng.uniform(-1.2, 0.3), rng.uniform(0.1, 0.35), rng.uniform(-0.8, 0.6)])
        p1 = p0 + np.array([rng.uniform(0.8, 1.4), rng.uniform(-0.15, 0.25), rng.normal(0, 0.4)])
        kc.plank(mb, p0, p1, 0.22, 0.03, mb.material(bc.M_TIMBER), weather=bc.CAMP, variation=float(rng.random()),
                 noise=noise)
    if burned:
        field = bc.CharField((0.0, 0.2, 0.0), 2.2, rng, climb=0.3)
        bc.apply_char(mb, field, char_at=0.45)
        bc.ember_bed(mb, (0.1, 0.32, 0.05), 0.75, 26, rng, noise)
    return mb


def build_pile(burned: bool) -> list[kc.MeshBuilder]:
    name = "salvage_pile_burned" if burned else "salvage_pile"
    return [salvage_pile(name, 531, burned=burned, lod=False), salvage_pile(name, 531, burned=burned, lod=True)]


# ---------------------------------------------------------------------------------------------
# Brine vat and evaporation pan
# ---------------------------------------------------------------------------------------------
VAT_R, VAT_H, STAVES = 0.7, 1.0, 18


def _stave(mb: kc.MeshBuilder, a0: float, a1: float, rng, noise, *, sprung: float = 0.0, fallen=None) -> None:
    ys = np.linspace(0.0, VAT_H, 5)
    angs = np.linspace(a0, a1, 3)
    bulge = VAT_R * (1.0 + 0.07 * np.sin(math.pi * ys / VAT_H))
    grid = np.zeros((len(ys), len(angs), 3))
    for i, y in enumerate(ys):
        for j, a in enumerate(angs):
            grid[i, j] = (math.cos(a) * bulge[i], y, math.sin(a) * bulge[i])
    mid = 0.5 * (a0 + a1)
    out_dir = np.array([math.cos(mid), 0.0, math.sin(mid)])
    if sprung:  # leaning outward about its foot
        axis = np.cross(kc.UP, out_dir)
        c, s = math.cos(sprung), math.sin(sprung)
        foot = grid[0].mean(axis=0)
        rel = grid - foot
        rel = rel * c + np.cross(axis, rel) * s + np.outer(np.dot(rel.reshape(-1, 3), axis), axis).reshape(rel.shape) * (1 - c)
        grid = rel + foot
    if fallen is not None:  # lying on the ground at `fallen` (x, z, yaw)
        fx, fz, fyaw = fallen
        grid = grid - grid[0].mean(axis=0)
        grid = grid @ (kc.rot_y(fyaw) @ kc.rot_z(math.pi * 0.5)).T + np.array([fx, 0.06, fz])
        out_dir = kc.UP
    from bs_wrecks import shell_strip  # noqa: PLC0415 (shared with the wrecks)

    shell_strip(mb, grid, out_dir, mb.material(bc.M_TIMBER), thick=0.035, variation=float(rng.random()), noise=noise,
                weather=bc.CAMP)


def _hoop(mb: kc.MeshBuilder, y: float, r: float, *, center=(0.0, 0.0), tilt=None) -> None:
    a = np.linspace(0, 2 * math.pi, 25)
    pts = np.stack([np.cos(a) * r + center[0], np.full_like(a, y), np.sin(a) * r + center[1]], axis=-1)
    if tilt is not None:
        pts = (pts - np.array([center[0], y, center[1]])) @ tilt.T + np.array([center[0], y, center[1]])
    kc.tube(mb, pts, 0.012, 4, mb.material(bc.M_IRON), first_normal=(0.0, 1.0, 0.0))


def _salt_disc(mb: kc.MeshBuilder, center, r: float, y: float, rng, noise, *, slot: str = bc.M_SALT, rough: float = 0.025,
               n: int = 11, grey=None) -> None:
    center = np.asarray(center, float)
    xs = np.linspace(-r, r, n) + center[0]
    zs = np.linspace(-r, r, n) + center[2]

    def h(X, Z):
        return y + (noise.fbm(np.stack([X * 6, np.full_like(X, y), Z * 6], axis=-1), 2) - 0.5) * rough * 2

    start_t = mb.triangle_count
    bc.heightfield(mb, xs, zs, h, mb.material(slot), keep=lambda X, Z: (X - center[0]) ** 2 + (Z - center[2]) ** 2 < r * r,
                   salt=lambda X, Z, Y: 1.0 + 0 * X, erosion=0.2, variation=float(rng.random()))
    if grey is not None:  # ash greying part of a spill
        lv = grey.level(bc.tri_centroids(mb, start_t))
        m = mb.material(bc.M_ASH)
        for k, level in enumerate(lv):
            if level > 0.5:
                mb.tri_mat[start_t + k] = m


def brine_vat(name: str, seed: int, *, burned: bool, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for("brine_vat", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (bc.LOD if lod else ""))
    pan_c = np.array([1.45, 0.0, 0.2])
    if lod:
        kc.tube(mb, np.array([[0, 0, 0], [0, VAT_H * (0.55 if burned else 1.0), 0]]), VAT_R * 1.04, 8,
                mb.material(bc.M_CHAR if burned else bc.M_TIMBER), cap_end=True)
        kc.rounded_block(mb, pan_c + (0, 0.08, 0), (0.8, 0.08, 0.5), mb.material(bc.M_TIMBER), radius=0.01, seg=1)
        return mb
    da = 2 * math.pi / STAVES
    sprung_set = {2, 3, 4} if burned else set()
    fallen_set = {5, 6} if burned else set()
    for k in range(STAVES):
        a0 = k * da + 0.006
        a1 = (k + 1) * da - 0.006
        if k in fallen_set:
            _stave(mb, a0, a1, rng, noise, fallen=(math.cos(k * da) * 1.5, math.sin(k * da) * 1.5 + 0.3, k * 0.7))
        else:
            _stave(mb, a0, a1, rng, noise, sprung=math.radians(rng.uniform(18, 35)) if k in sprung_set else 0.0)
    hoop_ys = (0.12, 0.5, 0.88)
    for j, y in enumerate(hoop_ys):
        r = VAT_R * (1.0 + 0.07 * math.sin(math.pi * y / VAT_H)) + 0.03
        if burned and j == 2:  # the top hoop has dropped to the ground
            _hoop(mb, 0.02, r * 1.02, center=(0.35, -0.9), tilt=kc.rot_x(0.08))
            continue
        _hoop(mb, y, r)
    # The brine: a salt-rimed crust high in the vat (intact); low, greyed and spilled out (burned).
    if burned:
        _salt_disc(mb, (0.0, 0.0, 0.0), VAT_R * 0.95, 0.35, rng, noise)
        _salt_disc(mb, (math.cos(4 * da) * 1.1, 0.0, math.sin(4 * da) * 1.1), 0.75, 0.02, rng, noise, rough=0.015,
                   grey=bc.CharField((0.9, 0.0, 1.2), 1.2, rng))
    else:
        _salt_disc(mb, (0.0, 0.0, 0.0), VAT_R * 1.0, 0.86, rng, noise)
        for _k in range(16):  # salt rime crusted on the rim
            a = rng.uniform(0, 2 * math.pi)
            p = np.array([math.cos(a) * VAT_R * 1.0, VAT_H + 0.01, math.sin(a) * VAT_R * 1.0])
            s = rng.uniform(0.03, 0.07)
            kc.rounded_block(mb, p, (s, s * 0.5, s * 0.8), mb.material(bc.M_SALT), rot=kc.rot_y(a), radius=s * 0.4, seg=1)
    # Evaporation pan: a shallow board tray with a salt crust; a wooden rake across it.
    tm = mb.material(bc.M_TIMBER)
    hx, hz, ph = 0.8, 0.5, 0.16
    for (a, b, up) in (((-hx, ph * 0.5, -hz), (hx, ph * 0.5, -hz), (0, 0, -1)), ((-hx, ph * 0.5, hz), (hx, ph * 0.5, hz), (0, 0, 1)),
                       ((-hx, ph * 0.5, -hz), (-hx, ph * 0.5, hz), (-1, 0, 0)), ((hx, ph * 0.5, -hz), (hx, ph * 0.5, hz), (1, 0, 0))):
        kc.plank(mb, pan_c + a, pan_c + b, ph, 0.03, tm, up=np.array(up, float), weather=bc.CAMP,
                 variation=float(rng.random()), noise=noise)
    kc.rounded_block(mb, pan_c + (0, 0.02, 0), (hx, 0.02, hz), tm, radius=0.01, seg=1, weather=bc.CAMP)
    grey = bc.CharField(pan_c + (0.4, 0, 0.2), 1.0, rng) if burned else None
    _salt_disc(mb, pan_c + (0, 0, 0), min(hx, hz) * 0.98, 0.07, rng, noise, rough=0.012, n=9, grey=grey)
    _salt_disc(mb, pan_c + (hx * 0.45, 0, 0), min(hx, hz) * 0.98, 0.07, rng, noise, rough=0.012, n=9, grey=grey)
    _spar(mb, pan_c + (-0.9, 0.18, -0.6), pan_c + (0.6, 0.2, 0.4), 0.02, rng, noise)
    kc.rounded_block(mb, pan_c + (0.62, 0.15, 0.42), (0.03, 0.06, 0.2), tm, rot=kc.rot_y(-0.6), radius=0.01, seg=1)
    if burned:
        field = bc.CharField((0.6, 0.0, 0.6), 1.8, rng, climb=0.5)
        bc.apply_char(mb, field, char_at=0.5)
    return mb


def build_vat(burned: bool) -> list[kc.MeshBuilder]:
    name = "brine_vat_burned" if burned else "brine_vat"
    return [brine_vat(name, 541, burned=burned, lod=False), brine_vat(name, 541, burned=burned, lod=True)]


# ---------------------------------------------------------------------------------------------
# The Order's branding brazier, Liss's crate, smoke
# ---------------------------------------------------------------------------------------------
def build_brazier(seed: int = 551) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("branding_brazier", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("branding_brazier" + (bc.LOD if lod else ""))
        rim_y = 0.82
        ys = np.linspace(rim_y - 0.2, rim_y, 6 if not lod else 3)
        radii = 0.08 + 0.26 * ((ys - ys[0]) / (ys[-1] - ys[0])) ** 0.6
        kc.tube(mb, np.stack([np.zeros_like(ys), ys, np.zeros_like(ys)], axis=-1), radii, 16 if not lod else 8,
                mb.material(bc.M_IRON), cap_start=True)
        for k in range(3):
            a = k * 2 * math.pi / 3 + 0.3
            top = np.array([math.cos(a) * 0.3, rim_y - 0.05, math.sin(a) * 0.3])
            foot = np.array([math.cos(a) * 0.48, 0.0, math.sin(a) * 0.48])
            kc.tube(mb, np.array([top, (top + foot) * 0.5 + np.array([0, 0.02, 0]), foot]), 0.016, 5 if not lod else 3,
                    mb.material(bc.M_IRON), cap_end=True)
        # Coal bed: dark lumps and live coals heaped in the bowl.
        if lod:
            kc.rounded_block(mb, (0, rim_y - 0.02, 0), (0.28, 0.05, 0.28), mb.material(bc.M_EMBER), radius=0.04, seg=1)
            out.append(mb)
            continue
        for k in range(30):
            a, r = rng.uniform(0, 2 * math.pi), 0.27 * math.sqrt(rng.random())
            p = np.array([math.cos(a) * r, rim_y - 0.03 + 0.05 * (1 - r / 0.27), math.sin(a) * r])
            s = rng.uniform(0.03, 0.055)
            slot = bc.M_EMBER if rng.random() < 0.55 else bc.M_CHAR
            kc.rounded_block(mb, p, (s, s * 0.7, s * 0.85), mb.material(slot), rot=kc.rot_y(rng.uniform(0, 3)),
                             radius=s * 0.4, seg=1, variation=float(rng.random()))
        # Three branding irons, heads in the coals, grips bound in deep lacquer-red cord.
        for k in range(3):
            a = k * 2 * math.pi / 3 + 1.2
            head = np.array([math.cos(a) * 0.1, rim_y + 0.0, math.sin(a) * 0.1])
            grip = head + np.array([math.cos(a) * 0.75, 0.32, math.sin(a) * 0.75])
            kc.tube(mb, np.array([head, grip]), 0.011, 5, mb.material(bc.M_IRON), cap_end=True)
            d = kc.normalize(grip - head)
            kc.tube(mb, np.array([grip - d * 0.2, grip]), 0.02, 6, mb.material(bc.M_RED), cap_start=True, cap_end=True)
            side = kc.normalize(np.cross(d, kc.UP))
            rot = np.column_stack([side, kc.normalize(np.cross(side, d)), d])
            kc.rounded_block(mb, head, (0.045, 0.008, 0.03), mb.material(bc.M_IRON_HOT), rot=rot, radius=0.004, seg=1)
        out.append(mb)
    return out


def build_liss_crate(seed: int = 561) -> list[kc.MeshBuilder]:
    out = []
    half = (0.3, 0.2, 0.2)
    for lod in (False, True):
        rng = kc.rng_for("liss_crate", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("liss_crate" + (bc.LOD if lod else ""))
        c = np.array([0.0, half[1] + 0.02, 0.0])
        if lod:
            kc.rounded_block(mb, c, half, mb.material(bc.M_TIMBER), radius=0.02, seg=1)
            out.append(mb)
            continue
        # The bound light inside, seen only through the board seams (steady glimmer_bound).
        kc.rounded_block(mb, c, (half[0] - 0.012, half[1] - 0.012, half[2] - 0.012), mb.material(bc.M_LEAK),
                         radius=0.01, seg=1)
        crate(mb, c, half, 0.0, rng, noise)
        for sx in (-1, 1):  # iron corner brackets
            for sy in (-1, 1):
                for sz in (-1, 1):
                    p = c + np.array([sx * (half[0] + 0.02), sy * (half[1] - 0.04), sz * (half[2] + 0.02)])
                    kc.rounded_block(mb, p, (0.035, 0.035, 0.035), mb.material(bc.M_IRON), radius=0.006, seg=1)
        for sx in (-1, 1):  # rope handles
            a = np.linspace(0, math.pi, 7)
            pts = c + np.stack([np.full_like(a, sx * (half[0] + 0.035)), 0.05 + np.sin(a) * 0.05, np.cos(a) * 0.08], axis=-1)
            kc.tube(mb, pts, 0.008, 4, mb.material(bc.M_ROPE))
        out.append(mb)
    return out


PLUME_H = 14.0


def build_smoke_plume(seed: int = 571) -> list[kc.MeshBuilder]:
    """Leans toward +X (the dresser yaws it downwind). UV.y runs 0 at the base to 1 at the top; UV.x
    around; UV2.y a per-plume variation the shader uses as a noise offset."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("smoke_plume", seed)
        mb = kc.MeshBuilder("smoke_plume" + (bc.LOD if lod else ""))
        n = 14 if not lod else 6
        t = np.linspace(0.0, 1.0, n)
        # Bent well over by the breeze: the column rises, then lies downwind (+X) as it cools.
        spine = np.stack([9.0 * t ** 1.5 + 0.4 * np.sin(t * 5.0), PLUME_H * t * (1.0 - 0.15 * t),
                          0.8 * np.sin(t * 3.0 + 1.0)], axis=-1)
        radii = 0.45 + 3.6 * t ** 0.9
        for k, (scale, var, off) in enumerate(((1.0, 0.2, 0.0), (0.68, 0.55, 0.35), (0.42, 0.85, -0.3))):
            if lod and k:
                break
            shell = spine + np.array([off, 0.0, -off]) * t[:, None]
            length = float(np.sum(np.linalg.norm(np.diff(shell, axis=0), axis=1)))  # UV.y 0..1 on every shell
            kc.tube(mb, shell, radii * scale, 12 if not lod else 6, mb.material(bc.M_SMOKE), v_scale=1.0 / length,
                    variation=var, u_repeat=1.0)
        out.append(mb)
    return out


TARGETS = {
    "camp_tent": lambda: build_tent(False),
    "camp_tent_burned": lambda: build_tent(True),
    "salvage_rack": lambda: build_rack(False),
    "salvage_rack_burned": lambda: build_rack(True),
    "crate_stack": lambda: build_crates(False),
    "crate_stack_burned": lambda: build_crates(True),
    "salvage_pile": lambda: build_pile(False),
    "salvage_pile_burned": lambda: build_pile(True),
    "brine_vat": lambda: build_vat(False),
    "brine_vat_burned": lambda: build_vat(True),
    "branding_brazier": build_brazier,
    "liss_crate": build_liss_crate,
    "smoke_plume": build_smoke_plume,
}
