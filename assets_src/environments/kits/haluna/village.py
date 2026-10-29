"""Haluna village kit: timber, thatch and red tile (haluna.md §1.2). Pure numpy; see kit_common.py.

Pieces (each is a target in build.py; LOD1 is a cheap stand-in for > 60 m):
  timber_stilt_post   a 0.15-0.2 m post, adze-faceted, lashed at the head, 2.4 m
  timber_deck_2m      a 2.0 x 1.8 m deck module: bearers, joists, 0.3 m planks with gaps
  timber_railing_2m   a 2.0 m railing module: posts, top rail, mid rail, lashings
  roof_thatch_hip     a hipped thatch roof module for a 4 x 5 m footprint (25 deg, 0.9 m eaves)
  roof_tile_hip       a hipped red tile roof for a 5 x 6 m footprint: corrugated cover-tile columns
                      at 0.25 m, white lime mortar on the ridge, hips and every seam (the texture)
  house_lane_a/b/c    6 x 6, 8 x 5 and 6 x 8 m houses with no shade deck (M3-ENV-743, Ch4's wake-night lane)
  house_tile_a/b/c    5 x 6, 4 x 5 and 6 x 8 m houses: coral base wall (0.9 m), 0.15 m post frame,
                      woven infill, shutters, a 1.8 m shade deck, the tile roof
  storehouse_stilt    a 3 x 4 m granary on 6 stilts (1.2 m) with a thatch roof
  stilt_house         a 4 x 5 m waterfront house on 2.0 m stilts: deck, railing, thatch roof
  lintel_gull_a/b/c   carved sun-silvered seabird, wings folded / half-raised / crying, 0.6-0.9 m,
                      faceted like adze work; modelled facing +X (the dresser yaws it to the sea)

Front of every building is +Z; origin at the centre of the footprint on the ground (y = 0).
Weathering parameters: kit_common.VILLAGE unless noted; `seed` changes every random choice.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

ROOF_PITCH_DEG = 25.0  # haluna.md §1.2
EAVE_M = 0.9
POST_M = 0.15
BASE_WALL_M = 0.9
WALL_TOP_M = 2.55
DECK_DEPTH_M = 1.8
DECK_HEIGHT_M = 0.45
TILE_COLUMN_M = 0.25  # kit_textures.ROOF_COLUMN_M
TILE_AMPLITUDE_M = 0.035
TIMBER_TILE_M = 1.6  # kit_textures.TILE_M["timber"][1]: UV v is metres along a board

TRI_BUDGET = {
    "timber_stilt_post": (400, 60),
    "timber_deck_2m": (1400, 120),
    "timber_railing_2m": (900, 120),
    "roof_thatch_hip": (3500, 400),
    "roof_tile_hip": (12000, 600),
    "house_tile": (22000, 1600),
    "storehouse_stilt": (7000, 900),
    "stilt_house": (14000, 1300),
    "lintel_gull": (2400, 400),
}

M_STONE = "kit_coral_stone"
M_TIMBER = "kit_timber"
M_CARVING = "kit_carved_wood"  # the lintel-gulls: adze-carved, sun-silvered, grain not stretched
M_THATCH = "kit_thatch"
M_TILE = "kit_roof_tile"
M_MORTAR = "kit_mortar_white"
M_WOVEN = "kit_woven_panel"
M_DARK = "kit_interior_dark"
M_LASHING = "kit_lashing"


# ---------------------------------------------------------------------------------------------
# Timber modules
# ---------------------------------------------------------------------------------------------
def post(mb: kc.MeshBuilder, base, top, radius: float, rng, noise, *, sides: int = 7, lash: bool = True,
         weather: kc.Weathering = kc.VILLAGE) -> None:
    """An adze-trimmed round post (irregular heptagon section) with a coir lashing near the head."""
    base = np.asarray(base, float)
    top = np.asarray(top, float)
    n = max(3, int(np.linalg.norm(top - base) / 0.4) + 2)
    pts = np.linspace(base, top, n)
    bow = kc.any_perpendicular(kc.normalize(top - base)) * rng.uniform(-0.02, 0.02)
    pts = pts + np.sin(np.linspace(0, math.pi, n))[:, None] * bow
    radii = radius * (1.0 + 0.06 * np.cos(np.linspace(0, 3, n))) * np.linspace(1.05, 0.95, n)
    kc.tube(mb, pts, radii, sides, mb.material(M_TIMBER), weather=weather, noise=noise, disp_m=radius * 0.18,
            disp_period_m=0.35, variation=float(rng.random()), v_scale=1.0, u_repeat=radius * 2 * math.pi,
            cap_end=True)
    if lash:
        axis = kc.normalize(top - base)
        for k in range(2):
            c = top - axis * (0.12 + 0.07 * k)
            ring = np.array([c - axis * 0.025, c + axis * 0.025])
            kc.tube(mb, ring, radius * 1.12, sides + 1, mb.material(M_LASHING), weather=weather,
                    variation=float(rng.random()), u_repeat=4.0, v_scale=8.0)


def build_stilt_post(seed: int = 1) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("timber_stilt_post", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("timber_stilt_post")
    post(mb, (0, 0, 0), (0, 2.4, 0), 0.09, rng, noise)
    lod = kc.MeshBuilder("timber_stilt_post-lod1")
    kc.tube(lod, np.array([[0, 0, 0], [0, 2.4, 0.0]]), 0.09, 5, lod.material(M_TIMBER), cap_end=True)
    return [mb, lod]


def deck(mb: kc.MeshBuilder, x0: float, x1: float, z0: float, z1: float, y: float, rng, noise, *,
         plank_w: float = 0.3, gap: float = 0.015, along_x: bool = False, weather=kc.VILLAGE,
         bearers: bool = True, missing_p: float = 0.0) -> None:
    """Planks laid across a rectangle at height y (top surface), with two bearers and joists below."""
    mat = mb.material(M_TIMBER)
    thick = 0.045
    if along_x:  # planks run along X, stacked in Z
        span_a, span_b = z0, z1
    else:
        span_a, span_b = x0, x1
    s = span_a + gap * 0.5
    while s + plank_w * 0.5 < span_b:
        w = plank_w * rng.uniform(0.85, 1.1)
        c = s + w * 0.5
        if rng.random() >= missing_p:
            dy = rng.uniform(-0.008, 0.008)
            if along_x:
                a, b = (x0 - rng.uniform(0, 0.04), y - thick * 0.5 + dy, c), (x1 + rng.uniform(0, 0.04),
                                                                              y - thick * 0.5 + dy, c)
            else:
                a, b = (c, y - thick * 0.5 + dy, z0 - rng.uniform(0, 0.04)), (c, y - thick * 0.5 + dy,
                                                                              z1 + rng.uniform(0, 0.04))
            kc.plank(mb, a, b, w - gap, thick, mat, weather=weather, variation=float(rng.random()), noise=noise,
                     sag_m=rng.uniform(0.0, 0.012), seg=2)
        s += w
    if bearers:
        by = y - thick - 0.06
        if along_x:
            for xb in np.linspace(x0 + 0.15, x1 - 0.15, max(2, int((x1 - x0) / 1.2) + 1)):
                kc.plank(mb, (xb, by, z0), (xb, by, z1), 0.1, 0.12, mat, weather=weather,
                         variation=float(rng.random()), noise=noise)
        else:
            for zb in np.linspace(z0 + 0.15, z1 - 0.15, max(2, int((z1 - z0) / 1.2) + 1)):
                kc.plank(mb, (x0, by, zb), (x1, by, zb), 0.1, 0.12, mat, weather=weather,
                         variation=float(rng.random()), noise=noise)


def build_deck_module(seed: int = 1) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("timber_deck_2m", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("timber_deck_2m")
    deck(mb, -1.0, 1.0, -0.9, 0.9, 0.0, rng, noise)
    lod = kc.MeshBuilder("timber_deck_2m-lod1")
    kc.rounded_block(lod, (0, -0.03, 0), (1.0, 0.03, 0.9), lod.material(M_TIMBER), seg=1, radius=0.01)
    return [mb, lod]


def railing(mb: kc.MeshBuilder, a, b, y: float, rng, noise, *, height: float = 0.9, weather=kc.VILLAGE) -> None:
    """Posts every ~1 m between points a and b (x, z) at deck height y, a top rail and a mid rail."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    length = float(np.linalg.norm(b - a))
    n = max(2, int(round(length / 1.0)) + 1)
    mat = mb.material(M_TIMBER)
    for t in np.linspace(0.0, 1.0, n):
        p = a + (b - a) * t
        post(mb, (p[0], y, p[1]), (p[0], y + height + 0.05, p[1]), 0.045, rng, noise, sides=6, lash=False,
             weather=weather)
    for h, w in ((height, 0.08), (height * 0.5, 0.05)):
        kc.plank(mb, (a[0], y + h, a[1]), (b[0], y + h, b[1]), w, 0.05, mat, weather=weather,
                 variation=float(rng.random()), noise=noise, sag_m=rng.uniform(0, 0.01), seg=2)


def build_railing_module(seed: int = 1) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("timber_railing_2m", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("timber_railing_2m")
    railing(mb, (-1.0, 0.0), (1.0, 0.0), 0.0, rng, noise)
    lod = kc.MeshBuilder("timber_railing_2m-lod1")
    kc.rounded_block(lod, (0, 0.9, 0), (1.0, 0.04, 0.03), lod.material(M_TIMBER), seg=1, radius=0.01)
    for x in (-1.0, 0.0, 1.0):
        kc.rounded_block(lod, (x, 0.47, 0), (0.03, 0.47, 0.03), lod.material(M_TIMBER), seg=1, radius=0.01)
    return [mb, lod]


# ---------------------------------------------------------------------------------------------
# Hipped roofs
# ---------------------------------------------------------------------------------------------
def _hip_faces(w: float, d: float, pitch_deg: float):
    """Yields (name, fn(s, t) -> point, s_range, slope_len) for the four faces of a hip roof over
    a w (x) by d (z) rectangle, eave at y = 0. s is metres along the eave; t 0 eave -> 1 ridge/apex."""
    tan_p = math.tan(math.radians(pitch_deg))
    short = min(w, d)
    rise = short * 0.5 * tan_p
    ridge_half = (max(w, d) - short) * 0.5
    slope_len = math.hypot(short * 0.5, rise)
    along_x = w >= d
    faces = []
    for sgn in (1.0, -1.0):
        if along_x:
            def long_face(s, t, sgn=sgn):
                z = sgn * d * 0.5 * (1.0 - t)
                half = w * 0.5 - t * (w * 0.5 - ridge_half)
                x = np.clip(s, -half, half)
                return np.stack([x, rise * t, np.broadcast_to(z, np.shape(x))], axis=-1)

            def short_face(s, t, sgn=sgn):
                x = sgn * w * 0.5 * (1.0 - t) + sgn * ridge_half * t
                half = d * 0.5 * (1.0 - t)
                z = np.clip(s, -half, half)
                return np.stack([np.broadcast_to(x, np.shape(z)), rise * t, z], axis=-1)

            faces.append(("long", long_face, (-w * 0.5, w * 0.5), sgn))
            faces.append(("short", short_face, (-d * 0.5, d * 0.5), sgn))
        else:
            def long_face(s, t, sgn=sgn):
                x = sgn * w * 0.5 * (1.0 - t)
                half = d * 0.5 - t * (d * 0.5 - ridge_half)
                z = np.clip(s, -half, half)
                return np.stack([np.broadcast_to(x, np.shape(z)), rise * t, z], axis=-1)

            def short_face(s, t, sgn=sgn):
                z = sgn * d * 0.5 * (1.0 - t) + sgn * ridge_half * t
                half = w * 0.5 * (1.0 - t)
                x = np.clip(s, -half, half)
                return np.stack([x, rise * t, np.broadcast_to(z, np.shape(x))], axis=-1)

            faces.append(("long", long_face, (-d * 0.5, d * 0.5), sgn))
            faces.append(("short", short_face, (-w * 0.5, w * 0.5), sgn))
    return faces, rise, ridge_half, slope_len, along_x


def _orient_grid(grid: np.ndarray, outward_hint: np.ndarray) -> bool:
    """True if the grid's (row, col) winding faces away from outward_hint (so it must be flipped)."""
    r, c = grid.shape[0] // 2, grid.shape[1] // 2
    du = grid[r, min(c + 1, grid.shape[1] - 1)] - grid[r, max(c - 1, 0)]
    dv = grid[min(r + 1, grid.shape[0] - 1), c] - grid[max(r - 1, 0), c]
    n = np.cross(du, dv)
    return float(np.dot(n, outward_hint)) < 0.0


def hip_roof(mb: kc.MeshBuilder, w: float, d: float, y_eave: float, rng, noise, *, kind: str = "tile",
             pitch_deg: float = ROOF_PITCH_DEG, weather=kc.VILLAGE, lod: bool = False, center=(0.0, 0.0)) -> None:
    """A hipped roof over a w x d rectangle (eaves included) whose eave line sits at y_eave.

    kind 'tile': cover-tile corrugation (columns down the slope, 0.25 m pitch, aligned to the
    roof_tile texture), white mortar ridge and hip rolls, a timber fascia and underside.
    kind 'thatch': stepped courses, a ragged, thick eave and a bound thatch ridge."""
    faces, rise, ridge_half, slope_len, along_x = _hip_faces(w, d, pitch_deg)
    cx, cz = center
    off = np.array([cx, y_eave, cz])
    surf_mat = mb.material(M_TILE if kind == "tile" else M_THATCH)
    under_mat = mb.material(M_TIMBER if kind == "tile" else M_THATCH)
    if lod:
        du, nt = 1.2, 2
    elif kind == "tile":
        du, nt = TILE_COLUMN_M / 3.0, max(5, int(slope_len / 0.7))
    else:
        du, nt = 0.4, max(6, int(slope_len / 0.35))
    thick = 0.12 if kind == "tile" else 0.28
    for _name, fn, (s0, s1), sgn in faces:
        ns = max(2, int(math.ceil((s1 - s0) / du)) + 1)
        s = np.linspace(s0, s1, ns)
        t = np.linspace(0.0, 1.0, nt + 1)
        S, T = np.meshgrid(s, t)  # rows = t (eave -> ridge), cols = s
        p = fn(S, T)
        # Face normal (outward and up) from the analytic plane.
        e = fn(np.array([s0 * 0.5, s1 * 0.5]), np.array([0.0, 0.0]))
        r = fn(np.array([0.0]), np.array([0.9]))[0]
        n_face = kc.normalize(np.cross(e[1] - e[0], r - e[0]))
        if n_face[1] < 0:
            n_face = -n_face
        slope_d = (1.0 - T) * slope_len  # metres down the slope from the ridge line
        if kind == "tile" and not lod:
            frac = (S / TILE_COLUMN_M) % 1.0
            bump = TILE_AMPLITUDE_M * np.sin(frac * math.pi) ** 0.7
            lap = 0.012 * ((slope_d / 0.30) % 1.0)  # each course steps out over the one below
            p = p + n_face * (bump + lap)[..., None]
        elif kind == "thatch":
            course = (slope_d / 0.2) % 1.0
            rag = noise.fbm(p * np.array([4.0, 1.0, 4.0]), 2)
            p = p + n_face * (0.04 * course + 0.03 * rag)[..., None]
            eave = (T < 0.02)
            p[..., 1] = p[..., 1] - np.where(eave, 0.05 + 0.08 * rag, 0.0)
            p = p - np.where(eave[..., None], n_face * 0.0, 0.0)
        p = p + off
        uv = np.stack([S, slope_d], axis=-1)
        breakup = noise.fbm(p / 0.8, 2)
        col = np.stack([
            np.clip(weather.moss * 0.6 * breakup * (1 - T * 0.5), 0, 1),
            np.clip(weather.salt * 0.5 * breakup, 0, 1),
            np.zeros_like(T),
            np.clip(weather.erosion * (0.3 + 0.7 * breakup), 0, 1),
        ], axis=-1)
        uv2 = np.stack([np.clip(0.75 + 0.25 * T, 0, 1), np.full(T.shape, float(rng.random()))], axis=-1)
        flip = _orient_grid(p, n_face)
        kc.quad_strip(mb, p, surf_mat, uv=uv, col=col, uv2=uv2, flip=flip)
        if not lod:
            # Underside (seen from the shade deck and the lane) and the eave edge.
            pu = fn(S, T) + off - np.array([0.0, thick, 0.0])
            kc.quad_strip(mb, pu, under_mat, uv=uv, col=col * np.array([0, 0, 0, 0.5]),
                          uv2=np.stack([np.full(T.shape, 0.45), uv2[..., 1]], axis=-1), flip=not flip)
            edge = np.stack([p[0], pu[0]], axis=0)
            kc.quad_strip(mb, edge, under_mat, uv=np.stack([np.stack([s, s]), np.stack([np.zeros(ns),
                          np.full(ns, thick)])], axis=-1), col=col[:2] * np.array([0, 0, 0, 1]),
                          uv2=np.stack([np.full((2, ns), 0.7), np.full((2, ns), 0.5)], axis=-1),
                          flip=_orient_grid(edge, np.array([n_face[0], 0.0, n_face[2]])))
    # Ridge and hip rolls.
    apex_y = rise + y_eave
    if along_x:
        ridge = np.array([[cx - ridge_half, apex_y, cz], [cx + ridge_half, apex_y, cz]])
        corners = [(cx + sx * w * 0.5, cz + sz * d * 0.5, cx + sx * ridge_half) for sx in (-1, 1) for sz in (-1, 1)]
        hips = [np.array([[x, y_eave, z], [xr, apex_y, cz]]) for x, z, xr in corners]
    else:
        ridge = np.array([[cx, apex_y, cz - ridge_half], [cx, apex_y, cz + ridge_half]])
        corners = [(cx + sx * w * 0.5, cz + sz * d * 0.5, cz + sz * ridge_half) for sx in (-1, 1) for sz in (-1, 1)]
        hips = [np.array([[x, y_eave, z], [cx, apex_y, zr]]) for x, z, zr in corners]
    roll_mat = mb.material(M_MORTAR if kind == "tile" else M_THATCH)
    roll_r = 0.09 if kind == "tile" else 0.16
    sides = 5 if lod else 9
    lift = np.array([0.0, roll_r * 0.45 + (TILE_AMPLITUDE_M if kind == "tile" else 0.05), 0.0])
    if ridge_half > 0.01:
        kc.tube(mb, np.linspace(ridge[0] - [0.12 * along_x, 0, 0.12 * (not along_x)],
                                ridge[1] + [0.12 * along_x, 0, 0.12 * (not along_x)], 6) + lift,
                roll_r, sides, roll_mat, weather=weather, noise=None if lod else noise, disp_m=0.01,
                variation=float(rng.random()), cap_start=True, cap_end=True)
    for h in hips:
        kc.tube(mb, np.linspace(h[0], h[1], 5) + lift * 0.8, roll_r * 0.85, sides, roll_mat, weather=weather,
                noise=None if lod else noise, disp_m=0.01, variation=float(rng.random()), cap_start=True)


def build_roof_tile(seed: int = 1) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("roof_tile_hip", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("roof_tile_hip")
    hip_roof(mb, 5.0 + 2 * EAVE_M, 6.0 + 2 * EAVE_M, 0.0, rng, noise, kind="tile")
    lod = kc.MeshBuilder("roof_tile_hip-lod1")
    hip_roof(lod, 5.0 + 2 * EAVE_M, 6.0 + 2 * EAVE_M, 0.0, rng, noise, kind="tile", lod=True)
    return [mb, lod]


def build_roof_thatch(seed: int = 1) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("roof_thatch_hip", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("roof_thatch_hip")
    hip_roof(mb, 4.0 + 2 * EAVE_M, 5.0 + 2 * EAVE_M, 0.0, rng, noise, kind="thatch", pitch_deg=32.0)
    lod = kc.MeshBuilder("roof_thatch_hip-lod1")
    hip_roof(lod, 4.0 + 2 * EAVE_M, 5.0 + 2 * EAVE_M, 0.0, rng, noise, kind="thatch", pitch_deg=32.0, lod=True)
    return [mb, lod]


# ---------------------------------------------------------------------------------------------
# Walls and houses
# ---------------------------------------------------------------------------------------------
def panel(mb: kc.MeshBuilder, a, b, y0: float, y1: float, mat_name: str, rng, *, thick: float = 0.04,
          inset: float = 0.0) -> None:
    """A flat infill panel between two (x, z) points from y0 to y1 (woven mat, boards, shutters)."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    mid = (a + b) * 0.5
    along = b - a
    ln = float(np.linalg.norm(along))
    yaw = math.atan2(-along[1], along[0])
    normal_xz = np.array([-along[1], along[0]]) / max(ln, 1e-9)
    c = np.array([mid[0] + normal_xz[0] * inset, (y0 + y1) * 0.5, mid[1] + normal_xz[1] * inset])
    kc.rounded_block(mb, c, (ln * 0.5, (y1 - y0) * 0.5, thick * 0.5), mb.material(mat_name), rot=kc.rot_y(yaw),
                     radius=0.01, seg=1, variation=float(rng.random()), uv_scale=1.0)


def frame_wall(mb: kc.MeshBuilder, a, b, y0: float, y1: float, outward, rng, noise, *, girts: int = 3,
               batten_pitch_m: float = 0.85, window: bool = False, battens: bool = True) -> None:
    """Timber framing on the outside face of a woven infill panel (M2 final pass): horizontal girts
    and vertical battens lashed over the mat, and optionally a window with a propped shutter, so a
    wall reads as built, not as one flat card. `outward` is the (x, z) direction away from the house.
    Callers pass a dedicated rng, so the framing never shifts the rest of the piece's randomness."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    out = kc.normalize(np.array([outward[0], 0.0, outward[1]]))
    off = out * 0.035
    tm = mb.material(M_TIMBER)
    a3, b3 = np.array([a[0], 0.0, a[1]]), np.array([b[0], 0.0, b[1]])
    ln = float(np.linalg.norm(b3 - a3))
    along = (b3 - a3) / max(ln, 1e-9)
    for k in range(girts):
        y = y0 + 0.08 + (y1 - y0 - 0.14) * (k / max(girts - 1, 1))
        kc.plank(mb, a3 + off + [0.0, y, 0.0], b3 + off + [0.0, y, 0.0], 0.07, 0.035, tm, up=out,
                 variation=float(rng.random()), noise=noise, sag_m=rng.uniform(0.0, 0.008), seg=2)
    n_bat = max(0, int(ln / batten_pitch_m) - 1) if battens else 0
    win_lo, win_hi = (0.35, 0.65) if window else (2.0, 2.0)
    for k in range(n_bat):
        t = (k + 1) / (n_bat + 1) + rng.uniform(-0.04, 0.04)
        if win_lo < t < win_hi:
            continue
        p = a3 + along * (ln * t) + off * 1.4
        kc.plank(mb, p + [0.0, y0 + 0.02, 0.0], p + [0.0, y1 - 0.02, 0.0], 0.05, 0.025, tm, up=out,
                 variation=float(rng.random()), noise=noise)
    if window:
        c = a3 + along * (ln * 0.5)
        ww = min(0.8, ln * 0.3)
        wy0, wy1 = y0 + (y1 - y0) * 0.45, y0 + (y1 - y0) * 0.85
        wa, wb = c - along * ww * 0.5 + out * 0.03, c + along * ww * 0.5 + out * 0.03
        panel(mb, wa[[0, 2]], wb[[0, 2]], wy0, wy1, M_DARK, rng, thick=0.012)
        # The shutter, hinged at the top and propped out on a stick.
        yaw = math.atan2(-along[2], along[0])
        side = 1.0 if np.dot(np.cross(along, [0.0, 1.0, 0.0]), out) < 0 else -1.0
        tilt = kc.rot_y(yaw) @ kc.rot_x(0.55 * side)
        half_h = (wy1 - wy0) * 0.5
        c3 = c + [0.0, wy1, 0.0] + out * (0.04 + math.sin(0.55) * half_h) - [0.0, math.cos(0.55) * half_h, 0.0]
        kc.rounded_block(mb, c3, (ww * 0.55, half_h, 0.016), tm, rot=tilt, radius=0.008, seg=1,
                         variation=float(rng.random()))
        foot = c + [0.0, wy0, 0.0] + out * 0.05
        tip = c3 - [0.0, half_h * 0.9, 0.0] + out * 0.02
        kc.plank(mb, foot, tip, 0.025, 0.025, tm, variation=float(rng.random()))


def coral_base(mb: kc.MeshBuilder, w: float, d: float, rng, noise, *, door_w: float = 1.1,
               weather=kc.VILLAGE, height: float = BASE_WALL_M) -> None:
    """Coral base wall around a w x d footprint (0.3 m thick), with a door gap centred on the front."""
    t = 0.3
    mat = mb.material(M_STONE)
    hw, hd = w * 0.5, d * 0.5
    segs = [
        ((-hw, -hd), (hw, -hd)),  # back
        ((-hw, -hd), (-hw, hd)),  # left
        ((hw, -hd), (hw, hd)),  # right
        ((-hw, hd), (-door_w * 0.5, hd)),  # front left of the door
        ((door_w * 0.5, hd), (hw, hd)),  # front right
    ]
    for a, b in segs:
        a, b = np.asarray(a, float), np.asarray(b, float)
        ln = float(np.linalg.norm(b - a))
        n = max(1, int(ln / 1.4))
        for k in range(n):
            p0 = a + (b - a) * (k / n)
            p1 = a + (b - a) * ((k + 1) / n)
            mid = (p0 + p1) * 0.5
            seg_len = ln / n
            yaw = math.atan2(-(b - a)[1], (b - a)[0])
            hgt = height * rng.uniform(0.96, 1.04)
            kc.rounded_block(mb, (mid[0], hgt * 0.5, mid[1]), (seg_len * 0.5 + 0.02, hgt * 0.5, t * 0.5), mat,
                             rot=kc.rot_y(yaw), radius=0.07, seg=3, noise=noise, disp_m=0.05, disp_period_m=0.35,
                             weather=weather, variation=float(rng.random()))


def house(name: str, w: float, d: float, seed: int, *, lod: bool = False,
          deck_m: float = DECK_DEPTH_M) -> kc.MeshBuilder:
    """A Haluna house: coral base, post frame, woven infill with shutters, a front shade deck (`deck_m` deep; 0 for
    a house whose door gives straight onto the lane), and the red tile hip roof over house + deck (+ eaves)."""
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
    hw, hd = w * 0.5, d * 0.5
    if lod:
        kc.rounded_block(mb, (0, WALL_TOP_M * 0.5, 0), (hw, WALL_TOP_M * 0.5, hd), mb.material(M_STONE), seg=1,
                         radius=0.05)
        if deck_m > 0.0:
            kc.rounded_block(mb, (0, DECK_HEIGHT_M * 0.5, hd + deck_m * 0.5),
                             (hw, DECK_HEIGHT_M * 0.5, deck_m * 0.5), mb.material(M_TIMBER), seg=1, radius=0.02)
        hip_roof(mb, w + 2 * EAVE_M, d + deck_m + 2 * EAVE_M, WALL_TOP_M - 0.1, rng, noise, kind="tile",
                 lod=True, center=(0.0, deck_m * 0.5))
        return mb
    coral_base(mb, w, d, rng, noise)
    frame_rng = kc.rng_for(name + "_frame", seed)
    # Post frame: corners + every ~1.6 m; plus deck posts along the front edge of the shade deck.
    xs = np.linspace(-hw, hw, max(2, int(round(w / 1.6)) + 1))
    zs = np.linspace(-hd, hd, max(2, int(round(d / 1.6)) + 1))
    ring = [(x, -hd) for x in xs] + [(x, hd) for x in xs] + [(-hw, z) for z in zs[1:-1]] + [(hw, z) for z in zs[1:-1]]
    for x, z in ring:
        post(mb, (x, BASE_WALL_M - 0.05, z), (x, WALL_TOP_M + 0.05, z), POST_M * 0.5, rng, noise, lash=False)
    for x in xs if deck_m > 0.0 else ():
        post(mb, (x, 0.0, hd + deck_m - 0.1), (x, WALL_TOP_M - 0.05, hd + deck_m - 0.1), POST_M * 0.5,
             rng, noise, lash=True)
    # Top plates.
    tm = mb.material(M_TIMBER)
    for (a, b) in (((-hw - 0.1, -hd), (hw + 0.1, -hd)), ((-hw - 0.1, hd), (hw + 0.1, hd)),
                   ((-hw, -hd - 0.1), (-hw, hd + max(deck_m, 0.1))), ((hw, -hd - 0.1), (hw, hd + max(deck_m, 0.1))),
                   ((-hw - 0.1, hd + deck_m - 0.1), (hw + 0.1, hd + deck_m - 0.1))):
        if deck_m <= 0.0 and a[1] == b[1] and a[1] > hd - 0.05:
            continue  # no deck: the front plate is the front wall's own (already laid)
        kc.plank(mb, (a[0], WALL_TOP_M, a[1]), (b[0], WALL_TOP_M, b[1]), 0.14, 0.16, tm, variation=float(rng.random()),
                 noise=noise)
    # Infill between posts: woven mat, with shutters (timber) on some bays and a door on the front.
    def bays(points):
        return list(zip(points[:-1], points[1:]))

    front = [(x, hd) for x in xs]
    back = [(x, -hd) for x in xs]
    left = [(-hw, z) for z in zs]
    right = [(hw, z) for z in zs]
    door_bay = len(xs) // 2 - (1 if len(xs) % 2 == 0 else 0)
    for side, pts, out in (("front", front, 1), ("back", back, -1), ("left", left, -1), ("right", right, 1)):
        for i, (a, b) in enumerate(bays(pts)):
            a, b = np.asarray(a, float), np.asarray(b, float)
            if side == "front" and i == door_bay:
                panel(mb, a, b, 0.05, WALL_TOP_M - 0.05, M_DARK, rng, thick=0.02, inset=-0.12)
                # Door leaf, half open.
                ln = float(np.linalg.norm(b - a))
                hinge = a + (b - a) * 0.08
                leaf_end = hinge + np.array([math.cos(1.1), math.sin(1.1)]) * (ln * 0.45)
                panel(mb, hinge, leaf_end, 0.08, 2.05, M_TIMBER, rng, thick=0.035)
                continue
            panel(mb, a, b, BASE_WALL_M, WALL_TOP_M - 0.08, M_WOVEN, rng, thick=0.03)
            has_window = rng.random() < 0.55
            # A sill girt over the coral base and, in a blind bay, a batten (M2 final pass; own rng).
            bay_along = kc.normalize(np.array([b[0] - a[0], 0.0, b[1] - a[1]]))
            frame_wall(mb, a, b, BASE_WALL_M, BASE_WALL_M + 0.14, (-bay_along[2] * out, bay_along[0] * out),
                       frame_rng, noise, girts=1, battens=False)
            if not has_window:
                frame_wall(mb, a, b, BASE_WALL_M + 0.1, WALL_TOP_M - 0.1, (-bay_along[2] * out, bay_along[0] * out),
                           frame_rng, noise, girts=0, batten_pitch_m=float(np.linalg.norm(b - a)) * 0.5)
            if has_window:
                # A window: dark opening with one propped shutter.
                c = (a + b) * 0.5
                along = kc.normalize(np.array([b[0] - a[0], 0.0, b[1] - a[1]]))
                nrm = np.array([-along[2], 0.0, along[0]]) * out
                ww = min(0.7, float(np.linalg.norm(b - a)) * 0.6)
                wa = c - along[[0, 2]] * ww * 0.5 + nrm[[0, 2]] * 0.03
                wb = c + along[[0, 2]] * ww * 0.5 + nrm[[0, 2]] * 0.03
                panel(mb, wa, wb, 1.35, 2.05, M_DARK, rng, thick=0.01)
                sa = wa + nrm[[0, 2]] * 0.02
                sb = wb + nrm[[0, 2]] * 0.02
                if rng.random() < 0.5:
                    panel(mb, sa, sb, 1.35, 2.05, M_TIMBER, rng, thick=0.03, inset=0.02)
                else:
                    # Propped open: rotate the shutter outward about its top edge.
                    mid = (sa + sb) * 0.5
                    ln = float(np.linalg.norm(sb - sa))
                    yaw = math.atan2(-(sb - sa)[1], (sb - sa)[0])
                    tilt = kc.rot_y(yaw) @ kc.rot_x(-0.6 * out * (1 if side in ("front", "back") else 1))
                    c3 = np.array([mid[0], 2.05, mid[1]]) + np.array([nrm[0], 0, nrm[2]]) * 0.2 - np.array([0, 0.3, 0])
                    kc.rounded_block(mb, c3, (ln * 0.5, 0.34, 0.015), tm, rot=tilt, radius=0.008, seg=1,
                                     variation=float(rng.random()))
    # Shade deck.
    if deck_m > 0.0:
        deck(mb, -hw, hw, hd + 0.05, hd + deck_m, DECK_HEIGHT_M, rng, noise, along_x=True)
    # Roof over house + deck.
    hip_roof(mb, w + 2 * EAVE_M, d + deck_m + 2 * EAVE_M, WALL_TOP_M - 0.1, rng, noise, kind="tile",
             center=(0.0, deck_m * 0.5))
    return mb


HOUSES = {"house_tile_a": (5.0, 6.0, 11), "house_tile_b": (4.0, 5.0, 12), "house_tile_c": (6.0, 8.0, 13)}
# M3-ENV-743: the houses with no shade deck, their doors straight onto the lane, at the sizes of Ch4's wake-night
# blocks (6 x 6 along the lane, Neme's 8 x 5, the inn's 6 x 8): the greybox's collision is their walls.
LANE_HOUSES = {"house_lane_a": (6.0, 6.0, 14), "house_lane_b": (8.0, 5.0, 15), "house_lane_c": (6.0, 8.0, 16)}


def build_house(name: str) -> list[kc.MeshBuilder]:
    if name in LANE_HOUSES:
        w, d, seed = LANE_HOUSES[name]
        return [house(name, w, d, seed, deck_m=0.0), house(name, w, d, seed, lod=True, deck_m=0.0)]
    w, d, seed = HOUSES[name]
    return [house(name, w, d, seed), house(name, w, d, seed, lod=True)]


def build_storehouse(seed: int = 21) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("storehouse_stilt", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("storehouse_stilt")
    w, d, stilt = 3.0, 4.0, 1.2
    for x in (-w * 0.5 + 0.1, w * 0.5 - 0.1):
        for z in (-d * 0.5 + 0.1, 0.0, d * 0.5 - 0.1):
            post(mb, (x, 0.0, z), (x, stilt + 0.05, z), 0.1, rng, noise)
            # Rat guard: a flat disc under the floor.
            kc.tube(mb, np.array([[x, stilt - 0.12, z], [x, stilt - 0.1, z]]), 0.28, 10, mb.material(M_TIMBER),
                    cap_start=True, cap_end=True, variation=float(rng.random()))
    deck(mb, -w * 0.5, w * 0.5, -d * 0.5, d * 0.5, stilt + 0.12, rng, noise)
    for a, b in (((-w / 2, -d / 2), (w / 2, -d / 2)), ((-w / 2, d / 2), (w / 2, d / 2)),
                 ((-w / 2, -d / 2), (-w / 2, d / 2)), ((w / 2, -d / 2), (w / 2, d / 2))):
        panel(mb, a, b, stilt + 0.12, stilt + 1.7, M_WOVEN, rng, thick=0.05)
    frame_rng = kc.rng_for("storehouse_stilt_frame", seed)
    for a, b in (((-w / 2, -d / 2), (w / 2, -d / 2)), ((-w / 2, d / 2), (w / 2, d / 2)),
                 ((-w / 2, -d / 2), (-w / 2, d / 2)), ((w / 2, -d / 2), (w / 2, d / 2))):
        frame_wall(mb, a, b, stilt + 0.12, stilt + 1.7, ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5), frame_rng, noise,
                   girts=2)
    for x, z in ((-w / 2, -d / 2), (w / 2, -d / 2), (-w / 2, d / 2), (w / 2, d / 2)):
        post(mb, (x, stilt + 0.1, z), (x, stilt + 1.8, z), 0.06, rng, noise, lash=False)
    hip_roof(mb, w + 1.4, d + 1.4, stilt + 1.65, rng, noise, kind="thatch", pitch_deg=34.0)
    # A notched-log ladder.
    kc.plank(mb, (0.0, 0.0, d * 0.5 + 0.9), (0.0, stilt + 0.12, d * 0.5 + 0.05), 0.22, 0.12, mb.material(M_TIMBER),
             variation=float(rng.random()), noise=noise)
    lod = kc.MeshBuilder("storehouse_stilt-lod1")
    kc.rounded_block(lod, (0, stilt + 0.9, 0), (w * 0.5, 0.8, d * 0.5), lod.material(M_WOVEN), seg=1, radius=0.02)
    for x in (-w * 0.5 + 0.1, w * 0.5 - 0.1):
        for z in (-d * 0.5 + 0.1, d * 0.5 - 0.1):
            kc.tube(lod, np.array([[x, 0, z], [x, stilt, z]]), 0.1, 5, lod.material(M_TIMBER))
    hip_roof(lod, w + 1.4, d + 1.4, stilt + 1.65, rng, noise, kind="thatch", pitch_deg=34.0, lod=True)
    return [mb, lod]


def build_stilt_house(seed: int = 22) -> list[kc.MeshBuilder]:
    """Waterfront house: 12 stilts (2.0 m), a full deck with a railing on three sides, thatch roof."""
    rng = kc.rng_for("stilt_house", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("stilt_house")
    w, d, stilt = 4.0, 5.0, 2.0
    dw, dd = w + 1.6, d + 2.2  # deck footprint (veranda on the front and sides)
    for x in np.linspace(-dw * 0.5 + 0.1, dw * 0.5 - 0.1, 4):
        for z in np.linspace(-d * 0.5 + 0.1, -d * 0.5 + dd - 0.1, 3):
            post(mb, (x, -0.8, z), (x, stilt + 0.05, z), 0.1, rng, noise, weather=kc.DROWNED)
    z0, z1 = -d * 0.5, -d * 0.5 + dd
    deck(mb, -dw * 0.5, dw * 0.5, z0, z1, stilt + 0.12, rng, noise, along_x=True, missing_p=0.03)
    y = stilt + 0.12
    railing(mb, (-dw * 0.5, z1 - 0.05), (dw * 0.5, z1 - 0.05), y, rng, noise)
    railing(mb, (-dw * 0.5 + 0.05, z0 + d), (-dw * 0.5 + 0.05, z1), y, rng, noise)
    railing(mb, (dw * 0.5 - 0.05, z0 + d), (dw * 0.5 - 0.05, z1), y, rng, noise)
    hw, hd = w * 0.5, d * 0.5
    for a, b in (((-hw, -hd), (hw, -hd)), ((-hw, -hd), (-hw, hd)), ((hw, -hd), (hw, hd)), ((-hw, hd), (-0.5, hd)),
                 ((0.5, hd), (hw, hd))):
        panel(mb, a, b, y, y + 2.0, M_WOVEN, rng, thick=0.05)
    frame_rng = kc.rng_for("stilt_house_frame", seed)
    for a, b in (((-hw, -hd), (hw, -hd)), ((-hw, -hd), (-hw, hd)), ((hw, -hd), (hw, hd)), ((-hw, hd), (-0.5, hd)),
                 ((0.5, hd), (hw, hd))):
        mid = ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)
        frame_wall(mb, a, b, y, y + 2.0, mid, frame_rng, noise, window=abs(a[0] - b[0]) < 1e-6)
    panel(mb, (-0.5, hd - 0.1), (0.5, hd - 0.1), y, y + 1.9, M_DARK, rng, thick=0.02)
    for x, z in ((-hw, -hd), (hw, -hd), (-hw, hd), (hw, hd), (-0.5, hd), (0.5, hd)):
        post(mb, (x, y, z), (x, y + 2.1, z), 0.07, rng, noise, lash=False)
    for x in (-dw * 0.5 + 0.1, dw * 0.5 - 0.1):
        post(mb, (x, y, z1 - 0.1), (x, y + 2.0, z1 - 0.1), 0.06, rng, noise, lash=True)
    hip_roof(mb, dw + 0.6, dd + 0.8, y + 1.95, rng, noise, kind="thatch", pitch_deg=30.0,
             center=(0.0, z0 + dd * 0.5))
    # Ladder down to the water.
    tm = mb.material(M_TIMBER)
    for x in (-0.25, 0.25):
        kc.plank(mb, (x, -0.6, z1 + 0.35), (x, y, z1 - 0.02), 0.06, 0.06, tm, variation=float(rng.random()))
    for k in range(6):
        yy = -0.3 + k * 0.42
        zz = z1 + 0.35 - (yy + 0.6) / (y + 0.6) * 0.37
        kc.plank(mb, (-0.27, yy, zz), (0.27, yy, zz), 0.05, 0.04, tm, variation=float(rng.random()))
    lod = kc.MeshBuilder("stilt_house-lod1")
    kc.rounded_block(lod, (0, y + 1.0, 0), (hw, 1.0, hd), lod.material(M_WOVEN), seg=1, radius=0.02)
    kc.rounded_block(lod, (0, y - 0.03, z0 + dd * 0.5), (dw * 0.5, 0.05, dd * 0.5), lod.material(M_TIMBER), seg=1,
                     radius=0.02)
    for x in (-dw * 0.5 + 0.1, dw * 0.5 - 0.1):
        for z in (z0 + 0.1, z1 - 0.1):
            kc.tube(lod, np.array([[x, -0.8, z], [x, y, z]]), 0.1, 5, lod.material(M_TIMBER))
    hip_roof(lod, dw + 0.6, dd + 0.8, y + 1.95, rng, noise, kind="thatch", pitch_deg=30.0, lod=True,
             center=(0.0, z0 + dd * 0.5))
    return [mb, lod]


# ---------------------------------------------------------------------------------------------
# Lintel-gull (an original carved seabird; the Ryukyuan roof-guardian idea transformed:
# wood not ceramic, a bird not a beast, facing the sea not the street; references.md §2)
# ---------------------------------------------------------------------------------------------
def _facet(mb: kc.MeshBuilder, start_v: int, start_t: int) -> None:
    """Re-emits triangles [start_t:] with unshared vertices and face normals (adze-cut facets)."""
    pos = np.asarray(mb.pos)
    tris = np.asarray(mb.tris[start_t:])
    mats = mb.tri_mat[start_t:]
    uv = np.asarray(mb.uv)
    uv2 = np.asarray(mb.uv2)
    col = np.asarray(mb.col)
    del mb.pos[start_v:], mb.nrm[start_v:], mb.uv[start_v:], mb.uv2[start_v:], mb.col[start_v:]
    del mb.tris[start_t:], mb.tri_mat[start_t:]
    for (a, b, c), m in zip(tris, mats):
        p = pos[[a, b, c]]
        n = kc.normalize(np.cross(p[1] - p[0], p[2] - p[0]))
        base = mb.add_vertices(p, np.tile(n, (3, 1)), uv[[a, b, c]], uv2[[a, b, c]], col[[a, b, c]])
        mb.add_tri(base, base + 1, base + 2, m)


def _loft(mb: kc.MeshBuilder, spine: np.ndarray, rx: np.ndarray, ry: np.ndarray, sides: int, mat: int,
          rng, noise, *, weather=kc.VILLAGE, droop=None) -> None:
    """Lofts elliptical sections (rx across Z, ry vertical) along a spine of points (mostly along X)."""
    ang = np.linspace(0.0, 2 * math.pi, sides + 1)
    rows = []
    for i, c in enumerate(spine):
        sec = np.stack([np.zeros(sides + 1), np.sin(ang) * ry[i], np.cos(ang) * rx[i]], axis=-1)
        if droop is not None:
            sec[:, 1] += droop[i] * (np.cos(ang) ** 2)
        rows.append(c + sec)
    p = np.asarray(rows)
    p = p + (noise.fbm(p / 0.08, 2)[..., None] - 0.5) * 0.008
    u = np.tile(ang / (2 * math.pi), (len(spine), 1))
    v = np.tile(np.linspace(0, 1, len(spine))[:, None], (1, sides + 1))
    breakup = noise.fbm(p / weather.noise_scale_m, 2)
    col = np.stack([np.zeros_like(u), weather.salt * breakup * 0.6, np.zeros_like(u),
                    weather.erosion * (0.5 + 0.5 * breakup)], axis=-1)
    uv2 = np.stack([np.full(u.shape, 0.95), np.full(u.shape, float(rng.random()))], axis=-1)
    # The outward hint is taken at the grid point _orient_grid measures (its middle row and column); a hint from
    # another column pointed across the section and wound every loft inside-out (M2-ENV-12).
    mid_r, mid_c = len(spine) // 2, (sides + 1) // 2
    flip = _orient_grid(p, p[mid_r, mid_c] - spine[mid_r])
    # Smooth normals for the LOD (the full mesh is re-faceted by _facet, which recomputes them from the winding).
    kc.quad_strip(mb, p, mat, uv=np.stack([u * 0.3, v * 0.6], axis=-1), col=col, uv2=uv2, flip=flip, smooth=True)


GULLS = {"lintel_gull_a": ("folded", 0.72, 31), "lintel_gull_b": ("raised", 0.82, 32),
         "lintel_gull_c": ("crying", 0.66, 33)}


def lintel_gull(name: str, pose: str, length: float, seed: int, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
    mat = mb.material(M_CARVING)
    s = length / 0.72
    sides = 6 if lod else 9
    n = 5 if lod else 9
    start_v, start_t = mb.vertex_count, mb.triangle_count
    # Body: tail (-X) to breast (+X); sits on a carved perch block.
    t = np.linspace(0.0, 1.0, n)
    spine = np.stack([(-0.36 + 0.62 * t) * s, (0.14 + 0.05 * np.sin(t * math.pi) + 0.03 * t) * s, np.zeros(n)],
                     axis=-1)
    prof = np.sin(np.clip(t, 0.04, 1.0) * math.pi * 0.92) ** 0.8
    _loft(mb, spine, (0.012 + 0.085 * prof) * s, (0.012 + 0.075 * prof) * s, sides, mat, rng, noise)
    # Neck and head.
    neck_lift = {"folded": 0.10, "raised": 0.12, "crying": 0.17}[pose]
    head_c = np.array([0.30 * s, (0.22 + neck_lift) * s, 0.0])
    tn = np.linspace(0.0, 1.0, max(3, n // 2))
    neck = np.array([0.20 * s, 0.18 * s, 0.0])[None, :] * (1 - tn[:, None]) + head_c[None, :] * tn[:, None]
    _loft(mb, neck, (0.05 - 0.012 * tn) * s, (0.055 - 0.012 * tn) * s, sides, mat, rng, noise)
    th = np.linspace(0.0, 1.0, max(4, n // 2 + 1))
    head = head_c[None, :] + np.stack([(-0.05 + 0.11 * th) * s, np.zeros_like(th), np.zeros_like(th)], axis=-1)
    hp = np.sin(np.clip(th, 0.05, 1.0) * math.pi) ** 0.6
    _loft(mb, head, (0.01 + 0.042 * hp) * s, (0.01 + 0.048 * hp) * s, sides, mat, rng, noise)
    # Beak (open for the crying pose: two mandibles).
    beak_root = head_c + np.array([0.055 * s, -0.005 * s, 0.0])
    tilt = {"folded": -0.15, "raised": -0.05, "crying": 0.45}[pose]
    tb = np.linspace(0.0, 1.0, 4)
    for gape in ((0.0,) if pose != "crying" else (0.18, -0.22)):
        d = np.array([math.cos(tilt + gape), math.sin(tilt + gape), 0.0])
        beak = beak_root[None, :] + d[None, :] * (tb[:, None] * 0.11 * s)
        beak[:, 1] -= (tb ** 2) * 0.012 * s * (1 if gape >= 0 else -1)
        _loft(mb, beak, (0.016 * (1 - tb) + 0.002) * s, (0.02 * (1 - tb) + 0.002) * s * (0.6 if gape else 1),
              5, mat, rng, noise)
    # Wings: long flattened lofts from the shoulder back past the tail.
    for side in (-1.0, 1.0):
        tw = np.linspace(0.0, 1.0, n)
        if pose == "raised":
            spine_w = np.stack([(0.12 - 0.5 * tw) * s, (0.2 + 0.24 * tw ** 0.8) * s, side * (0.09 + 0.12 * tw) * s],
                               axis=-1)
        else:
            spine_w = np.stack([(0.14 - 0.56 * tw) * s, (0.19 + 0.01 * tw) * s, side * (0.085 - 0.03 * tw) * s],
                               axis=-1)
        wp = np.sin(np.clip(tw, 0.05, 1.0) * math.pi) ** 0.5 * (1.0 - 0.6 * tw)
        _loft(mb, spine_w, (0.012 + 0.03 * wp) * s, (0.006 + 0.075 * wp) * s, 5, mat, rng, noise)
    # Tail wedge.
    tt = np.linspace(0.0, 1.0, 4)
    tail = np.stack([(-0.34 - 0.14 * tt) * s, (0.14 + 0.02 * tt) * s, np.zeros_like(tt)], axis=-1)
    _loft(mb, tail, (0.04 + 0.03 * tt) * s, (0.02 - 0.012 * tt) * s, 5, mat, rng, noise)
    # Perch block with a tenon into the ridge roll.
    kc.rounded_block(mb, (0.0, 0.045 * s, 0.0), (0.2 * s, 0.045 * s, 0.07 * s), mat, radius=0.012, seg=1,
                     variation=float(rng.random()))
    if not lod:
        _facet(mb, start_v, start_t)
    return mb


def build_gull(name: str) -> list[kc.MeshBuilder]:
    pose, length, seed = GULLS[name]
    return [lintel_gull(name, pose, length, seed), lintel_gull(name, pose, length, seed, lod=True)]
