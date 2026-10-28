"""Glass skate, Ch16 the Pale Rim's white shallows (M3-CRE-628): docs/kb/art/creatures/act2/glass_skate.md.

blender --background --factory-startup --python assets_src/creatures/glass_skate/build_glass_skate.py -- \
    --out assets/creatures/glass_skate/glass_skate.glb

A skate that buries itself in the white sand of the Rim's shallows, its back the colour of the water over the sand, so
that only its eyes and the line of its back show. Its one exaggeration: the back is nearly clear, like the water over
it (pale foam_white and cumulus_lit going glassy salt_glass toward the thin margins, on a glossy, clear-coated
surface). A broad rounded disc 1.4 m across with a pointed snout and a thick tail with two small dorsal fins, lying
flat (y 0 is the sand; the disc's underside lies on it). The eyes are lacquer_black on raised turrets; the belly
bone; the weak point a small spawn_wound split at the tail root.

**The battle read (M3-CRE-645).** The clear back stays, but its edges read: a thornback row of dark-tipped thorns
down the midline and the tail (and a short row on each shoulder), a rim of darker `sand_wet` pigment round the disc's
margin, and the eyes raised higher on darker turrets, each rimmed black.

Run without Blender (`python3 build_glass_skate.py --report`) for the triangle count and each clip's numbers.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 8251
PAL = {k: ck.hexrgb(v) for k, v in {
    "foam_white": "#EEF6F4", "cumulus_lit": "#FFF8EE", "salt_glass": "#BFE6E0", "lacquer_black": "#1D1916",
    "bone": "#E6DAC0", "spawn_wound": "#3FE0C8", "sand_wet": "#B59D74",
}.items()}
BACK = ck.mix(PAL["foam_white"] * 0.9, PAL["cumulus_lit"] * 0.88, 0.4)  # both held under the albedo ceiling
GLASS = PAL["salt_glass"] * 0.92
BLACK = PAL["lacquer_black"]
BELLY = PAL["bone"] * 0.95
RIM = PAL["sand_wet"]  # the margin's darker pigment
THORN = ck.mix(PAL["sand_wet"], PAL["lacquer_black"], 0.35)  # a thorn's base; its tip goes to lacquer_black

HALF_W = 0.7  # the disc is 1.4 m across
NOSE_Z, REAR_Z = 0.66, -0.5
DOME = 0.11  # the back's height over the margin at the middle
MARGIN = 0.012  # the margin's height over the sand
UNDER = 0.0  # the underside lies on the sand
BODY_Y = 0.055
DISC = 3  # bones per side
TAIL = np.array([(0.0, 0.06, -0.42), (0.0, 0.06, -0.65), (0.0, 0.055, -0.88), (0.0, 0.05, -1.1), (0.0, 0.045, -1.32)])
TAIL_R = (0.055, 0.045, 0.034, 0.022, 0.01)
EYE_X, EYE_Z = 0.085, 0.27
SPIRACLE_X, SPIRACLE_Z = 0.1, 0.17
TURRET_H = 0.045  # the eye bone's length above its head (the rig; the turret mesh is taller)
TURRET_TOP = 0.072  # the turret's height over the back
DISC_RINGS = 14  # the back's rings, centre to margin
WOUND_Z = -0.47  # the split at the tail root (the weak point)


def outline(a: np.ndarray) -> np.ndarray:
    """The disc's outline at angle a (0 = the left wing tip +x, pi/2 = the snout): rounded wings, a pointed snout, a
    rounded rear."""
    cu, cv = np.cos(a), np.sin(a)
    t = 1.0 / (np.abs(cu) ** 1.8 + np.abs(cv) ** 1.8) ** (1.0 / 1.8)
    uu, vv = cu * t, cv * t
    x = uu * HALF_W * (1.0 - 0.18 * np.maximum(vv, 0.0) ** 2)
    z = np.where(vv > 0, vv * NOSE_Z * (0.82 + 0.18 * np.abs(vv) ** 3), -vv * REAR_Z)
    z = z + 0.06 * (1.0 - np.abs(uu)) * (vv > 0)  # the snout's point
    return np.column_stack([x, np.zeros_like(x), z])


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    rig.add("body", (0, BODY_Y, -0.2), (0, BODY_Y, 0.25), "root")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for k in range(DISC):
            x0, x1 = s * (0.12 + k * 0.19), s * (0.12 + (k + 1) * 0.19)
            rig.add(f"disc_{tag}{k}", (x0, BODY_Y, 0.0), (x1, BODY_Y, 0.0), "body" if k == 0 else f"disc_{tag}{k - 1}")
        rig.add(f"eye_{tag}", (s * EYE_X, BODY_Y + 0.04, EYE_Z), (s * EYE_X, BODY_Y + 0.04 + TURRET_H + 0.04, EYE_Z),
                "body")
    for k in range(4):
        rig.add(f"tail{k}", TAIL[k], TAIL[k + 1], "body" if k == 0 else f"tail{k - 1}")
    return rig


def disc_skin(rig: ck.Rig):
    left = rig.chain([f"disc_l{k}" for k in range(DISC)], [(0.12 + k * 0.19, BODY_Y, 0.0) for k in range(DISC + 1)])
    right = rig.chain([f"disc_r{k}" for k in range(DISC)], [(-0.12 - k * 0.19, BODY_Y, 0.0) for k in range(DISC + 1)])
    body = rig.index("body")

    def f(P):
        Jl, Wl = left(P)
        Jr, Wr = right(P)
        n = len(P)
        J = np.zeros((n, 2), dtype=np.int64)
        W = np.zeros((n, 2))
        ax = np.abs(P[:, 0])
        for v in range(n):
            if ax[v] < 0.14:
                w = float(ck.smoothstep(0.06, 0.14, ax[v]))
                J[v] = (body, Jl[v, 0] if P[v, 0] >= 0 else Jr[v, 0])
                W[v] = (1.0 - w, w)
            elif P[v, 0] >= 0:
                J[v], W[v] = Jl[v], Wl[v]
            else:
                J[v], W[v] = Jr[v], Wr[v]
        return J, W

    return f


def top_height(P: np.ndarray, r: np.ndarray) -> np.ndarray:
    """The back's height: a low dome over the body, a ridge along the spine, thinning to the margin."""
    body = np.exp(-(P[:, 0] / 0.2) ** 2 - ((P[:, 2] - 0.02) / 0.42) ** 2)
    ridge = np.exp(-(P[:, 0] / 0.05) ** 2) * ck.smoothstep(0.45, -0.4, P[:, 2]) * 0.012
    return MARGIN + DOME * (1.0 - r ** 2) ** 1.6 * (0.45 + 0.55 * body) + ridge


def disc(mesh: ck.Mesh, rig: ck.Rig) -> None:
    segs, rings = 44, DISC_RINGS
    ang = np.linspace(0, 2 * math.pi, segs, endpoint=False)
    edge = outline(ang)
    skin = disc_skin(rig)
    radii = np.linspace(0.0, 1.0, rings + 1) ** 0.75  # rings closer together toward the margin, for the rim
    r = np.repeat(radii, segs)
    P = np.vstack([edge * rr for rr in radii])
    P[:, 1] = top_height(P, r)
    P[:segs, 0] = 0.0
    P[:segs, 2] = 0.0
    T = ck.grid_tris(rings + 1, segs, True)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    if float(fn[:, 1].sum()) < 0:
        T = ck.flip(T)
    n = ck.fbm(P * np.array([5.0, 5.0, 5.0]), SEED + 1)
    mottle = ck.smoothstep(0.1, 0.45, ck.fbm(P * 11.0, SEED + 2))
    col = BACK * (0.92 + 0.08 * n)[:, None]
    col = ck.mix(col, GLASS, (0.75 * ck.smoothstep(0.55, 0.98, r))[:, None])  # glassy toward the thin margins
    col = ck.mix(col, GLASS * 0.9, (0.35 * mottle)[:, None])  # a faint ripple-light mottle, like sand under water
    # the rim: a band of darker pigment round the margin, broken a little by the mottle, darkest at the edge
    rim = ck.smoothstep(0.8, 0.95, r) * (0.75 + 0.25 * (1.0 - mottle))
    col = ck.mix(col, RIM, (0.85 * rim)[:, None])
    # (the two dark spiracles behind the eyes are their own small parts, in eyes(): painted on this coarse a back
    # they smeared grey)
    # the weak point: a short split across the spine at the tail root
    split = np.exp(-(P[:, 0] / 0.035) ** 2 - ((P[:, 2] - WOUND_Z) / 0.014) ** 2)
    glow = ck.smoothstep(0.35, 0.8, split)
    col = ck.mix(col, PAL["spawn_wound"] * 0.65, glow[:, None])
    ck.finish(mesh, P, T, "back", col, skin, wet=0.85, cavity=0.15 * mottle + 0.4 * ck.smoothstep(0.1, 0.35, split) *
              (1.0 - glow), emission=glow)
    # the underside: flat on the sand, bone, darker at the gill slits
    under_r = np.linspace(0.0, 1.0, 7) ** 0.85
    Pu = np.vstack([edge * rr for rr in under_r])
    Pu[:, 1] = UNDER + (MARGIN - UNDER) * np.repeat(under_r, segs) ** 6
    Pu[:segs, 0] = 0.0
    Pu[:segs, 2] = 0.0
    Tu = ck.grid_tris(7, segs, True)
    fn = np.cross(Pu[Tu[:, 1]] - Pu[Tu[:, 0]], Pu[Tu[:, 2]] - Pu[Tu[:, 0]])
    if float(fn[:, 1].sum()) > 0:
        Tu = ck.flip(Tu)
    ck.finish(mesh, Pu, Tu, "belly", np.tile(BELLY, (len(Pu), 1)), skin, wet=0.6, cavity=0.1)
    # the margin's rim, closing the gap between back and belly
    Pr = np.vstack([edge, edge])
    Pr[:segs, 1] = top_height(edge, np.ones(segs))
    Pr[segs:, 1] = MARGIN
    Tr = ck.grid_tris(2, segs, True)
    c = Pr[Tr].mean(axis=1)
    fn = np.cross(Pr[Tr[:, 1]] - Pr[Tr[:, 0]], Pr[Tr[:, 2]] - Pr[Tr[:, 0]])
    if float((fn[:, [0, 2]] * c[:, [0, 2]]).sum()) < 0:
        Tr = ck.flip(Tr)
    ck.finish(mesh, Pr, Tr, "back", np.tile(RIM * 0.9, (len(Pr), 1)), skin, wet=0.85)


def eyes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    turret = ck.mix(ck.mix(BACK, GLASS, 0.4), RIM, 0.45)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        b = rig.bones[rig.index(f"eye_{tag}")]
        h0 = np.asarray(b.head)
        base = np.array([h0[0], top_height(h0[None], np.array([0.0]))[0] - 0.01, h0[2]])
        path = ck.bezier([base, base + np.array([0.0, TURRET_TOP * 0.6, 0.0]),
                          base + np.array([0.0, TURRET_TOP, 0.006])], 5)
        P, T = ck.tube(path, np.array([0.04, 0.032, 0.027, 0.025, 0.024]), 10, cap_start=False)
        up = ck.smoothstep(0.0, TURRET_TOP, P[:, 1] - base[1])
        ck.finish(mesh, P, T, "back", ck.mix(ck.mix(BACK, GLASS, 0.4), turret, up[:, None]), rig.rigid(f"eye_{tag}"),
                  wet=0.85, cavity=0.2)
        eye = path[-1] + np.array([s * 0.004, 0.012, 0.0])
        Pe, Te = ck.ellipsoid(eye, (0.024, 0.021, 0.026), 6, 10)
        ck.finish(mesh, Pe, Te, "eye", BLACK, rig.rigid(f"eye_{tag}"), wet=1.0)
        # the black lid round the eye's base, so it reads as an eye on a stalk, not a bead
        a = np.linspace(0.0, 2.0 * math.pi, 11)
        lid = eye + np.column_stack([0.026 * np.cos(a), np.full(11, -0.008), 0.028 * np.sin(a)])
        Pl, Tl = ck.tube(lid, 0.005, 4, cap_start=False, cap_end=False)
        ck.finish(mesh, Pl, Tl, "back", ck.mix(RIM, BLACK, 0.7), rig.rigid(f"eye_{tag}"), wet=0.9, cavity=0.3)
        # the spiracle behind it: a small dark opening, sunk into the back
        sp = np.array([s * SPIRACLE_X, 0.0, SPIRACLE_Z])
        sp[1] = back_y(sp[0], sp[2]) - 0.001
        Ps, Ts = ck.ellipsoid(sp, (0.017, 0.006, 0.022), 4, 8)
        ck.finish(mesh, Ps, Ts, "back", ck.mix(RIM, BLACK, 0.8), disc_skin(rig), wet=1.0, cavity=0.6)


def back_y(x: float, z: float) -> float:
    """The back's height at (x, z) on the rest disc."""
    a = math.atan2(z, x)
    e = outline(np.array([a]))[0]
    r = min(math.hypot(x, z) / max(math.hypot(e[0], e[2]), 1e-6), 1.0)
    return float(top_height(np.array([[x, 0.0, z]]), np.array([r]))[0])


def thorn(mesh: ck.Mesh, at, h: float, rb: float, bones) -> None:
    """A thorn raked back from the surface point `at`: a dark-tipped cone, its base sunk into the skin."""
    x, y, z = at
    path = np.array([(x, y - 0.004, z + 0.006), (x, y + 0.55 * h, z - 0.006), (x, y + h, z - 0.018)])
    P, T = ck.tube(path, np.array([rb, rb * 0.5, 0.0012]), 5, cap_start=False)
    tip = ck.smoothstep(y + 0.2 * h, y + h, P[:, 1])
    ck.finish(mesh, P, T, "back", ck.mix(THORN, BLACK, tip[:, None]), bones, wet=0.9, cavity=0.2 * (1.0 - tip))


def thorns(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The thornback rows: down the midline from behind the eyes to the tail root (stopping short of the split), a
    short row on each shoulder, and on along the tail to the first dorsal fin."""
    skin = disc_skin(rig)
    for k, z in enumerate(np.linspace(0.16, WOUND_Z + 0.07, 10)):
        h = 0.036 - 0.01 * k / 9
        thorn(mesh, (0.0, back_y(0.0, z), z), h, 0.012, skin)
    for s in (1.0, -1.0):
        for z in (0.06, -0.02, -0.1):
            x = s * (0.12 - 0.15 * (0.06 - z))
            thorn(mesh, (x, back_y(x, z), z), 0.018, 0.008, skin)
    tskin = rig.chain([f"tail{k}" for k in range(4)], TAIL)
    path = ck.bezier(list(TAIL), 18)
    rad = np.interp(np.linspace(0.0, 1.0, 18), np.linspace(0.0, 1.0, len(TAIL_R)), TAIL_R)
    for k, z in enumerate(np.linspace(-0.55, -0.9, 6)):
        y = float(np.interp(-z, -path[:, 2], path[:, 1])) + float(np.interp(-z, -path[:, 2], rad)) - 0.002
        thorn(mesh, (0.0, y, z), 0.026 - 0.01 * k / 5, 0.01 - 0.003 * k / 5, tskin)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = ck.bezier(list(TAIL), 18)
    u = np.linspace(0.0, 1.0, 18)
    rad = np.interp(u, np.linspace(0.0, 1.0, len(TAIL_R)), TAIL_R)
    P, T = ck.tube(path, rad, 8, squash=0.7, up_hint=(0.0, 1.0, 0.0))
    skin = rig.chain([f"tail{k}" for k in range(4)], TAIL)
    uu = np.concatenate([np.repeat(u, 8), [0.0, 1.0]])
    under = ck.smoothstep(0.0, -0.02, P[:, 1] - np.interp(-P[:, 2], -path[:, 2], path[:, 1]))
    thorns = np.exp(-(P[:, 0] / 0.01) ** 2) * (0.5 + 0.5 * np.cos(P[:, 2] * 60.0)) ** 8 * (1.0 - under)
    col = ck.mix(ck.mix(BACK, GLASS, (0.3 * uu)[:, None]), BELLY, under[:, None])
    col = ck.mix(col, ck.mix(BACK, BLACK, 0.5), (0.6 * thorns)[:, None])
    ck.finish(mesh, P, T, "back", col, skin, wet=0.85, cavity=0.3 * thorns)
    # two small dorsal fins near the tip: thin, both faces on their own vertices
    for k, (z0, h) in enumerate(((-0.98, 0.05), (-1.12, 0.04))):
        y0 = float(np.interp(-z0, -path[:, 2], path[:, 1])) + float(np.interp(-z0, -path[:, 2], rad)) * 0.6
        tri = np.array([(0.0, y0, z0 + 0.05), (0.0, y0 + h, z0 - 0.03), (0.0, y0, z0 - 0.06)])
        for face, nx in ((np.array([[0, 1, 2]]), 1.0), (np.array([[0, 2, 1]]), -1.0)):
            Pf = tri + np.array([nx * 0.002, 0.0, 0.0])
            N = np.tile([nx, 0.0, 0.0], (3, 1))
            ck.finish(mesh, Pf, face, "back", np.tile(ck.mix(BACK, GLASS, 0.6), (3, 1)), skin, wet=0.85, N=N)


def wound(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The weak point: a short split across the spine where the tail leaves the disc, its lips raised and dark, glowing
    inside."""
    c = np.array([0.0, float(top_height(np.array([[0.0, 0.0, WOUND_Z]]), np.array([0.93]))[0]) + 0.004, WOUND_Z])
    P, T = ck.ellipsoid(c, (0.045, 0.008, 0.011), 5, 10)
    glow = ck.smoothstep(0.0, 0.007, P[:, 1] - c[1])
    ck.finish(mesh, P, T, "back", ck.mix(ck.mix(BACK, BLACK, 0.45), PAL["spawn_wound"] * 0.65, glow[:, None]),
              rig.rigid("body"), wet=1.0, emission=glow, cavity=0.3 * (1.0 - glow))
    for side in (-1.0, 1.0):
        lip = c + np.outer(np.linspace(-1.0, 1.0, 7), np.array([0.045, 0.0, 0.0]))
        lip[:, 2] += side * 0.014 * (1.0 - 0.5 * np.linspace(-1.0, 1.0, 7) ** 2)
        Pl, Tl = ck.tube(lip, 0.005 * np.sin(np.linspace(0.3, math.pi - 0.3, 7)), 5)
        ck.finish(mesh, Pl, Tl, "back", ck.mix(BACK, BLACK, 0.55), rig.rigid("body"), wet=1.0, cavity=0.4)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("glass_skate")
    disc(mesh, rig)
    eyes(mesh, rig)
    thorns(mesh, rig)
    tail(mesh, rig)
    wound(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips (the disc's edges curl about z: + lifts the left edge, - the right)
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 3.2
ATTACK_SEC = 1.2
ATTACK_CONTACT = 0.5
CAST_SEC = 1.6
HIT_SEC = 0.5
KO_SEC = 1.6


def key_disc(clip: ck.Clip, t: float, curl: float, tip: float | None = None, wave: tuple = (0.0, 0.0, 0.0)) -> None:
    """Both sides of the disc: `curl` degrees up at each bone (`tip` for the outer one), plus a per-bone `wave`. Each
    bone turns on its parent, so the edge's angle is the sum down the chain."""
    tip = curl if tip is None else tip
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for k in range(DISC):
            a = (curl if k < DISC - 1 else tip) + wave[k]
            clip.key(f"disc_{tag}{k}", t, (0.0, 0.0, s * a))


def key_tail(clip: ck.Clip, t: float, pitch: float = 0.0, yaw: float = 0.0) -> None:
    for k in range(4):
        clip.key(f"tail{k}", t, (pitch * (0.6 + 0.2 * k), yaw * (0.5 + 0.3 * k), 0.0))


def build_idle() -> ck.Clip:
    """Buried: only the eyes and the breathing back move. The back rises and falls, the margins lift a hair with it,
    and each eye turns on its turret in its own time."""
    idle = ck.Clip("idle", IDLE_SEC, loop=True)
    idle.wave("body", amp_loc=(0.0, 0.005, 0.0), base_loc=(0.0, 0.005, 0.0), cycles=2)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        idle.wave(f"disc_{tag}0", amp_rot=(0.0, 0.0, s * 0.6), base_rot=(0.0, 0.0, s * 0.6), cycles=2, phase=0.4)
    for t, l, r in ((0.0, 0, 0), (0.5, 0, 0), (0.75, 18, 0), (1.4, 18, -6), (1.7, 0, -14), (2.4, -10, -14),
                    (2.7, 0, 0), (IDLE_SEC, 0, 0)):
        idle.key("eye_l", t, (0.0, l, 0.0))
        idle.key("eye_r", t, (0.0, r, 0.0))
    return idle


def build_attack() -> ck.Clip:
    """It erupts from the sand and slaps: the disc presses down, the whole skate heaves up nose-high with its edges
    curling, then comes down on the target, edges whipping down (contact 0.5 s), and settles back."""
    attack = ck.Clip("attack", ATTACK_SEC)
    for t, y, rx, curl, tip, tail in ((0.0, 0.0, 0.0, 0.0, None, 0.0), (0.16, 0.0, 0.0, 2.0, None, 4.0),
                                      (0.36, 0.5, -30.0, 14.0, 20.0, 2.0), (ATTACK_CONTACT, 0.3, 14.0, -8.0, -10.0, 14.0),
                                      (0.66, 0.08, 4.0, 3.0, 2.0, 8.0), (0.85, 0.0, 0.0, 1.0, None, 2.0),
                                      (ATTACK_SEC, 0.0, 0.0, 0.0, None, 0.0)):
        attack.key("root", t, (0.0, 0.0, 0.0), (0.0, y, 0.0))
        attack.key("body", t, (rx, 0.0, 0.0))
        key_disc(attack, t, curl, tip)
        key_tail(attack, t, tail)
        for tag in ("l", "r"):
            attack.key(f"eye_{tag}", t, (-0.6 * rx, 0.0, 0.0))
    return attack


def build_cast() -> ck.Clip:
    """The hide: it settles and stirs a cloud of white sand (the cloud is VFX): a ripple runs out along both edges of
    the disc twice, the body wriggling with it, the tail sweeping, the eyes drawn down."""
    cast = ck.Clip("cast", CAST_SEC)
    n = 16
    for i in range(n + 1):
        t = CAST_SEC * i / n
        env = math.sin(math.pi * t / CAST_SEC)
        w = [env * (4.0 + 2.0 * k) * math.sin(2.0 * math.pi * 2.0 * t / CAST_SEC - k * 1.1) for k in range(DISC)]
        key_disc(cast, t, 7.0 * env, None, tuple(w))
        cast.key("body", t, (0.0, 5.0 * env * math.sin(4.0 * math.pi * t / CAST_SEC), 0.0), (0.0, 0.01 * env, 0.0))
        key_tail(cast, t, 0.0, 22.0 * env * math.sin(2.0 * math.pi * 2.0 * t / CAST_SEC - 1.5))
        for tag in ("l", "r"):
            cast.key(f"eye_{tag}", t, (0.0, 0.0, 0.0), (0.0, -0.02 * env, 0.0))
    return cast


def build_hit(name: str = "hit", side: float = 1.0, amp: float = 1.0) -> ck.Clip:
    """It buckles, peaking at 0.1 s: the disc folds up at both edges, the body kinks and rolls, the tail whips.
    `hit_b` is authored here too (the kit's mirror would curl the edges down into the sand): the roll and the tail
    to the other side, 1.35 times heavier."""
    hit = ck.Clip(name, HIT_SEC)
    for t, s in ((0.0, 0.0), (0.1, amp), (0.24, 0.4 * amp), (HIT_SEC, 0.0)):
        hit.key("root", t, (0.0, 0.0, 0.0), (0.0, 0.09 * s, -0.05 * s))
        hit.key("body", t, (-8.0 * s, 0.0, side * 6.0 * s))
        key_disc(hit, t, 9.0 * s, 12.0 * s)
        key_tail(hit, t, 8.0 * s, side * 16.0 * s)
        for tag in ("l", "r"):
            hit.key(f"eye_{tag}", t, (25.0 * s, 0.0, 0.0))
    return hit


def build_ko() -> ck.Clip:
    """It flattens and lies still: a last shudder lifts its edges, they settle flat on the sand, the tail goes slack
    to one side and the eyes sink on their turrets."""
    ko = ck.Clip("ko", KO_SEC)
    for t, s, shudder in ((0.0, 0.0, 0.0), (0.2, 0.3, 1.0), (0.45, 0.6, 0.3), (0.8, 1.0, 0.0), (KO_SEC, 1.0, 0.0)):
        ko.key("body", t, (-3.0 * shudder, 0.0, 0.0), (0.0, 0.02 * shudder, 0.0))
        key_disc(ko, t, 4.0 * shudder)
        key_tail(ko, t, 3.0 * shudder, 14.0 * s)
        for tag in ("l", "r"):
            ko.key(f"eye_{tag}", t, (40.0 * s, 0.0, 0.0), (0.0, -0.02 * s, 0.0))
    return ko


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_attack(), build_cast(), build_hit(), build_ko(),
            build_hit("hit_b", -1.0, ck.HIT_B["amp"])]


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender)
# ---------------------------------------------------------------------------------------------
def fk(rig: ck.Rig, clip: ck.Clip, t: float) -> dict:
    """Each bone's pose as (R, offset) in rest space: p -> R p + offset (the export's convention)."""
    out: dict = {}
    for b in rig.bones:
        rdeg, loc = clip.sample(b.name, t)
        if b.name == "root" and clip.name in ck.IN_PLACE_CLIPS:
            loc = np.array([0.0, loc[1], 0.0])
        W = ck.euler(*rdeg)
        h = np.asarray(b.head)
        tl = h + loc - W @ h
        if b.parent:
            Rp, tp = out[b.parent]
            out[b.name] = (Rp @ W, Rp @ tl + tp)
        else:
            out[b.name] = (W, tl)
    return out


def skin(rig: ck.Rig, arrays: dict, pose: dict) -> np.ndarray:
    P, J, W = arrays["pos"], arrays["joints"], arrays["weights"]
    Rs = np.stack([pose[b.name][0] for b in rig.bones])
    ts = np.stack([pose[b.name][1] for b in rig.bones])
    out = np.zeros_like(P)
    for k in range(2):
        out += W[:, k:k + 1] * (np.einsum("nij,nj->ni", Rs[J[:, k]], P) + ts[J[:, k]])
    return out


def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    arrays = mesh.arrays()
    rest = arrays["pos"]
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    for c in ck.with_variety(clips):
        frames = max(int(round(c.length * ck.FPS)), 1)
        lo, hi, disp = np.inf, -np.inf, []
        for f in range(frames + 1):
            P = skin(rig, arrays, fk(rig, c, min(f / ck.FPS, c.length)))
            lo, hi = min(lo, float(P[:, 1].min())), max(hi, float(P[:, 1].max()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        P = skin(rig, arrays, fk(rig, c, c.length))
        print(f"{c.name:7s} {c.length:.2f}s: y {lo:+.3f}..{hi:.3f}; at the end y {P[:, 1].min():+.3f}..{P[:, 1].max():.3f};"
              f" peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


def build() -> tuple[ck.Rig, ck.Mesh, list[ck.Clip]]:
    rig = build_rig()
    return rig, build_mesh(rig), build_clips()


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and the clip checks; no export")
    args = ap.parse_args(argv)
    rig, mesh, clips = build()
    if args.report or not args.out:
        report(rig, mesh, clips)
        return
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "glass_skate"})
    print(f"glass_skate: {info}")


if __name__ == "__main__":
    main()
