"""Spar-Wraith, the Ch4 boss (M3-CRE-03; final pass M3-CRB-005): docs/kb/art/creatures/act1/spar_wraith.md.

blender --background --factory-startup --python assets_src/creatures/spar_wraith/build_spar_wraith.py -- \
    --out assets/creatures/spar_wraith/spar_wraith.glb

Undertow-spawn tangled in a dead trader's rigging: a long, many-jointed black body hangs head-down in a web of
shrouds and ratlines slung between two broken spars, which it uses as limbs, planted on the deck like a mantis's legs.

- The spars are a snapped mast and its yard's stump: tapered, hewn timber silvered by salt (the grain in the vertex
  colour, two long checks, adze dents), three iron bands bleeding rust, cleats with a line hanging off one, a fid
  hole under the break, splintered salt-pale tops, and a broken yard lashed across the right spar. Lines are belayed
  round them in tight turns.
- The rigging is a tangle of hemp and tarred lines of every thickness, each laid in three strands, sagging under its
  own weight: four shrouds set up on deadeyes and lanyards to iron straps on the deck, a ratline ladder on each flank
  (two rungs parted and hanging), lines from the spars to the body, broken lines frayed at their ends, a stay lashed
  through the hub, turns hitched round the body. Three big monkey's-fist knots sit in the web (the elemental weak
  points of the sheet: the art is the knots, the element's colour is VFX); a faint `spawn_wound` seeps from their
  hearts. A block-and-tackle hangs from the body: two iron-strapped blocks with brass sheave pins, three falls and a
  frayed hauling part, a hook under the lower block.
- The body is chitin over wet skin: eight telescoping plates (a lip rolled toward the tail, a dorsal keel, lateral
  flanges with a spine at each rear corner, pitted and scratched), paler sternites in front, and wet membranes
  between them. Where the membranes split they are open `spawn_wound` seams (ADR 0151); the largest, between the
  fifth and sixth plates, runs across the front toward the -X flank (the one the battle camera sees) and carries
  `vfx_wound`. Four hooked, jointed limbs grip the spars and the shrouds. A hooked tail spike is lashed into the hub.
- The head is wrong: a long blank face with skinned-over sockets where eyes should be, a brow, cheek ridges, a crest
  of short spines, and a mouth that is a seam: it runs down the face and under the chin, lipped, glowing, flanked by
  two hooked mandibles.
- `Shroud` (phase 1): its own sail, torn tarred sailcloth wrapped round its back and flanks, open in front: panels
  and doubled seams, a bolt rope down each edge with brass grommets, a reef band with its reef points hanging, rotted
  rents, a ragged hem with long tatters; two-sided. `Sheath` (phase 2): the sea hauled up its lines, a streaked skin
  of water over the body.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402
import grounding as gr  # noqa: E402

SEED = 4717
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "spawn_wound": "#3FE0C8", "timber_weathered": "#7E6A55",
    "sand_cloth": "#C9B48E", "bone": "#E6DAC0", "storm_slate": "#3E4A57", "brass": "#B08D57",
    "deep_teal_shadow": "#0E4A55", "foam_white": "#EEF6F4", "coral_stone_weathered": "#B9AE98",
    "laterite": "#A8573A", "volcanic_stone": "#3A3A3F", "overcast_slate": "#6F7E8E", "sand_wet": "#B59D74",
    "cold_blue_stone": "#5E6E80", "foliage_shadow": "#1E4A3A",
}.items()}

X_AX = np.array([1.0, 0.0, 0.0])
Y_AX = np.array([0.0, 1.0, 0.0])
Z_AX = np.array([0.0, 0.0, 1.0])

HUB = np.array([0.0, 3.4, -0.2])  # where the spars cross and the web hangs from
N_BODY = 5
BODY_TOP = np.array([0.0, 3.25, -0.1])
BODY_BOT = np.array([0.0, 1.25, 0.35])
BODY_CTRL = [BODY_TOP, BODY_TOP + np.array([0, -0.8, -0.25]), BODY_BOT + np.array([0, 0.5, -0.1]), BODY_BOT]

# M3-CRE-632: the spar's foot stands on the deck (its butt is sawn flat on it)
SPAR_FOOT_Y = 0.03


def g(x, w):
    return np.exp(-(np.asarray(x, dtype=np.float64) / w) ** 2)


def noise1(x, seed: int):
    x = np.atleast_1d(np.asarray(x, dtype=np.float64))
    return ck.value_noise(np.column_stack([x, np.full(len(x), 0.37 * seed), np.full(len(x), 1.7)]), seed)


def unit(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


# ---------------------------------------------------------------------------------------------
# Small geometry helpers (local to this build)
# ---------------------------------------------------------------------------------------------
def orient(P: np.ndarray, T: np.ndarray, C) -> np.ndarray:
    """Winds T outward: away from per-vertex centres C, or from one point C."""
    C = np.asarray(C, dtype=np.float64)
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    fn = np.cross(b - a, c - a)
    inner = C if C.ndim == 1 else (C[T[:, 0]] + C[T[:, 1]] + C[T[:, 2]]) / 3.0
    out = (a + b + c) / 3.0 - inner
    if np.sum(np.einsum("ij,ij->i", fn, out) < 0.0) > len(T) / 2:
        return ck.flip(T)
    return T


def loft(rings: list[np.ndarray], cap_start=None, cap_end=None, centres=None):
    """Closed loops (equal vertex counts) joined in order; optional fan caps to a point. Returns P, T."""
    n = len(rings[0])
    P = np.vstack(rings)
    cen = centres if centres is not None else [r.mean(axis=0) for r in rings]
    C = np.vstack([np.repeat(np.asarray(c)[None], n, axis=0) for c in cen])
    parts = [orient(P, ck.grid_tris(len(rings), n, True), C)]
    for tip, ring, inner in ((cap_start, 0, 1), (cap_end, len(rings) - 1, len(rings) - 2)):
        if tip is None:
            continue
        idx = len(P)
        P = np.vstack([P, np.asarray(tip, dtype=np.float64)[None]])
        r0 = ring * n
        cap = np.array([(r0 + q, idx, r0 + (q + 1) % n) for q in range(n)], dtype=np.int64)
        parts.append(orient(P, cap, np.asarray(cen[inner])))
    return P, np.vstack(parts)


def basis(d: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    d = unit(d)
    a = Y_AX if abs(d[1]) < 0.9 else X_AX
    e1 = unit(np.cross(d, a))
    return e1, np.cross(d, e1)


def nail(base, d, length, width, bend_dir, bend, twist=0.0) -> tuple[np.ndarray, np.ndarray]:
    """A square-sectioned spike (a spine, a splinter, a hook): base square, a narrower bent middle, a point."""
    d = unit(d)
    e1, e2 = basis(d)
    rows = []
    for t, w, tw in ((-0.012, width, 0.0), (0.55, width * 0.62, twist)):
        c = base + d * length * t + bend_dir * bend * length * max(t, 0.0) ** 2 * 0.6
        a = np.radians(45.0 + tw) + np.arange(4) * math.pi / 2
        rows.append(c + w * (np.outer(np.cos(a), e1) + np.outer(np.sin(a), e2)))
    tip = base + d * length + bend_dir * bend * length * 0.6
    P = np.vstack(rows + [tip[None]])
    T = [(0, 4, 1), (1, 4, 5), (1, 5, 2), (2, 5, 6), (2, 6, 3), (3, 6, 7), (3, 7, 0), (0, 7, 4)]
    T += [(4, 8, 5), (5, 8, 6), (6, 8, 7), (7, 8, 4)]
    T = np.asarray(T, dtype=np.int64)
    C = np.vstack([np.repeat(base[None], 4, 0), np.repeat((base + d * length * 0.55)[None], 4, 0),
                   (base + d * length * 0.9)[None]])
    return P, orient(P, T, C)


def box(c, e1, e2, e3, h1, h2, h3) -> tuple[np.ndarray, np.ndarray]:
    P = np.array([c + sx * h1 * e1 + sy * h2 * e2 + sz * h3 * e3
                  for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
    T = np.array([(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1), (2, 3, 7), (2, 7, 6),
                  (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)], dtype=np.int64)
    return P, orient(P, T, np.asarray(c))


def hook(mesh: ck.Mesh, base, d, curl_dir, length, width, bone, col_base, col_tip, n=6, segs=5, wet=1.0) -> None:
    """A curved, tapering hook (a claw, a mandible, a tail spike): it runs along d and curls toward curl_dir."""
    d = unit(d)
    c = unit(curl_dir - np.dot(curl_dir, d) * d)
    pts = []
    for k in range(n):
        t = k / (n - 1)
        ang = 1.9 * t * t
        pts.append(base + length * (d * math.sin(ang) / 1.9 * 1.6 * (1 - 0.25 * t) + c * (1 - math.cos(ang)) / 1.9))
    pts = np.array(pts)
    P, T = ck.tube(pts, width * np.linspace(1.0, 0.12, n), segs, cap_start=False)
    tt = np.concatenate([np.repeat(np.linspace(0, 1, n), segs), [1.0]])[: len(P)]
    col = ck.mix(col_base, col_tip, ck.smoothstep(0.45, 1.0, tt)[:, None])
    ck.finish(mesh, P, T, "carapace", col, bone, wet=wet, cavity=0.15)


def splinter_rings(end: np.ndarray, tan: np.ndarray, ring: np.ndarray, rng, reach: float = 1.0,
                   pinch: tuple[float, float] = (0.12, 0.6)) -> list[np.ndarray]:
    """Two jagged rings past a broken end: each corner runs on as a splinter of its own length."""
    ext = rng.uniform(0.02, 0.15, len(ring)) * reach
    ext[rng.integers(0, len(ring))] = rng.uniform(0.2, 0.3) * reach
    off = ring - end
    r1 = end + off * 0.9 + np.outer(ext * 0.45, tan)
    r2 = end + off * rng.uniform(*pinch, len(ring))[:, None] + np.outer(ext, tan)
    return [r1, r2]


# ---------------------------------------------------------------------------------------------
# Rope
# ---------------------------------------------------------------------------------------------
def sag_path(p0, p1, sag: float, n: int, bow=None) -> np.ndarray:
    """A line from p0 to p1 hanging under its own weight (a parabola), bowed sideways by `bow` if given."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    t = np.linspace(0.0, 1.0, n)[:, None]
    P = p0 + (p1 - p0) * t
    P[:, 1] -= 4.0 * sag * (t * (1 - t))[:, 0]
    if bow is not None:
        P += np.asarray(bow, float) * 4.0 * (t * (1 - t))
    return P


def rope(mesh: ck.Mesh, path, radius, bones, *, tar=0.0, salt=0.0, hue: float = 0.0, segs: int = 6,
         fray_start: bool = False, fray_end: bool = False, rng=None, emission=0.0) -> None:
    """A laid rope along `path`: three strands twisting along it, hemp (sand_cloth, salt-crusted) going to tar black
    by `tar` (a scalar or one value per path point); a frayed end splays into loose yarns."""
    path = np.asarray(path, dtype=np.float64)
    K = len(path)
    rad = np.broadcast_to(np.asarray(radius, dtype=np.float64), (K,))
    tan, nrm, bi = ck.frames_along(path, up_hint=(0.3, 0.2, 0.93))
    seglen = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    a = np.arange(segs) * (2.0 * math.pi / segs)
    rings, strand = [], []
    for k in range(K):
        ph = seglen[k] / max(rad[k], 0.004) * 0.55
        bump = np.cos(3.0 * a + ph)
        r = rad[k] * (1.0 + 0.16 * bump)
        rings.append(path[k] + r[:, None] * (np.outer(np.cos(a), nrm[k]) + np.outer(np.sin(a), bi[k])))
        strand.append(bump)
    P = np.vstack(rings)
    T = ck.flip(ck.grid_tris(K, segs, True))
    strand = np.concatenate(strand)
    extra = []
    if not fray_start:
        extra.append((path[0] - tan[0] * rad[0] * 0.5, 0))
    if not fray_end:
        extra.append((path[-1] + tan[-1] * rad[-1] * 0.5, K - 1))
    tris = [T]
    tar_ring = np.broadcast_to(np.asarray(tar, dtype=np.float64), (K,))
    tarv = np.repeat(tar_ring, segs)
    for tip, ring in extra:
        idx = len(P)
        P = np.vstack([P, tip[None]])
        strand = np.append(strand, 0.0)
        tarv = np.append(tarv, tar_ring[ring])
        r0 = ring * segs
        cap = [(r0 + s, idx, r0 + (s + 1) % segs) if ring == 0 else (r0 + s, r0 + (s + 1) % segs, idx)
               for s in range(segs)]
        tris.append(np.asarray(cap, dtype=np.int64))
    T = np.vstack(tris)
    hemp = ck.mix(PAL["sand_cloth"], PAL["sand_wet"] * 0.9, 0.35 + 0.35 * hue)
    crust = ck.smoothstep(0.1, 0.4, ck.fbm(P * 9.0, SEED + 401)) * salt
    stain = ck.smoothstep(0.0, 0.5, ck.fbm(P * 4.0, SEED + 402))
    col = ck.mix(hemp, PAL["timber_weathered"] * 0.62, (0.25 * stain)[:, None])
    col = ck.mix(col, PAL["lacquer_black"] * 1.2, (0.92 * tarv)[:, None])
    col = ck.mix(col, PAL["bone"] * 0.92, (0.6 * crust * (1 - 0.7 * tarv))[:, None])
    col = col * (0.88 + 0.12 * strand)[:, None]  # the strands' crowns lighter, the lay's grooves darker
    cav = np.clip(0.35 * (0.5 - 0.5 * strand), 0, 1)
    ck.finish(mesh, P, T, "rope", col, bones, wet=0.25 + 0.55 * tarv, cavity=cav, emission=emission)
    if rng is not None:
        for end, ring, flag in ((0, 0, fray_start), (K - 1, K - 1, fray_end)):
            if not flag:
                continue
            d = -tan[0] if end == 0 else tan[-1]
            for y in range(4):
                ang = 2 * math.pi * y / 4 + rng.uniform(-0.4, 0.4)
                side = math.cos(ang) * nrm[ring] + math.sin(ang) * bi[ring]
                base = path[ring] + side * rad[ring] * 0.5
                ln = rng.uniform(2.0, 4.0) * rad[ring] + 0.02
                tip = base + d * ln + side * ln * rng.uniform(0.35, 0.8) + np.array([0, -ln * 0.3, 0])
                Pf, Tf = ck.tube(np.array([base, 0.5 * (base + tip) + side * 0.004, tip]),
                                 np.array([rad[ring] * 0.4, rad[ring] * 0.28, 0.0015]), 3, cap_start=False)
                ck.finish(mesh, Pf, Tf, "rope", ck.mix(hemp, PAL["bone"], 0.35) * 0.95, bones, wet=0.2, cavity=0.1)


# ---------------------------------------------------------------------------------------------
# The body curve, measured
# ---------------------------------------------------------------------------------------------
_DU = np.linspace(0.0, 1.0, 3001)
_DC = ck.bezier(BODY_CTRL, 3001)
_DS = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(_DC, axis=0), axis=1))])
_DT = np.gradient(_DC, axis=0)
_DT /= np.linalg.norm(_DT, axis=1, keepdims=True)
LENGTH = float(_DS[-1])


def u_of_s(s):
    return np.interp(s, _DS, _DU)


def body_at(s: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(centre, tangent toward the head, ventral: the front, toward the party) at arclength s."""
    u = float(u_of_s(s))
    c = np.array([np.interp(u, _DU, _DC[:, i]) for i in range(3)])
    t = unit(np.array([np.interp(u, _DU, _DT[:, i]) for i in range(3)]))
    v = unit(np.cross(t, X_AX))
    return c, t, v


# Eight telescoping plates from the tail (top) to the neck; each ends in a membrane band (a gap) under the next.
N_PLATE = 8
S_PLATE0, S_PLATE1 = 0.16, LENGTH - 0.07
PLATE_EDGES = np.linspace(S_PLATE0, S_PLATE1, N_PLATE + 1)
GAP_W = np.array([0.045, 0.05, 0.05, 0.055, 0.075, 0.055, 0.05, 0.04])  # each plate's membrane width (m)
S_GAP = PLATE_EDGES[1:] - GAP_W * 0.5  # the membrane's middle at the end of each plate
# The open seams (ADR 0151): (gap, phi from, phi to, width m). phi: 0 is the +X flank, pi/2 the front (ventral, the
# party), pi the -X flank (the battle camera's), 3 pi/2 the back. Gap 4 carries the largest: across the front and
# round the -X flank; vfx_wound sits on it.
WOUNDS = (
    (1, 4.1, 5.2, 0.045), (2, 2.05, 3.0, 0.05),
    (4, 0.45, 3.4, 0.12), (6, 0.85, 1.6, 0.045),
)
WOUND_MAIN = 4
WOUND_MAIN_PHI = math.pi / 2 + 0.55


def envelope(s):
    u = np.asarray(u_of_s(s), dtype=np.float64)
    r = 0.075 + 0.175 * np.sin(math.pi * np.clip(u * 1.05, 0, 1)) ** 0.6 * (1 - 0.4 * ck.smoothstep(0.72, 1.0, u))
    return r + 0.05 * ck.smoothstep(0.88, 1.0, u) - 0.05 * ck.smoothstep(0.08, 0.0, u)


def plate_q(s):
    """(plate index, position 0..1 in it) at arclength s."""
    s = np.asarray(s, dtype=np.float64)
    k = np.clip(np.searchsorted(PLATE_EDGES, s, side="right") - 1, 0, N_PLATE - 1)
    q = (s - PLATE_EDGES[k]) / (PLATE_EDGES[k + 1] - PLATE_EDGES[k])
    return k, np.clip(q, 0.0, 1.0)


def plate_profile(s):
    """Radius factor along a plate: a lip rolled toward the tail, the plate tapering, the membrane dipping under."""
    k, q = plate_q(s)
    L = PLATE_EDGES[1] - PLATE_EDGES[0]
    m = GAP_W[k] / L
    out = np.zeros(len(np.atleast_1d(q)))
    qa, ma = np.atleast_1d(q), np.atleast_1d(m)
    for i in range(len(qa)):
        xs = [0.0, 0.05, 0.11, 0.2, 1 - ma[i], 1 - 0.7 * ma[i], 1 - 0.25 * ma[i], 1.0]
        ys = [0.84, 1.1, 1.06, 1.0, 0.93, 0.76, 0.74, 0.84]
        out[i] = np.interp(qa[i], xs, ys)
    inside = (np.atleast_1d(s) >= S_PLATE0) & (np.atleast_1d(s) <= S_PLATE1)
    return np.where(inside, out, 1.0), k, q, m


def wound_fields(s: np.ndarray, phi: np.ndarray):
    """(open, lip, spill, core) of the seams at body coordinates (s, phi)."""
    opn = np.zeros(len(s))
    lip = np.zeros(len(s))
    spill = np.zeros(len(s))
    core = np.zeros(len(s))
    for n, (gi, p0, p1, width) in enumerate(WOUNDS):
        ph = p0 + np.mod(phi - p0, 2.0 * math.pi)
        t = (ph - p0) / (p1 - p0)
        inside = (t >= 0.0) & (t <= 1.0)
        tt = np.clip(t, 0.0, 1.0)
        lens = np.where(inside, np.sin(math.pi * tt) ** 0.5, 0.0)
        line = S_GAP[gi] + 0.012 * np.sin(3.1 * ph + n) + 0.01 * noise1(ph * 2.3 + 5.0 * n, SEED + 40 + n)
        hw = 0.5 * width * lens * (0.75 + 0.25 * noise1(ph * 3.1 + 9.0 * n, SEED + 60 + n)) + 1e-4
        d = np.abs(s - line) / hw
        opn = np.maximum(opn, ck.smoothstep(1.0, 0.7, d) * (lens > 0.08))
        core = np.maximum(core, ck.smoothstep(0.7, 0.1, d) * (lens > 0.08))
        lip = np.maximum(lip, np.exp(-((d - 1.3) / 0.4) ** 2) * lens)
        spill = np.maximum(spill, np.exp(-(np.abs(s - line) / (hw + 0.07)) ** 2) * lens)
    return opn, lip, spill, core


def section(phi, k_plate, q, on_plate):
    """The body's section at angle phi: wider than deep, a keel down the back, lateral flanges on the plates."""
    cph, sph = np.cos(phi), np.sin(phi)
    flange = 0.36 * g(sph + 0.12, 0.15) * on_plate * ck.smoothstep(0.02, 0.12, q) * (1.0 - 0.5 * q)
    keel = 0.09 * g(sph + 1.0, 0.12) * on_plate
    sx = 1.12 * cph * (1.0 + flange)
    sy = sph * np.where(sph > 0, 0.78, 0.86) * (1.0 + keel)
    return sx, sy, flange


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def body_joints() -> np.ndarray:
    return ck.bezier(BODY_CTRL, N_BODY + 1)


def spar_ends(side: float) -> tuple[np.ndarray, np.ndarray]:
    top = HUB + np.array([side * 0.35, 0.25, 0.0])
    foot = np.array([side * 1.45, SPAR_FOOT_Y, 0.25])
    return top, foot


def body_bone_at(s: float) -> str:
    u = float(u_of_s(s))
    return f"body{min(int(u * N_BODY), N_BODY - 1)}"


def wound_main_point() -> tuple[np.ndarray, np.ndarray]:
    s = float(S_GAP[WOUND_MAIN])
    c, _t, v = body_at(s)
    out = math.cos(WOUND_MAIN_PHI) * X_AX + math.sin(WOUND_MAIN_PHI) * v
    return c + out * float(envelope(s)) * 0.88, out


BLOCK_HEAD_OFF = np.array([0.25, 0.0, 0.1])
BLOCK_TAIL_OFF = np.array([0.3, -0.5, 0.15])
TACKLE_DROP = 0.55
HEAD_SCALE = 1.3  # the head's local measurements are scaled by this


def build_rig() -> tuple[ck.Rig, np.ndarray]:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("hub", HUB, HUB + np.array([0, 0.3, 0]), "root")
    j = body_joints()
    for i in range(N_BODY):
        rig.add(f"body{i}", j[i], j[i + 1], "hub" if i == 0 else f"body{i - 1}")
    rig.add("head", j[-1], j[-1] + np.array([0, -0.2, 0.5]), f"body{N_BODY - 1}")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        top, foot = spar_ends(s)
        rig.add(f"spar_{tag}", top, foot, "hub")
    bh, bt = j[2] + BLOCK_HEAD_OFF, j[2] + BLOCK_TAIL_OFF
    rig.add("block", bh, bt, "body2")
    rig.add("tackle", bt, bt + np.array([0.0, -TACKLE_DROP, 0.0]), "block")
    # VFX anchors (unweighted): the largest seam, the centre of mass, where it tears out of the web
    pw, nw = wound_main_point()
    rig.add("vfx_wound", pw, pw + nw * 0.2, body_bone_at(float(S_GAP[WOUND_MAIN])))
    cc, _t, _v = body_at(LENGTH * 0.5)
    rig.add("vfx_core", cc, cc + np.array([0.0, 0.25, 0.0]), body_bone_at(LENGTH * 0.5))
    rig.add("vfx_phase", j[1], j[1] + np.array([0.0, 0.0, 0.25]), "body1")
    # M3-CRB-013: the shroud's lower half on a bone of its own, so the sail can billow, trail and be hauled down
    # (the clips key it to follow the body below body1, plus its own lag and flare)
    rig.add("sail", j[2], j[4], "body1")
    return rig, j


# ---------------------------------------------------------------------------------------------
# The spars
# ---------------------------------------------------------------------------------------------
SPAR = {  # per side: how far past the top it runs before the break, the bands, cleats, belays, checks
    "l": {"ext": 0.2, "bands": (0.3, 0.6, 0.83), "cleats": (0.22, 0.47), "belays": (0.36, 0.6), "fid": 0.9},
    "r": {"ext": 0.1, "bands": (0.27, 0.56, 0.86), "cleats": (0.2,), "belays": (0.4, 0.62), "fid": 0.93},
}
N_SIDES = 8


def spar_frame(side: float, ext: float):
    top, foot = spar_ends(side)
    tip = top + (top - foot) * ext
    d = unit(tip - foot)
    ef = unit(Z_AX - np.dot(Z_AX, d) * d)  # column 0 faces the front
    es = np.cross(d, ef)
    return foot, tip, d, ef, es


def spar_point(side: float, t: float) -> np.ndarray:
    """A point on the spar's axis at fraction t from the foot (0) to the top (1, the bone's head)."""
    top, foot = spar_ends(side)
    bow = np.array([side * 0.035, 0.0, 0.03]) * 4.0 * t * (1 - t)
    return foot + (top - foot) * t + bow


def spar_radius(t: float) -> float:
    return 0.14 - 0.045 * min(max(t, 0.0), 1.2)


def spars(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rng = np.random.default_rng(SEED)
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        cfg = SPAR[tag]
        bone = rig.rigid(f"spar_{tag}")
        foot, tip, d, ef, es = spar_frame(side, cfg["ext"])
        t_end = 1.0 + cfg["ext"]
        stations = list(np.linspace(0.0, t_end, 13))
        for tb in cfg["bands"]:
            stations += [tb - 0.035, tb + 0.035]
        stations += [cfg["fid"] - 0.03, cfg["fid"] - 0.012, cfg["fid"] + 0.012, cfg["fid"] + 0.03]
        stations = sorted(set(round(float(x), 4) for x in stations if 0.0 <= x <= t_end))
        a = np.arange(N_SIDES) * 2 * math.pi / N_SIDES + math.pi / N_SIDES
        checks = rng.choice(N_SIDES, 2, replace=False)
        check_span = [(rng.uniform(0.05, 0.3), rng.uniform(0.5, 0.85)) for _ in checks]
        rings, ts, cols = [], [], []
        for t in stations:
            c = spar_point(side, t)
            r = spar_radius(t) * (1.0 + 0.04 * noise1(np.arange(N_SIDES) * 1.7 + t * 9.0, SEED + 3 + int(side)))
            for ci, (c0, c1) in zip(checks, check_span):
                if c0 < t < c1:
                    r[ci] -= 0.014 * math.sin(math.pi * (t - c0) / (c1 - c0)) ** 0.5
            if abs(t - cfg["fid"]) < 0.02:  # the fid hole: a square slot through the front face
                r[np.cos(a) > 0.75] -= 0.045
            ring = c + r[:, None] * (np.outer(np.cos(a), ef) + np.outer(np.sin(a), es))
            if t == 0.0:
                ring[:, 1] = np.maximum(ring[:, 1], 0.004)  # sawn flat where it stands on the deck
            rings.append(ring)
            ts.append(np.full(N_SIDES, t))
            cols.append(np.arange(N_SIDES))
        # the snapped top: jagged rings past the last station
        end = spar_point(side, t_end)
        jag = splinter_rings(end, d, rings[-1], rng, 1.1)
        rings += jag
        ts += [np.full(N_SIDES, t_end + 0.02), np.full(N_SIDES, t_end + 0.05)]
        cols += [np.arange(N_SIDES)] * 2
        P, T = loft(rings, cap_start=spar_point(side, 0.0), cap_end=end + d * 0.06,
                    centres=[spar_point(side, min(tt[0], t_end)) for tt in ts])
        P[:, 1] = np.maximum(P[:, 1], 0.004)
        tv = np.concatenate(ts + [[0.0], [t_end + 0.06]])
        cv = np.concatenate(cols + [[0], [0]])
        grain = noise1(cv * 3.3 + side * 7.0, SEED + 5) * 0.5 + 0.5
        streak = ck.fbm(np.column_stack([cv * 1.3, tv * 14.0, np.full(len(tv), side)]), SEED + 6)
        nrm = ck.weld_normals(P, ck.vertex_normals(P, T))
        up = ck.smoothstep(-0.1, 0.6, nrm[:, 1])
        # silvered, salt-bleached timber: grey on top and on the weather side, browner and wetter low down
        col = ck.mix(PAL["timber_weathered"] * 0.62, PAL["timber_weathered"] * 0.92, grain[:, None])
        col = ck.mix(col, PAL["coral_stone_weathered"] * 0.8, (0.35 + 0.45 * up * (0.6 + 0.4 * grain))[:, None])
        col = col * (0.85 + 0.25 * ck.smoothstep(-0.3, 0.3, streak))[:, None]
        broken = ck.smoothstep(t_end - 0.01, t_end + 0.04, tv)
        col = ck.mix(col, PAL["bone"] * 0.9, broken[:, None])
        low = ck.smoothstep(0.18, 0.0, tv)
        col = ck.mix(col, PAL["lacquer_black"] * 1.4, (0.55 * low)[:, None])
        tarred = ck.smoothstep(0.8, 1.0, tv) * (1 - broken)  # tar where the rigging was set up
        col = ck.mix(col, PAL["lacquer_black"] * 1.3, (0.5 * tarred)[:, None])
        rust = np.zeros(len(P))
        for tb in cfg["bands"]:
            below = np.clip((tb - tv) / 0.16, 0, 1)
            drip = (noise1(cv * 5.1 + tb * 13.0, SEED + 7) > -0.1) * (tv < tb) * (1 - below)
            rust = np.maximum(rust, drip * (0.4 + 0.6 * up))
        col = ck.mix(col, PAL["laterite"] * 0.6, (0.6 * rust)[:, None])
        fid = (np.abs(tv - cfg["fid"]) < 0.02) & (np.cos(a[cv % N_SIDES]) > 0.75)
        check = np.zeros(len(P))
        for ci, (c0, c1) in zip(checks, check_span):
            check = np.maximum(check, (cv == ci) * (tv > c0) * (tv < c1))
        col = ck.mix(col, PAL["lacquer_black"], (0.85 * fid + 0.6 * check)[:, None])
        cav = np.clip(0.2 + 0.3 * (1 - grain) * (1 - broken) + 0.8 * fid + 0.6 * check + 0.3 * low, 0, 1)
        wet = np.clip(0.05 + 0.6 * low + 0.3 * tarred - 0.3 * up, 0.0, 1.0)
        ck.finish(mesh, P, T, "timber", col, bone, wet=wet, cavity=cav, flat=True)
        # loose splinters standing off the break
        for _ in range(3):
            base = end + (ef * rng.uniform(-1, 1) + es * rng.uniform(-1, 1)) * spar_radius(t_end) * 0.55
            Ps, Ts = nail(base, d + rng.normal(0, 0.25, 3), rng.uniform(0.12, 0.26), rng.uniform(0.012, 0.02),
                          unit(rng.normal(0, 1, 3)), rng.uniform(-0.3, 0.3))
            ck.finish(mesh, Ps, Ts, "timber", PAL["bone"] * rng.uniform(0.78, 0.92), bone, wet=0.1, cavity=0.15,
                      flat=True)
        # iron bands, each with two bolt heads, rust-dark
        for tb in cfg["bands"]:
            c = spar_point(side, tb)
            r = spar_radius(tb)
            aa = np.arange(10) * 2 * math.pi / 10
            band_rings = []
            for dt, dr in ((-0.03, 0.0), (-0.024, 0.016), (0.024, 0.016), (0.03, 0.0)):
                cc = spar_point(side, tb + dt / 3.8)
                band_rings.append(cc + (r * 1.04 + dr) * (np.outer(np.cos(aa), ef) + np.outer(np.sin(aa), es)))
            Pb, Tb = loft(band_rings, centres=[c] * 4)
            colb = ck.mix(PAL["volcanic_stone"] * 0.9, PAL["laterite"] * 0.55,
                          ck.smoothstep(-0.2, 0.4, ck.fbm(Pb * 14.0, SEED + 8))[:, None])
            ck.finish(mesh, Pb, Tb, "timber", colb, bone, wet=0.35, cavity=0.25, flat=True)
            for ang in (0.6, 0.6 + math.pi):
                o = math.cos(ang) * ef + math.sin(ang) * es
                Ph, Th = box(c + o * (r * 1.04 + 0.022), o, d, np.cross(o, d), 0.008, 0.014, 0.014)
                ck.finish(mesh, Ph, Th, "timber", PAL["volcanic_stone"] * 0.75, bone, wet=0.3, cavity=0.3, flat=True)
        # cleats: a horned bar on two feet, on the outboard face
        for tc in cfg["cleats"]:
            c = spar_point(side, tc)
            r = spar_radius(tc)
            o = unit(ef * 0.55 + es * (-side) * 0.0 + X_AX * side * 0.85)
            o = unit(o - np.dot(o, d) * d)
            base = c + o * (r + 0.035)
            hp = np.array([base - d * 0.12 + o * 0.012, base - d * 0.06, base, base + d * 0.06,
                           base + d * 0.12 + o * 0.012])
            Pc, Tc = ck.tube(hp, np.array([0.008, 0.02, 0.026, 0.02, 0.008]), 6, up_hint=tuple(o))
            colc = ck.mix(PAL["timber_weathered"] * 0.6, PAL["coral_stone_weathered"] * 0.7, 0.4)
            ck.finish(mesh, Pc, Tc, "timber", colc, bone, wet=0.2, cavity=0.25, flat=True)
            for f in (-0.04, 0.04):
                Pf, Tf = box(c + o * (r + 0.012) + d * f, o, d, np.cross(o, d), 0.022, 0.012, 0.014)
                ck.finish(mesh, Pf, Tf, "timber", colc * 0.85, bone, wet=0.2, cavity=0.4, flat=True)
        # a line made fast on the first cleat: figure-eight turns, then a hanging bight
        c = spar_point(side, cfg["cleats"][0])
        o = unit(X_AX * side * 0.85 + ef * 0.55)
        o = unit(o - np.dot(o, d) * d)
        base = c + o * (spar_radius(cfg["cleats"][0]) + 0.04)
        n_perp = np.cross(o, d)
        fig = [base + d * 0.09 * math.sin(th) + n_perp * 0.03 * math.sin(2 * th) + o * 0.012 for th in
               np.linspace(0, 4 * math.pi, 11)]
        rope(mesh, np.array(fig), 0.009, bone, tar=0.1, salt=0.6, hue=0.3, segs=4)
        bight = np.array([base - d * 0.02, base + np.array([side * 0.06, -0.15, 0.04]),
                          base + np.array([side * 0.1, -0.42, 0.06]), base + np.array([side * 0.05, -0.6, 0.02]),
                          base + np.array([side * 0.0, -0.4, -0.02]), base + n_perp * 0.03 + d * 0.03])
        rope(mesh, ck.bezier(bight, 9), 0.01, bone, tar=0.15, salt=0.5, hue=0.2, segs=4)


def belay_turns(mesh: ck.Mesh, rig: ck.Rig, side: float, t: float, turns: float, tar: float) -> np.ndarray:
    """Tight turns of line round the spar at t; returns where the line leaves them."""
    tag = "l" if side > 0 else "r"
    _f, _t, d, ef, es = spar_frame(side, SPAR[tag]["ext"])
    r = spar_radius(t) + 0.016
    n = int(turns * 6) + 1
    pts = []
    for k in range(n):
        th = 2 * math.pi * turns * k / (n - 1) + side
        tt = t + 0.028 * turns * (k / (n - 1) - 0.5)
        pts.append(spar_point(side, tt) + r * (math.cos(th) * ef + math.sin(th) * es))
    rope(mesh, np.array(pts), 0.012, rig.rigid(f"spar_{tag}"), tar=tar, salt=0.4, hue=0.5, segs=5)
    return pts[-1]


def yard_stub(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The right spar's broken yard, lashed across it under the break, sticking out to the camera's side."""
    rng = np.random.default_rng(SEED + 11)
    bone = rig.rigid("spar_r")
    c = spar_point(-1.0, 0.8)
    d = unit(np.array([-0.85, 0.22, 0.48]))
    e1, e2 = basis(d)
    rings = []
    stations = np.linspace(-0.22, 0.85, 9)
    a = np.arange(8) * 2 * math.pi / 8
    for s in stations:
        r = 0.07 - 0.02 * max(s, 0) + 0.004 * noise1(a * 2 + s * 5, SEED + 12)
        rings.append(c + d * s + np.array([0, -0.02 * s * s, 0]) + r[:, None] * (np.outer(np.cos(a), e1) +
                                                                            np.outer(np.sin(a), e2)))
    end = c + d * stations[-1] + np.array([0, -0.02 * stations[-1] ** 2, 0])
    rings += splinter_rings(end, d, rings[-1], rng, 0.8)
    P, T = loft(rings, cap_start=c + d * (stations[0] - 0.02), cap_end=end + d * 0.1)
    along = np.concatenate([np.repeat(np.arange(len(rings)), 8), [0, len(rings) - 1]])
    broken = (along >= len(stations)).astype(np.float64)
    grain = noise1(np.concatenate([np.tile(np.arange(8), len(rings)), [0, 0]]) * 2.9, SEED + 13) * 0.5 + 0.5
    nrm = ck.weld_normals(P, ck.vertex_normals(P, T))
    col = ck.mix(PAL["timber_weathered"] * 0.5, PAL["timber_weathered"] * 0.8, grain[:, None])
    col = ck.mix(col, PAL["coral_stone_weathered"] * 0.75, (0.5 * ck.smoothstep(0.0, 0.7, nrm[:, 1]))[:, None])
    col = ck.mix(col, PAL["bone"] * 0.9, broken[:, None])
    ck.finish(mesh, P, T, "timber", col, bone, wet=0.2, cavity=0.25 * (1 - grain), flat=True)
    # the lashing: a cross of turns binding the yard to the spar
    _f, _t, sd, ef, es = spar_frame(-1.0, SPAR["r"]["ext"])
    pts = []
    for k in range(12):
        th = 2 * math.pi * 2.5 * k / 11
        w = 1 if (k // 3) % 2 == 0 else -1
        pts.append(c + 0.11 * (math.cos(th) * ef + math.sin(th) * es) + (sd * 0.05 + d * 0.06) * w * math.sin(th))
    rope(mesh, np.array(pts), 0.011, bone, tar=0.55, salt=0.3, hue=0.6, segs=5)
    # a line hanging off the yard's end, frayed
    p0 = c + d * 0.7 + np.array([0, -0.04, 0])
    path = ck.bezier([p0, p0 + np.array([-0.05, -0.35, 0.05]), p0 + np.array([0.02, -0.8, 0.1])], 9)
    rope(mesh, path, 0.011, bone, tar=0.2, salt=0.5, hue=0.4, segs=4, fray_end=True, rng=rng)


# ---------------------------------------------------------------------------------------------
# The rigging
# ---------------------------------------------------------------------------------------------
ANCHORS = [np.array([x, 0.0, z]) for x, z in ((-0.95, -0.95), (0.95, -0.95), (-1.25, 0.8), (1.25, 0.8))]
DEADEYE_UP, DEADEYE_LO = 0.62, 0.3


def shroud_point(k: int, t: float) -> np.ndarray:
    """A point on shroud k (hub to its upper deadeye) at t (0 the hub, 1 the deadeye)."""
    a = ANCHORS[k]
    lo = a + (HUB - a) * (DEADEYE_UP / HUB[1])
    p = HUB + np.array([0, 0.08, 0]) + (lo - HUB - np.array([0, 0.08, 0])) * t
    p[1] -= 4.0 * 0.03 * t * (1 - t)
    return p


def monkeys_fist(mesh: ck.Mesh, c: np.ndarray, R: np.ndarray, size: float, bones, rng) -> None:
    """A monkey's fist: three sets of three turns round a core, each set at right angles to the last."""
    tube_r = size * 0.18
    off = size * 0.34
    for axis in range(3):
        ring_r = size * (0.72 + 0.09 * axis)  # each set lies over the last, so each reads as its own band
        e = R[:, axis]
        u_, v_ = R[:, (axis + 1) % 3], R[:, (axis + 2) % 3]
        for k in (-1, 0, 1):
            rr = ring_r * math.sqrt(max(1.0 - (k * off / (ring_r + 1e-9)) ** 2 * 0.6, 0.3))
            th = np.linspace(0, 2 * math.pi, 9)[:-1]
            pts = c + e * (k * off) + rr * (np.outer(np.cos(th), u_) + np.outer(np.sin(th), v_))
            pts = np.vstack([pts, pts[:1]])
            Pk, Tk = ck.tube(pts, tube_r, 4, cap_start=False, cap_end=False)
            inner = np.clip((np.linalg.norm(Pk - c, axis=1) - (size * 0.6)) / (size * 0.45), 0, 1)
            col = ck.mix(PAL["sand_cloth"] * 1.02, PAL["bone"] * 0.95, 0.35 + 0.2 * k * k)
            salt = ck.smoothstep(0.1, 0.4, ck.fbm(Pk * 22.0, SEED + 501 + axis))
            col = ck.mix(np.broadcast_to(col, (len(Pk), 3)), PAL["bone"], (0.5 * salt)[:, None])
            col = col * (0.55 + 0.45 * inner)[:, None]  # the turns shade each other where they cross
            ck.finish(mesh, Pk, Tk, "rope", col, bones, wet=0.3, cavity=0.6 * (1 - inner))
    Pc, Tc = ck.ellipsoid(c, (size * 0.62,) * 3, 3, 5)
    ck.finish(mesh, Pc, Tc, "rope", PAL["spawn_wound"] * 0.7, bones, wet=0.8, cavity=0.0, emission=1.0)


def rigging(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    rng = np.random.default_rng(SEED + 3)
    hub_b, root_b = rig.rigid("hub"), rig.rigid("root")
    # shrouds: hub down to the upper deadeyes, tarred aloft, hemp low down
    for k in range(4):
        pts = np.array([shroud_point(k, t) for t in np.linspace(0, 1, 10)])
        tar = ck.smoothstep(0.55, 0.15, np.linspace(0, 1, 10))
        rope(mesh, pts, 0.021, rig.blend("hub", "root", pts[0], pts[-1]), tar=0.25 + 0.6 * tar, salt=0.6,
             hue=0.2 * k, segs=5)
        deadeyes(mesh, k, root_b, rng)
    # ratlines: rungs across each flank's pair of shrouds; two on the +X side parted and hanging
    for side, (ka, kb) in ((-1.0, (0, 2)), (1.0, (1, 3))):
        for n, t in enumerate(np.linspace(0.4, 0.84, 5)):
            p0, p1 = shroud_point(ka, t), shroud_point(kb, t)
            if side > 0 and n == 2:
                for p, q, fs in ((p0, p1, False), (p1, p0, False)):
                    hang = p + (q - p) * rng.uniform(0.25, 0.4)
                    hang[1] -= rng.uniform(0.2, 0.32)
                    rope(mesh, ck.bezier([p, p + (q - p) * 0.12 + np.array([0, -0.04, 0]), hang], 5), 0.009, root_b,
                         tar=0.2, salt=0.5, hue=0.6, segs=4, fray_end=True, rng=rng)
                continue
            rope(mesh, sag_path(p0, p1, 0.035, 6), 0.0075, root_b, tar=0.15, salt=0.5, hue=0.4 + 0.1 * (n % 2), segs=4)
    # the stay through the hub, lashed round both spar tops and the tail
    tl, tr = spar_ends(1.0)[0], spar_ends(-1.0)[0]
    rope(mesh, sag_path(tl + np.array([0, 0.06, 0]), tr + np.array([0, 0.06, 0]), 0.05, 9), 0.02, hub_b, tar=0.8,
         salt=0.3, segs=5)
    for k in range(3):  # the lashing round the tail at the hub: loops at odd angles
        R = ck.euler(rng.uniform(-70, 70), rng.uniform(0, 180), rng.uniform(-70, 70))
        th = np.linspace(0, 2 * math.pi, 10)
        rr = rng.uniform(0.06, 0.1)
        pts = HUB + np.array([0, -0.07 * k - 0.02, 0.06]) + (rr * np.column_stack([np.cos(th), 0.5 * np.sin(2 * th),
                                                                              0.8 * np.sin(th)])) @ R.T
        rope(mesh, pts, 0.016, hub_b, tar=0.7 - 0.12 * k, salt=0.4, hue=0.3 * k, segs=5)
    # the web: lines from turns round the spars to the body, the three knots on them
    lines = []  # (p0 on a spar, its spar, body point, body bone, radius, knot at t or None)
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        for bi, tb in enumerate(SPAR[tag]["belays"]):
            p0 = belay_turns(mesh, rig, side, tb, 2.0 - 0.4 * bi, tar=0.3 + 0.3 * bi)
            for kb, radius in (((1, 0.016), (3, 0.011)) if bi == 0 else ((2, 0.019), (4, 0.012))):
                sb_ = LENGTH * (kb + 0.5) / (N_BODY + 0.5)
                c, _t, v = body_at(sb_)
                q = c + X_AX * side * float(envelope(sb_)) * 0.95
                lines.append((p0, f"spar_{tag}", q, f"body{min(kb, N_BODY - 1)}", radius))
    knots_on = {0: 0.42, 6: 0.45, 3: 0.5}  # which web lines carry a monkey's fist, and where along them
    for n, (p0, sb, q, bb, radius) in enumerate(lines):
        L = float(np.linalg.norm(q - p0))
        pts = sag_path(p0, q, 0.06 * L, max(int(L / 0.14), 6), bow=np.array([0, 0, 0.12 * L]))
        tar = ck.smoothstep(0.7, 1.0, np.linspace(0, 1, len(pts)))
        bones = rig.blend(sb, bb, p0, q)
        rope(mesh, pts, radius, bones, tar=0.15 + 0.8 * tar, salt=0.5, hue=(n % 3) * 0.3, segs=5)
        if n in knots_on:
            t = knots_on[n]
            c = pts[int(round(t * (len(pts) - 1)))]
            R = ck.euler(rng.uniform(0, 90), rng.uniform(0, 90), rng.uniform(0, 90))
            monkeys_fist(mesh, c, R, 0.13, bones, rng)
            # the knot's tail, hanging
            tail = ck.bezier([c, c + np.array([0.02, -0.18, 0.04]), c + np.array([-0.03, -0.38, 0.02])], 5)
            rope(mesh, tail, 0.013, bones, tar=0.1, salt=0.6, hue=0.2, segs=4, fray_end=True, rng=rng)
    # long lines from the spar tops to the deck, behind; a stay forward to the deck
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        p0 = spar_point(side, 0.97)
        a = np.array([side * 0.55, 0.012, -1.25])
        pts = sag_path(p0, a, 0.06, 14)
        rope(mesh, pts, 0.014, rig.blend(f"spar_{tag}", "root", p0, a),
             tar=0.6 * ck.smoothstep(0.6, 0.0, np.linspace(0, 1, 14)), salt=0.5, hue=0.5, segs=4)
        ring_bolt(mesh, a, root_b)
    # broken lines hanging from the hub and the spars, frayed where they parted
    for p0, bone, drop, sway in ((HUB + np.array([0.22, -0.02, 0.1]), "hub", 1.15, (0.15, 0.1)),
                                 (HUB + np.array([-0.18, -0.05, 0.14]), "hub", 0.8, (-0.12, 0.2)),
                                 (spar_point(1.0, 0.75) + np.array([0.0, 0.0, 0.1]), "spar_l", 0.7, (0.05, 0.1))):
        sx, sz = sway
        path = ck.bezier([p0, p0 + np.array([sx * 0.5, -drop * 0.4, sz]), p0 + np.array([sx, -drop, sz * 0.6])], 9)
        rope(mesh, path, rng.uniform(0.01, 0.015), rig.rigid(bone), tar=0.4, salt=0.4, hue=rng.uniform(0, 1), segs=4,
             fray_end=True, rng=rng)
    # turns hitched round the body: a line from the hub spiralling down the upper body
    s_line = np.linspace(0.12, LENGTH * 0.55, 26)
    pts = []
    for n, s in enumerate(s_line):
        c, _t, v = body_at(float(s))
        th = 1.4 + 2 * math.pi * 1.7 * n / (len(s_line) - 1)
        r = float(envelope(s)) * 1.18 + 0.02
        pts.append(c + r * (math.cos(th) * 1.12 * X_AX + math.sin(th) * v))
    pts = [HUB + np.array([0.05, -0.05, 0.08])] + pts
    skin = rig.chain([f"body{i}" for i in range(N_BODY)], j)
    rope(mesh, np.array(pts), 0.014, skin, tar=0.75, salt=0.25, hue=0.1, segs=5, fray_end=True, rng=rng)


def ring_bolt(mesh: ck.Mesh, p: np.ndarray, bone) -> None:
    Pb, Tb = ck.tube(np.array([p + np.array([0, 0.004, 0]), p + np.array([0, 0.03, 0])]), np.array([0.03, 0.022]), 6)
    Pb[:, 1] = np.maximum(Pb[:, 1], 0.002)
    ck.finish(mesh, Pb, Tb, "timber", PAL["volcanic_stone"] * 0.85, bone, wet=0.3, cavity=0.3, flat=True)


def deadeyes(mesh: ck.Mesh, k: int, bone, rng) -> None:
    """A pair of deadeyes set up with a lanyard, the lower one strapped to the deck by an iron chainplate."""
    a = ANCHORS[k]
    up = shroud_point(k, 1.0)
    d = unit(HUB - a)
    lo = a + d * (DEADEYE_LO / d[1])
    face = unit(np.cross(d, Y_AX) if abs(d[1]) < 0.99 else X_AX)  # the deadeyes' faces look across the shroud
    e_up = np.cross(face, d)
    for c, cc in ((up, 0), (lo, 1)):
        aa = np.arange(8) * 2 * math.pi / 8
        prof = []
        for w, rr in ((-0.026, 0.05), (-0.03, 0.062), (0.03, 0.062), (0.026, 0.05)):
            prof.append(c + face * w + rr * (np.outer(np.cos(aa), d) + np.outer(np.sin(aa), e_up)))
        P, T = loft(prof, cap_start=c - face * 0.024, cap_end=c + face * 0.024, centres=[c] * 4)
        col = ck.mix(PAL["timber_weathered"] * 0.75, PAL["coral_stone_weathered"] * 0.8,
                     ck.smoothstep(-0.2, 0.3, ck.fbm(P * 30.0, SEED + 90 + k * 2 + cc))[:, None])
        ck.finish(mesh, P, T, "timber", col, bone, wet=0.15, cavity=0.2, flat=True)
        for h in range(3):  # the three holes, dark, on both faces
            ang = math.pi / 2 + h * 2 * math.pi / 3
            hc = c + 0.03 * (math.cos(ang) * d + math.sin(ang) * e_up)
            for sgn in (1.0,):
                hc2 = hc + face * sgn * 0.0262
                ang5 = np.arange(5) * (2 * math.pi / 5)
                ring = hc2 + 0.011 * (np.outer(np.cos(ang5), d) + np.outer(np.sin(ang5), e_up))
                Ph = np.vstack([hc2[None] - face * sgn * 0.004, ring])
                Th = np.array([(0, 1 + q, 1 + (q + 1) % 5) for q in range(5)], dtype=np.int64)
                if np.dot(np.cross(Ph[Th[0, 1]] - Ph[0], Ph[Th[0, 2]] - Ph[0]), face * sgn) < 0:
                    Th = ck.flip(Th)
                ck.finish(mesh, Ph, Th, "timber", PAL["lacquer_black"], bone, wet=0.5, cavity=1.0)
    # the lanyard: three parts between the deadeyes
    for h in range(3):
        ang = math.pi / 2 + h * 2 * math.pi / 3
        o = 0.03 * (math.cos(ang) * d + math.sin(ang) * e_up)
        rope(mesh, np.array([up + o + face * 0.01 * (h - 1), lo + o - face * 0.01 * (h - 1)]), 0.0065, bone, tar=0.1,
             salt=0.4, hue=0.7, segs=3)
    # the chainplate: an iron strap from the lower deadeye to a bolt in the deck
    foot = a + np.array([0, 0.012, 0])
    mid = 0.5 * (lo + foot)
    Ps, Ts = box(mid, unit(lo - foot), face, np.cross(unit(lo - foot), face), float(np.linalg.norm(lo - foot)) * 0.5,
                 0.018, 0.007)
    Ps[:, 1] = np.maximum(Ps[:, 1], 0.002)
    ck.finish(mesh, Ps, Ts, "timber", ck.mix(PAL["volcanic_stone"], PAL["laterite"] * 0.6, 0.45), bone, wet=0.3,
              cavity=0.3, flat=True)
    ring_bolt(mesh, a, bone)


def block_and_tackle(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    rng = np.random.default_rng(SEED + 21)
    bb, tk = rig.rigid("block"), rig.rigid("tackle")
    top = j[2] + BLOCK_HEAD_OFF
    up_c = j[2] + BLOCK_TAIL_OFF
    lo_c = up_c + np.array([0.0, -TACKLE_DROP, 0.0])

    def block(c, size, bone, seed):
        radii = np.array([0.055, 0.1, 0.075]) * size
        Pb, Tb = ck.ellipsoid(c, radii, 5, 8)
        Pd = (Pb - c) / radii
        Pb = c + np.sign(Pd) * np.abs(Pd) ** 0.7 * radii  # squared off toward a block's cheeks
        col = ck.mix(PAL["timber_weathered"] * 0.5, PAL["timber_weathered"] * 0.85,
                     ck.smoothstep(-0.3, 0.3, ck.fbm(Pb * np.array([60.0, 8.0, 60.0]), seed))[:, None])
        ck.finish(mesh, Pb, Tb, "timber", col, bone, wet=0.4, cavity=0.25, flat=True)
        # iron strop round it (in the yz plane), the sheave pin's brass ends on the cheeks
        th = np.linspace(0, 2 * math.pi, 11)
        st = c + np.column_stack([np.zeros(11), 0.108 * size * np.cos(th), 0.082 * size * np.sin(th)])
        Ps, Ts = ck.tube(st, 0.011 * size, 4, cap_start=False, cap_end=False, up_hint=(1.0, 0.0, 0.0))
        ck.finish(mesh, Ps, Ts, "timber", ck.mix(PAL["volcanic_stone"], PAL["laterite"] * 0.55, 0.4), bone, wet=0.4,
                  cavity=0.2, flat=True)
        for sgn in (-1.0, 1.0):
            Pp, Tp = ck.tube(np.array([c + X_AX * sgn * 0.05 * size, c + X_AX * sgn * 0.066 * size]), 0.018 * size, 6)
            ck.finish(mesh, Pp, Tp, "timber", PAL["brass"] * 0.85, bone, wet=0.3, cavity=0.15)
        # the sheave showing in its slot at the bottom
        Pv, Tv = ck.ellipsoid(c + np.array([0, -0.07 * size, 0]), (0.02 * size, 0.04 * size, 0.04 * size), 3, 6)
        ck.finish(mesh, Pv, Tv, "timber", PAL["timber_weathered"] * 0.35, bone, wet=0.5, cavity=0.6)

    block(up_c, 1.0, bb, SEED + 22)
    block(lo_c, 0.8, tk, SEED + 23)
    # the pendant from the body to the upper block's eye
    rope(mesh, np.array([top, 0.5 * (top + up_c) + np.array([0.01, 0, 0]), up_c + np.array([0, 0.1, 0])]), 0.014, bb,
         tar=0.7, salt=0.2, segs=5)
    # three falls between the blocks
    for k, dz in enumerate((-0.045, 0.0, 0.045)):
        p0 = up_c + np.array([0.0, -0.09, dz])
        p1 = lo_c + np.array([0.0, 0.07, dz * 0.8])
        rope(mesh, np.linspace(p0, p1, 4), 0.0085, rig.blend("block", "tackle", p0, p1), tar=0.1, salt=0.5,
             hue=0.3 + 0.2 * k, segs=4)
    # the hauling part, hanging off and frayed
    p0 = up_c + np.array([0.0, -0.06, 0.07])
    path = ck.bezier([p0, p0 + np.array([0.06, -0.35, 0.15]), p0 + np.array([0.18, -0.55, 0.05]),
                      p0 + np.array([0.22, -0.9, 0.12])], 9)
    rope(mesh, path, 0.0095, rig.blend("block", "tackle", path[0], path[-1]), tar=0.1, salt=0.5, hue=0.5, segs=4,
         fray_end=True, rng=rng)
    # the hook under the lower block
    hook(mesh, lo_c + np.array([0, -0.075, 0]), np.array([0.0, -1.0, 0.0]), np.array([0.0, 0.0, 1.0]), 0.16, 0.016, tk,
         PAL["volcanic_stone"] * 0.9, PAL["laterite"] * 0.6, n=6, segs=5, wet=0.3)


# ---------------------------------------------------------------------------------------------
# The body
# ---------------------------------------------------------------------------------------------
NS = 18
NR = 92


def ring_positions() -> np.ndarray:
    s = np.linspace(0.0, LENGTH, 3001)
    dens = np.ones_like(s) * 0.8
    for k in range(N_PLATE):
        dens += 2.2 * g(s - PLATE_EDGES[k] - 0.012, 0.025) + 2.6 * g(s - S_GAP[k], GAP_W[k] * 0.6)
    dens += 2.0 * g(s - S_GAP[WOUND_MAIN], 0.06)
    dens += 1.0 * ck.smoothstep(0.1, 0.0, s)
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (dens[1:] + dens[:-1]) * np.diff(s))])
    return np.interp(np.linspace(0.0, cdf[-1], NR), cdf, s)


def body(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> dict:
    s_r = ring_positions()
    phi = np.arange(NS) * (2.0 * math.pi / NS)
    C, V, Tg = [], [], []
    for s in s_r:
        c, t, v = body_at(float(s))
        C.append(c)
        V.append(v)
        Tg.append(t)
    C, V, Tg = np.array(C), np.array(V), np.array(Tg)
    prof, kpl, q, m = plate_profile(s_r)
    S = np.repeat(s_r, NS)
    PH = np.tile(phi, NR)
    Q = np.repeat(q, NS)
    K = np.repeat(kpl, NS)
    M = np.repeat(m, NS)
    on_plate = ((Q > 0.02) & (Q < 1 - M)).astype(np.float64) * ((S >= S_PLATE0) & (S <= S_PLATE1))
    sx, sy, flange = section(PH, K, Q, on_plate)
    # no two plates alike: each a little fatter or thinner and set a little off the line
    mids = 0.5 * (PLATE_EDGES[:-1] + PLATE_EDGES[1:])
    jit = 1.0 + 0.07 * noise1(np.arange(N_PLATE) * 2.3, SEED + 107)
    shift = 0.018 * noise1(np.arange(N_PLATE) * 1.9, SEED + 108)
    R = np.repeat(envelope(s_r) * prof * np.interp(s_r, mids, jit), NS)
    C = C + np.outer(np.interp(s_r, mids, shift), X_AX)
    centre = np.repeat(C, NS, axis=0)
    Vv = np.repeat(V, NS, axis=0)
    out = np.outer(np.cos(PH), X_AX) + np.sin(PH)[:, None] * Vv
    P0 = centre + R[:, None] * (sx[:, None] * X_AX + sy[:, None] * Vv)
    membrane = ((Q >= 1 - M) | (Q < 0.02)).astype(np.float64) * ((S >= S_PLATE0) & (S <= S_PLATE1))
    ventral = ck.smoothstep(0.2, 0.75, np.sin(PH))
    # relief: pitting and scratches on the plates, folds in the membranes, sternite grooves in front
    pits = ck.smoothstep(0.25, 0.5, ck.fbm(P0 * 26.0, SEED + 101)) * on_plate
    scratch = np.abs(np.sin(P0 @ np.array([31.0, 13.0, -9.0]) + 4.0 * ck.fbm(P0 * 3.0, SEED + 102)))
    scratch = ck.smoothstep(0.55, 0.8, scratch)
    scratch = scratch * ck.smoothstep(0.1, 0.4, ck.fbm(P0 * 5.0, SEED + 103)) * on_plate
    fold = np.sin(PH * 9.0 + 6.0 * ck.fbm(P0 * 4.0, SEED + 104)) * membrane
    groove = g(np.cos(PH), 0.12) * ventral * on_plate  # the sternites' midline groove
    pleura = g(np.sin(PH) - 0.3, 0.1) * ((S >= S_PLATE0) & (S <= S_PLATE1))  # soft skin between back and belly plates
    opn, lip, spill, core = wound_fields(S, PH)
    lump = ck.fbm(P0 * 4.0, SEED + 105)
    disp = (0.008 * lump - 0.004 * pits + 0.006 * fold - 0.01 * groove - 0.028 * pleura - 0.05 * opn - 0.035 * core
            + 0.03 * lip)
    P = P0 + out * disp[:, None]
    T = orient(P, ck.flip(ck.grid_tris(NR, NS, True)), centre)
    # tail tip: a fan to a point above the first ring
    tip_idx = len(P)
    c0, t0, _v0 = body_at(0.0)
    P = np.vstack([P, (c0 - t0 * 0.03)[None]])
    cap = np.array([(q_, tip_idx, (q_ + 1) % NS) for q_ in range(NS)], dtype=np.int64)
    T = np.vstack([T, orient(P, cap, C[1])])
    neck_idx = len(P)
    c1, t1, _v1 = body_at(LENGTH)
    P = np.vstack([P, (c1 + t1 * 0.04)[None]])
    last = (NR - 1) * NS
    cap = np.array([(last + q_, last + (q_ + 1) % NS, neck_idx) for q_ in range(NS)], dtype=np.int64)
    T = np.vstack([T, orient(P, cap, C[-2])])
    pad = lambda a, v=0.0: np.concatenate([a, [v, v]])  # noqa: E731
    S, PH, on_plate, membrane, ventral = pad(S), pad(PH), pad(on_plate), pad(membrane, 1.0), pad(ventral)
    opn, lip, spill, core, pits, scratch, lump, Q, flange, fold, pleura = (
        pad(x) for x in (opn, lip, spill, core, pits, scratch, lump, Q, flange, fold, pleura))
    # colour: lacquer-black plates (abyss navy where the lacquer is thick), lips and flange edges worn to slate,
    # paler slate sternites in front, wet teal-dark membranes, scratches and pits; bruised round the seams
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], (0.7 * ck.smoothstep(-0.25, 0.35, lump))[:, None])
    edge = np.clip(g(Q - 0.06, 0.06) * on_plate + ck.smoothstep(0.08, 0.2, flange), 0, 1)
    col = ck.mix(col, PAL["overcast_slate"] * 0.75, (0.65 * edge)[:, None])
    # dried brine crusted along the lips and flanges, where the sea ran off it: the pale read at night
    salt = edge * ck.smoothstep(-0.05, 0.3, ck.fbm(P * np.array([14.0, 6.0, 14.0]), SEED + 109))
    col = ck.mix(col, PAL["bone"] * 0.82, (0.7 * salt)[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 0.95, (0.55 * ventral * on_plate)[:, None])
    col = ck.mix(col, ck.mix(PAL["abyss_navy"], PAL["deep_teal_shadow"], 0.35) * 0.8,
                 np.clip(0.9 * membrane + 0.8 * pleura, 0, 1)[:, None])
    col = ck.mix(col, PAL["cold_blue_stone"] * 0.75, (0.5 * scratch)[:, None])
    col = ck.mix(col, PAL["lacquer_black"] * 0.8, (0.6 * pits)[:, None])
    col = ck.mix(col, PAL["abyss_navy"], (0.6 * spill * (1 - opn))[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 1.15, (0.5 * lip * (1 - opn))[:, None])
    fib = 0.65 + 0.35 * ck.smoothstep(-0.3, 0.3, ck.fbm(P * np.array([30.0, 10.0, 30.0]), SEED + 106))
    col = ck.mix(col, PAL["deep_teal_shadow"] * 0.5, opn[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.85 * fib[:, None], core[:, None])
    emission = np.clip(0.25 * opn + 0.85 * core * fib, 0.0, 1.0)
    cavity = np.clip(0.12 + 0.6 * membrane * (0.5 + 0.5 * fold) + 0.5 * pleura + 0.4 * pits
                     + 0.7 * np.clip(opn - core, 0, 1)
                     + 0.4 * g(Q - 0.02, 0.03) * on_plate, 0.0, 1.0)
    wet = np.clip(0.8 - 0.1 * membrane - 0.3 * scratch - 0.6 * salt, 0.15, 1.0)
    skin = rig.chain([f"body{i}" for i in range(N_BODY)], j)
    ck.finish(mesh, P, T, "carapace", col, skin, wet=wet, cavity=cavity, emission=emission)
    return {"P": P, "s_r": s_r, "C": C, "V": V, "Tg": Tg, "skin": skin}


def body_spines(mesh: ck.Mesh, rig: ck.Rig, bd: dict) -> None:
    """A spine at each plate's flange corner, pointing out and up toward the tail; hooks down the keel; the tail
    spike."""
    rng = np.random.default_rng(SEED + 31)
    for k in range(N_PLATE):
        s = PLATE_EDGES[k] + 0.07 * (PLATE_EDGES[1] - PLATE_EDGES[0])
        c, t, v = body_at(float(s))
        r = float(envelope(s)) * 1.05
        bone = rig.rigid(body_bone_at(float(s)))
        for side in (-1.0, 1.0):
            base = c + X_AX * side * r * 1.12 * 1.3 - v * r * 0.1
            d = unit(X_AX * side * 1.0 - t * 0.9 - v * 0.15)
            ln = rng.uniform(0.1, 0.17) * (0.7 + 0.6 * math.sin(math.pi * (k + 0.5) / N_PLATE))
            Ps, Ts = nail(base, d, ln, 0.02, -t, rng.uniform(0.3, 0.8))
            tt = np.array([0, 0, 0, 0, 0.55, 0.55, 0.55, 0.55, 1.0])
            ck.finish(mesh, Ps, Ts, "carapace", ck.mix(PAL["lacquer_black"], PAL["bone"] * 0.7, tt[:, None] ** 2),
                      bone, wet=0.8, cavity=0.1, flat=True)
        if 1 <= k <= 6:
            base = c - v * r * 0.86 * 1.05
            Ps, Ts = nail(base, unit(-v - t * 0.6), rng.uniform(0.05, 0.09), 0.014, -t, 0.7)
            ck.finish(mesh, Ps, Ts, "carapace", PAL["lacquer_black"] * 1.2, bone, wet=0.9, cavity=0.1, flat=True)
    c, t, v = body_at(0.02)
    hook(mesh, c, -t + v * 0.1, -v, 0.34, 0.035, rig.rigid("body0"), PAL["lacquer_black"], PAL["bone"] * 0.75, n=7)


# ---------------------------------------------------------------------------------------------
# Limbs
# ---------------------------------------------------------------------------------------------
def limb(mesh: ck.Mesh, bone, root, knee, grip, side: float, rng) -> None:
    """A jointed, hooked limb: coxa, femur, tibia, and a tarsus that hooks round what it grips."""
    joints = [root, root + (knee - root) * 0.28, knee, knee + (grip - knee) * 0.62, grip]
    widths = [0.05, 0.042, 0.034, 0.024, 0.016]
    for i in range(4):
        a, b = joints[i], joints[i + 1]
        n = 4
        t = np.linspace(0, 1, n)
        path = a + np.outer(t, b - a)
        w0, w1 = widths[i], widths[i + 1]
        rad = (w0 + (w1 - w0) * t) * (0.78 + 0.32 * np.sin(np.pi * np.clip(t * 1.1, 0, 1)) ** 0.5)
        P, T = ck.tube(path, rad, 6, squash=0.8, up_hint=(0.0, 0.0, 1.0))
        tt = np.concatenate([np.repeat(t, 6), [0.0, 1.0]])
        joint = ck.smoothstep(0.18, 0.0, tt) + ck.smoothstep(0.82, 1.0, tt)
        col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"] * 1.4, (0.4 * ck.smoothstep(0.3, 0.6, tt) *
                                                                    ck.smoothstep(0.9, 0.6, tt))[:, None])
        col = ck.mix(col, PAL["deep_teal_shadow"] * 0.7, (0.7 * np.clip(joint, 0, 1))[:, None])
        ridge = ck.smoothstep(0.3, 0.6, ck.fbm(P * 20.0, SEED + 140 + i))
        col = ck.mix(col, PAL["overcast_slate"] * 0.55, (0.35 * ridge)[:, None])
        ck.finish(mesh, P, T, "carapace", col, bone, wet=0.9, cavity=0.15 + 0.4 * np.clip(joint, 0, 1))
        if i in (1, 2):  # a spur at the joint
            d = unit(b - a)
            Ps, Ts = nail(b - d * 0.02, unit(d + Y_AX * 0.4 + X_AX * side * 0.3), rng.uniform(0.05, 0.08), 0.01,
                          -d, 0.4)
            ck.finish(mesh, Ps, Ts, "carapace", ck.mix(PAL["lacquer_black"], PAL["bone"] * 0.6, 0.3), bone, wet=0.8,
                      flat=True)
    # the hooked claw, curling round the grip, and a smaller thumb-hook against it
    d = unit(grip - joints[3])
    hook(mesh, grip - d * 0.01, d, -Y_AX + d * 0.2, 0.15, 0.02, bone, PAL["lacquer_black"], PAL["bone"] * 0.75,
         n=5, segs=5)
    hook(mesh, grip - d * 0.04, unit(d - Y_AX * 0.4), Y_AX, 0.08, 0.012, bone, PAL["lacquer_black"],
         PAL["bone"] * 0.7, n=4, segs=4)


def limbs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rng = np.random.default_rng(SEED + 41)
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        # the upper pair reach up and out to grip the spars
        s = LENGTH * 0.55
        c, t, v = body_at(s)
        root = c + X_AX * side * float(envelope(s)) * 1.15 + v * 0.03
        grip = spar_point(side, 0.5) + np.array([-side * 0.11, 0.0, 0.06])
        knee = 0.5 * (root + grip) + np.array([side * 0.12, 0.42, 0.22])
        limb(mesh, rig.rigid(body_bone_at(s)), root, knee, grip, side, rng)
        # the lower pair grip the shrouds behind, hooked through the ratlines
        s = LENGTH * 0.78
        c, t, v = body_at(s)
        root = c + X_AX * side * float(envelope(s)) * 1.1
        grip = shroud_point(0 if side < 0 else 1, 0.62)
        knee = 0.5 * (root + grip) + np.array([side * 0.15, 0.3, 0.12])
        limb(mesh, rig.rigid(body_bone_at(s)), root, knee, grip, side, rng)


# ---------------------------------------------------------------------------------------------
# The head
# ---------------------------------------------------------------------------------------------
def head(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    """A long dark skull with a crest of spines, and on its front a face that is wrong: a pale, blank mask with
    skinned-over sockets where eyes should be, split down the middle by the mouth, a seam that glows from inside and
    runs on under the chin and down the throat, lipped, with a hooked mandible either side of it."""
    hb = rig.rigid("head")
    f = unit(np.array([0.0, -0.2, 0.5]))
    up = np.cross(f, X_AX)
    R = np.column_stack([X_AX, up, f])
    O = j[-1] + f * 0.02
    Rs = R * HEAD_SCALE
    zk = [-0.1, -0.02, 0.08, 0.18, 0.28, 0.36, 0.42, 0.46, 0.49, 0.505]
    wk = [0.12, 0.13, 0.135, 0.13, 0.125, 0.12, 0.112, 0.1, 0.08, 0.04]
    htk = [0.12, 0.13, 0.14, 0.14, 0.135, 0.13, 0.12, 0.11, 0.09, 0.04]
    hbk = [0.11, 0.115, 0.115, 0.11, 0.105, 0.1, 0.095, 0.085, 0.065, 0.03]
    zs = [-0.1, -0.04, 0.03, 0.1, 0.17, 0.23, 0.28, 0.32, 0.36, 0.4, 0.43, 0.455, 0.475, 0.49, 0.5, 0.505]
    na = 22
    u = np.arange(na) * 2 * math.pi / na
    a = u + 0.32 * np.sin(2 * u)  # denser round the midlines (top and bottom), where the seam and crest run
    ca, sa = np.cos(a), np.sin(a)
    rings, info = [], []
    for z in zs:
        w, ht, hbm = (float(np.interp(z, zk, v)) for v in (wk, htk, hbk))
        x = w * np.sign(ca) * np.abs(ca) ** 0.75
        y = np.where(sa >= 0, ht, hbm) * np.sign(sa) * np.abs(sa) ** 0.8
        xn = np.abs(ca)
        # the seam: under the chin and down the throat, and up the front behind the mask's split
        seam_line = g(ca, 0.13) * ((sa < 0) * ck.smoothstep(0.02, 0.12, z) + (sa >= 0) * ck.smoothstep(0.38, 0.46, z))
        lipz = g(np.abs(ca) - 0.22, 0.09) * (sa < 0) * ck.smoothstep(0.02, 0.12, z) * ck.smoothstep(0.47, 0.4, z)
        brow = g(z - 0.36, 0.06) * g(sa - 0.75, 0.22) * g(xn - 0.45, 0.35)
        cheek = g(z - 0.24, 0.09) * g(sa + 0.1, 0.35) * (xn > 0.5)
        crest = g(ca, 0.1) * (sa > 0.5) * ck.smoothstep(0.38, 0.0, z) * ck.smoothstep(-0.1, 0.05, z)
        rr = np.column_stack([x, y, np.full(na, z)])
        outw = unit_rows(np.column_stack([x / max(w, 1e-3), y / max(ht, 1e-3), np.zeros(na)]))
        ridge = 0.006 * np.sin(z * 80.0) * ck.smoothstep(0.3, 0.0, z) * (sa > -0.2)  # neck rings behind the skull
        disp = -0.035 * seam_line + 0.016 * lipz + 0.025 * brow + 0.024 * cheek + 0.03 * crest + ridge
        rr = rr + outw * disp[:, None]
        rings.append(rr)
        info.append(np.column_stack([seam_line, lipz, brow, crest, np.full(na, z)]))
    Pl, Tl = loft(rings, cap_start=np.array([0.0, 0.0, -0.13]), cap_end=np.array([0.0, 0.0, 0.51]),
                  centres=[np.array([0, 0, z]) for z in zs])
    inf = np.vstack(info + [np.array([[0, 0, 0, 0, -0.13]]), np.array([[1.0, 0, 0, 0, 0.51]])])
    seam, lipz, brow, crest, zl = inf.T
    lump = ck.fbm(Pl * 9.0, SEED + 151)
    Pl = Pl + 0.004 * lump[:, None] * np.array([1.0, 1.0, 0.0])
    P = Pl @ Rs.T + O
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(0.0, 0.5, lump)[:, None])
    col = ck.mix(col, PAL["overcast_slate"] * 0.6, (0.6 * brow + 0.4 * crest)[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 1.1, (0.7 * lipz * (1 - seam))[:, None])
    core = ck.smoothstep(0.45, 0.95, seam)
    col = ck.mix(col, PAL["deep_teal_shadow"] * 0.5, ck.smoothstep(0.15, 0.45, seam)[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.9, core[:, None])
    emission = np.clip(0.3 * ck.smoothstep(0.15, 0.45, seam) + 0.85 * core, 0, 1)
    cav = np.clip(0.15 + 0.5 * ck.smoothstep(0.15, 0.5, seam) * (1 - core), 0, 1)
    ck.finish(mesh, P, Tl, "carapace", col, hb, wet=0.9, cavity=cav, emission=emission)
    # the mask: two pale, curved half-plates split down the middle, a skinned-over socket in each
    A = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    for sgn in (-1.0, 1.0):
        rings_m, inf_m = [], []
        bs = np.linspace(0.0, 1.0, 7)
        for bv in bs:
            yb = -0.11 + 0.25 * bv
            W = 0.118 * math.sin(math.pi * (0.12 + 0.8 * bv)) ** 0.55
            sock = g(A - 0.5, 0.2) * float(g(bv - 0.67, 0.13))
            zf = 0.49 + 0.045 * (1 - A ** 2) - 0.05 * (bv - 0.55) ** 2 - 0.034 * sock
            xf = sgn * (0.017 + A * W)
            front = np.column_stack([xf, np.full(5, yb) + 0.012 * sock, zf])
            back_a = np.array([1.0, 0.5, 0.0])
            back = np.column_stack([sgn * (0.017 + back_a * W * 0.92), np.full(3, yb),
                                    0.49 + 0.045 * (1 - back_a ** 2) - 0.05 * (bv - 0.55) ** 2 - 0.028])
            rings_m.append(np.vstack([front, back]))
            edge = np.concatenate([np.maximum(ck.smoothstep(0.6, 1.0, A), abs(bv - 0.5) * 2 > 0.9), np.ones(3)])
            inf_m.append(np.column_stack([np.concatenate([sock, np.zeros(3)]), edge]))
        cen = [r.mean(axis=0) for r in rings_m]
        Pm, Tm = loft(rings_m, cap_start=cen[0] + np.array([0.0, -0.008, 0.0]),
                      cap_end=cen[-1] + np.array([0, 0.008, 0]), centres=cen)
        im = np.vstack(inf_m + [np.array([[0.0, 1.0]]), np.array([[0.0, 1.0]])])
        sock, edge = im.T
        crack = ck.smoothstep(0.3, 0.45, ck.fbm(Pm * 40.0, SEED + 171 + int(sgn)))
        colm = ck.mix(PAL["bone"] * 0.74, PAL["cold_blue_stone"] * 1.05, 0.35)
        colm = ck.mix(np.broadcast_to(colm, (len(Pm), 3)), PAL["storm_slate"], (0.55 * edge)[:, None])
        colm = ck.mix(colm, PAL["overcast_slate"] * 0.6, (0.5 * crack)[:, None])
        colm = ck.mix(colm, PAL["lacquer_black"] * 0.8, np.clip(1.5 * sock, 0, 1)[:, None])
        ck.finish(mesh, Pm @ Rs.T + O, Tm, "carapace", colm, hb, wet=0.25 + 0.4 * edge,
                  cavity=np.clip(0.1 + 0.9 * sock + 0.3 * crack, 0, 1))
    # the mandibles: a hooked pair at the mask's lower corners, curling in toward the seam
    for sgn in (-1.0, 1.0):
        base = O + Rs @ np.array([sgn * 0.07, -0.1, 0.46])
        d = R @ unit(np.array([sgn * 0.35, -0.6, 0.6]))
        hook(mesh, base, d, R @ np.array([-sgn, 0.0, 0.3]), 0.24, 0.03, hb, PAL["lacquer_black"], PAL["bone"] * 0.8,
             n=7, segs=6)
        base = O + Rs @ np.array([sgn * 0.035, -0.1, 0.3])  # small palps behind
        hook(mesh, base, R @ unit(np.array([sgn * 0.2, -1.0, 0.3])), R @ np.array([0.0, 0.0, 1.0]), 0.1, 0.012, hb,
             PAL["lacquer_black"], PAL["storm_slate"], n=5, segs=5)
    # the crest: short spines down the skull
    rng = np.random.default_rng(SEED + 161)
    for z in (0.02, 0.1, 0.18, 0.26):
        ht = float(np.interp(z, zk, htk))
        base = O + Rs @ np.array([0.0, ht + 0.02, z])
        Ps, Ts = nail(base, R @ unit(np.array([0.0, 1.0, -0.8])), rng.uniform(0.06, 0.1), 0.014,
                      R @ np.array([0, 0, -1.0]), 0.5)
        ck.finish(mesh, Ps, Ts, "carapace", ck.mix(PAL["lacquer_black"], PAL["bone"] * 0.6, 0.25), hb, wet=0.8,
                  flat=True)


def unit_rows(V: np.ndarray) -> np.ndarray:
    ln = np.linalg.norm(V, axis=1, keepdims=True)
    ln[ln < 1e-9] = 1.0
    return V / ln


# ---------------------------------------------------------------------------------------------
# Shroud (phase 1) and Sheath (phase 2)
# ---------------------------------------------------------------------------------------------
SAIL_OPEN = (math.pi / 2 - 0.8, math.pi / 2 + 0.95)  # the open front, toward the party (a little to the -X flank)


def shroud_mesh(rig: ck.Rig, j: np.ndarray) -> ck.Mesh:
    """Torn, tarred sailcloth wrapped round the back and flanks, open in front, gathered and lashed at the hub."""
    rng = np.random.default_rng(SEED + 51)
    m = ck.Mesh("Shroud")
    # M3-CRB-013: gathered at the hub on body0 and body1, the lower half on `sail` (blended across body1's last third)
    skin = rig.chain(["body0", "body1", "sail"], [j[0], j[1], j[2], j[4]])
    NU, NV = 20, 19
    s_end = LENGTH * 0.86
    us = np.linspace(0.0, 1.0, NU)
    p_from = SAIL_OPEN[1]
    p_to = SAIL_OPEN[0] + 2 * math.pi
    vs = np.linspace(0.0, 1.0, NV)
    P = np.zeros((NU, NV, 3))
    for i, uu in enumerate(us):
        s = 0.04 + (s_end - 0.04) * uu
        c, t, v = body_at(float(s))
        r_body = float(envelope(s))
        gather = ck.smoothstep(0.0, 0.18, uu)
        for k, vv in enumerate(vs):
            ph = p_from + (p_to - p_from) * vv
            fold = (0.07 * math.sin(vv * 2 * math.pi * 4.5 + uu * 2.5)
                    + 0.03 * math.sin(vv * 2 * math.pi * 9.5 + 1.0)) * (0.3 + 1.0 * uu)
            r = r_body * 1.65 * (0.45 + 0.55 * gather) + 0.09 + fold + 0.22 * uu * uu
            o = math.cos(ph) * 1.35 * X_AX + math.sin(ph) * v
            P[i, k] = c + o * r + Y_AX * (-0.04 * uu * uu * math.sin(math.pi * vv))
    P = P.reshape(-1, 3)
    P = P + (0.035 * ck.fbm(P * 3.0, SEED + 52))[:, None] * np.array([1.0, 0.4, 1.0])
    U = np.repeat(us, NV)
    Vv = np.tile(vs, NU)
    T = ck.grid_tris(NU, NV, False)
    # the ragged hem, long tatters, rotted rents
    hem = 0.72 + 0.12 * noise1(Vv * 9.0, SEED + 53) + 0.25 * (noise1(Vv * 19.0, SEED + 54) > 0.35)
    rot = ck.fbm(P * 3.4, SEED + 55)
    tc = T
    keep = []
    for tri in tc:
        uu = U[tri].mean()
        vv = Vv[tri].mean()
        if uu > hem[tri].min():
            keep.append(False)
            continue
        hole = rot[tri].max() > 0.25 and 0.15 < uu < 0.95
        keep.append(not hole)
    T = tc[np.array(keep)]
    # the cloth: panels running down it with doubled seams, faded and stained per panel, tarred and rotted at the rents
    panel = np.floor(Vv * 7.0)
    seam = g(np.mod(Vv * 7.0 + 0.5, 1.0) - 0.5, 0.06)
    shade = noise1(panel * 3.7, SEED + 56) * 0.5 + 0.5
    col = ck.mix(PAL["sand_cloth"] * 0.82, PAL["sand_cloth"] * 1.0, shade[:, None])
    stain = ck.smoothstep(0.0, 0.4, ck.fbm(P * 2.0, SEED + 57))
    col = ck.mix(col, PAL["timber_weathered"] * 0.75, (0.35 * stain)[:, None])
    col = ck.mix(col, PAL["timber_weathered"] * 0.55, (0.55 * seam)[:, None])
    reef = g(U - 0.42, 0.018)
    col = ck.mix(col, PAL["sand_cloth"] * 0.72, (0.6 * reef)[:, None])
    near_rot = ck.smoothstep(0.1, 0.25, rot)
    col = ck.mix(col, PAL["lacquer_black"] * 1.3, (0.75 * near_rot)[:, None])
    near_hem = ck.smoothstep(hem - 0.12, hem, U)
    col = ck.mix(col, PAL["lacquer_black"] * 1.5, (0.6 * near_hem)[:, None])
    top = ck.smoothstep(0.2, 0.0, U)
    col = ck.mix(col, PAL["lacquer_black"] * 1.2, (0.7 * top)[:, None])
    cav = np.clip(0.2 + 0.4 * seam + 0.3 * near_rot, 0, 1)
    wet = np.clip(0.35 + 0.5 * near_rot + 0.4 * near_hem, 0, 1)
    for inside in (False, True):
        Tt = ck.flip(T) if inside else T
        Ti = orient(P, Tt, np.vstack([body_at(float(0.04 + (s_end - 0.04) * x))[0] for x in U]))
        Ti = ck.flip(Ti) if inside else Ti
        ck.finish(m, P, Ti, "sail", col * (0.55 if inside else 1.0), skin, wet=wet, cavity=cav)
    # bolt ropes down both free edges, with brass grommets
    grid = P.reshape(NU, NV, 3)
    hem_u = [hem.reshape(NU, NV)[:, k].min() for k in (0, NV - 1)]
    for k, hu in zip((0, NV - 1), hem_u):
        n_ok = max(int(hu * (NU - 1)), 3)
        edge = grid[: n_ok + 1, k]
        rope(m, edge, 0.012, skin, tar=0.7, salt=0.3, segs=4, fray_end=True, rng=rng)
        for i in range(2, n_ok, 4):
            c = edge[i]
            nb = unit(np.cross(edge[min(i + 1, n_ok)] - edge[i - 1], grid[i, k + (1 if k == 0 else -1)] - c))
            Pg, Tg = ck.tube(np.array([c - nb * 0.008, c + nb * 0.008]), 0.016, 6, cap_start=True, cap_end=True)
            ck.finish(m, Pg, Tg, "sail", PAL["brass"] * 0.8, skin, wet=0.3, cavity=0.2)
    # reef points: short ties hanging from the reef band
    iu = int(round(0.42 * (NU - 1)))
    for k in range(2, NV - 2, 2):
        c = grid[iu, k]
        if rot[iu * NV + k] > 0.2:
            continue
        ln = rng.uniform(0.1, 0.18)
        path = np.array([c, c + np.array([0.0, -ln * 0.5, 0.0]) + rng.normal(0, 0.01, 3), c + np.array([0, -ln, 0])
                         + rng.normal(0, 0.02, 3)])
        rope(m, path, 0.007, skin, tar=0.2, salt=0.4, hue=0.5, segs=3)
    # lashings gathering the head of the sail at the hub
    for k in range(2):
        th = np.linspace(0, 2 * math.pi, 10)
        c, t, v = body_at(0.06 + 0.05 * k)
        r = float(envelope(0.06 + 0.05 * k)) * (1.45 * 0.55 + 0.1) + 0.07
        pts = c + r * (np.outer(np.cos(th), X_AX * 1.1) + np.outer(np.sin(th), v)) + t * 0.02 * np.sin(th * 2)[:, None]
        rope(m, pts, 0.014, skin, tar=0.85, salt=0.2, segs=4)
    return m


def sheath_mesh(rig: ck.Rig, j: np.ndarray) -> ck.Mesh:
    """The sea hauled up its lines: a streaked skin of water over the body (the head stays bare)."""
    m = ck.Mesh("Sheath")
    skin = rig.chain([f"body{i}" for i in range(N_BODY)], j)
    n, segs = 30, 12
    s_r = np.interp(np.linspace(0, 1, n) ** 0.9, [0, 1], [0.05, LENGTH * 0.94])
    phi = np.arange(segs) * 2 * math.pi / segs
    rings = []
    for s in s_r:
        c, t, v = body_at(float(s))
        pr, kk, qq, mm = plate_profile(np.array([s]))
        sx, sy, _fl = section(phi, kk[0], qq[0], 1.0)
        r = float(envelope(s)) * float(pr[0]) * 1.09 + 0.012
        rings.append(c + r * (np.outer(sx, X_AX) + np.outer(sy, v)))
    P, T = loft(rings, cap_start=body_at(0.0)[0] + np.array([0, 0.05, 0]),
                centres=[body_at(float(s))[0] for s in s_r])
    P = P + (0.02 * ck.fbm(P * 4.0, SEED + 32))[:, None]
    run = ck.smoothstep(0.6, 0.95, np.abs(np.sin(P[:, 1] * 9.0 + ck.fbm(P * 2.0, SEED + 33) * 3.0)))
    col = ck.mix(PAL["deep_teal_shadow"], PAL["storm_slate"], (0.5 * ck.fbm(P * 1.5, SEED + 35) + 0.5)[:, None])
    col = ck.mix(col, PAL["foam_white"] * 0.8, (0.7 * run)[:, None])
    ck.finish(m, P, T, "water", col, skin, wet=1.0)
    return m


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
BODIES = [f"body{i}" for i in range(N_BODY)]
LOWER = BODIES[1:]


def frame_times(length: float) -> list[float]:
    return [min(f / ck.FPS, length) for f in range(int(round(length * ck.FPS)) + 1)]


def rows(c: ck.Clip, bone: str, table) -> None:
    """Keys `bone` from (t, rot) or (t, rot, loc) rows."""
    for r in table:
        c.key(bone, r[0], r[1], r[2] if len(r) > 2 else (0.0, 0.0, 0.0))


def lower_rows(c: ck.Clip, table, scale=(1.0, 1.0, 1.0, 1.0)) -> None:
    """Keys body1..4 from (t, rot) rows, each segment's turn scaled (a bend shared down the body)."""
    for b, s in zip(LOWER, scale):
        for t, r in table:
            c.key(b, t, tuple(s * v for v in r))


def spar_lean(side: float, rx: float, rz: float) -> tuple[tuple, tuple]:
    """(rot, loc) turning a planted spar about its foot, so the foot stays put on the deck while the spar creaks.
    rz > 0 leans the top toward -X; rx > 0 leans it toward the party."""
    top, foot = spar_ends(side)
    d = foot - top
    return (rx, 0.0, rz), tuple(d - ck.euler(rx, 0.0, rz) @ d)


def lean_rows(c: ck.Clip, side: float, table) -> None:
    """Keys a planted spar's creak from (t, rx, rz) rows (degrees about its foot)."""
    tag = "l" if side > 0 else "r"
    for t, rx, rz in table:
        rot, loc = spar_lean(side, rx, rz)
        c.key(f"spar_{tag}", t, rot, loc)


def follow_sail(c: ck.Clip, drag: float = 0.0, lag: float = 0.12) -> ck.Clip:
    """Keys `sail` (the shroud's lower half) at every frame: body2's turn, half of body3's and a quarter of body4's
    (the body it hangs round), plus whatever the clip keyed on `sail` (a flare or a haul), plus `drag`: it trails
    body0's swing by `lag` seconds. The drag fades out over the last 0.2 s, so a clip still ends on its pose."""
    own = ck.Clip("_sail", c.length)
    own.keys["sail"] = c.keys.pop("sail", [])
    for t in frame_times(c.length):
        r = c.sample("body2", t)[0] + 0.5 * c.sample("body3", t)[0] + 0.25 * c.sample("body4", t)[0]
        ra, la = own.sample("sail", t)
        if drag:
            w = min(1.0, max(c.length - t, 0.0) / 0.2)
            r = r + drag * w * (c.sample("body0", max(t - lag, 0.0))[0] - c.sample("body0", t)[0])
        c.key("sail", t, tuple(r + ra), tuple(la))
    return c


def idle_clip() -> ck.Clip:
    idle = ck.Clip("idle", 3.4, loop=True)
    for i, b in enumerate(BODIES):
        idle.wave(b, amp_rot=(2.5, 0.0, 3.0), cycles=1, phase=-i * 0.5)
    idle.wave("head", amp_rot=(6.0, 8.0, 0.0), cycles=1, phase=-2.5)
    idle.wave("block", amp_rot=(0.0, 0.0, 10.0), cycles=1, phase=-3.0)
    idle.wave("tackle", amp_rot=(4.0, 0.0, 6.0), cycles=1, phase=-3.8)
    # M3-CRE-632: the hub (the web's centre) does not rock: the shrouds it carries are made fast to the deck and the
    # spars planted on it. The body still sways in the web.
    return follow_sail(idle)


# M3-CRB-013: every strike is authored as offsets from the rest pose and played from the phase's idle first frame
# (ck.in_pose), so each clip starts and ends exactly where its idle starts. Times below are seconds.
def spar_stab() -> ck.Clip:
    """Spar Stab (contact 0.8 s): the near spar (-X, toward the camera) tears its foot off the deck and swings it out,
    back and up, high and wide of the frame, while the body coils back in the web and the face lifts to its target
    (0.1-0.58 s, the telegraph); it drives the spar's foot down and across, forward at the party, the body lunging after
    it; it holds, then walks the spar back and plants it. The far spar braces on its foot as the weight comes onto it."""
    c = ck.Clip("attack", 1.6)
    rows(c, "spar_r", ((0.0, (0, 0, 0)), (0.1, (2, 0, -2), (0, 0.04, 0)), (0.42, (14, 0, -20), (0, 0.3, -0.05)),
                       (0.58, (16, 0, -22), (0, 0.34, -0.06)), (0.8, (-24, 0, 7), (0, -0.16, 0.22)),
                       (0.95, (-22, 0, 6), (0, -0.14, 0.2)), (1.2, (-8, 0, 0), (0, 0.16, 0.06)),
                       (1.42, (0, 0, -0.5), (0, 0.04, 0)), (1.6, (0, 0, 0))))
    lean_rows(c, 1.0, ((0.0, 0, 0), (0.45, 0, 1.6), (0.8, 0.6, 1.0), (0.9, 0.8, 2.0), (1.02, 0.3, 1.2),
                       (1.3, 0, 0.3), (1.6, 0, 0)))
    rows(c, "body0", ((0.0, (0, 0, 0)), (0.1, (2, 0, -1), (0, 0.02, -0.01)), (0.42, (14, 0, -7), (0, 0.12, -0.08)),
                      (0.58, (16, 0, -8), (0, 0.13, -0.09)), (0.8, (-14, 0, 4), (0, 0.04, 0.12)),
                      (0.95, (-12, 0, 3), (0, 0.03, 0.1)), (1.25, (4, 0, -1), (0, 0.02, 0)), (1.6, (0, 0, 0))))
    lower_rows(c, ((0.0, (0, 0, 0)), (0.42, (3, 0, 0)), (0.58, (3.5, 0, 0)), (0.8, (-4, 0, 0)), (0.95, (-3, 0, 0)),
                   (1.25, (1, 0, 0)), (1.6, (0, 0, 0))))
    rows(c, "head", ((0.0, (0, 0, 0)), (0.1, (-4, -3, 0)), (0.42, (-24, -14, 0)), (0.58, (-26, -15, 0)),
                     (0.8, (14, -6, 0)), (0.95, (12, -5, 0)), (1.25, (-3, 0, 0)), (1.6, (0, 0, 0))))
    rows(c, "block", ((0.0, (0, 0, 0)), (0.5, (0, 0, -8)), (0.85, (0, 0, 18)), (1.1, (0, 0, -10)), (1.4, (0, 0, 4)),
                      (1.6, (0, 0, 0))))
    rows(c, "tackle", ((0.0, (0, 0, 0)), (0.5, (10, 0, -15)), (0.85, (-20, 0, 28)), (1.1, (8, 0, -14)),
                       (1.4, (0, 0, 5)), (1.6, (0, 0, 0))))
    return follow_sail(c, drag=0.7)


def shroud_sweep() -> ck.Clip:
    """Shroud Sweep (contact 1.0 s): it draws back and twists to one side in the web (0.35-0.62 s), then swings
    the whole body out over the party on its lines in a wide arc, the shroud flaring and trailing behind it, the
    face leading; it swings back and settles."""
    c = ck.Clip("shroud_sweep", 1.9)
    rows(c, "body0", ((0.0, (0, 0, 0)), (0.35, (10, 22, -5), (0, 0.06, -0.05)), (0.62, (-6, 36, -8), (0, 0.14, 0.02)),
                      (0.85, (-28, 18, -4), (0, 0.2, 0.1)), (1.0, (-33, -8, 2), (0, 0.2, 0.12)),
                      (1.18, (-24, -34, 6), (0, 0.16, 0.08)), (1.45, (5, -14, 2), (0, 0.05, -0.02)),
                      (1.7, (-2, 3, 0), (0, 0.01, 0)), (1.9, (0, 0, 0))))
    lower_rows(c, ((0.0, (0, 0, 0)), (0.35, (2, -3, 0)), (0.62, (0, 4, 0)), (0.85, (-4, 6, 0)), (1.0, (-4, 2, 0)),
                   (1.18, (-4, -6, 0)), (1.45, (1, -2, 0)), (1.9, (0, 0, 0))))
    rows(c, "head", ((0.0, (0, 0, 0)), (0.35, (-14, 18, 0)), (0.62, (-18, 24, 0)), (0.85, (4, -6, 0)),
                     (1.0, (10, -22, 0)), (1.18, (6, -26, 0)), (1.45, (-4, -6, 0)), (1.9, (0, 0, 0))))
    rows(c, "block", ((0.0, (0, 0, 0)), (0.62, (0, 0, -14)), (0.95, (0, 0, 22)), (1.25, (0, 0, -12)), (1.6, (0, 0, 4)),
                      (1.9, (0, 0, 0))))
    rows(c, "tackle", ((0.0, (0, 0, 0)), (0.62, (0, 0, -20)), (0.85, (-25, 0, 10)), (1.0, (-10, 0, 32)),
                       (1.2, (15, 0, 0)), (1.3, (6, 0, -16)), (1.6, (0, 0, 6)), (1.9, (0, 0, 0))))
    for side, s in ((1.0, 1.0), (-1.0, -1.0)):  # the frame creaks as the weight swings across it
        lean_rows(c, side, ((0.0, 0, 0), (0.62, 0, 0.6 * s), (0.9, 0.6, -1.0 * s), (1.1, 0.4, 1.2 * s),
                            (1.35, 0, -0.4 * s), (1.6, 0, 0), (1.9, 0, 0)))
    return follow_sail(c, drag=0.8, lag=0.14)


def hit_clip(name: str, s: float = 1.0, amp: float = 1.0) -> ck.Clip:
    """It jerks in its lines (peak 0.1 s, where a hit snaps in): the body kicks back and aside, the face snaps up,
    the segments ripple, the tackle swings and the spars shudder on their feet. `s` = -1 recoils to the other side."""
    c = ck.Clip(name, 0.5)
    a = amp
    rows(c, "body0", ((0.0, (0, 0, 0)), (0.1, (13 * a, 0, -16 * s * a), (-0.1 * s * a, 0.12 * a, -0.06 * a)),
                      (0.22, (-6 * a, 0, 7 * s * a), (0.03 * s * a, 0.02 * a, 0.02 * a)),
                      (0.36, (2 * a, 0, -2 * s * a)), (0.5, (0, 0, 0))))
    for i, b in enumerate(LOWER):
        alt = 1.0 if i % 2 else -1.0
        rows(c, b, ((0.0, (0, 0, 0)), (0.1, (3 * a, 0, 7 * alt * s * a)), (0.22, (-1 * a, 0, -4 * alt * s * a)),
                    (0.36, (0, 0, 1 * alt * s * a)), (0.5, (0, 0, 0))))
    rows(c, "head", ((0.0, (0, 0, 0)), (0.1, (-22 * a, 12 * s * a, 0)), (0.22, (8 * a, -5 * s * a, 0)),
                     (0.36, (-2 * a, 1 * s * a, 0)), (0.5, (0, 0, 0))))
    rows(c, "block", ((0.0, (0, 0, 0)), (0.1, (0, 0, 12 * s * a)), (0.25, (0, 0, -6 * s * a)), (0.5, (0, 0, 0))))
    rows(c, "tackle", ((0.0, (0, 0, 0)), (0.1, (0, 0, 30 * s * a)), (0.25, (0, 0, -16 * s * a)),
                       (0.4, (0, 0, 5 * s * a)), (0.5, (0, 0, 0))))
    for side in (1.0, -1.0):
        lean_rows(c, side, ((0.0, 0, 0), (0.1, 0.5 * a, 1.2 * s * a), (0.22, -0.2 * a, -0.6 * s * a),
                            (0.36, 0, 0.2 * s * a), (0.5, 0, 0)))
    return follow_sail(c, drag=0.6, lag=0.08)


def cast_clip() -> ck.Clip:
    """The web draws taut and hauls the body up into it, arched, the face thrown back; the spars lean in."""
    c = ck.Clip("cast", 1.6)
    rows(c, "body0", ((0.0, (0, 0, 0)), (0.25, (4, 0, 0), (0, -0.04, 0)), (0.6, (-6, 0, 0), (0, 0.42, 0)),
                      (1.1, (-7, 0, 1), (0, 0.44, 0)), (1.6, (0, 0, 0))))
    lower_rows(c, ((0.0, (0, 0, 0)), (0.25, (3, 0, 0)), (0.6, (-6, 0, 0)), (1.1, (-6, 0, 0)), (1.6, (0, 0, 0))))
    rows(c, "head", ((0.0, (0, 0, 0)), (0.25, (8, 0, 0)), (0.6, (-34, 0, 0)), (1.1, (-32, 6, 0)), (1.6, (0, 0, 0))))
    rows(c, "tackle", ((0.0, (0, 0, 0)), (0.6, (-25, 0, 12)), (0.9, (10, 0, -8)), (1.2, (-4, 0, 3)), (1.6, (0, 0, 0))))
    for side, s in ((1.0, 1.0), (-1.0, -1.0)):
        lean_rows(c, side, ((0.0, 0, 0), (0.6, -0.5, -2.0 * s), (1.1, -0.5, -1.8 * s), (1.6, 0, 0)))
    return follow_sail(c, drag=0.5)


def lines_taut() -> ck.Clip:
    """Lines Taut (a buff, deck stance; the snap at 0.8 s): it gathers low on the deck, then every line snaps taut
    at once and hauls it half up off the planks, arched, the face thrown back; it hangs there trembling while the
    frame groans (the spars lean in on their feet), then the lines ease and it settles."""
    c = ck.Clip("lines_taut_deck", 1.8)
    tremble = [(0.9, 1.5), (1.0, -1.5), (1.1, 1.2), (1.2, -1.2), (1.32, 0.6)]
    rows(c, "body0", [(0.0, (0, 0, 0)), (0.35, (6, 0, 0), (0, 0.0, 0.02)), (0.62, (-4, 0, 0), (0, 0.25, 0)),
                      (0.8, (-12, 0, 0), (0, 0.55, -0.05))]
         + [(t, (-12.5, 0, z), (0, 0.56, -0.05)) for t, z in tremble]
         + [(1.55, (-3, 0, 0), (0, 0.15, 0)), (1.8, (0, 0, 0))])
    lower_rows(c, ((0.0, (0, 0, 0)), (0.35, (5, 0, 0)), (0.8, (-7, 0, 0)), (1.32, (-7, 0, 0)), (1.55, (-1, 0, 0)),
                   (1.8, (0, 0, 0))))
    rows(c, "head", [(0.0, (0, 0, 0)), (0.35, (12, 0, 0)), (0.8, (-32, 0, 0))]
         + [(t, (-30, 1.4 * z, 0)) for t, z in tremble] + [(1.55, (-6, 0, 0)), (1.8, (0, 0, 0))])
    rows(c, "block", ((0.0, (0, 0, 0)), (0.8, (-20, 0, 8)), (1.0, (6, 0, -6)), (1.25, (-4, 0, 3)), (1.8, (0, 0, 0))))
    rows(c, "tackle", ((0.0, (0, 0, 0)), (0.62, (10, 0, 0)), (0.8, (-40, 0, 14)), (1.0, (12, 0, -12)),
                       (1.25, (-8, 0, 5)), (1.55, (3, 0, 0)), (1.8, (0, 0, 0))))
    for side, s in ((1.0, 1.0), (-1.0, -1.0)):
        lean_rows(c, side, [(0.0, 0, 0), (0.62, 0, 0), (0.8, -1.0, -2.0 * s)]
                  + [(t, -1.0, (-2.0 + 0.4 * z) * s) for t, z in tremble] + [(1.6, 0, 0), (1.8, 0, 0)])
    return follow_sail(c, drag=0.5)


def haul() -> ck.Clip:
    """Haul (deck stance; contact 1.1 s, the yank): it rears up and turns its face on a foe (0.25-0.48 s), flings
    its block and hook out at them (0.75 s), holds reaching, then hauls back hard, the body snapping back up the
    deck and the frame groaning back on its feet as the line comes in; it settles."""
    c = ck.Clip("haul_deck", 2.0)
    rows(c, "body0", ((0.0, (0, 0, 0)), (0.25, (6, -8, 0), (0, 0.18, -0.04)), (0.48, (10, -14, 0), (0, 0.36, -0.08)),
                      (0.75, (-16, -6, 12), (0, 0.26, 0.18)), (0.92, (-17, -5, 13), (0, 0.24, 0.2)),
                      (1.1, (18, 8, -16), (0, 0.2, -0.16)), (1.35, (12, 5, -11), (0, 0.12, -0.1)),
                      (1.7, (-2, 0, 0), (0, 0.02, 0)), (2.0, (0, 0, 0))))
    lower_rows(c, ((0.0, (0, 0, 0)), (0.48, (4, 0, 0)), (0.75, (-5, 0, 0)), (0.92, (-5, 0, 0)), (1.1, (7, 0, 0)),
                   (1.35, (4, 0, 0)), (1.7, (0, 0, 0)), (2.0, (0, 0, 0))))
    rows(c, "head", ((0.0, (0, 0, 0)), (0.25, (-12, -10, 0)), (0.48, (-26, -16, 0)), (0.75, (14, -8, 0)),
                     (0.92, (12, -8, 0)), (1.1, (-22, 14, 0)), (1.35, (-14, 8, 0)), (1.7, (-2, 0, 0)),
                     (2.0, (0, 0, 0))))
    rows(c, "block", ((0.0, (0, 0, 0)), (0.45, (25, 0, 0)), (0.75, (-40, 0, 6)), (0.92, (-45, 0, 6)),
                      (1.12, (-5, 0, -2)), (1.35, (18, 0, -3)), (1.6, (-4, 0, 0)), (2.0, (0, 0, 0))))
    rows(c, "tackle", ((0.0, (0, 0, 0)), (0.45, (35, 0, 0)), (0.78, (-75, 0, 8)), (0.92, (-85, 0, 8)),
                       (1.12, (-15, 0, -6)), (1.35, (35, 0, -6)), (1.62, (-12, 0, 2)), (1.85, (3, 0, 0)),
                       (2.0, (0, 0, 0))))
    for side in (1.0, -1.0):
        lean_rows(c, side, ((0.0, 0, 0), (0.75, 0.6, 0), (1.1, -2.0, 0), (1.22, -1.2, 0), (1.35, -1.8, 0),
                            (1.7, -0.2, 0), (2.0, 0, 0)))
    return follow_sail(c, drag=0.5)


def sea_lash() -> ck.Clip:
    """Sea Lash (deck stance; contact 1.0 s): it rises and coils its sheathed body to one side (0.3-0.58 s), then
    lashes it out across the whole party like a whip, the body first and the head cracking last; it recoils."""
    c = ck.Clip("sea_lash_deck", 1.9)
    rows(c, "body0", ((0.0, (0, 0, 0)), (0.3, (4, 18, -4), (0, 0.2, 0)), (0.58, (6, 32, -8), (0, 0.32, -0.04)),
                      (0.8, (-8, 8, 2), (0, 0.3, 0.06)), (1.0, (-14, -30, 10), (0, 0.25, 0.12)),
                      (1.2, (-8, -36, 8), (0, 0.16, 0.06)), (1.5, (2, -8, 1), (0, 0.04, 0)), (1.9, (0, 0, 0))))
    for i, b in enumerate(LOWER):  # the lash runs down the body: each segment a little later than the one above
        d = 0.04 * i
        rows(c, b, ((0.0, (0, 0, 0)), (0.3, (0, 4, -2)), (0.58, (2, 6, -3)), (0.8 + d, (-2, 10, 2)),
                    (1.0 + d, (-3, -6, 3)), (1.12 + d, (-2, -10, 2)), (1.45, (0, -2, 0)), (1.9, (0, 0, 0))))
    rows(c, "head", ((0.0, (0, 0, 0)), (0.3, (-10, 20, 0)), (0.58, (-18, 28, 0)), (0.8, (-6, 14, 0)),
                     (1.0, (16, -30, 0)), (1.2, (8, -24, 0)), (1.5, (-2, -4, 0)), (1.9, (0, 0, 0))))
    rows(c, "block", ((0.0, (0, 0, 0)), (0.58, (0, 0, -12)), (1.0, (0, 0, 20)), (1.3, (0, 0, -8)), (1.9, (0, 0, 0))))
    rows(c, "tackle", ((0.0, (0, 0, 0)), (0.58, (0, 0, -30)), (1.0, (-15, 0, 45)), (1.3, (6, 0, -20)), (1.6, (0, 0, 8)),
                       (1.9, (0, 0, 0))))
    for side, s in ((1.0, 1.0), (-1.0, -1.0)):
        lean_rows(c, side, ((0.0, 0, 0), (0.58, 0, -0.6 * s), (1.0, 0.8, 1.2 * s), (1.15, 0.3, -0.6 * s),
                            (1.4, 0, 0.2 * s), (1.9, 0, 0)))
    return follow_sail(c, drag=0.7)


def deck_pose(c: ck.Clip, t: float, d: float) -> None:
    """`hauled_down` (m2-slice act1_ch04 §5): the body dropped out of the web onto the deck (the spars stay
    planted)."""
    c.key("body0", t, (8.0 * d, 0, 0), (0, -1.05 * d, 0.25 * d))
    for i, b in enumerate(LOWER, 1):
        c.key(b, t, (12.0 * d * (1 if i % 2 else -0.5), 0, 0))
    c.key("head", t, (-10.0 * d, 0, 0))


# On the deck the block and its hook ride up against the body instead of lying on the planks (so the hook's floor
# correction rarely has to act, and never flips from frame to frame)
DECK_GEAR = {"block": (-35.0, 0.0, 0.0), "tackle": (-40.0, 0.0, 0.0)}


def phase_drop() -> ck.Clip:
    """`hauled_down` (1.8 s): every line snaps at once (0.2 s): it jerks up in the web and the frame jolts; it hangs
    a beat, thrashing; then it is hauled down out of the web and slams onto the deck (0.82 s), the shroud billowing
    up round it as it falls and slumping onto the planks after; it bounces and settles on the deck, face up. The
    shroud goes as it ends (creatures.json `hide_after`), as the sea comes up its lines (`show_after` Sheath)."""
    c = ck.Clip("phase_drop", 1.8)
    for t, d in ((0.0, 0.0), (0.2, -0.18), (0.42, -0.12), (0.62, 0.22), (0.72, 0.62), (0.82, 1.1), (0.95, 0.9),
                 (1.15, 1.03), (1.4, 0.98), (1.8, 1.0)):
        deck_pose(c, t, d)
    extra = {0.2: ((-10, 0, 0), (-26, 0, 0)), 0.42: ((0, 0, 6), (-18, 12, 0)), 0.82: ((4, 0, -3), (12, 0, 0)),
             0.95: ((-3, 0, 2), (-14, -6, 0))}  # body0 and head on top of the drop: the jerk, the thrash, the slam
    for b, k in (("body0", 0), ("head", 1)):
        ks = c.keys[b]
        c.keys[b] = [(t, tuple(np.add(r, extra[t][k] if t in extra else (0, 0, 0))), l) for t, r, l in ks]
    rows(c, "block", ((0.0, (0, 0, 0)), (0.2, (0, 0, 30)), (0.42, (0, 0, -24)), (0.82, (-20, 0, 36)),
                      (1.0, (-40, 0, -16)), (1.3, (-34, 0, 6)), (1.8, DECK_GEAR["block"])))
    rows(c, "tackle", ((0.0, (0, 0, 0)), (0.2, (-30, 0, 20)), (0.42, (20, 0, -30)), (0.72, (-55, 0, 10)),
                       (0.95, (-20, 0, 22)), (1.2, (-48, 0, -8)), (1.5, (-38, 0, 2)), (1.8, DECK_GEAR["tackle"])))
    # the shroud: it billows up as the body falls out from under it, then slumps onto the deck
    rows(c, "sail", ((0.0, (0, 0, 0)), (0.2, (-8, 0, 0)), (0.42, (6, 0, 4)), (0.72, (40, 0, -6)), (0.85, (55, 0, 0)),
                     (1.1, (20, 0, 4)), (1.4, (0, 0, 0)), (1.8, (0, 0, 0))))
    for side in (1.0, -1.0):  # the frame jolts as the lines part, and again as the deck takes the weight
        lean_rows(c, side, ((0.0, 0, 0), (0.2, 1.2, 1.2 * side), (0.32, -0.6, -0.6 * side), (0.5, 0, 0),
                            (0.82, -0.8, 0), (0.92, 0.6, 0), (1.05, -0.2, 0), (1.3, 0, 0), (1.8, 0, 0)))
    return follow_sail(c)


def ko_clip() -> ck.Clip:
    """The lines part and it drops to the deck; the spars fall outward."""
    ko = ck.Clip("ko", 2.2)
    for t, d in ((0.0, 0.0), (0.5, 0.15), (1.1, 1.0), (1.5, 1.05), (2.2, 1.05)):
        ko.key("body0", t, (10.0 * d, 0, 0), (0, -1.6 * d, 0.2 * d))
        for i, b in enumerate(LOWER, 1):
            ko.key(b, t, (18.0 * d * (1 if i % 2 else -0.6), 0, 6.0 * d))
        ko.key("head", t, (30.0 * d, 0, 0))
        ko.key("spar_l", t, (0, 0, 22.0 * d))
        ko.key("spar_r", t, (0, 0, -22.0 * d))
    return follow_sail(ko, drag=0.6)


def ko_deck_clip() -> ck.Clip:
    """The KO from the deck (`hauled_down` maps `ko` to it): the last lines part with a jerk (0.4 s), the body slumps
    flat along the planks and the face goes down; the spars fall outward. Played from the deck pose."""
    c = ck.Clip("ko_deck", 2.2)
    for t, d, jerk in ((0.0, 0.0, 0.0), (0.4, 0.08, 1.0), (1.05, 1.0, 0.0), (1.4, 1.03, 0.0), (2.2, 1.03, 0.0)):
        c.key("body0", t, (2.5 * d - 4.0 * jerk, 0, 0), (0, -0.63 * d + 0.1 * jerk, -0.04 * d))
        for i, b in enumerate(LOWER, 1):
            c.key(b, t, ((6.9 if i % 2 else -3.6) * d, 0, 6.0 * d))
        c.key("head", t, (40.0 * d - 12.0 * jerk, 0, 0))
        c.key("spar_l", t, (0, 0, 22.0 * d))
        c.key("spar_r", t, (0, 0, -22.0 * d))
    return follow_sail(c, drag=0.6)


def build_clips() -> list[ck.Clip]:
    idle = idle_clip()
    idle0 = {b: tuple(np.asarray(v, float) for v in idle.sample(b, 0.0)) for b in idle.keys}

    def from_idle(c: ck.Clip, name: str | None = None, pose: dict | None = None) -> ck.Clip:
        base = dict(idle0)
        for b, (r, l) in (pose or {}).items():
            r0, l0 = base.get(b, (np.zeros(3), np.zeros(3)))
            base[b] = (r0 + r, l0 + l)
        return ck.in_pose(c, name or c.name, base)

    # ready: drawn up into the web, the body tense and twitching, the head raised toward the party; a loop
    ready = ck.Clip("ready", 2.0, loop=True)
    ready.wave("body0", amp_rot=(0.8, 0.0, 0.0), amp_loc=(0.0, 0.02, 0.0), cycles=2, base_loc=(0.0, 0.09, 0.0))
    for i, b in enumerate(LOWER, 1):
        ready.wave(b, amp_rot=(1.5, 0.0, 2.0), cycles=2, phase=-i * 0.6, base_rot=(-4.0, 0.0, 0.0))
    ready.wave("head", amp_rot=(3.0, 10.0, 0.0), cycles=2, phase=-1.5, base_rot=(-14.0, 0.0, 0.0))
    ready.wave("block", amp_rot=(0.0, 0.0, 6.0), cycles=2, phase=-2.0)
    ready.wave("tackle", amp_rot=(3.0, 0.0, 5.0), cycles=2, phase=-2.6)
    follow_sail(ready)

    # intro: it unfolds in the web. Curled low and slack with the spars lifted, the spars come down and plant, the
    # lines snap taut and haul it up, it uncurls segment by segment and lifts its head to the party, then settles.
    intro = ck.Clip("intro", 2.8)
    keys = ((0.0, 1.0, 0.0, 0.0), (0.45, 0.95, 0.15, 0.0), (0.75, 0.85, 1.0, 0.0), (1.0, 0.25, 1.0, 0.6),
            (1.25, -0.12, 1.0, 1.0), (1.6, 0.0, 1.0, 1.0), (2.1, 0.0, 1.0, 0.85))
    for t, slack, plant, rear in keys:
        intro.key("body0", t, (6.0 * slack, 0.0, 0.0), (0.0, -0.38 * slack + 0.08 * rear, 0.05 * slack))
        for i, b in enumerate(LOWER, 1):
            curl = 16.0 * slack * (1 if i % 2 else -0.7)
            intro.key(b, t, (curl - 3.0 * rear, 2.0 * math.sin(t * 7.0 + i) * slack, 0.0))
        intro.key("head", t, (34.0 * slack - 24.0 * rear, 12.0 * math.sin(t * 4.0) * rear, 0.0))
        intro.key("spar_l", t, (0.0, 0.0, 14.0 * (1 - plant)))
        intro.key("spar_r", t, (0.0, 0.0, -14.0 * (1 - plant)))
        intro.key("block", t, (0.0, 0.0, 25.0 * slack * math.sin(t * 6.0)))
        intro.key("tackle", t, (0.0, 0.0, 18.0 * slack * math.sin(t * 6.0 + 1.0)))
    for b in [k for k in idle.keys if k != "sail"] + ["spar_l", "spar_r"]:  # end on idle's first frame
        r, loc = idle.sample(b, 0.0)
        intro.key(b, 2.8, tuple(r), tuple(loc))
    follow_sail(intro, drag=0.5)

    deck = ck.pose_of(lambda c: deck_pose(c, 0.0, 1.0))
    deck.update({b: (np.asarray(r, float), np.zeros(3)) for b, r in DECK_GEAR.items()})
    deck_sail = ck.Clip("_deck", 1.0)
    for b, (r, l) in deck.items():
        deck_sail.key(b, 0.0, tuple(r), tuple(l))
    deck["sail"] = tuple(np.asarray(v, float) for v in follow_sail(deck_sail).sample("sail", 0.0))
    idle_deck = ck.in_pose(idle, "idle_deck", deck)

    cast = cast_clip()
    hit = hit_clip("hit")
    stab = spar_stab()
    out = [idle, ready, intro, from_idle(stab), from_idle(shroud_sweep()), from_idle(cast), from_idle(hit),
           from_idle(hit_clip("hit_b", -1.0, 1.35)), from_idle(ck.varied(cast, "idle_b", **ck.IDLE_B)),
           from_idle(ko_clip()), from_idle(phase_drop()), idle_deck]
    out += [from_idle(c, f"{c.name}_deck", deck) for c in (stab, cast, hit)]
    out += [from_idle(c, pose=deck) for c in (lines_taut(), haul(), sea_lash(), ko_deck_clip())]
    return out


# Kept off the floor (M3-CRE-632, common/grounding.py): where the body drops to the deck (the KO, `phase_drop` and the
# deck clips) the shroud's hem turns back onto the planks, the tackle swings aside, the head turns up and the body
# lifts the least it takes to lie on the deck; the shroud and sheath are measured with it. The intro's slack start is
# measured the same way.
DECK_CLIPS = ("ko", "phase_drop", "idle_deck", "attack_deck", "cast_deck", "hit_deck", "lines_taut_deck", "haul_deck",
              "sea_lash_deck", "ko_deck", "intro")
GROUNDED_LIMBS = [("sail", 0, 1.0, 90.0, DECK_CLIPS), ("tackle", 0, -1.0, 80.0, DECK_CLIPS),
                  ("head", 0, -1.0, 30.0, DECK_CLIPS), ("body0", gr.LIFT, 1.0, 1.6, DECK_CLIPS)]


def export_clips(rig: ck.Rig, meshes: list[ck.Mesh]) -> list[ck.Clip]:
    return gr.grounded(rig, meshes, build_clips(), GROUNDED_LIMBS)


def build(rig: ck.Rig, j: np.ndarray) -> tuple[ck.Mesh, ck.Mesh, ck.Mesh]:
    mesh = ck.Mesh("spar_wraith")
    spars(mesh, rig)
    yard_stub(mesh, rig)
    bd = body(mesh, rig, j)
    body_spines(mesh, rig, bd)
    limbs(mesh, rig)
    head(mesh, rig, j)
    rigging(mesh, rig, j)
    block_and_tackle(mesh, rig, j)
    return mesh, shroud_mesh(rig, j), sheath_mesh(rig, j)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, j = build_rig()
    mesh, shroud, sheath = build(rig, j)
    info = ck.export_creature(mesh, rig, export_clips(rig, [mesh, shroud, sheath]), args.out,
                              extra_meshes=[shroud, sheath], extras={"hymn_creature": "spar_wraith"})
    print(f"spar_wraith: {info} (body {mesh.triangle_count}, shroud {shroud.triangle_count}, "
          f"sheath {sheath.triangle_count})")


if __name__ == "__main__":
    main()
