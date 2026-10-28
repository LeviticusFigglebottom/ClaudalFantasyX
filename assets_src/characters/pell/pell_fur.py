"""Pell's fur, crest, whiskers and brow tufts (no bpy), pell.md §5 and §9.

* **The fur flow** (`flow_dir`): the direction the short, sleek fur lies at any point of the body: from the muzzle back
  over the skull and down the back of the neck, down the spine to its tail, from the shoulders to the wrists and from
  the hips to the ankles, down the front of the neck and the chest. A blend of limb and spine segments, each pointing
  downstream, projected on the skin's tangent plane. pell_textures bakes it into the body and head normal maps (the
  1.5 mm strand-scale fur normal) and the fringe cards and brow tufts follow it.
* **The silhouette fringe** (`fringe_cards`): short fur cards (8-14 mm) only where the outline needs softening: the
  back of the neck, the shoulders' top line, the backs of the forearms above the tile wraps and the calves. One
  segment each, rooted on the shipped skin (`surface`, asha_hair.MeshScalp's interface), on the hero-owned
  `pell_fur.png` strand atlas (Toma's short-card method: M2-CHR-524's rules, the skin's normal for shading).
* **The crest** (`crest`): `count` fine heron feathers rooted along a `line_m` line on the crown's midline, lying back
  along the skull at rest (each `length_m`, the tips about 6 cm off the back of the skull), two crossed cards each on
  the hero-owned `pell_feather.png`. Head-rigid; its motion is two shape keys: `crest_raise` (each feather turned up
  `raised_deg` about its root) and `crest_flat` (wind- and rain-flattened, Ch8: pressed down onto the skull and drawn
  back).
* **Whiskers** (`whiskers`): `per_side` fine pale whiskers on each whisker pad, 6-11 cm, thin cards in the Head object
  (Toma's face-hair method: build_pell gives each card vertex its nearest skin vertex's shape deltas, plus a lever
  term so cheek_raise and mouth_smile push the tips forward and mouth_frown lets them droop).
* **Brow tufts** (`brow_tufts`): about 60 short cards of paler, longer fur over each eye, in the Head object, so the
  brow shapes move them (they are the main instrument of his worry).

Seeded, deterministic; no wind on any of them (`STILL`).
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, grid

TAG_FUR = 44
TAG_WHISKER = 45
TAG_TUFT = 46
TAG_CREST = 47
STILL = (0.0, 0.0, 0.0, 0.0)
FUR_COLS = 8  # pell_fur.png: columns 0-5 short fur tufts, 6 the brow tuft, 7 a single whisker
FUR_TUFT_COLS = (0, 1, 2, 3, 4, 5)
FUR_BROW_COL = 6
FUR_WHISKER_COL = 7
FUR_INSET = 0.03  # of a column: UVs off the neighbours (mip bleed)
FEATHER_COLS = 4  # pell_feather.png: four feathers, V root (0) -> tip (1)
WHISKER_SEG = 4
CREST_SEG = 6


def smooth01(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def _unit(v: np.ndarray) -> np.ndarray:
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def _seg_dist(P: np.ndarray, a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ab = b - a
    t = np.clip((P - a) @ ab / max(float(ab @ ab), 1e-12), 0.0, 1.0)
    return np.linalg.norm(P - (a + np.outer(t, ab)), axis=1), t


def flow_segments(lm) -> list:
    """(a, b, falloff) segments whose direction a -> b is the fur's downstream direction near them."""
    S = lm.S
    sp = lm.side_pt
    segs = []
    tip = lm.P("nose_tip")
    crown = lm.P("crown")
    back = lm.P("skull_base") + np.array([0.0, 0.03 * S, 0.0])
    segs += [(tip, crown + np.array([0.0, 0.02 * S, -0.03 * S]), 0.06 * S), (crown, back, 0.08 * S)]
    segs += [(lm.P("chin"), lm.P("notch"), 0.05 * S), (back, lm.P("neck_base") + np.array([0.0, 0.05 * S, 0.0]),
                                                       0.06 * S)]
    segs += [(lm.P("notch"), np.array([0.0, 0.0, float(lm.P("crotch")[2])]), 0.18 * S)]
    for sd in ("L", "R"):
        segs += [(sp("acromion", sd), sp("elbow", sd), 0.07 * S), (sp("elbow", sd), sp("wrist", sd), 0.06 * S)]
        segs += [(sp("hip", sd), sp("knee", sd), 0.09 * S), (sp("knee", sd), sp("ankle", sd), 0.07 * S)]
    return segs


def flow_dir(lm, P: np.ndarray, N: np.ndarray, segs: list | None = None) -> np.ndarray:
    """The fur's direction at P (unit, in the tangent plane of the normal N)."""
    segs = segs or flow_segments(lm)
    acc = np.zeros_like(P)
    for a, b, fall in segs:
        d, _t = _seg_dist(P, a, b)
        w = np.exp(-((d / fall) ** 2)) + 1e-6
        acc += w[:, None] * _unit(b - a)[None, :]
    acc = acc - np.sum(acc * N, axis=1, keepdims=True) * N
    bad = np.linalg.norm(acc, axis=1) < 1e-6
    if bad.any():  # straight down the tangent plane
        g = np.array([0.0, 0.0, -1.0])
        acc[bad] = g - np.sum(g * N[bad], axis=1, keepdims=True) * N[bad]
    return _unit(acc)


# ---------------------------------------------------------------------------------------------
# cards
# ---------------------------------------------------------------------------------------------
def _card(part: Part, pts: np.ndarray, nrm: np.ndarray, width: float, rect_u: tuple, mat: str, tag: int,
          taper: float = 0.6) -> np.ndarray:
    """A card along `pts` (root first), V by arc length 0 -> 1, U across `rect_u`. Returns its vertex ids."""
    n = len(pts)
    T = np.gradient(pts, axis=0)
    T = _unit(T)
    side = _unit(np.cross(T, nrm))
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    s /= max(float(s[-1]), 1e-12)
    P = np.zeros((n, 2, 3))
    for k in range(n):
        w = width * (1.0 - taper * s[k]) * 0.5
        P[k, 0] = pts[k] - side[k] * w
        P[k, 1] = pts[k] + side[k] * w
    u0, u1 = rect_u
    cols = [[STILL, STILL] for _ in range(n)]
    return grid(part, P, mat, colors=cols, tags=tag, uv_fn=lambda j, i: (u0 + (u1 - u0) * i, float(s[j])))


def _fur_u(col: int) -> tuple:
    return ((col + FUR_INSET) / FUR_COLS, (col + 1 - FUR_INSET) / FUR_COLS)


def fringe_regions(lm, P: np.ndarray, N: np.ndarray, reg: np.ndarray, fp: dict) -> np.ndarray:
    """0..1 per skin point: where the silhouette fringe grows (pell.md §5)."""
    S = lm.S
    out = np.zeros(len(P))
    notch, sb = lm.P("notch"), lm.P("skull_base")
    # the back of the neck: behind the neck's axis, between the shoulders' top and the skull
    neck = (P[:, 2] > float(notch[2]) - 0.02 * S) & (P[:, 2] < float(sb[2])) & (N[:, 1] > 0.25)
    out = np.maximum(out, neck.astype(float) * np.isin(reg, ["torso"]))
    # the shoulders' top line: facing up, within the shoulder span, not under the mantle (his right)
    sh_z = float(lm.P("shoulder")[2])
    top = (N[:, 2] > 0.5) & (P[:, 2] > sh_z - 0.04 * S) & (P[:, 2] < float(notch[2]) + 0.05 * S)
    top &= P[:, 0] > float(fp["mantle_clear_x_m"])  # the left shoulder only (the mantle lies on the right)
    out = np.maximum(out, top.astype(float))
    # the backs of the forearms, between the elbow and the tile wraps
    for sd in ("L", "R"):
        el, wr = lm.side_pt("elbow", sd), lm.side_pt("wrist", sd)
        ax = wr - el
        t = (P - el) @ ax / float(ax @ ax)
        dorsal = N @ np.array([0.0, 0.6, 0.8]) > 0.3
        m = (reg == f"arm_{sd}") & (t > 0.08) & (t < float(fp["fringe_forearm_to"])) & dorsal
        out = np.maximum(out, m.astype(float))
    # look-dev review: the outlines that read as bare skin (the outer upper arms, the hips and buttocks, the outer and
    # back thighs, the left side under the arm), so he does not read as a bald mannequin
    for sd in ("L", "R"):
        sg = 1.0 if sd == "L" else -1.0
        sh, el = lm.side_pt("shoulder", sd), lm.side_pt("elbow", sd)
        ax = el - sh
        t = (P - sh) @ ax / float(ax @ ax)
        outer = (N @ np.array([sg, 0.3, 0.0])) > 0.45
        m = (reg == f"arm_{sd}") & (t > 0.3) & (t < 0.95) & outer
        out = np.maximum(out, m.astype(float))
        hp, kn = lm.side_pt("hip", sd), lm.side_pt("knee", sd)
        ax = kn - hp
        t = (P - hp) @ ax / float(ax @ ax)
        lat = (N @ np.array([sg, 0.5, 0.0])) > 0.5
        m = (reg == f"leg_{sd}") & (t > -0.1) & (t < 0.75) & lat
        out = np.maximum(out, m.astype(float))
    hz = float(lm.side_pt("hip", "L")[2])
    hips = np.isin(reg, ["torso"]) & (P[:, 2] < hz + 0.12 * S) & (P[:, 2] > hz - 0.12 * S)
    hips &= (np.abs(N[:, 0]) > 0.55) | (N[:, 1] > 0.5)
    out = np.maximum(out, hips.astype(float))
    side = np.isin(reg, ["torso"]) & (N[:, 0] > 0.6) & (P[:, 2] > hz + 0.12 * S) & (P[:, 2] < sh_z - 0.12 * S)
    out = np.maximum(out, side.astype(float))
    # the calves
    for sd in ("L", "R"):
        kn, an = lm.side_pt("knee", sd), lm.side_pt("ankle", sd)
        ax = an - kn
        t = (P - kn) @ ax / float(ax @ ax)
        m = (reg == f"leg_{sd}") & (t > 0.12) & (t < 0.7) & (N[:, 1] > 0.35)
        out = np.maximum(out, m.astype(float))
    return out


def fringe_cards(lm, fp: dict, surface, roots: np.ndarray, rng) -> tuple[Part, np.ndarray]:
    """The silhouette fringe on `roots` (points on the skin, already chosen in the fringe regions): one-segment cards
    `length_m` long along the fur flow, lifted off the skin by `lift_m` with the tip rising (the fur stands out a
    little at the outline). Returns (part, the root of each vertex's card)."""
    part = Part("Fur")
    lo, hi = fp["fringe_length_m"]
    wlo, whi = fp["fringe_width_m"]
    lift = float(fp["fringe_lift_m"])
    segs = flow_segments(lm)
    roots = surface.project(roots, lift)
    N = surface.normal(roots)
    D = flow_dir(lm, roots, N, segs)
    n = len(roots)
    L = rng.uniform(lo, hi, n)
    rise = rng.uniform(0.4, 0.8, n)
    ids_root = []
    for c in range(n):
        a = roots[c]
        b = surface.project(a + D[c] * L[c], lift)[0] + N[c] * L[c] * rise[c]
        pts = np.array([a, b])
        # the card stands on the skin (its plane holds the flow and the normal), so at the outline it is seen
        # face-on and breaks the silhouette (look-dev review); a random lean off upright
        twist = rng.uniform(-0.5, 0.5)
        side = _unit(np.cross(D[c], N[c]))
        nrm = np.array([side, side]) * math.cos(twist) + np.array([N[c], N[c]]) * math.sin(twist)
        first = len(part.V)
        _card(part, pts, nrm, float(rng.uniform(wlo, whi)), _fur_u(int(rng.choice(FUR_TUFT_COLS))), "fur",
              TAG_FUR, 0.5)
        ids_root += [c] * (len(part.V) - first)
    return part, np.array(ids_root, dtype=int)


# ---------------------------------------------------------------------------------------------
# the crest
# ---------------------------------------------------------------------------------------------
def _rot(axis: np.ndarray, ang: float) -> np.ndarray:
    a = _unit(np.asarray(axis, dtype=float))
    c, s = math.cos(ang), math.sin(ang)
    x, y, z = a
    return np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                     [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                     [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])


def _rot_onto(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """The shortest rotation taking unit a onto unit b (a matrix)."""
    v = np.cross(a, b)
    c = float(a @ b)
    if c < -1.0 + 1e-9:
        return -np.eye(3)
    vx = np.array([[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]])
    return np.eye(3) + vx + vx @ vx * (1.0 / (1.0 + c))


def crest(lm, cp: dict, surface, rng) -> tuple[Part, dict, dict]:
    """The feather crest: (part, {key: deltas}, info). Rooted along the crown's midline from the brow-side end
    `line_m` back, each feather a polyline lying back over the skull (its height off the skin growing to `tip_off_m`
    at the tip), two crossed cards each (one along the skin, one standing in the feather's plane)."""
    S = lm.S
    part = Part("Crest")
    n = int(cp["count"])
    L = float(cp["length_m"])
    line = float(cp["line_m"])
    crown = surface.project(np.array([lm.P("crown")]))[0]
    yc = float(lm.P("head_c")[1])
    # the root line: along the midline from a little in front of the crown to `line` behind it
    roots = []
    for k in range(n):
        f = k / max(n - 1, 1)
        y = float(crown[1]) - float(cp["line_front_m"]) + line * f
        guess = np.array([[0.0, y, float(crown[2]) + 0.05 * S]])
        p = surface.project(guess)[0]
        roots.append(p)
    roots = np.array(roots)
    roots[:, 0] = 0.0
    rest_pts, raise_pts, flat_pts, widths, cols = [], [], [], [], []
    up = np.array([0.0, 0.0, 1.0])
    for k in range(n):
        f = k / max(n - 1, 1)
        r0 = roots[k]
        Lk = L * (0.78 + 0.22 * math.sin(math.pi * (0.25 + 0.75 * f))) * rng.uniform(0.95, 1.05)
        # the feather's path: an arc in the head's midplane (splayed a little sideways), leaving the crown at
        # `root_elev_deg` and turning over to `tip_elev_deg` at its tip, kept `root_off_m` off the skull
        splay = math.radians(float(cp["splay_deg"])) * (f - 0.5) * 2.0 * rng.uniform(0.6, 1.0)
        def arc(e0: float, e1: float) -> np.ndarray:
            s = np.linspace(0.0, 1.0, CREST_SEG + 1)
            el = math.radians(e0) + (math.radians(e1) - math.radians(e0)) * s
            step = np.stack([np.sin(splay) * np.cos(el), np.cos(splay) * np.cos(el), np.sin(el)], axis=1)
            pts = r0 + np.concatenate([[np.zeros(3)], np.cumsum(step[1:] * (Lk / CREST_SEG), axis=0)])
            for _ in range(3):  # clear of the skull
                d = surface.sdf(pts) - float(cp["root_off_m"])
                low = d < 0.0
                if not low.any():
                    break
                pts[low] = pts[low] - surface.normal(pts[low]) * d[low][:, None]
            return pts

        pts = arc(float(cp["root_elev_deg"]), float(cp["tip_elev_deg"]))
        rest_pts.append(pts)
        # crest_raise: turned up about the root (the axis across the head), the front feathers a little more
        R = _rot(np.array([1.0, 0.0, 0.0]), math.radians(float(cp["raised_deg"])) * (1.05 - 0.15 * f))
        raise_pts.append(r0 + (pts - r0) @ R.T)
        # crest_flat: pressed down onto the skull and drawn back (Ch8: flattened by the wind and rain)
        flat_pts.append(arc(float(cp["flat_root_elev_deg"]), float(cp["flat_tip_elev_deg"])))
        widths.append(float(cp["width_m"]) * rng.uniform(0.85, 1.1))
        cols.append(int(rng.integers(FEATHER_COLS)))
    deltas = {"crest_raise": [], "crest_flat": []}
    for k in range(n):
        u0 = (cols[k] + 0.02) / FEATHER_COLS
        u1 = (cols[k] + 0.98) / FEATHER_COLS
        for which in ("flat", "stand"):
            variants = {}
            for key, pts in (("rest", rest_pts[k]), ("crest_raise", raise_pts[k]), ("crest_flat", flat_pts[k])):
                T = _unit(np.gradient(pts, axis=0))
                if which == "flat":  # across the skull, facing out of it (the normal turns with the feather)
                    N0 = surface.normal(rest_pts[k])
                    if key != "rest":
                        T0 = _unit(np.gradient(rest_pts[k], axis=0))
                        N0 = np.array([_rot_onto(T0[i], T[i]) @ N0[i] for i in range(len(T))])
                else:  # standing in the plane of the feather and the up axis
                    N0 = _unit(np.cross(T, up))
                tmp = Part("tmp")
                _card(tmp, pts, N0, widths[k] * (1.0 if which == "flat" else 0.7), (u0, u1), "crest", TAG_CREST,
                      0.35)
                variants[key] = tmp
            base = variants["rest"]
            part.extend(base)
            for key in deltas:
                deltas[key].append(variants[key].varr() - base.varr())
    out = {k: np.concatenate(v) for k, v in deltas.items()}
    part.C = [STILL] * len(part.V)
    info = {"roots": roots, "tips": np.array([p[-1] for p in rest_pts]),
            "tips_raised": np.array([p[-1] for p in raise_pts])}
    return part, out, info


# ---------------------------------------------------------------------------------------------
# whiskers and brow tufts (the Head object)
# ---------------------------------------------------------------------------------------------
def whisker_roots(lm, face, wp: dict, surface) -> list:
    """(side, root, outward direction) per whisker: rows on each whisker pad, beside the nose pad and above the
    mouth's line, fanning out and back."""
    S = lm.S
    tip = lm.P("nose_tip")
    mouth = lm.P("mouth")
    out = []
    n = int(wp["per_side"])
    rows = (4, 4, 3)
    k = 0
    for sd, sg in (("L", 1.0), ("R", -1.0)):
        k = 0
        for r, count in enumerate(rows):
            z = float(mouth[2]) + (float(tip[2]) - float(mouth[2])) * (0.30 + 0.28 * r)
            for c in range(count):
                if k >= n:
                    break
                x = sg * (0.010 + 0.0055 * c + 0.002 * r) * S
                guess = np.array([[x, float(tip[1]) + (0.012 + 0.010 * c) * S, z]])
                p = surface.project(guess)[0]
                nrm = surface.normal(p[None, :])[0]
                d = _unit(np.array([sg * 1.0, 0.55 + 0.1 * c, -0.10 - 0.10 * r]) * 0.6 + nrm * 0.4)
                out.append((sd, p, d, r, c))
                k += 1
    return out


def whiskers(lm, face, wp: dict, surface, rng) -> tuple[Part, np.ndarray, np.ndarray]:
    """The whisker cards: each a thin card of WHISKER_SEG segments from its root on the pad, out and back, arcing down
    a little toward the tip (pale, fine). Returns (part, per-vertex t along the whisker 0..1, per-vertex root point)."""
    part = Part("Whiskers")
    lo, hi = wp["length_m"]
    width = float(wp["width_m"])
    ts, rootp = [], []
    for sd, p, d, r, c in whisker_roots(lm, face, wp, surface):
        L = lo + (hi - lo) * (1.0 - 0.25 * r) * rng.uniform(0.75, 1.0)
        down = np.array([0.0, 0.0, -1.0])
        pts = [p]
        for i in range(1, WHISKER_SEG + 1):
            t = i / WHISKER_SEG
            pts.append(p + d * L * t + down * L * float(wp["droop"]) * t * t)
        pts = np.array(pts)
        nrm = np.array([_unit(np.cross(d, np.array([0.0, 0.0, 1.0])))] * len(pts))
        nrm = _unit(np.cross(_unit(np.gradient(pts, axis=0)), nrm))
        first = len(part.V)
        _card(part, pts, nrm, width, _fur_u(FUR_WHISKER_COL), "whisker", TAG_WHISKER, 0.7)
        k = len(part.V) - first
        tt = np.repeat(np.linspace(0.0, 1.0, len(pts)), 2)
        ts += list(tt[:k])
        rootp += [p] * k
    return part, np.array(ts), np.array(rootp)


def brow_tufts(lm, face, bp: dict, surface, rng) -> Part:
    """About `count` short cards over each eye where a human's brow is (the eye frame's brow line), along the fur's
    flow there: out and back over the brow."""
    part = Part("BrowTufts")
    S = lm.S
    lo, hi = bp["length_m"]
    wlo, whi = bp["width_m"]
    lift = float(bp["lift_m"])
    for sd in ("L", "R"):
        fr = face.eyes[sd]
        n = int(bp["count"])
        a = rng.uniform(-0.6, 1.0, n)  # along the brow: medial (-) to lateral (+), in half-widths
        b = rng.normal(0.0, 0.35, n)
        x = fr.E[0] + fr.sgn * (a * 0.016 * S + 0.002 * S)
        z = fr.E[2] + 0.016 * S + b * 0.0045 * S - 0.003 * S * np.maximum(a, 0.0) ** 2
        guess = np.stack([x, np.full(n, fr.E[1] - 0.03 * S), z], axis=1)
        roots = surface.project(guess, lift)
        N = surface.normal(roots)
        D = _unit(np.stack([np.full(n, fr.sgn * 0.8), np.full(n, 0.35), 0.45 + 0.25 * (a < 0)], axis=1))
        D = _unit(D - np.sum(D * N, axis=1, keepdims=True) * N)
        L = rng.uniform(lo, hi, n)
        for c in range(n):
            tip = surface.project((roots[c] + D[c] * L[c])[None, :], lift)[0] + N[c] * L[c] * 0.35
            pts = np.array([roots[c], 0.5 * (roots[c] + tip) + N[c] * L[c] * 0.08, tip])
            _card(part, pts, np.array([N[c]] * 3), float(rng.uniform(wlo, whi)), _fur_u(FUR_BROW_COL), "fur_brow",
                  TAG_TUFT, 0.55)
    return part
