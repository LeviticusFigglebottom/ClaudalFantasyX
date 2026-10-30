"""The Saltgrass Causeway zone (vertical_slice.md B06, haluna.md §2; M2-ENV-10). Pure numpy; see kit_common.py.

  causeway_flats   the low-tide flats the causeway crosses: ~400 x 320 m of sand and mud between Haluna's
                   causeway head (the zone origin) and the Shell Shrine's islet (north-east). Heights are
                   relative to the tide datum: the flats sit just above low water (-0.7 m), meandering
                   channels and tidepools dip below it so the zone's sea plane fills them, saltgrass banks
                   rise above -0.2 m, and the causeway's bed runs along the path as a low ridge. Vertex
                   colours are env_ground's masks (R lane, G turf, B seagrass, A reef rubble), not the
                   weathering channels.

    python3 assets_src/environments/kits/haluna/causeway_zone.py --layout \\
        assets/environments/zones/saltgrass_causeway/causeway_layout.json

writes the zone's layout (HalunaDresser format, every piece with an explicit height, plus `instances`: the
saltgrass scatter as baked transforms, and `path` / `anchors` for m2-slice's rails and triggers). The same
height function places everything, so the layout and the terrain agree without a runtime height query.

Coordinates are the zone's: metres, +X east, -Z north, the origin at the causeway head on the tide datum.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kit_common as kc  # noqa: E402

M_GROUND = "kit_causeway_ground"
SEED = 1006
LOW_WATER_M = -0.7  # haluna.md §0: the causeway is exposed at low water
RECT = (-60.0, -270.0, 400.0, 330.0)  # x0, z0, width (x), depth (z)
CELL_M = (2.0, 6.0)  # LOD0, LOD1 grid
TRI_BUDGET = {"causeway_flats": (90000, 12000)}

# The path: control points from the causeway head to the islet's steps (~285 m), a slow S so the line leads
# away (C01, C06). Densified at 1 m for the bed, the slabs and m2-slice's rail.
PATH_CTRL = np.array([[0.0, 0.0], [28.0, -14.0], [62.0, -40.0], [96.0, -58.0], [128.0, -86.0], [158.0, -118.0],
                      [190.0, -134.0], [216.0, -158.0], [236.0, -184.0]])
DISC_AT_M = 205.0  # the Drownbell's widened disc (B10), along the path
DISC_R_M = 15.1  # the causeway_disc kit piece's paving radius (arenas.py, M2-ENV-11)
DISC_WALL_R_M = 15.85  # its foundation wall; the ground drops under it to the wall foot
DISC_FOOT_M = -1.55
ISLET = (262.0, -212.0, 26.0)  # x, z, radius: the Shell Shrine's tidal islet
BED_HALF_W_M = 4.5
SALTGRASS_ABOVE_M = -0.2  # haluna.md §2.3: saltgrass covers 70 % of the ground above -0.2 m


def _catmull(ctrl: np.ndarray, step_m: float) -> np.ndarray:
    pts = []
    p = np.vstack([ctrl[0] * 2 - ctrl[1], ctrl, ctrl[-1] * 2 - ctrl[-2]])
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        n = max(2, int(np.linalg.norm(p2 - p1) / step_m))
        for t in np.linspace(0.0, 1.0, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    pts.append(ctrl[-1])
    return np.asarray(pts)


PATH = _catmull(PATH_CTRL, 1.0)
PATH_S = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(PATH, axis=0), axis=1))])


def point_at(s: float) -> tuple[np.ndarray, np.ndarray]:
    """Path position and unit tangent at arc length s."""
    s = float(np.clip(s, 0.0, PATH_S[-1]))
    i = int(np.clip(np.searchsorted(PATH_S, s) - 1, 0, len(PATH) - 2))
    f = (s - PATH_S[i]) / max(PATH_S[i + 1] - PATH_S[i], 1e-9)
    p = PATH[i] + (PATH[i + 1] - PATH[i]) * f
    t = PATH[i + 1] - PATH[i]
    return p, t / max(np.linalg.norm(t), 1e-9)


def path_distance(x: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Distance from each (x, z) to the path polyline (vectorised, chunked)."""
    q = np.stack([np.asarray(x, float), np.asarray(z, float)], axis=-1)
    flat = q.reshape(-1, 2)
    best = np.full(len(flat), 1e9)
    a, b = PATH[:-1], PATH[1:]
    ab = b - a
    ab2 = np.maximum((ab * ab).sum(1), 1e-9)
    for k in range(0, len(flat), 4096):
        c = flat[k:k + 4096]
        t = np.clip(((c[:, None, :] - a[None]) * ab[None]).sum(-1) / ab2[None], 0.0, 1.0)
        d = np.linalg.norm(c[:, None, :] - (a[None] + ab[None] * t[..., None]), axis=-1)
        best[k:k + 4096] = d.min(1)
    return best.reshape(q.shape[:-1])


class Field:
    """The zone's height and masks: one deterministic function shared by the mesh and the layout."""

    def __init__(self, seed: int = SEED):
        self.rng = kc.rng_for("causeway_flats", seed)
        self.noise = kc.Noise3(self.rng)
        disc_p, _t = point_at(DISC_AT_M)
        self.disc = disc_p
        # Tidepools beside the path for C03 and the banter (arc length, side, radius).
        self.pools = [(66.0, -1.0, 3.2), (71.0, 1.0, 2.2), (118.0, -1.0, 2.6), (150.0, 1.0, 3.6), (174.0, -1.0, 2.0)]
        self.pool_xy = []
        for s, side, r in self.pools:
            p, t = point_at(s)
            n = np.array([t[1], -t[0]]) * side
            self.pool_xy.append((p + n * (BED_HALF_W_M + 6.5 + r * 1.4), r))  # clear of the bed's ridge

    def _n(self, x, z, scale: float, octaves: int = 3, off: float = 0.0):
        p = np.stack([np.asarray(x) / scale + off, np.asarray(z) / scale - off, np.full(np.shape(x), off)], axis=-1)
        return self.noise.fbm(p, octaves)

    def height(self, x, z):
        x = np.asarray(x, float)
        z = np.asarray(z, float)
        d = path_distance(x, z)
        # Ripple-and-runnel mud: broad swells plus metre-scale hollows that dip under low water, so
        # the flats glint with standing puddles (the brief's "tidepools flashing").
        flats = (-0.6 + 0.2 * (self._n(x, z, 60.0, 3) - 0.5) + 0.05 * (self._n(x, z, 7.0, 2, 3.1) - 0.5)
                 - 0.22 * kc.smoothstep(0.58, 0.72, self._n(x, z, 4.5, 2, 6.2)))
        # Meandering channels crossing the flats (they fill from the sea and carry seagrass).
        w = self._n(x, z, 90.0, 2, 7.7)
        ch = np.abs(np.sin(x / 31.0 + z / 47.0 + w * 5.0))
        chan = (1.0 - kc.smoothstep(0.0, 0.3, ch)) * 0.8
        # Saltgrass banks: broad hummocks that rise above the grass line, densest near the path.
        bank = kc.smoothstep(0.42, 0.62, self._n(x, z, 22.0, 3, 1.9)) * 0.75
        bank = bank * (0.55 + 0.45 * (1.0 - kc.smoothstep(10.0, 70.0, d)))
        h = flats - chan + bank
        for (pxy, r) in self.pool_xy:
            dp = np.hypot(x - pxy[0], z - pxy[1])
            h = np.minimum(h, np.where(dp < r * 1.4, -0.95 + 0.35 * (dp / (r * 1.4)) ** 2, 9.0))
        # The causeway's bed: a low ridge under the slabs, never cut by a channel.
        bed = -0.05 - 0.15 * kc.smoothstep(BED_HALF_W_M, BED_HALF_W_M + 6.0, d)
        h = np.where(d < BED_HALF_W_M + 6.0, np.maximum(h, bed), h)
        # The Drownbell's disc is the causeway_disc kit piece on the tide datum (haluna.md §2.2): the ground runs
        # under its foundation wall at the wall foot and comes up to a low apron of sand against the wall face.
        dd = np.hypot(x - self.disc[0], z - self.disc[1])
        apron = np.minimum(np.maximum(h, -0.35), -0.15)
        h = np.where(dd < DISC_WALL_R_M, DISC_FOOT_M - 0.05,
                     np.where(dd < DISC_WALL_R_M + 3.0, apron, h))
        # The islet rises out of the flats to the shrine's podium height.
        di = np.hypot(x - ISLET[0], z - ISLET[1])
        isl = -1.2 + 2.0 * (1.0 - kc.smoothstep(ISLET[2] * 0.4, ISLET[2], di)) + 0.15 * (self._n(x, z, 6.0, 2, 4.4) - 0.5)
        h = np.maximum(h, isl)  # below the flats away from the islet, so it only lifts the islet itself
        # Out to sea at the zone's edges.
        x0, z0, wx, wz = RECT
        edge = np.minimum.reduce([x - x0, x0 + wx - x, z - z0, z0 + wz - z])
        h = h - 2.5 * (1.0 - kc.smoothstep(0.0, 40.0, edge))
        return h

    def masks(self, x, z, h):
        d = path_distance(x, z)
        lane = 1.0 - kc.smoothstep(BED_HALF_W_M - 1.5, BED_HALF_W_M + 1.0, d)
        turf = kc.smoothstep(SALTGRASS_ABOVE_M - 0.08, SALTGRASS_ABOVE_M + 0.12, h) * (1.0 - lane)
        sea = 1.0 - kc.smoothstep(LOW_WATER_M - 0.3, LOW_WATER_M + 0.05, h)
        # A green-brown algae film mottles the wet mud just above the water (env_ground's seagrass channel).
        film = (1.0 - kc.smoothstep(LOW_WATER_M, LOW_WATER_M + 0.25, h)) * kc.smoothstep(0.45, 0.7, self._n(x, z, 3.0, 2, 2.2))
        sea = np.maximum(sea, 0.55 * film)
        rubble = kc.smoothstep(0.6, 0.8, self._n(x, z, 9.0, 2, 5.5)) * (1.0 - turf) * 0.8
        rubble = np.maximum(rubble, (1.0 - kc.smoothstep(BED_HALF_W_M, BED_HALF_W_M + 3.0, d)) * 0.35)
        return np.stack([lane, turf, sea, rubble], axis=-1)


def build_flats(seed: int = SEED) -> list[kc.MeshBuilder]:
    field = Field(seed)
    x0, z0, wx, wz = RECT
    out = []
    for lod, cell in enumerate(CELL_M):
        nx, nz = int(wx / cell) + 1, int(wz / cell) + 1
        xs = np.linspace(x0, x0 + wx, nx)
        zs = np.linspace(z0, z0 + wz, nz)
        X, Z = np.meshgrid(xs, zs)
        H = field.height(X, Z)
        grid = np.stack([X, H, Z], axis=-1)
        col = field.masks(X, Z, H)
        uv = np.stack([X, Z], axis=-1)
        mb = kc.MeshBuilder("causeway_flats" + ("-lod1" if lod else ""))
        uv2 = np.stack([np.ones_like(H), np.full(H.shape, 0.5)], axis=-1)
        kc.quad_strip(mb, grid, mb.material(M_GROUND), uv=uv, col=col, uv2=uv2, flip=True)
        out.append(mb)
    return out


TARGETS = {"causeway_flats": build_flats}


# ---------------------------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------------------------
def _yaw_deg(t: np.ndarray) -> float:
    """Yaw for a piece whose local -Z should run along the 2D direction t (x, z)."""
    return math.degrees(math.atan2(-t[0], -t[1]))


def _walk_y(field: Field, x: float, z: float) -> float:
    """The walked surface: the disc's paving top (y 0) inside its rim, else the ground."""
    if math.hypot(x - field.disc[0], z - field.disc[1]) < DISC_R_M:
        return 0.0
    return float(field.height(np.array(x), np.array(z)))


def build_layout(seed: int = SEED) -> dict:
    field = Field(seed)
    rng = kc.rng_for("causeway_layout", seed)
    pieces = []

    def put(piece: str, x: float, z: float, yaw: float, dy: float = 0.0, **kw) -> bool:
        if math.hypot(x - field.disc[0], z - field.disc[1]) < DISC_WALL_R_M + 1.5:
            return False  # nothing set down on the Drownbell's disc but the disc itself
        y = float(field.height(np.array(x), np.array(z))) + dy
        e = {"piece": piece, "at": [round(float(x), 2), round(float(z), 2)], "y": round(y, 3),
             "yaw_deg": round(float(yaw), 1)}
        e.update(kw)
        pieces.append(e)
        return True

    total = float(PATH_S[-1])
    # The head: slab steps up off Haluna's beach onto the bed.
    p, t = point_at(1.5)
    put("causeway_slab_steps", p[0], p[1], _yaw_deg(t), -0.12)
    # The slab path, 2.6 m pitch, wandering a little; broken and sunk slabs where the bed has given way.
    s = 4.0
    k = 0
    while s < total - 3.0:
        p, t = point_at(s)
        if np.hypot(p[0] - field.disc[0], p[1] - field.disc[1]) > DISC_R_M - 1.0:
            n = np.array([t[1], -t[0]])
            wob = math.sin(s * 0.11) * 0.35 + float(rng.normal(0, 0.08))
            q = p + n * wob
            broken = (k % 7 == 3) or float(rng.random()) < 0.08
            piece = "causeway_slab_broken" if broken else "causeway_slab_flat"
            sunk = -0.12 if float(rng.random()) < 0.15 else 0.0
            put(piece, q[0], q[1], _yaw_deg(t) + float(rng.uniform(-5, 5)), 0.02 + sunk,
                tilt_deg=[round(float(rng.normal(0, 1.2)), 2), round(float(rng.normal(0, 1.2)), 2)])
        s += 2.6
        k += 1
    # Pilgrim marker posts every 20 m, alternating sides; the third is the broken one in C04's foreground.
    posts = []
    for i, s in enumerate(np.arange(12.0, total - 8.0, 20.0)):
        p, t = point_at(float(s))
        side = 1.0 if i % 2 == 0 else -1.0
        n = np.array([t[1], -t[0]]) * side
        q = p + n * (BED_HALF_W_M - 1.6)
        piece = "pilgrim_marker_post_broken" if i == 2 else ("pilgrim_marker_post_leaning" if i % 4 == 1
                                                               else "pilgrim_marker_post")
        if put(piece, q[0], q[1], _yaw_deg(t) + 90.0 + float(rng.uniform(-10, 10))):
            posts.append([round(float(q[0]), 2), round(float(q[1]), 2)])
    # Coral heads: a few beside the path, more out on the flats and in the channels.
    for i in range(46):
        if i < 14:
            s = float(rng.uniform(8.0, total - 10.0))
            p, t = point_at(s)
            n = np.array([t[1], -t[0]]) * (1.0 if rng.random() < 0.5 else -1.0)
            q = p + n * float(rng.uniform(BED_HALF_W_M + 1.0, BED_HALF_W_M + 9.0))
        else:
            x0, z0, wx, wz = RECT
            q = np.array([x0 + 40 + rng.random() * (wx - 80), z0 + 40 + rng.random() * (wz - 80)])
            if float(path_distance(q[0], q[1])) < BED_HALF_W_M + 2.0:
                continue
        name = ("coral_boulder_a", "coral_boulder_b", "coral_boulder_c")[int(rng.integers(0, 3))]
        put(name, q[0], q[1], float(rng.uniform(0, 360)), -0.15, scale=round(float(rng.uniform(0.8, 1.3)), 2))
    # The Lit Age ring (C05), half buried 9 m off the path at 132 m, its crack toward the path.
    p, t = point_at(132.0)
    n = np.array([t[1], -t[0]])
    ring = p + n * 9.0
    put("lit_age_ring", ring[0], ring[1], _yaw_deg(t) + 80.0, -0.25)
    # A wreck rib out on the flats, and the far shrine on its islet (C01's vista).
    put("wreck_rib", 84.0, -12.0, 140.0, -0.15)
    put("shell_shrine_massing", ISLET[0], ISLET[1], 25.0, 0.0)
    # The Drownbell's disc sits on its own datum (paving top y 0), not on the ground it hollows out.
    pieces.append({"piece": "causeway_disc", "at": [round(float(field.disc[0]), 2), round(float(field.disc[1]), 2)],
                   "y": 0.0, "yaw_deg": 0.0, "on_datum": True})
    # Saltgrass: 70 % cover above the grass line, patchy, never on the bed or the disc.
    x0, z0, wx, wz = RECT
    srng = kc.rng_for("causeway_saltgrass", seed)
    cand = srng.random((60000, 2)) * np.array([wx, wz]) + np.array([x0, z0])
    hc = field.height(cand[:, 0], cand[:, 1])
    dc = path_distance(cand[:, 0], cand[:, 1])
    patch = field._n(cand[:, 0], cand[:, 1], 14.0, 2, 8.8)
    dd = np.hypot(cand[:, 0] - field.disc[0], cand[:, 1] - field.disc[1])
    ok = (hc > SALTGRASS_ABOVE_M) & (dc > BED_HALF_W_M - 0.5) & (patch > 0.3) & (dd > DISC_R_M + 1.0)
    pts = cand[ok][:12000]
    # Clumps grow with the patch: thin and small at a patch's edge, full in its heart (the audit, 2026-10-29: one even
    # size read as a tiled field from the bed).
    grow = np.clip((patch[ok][:12000] - 0.3) / 0.35, 0.0, 1.0)
    grass = {"a": [], "b": []}
    for (gx, gz), gh, g in zip(pts, field.height(pts[:, 0], pts[:, 1]), grow):
        key = "a" if srng.random() < 0.6 else "b"
        size = float(srng.uniform(0.75, 1.3)) * (0.55 + 0.6 * float(g))
        grass[key].append([round(float(gx), 2), round(float(gh), 3), round(float(gz), 2),
                           round(float(srng.uniform(0, 360)), 1), round(size, 2)])
    veg = "res://assets/environments/vegetation/"
    instances = [{"name": f"Saltgrass_{k.upper()}", "glb": veg + "saltgrass_clumps.glb", "mesh_node": f"saltgrass_{k}",
                  "material": veg + "materials/saltgrass.tres", "visibility_end_m": 220.0, "xforms": v}
                 for k, v in grass.items()]
    instances += _dress(field, seed, put, posts)
    tide_pools = [[round(float(c[0]), 2), round(float(c[1]), 2), r] for c, r in field.pool_xy]
    return {
        "schema": "hymn-zone-layout/1",
        "zone": "ch03/saltgrass_causeway (B06; generated by assets_src/environments/kits/haluna/causeway_zone.py)",
        "seed": seed,
        "kit_dir": "res://assets/environments/kits/haluna/",
        "materials_dir": "res://assets/environments/kits/haluna/materials/",
        "lod1_from_m": 75.0, "lod_end_m": 2500.0, "lod_margin_m": 2.0,
        "prop_lods": PROP_LODS,
        "pieces": [{"piece": "causeway_flats", "at": [0.0, 0.0], "y": 0.0, "yaw_deg": 0.0, "lod1_from_m": 160.0}]
        + pieces,
        "instances": instances,
        "path": [[round(float(a), 2), round(_walk_y(field, a, b) + 0.32, 3), round(float(b), 2)] for a, b in PATH[::4]],
        "anchors": {
            "head": [0.0, 0.0], "islet_steps": [round(float(PATH[-1][0]), 2), round(float(PATH[-1][1]), 2)],
            "marker_posts": posts, "broken_post": posts[2], "tide_pools": tide_pools,
            "lit_age_ring": [round(float(ring[0]), 2), round(float(ring[1]), 2)],
            "drownbell_disc": [round(float(field.disc[0]), 2), round(float(field.disc[1]), 2), DISC_R_M],
            "low_water_m": LOW_WATER_M,
        },
    }


# ---- M3-ENV-701: set dressing (the human's playtest: "parts look primitive") ----------------------------
# Pilgrims' offerings at the marker posts, the tide's wrack and lost gear out on the flats, and shells and
# pebbles along the bed's edges. A separate rng, so the M2-ENV-10 placements above are unchanged.
PROP_LODS = {"offering_step": [22.0, 90.0], "tide_debris": [30.0, 140.0], "net_heap": [30.0, 120.0],
             "rope_coil": [18.0, 55.0], "crate_stack": [30.0, 120.0]}
LITTER = "res://assets/environments/kits/haluna/village_litter.glb"
LITTER_MATS = {"shell_scatter": "kit_nacre", "pebble_cluster": "kit_coral_stone"}


def _dress(field: Field, seed: int, put, posts: list) -> list[dict]:
    rng = kc.rng_for("causeway_dressing", seed)
    total = float(PATH_S[-1])
    # Offerings at every second marker post, a metre in from the post, facing the path (not the broken one in
    # C04's foreground).
    for i, (px, pz) in enumerate(posts):
        if i % 2 or i == 2:
            continue
        s = float(PATH_S[int(np.argmin(np.hypot(PATH[:, 0] - px, PATH[:, 1] - pz)))])
        p, _t = point_at(s)
        n = np.array([px - p[0], pz - p[1]])
        n = n / max(float(np.linalg.norm(n)), 1e-6)
        q = np.array([px, pz]) - n * 1.0
        put("offering_step", q[0], q[1], math.degrees(math.atan2(-n[0], -n[1])), -0.05)
    # The wrack: driftwood and kelp left along the flats either side of the bed, lost nets and coils, and a
    # broken crate stack near the wreck rib.
    for _ in range(16):
        s = float(rng.uniform(10.0, total - 12.0))
        p, t = point_at(s)
        n = np.array([t[1], -t[0]]) * (1.0 if rng.random() < 0.5 else -1.0)
        q = p + n * float(rng.uniform(BED_HALF_W_M + 1.5, BED_HALF_W_M + 14.0))
        put("tide_debris", q[0], q[1], float(rng.uniform(0, 360)), -0.06)
    for _ in range(4):
        s = float(rng.uniform(20.0, total - 20.0))
        p, t = point_at(s)
        n = np.array([t[1], -t[0]]) * (1.0 if rng.random() < 0.5 else -1.0)
        q = p + n * float(rng.uniform(BED_HALF_W_M + 2.0, BED_HALF_W_M + 10.0))
        put("net_heap", q[0], q[1], float(rng.uniform(0, 360)), -0.12)
        r = q + rng.normal(0, 1.2, 2)
        put("rope_coil", r[0], r[1], float(rng.uniform(0, 360)), -0.03)
    put("crate_stack", 87.5, -9.0, 25.0, -0.25, tilt_deg=[6.0, -9.0])
    put("tide_debris", 80.5, -15.5, 210.0, -0.06)
    # Shells and pebbles along the bed's edges (baked instances, as the saltgrass).
    out = []
    for node, count in (("shell_scatter", 700), ("pebble_cluster", 450)):
        lrng = kc.rng_for("causeway_litter_" + node, seed)
        rows = []
        tries = 0
        while len(rows) < count and tries < count * 6:
            tries += 1
            s = float(lrng.uniform(2.0, total - 2.0))
            p, t = point_at(s)
            n = np.array([t[1], -t[0]]) * (1.0 if lrng.random() < 0.5 else -1.0)
            q = p + n * float(lrng.uniform(BED_HALF_W_M - 0.4, BED_HALF_W_M + 6.0))
            if math.hypot(q[0] - field.disc[0], q[1] - field.disc[1]) < DISC_WALL_R_M + 1.0:
                continue
            h = float(field.height(np.array(q[0]), np.array(q[1])))
            rows.append([round(float(q[0]), 2), round(h, 3), round(float(q[1]), 2),
                         round(float(lrng.uniform(0, 360)), 1), round(float(lrng.uniform(0.8, 1.4)), 2)])
        out.append({"name": "Litter_" + node, "glb": LITTER, "mesh_node": node,
                    "material": f"res://assets/environments/kits/haluna/materials/{LITTER_MATS[node]}.tres",
                    "visibility_end_m": 50.0, "xforms": rows})
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--layout", required=True, help="write the zone layout JSON here")
    args = ap.parse_args(argv)
    lay = build_layout()
    out = Path(args.layout)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(lay, indent=1) + "\n", encoding="utf-8")
    n_grass = sum(len(i["xforms"]) for i in lay["instances"] if i["name"].startswith("Saltgrass"))
    print(f"CAUSEWAY layout: {len(lay['pieces'])} pieces, {n_grass} saltgrass, path {PATH_S[-1]:.0f} m -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
