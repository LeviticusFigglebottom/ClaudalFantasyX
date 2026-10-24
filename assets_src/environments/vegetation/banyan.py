"""Hero banyan generator (M2-ENV-07): the oldest living thing in Haluna (haluna.md §1.3), the tree
whose aerial roots frame the chapel court in H07 (haluna.md §5.1).

Anatomy, in the order it is grown (every random draw happens here, in this order):
  1. Fused trunk: `stems` twisted stems converging from a ~1.1 m radius at the ground to the crotch at
     5-6 m, round a core column, so the trunk reads as many old roots grown together.
  2. Buttresses: tall, thin flanges between the stems that run down and out to the ground, each
     continuing as a half-buried surface root; more surface roots snake out between them.
  3. Limbs: `limbs` near-horizontal limbs from the crotch, sagging and then curling up at the tips.
     `hero_limbs` fixes some azimuths, reaches and prop-root counts (the two great limbs that reach
     either side of the chapel court); the rest fill the largest gaps around the trunk.
  4. Branches rise from each limb (alternating sides) to leaf clumps; more clumps cap the trunk top.
  5. Each clump is a flattened ellipsoid of twig clusters: branchlets from the branch end, a twig
     to each cluster, and 2-4 leaf sprays per cluster (painted twigs of real-size leaves,
     veg_common.COASTAL_ATLAS). The underside is sparser and darker, so you look up into a crown.
  6. Prop roots: aerial roots that reached the ground and thickened into pillars, one to three
     strands twisted together, flared at the foot and where they leave the limb.
  7. Hanging aerial roots: bunches of thin, braided, tapering strands from the limbs and the lower
     branches; a few long ones reach the ground (the next generation of props).

Asset frame: Blender metres, +Z up, the trunk on the origin. LOD0 is the hero (H07 is about 7 m from
the trunk); LOD1 keeps the silhouette with fewer, larger sprays round opaque clump cores.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

import canopy
import veg_common as vc
from canopy import Limb
from veg_common import UP, MeshBuilder

VARIANTS: dict[str, dict] = {
    "hero": {
        "seed": 91, "height": 14.0, "crown_radius": 12.0, "limbs": 7, "stems": 7, "buttresses": 7,
        "surface_roots": 6,
        # (azimuth deg in the asset frame, reach as a fraction of crown_radius, prop roots on it, start
        # height m, elevation deg, sag m). Placed at yaw 30 in Haluna, 180 and 106 flank the chapel court
        # (asset azimuth ~135); the 180 limb runs low (~4 m) over the court, so it arches across the top
        # of H07 with its root curtains.
        "hero_limbs": ((180.0, 0.9, 3, 4.75, 2.0, 0.5), (106.0, 0.8, 2, 4.8, 4.0, 0.4)),
        "hero_low_clumps": 3,  # small leaf clumps sitting on each hero limb (leaves down to its height)
        "hero_root_share": 0.5,  # share of the hanging-root bunches on the hero limbs
        "foliage_floor_m": 4.0,  # lowest leaf cluster
        "extra_props": 5,
        "root_bunches": 70,
        "cluster_density": 0.75,  # twig clusters per m2 of clump surface
        "branch_spacing_m": (1.5, 2.1),
        "top_clumps": 5,
        # The walk to the chapel door under the tree (a capsule on the ground: end points in the asset
        # frame, half-width m). The village keeps it clear: no prop root stands in it, and hanging roots
        # over it are cut at head height. At yaw 30 in Haluna it runs from the lane past the H07 camera
        # to the chapel front.
        "path": ((-4.2, -7.9), (-9.6, 7.2), 1.6),
        "path_cut_m": 2.4,
    },
}

LODS: list[dict] = [
    {"stem_sides": 12, "limb_sides": 9, "branch_sides": 6, "branchlet_sides": 4, "twig_sides": 3, "root_sides": 4,
     "prop_sides": 8, "flange_sides": 10, "step": 1, "card_rows": 2, "card_keep": 1.0, "card_scale": 1.0,
     "root_keep": 1.0, "twigs": True, "branchlets": True, "surface_roots": True, "cores": False},
    {"stem_sides": 6, "limb_sides": 5, "branch_sides": 4, "branchlet_sides": 0, "twig_sides": 0, "root_sides": 3,
     "prop_sides": 5, "flange_sides": 6, "step": 3, "card_rows": 1, "card_keep": 0.26, "card_scale": 1.75,
     "root_keep": 0.2, "twigs": False, "branchlets": False, "surface_roots": False, "cores": True},
]

TRI_BUDGET = [60000, 10000]

MATERIALS = {"bark": "banyan_bark", "root": "banyan_root", "leaf": "banyan_leaf"}
SPRAYS = ("banyan_spray_a", "banyan_spray_b")


@dataclass
class Clump:
    center: np.ndarray
    radii: np.ndarray
    phase: float
    anchor: np.ndarray  # where its branch ends (branchlets start here)
    g: float  # secondary weight at the anchor
    waves: np.ndarray = field(default_factory=lambda: np.zeros((0, 5)))
    tint: float = 0.5


@dataclass
class Tree:
    height: float
    stems: list = field(default_factory=list)  # Limb
    flanges: list = field(default_factory=list)  # (centers, half_thick, half_high, phase)
    surface: list = field(default_factory=list)  # Limb (LOD0 only)
    limbs: list = field(default_factory=list)  # Limb: primary limbs
    branches: list = field(default_factory=list)  # Limb
    branchlets: list = field(default_factory=list)  # Limb
    twigs: list = field(default_factory=list)  # Limb
    props: list = field(default_factory=list)  # Limb
    roots: list = field(default_factory=list)  # Limb (hanging; keep-filtered per LOD)
    clumps: list = field(default_factory=list)  # Clump
    sprays: list = field(default_factory=list)  # dicts for canopy.mesh_spray (+ "clump", "rect", "keep")


def fill_azimuths(fixed: list[float], n: int, rng: np.random.Generator) -> list[float]:
    """Adds azimuths (radians) into the largest circular gaps until there are n."""
    az = list(fixed)
    while len(az) < n:
        s = sorted(a % (2 * math.pi) for a in az)
        gaps = [((s[(i + 1) % len(s)] - s[i]) % (2 * math.pi)) or 2 * math.pi for i in range(len(s))]
        i = int(np.argmax(gaps))
        az.append(s[i] + gaps[i] * (0.5 + rng.uniform(-0.12, 0.12)))
    return az


def path_distance(xy: np.ndarray, path) -> float:
    """Horizontal distance from xy to the kept-clear walk's centre line, minus its half-width."""
    a, b, hw = np.asarray(path[0], float), np.asarray(path[1], float), float(path[2])
    ab = b - a
    t = float(np.clip(np.dot(xy[:2] - a, ab) / float(np.dot(ab, ab)), 0.0, 1.0))
    return float(np.linalg.norm(xy[:2] - (a + ab * t))) - hw


def _point_on(limb: Limb, s: float) -> tuple[np.ndarray, float]:
    k = np.linspace(0.0, 1.0, len(limb.pts))
    p = np.array([np.interp(s, k, limb.pts[:, i]) for i in range(3)])
    return p, float(np.interp(s, k, limb.radii))


def _surface_root(start: np.ndarray, heading: float, length: float, r0: float, rng) -> Limb:
    m = 7
    pts = [np.array([start[0], start[1], 0.0])]
    h = heading
    for _ in range(m - 1):
        h += rng.normal(0.0, 0.3)
        pts.append(pts[-1] + np.array([math.cos(h), math.sin(h), 0.0]) * length / (m - 1))
    pts = np.array(pts)
    radii = r0 * (1.0 - 0.68 * np.linspace(0.0, 1.0, m))
    pts[:, 2] = -0.35 * radii  # two thirds of each root shows above the sand
    return Limb(pts, radii, 0.0, kind="bark", cap=True, ao0=0.55, ao1=0.7)


def make_tree(p: dict) -> Tree:
    rng = vc.rng_for("banyan", int(p["seed"]))
    H = float(p["height"])
    R = float(p["crown_radius"])
    tree = Tree(height=H)

    # 1. Fused trunk.
    n_st = int(p["stems"])
    for k in range(n_st):
        a0 = 2 * math.pi * k / n_st + rng.uniform(-0.25, 0.25)
        rb = rng.uniform(0.85, 1.25)
        top = rng.uniform(5.0, 6.0)
        twist = rng.uniform(0.5, 1.0)
        r0 = rng.uniform(0.34, 0.5)
        t = np.linspace(0.0, 1.0, 10)
        dist = rb * (1 - t) ** 1.3 + 0.42 * t
        ang = a0 + twist * t
        pts = np.stack([np.cos(ang) * dist, np.sin(ang) * dist, -0.4 + t * (top + 0.4)], axis=-1)
        radii = r0 * (1 + 0.5 * (1 - t) ** 3) * (1 - 0.25 * t)
        tree.stems.append(Limb(pts, radii, 0.0, cap=True, ao0=0.5, ao1=0.8))
    t = np.linspace(0.0, 1.0, 6)
    tree.stems.append(Limb(np.stack([np.zeros(6), np.zeros(6), -0.4 + t * 6.2], axis=-1), 1.05 - 0.38 * t, 0.0,
                           cap=True, ao0=0.45, ao1=0.7))

    # 2. Buttresses and surface roots.
    n_b = int(p["buttresses"])
    for k in range(n_b):
        a = 2 * math.pi * (k + 0.5) / n_b + rng.uniform(-0.2, 0.2)
        zs = rng.uniform(1.3, 2.3)
        dend = rng.uniform(2.3, 3.5)
        wig = rng.uniform(-0.25, 0.25)
        t = np.linspace(0.0, 1.0, 9)
        d = 0.8 + (dend - 0.8) * t
        dv = np.array([math.cos(a), math.sin(a)])
        pv = np.array([-math.sin(a), math.cos(a)])
        xy = dv[None, :] * d[:, None] + pv[None, :] * (wig * np.sin(math.pi * t))[:, None]
        ztop = zs * (1 - t) ** 1.6 + 0.14
        centers = np.column_stack([xy, (ztop - 0.25) * 0.5])
        half_thick = rng.uniform(0.11, 0.17) * (1 - 0.55 * t)
        tree.flanges.append((centers, half_thick, (ztop + 0.25) * 0.5, 0.0))
        tree.surface.append(_surface_root(centers[-1], a + rng.uniform(-0.4, 0.4), rng.uniform(1.5, 4.0),
                                          rng.uniform(0.09, 0.13), rng))
    for _ in range(int(p["surface_roots"])):
        a = rng.uniform(0, 2 * math.pi)
        tree.surface.append(_surface_root(np.array([math.cos(a), math.sin(a)]) * 1.15, a, rng.uniform(2.0, 5.0),
                                          rng.uniform(0.1, 0.15), rng))

    # 3. Limbs.
    hero = list(p["hero_limbs"])
    az = fill_azimuths([math.radians(h[0]) for h in hero], int(p["limbs"]), rng)
    limb_reach = []
    for i, a in enumerate(az):
        frac = hero[i][1] if i < len(hero) else rng.uniform(0.55, 0.78)
        reach = R * frac
        z0 = rng.uniform(4.6, 5.6)
        elev = math.radians(rng.uniform(8.0, 18.0))
        sag = rng.uniform(0.2, 0.7) * reach / 10.0
        if i < len(hero):
            z0, elev, sag = hero[i][3], math.radians(hero[i][4]), hero[i][5]
        curl = rng.uniform(1.2, 2.6)
        wav_a, wav_f, wav_p = rng.uniform(0.3, 0.8), rng.uniform(1.0, 2.0), rng.uniform(0, 2 * math.pi)
        if i < len(hero):
            wav_a *= 1.6
        r0 = 0.5 if i < len(hero) else rng.uniform(0.36, 0.46)
        s = np.linspace(0.0, 1.0, 14)
        dv = np.array([math.cos(a), math.sin(a), 0.0])
        pv = np.array([-math.sin(a), math.cos(a), 0.0])
        horiz = 0.35 + reach * s
        z = z0 + reach * s * math.tan(elev) - sag * np.sin(math.pi * s) + curl * s ** 3
        wander = wav_a * np.sin(math.pi * s * wav_f + wav_p) * s
        pts = dv[None, :] * horiz[:, None] + pv[None, :] * wander[:, None] + UP[None, :] * z[:, None]
        radii = r0 * (1 - 0.72 * s ** 1.05)
        tree.limbs.append(Limb(pts, radii, float(rng.random()), g0=0.0, g1=0.12, cap=True, ao0=0.55, ao1=0.8))
        limb_reach.append(reach)

    # 4. Branches and clumps along each limb, then clumps capping the trunk top.
    floor = float(p["foliage_floor_m"])

    def add_clump(anchor: np.ndarray, center: np.ndarray, phase: float, g: float, rh: float, rv: float) -> None:
        center = center.copy()
        center[2] = min(center[2], H - rv * 0.9)
        rv = min(rv, max(1.0, center[2] - floor - 0.8))
        waves = canopy.random_waves(rng, 4, 0.16)
        tree.clumps.append(Clump(center, np.array([rh, rh * rng.uniform(0.85, 1.15), rv]), phase, anchor, g, waves,
                                 float(rng.random())))

    for li, limb in enumerate(tree.limbs):
        reach = limb_reach[li]
        s_b = 0.3 + rng.uniform(0.0, 0.08)
        side = 1.0 if rng.random() < 0.5 else -1.0
        while s_b < 0.9:
            start, rl = _point_on(limb, s_b)
            out = vc.normalize(np.array([start[0], start[1], 0.0]))
            perp = np.array([-out[1], out[0], 0.0])
            e = math.radians(rng.uniform(35.0, 65.0) if li >= len(hero) else rng.uniform(18.0, 45.0))
            d = vc.normalize(out * math.cos(e) * 0.7 + perp * side * 0.55 * math.cos(e) + UP * math.sin(e))
            length = rng.uniform(2.2, 3.6)
            phase = float(rng.random())
            m = 6
            pts = [start]
            h = d.copy()
            for _ in range(m - 1):
                h = vc.normalize(h + UP * 0.12)
                pts.append(pts[-1] + h * length / (m - 1))
            pts = np.array(pts)
            if pts[-1, 2] > H - 2.2:  # keep the crown under its height
                pts = start + (pts - start) * max(0.3, (H - 2.2 - start[2]) / max(pts[-1, 2] - start[2], 1e-3))
            g0 = 0.12 * s_b
            radii = 0.6 * rl * (1 - 0.7 * np.linspace(0.0, 1.0, m))
            tree.branches.append(Limb(pts, radii, phase, g0=g0, g1=0.35, cap=True, ao0=0.6, ao1=0.8))
            add_clump(pts[-1], pts[-1] + UP * rng.uniform(0.3, 0.7) + out * 0.6, phase, 0.35,
                      rng.uniform(2.0, 3.0), rng.uniform(1.3, 1.9))
            side = -side
            s_b += rng.uniform(*p["branch_spacing_m"]) / reach
        add_clump(limb.pts[-1], limb.pts[-1] + UP * rng.uniform(0.6, 1.0), limb.phase, 0.12,
                  rng.uniform(2.2, 3.0), rng.uniform(1.4, 1.9))
        if li < len(hero):
            n_low = int(p["hero_low_clumps"])
            for k in range(n_low):
                at, _rl = _point_on(limb, 0.3 + 0.55 * (k + rng.uniform(0.2, 0.8)) / n_low)
                c = Clump(at + UP * rng.uniform(0.8, 1.1), np.array([1.7, 1.5, 1.0]) * rng.uniform(0.9, 1.15),
                          limb.phase, at, 0.12, canopy.random_waves(rng, 4, 0.16), float(rng.random()))
                tree.clumps.append(c)
    n_top = int(p["top_clumps"])
    for k in range(n_top):
        a = 2 * math.pi * k / n_top + rng.uniform(-0.4, 0.4)
        out = np.array([math.cos(a), math.sin(a), 0.0])
        start = np.array([0.0, 0.0, 5.6]) + out * 0.3
        end = start + vc.normalize(out * rng.uniform(0.35, 0.9) + UP) * rng.uniform(4.2, 5.2)
        phase = float(rng.random())
        t = np.linspace(0.0, 1.0, 6)
        pts = start + (end - start) * t[:, None] + out * (0.5 * np.sin(math.pi * t))[:, None]
        tree.branches.append(Limb(pts, 0.32 * (1 - 0.7 * t), phase, g0=0.0, g1=0.3, cap=True, ao0=0.5, ao1=0.8))
        add_clump(end, end + UP * 0.8 + out * 1.2, phase, 0.3, rng.uniform(2.6, 3.2), rng.uniform(1.6, 2.0))

    # 5. Branchlets, twigs and sprays per clump.
    density = float(p["cluster_density"])
    for ci, c in enumerate(tree.clumps):
        anchors = [c.anchor]
        for k in range(4):
            a = 2 * math.pi * k / 4 + rng.uniform(-0.5, 0.5)
            dirv = vc.normalize(np.array([math.cos(a), math.sin(a), rng.uniform(0.1, 0.8)]))
            end = c.center + dirv * c.radii * 0.62
            t = np.linspace(0.0, 1.0, 4)
            pts = c.anchor + (end - c.anchor) * t[:, None] + UP * (0.25 * np.sin(math.pi * t))[:, None]
            tree.branchlets.append(Limb(pts, 0.07 - 0.045 * t, c.phase, g0=c.g, g1=c.g + 0.2, cap=True,
                                        ao0=0.6, ao1=0.75))
            anchors.extend(list(pts[1:]))
        anchors = np.array(anchors)
        rh, rv = float(c.radii[:2].mean()), float(c.radii[2])
        area = 4 * math.pi * (((rh * rh) ** 1.6 + 2 * (rh * rv) ** 1.6) / 3) ** (1 / 1.6)
        n = int(round(area * density))
        for _ in range(n):
            d = vc.normalize(rng.normal(0.0, 1.0, 3))
            under_keep = rng.random()
            shell = rng.uniform(0.82, 1.0) if rng.random() > 0.2 else rng.uniform(0.5, 0.8)
            if d[2] < -0.3 and under_keep > 0.55:
                continue
            pos = c.center + d * c.radii * shell
            inside = False
            for cj, o in enumerate(tree.clumps):
                if cj != ci and float(np.linalg.norm((pos - o.center) / o.radii)) < 0.85:
                    inside = True
                    break
            if inside or pos[2] < floor:
                continue
            src = canopy.nearest_point(anchors, pos)
            if float(np.linalg.norm(pos - src)) > 0.3:
                t = np.linspace(0.0, 1.0, 2)
                tree.twigs.append(Limb(src + (pos - src) * t[:, None], np.array([0.018, 0.008]), c.phase,
                                       g0=c.g + 0.2, g1=0.55, ao0=0.65, ao1=0.75))
            top = (d[2] + 1.0) * 0.5
            ao = float(np.clip(0.26 + 0.46 * top + 0.22 * (shell - 0.6) + 0.18 * (pos[2] - 6.0) / (H - 6.0), 0.18, 1.0))
            for _k in range(int(rng.integers(2, 5))):
                tree.sprays.append({
                    "attach": pos + rng.normal(0.0, 0.08, 3),
                    "out": vc.normalize(d * 0.8 + rng.normal(0.0, 0.5, 3) + UP * 0.25),
                    "face": vc.normalize(UP * 0.7 + d * 0.5 + rng.normal(0.0, 0.6, 3)),
                    "size": rng.uniform(0.62, 0.86), "droop": rng.uniform(0.05, 0.25), "cup": rng.uniform(0.05, 0.18),
                    "phase": c.phase, "tint": float(rng.random()), "ao": ao, "g": 0.55,
                    "rect": SPRAYS[int(rng.integers(0, len(SPRAYS)))], "keep": float(rng.random()), "clump": ci,
                })

    # 6. Prop roots.
    counts = [hero[i][2] if i < len(hero) else 0 for i in range(len(tree.limbs))]
    for _ in range(int(p["extra_props"])):
        counts[len(hero) + int(rng.integers(0, len(tree.limbs) - len(hero)))] += 1
    for li, limb in enumerate(tree.limbs):
        reach = limb_reach[li]
        placed: list[float] = []
        for _ in range(counts[li]):
            for _try in range(30):
                s = rng.uniform(0.0, 1.0)
                dist = 0.35 + reach * s
                at, rl = _point_on(limb, s)
                if (3.2 <= dist <= reach * 0.92 and all(abs(dist - q) > 1.4 for q in placed)
                        and path_distance(at, p["path"]) > 0.4):
                    break
            else:
                continue
            placed.append(dist)
            attach = at - UP * rl * 0.5
            big = li < len(hero)
            rp = rng.uniform(0.2, 0.34) if big else rng.uniform(0.12, 0.26)
            n_str = 1 if rp < 0.16 else int(rng.integers(2, 4))
            foot = np.array([attach[0] + rng.normal(0, 0.25), attach[1] + rng.normal(0, 0.25), -0.6])
            twist = rng.uniform(0.4, 1.2) * 2 * math.pi
            ph0 = rng.uniform(0, 2 * math.pi)
            bow = rng.uniform(-0.3, 0.3)
            bow_dir = vc.normalize(np.array([rng.normal(), rng.normal(), 0.0]))
            t = np.linspace(0.0, 1.0, 12)
            axis = attach * (1 - t)[:, None] + foot * t[:, None] + bow_dir * (bow * np.sin(math.pi * t))[:, None]
            for j in range(n_str):
                ang = ph0 + 2 * math.pi * j / n_str + twist * t
                off = 0.55 * rp if n_str > 1 else 0.0
                pts = axis + np.stack([np.cos(ang), np.sin(ang), np.zeros_like(t)], axis=-1) * off
                rs = rp / math.sqrt(n_str) * 1.1 * (1 + 0.7 * vc.smoothstep(0.78, 1.0, t)
                                                    + 0.35 * (1 - vc.smoothstep(0.0, 0.15, t)))
                tree.props.append(Limb(pts, rs, limb.phase, kind="root" if rp < 0.2 else "bark", keep=float(j),
                                       ao0=0.75, ao1=0.5))

    # 7. Hanging aerial roots.
    for _ in range(int(p["root_bunches"])):
        pick = rng.random()
        if pick < float(p["hero_root_share"]):
            src = tree.limbs[int(rng.integers(0, len(hero)))]
            s = rng.uniform(0.25, 0.97)
        elif pick < 0.8:
            src = tree.limbs[int(rng.integers(0, len(tree.limbs)))]
            s = rng.uniform(0.2, 0.97)
        else:
            src = tree.branches[int(rng.integers(0, len(tree.branches)))]
            s = rng.uniform(0.0, 0.5)
        at, rl = _point_on(src, s)
        attach = at - UP * rl * 0.6
        long = rng.random() < 0.35
        n_str = int(rng.integers(2, 8))
        base_len = attach[2] * (rng.uniform(0.55, 0.97) if long else rng.uniform(0.12, 0.5))
        braid_turns = rng.uniform(0.5, 1.5)
        braid_ph = rng.uniform(0, 2 * math.pi)
        for j in range(n_str):
            off = rng.normal(0.0, 0.07, 2)
            length = min(base_len * rng.uniform(0.6, 1.05), attach[2] - 0.25)
            anchored = long and rng.random() < 0.12
            clear = path_distance(attach, p["path"]) < 0.3
            if anchored and not clear:
                length = attach[2] + 0.3
            else:
                anchored = False
            if clear:  # cut at head height over the walk
                length = min(length, attach[2] - float(p["path_cut_m"]))
            if length < 0.15:
                continue
            drift = rng.normal(0.0, 0.05, 2)
            r0 = rng.uniform(0.025, 0.05) if anchored else rng.uniform(0.007, 0.02)
            keep = float(rng.random())
            t = np.linspace(0.0, 1.0, 7)
            ang = braid_ph + 2 * math.pi * (braid_turns * t + j / n_str)
            xy = (off[None, :] * (0.3 + 0.7 * t)[:, None] + drift[None, :] * t[:, None]
                  + 0.025 * np.stack([np.cos(ang), np.sin(ang)], axis=-1))
            pts = np.column_stack([attach[0] + xy[:, 0], attach[1] + xy[:, 1], attach[2] - length * t])
            if anchored:
                radii = r0 * (1 + 0.6 * vc.smoothstep(0.85, 1.0, t))
                g1 = 0.0
            else:
                radii = r0 * (1 - 0.6 * t ** 1.5)
                g1 = 0.5
            tree.roots.append(Limb(pts, radii, float(rng.random()), g0=0.0, g1=g1, kind="root", keep=keep,
                                   cap=not anchored, ao0=0.6, ao1=0.85))
    return tree


def build_lod(tree: Tree, name: str, lod: dict) -> MeshBuilder:
    mb = MeshBuilder(name)
    bark = mb.material(MATERIALS["bark"])
    root = mb.material(MATERIALS["root"])
    leaf = mb.material(MATERIALS["leaf"])
    H = tree.height
    st = lod["step"]
    for lb in tree.stems:
        canopy.mesh_limb(mb, lb, bark, lod["stem_sides"], H, step=min(st, 2))
    for centers, ht, hh, ph in tree.flanges:
        idx = list(range(0, len(centers) - 1, st)) + [len(centers) - 1]
        canopy.mesh_flange(mb, centers[idx], ht[idx], hh[idx], bark, lod["flange_sides"], H, ph)
    if lod["surface_roots"]:
        for lb in tree.surface:
            canopy.mesh_limb(mb, lb, bark, 6, H)
    for lb in tree.limbs:
        canopy.mesh_limb(mb, lb, bark, lod["limb_sides"], H, step=min(st, 2))
    for lb in tree.branches:
        canopy.mesh_limb(mb, lb, bark, lod["branch_sides"], H, step=min(st, 2))
    if lod["branchlets"]:
        for lb in tree.branchlets:
            canopy.mesh_limb(mb, lb, bark, lod["branchlet_sides"], H)
    if lod["twigs"]:
        for lb in tree.twigs:
            canopy.mesh_limb(mb, lb, bark, lod["twig_sides"], H)
    for lb in tree.props:
        if lod["cores"] and lb.keep > 0:  # LOD1: one strand per prop root
            continue
        canopy.mesh_limb(mb, lb, root if lb.kind == "root" else bark, lod["prop_sides"], H, step=min(st, 2))
    for lb in tree.roots:
        if lb.keep <= lod["root_keep"]:
            canopy.mesh_limb(mb, lb, root, lod["root_sides"], H, step=min(st, 2))
    for sp in tree.sprays:
        if sp["keep"] <= lod["card_keep"]:
            c = tree.clumps[sp["clump"]]
            canopy.mesh_spray(mb, sp, leaf, vc.COASTAL_ATLAS[sp["rect"]], vc.COASTAL_SPRAY_M["banyan"], H,
                              rows=lod["card_rows"], scale=lod["card_scale"], clump_center=c.center,
                              size_px=vc.COASTAL_LEAF_SIZE)
    if lod["cores"]:
        for c in tree.clumps:
            canopy.mesh_core(mb, c.center, c.radii * 0.72, c.waves, leaf, vc.COASTAL_ATLAS["banyan_mass"], H,
                             rings=4, segs=6, phase=c.phase, ao=(0.25, 0.75), tint=c.tint)
    return mb


def build(variant: str = "hero", name: str | None = None) -> list[MeshBuilder]:
    tree = make_tree(VARIANTS[variant])
    name = name or f"banyan_{variant}"
    return [build_lod(tree, name if i == 0 else f"{name}-lod{i}", lod) for i, lod in enumerate(LODS)]
