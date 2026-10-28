"""Ridge lynx, Ch12 Keth Pass (M3-CRE-628): docs/kb/art/creatures/act2/ridge_lynx.md.

blender --background --factory-startup --python assets_src/creatures/ridge_lynx/build_ridge_lynx.py -- \
    --out assets/creatures/ridge_lynx/ridge_lynx.glb

A high-pass lynx in its thick winter coat: ordinary, hungry, beautiful, the first Act II foe that is only an animal in
a hard winter. A long-legged cat 0.75 m at the shoulder, on big snowshoe paws, with a short black-tipped tail, black
ear tufts and a frosted ruff. Its one exaggeration is the pounce: it crouches low (the telegraph) and clears the
front row in one leap. The coat is overcast_slate going cumulus_shadow on the belly, with faint lacquer_black spots;
the eyes dusk_gold; frost on the ruff salt_glass. Its weak point is an old wound on its camera-side flank (-x) where a
herder's sling caught it, small, in spawn_wound.

The legs hang from a `body` carrier (like the Avalanche Ram's), so the spine breathes without lifting a paw, and they
are posed in their own planes by a two-bone solve that keeps each planted paw where it stands, level, while the body
crouches, launches, lands or lies down.

**The battle read (M3-CRE-645).** The first muzzle (an ellipsoid) read short and pug-like at review distance, so the
face is a cat's: a longer wedge muzzle from the brow to a blunt front, a dark nose leather, pale whisker pads with
rows of dark whisker spots and pale whiskers, a dark mouth line, and a longer chin. The ear tufts stay. The head
bone is unchanged (its tail stays at NOSE); the new muzzle reaches past it on the same bone.

Run without Blender (`python3 build_ridge_lynx.py --report`) for the triangle count and each clip's numbers.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 8213
PAL = {k: ck.hexrgb(v) for k, v in {
    "overcast_slate": "#6F7E8E", "cumulus_shadow": "#8FA7C4", "lacquer_black": "#1D1916", "dusk_gold": "#F2A64A",
    "salt_glass": "#BFE6E0", "spawn_wound": "#3FE0C8", "storm_slate": "#3E4A57",
}.items()}
COAT = PAL["overcast_slate"]
BELLY = ck.mix(PAL["cumulus_shadow"], PAL["overcast_slate"], 0.25)
BLACK = PAL["lacquer_black"]
FROST = PAL["salt_glass"] * 0.95
PAD = ck.mix(PAL["storm_slate"], PAL["lacquer_black"], 0.5)

# ---------------------------------------------------------------------------------------------
# Proportions (Godot axes: x right, y up, facing +z; metres; the ground at y 0)
# ---------------------------------------------------------------------------------------------
BODY_PIVOT = np.array([0.0, 0.56, -0.04])  # the body carrier's head: crouch and leap pitch about it
SPINE = np.array([(0, 0.6, -0.38), (0, 0.6, -0.16), (0, 0.59, 0.05), (0, 0.6, 0.24), (0, 0.64, 0.4)])
TORSO_PATH = ((0, 0.6, -0.5), (0, 0.63, -0.22), (0, 0.57, 0.08), (0, 0.585, 0.34), (0, 0.66, 0.5))
TORSO_U = (0.0, 0.08, 0.3, 0.55, 0.78, 0.92, 1.0)
TORSO_R = (0.05, 0.14, 0.15, 0.13, 0.17, 0.145, 0.07)  # rump, haunch, waist, chest, the chest front
TORSO_RINGS, TORSO_SEGS = 30, 22
NECK = np.array([(0, 0.64, 0.4), (0, 0.73, 0.5), (0, 0.8, 0.58)])
HEAD_C = np.array([0.0, 0.84, 0.645])  # the cranium
NOSE = np.array([0.0, 0.822, 0.78])  # the head bone's tail (the rig)
# the wedge muzzle, lofted from inside the cranium to its blunt front: (z, top y, bottom y, half-width) per station
MUZZLE = ((0.668, 0.85, 0.77, 0.058), (0.71, 0.842, 0.771, 0.053), (0.75, 0.834, 0.774, 0.046),
          (0.782, 0.83, 0.777, 0.039), (0.804, 0.827, 0.781, 0.034), (0.816, 0.822, 0.786, 0.028))
MUZZLE_ROUND = 2.6  # the section's superellipse exponent: 2 an oval, higher squarer
NOSE_TIP = np.array([0.0, 0.818, 0.817])  # the nose leather's centre
PAD_AT = (0.017, 0.791, 0.806)  # a whisker pad's centre (x on the left)
PAD_R = (0.02, 0.019, 0.022)  # its radii (kept inside the cheek's width: the KO lays the head on its side)
EYE_AT = (0.042, 0.858, 0.712)
EAR = ((0.054, 0.905, 0.615), (0.07, 1.0, 0.595))  # an ear's base and tip (x on the left)
TUFT_LEN = 0.06
TAIL = np.array([(0, 0.68, -0.47), (0, 0.64, -0.54), (0, 0.58, -0.6), (0, 0.52, -0.63)])
LEG_X = {"fl": 0.11, "fr": -0.11, "bl": 0.12, "br": -0.12}
# joints in the leg's plane, (y, z): the top (shoulder or hip), the elbow or stifle, the wrist or hock, the toe
FRONT_YZ = ((0.5, 0.28), (0.28, 0.22), (0.085, 0.27), (0.035, 0.38))
HIND_YZ = ((0.53, -0.36), (0.33, -0.22), (0.15, -0.42), (0.035, -0.3))
LEGS = ("fl", "fr", "bl", "br")
PAW_R = (0.068, 0.04, 0.088)  # the snowshoe pad's radii
WOUND = np.array([-0.125, 0.6, -0.08])  # the old sling wound on the camera-side flank
FUR = 0.016  # the coat's depth, pushed out in tufts


def leg_joints(name: str) -> np.ndarray:
    yz = FRONT_YZ if name[0] == "f" else HIND_YZ
    return np.array([(LEG_X[name], y, z) for y, z in yz])


def pad_centre(name: str) -> np.ndarray:
    j = leg_joints(name)
    return np.array([j[3][0], PAW_R[1], j[3][2] - 0.035])


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.25, 0))
    rig.add("body", BODY_PIVOT, BODY_PIVOT + np.array([0.0, 0.2, 0.0]), "root")
    for k in range(4):
        rig.add(f"spine{k}", SPINE[k], SPINE[k + 1], "body" if k == 0 else f"spine{k - 1}")
    rig.add("neck0", NECK[0], NECK[1], "spine3")
    rig.add("neck1", NECK[1], NECK[2], "neck0")
    rig.add("head", NECK[2], NOSE, "neck1")
    rig.add("jaw", (0, 0.785, 0.66), (0, 0.765, 0.77), "head")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"ear_{tag}", (s * EAR[0][0], EAR[0][1], EAR[0][2]), (s * EAR[1][0], EAR[1][1], EAR[1][2]), "head")
    for k in range(3):
        rig.add(f"tail{k}", TAIL[k], TAIL[k + 1], "spine0" if k == 0 else f"tail{k - 1}")
    for name in LEGS:  # the legs hang from the body, so the spine can move without lifting a paw
        j = leg_joints(name)
        rig.add(f"{name}_upper", j[0], j[1], "body")
        rig.add(f"{name}_lower", j[1], j[2], f"{name}_upper")
        rig.add(f"{name}_paw", j[2], j[3], f"{name}_lower")
    return rig


# ---------------------------------------------------------------------------------------------
# Coat
# ---------------------------------------------------------------------------------------------
def tufted(P: np.ndarray, T: np.ndarray, depth, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """The coat pushed out in clumps along the normals; returns the moved points and the clump (0..1)."""
    clump = ck.smoothstep(-0.3, 0.7, ck.value_noise(P * 42.0, seed)) * (0.7 + 0.3 * ck.fbm(P * 9.0, seed + 1))
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    depth = np.broadcast_to(np.asarray(depth, dtype=np.float64), (len(P),))
    return P + N * (depth * (0.35 + 0.65 * clump))[:, None], clump


def coat_colour(P: np.ndarray, under: np.ndarray, clump: np.ndarray, seed: int) -> np.ndarray:
    """Slate going to the pale belly, faint black spots, the clumps' tips a little lighter."""
    col = ck.mix(COAT, BELLY, under[:, None])
    col = col * (0.9 + 0.12 * clump + 0.08 * ck.fbm(P * 5.0, seed))[:, None]
    spots = ck.smoothstep(0.32, 0.5, ck.value_noise(P * np.array([16.0, 16.0, 11.0]), seed + 2))
    spots = spots * (1.0 - under) * 0.3  # faint, and not on the belly
    return np.maximum(ck.mix(col, BLACK, spots[:, None]), BLACK)


def torso(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = ck.bezier(TORSO_PATH, TORSO_RINGS)
    u = np.linspace(0.0, 1.0, TORSO_RINGS)
    rad = np.interp(u, TORSO_U, TORSO_R)
    P, T = ck.tube(path, rad, TORSO_SEGS, squash=0.74, up_hint=(0.0, 1.0, 0.0))  # deep and narrow
    cy = np.interp(P[:, 2], path[:, 2], path[:, 1])
    below = P[:, 1] < cy
    keel = 0.05 * ck.smoothstep(0.5, 0.85, np.interp(P[:, 2], path[:, 2], u))  # the deep chest
    P[:, 1] -= below * keel * ck.smoothstep(0.0, -0.1, P[:, 1] - cy)
    under = ck.smoothstep(cy - 0.02, cy - 0.13, P[:, 1])
    P, clump = tufted(P, T, FUR * (1.0 + 0.6 * ck.smoothstep(cy, cy + 0.1, P[:, 1])), SEED + 10)
    col = coat_colour(P, under, clump, SEED + 11)
    # the old sling wound: a short ridged scar on the flank, its parting glowing (centred on the coat's surface
    # nearest WOUND's height and length, on its side)
    side = np.where(P[:, 0] * np.sign(WOUND[0]) > 0.0, 0.0, 1e3)
    at = P[int(np.argmin((P[:, 1] - WOUND[1]) ** 2 + (P[:, 2] - WOUND[2]) ** 2 + side))]
    d = (P - at) / np.array([0.05, 0.045, 0.095])
    scar = np.exp(-(d ** 2).sum(axis=1))
    slit = ck.smoothstep(0.45, 0.8, scar)
    lip = ck.smoothstep(0.15, 0.5, scar) * (1.0 - slit)
    col = ck.mix(col, ck.mix(COAT, BLACK, 0.5), lip[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.6, slit[:, None])
    skin = rig.chain([f"spine{k}" for k in range(4)], SPINE)
    ck.finish(mesh, P, T, "coat", col, skin, cavity=0.25 * (1.0 - clump) + 0.5 * lip, emission=slit)
    # the parting itself: a narrow slit along the body with raised dark lips, glowing inside (the weak point)
    n = ck.weld_normals(P, ck.vertex_normals(P, T))[int(np.argmin(np.linalg.norm(P - at, axis=1)))]
    c = at - n * 0.004
    Ps, Ts = ck.ellipsoid(c, (0.009, 0.013, 0.065), 6, 12)
    Ps = c + (Ps - c) @ np.array([[1.0, 0.0, 0.0], [0.0, math.cos(0.25), -math.sin(0.25)],
                                  [0.0, math.sin(0.25), math.cos(0.25)]]).T  # a little aslant, as the stone struck
    glow = ck.smoothstep(0.3, 0.9, ((Ps - c) @ n) / 0.009)  # the ridge facing out
    ck.finish(mesh, Ps, Ts, "coat", ck.mix(ck.mix(COAT, BLACK, 0.5), PAL["spawn_wound"] * 0.65, glow[:, None]), skin,
              emission=glow, cavity=0.3 * (1.0 - glow))
    for side in (-1.0, 1.0):
        up = np.array([0.0, math.cos(0.25), math.sin(0.25)]) * side * 0.016
        lip_path = c + n * 0.004 + up + np.outer(np.linspace(-1.0, 1.0, 7), np.array([0.0, -math.sin(0.25),
                                                                                      math.cos(0.25)]) * 0.06)
        lip_path = lip_path - np.outer(np.linspace(-1.0, 1.0, 7) ** 2, up) * 0.6
        Pl, Tl = ck.tube(lip_path, 0.006 * np.sin(np.linspace(0.3, math.pi - 0.3, 7)), 5)
        ck.finish(mesh, Pl, Tl, "coat", ck.mix(COAT, BLACK, 0.6), skin, cavity=0.4)


def neck_and_ruff(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = ck.bezier([NECK[0] + np.array([0, -0.02, -0.06]), NECK[1], NECK[2] + np.array([0, 0.0, 0.03])], 10)
    P, T = ck.tube(path, np.linspace(0.12, 0.09, 10), 16, squash=0.85, up_hint=(0.0, 1.0, 0.0))
    under = ck.smoothstep(0.02, -0.06, P[:, 1] - np.interp(P[:, 2], path[:, 2], path[:, 1]))
    P, clump = tufted(P, T, FUR * 1.3, SEED + 20)
    skin = rig.chain(["spine3", "neck0", "neck1"], [SPINE[3], NECK[0], NECK[1], NECK[2]])
    ck.finish(mesh, P, T, "coat", coat_colour(P, under, clump, SEED + 21), skin, cavity=0.25 * (1.0 - clump))
    # the ruff: a flared collar of fur round the cheeks and throat, its points swept back and frosted
    n_ang, n_row = 30, 4
    ang = np.linspace(-0.92 * math.pi, 0.92 * math.pi, n_ang)  # open at the top of the head
    centre = np.array([0.0, 0.81, 0.655])
    rows = []
    for r in range(n_row):
        t = r / (n_row - 1)
        jag = 1.0 + (0.35 * t) * np.where(np.arange(n_ang) % 2 == 0, 1.0, 0.25)
        rad = (0.075 + 0.075 * t * jag)[:, None] * np.array([1.0, 1.08])[None, :]
        back = -0.01 - 0.06 * t * jag
        rows.append(centre + np.column_stack([np.sin(ang) * rad[:, 0], -np.cos(ang) * rad[:, 1], np.full(n_ang, back)]))
    P = np.vstack(rows)
    T = ck.grid_tris(n_row, n_ang, False)
    tip = np.repeat(np.linspace(0.0, 1.0, n_row), n_ang)
    col = ck.mix(ck.mix(BELLY, COAT, 0.3), FROST, ck.smoothstep(0.55, 1.0, tip)[:, None])
    N = np.tile(np.array([0.0, 0.0, 1.0]), (len(P), 1))
    radial = P - centre
    radial[:, 2] = 0.0
    N = radial / np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9) * 0.7 + N * 0.3
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    ck.finish(mesh, P, T, "coat", col, rig.rigid("head"), cavity=0.3 * (1.0 - tip), wet=0.0, N=N)
    # its other face (its own vertices, so the export keeps both faces of the thin collar)
    ck.finish(mesh, P - N * 0.002, ck.flip(T), "coat", col, rig.rigid("head"), cavity=0.3 * (1.0 - tip), wet=0.0, N=-N)


def head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    hb = rig.rigid("head")
    P, T = ck.ellipsoid(HEAD_C, (0.088, 0.078, 0.092), 10, 16)
    under = ck.smoothstep(HEAD_C[1] - 0.01, HEAD_C[1] - 0.07, P[:, 1])
    P, clump = tufted(P, T, FUR * 0.6, SEED + 30)
    col = coat_colour(P, under, clump, SEED + 31)
    # dark lines from the eyes back over the cheeks (a lynx's facial streaks), faint
    streak = np.exp(-((np.abs(P[:, 0]) - 0.06) / 0.012) ** 2 - ((P[:, 1] - 0.83) / 0.01) ** 2) * (P[:, 2] < 0.7)
    col = ck.mix(col, BLACK, (0.45 * streak)[:, None])
    ck.finish(mesh, P, T, "coat", col, hb, cavity=0.2 * (1.0 - clump))
    muzzle(mesh, hb)
    for s in (-1.0, 1.0):
        c = np.array([s * EYE_AT[0], EYE_AT[1], EYE_AT[2]])
        Pe, Te = ck.ellipsoid(c, (0.016, 0.013, 0.012), 6, 8)
        ck.finish(mesh, Pe, Te, "eye", PAL["dusk_gold"], hb, wet=1.0)
        Pp, Tp = ck.ellipsoid(c + np.array([0.0, 0.0, 0.009]), (0.0035, 0.009, 0.004), 4, 6)
        ck.finish(mesh, Pp, Tp, "eye", BLACK, hb, wet=1.0)
        # the black eye-line round each eye
        Pl, Tl = ck.ellipsoid(c + np.array([0.0, 0.0, -0.003]), (0.02, 0.016, 0.011), 6, 8)
        ck.finish(mesh, Pl, Tl, "coat", BLACK, hb, cavity=0.3)
    jb = rig.bones[rig.index("jaw")]
    h0, h1 = np.asarray(jb.head), np.asarray(jb.tail)
    chin = h1 + np.array([0.0, 0.004, 0.024])  # the chin reaches under the whisker pads
    Pj, Tj = ck.tube(np.array([h0, (h0 + h1) / 2, h1, chin]), np.array([0.035, 0.03, 0.022, 0.012]), 8, squash=0.7,
                     up_hint=(1.0, 0.0, 0.0))
    ck.finish(mesh, Pj, Tj, "coat", ck.mix(BELLY, PAL["salt_glass"] * 0.8, 0.3), rig.rigid("jaw"), cavity=0.2)


def muzzle(mesh: ck.Mesh, hb: int) -> None:
    """The wedge muzzle on the head bone: a lofted superellipse section narrowing to a blunt front, coat on top and
    pale below; the nose leather, the whisker pads with their dark spots and pale whiskers, and the mouth line."""
    segs = 12
    th = np.arange(segs) * (2.0 * math.pi / segs)
    ex = 2.0 / MUZZLE_ROUND
    cx, cy = np.sign(np.cos(th)) * np.abs(np.cos(th)) ** ex, np.sign(np.sin(th)) * np.abs(np.sin(th)) ** ex
    rings = []
    for z, top, bot, w in MUZZLE:
        rings.append(np.column_stack([w * cx, (top + bot) / 2 + (top - bot) / 2 * cy, np.full(segs, z)]))
    P = np.vstack(rings + [np.array([[0.0, (MUZZLE[-1][1] + MUZZLE[-1][2]) / 2, MUZZLE[-1][0] + 0.006]])])
    T = ck.grid_tris(len(MUZZLE), segs, True)
    r0 = (len(MUZZLE) - 1) * segs
    T = np.vstack([T, [(r0 + k, r0 + (k + 1) % segs, len(P) - 1) for k in range(segs)]])
    axis_y = np.interp(P[:, 2], [m[0] for m in MUZZLE], [(m[1] + m[2]) / 2 for m in MUZZLE])
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    out = P[T].mean(axis=1) - np.column_stack([np.zeros(len(T)), axis_y[T].mean(axis=1), P[T].mean(axis=1)[:, 2]])
    out[-segs:] = (0.0, 0.0, 1.0)  # the front cap faces forward
    T = np.where(((fn * out).sum(axis=1) < 0)[:, None], T[:, ::-1], T)
    pale = ck.smoothstep(axis_y + 0.004, axis_y - 0.018, P[:, 1])
    col = ck.mix(COAT, ck.mix(BELLY, PAL["salt_glass"] * 0.8, 0.4), pale[:, None])
    col = col * (0.95 + 0.06 * ck.fbm(P * 40.0, SEED + 32))[:, None]
    ck.finish(mesh, P, T, "coat", col, hb, cavity=0.15)
    # the nose leather: a rounded triangle, broad at the top, on the muzzle's front
    Pn, Tn = ck.ellipsoid(NOSE_TIP, (0.02, 0.012, 0.011), 5, 8)
    Pn[:, 0] *= 0.55 + 0.45 * ck.smoothstep(NOSE_TIP[1] - 0.012, NOSE_TIP[1] + 0.008, Pn[:, 1])
    ck.finish(mesh, Pn, Tn, "coat", ck.mix(PAD, BLACK, 0.4), hb, wet=0.7, cavity=0.2)
    # the whisker pads, pale and full, with three rows of dark whisker spots and the whiskers themselves
    whisk = PAL["salt_glass"] * 0.95
    for sx in (1.0, -1.0):
        c = np.array([sx * PAD_AT[0], PAD_AT[1], PAD_AT[2]])
        Pp, Tp = ck.ellipsoid(c, PAD_R, 5, 8)
        q = (Pp - c) / np.array(PAD_R)
        spots = ((np.sin(q[:, 1] * 7.0) > 0.55) & (np.abs(q[:, 0]) > 0.45) & (q[:, 2] > -0.2)).astype(np.float64)
        cp = ck.mix(ck.mix(BELLY, PAL["salt_glass"] * 0.9, 0.75), BLACK, (0.6 * spots)[:, None])
        ck.finish(mesh, Pp, Tp, "coat", cp, hb, cavity=0.1)
        for k in range(4):
            root = c + np.array([sx * 0.02, 0.008 - 0.007 * k, -0.002 - 0.003 * k])
            fan = math.radians(12.0 - 10.0 * k)
            d = np.array([sx * math.cos(fan) * 0.5, math.sin(fan) * 0.5 - 0.05, -0.8])  # swept back along the cheek
            d /= np.linalg.norm(d)
            length = 0.075 - 0.008 * k
            path = np.array([root, root + d * length * 0.5 + np.array([0, 0.004, 0]), root + d * length])
            Pw, Tw = ck.tube(path, np.array([0.0016, 0.0011, 0.0005]), 3, cap_start=False)
            ck.finish(mesh, Pw, Tw, "coat", whisk, hb, cavity=0.0)
    # the mouth line: down from the nose between the pads, and back under each pad
    mouth = np.array([(0.036, 0.774, 0.78), (0.022, 0.772, 0.797), (0.006, 0.777, 0.814), (0.0, 0.785, 0.819),
                      (0.0, 0.806, 0.82)])
    for sx in (1.0, -1.0):
        Pm, Tm = ck.tube(mouth * np.array([sx, 1.0, 1.0]), 0.0028, 4)
        ck.finish(mesh, Pm, Tm, "coat", BLACK, hb, cavity=0.5)


def ears(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        b = rig.bones[rig.index(f"ear_{tag}")]
        h0, h1 = np.asarray(b.head), np.asarray(b.tail)
        path = ck.bezier([h0, (h0 + h1) / 2 + np.array([s * 0.004, 0.0, 0.006]), h1], 6)
        P, T = ck.tube(path, np.linspace(0.036, 0.006, 6), 8, squash=0.42, up_hint=(0.0, 0.0, 1.0))
        back = ck.smoothstep(0.0, -0.01, P[:, 2] - np.interp(P[:, 1], path[:, 1], path[:, 2]))  # the ear's back
        tipdark = ck.smoothstep(0.55, 0.95, (P[:, 1] - h0[1]) / (h1[1] - h0[1]))
        col = ck.mix(COAT, BLACK, np.maximum(tipdark, 0.5 * back)[:, None])
        ck.finish(mesh, P, T, "coat", col, rig.rigid(f"ear_{tag}"), cavity=0.2)
        # the tuft: a black brush standing off the tip
        tpath = ck.bezier([h1 - np.array([0, 0.008, 0]), h1 + np.array([s * 0.004, TUFT_LEN * 0.6, -0.004]),
                           h1 + np.array([s * 0.01, TUFT_LEN, -0.012])], 5)
        Pt, Tt = ck.tube(tpath, np.linspace(0.008, 0.0015, 5), 5)
        ck.finish(mesh, Pt, Tt, "coat", BLACK, rig.rigid(f"ear_{tag}"), cavity=0.1)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = ck.bezier([TAIL[0], TAIL[1], TAIL[2], TAIL[3] + np.array([0, -0.02, -0.01])], 12)
    P, T = ck.tube(path, np.interp(np.linspace(0, 1, 12), [0, 0.3, 0.85, 1], [0.045, 0.042, 0.035, 0.02]), 10)
    u = np.repeat(np.linspace(0, 1, 12), 10)
    u = np.concatenate([u, [0.0, 1.0]])
    P, clump = tufted(P, T, FUR * 0.8, SEED + 40)
    col = coat_colour(P, np.zeros(len(P)), clump, SEED + 41)
    col = ck.mix(col, BLACK, ck.smoothstep(0.72, 0.85, u)[:, None])  # the black tip
    ck.finish(mesh, P, T, "coat", col, rig.chain(["tail0", "tail1", "tail2"], TAIL), cavity=0.2 * (1.0 - clump))


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for name in LEGS:
        j = leg_joints(name)
        pc = pad_centre(name)
        pad_top = pc + np.array([0.0, PAW_R[1] * 0.7, 0.01])
        pts = [j[0], j[1], j[2], pad_top]
        per = 6
        path = np.vstack([np.linspace(pts[k], pts[k + 1], per, endpoint=(k == 2)) for k in range(3)])
        u = np.linspace(0.0, 1.0, len(path))
        front = name[0] == "f"
        rad = np.interp(u, [0.0, 0.3, 0.42, 0.62, 0.72, 1.0],
                        [0.068, 0.05, 0.04, 0.034, 0.038, 0.05] if front else [0.078, 0.058, 0.04, 0.033, 0.036, 0.05])
        P, T = ck.tube(path, rad, 10, cap_start=True, cap_end=False)
        P, clump = tufted(P, T, FUR * (0.6 + 0.6 * ck.smoothstep(0.35, 0.12, P[:, 1])), SEED + 50 + LEGS.index(name))
        inner = ck.smoothstep(0.02, -0.04, (P[:, 0] - j[0][0]) * np.sign(j[0][0]))
        under = np.maximum(inner * 0.6, ck.smoothstep(0.3, 0.1, P[:, 1]) * 0.5)
        col = coat_colour(P, under, clump, SEED + 60 + LEGS.index(name))
        skin = rig.chain([f"{name}_upper", f"{name}_lower", f"{name}_paw"], j[:3].tolist() + [pad_top])
        ck.finish(mesh, P, T, "coat", col, skin, cavity=0.2 * (1.0 - clump))
        # the snowshoe pad: broad and furred, the sole flat on the ground, four toes at its front
        Pp, Tp = ck.ellipsoid(pc, PAW_R, 8, 14)
        Pp[:, 1] = np.maximum(Pp[:, 1], 0.0)  # the sole flat on the ground
        sole = ck.smoothstep(0.008, 0.0, Pp[:, 1])
        cp = ck.mix(ck.mix(BELLY, COAT, 0.4), PAD, sole[:, None])
        ck.finish(mesh, Pp, Tp, "coat", cp, rig.rigid(f"{name}_paw"), cavity=0.2 * sole)
        for k in range(4):
            a = (k - 1.5) * 0.42
            c = pc + np.array([math.sin(a) * PAW_R[0] * 0.78, -0.006, math.cos(a) * PAW_R[2] * 0.82])
            Pt, Tt = ck.ellipsoid(c, (0.022, 0.026, 0.026), 4, 6)
            Pt[:, 1] = np.maximum(Pt[:, 1], 0.0)
            ck.finish(mesh, Pt, Tt, "coat", ck.mix(BELLY, COAT, 0.5), rig.rigid(f"{name}_paw"), cavity=0.2)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("ridge_lynx")
    torso(mesh, rig)
    neck_and_ruff(mesh, rig)
    head(mesh, rig)
    ears(mesh, rig)
    tail(mesh, rig)
    legs(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Poses: each leg solved in its own plane (two bones to the wrist or hock; the paw kept level)
# ---------------------------------------------------------------------------------------------
def _rot2(v, deg: float) -> np.ndarray:
    """(y, z) turned as ck.rot_x turns it (positive turns +y toward +z)."""
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


def _ang(v) -> float:
    return math.degrees(math.atan2(v[1], v[0]))


def _wrap(deg: float) -> float:
    """An angle in [-180, 180), so a scaled or blended pose turns the short way."""
    return (deg + 180.0) % 360.0 - 180.0


def _cross(a, b) -> float:
    return float(a[0] * b[1] - a[1] * b[0])


def top_joint(name: str, body: tuple, lift: float = 0.0, advance: float = 0.0) -> np.ndarray:
    """The leg's top joint (y, z) under a body pose (rx, (dy, dz)) about BODY_PIVOT and the root's (lift, advance)."""
    rx, off = body
    piv = BODY_PIVOT[1:]
    return piv + _rot2(leg_joints(name)[0, 1:] - piv, rx) + np.asarray(off) + np.array([lift, advance])


def solve(name: str, body: tuple, target, lift: float = 0.0, advance: float = 0.0, paw: float | None = None) -> tuple:
    """(upper, lower, paw) degrees putting the wrist (or hock) at `target` (y, z), the knee bending the way it does
    at rest; the paw keeps its rest angle (level) unless `paw` gives its absolute turn from rest."""
    j = leg_joints(name)[:, 1:]
    u, v = j[1] - j[0], j[2] - j[1]
    l1, l2 = float(np.linalg.norm(u)), float(np.linalg.norm(v))
    j0 = top_joint(name, body, lift, advance)
    d = np.asarray(target, dtype=np.float64) - j0
    dist = float(np.clip(np.linalg.norm(d), abs(l1 - l2) + 1e-4, l1 + l2 - 1e-4))
    alpha = math.degrees(math.acos(np.clip((l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist), -1.0, 1.0)))
    side = math.copysign(1.0, _cross(j[2] - j[0], j[1] - j[0]))
    best = None
    for sgn in (1.0, -1.0):
        psi1 = _ang(d) + sgn * alpha
        knee = j0 + l1 * np.array([math.cos(math.radians(psi1)), math.sin(math.radians(psi1))])
        if math.copysign(1.0, _cross(d, knee - j0)) == side:
            best = (psi1, knee)
    psi1, knee = best
    tip = j0 + d / max(float(np.linalg.norm(d)), 1e-9) * dist
    a1 = psi1 - _ang(u)
    a2 = _ang(tip - knee) - _ang(v)
    rx = body[0]
    upper = _wrap(a1 - rx)
    lower = _wrap(a2 - a1)
    paw_deg = _wrap(-a2 if paw is None else paw - a2)
    return (upper, lower, paw_deg)


def rest_wrist(name: str) -> np.ndarray:
    return leg_joints(name)[2, 1:]


def key_leg(clip: ck.Clip, name: str, t: float, abc) -> None:
    for seg, deg in zip(("upper", "lower", "paw"), abc):
        clip.key(f"{name}_{seg}", t, (float(deg), 0.0, 0.0))


def frame_times(length: float) -> list[float]:
    return [min(f / ck.FPS, length) for f in range(int(round(length * ck.FPS)) + 1)]


def track(length: float, keys) -> list:
    """Per frame, the eased value of `keys` [(t, value tuple)] (as a clip eases between keys)."""
    c = ck.Clip("_t", length)
    for t, val in keys:
        v = list(val) + [0.0] * (6 - len(val))
        c.key("x", t, tuple(v[:3]), tuple(v[3:6]))
    out = []
    for t in frame_times(length):
        r, loc = c.sample("x", t)
        out.append((t, np.concatenate([r, loc])))
    return out


def key_head(clip: ck.Clip, t: float, neck=(0.0, 0.0), head: float = 0.0, jaw: float = 0.0, ears: float = 0.0,
             yaw=(0.0, 0.0, 0.0)) -> None:
    """Neck bones pitched (+ nose down), the head, the jaw (+ opens) and the ears (- laid back); `yaw` turns the two
    neck bones and the head sideways."""
    clip.key("neck0", t, (neck[0], yaw[0], 0.0))
    clip.key("neck1", t, (neck[1], yaw[1], 0.0))
    clip.key("head", t, (head, yaw[2], 0.0))
    clip.key("jaw", t, (jaw, 0.0, 0.0))
    clip.key("ear_l", t, (ears, 0.0, 0.0))
    clip.key("ear_r", t, (ears, 0.0, 0.0))


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 3.0
ATTACK_SEC = 1.4
ATTACK_CONTACT = 0.7
CAST_SEC = 1.6
HIT_SEC = 0.5
KO_SEC = 3.0
CROUCH = (7.0, (-0.15, -0.05))  # the telegraph: low, its weight back over the haunches, nose down a little
AIR = {  # the legs in the leap: (upper, lower, paw) at the apex and at the strike
    "apex": {"f": (-62.0, -18.0, -20.0), "b": (58.0, 25.0, 30.0)},
    "strike": {"f": (-92.0, -6.0, -35.0), "b": (-14.0, 52.0, -10.0)},
}


def build_idle() -> ck.Clip:
    """Standing watch: a breath (the steam is VFX), the tail flicks, an ear turns, then the other."""
    idle = ck.Clip("idle", IDLE_SEC, loop=True)
    idle.wave("spine2", amp_rot=(0.8, 0.0, 0.0), amp_loc=(0.0, 0.006, 0.0), cycles=2)
    idle.wave("spine3", amp_rot=(-1.0, 0.0, 0.0), cycles=2, phase=0.5)
    idle.wave("neck1", amp_rot=(1.5, 4.0, 0.0), cycles=1)
    idle.wave("tail0", amp_rot=(0.0, 6.0, 0.0), cycles=1, phase=0.6)
    for t, flick in ((0.0, 0.0), (1.5, 0.0), (1.7, 1.0), (1.85, -0.6), (2.05, 0.4), (2.3, 0.0), (IDLE_SEC, 0.0)):
        idle.key("tail1", t, (-14.0 * abs(flick), 18.0 * flick, 0.0))
        idle.key("tail2", t, (-10.0 * abs(flick), 26.0 * flick, 0.0))
    for t, el, er in ((0.0, 0.0, 0.0), (0.6, 0.0, 0.0), (0.8, 1.0, 0.0), (1.3, 1.0, 0.0), (1.5, 0.0, 0.0),
                      (2.1, 0.0, 0.0), (2.3, 0.0, 1.0), (2.7, 0.0, 1.0), (IDLE_SEC, 0.0, 0.0)):
        idle.key("ear_l", t, (-8.0 * el, 28.0 * el, 0.0))
        idle.key("ear_r", t, (-8.0 * er, -28.0 * er, 0.0))
    return idle


def build_attack() -> ck.Clip:
    """The pounce: the crouch (the telegraph), the leap over the front row and the strike as it comes down on the back
    row (contact 0.7 s), forepaws raking; it lands in a crouch and straightens. In place: the leap's arc is the
    root's height; the sequencer carries it across."""
    attack = ck.Clip("attack", ATTACK_SEC)
    body = track(ATTACK_SEC, ((0.0, (0.0,)), (0.38, (CROUCH[0], 0.0, 0.0, 0.0, *CROUCH[1])), (0.47, (CROUCH[0],)),
                              (0.56, (-14.0,)), (0.64, (-6.0,)), (ATTACK_CONTACT, (16.0,)), (0.84, (6.0, 0, 0, 0, -0.1, 0.02)),
                              (1.05, (2.0, 0, 0, 0, -0.03, 0.0)), (ATTACK_SEC, (0.0,))))
    lift = track(ATTACK_SEC, ((0.0, (0, 0, 0, 0.0)), (0.47, (0, 0, 0, 0.0)), (0.6, (0, 0, 0, 0.64)),
                              (ATTACK_CONTACT, (0, 0, 0, 0.36)), (0.84, (0, 0, 0, 0.0)), (ATTACK_SEC, (0, 0, 0, 0.0))))
    for (t, b), (_t, lf) in zip(body, lift):
        pose = (float(b[0]), (float(b[4]), float(b[5])))
        attack.key("body", t, (pose[0], 0.0, 0.0), (0.0, pose[1][0], pose[1][1]))
        attack.key("root", t, (0.0, 0.0, 0.0), (0.0, float(lf[3]), 0.0))
        # the legs: planted on the ground, posed in the air, blended across take-off and landing
        air = float(ck.smoothstep(0.44, 0.53, t) * (1.0 - ck.smoothstep(0.74, 0.84, t)))
        strike = float(ck.smoothstep(0.6, ATTACK_CONTACT, t))
        for name in LEGS:
            ground = np.asarray(solve(name, pose, rest_wrist(name), lift=float(lf[3])))
            fb = name[0]
            flying = ck.mix(np.asarray(AIR["apex"][fb]), np.asarray(AIR["strike"][fb]), strike)
            key_leg(attack, name, t, ck.mix(ground, flying, air))
    for t, neck, head, jaw, ears in ((0.0, (0, 0), 0, 0, 0), (0.38, (14, 4), -16, 0, -35), (0.47, (14, 4), -16, 4, -40),
                                     (0.6, (-6, -4), 4, 10, -45), (ATTACK_CONTACT, (10, 8), -4, 30, -45),
                                     (0.84, (8, 4), -8, 12, -30), (ATTACK_SEC, (0, 0), 0, 0, 0)):
        key_head(attack, t, neck, head, jaw, ears)
    for t, a, b in ((0.0, 0, 0), (0.38, 8, 6), (0.56, -28, -12), (ATTACK_CONTACT, -18, 10), (0.9, 6, 4),
                    (ATTACK_SEC, 0, 0)):
        attack.key("tail0", t, (a, 0.0, 0.0))
        attack.key("tail1", t, (b, 0.0, 0.0))
    for t, s in ((0.0, 0.0), (0.38, 1.0), (0.56, -0.8), (ATTACK_CONTACT, 0.6), (0.9, 0.2), (ATTACK_SEC, 0.0)):
        attack.key("spine1", t, (-3.0 * s, 0.0, 0.0))  # the back arches in the crouch, stretches in the leap
        attack.key("spine2", t, (-4.0 * s, 0.0, 0.0))
    return attack


def build_cast() -> ck.Clip:
    """The yowl that shakes the snow off the rocks: it braces back, lifts its head and opens its jaw wide, ears laid
    flat, the tail lashing."""
    cast = ck.Clip("cast", CAST_SEC)
    body = track(CAST_SEC, ((0.0, (0.0,)), (0.45, (-5.0, 0, 0, 0, -0.04, -0.05)), (1.15, (-6.0, 0, 0, 0, -0.05, -0.05)),
                            (CAST_SEC, (0.0,))))
    for t, b in body:
        pose = (float(b[0]), (float(b[4]), float(b[5])))
        cast.key("body", t, (pose[0], 0.0, 0.0), (0.0, pose[1][0], pose[1][1]))
        for name in LEGS:
            key_leg(cast, name, t, solve(name, pose, rest_wrist(name)))
    for t, s, jaw in ((0.0, 0.0, 0.0), (0.45, 0.7, 10.0), (0.75, 1.0, 34.0), (1.15, 0.95, 30.0), (CAST_SEC, 0.0, 0.0)):
        key_head(cast, t, (-22.0 * s, -12.0 * s), -24.0 * s, jaw, -42.0 * s)
    for t, y in ((0.0, 0), (0.4, 20), (0.7, -24), (1.0, 22), (1.3, -12), (CAST_SEC, 0)):
        cast.key("tail0", t, (-6.0 if 0 < t < CAST_SEC else 0.0, y * 0.5, 0.0))
        cast.key("tail1", t, (0.0, y, 0.0))
    return cast


def build_hit() -> ck.Clip:
    """It twists aside from the blow, peaking at 0.1 s: the body turns and slides off the line, the spine bends away,
    the head whips round, ears back. The body only turns about the vertical and slides, so the paws stay on the
    ground."""
    hit = ck.Clip("hit", HIT_SEC)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.24, 0.5), (0.38, 0.15), (HIT_SEC, 0.0)):
        hit.key("body", t, (0.0, 16.0 * s, 0.0), (0.07 * s, 0.0, -0.04 * s))
        hit.key("spine1", t, (0.0, -6.0 * s, 0.0))
        hit.key("spine2", t, (0.0, -8.0 * s, 0.0))
        hit.key("spine3", t, (0.0, -6.0 * s, 0.0))
        key_head(hit, t, (-8.0 * s, -4.0 * s), 6.0 * s, 14.0 * s, -40.0 * s, yaw=(-12.0 * s, -10.0 * s, -8.0 * s))
        hit.key("tail0", t, (-10.0 * s, 20.0 * s, 0.0))
    return hit


KO_STEP = ((0.05, 0.45, ("fl", "br")), (0.5, 0.95, ("fr", "bl")))  # the two limping steps: start, end, legs
KO_STRIDE = 0.12  # each step carries the root this far; a stepping leg moves twice it
KO_SAG = (1.0, 1.45)  # it sags, its legs giving
SAG = (3.0, (-0.12, 0.0))
KO_ROLL = (1.45, 2.4)  # then it lies down on its side in the snow (its left side: the old wound stays toward us)
ROLL_DEG = -84.0
ROLL_PIVOT_X = 0.185  # the flank it rolls onto: the torso's half-width with its coat and the legs under it
RELAXED = {"f": (-24.0, 18.0, -14.0), "b": (20.0, -12.0, -6.0)}  # the legs lying loose, a little bent


def build_ko() -> ck.Clip:
    """It limps two steps (the second dips onto the stiff fore), sags as its legs give, and lies down on its side in
    the snow, the legs loose, its head laid on the ground. No thrash."""
    ko = ck.Clip("ko", KO_SEC)
    adv = track(KO_SEC, ((0.0, (0, 0, 0, 0.0)), (KO_STEP[0][1], (0, 0, 0, KO_STRIDE)),
                         (KO_STEP[1][1], (0, 0, 0, 2 * KO_STRIDE)), (KO_SEC, (0, 0, 0, 2 * KO_STRIDE))))
    body = track(KO_SEC, ((0.0, (0.0,)), (0.25, (2.0, 0, 0, 0, -0.02, 0.0)), (0.5, (0.0, 0, 0, 0, -0.01, 0.0)),
                          (0.72, (5.0, 0, 0, 0, -0.07, 0.0)), (KO_STEP[1][1], (2.0, 0, 0, 0, -0.04, 0.0)),
                          (KO_SAG[1], (SAG[0], 0, 0, 0, *SAG[1])), (KO_ROLL[1], (0.0,)), (KO_SEC, (0.0,))))
    roll = track(KO_SEC, ((0.0, (0.0,)), (KO_ROLL[0], (0.0,)), (2.0, (ROLL_DEG * 0.7,)), (KO_ROLL[1], (ROLL_DEG,)),
                          (KO_SEC, (ROLL_DEG,))))
    pivot = np.array([ROLL_PIVOT_X, 0.0, 0.0])
    sagged: dict = {}
    for (t, b), (_t, a), (_t2, r) in zip(body, adv, roll):
        pose = (float(b[0]), (float(b[4]), float(b[5])))
        z = float(a[3])
        rz = float(r[0])
        off = pivot - ck.rot_z(rz) @ pivot
        ko.key("body", t, (pose[0], 0.0, 0.0), (0.0, pose[1][0], pose[1][1]))
        ko.key("root", t, (0.0, 0.0, rz), (float(off[0]), float(off[1]), z))
        for name in LEGS:
            if t <= KO_SAG[1]:
                # where the paw stands: its rest place, moved by each step it has taken; lifted while it swings
                planted = rest_wrist(name).copy()
                for s0, s1, legs_ in KO_STEP:
                    if name in legs_:
                        planted[1] += 2 * KO_STRIDE * float(ck.smoothstep(s0, s1, t))
                        limp = 0.45 if name == "fr" else 1.0  # the stiff fore barely lifts
                        planted[0] += 0.06 * limp * math.sin(math.pi * float(np.clip((t - s0) / (s1 - s0), 0.0, 1.0)))
                sagged[name] = np.asarray(solve(name, pose, planted, advance=z))
                key_leg(ko, name, t, sagged[name])
            else:  # rolling over: the legs let go
                e = float(ck.smoothstep(KO_SAG[1], KO_ROLL[1], t))
                key_leg(ko, name, t, ck.mix(sagged[name], np.asarray(RELAXED[name[0]]), e))
    for t, neck, head, ears, yaw in ((0.0, (0, 0), 0, 0, 0.0), (0.72, (8, 2), -4, -12, 0.0),
                                     (KO_STEP[1][1], (2, 0), 0, -6, 0.0), (KO_SAG[1], (10, 4), 0, -14, 0.0),
                                     (KO_ROLL[1], (16, 6), 4, -22, 0.6), (KO_SEC, (20, 8), 6, -28, 1.0)):
        # the head turns less than the neck, so the longer muzzle (M3-CRE-645) lies on the snow, not in it
        key_head(ko, t, neck, head, 0.0, ears, yaw=(18.0 * yaw, 14.0 * yaw, 4.0 * yaw))
    for t, a, y in ((0.0, 0, 0), (1.2, 10, 0), (KO_ROLL[1], 20, 18), (KO_SEC, 22, 24)):
        ko.key("tail0", t, (a, y, 0.0))
        ko.key("tail1", t, (a * 0.4, y * 0.6, 0.0))
    return ko


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_attack(), build_cast(), build_hit(), build_ko()]


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender): skinned bounds, the paws and the peak time per clip
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
        lo, hi, disp = np.inf, -np.inf, []
        for t in frame_times(c.length):
            P = skin(rig, arrays, fk(rig, c, t))
            lo, hi = min(lo, float(P[:, 1].min())), max(hi, float(P[:, 1].max()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        end = fk(rig, c, c.length)
        P = skin(rig, arrays, end)
        paws = [round(float((end[f"{n}_paw"][0] @ pad_centre(n) + end[f"{n}_paw"][1])[1] - PAW_R[1]), 3) for n in LEGS]
        print(f"{c.name:7s} {c.length:.2f}s: y {lo:+.3f}..{hi:.3f}; at the end y {P[:, 1].min():+.3f}..{P[:, 1].max():.3f},"
              f" pad soles y {paws}; peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "ridge_lynx"})
    print(f"ridge_lynx: {info}")


if __name__ == "__main__":
    main()
