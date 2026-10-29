"""Liss's hair (no bpy), act1_npcs.md §2.5 and the hair contract in character_shading.md.

* **The crop** (2-4 cm, roughly cut, `hair_brown_dark` #2A1C14 with sun-rust tips over the outer 25%: the hair
  shader's `col_tip` from `tip_start`, the cards only carry V root 0 -> tip 1): a hairline row on the soft-root atlas
  columns, three lifted layers of short cards over the shipped head mesh (asha_hair.MeshScalp) and a few ruffled
  tufts, on Rhen's card machinery (rhen_hair._emit, asha_hair._ribbon and Asha's strand atlas) with her own hairline
  and flow: a woman's hairline (Asha's), the crop falling forward over the crown and down the sides and the nape from
  a whorl behind the top of the head.
* **The tail** (story sheet: one long tail at the nape): a two-strand twist 1.8 cm thick and 45 cm long, two strand
  tubes wound round a spine that runs from the nape down the upper back (asha_hair.braid's construction, two strands
  instead of three), a few loose tip cards, and seven salvaged glass beads threaded on it (four salt glass, two
  copper-green, one amber). M1-CHR-14 from the start: the root is seated on the shipped head surface (4 mm off the
  skin, inside the crop's lift), the clearance from the body grows from there over 7 cm, and every crop card stops
  12 mm short of the root.

The module supplies the hairline and flow interface asha_textures reads (`hairline_v`, `in_hair`, `_gather`,
`_flow_dir`), so the skin maps paint the scalp under the cards. Vertex colour = wind (the crop pinned at the root, its
tips a little free; the tail's tip cards free). Seeded, deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import asha_hair
import rhen_hair
from asha_hair import ROOT_CAST_H, SLOTS_FULL, SLOTS_HAIRLINE, SLOTS_SPARSE, Scalp, _ribbon  # noqa: F401
from asha_mesh import Part, arclen, catmull_rom, frames_along, tube, uv_sphere

TAG_HAIR = asha_hair.TAG_HAIR
WIND_OUTER = 0.18  # the crop's outer layer: short, it barely moves
ROOT_SEAT = 0.0015  # m at s = 1: the tail root's centre off the shipped skin (asha_hair.BRAID_ROOT_SEAT 4 mm: hers
# sits a little deeper, so the nape skin pulling back as the chin lifts still touches the root ring)
ROOT_RAMP = 0.07  # m along the tail over which the body clearance grows to TAIL_CLEAR
TAIL_CLEAR = 0.032  # m: the tail's spine off the body field below the root (over the coat and the harness)
TAIL_ROOT_H = 0.40  # head heights above the chin: the tail's root on the back of the head
TAIL_RINGS = 140  # rings per strand tube (each strand >= 300 vertices: the probe's braid strand)
TAIL_AROUND = 6
FRINGE_SPILL = 0.05  # head heights a front card may run past the hairline
FRINGE_STAGGER = (0.1, 2.6)  # each crop card's own share of FRINGE_SPILL: the fringe's ends stagger (liss_review.md;
# widened at big13's review so the clumps break the edge at different depths over the brow)
# the Lead's gate review (big13): the fringe read as blocky "teeth" at dialogue range: stopped cards ended square on the
# atlas's opaque mid-strand, all on one line. Cards now gather in clumps that draw together toward their tips, every
# card ends on the atlas's fading tip, and the tips taper to a point
CLUMP_SIZE = 5  # crop cards per clump
CLUMP_PULL = 0.6  # how far a card's tip is drawn onto its clump's lead card (0 at the root)
CLUMP_EASE = 1.5  # the pull's power along the card: the roots stay spread, the tips gather
TIP_TAPER = (0.75, 0.85, 0.9)  # the width lost by the tip: hairline row, layers, tufts
BEAD_MATS = {"salt": "bead_salt", "green": "bead_green", "amber": "bead_amber"}


# ---------------------------------------------------------------------------------------------
# Hairline and flow (the interface asha_textures reads)
# ---------------------------------------------------------------------------------------------
def hairline_v(lm, P: np.ndarray) -> np.ndarray:
    """Head heights above the chin by azimuth (0 the front, +90 her left). A woman's front (Asha's), but a crop has
    no long hair falling over the sides: the hairline comes down in front of and over the ears (short sideburns) and
    low at the nape, so the sides read as cropped hair, not bare temple."""
    yc = lm.P("head_c")[1]
    phi = np.degrees(np.arctan2(P[:, 0], -(P[:, 1] - yc)))
    a = np.abs(phi)
    xs = [0, 30, 50, 64, 74, 82, 92, 104, 118, 140, 162, 180]
    vs = [0.734, 0.728, 0.690, 0.630, 0.575, 0.530, 0.545, 0.545, 0.44, 0.30, 0.235, 0.225]
    t = np.radians(phi)
    wander = 0.004 * np.sin(7.0 * t + 1.1) + 0.003 * np.sin(13.0 * t + 2.3) + 0.0015 * np.sin(29.0 * t + 0.4)
    return np.interp(a, xs, vs) + wander


def in_hair(lm, P: np.ndarray, margin_h: float = 0.0) -> np.ndarray:
    zc = lm.P("chin")[2]
    v = (P[:, 2] - zc) / lm.h
    return v > hairline_v(lm, P) + margin_h


def _gather(lm) -> np.ndarray:
    """The crown whorl the crop falls away from (named after Asha's braid gather: the same interface)."""
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    return np.array([0.04 * lm.head_w, yc + 0.18 * lm.h, zc + 1.0 * lm.h])


def _flow_dir(lm, P: np.ndarray, N: np.ndarray, G: np.ndarray) -> np.ndarray:
    """Away from the whorl: forward over the crown (a rough fringe toward her right), down at the sides and the
    nape."""
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    away = P - G
    away /= np.maximum(np.linalg.norm(away, axis=1, keepdims=True), 1e-9)
    v = (P[:, 2] - zc) / lm.h
    top = np.clip((v - 0.70) / 0.18, 0.0, 1.0)
    front = np.clip(-(P[:, 1] - yc) / (0.35 * lm.h), 0.0, 1.0)
    fwd = np.array([-0.25, -1.0, 0.0])
    down = np.array([0.0, 0.2, -1.0])
    d = (away * 0.7 + fwd[None, :] * (top * (0.4 + 0.5 * front))[:, None]
         + down[None, :] * ((1.0 - top) * 0.9)[:, None])
    d = d - np.sum(d * N, axis=1, keepdims=True) * N
    return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)


# ---------------------------------------------------------------------------------------------
# The crop
# ---------------------------------------------------------------------------------------------
def _trace(scalp, lm, roots: np.ndarray, length: np.ndarray, lift: float, G: np.ndarray, seg: int,
           rise: np.ndarray | None, stop_at: np.ndarray | None, stop_r: float,
           spill: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Paths of `seg` steps along the flow (rhen_hair._trace with her hairline), each stopped where it would come
    within `stop_r` of `stop_at` (the tail root), or where it would pass the hairline by more than its own `spill`
    (head heights, at the front; default FRINGE_SPILL): a stopped card ends there, so the fringe's ends stagger instead
    of piling up on one line (liss_review.md). Returns (paths, points kept per path)."""
    spill = np.full(len(roots), FRINGE_SPILL) if spill is None else spill
    step = length / seg
    paths = [scalp.project(roots, lift)]
    keep = np.full(len(roots), seg + 1)
    if stop_at is not None:
        keep[np.linalg.norm(paths[0] - stop_at, axis=1) < stop_r] = 0
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    for k in range(seg):
        cur = paths[-1]
        N = scalp.normal(cur)
        nxt = scalp.project(cur + _flow_dir(lm, cur, N, G) * step[:, None], lift, iters=3)
        front = np.clip(-(nxt[:, 1] - yc) / (0.3 * lm.h), 0.0, 1.0) ** 2
        ok = (nxt[:, 2] - zc) / lm.h > hairline_v(lm, nxt) - spill * front - 0.01
        nxt = np.where(ok[:, None], nxt, cur)
        stopped = ~ok & (keep > k + 1)
        keep[stopped] = k + 1
        if stop_at is not None:
            near = (np.linalg.norm(nxt - stop_at, axis=1) < stop_r) & (keep > k + 1)
            keep[near] = k + 1
        paths.append(nxt)
    out = np.stack(paths, axis=1)
    if rise is not None:
        t = (np.arange(seg + 1) / seg) ** 2
        Nn = scalp.normal(out.reshape(-1, 3)).reshape(out.shape)
        out = out + Nn * (rise[:, None] * t[None, :])[..., None]
    return out, keep


def _roots_inside(scalp, lm, rng, n: int, margin: float) -> np.ndarray:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    d_in = rng.normal(size=(n * 6, 3))
    d_in[:, 2] = np.abs(d_in[:, 2]) * 1.2 + 0.05
    d_in /= np.linalg.norm(d_in, axis=1, keepdims=True)
    p_in = scalp.project(hc + d_in * ROOT_CAST_H * lm.h)
    return p_in[in_hair(lm, p_in, margin)][:n]


def _hairline_roots(scalp, lm, phi: np.ndarray, inside_h) -> np.ndarray:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    d = np.stack([np.sin(phi), -np.cos(phi), np.zeros(len(phi))], axis=1)
    p = scalp.project(hc + d * ROOT_CAST_H * lm.h)
    for _ in range(10):
        dz = (zc + (hairline_v(lm, p) + inside_h) * lm.h) - p[:, 2]
        p = scalp.project(p + np.stack([np.zeros(len(p)), np.zeros(len(p)), dz], axis=1))
    return p


def _clump(paths: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Each card drawn toward the lead card of its clump (the nearest lead by root), more toward the tip. A stopped
    path holds its last point, so a card that runs on past its lead's end converges on it."""
    n, m = paths.shape[:2]
    lead = rng.choice(n, max(1, n // CLUMP_SIZE), replace=False)
    own = lead[np.argmin(np.linalg.norm(paths[:, None, 0] - paths[None, lead, 0], axis=2), axis=1)]
    w = CLUMP_PULL * (np.arange(m) / (m - 1)) ** CLUMP_EASE
    return paths + (paths[own] - paths) * w[None, :, None]


def _emit_kept(part: Part, scalp, paths: np.ndarray, keep: np.ndarray, widths, slots, rng, taper: float, v_range,
               wind: float, twist: float = 0.0) -> None:
    """rhen_hair._emit for the cards that keep at least two points (a stopped card ends where it stopped, on the
    atlas's tip all the same: a cut V range ended it square on the opaque mid-strand)."""
    for c in range(len(paths)):
        k = int(keep[c])
        if k < 2:
            rng.random()  # keep the stream aligned whether or not a card is emitted
            continue
        rhen_hair._emit(part, scalp, paths[c:c + 1, :k], widths[c:c + 1], slots[c:c + 1], rng, taper, v_range, wind,
                        twist)


def crop(lm, params: dict, rng: np.random.Generator, scalp, root: np.ndarray | None) -> Part:
    part = Part("HairHead")
    G = _gather(lm)
    s = lm.h / 0.222
    lo, hi = params["length_m"]
    seg = int(params["card_segments"])
    stop_r = float(params["tail_card_stop_m"]) * s
    lim = math.pi * 0.97
    n_hl = 70
    phi = np.sort(np.linspace(-lim, lim, n_hl) + rng.uniform(-0.4, 0.4, n_hl) * (2 * lim / n_hl))
    roots = _hairline_roots(scalp, lm, phi, rng.uniform(-0.001, 0.007, n_hl))
    length = rng.uniform(0.5 * lo, 0.8 * lo, n_hl) * s
    paths, keep = _trace(scalp, lm, roots, length, 0.0009 * s, G, 3, rng.uniform(0.0, 0.002, n_hl) * s, root, stop_r,
                         rng.uniform(*FRINGE_STAGGER, n_hl) * FRINGE_SPILL)
    _emit_kept(part, scalp, _clump(paths, rng), keep, rng.uniform(0.004, 0.007, n_hl) * s,
               rng.choice(SLOTS_HAIRLINE, n_hl), rng, TIP_TAPER[0], (0.0, 0.75), 0.0)
    wlo, whi = params["card_width_m"]
    layers = [(0.0012 * s, params["scalp_cards"][0], 1.0, 0.002, 0.0),
              (0.0026 * s, params["scalp_cards"][1], 0.85, 0.004, 0.5 * WIND_OUTER),
              (0.0042 * s, params["scalp_cards"][2], 0.7, 0.008, WIND_OUTER)]
    for li, (lift, count, wk, rise, wind) in enumerate(layers):
        r = _roots_inside(scalp, lm, rng, int(count), 0.012 + 0.01 * li)
        n = len(r)
        length = rng.uniform(lo, hi, n) * s
        paths, keep = _trace(scalp, lm, r, length, lift, G, seg, rng.uniform(0.3, 1.0, n) * rise * s, root, stop_r,
                             rng.uniform(*FRINGE_STAGGER, n) * FRINGE_SPILL)
        if li == 2:
            slots = np.where(rng.random(n) < 0.5, rng.choice(SLOTS_SPARSE, n), rng.integers(SLOTS_FULL, size=n))
        else:
            slots = rng.integers(SLOTS_FULL, size=n)
        _emit_kept(part, scalp, _clump(paths, rng), keep, rng.uniform(wlo, whi, n) * wk * s, slots, rng, TIP_TAPER[1],
                   (0.0, 0.9), wind, 0.25 * li)
    # ruffled tufts on the crown and at the front (rough cut: the silhouette breaks)
    n_t = 40
    r = _roots_inside(scalp, lm, rng, n_t * 3, 0.03)
    zc = lm.P("chin")[2]
    r = r[(r[:, 2] - zc) / lm.h > 0.72][:n_t]
    m = len(r)
    yc = lm.P("head_c")[1]
    front = np.clip(-(r[:, 1] - yc) / (0.3 * lm.h), 0.0, 1.0)
    paths, keep = _trace(scalp, lm, r, rng.uniform(0.9 * lo, 1.05 * hi, m) * s, 0.0048 * s, G, seg,
                         (0.004 + 0.006 * front) * rng.uniform(0.6, 1.2, m) * s, root, stop_r,
                         rng.uniform(*FRINGE_STAGGER, m) * FRINGE_SPILL)
    slots = np.where(rng.random(m) < 0.4, rng.choice(SLOTS_SPARSE, m), rng.integers(SLOTS_FULL, size=m))
    _emit_kept(part, scalp, _clump(paths, rng), keep, rng.uniform(0.004, 0.0065, m) * s, slots, rng, TIP_TAPER[2],
               (0.05, 0.9), WIND_OUTER, 0.4)
    return part


# ---------------------------------------------------------------------------------------------
# The tail
# ---------------------------------------------------------------------------------------------
def tail_root(lm, scalp) -> np.ndarray:
    """The tail's root: at the nape, inside the hairline, seated ROOT_SEAT off the shipped skin."""
    s = lm.h / 0.222
    zc = lm.P("chin")[2]
    yc = lm.P("head_c")[1]
    # high enough on the occiput that the skin under it rides the head bone (lower, on the nape proper, the neck's
    # weights pulled the skin away from the head-rigid root as the chin lifted)
    guess = np.array([[0.0, yc + 0.5 * lm.h, zc + TAIL_ROOT_H * lm.h]])
    return scalp.project(guess, ROOT_SEAT * s)[0]


def tail_spine(lm, body, params: dict, root: np.ndarray) -> np.ndarray:
    """From the root down the nape and the upper back, the clearance from the body growing from ROOT_SEAT to
    TAIL_CLEAR over ROOT_RAMP (asha_hair.braid_spine's M1-CHR-14 construction)."""
    s = lm.h / 0.222
    nb = lm.P("neck_base")
    ctrl = np.array([
        root,
        root + np.array([0.0, 0.006, -0.035]) * s,
        np.array([0.0, nb[1] + 0.07 * s, nb[2] - 0.01 * s]),
        np.array([0.004 * s, nb[1] + 0.10 * s, nb[2] - 0.12 * s]),
        np.array([0.008 * s, nb[1] + 0.11 * s, nb[2] - 0.26 * s]),
        np.array([0.010 * s, nb[1] + 0.11 * s, nb[2] - 0.42 * s]),
    ])
    C = catmull_rom(ctrl, 400)
    L = arclen(C)
    total = float(params["tail_length_m"]) * s
    C = C[L <= total]
    L = L[L <= total]
    ramp = np.clip(L / (ROOT_RAMP * s), 0.0, 1.0)
    ramp = ramp * ramp * (3.0 - 2.0 * ramp)
    clear = (ROOT_SEAT + (TAIL_CLEAR - ROOT_SEAT) * ramp) * s
    for _ in range(8):
        d = body.sdf(C)
        g = body.grad(C)
        g /= np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-9)
        push = np.maximum(clear - d, 0.0) * (ramp > 0.0)
        C = C + g * push[:, None]
        C[1:-1] = 0.5 * C[1:-1] + 0.25 * (C[:-2] + C[2:])
        C[0] = root
    return catmull_rom(C, 200)


def tail(lm, body, params: dict, rng: np.random.Generator, root: np.ndarray) -> tuple[Part, np.ndarray]:
    """The two strand tubes, the loose tip cards and the beads (one mesh, `HairTail`; the beads on their own
    materials). Returns (part, spine)."""
    part = Part("HairTail")
    s = lm.h / 0.222
    C = tail_spine(lm, body, params, root)
    L = arclen(C)
    total = float(L[-1])
    tip = 0.05 * s  # the loose tip cards take the last 5 cm
    nb = int(np.searchsorted(L, total - tip))
    Cb, Lb = C[: nb + 1], L[: nb + 1]
    T, N, B = frames_along(Cb, np.array([0.0, 1.0, 0.0]))
    r0 = 0.5 * float(params["tail_thickness_m"]) * s
    period = float(params["tail_twist_m"]) * s
    idx = np.linspace(0, len(Cb) - 1, TAIL_RINGS).astype(int)
    n_str = int(params["tail_strands"])
    strand_lines = []
    for k in range(n_str):
        ph = 2 * math.pi * k / n_str
        pts, rad = [], []
        for ii in idx:
            u = Lb[ii] / max(Lb[-1], 1e-9)
            w = r0 * (1.0 - 0.30 * u)
            t = 2 * math.pi * Lb[ii] / period
            off = N[ii] * (0.48 * w * math.cos(t + ph)) + B[ii] * (0.48 * w * math.sin(t + ph))
            pts.append(Cb[ii] + off)
            rad.append(w * 0.56)
        pts = np.array(pts)
        strand_lines.append((pts, np.array(rad)))
        slot = int(rng.integers(SLOTS_FULL))
        cols = [[(0.10 + 0.6 * (j / (TAIL_RINGS - 1)) ** 2, 0.2 * j / (TAIL_RINGS - 1), k / n_str, 0.0)] * TAIL_AROUND
                for j in range(TAIL_RINGS)]
        # capped at the tip: the strand's only open end is its root (the probe's root ring is the open end nearer
        # the scalp; an open tip on the back read as the "nearer" end, the head skin being open at the neck)
        tube(part, pts, np.array(rad), TAIL_AROUND, "hair", np.array([0.0, 1.0, 0.0]),
             uv_rect=((slot + 0.2) / asha_hair.CLUMPS, 0.05, (slot + 0.8) / asha_hair.CLUMPS, 0.72), colors=cols,
             tags=TAG_HAIR, cap_end=True)
    # the loose tip: cards fanning from the twist's end
    end, Tend = Cb[-1], T[-1]
    for _c in range(14):
        ang = 2 * math.pi * rng.random()
        rad_ = rng.uniform(0.2, 1.0) * r0 * 0.5
        dirn = N[-1] * math.cos(ang) + B[-1] * math.sin(ang)
        start = end + dirn * rad_
        length = rng.uniform(0.8, 1.2) * tip
        spread = dirn * rng.uniform(0.05, 0.2)
        pts = np.array([start + (Tend + spread * (t ** 1.5)) * length * t for t in np.linspace(0, 1, 6)])
        nrm = np.tile(dirn, (len(pts), 1))
        _ribbon(part, pts, nrm, rng.uniform(0.005, 0.009) * s, int(rng.integers(SLOTS_FULL)),
                lambda t, ph=float(rng.random()): (0.5 + 0.5 * t, 0.4 * t, ph, 0.2 * t), taper=0.6)
    # the beads, threaded on the strands (alternating), sitting a little out from the strand's centre
    for i, (kind, dia, at) in enumerate(params["beads"]):
        pts, rad = strand_lines[i % n_str]
        j = int(round(float(at) * (len(pts) - 1)))
        c = pts[j]
        out = c - Cb[idx[j]]
        out /= max(np.linalg.norm(out), 1e-9)
        tdir = pts[min(j + 1, len(pts) - 1)] - pts[max(j - 1, 0)]
        tdir /= max(np.linalg.norm(tdir), 1e-9)
        r = 0.5 * float(dia) * s
        uv_sphere(part, c + out * max(r - rad[j], 0.0) * 0.6, r, 12, 8, BEAD_MATS[kind], axis_fwd=tdir,
                  tags=TAG_HAIR)
    part.C = part.C + [(0.0, 0.0, 0.0, 0.0)] * (len(part.V) - len(part.C))
    return part, C


def build_hair(lm, body, params: dict, scalp=None) -> dict:
    """`scalp`: MeshScalp on the shipped head (build_liss); the anatomy field when omitted. Returns
    {"HairHead": crop, "HairTail": tail, "spine": tail spine, "root": tail root}."""
    scalp = scalp or Scalp(body)
    seed = int(params["seed"])
    root = tail_root(lm, scalp)
    head = crop(lm, params, np.random.default_rng([seed, 0]), scalp, root)
    head.C = head.C + [(0.0, 0.0, 0.0, 0.0)] * (len(head.V) - len(head.C))
    tl, spine = tail(lm, body, params, np.random.default_rng([seed, 1]), root)
    return {"HairHead": head, "HairTail": tl, "spine": spine, "root": root}
