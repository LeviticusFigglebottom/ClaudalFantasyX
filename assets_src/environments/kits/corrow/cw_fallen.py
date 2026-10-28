"""After the wall fell (M3-ENV-04B; corrow.md §1.4 and §7): the broken Watchers, the broken stair and
Liss's hoist cut down. Pure numpy; see cw_common.py. Each piece goes where the piece it replaces stood,
with the same transform, so a swap needs no new placement maths.

  watcher_head_b        a second carving of the parapet head (cw_common.CARVING_B: an older, heavier face,
                        lower lids, a broader nose, three long crown waves): same frame, footprint and
                        budget as watcher_head, so a zone can mix the two hands along the row.
  watcher_head_fallen   a head down on its side in the rubble, its face (the second carving) turned up and
                        still humming; the neck sheared on a ragged slant (cw_laterite_broken), a corner of
                        its crown knocked off. Origin on the ground under its centre; it lies along local
                        +-X, the face toward +Z and up; sunk 0.3 m into the rubble with blocks against it.
  watcher_head_cracked  a head of the row (the first carving) still on the parapet but leaning out of the
                        line toward the sea, pivoted on its front bed-joint (12 deg, with 11 deg of roll and 6 of yaw),
                        a crack running down through its face from the crown, a crown corner gone. Origin and
                        frame as watcher_head: swap one for the other in place.
  fisher_stair_broken   the Fisher Stair after the fall, in fisher_stair's frame: the first 12 steps of the
                        lower flight still stand against the wall that held, broken off raw at the gap's west
                        joint (stair x 4.08, +3.4 m); the landing and the middle of the stair went with the
                        wall, and the upper flight's top 15 steps hang from the head landing, swung down
                        24 deg, broken off raw at their lower end; under the head landing the side wall
                        keeps only its upper courses; the hand-line hangs slack in a deep bight across the
                        gap between the two.
  liss_hoist_cut        Liss's hoist after the Stillguard cut it down (act outline Ch8, last beat), in the head's
                        frame like liss_hoist: the spar down on the walk, the cut ends of the head-rope
                        hanging from the two strap-plates still bolted into the head, the guys cut at their
                        ring-bolts, the block and its cut fall lying with the spar, the empty iron shoe.
"""

from __future__ import annotations

import math

import numpy as np

import cw_common as cw
import cw_stair
import cw_watchers as cwh
from cw_common import kc

TRI_BUDGET = {"watcher_head": (10500, 500), "watcher_head_broken": (11000, 600), "fisher_stair_broken": (12000, 900),
              "liss_hoist_cut": (3000, 300)}
BUDGET_KEY = {"watcher_head_b": "watcher_head", "watcher_head_fallen": "watcher_head_broken",
              "watcher_head_cracked": "watcher_head_broken"}

LEAN_DEG = 12.0  # the cracked head's lean out of the line, toward the sea
BROKEN_SWEEP = math.pi + 0.52  # the back's arc that exactly closes the front's (see cw_watchers.head)
BREAK_W = kc.Weathering(moss=0.0, salt=0.1, wet=0.4, erosion=0.3, noise_scale_m=0.5)


# ---------------------------------------------------------------------------------------------
# The broken heads
# ---------------------------------------------------------------------------------------------
def _neck_shear(a):
    """The fallen head's sheared neck: a ragged slant round the base (height by squircle angle)."""
    a = np.asarray(a, float)
    # A smooth slant (a ragged line here would skew the rows column by column and saw through the carving;
    # the raggedness is the fracture cap's).
    return np.clip(0.34 + 0.24 * np.cos(a) + 0.08 * np.sin(a) + 0.02 * np.sin(3.0 * a + 1.0), 0.02, 0.8)


def _rings(mb: kc.MeshBuilder, lod: bool) -> np.ndarray:
    """Indices of the bottom ring of a head built by cw_watchers.head (front row 0, then the back's row 0
    without its two seam columns), in order round the base."""
    rows = 10 if lod else 61
    nf, nb = (9, 9) if lod else (43, 21)
    front = list(range(nf))
    back = [rows * nf + c for c in range(1, nb - 1)]
    return np.asarray(front + back)


def _base_cap(mb: kc.MeshBuilder, ring_idx: np.ndarray, mat: int, noise: kc.Noise3 | None, *, depth: float,
              col) -> None:
    """Closes a head's base: a ragged fracture (depth > 0 dishes it into the stone) or a flat bed (0)."""
    ring = np.asarray(mb.pos, float)[ring_idx]
    c = ring.mean(axis=0)
    mid = c + (ring - c) * 0.55
    if noise is not None:
        mid[:, 1] += (noise.fbm(mid / 0.25, 2) - 0.5) * depth * 2.5 + depth * 0.5
    centre = c + np.array([0.0, depth, 0.0])
    n = len(ring)
    pts = np.vstack([ring, mid, centre[None]])
    base = mb.add_vertices(pts, np.tile(-kc.UP, (len(pts), 1)), pts[:, [0, 2]], np.tile([0.55, 0.5], (len(pts), 1)),
                           np.tile(col, (len(pts), 1)))

    def tri(a, b, cc):
        pa, pb, pc = pts[a - base], pts[b - base], pts[cc - base]
        if np.cross(pb - pa, pc - pa)[1] <= 0.0:
            mb.add_tri(a, b, cc, mat)
        else:
            mb.add_tri(a, cc, b, mat)

    for k in range(n):
        k1 = (k + 1) % n
        tri(base + k, base + k1, base + n + k1)
        tri(base + k, base + n + k1, base + n + k)
        tri(base + n + k, base + n + k1, base + 2 * n)


def _chip_crown(mb: kc.MeshBuilder, start_v: int, start_t: int, mat_broken: int, *, sx: float) -> None:
    """Knocks a corner off the crown (on the sx side): vertices past a slanted plane are pressed onto it
    and the faces left on the plane take the raw break."""
    p = np.asarray(mb.pos[start_v:], float)
    plane = 2.05 + (0.75 - sx * p[:, 0]) * 1.2 - 0.12 * (p[:, 2] < 0.0)
    cut = p[:, 1] > plane
    p[cut, 1] = plane[cut]
    mb.pos[start_v:] = p.tolist()
    tris = np.asarray(mb.tris[start_t:], dtype=np.int64) - start_v
    cut_full = np.nonzero(cut[tris].all(axis=1))[0]
    for k in cut_full:
        mb.tri_mat[start_t + k] = mat_broken


def _crack(mb: kc.MeshBuilder, start_v: int, pts2: np.ndarray, *, depth: float = 0.032, width: float = 0.03,
           shift: float = 0.012) -> None:
    """A crack through the stone along a polyline in the head's (x, y): a groove along each vertex's normal,
    the stone on one side of it standing a little proud (it has moved)."""
    p = np.asarray(mb.pos[start_v:], float)
    n = np.asarray(mb.nrm[start_v:], float)
    xy = p[:, :2]
    best = np.full(len(p), np.inf)
    side = np.zeros(len(p))
    for a, b in zip(pts2[:-1], pts2[1:]):
        ab = b - a
        t = np.clip(((xy - a) @ ab) / float(ab @ ab), 0.0, 1.0)
        q = a + t[:, None] * ab
        d = np.linalg.norm(xy - q, axis=1)
        closer = d < best
        best = np.where(closer, d, best)
        cr = ab[0] * (xy[:, 1] - a[1]) - ab[1] * (xy[:, 0] - a[0])
        side = np.where(closer, np.sign(cr), side)
    groove = -depth * np.exp(-(best / width) ** 2)
    proud = shift * (side > 0) * kc.smoothstep(0.0, 0.04, best)
    p = p + n * (groove + proud)[:, None]
    mb.pos[start_v:] = p.tolist()
    col = np.asarray(mb.col[start_v:], float)
    col[:, 2] = np.clip(col[:, 2] + 0.5 * np.exp(-(best / (width * 2.0)) ** 2), 0, 1)  # damp in the crack
    mb.col[start_v:] = col.tolist()
    uv2 = np.asarray(mb.uv2[start_v:], float)
    uv2[:, 0] = np.clip(uv2[:, 0] - 0.5 * np.exp(-(best / width) ** 2), 0.25, 1.0)
    mb.uv2[start_v:] = uv2.tolist()


def _xform(mb: kc.MeshBuilder, start_v: int, rot: np.ndarray, pivot, offset) -> None:
    p = np.asarray(mb.pos[start_v:], float)
    n = np.asarray(mb.nrm[start_v:], float)
    pivot = np.asarray(pivot, float)
    mb.pos[start_v:] = ((p - pivot) @ rot.T + pivot + np.asarray(offset, float)).tolist()
    mb.nrm[start_v:] = kc.normalize(n @ rot.T).tolist()


def build_head_b(seed: int = 823) -> list[kc.MeshBuilder]:
    return [cwh.head("watcher_head_b", seed, lod=lod, carving=cw.CARVING_B) for lod in (False, True)]


def fallen_head(name: str, seed: int, *, lod: bool) -> kc.MeshBuilder:
    mb = cwh.head(name, seed, lod=lod, carving=cw.CARVING_B, base=_neck_shear, back_sweep=BROKEN_SWEEP)
    noise = kc.Noise3(kc.rng_for(name + "_break", seed))
    i_broken = mb.material(cw.M_BROKEN)
    ring = _rings(mb, lod)
    n_head_tris = mb.triangle_count
    _chip_crown(mb, 0, 0, i_broken, sx=1.0)
    _base_cap(mb, ring, i_broken, None if lod else noise, depth=0.12, col=[0.0, 0.05, 0.3, 0.3])
    kc.recompute_normals(mb, 0, 0)
    del n_head_tris
    # Down on its side: the head's up along -X, its face turned 43 deg toward the sky, sunk into the rubble.
    rot = kc.rot_x(-0.75) @ kc.rot_z(math.pi * 0.5 + 0.1)
    _xform(mb, 0, rot, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    p = np.asarray(mb.pos, float)
    lo, hi = p.min(axis=0), p.max(axis=0)
    mid = (lo + hi) * 0.5
    _xform(mb, 0, np.eye(3), (0.0, 0.0, 0.0), (-mid[0], -lo[1] - 0.3, -mid[2]))
    # The rubble it lies in: blocks against its cheek and under its crown.
    rng = kc.rng_for(name + "_rubble", seed)
    i_lat = mb.material(cw.M_LATERITE)
    for k, (x, z) in enumerate(((-1.6, -0.9), (1.5, -0.8), (0.3, -1.25), (-0.9, 0.95), (1.2, 0.9))):
        size = np.array([1.1, 0.45, 0.7]) * rng.uniform(0.7, 1.1, 3)
        rot_b = kc.rot_y(rng.uniform(0.0, math.pi)) @ kc.rot_x(rng.uniform(-0.5, 0.5)) @ kc.rot_z(rng.uniform(-0.5, 0.5))
        kc.rounded_block(mb, (x, size[1] * 0.2 - 0.05, z), size * 0.5, i_broken if k % 2 else i_lat, rot=rot_b,
                         radius=0.05, seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.03, disp_period_m=0.5,
                         weather=BREAK_W, variation=float(rng.random()), wet_bias=0.2)
    return mb


def cracked_head(name: str, seed: int, *, lod: bool) -> kc.MeshBuilder:
    flat = lambda a: np.zeros_like(np.asarray(a, float))  # noqa: E731  (the bed joint, flat)
    mb = cwh.head(name, seed, lod=lod, carving=cw.CARVING_A, base=flat, back_sweep=BROKEN_SWEEP)
    noise = kc.Noise3(kc.rng_for(name + "_break", seed))
    i_broken = mb.material(cw.M_BROKEN)
    i_lat = mb.material(cw.M_LATERITE)
    ring = _rings(mb, lod)
    _chip_crown(mb, 0, 0, i_broken, sx=-1.0)
    kc.recompute_normals(mb, 0, 0)
    if not lod:
        _crack(mb, 0, np.array([[0.42, 2.5], [0.2, 2.0], [0.05, 1.55], [-0.3, 1.15], [-0.55, 0.7], [-0.98, 0.35]]))
        kc.recompute_normals(mb, 0, 0)
    _base_cap(mb, ring, i_lat, None, depth=0.0, col=[0.0, 0.2, 0.3, 0.5])
    # Leaning out of the line: pivoted on its front bed-joint toward the sea, with a little roll and yaw.
    front = float(np.asarray(mb.pos, float)[:, 2].max())
    rot = kc.rot_y(0.1) @ kc.rot_z(-0.2) @ kc.rot_x(math.radians(LEAN_DEG))
    _xform(mb, 0, rot, (0.0, 0.0, cwh.HEAD_FRONT * 0.9), (0.0, 0.0, 0.0))
    del front, noise
    return mb


def build_fallen(seed: int = 824) -> list[kc.MeshBuilder]:
    return [fallen_head("watcher_head_fallen", seed, lod=lod) for lod in (False, True)]


def build_cracked(seed: int = 825) -> list[kc.MeshBuilder]:
    return [cracked_head("watcher_head_cracked", seed, lod=lod) for lod in (False, True)]


# ---------------------------------------------------------------------------------------------
# The broken stair
# ---------------------------------------------------------------------------------------------
BREAK_X = 12 * cw_stair.GOING_M  # the flight broke after its 12th step, at the gap's west joint (s -36 in the preview)
HANG_FROM = 14  # flight-2 steps from this one up still hang from the head landing
HANG_DEG = 24.0
HEAD_UNDERCUT_Y = 8.2  # the side wall under the head landing survives down to about here


def _pivot_rot(deg: float) -> np.ndarray:
    return kc.rot_z(math.radians(deg))


def stair_broken(name: str, seed: int, *, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
    i_step, i_wall, i_iron, i_rope, i_broken = (mb.material(cw.M_CARVED), mb.material(cw.M_LATERITE),
                                                mb.material(cw.M_IRON), mb.material(cw.M_ROPE),
                                                mb.material(cw.M_BROKEN))
    steps, land, head = cw_stair.layout_steps()
    n1 = cw_stair.FLIGHT1[0] - 1
    flight1, flight2 = steps[:n1], steps[n1:]
    W, BURY, zf = cw_stair.WIDTH_M, cw_stair.BURY_M, cw_stair.z_face
    r2 = cw_stair.FLIGHT2[1]

    def tread(x0, x1, top, riser, depth=None):
        zi = float(zf(top)) + BURY
        cw_stair._tread(mb, x0, x1, top, riser, i_step, rng, noise, lod=lod, z_in=zi, z_out=zi - BURY - W, depth=depth)

    # 1. The lower flight's first steps, standing against the wall that held, broken off at the gap's
    # west joint: a raw face down to the lane.
    kept = [st for st in flight1 if st[1] <= BREAK_X + 1e-6]
    top_kept = kept[-1][2]
    if lod:
        zi_a, zi_b = float(zf(cw.TOWN_Y)) + BURY, float(zf(top_kept)) + BURY
        P = np.array([[[0.0, cw.TOWN_Y, zi_a], [0.0, cw.TOWN_Y, zi_a - BURY - W]],
                      [[BREAK_X, top_kept, zi_b], [BREAK_X, top_kept, zi_b - BURY - W]]])
        cw.grid_surface(mb, P, i_step, outward=kc.UP, uv=P[..., [0, 2]], col=np.tile([0, 0.2, 0.2, 0.6], (2, 2, 1)),
                        uv2=np.tile([0.9, 0.5], (2, 2, 1)), smooth=False)
    else:
        for x0, x1, top, riser in kept:
            tread(x0, x1, top, riser)
    zi = float(zf(top_kept)) + BURY
    zs = np.linspace(zi, zi - BURY - W - 0.03, 3 if lod else 9)
    jag = BREAK_X + (0.0 if lod else 1.0) * (0.12 * np.sin(zs * 4.1) + 0.08 * np.sin(zs * 9.3 + 0.7))
    ys = np.array([cw.TOWN_Y - 0.3, top_kept - 0.02])
    E = np.stack([np.stack([jag + (0.0 if lod else 0.25) * (k == 0), np.full_like(zs, y), zs], -1)
                  for k, y in enumerate(ys)])
    cw.grid_surface(mb, E, i_broken, outward=np.array([1.0, 0.0, 0.0]), uv=E[..., [2, 1]],
                    col=np.tile([0.0, 0.05, 0.3, 0.3], E.shape[:2] + (1,)), uv2=np.tile([0.7, 0.5], E.shape[:2] + (1,)),
                    smooth=False)
    # 2. The upper flight's top steps, hanging from the head landing, broken off raw at their lower end.
    start_v, start_t = mb.vertex_count, mb.triangle_count
    hang = flight2[HANG_FROM:]
    if lod:
        xa, xb = hang[0][0], head[0]
        ya, yb = hang[0][2] - hang[0][3], cw_stair.HEAD_Y
        zia, zib = float(zf(ya)) + BURY, float(zf(yb)) + BURY
        P = np.array([[[xa, ya, zia], [xa, ya, zia - BURY - W]], [[xb, yb, zib], [xb, yb, zib - BURY - W]]])
        cw.grid_surface(mb, P, i_step, outward=kc.UP, uv=P[..., [0, 2]], col=np.tile([0, 0.2, 0.2, 0.6], (2, 2, 1)),
                        uv2=np.tile([0.9, 0.5], (2, 2, 1)), smooth=False)
    else:
        for x0, x1, top, riser in hang:
            tread(x0, x1, top, riser)
    # Its soffit (the flight's underside, seen from the lanes now) and the raw end where it broke.
    x_low = hang[0][0]
    y_low = hang[0][2] - hang[0][3] - 0.55
    y_high = cw_stair.HEAD_Y - 0.9
    za, zb = float(zf(y_low)) + BURY, float(zf(y_low)) - W
    S = np.array([[[x_low, y_low, za], [x_low, y_low, zb]], [[head[0], y_high, za], [head[0], y_high, zb]]])
    cw.grid_surface(mb, S, i_wall, outward=-kc.UP, uv=S[..., [0, 2]], col=np.tile([0.0, 0.1, 0.35, 0.5], (2, 2, 1)),
                    uv2=np.tile([0.45, 0.5], (2, 2, 1)), smooth=False)
    zs = np.linspace(za, zb, 3 if lod else 9)
    jag = (0.0 if lod else 1.0) * (0.1 * np.sin(zs * 5.3) + 0.06 * np.sin(zs * 11.0 + 2.0))
    top_low = hang[0][2]
    E = np.stack([np.stack([x_low + jag, np.full_like(zs, y_low), zs], -1),
                  np.stack([x_low + jag * 0.5, np.full_like(zs, top_low - 0.01), zs], -1)])
    cw.grid_surface(mb, E, i_broken, outward=np.array([-1.0, 0.0, 0.0]), uv=E[..., [2, 1]],
                    col=np.tile([0.0, 0.05, 0.3, 0.3], E.shape[:2] + (1,)), uv2=np.tile([0.6, 0.5], E.shape[:2] + (1,)),
                    smooth=False)
    # The hanging part's stanchions (bent with it).
    hang_tops = []
    for xk in np.arange(x_low + 0.4, head[0], cw_stair.STANCHION_PITCH_M):
        y0 = float(cw_stair._tread_top(xk, steps, land, head))
        zk = float(zf(y0)) - W + 0.12
        base_p = np.array([xk, y0 - 0.05, zk])
        tip = base_p + np.array([0.0, cw_stair.STANCHION_H + 0.05, 0.0])
        hang_tops.append(tip - np.array([0.0, 0.04, 0.0]))
        kc.tube(mb, np.array([base_p, tip]), 0.03 if lod else 0.022, 3 if lod else 6, i_iron, cap_end=True,
                weather=cw.IRON_W)
    pivot = np.array([head[0], cw_stair.HEAD_Y - r2, 0.0])
    rot = _pivot_rot(HANG_DEG)
    _xform(mb, start_v, rot, pivot, (0.0, 0.0, 0.0))
    hang_tops = [(t - pivot) @ rot.T + pivot for t in hang_tops]
    del start_t
    # 3. The head landing, its two steps down onto the walk, and the side wall under it, torn below.
    zi_h = float(zf(cw_stair.HEAD_Y)) + BURY
    cw_stair._tread(mb, head[0], head[1], cw_stair.HEAD_Y, r2, i_step, rng, noise, lod=lod, z_in=zi_h,
                    z_out=zi_h - BURY - W, depth=0.3)
    kz0, kz1, _kh = cw.KERB
    G = np.stack(np.meshgrid(np.linspace(head[0], head[1], 2 if lod else 4), np.linspace(kz1, zi_h, 2 if lod else 3),
                             indexing="ij"), -1)
    G = np.stack([G[..., 0], np.full(G.shape[:2], cw_stair.HEAD_Y), G[..., 1]], -1)
    cw.grid_surface(mb, G, i_step, outward=kc.UP, uv=G[..., [0, 2]], col=np.tile([0, 0.2, 0.3, 0.6], G.shape[:2] + (1,)),
                    uv2=np.tile([0.95, 0.4], G.shape[:2] + (1,)))
    drop = (cw_stair.HEAD_Y - cw.WALK_Y) / 2.0
    for k in range(2):
        za_, zb_ = kz1 + k * 0.36, kz1 + (k + 1) * 0.36
        y = cw_stair.HEAD_Y - (k + 1) * drop
        if k == 0:
            T = np.stack(np.meshgrid(np.linspace(head[0], head[1], 2 if lod else 4), [za_, zb_], indexing="ij"), -1)
            Tt = np.stack([T[..., 0], np.full(T.shape[:2], y), T[..., 1]], -1)
            cw.grid_surface(mb, Tt, i_step, outward=kc.UP, uv=Tt[..., [0, 2]],
                            col=np.tile([0, 0.2, 0.3, 0.7], Tt.shape[:2] + (1,)), uv2=np.tile([0.9, 0.3], Tt.shape[:2] + (1,)))
        R = np.stack(np.meshgrid(np.linspace(head[0], head[1], 2 if lod else 4), [y, y + drop], indexing="ij"), -1)
        Rt = np.stack([R[..., 0], R[..., 1], np.full(R.shape[:2], za_)], -1)
        cw.grid_surface(mb, Rt, i_step, outward=np.array([0, 0, 1.0]), uv=Rt[..., [0, 1]],
                        col=np.tile([0, 0.2, 0.2, 0.7], Rt.shape[:2] + (1,)), uv2=np.tile([0.8, 0.3], Rt.shape[:2] + (1,)))
    # 4. The battered side wall: whole under the steps that stand, its top stepping down where it broke;
    # under the head landing only its upper courses, ragged underneath.
    offs = kc.rng_for(name + "_courses", seed).uniform(-1.0, 1.0, 64)
    ci = math.cos(math.radians(cw.INNER_BATTER_DEG))
    si = math.sin(math.radians(cw.INNER_BATTER_DEG))

    def side_wall(xs, y_bottom, y_top_fn):
        ys = np.arange(cw.TOWN_Y - 0.4, cw_stair.HEAD_Y + 0.01, 1.0 if lod else cw.COURSE_M)
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        top = y_top_fn(xs)
        bot = y_bottom(xs)
        Yc = np.clip(Y, bot[:, None], top[:, None])
        Yc[:, -1] = top
        Yc[:, 0] = bot
        disp = np.zeros_like(Yc) if lod else cw.course_profile(Yc, offs, groove_m=0.018) * (Yc < top[:, None] - 0.01)
        P = np.stack([X, Yc + disp * si, zf(Yc) - W - 0.03 - disp * ci], -1)
        breakup = noise.fbm(P / 1.6, 2)
        col = np.stack([np.clip((1.0 - kc.smoothstep(cw.TOWN_Y, cw.TOWN_Y + 2.0, Yc)) * (breakup - 0.2), 0, 1),
                        np.full_like(Yc, 0.15),
                        np.clip((1.0 - kc.smoothstep(cw.TOWN_Y, cw.TOWN_Y + 0.8, Yc)) * 0.6, 0, 1),
                        np.clip(0.4 + 0.5 * breakup, 0, 1)], -1)
        ao = np.clip(0.65 + 0.35 * kc.smoothstep(cw.TOWN_Y - 0.4, cw.TOWN_Y + 1.5, Yc), 0.3, 1.0)
        cw.grid_surface(mb, P, i_wall, outward=np.array([0.0, 0.1, -1.0]), uv=np.stack([X, Yc], -1), col=col,
                        uv2=np.stack([ao, np.full_like(Yc, 0.5)], -1))

    xs1 = np.linspace(0.0, BREAK_X, 5 if lod else 17)
    full_top = lambda xs: cw_stair._side_line(xs, steps, land, head)  # noqa: E731

    def broken_top(xs):
        t = full_top(xs)
        # The last two metres step down in whole courses toward the break.
        fall = np.floor(kc.smoothstep(BREAK_X - 1.6, BREAK_X, xs) * 4.0) * cw.COURSE_M
        return np.maximum(t - fall, cw.TOWN_Y + 0.3)

    side_wall(xs1, lambda xs: np.full_like(xs, cw.TOWN_Y - 0.4), broken_top)
    xs2 = np.linspace(head[0], head[1], 3 if lod else 9)
    rag = lambda xs: HEAD_UNDERCUT_Y + (0.0 if lod else 1.0) * np.floor(np.abs(np.sin(xs * 2.3)) * 3.0) * cw.COURSE_M  # noqa: E731
    side_wall(xs2, rag, lambda xs: np.full_like(xs, cw_stair.HEAD_Y - 0.2))
    # The head landing's underside, open now over the undercut: a rough bed at the side wall's ragged foot.
    zb_in, zb_out = float(zf(HEAD_UNDERCUT_Y)) + BURY, float(zf(HEAD_UNDERCUT_Y)) - W - 0.03
    B = np.array([[[head[0], HEAD_UNDERCUT_Y, zb_in], [head[0], HEAD_UNDERCUT_Y, zb_out]],
                  [[head[1], HEAD_UNDERCUT_Y, zb_in], [head[1], HEAD_UNDERCUT_Y, zb_out]]])
    cw.grid_surface(mb, B, i_broken, outward=-kc.UP, uv=B[..., [0, 2]], col=np.tile([0.0, 0.05, 0.4, 0.3], (2, 2, 1)),
                    uv2=np.tile([0.35, 0.5], (2, 2, 1)), smooth=False)
    # The hanging part's west end face, between its soffit and the head landing's bed.
    # 5. The hand-line: the standing stanchions, the line slack across the gap to the hanging part's, on up
    # to the head landing.
    tops = []
    for xk in np.arange(0.3, BREAK_X - 0.3, cw_stair.STANCHION_PITCH_M):
        y0 = float(cw_stair._tread_top(xk, steps, land, head))
        zk = float(zf(y0)) - W + 0.12
        base_p = np.array([xk, y0 - 0.05, zk])
        tip = base_p + np.array([0.0, cw_stair.STANCHION_H + 0.05, 0.0])
        tops.append(tip - np.array([0.0, 0.04, 0.0]))
        kc.tube(mb, np.array([base_p, tip]), 0.03 if lod else 0.022, 3 if lod else 6, i_iron, cap_end=True,
                weather=cw.IRON_W)
        if not lod:
            kc.tube(mb, np.array([tip - [0.0, 0.0, 0.05], tip + [0.0, 0.0, 0.05]]), 0.032, 6, i_iron, weather=cw.IRON_W)
    head_post = np.array([head[0] + 0.3, cw_stair.HEAD_Y + cw_stair.STANCHION_H - 0.04,
                          float(zf(cw_stair.HEAD_Y)) - W + 0.12])
    kc.tube(mb, np.array([head_post - [0, cw_stair.STANCHION_H, 0], head_post + [0, 0.04, 0]]), 0.03 if lod else 0.022,
            3 if lod else 6, i_iron, cap_end=True, weather=cw.IRON_W)
    line = []
    chain = tops + hang_tops + [head_post]
    for k, (a, b) in enumerate(zip(chain[:-1], chain[1:])):
        gap = k == len(tops) - 1
        n = (5 if lod else 17) if gap else (3 if lod else 7)
        t = np.linspace(0.0, 1.0, n)[:-1]
        seg = a[None] + (b - a)[None] * t[:, None]
        sag = 2.6 if gap else 0.07  # slack: it hangs in a deep bight across the gap
        seg[:, 1] -= 4.0 * sag * t * (1.0 - t)
        line.append(seg)
    line.append(chain[-1][None])
    kc.tube(mb, np.vstack(line), 0.03 if lod else 0.02, 3 if lod else 5, i_rope, weather=cw.IRON_W)
    cw.bend(mb)
    return mb


def build_stair_broken(seed: int = 852) -> list[kc.MeshBuilder]:
    return [stair_broken("fisher_stair_broken", seed, lod=lod) for lod in (False, True)]


# ---------------------------------------------------------------------------------------------
# Liss's hoist, cut down
# ---------------------------------------------------------------------------------------------
WALK_LOCAL_Y = cw.WALK_Y - (cw.WALK_Y + cw.PARAPET[2])  # -0.9: the walk in the head's frame


def _rope_on_walk(mb: kc.MeshBuilder, pts: np.ndarray, r: float, mat: int, *, sides: int) -> None:
    """A rope lying slack on the walk through the given (x, z) points (smoothed), resting on the slabs."""
    pts = np.asarray(pts, float)
    t = np.linspace(0.0, 1.0, len(pts))
    tt = np.linspace(0.0, 1.0, max(len(pts) * 4, 6))
    x = np.interp(tt, t, pts[:, 0])
    z = np.interp(tt, t, pts[:, 1])
    k = np.array([0.25, 0.5, 0.25])
    for _ in range(2):
        x[1:-1] = np.convolve(x, k, mode="same")[1:-1]
        z[1:-1] = np.convolve(z, k, mode="same")[1:-1]
    c = np.stack([x, np.full_like(x, WALK_LOCAL_Y + r * 0.9), z], -1)
    kc.tube(mb, c, r, sides, mat, weather=cw.IRON_W, variation=0.4, cap_start=True, cap_end=True)


def hoist_cut(name: str, seed: int, *, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
    i_t, i_r, i_i = mb.material(cw.M_TIMBER), mb.material(cw.M_ROPE), mb.material(cw.M_IRON)
    sides = 3 if lod else 5
    rr = 0.03 if lod else 0.016
    heel_shoe = np.array([0.15, cwh.KERB_TOP_LOCAL + 0.12, cwh.KERB_Z_LOCAL])
    # The spar, down on the walk: its heel dropped off the kerb beside the shoe, lying along the walk toward
    # the head, its tip propped on the block.
    heel = np.array([0.55, WALK_LOCAL_Y + 0.09, cwh.KERB_Z_LOCAL + 0.75])
    ang = math.radians(38.0)
    tip = heel + np.array([math.cos(ang), 0.0, math.sin(ang)]) * cwh.SPAR_M + np.array([0.0, 0.1, 0.0])
    kc.tube(mb, np.array([heel, (heel + tip) * 0.5, tip]), np.array([0.09, 0.085, 0.075]), 5 if lod else 9, i_t,
            noise=None if lod else noise, disp_m=0.01, variation=0.3, cap_start=True, cap_end=True,
            weather=kc.Weathering(moss=0.0, salt=0.4, wet=0.45, erosion=0.6))
    # The two cut ends of the head-rope, hanging from the strap-plates still bolted into the head.
    strap = np.array([0.0, 1.35, -cwh.HEAD_BACK - 0.03])
    for k, sx in enumerate((-0.18, 0.18)):
        a = strap + np.array([sx, 0.0, -0.09])
        ln = 0.55 + 0.25 * k
        c = np.array([a, a + [0.02 * (k - 0.5), -ln * 0.5, -0.06], a + [0.04 * (k - 0.5), -ln, -0.04]])
        kc.tube(mb, c, rr, sides, i_r, weather=cw.IRON_W, variation=0.4, cap_end=True)
    # The rest of the head-rope, still made fast at the spar's tip, lying where it fell across the walk.
    _rope_on_walk(mb, [[tip[0], tip[2]], [tip[0] - 0.6, tip[2] + 0.6], [tip[0] - 1.6, tip[2] + 0.3],
                       [tip[0] - 2.2, tip[2] + 1.0], [tip[0] - 3.1, -1.6]], rr, i_r, sides=sides)
    if not lod:
        _rope_on_walk(mb, [[tip[0] + 0.1, tip[2] + 0.05], [tip[0] + 0.5, tip[2] + 0.8], [tip[0] - 0.4, -1.3],
                           [tip[0] - 1.5, -1.0]], rr, i_r, sides=sides)
    # The guys, cut at their ring-bolts: short tails on the kerb; their long ends with the spar.
    for sx in (-1.0, 1.0):
        ring = np.array([sx * 2.6, cwh.KERB_TOP_LOCAL + 0.04, cwh.KERB_Z_LOCAL + 0.1])
        if not lod:
            kc.tube(mb, np.array([ring - [0, 0.02, 0], ring + [0, 0.05, 0]]), 0.035, 6, i_i, cap_end=True)
            tail = np.array([ring + [0, 0.05, 0], ring + [sx * 0.15, 0.02, 0.18], ring + [sx * 0.22, -0.01, 0.32]])
            kc.tube(mb, tail, rr, sides, i_r, weather=cw.IRON_W, cap_end=True)
    _rope_on_walk(mb, [[tip[0] - 0.4, tip[2] - 0.2], [tip[0] - 1.4, tip[2] - 1.4], [heel[0] + 1.9, heel[2] - 0.3]], rr,
                  i_r, sides=sides)
    # The block, still on the spar's tip, lying on its cheek; the fall cut, a short tail and a loose coil.
    blk = tip + np.array([0.05, -0.04, 0.22])
    kc.rounded_block(mb, blk, (0.17, 0.07, 0.12), i_t, rot=kc.rot_y(-ang), radius=0.03, seg=1 if lod else 2,
                     variation=0.6)
    if lod:
        return mb
    kc.rounded_block(mb, blk, (0.2, 0.08, 0.02), i_i, rot=kc.rot_y(-ang), radius=0.01, seg=1)
    t = np.linspace(0.0, 2.0 * np.pi * 1.6, 34)
    cc = blk + np.array([0.6, 0.0, 0.5])
    rad = 0.32 + 0.05 * np.sin(t * 1.7)
    pts = np.stack([cc[0] + rad * np.cos(t), np.full_like(t, WALK_LOCAL_Y + rr), cc[2] + rad * np.sin(t)], -1)
    pts[:, 1] += 0.012 * t / (2 * np.pi)
    kc.tube(mb, pts, rr, sides, i_r, weather=cw.IRON_W, cap_start=True, cap_end=True)
    # The iron: the empty shoe on the kerb, the strap-plates and their bolt heads on the head's back.
    kc.rounded_block(mb, heel_shoe + np.array([0, -0.05, 0]), (0.16, 0.1, 0.16), i_i, radius=0.015, seg=1,
                     rot=kc.rot_x(-math.radians(cwh.SPAR_RAKE_DEG)))
    for sx in (-0.18, 0.18):
        c = strap + np.array([sx, 0.0, 0.0])
        kc.rounded_block(mb, c, (0.05, 0.32, 0.012), i_i, radius=0.006, seg=1)
        for by in (-0.22, 0.22):
            kc.rounded_block(mb, c + np.array([0.0, by, -0.016]), (0.022, 0.022, 0.012), i_i, radius=0.008, seg=1)
        kc.tube(mb, np.array([c + [0, 0.0, -0.01], c + [0, 0.0, -0.09]]), 0.022, 6, i_i, cap_end=True)
    # The spare coil by the heel, left where it lay.
    coil_c = heel_shoe + np.array([0.7, -0.5, 0.9])
    t = np.linspace(0.0, 2.0 * np.pi * 3.0, 60)
    rad = 0.24 + 0.012 * t / (2 * np.pi)
    pts = np.stack([coil_c[0] + rad * np.cos(t), coil_c[1] + 0.03 + 0.018 * t / (2 * np.pi), coil_c[2] + rad * np.sin(t)],
                   -1)
    kc.tube(mb, pts, 0.018, 5, i_r, weather=cw.IRON_W)
    return mb


def build_hoist_cut(seed: int = 842) -> list[kc.MeshBuilder]:
    return [hoist_cut("liss_hoist_cut", seed, lod=lod) for lod in (False, True)]


TARGETS = {
    "watcher_head_b": build_head_b,
    "watcher_head_fallen": build_fallen,
    "watcher_head_cracked": build_cracked,
    "fisher_stair_broken": build_stair_broken,
    "liss_hoist_cut": build_hoist_cut,
}
