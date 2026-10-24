"""Spawn-polyp battle model (M2-CRE-07): docs/kb/art/creatures/spawn_polyp.md.

blender --background --factory-startup --python assets_src/creatures/spawn_polyp/build_spawn_polyp.py -- \
    --out assets/creatures/spawn_polyp/spawn_polyp.glb

Undertow-spawn: a cracked dome of wet lacquer-black plates over a dark core that seeps spawn_wound light through the
gaps, and five soft tube-mouths of different lengths rising from it, leaning outward and toward +z (the stage turns
+z to the party) like a half-open hand. Every mouth is a soft lip ring whose interior glows spawn_wound; six lip
bones per mouth open and close it. Two closed buds on the shell say that more are coming.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 7319
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "deep_teal_shadow": "#0E4A55", "sea_glow": "#1C6B78",
    "lagoon_teal": "#1FA3A6", "spawn_wound": "#3FE0C8",
}.items()}

DOME_R = np.array([0.25, 0.115, 0.24])  # the shell's radii (x, y up, z forward); 0.5 m across, seated on y = 0
CORE_R = DOME_R * 0.93
SEGS = 16  # sides of a tube
LIPS = 6  # lip bones per mouth
# The five tubes: root (x, z) on the shell, the mouth's height (m) and the bend. Ordered across x for the current's
# travelling sway. The tallest stands at the back so the shorter ones read in front of it from the party's side.
TUBES = (
    ((-0.125, 0.035), 0.27, 1.15),
    ((-0.055, -0.06), 0.43, 0.9),
    ((0.005, -0.03), 0.60, 0.8),
    ((0.075, 0.07), 0.34, 1.0),
    ((0.13, -0.035), 0.24, 1.2),
)
SPLAY_Z = 0.12
BUDS = (((-0.04, 0.15), 0.07), ((0.17, 0.06), 0.055))


def unit(v) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    return v / max(float(np.linalg.norm(v)), 1e-12)


def aa(axis, deg: float) -> tuple[float, float, float]:
    """An axis-angle rotation as the kit's Euler key (X first, then Y, then Z, about the rest axes)."""
    k = unit(axis)
    a = math.radians(deg)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    R = np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * (K @ K)
    ry = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    rx = math.atan2(R[2, 1], R[2, 2])
    rz = math.atan2(R[1, 0], R[0, 0])
    return (math.degrees(rx), math.degrees(ry), math.degrees(rz))


def core_y(x: float, z: float) -> float:
    q = 1.0 - (x / CORE_R[0]) ** 2 - (z / CORE_R[2]) ** 2
    return CORE_R[1] * math.sqrt(max(q, 0.0))


def oriented(P: np.ndarray, T: np.ndarray, out_fn) -> np.ndarray:
    """Flips T if most of its faces point against out_fn(centroids) (so cull_back shows the outside)."""
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    c = P[T].mean(axis=1)
    return ck.flip(T) if float(((fn * out_fn(c)).sum(axis=1) > 0).mean()) < 0.5 else T


# ---------------------------------------------------------------------------------------------
# Tube geometry: a centre path, and a profile of rings (s along the path, h along the end tangent, r)
# ---------------------------------------------------------------------------------------------
class Path3:
    def __init__(self, ctrl, n: int = 48) -> None:
        self.P = ck.bezier(ctrl, n)
        self.tan, self.nrm, self.bin = ck.frames_along(self.P, up_hint=(0.0, 0.0, 1.0))
        seg = np.linalg.norm(np.diff(self.P, axis=0), axis=1)
        self.s = np.concatenate([[0.0], np.cumsum(seg)])
        self.length = float(self.s[-1])

    def at(self, u: float):
        """Position and frame at arc fraction u (0..1)."""
        x = min(max(u, 0.0), 1.0) * self.length
        k = int(min(np.searchsorted(self.s, x, side="right") - 1, len(self.s) - 2))
        f = (x - self.s[k]) / max(self.s[k + 1] - self.s[k], 1e-12)
        p = ck.mix(self.P[k], self.P[k + 1], f)
        t = unit(ck.mix(self.tan[k], self.tan[k + 1], f))
        n = ck.mix(self.nrm[k], self.nrm[k + 1], f)
        n = unit(n - np.dot(n, t) * t)
        return p, t, n, np.cross(t, n)


def outward(P: np.ndarray, T: np.ndarray, path: Path3, segs: int = SEGS) -> np.ndarray:
    """Flips a swept surface's triangles if its first band faces into the tube."""
    band = T[: 2 * segs]
    fn = np.cross(P[band[:, 1]] - P[band[:, 0]], P[band[:, 2]] - P[band[:, 0]])
    c = P[band].mean(axis=1) - path.P[0]
    c = c - np.outer(c @ path.tan[0], path.tan[0])
    return ck.flip(T) if float((fn * c).sum()) < 0 else T


def tube_dims(height: float) -> tuple[float, float, float]:
    """(root radius, waist radius, lip radius) for a tube whose mouth stands at `height`."""
    f = 0.8 + 0.4 * (height / 0.6)
    return 0.05 * f, 0.026 * f, 0.036 * f


def tube_path(root_xz, height: float, bend: float) -> tuple[Path3, np.ndarray]:
    x, z = root_xz
    p0 = np.array([x, core_y(x, z) - 0.03, z])
    radial = unit(np.array([x, 0.0, z + SPLAY_Z]))  # outward from a point behind the centre: a hand opening to +z
    lean = unit(np.array([0.0, 1.0, 0.0]) + radial * (0.42 * bend) + np.array([0.0, 0.0, 0.18 * bend]))
    rise = height - p0[1]
    L = rise / lean[1]
    p3 = p0 + lean * L
    p3[1] = height
    p1 = p0 + np.array([0.0, 0.33 * rise, 0.0])
    p2 = p0 + np.array([0.0, 0.66 * rise, 0.0]) + (lean * L - np.array([0.0, rise, 0.0])) * 0.55
    return Path3([p0, p1, p2, p3]), radial


def ring_profile(height: float, length: float, closed: bool = False):
    """[(u, h, r, slot, emission, zone)] from the buried root up the outside, over the lip, down inside to a cap.
    zone: 'chain' rings follow the tube bones, 'lip' rings follow the lip bones."""
    r0, rw, rl = tube_dims(height)
    lip_t = 0.014 if not closed else 0.006
    n_out = 6 + int(length * 12)
    out = []
    for k in range(n_out):
        u = (k / (n_out - 1)) * (1.0 - 0.6 * lip_t / length)
        taper = (1.0 - u) ** 2.6
        flare = ck.smoothstep(0.62, 1.0, u)
        r = rw + (r0 - rw) * taper + (rl - rw) * float(flare)
        r *= 1.0 - 0.07 * math.sin(u * math.pi * 3.0) ** 8  # two soft constrictions, like a sea-squirt's neck
        out.append((u, 0.0, r, "tube", 0.4 * u ** 2, "chain"))
    lip_c = rl if not closed else rl * 0.35
    for phi in (-50.0, 10.0, 70.0, 125.0):
        a = math.radians(phi)
        out.append((1.0, lip_t * math.sin(a), lip_c + lip_t * math.cos(a), "tube", 0.55, "lip"))
    inner = [(1.0, lip_t * math.sin(math.radians(125.0)), lip_c + lip_t * math.cos(math.radians(125.0)), "mouth",
              0.1, "lip"),
             (1.0, 0.0, lip_c - lip_t, "mouth", 0.22, "lip"),
             (1.0, -0.022, lip_c - lip_t - 0.003, "mouth", 0.6, "lip"),
             (1.0, -0.05, (lip_c - lip_t) * 0.7, "mouth", 1.0, "lip")]
    return out, inner, -0.075 if not closed else -0.02


def sweep(path: Path3, rings, segs: int, wobble: float = 0.0, seed: int = 0) -> np.ndarray:
    """Rings along the path; `wobble` makes each section soft and uneven (never a machined cylinder), and the lip
    rings scallop."""
    a = np.arange(segs) * (2.0 * math.pi / segs)
    ca, sa = np.cos(a), np.sin(a)
    rows = []
    for k, (u, h, r, *rest) in enumerate(rings):
        p, t, n, b = path.at(u)
        q = np.column_stack([ca * 1.3, sa * 1.3, np.full(segs, u * 5.0)])
        lip = bool(rest) and rest[2] == "lip"
        m = 1.0 + (0.25 if lip else 1.0) * wobble * ck.value_noise(q, seed)
        if lip:
            m = m * (1.0 + 0.035 * np.sin(a * 3.0 + seed))
        rows.append(p + t * h + (r * m)[:, None] * (np.outer(ca, n) + np.outer(sa, b)))
    return np.vstack(rows)


def tube_part(mesh: ck.Mesh, rig: ck.Rig, i: int, path: Path3, height: float, rng: np.random.Generator) -> None:
    outer, inner, cap_h = ring_profile(height, path.length)
    rings = outer + inner
    P = sweep(path, rings, SEGS, wobble=0.13, seed=SEED + 11 * i)
    p_end, t_end, _, _ = path.at(1.0)
    cap = p_end + t_end * cap_h
    P = np.vstack([P, cap[None]])
    R = len(rings)
    T = ck.grid_tris(R, SEGS, True)
    r_last = (R - 1) * SEGS
    capT = np.asarray([(r_last + s, R * SEGS, r_last + (s + 1) % SEGS) for s in range(SEGS)], dtype=np.int64)
    T = np.vstack([T, capT])
    T = outward(P, T, path)
    # normals over the whole surface, so the tube and the mouth meet without a shading seam
    N = ck.weld_normals(P, ck.vertex_normals(P, T))

    # per-vertex attributes
    ang = np.tile(np.arange(SEGS) * (2.0 * math.pi / SEGS), R)
    ring_of = np.repeat(np.arange(R), SEGS)
    u = np.array([rings[k][0] for k in range(R)])[ring_of]
    zone_lip = np.array([rings[k][5] == "lip" for k in range(R)])[ring_of]
    emis = np.array([rings[k][4] for k in range(R)])[ring_of]
    ang = np.append(ang, 0.0)
    ring_of = np.append(ring_of, R)
    u = np.append(u, 1.0)
    zone_lip = np.append(zone_lip, False)
    emis = np.append(emis, 1.0)

    # skinning: the chain by arc fraction below the lip, two nearest lip bones by angle above it
    tb = [rig.index(f"tube{i}_{j}") for j in range(3)]
    lb = [rig.index(f"lip{i}_{k}") for k in range(LIPS)]
    n = len(P)
    J = np.zeros((n, 2), dtype=np.int64)
    W = np.zeros((n, 2))
    for v in range(n):
        if zone_lip[v]:
            x = (ang[v] / (2.0 * math.pi)) * LIPS
            k0 = int(math.floor(x)) % LIPS
            f = x - math.floor(x)
            J[v] = (lb[k0], lb[(k0 + 1) % LIPS])
            W[v] = (1.0 - f, f)
        else:
            x = min(max(u[v] * 3.0 - 0.5, 0.0), 1.9999)  # 0 at bone 0's middle .. 2 at bone 2's middle
            j = int(x)
            f = float(ck.smoothstep(0.0, 1.0, x - j))
            J[v], W[v] = (tb[j], tb[j + 1]), (1.0 - f, f)

    # colour: lacquer at the root, deep teal up the stalk, lighter and glassier toward the lip
    up = ck.smoothstep(0.45, 0.97, u)
    col = ck.mix(PAL["deep_teal_shadow"] * 0.8, PAL["sea_glow"], up[:, None])
    col = ck.mix(col, PAL["lagoon_teal"] * 0.8, (0.35 * ck.smoothstep(0.92, 1.0, u) * ~zone_lip + 0.45 * zone_lip)[:, None])
    col = ck.mix(col, PAL["lacquer_black"], (1.0 - ck.smoothstep(0.05, 0.35, u))[:, None])
    stripe = 0.5 + 0.5 * np.cos(ang * 6.0 + i)
    col = col * (0.9 + 0.1 * stripe)[:, None]
    blot = ck.smoothstep(0.1, 0.45, ck.fbm(P * 9.0, SEED + 30 + i))
    col = col * (1.0 - 0.25 * blot)[:, None]
    # the light inside shows faintly through the thin upper wall; a few drifting wound flecks low on the stalk
    through = ck.smoothstep(0.65, 1.0, u) * 0.32 * ~zone_lip
    emission = np.where(zone_lip | (ring_of == R), emis, through)
    cavity = 0.35 * (1.0 - ck.smoothstep(0.0, 0.12, u)) + 0.25 * (1.0 - stripe) * 0.4
    mouth_col = ck.mix(PAL["deep_teal_shadow"], PAL["spawn_wound"], (0.15 + 0.6 * emis)[:, None])
    is_mouth = np.array([rings[k][3] == "mouth" for k in range(R)] + [True])[ring_of]

    # split into the tube slot and the mouth slot along the shared ring (duplicated vertices, the same normals)
    first_mouth = len(outer)  # inner[0] repeats the last lip ring's place in the mouth slot (a zero-area band)
    for slot, ring_range in (("tube", range(0, first_mouth)), ("mouth", range(first_mouth, R + 1))):
        keep = np.isin(ring_of, list(ring_range))
        idx = np.nonzero(keep)[0]
        remap = -np.ones(n, dtype=np.int64)
        remap[idx] = np.arange(len(idx))
        tri_ok = keep[T].all(axis=1)
        Ts = remap[T[tri_ok]]
        c = np.where(is_mouth[idx, None], mouth_col[idx], col[idx])
        Jk, Wk = J[idx], W[idx]
        ck.finish(mesh, P[idx], Ts, slot, c, lambda _P, Jk=Jk, Wk=Wk: (Jk, Wk), wet=1.0,
                  cavity=np.where(is_mouth[idx], 0.5, cavity[idx]), emission=emission[idx], N=N[idx])


def bud(mesh: ck.Mesh, rig: ck.Rig, xz, height_above: float) -> None:
    x, z = xz
    y0 = core_y(x, z) - 0.01
    radial = unit(np.array([x, 0.0, z]))
    p0 = np.array([x, y0, z])
    p3 = p0 + unit(np.array([0.0, 1.0, 0.0]) + radial * 0.8) * height_above
    path = Path3([p0, p0 + np.array([0.0, height_above * 0.5, 0.0]), p3], 12)
    rings = []
    m = 6
    for k in range(m):
        u = k / (m - 1)
        r = 0.022 * (1.0 - 0.75 * u ** 1.6) + 0.004
        rings.append((u, 0.0, r, "tube", 0.0, "chain"))
    P = sweep(path, rings, 8)
    tip = p3 + path.at(1.0)[1] * 0.006
    P = np.vstack([P, tip[None]])
    T = ck.grid_tris(m, 8, True)
    last = (m - 1) * 8
    T = np.vstack([T, [(last + s, m * 8, last + (s + 1) % 8) for s in range(8)]])
    T = outward(P, T, path, 8)
    u = np.append(np.repeat([r[0] for r in rings], 8), 1.0)
    col = ck.mix(PAL["lacquer_black"], PAL["deep_teal_shadow"], ck.smoothstep(0.1, 0.8, u)[:, None])
    ck.finish(mesh, P, T, "tube", col, rig.rigid("base"), wet=1.0, cavity=0.2,
              emission=ck.smoothstep(0.75, 1.0, u) * 0.9)


# ---------------------------------------------------------------------------------------------
# The shell: a dark core and overlapping beveled lacquer plates; the gaps between them seep light
# ---------------------------------------------------------------------------------------------
def core(mesh: ck.Mesh, rig: ck.Rig) -> None:
    prof = []
    rings = 9
    for k in range(rings + 1):
        th = (math.pi / 2) * k / rings * 1.08  # past the equator, so the foot tucks under
        prof.append((math.sin(th), math.cos(th)))
    P, T = ck.lathe(prof, 24)
    P = P * CORE_R
    P[:, 1] = np.maximum(P[:, 1], -0.012)
    noise = ck.fbm(P * 14.0, SEED + 3)
    seep = ck.smoothstep(-0.05, 0.3, noise)
    col = ck.mix(PAL["abyss_navy"], PAL["deep_teal_shadow"], (0.5 * seep)[:, None])
    T = oriented(P, T, lambda c: c)
    ck.finish(mesh, P, T, "core", col, rig.rigid("base"), wet=1.0, cavity=0.6 - 0.4 * seep, emission=0.25 + 0.6 * seep)


def plate_dirs(rng: np.random.Generator) -> np.ndarray:
    pts = [(0.0, 1.0, 0.0)]
    golden = math.pi * (3.0 - math.sqrt(5.0))
    n = 11
    for i in range(n):
        y = 0.82 - (i / (n - 1)) * 0.78
        r = math.sqrt(max(1.0 - y * y, 0.0))
        a = golden * i * 2.2 + rng.uniform(-0.2, 0.2)
        pts.append((r * math.sin(a), y, r * math.cos(a)))
    return np.asarray(pts)


def plates(mesh: ck.Mesh, rig: ck.Rig, rng: np.random.Generator) -> None:
    dirs = plate_dirs(rng)
    S, U = 12, (0.0, 0.3, 0.6, 0.85, 1.0)
    for k, c in enumerate(dirs):
        c = unit(c)
        e1 = unit(np.cross(c, [0.0, 0.0, 1.0]) if abs(c[2]) < 0.9 else np.cross(c, [1.0, 0.0, 0.0]))
        e2 = np.cross(c, e1)
        corners = int(rng.integers(5, 8))
        rot = rng.uniform(0, 2 * math.pi)
        alpha0 = rng.uniform(0.47, 0.58) if k else 0.5
        lift = 1.0 + 0.035 + 0.03 * (k % 3) / 2.0 + rng.uniform(0.0, 0.01)
        phi = np.arange(S) * (2.0 * math.pi / S)
        # a shard: a polygon of `corners` sides, its corners nicked
        poly = np.cos(math.pi / corners) / np.cos(((phi + rot) % (2 * math.pi / corners)) - math.pi / corners)
        alpha = alpha0 * poly * (1.0 + 0.08 * np.sin(phi * 3.0 + k))
        rows = []
        for j, uu in enumerate(list(U) + [1.0]):
            th = alpha * uu
            d = (np.cos(th)[:, None] * c + np.sin(th)[:, None] * (np.outer(np.cos(phi), e1) + np.outer(np.sin(phi), e2)))
            dome = 1.0 - 0.03 * uu ** 2  # each plate is a little flatter than the dome (it is a lid, not skin)
            scale = lift * dome * (0.9 if j == len(U) else 1.0)  # the last ring turns down: the plate's bevel
            rows.append(d * DOME_R * scale)
        P = np.vstack(rows)
        P[:, 1] = np.maximum(P[:, 1], -0.004)
        T = ck.grid_tris(len(rows), S, True)
        T = oriented(P, T, lambda q: q)
        ring = np.repeat(np.arange(len(rows)), S)
        edge = (ring >= len(U) - 1).astype(np.float64)
        tone = rng.uniform(0.0, 1.0)
        base = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], 0.15 + 0.45 * tone)
        polar = np.clip(P[:, 1] / DOME_R[1], 0.0, 1.0)
        colr = ck.mix(np.broadcast_to(base, P.shape), PAL["abyss_navy"], (0.4 * (1.0 - polar))[:, None])
        colr = colr * (1.0 + 0.35 * edge)[:, None]  # the bevel catches light
        scar = ck.smoothstep(0.1, 0.5, ck.fbm(P * 24.0, SEED + 50 + k)) * (1.0 - edge)
        colr = ck.mix(colr, PAL["deep_teal_shadow"] * 0.6, (0.18 * scar)[:, None])
        # hairline cracks on some plates, faintly lit from the core below
        crack = np.zeros(len(P))
        ck.finish(mesh, P, T, "shell", colr, rig.rigid("base"), wet=1.0, cavity=edge * 0.4 + crack * 0.5,
                  emission=crack * 0.7, flat=False)


# ---------------------------------------------------------------------------------------------
# Rig, mesh, clips
# ---------------------------------------------------------------------------------------------
PATHS: list[tuple[Path3, np.ndarray]] = [tube_path(xz, h, b) for xz, h, b in TUBES]


def lip_frame(i: int):
    """The lip ring of tube i: (pivot centres, radial directions, end tangent) per lip bone."""
    path, _ = PATHS[i]
    outer, _, _ = ring_profile(TUBES[i][1], path.length)
    u_piv, _, r_piv, *_ = [r for r in outer if r[5] == "chain"][-1]
    p, _, n, b = path.at(u_piv)
    t = path.at(1.0)[1]
    out = []
    for k in range(LIPS):
        a = k * (2.0 * math.pi / LIPS)
        d = math.cos(a) * n + math.sin(a) * b
        out.append((p + d * r_piv, d))
    return out, t


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    rig.add("base", (0, 0.04, 0), (0, 0.12, 0), "root")
    for i, (path, _) in enumerate(PATHS):
        parent = "base"
        for j in range(3):
            h = path.at(j / 3.0)[0]
            t = path.at((j + 1) / 3.0)[0]
            rig.add(f"tube{i}_{j}", h, t, parent)
            parent = f"tube{i}_{j}"
        piv, t = lip_frame(i)
        for k, (p, d) in enumerate(piv):
            rig.add(f"lip{i}_{k}", p, p + t * 0.03 + d * 0.01, f"tube{i}_2")
    return rig


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    rng = np.random.default_rng(SEED)
    mesh = ck.Mesh("spawn_polyp")
    core(mesh, rig)
    plates(mesh, rig, rng)
    for i, (path, _) in enumerate(PATHS):
        tube_part(mesh, rig, i, path, TUBES[i][1], rng)
    for xz, h in BUDS:
        bud(mesh, rig, xz, h)
    return mesh


def lip_axes(i: int) -> list[np.ndarray]:
    """The axis that opens lip bone k (positive degrees flare it outward, negative pinch it shut)."""
    piv, t = lip_frame(i)
    return [np.cross(t, d) for _, d in piv]


def key_mouth(clip: ck.Clip, i: int, t: float, deg: float) -> None:
    for k, ax in enumerate(lip_axes(i)):
        clip.key(f"lip{i}_{k}", t, aa(ax, deg))


def out_axis(i: int) -> np.ndarray:
    """Rotating a tube by positive degrees about this axis bends it outward (away from the shell's centre)."""
    return np.cross([0.0, 1.0, 0.0], PATHS[i][1])


def ko_axis(i: int) -> np.ndarray:
    x, z = TUBES[i][0]
    r = np.array([x, 0.0, z])
    r = unit(r) if np.linalg.norm(r) > 0.05 else np.array([0.0, 0.0, -1.0])
    return np.cross([0.0, 1.0, 0.0], r)


def tube_dir(i: int) -> np.ndarray:
    path, _ = PATHS[i]
    return unit(path.P[-1] - path.P[0])


def build_clips() -> list[ck.Clip]:
    nt = len(TUBES)
    idle = ck.Clip("idle", 2.8, loop=True)
    idle.wave("base", amp_loc=(0.0, 0.004, 0.0), cycles=1, phase=0.4)
    for i in range(nt):
        for j in range(3):
            ph = -1.15 * i - 0.55 * j  # the current travels across the five, and up each tube
            idle.wave(f"tube{i}_{j}", amp_rot=(1.6 + 0.6 * j, 0.0, -(2.6 + 1.2 * j)), cycles=1, phase=ph)
        # the mouths breathe open and shut out of phase: a ripple of light round the cluster
        steps = 14
        for s in range(steps + 1):
            t = idle.length * s / steps
            deg = 8.0 + 20.0 * math.sin(2.0 * math.pi * s / steps + i * 2.0 * math.pi * 2 / nt)
            key_mouth(idle, i, t, deg)

    attack = ck.Clip("attack", 0.9)
    for i in range(nt):
        fwd = np.array([1.0, 0.0, 0.0])
        for t, back, mouth in ((0.0, 0.0, 0.0), (0.3, -1.0, -22.0), (0.46, 1.0, 38.0), (0.62, 0.7, 26.0),
                               (0.9, 0.0, 0.0)):
            for j in range(3):
                a = (16.0, 12.0, 10.0)[j] * back if back < 0 else (24.0, 14.0, 10.0)[j] * back
                inward = -6.0 * abs(back) if back < 0 else 0.0
                rot = np.add(aa(fwd, a), aa(out_axis(i), inward)) if j == 0 else aa(fwd, a)
                attack.key(f"tube{i}_{j}", t, tuple(rot))
            key_mouth(attack, i, t, mouth)
    for t, z in ((0.0, 0.0), (0.3, -0.02), (0.46, 0.04), (0.9, 0.0)):
        attack.key("base", t, loc=(0.0, 0.0, z))

    cast = ck.Clip("cast", 1.5)  # polyp_mend: release at 0.6 s
    for i in range(nt):
        d = tube_dir(i)
        for t, open_, mouth in ((0.0, 0.0, 0.0), (0.35, 0.8, 34.0), (0.6, 1.0, 55.0), (0.8, 0.85, 34.0),
                                (1.0, 1.0, 55.0), (1.2, 0.8, 36.0), (1.5, 0.0, 0.0)):
            for j in range(3):
                stretch = d * 0.018 * open_  # each segment slides a little up its tube: the tubes stretch
                lean = aa([1.0, 0.0, 0.0], 7.0 * open_ * (1.0 if j == 0 else 0.5))
                cast.key(f"tube{i}_{j}", t, lean, tuple(stretch if j else stretch * 0.5))
            key_mouth(cast, i, t, mouth)
    for t, y in ((0.0, 0.0), (0.6, 0.01), (1.5, 0.0)):
        cast.key("base", t, loc=(0.0, y, 0.0))

    hit = ck.Clip("hit", 0.4)
    for i in range(nt):
        d = tube_dir(i)
        for t, pull in ((0.0, 0.0), (0.08, 1.0), (0.18, 0.9), (0.4, 0.0)):
            hit.key(f"tube{i}_0", t, aa(out_axis(i), -9.0 * pull), tuple(-d * 0.05 * pull))
            hit.key(f"tube{i}_1", t, aa(out_axis(i), -6.0 * pull))
            key_mouth(hit, i, t, -24.0 * pull)
    for t, y in ((0.0, 0.0), (0.08, -0.012), (0.4, 0.0)):
        hit.key("base", t, loc=(0.0, y, 0.0))

    ko = ck.Clip("ko", 1.4)
    order = [2, 1, 3, 0, 4]  # the tallest goes first, the short outer ones last
    for rank, i in enumerate(order):
        t0 = 0.05 + 0.14 * rank
        d = tube_dir(i)
        ax = ko_axis(i)
        tall = TUBES[i][1] / 0.6
        curl = ((26.0, 30.0), (40.0 + 30.0 * tall, 46.0 + 30.0 * tall), (50.0 + 25.0 * tall, 56.0 + 25.0 * tall))
        for j, (deg, deg_end) in enumerate(curl):
            sink = tuple(-d * (0.06 + 0.04 * tall)) if j == 0 else (0, 0, 0)
            ko.key(f"tube{i}_{j}", 0.0)
            ko.key(f"tube{i}_{j}", t0 + 0.06 * j)
            ko.key(f"tube{i}_{j}", t0 + 0.4 + 0.1 * j, aa(ax, deg * 0.8), tuple(np.asarray(sink) * 0.7))
            ko.key(f"tube{i}_{j}", t0 + 0.6 + 0.1 * j, aa(ax, deg), sink)
            ko.key(f"tube{i}_{j}", 1.4, aa(ax, deg_end), sink)
        key_mouth(ko, i, 0.0, 0.0)
        key_mouth(ko, i, 0.9 + 0.04 * rank, 6.0)
        key_mouth(ko, i, 1.25 + 0.03 * rank, -26.0)
        key_mouth(ko, i, 1.4, -26.0)
    for t, y in ((0.0, 0.0), (0.9, -0.015), (1.4, -0.02)):
        ko.key("base", t, loc=(0.0, y, 0.0))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "spawn_polyp"})
    print(f"spawn_polyp: {info}")


if __name__ == "__main__":
    main()
