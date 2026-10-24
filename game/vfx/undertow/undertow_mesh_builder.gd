@tool
class_name UndertowMeshBuilder
extends RefCounted
## Meshes for the Undertow storm (M1-RND-03). Pure: no nodes, unit-tested.
##   sea_disc()       polar disc for the maelstrom, rings packed toward the throat
##   unit_tube()      open unit cylinder the shell and spray shaders map onto the storm envelope
##   proxy()          closed cylinder the raymarched body is drawn on (back faces)
##   footprint()      editor gizmo lines: footprint circles at sea level and the eye axis (M1-RND-09)
##   streamers()      curtains of held light hanging off the wall's wounds to the sea (M2-RND-05)
##   bolt()           a branching lightning stroke as view-facing segment quads (M2-RND-05)

## The tube's height runs from -0.5 to 0.5 (CylinderMesh convention); shaders rely on it.
const UNIT_HEIGHT := 1.0
const UNIT_RADIUS := 1.0


## Polar disc of `radius` (m) in the XZ plane: a centre vertex plus `rings` rings of `segments`
## vertices at radius * (i / rings)^power, so a power > 1 packs rings toward the centre, where the
## funnel is steep. Front faces point up (+Y), wound clockwise as Godot expects.
static func sea_disc(radius: float, rings: int, segments: int, power: float) -> ArrayMesh:
	var n_rings := maxi(rings, 1)
	var n_seg := maxi(segments, 3)
	var verts := PackedVector3Array()
	var normals := PackedVector3Array()
	verts.append(Vector3.ZERO)
	normals.append(Vector3.UP)
	for i in range(1, n_rings + 1):
		var r := radius * pow(float(i) / n_rings, power)
		for j in n_seg:
			var a := TAU * j / n_seg
			verts.append(Vector3(r * cos(a), 0.0, r * sin(a)))
			normals.append(Vector3.UP)
	var indices := PackedInt32Array()
	for j in n_seg:
		indices.append_array([0, 1 + j, 1 + (j + 1) % n_seg])
	for i in range(n_rings - 1):
		var inner := 1 + i * n_seg
		var outer := inner + n_seg
		for j in n_seg:
			var j1 := (j + 1) % n_seg
			indices.append_array([inner + j, outer + j, inner + j1])
			indices.append_array([outer + j, outer + j1, inner + j1])
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_INDEX] = indices
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh


## Open cylinder of radius 1 and height 1 (y in [-0.5, 0.5]) with `rings` height subdivisions.
static func unit_tube(rings: int, segments: int) -> CylinderMesh:
	var m := CylinderMesh.new()
	m.top_radius = UNIT_RADIUS
	m.bottom_radius = UNIT_RADIUS
	m.height = UNIT_HEIGHT
	m.rings = maxi(rings, 1)
	m.radial_segments = maxi(segments, 3)
	m.cap_top = false
	m.cap_bottom = false
	return m


## Closed cylinder bounding the storm: the raymarch proxy (its shader clips rays analytically, so
## the tessellation only needs to cover the silhouette).
static func proxy(radius: float, height: float, segments: int) -> CylinderMesh:
	var m := CylinderMesh.new()
	m.top_radius = radius
	m.bottom_radius = radius
	m.height = height
	m.rings = 1
	m.radial_segments = maxi(segments, 3)
	return m


## Line mesh (PRIMITIVE_LINES) for UndertowStorm's editor gizmo: one circle of `segments` chords per
## radius in `radii` (m) at sea level (y = 0), plus the eye axis from sea level to `height` (m).
static func footprint(radii: PackedFloat32Array, height: float, segments: int) -> ArrayMesh:
	var n_seg := maxi(segments, 3)
	var verts := PackedVector3Array()
	for r in radii:
		for i in n_seg:
			var a0 := TAU * float(i) / float(n_seg)
			var a1 := TAU * float(i + 1) / float(n_seg)
			verts.append(Vector3(cos(a0) * r, 0.0, sin(a0) * r))
			verts.append(Vector3(cos(a1) * r, 0.0, sin(a1) * r))
	verts.append(Vector3.ZERO)
	verts.append(Vector3(0.0, height, 0.0))
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_LINES, arrays)
	return mesh


## Curtains of held light (M2-RND-05) hanging off the wall's wounds down its outer face to the sea.
## Each anchor is (radius m, height m, angle rad) on the wall; a curtain falls from it to the sea
## (y = h (1 - t)^drop), bulges out from the face toward the foot (r + reach_m t^2, like the spray),
## trails `twist_rad` sideways, and widens from 0.5 to 1.5 x `width_m` across the storm's tangent, so
## the outside sees its face. UV = (across 0..1, along t 0..1); UV2 = (a per-curtain phase in [0, 1),
## arc length from the anchor in m) for the shader's mote pattern.
static func streamers(
	anchors: PackedVector3Array, reach_m: float, drop: float, twist_rad: float, width_m: float, segments: int
) -> ArrayMesh:
	var n_seg := maxi(segments, 1)
	var verts := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var uv2s := PackedVector2Array()
	var indices := PackedInt32Array()
	for k in anchors.size():
		var anchor := anchors[k]
		var phase := fposmod(float(k) * 0.6180339887, 1.0)
		var base := verts.size()
		var arc := 0.0
		var prev := Vector3.ZERO
		for i in n_seg + 1:
			var t := float(i) / float(n_seg)
			var r := anchor.x + reach_m * t * t
			var a := anchor.z + twist_rad * t
			var y := anchor.y * pow(1.0 - t, drop)
			var radial := Vector3(cos(a), 0.0, sin(a))
			var tangent := Vector3(-sin(a), 0.0, cos(a))
			var half := 0.5 * width_m * (0.5 + t)
			var c := radial * r + Vector3(0.0, y, 0.0)
			if i > 0:
				arc += c.distance_to(prev)
			prev = c
			for side in 2:
				verts.append(c + tangent * half * (2.0 * float(side) - 1.0))
				normals.append(radial)
				uvs.append(Vector2(float(side), t))
				uv2s.append(Vector2(phase, arc))
		for i in n_seg:
			var v := base + i * 2
			indices.append_array([v, v + 2, v + 1, v + 1, v + 2, v + 3])
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_TEX_UV2] = uv2s
	arrays[Mesh.ARRAY_INDEX] = indices
	var mesh := ArrayMesh.new()
	if not verts.is_empty():
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh


## One lightning stroke (M2-RND-05) from `top` to `bottom` (storm-local m), deterministic in `seed`:
## a main channel of `segments` jagged steps (each point pushed sideways by up to `jag` x the step)
## and `branches` forks that leave it at random points and die out. Every segment is a quad whose
## four vertices sit on its endpoints; the shader pushes them apart across the view by the width.
## NORMAL = the segment direction, UV = (side -1/+1, along 0..1 of its channel), COLOR.r = width
## scale (forks are thinner), COLOR.g = brightness scale.
static func bolt(seed: int, top: Vector3, bottom: Vector3, segments: int, branches: int, jag: float) -> ArrayMesh:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed
	var verts := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var colors := PackedColorArray()
	var indices := PackedInt32Array()
	var main := _bolt_path(rng, top, bottom, maxi(segments, 2), jag)
	_bolt_quads(main, 1.0, 1.0, verts, normals, uvs, colors, indices)
	var span := top.distance_to(bottom)
	for b in maxi(branches, 0):
		var at := rng.randi_range(1, main.size() - 2)
		var start := main[at]
		var dir := (bottom - top).normalized()
		var side := Vector3(rng.randf_range(-1.0, 1.0), 0.0, rng.randf_range(-1.0, 1.0)).normalized()
		var end := start + (dir * 0.6 + side * 0.8).normalized() * span * rng.randf_range(0.15, 0.35)
		var fork := _bolt_path(rng, start, end, maxi(segments / 2, 2), jag)
		_bolt_quads(fork, 0.55, 0.6, verts, normals, uvs, colors, indices)
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_COLOR] = colors
	arrays[Mesh.ARRAY_INDEX] = indices
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh


static func _bolt_path(
	rng: RandomNumberGenerator, a: Vector3, b: Vector3, steps: int, jag: float
) -> PackedVector3Array:
	var out := PackedVector3Array()
	var step := a.distance_to(b) / float(steps)
	for i in steps + 1:
		var p := a.lerp(b, float(i) / float(steps))
		if i > 0 and i < steps:
			p += (
				Vector3(rng.randf_range(-1.0, 1.0), rng.randf_range(-0.3, 0.3), rng.randf_range(-1.0, 1.0)) * jag * step
			)
		out.append(p)
	return out


static func _bolt_quads(
	path: PackedVector3Array,
	width: float,
	bright: float,
	verts: PackedVector3Array,
	normals: PackedVector3Array,
	uvs: PackedVector2Array,
	colors: PackedColorArray,
	indices: PackedInt32Array
) -> void:
	for i in path.size() - 1:
		var a := path[i]
		var b := path[i + 1]
		var d := (b - a).normalized()
		var v := verts.size()
		var s0 := float(i) / float(path.size() - 1)
		var s1 := float(i + 1) / float(path.size() - 1)
		for e in [[a, s0, -1.0], [a, s0, 1.0], [b, s1, -1.0], [b, s1, 1.0]]:
			verts.append(e[0])
			normals.append(d)
			uvs.append(Vector2(e[2], e[1]))
			colors.append(Color(width, bright, 0.0, 1.0))
		indices.append_array([v, v + 2, v + 1, v + 1, v + 2, v + 3])
