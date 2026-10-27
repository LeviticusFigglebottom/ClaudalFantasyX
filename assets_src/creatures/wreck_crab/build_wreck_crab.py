"""Wreck crab, Ch6 the Brine Shoals (M3-CRE-05): docs/kb/art/creatures/act1/wreck_crab.md.

blender --background --factory-startup --python assets_src/creatures/wreck_crab/build_wreck_crab.py -- \
    --out assets/creatures/wreck_crab/wreck_crab.glb

A variant of the reef crab (its rig, legs, eyes, claws and clips are imported from the reef crab's build module,
which is not edited). Where the reef crab grows drowned-house coral, this one lives in the wrecks: a low carapace
crusted with salt (mortar_white, salt_glass crystals) and wreck timber, and on its back, the way a hermit crab
wears a shell, a broken Saltwright lamp housing lying on its side: a brass octagonal cage, scorched and green with
patina, its salt-glass panes crazed and two of them gone. The lamp still holds a little bound light (glimmer_bound,
the world's bound lamp light, not the crab's own: art sign-off in the sheet). The crab's own weak point is a
spawn_wound crack in the crust on its crusher's side.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "common"))
sys.path.insert(0, str(_HERE.parent / "reef_crab"))
import build_reef_crab as rc  # noqa: E402
import creature_kit as ck  # noqa: E402

SEED = 6421
PAL = {k: ck.hexrgb(v) for k, v in {
    "mortar_white": "#E6E1D6", "salt_glass": "#BFE6E0", "coral_stone_weathered": "#B9AE98",
    "timber_weathered": "#7E6A55", "sand_wet": "#B59D74", "laterite": "#A8573A", "tortoiseshell": "#6B3A1E",
    "lacquer_black": "#1D1916", "brass": "#B08D57", "bronze_patina": "#5F8A78", "glimmer_bound": "#4FB3B0",
    "spawn_wound": "#3FE0C8", "storm_slate": "#3E4A57",
}.items()}
SALT = PAL["mortar_white"] * 0.9  # salt crust held under the albedo ceiling
# the limbs' chitin, bleached: pale grey wreck tones above, weathered timber grey-brown below
LEG_PALE = ck.mix(PAL["coral_stone_weathered"], PAL["timber_weathered"], 0.6) * 0.92
LEG_DARK = ck.mix(PAL["timber_weathered"], PAL["storm_slate"], 0.35) * 0.9
BODY_Y = rc.BODY_Y
CRUST_R = (0.47, 0.15, 0.38)  # lower than the reef crab's coral dome: the lamp is its height

# The lamp housing: an octagonal brass cage on its side, its open collar forward over the carapace.
LAMP_AXIS_DEG = -76.0  # rot_x: the housing's +y (collar to cap) leans back and up
LAMP_AT = np.array([0.0, 0.53, 0.17])  # the collar's centre
LAMP_R = 0.25
LAMP_H = 0.48  # collar to shoulder; the cap rises 0.12 above that
SIDES = 8
BROKEN = (7, 0)  # the panes knocked out: the top and the top of the camera side (-x, once turned)


def _orient(P: np.ndarray, T: np.ndarray, out_fn) -> np.ndarray:
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    c = P[T].mean(axis=1)
    return ck.flip(T) if float(((fn * out_fn(c)).sum(axis=1) > 0).mean()) < 0.5 else T


def _lamp(P: np.ndarray) -> np.ndarray:
    """Lamp-local (y along the housing, collar at 0) to the crab's space."""
    return ck.transform(P, ck.rot_x(LAMP_AXIS_DEG), LAMP_AT)


def _radial(c: np.ndarray) -> np.ndarray:
    return c * np.array([1.0, 0.0, 1.0])


# ---------------------------------------------------------------------------------------------
# The crab's own crust
# ---------------------------------------------------------------------------------------------
def crust(mesh: ck.Mesh, rig: ck.Rig, rng: np.random.Generator) -> None:
    rings, segs = 20, 44
    prof = []
    for i in range(rings + 1):
        th = (math.pi / 2) * (i / rings) ** 0.85
        prof.append((math.sin(th), math.cos(th)))
    U, T = ck.lathe(prof, segs)

    def on_crust(Uq):
        Pq = Uq * np.asarray(CRUST_R)
        Pq[:, 2] += 0.04 * Uq[:, 2] * (Uq[:, 2] > 0)
        return Pq

    P = on_crust(U)
    n_out = U / np.asarray(CRUST_R)
    n_out /= np.linalg.norm(n_out, axis=1, keepdims=True)
    polar = np.arccos(np.clip(U[:, 1], -1, 1)) / (math.pi / 2)
    azim = np.arctan2(U[:, 0], U[:, 2])
    front = ck.smoothstep(0.2, 0.9, np.cos(azim)) * ck.smoothstep(0.75, 1.0, polar)
    lump = ck.fbm(P * 9.0, SEED + 1)
    # the salt grows in plates: cells (nearest of scattered centres on the dome) each lifted and tilted on its own,
    # split by deep cracks, the way a salt pan dries and buckles; and on the plates, crusty nodules of salt
    srng = np.random.default_rng(SEED + 7)
    n_cell = 46
    a_c = srng.uniform(-math.pi, math.pi, n_cell)
    p_c = np.sqrt(srng.uniform(0.0, 1.0, n_cell)) * 0.97
    Uc = np.column_stack([np.sin(p_c * math.pi / 2) * np.sin(a_c), np.cos(p_c * math.pi / 2),
                          np.sin(p_c * math.pi / 2) * np.cos(a_c)])
    Pc = on_crust(Uc)
    dist = np.linalg.norm(P[:, None, :] - Pc[None, :, :], axis=2)
    order = np.argsort(dist, axis=1)
    near = order[:, 0]
    f1 = dist[np.arange(len(P)), near]
    f2 = dist[np.arange(len(P)), order[:, 1]]
    crack = ck.smoothstep(0.03, 0.008, f2 - f1)
    lift_c = srng.uniform(0.004, 0.03, n_cell)
    tilt_c = srng.normal(0.0, 1.0, (n_cell, 3))
    tilt = ((P - Pc[near]) * tilt_c[near]).sum(axis=1) * 0.18  # a buckled plate rises toward one edge
    plate = np.clip(lift_c[near] + tilt - 0.25 * f1 * f1 / 0.01, 0.0, 0.04)
    n_nod = 120
    a_n = srng.uniform(-math.pi, math.pi, n_nod)
    p_n = srng.uniform(0.3, 0.99, n_nod)  # most on the flanks that show under the lamp
    Pn = on_crust(np.column_stack([np.sin(p_n * math.pi / 2) * np.sin(a_n), np.cos(p_n * math.pi / 2),
                                   np.sin(p_n * math.pi / 2) * np.cos(a_n)]))
    r_n = srng.uniform(0.024, 0.055, n_nod)
    h_n = srng.uniform(0.014, 0.04, n_nod)
    dn = np.linalg.norm(P[:, None, :] - Pn[None, :, :], axis=2)
    nod = (h_n[None, :] * np.exp(-(dn / r_n[None, :]) ** 2)).max(axis=1)
    nod_mask = ck.smoothstep(0.004, 0.02, nod)
    rough = ck.fbm(P * 40.0, SEED + 8)
    disp = (0.012 * ck.smoothstep(-0.1, 0.4, lump) + 0.01 * front
            + plate * (1.0 - crack) - 0.012 * crack + nod + 0.004 * rough)
    disp = disp * (1.0 - 0.5 * ck.smoothstep(0.96, 1.0, polar))  # the rim tucks under, onto the body
    P = P + n_out * disp[:, None]
    P[:, 1] += BODY_Y
    T = _orient(P, T, lambda c: c - np.array([0.0, BODY_Y, 0.0]))
    tone_c = srng.uniform(0.0, 1.0, n_cell)
    col = ck.mix(PAL["coral_stone_weathered"] * 0.82, SALT, ck.smoothstep(0.2, 0.7, tone_c[near])[:, None])
    col = ck.mix(col, PAL["salt_glass"] * 0.85, (0.35 * ck.smoothstep(0.85, 1.0, tone_c[near]))[:, None])
    col = col * (0.9 + 0.12 * ck.fbm(P * 23.0, SEED + 2))[:, None]
    col = ck.mix(col, SALT * 1.04, (0.8 * nod_mask)[:, None])  # the nodules are the freshest, whitest salt
    col = ck.mix(col, PAL["timber_weathered"] * 0.5, (0.85 * crack)[:, None])  # grime packed in the cracks
    col = ck.mix(col, PAL["sand_wet"] * 0.75, (0.4 * ck.smoothstep(0.96, 1.0, polar))[:, None])
    # the weak point: a crack in the crust on the crusher's side (-x), at the shoulder, lit from inside
    centre = np.array([rc.SIDE_R * 0.66, 0.55, 0.42])
    wd = np.linalg.norm(U - centre / np.linalg.norm(centre), axis=1)
    jag = 0.5 + 0.5 * np.abs(np.sin(U[:, 2] * 38.0 + U[:, 1] * 11.0))
    wound = ck.smoothstep(0.24, 0.08, wd) * jag
    col = ck.mix(col, PAL["spawn_wound"] * 0.5, (0.85 * wound)[:, None])
    wet = ck.smoothstep(0.9, 1.0, polar) * 0.5 * (1.0 - nod_mask)  # salt is dry; only the skirt is damp
    ck.finish(mesh, P, T, "shell", col, rig.rigid("body"), wet=wet,
              cavity=np.clip(0.85 * crack + 0.3 * (1.0 - nod_mask) * ck.smoothstep(0.01, 0.0, plate) + 0.3 * wound,
                             0.0, 1.0),
              emission=wound, flat=True)

    # underside, as the reef crab's
    prof = [(0.0, -1.0)] + [(math.sin((math.pi / 2) * i / 8), -math.cos((math.pi / 2) * i / 8)) for i in range(1, 9)]
    Pu, Tu = ck.lathe(prof, 20)
    Pu = Pu * np.array([0.44, 0.10, 0.35]) + np.array([0.0, BODY_Y - 0.03, 0.0])
    Tu = _orient(Pu, Tu, lambda c: c - np.array([0.0, BODY_Y, 0.0]))
    cu = ck.mix(PAL["sand_wet"] * 0.85, LEG_DARK, 0.5 + 0.5 * ck.fbm(Pu * 7.0, SEED + 3)[:, None])
    ck.finish(mesh, Pu, Tu, "chitin", cu, rig.rigid("body"), wet=0.9, cavity=0.3)
    for x, y in ((0.0, 0.40), (-0.06, 0.37), (0.06, 0.37), (0.0, 0.34)):
        Pm, Tm = ck.ellipsoid((x, y, 0.37), (0.05, 0.035, 0.03), 4, 6)
        ck.finish(mesh, Pm, Tm, "chitin", ck.mix(LEG_PALE, LEG_DARK, 0.5), rig.rigid("body"),
                  wet=0.8, cavity=0.5)

    # salt crystals: small faceted clusters on the crust and the lamp's underside
    for k in range(26):
        a = rng.uniform(-math.pi, math.pi)
        pol = rng.uniform(0.35, 0.95)
        u = np.array([math.sin(pol * math.pi / 2) * math.sin(a), math.cos(pol * math.pi / 2),
                      math.sin(pol * math.pi / 2) * math.cos(a)])
        c = u * np.asarray(CRUST_R) + np.array([0.0, BODY_Y, 0.0])
        s = rng.uniform(0.012, 0.03)
        Pc, Tc = ck.ellipsoid((0, 0, 0), (s, s * rng.uniform(1.2, 2.2), s), 2, 4)
        Pc = ck.transform(Pc, ck.euler(*rng.uniform(-35, 35, 3)), c)
        Tc = _orient(Pc, Tc, lambda q, c=c: q - c)
        tint = ck.mix(PAL["salt_glass"] * 0.9, SALT, rng.uniform(0.0, 0.6))
        ck.finish(mesh, Pc, Tc, "glass", tint, rig.rigid("body"), wet=0.3, flat=True)


def timbers(mesh: ck.Mesh, rig: ck.Rig, rng: np.random.Generator) -> None:
    """Wreck timber lodged in the crust: plank ends with broken, splintered tips."""
    for k, (c, yaw, pitch, L, w) in enumerate((((0.34, 0.50, -0.16), 62.0, -14.0, 0.50, 0.10),
                                               ((-0.40, 0.47, 0.02), -78.0, -18.0, 0.36, 0.08),
                                               ((0.16, 0.48, -0.36), 150.0, -26.0, 0.42, 0.09))):
        n = 7
        s = np.linspace(-0.5, 0.5, n)
        splinter = np.where(s > 0.3, rng.uniform(-0.6, 0.0, n), 0.0)
        rows = []
        for i, sv in enumerate(s):
            z = sv * L
            hw = w * 0.5
            th = 0.024
            end = 1.0 + splinter[i]
            rows.append([(-hw * end, th, z), (hw, th, z), (hw, -th, z), (-hw * end, -th, z)])
        P = np.asarray(rows, dtype=np.float64).reshape(-1, 3)
        T = ck.grid_tris(n, 4, True)
        cap0 = np.array([[0, 1, 2], [0, 2, 3]])
        last = (n - 1) * 4
        cap1 = np.array([[last, last + 2, last + 1], [last, last + 3, last + 2]])
        T = np.vstack([T, cap0, cap1])
        R = ck.euler(pitch, yaw, rng.uniform(-10, 10))
        Pw = ck.transform(P, R, c)
        cen = np.asarray(c)
        T = _orient(Pw, T, lambda q, R=R, cen=cen: (q - cen) - np.outer((q - cen) @ R[:, 2], R[:, 2]))
        grain = 0.5 + 0.5 * np.sin(P[:, 0] * 160.0 + 6.0 * ck.fbm(P * 8.0, SEED + 40 + k))
        col = PAL["timber_weathered"] * (0.75 + 0.2 * grain)[:, None]
        col = ck.mix(col, SALT, (0.35 * ck.smoothstep(0.1, 0.4, ck.fbm(Pw * 12.0, SEED + 50 + k)))[:, None])
        ck.finish(mesh, Pw, T, "timber", col, rig.rigid("body"), wet=0.3, cavity=0.3 * (1.0 - grain), flat=True)


# ---------------------------------------------------------------------------------------------
# The lamp housing
# ---------------------------------------------------------------------------------------------
def _brass(P: np.ndarray, seed: int) -> np.ndarray:
    """Brass, scorched black and green with patina in patches, crusted with salt underneath."""
    n1 = ck.fbm(P * 9.0, seed)
    n2 = ck.fbm(P * 15.0, seed + 1)
    col = ck.mix(PAL["brass"] * 0.85, PAL["bronze_patina"], ck.smoothstep(-0.1, 0.25, n1)[:, None])
    col = ck.mix(col, PAL["lacquer_black"], (0.85 * ck.smoothstep(-0.1, 0.2, n2))[:, None])  # the scorch
    return col


def lamp(mesh: ck.Mesh, rig: ck.Rig, rng: np.random.Generator) -> None:
    ib = rig.rigid("body")
    half = math.pi / SIDES
    ang = np.arange(SIDES) * (2.0 * math.pi / SIDES) + half

    # the crazed salt-glass panes: one flat panel per side, the broken ones missing their upper part
    for k in range(SIDES):
        a0, a1 = ang[k] - half, ang[k] + half
        nv, nh = 6, 3
        rows = []
        for i in range(nv):
            y = 0.05 + (LAMP_H - 0.08) * i / (nv - 1)
            row = []
            for j in range(nh):
                a = a0 + (a1 - a0) * j / (nh - 1)
                r = LAMP_R * 0.93 * math.cos(half) / math.cos(a - ang[k])  # a flat pane between two corners
                row.append((r * math.sin(a), y, r * math.cos(a)))
            rows.append(row)
        P = np.asarray(rows, dtype=np.float64).reshape(-1, 3)
        T = ck.grid_tris(nv, nh, False)
        if k in BROKEN:
            keep_rows = 2 if k == BROKEN[0] else 3
            T = T[(T // nh).max(axis=1) < keep_rows]
        T = _orient(P, T, _radial)
        craze = ck.smoothstep(0.82, 1.0, np.abs(ck.value_noise(P * 30.0, SEED + 60 + k)) * 2.0)
        col = ck.mix(PAL["salt_glass"] * 0.45, PAL["storm_slate"], 0.6)  # smoked, sea-dulled glass
        col = ck.mix(np.broadcast_to(col, P.shape), SALT, (0.7 * craze)[:, None])
        soot = ck.smoothstep(-0.05, 0.25, ck.fbm(P * 8.0, SEED + 70 + k))
        col = ck.mix(col, PAL["lacquer_black"], (0.75 * soot)[:, None])
        Pw = _lamp(P)
        ck.finish(mesh, Pw, T, "glass", col, ib, wet=0.5, cavity=0.4 * craze, emission=0.35 * (1.0 - soot), flat=True)
        # the inner face, so a pane reads from inside through the broken ones
        ck.finish(mesh, Pw, ck.flip(T), "glass", col * 0.7, ib, wet=0.5, emission=0.5 * (1.0 - soot), flat=True)

    # the corner ribs
    for k in range(SIDES):
        a = ang[k] - half
        base = np.array([LAMP_R * math.sin(a), 0.0, LAMP_R * math.cos(a)])
        bent = 0.03 if k == 3 else 0.0  # one rib bent outward where the panes broke
        path = np.array([base + (0, 0.02, 0), base * (1.0 + bent) + (0, LAMP_H * 0.5, 0), base + (0, LAMP_H, 0)])
        path = ck.bezier(path, 6)
        P, T = ck.tube(path, 0.013, 6, squash=0.7)
        Pw = _lamp(P)
        ck.finish(mesh, Pw, T, "brass", _brass(Pw, SEED + 80 + k), ib, wet=0.2, cavity=0.2)

    # the collar (open: the crab lives in it) and the shoulder band: rectangular-section rings
    for k, (y0, y1, r0, r1) in enumerate(((0.0, 0.055, LAMP_R * 0.98, LAMP_R * 1.1),
                                          (LAMP_H - 0.03, LAMP_H + 0.02, LAMP_R * 0.96, LAMP_R * 1.07))):
        P, T = ck.lathe([(r0, y0), (r1, y0), (r1, y1), (r0, y1), (r0, y0)], SIDES * 2)
        rm, ym = (r0 + r1) / 2.0, (y0 + y1) / 2.0

        def out(c, rm=rm, ym=ym):
            rad = _radial(c)
            ln = np.linalg.norm(rad, axis=1, keepdims=True)
            return rad / np.maximum(ln, 1e-9) * (ln - rm) + np.column_stack([np.zeros(len(c)), c[:, 1] - ym,
                                                                             np.zeros(len(c))])

        T = _orient(P, T, out)
        Pw = _lamp(P)
        ck.finish(mesh, Pw, T, "brass", _brass(Pw, SEED + 90 + k), ib, wet=0.2, cavity=0.15, flat=True)

    # the cap: a stepped dome, the chimney, and the carrying ring
    prof = [(LAMP_R * 1.06, LAMP_H + 0.02), (LAMP_R * 0.95, LAMP_H + 0.05), (LAMP_R * 0.7, LAMP_H + 0.09),
            (LAMP_R * 0.42, LAMP_H + 0.115), (0.05, LAMP_H + 0.125), (0.05, LAMP_H + 0.17), (0.0, LAMP_H + 0.175)]
    P, T = ck.lathe(prof[::-1], SIDES * 2)
    T = _orient(P, T, lambda c: _radial(c) + (c - np.array([0.0, LAMP_H, 0.0])) * np.array([0, 1, 0]))
    dent = np.exp(-((P[:, 0] - 0.1) / 0.06) ** 2 - ((P[:, 2] + 0.05) / 0.06) ** 2)
    P[:, 1] -= 0.025 * dent  # a dent in the cap
    Pw = _lamp(P)
    ck.finish(mesh, Pw, T, "brass", _brass(Pw, SEED + 95), ib, wet=0.2, cavity=0.3 * dent)
    t = np.linspace(0.0, math.pi, 9)  # the carrying ring's arch over the chimney
    ring = np.column_stack([0.06 * np.cos(t), LAMP_H + 0.165 + 0.06 * np.sin(t), np.zeros(len(t))])
    P, T = ck.tube(ring, 0.008, 5)
    Pw = _lamp(P)
    ck.finish(mesh, Pw, T, "brass", _brass(Pw, SEED + 97), ib, wet=0.2)

    # the bound light still in it: faint, steady, in the housing's heart
    lc = np.array([0.0, LAMP_H * 0.62, 0.0])
    Pl, Tl = ck.ellipsoid(lc, (LAMP_R * 0.45, LAMP_H * 0.24, LAMP_R * 0.45), 6, 10)
    Tl = _orient(Pl, Tl, lambda c: c - lc)
    glow = 0.65 + 0.35 * ck.fbm(Pl * 12.0, SEED + 99)
    ck.finish(mesh, _lamp(Pl), Tl, "lamp_light", PAL["glimmer_bound"] * 0.7, ib, emission=glow)

    # the crab's soft abdomen, curled into the housing's open collar the way a hermit crab fills its shell
    ac = np.array([0.0, LAMP_H * 0.2, 0.0])
    Pa, Ta = ck.ellipsoid(ac, (LAMP_R * 0.92, LAMP_H * 0.26, LAMP_R * 0.92), 7, 12)
    Ta = _orient(Pa, Ta, lambda c: c - ac)
    rib = 0.5 + 0.5 * np.cos(Pa[:, 1] * 70.0)
    ca = ck.mix(PAL["sand_wet"] * 0.75, ck.mix(PAL["laterite"], LEG_DARK, 0.8) * 0.85, (0.3 + 0.4 * rib)[:, None])
    ck.finish(mesh, _lamp(Pa), Ta, "chitin", ca, ib, wet=0.9, cavity=0.4 * (1.0 - rib))


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    rng = np.random.default_rng(SEED)
    mesh = ck.Mesh("wreck_crab")
    # the reef crab's limbs, bleached by the salt toward grey wreck timber, and crusted with salt where the
    # wrecks rub (its parts are wrapped in memory: the reef crab's build is not edited); the crusher's fixed finger
    # (the reef crab's "shell" slot, which here is the salt crust) is salt, not coral
    rc.PAL = dict(rc.PAL)
    rc.PAL["laterite"] = LEG_PALE
    rc.PAL["tortoiseshell"] = LEG_DARK
    rc.PAL["coral_stone_weathered"] = SALT / 0.92
    crust(mesh, rig, rng)
    timbers(mesh, rig, rng)
    lamp(mesh, rig, rng)
    finish = rc.ck.finish
    # the leg segments by bone: (from, to, which), to find the joints the salt cakes on
    leg_seg = {}
    for tag in "lr":
        for i in range(4):
            for seg in "ab":
                b = rig.bones[rig.index(f"leg_{tag}{i}_{seg}")]
                leg_seg[rig.index(f"leg_{tag}{i}_{seg}")] = (np.asarray(b.head), np.asarray(b.tail), seg)

    def leg_salt(P, T, bone):
        """On a leg segment: (salt ring, barnacle nodule, nodule rim, outward push). Salt cakes in rings at the
        joints (the knee, the hip, and the carpus halfway down the lower leg) where the wrecks' brine pools and
        dries, and a few barnacles sit on the upper segments, all lifted off the chitin so they read in battle."""
        h, tl, seg = leg_seg[bone]
        d = tl - h
        t = np.clip(((P - h) @ d) / float(d @ d), 0.0, 1.0)
        if seg == "a":
            ring = np.maximum(ck.smoothstep(0.85, 0.97, t), ck.smoothstep(0.15, 0.03, t))
        else:  # the tube's rings sit every sixth of the segment: one ring of vertices per band keeps them crisp
            ring = np.maximum(ck.smoothstep(0.12, 0.02, t), ck.smoothstep(0.1, 0.02, np.abs(t - 0.5)))
        ring = ring * (0.75 + 0.5 * ck.fbm(P * 17.0, SEED + 122)).clip(0.0, 1.0)
        n = ck.value_noise(P * 26.0, SEED + 123)
        up = ck.smoothstep(0.08, 0.2, P[:, 1]) * (1.0 - ring)
        nod = ck.smoothstep(0.4, 0.6, n) * up
        rim = ck.smoothstep(0.1, 0.35, n) * up * (1.0 - nod)
        push = 0.02 * ring + 0.022 * nod
        return ring, nod, rim, ck.vertex_normals(P, T) * push[:, None]

    def salted(mesh_, P, T, mat, color, bones, **kw):
        if mat != "chitin":
            return finish(mesh_, P, T, mat, color, bones, **kw)
        P = np.asarray(P, dtype=np.float64)
        col = np.broadcast_to(np.asarray(color, dtype=np.float64), (len(P), 3))
        salt = ck.smoothstep(0.02, 0.3, ck.fbm(P * 13.0, SEED + 120)) * ck.smoothstep(0.02, 0.2, P[:, 1])
        cav = np.asarray(kw.get("cavity", 0.0)) + 0.7 * salt * (1.0 - salt)  # crusty edges
        amount = 0.7 * salt
        if isinstance(bones, int) and bones in leg_seg:
            ring, nod, rim, push = leg_salt(P, np.asarray(T), bones)
            col = col * (0.72 + 0.28 * salt - 0.3 * rim)[:, None]  # bare chitin darker, so the salt reads
            amount = np.maximum(amount, 0.95 * np.clip(1.4 * np.maximum(ring, nod), 0.0, 1.0))
            cav = cav + 0.7 * rim + 0.6 * ring * (1.0 - ring)
            P = P + push
        col = ck.mix(col, SALT, amount[:, None]) * (0.92 + 0.1 * ck.fbm(P * 31.0, SEED + 121))[:, None]
        kw["cavity"] = np.clip(cav, 0.0, 1.0)
        kw["wet"] = np.asarray(kw.get("wet", 0.0)) * (1.0 - amount)
        return finish(mesh_, P, T, mat, col, bones, **kw)

    rc.ck.finish = salted
    try:
        rc.eyes(mesh, rig)
        rc.legs(mesh, rig)
        rc.claws(mesh, rig, rng)
    finally:
        rc.ck.finish = finish
    return mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = rc.build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, rc.build_clips(), args.out, extras={"hymn_creature": "wreck_crab"})
    print(f"wreck_crab: {info}")


if __name__ == "__main__":
    main()
