"""Helper bones for deep poses (M1-CHR-15): skirt panels and shoulder correctives, and the weights that use them.

Pure numpy (Blender's build space: +X the hero's left, -Y the way she faces, +Z up); build_asha.add_bones puts the
bones on the game skeleton. No pose names these bones: hero_clips.py keys them in every clip from the pose itself
(hero_clips.helper_pose), so they are a deterministic drape baked into the clips.

* **Skirt panels** (`DEF-skirt_<k>`, `DEF-skirt_<k>.001`, `DEF-skirt_<k>.002`, k = 0..SKIRT_SECTORS-1 round from
  the front, to her left): each sector of a floor-length skirt is a three-bone chain hanging from the hips, pivoting
  at the hip joints' height on the outer skirt (hips -> mid-thigh, mid-thigh -> just below the knees, then on to the
  hem; M2-CHR-522 split the old lower bone at the knee). The clips swing each bone out just far enough that the legs
  stay inside the cloth, so the bone below the knee hangs back towards the vertical from wherever the knee pushed
  the cloth: the skirt drapes from the knee instead of standing out as a rigid bell. Skirt cloth below the pivot
  rides the two nearest sectors' chains instead of the legs: each panel moves rigidly, so nothing stretches between
  the knees and the under-layer cannot twist.
* **Shoulder correctives** (`DEF-armpit.L` / `.R`): a copy of the upper arm (same head, tail and roll, parented to
  the shoulder) that turns hero_clips.ARMPIT_SHARE of the upper arm's own turn. The underarm skin next to the torso
  takes part of its upper-arm weight onto it, and the torso cloth's armhole edge takes the same share where it lies
  over that skin, so the two move together when the arms come down instead of the arm's inner skin sliding out
  through the bodice.
"""
from __future__ import annotations

import math

import numpy as np

SECTOR_EDGE_TOL = 1e-6  # rad: skirt_bone_specs' sector edge tolerance
SKIRT_SECTORS = 16  # big14's review (the skirt as cloth): 8 panels were too coarse to fold; 16 halve each panel
SKIRT_BONE = "DEF-skirt_"
ARMPIT_BONE = "DEF-armpit."
# skirt weights (m at s = 1): the band above the pivot over which the cloth hands over from the hips to the panels,
# the band about the panels' first joint over which the upper bone hands over to the middle one, and (M2-CHR-522) the
# band about the second joint (below the knee) over which the middle bone hands over to the lowest
SKIRT_TOP_BAND = 0.05
SKIRT_KNEE_BAND = 0.16  # big17 review: 0.06 bent the cloth in a crease at the joint (a faceted plank)
SKIRT_SHIN_BAND = 0.18  # and 0.08 here: the bend now spreads over the shin like cloth
SKIRT_PIVOT_ABOVE_HIP = 0.09  # m (at s = 1): the panels pivot this far above the hip joints (over a raised thigh)
SKIRT_HUG_NEAR = 0.012  # m (at s = 1): skirt cloth this near a leg's skin at rest follows that leg
SKIRT_HUG_FAR = 0.035  # m: and from this far on it rides the panels
SKIRT_SPLIT = 0.7  # the upper panel bone runs this much of the way from the pivot down to the knees' height
SKIRT_SHIN_SPLIT = 0.1  # M2-CHR-522: the lowest bone starts this much of the way from the knees' height to the hem
SKIRT_PIVOT_SLICE = 0.03  # m: the skirt ring this near the pivot height sets each panel's pivot radius
# armpit weights: along the upper arm (fraction of its length from the shoulder joint), the share of the upper-arm
# weight moved to the corrective falls from ARMPIT_MAX at ARMPIT_T0 to 0 at ARMPIT_T1; round the arm it is full on
# the underside (towards the torso) and fades out over the top
ARMPIT_MAX = 1.0
ARMPIT_T0 = 0.3
ARMPIT_T1 = 0.65
ARMPIT_TSTART = (0.03, 0.13)  # and it fades in over these fractions, clear of the chest and shoulder at the joint
ARMPIT_UNDER = (-0.35, 0.35)  # cos to the arm's up: the share is full below the first, none above the second
HANG_MAX = 0.75
HANG_FROM = 0.04  # m (at s = 1)
HANG_RAMP = 0.15  # m
ARMPIT_CLOTH_REACH = 0.02  # m: a cloth vertex this near underarm skin takes that skin's weights
ARMPIT_CLOTH_FULL = 0.3  # the skin's corrective share at which the cloth over it takes ARMPIT_CLOTH_MIX of the skin's weights
ARMPIT_CLOTH_MIX = 0.0


def smooth01(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def skirt_names() -> list[str]:
    out = []
    for k in range(SKIRT_SECTORS):
        out += [f"{SKIRT_BONE}{k}", f"{SKIRT_BONE}{k}.001", f"{SKIRT_BONE}{k}.002"]
    return out


def armpit_names() -> list[str]:
    return [f"{ARMPIT_BONE}L", f"{ARMPIT_BONE}R"]


def _azimuth(P: np.ndarray, centre: np.ndarray) -> np.ndarray:
    """Radians round the vertical through `centre`: 0 at the front (-Y), +pi/2 at her left (+X)."""
    return np.arctan2(P[:, 0] - centre[0], -(P[:, 1] - centre[1]))


def skirt_bone_specs(P_outer: np.ndarray, centre: np.ndarray, z_pivot: float, z_knee: float, z_hem: float,
                     parent: str) -> list:
    """(name, head, tail, parent) of the panel chains: each pivots on the outer skirt at the pivot height in its
    sector's direction; the upper bone hangs straight down SKIRT_SPLIT of the way to the knees' height (raised
    forward, it ends at the knee), the middle one on to SKIRT_SHIN_SPLIT of the way from the knees to the hem (the
    knee's contact with the cloth), the lowest one on to the hem."""
    near = np.abs(P_outer[:, 2] - z_pivot) < SKIRT_PIVOT_SLICE
    az = _azimuth(P_outer[near], centre)
    rad = np.linalg.norm(P_outer[near, :2] - centre[:2], axis=1)
    specs = []
    for k in range(SKIRT_SECTORS):
        phi = 2.0 * math.pi * k / SKIRT_SECTORS
        d = np.abs((az - phi + math.pi) % (2.0 * math.pi) - math.pi)
        # a ring column on a sector's edge counts for both sides: with 64 columns over 16 sectors every fourth one lies
        # exactly on an edge, and a strict test picked a side by the angle's last bit (host determinism, M2-CHR-11)
        r0 = float(rad[d < math.pi / SKIRT_SECTORS + SECTOR_EDGE_TOL].max())
        u = np.array([math.sin(phi), -math.cos(phi), 0.0])
        top = np.array([centre[0], centre[1], z_pivot]) + u * r0
        knee = np.array([top[0], top[1], z_pivot + (z_knee - z_pivot) * SKIRT_SPLIT])
        shin = np.array([top[0], top[1], z_shin_split(z_knee, z_hem)])
        hem = np.array([top[0], top[1], z_hem])
        a, b, c = f"{SKIRT_BONE}{k}", f"{SKIRT_BONE}{k}.001", f"{SKIRT_BONE}{k}.002"
        specs += [(a, top, knee, parent), (b, knee, shin, a), (c, shin, hem, b)]
    return specs


def z_shin_split(z_knee: float, z_hem: float) -> float:
    """Height of the panels' second joint (the lowest bone's head): SKIRT_SHIN_SPLIT of the way from the knees down
    to the hem."""
    return z_knee + (z_hem - z_knee) * SKIRT_SHIN_SPLIT


def skirt_weights(P: np.ndarray, W0: np.ndarray, names: list[str], centre: np.ndarray, z_pivot: float,
                  z_knee: float, z_hem: float, S: float, W_legs: np.ndarray, d_leg: np.ndarray) -> np.ndarray:
    """Skirt cloth below the pivot on the two nearest sectors' chains (the upper bone above the panels' first joint,
    the middle one between the joints, the lowest below the second joint, blended over SKIRT_KNEE_BAND and
    SKIRT_SHIN_BAND); above it the hips' weights W0, handed over across SKIRT_TOP_BAND.
    Cloth that hugs a leg at rest (within SKIRT_HUG_NEAR of its skin, d_leg) keeps that leg's weights W_legs instead,
    fading to the panels by SKIRT_HUG_FAR: it stays over the leg (and over the cut edge of the hidden thigh), while
    the cloth that spans between the legs and the flared outer skirt ride the panels."""
    z_joint = z_pivot + (z_knee - z_pivot) * SKIRT_SPLIT  # the panel bones' joint
    n = SKIRT_SECTORS
    s = (_azimuth(P, centre) / (2.0 * math.pi) * n) % n
    k0 = np.floor(s).astype(int) % n
    f = s - np.floor(s)
    z_shin = z_shin_split(z_knee, z_hem)  # the second joint
    lower = smooth01((z_joint + 0.5 * SKIRT_KNEE_BAND * S - P[:, 2]) / (SKIRT_KNEE_BAND * S))
    shin = smooth01((z_shin + 0.5 * SKIRT_SHIN_BAND * S - P[:, 2]) / (SKIRT_SHIN_BAND * S))
    panel = smooth01((z_pivot + SKIRT_TOP_BAND * S - P[:, 2]) / (SKIRT_TOP_BAND * S))
    hug = smooth01((SKIRT_HUG_FAR * S - d_leg) / ((SKIRT_HUG_FAR - SKIRT_HUG_NEAR) * S))
    W = np.zeros((len(P), len(names)), dtype=np.float64)
    rows = np.arange(len(P))
    for kk, wk in ((k0, 1.0 - f), ((k0 + 1) % n, f)):
        up = np.array([names.index(f"{SKIRT_BONE}{k}") for k in range(n)])[kk]
        mid = np.array([names.index(f"{SKIRT_BONE}{k}.001") for k in range(n)])[kk]
        lo = np.array([names.index(f"{SKIRT_BONE}{k}.002") for k in range(n)])[kk]
        np.add.at(W, (rows, up), wk * (1.0 - lower))
        np.add.at(W, (rows, mid), wk * lower * (1.0 - shin))
        np.add.at(W, (rows, lo), wk * lower * shin)
    W = W * (1.0 - hug)[:, None] + W_legs.astype(np.float64) * hug[:, None]
    out = W0.astype(np.float64) * (1.0 - panel)[:, None] + W * panel[:, None]
    return _limit4(out).astype(np.float32)


def armpit_share(P: np.ndarray, head: np.ndarray, tail: np.ndarray, side_x: float) -> np.ndarray:
    """(n,) fraction of the upper-arm weight a skin vertex moves onto its side's corrective."""
    d = tail - head
    L = float(np.linalg.norm(d))
    d = d / L
    up = np.array([0.0, 0.0, 1.0]) - d * d[2]
    up /= np.linalg.norm(up)
    rel = P - head
    t = rel @ d / L
    radial = rel - np.outer(rel @ d, d)
    rn = radial / np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
    under = smooth01((ARMPIT_UNDER[1] - rn @ up) / (ARMPIT_UNDER[1] - ARMPIT_UNDER[0]))  # 1 on the underside
    along = smooth01((ARMPIT_T1 - t) / (ARMPIT_T1 - ARMPIT_T0))
    near_side = np.sign(P[:, 0]) == np.sign(side_x)
    start = smooth01((t - ARMPIT_TSTART[0]) / (ARMPIT_TSTART[1] - ARMPIT_TSTART[0]))  # not the chest at the joint
    return ARMPIT_MAX * along * under * start * near_side


def armpit_skin_weights(P: np.ndarray, W: np.ndarray, names: list[str], arms: dict) -> tuple[np.ndarray, np.ndarray]:
    """Moves part of each skin vertex's upper-arm weight to the corrective. `arms`: side -> (head, tail) of the upper
    arm. Returns the new weights (columns `names`, which hold the correctives) and each vertex's moved share of its
    total weight (for the cloth over it)."""
    W64 = W.astype(np.float64)
    moved = np.zeros(len(P))
    for side, (head, tail) in arms.items():
        ua = names.index(f"DEF-upper_arm.{side}")
        h = names.index(f"{ARMPIT_BONE}{side}")
        share = armpit_share(P, head, tail, head[0]) * W64[:, ua]
        share = np.where(share > 1e-4, share, 0.0)
        W64[:, h] += share
        W64[:, ua] -= share
        moved += share
    out = W.copy()
    rows = moved > 0.0  # the other rows keep their exact weights
    out[rows] = _limit4(W64[rows]).astype(np.float32)
    return out, moved


def armpit_cloth_weights(Pc: np.ndarray, Wc: np.ndarray, names: list[str], Ps: np.ndarray, Ws: np.ndarray,
                         arms: dict, S: float) -> np.ndarray:
    """Torso cloth over the underarm: a vertex whose nearest skin vertex rides a corrective takes that skin's weights
    (in proportion to the skin's corrective share, ARMPIT_CLOTH_FULL for all of it), fading back to its own between
    ARMPIT_CLOTH_REACH and 3 cm further, so the cloth and the skin under it turn together."""
    out = Wc.copy()
    Wc = Wc.astype(np.float64)
    touched = np.zeros(len(Pc), dtype=bool)
    r0, r1 = ARMPIT_CLOTH_REACH * S, (ARMPIT_CLOTH_REACH + 0.03) * S
    for side, (head, tail) in arms.items():
        h = names.index(f"{ARMPIT_BONE}{side}")
        zone = 1.2 * float(np.linalg.norm(tail - head))
        near = np.nonzero(np.linalg.norm(Ps - head, axis=1) < zone + r1)[0]
        Q = Ps[near]
        for i in np.nonzero(np.linalg.norm(Pc - head, axis=1) < zone)[0]:
            dd = np.linalg.norm(Q - Pc[i], axis=1)
            j = int(np.argmin(dd))
            share = float(Ws[near[j], h])
            if dd[j] >= r1 or share <= 1e-4:
                continue
            f = float(smooth01(np.array([(r1 - dd[j]) / (r1 - r0)]))[0]) * min(1.0, share / ARMPIT_CLOTH_FULL) * ARMPIT_CLOTH_MIX
            if f <= 1e-4:
                continue
            Wc[i] = Wc[i] * (1.0 - f) + Ws[near[j]] * f
            touched[i] = True
    out[touched] = _limit4(Wc[touched]).astype(np.float32)
    return out


def hanging_weights(P: np.ndarray, W: np.ndarray, names: list[str], head: np.ndarray, wrist: np.ndarray,
                    side: str, S: float) -> np.ndarray:
    """A sheet hanging below an arm (Asha's verse-sleeve bag) moves part of its arm weights onto that side's
    corrective, by how far it hangs below the arm's line at rest (HANG_MAX from HANG_FROM + HANG_RAMP down): when the
    arm comes down, the bag turns with it less and keeps hanging beside the hip instead of swinging into the waist."""
    W64 = W.astype(np.float64)
    d = wrist - head
    t = np.clip((P - head) @ d / float(d @ d), 0.0, 1.0)
    below = (head[2] + t * d[2]) - P[:, 2]
    share = HANG_MAX * smooth01((below - HANG_FROM * S) / (HANG_RAMP * S))
    arm = [names.index(n) for n in names if n.startswith((f"DEF-upper_arm.{side}", f"DEF-forearm.{side}"))]
    h = names.index(f"{ARMPIT_BONE}{side}")
    moved = W64[:, arm] * share[:, None]
    W64[:, arm] -= moved
    W64[:, h] += moved.sum(axis=1)
    out = W.copy()
    rows = share > 1e-4
    out[rows] = _limit4(W64[rows]).astype(np.float32)
    return out


def _limit4(W: np.ndarray) -> np.ndarray:
    if W.shape[1] > 4:
        thr = -np.sort(-W, axis=1)[:, 3:4]
        W = np.where(W >= thr, W, 0.0)
    return W / np.maximum(W.sum(axis=1, keepdims=True), 1e-12)
