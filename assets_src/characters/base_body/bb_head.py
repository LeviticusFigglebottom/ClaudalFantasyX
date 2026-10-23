"""Head cage with face loop-flow (M1-CHR-02, review-sweep-B on M1-CHR-01). Pure numpy, no bpy.

The head is a box lattice ray-cast from the head centre onto the head field, like the M1-CHR-01
cage, but the lattice lines are placed on the face's landmarks and two kinds of feature block are
cut out of its front face and refilled with concentric loops:

* **Eyes** (6 x 2 cells, 16-vertex loops): two orbicularis-oculi loops interpolated from the block
  boundary toward the almond, a crease / lower-lid loop, the lid's outer surface, then the lid
  margin as two pinned loops (outer edge on the lid surface, inner edge on the globe: the margin's
  thickness), then a socket loop inside the globe, capped. The canthi are block-side midpoints,
  so they are loop vertices, and every loop is a true edge loop around the eye.
* **Mouth** (14 x 4 cells, 36-vertex loops): the nasolabial / outer orbicularis-oris loop, a
  second orbicularis loop, the vermilion border, mid-vermilion, the contact line (pinned), the
  inner lip (pinned) and the mouth bag, capped. The mouth corners are block-side midpoints.

Poles (valence 3 / 5) sit only at the block corners: lateral brow, the side of the nasal bridge,
below the lateral canthus, beside the alae and below the mouth corners, away from the lid and lip
lines. After one Catmull-Clark level each loop doubles (eye 32, mouth 72 vertices).

Ring vertex positions come from the face frames in bb_face (EyeFrame.contour / margin_point and
the lip outline from Face._lips' border heights), so the loops follow the sculpt's sliders.
"""
from __future__ import annotations

import math

import numpy as np

from bb_params import v3

Arr = np.ndarray

# Lattice lines on the front face, in metres at Asha's head (h = 0.222), scaled by h / 0.222.
# X (half, the other half mirrored): the eye block is lines 12..54 mm, the mouth block 0..40 mm.
X_HALF_MM = [0.0, 6.0, 12.0, 19.0, 26.0, 33.0, 40.0, 47.0, 54.0, None]  # None = head half-width
EYE_X_LINES = (2, 8)  # eye block spans X_HALF lines 2..8 (6 cells)
MOUTH_X_LINE = 6  # mouth block spans -line 6 .. +line 6 (12 cells)
NY = 8  # depth cells (front to back)
NECK_HOLE_X = 6  # neck hole on the bottom face spans -line 6 .. +line 6 (12 cells, +-40 mm)
NECK_HOLE_Y = (2, 6)  # and depth cells 2..6 (4 cells, centred under the neck column): 32 vertices


def _z_lines(lm) -> tuple[Arr, dict]:
    """Z lattice lines (absolute) and the indices of the feature blocks."""
    h = lm.h
    zc = lm.P("chin")[2]
    s = h / 0.222
    zm = lm.P("mouth")[2]
    ze = lm.P("eye")[2]
    mouth = [zm - 0.0155 * s, zm - 0.0078 * s, zm, zm + 0.0080 * s, zm + 0.0160 * s]
    eye = [ze - 0.0115 * s, ze, ze + 0.0125 * s]
    z = [zc, zc + 0.012 * s, zc + 0.022 * s] + mouth + [zc + 0.326 * h, zc + 0.38 * h, zc + 0.42 * h] + eye
    z += [zc + 0.64 * h, zc + 0.82 * h, zc + 1.0 * h]
    idx = {"mouth": (3, 7), "eye": (11, 13)}
    return np.array(z), idx


def _x_lines(lm) -> Arr:
    s = lm.h / 0.222
    half = [x * 0.001 * s if x is not None else lm.head_w * 0.5 for x in X_HALF_MM]
    return np.array([-v for v in half[:0:-1]] + half)


def cast_in(body, region, O: Arr, D: Arr, tmax: float = 0.12, steps: int = 240) -> Arr:
    """First entry into the region's field along rays O + t D (origins outside)."""
    D = D / np.linalg.norm(D, axis=1, keepdims=True)
    ts = np.linspace(0.0, tmax, steps)
    pts = O[:, None, :] + D[:, None, :] * ts[None, :, None]
    d = body.sdf(pts.reshape(-1, 3), region).reshape(len(O), steps)
    j = np.argmax(d < 0, axis=1)
    j = np.maximum(j, 1)
    lo, hi = ts[j - 1].copy(), ts[j].copy()
    for _ in range(20):
        mid = 0.5 * (lo + hi)
        inside = body.sdf(O + D * mid[:, None], region) < 0
        hi = np.where(inside, mid, hi)
        lo = np.where(inside, lo, mid)
    return O + D * hi[:, None]


def build_head(cg, cast) -> Arr:
    """Adds the head to the cage; returns the neck-hole loop (32 vertices)."""
    lm, body = cg.lm, cg.body
    h = lm.h
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    O = v3(0, yc + 0.02 * h, zc + 0.5 * h)
    X = _x_lines(lm)
    Z, zidx = _z_lines(lm)
    nx, nz = len(X) - 1, len(Z) - 1
    ny = NY
    y_front, y_back = yc - 0.40 * h, yc + 0.47 * h
    Y = np.linspace(y_front, y_back, ny + 1)
    Y[1] = y_front + 0.06 * h
    mid_x = nx // 2
    ids: dict[tuple[int, int, int], int] = {}
    keys, pts = [], []
    for i in range(nx + 1):
        for j in range(ny + 1):
            for k in range(nz + 1):
                if i in (0, nx) or j in (0, ny) or k in (0, nz):
                    keys.append((i, j, k))
                    pts.append(v3(X[i], Y[j], Z[k]))
    B = np.array(pts)
    hits = cast(body, "head", np.repeat(O[None, :], len(B), axis=0), B - O, tmax=0.3, steps=200)
    vid = cg.add(hits, "head")
    for key, v in zip(keys, vid):
        ids[key] = int(v)

    ex0, ex1 = mid_x + EYE_X_LINES[0], mid_x + EYE_X_LINES[1]  # left eye (+X) block x cells
    rx0, rx1 = mid_x - EYE_X_LINES[1], mid_x - EYE_X_LINES[0]  # right eye
    mx0, mx1 = mid_x - MOUTH_X_LINE, mid_x + MOUTH_X_LINE
    ez0, ez1 = zidx["eye"]
    mz0, mz1 = zidx["mouth"]
    hx0, hx1 = mid_x - NECK_HOLE_X, mid_x + NECK_HOLE_X
    hy0, hy1 = NECK_HOLE_Y

    def skip(face: str, a: int, b: int) -> bool:
        if face == "front":  # a = x cell, b = z cell
            if ez0 <= b < ez1 and (ex0 <= a < ex1 or rx0 <= a < rx1):
                return True
            if mz0 <= b < mz1 and mx0 <= a < mx1:
                return True
        if face == "bottom":  # a = x cell, b = y cell
            if hx0 <= a < hx1 and hy0 <= b < hy1:
                return True
        return False

    front_faces = []
    faces = []
    for a in range(nx):
        for b in range(nz):
            if not skip("front", a, b):
                front_faces.append((ids[(a, 0, b)], ids[(a + 1, 0, b)], ids[(a + 1, 0, b + 1)], ids[(a, 0, b + 1)]))
            faces.append((ids[(a, ny, b)], ids[(a, ny, b + 1)], ids[(a + 1, ny, b + 1)], ids[(a + 1, ny, b)]))
    for a in range(ny):
        for b in range(nz):
            faces.append((ids[(0, a, b)], ids[(0, a, b + 1)], ids[(0, a + 1, b + 1)], ids[(0, a + 1, b)]))
            faces.append((ids[(nx, a, b)], ids[(nx, a + 1, b)], ids[(nx, a + 1, b + 1)], ids[(nx, a, b + 1)]))
    for a in range(nx):
        for b in range(ny):
            faces.append((ids[(a, b, nz)], ids[(a + 1, b, nz)], ids[(a + 1, b + 1, nz)], ids[(a, b + 1, nz)]))
            if not skip("bottom", a, b):
                faces.append((ids[(a, b, 0)], ids[(a, b + 1, 0)], ids[(a + 1, b + 1, 0)], ids[(a + 1, b, 0)]))
    # face regions: "head" = the face mask (the lattice's front face and the feature loops), "scalp" =
    # the rest of the skull (under the hair; it gets a lower texel density in the UV pack)
    for q in front_faces:
        cg.quad(*q, "head")
    for q in faces:
        cg.quad(*q, "scalp")
    # UV: the face mask is its own island (cut in front of the ears, along the hairline and under the
    # chin), so a conformal unwrap does not shrink the face into the middle of a skull-sized island
    for k in range(nz):
        cg.seam(ids[(0, 0, k)], ids[(0, 0, k + 1)])
        cg.seam(ids[(nx, 0, k)], ids[(nx, 0, k + 1)])
    for i in range(nx):
        cg.seam(ids[(i, 0, 0)], ids[(i + 1, 0, 0)])
        cg.seam(ids[(i, 0, nz)], ids[(i + 1, 0, nz)])
    # back-of-head seam: x = mid on the back face, then over the top to the middle
    for k in range(0, nz):
        cg.seam(ids[(mid_x, ny, k)], ids[(mid_x, ny, k + 1)])
    for j in range(ny, ny // 2, -1):
        cg.seam(ids[(mid_x, j, nz)], ids[(mid_x, j - 1, nz)])

    def block_loop(a0: int, a1: int, b0: int, b1: int) -> list[int]:
        loop = [ids[(a, 0, b0)] for a in range(a0, a1 + 1)]
        loop += [ids[(a1, 0, b)] for b in range(b0 + 1, b1 + 1)]
        loop += [ids[(a, 0, b1)] for a in range(a1 - 1, a0 - 1, -1)]
        loop += [ids[(a0, 0, b)] for b in range(b1 - 1, b0, -1)]
        return loop

    for side, (a0, a1) in (("L", (ex0, ex1)), ("R", (rx0, rx1))):
        _eye(cg, np.array(block_loop(a0, a1, ez0, ez1)), side)
    _mouth(cg, np.array(block_loop(mx0, mx1, mz0, mz1)))
    hole = block_loop_bottom(ids, hx0, hx1, hy0, hy1)
    return np.array(hole)


def block_loop_bottom(ids, a0: int, a1: int, b0: int, b1: int) -> list[int]:
    hole = [ids[(a, b0, 0)] for a in range(a0, a1 + 1)]
    hole += [ids[(a1, b, 0)] for b in range(b0 + 1, b1 + 1)]
    hole += [ids[(a, b1, 0)] for a in range(a1 - 1, a0 - 1, -1)]
    hole += [ids[(a0, b, 0)] for b in range(b1 - 1, b0, -1)]
    return hole


def _onto_face(cg, xz: Arr) -> Arr:
    """Frontal (x, z) points -> the head surface in front of them (ray along +Y)."""
    lm = cg.lm
    y0 = lm.P("head_c")[1] - 0.62 * lm.h
    O = np.stack([xz[:, 0], np.full(len(xz), y0), xz[:, 1]], axis=1)
    D = np.repeat(np.array([[0.0, 1.0, 0.0]]), len(xz), axis=0)
    return cast_in(cg.body, "head", O, D, tmax=0.40 * lm.h * 1.6, steps=320)


def _loop_angles(xz: Arr, cx: float, cz: float, hx: float, hz: float) -> Arr:
    """Angles of boundary vertices around a block centre, in block-normalised coordinates."""
    return np.unwrap(np.arctan2((xz[:, 1] - cz) / hz, (xz[:, 0] - cx) / hx))


def _eye(cg, B: Arr, side: str) -> None:
    import bb_anatomy

    lm = cg.lm
    fr = cg.body.face.eyes[side]
    V = cg.V
    xz = V[B][:, [0, 2]]
    cx, cz = 0.5 * (xz[:, 0].min() + xz[:, 0].max()), 0.5 * (xz[:, 1].min() + xz[:, 1].max())
    hx, hz = 0.5 * (xz[:, 0].max() - xz[:, 0].min()), 0.5 * (xz[:, 1].max() - xz[:, 1].min())
    ang = _loop_angles(xz, cx, cz, hx, hz)
    # contour angle: in eye-local terms (a toward the outer canthus); mirror for the right eye
    t = ang if side == "L" else math.pi - ang
    a, b = fr.contour(t)
    E = fr.E

    def contour_xz(scale: float) -> Arr:
        return np.stack([E[0] + fr.sgn * a * scale, E[2] + b * scale], axis=1)

    th = bb_anatomy.LID_THICKNESS * lm.S
    rings = []
    for s_blend, scale in ((0.42, 2.1), (0.75, 1.55), (1.0, 1.16)):
        p = (1 - s_blend) * xz + s_blend * contour_xz(scale)
        rings.append((cg.add(_onto_face(cg, p), "head"), False))
    rings.append((cg.add(fr.margin_point(t, th * 0.96), "head", pin=True), True))  # margin, outer edge
    rings.append((cg.add(fr.margin_point(t, 0.00025), "head", pin=True), True))  # margin, on the globe
    sock = E + np.stack([fr.sgn * a * 0.62, np.full(len(a), -0.30 * fr.R), b * 0.62], axis=1)
    rings.append((cg.add(sock, "head", pin=True), True))
    prev = B
    for r, _p in rings:
        cg.bridge(prev, r, "head")
        prev = r
    cg.seam_loop(rings[4][0])
    n = len(B)
    cap = cg.fill_grid(rings[-1][0], 2, n // 2 - 2, "head", pin=True)
    for rr in range(1, cap.shape[0] - 1):
        for cc in range(1, cap.shape[1] - 1):
            i = cap[rr, cc]
            cg.set_pos([i], [cg.V[i] + v3(0, 0.22 * fr.R, 0)])
    cg.groups[f"eyelid_{side}"] = rings[3][0].tolist() + rings[4][0].tolist()
    cg.groups[f"eye_rings_{side}"] = [r.tolist() for r, _p in rings]


def lip_outline(face, x: Arr, upper: bool) -> Arr:
    """z of the vermilion border (upper or lower) at x, from the same terms as Face._lips."""
    s = face.s
    p = face.p
    fl = float(p["lip_fullness"])
    W = face.mouth_half
    zm = face.lm.P("mouth")[2]
    xr = np.abs(x) / W
    lift = float(p["mouth_corner_lift"]) * xr * xr
    if upper:
        bow = 0.0012 * s * np.exp(-(((xr - 0.21) / 0.11) ** 2)) - 0.0006 * s * np.exp(-((xr / 0.08) ** 2))
        hgt = (0.0068 * s * fl) * (1.0 - 0.70 * xr * xr) + bow
        return zm + lift + np.maximum(hgt, 0.0004 * s)
    hgt = (0.0090 * s * fl) * (1.0 - 0.62 * xr * xr)
    return zm + lift - np.maximum(hgt, 0.0004 * s)


def _mouth(cg, B: Arr) -> None:
    lm, face = cg.lm, cg.body.face
    h = lm.h
    s = h / 0.222
    M = lm.P("mouth")
    V = cg.V
    xz = V[B][:, [0, 2]]
    cx, cz = 0.0, M[2]
    hx, hz = 0.5 * (xz[:, 0].max() - xz[:, 0].min()), 0.5 * (xz[:, 1].max() - xz[:, 1].min())
    ang = _loop_angles(xz, cx, cz, hx, hz)
    W = face.mouth_half
    lift = float(lm.p["mouth_corner_lift"])
    up = np.sin(ang) > 1e-6
    lo = np.sin(ang) < -1e-6
    x = W * np.cos(ang)
    zz_line = M[2] + lift * (x / W) ** 2 + 0.00035 * s * np.sign(np.sin(ang))
    z_border = np.where(up, lip_outline(face, x, True), np.where(lo, lip_outline(face, x, False), zz_line))
    rings = []
    # nasolabial / outer orbicularis loop, then a second loop, both interpolated toward a lip-shaped
    # outline grown around the mouth; then the vermilion border and mid-vermilion
    for s_blend, grow in ((0.40, 2.2), (0.72, 1.5)):
        zt = M[2] + (z_border - M[2]) * grow
        xt = x * (1.0 + 0.12 * (grow - 1.0))
        p = (1 - s_blend) * xz + s_blend * np.stack([xt, zt], axis=1)
        rings.append(cg.add(_onto_face(cg, p), "head"))
    rings.append(cg.add(_onto_face(cg, np.stack([x * 1.01, z_border], axis=1)), "head"))
    zmid = 0.5 * (z_border + zz_line)
    rings.append(cg.add(_onto_face(cg, np.stack([x, zmid], axis=1)), "head"))
    # contact line: on the lips' surface, just inside the crevice (pinned)
    line = _onto_face(cg, np.stack([x * 0.995, zz_line], axis=1)) + v3(0, 0.0018 * s, 0)
    li = cg.add(line, "head", pin=True)
    rings.append(li)
    inner = line + np.stack([np.zeros(len(x)), np.full(len(x), 0.0045 * s), np.sign(np.sin(ang)) * 0.0022 * s], axis=1)
    inner[:, 0] *= 0.96
    rings.append(cg.add(inner, "head", pin=True))
    bag = np.stack([x * 0.72, line[:, 1] + 0.016 * s, M[2] + np.sign(np.sin(ang)) * 0.010 * s], axis=1)
    gi = cg.add(bag, "head", pin=True)
    rings.append(gi)
    prev = B
    for k, r in enumerate(rings):
        # faces behind the inner lip (the wet inner lip onward) are the mouth bag
        cg.bridge(prev, r, "mouth" if k >= len(rings) - 2 else "head")
        prev = r
    cg.seam_loop(li)
    n = len(B)
    cg.fill_grid(gi, 2, n // 2 - 2, "head", pin=True, bulge=v3(0, 0.010 * s, 0), freg="mouth")
    cg.groups["lip_line"] = li.tolist()
    cg.groups["mouth_rings"] = [r.tolist() for r in rings]
