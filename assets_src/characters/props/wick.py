"""The chandler's wick, the wick bundle and the trimming shears (M3-CHR-03; act1_npcs.md §4.4). Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/props/wick.py [-- --out-dir DIR]
    # -> assets/characters/props/wick/{wick,wick_bundle,trimming_shears}.glb and materials/*.tres

**One source for every wick in the game** (the art decision in §4.4): Mother Kell's hand in Ch1, the bundle on her
apron, Rhen's tin, and the E7 post-credits lamp all instance `wick.glb` (or the bundle, which is twelve of the same
wick). It is never fitted to Rhen's lantern, which burns oil (ADR 0022 sweep-H/I/J watch). The wick is trade stock: one
of twelve identical wicks, nothing handed down.

* `wick.glb`: a 9 cm twisted cotton wick, 4 mm thick (three plied strands), the top 1 cm stiffened with wax. Origin at
  its middle, the length along +Y (glTF), so a `BoneAttachment3D` on `DEF-hand.R` places it between thumb and finger.
* `wick_bundle.glb`: twelve wicks tied with thread 2 cm below their waxed tips, a thread loop above the tie. Origin at
  the top of the loop (the hang point on the apron's right, on a hips attachment); the wicks hang down -Y.
* `trimming_shears.glb`: small iron shears (blades, pivot and two finger rings) on a cord. Origin at the top of the
  cord (the hang point beside the bundle); the shears hang down -Y.

Materials (StandardMaterial3D text resources, one per glTF slot, which the `characters` import rule maps from
`materials/<slot>.tres`): `wick_cotton` (sand_cloth), `wick_wax` (the darker waxed tip), `thread`, `cord`,
`shears_iron`. Everything is generated here; nothing is downloaded. Deterministic (no randomness, fixed tessellation).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT_DIR = ROOT / "assets" / "characters" / "props" / "wick"

WICK_LEN = 0.09  # m (§4.4)
WICK_R = 0.002  # m: 4 mm thick
WAX_LEN = 0.01  # m: the stiffened top
WAX_R = 0.0023  # m: the wax coat adds a little
PLIES = 3  # twisted strands
TWIST_TURNS = 7.0  # ply twists over the length
PLY_DEPTH = 0.18  # x radius: the groove between plies
RING_SEG = 10  # around
ROWS = 28  # along
BUNDLE_N = 12
BUNDLE_ROWS = 12  # the bundle's wicks: the same profile at a lighter tessellation (a hip prop)
BUNDLE_SEG = 6
TIE_BELOW_TIP = 0.02  # m
TIE_R = 0.0092  # m: the thread wrap round the bundle
TIE_W = 0.004  # m
LOOP_R = 0.009  # m: the hanging loop
THREAD_R = 0.0006  # m
SHEAR_LEN = 0.12  # m overall
BLADE_LEN = 0.055
BLADE_W = 0.007
BLADE_T = 0.0016
RING_R = 0.011  # finger ring radius
RING_T = 0.0022
CORD_LEN = 0.10  # m from the hang point to the rings
CORD_R = 0.0012

# name -> (albedo hex, roughness, metallic)
MATERIALS = {
    "wick_cotton": ("#C9B48E", 0.95, 0.0),  # sand_cloth (palette.json)
    "wick_wax": ("#9A8462", 0.55, 0.0),
    "thread": ("#B8A88A", 0.9, 0.0),
    "cord": ("#6A5236", 0.9, 0.0),
    "shears_iron": ("#4A4844", 0.45, 0.85),
}


def log(msg: str) -> None:
    print(f"[wick] {msg}", flush=True)


class Mesh:
    """Vertices, quads/triangles, per-corner UVs and a material per face (Blender Z up)."""

    def __init__(self) -> None:
        self.V: list = []
        self.F: list = []
        self.UV: list = []
        self.M: list = []

    def grid(self, P: np.ndarray, mat, closed: bool = True) -> None:
        """A (rows, cols, 3) grid as quads; columns wrap when `closed`. `mat`: a name, or row index -> name."""
        rows, cols = P.shape[:2]
        base = len(self.V)
        self.V += [tuple(float(c) for c in p) for p in P.reshape(-1, 3)]
        ncol = cols if closed else cols - 1
        for j in range(rows - 1):
            for i in range(ncol):
                i2 = (i + 1) % cols
                a, b = base + j * cols + i, base + j * cols + i2
                c, d = base + (j + 1) * cols + i2, base + (j + 1) * cols + i
                self.F.append((a, b, c, d))
                u0, u1 = i / ncol, (i + 1) / ncol
                v0, v1 = j / (rows - 1), (j + 1) / (rows - 1)
                self.UV.append([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
                self.M.append(mat(j) if callable(mat) else mat)

    def cap(self, ring: list[int], centre: tuple, mat: str, flip: bool) -> None:
        c = len(self.V)
        self.V.append(tuple(float(x) for x in centre))
        n = len(ring)
        for i in range(n):
            a, b = ring[i], ring[(i + 1) % n]
            self.F.append((b, a, c) if flip else (a, b, c))
            self.UV.append([(0.5, 0.5)] * 3)
            self.M.append(mat)

    def extend(self, other: "Mesh") -> None:
        base = len(self.V)
        self.V += other.V
        self.F += [tuple(i + base for i in f) for f in other.F]
        self.UV += other.UV
        self.M += other.M

    def moved(self, R: np.ndarray, t: np.ndarray) -> "Mesh":
        out = Mesh()
        P = np.asarray(self.V) @ R.T + t
        out.V = [tuple(float(c) for c in p) for p in P]
        out.F, out.UV, out.M = list(self.F), list(self.UV), list(self.M)
        return out

    def tris(self) -> int:
        return sum(len(f) - 2 for f in self.F)


def tube(path: np.ndarray, radius, seg: int, mat_of=None, mat: str = "", caps: bool = True) -> Mesh:
    """A tube along `path` (n, 3) with `radius(t, theta)` (t in 0..1); `mat_of(t)` picks a row's material."""
    n = len(path)
    T = np.gradient(path, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    ref = np.array([1.0, 0.0, 0.0]) if abs(T[0][0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    N0 = np.cross(T[0], ref)
    N0 /= np.linalg.norm(N0)
    frames = []
    N = N0
    for k in range(n):  # parallel transport
        N = N - T[k] * (N @ T[k])
        N /= np.linalg.norm(N)
        frames.append((N, np.cross(T[k], N)))
    th = np.linspace(0.0, 2.0 * math.pi, seg, endpoint=False)
    P = np.zeros((n, seg, 3))
    for k in range(n):
        t = k / (n - 1)
        r = np.array([radius(t, a) for a in th])
        Nk, Bk = frames[k]
        P[k] = path[k] + (np.outer(np.cos(th) * r, Nk) + np.outer(np.sin(th) * r, Bk))
    m = Mesh()
    m.grid(P, mat if mat_of is None else (lambda j: mat_of((j + 0.5) / (n - 1))))
    if caps:
        m0, m1 = (mat, mat) if mat_of is None else (mat_of(0.0), mat_of(1.0))
        m.cap(list(range(seg)), path[0], m0, flip=True)
        m.cap(list(range((n - 1) * seg, n * seg)), path[-1], m1, flip=False)
    return m


def wick(rows: int = ROWS, seg: int = RING_SEG) -> Mesh:
    """One wick, centred on the origin, along +Z (Blender), the waxed tip at the top."""
    z = np.linspace(-0.5 * WICK_LEN, 0.5 * WICK_LEN, rows + 1)
    path = np.stack([np.zeros_like(z), np.zeros_like(z), z], axis=1)
    wax_from = 1.0 - WAX_LEN / WICK_LEN

    def radius(t: float, a: float) -> float:
        twist = 2.0 * math.pi * TWIST_TURNS * t
        groove = 1.0 - PLY_DEPTH * (0.5 + 0.5 * math.cos(PLIES * (a + twist)))
        if t >= wax_from:  # the wax fills the grooves and rounds the tip
            k = min((t - wax_from) / 0.02, 1.0)
            r = WICK_R * groove * (1 - k) + WAX_R * k
            tip = math.sqrt(max(1.0 - ((t - 0.985) / 0.015) ** 2, 0.0)) if t > 0.985 else 1.0
            return r * (0.55 + 0.45 * tip)
        return WICK_R * groove

    return tube(path, radius, seg, mat_of=lambda t: "wick_wax" if t >= wax_from else "wick_cotton")


def ring(centre: np.ndarray, axis: np.ndarray, R: float, r: float, mat: str, seg: int = 20, around: int = 6,
         stretch: tuple = (1.0, 1.0)) -> Mesh:
    """A torus (R major, r minor) about `axis`; `stretch` scales its two in-plane axes (an oval ring)."""
    axis = axis / np.linalg.norm(axis)
    e1 = np.cross(axis, [0.0, 0.0, 1.0] if abs(axis[2]) < 0.9 else [1.0, 0.0, 0.0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    a = np.linspace(0.0, 2.0 * math.pi, seg + 1)
    path = centre + np.outer(np.cos(a) * R * stretch[0], e1) + np.outer(np.sin(a) * R * stretch[1], e2)
    path[-1] = path[0]
    m = tube(path[:-1], lambda t, b: r, around, mat=mat, caps=False)
    # close the loop: tie the last ring to the first
    n = seg
    base_last = (n - 1) * around
    for i in range(around):
        i2 = (i + 1) % around
        m.F.append((base_last + i, base_last + i2, i2, i))
        m.UV.append([(0, 0), (1, 0), (1, 1), (0, 1)])
        m.M.append(mat)
    return m


def wick_bundle() -> Mesh:
    """Twelve wicks (a ring of eight round a ring of four), tied below the tips, a thread loop above; the origin at
    the top of the loop, the wicks hanging down -Z."""
    out = Mesh()
    one = wick(BUNDLE_ROWS, BUNDLE_SEG)  # the same wick, lighter: twelve of them hang at the hip
    tip_z = 0.5 * WICK_LEN
    tie_z = tip_z - TIE_BELOW_TIP
    spots = [(0.0035 * math.cos(2 * math.pi * k / 4 + 0.4), 0.0035 * math.sin(2 * math.pi * k / 4 + 0.4))
             for k in range(4)]
    spots += [(0.0078 * math.cos(2 * math.pi * k / 8), 0.0078 * math.sin(2 * math.pi * k / 8)) for k in range(8)]
    assert len(spots) == BUNDLE_N
    for k, (x, y) in enumerate(spots):
        # the wicks splay outward a little below the tie (fixed angles: deterministic; negative about z x d is out)
        lean = -math.radians(2.0 + 1.5 * (k % 3))
        d = np.array([x, y, 0.0])
        dn = d / max(np.linalg.norm(d), 1e-9)
        ax = np.cross([0.0, 0.0, 1.0], dn)
        ax = ax / max(np.linalg.norm(ax), 1e-9)
        c, s = math.cos(lean), math.sin(lean)
        K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
        R = np.eye(3) + s * K + (1 - c) * (K @ K)
        w = one.moved(R, np.array([x, y, 0.0]) - R @ np.array([0.0, 0.0, tie_z]) + np.array([0.0, 0.0, tie_z]))
        out.extend(w)
    # the tie: three turns of thread round the bundle
    for k in range(3):
        out.extend(ring(np.array([0.0, 0.0, tie_z + (k - 1) * TIE_W / 3]), np.array([0.0, 0.0, 1.0]), TIE_R,
                        THREAD_R * 1.4, "thread", seg=16, around=4))
    # the loop: a thread oval from the tie up past the tips
    loop_c = np.array([0.0, 0.0, tip_z + LOOP_R * 0.9])
    out.extend(ring(loop_c, np.array([1.0, 0.0, 0.0]), LOOP_R, THREAD_R, "thread", seg=20, around=5,
                    stretch=(1.0, 1.8)))
    top = float(np.asarray(out.V)[:, 2].max())
    return out.moved(np.eye(3), np.array([0.0, 0.0, -top]))


def blade(sign: float) -> Mesh:
    """One shear blade from the pivot (origin) down -Z, a flattened tapered bar, its edge toward x = 0."""
    n = 8
    z = np.linspace(0.0, -BLADE_LEN, n)
    P = np.zeros((n, 4, 3))
    for k, zz in enumerate(z):
        t = k / (n - 1)
        w = BLADE_W * (1.0 - 0.85 * t)
        th = BLADE_T * (1.0 - 0.5 * t)
        x0 = sign * 0.0004
        P[k] = [(x0, -th / 2, zz), (x0 + sign * w, -th / 2, zz), (x0 + sign * w, th / 2, zz), (x0, th / 2, zz)]
    m = Mesh()
    m.grid(P, "shears_iron")
    m.cap([0, 1, 2, 3], P[0].mean(axis=0), "shears_iron", flip=sign > 0)
    last = list(range((n - 1) * 4, n * 4))
    m.cap(last, P[-1].mean(axis=0), "shears_iron", flip=sign < 0)
    return m


def trimming_shears() -> Mesh:
    """Small iron shears, closed, hanging on a cord by one ring; the origin at the cord's top."""
    s = Mesh()
    # two blades crossing at the pivot, a few degrees open, mirrored about x
    for sign, ang in ((1.0, 4.0), (-1.0, -4.0)):
        b = blade(sign)
        c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        R = np.array([[c, 0, sn], [0, 1, 0], [-sn, 0, c]])
        s.extend(b.moved(R, np.zeros(3)))
    # shanks up from the pivot to the finger rings
    shank = SHEAR_LEN - BLADE_LEN - 2.0 * RING_R
    for sign in (1.0, -1.0):
        path = np.array([[0.0, 0.0, 0.0], [sign * 0.004, 0.0, shank * 0.5], [sign * 0.008, 0.0, shank]])
        s.extend(tube(path, lambda t, a: RING_T * (1.1 - 0.2 * t), 6, mat="shears_iron"))
        s.extend(ring(np.array([sign * (0.008 + RING_R * 0.6), 0.0, shank + RING_R]), np.array([0.0, 1.0, 0.0]),
                      RING_R, RING_T * 0.6, "shears_iron", seg=16, around=6, stretch=(0.85, 1.0)))
    # the pivot rivet
    s.extend(ring(np.zeros(3), np.array([0.0, 1.0, 0.0]), 0.0018, 0.0012, "shears_iron", seg=8, around=5))
    # the cord: through the left ring's top, up to the hang point
    ring_top = np.array([0.008 + RING_R * 0.6, 0.0, shank + 2.0 * RING_R])
    k = np.linspace(0.0, 1.0, 9)
    path = np.stack([ring_top[0] * (1 - k) + 0.0 * k, 0.0015 * np.sin(math.pi * k),
                     ring_top[2] + CORD_LEN * k], axis=1)
    s.extend(tube(path, lambda t, a: CORD_R, 6, mat="cord"))
    top = float(np.asarray(s.V)[:, 2].max())
    return s.moved(np.eye(3), np.array([0.0, 0.0, -top]))


def material(name: str) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    hx, rough, metal = MATERIALS[name]
    rgb = [int(hx[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    mat.diffuse_color = (*[c ** 2.2 for c in rgb], 1.0)
    mat.roughness = rough
    mat.metallic = metal
    return mat


def make_object(name: str, m: Mesh) -> bpy.types.Object:
    me = bpy.data.meshes.new(name)
    me.from_pydata(m.V, [], m.F)
    names = sorted(set(m.M), key=list(MATERIALS).index)
    for n in names:
        me.materials.append(material(n))
    idx = {n: i for i, n in enumerate(names)}
    for p, mm in zip(me.polygons, m.M):
        p.material_index = idx[mm]
        p.use_smooth = True
    uvl = me.uv_layers.new(name="UVMap")
    uvl.data.foreach_set("uv", [x for face in m.UV for c in face for x in (c[0], 1.0 - c[1])])
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def export(ob: bpy.types.Object, path: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.gltf(
        filepath=str(path), export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
        export_tangents=False, export_normals=True, export_texcoords=True, export_extras=False, export_skins=False,
        export_morph=False, export_animations=False, export_materials="EXPORT", export_vertex_color="NONE")


def write_material(out: Path, name: str) -> None:
    hx, rough, metal = MATERIALS[name]
    r, g, b = (int(hx[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    body = (f'[gd_resource type="StandardMaterial3D" format=3]\n\n[resource]\nresource_name = "{name}"\n'
            f"albedo_color = Color({r:.3f}, {g:.3f}, {b:.3f}, 1)\nmetallic = {metal}\nroughness = {rough}\n")
    (out / f"{name}.tres").write_text(body, encoding="utf-8")


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="wick.py")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    out = Path(args.out_dir).resolve() if args.out_dir else OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    (out / "materials").mkdir(exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for name, build in (("wick", wick), ("wick_bundle", wick_bundle), ("trimming_shears", trimming_shears)):
        m = build()
        ob = make_object(name.title().replace("_", ""), m)
        path = out / f"{name}.glb"
        export(ob, path)
        log(f"{path.name}: {m.tris()} tris, {path.stat().st_size} bytes")
    for name in MATERIALS:
        write_material(out / "materials", name)
    log(f"wrote {len(MATERIALS)} materials")
    return 0


if __name__ == "__main__":
    sys.exit(main())
