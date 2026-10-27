"""The Drownbell, boss of the vertical slice (M2-CRE-08): docs/kb/art/creatures/drownbell.md.

blender --background --factory-startup --python assets_src/creatures/drownbell/build_drownbell.py -- \
    --out assets/creatures/drownbell/drownbell.glb

The Shell Shrine's lost bronze bell, kept by the Undertow: a 2.4 m bell-hood with the shrine's fan-shells cast round
its shoulder, verdigris and worn brass, cracks that bleed spawn_wound light, a barnacled rim whose lip sits at the
VFX `rim` anchor (0.29 m), and under it a black wet mass that walks it on six short legs. The rim is its own mesh
(`Rim`), with a broken variant (`RimBroken`, a section of the lip gone) for `charge_broken`.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 9311
PAL = {k: ck.hexrgb(v) for k, v in {
    "bronze_patina": "#5F8A78", "brass": "#B08D57", "coral_stone_weathered": "#B9AE98", "lacquer_black": "#1D1916",
    "abyss_navy": "#061A2B", "spawn_wound": "#3FE0C8", "timber_weathered": "#7E6A55", "foliage_shadow": "#1E4A3A",
    "deep_teal_shadow": "#0E4A55", "sand_wet": "#B59D74",
}.items()}

LIP_Y = 0.29  # the rim's lowest edge: the VFX `rim` anchor (0.12 x 2.4 m)
RIM_TOP = 0.50  # where the rim band meets the bell body
RIM_R = 0.85
SEGS = 72
WET_LINE = 0.75
BREAK_ARC = (math.radians(-80.0), math.radians(25.0))  # azimuth span of the lip lost in RimBroken (camera side)
CRACKS = (-1.25, -0.35, 0.55, 2.35)  # hood crack azimuths (radians; 0 = +Z, the face)


def outer_r(y: np.ndarray) -> np.ndarray:
    """The bell's outer radius by height: a lip flaring out of a narrow waist, a rounded shoulder, a domed crown."""
    y = np.asarray(y, dtype=np.float64)
    flare = 0.53 + 0.29 * ck.smoothstep(1.30, RIM_TOP, y) ** 2.2
    shoulder = 0.53 + 0.10 * np.exp(-((y - 1.80) / 0.30) ** 2)
    r = np.where(y < 1.30, flare, shoulder)
    crown = ck.smoothstep(1.98, 2.33, y)
    return r * np.sqrt(np.clip(1.0 - crown ** 2.4, 0.0, 1.0))


def bell_profile() -> list[tuple[float, float]]:
    """Outer surface from the crown down to the rim join, then the inside back up (radius, y)."""
    out = []
    ys = np.concatenate([np.linspace(2.32, 1.98, 10), np.linspace(1.96, RIM_TOP, 44)])
    for y in ys:
        out.append((float(outer_r(np.array([y]))[0]), float(y)))
    out[0] = (0.0, 2.33)
    inner = []
    for y in np.linspace(RIM_TOP, 2.05, 14):
        inner.append((float(outer_r(np.array([y]))[0]) - 0.07 - 0.03 * ck.smoothstep(1.6, 2.05, y), float(y)))
    inner.append((0.0, 2.12))
    return out + inner


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.25, 0))
    rig.add("bell", (0, 0.3, 0), (0, 2.3, 0), "root")
    rig.add("rim", (0, LIP_Y, 0), (0, RIM_TOP, 0), "bell")
    rig.add("mass", (0, 0.35, 0), (0, 0.9, 0), "bell")
    for i in range(6):
        a = (i + 0.5) * 2.0 * math.pi / 6.0
        s, c = math.sin(a), math.cos(a)
        hip = (0.45 * s, 0.40, 0.45 * c)
        knee = (0.78 * s, 0.34, 0.78 * c)
        foot = (0.92 * s, 0.0, 0.92 * c)
        rig.add(f"leg{i}_a", hip, knee, "mass")
        rig.add(f"leg{i}_b", knee, foot, f"leg{i}_a")
    rp = rope_path()
    rig.add("rope0", rp[0], rp[3], "bell")
    rig.add("rope1", rp[3], rp[6], "rope0")
    rig.add("rope2", rp[6], rp[9], "rope1")
    return rig


def rope_path() -> np.ndarray:
    a = math.radians(-145.0)  # back-left, so it frames the silhouette without crossing the face
    s, c = math.sin(a), math.cos(a)
    pts = [(0.10 * s, 2.40, 0.10 * c), (0.45 * s, 2.25, 0.45 * c), (0.75 * s, 1.55, 0.75 * c),
           (0.95 * s, 0.25, 0.95 * c), (1.25 * s, 0.02, 1.25 * c)]
    return ck.bezier(pts, 10)


def _subset(P, T, keep_tri, arrays):
    """Triangles `keep_tri` of a part, with only the vertices they use."""
    T = T[keep_tri]
    used = np.unique(T.reshape(-1))
    remap = np.full(len(P), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    return P[used], remap[T], [a[used] if hasattr(a, "__len__") and np.ndim(a) > 0 and len(a) == len(P) else a
                               for a in arrays]


def bell_body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    prof = bell_profile()
    P, T = ck.lathe(prof, SEGS)
    n_out = len(prof) - 15  # rows on the outside
    row = np.repeat(np.arange(len(prof)), SEGS)
    outside = row < n_out
    unit_az = np.arctan2(P[:, 0], P[:, 2])
    y = P[:, 1]
    # the fan-shell band: 12 scallops round the shoulder, ribs fanning up from a hinge
    k = 12
    sector = (unit_az + math.pi) / (2 * math.pi) * k
    u = (sector - np.floor(sector)) - 0.5  # -0.5..0.5 across a shell
    v = (y - 1.52) / 0.42  # 0 at the hinge .. 1 at the shell's edge
    rr = np.sqrt((u * 2.1) ** 2 + v ** 2)
    in_shell = (v > 0) & (rr < 1.0) & outside
    ang = np.arctan2(u * 2.1, np.maximum(v, 1e-4))
    ribs = 0.5 + 0.5 * np.cos(ang * 9.0)
    shell_disp = np.where(in_shell, (0.018 + 0.016 * ribs) * ck.smoothstep(1.0, 0.86, rr), 0.0)
    rim_bead = np.where(outside, 0.016 * np.exp(-((y - 1.50) / 0.02) ** 2) + 0.014 * np.exp(-((y - 1.97) / 0.022) ** 2), 0.0)
    # cracks: jagged vertical lines that bleed light
    crack = np.zeros(len(P))
    for i, az in enumerate(CRACKS):
        lo, hi = 0.65 + 0.2 * (i % 2), 1.55 + 0.25 * ((i + 1) % 2)
        jag = 0.05 * np.sin(y * 23.0 + i) + 0.03 * np.sin(y * 57.0 + 2 * i)
        d = np.abs(np.angle(np.exp(1j * (unit_az - az - jag)))) * outer_r(y)
        crack = np.maximum(crack, np.exp(-(d / 0.03) ** 2) * ck.smoothstep(lo, lo + 0.1, y) * ck.smoothstep(hi, hi - 0.15, y))
    crack *= outside
    pitting = ck.fbm(P * 7.0, SEED + 1) * 0.006
    radial = np.column_stack([P[:, 0], np.zeros(len(P)), P[:, 2]])
    rn = np.linalg.norm(radial, axis=1, keepdims=True)
    radial = np.where(rn > 1e-6, radial / np.maximum(rn, 1e-6), 0.0)
    disp = shell_disp + rim_bead + pitting - 0.01 * crack
    P = P + radial * (disp * np.where(outside, 1.0, -0.3))[:, None]
    # colour: brass on the high points and crown, verdigris in the hollows and on the shoulder, darker and wet low
    patina_n = ck.fbm(P * 3.2, SEED + 2)
    hollow = np.where(in_shell, 1.0 - ribs, 0.0) * 0.8 + ck.smoothstep(1.85, 1.6, y) * 0.25
    patina = np.clip(0.55 + 0.9 * patina_n + 0.6 * hollow - 0.5 * ck.smoothstep(2.1, 2.3, y)
                     - 0.35 * np.where(in_shell, ribs, 0.0), 0.0, 1.0)
    col = ck.mix(PAL["brass"], PAL["bronze_patina"], patina[:, None])
    col = col * (1.0 + 0.10 * ck.fbm(P * 11.0, SEED + 3)[:, None])
    inside_col = PAL["bronze_patina"] * 0.45
    col = np.where(outside[:, None], col, inside_col)
    wet = ck.smoothstep(WET_LINE + 0.15, WET_LINE - 0.1, y)
    col = ck.mix(col, PAL["deep_teal_shadow"], (0.25 * wet)[:, None])
    col = ck.mix(col, PAL["lacquer_black"], (0.6 * crack)[:, None])
    cavity = np.clip(hollow * 0.6 + crack * 0.4 + np.where(outside, 0.0, 0.6), 0, 1)
    emission = np.zeros(len(P))
    ck.finish(mesh, P, T, "bronze", col, rig.rigid("bell"), wet=wet, cavity=cavity, emission=emission)


def crack_ribbons(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The hood's wounds: jagged emissive ribbons a few millimetres proud of the bronze (bright core, dark lips)."""
    for i, az in enumerate(CRACKS):
        lo, hi = 0.65 + 0.2 * (i % 2), 1.55 + 0.25 * ((i + 1) % 2)
        ys = np.linspace(lo, hi, 48)
        jag = 0.05 * np.sin(ys * 23.0 + i) + 0.03 * np.sin(ys * 57.0 + 2 * i)
        a = az + jag
        r = outer_r(ys) + 0.004
        centre = np.column_stack([r * np.sin(a), ys, r * np.cos(a)])
        tang = np.column_stack([np.cos(a), np.zeros_like(a), -np.sin(a)])
        width = 0.022 * np.sin(np.linspace(0.15, math.pi - 0.15, 48)) ** 0.5
        rows = [centre - tang * width[:, None], centre, centre + tang * width[:, None]]
        P = np.stack(rows, axis=1).reshape(-1, 3)
        T = ck.grid_tris(48, 3, False)
        T = T[:, ::-1]
        glow = np.tile([0.15, 1.0, 0.15], 48)
        col = ck.mix(np.tile(PAL["lacquer_black"], (len(P), 1)), np.tile(PAL["spawn_wound"], (len(P), 1)), glow[:, None])
        N = np.repeat(np.column_stack([np.sin(a), np.zeros_like(a), np.cos(a)]), 3, axis=0)
        ck.finish(mesh, P, T, "bronze", col, rig.rigid("bell"), wet=0.3, cavity=0.0, emission=glow, N=N)


def rim_band(rig: ck.Rig, broken: bool, rng: np.random.Generator) -> ck.Mesh:
    """The thick flared lip from LIP_Y to RIM_TOP, ringed with barnacles and three bright cracks (the weak point).
    `broken` takes out a section of the lip with a jagged, dark edge."""
    mesh = ck.Mesh("RimBroken" if broken else "Rim")
    r_top = float(outer_r(np.array([RIM_TOP]))[0])
    prof = [(r_top - 0.07, RIM_TOP), (r_top - 0.04, RIM_TOP - 0.08), (RIM_R - 0.08, LIP_Y + 0.03),
            (RIM_R - 0.06, LIP_Y), (RIM_R + 0.0, LIP_Y - 0.005), (RIM_R + 0.035, LIP_Y + 0.035),
            (RIM_R + 0.03, LIP_Y + 0.08), (0.5 * (RIM_R + r_top) + 0.02, 0.5 * (LIP_Y + RIM_TOP) + 0.03),
            (r_top + 0.012, RIM_TOP - 0.02), (r_top, RIM_TOP)]
    prof = prof[::-1]  # outside first, then round the lip to the inside
    segs = 96
    P, T = ck.lathe(prof, segs)
    az = np.arctan2(P[:, 0], P[:, 2])
    y = P[:, 1]
    crack = np.zeros(len(P))
    for az0 in (-0.9, -0.15, 2.6):  # three lip cracks, the camera side favoured
        d = np.abs(np.angle(np.exp(1j * (az - az0 - 0.04 * np.sin(y * 60.0)))))
        crack = np.maximum(crack, np.exp(-(d / 0.035) ** 2))
    n = ck.fbm(P * 9.0, SEED + 11)
    col = ck.mix(PAL["bronze_patina"] * 0.8, PAL["brass"], ck.smoothstep(0.1, 0.4, n)[:, None] * 0.5)
    col = ck.mix(col, PAL["sand_wet"] * 0.6, 0.35)
    col = ck.mix(col, PAL["spawn_wound"] * 0.6, crack[:, None])
    keep = np.ones(len(T), dtype=bool)
    if broken:
        tri_az = np.arctan2(P[T, 0].mean(axis=1), P[T, 2].mean(axis=1))
        jag = 0.08 * np.sin(P[T, 1].mean(axis=1) * 40.0)
        gone = (tri_az > BREAK_ARC[0] + jag) & (tri_az < BREAK_ARC[1] - jag)
        keep = ~gone
        edge = np.minimum(np.abs(az - BREAK_ARC[0]), np.abs(az - BREAK_ARC[1]))
        scorch = ck.smoothstep(0.25, 0.0, edge)
        col = ck.mix(col, PAL["lacquer_black"], (0.8 * scorch)[:, None])
        crack = crack * (1.0 - scorch)  # the light goes out of the broken lip
    Ps, Ts, (cs, es) = _subset(P, T, keep, [col, crack])
    ck.finish(mesh, Ps, Ts, "rim", cs, rig.rigid("rim"), wet=0.8, cavity=0.25, emission=es * 1.0)
    # barnacles: small cones scattered on the band's outside
    rng_b = np.random.default_rng(SEED + 21)
    for _ in range(46):
        a = rng_b.uniform(-math.pi, math.pi)
        if broken and BREAK_ARC[0] - 0.05 < a < BREAK_ARC[1] + 0.05:
            continue
        yy = rng_b.uniform(LIP_Y + 0.03, RIM_TOP - 0.03)
        rr = float(np.interp(yy, [LIP_Y, LIP_Y + 0.1, RIM_TOP], [RIM_R + 0.04, RIM_R + 0.03, r_top + 0.01]))
        sz = rng_b.uniform(0.018, 0.04)
        base = np.array([rr * math.sin(a), yy, rr * math.cos(a)])
        Pb, Tb = ck.lathe([(0.0, sz * 0.55), (sz * 0.45, sz * 0.75), (sz * 0.9, sz * 0.2), (sz, -sz * 0.2)], 6)
        Rb = ck.rot_y(math.degrees(a)) @ ck.rot_x(90.0)
        Pb = ck.transform(Pb, Rb, base)
        ck.finish(mesh, Pb, Tb, "rim", PAL["coral_stone_weathered"] * rng_b.uniform(0.75, 1.0), rig.rigid("rim"),
                  wet=0.6, cavity=0.3)
    return mesh


def crown(mesh: ck.Mesh, rig: ck.Rig) -> None:
    # the snapped hanging loop: an arc of a thick ring standing on the crown, one side broken off
    arc = np.linspace(math.radians(-20.0), math.radians(200.0), 16)
    path = np.column_stack([0.13 * np.cos(arc), 2.33 + 0.13 * np.sin(arc) + 0.05, np.zeros_like(arc)])
    P, T = ck.tube(path, 0.035, 10)
    n = ck.fbm(P * 12.0, SEED + 31)
    col = ck.mix(PAL["brass"], PAL["bronze_patina"], ck.smoothstep(-0.1, 0.3, n)[:, None])
    ck.finish(mesh, P, T, "bronze", col, rig.rigid("bell"), cavity=0.2)
    Pc, Tc = ck.ellipsoid((0, 2.31, 0), (0.17, 0.06, 0.17), 5, 16)
    ck.finish(mesh, Pc, Tc, "bronze", PAL["brass"] * 0.9, rig.rigid("bell"), cavity=0.3)


def rope(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rp = rope_path()
    path = ck.bezier(rp[[0, 2, 5, 7, 9]], 24)
    P, T = ck.tube(path, np.linspace(0.042, 0.032, 24), 8)
    twist = 0.5 + 0.5 * np.sin(np.arctan2(P[:, 0] - path[:, 0].mean(), P[:, 2]) * 3.0 + P[:, 1] * 40.0)
    col = ck.mix(PAL["timber_weathered"], PAL["foliage_shadow"], (ck.smoothstep(1.2, 0.3, P[:, 1]) * 0.7)[:, None])
    col = col * (0.85 + 0.15 * twist)[:, None]
    chain = rig.chain(["rope0", "rope1", "rope2"], [rp[0], rp[3], rp[6], rp[9]])
    ck.finish(mesh, P, T, "rope", col, chain, wet=ck.smoothstep(1.0, 0.3, P[:, 1]), cavity=0.3 * (1 - twist))
    # weed strands hanging off the rope
    rng = np.random.default_rng(SEED + 41)
    for i in range(7):
        t = rng.uniform(0.25, 0.85)
        p0 = path[int(t * 23)]
        dirn = np.array([rng.uniform(-0.15, 0.15), -1.0, rng.uniform(-0.15, 0.15)])
        L = rng.uniform(0.2, 0.45)
        sp = ck.bezier([p0, p0 + dirn * L * 0.5 + np.array([0.05, 0, 0]), p0 + dirn * L], 6)
        Pw, Tw = ck.tube(sp, np.linspace(0.012, 0.003, 6), 5, squash=0.3)
        ck.finish(mesh, Pw, Tw, "rope", PAL["foliage_shadow"] * 1.2, chain, wet=1.0, cavity=0.2)


def under_body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    # the black wet mass filling the bell's mouth, with wounds
    P, T = ck.ellipsoid((0, 0.62, 0), (0.62, 0.42, 0.62), 10, 24)
    P[:, 1] = np.maximum(P[:, 1], 0.24)
    n = ck.fbm(P * 6.0, SEED + 51)
    radial = P - np.array([0, 0.62, 0])
    radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-6)
    P = P + radial * (0.03 * n)[:, None]
    wound = ck.smoothstep(0.25, 0.45, n) * ck.smoothstep(0.55, 0.3, P[:, 1])
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.3, n)[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.5, wound[:, None])
    ck.finish(mesh, P, T, "carapace", col, rig.rigid("mass"), wet=1.0, cavity=0.2, emission=wound)
    for i in range(6):
        a = rig.bones[rig.index(f"leg{i}_a")]
        b = rig.bones[rig.index(f"leg{i}_b")]
        for seg, bone, r0, r1 in (("a", a, 0.075, 0.065), ("b", b, 0.065, 0.02)):
            p0, p1 = np.asarray(bone.head), np.asarray(bone.tail)
            mid = (p0 + p1) / 2 + np.array([0.0, 0.05 if seg == "a" else 0.0, 0.0])
            path = ck.bezier([p0, mid, p1], 7)
            Pl, Tl = ck.tube(path, np.linspace(r0, r1, 7), 8, squash=0.8)
            band = ck.smoothstep(0.92, 1.0, np.abs(np.sin(np.linalg.norm(Pl - p0, axis=1) * 30.0)))
            col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], (0.4 * band)[:, None])
            ck.finish(mesh, Pl, Tl, "carapace", col, rig.rigid(f"leg{i}_{seg}"), wet=1.0, cavity=band * 0.4)


def build_meshes(rig: ck.Rig) -> tuple[ck.Mesh, list[ck.Mesh]]:
    rng = np.random.default_rng(SEED)
    mesh = ck.Mesh("drownbell")
    bell_body(mesh, rig)
    crack_ribbons(mesh, rig)
    crown(mesh, rig)
    rope(mesh, rig)
    under_body(mesh, rig)
    return mesh, [rim_band(rig, False, rng), rim_band(rig, True, rng)]


LEGS = [f"leg{i}" for i in range(6)]


def _leg_out(i: int, deg: float) -> tuple[float, float, float]:
    """A rotation that swings leg i's upper segment up (+deg) or down about its own outward axis."""
    a = (i + 0.5) * 2.0 * math.pi / 6.0
    return (-deg * math.cos(a), 0.0, deg * math.sin(a))


def _tip(rz: float, rx: float, pivot_x: float, pivot_z: float, pivot_y: float = LIP_Y) -> tuple[tuple, tuple]:
    """Rotation (rx, 0, rz) of the whole bell about a point on its lip, as a root rotation and offset."""
    R = ck.euler(rx, 0.0, rz)
    p = np.array([pivot_x, pivot_y, pivot_z])
    off = p - R @ p
    return (rx, 0.0, rz), tuple(off)


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 3.2, loop=True)
    idle.wave("bell", amp_rot=(1.0, 0.0, 1.5), cycles=1)
    idle.wave("rope0", amp_rot=(0.0, 0.0, 3.0), cycles=1, phase=0.6)
    idle.wave("rope1", amp_rot=(0.0, 0.0, 5.0), cycles=1, phase=1.2)
    idle.wave("rope2", amp_rot=(0.0, 0.0, 7.0), cycles=1, phase=1.8)
    for i, leg in enumerate(LEGS):
        lift = 12.0 if i in (1, 4) else 0.0
        t0 = 0.6 if i == 1 else 2.0
        idle.key(f"{leg}_a", 0.0)
        if lift:
            idle.key(f"{leg}_a", t0, (0, 0, 0))
            idle.key(f"{leg}_a", t0 + 0.3, _leg_out(i, lift))
            idle.key(f"{leg}_a", t0 + 0.6, (0, 0, 0))
        idle.key(f"{leg}_a", 3.2)
    idle.wave("mass", amp_loc=(0.0, 0.012, 0.0), cycles=2)

    def legs_extend(c: ck.Clip, t: float, deg: float) -> None:
        for i, leg in enumerate(LEGS):
            c.key(f"{leg}_a", t, _leg_out(i, -deg))
            c.key(f"{leg}_b", t, _leg_out(i, deg * 0.6))

    attack = ck.Clip("attack", 1.5)  # hood_slam
    for t, rx, lift, fwd, ext in ((0.0, 0, 0, 0, 0), (0.55, -10, 0.5, -0.05, 18), (0.8, 9, -0.02, 0.28, 0),
                                  (1.0, 4, 0.0, 0.22, 0), (1.5, 0, 0, 0, 0)):
        attack.key("root", t, (rx, 0, 0), (0, lift, fwd))
        legs_extend(attack, t, ext)
    for t, r in ((0.0, 0), (0.55, -10), (0.8, 18), (1.1, -6), (1.5, 0)):
        attack.key("rope1", t, (r, 0, 0))

    cast = ck.Clip("cast", 1.8)  # the toll's swing; the ring lands at 1.0 s
    for t, rx, rz in ((0.0, 0, 0), (0.5, -13, 2), (1.0, 15, -2), (1.15, 13, -1.5), (1.4, -6, 1), (1.8, 0, 0)):
        cast.key("bell", t, (rx, 0, rz))
    for t, s in ((0.95, 0.0), (1.0, 1.0), (1.05, -1.0), (1.1, 0.8), (1.15, -0.6), (1.2, 0.4), (1.3, 0.0)):
        cast.key("rim", t, (0.0, 0.0, 1.2 * s))
    for t, r in ((0.0, 0), (0.5, 12), (1.0, -22), (1.4, 8), (1.8, 0)):
        cast.key("rope1", t, (r, 0, 0))
        cast.key("rope2", t, (r * 1.3, 0, 0))

    # M3-CRE-617: the blow rocks the whole bell back on its legs (peak at 0.1 s, where a hit snaps in), the legs
    # brace, the rim rings and the bell shivers as it settles.
    hit = ck.Clip("hit", 0.6)
    for k, t in enumerate(np.linspace(0.0, 0.54, 10)):
        s = (1.0 if k % 2 else -1.0) * (1.0 - t / 0.6) * (0.0 if k == 0 else 1.0)
        hit.key("bell", float(t), (0.8 * s, 0.0, 2.6 * s))
    hit.key("bell", 0.6)
    for t, rx, lift in ((0.0, 0.0, 0.0), (0.1, -5.0, 0.04), (0.26, 2.2, 0.0), (0.42, -0.8, 0.0), (0.6, 0.0, 0.0)):
        hit.key("root", t, (rx, 0, 0), (0, lift, -0.06 * rx / 5.0))
    for t, s in ((0.06, 0.0), (0.1, 1.0), (0.15, -0.8), (0.2, 0.6), (0.26, -0.4), (0.34, 0.2), (0.44, 0.0)):
        hit.key("rim", t, (0.0, 0.0, 1.0 * s))
    for t, deg in ((0.0, 0.0), (0.1, 9.0), (0.35, 3.0), (0.6, 0.0)):
        legs_extend(hit, t, deg)

    phase = ck.Clip("phase_change", 2.4)  # the legs fold; CreatureActor sinks and tilts the model (creatures.json)
    for t, deg in ((0.0, 0.0), (0.8, 20.0), (1.8, 38.0), (2.4, 40.0)):
        for i, leg in enumerate(LEGS):
            phase.key(f"{leg}_a", t, _leg_out(i, deg))
            phase.key(f"{leg}_b", t, _leg_out(i, -deg * 1.4))
    for t, rx in ((0.0, 0.0), (0.6, -4.0), (1.4, 5.0), (2.0, -2.0), (2.4, 0.0)):
        phase.key("bell", t, (rx, 0, 0))

    flood = ck.Clip("idle_flood", 3.6, loop=True)
    flood.wave("bell", amp_rot=(1.6, 0.0, 2.2), cycles=1)
    for i, leg in enumerate(LEGS):
        flood.key(f"{leg}_a", 0.0, _leg_out(i, 40.0))
        flood.key(f"{leg}_a", 3.6, _leg_out(i, 40.0))
        flood.key(f"{leg}_b", 0.0, _leg_out(i, -56.0))
        flood.key(f"{leg}_b", 3.6, _leg_out(i, -56.0))
    flood.wave("rope1", amp_rot=(4.0, 0.0, 6.0), cycles=1, phase=0.9)
    flood.wave("rope2", amp_rot=(6.0, 0.0, 9.0), cycles=1, phase=1.5)

    ko = ck.Clip("ko", 2.6)  # it tips onto its side about the lip and slides seaward (+x), rim toward the sea
    for t, rz, slide, drop in ((0.0, 0.0, 0.0, 0.0), (0.5, -6.0, 0.0, 0.0), (1.2, -30.0, 0.05, 0.08),
                               (1.9, -68.0, 0.15, 0.24), (2.2, -76.0, 0.2, 0.3), (2.6, -74.0, 0.22, 0.29)):
        rot, off = _tip(rz, 0.0, RIM_R, 0.0)
        ko.key("root", t, rot, (off[0] + slide, off[1] - drop, off[2]))
    for i, leg in enumerate(LEGS):
        ko.key(f"{leg}_a", 0.0)
        ko.key(f"{leg}_a", 1.4, _leg_out(i, 45.0))
        ko.key(f"{leg}_a", 2.6, _leg_out(i, 50.0))
        ko.key(f"{leg}_b", 0.0)
        ko.key(f"{leg}_b", 1.4, _leg_out(i, -60.0))
        ko.key(f"{leg}_b", 2.6, _leg_out(i, -70.0))
    return [idle, attack, cast, hit, ko, phase, flood]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh, extra = build_meshes(rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extra_meshes=extra,
                              extras={"hymn_creature": "drownbell"})
    print(f"drownbell: {info}")


if __name__ == "__main__":
    main()
