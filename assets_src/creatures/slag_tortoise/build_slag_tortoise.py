"""Slag tortoise, Ch5 the copper veins (M3-CRE-04): docs/kb/art/creatures/act1/slag_tortoise.md.

blender --background --factory-startup --python assets_src/creatures/slag_tortoise/build_slag_tortoise.py -- \
    --out assets/creatures/slag_tortoise/slag_tortoise.glb

A terrace tortoise whose shell carries cooled slag from the ash-plume: a glassy black crust far bigger than the
tortoise, cracked into plates with green copper weeping from the seams, a spawn_wound crack over the neck. Dusty
laterite skin, stubby legs, a beaked head on a wrinkled neck.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402
import grounding as gr  # noqa: E402

SEED = 5203
PAL = {k: ck.hexrgb(v) for k, v in {
    "volcanic_stone": "#3A3A3F", "bronze_patina": "#5F8A78", "laterite": "#A8573A", "sand_dry": "#EFDDB4",
    "spawn_wound": "#3FE0C8", "lacquer_black": "#1D1916", "tortoiseshell": "#6B3A1E", "bone": "#E6DAC0",
}.items()}

SHELL_C = np.array([0.0, 0.38, -0.05])
# The crust (M3-CRE-654): a lathe of SHELL_RINGS rings by SHELL_SEGS that skirts down past its equator to a hem at
# HEM_LOW over the flanks (raised over the neck and the tail), with slag drips hanging at the DRIPS azimuths (radians,
# 0 = the head, pi/2 = +x).
SHELL_RINGS = 44
SHELL_SEGS = 112
HEM_LOW = 0.25
DRIPS = (0.95, 1.6, 2.35, 3.7, 4.5, 5.25)
HEAD_STATIONS = 14
HEAD_ANGLES = 18
NECK_FOLDS = 4.5
CLINKERS = 12
SHELL_R = np.array([0.6, 0.42, 0.68])
# A variant's parameters (the scree crawler's frost-split scree and shaggier skin, M3-CRE-628); these values are the
# slag tortoise's: the shell's plate count, each plate's lift, faceted plates, and the skin's shag (metres).
SHELL_CELLS = 22
SHELL_LUMP = 0.06
# The primitive pass (M3-CRE-660): each plate is a slab tilted its own way by up to PLATE_TILT (a fraction of the
# radius per radian off its centre), so neighbours step at a seam instead of melting into one blob; the seam is
# SEAM_W wide (in the cell-distance gap) and sinks SEAM_DEPTH; the plate crowns' glass is at most GLASS.
PLATE_TILT = 0.12
SEAM_W = 0.022
SEAM_DEPTH = 0.07
GLASS = 0.5
SHELL_FLAT = False
SKIN_SHAG = 0.0
# The KO (M3-CRE-631): how far the legs tuck in (degrees) and the body rises (metres) by the end of the roll.
KO_TUCK = 40.0
KO_RISE = 0.04


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.2, 0))
    rig.add("shell", (0, 0.3, -0.3), (0, 0.3, 0.3), "root")
    rig.add("neck", (0, 0.3, 0.45), (0, 0.36, 0.72), "shell")
    rig.add("head", (0, 0.36, 0.72), (0, 0.36, 0.92), "neck")
    for sx, sz, tag in ((1, 1, "fl"), (-1, 1, "fr"), (1, -1, "bl"), (-1, -1, "br")):
        rig.add(f"leg_{tag}", (sx * 0.42, 0.28, sz * 0.38), (sx * 0.5, 0.0, sz * 0.45), "shell")
    rig.add("tail", (0, 0.25, -0.62), (0, 0.15, -0.82), "shell")
    return rig


def _hem(phi: np.ndarray) -> np.ndarray:
    """The crust's lower edge (m) round the azimuth phi (0 = +z, the head; pi/2 = +x): raised over the neck and the
    tail, low over the flanks, with slag drips hanging in narrow tongues (M3-CRE-654)."""
    front = np.exp(-(phi / 0.42) ** 2) + np.exp(-((phi - 2 * math.pi) / 0.42) ** 2)
    back = np.exp(-((phi - math.pi) / 0.35) ** 2)
    ring = np.column_stack([np.cos(phi), np.sin(phi), np.zeros_like(phi)])
    h = HEM_LOW + 0.2 * front + 0.07 * back + 0.025 * ck.fbm(ring * 3.0, SEED + 3)
    for a in DRIPS:
        h -= 0.1 * np.exp(-(np.angle(np.exp(1j * (phi - a))) / 0.06) ** 2)
    return h


def shell(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rings, segs = SHELL_RINGS, SHELL_SEGS
    phi = np.arange(segs) * (2.0 * math.pi / segs)
    th_max = np.arccos(np.clip((_hem(phi) - SHELL_C[1]) / SHELL_R[1], -1.0, 1.0))
    rows = []
    for i in range(rings + 1):
        th = th_max * (i / rings) ** 0.9
        rows.append(np.column_stack([np.sin(th) * np.sin(phi), np.cos(th), np.sin(th) * np.cos(phi)]))
    unit = np.vstack(rows)
    T = ck.grid_tris(rings + 1, segs, True)  # top to hem, as lathe(): outward
    rng = np.random.default_rng(SEED)
    cells = rng.normal(size=(SHELL_CELLS, 3))
    cells[:, 1] = np.abs(cells[:, 1]) + 0.3
    cells /= np.linalg.norm(cells, axis=1, keepdims=True)
    d = unit @ cells.T
    o = np.argsort(-d, axis=1)
    gap = d[np.arange(len(d)), o[:, 0]] - d[np.arange(len(d)), o[:, 1]]
    seam = 1.0 - ck.smoothstep(0.0, SEAM_W, gap)
    crack = 1.0 - ck.smoothstep(0.0, 0.55 * SEAM_W, gap)  # the open crack along a seam's middle
    dome = ck.smoothstep(0.0, 0.12, gap) ** 0.5  # each plate swells to its middle
    lump = rng.uniform(0.0, SHELL_LUMP, len(cells))[o[:, 0]] + 0.015 * ck.fbm(unit * 4.0, SEED + 1)
    # each plate tilts its own way: a slab, so the seams show steps and the plates read as broken crust
    tilt = rng.normal(size=(len(cells), 3)) * PLATE_TILT
    near = cells[o[:, 0]]
    tilt_v = (tilt[o[:, 0]] * (unit - near)).sum(axis=1)
    rough = 0.008 * ck.fbm(unit * 18.0, SEED + 8)  # the cooled glass's ripple
    hem_row = np.repeat(np.arange(rings + 1) / rings, segs)
    lip = ck.smoothstep(0.8, 1.0, hem_row)  # the hem rolls under, thick and rounded
    lift = lump + tilt_v + 0.025 * dome + rough
    P = SHELL_C + unit * SHELL_R * (1.0 + lift * (1.0 - seam) - SEAM_DEPTH * seam - 0.03 * lip)[:, None]
    P[:, 1] = np.maximum(P[:, 1], 0.1)
    # the weak point: one short closed crack low on the crust's brow over the neck, jagged across it
    line = 0.42 + 0.035 * np.sin(unit[:, 0] * 45.0)
    neck_crack = (np.exp(-((unit[:, 1] - line) / 0.045) ** 2) * ck.smoothstep(0.14, 0.08, np.abs(unit[:, 0]))
                  * ck.smoothstep(0.6, 0.8, unit[:, 2]))
    neck_crack = ck.smoothstep(0.2, 0.7, neck_crack)
    pits = ck.smoothstep(0.35, 0.6, ck.value_noise(unit * 26.0, SEED + 4))  # gas vesicles in the glass
    # copper weeps out of the seams and runs down the dome in streaks
    streak = ck.smoothstep(0.1, 0.5, ck.value_noise(unit * np.array([22.0, 2.5, 22.0]), SEED + 5))
    below = ck.smoothstep(0.06, 0.0, gap - 0.02 * (1.0 - unit[:, 1]))
    # the copper is a thin lip either side of the dark crack, and a few runs below it
    weep = np.clip(0.9 * seam * (1 - crack) + 0.25 * streak * below * np.clip(1.0 - unit[:, 1], 0.0, 1.0) ** 0.5,
                   0.0, 1.0)
    col = ck.mix(PAL["volcanic_stone"] * 0.8, PAL["lacquer_black"], (0.6 + 0.3 * ck.fbm(P * 8.0, SEED + 2))[:, None])
    # each plate its own cooling: most black glass, some a grey ash-skinned crust, a few rust-stained
    tone = np.random.default_rng(SEED + 6).uniform(0.0, 1.0, (len(cells), 2))[o[:, 0]]
    ash = ck.smoothstep(0.55, 0.75, tone[:, 0]) * dome
    rust = ck.smoothstep(0.8, 0.95, tone[:, 1]) * dome
    col = ck.mix(col, PAL["volcanic_stone"] * 1.35, (0.45 * dome * (1 - pits))[:, None])  # the plate crowns
    col = ck.mix(col, ck.mix(PAL["volcanic_stone"] * 1.6, PAL["sand_dry"] * 0.45, 0.3), (0.75 * ash)[:, None])
    col = ck.mix(col, ck.mix(PAL["laterite"], PAL["volcanic_stone"], 0.45), (0.6 * rust)[:, None])
    col = ck.mix(col, PAL["bronze_patina"] * 1.2, (0.9 * weep)[:, None])
    col = ck.mix(col, PAL["lacquer_black"] * 0.6, (0.95 * crack)[:, None])
    dust = ck.smoothstep(0.75, 1.0, unit[:, 1]) * (0.25 + 0.5 * seam)
    col = ck.mix(col, PAL["sand_dry"] * 0.5, (0.35 * dust)[:, None])  # ash dust on top, thickest in the seams
    col = ck.mix(col, PAL["spawn_wound"] * 0.6, neck_crack[:, None])
    cavity = np.clip(0.75 * seam + 0.25 * crack + 0.35 * pits * (1 - seam) + 0.4 * lip, 0.0, 1.0)
    # glassy only where the slag cooled smooth (the plate crowns); the seams and pits stay dull
    glass = GLASS * dome * (1 - pits) * (1 - weep) * (1 - ash) * (0.6 + 0.4 * ck.fbm(unit * 9.0, SEED + 9))
    ck.finish(mesh, P, T, "crust", col, rig.rigid("shell"), wet=glass, cavity=cavity, emission=neck_crack,
              flat=SHELL_FLAT)
    # clinker: lumps of slag fused on the dome, faceted where they cracked as they cooled
    crng = np.random.default_rng(SEED + 7)
    for k in range(CLINKERS):
        az, el = crng.uniform(0.0, 2 * math.pi), crng.uniform(0.35, 1.05)
        n = np.array([math.cos(el) * math.sin(az), math.sin(el), math.cos(el) * math.cos(az)])
        if n[2] > 0.55 and abs(n[0]) < 0.3:  # clear of the weak point's crack
            n[0] += 0.35
            n /= np.linalg.norm(n)
        size = crng.uniform(0.05, 0.11)
        Pk, Tk = ck.ellipsoid((0.0, 0.0, 0.0), (size, size * 0.6, size * crng.uniform(0.8, 1.3)), 3, 6)
        Pk = Pk * (1.0 + 0.25 * ck.value_noise(Pk * 30.0, SEED + 60 + k))[:, None]
        Pk = ck.transform(Pk, _frame(n, (0.0, 0.0, 1.0)) @ ck.rot_y(crng.uniform(0, 180)),
                          SHELL_C + n * SHELL_R * 1.02)
        kc = ck.mix(PAL["lacquer_black"], PAL["volcanic_stone"], crng.uniform(0.2, 0.7))
        ck.finish(mesh, Pk, Tk, "crust", kc, rig.rigid("shell"), wet=0.7, cavity=0.2, flat=True)
    # the plastron and the tortoise's own body under the crust, seen in the openings
    Pu, Tu = ck.lathe([(0.0, 0.17), (0.5, 0.19), (0.6, 0.27), (0.5, 0.4)], 40)
    Pu = Pu * np.array([1.0, 1.0, 1.12]) + np.array([0, 0, -0.05])
    ck.finish(mesh, Pu, ck.flip(Tu), "skin", PAL["tortoiseshell"] * 0.8, rig.rigid("shell"), cavity=0.5)


def shag(P: np.ndarray, T: np.ndarray, seed: int) -> np.ndarray:
    """The skin pushed out in tufts by SKIN_SHAG (a variant's shaggier skin); unchanged when it is 0."""
    if not SKIN_SHAG:
        return P
    tuft = ck.smoothstep(-0.2, 0.6, ck.value_noise(P * 38.0, seed)) * (0.6 + 0.4 * ck.fbm(P * 11.0, seed + 1))
    return P + ck.vertex_normals(P, T) * (SKIN_SHAG * tuft)[:, None]


def _skin_col(P: np.ndarray, folds) -> np.ndarray:
    """Dusty laterite skin, paler on the fold crests."""
    col = ck.mix(PAL["laterite"], PAL["tortoiseshell"], (0.3 + 0.3 * ck.fbm(P * 12.0, SEED + 30))[:, None])
    return ck.mix(col, PAL["sand_dry"] * 0.85, (0.45 * np.broadcast_to(folds, (len(P),)))[:, None])


def _frame(n: np.ndarray, hint) -> np.ndarray:
    """A rotation whose y axis is n (columns x, y, z), its z axis near `hint`."""
    y = n / np.linalg.norm(n)
    x = np.cross(np.asarray(hint, dtype=np.float64), y)
    if np.linalg.norm(x) < 1e-6:
        x = np.cross(np.array([1.0, 0.0, 0.0]), y)
    x /= np.linalg.norm(x)
    return np.column_stack([x, y, np.cross(x, y)])


def leg(mesh: ck.Mesh, rig: ck.Rig, tag: str) -> None:
    """An elephantine leg: a ringed column, a round pad and blunt nails, with thick scales down the fore legs' fronts
    and a few on the hind legs' backs (M3-CRE-654)."""
    b = rig.bones[rig.index(f"leg_{tag}")]
    h0, h1 = np.asarray(b.head), np.asarray(b.tail)
    sx = 1.0 if tag[1] == "l" else -1.0
    fore = tag[0] == "f"
    bone = rig.rigid(f"leg_{tag}")
    ankle = h1 + np.array([0.0, 0.07, 0.0])
    path = ck.bezier([h0 + np.array([-sx * 0.04, 0.05, 0.0]), h0 + 0.5 * (ankle - h0) + np.array([sx * 0.03, 0, 0]),
                      ankle], 7)
    P, T = ck.tube(path, np.array([0.12, 0.115, 0.105, 0.095, 0.088, 0.085, 0.088]), 12)
    P = shag(P, T, SEED + 20)
    rings = 0.5 + 0.5 * np.sin(P[:, 1] * 95.0)
    ck.finish(mesh, P, T, "skin", _skin_col(P, 0.6 * rings), bone, cavity=0.45 * (1 - rings))
    # the pad: flat on the floor (M3-CRE-631: a flat sole)
    Pp, Tp = ck.ellipsoid(h1 + np.array([0.0, 0.045, 0.01]), (0.105, 0.05, 0.115), 5, 10)
    Pp[:, 1] = np.maximum(Pp[:, 1], 0.0)
    ck.finish(mesh, Pp, Tp, "skin", _skin_col(Pp, 0.3) * 0.9, bone, cavity=0.3)
    # blunt nails round the front of the pad
    nails = 5 if fore else 4
    for k in range(nails):
        a = math.radians(-45.0 + 90.0 * k / (nails - 1))
        out = np.array([math.sin(a), 0.0, math.cos(a)])
        base = h1 + np.array([0.0, 0.04, 0.01]) + out * np.array([0.09, 0.0, 0.1])
        tip = base + out * 0.045 + np.array([0.0, -0.035, 0.0])
        Pc, Tc = ck.tube(ck.bezier([base, base + out * 0.03, tip], 4), np.array([0.019, 0.016, 0.01, 0.003]), 4)
        Pc[:, 1] = np.maximum(Pc[:, 1], 0.0)
        ck.finish(mesh, Pc, Tc, "skin", ck.mix(PAL["bone"] * 0.75, PAL["tortoiseshell"], 0.35), bone, wet=0.15)
    # scales: staggered rows of thick plates
    rows_, cols_ = (5, 4) if fore else (3, 3)
    face = 1.0 if fore else -1.0
    rng = np.random.default_rng(SEED + 40 + ("fl", "fr", "bl", "br").index(tag))
    tan, _, _ = ck.frames_along(path)
    for r in range(rows_):
        t = 0.3 + 0.62 * r / max(rows_ - 1, 1)
        k = t * (len(path) - 1)
        i0 = min(int(k), len(path) - 2)
        f = k - i0
        c = path[i0] * (1 - f) + path[i0 + 1] * f
        rad = 0.112 - 0.025 * t
        for cidx in range(cols_):
            a = (cidx - (cols_ - 1) / 2 + 0.5 * (r % 2) - 0.25) * 0.5
            out = np.array([math.sin(a) * 0.6 + sx * 0.35, 0.0, math.cos(a) * face])
            out -= tan[i0] * (out @ tan[i0])
            out /= np.linalg.norm(out)
            # a scute: domed, its lower edge lifted over the next row (overlapping, as a tortoise's leg)
            Ps, Ts = ck.ellipsoid((0.0, 0.0, 0.0), (0.038, 0.013, 0.032), 4, 8)
            Ps[:, 1] += 0.006 * ck.smoothstep(0.0, -0.03, Ps[:, 2])
            Ps = ck.transform(Ps, _frame(out, tan[i0]) @ ck.rot_x(-18.0), c + out * (rad - 0.006))
            tone = rng.uniform(0.0, 1.0)
            colp = ck.mix(PAL["laterite"] * 0.85, PAL["sand_dry"] * 0.8, 0.25 + 0.35 * tone)
            ck.finish(mesh, Ps, Ts, "skin", colp, bone, cavity=0.25)


def head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A tortoise head: a wedge skull under big scutes, a hooked keratin beak over a mouth line, a hooded eye under a
    brow, and two nostrils (M3-CRE-654)."""
    h0 = np.asarray(rig.bones[rig.index("head")].head)
    bone = rig.rigid("head")
    nst, nang = HEAD_STATIONS, HEAD_ANGLES
    s = np.linspace(0.0, 1.0, nst)
    zc = h0[2] - 0.05 + 0.27 * s
    yc = h0[1] + 0.005 - 0.03 * s ** 2
    w = np.interp(s, [0, 0.25, 0.55, 0.8, 0.93, 1.0], [0.07, 0.085, 0.078, 0.055, 0.035, 0.0])
    top = np.interp(s, [0, 0.3, 0.6, 0.8, 0.93, 1.0], [0.075, 0.08, 0.068, 0.05, 0.03, 0.0])
    bot = np.interp(s, [0, 0.3, 0.6, 0.8, 0.93, 1.0], [0.065, 0.062, 0.052, 0.038, 0.012, 0.0])
    hook = 0.042 * ck.smoothstep(0.78, 1.0, s)  # the upper beak's tip curls down past the lower
    a = np.linspace(0.0, 2.0 * math.pi, nang, endpoint=False)
    sa, ca = np.sin(a), np.cos(a)
    e = 2.0 / 2.4
    rows = []
    for k in range(nst):
        x = w[k] * np.sign(sa) * np.abs(sa) ** e
        y = np.where(ca > 0, top[k], bot[k]) * np.sign(ca) * np.abs(ca) ** e - hook[k]
        rows.append(np.column_stack([x, yc[k] + y, np.full(nang, zc[k])]))
    P = np.vstack(rows)
    T = ck.grid_tris(nst, nang, True)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    if float((fn[:, 1] * (P[T[:, 0], 1] - yc.mean())).sum()) < 0:
        T = ck.flip(T)
    S = np.repeat(s, nang)
    A = np.tile(a, nst)
    CA = np.tile(ca, nst)
    for sxe in (-1.0, 1.0):  # the brow over each eye
        d2 = ((P[:, 0] - sxe * 0.06) / 0.03) ** 2 + ((P[:, 2] - (h0[2] + 0.055)) / 0.035) ** 2
        P[:, 1] += 0.012 * np.exp(-d2) * (CA > 0.2)
    mouth_a = 2.05
    side = np.minimum(np.abs(A - mouth_a), np.abs(A - (2 * math.pi - mouth_a)))
    mouth = np.exp(-(side / 0.12) ** 2) * ck.smoothstep(0.3, 0.45, S)
    beak = ck.smoothstep(0.66, 0.76, S)
    rng = np.random.default_rng(SEED + 50)
    seeds = np.column_stack([rng.uniform(-0.08, 0.08, 9), np.zeros(9), h0[2] + rng.uniform(-0.04, 0.16, 9)])
    dd = np.linalg.norm((P * np.array([1.0, 0.0, 1.0]))[:, None, :] - seeds[None], axis=2)
    dd.sort(axis=1)
    upper = ck.smoothstep(0.0, 0.5, CA)
    scute = ck.smoothstep(0.0, 0.012, dd[:, 1] - dd[:, 0]) * upper * (1 - beak)
    col = _skin_col(P, 0.5 * scute)
    col = ck.mix(col, PAL["tortoiseshell"] * 0.9, (0.4 * upper * (1 - scute))[:, None])
    col = ck.mix(col, ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.55), beak[:, None])
    col = ck.mix(col, PAL["bone"] * 0.7, (beak * ck.smoothstep(0.92, 1.0, S) * 0.5)[:, None])  # a worn tip
    col = ck.mix(col, PAL["lacquer_black"], (0.8 * mouth)[:, None])
    cav = np.clip(0.9 * mouth + 0.5 * (1 - scute) * upper * (1 - beak), 0.0, 1.0)
    ck.finish(mesh, P, T, "skin", col, bone, wet=0.1 + 0.3 * beak, cavity=cav)
    circle = np.linspace(0, 2 * math.pi, 13)
    for sxe in (-1.0, 1.0):
        c = np.array([sxe * 0.071, h0[1] + 0.03, h0[2] + 0.06])
        Pe, Te = ck.ellipsoid(c, (0.019,) * 3, 5, 8)
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"], bone, wet=1.0)
        ring = c + np.array([-sxe * 0.004, 0.0, 0.0]) + 0.019 * np.column_stack(
            [np.zeros(13), np.cos(circle), np.sin(circle)])
        Pl, Tl = ck.tube(ring, 0.0065, 5, cap_start=False, cap_end=False)
        ck.finish(mesh, Pl, Tl, "skin", PAL["laterite"] * 0.8, bone, cavity=0.4)
        Pn, Tn = ck.ellipsoid((sxe * 0.012, yc[-3] + top[-3] - 0.03, zc[-3]), (0.007, 0.005, 0.006), 3, 5)
        ck.finish(mesh, Pn, Tn, "skin", PAL["lacquer_black"], bone, cavity=1.0)


def limbs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for tag in ("fl", "fr", "bl", "br"):
        leg(mesh, rig, tag)
    # the neck: loose skin in deep folds
    n = rig.bones[rig.index("neck")]
    nr = 20
    path = ck.bezier([np.asarray(n.head) - np.array([0, 0, 0.12]), n.head, n.tail], nr)
    u = np.linspace(0.0, 1.0, nr)
    fold = 0.5 + 0.5 * np.cos(u * math.pi * 2 * NECK_FOLDS)
    P, T = ck.tube(path, np.linspace(0.12, 0.078, nr) * (1.0 + 0.1 * fold), 12)
    P = shag(P, T, SEED + 21)
    fr = np.concatenate([np.repeat(fold, 12), np.zeros(len(P) - nr * 12)])
    ck.finish(mesh, P, T, "skin", _skin_col(P, 0.7 * fr), rig.rigid("neck"), cavity=0.55 * (1 - fr))
    # the collar: the loose skin where the neck leaves the crust, rigid on the shell, pleated
    cl = np.column_stack([np.zeros(5), 0.31 + 0.02 * np.linspace(0, 1, 5), np.linspace(0.5, 0.64, 5)])
    Pc, Tc = ck.tube(cl, np.array([0.13, 0.142, 0.15, 0.148, 0.138]), 14, cap_start=False, cap_end=False)
    wr = 0.5 + 0.5 * np.cos(np.tile(np.arange(14) * (2 * math.pi / 14), 5) * 5)
    Pc = Pc + (Pc - np.repeat(cl, 14, axis=0)) * (0.08 * wr)[:, None]
    Pc = shag(Pc, Tc, SEED + 22)
    ck.finish(mesh, Pc, Tc, "skin", _skin_col(Pc, 0.6 * wr), rig.rigid("shell"), cavity=0.6 * (1 - wr))
    head(mesh, rig)
    t = rig.bones[rig.index("tail")]
    th, tt = np.asarray(t.head), np.asarray(t.tail)
    Pt, Tt = ck.tube(ck.bezier([th, (th + tt) / 2 + np.array([0, 0.01, 0]), tt], 4), np.array([0.06, 0.045, 0.025,
                                                                                               0.008]), 8)
    ck.finish(mesh, Pt, Tt, "skin", _skin_col(Pt, 0.2), rig.rigid("tail"), cavity=0.3)
    Ps, Ts = ck.ellipsoid(tt + np.array([0, 0.004, 0.0]), (0.014, 0.009, 0.02), 3, 5)
    ck.finish(mesh, Ps, Ts, "skin", PAL["bone"] * 0.7, rig.rigid("tail"), flat=True)  # the tail's horny spur


def build_mesh(rig: ck.Rig, name: str = "slag_tortoise") -> ck.Mesh:
    mesh = ck.Mesh(name)
    shell(mesh, rig)
    limbs(mesh, rig)
    return mesh


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 3.2, loop=True)
    for t, out in ((0.0, 0.0), (0.8, 0.0), (1.4, -0.08), (2.2, -0.08), (2.8, 0.0), (3.2, 0.0)):
        idle.key("neck", t, (8.0 * out / 0.08, 0, 0), (0, 0, out))
    idle.wave("head", amp_rot=(0.0, 12.0, 0.0), cycles=1)
    idle.wave("shell", amp_loc=(0.0, 0.01, 0.0), cycles=2)
    attack = ck.Clip("attack", 1.2)
    for t, out, bite in ((0.0, 0.0, 0), (0.35, -0.08, 0), (0.55, 0.18, 12), (0.7, 0.16, -4), (1.2, 0.0, 0)):
        attack.key("neck", t, (bite, 0, 0), (0, 0, out))
        attack.key("shell", t, (-3.0 * out / 0.18, 0, 0), (0, 0, 0.1 * max(out, 0)))
    cast = ck.Clip("cast", 1.4)  # it withdraws into the crust
    for t, s in ((0.0, 0.0), (0.35, 1.0), (1.0, 1.0), (1.4, 0.0)):
        cast.key("neck", t, (0, 0, 0), (0, -0.02 * s, -0.28 * s))
        for tag, sx in (("fl", 1), ("fr", -1), ("bl", 1), ("br", -1)):
            cast.key(f"leg_{tag}", t, (0, 0, 0), (-sx * 0.08 * s, 0.12 * s, 0))
        cast.key("shell", t, (0, 0, 0), (0, -0.1 * s, 0))
    hit = ck.Clip("hit", 0.5)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.5, 0.0)):
        hit.key("neck", t, (0, 0, 0), (0, 0, -0.15 * s))
        hit.key("shell", t, (4.0 * s, 0, 0))
    # it rolls onto its side about the right edge. M3-CRE-631: it draws its legs in toward the plastron as it tips
    # (a left leg tucks with -z, a right one with +z), and rides up by the crust's overhang past the pivot, so the
    # crust and the legs underneath stay on the floor (they sank 8.5 cm)
    ko = ck.Clip("ko", 1.6)
    pivot = np.array([-0.55, 0.0, 0.0])
    for t, roll in ((0.0, 0.0), (0.6, -20.0), (1.2, -78.0), (1.6, -84.0)):
        R = ck.euler(0.0, 0.0, -roll)
        off = pivot - R @ pivot + np.array([0.0, KO_RISE * abs(roll) / 84.0, 0.0])
        ko.key("root", t, (0, 0, -roll), tuple(off))
        for tag, sx in (("fl", 1), ("fr", -1), ("bl", 1), ("br", -1)):
            ko.key(f"leg_{tag}", t, (abs(roll) * 0.3, 0, -sx * KO_TUCK * abs(roll) / 84.0))
        ko.key("neck", t, (25.0 * abs(roll) / 84.0, 0, 0))
    return [idle, attack, cast, hit, ko]


# The limbs kept on the floor (M3-CRE-631, common/grounding.py): a stubby leg is pushed up into the shell, by at most
# 0.2 m, wherever the shell's bob, pitch or roll would press its sole through the floor. M3-CRE-654: in the KO the whole
# body first rides up the least it takes for the crust it rolls onto (its skirt, drips and clinker) to rest on the floor.
GROUNDED_LIMBS = [("root", gr.LIFT, 1.0, 0.1, ("ko",))] + [
    (f"leg_{tag}", gr.LIFT, 1.0, 0.2) for tag in ("fl", "fr", "bl", "br")]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "slag_tortoise"})
    print(f"slag_tortoise: {info}")


if __name__ == "__main__":
    main()
