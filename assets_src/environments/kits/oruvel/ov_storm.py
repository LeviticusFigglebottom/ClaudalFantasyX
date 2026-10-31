"""Oruvel in the storm (M3-ENV-07B; oruvel.md §7, act1_ch01 C1-12 to C1-15, §5): the breaking-raft state of the
raft-town kit. Pure numpy; see ov_common.py. Every broken piece is in the same frame as the intact piece it replaces
(same origin, same deck heights), so the storm state swaps pieces one for one.

  raft_deck_broken     raft_deck torn between its middle and east hulls: the bearers snapped along the tear, planks
                       sprung and missing, the east hull and its strip of deck pulling away (rolled, drifted 1.2 m,
                       settling), its lashings snapped and trailing in the water, loose planks in the gap
  plank_bridge_broken  plank_bridge gone at mid-span (C1-13, "the bridge goes"): each half still lashed at its deck
                       end and hanging into the water, splintered stringers, the hand-rope and a stay trailing,
                       planks floating below; y 0 is still both deck tops
  hull_capsized        hull_cabin keel-up and awash: the tarred bottom showing 0.3 m clear, rolled and down by the
                       bow, its painter trailing, a thwart, an oar and a basket floating by it; origin at the waterline
  storm_debris         the town coming apart on the water: a cabin's keel-roof adrift (keel-up, torn wall boards
                       hanging from its eaves, its lamp rail still on), floating planks, barrels, a crate, a basket,
                       glass floats and a torn net; over about 14 x 10 m round the origin at the waterline
  net_pen_split_a/b/c  Hullgnaw's arena split three ways (§5 phase 2): the net-pen as three sections, each built in the
                       net_pen frame and then moved so its origin is its hinge (SPLIT_SECTIONS: the hinge, the open
                       pose, the swell); placed at net_pen + hinge with no turn they compose the pen. A: the north
                       walkway with the practice net and its posts; B: the west walkway and the south walkway's west
                       part; C: the east walkway and the rest of the south walkway. The pen net is torn at every split
                       (ragged, its head sagging, twine trailing); the south hand-rope is snapped in two
  reef_edge_far        the sea drawn back off the outer reef (C1-12, O11): a 240 x 40 m strip of exposed reef flat
                       standing just clear of the water with coral heads, and seven of the drowned city's tower crowns
                       standing clear for the first time in years (broken tops, column stubs, dark window rows, weed
                       to their old waterline); for 250 m and beyond; origin at the waterline, long side along X

Everything here is soaked (`soak`: VC.B wet high, salt washed off): the storm's spray and rain are over all of it.
Nothing emits (Kell's beacon is a light the zone adds, oruvel.md §7).
"""

from __future__ import annotations

import math

import numpy as np

import ov_common as oc
import ov_hulls as ohl

kc = oc.kc

M_REEF = "ov_reef"  # the exposed reef flat: pale coral rubble, wet
M_CROWN = "ov_crown"  # the drowned towers' crowns: coral-crusted concrete

TRI_BUDGET = {
    "raft_deck_broken": (18000, 900),
    "plank_bridge_broken": (5000, 220),
    "hull_capsized": (5500, 300),
    "storm_debris": (9000, 500),
    "net_pen_split_a": (7000, 400),
    "net_pen_split_b": (7000, 400),
    "net_pen_split_c": (7000, 400),
    "reef_edge_far": (6000, 1500),
}

STORM = kc.Weathering(moss=0.0, salt=0.3, wet=0.9, erosion=0.6, noise_scale_m=0.6)
TEAR_X = 1.45  # raft_deck_broken: the tear runs along z between the middle hull (x 0) and the east one (x 3)
TORN_POSE = {"pivot": (3.0, 0.0, 0.0), "to": (4.2, -0.25, 0.6), "yaw_deg": 8.0, "roll_deg": 12.0, "pitch_deg": -3.0}
BRIDGE_NEAR_S, BRIDGE_FAR_S = 0.55, 0.66  # plank_bridge_broken: the span is gone between these fractions
BRIDGE_DROP_DEG = (30.0, 48.0)  # each half's hang below the deck line at its lashed end
BRIDGE_WATER_Y = -0.74  # the sea in the bridge's frame (decks ride 0.7-0.8 above it)
PEN_HALF, PEN_INNER, PEN_SPLIT_X = 6.0, 4.6, 0.8
# The net-pen's split (act1_ch01 §5 phase 2), in the net_pen frame (origin the pool's middle at the waterline, yaw 0).
# Each section: its hinge (the piece's origin), the open pose relative to the rest pose (drift in metres; a turn about
# the hinge's +Y; a tilt [about the piece's local X, local Z] as HalunaDresser's tilt_deg), and the swell it pitches
# with once open (degrees about local X, period, phase). The rig: amount a in 0..1 (0 = the intact pen at rest),
#   origin = pen + hinge + a * drift,  basis = yaw(a * yaw_deg) * euler(a * tilt + a * swell(t)).
SPLIT_SECTIONS = {
    "net_pen_split_a": {"hinge": (0.0, 0.0, -5.3),
                        "open": {"drift": (0.4, -0.1, -1.5), "yaw_deg": 5.0, "tilt_deg": (12.0, -4.0)},
                        "swell": {"pitch_deg": 2.5, "period_s": 5.5, "phase": 0.0}},
    "net_pen_split_b": {"hinge": (-5.3, 0.0, 5.3),
                        "open": {"drift": (-1.5, -0.12, 1.2), "yaw_deg": -8.0, "tilt_deg": (-3.5, 5.0)},
                        "swell": {"pitch_deg": 2.0, "period_s": 6.1, "phase": 2.1}},
    "net_pen_split_c": {"hinge": (5.3, 0.0, 5.3),
                        "open": {"drift": (1.6, -0.14, 1.3), "yaw_deg": 9.0, "tilt_deg": (-5.5, 3.5)},
                        "swell": {"pitch_deg": 2.2, "period_s": 4.8, "phase": 4.0}},
}
REEF = (240.0, 40.0)  # reef_edge_far: length along X, depth along Z
# Tower crowns: (x, z, half width, half depth, height of the broken floor above the water, column stubs' extra height)
CROWNS = ((-92.0, -4.0, 7.0, 5.0, 2.2, 3.4), (-58.0, 3.0, 9.0, 6.0, 4.6, 2.6), (-27.0, -6.0, 6.0, 6.0, 1.4, 2.0),
          (6.0, 1.0, 10.0, 6.5, 5.8, 3.0), (39.0, -3.0, 7.5, 5.5, 3.1, 2.4), (70.0, 4.0, 6.5, 6.5, 2.0, 3.6),
          (101.0, -2.0, 8.0, 5.0, 3.8, 2.2))


# ---------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------
def soak(mb: kc.MeshBuilder, water_y: float = 0.0, *, top: float = 0.55, bottom: float = 0.95, start_v: int = 0,
         salt: float = 0.45) -> None:
    """Storm-soaks vertices [start_v:]: VC.B (wet) at least `top`, rising to `bottom` toward the water; the salt
    crust (VC.G) washed down to `salt` of what it was."""
    if not mb.col:
        return
    col = np.asarray(mb.col[start_v:], float)
    y = np.asarray(mb.pos[start_v:], float)[:, 1]
    wet = top + (bottom - top) * np.clip((water_y + 1.6 - y) / 1.8, 0.0, 1.0)
    col[:, 2] = np.clip(np.maximum(col[:, 2], wet), 0.0, 1.0)
    col[:, 1] = col[:, 1] * salt
    mb.col[start_v:] = col.tolist()


def shift(mb: kc.MeshBuilder, offset) -> None:
    if mb.pos:
        mb.pos = (np.asarray(mb.pos, float) + np.asarray(offset, float)).tolist()


def merge_posed(mb: kc.MeshBuilder, part: kc.MeshBuilder, pivot, to, rot: np.ndarray) -> None:
    """Merges `part` turned by `rot` about `pivot` and moved so the pivot lands on `to`."""
    rot = np.asarray(rot, float)
    mb.merge(part, rot, np.asarray(to, float) - rot @ np.asarray(pivot, float))


def euler_yxz(yaw_deg: float, pitch_deg: float, roll_deg: float) -> np.ndarray:
    """Godot's Basis(UP, yaw) * Basis.from_euler((pitch, 0, roll)) as a 3x3 (HalunaDresser's yaw_deg / tilt_deg)."""
    return kc.rot_y(math.radians(yaw_deg)) @ kc.rot_x(math.radians(pitch_deg)) @ kc.rot_z(math.radians(roll_deg))


def broken_plank(mb: kc.MeshBuilder, a, b, width: float, thick: float, mat: int, rng, *, up=oc.UP, noise=None,
                 weather: kc.Weathering = oc.SUN, splinters: int = 3, both: bool = False) -> None:
    """A board from a toward b snapped short of b: the board stops 0.1 m early and its end splits into `splinters`
    slivers of different lengths, bent a little (a fresh break, not a sawn end). `both` breaks the a end too."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    t = kc.normalize(b - a)
    upv = kc.normalize(np.asarray(up, float) - t * float(np.dot(up, t)))
    side = np.cross(t, upv)
    cut = 0.1
    a2 = a + t * cut if both else a
    b2 = b - t * cut
    kc.plank(mb, a2, b2, width, thick, mat, up=upv, weather=weather, variation=float(rng.random()), noise=noise)
    ends = [(b2, t)] + ([(a2, -t)] if both else [])
    for p, d in ends:
        for k in range(splinters):
            off = (k - (splinters - 1) * 0.5) * width / splinters
            ln = float(rng.uniform(0.05, 0.28))
            bend = upv * float(rng.uniform(-0.05, 0.08)) + side * float(rng.uniform(-0.04, 0.04))
            s0 = p - d * 0.02 + side * off
            kc.plank(mb, s0, s0 + d * ln + bend * ln, width / splinters * 0.85, thick * float(rng.uniform(0.5, 0.9)),
                     mat, up=upv, weather=weather, variation=float(rng.random()))


def trailing_rope(mb: kc.MeshBuilder, start, direction, length: float, water_y: float, mat: int, rng, *,
                  radius: float = 0.018, n: int = 10, fray: bool = True) -> None:
    """A snapped line: from `start` it falls to the water and trails `length` metres along `direction` just under
    the surface, wandering a little, thinning to a frayed end (three short strands splayed)."""
    start = np.asarray(start, float)
    d = np.asarray(direction, float) * np.array([1.0, 0.0, 1.0])
    d = kc.normalize(d)
    perp = np.array([-d[2], 0.0, d[0]])
    s = np.linspace(0.0, 1.0, n)
    phase = float(rng.uniform(0.0, 6.28))
    drop = max(float(start[1]) - water_y, 0.0)
    y = water_y - 0.03 + (drop + 0.03) * (1.0 - np.clip(s * 2.2, 0.0, 1.0)) ** 1.6
    pts = start[None, :] * np.array([1.0, 0.0, 1.0]) + d[None, :] * (length * s)[:, None] \
        + perp[None, :] * (0.18 * np.sin(5.0 * s + phase) * s)[:, None]
    pts[:, 1] = y
    radii = radius * (1.0 - 0.45 * s ** 3)
    kc.tube(mb, pts, radii, 4, mat, weather=STORM, variation=float(rng.random()), cap_start=True, cap_end=True)
    if fray:
        end, prev = pts[-1], pts[-2]
        dd = kc.normalize(end - prev)
        for k in range(3):
            a = (k - 1) * 0.5
            tip = end + (dd * math.cos(a) + perp * math.sin(a)) * 0.12
            kc.tube(mb, np.array([end, tip]), radius * 0.35, 3, mat, weather=STORM)


def torn_net(mb: kc.MeshBuilder, p0, p1, drop: float, sag: float, rng, noise, *, side, belly: float = 0.3,
             tear_start: bool = False, tear_end: bool = False, nu: int = 10, nv: int = 5) -> None:
    """oc.net, torn where the pen split: toward a torn end the net hangs shorter and ragged, its head sags (the head
    rope parted) and it bellies further out; a few strands of twine trail from the torn edge."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    side = np.asarray(side, float)
    u = np.linspace(0.0, 1.0, nu)
    v = np.linspace(0.0, 1.0, nv)
    tear = np.zeros(nu)
    if tear_start:
        tear = np.maximum(tear, 1.0 - kc.smoothstep(0.0, 0.3, u))
    if tear_end:
        tear = np.maximum(tear, kc.smoothstep(0.7, 1.0, u))
    rag = rng.uniform(0.0, 0.3, nu)
    dropf = np.clip(1.0 - (0.7 + rag) * tear, 0.12, 1.0)
    head = p0 + (p1 - p0) * u[:, None] - oc.UP * (4.0 * sag * u * (1.0 - u) + 0.45 * tear)[:, None]
    P = head[None, :, :] - oc.UP * (drop * dropf[None, :] * v[:, None])[..., None] \
        + side * (belly * np.sin(math.pi * v)[:, None] * (0.6 + 0.4 * np.sin(math.pi * u))[None, :]
                  * (1.0 + 0.8 * tear)[None, :])[..., None]
    P = P + (noise.fbm(P / 0.5, 2)[..., None] - 0.5) * side * 0.14
    ln = float(np.linalg.norm(p1 - p0))
    uvs = np.stack([np.broadcast_to(u[None, :] * ln, (nv, nu)), (v[:, None] * drop * dropf[None, :])], axis=-1)
    oc.surface(mb, P, mb.material(oc.M_NET), outward=side, uv=uvs, col=np.array([0.0, 0.1, 0.8, 0.5]),
               uv2=np.array([1.0, 0.5]))
    rope = mb.material(oc.M_ROPE)
    for j in [j for j in range(nu) if tear[j] > 0.6][:3]:
        top = P[-1, j]
        tail = top - oc.UP * float(rng.uniform(0.3, 0.8)) + side * float(rng.uniform(-0.1, 0.25))
        kc.tube(mb, np.array([top, (top + tail) * 0.5 + side * 0.06, tail]), 0.006, 3, rope, weather=STORM)


def _hull_under(mb: kc.MeshBuilder, rng, noise, hx: float, length: float, beam: float, depth: float, paint: str,
                deck_y: float, lod: bool) -> None:
    """A raft hull lashed under a deck at deck_y (as ov_hulls.raft does)."""
    gun = deck_y - 0.21
    h = oc.hull("h", length, beam, depth, rng, noise, waterline=-gun, lod=lod, paint=paint,
                sheer=0.25 + 0.1 * float(rng.random()), open_top=True, frames=False)
    oc.place(mb, h, hx, gun, float(rng.uniform(-0.4, 0.4)))


def _bearers(mb: kc.MeshBuilder, x_from: float, x_to: float, z0: float, z1: float, y: float, rng, noise,
             *, broken_end: bool = True, spacing: float = 1.2) -> None:
    """Bearers along x under planks that run along z (oc.deck's along_x=False layout), from x_from toward x_to; with
    `broken_end` each one snaps a different way short of (or past) x_to."""
    timber = mb.material(oc.M_TIMBER)
    by = y - 0.045 - 0.06
    n = max(2, int((z1 - z0) / spacing) + 1)
    sgn = 1.0 if x_to > x_from else -1.0
    for zb in np.linspace(z0 + 0.15, z1 - 0.15, n):
        end = x_to + sgn * float(rng.uniform(-0.1, 0.3))
        if broken_end:
            broken_plank(mb, (x_from, by, zb), (end, by, zb), 0.1, 0.12, timber, rng, noise=noise)
        else:
            kc.plank(mb, (x_from, by, zb), (x_to, by, zb), 0.1, 0.12, timber, variation=float(rng.random()),
                     noise=noise)


# ---------------------------------------------------------------------------------------------
# raft_deck_broken
# ---------------------------------------------------------------------------------------------
def build_raft_deck_broken(seed: int = 781) -> list[kc.MeshBuilder]:
    out = []
    y = ohl.RAFT_DECK_Y
    x0, x1, z0, z1 = -4.5, 4.5, -3.5, 3.5
    p = TORN_POSE
    rot = euler_yxz(p["yaw_deg"], p["pitch_deg"], p["roll_deg"])
    for lod in (False, True):
        rng = kc.rng_for("raft_deck_broken", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("raft_deck_broken" + (oc.LOD if lod else ""))
        timber, rope = mb.material(oc.M_TIMBER), mb.material(oc.M_ROPE)
        # The part that holds: the west and middle hulls under 6 m of deck, torn along the middle hull's east side.
        oc.deck(mb, x0, TEAR_X, z0, z1, y, rng, noise, along_x=False, lod=lod, missing_p=0.07, bearers=False)
        for hx, length, beam, depth, paint in ((-3.0, 11.0, 2.3, 1.15, oc.M_PAINT), (0.0, 11.4, 2.4, 1.2,
                                                                                     oc.M_PAINT_RED)):
            _hull_under(mb, rng, noise, hx, length, beam, depth, paint, y, lod)
        ohl._float_log(mb, rng, noise, x0 - 0.35, z0 + 0.3, z1 - 0.3, 0.12, lod=lod)
        # The part pulling away: the east hull and its strip of deck, built in place and then posed.
        sec = kc.MeshBuilder("torn")
        oc.deck(sec, TEAR_X + 0.17, x1, z0, z1, y, rng, noise, along_x=False, lod=lod, missing_p=0.05, bearers=False)
        _hull_under(sec, rng, noise, 3.0, 10.6, 2.2, 1.1, oc.M_PAINT_WHITE, y, lod)
        ohl._float_log(sec, rng, noise, x1 + 0.35, z0 + 0.3, z1 - 0.3, 0.12, lod=lod)
        if not lod:
            _bearers(mb, x0, TEAR_X, z0, z1, y, rng, noise)
            _bearers(sec, x1, TEAR_X + 0.17, z0, z1, y, rng, noise)
            for part, xs, cleats in ((mb, (x0 - 0.03,), ((x0 + 0.2, z0 + 0.2), (x0 + 0.2, z1 - 0.2))),
                                     (sec, (x1 + 0.03,), ((x1 - 0.2, z0 + 0.2), (x1 - 0.2, z1 - 0.2)))):
                ptimber = part.material(oc.M_TIMBER)
                prope = part.material(oc.M_ROPE)
                for xx in xs:
                    kc.plank(part, (xx, y - 0.12, z0), (xx, y - 0.12, z1), 0.2, 0.05, ptimber, up=(1.0, 0.0, 0.0),
                             variation=float(rng.random()), noise=noise, seg=3)
                for cx, cz in cleats:
                    ohl._cleat(part, (cx, y, cz), rng, noise)
                    oc.lashing(part, (cx, y + 0.22, cz), (0.0, 1.0, 0.0), 0.075, prope, turns=3)
            # The end fascias, each broken at the tear.
            for zz in (z0 - 0.03, z1 + 0.03):
                broken_plank(mb, (x0, y - 0.12, zz), (TEAR_X + 0.1, y - 0.12, zz), 0.2, 0.05, timber, rng,
                             up=(0.0, 0.0, 1.0), noise=noise)
                broken_plank(sec, (x1, y - 0.12, zz), (TEAR_X + 0.2, y - 0.12, zz), 0.2, 0.05,
                             sec.material(oc.M_TIMBER), rng, up=(0.0, 0.0, 1.0), noise=noise)
            # The lashings that held: a few still square on the hulls, the rest parted and trailing.
            for hx in (-3.0, 0.0):
                for zb in np.linspace(z0 + 0.15, z1 - 0.15, 6)[::2]:
                    oc.cross_lash(mb, (hx, y - 0.14, zb), 0.17, rope)
            for zb in (-2.6, -0.4, 1.9):
                trailing_rope(mb, (TEAR_X - 0.05, y - 0.16, zb), (1.0, 0.0, 0.25), float(rng.uniform(1.6, 2.4)),
                              0.0, rope, rng)
            for zb in (-1.5, 1.0):
                trailing_rope(sec, (TEAR_X + 0.25, y - 0.16, zb), (-1.0, 0.0, -0.2), float(rng.uniform(1.0, 1.6)),
                              0.0, sec.material(oc.M_ROPE), rng)
            # Sprung planks at the tear: two lifted at one end, one lying askew across the deck.
            for xx, za, zb, lift in ((TEAR_X - 0.16, -1.4, 0.9, 0.42), (TEAR_X - 0.45, 1.2, 3.1, 0.28)):
                broken_plank(mb, (xx, y - 0.02, za), (xx + 0.08, y + lift, zb), 0.26, 0.044, timber, rng,
                             noise=noise)
            kc.plank(mb, (-1.2, y + 0.03, -2.2), (0.6, y + 0.06, -0.9), 0.27, 0.044, timber,
                     variation=float(rng.random()), noise=noise)
        else:
            kc.rounded_block(mb, (-3.0, y - 0.14, 0.0), (0.12, 0.05, 3.4), timber, seg=1, radius=0.01)
        merge_posed(mb, sec, p["pivot"], p["to"], rot)
        if not lod:
            # Loose planks in the opening water.
            for k in range(3):
                cx, cz = 2.1 + 0.3 * k, -2.0 + 1.6 * k + float(rng.uniform(-0.3, 0.3))
                a = float(rng.uniform(-0.6, 0.6)) + 0.3
                d = np.array([math.sin(a), 0.0, math.cos(a)]) * float(rng.uniform(0.7, 1.1))
                broken_plank(mb, (cx, 0.02, cz) - d, (cx, 0.04, cz) + d, 0.26, 0.044, timber, rng, noise=noise,
                             weather=STORM)
        soak(mb)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# plank_bridge_broken
# ---------------------------------------------------------------------------------------------
def build_plank_bridge_broken(seed: int = 782) -> list[kc.MeshBuilder]:
    """Along +Z from z 0 to z SPAN at y 0, as plank_bridge; each half hinged down from its lashed end."""
    out = []
    L, hw = ohl.BRIDGE_SPAN, ohl.BRIDGE_W * 0.5
    for lod in (False, True):
        rng = kc.rng_for("plank_bridge_broken", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("plank_bridge_broken" + (oc.LOD if lod else ""))
        timber, rope, tar = mb.material(oc.M_TIMBER), mb.material(oc.M_ROPE), mb.material(oc.M_ROPE_TAR)
        for (s_a, s_b, s_end), drop in zip(((0.0, BRIDGE_NEAR_S, 0.0), (BRIDGE_FAR_S, 1.0, 1.0)), BRIDGE_DROP_DEG):
            half = kc.MeshBuilder("half")
            ht, hr = half.material(oc.M_TIMBER), half.material(oc.M_ROPE)
            za, zb = s_a * L, s_b * L
            inward = 1.0 if s_end == 0.0 else -1.0  # from the lashed end toward the break
            z_fix, z_brk = (za, zb) if s_end == 0.0 else (zb, za)
            if lod:
                kc.plank(half, (0.0, -0.05, z_fix), (0.0, -0.05, z_brk), 2 * hw, 0.05, ht)
            else:
                for off in (-hw + 0.1, hw - 0.1):
                    broken_plank(half, (off, -0.1, z_fix - inward * 0.24), (off, -0.1, z_brk + inward *
                                                                            float(rng.uniform(0.0, 0.3))),
                                 0.1, 0.12, ht, rng, noise=noise, splinters=4)
                n = 18
                for k in range(n):
                    s = (k + 0.5) / n
                    if not (s_a < s < s_b) or rng.random() < 0.18:
                        continue
                    z = s * L
                    kc.plank(half, (-hw, -0.02, z), (hw, -0.02, z), L / n - 0.04, 0.04, ht,
                             variation=float(rng.random()), noise=noise)
                    if k % 3 == 1:
                        for off in (-hw + 0.1, hw - 0.1):
                            oc.lashing(half, (off, -0.06, z), (0.0, 0.0, 1.0), 0.06, hr, turns=2, pitch=0.03)
                # The hard lashings at the deck end still hold; the end beam is still bound to the deck edge.
                kc.plank(half, (-hw - 0.15, -0.1, z_fix), (hw + 0.15, -0.1, z_fix), 0.14, 0.12, ht,
                         variation=float(rng.random()), noise=noise)
                for off in (-hw + 0.1, hw - 0.1):
                    oc.lashing(half, (off, -0.1, z_fix), (1.0, 0.0, inward), 0.09, hr, turns=5, pitch=0.028,
                               rope_r=0.018)
                # A hand-rope post at the lashed end, its rope parted and trailing toward the break.
                s_post = 0.06 if s_end == 0.0 else 0.94
                pp = np.array([hw + 0.04, 0.0, s_post * L])
                ohl.village_post(half, pp - np.array([0.0, 0.18, 0.0]), pp + np.array([0.0, 0.95, 0.0]), 0.042, rng,
                                 noise, 6)
            rot = kc.rot_x(math.radians(drop) * (1.0 if s_end == 0.0 else -1.0))
            merge_posed(mb, half, (0.0, -0.1, z_fix), (0.0, -0.1, z_fix), rot)
        if not lod:
            # The hand-ropes and one stay hang from the posts and the deck ends into the water.
            trailing_rope(mb, (hw + 0.04, 0.85, 0.06 * L), (0.15, 0.0, 1.0), 2.2, BRIDGE_WATER_Y, rope, rng)
            trailing_rope(mb, (hw + 0.04, 0.85, 0.94 * L), (0.3, 0.0, -1.0), 1.6, BRIDGE_WATER_Y, rope, rng)
            trailing_rope(mb, (-hw * 1.3, -0.08, -0.3), (-0.4, 0.0, 1.0), 2.6, BRIDGE_WATER_Y, tar, rng,
                          radius=0.013)
            # Planks knocked out of it, floating below the gap.
            for k in range(4):
                cz = L * 0.5 + float(rng.uniform(-1.4, 1.6))
                cx = float(rng.uniform(-1.6, 1.6))
                a = float(rng.uniform(-1.2, 1.2))
                d = np.array([math.cos(a), 0.0, math.sin(a)]) * hw
                kc.plank(mb, np.array([cx, BRIDGE_WATER_Y + 0.02, cz]) - d,
                         np.array([cx, BRIDGE_WATER_Y + 0.03, cz]) + d, L / 18 - 0.04, 0.04, timber, weather=STORM,
                         variation=float(rng.random()), noise=noise)
        soak(mb, BRIDGE_WATER_Y)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# hull_capsized
# ---------------------------------------------------------------------------------------------
def build_hull_capsized(seed: int = 783) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hull_capsized", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("hull_capsized" + (oc.LOD if lod else ""))
        h = oc.hull("h", 10.0, 2.6, 1.2, rng, noise, waterline=-0.55, lod=lod, sheer=0.32, open_top=True,
                    keel_up=True)
        # Keel-up its keel stands about 1.23 above the old gunwale: put 0.3 of it clear of the water.
        mb.merge(h, euler_yxz(0.0, -2.5, 9.0), (0.0, -0.93, 0.0))
        if not lod:
            timber, rope = mb.material(oc.M_TIMBER), mb.material(oc.M_ROPE)
            trailing_rope(mb, (0.0, -0.05, -5.0), (0.3, 0.0, -1.0), 3.2, 0.0, rope, rng, radius=0.02)
            kc.plank(mb, (2.0, 0.02, -1.4), (3.9, 0.04, -0.6), 0.22, 0.04, timber, weather=STORM,
                     variation=float(rng.random()), noise=noise)
            # An oar and a basket floating off her quarter.
            kc.tube(mb, np.array([[-2.2, 0.03, 2.6], [-3.4, 0.05, 4.6]]), 0.03, 5, timber, cap_start=True, cap_end=True)
            kc.rounded_block(mb, (-3.5, 0.05, 4.8), (0.08, 0.012, 0.2), timber, rot=kc.rot_y(0.55), radius=0.01,
                             seg=1)
            oc.basket(mb, (2.6, -0.12, 3.2), 0.22, 0.28, rng)
        soak(mb)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# storm_debris
# ---------------------------------------------------------------------------------------------
def build_storm_debris(seed: int = 784) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("storm_debris", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("storm_debris" + (oc.LOD if lod else ""))
        timber, rope = mb.material(oc.M_TIMBER), mb.material(oc.M_ROPE)
        # A cabin's keel-roof adrift, keel-up as it sat, low in the water: torn wall boards still nailed under its
        # eaves, its lamp rail still on one side.
        roof = kc.MeshBuilder("roof")
        oc.keel_roof(roof, 7.0, 4.4, 1.0, 0.0, rng, noise, lod=lod, paint=oc.M_PAINT_TEAL, sheer=0.26)
        if not lod:
            rt = roof.material(oc.M_TIMBER)
            for k in range(6):
                sgn = 1.0 if k % 2 else -1.0
                z = -2.4 + k * 0.95
                xe = sgn * float(oc.hull_halfbreadth(4.4, 2.0 * z / 7.0)) * 0.9
                broken_plank(roof, (xe, -0.05, z - 0.35), (xe + sgn * 0.05, -float(rng.uniform(0.5, 1.1)),
                                                             z - 0.3 + float(rng.uniform(-0.2, 0.2))),
                             0.22, 0.035, rt, rng, up=(sgn, 0.0, 0.0), noise=noise)
            ri = roof.material(oc.M_IRON)
            kc.tube(roof, np.array([[2.0, -0.12, -2.0], [2.05, -0.12, 1.6]]), 0.012, 4, ri, cap_start=True,
                    cap_end=True)
            for zh in (-1.4, -0.3, 0.8):
                kc.tube(roof, np.array([[2.03, -0.12, zh], [2.05, -0.24, zh], [2.09, -0.2, zh]]), 0.007, 4, ri)
        merge_posed(mb, roof, (0.0, 0.0, 0.0), (-3.0, -0.2, -1.0), euler_yxz(28.0, 4.0, -24.0))
        # Floating planks, some broken, a few still nailed in pairs.
        n = 6 if lod else 14
        for k in range(n):
            cx, cz = float(rng.uniform(-7.0, 7.0)), float(rng.uniform(-5.0, 5.0))
            if abs(cx + 3.0) < 2.6 and abs(cz + 1.0) < 3.6:
                cx += 5.5
            a = float(rng.uniform(0.0, math.pi))
            ln = float(rng.uniform(0.9, 2.6))
            d = np.array([math.cos(a), 0.0, math.sin(a)]) * ln * 0.5
            pa, pb = np.array([cx, 0.02, cz]) - d, np.array([cx, 0.03 + float(rng.uniform(0, 0.04)), cz]) + d
            if lod:
                kc.plank(mb, pa, pb, 0.26, 0.04, timber)
            elif k % 3 == 0:
                broken_plank(mb, pa, pb, 0.26, 0.044, timber, rng, noise=noise, weather=STORM, both=True)
            else:
                kc.plank(mb, pa, pb, 0.26, 0.044, timber, weather=STORM, variation=float(rng.random()), noise=noise)
                if k % 4 == 1:
                    side = np.array([-d[2], 0.0, d[0]]) / max(np.linalg.norm(d), 1e-9) * 0.27
                    kc.plank(mb, pa + side, pb + side * 1.1, 0.26, 0.044, timber, weather=STORM,
                             variation=float(rng.random()), noise=noise)
        oc.barrel(mb, (2.8, -0.22, 2.6), 0.32, 0.9, rng, lying=True, lod=lod)
        oc.barrel(mb, (5.2, -0.2, -3.1), 0.3, 0.85, rng, lying=True, lod=lod)
        oc.crate(mb, (-6.2, 0.05, 3.4), (0.45, 0.3, 0.32), rng, noise, lod=lod, yaw=0.7)
        if not lod:
            oc.basket(mb, (0.8, -0.14, 4.2), 0.24, 0.3, rng)
            glass = mb.material(oc.M_GLASS)
            for k in range(4):
                fx, fz = float(rng.uniform(-5.5, 6.5)), float(rng.uniform(-4.5, 4.5))
                oc.lathe(mb, [(0.0, -0.07), (0.055, -0.045), (0.065, 0.0), (0.055, 0.045), (0.0, 0.07)], glass,
                         sides=8, at=(fx, 0.01, fz))
            # A torn net floating with a parted head rope.
            torn_net(mb, (1.5, 0.05, -4.2), (4.6, 0.02, -2.4), 1.6, 0.05, rng, noise, side=(0.0, 1.0, 0.0),
                     belly=0.04, tear_end=True, nu=8, nv=4)
            trailing_rope(mb, (1.5, 0.05, -4.2), (-1.0, 0.0, -0.3), 1.8, 0.0, rope, rng)
        soak(mb)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# net_pen_split_a / _b / _c
# ---------------------------------------------------------------------------------------------
def _pen_strip(mb: kc.MeshBuilder, rng, noise, x0: float, x1: float, z0: float, z1: float, *, lod: bool,
               runs_along_x: bool, broken_x: float | None = None, broken_from: float | None = None) -> None:
    """One of net_pen's walkways (its planks across it, three float logs under it); with `broken_x` its bearers
    (which run along x) snap at that end instead of reaching it."""
    y = ohl.NET_PEN_Y
    bearers = broken_x is None
    oc.deck(mb, x0, x1, z0, z1, y, rng, noise, along_x=not runs_along_x, lod=lod, missing_p=0.04, bearers=bearers)
    if not bearers and not lod:
        _bearers(mb, broken_from, broken_x, z0, z1, y, rng, noise)
    if runs_along_x:
        ohl._float_log(mb, rng, noise, (z0 + z1) * 0.5, x0 + 0.3, x1 - 0.3, 0.1, lod=lod, along_x=True, n=3)
    else:
        ohl._float_log(mb, rng, noise, (x0 + x1) * 0.5, z0 - 0.4, z1 + 0.4, 0.1, lod=lod, n=3)


def _pen_section(name: str, seed: int) -> list[kc.MeshBuilder]:
    out = []
    half, inner, sx = PEN_HALF, PEN_INNER, PEN_SPLIT_X
    y = ohl.NET_PEN_Y
    hinge = np.asarray(SPLIT_SECTIONS[name]["hinge"], float)
    part = name[-1]
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (oc.LOD if lod else ""))
        rope = mb.material(oc.M_ROPE)
        if part == "a":
            _pen_strip(mb, rng, noise, -half, half, -half, -inner, lod=lod, runs_along_x=True)
        elif part == "b":
            _pen_strip(mb, rng, noise, -half, -inner, -inner, inner, lod=lod, runs_along_x=False)
            _pen_strip(mb, rng, noise, -half, sx, inner, half, lod=lod, runs_along_x=True, broken_x=sx,
                       broken_from=-half)
        else:
            _pen_strip(mb, rng, noise, inner, half, -inner, inner, lod=lod, runs_along_x=False)
            _pen_strip(mb, rng, noise, sx, half, inner, half, lod=lod, runs_along_x=True, broken_x=sx,
                       broken_from=half)
        posts = {"a": ((-inner, -inner, 2.4), (inner, -inner, 2.4)), "b": ((-inner, inner, 1.2),),
                 "c": ((inner, inner, 1.2),)}[part]
        if lod:
            for cx, cz, ph in posts:
                kc.tube(mb, np.array([[cx, y, cz], [cx, y + ph, cz]]), 0.08, 4, mb.material(oc.M_TIMBER))
        else:
            for cx, cz, ph in posts:
                ohl.village_post(mb, (cx, y - 0.3, cz), (cx, y + ph, cz), 0.08, rng, noise)
            ny = y - 0.1
            if part == "a":
                torn_net(mb, (-inner, ny, -inner), (inner, ny, -inner), 2.4, 0.05, rng, noise, side=(0, 0, 1),
                         belly=0.35, tear_start=True, tear_end=True)
                # The practice net between the north posts, still up; a sodden belly in it.
                oc.rope(mb, (-inner, y + 2.3, -inner), (inner, y + 2.3, -inner), 0.16, 0.02, rope, n=12)
                oc.net(mb, (-inner, y + 2.28, -inner), (inner, y + 2.24, -inner), 2.1, 0.16, nu=12, nv=6,
                       noise=noise, side=(0.0, 0.0, 1.0), belly=0.45)
                glass = mb.material(oc.M_GLASS)
                for k in range(9):
                    f = (k + 0.5) / 9
                    fx = -inner + f * 2 * inner
                    fy = y + 2.3 - 4.0 * 0.16 * f * (1 - f) - 0.06
                    oc.lathe(mb, [(0.0, -0.06), (0.05, -0.04), (0.06, 0.0), (0.05, 0.04), (0.0, 0.06)], glass,
                             sides=8, at=(fx, fy, -inner + 0.03))
            elif part == "b":
                torn_net(mb, (-inner, ny, inner), (-inner, ny, -inner), 2.4, 0.05, rng, noise, side=(1, 0, 0),
                         belly=0.35, tear_end=True)
                torn_net(mb, (sx, ny, inner), (-inner, ny, inner), 2.4, 0.05, rng, noise, side=(0, 0, -1),
                         belly=0.35, tear_start=True, nu=8)
                trailing_rope(mb, (-inner, y + 1.1, inner), (1.0, 0.0, 0.35), 3.4, 0.0, rope, rng)
                timber = mb.material(oc.M_TIMBER)
                for x in (-0.25, 0.25):  # the ladder into the pool, on the south walkway west of the split
                    kc.plank(mb, (x, -0.9, inner - 0.15), (x, y + 0.4, inner + 0.02), 0.05, 0.05, timber,
                             variation=0.3)
                for k in range(4):
                    yy = -0.6 + k * 0.33
                    kc.plank(mb, (-0.25, yy, inner - 0.12 + 0.02 * k), (0.25, yy, inner - 0.12 + 0.02 * k), 0.04,
                             0.04, timber, variation=0.5)
            else:
                torn_net(mb, (inner, ny, -inner), (inner, ny, inner), 2.4, 0.05, rng, noise, side=(-1, 0, 0),
                         belly=0.35, tear_start=True)
                torn_net(mb, (inner, ny, inner), (sx, ny, inner), 2.4, 0.05, rng, noise, side=(0, 0, -1),
                         belly=0.35, tear_end=True, nu=6)
                trailing_rope(mb, (inner, y + 1.1, inner), (-1.0, 0.0, 0.4), 2.6, 0.0, rope, rng)
        soak(mb)
        shift(mb, -hinge)
        out.append(mb)
    return out


def build_net_pen_split_a(seed: int = 785) -> list[kc.MeshBuilder]:
    return _pen_section("net_pen_split_a", seed)


def build_net_pen_split_b(seed: int = 786) -> list[kc.MeshBuilder]:
    return _pen_section("net_pen_split_b", seed)


def build_net_pen_split_c(seed: int = 787) -> list[kc.MeshBuilder]:
    return _pen_section("net_pen_split_c", seed)


def section_pose(name: str, amount: float, t: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """The rig, as Combat drives it (and the preview poses it): the section's (basis 3x3, origin) in the net_pen frame
    at split `amount` (0 = rest, the intact pen; 1 = open) and swell time `t` seconds."""
    s = SPLIT_SECTIONS[name]
    o, sw = s["open"], s["swell"]
    swell = sw["pitch_deg"] * math.sin(2.0 * math.pi * t / sw["period_s"] + sw["phase"])
    basis = euler_yxz(amount * o["yaw_deg"], amount * (o["tilt_deg"][0] + swell), amount * o["tilt_deg"][1])
    origin = np.asarray(s["hinge"], float) + amount * np.asarray(o["drift"], float)
    return basis, origin


# PC pass 7 row 77 (the Lead, 10-31): from O17 at 250-300 m each crown read as a plain grey box on the horizon
# (greybox). A broken tower's top is ragged: the next floor's walls stand in stretches of different heights round the
# edge, gaps where they fell, so the skyline is a row of broken towers. Deterministic by position (no rng draw, so the
# rest of the piece is unchanged); the step is coarser at LOD1, which is what 300 m sees. The windows grow to read.
CROWN_WINDOW_HALF = (0.5, 0.75, 0.03)
PARAPET_STEP_M = (1.4, 3.0)  # LOD0, LOD1
PARAPET_T = 0.35


def _broken_parapet(mb, mat: int, cx: float, cz: float, hx: float, hz: float, h: float, stub: float,
                    lod: bool) -> None:
    step = PARAPET_STEP_M[1 if lod else 0]
    for side, (ax, az, length) in enumerate(((1, 0, hx), (0, 1, hz), (-1, 0, hx), (0, -1, hz))):
        # The side's outer face: along (ax, az) at the far edge of the other axis.
        n_seg = max(1, int(round(2 * length / step)))
        for k in range(n_seg):
            t = -length + (k + 0.5) * 2 * length / n_seg
            u = math.sin(cx * 0.37 + cz * 0.91 + side * 2.1 + k * 1.7)  # a fixed, irregular height pattern
            if u < -0.55:
                continue  # fallen here
            hh = stub * (0.25 + 0.75 * (0.5 + 0.5 * u) ** 1.5)
            if ax:
                px, pz = cx + t, cz + (hz - PARAPET_T * 0.5) * (1 if side == 0 else -1)
                half = (length / n_seg - 0.03, hh * 0.5, PARAPET_T * 0.5)
            else:
                px, pz = cx + (hx - PARAPET_T * 0.5) * (1 if side == 1 else -1), cz + t
                half = (PARAPET_T * 0.5, hh * 0.5, length / n_seg - 0.03)
            kc.rounded_block(mb, (px, h + hh * 0.5, pz), half, mat, radius=0.04, seg=1, weather=STORM)


# ---------------------------------------------------------------------------------------------
# reef_edge_far
# ---------------------------------------------------------------------------------------------
def build_reef_edge_far(seed: int = 788) -> list[kc.MeshBuilder]:
    out = []
    length, depth = REEF
    for lod in (False, True):
        rng = kc.rng_for("reef_edge_far", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("reef_edge_far" + (oc.LOD if lod else ""))
        reef, crown, dark = mb.material(M_REEF), mb.material(M_CROWN), mb.material(oc.M_DARK)
        # The reef flat, bared: a low shelf just clear of the water (0.1-0.5 m), its edges running under.
        nx, nz = (24, 5) if lod else (60, 9)
        xs = np.linspace(-length * 0.5, length * 0.5, nx)
        zs = np.linspace(-depth * 0.5, depth * 0.5, nz)
        X, Z = np.meshgrid(xs, zs)
        P0 = np.stack([X, np.zeros_like(X), Z], axis=-1)
        n = noise.fbm(P0 / 9.0, 3)
        edge = np.minimum(1.0 - np.abs(Z) / (depth * 0.5), 1.0 - np.abs(X) / (length * 0.5))
        Y = -0.9 + 1.25 * kc.smoothstep(0.0, 0.35, edge) + 0.35 * (n - 0.5)
        P = np.stack([X, Y, Z], axis=-1)
        col = np.stack([np.zeros_like(X), 0.25 * n, np.clip(0.95 - 0.5 * kc.smoothstep(0.1, 0.5, Y), 0, 1),
                        0.4 + 0.3 * n], axis=-1)
        oc.surface(mb, P, reef, outward=(0.0, 1.0, 0.0), uv=np.stack([X * 0.25, Z * 0.25], -1), col=col,
                   uv2=np.array([1.0, 0.5]))
        if not lod:
            # Coral heads on the flat, wet and dark-crowned.
            for k in range(26):
                cx, cz = float(rng.uniform(-length * 0.46, length * 0.46)), float(rng.uniform(-depth * 0.3, depth * 0.3))
                r = float(rng.uniform(0.6, 1.8))
                kc.rounded_block(mb, (cx, 0.0, cz), (r, r * 0.45, r * float(rng.uniform(0.7, 1.2))), reef,
                                 rot=kc.rot_y(float(rng.uniform(0, 3))), radius=r * 0.4, seg=1, noise=noise,
                                 disp_m=0.15, weather=STORM, variation=float(rng.random()))
        # The crowns of the drowned towers, standing clear: the broken top floor's slab on its walls, column stubs
        # and a wall fragment above it, a row of dark window holes in the walls, weed to the old waterline.
        for cx, cz, hx, hz, h, stub in CROWNS:
            outline = np.array([[cx - hx, cz - hz], [cx + hx, cz - hz], [cx + hx, cz + hz], [cx - hx, cz + hz]])
            kc.polygon_prism(mb, outline, -1.0, h, crown, col=np.array([0.0, 0.2, 0.8, 0.6]),
                             uv2=np.array([0.8, float(rng.random())]))
            _broken_parapet(mb, crown, cx, cz, hx, hz, h, stub, lod)
            if lod:
                continue
            for sgn in (-1.0, 1.0):  # window rows on the long faces, one floor down from the top
                for k in range(int(hx // 1.6)):
                    wx = cx - hx + 0.9 + k * 1.6
                    if rng.random() < 0.2:
                        continue
                    kc.rounded_block(mb, (wx, h - 1.3, cz + sgn * (hz + 0.02)), CROWN_WINDOW_HALF, dark, seg=1,
                                     radius=0.01)
            ncol = 4 + int(rng.integers(0, 3))
            for k in range(ncol):
                px = cx + float(rng.uniform(-hx + 0.6, hx - 0.6))
                pz = cz + float(rng.uniform(-hz + 0.6, hz - 0.6))
                ph = stub * float(rng.uniform(0.35, 1.0))
                kc.rounded_block(mb, (px, h + ph * 0.5, pz), (0.32, ph * 0.5, 0.32), crown,
                                 rot=kc.rot_z(float(rng.normal(0, 0.06))), radius=0.05, seg=1, noise=noise,
                                 disp_m=0.06, weather=STORM, variation=float(rng.random()))
            fw = hx * float(rng.uniform(0.4, 0.8))
            kc.rounded_block(mb, (cx - hx + fw * 0.5, h + stub * 0.45, cz - hz + 0.2), (fw * 0.5, stub * 0.45, 0.18),
                             crown, radius=0.05, seg=1, noise=noise, disp_m=0.12, weather=STORM,
                             variation=float(rng.random()))
        # Weed and wet low, the tops dry and pale (the shader's tide band adds the weed film at the live water).
        col = np.asarray(mb.col, float)
        yv = np.asarray(mb.pos, float)[:, 1]
        col[:, 2] = np.clip(np.maximum(col[:, 2], 1.0 - kc.smoothstep(0.5, 2.5, yv)), 0.0, 1.0)
        mb.col = col.tolist()
        out.append(mb)
    return out


TARGETS = {
    "raft_deck_broken": build_raft_deck_broken,
    "plank_bridge_broken": build_plank_bridge_broken,
    "hull_capsized": build_hull_capsized,
    "storm_debris": build_storm_debris,
    "net_pen_split_a": build_net_pen_split_a,
    "net_pen_split_b": build_net_pen_split_b,
    "net_pen_split_c": build_net_pen_split_c,
    "reef_edge_far": build_reef_edge_far,
}
