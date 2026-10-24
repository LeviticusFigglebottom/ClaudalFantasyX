"""Wall-polyp, Ch8 the seawall (M3-CRE-06): docs/kb/art/creatures/act1/wall_polyp.md.

blender --background --factory-startup --python assets_src/creatures/wall_polyp/build_wall_polyp.py -- \
    --out assets/creatures/wall_polyp/wall_polyp.glb

A variant of the spawn-polyp rooted on the seawall's stones: the same wet lacquer shell, seeping core and five
lit tube-mouths (built by the spawn-polyp's build module, imported and re-proportioned, not edited), but flatter
and wider, clamped over a broken piece of the wall. The piece is three laterite blocks; the middle one carries a
fragment of a Watcher, one of the wall's carved humming faces (closed eyes, open mouth). The shell grows over its
brow, black roots creep out of its stone mouth and down its chin, and the mouth glows spawn_wound with the polyp's
light, so burning the polyp off (it is fire-weak) scars the face. The mouths lean out over the stone's edge toward
the party. Rooted: its clips are the spawn-polyp's.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "common"))
sys.path.insert(0, str(_HERE.parent / "spawn_polyp"))
import build_spawn_polyp as sp  # noqa: E402
import creature_kit as ck  # noqa: E402

SEED = 8807
PAL = {k: ck.hexrgb(v) for k, v in {
    "coral_stone_weathered": "#B9AE98", "mortar_white": "#E6E1D6", "laterite": "#A8573A", "storm_slate": "#3E4A57",
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "spawn_wound": "#3FE0C8", "sand_wet": "#B59D74",
}.items()}
STONE = ck.mix(PAL["coral_stone_weathered"], PAL["storm_slate"], 0.25)  # the wall's grey laterite, weathered

# The piece of wall: the Watcher's block in the middle (its carved face to +z, the party), a lower block each side.
FACE_LO = np.array([-0.30, 0.0, -0.24])
FACE_HI = np.array([0.30, 0.40, 0.20])
FACE_Z = 0.22  # the carved panel's base plane, proud of the block's front
SIDE_BLOCKS = (  # (centre, half extents, yaw)
    (np.array([-0.47, 0.10, -0.04]), np.array([0.16, 0.10, 0.19]), 7.0),
    (np.array([0.45, 0.12, -0.05]), np.array([0.15, 0.12, 0.18]), -9.0),
)
H = float(FACE_HI[1])  # the polyp sits on the Watcher's block

# The polyp, re-proportioned: a flatter, wider shell and mouths that lean out further toward the party.
sp.DOME_R = np.array([0.36, 0.075, 0.24])
sp.CORE_R = sp.DOME_R * 0.93
sp.SPLAY_Z = 0.22
sp.TUBES = (
    ((-0.20, 0.06), 0.25, 1.7),
    ((-0.09, -0.05), 0.38, 1.3),
    ((0.0, -0.08), 0.50, 1.1),
    ((0.10, 0.04), 0.33, 1.5),
    ((0.21, -0.03), 0.23, 1.8),
)
sp.BUDS = (((-0.13, 0.15), 0.06), ((0.25, 0.10), 0.05), ((0.06, 0.17), 0.045))
sp.PATHS = [sp.tube_path(xz, h, b) for xz, h, b in sp.TUBES]
SHELL_Z = -0.05  # the shell's centre sits back on the block, so the Watcher's eyes show


def _place(P: np.ndarray) -> np.ndarray:
    """Polyp space to this model: lifted onto the block and draped down over its edges (a clamped limpet)."""
    P = np.asarray(P, dtype=np.float64).copy()
    low = ck.smoothstep(0.16, 0.06, P[:, 1])  # only the shell and the core drape; the tubes stand
    P[:, 2] += SHELL_Z
    ex = np.maximum(np.abs(P[:, 0]) - (FACE_HI[0] - 0.03), 0.0)
    ez = 0.5 * np.maximum(P[:, 2] - (FACE_HI[2] - 0.02), 0.0) + np.maximum((FACE_LO[2] + 0.03) - P[:, 2], 0.0)
    P[:, 1] += H - low * np.minimum(1.4 * np.sqrt(ex * ex + ez * ez), 0.16)
    return P


def _polyp_parts(mesh: ck.Mesh, rig: ck.Rig, rng: np.random.Generator) -> None:
    real = ck.finish

    def finish(mesh_, P, T, *a, N=None, **kw):
        Q = _place(P)
        if N is not None:  # a draped vertex's normal is recomputed; the rest keep theirs
            moved = np.abs((Q - P)[:, 1] - H) > 1e-9
            if moved.any():
                N = np.where(moved[:, None], ck.weld_normals(Q, ck.vertex_normals(Q, T)), N)
        return real(mesh_, Q, T, *a, N=N, **kw)

    ck.finish = finish
    try:
        sp.core(mesh, rig)
        sp.plates(mesh, rig, rng)
        for i, (path, _) in enumerate(sp.PATHS):
            sp.tube_part(mesh, rig, i, path, sp.TUBES[i][1], rng)
        for xz, h in sp.BUDS:
            sp.bud(mesh, rig, xz, h)
    finally:
        ck.finish = real


def build_rig() -> ck.Rig:
    rig = sp.build_rig()
    for b in rig.bones[1:]:
        b.head = tuple(_place(np.asarray([b.head]))[0])
        b.tail = tuple(_place(np.asarray([b.tail]))[0])
    return rig


# ---------------------------------------------------------------------------------------------
# The wall
# ---------------------------------------------------------------------------------------------
def _box(lo: np.ndarray, hi: np.ndarray, n: int = 4):
    """A box as six n x n grids, wound outward."""
    c = (lo + hi) / 2.0
    h = (hi - lo) / 2.0
    Ps, Ts, base = [], [], 0
    g = np.linspace(-1.0, 1.0, n)
    a, b = np.meshgrid(g, g, indexing="ij")
    a, b = a.ravel(), b.ravel()
    for ax in range(3):
        for s in (-1.0, 1.0):
            u, v = [k for k in range(3) if k != ax]
            q = np.zeros((n * n, 3))
            q[:, ax] = s
            q[:, u] = a
            q[:, v] = b
            T = ck.grid_tris(n, n, False)
            P = c + q * h
            fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
            if float(fn[:, ax].sum()) * s < 0:
                T = ck.flip(T)
            Ps.append(P)
            Ts.append(T + base)
            base += len(P)
    return np.vstack(Ps), np.vstack(Ts)


def _stone_col(P: np.ndarray, seed: int, edge: np.ndarray, stain: float = 0.45) -> np.ndarray:
    n = ck.fbm(P * 6.0, seed)
    col = STONE * (0.9 + 0.12 * ck.fbm(P * 25.0, seed + 1))[:, None]
    col = ck.mix(col, PAL["laterite"] * 0.85, (stain * ck.smoothstep(0.0, 0.35, n))[:, None])  # the laterite shows
    col = ck.mix(col, PAL["mortar_white"] * 0.92, (0.75 * edge)[:, None])  # old mortar on the joints
    col = ck.mix(col, PAL["sand_wet"] * 0.7, (0.5 * ck.smoothstep(0.06, 0.0, P[:, 1]))[:, None])
    return col


def block(mesh: ck.Mesh, rig: ck.Rig, lo, hi, yaw: float, seed: int) -> None:
    lo, hi = np.asarray(lo, dtype=np.float64), np.asarray(hi, dtype=np.float64)
    c = (lo + hi) / 2.0
    h = (hi - lo) / 2.0
    P, T = _box(lo, hi, 5)
    q = (P - c) / h
    corner = np.sort(np.abs(q), axis=1)[:, 1]  # 1 on an edge, less inside a face
    P = c + (P - c) * (1.0 - 0.07 * ck.smoothstep(0.6, 1.0, corner))[:, None]  # worn edges
    rad = (P - c) / np.maximum(np.linalg.norm(P - c, axis=1, keepdims=True), 1e-9)
    chip = ck.fbm(P * 11.0, seed)
    P = P + rad * (0.012 * chip - 0.02 * ck.smoothstep(0.15, 0.35, chip) * ck.smoothstep(0.7, 1.0, corner))[:, None]
    P = c + (P - c) @ ck.rot_y(yaw).T
    P[:, 1] = np.maximum(P[:, 1], -0.005)
    col = _stone_col(P, seed + 3, ck.smoothstep(0.75, 1.0, corner) * ck.smoothstep(-0.1, 0.2, ck.fbm(P * 9.0, seed + 5)))
    ck.finish(mesh, P, T, "stone", col, rig.rigid("base"), wet=0.4 * ck.smoothstep(0.1, 0.0, P[:, 1]),
              cavity=0.3 * ck.smoothstep(0.8, 1.0, corner), N=ck.vertex_normals(P, T))  # each face smooth, edges crisp


def _watcher(u: np.ndarray, v: np.ndarray):
    """The carved face's relief (metres, toward +z) and its mouth mask, on the panel's (u -1..1, v 0..1)."""
    def bump(cu, cv, ru, rv):
        return np.exp(-((u - cu) / ru) ** 2 - ((v - cv) / rv) ** 2)

    r = 0.016 * np.exp(-((v - 0.84) / 0.05) ** 2) * ck.smoothstep(0.95, 0.6, np.abs(u))  # the brow
    for s in (-1.0, 1.0):
        r += 0.014 * bump(s * 0.42, 0.67, 0.22, 0.07)  # closed eyelids
        lid = np.exp(-((v - (0.655 - 0.25 * (u - s * 0.42) ** 2)) / 0.012) ** 2) * bump(s * 0.42, 0.66, 0.2, 0.2)
        r -= 0.008 * lid  # the lid's line
        r += 0.010 * bump(s * 0.55, 0.42, 0.22, 0.14)  # cheeks
    r += 0.03 * bump(0.0, 0.48, 0.09, 0.14) + 0.012 * bump(0.0, 0.64, 0.06, 0.12)  # the nose
    mo = ((u / 0.34) ** 2 + ((v - 0.22) / 0.10) ** 2)  # the open mouth: humming
    mouth = ck.smoothstep(1.0, 0.7, mo)
    lips = np.exp(-((np.sqrt(mo) - 1.12) / 0.16) ** 2)
    r += 0.012 * lips - 0.045 * mouth
    r += 0.006 * bump(0.0, 0.05, 0.3, 0.06)  # the chin
    return r, mouth, lips


def watcher_panel(mesh: ck.Mesh, rig: ck.Rig) -> None:
    nu, nv = 26, 22
    u = np.linspace(-1.0, 1.0, nu)
    v = np.linspace(0.0, 1.0, nv)
    U, V = np.meshgrid(u, v, indexing="ij")
    U, V = U.ravel(), V.ravel()
    relief, mouth, lips = _watcher(U, V)
    relief = relief * 1.8  # cut deep enough to read at battle distance
    # a fragment: the block broke across its upper right corner
    broken = ck.smoothstep(1.55, 1.75, U + V * 1.1)
    x = U * (FACE_HI[0] - 0.015)
    y = 0.012 + V * (FACE_HI[1] - 0.03)
    border = np.maximum(np.abs(U), np.abs(V * 2.0 - 1.0))
    skirt = (np.abs(U) > 0.999) | (V < 0.001) | (V > 0.999)
    weather = ck.fbm(np.column_stack([x, y, np.zeros_like(x)]) * 14.0, SEED + 7) * 0.006
    z = FACE_Z + relief * (1.0 - broken) + weather - 0.03 * broken
    z = np.where(skirt, FACE_HI[2] - 0.004, z)
    P = np.column_stack([x, y, z])
    T = ck.grid_tris(nu, nv, False)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    if float(fn[:, 2].sum()) < 0:
        T = ck.flip(T)
    edge = ck.smoothstep(0.92, 1.0, border)
    col = _stone_col(P, SEED + 9, edge * 0.6, stain=0.15)  # the carving was kept clean
    col = ck.mix(col, PAL["coral_stone_weathered"] * 1.05, (0.35 * lips)[:, None])  # worn smooth by hands
    col = ck.mix(col, PAL["lacquer_black"], (0.7 * mouth)[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.7, (0.9 * ck.smoothstep(0.2, 0.9, mouth))[:, None])
    cav = 0.6 * mouth + 0.5 * ck.smoothstep(0.0, -0.006, relief) * (1.0 - mouth) + 0.3 * broken
    ck.finish(mesh, P, T, "stone", col, rig.rigid("base"), cavity=cav, emission=ck.smoothstep(0.15, 0.8, mouth))


def _strap(mesh: ck.Mesh, ib: int, path: np.ndarray, r0: float, k: int) -> None:
    """A flat lacquer strap lying on the stone (a poured root, not a leg): wide, thin, tapering, lit in seams."""
    n = len(path)
    rad = np.linspace(r0, r0 * 0.3, n) * (1.0 + 0.2 * np.sin(np.arange(n) * 1.9 + k))
    P, T = ck.tube(path, rad, 6, squash=0.32, up_hint=(0.0, 1.0, 0.0))
    t = np.concatenate([np.repeat(np.linspace(0.0, 1.0, n), 6), [0.0, 1.0]])[: len(P)]
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], (0.25 + 0.3 * t)[:, None])
    seam = ck.smoothstep(0.22, 0.38, ck.fbm(P * 28.0, SEED + 20 + k)) * (1.0 - t)
    col = ck.mix(col, PAL["spawn_wound"] * 0.5, (0.6 * seam)[:, None])
    ck.finish(mesh, P, T, "shell", col, ib, wet=1.0, cavity=0.2, emission=seam * 0.6)


def roots(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Lacquer roots clamping the shell to the stones: poured over the block's sides onto the side blocks and
    down its back, over the Watcher's brow at the corners, and out of its stone mouth down the chin."""
    ib = rig.rigid("base")
    x_edge = FACE_HI[0] + 0.012
    k = 0
    for sx, top in ((-1.0, SIDE_BLOCKS[0][0][1] + SIDE_BLOCKS[0][1][1]), (1.0, SIDE_BLOCKS[1][0][1] + SIDE_BLOCKS[1][1][1])):
        for z0, reach in ((-0.14, 0.13), (0.0, 0.17), (0.12, 0.10)):  # over the side, down and out along the block
            path = ck.bezier([(sx * 0.24, H + 0.025, z0), (sx * x_edge, H + 0.012, z0), (sx * x_edge, H - 0.06, z0),
                              (sx * x_edge, top + 0.02, z0 + 0.02), (sx * (x_edge + reach), top + 0.012, z0 + 0.03)],
                             10)
            _strap(mesh, ib, path, 0.034, k)
            k += 1
    for x0 in (-0.16, 0.08):  # down the back to the ground
        z_edge = FACE_LO[2] - 0.012
        path = ck.bezier([(x0, H + 0.025, -0.16), (x0, H + 0.012, z_edge), (x0 + 0.02, H * 0.5, z_edge),
                          (x0 + 0.03, 0.02, z_edge - 0.01), (x0 + 0.04, 0.008, z_edge - 0.08)], 10)
        _strap(mesh, ib, path, 0.034, k)
        k += 1
    for sx in (-1.0, 1.0):  # over the brow at the face's corners
        path = ck.bezier([(sx * 0.17, H + 0.02, 0.10), (sx * 0.22, H + 0.012, FACE_Z + 0.012),
                          (sx * 0.24, H - 0.06, FACE_Z + 0.016), (sx * 0.26, H - 0.12, FACE_Z + 0.012)], 8)
        _strap(mesh, ib, path, 0.026, k)
        k += 1
    mouth_y = 0.012 + 0.22 * (FACE_HI[1] - 0.03)
    for sx in (-0.5, 0.35):  # out of the stone mouth, over the lower lip and down the chin
        path = ck.bezier([(sx * 0.08, mouth_y, FACE_Z - 0.03), (sx * 0.09, mouth_y - 0.03, FACE_Z + 0.025),
                          (sx * 0.11, mouth_y - 0.07, FACE_Z + 0.022), (sx * 0.13, 0.01, FACE_Z + 0.03)], 8)
        _strap(mesh, ib, path, 0.016, k)
        k += 1


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("wall_polyp")
    block(mesh, rig, FACE_LO, FACE_HI, 0.0, SEED + 30)
    watcher_panel(mesh, rig)
    for k, (c, h, yaw) in enumerate(SIDE_BLOCKS):
        block(mesh, rig, c - h, c + h, yaw, SEED + 40 + 10 * k)
    _polyp_parts(mesh, rig, np.random.default_rng(sp.SEED))
    roots(mesh, rig)
    return mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, sp.build_clips(), args.out, extras={"hymn_creature": "wall_polyp"})
    print(f"wall_polyp: {info}")


if __name__ == "__main__":
    main()
