"""The Stillguard's open-face helm (no bpy), M3-CHR-508: a lacquered shell skull-cap over the cropped head, open at the
face, its rim dropping from the forehead over the temples to the nape and turned out in a narrow gold-piped brim.

The shell is an ellipsoid fitted to the shipped skull (every head-skin vertex above FIT_V inside it by `helm_clear_m`:
over the crop, which the helm hides), cut at the rim line (head heights above the chin, RIM_V, by azimuth): a smooth
lacquered shape, not the skull's facets. A second
layer `helm_thickness_m` inside it, the rim strip between them and a fan at the crown close it. Its UVs sit on Moll's
costume atlas (moll_costume.ATLAS): the outside on the cuirass's top row (red lacquer, the gold piping along the brim),
the inside on the lames' backs, the rim strip on the gold edge. Rigid on the head (build_moll). Deterministic.
"""
from __future__ import annotations

import numpy as np

import moll_costume as C
from asha_costume import TAG_CLOTH
from asha_mesh import Part, grid

COLS = 32
ROWS = 9
CROWN_T = 0.93  # the last ring's share of the way from the rim to the crown (the fan closes the rest)
# the rim line by |azimuth| (degrees from the front): over the forehead, down over the temples, above the ears, to the
# nape (head heights above the chin)
RIM_AZ = (0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0)
RIM_V = (0.82, 0.81, 0.77, 0.73, 0.66, 0.56, 0.52)
HEAD_C_V = 0.55  # the shell's centre height, head heights above the chin (as toma_hair's roots)
FIT_ITERS = 400
FIT_MIN_SHARE = 0.05  # the least share of the worst point's distance its axis may take (a guard on the solve)
FIT_V = 0.74  # head heights above the chin: the skull the shell is fitted to (above the ears)
BRIM_DROP = 0.006  # m: the brim's outer edge below the rim


def skull_ellipsoid(lm, V: np.ndarray, F: np.ndarray, freg: np.ndarray, clear: float) -> tuple:
    """(centre, radii) of an axis-aligned ellipsoid centred on the skull's mid-sagittal box that holds every shipped
    head-skin vertex above FIT_V (each axis grown only as far as a point needs), then `clear` out."""
    zc = float(lm.P("chin")[2])
    used = np.unique(F[np.isin(freg, ["head", "scalp"])])
    used = used[used >= 0]
    P = V[used]
    P = P[P[:, 2] > zc + FIT_V * lm.h]
    c = np.array([0.0, 0.5 * (P[:, 1].min() + P[:, 1].max()), zc + HEAD_C_V * lm.h])
    r = np.array([np.abs(P[:, 0]).max(), 0.5 * (P[:, 1].max() - P[:, 1].min()), P[:, 2].max() - c[2]])
    for _ in range(FIT_ITERS):  # grow only the axis that holds the worst point out, until every point is inside
        q = (P - c) / r
        n = (q * q).sum(axis=1)
        k = int(np.argmax(n))
        if n[k] <= 1.0:
            break
        ax = int(np.argmax(np.abs(q[k])))
        rest = float(n[k] - q[k, ax] ** 2)
        r[ax] = abs(float(P[k, ax] - c[ax])) / np.sqrt(max(1.0 - rest, FIT_MIN_SHARE))
    return c, r + clear


def helm(lm, body, params: dict, surface, V=None, F=None, freg=None) -> Part:
    """The helm as a Part (build_moll's `helm` hook: (lm, body, costume params, head surface, V, F, freg))."""
    S = lm.S
    clear = float(params["helm_clear_m"]) * S
    thick = float(params["helm_thickness_m"])
    zc = float(lm.P("chin")[2])
    c, (ra, rb, rc) = skull_ellipsoid(lm, V, F, freg, clear)
    phi = 2 * np.pi * np.arange(COLS) / COLS
    z_rim = zc + np.interp(np.abs(np.degrees(((phi + np.pi) % (2 * np.pi)) - np.pi)), RIM_AZ, RIM_V) * lm.h
    th0 = np.arccos(np.clip((z_rim - c[2]) / rc, -0.95, 0.95))  # from the top down to the rim

    def point(th: np.ndarray, ph: np.ndarray) -> np.ndarray:
        return c + np.stack([ra * np.sin(th) * np.sin(ph), -rb * np.sin(th) * np.cos(ph), rc * np.cos(th)], axis=-1)

    def normal(th: np.ndarray, ph: np.ndarray) -> np.ndarray:
        n = np.stack([np.sin(th) * np.sin(ph) / ra, -np.sin(th) * np.cos(ph) / rb, np.cos(th) / rc], axis=-1)
        return n / np.linalg.norm(n, axis=-1, keepdims=True)

    P = np.zeros((ROWS + 1, COLS, 3))
    N = np.zeros_like(P)
    for j in range(ROWS):
        th = th0 * (1.0 - CROWN_T * j / (ROWS - 1))
        P[j + 1], N[j + 1] = point(th, phi), normal(th, phi)
    up = np.array([0.0, 0.0, 1.0])
    out = P[1] - c
    out[:, 2] = 0.0
    out /= np.linalg.norm(out, axis=1, keepdims=True)
    P[0] = P[1] + out * float(params["helm_brim_m"]) * S - up * BRIM_DROP * S
    N[0] = N[1]
    top = c + up * rc
    hc = c
    part = Part("Helm")
    u0, v0, u1, v1 = C.ATLAS["cuirass"]
    hv = (v1 - v0) / C.CUIRASS_ROWS_V
    uh = 0.5 * (u1 - u0)  # the top row's front plate
    face = (u0, v0, u0 + uh, v0 + hv)

    def uv(rect):
        return lambda j, i: (rect[0] + (rect[2] - rect[0]) * i / COLS, rect[1] + (rect[3] - rect[1]) * j / ROWS)

    def shell(Pg: np.ndarray, apex: np.ndarray, rect, flip: bool) -> None:
        ids = grid(part, Pg, "cloth", closed_u=True, tags=TAG_CLOTH, flip=flip, uv_fn=uv(rect))
        a = part.add_v(apex, tag=TAG_CLOTH)
        for i in range(COLS):
            f = (int(ids[-1, i]), int(ids[-1, (i + 1) % COLS]), a)
            part.add_f(f[::-1] if flip else f, [(rect[0], rect[3])] * 3, "cloth")

    # the outer layer faces away from the head (grid rows run brim -> crown, columns round to the left)
    a0, b0, c0 = P[1, 0], P[1, 1], P[2, 0]
    flip = bool(np.cross(b0 - a0, c0 - a0) @ (a0 - hc) < 0)
    shell(P, top, face, flip)
    Pin = P - N * thick
    shell(Pin, top - (top - hc) / np.linalg.norm(top - hc) * thick, C.ATLAS["lame_back"], not flip)
    E = np.stack([P[0], Pin[0]], axis=0)
    eu0, ev0, eu1, ev1 = C.ATLAS["top_edge"]
    grid(part, E, "cloth", closed_u=True, tags=TAG_CLOTH, flip=not flip,
         uv_fn=lambda j, i: (eu0 + (eu1 - eu0) * i / COLS, ev0 + (ev1 - ev0) * j))
    if params.get("veil"):  # M4-A2P-051: the Abiding guard's veil, hung from the brim (rigid on the head with it)
        veil(part, lm, params, c, (ra, rb, rc), V, F, freg, flip)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part


VEIL_AZ = 85.0  # degrees either side of the front: the veil's span round the face
VEIL_COLS = 32
VEIL_ROWS = 10
VEIL_THICK = 0.0015  # m: the gauze's two faces
VEIL_FOLDS = 11  # folds across the span
VEIL_FOLD_AMP = (0.0015, 0.006)  # m: a fold's depth at the brim and at the hem (the gauze falls into its folds)
VEIL_HEM_RISE = 0.035  # m: the hem rises this much toward the span's ends (it hangs longest at the front)


def veil(part: Part, lm, params: dict, c: np.ndarray, radii: tuple, V, F, freg, flip: bool) -> None:
    """M4-A2P-051 (act2_ch16.md 5a: "veiled gold lacquer"): a gauze curtain from the helm's rim over the face to
    `veil_drop_m` below the chin, round the front VEIL_AZ either side. Each column stands `veil_clear_m` off the
    furthest head skin in its direction below the rim (the nose, the lips, the chin), so the face never comes through;
    two faces VEIL_THICK apart, on the costume atlas's sash island (the palette's linen: his gauze)."""
    S = lm.S
    ra, rb, _rc = radii
    clear = float(params["veil_clear_m"]) * S
    zc = float(lm.P("chin")[2])
    z_bot = zc - float(params["veil_drop_m"]) * S
    used = np.unique(F[np.isin(freg, ["head", "scalp", "mouth"])])
    H = V[used[used >= 0]]
    az = np.radians(np.linspace(-VEIL_AZ, VEIL_AZ, VEIL_COLS))
    d = np.stack([np.sin(az), -np.cos(az), np.zeros_like(az)], axis=1)  # outward in the plan (front is -Y)
    z_rim = zc + np.interp(np.abs(np.degrees(az)), RIM_AZ, RIM_V) * lm.h
    ell = 1.0 / np.sqrt((np.sin(az) / ra) ** 2 + (np.cos(az) / rb) ** 2)  # the shell's plan radius per column
    Hc = H - np.array([c[0], c[1], 0.0])
    reach = np.zeros(VEIL_COLS)
    for i in range(VEIL_COLS):  # the furthest skin within 12 degrees of this column, below its rim
        below = Hc[:, 2] < z_rim[i]
        ang = np.arctan2(Hc[:, 0], -Hc[:, 1])
        near = below & (np.abs(ang - az[i]) < np.radians(12.0))
        reach[i] = float((Hc[near, :2] @ d[i, :2]).max()) if near.any() else 0.0
    r = np.maximum(ell, reach + clear)
    r = np.maximum(r, np.convolve(np.pad(r, 1, mode="edge"), np.ones(3) / 3.0, mode="valid"))  # no notches
    P = np.zeros((VEIL_ROWS, VEIL_COLS, 3))
    span = np.abs(np.degrees(az)) / VEIL_AZ
    hem = z_bot + VEIL_HEM_RISE * S * span ** 2
    fold = np.cos(np.pi * VEIL_FOLDS * np.degrees(az) / VEIL_AZ)  # a crest at the front
    for j in range(VEIL_ROWS):
        t = j / (VEIL_ROWS - 1)
        z = z_rim + (hem - z_rim) * t
        amp = (VEIL_FOLD_AMP[0] + (VEIL_FOLD_AMP[1] - VEIL_FOLD_AMP[0]) * t) * S
        rr = r + amp * (0.5 + 0.5 * fold)  # folds only outward: the clearance holds
        P[j] = np.array([c[0], c[1], 0.0]) + d * rr[:, None] + np.stack([np.zeros(VEIL_COLS)] * 2 + [z], axis=1)
    u0, v0, u1, v1 = C.ATLAS["sash"]
    rect = lambda j, i: (u0 + (u1 - u0) * i / (VEIL_COLS - 1), v0 + (v1 - v0) * j / (VEIL_ROWS - 1))  # noqa: E731
    grid(part, P, "cloth", tags=TAG_CLOTH, flip=flip, uv_fn=rect)
    grid(part, P - d[None, :, :] * VEIL_THICK * S, "cloth", tags=TAG_CLOTH, flip=not flip, uv_fn=rect)
