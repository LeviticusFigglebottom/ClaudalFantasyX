"""Procedural test meshes for the M1-RND-04 character shaders (headless Blender 5.0).

    ~/.cache/hymn/blender-5.0.1+dfsg-5/blender --background --factory-startup \
        --python assets_src/characters/shader_test/build_shader_test_meshes.py

Writes assets/characters/shader_test/shader_test_bust.glb (head with facial relief, ears, lids and
neck; eyeballs, cornea shells, eye-occlusion shells and tear lines as separate nodes with their
origin at the eyeball centre; hair cards; a lacquer collar) and shader_test_cloth.glb (a hanging
drape and a verse-sleeve tube). Everything is generated from math in this file and layout.py; no
input data. Deterministic: a fixed seed drives every random choice.

These are shader test props, not the hero. The production Asha comes from the character stream.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import layout as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "assets" / "characters" / "shader_test"
SEED = 41


def gauss(x: float, z: float, cx: float, cz: float, sx: float, sz: float) -> float:
    return math.exp(-(((x - cx) / sx) ** 2) - ((z - cz) / sz) ** 2)


def smoothstep(e0: float, e1: float, x: float) -> float:
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3.0 - 2.0 * t)


def new_object(name: str, bm: bmesh.types.BMesh, location=(0.0, 0.0, 0.0)) -> bpy.types.Object:
    # Triangulate here with a fixed rule: the exporter's own triangulation is not byte-stable
    # between runs, and the assets must regenerate identically (PROVENANCE).
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="FIXED", ngon_method="EAR_CLIP")
    # bmesh operators order their output by pointer hashes; sort faces by vertex indices instead.
    # Blender 5's BMElemSeq.sort needs a number from `key` (M1-RND-14), so rank the tuple keys first.
    bm.verts.index_update()
    bm.faces.index_update()
    keys = {f.index: tuple(sorted(v.index for v in f.verts)) for f in bm.faces}
    rank = {i: r for r, i in enumerate(sorted(keys, key=lambda i: keys[i]))}
    bm.faces.sort(key=lambda f: rank[f.index])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    bpy.context.scene.collection.objects.link(ob)
    return ob


def set_vertex_colors(ob: bpy.types.Object, fn) -> None:
    """fn(vertex_index, co) -> (r, g, b, a); stored per point as the active colour attribute."""
    me = ob.data
    attr = me.color_attributes.new(name="Color", type="FLOAT_COLOR", domain="POINT")
    for i, v in enumerate(me.vertices):
        attr.data[i].color = fn(i, v.co)
    me.color_attributes.active_color = attr


# ------------------------------------------------------------------------------------------------
# Head
# ------------------------------------------------------------------------------------------------
def face_offset(x: float, z: float) -> float:
    """Forward (-Y) displacement of the front surface at (x, z), in metres."""
    off = 0.0
    for side in (-1.0, 1.0):
        off += 0.0042 * gauss(x, z, side * 0.030, 0.031, 0.022, 0.007)  # brow ridge
        off += 0.0060 * gauss(x, z, side * 0.046, -0.010, 0.017, 0.014)  # cheekbone
        off -= 0.0040 * gauss(x, z, side * 0.043, -0.052, 0.014, 0.016)  # cheek hollow
        off += 0.0050 * gauss(x, z, side * 0.0115, -0.031, 0.0055, 0.0050)  # nostril wing
        off += 0.0022 * gauss(x, z, side * 0.020, -0.060, 0.004, 0.004)  # mouth corner
        off -= 0.0010 * gauss(x, z, side * 0.031, 0.027, 0.015, 0.0030)  # lid crease
    # Nose: a ridge from the bridge to the tip, widening downward.
    t = smoothstep(0.022, -0.030, z)
    width = 0.0055 + 0.0055 * t
    ridge = (0.004 + 0.011 * t * t) * math.exp(-((x / width) ** 2))
    ridge *= (1.0 - smoothstep(-0.030, -0.040, z)) * (1.0 - smoothstep(0.018, 0.03, z))
    off += ridge
    off += 0.0030 * gauss(x, z, 0.0, -0.030, 0.008, 0.007)  # tip
    off += 0.0030 * gauss(x, z, 0.0, -0.042, 0.007, 0.005)  # philtrum fills under the nose
    # Maxilla / mouth volume: the face below the nose comes forward of the ellipsoid.
    off += 0.013 * gauss(x, z, 0.0, -0.044, 0.030, 0.030)
    # Lips and chin.
    off += 0.0030 * gauss(x, z, 0.0, -0.0530, 0.018, 0.0045)
    off += 0.0065 * gauss(x, z, 0.0, -0.0650, 0.017, 0.0055)
    off -= 0.0016 * gauss(x, z, 0.0, -0.0588, 0.020, 0.0012)  # mouth line
    off -= 0.0030 * gauss(x, z, 0.0, -0.0760, 0.012, 0.004)  # mentolabial fold
    off += 0.0200 * gauss(x, z, 0.0, -0.0880, 0.026, 0.020)  # mandible / chin volume
    off += 0.0040 * gauss(x, z, 0.0, -0.0950, 0.014, 0.008)  # chin point
    off -= 0.0040 * gauss(x, z, 0.0, 0.020, 0.012, 0.006)  # nasal root (between the eyes)
    return off


def socket_depth(x: float, z: float) -> float:
    """How far the skin sinks into each eye socket, hidden behind the lid skirt (add_lids)."""
    depth = 0.0
    for side in (-1.0, 1.0):
        depth += L.EYE_RECESS * (1.0 - smoothstep(1.0, L.LID_SKIRT_FIELD, L.almond(x, z, side)))
    return depth


def head_surface(d: Vector, socket: bool = True) -> Vector:
    """Deformed head surface point for the unit sphere direction d."""
    x, y, z = d.x * L.HEAD_RX, d.y * L.HEAD_RY, d.z * L.HEAD_RZ
    # Jaw and chin taper; flatter sides; slightly fuller back of the skull.
    jaw = smoothstep(-0.015, -0.11, z)
    x *= 1.0 - 0.24 * jaw
    y *= 1.0 - 0.10 * jaw * (1.0 if y < 0 else 0.4)
    if y > 0.0:
        y *= 1.0 + 0.06 * smoothstep(-0.02, 0.06, z)
    front = smoothstep(0.15, 0.6, -d.y)
    off = face_offset(x, z) - (socket_depth(x, z) if socket else 0.0)
    return Vector((x, y - off * front, z))


def head_front_point(x: float, z: float, socket: bool = True) -> Vector:
    """Head surface point in front of (x, z); valid in the eye region (no jaw taper there)."""
    sx, sz = x / L.HEAD_RX, z / L.HEAD_RZ
    d = Vector((sx, -math.sqrt(max(0.0, 1.0 - sx * sx - sz * sz)), sz))
    return head_surface(d.normalized(), socket)


def head_uv_of(p: Vector) -> tuple[float, float]:
    d = Vector((p.x / L.HEAD_RX, p.y / L.HEAD_RY, p.z / L.HEAD_RZ)).normalized()
    u, v = L.ellipsoid_dir_to_uv(d.x, d.y, d.z)
    return u, 1.0 - v


def build_head() -> bpy.types.Object:
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=L.HEAD_SEG_U, v_segments=L.HEAD_SEG_V, radius=1.0)
    uv_layer = bm.loops.layers.uv.new("UVMap")
    dirs = {v: v.co.normalized() for v in bm.verts}
    for v in bm.verts:
        v.co = head_surface(dirs[v])
        x, z = v.co.x, v.co.z
        outside_skirts = min(L.almond(x, z, -1.0), L.almond(x, z, 1.0)) > L.LID_SKIRT_FIELD
        if dirs[v].y < -0.5 and outside_skirts:
            v.co = push_out_of_eyes(v.co, 0.0006)
    for f in bm.faces:
        for loop in f.loops:
            d = dirs[loop.vert]
            u, vv = L.ellipsoid_dir_to_uv(d.x, d.y, d.z)
            loop[uv_layer].uv = (u, 1.0 - vv)
        # Fix the seam: faces straddling U = 0/1 get their low U values wrapped.
        us = [lp[uv_layer].uv.x for lp in f.loops]
        if max(us) - min(us) > 0.5:
            for lp in f.loops:
                if lp[uv_layer].uv.x < 0.5:
                    lp[uv_layer].uv.x += 1.0
    add_ears(bm, uv_layer)
    add_neck(bm, uv_layer)
    add_lids(bm, uv_layer)
    return new_object("Head", bm)


def add_ears(bm: bmesh.types.BMesh, uv_layer) -> None:
    """Thin flattened ellipsoids (3 mm at the rim): the transmission test for the skin shader."""
    u0, v0, u1, v1 = L.EAR_UV
    for side in (-1.0, 1.0):
        ear = bmesh.new()
        bmesh.ops.create_uvsphere(ear, u_segments=32, v_segments=24, radius=1.0)
        for v in ear.verts:
            d = v.co.copy()
            rim = abs(d.x) < 0.3 and (d.y * d.y + d.z * d.z) > 0.8
            v.co = Vector((d.x * (0.0045 if not rim else 0.003), d.y * 0.017, d.z * 0.030))
        rot = Matrix.Rotation(math.radians(-14.0 * side), 3, "Z")
        bmesh.ops.rotate(ear, verts=ear.verts, cent=(0, 0, 0), matrix=rot)
        bmesh.ops.translate(ear, verts=ear.verts, vec=Vector((side * (L.HEAD_RX * 0.97), 0.008, 0.002)))
        mapping = {}
        for v in ear.verts:
            mapping[v] = bm.verts.new(v.co)
        for f in ear.faces:
            nf = bm.faces.new([mapping[v] for v in f.verts])
            for lp in nf.loops:
                co = lp.vert.co
                lp[uv_layer].uv = (
                    u0 + (u1 - u0) * (0.5 + (co.y - 0.008) / 0.04),
                    1.0 - (v0 + (v1 - v0) * (0.5 - (co.z - 0.002) / 0.066)),
                )
        ear.free()


def add_neck(bm: bmesh.types.BMesh, uv_layer) -> None:
    u0, v0, u1, v1 = L.NECK_UV
    seg_a, seg_h = 64, 16
    z_top, z_bot = -0.055, -0.26
    rows = []
    for j in range(seg_h + 1):
        t = j / seg_h
        z = z_top + (z_bot - z_top) * t
        flare = 1.0 + 0.35 * smoothstep(0.75, 1.0, t)  # into the shoulders
        rows.append(
            [
                bm.verts.new(
                    Vector(
                        (
                            0.050 * flare * math.cos(2 * math.pi * i / seg_a),
                            0.012 + 0.055 * flare * math.sin(2 * math.pi * i / seg_a),
                            z,
                        )
                    )
                )
                for i in range(seg_a)
            ]
        )
    for j in range(seg_h):
        for i in range(seg_a):
            i2 = (i + 1) % seg_a
            f = bm.faces.new((rows[j][i], rows[j + 1][i], rows[j + 1][i2], rows[j][i2]))
            for lp, (ii, jj) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))):
                lp[uv_layer].uv = (u0 + (u1 - u0) * ii / seg_a, 1.0 - (v0 + (v1 - v0) * jj / seg_h))


# ------------------------------------------------------------------------------------------------
# Eyes (each part its own object, origin at the eyeball centre, local -Y = gaze in Blender)
# ------------------------------------------------------------------------------------------------
def eye_centre(side: float) -> Vector:
    x, z = side * L.EYE_X, L.EYE_Z
    sx, sz = x / L.HEAD_RX, z / L.HEAD_RZ
    y_surface = -L.HEAD_RY * math.sqrt(max(0.0, 1.0 - sx * sx - sz * sz))
    return Vector((x, y_surface + L.EYE_RADIUS - L.EYE_PROTRUDE, z))


def sphere(radius: float, seg_u: int = 48, seg_v: int = 32) -> bmesh.types.BMesh:
    """UV sphere whose pole axis is Y (so the -Y pole is the gaze), with spherical UVs."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg_u, v_segments=seg_v, radius=radius)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for lp in f.loops:
            d = lp.vert.co.normalized()
            lp[uv_layer].uv = (0.5 + math.atan2(d.x, d.z) / (2 * math.pi), 0.5 + 0.5 * -d.y)
    return bm


def cornea_shell(radius: float) -> bmesh.types.BMesh:
    bm = sphere(radius, 64, 48)
    zl = math.sqrt(max(L.EYE_RADIUS**2 - L.IRIS_RADIUS**2, 0.0))
    zc = zl - math.sqrt(max(L.CORNEA_RADIUS**2 - L.IRIS_RADIUS**2, 0.0))
    shell = radius - L.EYE_RADIUS
    for v in bm.verts:
        d = v.co.normalized()
        if d.y < 0.0:
            # Distance along d to the corneal sphere (centre at -Y zc, radius CORNEA_RADIUS).
            c = Vector((0.0, -zc, 0.0))
            b = d.dot(c)
            disc = b * b - (c.length_squared - L.CORNEA_RADIUS**2)
            if disc > 0.0:
                t = b + math.sqrt(disc) + shell
                if t > radius:
                    v.co = d * t
    return bm


CONTOUR_SEGMENTS = 96


def eye_contour(side: float) -> list[tuple[float, float]]:
    """Lid-margin contour as (angle, projected radius) around the eye centre. Angle 0 points to the
    outer corner and pi/2 up. Solved by bisection on layout.almond == 1."""
    c = eye_centre(side)
    out = []
    for i in range(CONTOUR_SEGMENTS):
        a = 2.0 * math.pi * i / CONTOUR_SEGMENTS
        lo, hi = 0.0, 0.04
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if L.almond(c.x + side * mid * math.cos(a), c.z + mid * math.sin(a), side) < 1.0:
                lo = mid
            else:
                hi = mid
        out.append((a, lo))
    return out


def push_out_of_eyes(p: Vector, clearance: float) -> Vector:
    """Moves a skin point radially out of either eyeball (front hemisphere) to R + clearance, so
    the eyeball never pokes through the lids or the socket skin."""
    for side in (-1.0, 1.0):
        c = eye_centre(side)
        d = p - c
        if d.y < 0.0 and d.length < L.EYE_RADIUS + clearance:
            p = c + d.normalized() * (L.EYE_RADIUS + clearance)
    return p


def on_eye_sphere(side: float, a: float, s: float, radius: float) -> Vector:
    """Eye-local point on a sphere of `radius` whose projection lies at radius s, contour angle a."""
    s = min(s, radius * 0.999)
    return Vector((side * s * math.cos(a), -math.sqrt(radius * radius - s * s), s * math.sin(a)))


def add_lids(bm: bmesh.types.BMesh, uv_layer) -> None:
    """Lid skirts: from the margin (resting on the eyeball) outward over the socket, ending on the
    face surface, so the opening is a smooth, finely sampled curve instead of a mesh intersection."""
    rings = 14
    for side in (-1.0, 1.0):
        c = eye_centre(side)
        contour = eye_contour(side)
        grid = []
        for j in range(rings + 1):
            t = j / rings
            row = []
            for a, s0 in contour:
                upper = max(0.0, math.sin(a))
                s = s0 * (1.0 + (L.LID_SKIRT_SCALE - 1.0) * t)
                bulge = 0.0012 * upper * math.sin(math.pi * min(t * 1.4, 1.0))  # upper-lid fat pad
                lift = 0.0003 + L.LID_THICKNESS * smoothstep(0.0, 0.25, t) + bulge
                p_ball = c + on_eye_sphere(side, a, min(s, L.EYE_RADIUS * 0.97), L.EYE_RADIUS + lift)
                x, z = c.x + side * s * math.cos(a), c.z + s * math.sin(a)
                # The outer edge tucks just under the face skin so the two never z-fight.
                p_face = head_front_point(x, z, socket=False) + Vector((0.0, L.LID_TUCK * t, 0.0))
                p = push_out_of_eyes(p_ball.lerp(p_face, smoothstep(0.35, 1.0, t)), lift)
                row.append(bm.verts.new(p))
            grid.append(row)
        n = len(contour)
        for j in range(rings):
            for i in range(n):
                i2 = (i + 1) % n
                quad = (grid[j][i], grid[j][i2], grid[j + 1][i2], grid[j + 1][i])
                normal = (quad[1].co - quad[0].co).cross(quad[3].co - quad[0].co)
                if normal.y > 0.0:  # face forward (-Y), toward the viewer
                    quad = tuple(reversed(quad))
                f = bm.faces.new(quad)
                for lp in f.loops:
                    lp[uv_layer].uv = head_uv_of(lp.vert.co)


def contour_patch(side: float, kind: str) -> bmesh.types.BMesh:
    """kind "occlusion": a shell over the whole opening (U inner->outer corner, V upper->lower lid).
    kind "tear": a strip inside the lower margin (U inner->outer, V lid->eyeball)."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    contour = eye_contour(side)
    rows: list[list] = []
    if kind == "occlusion":
        radius = L.EYE_RADIUS + 0.0017
        nr = 10
        for j in range(nr + 1):
            fr = 1.06 * j / nr
            rows.append(
                [(on_eye_sphere(side, a, s0 * fr, radius), (0.5 + 0.5 * fr * math.cos(a), 0.5 - 0.5 * fr * math.sin(a))) for a, s0 in contour]
            )
        closed = True
    else:
        radius = L.EYE_RADIUS + 0.0004
        lower = sorted((cc for cc in contour if math.pi < cc[0] < 2.0 * math.pi), key=lambda cc: -math.cos(cc[0]))
        for j in range(3):
            w = 0.0014 * j / 2
            rows.append(
                [(on_eye_sphere(side, a, max(s0 - w, 0.0), radius), (k / (len(lower) - 1), j / 2)) for k, (a, s0) in enumerate(lower)]
            )
        closed = False
    grid = [[(bm.verts.new(p), uv) for p, uv in row] for row in rows]
    n = len(grid[0])
    for j in range(len(grid) - 1):
        for i in range(n if closed else n - 1):
            i2 = (i + 1) % n
            cells = (grid[j][i], grid[j][i2], grid[j + 1][i2], grid[j + 1][i])
            # Faces point away from the eye centre (toward the viewer).
            normal = (cells[1][0].co - cells[0][0].co).cross(cells[3][0].co - cells[0][0].co)
            if normal.dot(cells[0][0].co) < 0.0:
                cells = tuple(reversed(cells))
            if len({id(cc[0]) for cc in cells}) < 4:
                continue  # the centre ring of the occlusion shell collapses to a point
            f = bm.faces.new([cc[0] for cc in cells])
            for lp, cc in zip(f.loops, cells):
                lp[uv_layer].uv = (cc[1][0], 1.0 - cc[1][1])
    return bm


def build_eyes() -> None:
    for side, tag in ((-1.0, "R"), (1.0, "L")):  # character's right eye is at -X (viewer's left)
        c = eye_centre(side)
        new_object(f"Eye{tag}", sphere(L.EYE_RADIUS), c)
        new_object(f"Cornea{tag}", cornea_shell(L.EYE_RADIUS + 0.0002), c)
        new_object(f"EyeOcclusion{tag}", contour_patch(side, "occlusion"), c)
        new_object(f"TearLine{tag}", contour_patch(side, "tear"), c)


# ------------------------------------------------------------------------------------------------
# Hair cards
# ------------------------------------------------------------------------------------------------
def head_surface_normal(p: Vector) -> Vector:
    return Vector((p.x / L.HEAD_RX**2, p.y / L.HEAD_RY**2, p.z / L.HEAD_RZ**2)).normalized()


def project_to_head(p: Vector, lift: float) -> Vector:
    q = Vector((p.x / L.HEAD_RX, p.y / L.HEAD_RY, p.z / L.HEAD_RZ))
    q.normalize()
    s = Vector((q.x * L.HEAD_RX, q.y * L.HEAD_RY, q.z * L.HEAD_RZ))
    return s + head_surface_normal(s) * lift


HAIRLINE_CARDS = 70


def build_hair() -> bpy.types.Object:
    rng = random.Random(SEED)
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    colors = []  # per created vertex (r, g, b, a)
    layers = [(0.0020, 260, 0.0), (0.0042, 160, 0.5), (0.0065, 80, 1.0)]
    seg = 18
    for lift, count, layer in layers:
        made = 0
        while made < count:
            if layer == 0.0 and made < HAIRLINE_CARDS:
                # A row of roots exactly on the front hair-line, for a clean edge.
                phi = math.pi * (-0.32 + 0.64 * (made + rng.random() * 0.6) / HAIRLINE_CARDS)
                hz = L.hairline_z(math.sin(phi), -math.cos(phi)) + 0.002
                dz = hz / L.HEAD_RZ
                hr = math.sqrt(max(0.0, 1.0 - dz * dz))
                d = Vector((math.sin(phi) * hr, -math.cos(phi) * hr, dz))
            else:
                d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.2, 1))).normalized()
                if d.z * L.HEAD_RZ < L.hairline_z(d.x, d.y) + 0.004:
                    continue
            hairline_card = layer == 0.0 and made < HAIRLINE_CARDS
            made += 1
            p = project_to_head(Vector((d.x * L.HEAD_RX, d.y * L.HEAD_RY, d.z * L.HEAD_RZ)), lift)
            length = rng.uniform(0.26, 0.42) * (0.75 if layer > 0.9 else 1.0)
            width = rng.uniform(0.014, 0.026) * (1.3 if layer < 0.1 else 1.0)
            slot = rng.randrange(L.HAIR_CLUMPS)
            phase = rng.random()
            side_sweep = rng.uniform(-0.15, 0.15)
            step = length / seg
            pts = [p]
            free = False
            for _ in range(seg):
                cur = pts[-1]
                n = head_surface_normal(cur)
                want = Vector((side_sweep * 0.3 + cur.x * 2.0, 1.0, -0.6 - 2.5 * max(0.0, cur.y) / L.HEAD_RY)).normalized()
                if hairline_card and cur.y < -0.02:
                    want = Vector((cur.x * 0.4, 0.5, 1.0)).normalized()  # up and back off the forehead
                if not free:
                    tdir = (want - n * want.dot(n)).normalized()
                    nxt = project_to_head(cur + tdir * step, lift)
                    if nxt.z < -0.03 and nxt.y > 0.01:
                        free = True
                else:
                    tdir = Vector((cur.x * 0.6 + side_sweep * 0.05, 0.22, -1.0)).normalized()
                    nxt = cur + tdir * step
                    # stay outside the neck
                    r = math.hypot(nxt.x / 0.058, (nxt.y - 0.012) / 0.066)
                    if r < 1.0 + lift * 10 and nxt.z < -0.05:
                        s = (1.0 + lift * 10) / r
                        nxt = Vector((nxt.x * s, 0.012 + (nxt.y - 0.012) * s, nxt.z))
                pts.append(nxt)
            # Ribbon across the strand, lying in the head's tangent plane.
            u0 = slot / L.HAIR_CLUMPS
            u1 = (slot + 1) / L.HAIR_CLUMPS
            left, right = [], []
            for k, cur in enumerate(pts):
                tangent = (pts[min(k + 1, seg)] - pts[max(k - 1, 0)]).normalized()
                n = head_surface_normal(cur) if cur.z > -0.03 else Vector((cur.x, cur.y - 0.012, 0.0)).normalized()
                bvec = tangent.cross(n).normalized()
                taper = 1.0 - 0.45 * (k / seg)
                w = width * taper * 0.5
                left.append(bm.verts.new(cur - bvec * w))
                right.append(bm.verts.new(cur + bvec * w))
                t = k / seg
                for _side in (0, 1):
                    colors.append((t * t, t, phase, t))
            for k in range(seg):
                f = bm.faces.new((left[k], right[k], right[k + 1], left[k + 1]))
                for lp, (uu, vv) in zip(f.loops, ((u0, k), (u1, k), (u1, k + 1), (u0, k + 1))):
                    lp[uv_layer].uv = (uu, 1.0 - vv / seg)
    ob = new_object("Hair", bm)
    set_vertex_colors(ob, lambda i, co: colors[i])
    return ob


# ------------------------------------------------------------------------------------------------
# Lacquer collar (asha.md §4.1 layer 5: a 6 cm standing collar), solid 2.5 mm
# ------------------------------------------------------------------------------------------------
def build_collar() -> bpy.types.Object:
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    seg_a, seg_h = 96, 10
    arc = math.radians(L.COLLAR_ARC_DEG)
    a0 = -math.pi / 2 - arc / 2  # centred on the front (-Y)
    rows = []
    for j in range(seg_h + 1):
        t = j / seg_h
        z = -0.105 + L.COLLAR_HEIGHT * t
        r = L.COLLAR_RADIUS * (1.0 + 0.10 * t)  # flares out slightly at the top
        rows.append(
            [bm.verts.new(Vector((r * math.cos(a0 + arc * i / seg_a), 0.012 + 1.12 * r * math.sin(a0 + arc * i / seg_a), z))) for i in range(seg_a + 1)]
        )
    for j in range(seg_h):
        for i in range(seg_a):
            f = bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
            for lp, (ii, jj) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                lp[uv_layer].uv = (ii / seg_a, jj / seg_h)
    # 2.5 mm leather (asha.md §9.2). bmesh solidify, not the modifier: evaluated modifiers are
    # not byte-stable between runs.
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.0025)
    return new_object("Collar", bm)


# ------------------------------------------------------------------------------------------------
# Cloth: drape (a hanging banner with folds) and the verse-sleeve tube
# ------------------------------------------------------------------------------------------------
def build_drape() -> bpy.types.Object:
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    nu, nv = 120, 150
    grid = []
    colors = []
    for j in range(nv + 1):
        t = j / nv  # 0 top .. 1 hem
        row = []
        for i in range(nu + 1):
            s = i / nu
            gather = 1.0 - 0.18 * (1.0 - t)  # gathered at the rod
            x = (s - 0.5) * L.DRAPE_W * gather
            amp = 0.010 + 0.028 * t
            y = amp * math.sin(2 * math.pi * 5.0 * s + 0.6) + 0.35 * amp * math.sin(2 * math.pi * 11.0 * s + 2.0 * t)
            y += 0.03 * t * t * math.sin(math.pi * s)  # hem bellies out
            z = -L.DRAPE_H * t
            row.append(bm.verts.new(Vector((x, y, z))))
            colors.append((t**1.5, t, (s * 3.0) % 1.0, 0.5 * t))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            f = bm.faces.new((grid[j][i], grid[j + 1][i], grid[j + 1][i + 1], grid[j][i + 1]))
            for lp, (ii, jj) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))):
                lp[uv_layer].uv = (ii / nu, 1.0 - jj / nv)
    ob = new_object("Drape", bm)
    set_vertex_colors(ob, lambda i, co: colors[i])
    return ob


def build_sleeve() -> bpy.types.Object:
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    nu, nv = 64, 120
    grid = []
    colors = []
    for j in range(nv + 1):
        t = j / nv  # 0 shoulder .. 1 cuff
        r = L.SLEEVE_R_SHOULDER + (L.SLEEVE_R_CUFF - L.SLEEVE_R_SHOULDER) * t**1.4
        z = -L.SLEEVE_LENGTH * t
        sway = 0.05 * t * t  # hangs slightly forward and out
        row = []
        for i in range(nu + 1):
            a = 2 * math.pi * (i / nu - 0.5)  # U = 0.5 faces outward (+X), seam on the inner side
            fold = 1.0 + 0.06 * t * math.sin(6 * a + 3 * t)
            row.append(bm.verts.new(Vector((r * fold * math.cos(a) + sway, r * fold * math.sin(a) * 0.85, z))))
            colors.append((t, t, 0.3, t))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            f = bm.faces.new((grid[j][i], grid[j + 1][i], grid[j + 1][i + 1], grid[j][i + 1]))
            for lp, (ii, jj) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))):
                lp[uv_layer].uv = (ii / nu, 1.0 - jj / nv)
    ob = new_object("Sleeve", bm)
    set_vertex_colors(ob, lambda i, co: colors[i])
    return ob


# ------------------------------------------------------------------------------------------------
def export(path: Path, objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_tangents=False,  # Godot generates them on import (ensure_tangents); the exporter's are not byte-stable
        export_normals=True,
        export_texcoords=True,
        export_materials="NONE",
        export_vertex_color="ACTIVE",
        export_all_vertex_colors=False,
        export_yup=True,
        export_animations=False,
    )
    print(f"wrote {path} ({path.stat().st_size} bytes)")


def main() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    OUT.mkdir(parents=True, exist_ok=True)
    head = build_head()
    build_eyes()
    hair = build_hair()
    collar = build_collar()
    eyes = [ob for ob in bpy.context.scene.objects if ob.name.startswith(("Eye", "Cornea", "TearLine"))]
    export(OUT / "shader_test_bust.glb", [head, hair, collar, *eyes])
    drape = build_drape()
    sleeve = build_sleeve()
    export(OUT / "shader_test_cloth.glb", [drape, sleeve])


main()
