class_name WaterMeshBuilder
extends RefCounted
## Builds the water surface grid (M1-RND-01): uniform cells in a square core around the origin,
## then cells that grow geometrically out to the horizon. One draw call, no seams, no T-junctions.
## The vertex shader displaces it in world space, so the grid only sets how finely waves are
## sampled: keep core_cell_m <= a quarter of the shortest wavelength.

## Cells never grow past this multiple of the core cell (keeps the far grid from getting so
## coarse that the longest swell aliases).
const MAX_CELL_GROWTH := 512.0


## Sorted axis coordinates: -outer .. -core, uniform core, core .. outer.
static func axis_coords(
	core_half_m: float, core_cell_m: float, outer_half_m: float, growth: float
) -> PackedFloat32Array:
	var cells := maxi(int(ceil(core_half_m / core_cell_m)), 1)
	var core_half := cells * core_cell_m
	var pos := PackedFloat32Array()
	var x := core_half
	var cell := core_cell_m
	var outer := PackedFloat32Array()
	while x < outer_half_m - 1e-4:
		cell = minf(cell * growth, core_cell_m * MAX_CELL_GROWTH)
		x = minf(x + cell, outer_half_m)
		outer.append(x)
	for i in range(outer.size() - 1, -1, -1):
		pos.append(-outer[i])
	for i in range(-cells, cells + 1):
		pos.append(i * core_cell_m)
	pos.append_array(outer)
	return pos


static func build(core_half_m: float, core_cell_m: float, outer_half_m: float, growth: float) -> ArrayMesh:
	var axis := axis_coords(core_half_m, core_cell_m, outer_half_m, growth)
	var n := axis.size()
	var extent := axis[n - 1]
	var verts := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	verts.resize(n * n)
	normals.resize(n * n)
	uvs.resize(n * n)
	for j in n:
		for i in n:
			var idx := j * n + i
			verts[idx] = Vector3(axis[i], 0.0, axis[j])
			normals[idx] = Vector3.UP
			uvs[idx] = Vector2(axis[i], axis[j]) / (2.0 * extent) + Vector2(0.5, 0.5)
	var indices := PackedInt32Array()
	indices.resize((n - 1) * (n - 1) * 6)
	var k := 0
	for j in n - 1:
		for i in n - 1:
			var a := j * n + i
			var b := a + 1
			var c := a + n
			var d := c + 1
			# Clockwise seen from above (+Y): Godot's front-face winding.
			indices[k] = a
			indices[k + 1] = b
			indices[k + 2] = c
			indices[k + 3] = b
			indices[k + 4] = d
			indices[k + 5] = c
			k += 6
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = indices
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh
