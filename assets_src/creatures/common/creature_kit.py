"""Shared kit for the procedural battle creatures (M2-CRE-02). docs/kb/art/creatures/pipeline.md.

Everything is authored in **Godot axes** (x right, y up, the creature facing +z) and in metres, and is converted
to Blender's axes only at export. The geometry is pure numpy, so it is deterministic; Blender is used only to
build the armature, the skin and the clips and to write the glTF.

Vertex data (read by game/shaders/creature/creature.gdshader):
  COLOR_0.rgb  albedo, sRGB-encoded palette colour
  COLOR_0.a    wetness 0 (dry) .. 1 (wet)
  TEXCOORD_0   a rest-pose detail coordinate (metres), the domain of the shader's noise
  TEXCOORD_1   x: cavity 0 (open) .. 1 (deep crevice); y: emission mask 0 .. 1 (the wounds)

A part is skinned to at most two bones (JOINTS_0 / WEIGHTS_0).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

FPS = 30
# Strike clips play in place (battle-presentation's clip contract, M2-BPR-02): the sequencer moves the fighter to its
# target, so the root bone keeps no horizontal travel in these. Vertical travel (a dive, a hop) and body leans stay.
IN_PLACE_CLIPS = ("attack", "cast")


def hexrgb(h: str) -> np.ndarray:
    """'#RRGGBB' -> sRGB floats (0..1)."""
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float64)


def mix(a, b, t):
    return np.asarray(a) * (1.0 - t) + np.asarray(b) * t


def smoothstep(e0: float, e1: float, x):
    t = np.clip((np.asarray(x, dtype=np.float64) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def rot_x(deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float64)


def rot_y(deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float64)


def rot_z(deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)


def euler(rx: float, ry: float, rz: float) -> np.ndarray:
    """X first, then Y, then Z, about fixed (rest) axes."""
    return rot_z(rz) @ rot_y(ry) @ rot_x(rx)


def value_noise(p: np.ndarray, seed: int) -> np.ndarray:
    """Deterministic 3D value noise in [-1, 1] at points p (N, 3); a hash lattice, trilinear, smoothed."""
    p = np.asarray(p, dtype=np.float64)
    i = np.floor(p).astype(np.int64)
    f = p - i
    f = f * f * (3.0 - 2.0 * f)

    def h(ix, iy, iz):
        n = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
        n = (n ^ (n >> 13)) * 1274126177
        n = n ^ (n >> 16)
        return ((n & 0xFFFF).astype(np.float64) / 32767.5) - 1.0

    out = np.zeros(len(p))
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out += w * h(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz)
    return out


def fbm(p: np.ndarray, seed: int, octaves: int = 3) -> np.ndarray:
    out = np.zeros(len(p))
    amp, freq = 0.5, 1.0
    for o in range(octaves):
        out += amp * value_noise(np.asarray(p) * freq, seed + o * 17)
        amp *= 0.5
        freq *= 2.03
    return out


# ---------------------------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------------------------
@dataclass
class Mesh:
    """One skinned mesh: vertices with colour, detail UV, cavity/emission UV2 and two bone influences."""

    name: str
    materials: list[str] = field(default_factory=list)
    pos: list = field(default_factory=list)
    nrm: list = field(default_factory=list)
    col: list = field(default_factory=list)
    uv: list = field(default_factory=list)
    uv2: list = field(default_factory=list)
    joints: list = field(default_factory=list)
    weights: list = field(default_factory=list)
    tris: list = field(default_factory=list)
    tri_mat: list = field(default_factory=list)
    count: int = 0

    def material(self, name: str) -> int:
        if name not in self.materials:
            self.materials.append(name)
        return self.materials.index(name)

    def add(self, P, N, C, UV, UV2, J, W, T, mat: str) -> int:
        """Appends vertices (arrays of equal length) and local triangles T (M, 3); returns the base index."""
        base = self.count
        n = len(P)
        self.pos.append(np.asarray(P, dtype=np.float64))
        self.nrm.append(np.asarray(N, dtype=np.float64))
        self.col.append(np.asarray(C, dtype=np.float64))
        self.uv.append(np.asarray(UV, dtype=np.float64))
        self.uv2.append(np.asarray(UV2, dtype=np.float64))
        self.joints.append(np.asarray(J, dtype=np.int64))
        self.weights.append(np.asarray(W, dtype=np.float64))
        T = np.asarray(T, dtype=np.int64) + base
        self.tris.append(T)
        self.tri_mat.append(np.full(len(T), self.material(mat), dtype=np.int64))
        self.count += n
        return base

    def arrays(self) -> dict:
        cat = np.concatenate
        return {
            "pos": cat(self.pos), "nrm": cat(self.nrm), "col": cat(self.col), "uv": cat(self.uv),
            "uv2": cat(self.uv2), "joints": cat(self.joints), "weights": cat(self.weights),
            "tris": cat(self.tris), "tri_mat": cat(self.tri_mat),
        }

    @property
    def triangle_count(self) -> int:
        return int(sum(len(t) for t in self.tris))


def grid_tris(rows: int, cols: int, wrap: bool) -> np.ndarray:
    """Triangles for a rows x cols vertex grid (row-major); `wrap` joins the last column to the first."""
    out = []
    cmax = cols if wrap else cols - 1
    for r in range(rows - 1):
        for c in range(cmax):
            c1 = (c + 1) % cols
            a, b = r * cols + c, r * cols + c1
            d, e = (r + 1) * cols + c, (r + 1) * cols + c1
            out.append((a, d, b))
            out.append((b, d, e))
    return np.asarray(out, dtype=np.int64)


def vertex_normals(P: np.ndarray, T: np.ndarray) -> np.ndarray:
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    N = np.zeros_like(P)
    for k in range(3):
        np.add.at(N, T[:, k], fn)
    ln = np.linalg.norm(N, axis=1, keepdims=True)
    ln[ln < 1e-12] = 1.0
    return N / ln


def weld_normals(P: np.ndarray, N: np.ndarray, quantum: float = 1e-5) -> np.ndarray:
    """Averages normals of coincident vertices (a wrapped seam, a pole), so a part shades smoothly across them."""
    key = np.round(P / quantum).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    acc = np.zeros((inv.max() + 1, 3))
    np.add.at(acc, inv, N)
    out = acc[inv]
    ln = np.linalg.norm(out, axis=1, keepdims=True)
    ln[ln < 1e-12] = 1.0
    return out / ln


@dataclass
class Shade:
    """How a part is coloured: a base colour and per-vertex functions of the rest position."""

    color: np.ndarray
    wet: float = 0.0
    cavity: float = 0.0
    emission: float = 0.0


def finish(mesh: Mesh, P: np.ndarray, T: np.ndarray, mat: str, color, bones, *, wet=0.0, cavity=0.0,
           emission=0.0, uv=None, flat: bool = False, N: np.ndarray | None = None) -> int:
    """Adds a part. `color` is an (3,) or (n, 3) sRGB array, `wet`/`cavity`/`emission` scalars or (n,) arrays,
    `bones` a function P -> (J (n, 2), W (n, 2)) or a (bone index) int for a rigid part."""
    P = np.asarray(P, dtype=np.float64)
    T = np.asarray(T, dtype=np.int64)
    n = len(P)
    color = np.asarray(color, dtype=np.float64)
    C = np.zeros((n, 4))
    C[:, :3] = np.broadcast_to(color, (n, 3)) if color.ndim == 1 else color
    C[:, 3] = np.broadcast_to(np.asarray(wet, dtype=np.float64), (n,))
    UV2 = np.zeros((n, 2))
    UV2[:, 0] = np.broadcast_to(np.asarray(cavity, dtype=np.float64), (n,))
    UV2[:, 1] = np.broadcast_to(np.asarray(emission, dtype=np.float64), (n,))
    if uv is None:
        uv = np.column_stack([P[:, 0] + P[:, 2] * 0.71, P[:, 1] - P[:, 2] * 0.37])
    uv = np.asarray(uv, dtype=np.float64)
    if isinstance(bones, int):
        J = np.tile([bones, 0], (n, 1))
        W = np.tile([1.0, 0.0], (n, 1))
    else:
        J, W = bones(P)
    if flat:  # faceted: every triangle gets its own vertices and its face normal
        idx = T.reshape(-1)
        fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
        fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
        P, C, UV2, uv, J, W = P[idx], C[idx], UV2[idx], uv[idx], J[idx], W[idx]
        N = np.repeat(fn, 3, axis=0)
        T = np.arange(len(P)).reshape(-1, 3)
    elif N is None:
        N = weld_normals(P, vertex_normals(P, T))
    return mesh.add(P, N, C, uv, UV2, J, W, T, mat)


def lathe(profile: list[tuple[float, float]], segs: int) -> tuple[np.ndarray, np.ndarray]:
    """A surface of revolution about +y: `profile` is [(radius, y)] from one end to the other.
    Returns (P (rows*segs, 3), T); rows run along the profile. A radius of 0 is a pole."""
    a = np.arange(segs) * (2.0 * math.pi / segs)
    rows = []
    for r, y in profile:
        rows.append(np.column_stack([r * np.sin(a), np.full(segs, y), r * np.cos(a)]))
    P = np.vstack(rows)
    return P, grid_tris(len(profile), segs, True)


def ellipsoid(center, radii, rings: int = 10, segs: int = 16) -> tuple[np.ndarray, np.ndarray]:
    """An ellipsoid (poles on y). Returns (P, T)."""
    prof = []
    for i in range(rings + 1):
        th = math.pi * i / rings
        prof.append((math.sin(th), math.cos(th)))  # top pole to bottom pole: lathe() winds that outward
    P, T = lathe(prof, segs)
    P = P * np.asarray(radii, dtype=np.float64) + np.asarray(center, dtype=np.float64)
    return P, T


def frames_along(path: np.ndarray, up_hint=(0.0, 1.0, 0.0)) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Parallel-transport frames (tangent, normal, binormal) along a polyline path (K, 3)."""
    path = np.asarray(path, dtype=np.float64)
    K = len(path)
    tan = np.gradient(path, axis=0)
    tan /= np.linalg.norm(tan, axis=1, keepdims=True)
    up = np.asarray(up_hint, dtype=np.float64)
    if abs(float(np.dot(up, tan[0]))) > 0.95:
        up = np.array([1.0, 0.0, 0.0]) if abs(tan[0][0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    nrm = np.zeros_like(path)
    n0 = up - np.dot(up, tan[0]) * tan[0]
    nrm[0] = n0 / np.linalg.norm(n0)
    for k in range(1, K):
        n = nrm[k - 1] - np.dot(nrm[k - 1], tan[k]) * tan[k]
        ln = np.linalg.norm(n)
        nrm[k] = n / ln if ln > 1e-9 else nrm[k - 1]
    bin_ = np.cross(tan, nrm)
    return tan, nrm, bin_


def tube(path, radius, segs: int = 12, cap_start: bool = True, cap_end: bool = True,
         up_hint=(0.0, 1.0, 0.0), squash: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """A tube along `path` (K, 3) with `radius` a scalar or (K,) array; `squash` scales the binormal axis
    (an oval section). The rings run along the path, ring k at path[k]. Ends close to a point when capped."""
    path = np.asarray(path, dtype=np.float64)
    K = len(path)
    rad = np.broadcast_to(np.asarray(radius, dtype=np.float64), (K,))
    tan, nrm, bin_ = frames_along(path, up_hint)
    a = np.arange(segs) * (2.0 * math.pi / segs)
    ca, sa = np.cos(a), np.sin(a)
    rings = [path[k] + rad[k] * (np.outer(ca, nrm[k]) + squash * np.outer(sa, bin_[k])) for k in range(K)]
    P = np.vstack(rings)
    T = flip(grid_tris(K, segs, True))  # outward-facing
    extra = []
    if cap_start:
        extra.append((path[0] - tan[0] * rad[0] * 0.35, 0))
    if cap_end:
        extra.append((path[-1] + tan[-1] * rad[-1] * 0.35, K - 1))
    tris = [T]
    for tip, ring in extra:
        idx = len(P)
        P = np.vstack([P, tip[None]])
        r0 = ring * segs
        cap = []
        for s in range(segs):
            s1 = (s + 1) % segs
            cap.append((r0 + s, idx, r0 + s1) if ring == 0 else (r0 + s, r0 + s1, idx))
        tris.append(np.asarray(cap, dtype=np.int64))
    return P, np.vstack(tris)


def flip(T: np.ndarray) -> np.ndarray:
    return np.asarray(T)[:, ::-1].copy()


def transform(P: np.ndarray, R: np.ndarray | None = None, t=(0.0, 0.0, 0.0), s=1.0) -> np.ndarray:
    P = np.asarray(P, dtype=np.float64) * s
    if R is not None:
        P = P @ np.asarray(R).T
    return P + np.asarray(t, dtype=np.float64)


def bezier(pts, n: int) -> np.ndarray:
    """n points on a cubic (or any degree) Bezier curve through control points `pts`."""
    pts = np.asarray(pts, dtype=np.float64)
    t = np.linspace(0.0, 1.0, n)[:, None]
    d = len(pts) - 1
    out = np.zeros((n, 3))
    for i, p in enumerate(pts):
        out += math.comb(d, i) * (t ** i) * ((1 - t) ** (d - i)) * p
    return out


# ---------------------------------------------------------------------------------------------
# Rig and clips
# ---------------------------------------------------------------------------------------------
@dataclass
class Bone:
    name: str
    head: tuple
    tail: tuple
    parent: str | None = None


@dataclass
class Rig:
    bones: list[Bone] = field(default_factory=list)

    def add(self, name: str, head, tail, parent: str | None = None) -> int:
        self.bones.append(Bone(name, tuple(float(v) for v in head), tuple(float(v) for v in tail), parent))
        return len(self.bones) - 1

    def index(self, name: str) -> int:
        for i, b in enumerate(self.bones):
            if b.name == name:
                return i
        raise KeyError(name)

    def rigid(self, name: str):
        return self.index(name)

    def blend(self, a: str, b: str, axis_from, axis_to):
        """A two-bone blend along a segment: weight goes from bone a at axis_from to bone b at axis_to."""
        ia, ib = self.index(a), self.index(b)
        p0, p1 = np.asarray(axis_from, dtype=np.float64), np.asarray(axis_to, dtype=np.float64)
        d = p1 - p0

        def f(P):
            t = np.clip(((P - p0) @ d) / float(d @ d), 0.0, 1.0)
            w = smoothstep(0.0, 1.0, t)
            J = np.tile([ia, ib], (len(P), 1))
            W = np.column_stack([1.0 - w, w])
            return J, W

        return f

    def chain(self, names: list[str], points):
        """Skin along a chain: names[k] owns the span from points[k] to points[k+1] (one bone per span, blended
        with the next bone across the span's last third)."""
        idx = [self.index(n) for n in names]
        pts = np.asarray(points, dtype=np.float64)

        def f(P):
            n = len(P)
            best_k = np.zeros(n, dtype=np.int64)
            best_t = np.zeros(n)
            best_d = np.full(n, np.inf)
            for k in range(len(idx)):
                a, b = pts[k], pts[k + 1]
                d = b - a
                t = np.clip(((P - a) @ d) / float(d @ d), 0.0, 1.0)
                q = a + t[:, None] * d
                dist = np.linalg.norm(P - q, axis=1)
                better = dist < best_d - 1e-12
                best_d = np.where(better, dist, best_d)
                best_k = np.where(better, k, best_k)
                best_t = np.where(better, t, best_t)
            J = np.zeros((n, 2), dtype=np.int64)
            W = np.zeros((n, 2))
            for v in range(n):
                k = int(best_k[v])
                t = float(best_t[v])
                J[v, 0] = idx[k]
                if k + 1 < len(idx) and t > 0.66:
                    w = float(smoothstep(0.66, 1.0, t)) * 0.5
                    J[v, 1] = idx[k + 1]
                    W[v] = (1.0 - w, w)
                elif k > 0 and t < 0.34:
                    w = float(smoothstep(0.34, 0.0, t)) * 0.5
                    J[v, 1] = idx[k - 1]
                    W[v] = (1.0 - w, w)
                else:
                    J[v, 1] = idx[k]
                    W[v] = (1.0, 0.0)
            return J, W

        return f


@dataclass
class Clip:
    """A clip: per bone, keys (t seconds, (rx, ry, rz) degrees about the rest axes, (x, y, z) metres offset).
    Keys ease in and out (a smooth hold at each key). A looping clip should end where it starts."""

    name: str
    length: float
    loop: bool = False
    keys: dict = field(default_factory=dict)

    def key(self, bone: str, t: float, rot=(0.0, 0.0, 0.0), loc=(0.0, 0.0, 0.0)) -> "Clip":
        self.keys.setdefault(bone, []).append((float(t), tuple(float(v) for v in rot), tuple(float(v) for v in loc)))
        return self

    def wave(self, bone: str, amp_rot=(0.0, 0.0, 0.0), amp_loc=(0.0, 0.0, 0.0), cycles: float = 1.0,
             phase: float = 0.0, base_rot=(0.0, 0.0, 0.0), base_loc=(0.0, 0.0, 0.0), steps: int = 12) -> "Clip":
        """A sinusoid over the whole clip (an idle's breath or sway), keyed `steps` times per cycle."""
        n = max(int(round(steps * cycles)), 2)
        for i in range(n + 1):
            t = self.length * i / n
            s = math.sin(2.0 * math.pi * (cycles * i / n) + phase)
            self.key(bone, t, tuple(b + a * s for a, b in zip(amp_rot, base_rot)),
                     tuple(b + a * s for a, b in zip(amp_loc, base_loc)))
        return self

    def sample(self, bone: str, t: float) -> tuple[np.ndarray, np.ndarray]:
        ks = sorted(self.keys.get(bone, []), key=lambda k: k[0])
        if not ks:
            return np.zeros(3), np.zeros(3)
        if t <= ks[0][0]:
            return np.asarray(ks[0][1]), np.asarray(ks[0][2])
        for a, b in zip(ks, ks[1:]):
            if a[0] <= t <= b[0]:
                span = b[0] - a[0]
                u = 0.0 if span <= 0 else (t - a[0]) / span
                u = u * u * (3.0 - 2.0 * u)
                return mix(a[1], b[1], u), mix(a[2], b[2], u)
        return np.asarray(ks[-1][1]), np.asarray(ks[-1][2])


# ---------------------------------------------------------------------------------------------
# Blender export (bpy imported lazily, inside Blender only)
# ---------------------------------------------------------------------------------------------
G2B = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])  # Godot (x, y, z) -> Blender (x, -z, y)



def pose_of(build) -> dict:
    """A pose as {bone: (rot, loc)}, read from a one-key scratch clip that `build` keys at t = 0."""
    c = Clip("_pose", 1.0)
    build(c)
    return {b: (np.asarray(ks[0][1], float), np.asarray(ks[0][2], float)) for b, ks in c.keys.items()}


def in_pose(base: Clip, name: str, pose: dict) -> Clip:
    """`base` played from `pose`: the pose is added to every key of its bones, and held on bones `base` leaves alone."""
    out = Clip(name, base.length, loop=base.loop)
    zero = (np.zeros(3), np.zeros(3))
    for b, ks in base.keys.items():
        pr, pl = pose.get(b, zero)
        for t, r, l in ks:
            out.key(b, t, tuple(np.asarray(r, float) + pr), tuple(np.asarray(l, float) + pl))
    for b, (pr, pl) in pose.items():
        if b not in base.keys:
            out.key(b, 0.0, tuple(pr), tuple(pl))
            out.key(b, base.length, tuple(pr), tuple(pl))
    return out


def _g2b(v) -> np.ndarray:
    return np.asarray(v, dtype=np.float64) @ G2B.T


def export_creature(mesh: Mesh, rig: Rig, clips: list[Clip], out_path: str, extra_meshes: list | None = None,
                    extras: dict | None = None) -> dict:
    """Writes the skinned creature, its rig and its clips (one glTF animation per clip) to a .glb.
    `extra_meshes`: further skinned meshes (e.g. a broken-rim variant) in the same rig."""
    import bpy  # noqa: PLC0415
    from mathutils import Matrix, Quaternion  # noqa: PLC0415

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS

    arm_data = bpy.data.armatures.new("Armature")
    arm = bpy.data.objects.new("Armature", arm_data)
    scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for b in rig.bones:
        eb = arm_data.edit_bones.new(b.name)
        eb.head = tuple(_g2b(b.head))
        eb.tail = tuple(_g2b(b.tail))
        eb.roll = 0.0
        if b.parent:
            eb.parent = arm_data.edit_bones[b.parent]
            eb.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")

    for m in [mesh] + list(extra_meshes or []):
        _mesh_object(m, rig, arm)

    rest = {b.name: np.array(arm_data.bones[b.name].matrix_local.to_3x3()) for b in rig.bones}
    arm.animation_data_create()
    names = []
    for clip in clips:
        act = bpy.data.actions.new(clip.name)
        act.use_fake_user = True
        arm.animation_data.action = act
        frames = max(int(round(clip.length * FPS)), 1)
        for f in range(frames + 1):
            t = min(f / FPS, clip.length)
            for b in rig.bones:
                pb = arm.pose.bones[b.name]
                pb.rotation_mode = "QUATERNION"
                rdeg, loc = clip.sample(b.name, t)
                if b.name == "root" and clip.name in IN_PLACE_CLIPS:
                    loc = np.array([0.0, loc[1], 0.0])
                W = G2B @ euler(*rdeg) @ G2B.T
                R = rest[b.name]
                local = R.T @ W @ R
                q = Matrix(local.tolist()).to_quaternion()
                if q.w < 0:
                    q = Quaternion((-q.w, -q.x, -q.y, -q.z))
                pb.rotation_quaternion = q
                pb.location = tuple(R.T @ _g2b(loc))
                pb.scale = (1.0, 1.0, 1.0)
                pb.keyframe_insert("rotation_quaternion", frame=f + 1)
                pb.keyframe_insert("location", frame=f + 1)
                pb.keyframe_insert("scale", frame=f + 1)
        track = arm.animation_data.nla_tracks.new()
        track.name = clip.name
        strip = track.strips.new(clip.name, 1, act)
        strip.name = clip.name
        arm.animation_data.action = None
        names.append(clip.name)
    for pb in arm.pose.bones:
        pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        pb.location = (0.0, 0.0, 0.0)
    for k, v in (extras or {}).items():
        arm[k] = v

    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_texcoords=True,
        export_normals=True,
        export_tangents=False,
        export_vertex_color="ACTIVE",
        export_all_vertex_colors=False,
        export_materials="EXPORT",
        export_image_format="NONE",
        export_cameras=False,
        export_lights=False,
        export_skins=True,
        export_animations=True,
        export_animation_mode="NLA_TRACKS",
        export_force_sampling=True,
        export_frame_step=1,
        export_def_bones=False,
        export_optimize_animation_size=False,
        export_extras=bool(extras),
    )
    return {"triangles": mesh.triangle_count + sum(m.triangle_count for m in extra_meshes or []),
            "vertices": mesh.count, "bones": len(rig.bones), "clips": names}


def _mesh_object(m: Mesh, rig: Rig, arm):
    import bpy  # noqa: PLC0415

    a = m.arrays()
    me = bpy.data.meshes.new(m.name)
    bpos = _g2b(a["pos"])
    tris = a["tris"]
    me.vertices.add(len(bpos))
    me.vertices.foreach_set("co", bpos.astype(np.float32).ravel())
    me.loops.add(len(tris) * 3)
    me.loops.foreach_set("vertex_index", tris.astype(np.int32).ravel())
    me.polygons.add(len(tris))
    me.polygons.foreach_set("loop_start", (np.arange(len(tris)) * 3).astype(np.int32))
    me.polygons.foreach_set("material_index", a["tri_mat"].astype(np.int32))
    me.update(calc_edges=True)
    me.validate(clean_customdata=False)
    loop_v = tris.ravel()
    uv0 = a["uv"][loop_v].copy()
    uv1 = a["uv2"][loop_v].copy()
    uv0[:, 1] = 1.0 - uv0[:, 1]
    uv1[:, 1] = 1.0 - uv1[:, 1]
    l0 = me.uv_layers.new(name="UVMap")
    l0.data.foreach_set("uv", uv0.astype(np.float32).ravel())
    l1 = me.uv_layers.new(name="UV2")
    l1.data.foreach_set("uv", uv1.astype(np.float32).ravel())
    me.uv_layers.active = l0
    ca = me.color_attributes.new("Color", "FLOAT_COLOR", "POINT")
    ca.data.foreach_set("color", a["col"].astype(np.float32).ravel())
    me.color_attributes.active_color = ca
    for name in m.materials:
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        me.materials.append(mat)
    me.normals_split_custom_set_from_vertices(_g2b(a["nrm"]).astype(np.float32).tolist())
    ob = bpy.data.objects.new(m.name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = arm
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    groups = [ob.vertex_groups.new(name=b.name) for b in rig.bones]
    J, W = a["joints"], a["weights"]
    for v in range(len(J)):
        for k in range(2):
            if W[v, k] > 1e-6:
                groups[int(J[v, k])].add([v], float(W[v, k]), "REPLACE")
    return ob
