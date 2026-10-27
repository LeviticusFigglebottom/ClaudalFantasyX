"""The drowned tower's shell and rooms (oruvel_underway.md §2): Lit Age cast coral-concrete clad in white ceramic,
four hundred years under the sea. Pure numpy; see ou_common.py.

  tower_bay          6.0 x 3.2 x 0.35 m wall bay: a 2.4 x 1.7 m window (sill 0.8 m), white ceramic cladding in a sill
                     band and a spandrel band on the outer face (+Z) with about half fallen, coral on the sill; the
                     inner face (-Z, the gallery's) with a cast skirting, a stepped cornice, pier fillets, the window's
                     reveal framed and growth crusted low (M3-ENV-705)
  tower_bay_solid    the same bay without a window (a recessed panel): the facade's rhythm
  tower_bay_broken   the top broken away along a falling line, a bite out of one pier, rebar stubs: the crown
  tower_pier         a 0.7 m chamfered corner column, 3.2 m
  floor_slab         6 x 6 x 0.3 m slab, origin at its top (the floor level), coffered underside, silt on top
  floor_slab_broken  cracked through: one part in place, the other hanging 24 deg on its rebar; a 1.9 m slot between
                     them is a tether drop
  bell_room          a 6 x 6 x 3.2 m sealed room (door on +Z): dry pale walls above the air line (0.7 m under the
                     ceiling), a calcite tide-ring at the line, calcite drips from the ceiling
  current_shaft      one storey of a 2.6 m cast duct (14 staves, two vents) with brass bands, a grating and weed
                     streaming upward: stacks
  stair_flight       one straight flight 3.2 m down over 6.0 m along +X with a half landing, side walls, a broken
                     balustrade on -Z; origin at the lip
"""

from __future__ import annotations

import math

import numpy as np

import ou_common as oc

kc = oc.kc
BAY_W = 6.0
STOREY = 3.2
WALL_T = 0.35
WIN = (-1.2, 1.2, 0.8, 2.5)  # x0, x1, y0, y1
AIR_LINE = STOREY - 0.7

TRI_BUDGET = {
    "tower_bay": (3500, 200),
    "tower_bay_solid": (3500, 200),
    "tower_bay_broken": (4500, 200),
    "tower_pier": (900, 60),
    "floor_slab": (3500, 200),
    "floor_slab_broken": (5000, 200),
    "bell_room": (8000, 600),
    "current_shaft": (8000, 600),
    "stair_flight": (8000, 600),
}


def _clamp_y(mb: kc.MeshBuilder, start: int, top_fn, noise) -> None:
    """Pulls every vertex above top_fn(x, z) down onto it (a broken top), marking it eroded."""
    p = np.asarray(mb.pos[start:])
    lim = top_fn(p[:, 0], p[:, 2])
    over = p[:, 1] > lim
    jitter = (noise.fbm(p / 0.09, 2) - 0.5) * 0.08
    p[:, 1] = np.where(over, lim + jitter, p[:, 1])
    mb.pos[start:] = p.tolist()
    col = np.asarray(mb.col[start:])
    col[:, 3] = np.where(over, 1.0, col[:, 3])
    mb.col[start:] = col.tolist()


def _rebar_up(mb: kc.MeshBuilder, root, rng, *, length: float, radius: float = 0.011, out=(0.0, 1.0, 0.0)) -> None:
    """A rusted bar leaving the concrete at `root`, bending over under its own corrosion."""
    d = kc.normalize(np.asarray(out, float))
    pts = [np.asarray(root, float) - d * 0.05]
    for k in range(1, 5):
        d = kc.normalize(d + np.array([rng.normal(0, 0.18), -0.35 * k / 4, rng.normal(0, 0.18)]))
        pts.append(pts[-1] + d * length / 4)
    kc.tube(mb, np.asarray(pts), np.linspace(radius, radius * 0.7, 5), 4, mb.material(oc.M_REBAR),
            weather=oc.DROWNED, cap_end=True, variation=float(rng.random()))


def _cladding(mb: kc.MeshBuilder, rng, noise, *, keep_above: float = 0.5, top_fn=None) -> None:
    """White ceramic cladding on the outer face, in two bands that run the bay's whole width: the sill band (0 to
    0.8 m) and the spandrel band (2.5 to 3.2 m), in 0.6 m panels, so the storeys read as pale ribbons with the cast
    piers bare between them. About half the panels have fallen, in runs (where the noise field is low); a few hang
    popped off their fixings."""
    mat = mb.material(oc.M_CERAMIC)
    z = WALL_T * 0.5 + 0.014
    for y0, y1 in ((0.0, WIN[2]), (WIN[3], STOREY)):
        n = int(round(BAY_W / 0.6))
        pw, ph = BAY_W / n, y1 - y0
        for i in range(n):
            cx, cy = -BAY_W * 0.5 + (i + 0.5) * pw, (y0 + y1) * 0.5
            gone = noise.fbm(np.array([cx / 1.4, cy * 0.3, 5.0]), 2) + rng.uniform(-0.08, 0.08)
            if gone < keep_above or (top_fn is not None and y1 > float(top_fn(cx, 0.0))):
                continue
            popped = rng.random() < 0.07
            rot = kc.rot_x(rng.uniform(0.1, 0.3)) if popped else kc.rot_z(rng.normal(0, 0.006))
            oc.block(mb, (cx, cy, z + (0.03 if popped else 0.0)), (pw * 0.5 - 0.01, ph * 0.5 - 0.02, 0.012), mat,
                     rng=rng, rot=rot, seg=1, radius=0.006, weather=oc.CAST)


def _inner_face(mb: kc.MeshBuilder, rng, noise, *, window: bool, top_fn=None) -> None:
    """The gallery's side (-Z), which the fight sees: a cast skirting and a stepped cornice the bay's whole width, a
    fillet down each pier's inner edge, the window's reveal framed, and growth crusted low on the wall where the silt
    settles. Everything above a broken top is left off."""
    mat = mb.material(oc.M_CONCRETE)
    z = -WALL_T * 0.5
    top = (lambda x: float(top_fn(np.array(x), 0.0))) if top_fn is not None else (lambda x: STOREY)
    kw = dict(rng=rng, noise=noise, seg=1, weather=oc.CAST)
    oc.block(mb, (0.0, 0.11, z - 0.03), (BAY_W * 0.5, 0.11, 0.035), mat, radius=0.012, **kw)
    if top_fn is None:  # a broken bay has lost its cornice with its top
        oc.block(mb, (0.0, STOREY - 0.1, z - 0.04), (BAY_W * 0.5, 0.1, 0.045), mat, radius=0.015, **kw)
        oc.block(mb, (0.0, STOREY - 0.25, z - 0.02), (BAY_W * 0.5, 0.05, 0.025), mat, radius=0.01, **kw)
    for x in (-2.82, -1.38, 1.38, 2.82):
        if window or abs(x) > 2.0:
            y1 = min(STOREY - 0.3, top(x) - 0.05)
            if y1 > 0.5:
                oc.block(mb, (x, (0.22 + y1) * 0.5, z - 0.02), (0.06, (y1 - 0.22) * 0.5, 0.025), mat, radius=0.01,
                         **kw)
    if window:
        x0, x1, y0, y1 = WIN
        oc.block(mb, (0.0, y0 - 0.04, z - 0.03), ((x1 - x0) * 0.5 + 0.12, 0.04, 0.04), mat, radius=0.012, **kw)
        if top_fn is None:
            oc.block(mb, (0.0, y1 + 0.06, z - 0.03), ((x1 - x0) * 0.5 + 0.12, 0.06, 0.04), mat, radius=0.012, **kw)
    # Growth: sponges and coral crust low on the wall, thinning upward.
    for _k in range(9):
        x = float(rng.uniform(-2.8, 2.8))
        y = float(rng.uniform(0.25, 1.6) ** 1.4)
        if window and WIN[0] < x < WIN[1] and y > WIN[2] - 0.05:
            continue
        if y > top(x) - 0.2:
            continue
        slot = oc.CORALS[int(rng.integers(0, len(oc.CORALS)))]
        oc.coral_knob(mb, (x, y, z - 0.02), float(rng.uniform(0.05, 0.12)), rng, noise, slot, squash=0.35)


def _sill_growth(mb: kc.MeshBuilder, rng, noise, y: float, x0: float, x1: float, count: int) -> None:
    for _k in range(count):
        x = rng.uniform(x0 + 0.15, x1 - 0.15)
        slot = oc.CORALS[int(rng.integers(0, 4))]
        if rng.random() < 0.4:
            oc.branch_coral(mb, (x, y, rng.uniform(0.0, 0.12)), rng, slot, height=rng.uniform(0.08, 0.16), depth=2,
                            radius=0.012)
        else:
            oc.coral_knob(mb, (x, y + 0.02, rng.uniform(-0.05, 0.12)), rng.uniform(0.05, 0.1), rng, noise, slot)


def bay(name: str, seed: int, *, window: bool = True, broken: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name)
    mat = mb.material(oc.M_CONCRETE)
    t = WALL_T * 0.5
    start = mb.vertex_count
    kw = dict(rng=rng, noise=noise, disp_m=0.03, period=0.5, weather=oc.DROWNED)
    oc.block(mb, (-2.1, STOREY * 0.5, 0.0), (0.9, STOREY * 0.5, t), mat, seg=5, **kw)
    oc.block(mb, (2.1, STOREY * 0.5, 0.0), (0.9, STOREY * 0.5, t), mat, seg=5, **kw)
    if window:
        oc.block(mb, (0.0, WIN[2] * 0.5, 0.0), (1.22, WIN[2] * 0.5, t), mat, seg=3, **kw)
        if not broken:  # broken: the window's head is gone with the top
            oc.block(mb, (0.0, (WIN[3] + STOREY) * 0.5, 0.0), (1.22, (STOREY - WIN[3]) * 0.5, t), mat, seg=3, **kw)
    else:
        # A recessed panel between the piers (a blind bay).
        oc.block(mb, (0.0, STOREY * 0.5, -0.06), (1.22, STOREY * 0.5, t - 0.06), mat, seg=4, **kw)
    top_fn = None
    if broken:
        fall = rng.uniform(1.2, 2.2) * (1 if rng.random() < 0.5 else -1)

        def top_fn(x, _z, fall=fall):
            x = np.asarray(x, float)
            n = noise.fbm(np.stack([x * 1.1, np.full_like(x, 3.0), np.zeros_like(x)], axis=-1), 3)
            bite = 0.7 * np.exp(-((x - 2.0 * np.sign(fall)) / 0.6) ** 2)
            return STOREY - 0.35 - 0.8 * n - fall * 0.35 * (x / BAY_W + 0.5) - bite

        _clamp_y(mb, start, top_fn, noise)
        kc.recompute_normals(mb, start, 0)
        for x in np.arange(-2.9, 2.9, 0.22):
            if rng.random() < 0.5:
                continue
            y0 = float(top_fn(np.array(x), 0.0)) - 0.04
            for zz in (-t * 0.5, t * 0.5):
                if rng.random() < 0.55:
                    _rebar_up(mb, (x, y0, zz), rng, length=rng.uniform(0.15, 0.6))
    _cladding(mb, rng, noise, top_fn=top_fn)
    _inner_face(mb, rng, noise, window=window, top_fn=top_fn)
    if window and not broken:
        _sill_growth(mb, rng, noise, WIN[2], WIN[0], WIN[1], 4)
        if rng.random() < 0.6:
            # A bent iron mullion left in the opening.
            x = rng.uniform(-0.6, 0.6)
            kc.tube(mb, np.array([[x, WIN[2], 0.0], [x + 0.05, 1.5, 0.02], [x + 0.25, 2.1, 0.12]]), 0.018, 5,
                    mb.material(oc.M_IRON), weather=oc.DROWNED, cap_end=True)
    elif window:
        _sill_growth(mb, rng, noise, WIN[2], WIN[0], WIN[1], 3)
    return mb


def _bay_lod(name: str, *, window: bool, broken: bool) -> kc.MeshBuilder:
    lod = kc.MeshBuilder(name + oc.LOD)
    m = lod.material(oc.M_CONCRETE)
    h = STOREY - (1.0 if broken else 0.0)
    if window:
        for c, half in (((-2.1, h * 0.5, 0), (0.9, h * 0.5, WALL_T * 0.5)), ((2.1, h * 0.5, 0), (0.9, h * 0.5, WALL_T * 0.5)),
                        ((0, WIN[2] * 0.5, 0), (1.2, WIN[2] * 0.5, WALL_T * 0.5))):
            kc.rounded_block(lod, c, half, m, seg=1, radius=0.02)
        if not broken:
            kc.rounded_block(lod, (0, (WIN[3] + STOREY) * 0.5, 0), (1.2, (STOREY - WIN[3]) * 0.5, WALL_T * 0.5), m, seg=1,
                             radius=0.02)
    else:
        kc.rounded_block(lod, (0, h * 0.5, 0), (3.0, h * 0.5, WALL_T * 0.5), m, seg=1, radius=0.02)
    return lod


def build_bay(seed: int = 601) -> list[kc.MeshBuilder]:
    return [bay("tower_bay", seed), _bay_lod("tower_bay", window=True, broken=False)]


def build_bay_solid(seed: int = 602) -> list[kc.MeshBuilder]:
    return [bay("tower_bay_solid", seed, window=False), _bay_lod("tower_bay_solid", window=False, broken=False)]


def build_bay_broken(seed: int = 603) -> list[kc.MeshBuilder]:
    return [bay("tower_bay_broken", seed, broken=True), _bay_lod("tower_bay_broken", window=True, broken=True)]


def build_pier(seed: int = 604) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("tower_pier", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("tower_pier")
    oc.block(mb, (0, STOREY * 0.5, 0), (0.35, STOREY * 0.5, 0.35), mb.material(oc.M_CONCRETE), rng=rng, noise=noise,
             seg=4, radius=0.06, disp_m=0.03, period=0.4)
    lod = kc.MeshBuilder("tower_pier" + oc.LOD)
    kc.rounded_block(lod, (0, STOREY * 0.5, 0), (0.35, STOREY * 0.5, 0.35), lod.material(oc.M_CONCRETE), seg=1, radius=0.05)
    return [mb, lod]


def _silt_dust(mb: kc.MeshBuilder, noise, x0: float, x1: float, z0: float, z1: float, y: float, n: int = 25) -> None:
    """Silt settled on a floor in drifts: one sheet that rises a few centimetres above the floor where the noise
    gathers it and sinks just under it elsewhere, so the drifts end in soft natural contours, not grid steps."""
    xs = np.linspace(x0, x1, n)
    zs = np.linspace(z0, z1, n)

    def h(X, Z):
        f = noise.fbm(np.stack([X / 1.4, np.full_like(X, 9.0), Z / 1.4], axis=-1), 3)
        return y - 0.025 + np.clip((f - 0.47) * 0.5, -0.02, 0.07)

    oc.heightfield(mb, xs, zs, h, mb.material(oc.M_SILT), erosion=0.2)


def _slab(mb: kc.MeshBuilder, rng, noise, x0: float, x1: float, *, coffers: bool = True) -> int:
    """A slab part spanning x0..x1 (z -3..3), its top at y 0; returns the first vertex index."""
    mat = mb.material(oc.M_CONCRETE)
    start = mb.vertex_count
    cx, hx = (x0 + x1) * 0.5, (x1 - x0) * 0.5
    oc.block(mb, (cx, -0.09, 0.0), (hx, 0.09, 3.0), mat, rng=rng, noise=noise, seg=6, disp_m=0.015, period=0.6)
    if coffers:
        for z in (-1.5, 1.5):
            oc.block(mb, (cx, -0.27, z), (hx, 0.1, 0.12), mat, rng=rng, noise=noise, seg=3, disp_m=0.01)
        for x in (-1.5, 1.5):
            if x0 < x < x1:
                oc.block(mb, (x, -0.27, 0.0), (0.12, 0.1, 2.88), mat, rng=rng, noise=noise, seg=3, disp_m=0.01)
    return start


def build_slab(seed: int = 605) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("floor_slab", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("floor_slab")
    _slab(mb, rng, noise, -3.0, 3.0)
    _silt_dust(mb, noise, -2.9, 2.9, -2.9, 2.9, 0.0)
    lod = kc.MeshBuilder("floor_slab" + oc.LOD)
    kc.rounded_block(lod, (0, -0.15, 0), (3.0, 0.15, 3.0), lod.material(oc.M_CONCRETE), seg=1, radius=0.02)
    return [mb, lod]


def build_slab_broken(seed: int = 606, tilt_deg: float = 24.0) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("floor_slab_broken", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("floor_slab_broken")
    # A: the part still on its beams, broken along a ragged line near x = -0.4.
    sa = _slab(mb, rng, noise, -3.0, -0.2)

    def edge_a(p):
        n = noise.fbm(np.column_stack([np.full(len(p), 2.0), p[:, 1] * 3.0, p[:, 2] * 1.4]), 3)
        return -0.25 - 0.55 * n

    p = np.asarray(mb.pos[sa:])
    lim = edge_a(p)
    over = p[:, 0] > lim
    p[:, 0] = np.where(over, lim, p[:, 0])
    mb.pos[sa:] = p.tolist()
    kc.recompute_normals(mb, sa, 0)
    _silt_dust(mb, noise, -2.9, -0.9, -2.9, 2.9, 0.0, n=11)
    # B: the far part, hinged on its support at x = 3 and hanging with its broken edge down.
    sub = kc.MeshBuilder("b")
    _slab(sub, rng, noise, 1.4, 3.0)
    pb = np.asarray(sub.pos)
    lim_b = 1.55 + 0.5 * noise.fbm(np.column_stack([np.full(len(pb), 6.0), pb[:, 1] * 3.0, pb[:, 2] * 1.4]), 3)
    pb[:, 0] = np.where(pb[:, 0] < lim_b, lim_b, pb[:, 0])
    sub.pos = pb.tolist()
    kc.recompute_normals(sub, 0, 0)
    a = math.radians(tilt_deg)
    hinge = np.array([3.0, 0.0, 0.0])
    rz = kc.rot_z(a)  # rotates +X toward +Y; about the hinge the free end (x < 3) goes down
    pts = (np.asarray(sub.pos) - hinge) @ rz.T + hinge
    sub.pos = pts.tolist()
    sub.nrm = (np.asarray(sub.nrm) @ rz.T).tolist()
    mb.merge(sub)
    # Rebar across the crack: from A's edge, hanging, and from B's edge, curling down.
    for z in np.arange(-2.8, 2.9, 0.3):
        if rng.random() < 0.35:
            continue
        x_a = float(edge_a(np.array([[0.0, -0.1, z]]))[0])
        _rebar_up(mb, (x_a, -0.12, z), rng, length=rng.uniform(0.3, 0.9), out=(1.0, -0.6, rng.normal(0, 0.2)))
        if rng.random() < 0.6:
            xb = 3.0 + (1.6 - 3.0) * math.cos(a)
            yb = -(3.0 - 1.6) * math.sin(a) - 0.1
            _rebar_up(mb, (xb, yb, z), rng, length=rng.uniform(0.2, 0.7), out=(-1.0, -0.8, rng.normal(0, 0.2)))
    # Growth on the high edges (the light reaches them).
    for _k in range(5):
        x = rng.uniform(-2.6, -0.8)
        oc.coral_knob(mb, (x, 0.02, rng.uniform(-2.7, 2.7)), rng.uniform(0.06, 0.12), rng, noise,
                      oc.CORALS[int(rng.integers(0, 4))])
    lod = kc.MeshBuilder("floor_slab_broken" + oc.LOD)
    kc.rounded_block(lod, (-1.6, -0.15, 0), (1.4, 0.15, 3.0), lod.material(oc.M_CONCRETE), seg=1, radius=0.02)
    return [mb, lod]


def build_bell_room(seed: int = 607) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("bell_room", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("bell_room")
    wet, ring, dry = mb.material(oc.M_CONCRETE), mb.material(oc.M_CALCITE), mb.material(oc.M_CONCRETE_DRY)
    t = 0.15
    lo, hi = AIR_LINE - 0.06, AIR_LINE + 0.06
    # Each wall: (centre x, centre z, half length, along x?) on the room's inner 6 m square.
    walls = [(0.0, -3.0 + t, 3.0, True), (-3.0 + t, 0.0, 3.0 - 2 * t, False), (3.0 - t, 0.0, 3.0 - 2 * t, False)]
    # The door wall (+Z): two parts either side of a 1.0 m door, and a lintel over it.
    for x0, x1 in ((-3.0, -0.5), (0.5, 3.0)):
        walls.append(((x0 + x1) * 0.5, 3.0 - t, (x1 - x0) * 0.5, True))
    for cx, cz, hl, along_x in walls:
        half = (hl, 0, t) if along_x else (t, 0, hl)
        for y0, y1, m, w, seg in ((0.0, lo, wet, oc.DROWNED, 4), (lo, hi, ring, oc.CAST, 2), (hi, STOREY, dry, oc.DRY, 3)):
            pad = 0.012 if m == ring else 0.0
            hh = (half[0] + (pad if not along_x else 0), (y1 - y0) * 0.5, half[2] + (pad if along_x else 0))
            oc.block(mb, (cx, (y0 + y1) * 0.5, cz), hh, m, rng=rng, noise=noise, seg=seg, disp_m=0.015, weather=w)
    oc.block(mb, (0.0, (2.1 + STOREY) * 0.5, 3.0 - t), (0.5, (STOREY - 2.1) * 0.5, t), dry, rng=rng, noise=noise,
             seg=2, weather=oc.DRY)
    # Calcite drips hanging from the ceiling (the slab above), thickest near the walls.
    for _k in range(14):
        x, z = rng.uniform(-2.6, 2.6, 2)
        if abs(x) < 2.0 and abs(z) < 2.0 and rng.random() < 0.6:
            continue
        L = rng.uniform(0.05, 0.22)
        oc.lathe(mb, [(0.0, -L), (0.012, -L * 0.6), (0.025, 0.0)], ring, sides=6,
                 center=(x, STOREY, z), weather=oc.CAST)
    lod = kc.MeshBuilder("bell_room" + oc.LOD)
    m = lod.material(oc.M_CONCRETE)
    for cx, cz, hl, along_x in walls:
        half = (hl, STOREY * 0.5, t) if along_x else (t, STOREY * 0.5, hl)
        kc.rounded_block(lod, (cx, STOREY * 0.5, cz), half, m, seg=1, radius=0.02)
    return [mb, lod]


SHAFT_R = 1.3
SHAFT_STAVES = 14
SHAFT_VENTS = (3, 10)


def build_shaft(seed: int = 608) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("current_shaft", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("current_shaft")
    mat = mb.material(oc.M_CONCRETE)
    w = 2 * math.pi * SHAFT_R / SHAFT_STAVES
    for k in range(SHAFT_STAVES):
        a = 2 * math.pi * k / SHAFT_STAVES
        c = np.array([math.sin(a) * SHAFT_R, 0.0, math.cos(a) * SHAFT_R])
        rot = kc.rot_y(a)
        if k in SHAFT_VENTS:
            # A vent: two short staves with a slotted gap where the tide breathes through.
            for y0, y1 in ((0.0, 0.9), (2.3, STOREY)):
                cc = c + np.array([0, (y0 + y1) * 0.5, 0])
                oc.block(mb, cc, (w * 0.5 - 0.006, (y1 - y0) * 0.5, 0.13), mat, rng=rng, noise=noise, rot=rot, seg=2,
                         disp_m=0.01)
            for y in (1.25, 1.6, 1.95):
                oc.block(mb, c + np.array([0, y, 0]), (w * 0.5 - 0.01, 0.04, 0.05), mb.material(oc.M_IRON), rng=rng,
                         rot=rot, seg=1, radius=0.01)
            continue
        oc.block(mb, c + np.array([0, STOREY * 0.5, 0]), (w * 0.5 - 0.006, STOREY * 0.5, 0.13), mat, rng=rng,
                 noise=noise, rot=rot, seg=3, disp_m=0.012)
    for y in (0.25, STOREY - 0.25):
        oc.ring(mb, (0, y, 0), SHAFT_R + 0.15, 0.035, mb.material(oc.M_BRASS), segs=40, sides=5)
        oc.ring(mb, (0, y, 0), SHAFT_R - 0.15, 0.03, mb.material(oc.M_BRASS), segs=40, sides=5)
    for x in np.linspace(-1.0, 1.0, 7):
        half_len = math.sqrt(max(SHAFT_R ** 2 - x ** 2, 0.0)) - 0.12
        oc.block(mb, (x, 0.03, 0.0), (0.025, 0.03, half_len), mb.material(oc.M_IRON), rng=rng, seg=1, radius=0.01)
    # Weed streaming up from the inner wall: the current runs upward.
    weed = mb.material(oc.M_WEED)
    for _k in range(16):
        a = rng.uniform(0, 2 * math.pi)
        y0 = rng.uniform(0.2, STOREY - 0.6)
        r0 = SHAFT_R - 0.14
        L = rng.uniform(0.5, 1.2)
        pts = []
        for s in np.linspace(0.0, 1.0, 6):
            r = r0 - 0.35 * s ** 1.2
            aa = a + 0.25 * s
            pts.append([math.sin(aa) * r, y0 + L * s, math.cos(aa) * r])
        side = np.array([math.cos(a), 0.0, -math.sin(a)])
        oc.ribbon(mb, np.asarray(pts), np.linspace(0.05, 0.02, 6), side, [weed], variation=float(rng.random()))
    oc.patina(mb, noise, amount=0.5)
    lod = kc.MeshBuilder("current_shaft" + oc.LOD)
    ang = np.linspace(0, 2 * math.pi, 9)
    for a0, a1 in zip(ang[:-1], ang[1:]):
        am = (a0 + a1) * 0.5
        kc.rounded_block(lod, (math.sin(am) * SHAFT_R, STOREY * 0.5, math.cos(am) * SHAFT_R),
                         (SHAFT_R * math.sin((a1 - a0) / 2), STOREY * 0.5, 0.13), lod.material(oc.M_CONCRETE),
                         rot=kc.rot_y(am), seg=1, radius=0.02)
    return [mb, lod]


STEP_RUN = 0.48
STEP_RISE = 0.32
STAIR_W = 1.8


def stair_profile() -> list[tuple[float, float, float]]:
    """(x0, x1, top y) of each tread and the landing, from the lip down."""
    out = []
    for k in range(5):
        out.append((STEP_RUN * k, STEP_RUN * (k + 1), -STEP_RISE * (k + 1)))
    out.append((2.4, 3.6, -1.6))
    for k in range(5):
        out.append((3.6 + STEP_RUN * k, 3.6 + STEP_RUN * (k + 1), -1.6 - STEP_RISE * (k + 1)))
    return out


def build_stair(seed: int = 609) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("stair_flight", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("stair_flight")
    mat = mb.material(oc.M_CONCRETE)
    hw = STAIR_W * 0.5
    for x0, x1, y in stair_profile():
        if x1 - x0 > 1.0:
            oc.block(mb, ((x0 + x1) * 0.5, y - 0.15, 0.0), ((x1 - x0) * 0.5, 0.15, hw), mat, rng=rng, noise=noise,
                     seg=3, disp_m=0.012)
            continue
        oc.block(mb, ((x0 + x1) * 0.5 - 0.01, y - 0.17, 0.0), ((x1 - x0) * 0.5 + 0.02, 0.17, hw), mat, rng=rng,
                 noise=noise, seg=2, radius=0.04, disp_m=0.01)
    # Soffits under the two flights and the side walls along them.
    for x0, x1, y0, y1 in ((0.0, 2.4, 0.0, -1.6), (3.6, 6.0, -1.6, -3.2)):
        ang = math.atan2(y1 - y0, x1 - x0)
        L = math.hypot(x1 - x0, y1 - y0)
        c = np.array([(x0 + x1) * 0.5 + 0.12, (y0 + y1) * 0.5 - 0.42, 0.0])
        oc.block(mb, c, (L * 0.5, 0.12, hw), mat, rng=rng, noise=noise, rot=kc.rot_z(ang), seg=3, disp_m=0.01)
        c2 = np.array([(x0 + x1) * 0.5, (y0 + y1) * 0.5 + 0.2, hw + 0.12])
        oc.block(mb, c2, (L * 0.5 + 0.1, 0.75, 0.12), mat, rng=rng, noise=noise, rot=kc.rot_z(ang), seg=3, disp_m=0.015)
    oc.block(mb, (3.0, -1.6 + 0.6, hw + 0.12), (0.7, 0.75, 0.12), mat, rng=rng, noise=noise, seg=3)
    # A broken balustrade on the open side (-Z): ceramic posts, several snapped, one length of brass rail.
    cer = mb.material(oc.M_CERAMIC)
    posts = []
    for x in np.arange(0.3, 6.0, 0.6):
        tread = [p for p in stair_profile() if p[0] <= x < p[1]]
        y = tread[0][2] if tread else -3.2
        h = 0.95 if rng.random() > 0.4 else rng.uniform(0.25, 0.6)
        oc.lathe(mb, [(0.06, 0.0), (0.05, 0.1), (0.035, h * 0.5), (0.045, h * 0.9), (0.03, h)], cer, sides=8,
                 center=(x, y, -hw + 0.1), noise=noise, disp_m=0.006 if h < 0.9 else 0.0)
        posts.append((x, y, h))
    whole = [p for p in posts if p[2] > 0.9]
    if len(whole) >= 2:
        a, b = whole[0], whole[1]
        kc.tube(mb, np.array([[a[0], a[1] + a[2], -hw + 0.1], [b[0], b[1] + b[2], -hw + 0.1],
                              [b[0] + 0.5, b[1] + b[2] - 0.35, -hw + 0.05]]), 0.025, 6, mb.material(oc.M_BRASS),
                weather=oc.CAST, cap_start=True, cap_end=True)
    for _k in range(7):
        x0, x1, y = stair_profile()[int(rng.integers(0, 11))]
        oc.coral_knob(mb, (x1 - 0.05, y + 0.02, rng.uniform(-0.7, 0.7)), rng.uniform(0.04, 0.08), rng, noise,
                      oc.CORALS[int(rng.integers(0, 5))])
    oc.patina(mb, noise, amount=0.5)
    lod = kc.MeshBuilder("stair_flight" + oc.LOD)
    for x0, x1, y0, y1 in ((0.0, 2.4, 0.0, -1.6), (3.6, 6.0, -1.6, -3.2)):
        ang = math.atan2(y1 - y0, x1 - x0)
        L = math.hypot(x1 - x0, y1 - y0)
        kc.rounded_block(lod, ((x0 + x1) * 0.5, (y0 + y1) * 0.5 - 0.25, 0.0), (L * 0.5, 0.25, hw),
                         lod.material(oc.M_CONCRETE), rot=kc.rot_z(ang), seg=1, radius=0.02)
    kc.rounded_block(lod, (3.0, -1.75, 0.0), (0.6, 0.15, hw), lod.material(oc.M_CONCRETE), seg=1, radius=0.02)
    return [mb, lod]


TARGETS = {
    "tower_bay": build_bay,
    "tower_bay_solid": build_bay_solid,
    "tower_bay_broken": build_bay_broken,
    "tower_pier": build_pier,
    "floor_slab": build_slab,
    "floor_slab_broken": build_slab_broken,
    "bell_room": build_bell_room,
    "current_shaft": build_shaft,
    "stair_flight": build_stair,
}
