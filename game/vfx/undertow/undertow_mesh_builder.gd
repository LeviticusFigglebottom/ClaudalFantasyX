class_name UndertowMeshBuilder
extends RefCounted
## Meshes for the Undertow storm (M1-RND-03). Pure: no nodes, unit-tested.
##   sea_disc()       polar disc for the maelstrom, rings packed toward the throat
##   unit_tube()      open unit cylinder the shell and spray shaders map onto the storm envelope
##   proxy()          closed cylinder the raymarched body is drawn on (back faces)

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
