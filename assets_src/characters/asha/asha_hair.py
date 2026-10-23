"""Asha's hair cards (no bpy), asha.md §5 and the hair contract in character_shading.md.

Black, very long hair parted on the left, drawn back into one three-strand side braid that starts
behind the left ear and falls over the front of the left shoulder to the hip:

* **Scalp**: three layers of cards (base, mid, top), rooted inside the hairline and traced over the
  scalp along a flow field toward the braid's gather point G behind the left ear; the part line
  on the left splits the flow. Cards lie in the scalp's tangent plane, lifted per layer.
* **Braid**: three strand tubes woven around a spine (x = A sin(t + phi), depth = B sin 2(t + phi)),
  the spine pushed clear of the body field; three shell clasps; a loose 9 cm tail of cards.
* **Flyaways** (thin, low alpha) at the crown and on the braid, and two uncut face-framing strands
  on the right temple.
* **Comb**: her mother's tortoiseshell comb behind the left ear.

UVs: the 2K atlas (asha_textures.hair_atlas) has 16 strand-clump columns; a card uses one column,
V root (0) -> tip (1). Vertex colour = wind weights (R primary, G secondary, B phase, A flutter;
character_wind.gdshaderinc); scalp cards are pinned (R = 0). Seeded, deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, arclen, catmull_rom, frames_along, grid, tube

CLUMPS = 16
TAG_HAIR = 41


def hairline_v(lm, P: np.ndarray) -> np.ndarray:
    """Hairline height (head heights above the chin) for points P, by azimuth around the head axis.
    0 = front, +90 = the character's left. The front is 'moderately high' (asha.md §6.1)."""
    yc = lm.P("head_c")[1]
    phi = np.degrees(np.arctan2(P[:, 0], -(P[:, 1] - yc)))
    a = np.abs(phi)
    xs = [0, 30, 50, 66, 76, 84, 96, 112, 135, 160, 180]
    vs = [0.80, 0.785, 0.735, 0.665, 0.60, 0.585, 0.635, 0.50, 0.32, 0.25, 0.24]
    return np.interp(a, xs, vs)


def in_hair(lm, P: np.ndarray, margin_h: float = 0.0) -> np.ndarray:
    zc = lm.P("chin")[2]
    v = (P[:, 2] - zc) / lm.h
    return v > hairline_v(lm, P) + margin_h


class Scalp:
    """Projection onto the head field and its normals (head region only, no lids)."""

    def __init__(self, body) -> None:
        self.body = body
        self.reg = body.regions["head"]

    def sdf(self, P: np.ndarray) -> np.ndarray:
        return self.reg.sdf(P)

    def normal(self, P: np.ndarray) -> np.ndarray:
        e = 3e-4
        g = np.zeros_like(P)
        for i in range(3):
            d = np.zeros(3)
            d[i] = e
            g[:, i] = self.sdf(P + d) - self.sdf(P - d)
        return g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)

    def project(self, P: np.ndarray, lift: float = 0.0, iters: int = 4) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, dtype=float)).copy()
        for _ in range(iters):
            d = self.sdf(P) - lift
            P = P - self.normal(P) * d[:, None]
        return P


def _gather(lm) -> np.ndarray:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    return np.array([lm.head_w * 0.40, yc + 0.30 * lm.h, zc + 0.37 * lm.h])


def _part_x(lm) -> float:
    return lm.head_w * 0.17  # parted on the left (+X)


def _flow_dir(lm, P: np.ndarray, N: np.ndarray, G: np.ndarray) -> np.ndarray:
    """Tangent flow toward the gather point, split at the part line."""
    yc = lm.P("head_c")[1]
    to_g = G - P
    d = to_g / np.maximum(np.linalg.norm(to_g, axis=1, keepdims=True), 1e-9)
    # near the part on the crown, comb away from it first (right of the part sweeps over the top)
    px = _part_x(lm)
    front = np.clip(-(P[:, 1] - yc) / (0.4 * lm.h), -1.0, 1.0)
    near = np.exp(-((P[:, 0] - px) / (0.12 * lm.h)) ** 2) * np.clip(front + 0.5, 0, 1)
    away = np.stack([np.sign(P[:, 0] - px), np.zeros(len(P)), np.zeros(len(P))], axis=1)
    back = np.array([0.0, 1.0, -0.2])
    d = d + away * near[:, None] * 0.8 + back * 0.35
    d = d - np.sum(d * N, axis=1, keepdims=True) * N
    return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)


def _ribbon(part: Part, pts: np.ndarray, nrm: np.ndarray, width: float, slot: int, color_fn, taper: float = 0.45,
            v_range=(0.0, 1.0), mat: str = "hair") -> None:
    n = len(pts)
    T = np.gradient(pts, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    side = np.cross(T, nrm)
    side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-12)
    P = np.zeros((n, 2, 3))
    cols = []
    for k in range(n):
        w = width * (1.0 - taper * k / (n - 1)) * 0.5
        P[k, 0] = pts[k] - side[k] * w
        P[k, 1] = pts[k] + side[k] * w
        t = k / (n - 1)
        cols.append([color_fn(t), color_fn(t)])
    u0, u1 = slot / CLUMPS, (slot + 1) / CLUMPS
    v0, v1 = v_range
    grid(part, P, mat, colors=cols, tags=TAG_HAIR,
         uv_fn=lambda j, i: (u0 + (u1 - u0) * i, v0 + (v1 - v0) * j / (n - 1)))


def scalp_cards(lm, body, params: dict, rng: np.random.Generator) -> Part:
    part = Part("HairScalp")
    scalp = Scalp(body)
    G = _gather(lm)
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    s = lm.h / 0.222
    layers = [(0.0016 * s, params["scalp_cards"][0], 0.0), (0.0034 * s, params["scalp_cards"][1], 0.5),
              (0.0055 * s, params["scalp_cards"][2], 1.0)]
    seg = 9
    for li, (lift, count, layer) in enumerate(layers):
        # roots: a third of the base layer exactly on the hairline (a clean edge), the rest inside
        n_line = count // 3 if li == 0 else 0
        phi = np.sort(rng.uniform(-math.pi * 0.86, math.pi * 0.86, n_line))
        d_line = np.stack([np.sin(phi), -np.cos(phi), np.zeros(n_line)], axis=1)
        d_in = rng.normal(size=(count * 6, 3))
        d_in[:, 2] = np.abs(d_in[:, 2]) * 1.2 + 0.1
        d_in /= np.linalg.norm(d_in, axis=1, keepdims=True)
        p_in = scalp.project(hc + d_in * 0.2 * lm.h)
        ok = in_hair(lm, p_in, 0.02) & (np.linalg.norm(p_in - G, axis=1) > 0.04 * s)
        p_in = p_in[ok][: count - n_line]
        if n_line:
            p_line = scalp.project(hc + d_line * 0.2 * lm.h)
            for _ in range(10):
                v = hairline_v(lm, p_line) + 0.012
                dz = (zc + v * lm.h) - p_line[:, 2]
                p_line = scalp.project(p_line + np.stack([np.zeros(n_line), np.zeros(n_line), dz], axis=1))
            roots = np.concatenate([p_line, p_in])
        else:
            roots = p_in
        n = len(roots)
        length = rng.uniform(0.10, 0.20, n) * s
        length[:n_line] *= 1.25
        step = length / seg
        paths = [scalp.project(roots, lift)]
        alive = np.ones(n, dtype=bool)
        stop = np.full(n, seg)
        for k in range(seg):
            cur = paths[-1]
            N = scalp.normal(cur)
            fdir = _flow_dir(lm, cur, N, G)
            nxt = scalp.project(cur + fdir * step[:, None], lift, iters=3)
            near = np.linalg.norm(nxt - G, axis=1) < 0.03 * s
            newly = alive & near
            stop[newly] = k + 1
            alive &= ~near
            nxt = np.where(alive[:, None] | newly[:, None], nxt, cur)
            paths.append(nxt)
        paths = np.stack(paths, axis=1)  # (n, seg+1, 3)
        widths = rng.uniform(0.014, 0.026, n) * s * (1.25 if layer == 0.0 else 1.0)
        slots = rng.integers(CLUMPS, size=n)
        phases = rng.random(n)
        for c in range(n):
            pts = paths[c, : stop[c] + 1]
            if len(pts) < 4:
                continue
            nrm = scalp.normal(pts)
            _ribbon(part, pts, nrm, float(widths[c]), int(slots[c]), lambda t, ph=float(phases[c]): (0.0, 0.0, ph, 0.0),
                    taper=0.35, v_range=(0.0, 0.85))
    return part


def braid_spine(lm, body, params: dict) -> np.ndarray:
    s = lm.h / 0.222
    G = _gather(lm)
    zc = lm.P("chin")[2]
    notch = lm.P("notch")
    acro = lm.side_pt("acromion", "L")
    nip = lm.side_pt("nipple", "L")
    ctrl = np.array([
        G,
        G + np.array([0.004, 0.004, -0.05]) * s,
        np.array([acro[0] * 0.62, notch[1] + 0.01 * s, notch[2] + 0.03 * s]),
        np.array([acro[0] * 0.66, notch[1] - 0.05 * s, notch[2] - 0.06 * s]),
        np.array([nip[0] * 0.92, nip[1] - 0.04 * s, nip[2] - 0.05 * s]),
        np.array([nip[0] * 0.95, nip[1] - 0.02 * s, lm.P("waist")[2] - 0.02 * s]),
        np.array([nip[0] * 1.0, nip[1] + 0.0 * s, lm.P("waist")[2] - 0.25 * s]),
    ])
    C = catmull_rom(ctrl, 400)
    L = arclen(C)
    total = params["braid_length_m"] * s + params["tail_m"] * s
    C = C[L <= total]
    # keep it clear of the body (+ the vest on the chest) and the costume
    clear = 0.024 * s
    for _ in range(6):
        d = body.sdf(C)
        g = body.grad(C)
        g /= np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-9)
        push = np.maximum(clear - d, 0.0)
        C = C + g * push[:, None]
        # smooth
        C[1:-1] = 0.5 * C[1:-1] + 0.25 * (C[:-2] + C[2:])
    _ = zc
    return catmull_rom(C, 200)


def braid(lm, body, params: dict, rng: np.random.Generator) -> tuple[Part, Part, np.ndarray]:
    part = Part("HairBraid")
    acc = Part("HairClasps")
    s = lm.h / 0.222
    C = braid_spine(lm, body, params)
    L = arclen(C)
    braid_len = params["braid_length_m"] * s
    nb = int(np.searchsorted(L, braid_len))
    Cb = C[: nb + 1]
    Lb = L[: nb + 1]
    T, N, B = frames_along(Cb, np.array([0.0, -1.0, 0.0]))
    # N points roughly forward-ish: orient the weave plane across the body (B lateral)
    n_seg = 120
    idx = np.linspace(0, len(Cb) - 1, n_seg).astype(int)
    r0 = 0.0145 * s  # braid half-width at the top, tapering to the tail
    for k in range(3):
        ph = 2 * math.pi * k / 3
        pts, rad = [], []
        for ii in idx:
            u = Lb[ii] / braid_len
            w = r0 * (1.0 - 0.42 * u)
            t = Lb[ii] / (0.028 * s) * math.pi  # one cross every ~2.8 cm
            off = N[ii] * (0.55 * w * math.sin(t + ph)) + B[ii] * (0.45 * w * math.sin(2 * (t + ph)))
            pts.append(Cb[ii] + off)
            rad.append(w * 0.56)
        pts = np.array(pts)
        slot = int(rng.integers(CLUMPS))
        cols = [[(0.15 + 0.85 * (j / (n_seg - 1)) ** 2, 0.3 * j / (n_seg - 1), k / 3.0, 0.0)] * 6 for j in range(n_seg)]
        tube(part, pts, np.array(rad), 6, "hair", np.array([0.0, -1.0, 0.0]),
             uv_rect=(slot / CLUMPS, 0.05, (slot + 1) / CLUMPS, 0.72), colors=cols, tags=TAG_HAIR)
    # clasps (bone shell bands)
    for cm in params["clasps_m"]:
        ii = int(np.searchsorted(Lb, cm * s))
        ii = min(ii, len(Cb) - 3)
        u = Lb[ii] / braid_len
        w = r0 * (1.0 - 0.42 * u)
        seg = Cb[max(ii - 3, 0): ii + 4]
        tube(acc, catmull_rom(seg, 4), w * 1.12, 10, "bone", np.array([0.0, -1.0, 0.0]), tags=TAG_HAIR)
    # tail: loose cards fanning from the braid end
    end = Cb[-1]
    Tend = T[-1]
    for c in range(30):
        ang = 2 * math.pi * rng.random()
        rad = rng.uniform(0.2, 1.0) * r0 * 0.5
        start = end + (N[-1] * math.cos(ang) + B[-1] * math.sin(ang)) * rad
        length = rng.uniform(0.085, 0.12) * s
        spread = (N[-1] * math.cos(ang) + B[-1] * math.sin(ang)) * rng.uniform(0.05, 0.22)
        pts = np.array([start + (Tend + spread * (t ** 1.5)) * length * t for t in np.linspace(0, 1, 7)])
        nrm = np.tile(np.cross(Tend, B[-1]), (len(pts), 1))
        nrm = np.array([(N[-1] * math.cos(ang) + B[-1] * math.sin(ang))] * len(pts))
        _ribbon(part, pts, nrm, rng.uniform(0.006, 0.011) * s, int(rng.integers(CLUMPS)),
                lambda t, ph=float(rng.random()): (0.6 + 0.4 * t, 0.5 * t, ph, 0.2 * t), taper=0.6)
    return part, acc, Cb


def flyaways(lm, body, params: dict, rng: np.random.Generator, braid_spine_pts: np.ndarray) -> Part:
    part = Part("HairFlyaways")
    scalp = Scalp(body)
    s = lm.h / 0.222
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    n = params["flyaways"]
    for i in range(n):
        if i < n * 0.6:  # crown
            d = rng.normal(size=3)
            d[2] = abs(d[2]) + 0.8
            d /= np.linalg.norm(d)
            p = scalp.project((hc + d * 0.2 * lm.h)[None, :], 0.006 * s)[0]
            nrm = scalp.normal(p[None, :])[0]
            tdir = rng.normal(size=3)
            tdir -= (tdir @ nrm) * nrm
            tdir /= np.linalg.norm(tdir)
            length = rng.uniform(0.03, 0.07) * s
            pts = np.array([p + tdir * length * t + nrm * (0.004 * s) * t * t for t in np.linspace(0, 1, 5)])
        else:  # off the braid surface
            k = int(rng.integers(10, len(braid_spine_pts) - 5))
            c = braid_spine_pts[k]
            tdir = braid_spine_pts[k + 3] - braid_spine_pts[k]
            tdir /= np.linalg.norm(tdir)
            out = np.cross(tdir, rng.normal(size=3))
            out /= np.linalg.norm(out)
            p = c + out * 0.013 * s
            length = rng.uniform(0.03, 0.06) * s
            pts = np.array([p + (tdir * 0.9 + out * 0.4) * length * t for t in np.linspace(0, 1, 5)])
            nrm = out
        nrms = np.tile(nrm, (len(pts), 1))
        _ribbon(part, pts, nrms, rng.uniform(0.0012, 0.0022) * s, int(rng.integers(CLUMPS)),
                lambda t, ph=float(rng.random()): (0.3 * t, 0.3 * t, ph, 0.6 * t), taper=0.3, v_range=(0.3, 1.0))
    return part


def front_strands(lm, body, params: dict, rng: np.random.Generator) -> Part:
    """Two uncut face-framing strands on the right temple (asha.md §5)."""
    part = Part("HairFront")
    scalp = Scalp(body)
    s = lm.h / 0.222
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    for k in range(params["front_strands"]):
        x = -lm.head_w * (0.30 + 0.06 * k)
        root = scalp.project(np.array([[x, yc - 0.30 * lm.h, zc + (0.72 - 0.03 * k) * lm.h]]), 0.004 * s)[0]
        for c in range(3):
            ctrl = np.array([
                root + np.array([0.003 * c, 0.0, 0.0]) * s,
                root + np.array([-0.008 - 0.002 * c, -0.010, -0.030]) * s,
                root + np.array([-0.012 - 0.003 * c, -0.012, -0.065]) * s,
                root + np.array([-0.010 - 0.004 * c, -0.008, -0.095 - 0.01 * k]) * s,
            ])
            pts = catmull_rom(ctrl, 12)
            # keep clear of the face
            for _ in range(3):
                d = scalp.sdf(pts)
                nrm = scalp.normal(pts)
                pts = pts + nrm * np.maximum(0.004 * s - d, 0.0)[:, None]
            nrm = scalp.normal(pts)
            _ribbon(part, pts, nrm, rng.uniform(0.006, 0.010) * s, int(rng.integers(CLUMPS)),
                    lambda t, ph=float(rng.random()): (0.9 * t, 0.6 * t, ph, 0.4 * t), taper=0.55)
    return part


def comb(lm, body) -> Part:
    """Her mother's tortoiseshell comb, set into the hair behind the left ear (asha.md §4.1 #9)."""
    part = Part("HairComb")
    s = lm.h / 0.222
    G = _gather(lm)
    scalp = Scalp(body)
    c = G + np.array([-0.006, -0.026, 0.040]) * s
    c = scalp.project(c[None, :], 0.010 * s)[0]
    nrm = scalp.normal(c[None, :])[0]
    up = np.array([0.0, 0.0, 1.0])
    side = np.cross(nrm, up)
    side /= np.linalg.norm(side)
    up = np.cross(side, nrm)
    nu, nv = 10, 3
    P = np.zeros((nv + 1, nu + 1, 3))
    for j in range(nv + 1):
        for i in range(nu + 1):
            a = (i / nu - 0.5) * 1.2
            P[j, i] = c + side * math.sin(a) * 0.026 * s + up * (j / nv - 0.5) * 0.016 * s + nrm * (math.cos(a) - 1) * 0.012 * s
    grid(part, P, "tortoiseshell", tags=TAG_HAIR)
    back = P - nrm * 0.0025 * s
    grid(part, back, "tortoiseshell", tags=TAG_HAIR, flip=True)
    return part


def build_hair(lm, body, params: dict) -> dict[str, Part]:
    rng = np.random.default_rng(int(params["seed"]))
    out = {"HairScalp": scalp_cards(lm, body, params, rng)}
    br, clasps, spine = braid(lm, body, params, rng)
    out["HairBraid"] = br
    out["HairClasps"] = clasps
    out["HairFlyaways"] = flyaways(lm, body, params, rng, spine)
    out["HairFront"] = front_strands(lm, body, params, rng)
    out["HairComb"] = comb(lm, body)
    for p in out.values():  # wind colours everywhere (accessories are pinned)
        p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    return out
