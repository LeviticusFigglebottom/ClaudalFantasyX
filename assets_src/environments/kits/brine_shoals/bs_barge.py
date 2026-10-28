"""Sefir's white progress barge (brine_shoals.md §2; ADR 0017 (a); bible §5: poled, never rowed, no wake).
Pure numpy; see bs_common.py.

  white_barge   12 m x 3.4 m, flat-bottomed and square-ended with raked ends, draft 0.5 m (origin at the
                waterline, bow toward +X); white lacquer with a thin lacquer-red sheer line; a low four-post
                canopy whose roof carries a small tiered red base and gilded bowl-dome finial (Ansedra's
                skyline in miniature); a stern platform for the pole-men and a 5 m pole in its crutches.
                M3-ENV-705 (B05 read flat white): the Order's trim. The gilt Level line along each side over
                red-lacquer panel studs; gilt capitals on the canopy posts, a white fringe round the roof and white
                curtains tied back at the posts; an upswept red prow post carrying the Level sign (a gilt disc
                crossed by its bar); a red cushion on the bench. Red and gold stay lines and points
                (test_order_colours_stay_small).
"""

from __future__ import annotations

import math

import numpy as np

import bs_common as bc
from bs_common import kc

TRI_BUDGET = {"white_barge": (12000, 1200)}

LENGTH, BEAM, DRAFT, FREEBOARD = 12.0, 3.4, 0.5, 0.62
CLEAN = kc.Weathering(moss=0.0, salt=0.0, wet=0.0, erosion=0.05)


def _section(x: float) -> np.ndarray:
    """Half-section points (gunwale -> chine -> centre bottom) at station x, port side (z < 0)."""
    t = abs(x) / (LENGTH * 0.5)
    rake = kc.smoothstep(0.72, 1.0, t)  # the bottom sweeps up into the raked ends
    bottom_y = -DRAFT + (DRAFT + 0.05) * float(rake) ** 1.4
    half_bottom = (BEAM * 0.5 - 0.25) * (1.0 - 0.18 * float(rake))
    half_top = BEAM * 0.5 * (1.0 - 0.1 * float(rake))
    sheer = FREEBOARD + 0.12 * t ** 2
    return np.array([[x, sheer, -half_top], [x, (sheer + bottom_y) * 0.5 + 0.05, -(half_top * 0.6 + half_bottom * 0.4)],
                     [x, bottom_y, -half_bottom], [x, bottom_y - 0.01, 0.0]])


def hull_grid(n_x: int) -> np.ndarray:
    xs = np.linspace(-LENGTH * 0.5, LENGTH * 0.5, n_x)
    rows = []
    for x in xs:
        port = _section(x)
        stbd = port[::-1][1:] * np.array([1.0, 1.0, -1.0])
        rows.append(np.vstack([port, stbd]))
    return np.asarray(rows)


def build_barge(seed: int = 601) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("white_barge", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("white_barge" + (bc.LOD if lod else ""))
        wm, red, gold = mb.material(bc.M_BARGE), mb.material(bc.M_RED), mb.material(bc.M_GOLD)
        grid = hull_grid(25 if not lod else 7)
        uv = np.stack([np.broadcast_to(np.arange(grid.shape[1])[None, :] * 0.5, grid.shape[:2]),
                       np.broadcast_to(np.linspace(0, LENGTH, grid.shape[0])[:, None], grid.shape[:2])], axis=-1)
        col = np.array([0.0, 0.0, 0.0, 0.05])
        # Outer hull (faces outward: away from the centre line and down).
        flip = float(np.dot(np.cross(grid[0, 1] - grid[0, 0], grid[1, 0] - grid[0, 0]), [0.0, 0.3, -1.0])) < 0
        kc.quad_strip(mb, grid, wm, uv=uv, col=col, uv2=np.array([0.95, 0.5]), flip=flip)
        # Square end transoms.
        for row, sgn in ((grid[0], -1.0), (grid[-1], 1.0)):
            c = row.mean(axis=0)
            base = mb.add_vertices(np.vstack([row, c[None]]), np.tile([sgn, 0.0, 0.0], (len(row) + 1, 1)),
                                   np.zeros((len(row) + 1, 2)), np.tile([0.9, 0.5], (len(row) + 1, 1)),
                                   np.tile(col, (len(row) + 1, 1)))
            for k in range(len(row) - 1):
                if sgn > 0:
                    mb.add_tri(base + k, base + k + 1, base + len(row), wm)
                else:
                    mb.add_tri(base + k + 1, base + k, base + len(row), wm)
        deck_y = 0.42
        # Deck and the bulwarks' inner faces.
        xs = np.linspace(-LENGTH * 0.5 + 0.05, LENGTH * 0.5 - 0.05, 13 if not lod else 3)
        half = np.array([_section(x)[0, 2] for x in xs]) * -1.0 - 0.06
        dgrid = np.stack([np.stack([xs, np.full_like(xs, deck_y), -half], axis=-1),
                          np.stack([xs, np.full_like(xs, deck_y), half], axis=-1)], axis=1)
        dflip = float(np.cross(dgrid[0, 1] - dgrid[0, 0], dgrid[1, 0] - dgrid[0, 0])[1]) < 0
        kc.quad_strip(mb, dgrid, wm, uv=np.zeros(dgrid.shape[:2] + (2,)), col=col, uv2=np.array([0.85, 0.4]),
                      flip=dflip, smooth=False)
        for s in (-1.0, 1.0):
            sheer = np.array([_section(x)[0] for x in xs]) * np.array([1.0, 1.0, -s * -1.0 if s > 0 else 1.0])
            sheer[:, 2] = s * (np.abs(sheer[:, 2]) - 0.06)
            low = sheer.copy()
            low[:, 1] = deck_y
            bgrid = np.stack([low, sheer], axis=1)
            bflip = float(np.dot(np.cross(bgrid[0, 1] - bgrid[0, 0], bgrid[1, 0] - bgrid[0, 0]), [0, 0, -s])) < 0
            kc.quad_strip(mb, bgrid, wm, uv=np.zeros(bgrid.shape[:2] + (2,)), col=col, uv2=np.array([0.8, 0.5]),
                          flip=bflip, smooth=False)
        if lod:
            kc.rounded_block(mb, (0.3, 1.6, 0.0), (2.3, 0.04, 1.4), wm, radius=0.02, seg=1)
            out.append(mb)
            continue
        # Gunwale cap rail and the lacquer-red sheer line just below it.
        for s in (-1.0, 1.0):
            pts = np.array([_section(x)[0] for x in np.linspace(-LENGTH * 0.5, LENGTH * 0.5, 13)])
            pts[:, 2] = s * np.abs(pts[:, 2])
            for a, b in zip(pts[:-1], pts[1:]):
                kc.plank(mb, a + (0, 0.03, 0), b + (0, 0.03, 0), 0.12, 0.05, wm, weather=CLEAN, variation=0.5)
                o = np.array([0.0, -0.08, s * 0.012])
                kc.plank(mb, a + o, b + o, 0.06, 0.015, red, up=np.array([0.0, 0.0, s]), weather=CLEAN, variation=0.5)
        # The canopy: four posts, a gently arched roof, the finial (tiered red base, gilded bowl, spire).
        cx, hx, hz, top = 0.3, 2.2, 1.25, 2.55
        for sx in (-1, 1):
            for sz in (-1, 1):
                kc.tube(mb, np.array([[cx + sx * hx, deck_y, sz * hz], [cx + sx * hx, top, sz * hz]]), 0.055, 8, wm,
                        weather=CLEAN, cap_end=True)
                kc.rounded_block(mb, (cx + sx * hx, top - 0.06, sz * hz), (0.09, 0.06, 0.09), gold, radius=0.02,
                                 seg=1)
        rx = np.linspace(cx - hx - 0.25, cx + hx + 0.25, 9)
        rz = np.linspace(-hz - 0.3, hz + 0.3, 7)
        X, Z = np.meshgrid(rx, rz, indexing="ij")
        roof = np.stack([X, top + 0.05 + 0.22 * (1.0 - (Z / (hz + 0.3)) ** 2), Z], axis=-1)
        for f in (False, True):
            kc.quad_strip(mb, roof + (0, -0.03 * f, 0), wm, uv=np.zeros(roof.shape[:2] + (2,)), col=col,
                          uv2=np.array([0.9, 0.5]), flip=f)
        rt = top + 0.27
        kc.tube(mb, np.array([[cx, rt - 0.02, 0], [cx, rt + 0.08, 0]]), 0.2, 12, red, cap_end=True)
        kc.tube(mb, np.array([[cx, rt + 0.08, 0], [cx, rt + 0.14, 0]]), 0.15, 12, red, cap_end=True)
        a = np.linspace(0.0, math.pi * 0.5, 6)
        dome = np.stack([np.full_like(a, cx), rt + 0.14 + np.sin(a) * 0.17, np.zeros_like(a)], axis=-1)
        kc.tube(mb, dome, np.cos(a) * 0.17 + 0.005, 12, gold, cap_end=True)
        kc.tube(mb, np.array([[cx, rt + 0.3, 0], [cx, rt + 0.75, 0]]), np.array([0.018, 0.004]), 6, gold)
        _trim(mb, rng, deck_y, cx, hx, hz, top)
        # A bench and its cushion under the canopy.
        kc.rounded_block(mb, (cx - 1.2, deck_y + 0.16, 0.0), (0.24, 0.16, 0.7), wm, radius=0.03, seg=2, weather=CLEAN)
        kc.rounded_block(mb, (cx - 1.2, deck_y + 0.36, 0.0), (0.22, 0.05, 0.66), red, radius=0.04, seg=2)
        kc.rounded_block(mb, (cx - 1.42, deck_y + 0.5, 0.0), (0.04, 0.2, 0.7), wm, radius=0.02, seg=1, weather=CLEAN)
        # Stern platform for the pole-men; crutches and the lying pole (plain timber).
        sx0 = -LENGTH * 0.5 + 0.2
        kc.rounded_block(mb, (sx0 + 0.6, deck_y + 0.12, 0.0), (0.6, 0.12, 1.3), wm, radius=0.02, seg=1, weather=CLEAN)
        for x in (sx0 + 0.6, sx0 + 4.4):
            kc.tube(mb, np.array([[x, deck_y, 1.45], [x, deck_y + 0.55, 1.45]]), 0.03, 6, wm, cap_end=True)
        kc.tube(mb, np.array([[sx0 + 0.1, deck_y + 0.58, 1.45], [sx0 + 5.1, deck_y + 0.6, 1.45]]), 0.035, 6,
                mb.material(bc.M_TIMBER), cap_start=True, cap_end=True, weather=bc.CAMP, noise=noise, disp_m=0.002)
        out.append(mb)
    return out


def _trim(mb, rng, deck_y: float, cx: float, hx: float, hz: float, top: float) -> None:
    """The Order's trim on the hull and the canopy (M3-ENV-705; see the module notes)."""
    red, gold, cloth = mb.material(bc.M_RED), mb.material(bc.M_GOLD), mb.material(bc.M_CANVAS)
    xs = np.linspace(-LENGTH * 0.5 + 0.8, LENGTH * 0.5 - 0.8, 15)
    for s in (-1.0, 1.0):
        sec = np.array([_section(x) for x in xs])
        top_pt, mid_pt = sec[:, 0].copy(), sec[:, 1].copy()
        top_pt[:, 2] *= -s
        mid_pt[:, 2] *= -s
        line = top_pt + (mid_pt - top_pt) * 0.55
        line[:, 2] += s * 0.03
        # The gilt Level line: a flat leaf strip laid on the side, facing out (gold stays a line, not a surface).
        strip = np.stack([line + np.array([0.0, 0.014, 0.0]), line - np.array([0.0, 0.014, 0.0])], axis=0)
        n0 = np.cross(strip[0, 1] - strip[0, 0], strip[1, 0] - strip[0, 0])
        kc.quad_strip(mb, strip, gold, uv=np.zeros(strip.shape[:2] + (2,)), col=(0.0, 0.0, 0.0, 0.05),
                      uv2=(0.95, 0.5), flip=bool(n0[2] * s < 0.0), smooth=False)
        for k in range(0, len(xs), 2):  # the panel studs: red lacquer, gilt-capped, between line and sheer
            p = top_pt[k] + (line[k] - top_pt[k]) * 0.5 + np.array([0.0, 0.0, s * 0.03])
            kc.rounded_block(mb, p, (0.06, 0.1, 0.02), red, radius=0.01, seg=1)
            kc.rounded_block(mb, p + np.array([0.0, 0.11, 0.0]), (0.07, 0.015, 0.025), red, radius=0.005, seg=1)
    # The roof's white fringe: an edge rod and tassels every 0.3 m round it.
    rx0, rx1, rz0 = cx - hx - 0.25, cx + hx + 0.25, hz + 0.3
    edge = np.array([[rx0, top + 0.05, -rz0], [rx1, top + 0.05, -rz0], [rx1, top + 0.05, rz0], [rx0, top + 0.05, rz0],
                     [rx0, top + 0.05, -rz0]])
    kc.tube(mb, edge, 0.025, 6, cloth)
    for a, b in zip(edge[:-1], edge[1:]):
        n = int(np.linalg.norm(b - a) / 0.3)
        for t in np.linspace(0.0, 1.0, n, endpoint=False):
            q = a + (b - a) * t
            kc.tube(mb, np.array([q, q - np.array([0.0, 0.16, 0.0])]), np.array([0.012, 0.025]), 4, cloth, cap_end=True)
    # White curtains along the long sides, hanging from the roof edge and tied back to each post.
    for sz in (-1.0, 1.0):
        z = sz * (hz + 0.02)
        for sx in (-1.0, 1.0):
            x_post = cx + sx * hx
            x_free = cx + sx * 0.35
            u = np.linspace(0.0, 1.0, 6)
            v = np.linspace(0.0, 1.0, 7)
            U, V = np.meshgrid(u, v, indexing="ij")
            # Gathered toward the post near the tie (V ~ 0.55), falling free above and below it.
            gather = np.sin(np.clip(V / 0.55, 0.0, 1.0) * math.pi * 0.5) * (1.0 - 0.6 * np.clip((V - 0.55) / 0.45, 0, 1))
            X = x_free + (x_post - x_free) * (U * (1.0 - 0.85 * gather) + 0.85 * gather)
            Y = top - V * (top - deck_y - 0.15)
            Z = np.full_like(X, z) + sz * 0.04 * np.sin(U * math.pi * 5.0) * (1.0 - gather)
            grid = np.stack([X, Y, Z], -1)
            for f in (False, True):
                kc.quad_strip(mb, grid, cloth, uv=np.stack([U, V], -1), col=(0.0, 0.0, 0.0, 0.1),
                              uv2=(0.9, float(rng.random())), flip=f)
            tie = np.array([x_post - sx * 0.12, top - 0.55 * (top - deck_y - 0.15), z])
            kc.tube(mb, np.array([tie - [0.0, 0.0, 0.08], tie + [0.0, 0.0, 0.08]]), 0.03, 6, red)
    # The prow post at the bow, swept up, carrying the Level sign.
    t = np.linspace(0.0, 1.0, 9)
    bow = LENGTH * 0.5 - 0.1
    post = np.stack([bow + 0.35 * t ** 2, FREEBOARD + 0.12 + 1.3 * t, np.zeros_like(t)], -1)
    kc.tube(mb, post, np.linspace(0.08, 0.05, len(t)), 8, red, cap_end=True)
    sign = post[-1] + np.array([0.0, 0.25, 0.0])
    a = np.linspace(0.0, 2 * math.pi, 17)
    kc.tube(mb, np.stack([sign[0] + np.zeros_like(a), sign[1] + np.sin(a) * 0.22, sign[2] + np.cos(a) * 0.22], -1),
            0.025, 5, gold)
    kc.rounded_block(mb, sign, (0.025, 0.02, 0.3), gold, radius=0.01, seg=1)


TARGETS = {"white_barge": build_barge}
