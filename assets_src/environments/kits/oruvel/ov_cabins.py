"""Oruvel's cabins, the stall and the open-throat lintel-gull (oruvel.md §2). Pure numpy; see ov_common.py.

  cabin_keelroof    4.0 x 5.6 m cabin of salvaged hull planks (three old paints in patches) under an upturned 7 m
                    hull: the keel is the ridge (top at KEELROOF_RIDGE_Y), stem and stern overhang the gables; a door
                    with a canvas curtain on +X, a shuttered window on -X, the eave lamp rail with a hung lantern;
                    origin at the floor's middle (it stands on a deck)
  cabin_patched     3.6 x 4.2 m plank cabin under a lean-to plank roof (high side -X at 3.0 m, eave +X at 2.2 m), its
                    walls patched with Lit Age ceramic panels and brass sheet, a water jar by the door, a laundry line
                    on a pole to +X
  stall_awning      3.0 x 2.0 m stall: a plank counter on crates facing +X under a patched, striped awning on four
                    oars, baskets, a jar and a hung lantern
  lintel_gull_open  Haluna's crying lintel-gull (village.py, read-only) at 0.70 m with its throat bored hollow: a dark
                    bore mouth between the open mandibles and a round wind-hole at the nape, their rims cut sharp;
                    faces local +X (the sea), origin on its perch's base
"""

from __future__ import annotations

import math

import numpy as np

import ov_common as oc

kc = oc.kc

TRI_BUDGET = {
    "cabin_keelroof": (10000, 600),
    "cabin_patched": (10000, 500),
    "stall_awning": (5000, 300),
    "lintel_gull_open": (3600, 420),  # the O10 hero close-up carving (village.lintel_gull fine)
}

KEELROOF = (8.0, 4.8, 1.1, 2.32, 0.28)  # roof hull length, beam, depth, eave height, sheer
KEELROOF_RIDGE_Y = KEELROOF[3] + KEELROOF[2] + 0.08  # the keel's top amidships
KEELROOF_GULL_Z = 2.9  # the gull perches near the keel's south end (local +Z), over the gable, facing the sea
CABIN_W, CABIN_D, WALL_H = 3.6, 5.6, 2.15
GULL_LEN = 0.70


def _gable_top(z_wall: float):
    L, B, D, eave, sheer = KEELROOF
    return lambda s: oc.keel_roof_underside(-CABIN_W * 0.5 + s, z_wall, L, B, D, eave, sheer)


def build_cabin_keelroof(seed: int = 721) -> list[kc.MeshBuilder]:
    out = []
    hw, hd = CABIN_W * 0.5, CABIN_D * 0.5
    L, B, D, eave, sheer = KEELROOF
    walls = (oc.M_TIMBER, oc.M_PAINT_RED, oc.M_PAINT, oc.M_PAINT_OCHRE)
    for lod in (False, True):
        rng = kc.rng_for("cabin_keelroof", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("cabin_keelroof" + (oc.LOD if lod else ""))
        dark = mb.material(oc.M_DARK)
        # The interior: a dark box just inside the walls, so the door and window read as shade.
        kc.polygon_prism(mb, np.array([[-hw + 0.08, -hd + 0.08], [hw - 0.08, -hd + 0.08], [hw - 0.08, hd - 0.08],
                                       [-hw + 0.08, hd - 0.08]]), 0.0, WALL_H + 0.25, dark,
                         col=np.array([0.0, 0.0, 0.0, 0.3]), uv2=np.array([0.3, 0.5]))
        door = (hd - 0.5, hd + 0.5, 0.0, 1.95)
        window = (3.4, 4.3, 1.0, 1.72)
        oc.plank_wall(mb, (hw, -hd), (hw, hd), 0.0, WALL_H, (1.0, 0.0), rng, noise, openings=[door], slots=walls,
                      lod=lod)
        oc.plank_wall(mb, (-hw, hd), (-hw, -hd), 0.0, WALL_H, (-1.0, 0.0), rng, noise, openings=[window], slots=walls,
                      lod=lod)
        for zw, sgn in ((-hd, -1.0), (hd, 1.0)):
            top = _gable_top(zw)
            oc.plank_wall(mb, (-hw, zw), (hw, zw), 0.0, eave + D, (0.0, sgn), rng, noise, slots=walls, top_fn=top,
                          lod=lod)
        oc.keel_roof(mb, L, B, D, eave, rng, noise, lod=lod, paint=oc.M_PAINT_TEAL, sheer=sheer)
        if not lod:
            for cx in (-hw, hw):
                for cz in (-hd, hd):
                    oc.village.post(mb, (cx, -0.05, cz), (cx, eave + 0.02, cz), 0.07, rng, noise, weather=oc.SUN)
            # The door's canvas curtain, half drawn; the doorstep; the window's shutter swung open.
            oc.canvas(mb, [(hw - 0.05, 1.95, -0.48), (hw - 0.05, 1.95, -0.02), (hw - 0.02, 0.15, -0.08),
                           (hw - 0.02, 0.15, -0.46)], 0.04, oc.M_CANVAS_TEAL, nu=4, nv=5)
            kc.plank(mb, (hw + 0.2, 0.03, -0.6), (hw + 0.2, 0.03, 0.6), 0.3, 0.06, mb.material(oc.M_TIMBER),
                     variation=0.6, noise=noise)
            wz0 = -hd + window[0]
            kc.rounded_block(mb, (-hw - 0.45, 1.36, wz0 - 0.05), (0.42, 0.37, 0.025), mb.material(oc.M_PAINT_RED),
                             rot=kc.rot_y(math.radians(78.0)), radius=0.01, seg=1, noise=noise, disp_m=0.004)
            # The eave lamp rail on the door side: an iron bar with hooks, one lantern hung by the door.
            iron = mb.material(oc.M_IRON)
            kc.tube(mb, np.array([[hw + 0.14, eave - 0.12, -hd + 0.4], [hw + 0.14, eave - 0.12, hd - 0.9]]), 0.012, 4,
                    iron, cap_start=True, cap_end=True)
            for zh in np.linspace(-hd + 0.7, hd - 1.1, 5):
                kc.tube(mb, np.array([[hw + 0.14, eave - 0.12, zh], [hw + 0.16, eave - 0.24, zh],
                                      [hw + 0.2, eave - 0.2, zh]]), 0.007, 4, iron)
            oc.lantern(mb, (hw + 0.17, eave - 0.56, 0.9), rng)
            # A coil and a basket by the door, a second lantern hook by the door frame (empty).
            oc.coil(mb, (hw + 0.5, 0.0, -hd + 0.8), 0.22, mb.material(oc.M_ROPE), turns=5)
            oc.basket(mb, (hw + 0.45, 0.0, hd + 0.75), 0.22, 0.3, rng)
            kc.tube(mb, np.array([[hw + 0.04, 1.75, -0.62], [hw + 0.12, 1.75, -0.62],
                                  [hw + 0.13, 1.68, -0.62]]), 0.008, 4, iron)
        out.append(mb)
    return out


def build_cabin_patched(seed: int = 722) -> list[kc.MeshBuilder]:
    out = []
    w, d = 3.6, 4.2
    hw, hd = w * 0.5, d * 0.5
    y_hi, y_lo = 3.0, 2.2

    def roof_y(x: float) -> float:
        return y_hi + (y_lo - y_hi) * (x + hw) / w

    walls = (oc.M_TIMBER, oc.M_TIMBER, oc.M_PAINT_WHITE, oc.M_PAINT)
    for lod in (False, True):
        rng = kc.rng_for("cabin_patched", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("cabin_patched" + (oc.LOD if lod else ""))
        timber = mb.material(oc.M_TIMBER)
        dark = mb.material(oc.M_DARK)
        kc.polygon_prism(mb, np.array([[-hw + 0.08, -hd + 0.08], [hw - 0.08, -hd + 0.08], [hw - 0.08, hd - 0.08],
                                       [-hw + 0.08, hd - 0.08]]), 0.0, y_lo - 0.05, dark,
                         col=np.array([0.0, 0.0, 0.0, 0.3]), uv2=np.array([0.3, 0.5]))
        door = (hd - 1.4, hd - 0.5, 0.0, 1.9)
        oc.plank_wall(mb, (hw, -hd), (hw, hd), 0.0, y_lo - 0.02, (1.0, 0.0), rng, noise, openings=[door], slots=walls,
                      lod=lod)
        oc.plank_wall(mb, (-hw, hd), (-hw, -hd), 0.0, y_hi - 0.02, (-1.0, 0.0), rng, noise, slots=walls, lod=lod)
        for zw, sgn in ((-hd, -1.0), (hd, 1.0)):
            oc.plank_wall(mb, (-hw, zw), (hw, zw), 0.0, y_hi, (0.0, sgn), rng, noise, slots=walls,
                          top_fn=lambda s: roof_y(-hw + s) - 0.04,
                          openings=[(1.2, 2.0, 1.05, 1.65)] if sgn > 0 else [], lod=lod)
        # The lean-to roof: boards running down the slope, overhanging 0.35 m at the eave and 0.15 at the back.
        x0, x1 = -hw - 0.15, hw + 0.35
        if lod:
            kc.plank(mb, (x0, roof_y(x0) + 0.05, 0.0), (x1, roof_y(x1) + 0.05, 0.0), d + 0.5, 0.06, timber)
        else:
            nb = int((d + 0.5) / 0.24)
            slot = timber
            for k in range(nb):
                z = -hd - 0.25 + (k + 0.5) * (d + 0.5) / nb
                if rng.random() < 0.3:
                    slot = timber if rng.random() < 0.7 else mb.material(oc.PAINTS[int(rng.integers(0, 5))])
                dy = 0.02 * (k % 2)
                kc.plank(mb, (x0, roof_y(x0) + 0.05 + dy, z), (x1, roof_y(x1) + 0.05 + dy, z),
                         (d + 0.5) / nb + 0.02, 0.035, slot, up=kc.normalize(np.array([(y_hi - y_lo) / w, 1.0, 0.0])),
                         weather=oc.SUN, variation=float(rng.random()), noise=noise, seg=2)
            for xr in (x0 + 0.3, 0.0, x1 - 0.4):  # purlins under the boards
                kc.plank(mb, (xr, roof_y(xr) - 0.04, -hd - 0.25), (xr, roof_y(xr) - 0.04, hd + 0.25), 0.08, 0.1,
                         timber, variation=float(rng.random()), noise=noise)
            # Salvage patches: Lit Age ceramic panels on the walls and roof, a brass sheet over a rotten board.
            for c, n, pw, ph in (((hw + 0.04, 0.9, -1.2), (1, 0, 0), 0.6, 0.6), ((hw + 0.04, 1.5, -0.55), (1, 0, 0),
                                                                                    0.6, 0.6),
                                 ((-0.4, 1.2, hd + 0.04), (0, 0, 1), 0.6, 0.6), ((0.6, 0.55, -hd - 0.04), (0, 0, -1),
                                                                                  0.6, 0.6),
                                 ((-hw - 0.04, 2.1, 0.7), (-1, 0, 0), 0.6, 0.6),
                                 ((-hw - 0.04, 1.5, 0.7), (-1, 0, 0), 0.6, 0.6)):
                oc.ceramic_panel(mb, c, pw, ph, n, rng, noise)
            for zc in (-0.9, -0.25):
                c = np.array([0.3, roof_y(0.3) + 0.1, zc])
                kc.rounded_block(mb, c, (0.3, 0.018, 0.3), mb.material(oc.M_CERAMIC),
                                 rot=kc.rot_z(-math.atan((y_hi - y_lo) / w)), radius=0.01, seg=1, noise=noise,
                                 disp_m=0.004)
            kc.rounded_block(mb, (-0.8, 0.75, -hd - 0.035), (0.45, 0.3, 0.008), mb.material(oc.M_BRASS), radius=0.004,
                             seg=1, noise=noise, disp_m=0.006, disp_period_m=0.15)
            for cx in (-hw, hw):
                for cz in (-hd, hd):
                    oc.village.post(mb, (cx, -0.05, cz), (cx, roof_y(cx) - 0.02, cz), 0.065, rng, noise,
                                    weather=oc.SUN)
            # The water jar by the door, the laundry line out to a pole on +X with four cloths pegged on it.
            oc.jar(mb, (hw + 0.4, 0.0, hd - 0.15), 0.75, rng)
            pole = np.array([hw + 3.0, 0.0, -0.6])
            oc.village.post(mb, pole - np.array([0.0, 0.1, 0.0]), pole + np.array([0.0, 2.3, 0.0]), 0.05, rng, noise,
                            weather=oc.SUN)
            a = np.array([hw + 0.05, 2.05, -0.9])
            b = pole + np.array([0.0, 2.2, 0.0])
            rope = mb.material(oc.M_ROPE)
            oc.rope(mb, a, b, 0.18, 0.009, rope, n=10)
            for f, slot, cw, ch in ((0.2, oc.M_CANVAS_TEAL, 0.5, 0.7), (0.42, oc.M_CANVAS, 0.42, 0.9),
                                    (0.62, oc.M_CANVAS_RED, 0.55, 0.6), (0.82, oc.M_CANVAS, 0.35, 0.5)):
                p = a + (b - a) * f - np.array([0.0, 4.0 * 0.18 * f * (1 - f), 0.0])
                dv = kc.normalize(b - a) * cw * 0.5
                oc.canvas(mb, [p - dv, p + dv, p + dv - np.array([0, ch, 0]) + np.array([0.02, 0, 0.05]),
                               p - dv - np.array([0, ch, 0]) + np.array([0.02, 0, 0.05])], -0.03, slot, nu=3, nv=3)
        out.append(mb)
    return out


def build_stall_awning(seed: int = 723) -> list[kc.MeshBuilder]:
    out = []
    w, d = 3.0, 2.0
    hw, hd = d * 0.5, w * 0.5  # counter faces +X: x across the stall's depth, z along its front
    for lod in (False, True):
        rng = kc.rng_for("stall_awning", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("stall_awning" + (oc.LOD if lod else ""))
        timber = mb.material(oc.M_TIMBER)
        # Four oars as poles (front 2.3 m, back 2.0 m), blade up on the front pair.
        poles = [(hw, -hd, 2.3), (hw, hd, 2.3), (-hw, -hd, 2.0), (-hw, hd, 2.0)]
        for x, z, h in poles:
            if lod:
                kc.tube(mb, np.array([[x, 0.0, z], [x, h, z]]), 0.04, 4, timber)
            else:
                kc.tube(mb, np.array([[x, -0.02, z], [x, h, z]]), 0.035, 6, timber, cap_end=True,
                        variation=float(rng.random()))
                if h > 2.1:
                    kc.rounded_block(mb, (x, h + 0.18, z), (0.025, 0.25, 0.09), timber, radius=0.01, seg=1,
                                     variation=float(rng.random()))
        oc.canvas(mb, [(hw + 0.35, 2.28, -hd - 0.15), (hw + 0.35, 2.28, hd + 0.15), (-hw - 0.1, 2.02, hd + 0.15),
                       (-hw - 0.1, 2.02, -hd - 0.15)], 0.07, oc.M_CANVAS, nu=3 if lod else 9, nv=3 if lod else 5,
                  stripes=None if lod else oc.M_CANVAS_TEAL, stripe_n=7, double=not lod)
        # The counter: two crates and a board along the front; baskets and a jar on and behind it.
        for zc in (-0.9, 0.9):
            oc.crate(mb, (hw - 0.3, 0.38, zc), (0.28, 0.38, 0.32), rng, noise, lod=lod)
        kc.plank(mb, (hw - 0.3, 0.8, -hd + 0.05), (hw - 0.3, 0.8, hd - 0.05), 0.55, 0.05, timber,
                 variation=float(rng.random()), noise=None if lod else noise)
        if not lod:
            oc.basket(mb, (hw - 0.35, 0.825, -0.6), 0.2, 0.16, rng)
            oc.basket(mb, (hw - 0.3, 0.825, 0.35), 0.17, 0.14, rng)
            oc.jar(mb, (-hw + 0.3, 0.0, -0.9), 0.6, rng)
            oc.basket(mb, (-hw + 0.35, 0.0, 0.6), 0.25, 0.32, rng)
            oc.crate(mb, (-hw + 0.4, 0.22, 0.0), (0.25, 0.22, 0.3), rng, noise, yaw=0.3)
            kc.tube(mb, np.array([[hw + 0.1, 2.1, 0.4], [hw + 0.1, 1.85, 0.4]]), 0.006, 4, mb.material(oc.M_IRON))
            oc.lantern(mb, (hw + 0.1, 1.55, 0.4), rng)
        out.append(mb)
    return out


PERCH_TRIS = 12  # village.lintel_gull's last primitive: the perch block (a rounded_block, seg 1)


def _signed_volume(mb: kc.MeshBuilder, t0: int, t1: int) -> float:
    p = np.asarray(mb.pos)
    t = np.asarray(mb.tris[t0:t1])
    c = p.mean(axis=0)
    v0, v1, v2 = p[t[:, 0]] - c, p[t[:, 1]] - c, p[t[:, 2]] - c
    return float(np.einsum("ij,ij->i", v0, np.cross(v1, v2)).sum() / 6.0)


def _turn_lofts_outward(mb: kc.MeshBuilder) -> None:
    """A guard: village.lintel_gull's lofts came out wound inside-out until M2-ENV-12 fixed them at the source, so
    a back-face-culled material showed their inner faces. If their signed volume is ever negative again, this turns
    them outward: the windings of every triangle before the perch reversed, their normals negated. Now a no-op."""
    n_loft = mb.triangle_count - PERCH_TRIS
    if _signed_volume(mb, 0, n_loft) >= 0.0:
        return
    verts = sorted({i for tri in mb.tris[:n_loft] for i in tri})
    for k in range(n_loft):
        a, b, c = mb.tris[k]
        mb.tris[k] = (a, c, b)
    for i in verts:
        mb.nrm[i] = [-v for v in mb.nrm[i]]


def build_lintel_gull_open(seed: int = 34) -> list[kc.MeshBuilder]:
    """Haluna's crying gull, read-only (village.lintel_gull), with the throat bored through (C1-11)."""
    out = []
    s = GULL_LEN / 0.72
    for lod in (False, True):
        mb = oc.village.lintel_gull("lintel_gull_open" + (oc.LOD if lod else ""), "crying", GULL_LEN, seed, lod=lod,
                                    fine=True)
        mb.name = "lintel_gull_open" + (oc.LOD if lod else "")
        _turn_lofts_outward(mb)
        carved, dark = mb.material(oc.M_CARVED), mb.material(oc.M_DARK)
        head_c = np.array([0.30 * s, 0.39 * s, 0.0])  # village.py: the crying pose's head centre
        mouth = head_c + np.array([0.052 * s, -0.004 * s, 0.0])  # between the open mandibles, at the beak's root
        nape = head_c + np.array([-0.047 * s, 0.012 * s, 0.0])
        oc.disc(mb, mouth + np.array([0.004, 0.0, 0.0]), (1.0, 0.18, 0.0), 0.017 * s, dark, sides=6 if lod else 10)
        oc.disc(mb, nape, (-1.0, 0.25, 0.0), 0.021 * s, dark, sides=6 if lod else 10)
        if not lod:
            oc.ring(mb, mouth + np.array([0.003, 0.0, 0.0]), (1.0, 0.18, 0.0), 0.018 * s, 0.0035 * s, carved, segs=10)
            oc.ring(mb, nape + np.array([-0.002, 0.0, 0.0]), (-1.0, 0.25, 0.0), 0.022 * s, 0.004 * s, carved, segs=10)
        out.append(mb)
    return out


TARGETS = {
    "cabin_keelroof": build_cabin_keelroof,
    "cabin_patched": build_cabin_patched,
    "stall_awning": build_stall_awning,
    "lintel_gull_open": build_lintel_gull_open,
}
