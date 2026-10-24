class_name HalunaTerrain
extends Node3D
## Procedural ground for the Haluna mood test (M1-ENV-01): the east-facing crescent beach, the village
## terrace behind it, a low island interior, the lagoon flats and the reef drop-off (haluna.md §0).
## Heights are metres above the tide datum (0 = mean sea level). Deterministic (seeded noise).
##
## Two meshes: a fine core (village, beach, dock) and a coarse outer field that dips under the core.
## Vertex colour masks for env_ground.gdshader: R lane, G turf, B seagrass, A reef rubble. Lanes come
## from the layout (HalunaDresser passes them in) and are rasterised into a mask grid first, so the
## build stays O(vertices + lane cells) in GDScript.

const CORE_SINK_M := 0.6
## How close to a core grid point a sample must be to read the cached height (grid cells).
const GRID_EPS := 1e-4

## All shape numbers live in the zone layout JSON ("terrain"); these are only the fallbacks.
var shore_tip_x_m: float = 50.0
var shore_half_len_m: float = 210.0
var tip_recede: float = 2.2
var beach_width_m: float = 28.0
var beach_head_y_m: float = 1.6
var terrace_slope: float = 0.004
var interior_start_m: float = 190.0
var interior_rise_m: float = 5.0
var lagoon_slope: float = 0.012
var lagoon_shelf_m: float = 0.6
## Along-shore variation of the nearshore shelf (fraction of its depth, and its period along z): the
## wash zone's width follows the depth, so without it the surf reads as one even stripe (H01).
var shelf_variation: float = 0.0
var shelf_variation_period_m: float = 40.0
var reef_edge_m: float = 270.0
var reef_depth_m: float = 22.0
var reef_width_m: float = 40.0
## The island is small: its far (west) shore lies this far inland of the beach.
var west_coast_m: float = 430.0
var noise_amp_m: float = 0.35
var noise_period_m: float = 28.0
var core_rect: Rect2 = Rect2(-160.0, -130.0, 230.0, 260.0)
var core_cell_m: float = 1.0
var outer_rect: Rect2 = Rect2(-700.0, -1400.0, 2600.0, 2400.0)
var outer_cell_m: float = 8.0
var lane_width_m: float = 3.2
var seed_value: int = 7
## Each lane: PackedVector2Array of (x, z) points.
var lanes: Array[PackedVector2Array] = []
## Each entry: Vector3(x, z, radius) of a flat pad (house yards, the chapel court) at its ground height.
var pads: Array[Vector3] = []
## Islets: Vector4(x, z, radius, height) raised out of the lagoon (the Shell Shrine).
var islets: Array[Vector4] = []
## Distant islands on the horizon: Vector4(x, z, radius, height) as low-res noise domes
## (atmospheric perspective fades them to pale cyan-blue, references §1.6).
var far_islands: Array[Vector4] = []
var far_island_cells: int = 48

var material: Material

var _noise := FastNoiseLite.new()
var _lane_mask := PackedFloat32Array()
var _mask_origin := Vector2.ZERO
var _mask_cell := 1.0
var _mask_size := Vector2i.ZERO
## M2-ENV-05: the core mesh's heights (row-major on the core_cell_m grid from core_rect.position), kept
## for grid_height(): the zone's walk collision samples the same 1 m grid and reads them instead of
## computing every height a second time.
var _core_heights := PackedFloat32Array()
var _core_n := Vector2i.ZERO


func configure(data: Dictionary) -> void:
	for key: String in data:
		var v: Variant = data[key]
		match key:
			"core_rect", "outer_rect":
				var a: Array = v
				set(key, Rect2(float(a[0]), float(a[1]), float(a[2]), float(a[3])))
			"pads", "islets", "lanes":
				pass
			"far_islands":
				far_islands.clear()
				for f: Array in v:
					far_islands.append(Vector4(float(f[0]), float(f[1]), float(f[2]), float(f[3])))
			_:
				set(key, v)


func build() -> void:
	_noise.seed = seed_value
	_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	_noise.frequency = 1.0 / noise_period_m
	_noise.fractal_octaves = 3
	_rasterise_lanes()
	for c in get_children():
		c.queue_free()
	_core_heights = PackedFloat32Array()
	_core_n = Vector2i.ZERO
	_add_mesh("Core", core_rect, core_cell_m, 0.0)
	_add_mesh("Outer", outer_rect, outer_cell_m, CORE_SINK_M)
	for k in far_islands.size():
		_add_far_island(k, far_islands[k])


## Distance inland from the shoreline at z (negative = offshore).
func inland_m(x: float, z: float) -> float:
	var az := absf(z)
	var shore := shore_tip_x_m * pow(minf(az, shore_half_len_m) / shore_half_len_m, 2.0)
	if az > shore_half_len_m:
		shore -= tip_recede * (az - shore_half_len_m)
	return shore - x


## height_at(x, z), read from the core mesh's samples when (x, z) is one of its grid points (M2-ENV-05;
## the mesh computed it with height_at at those exact coordinates and keeps it at 32-bit precision, the
## precision the collision heightmap stores), else computed.
func grid_height(x: float, z: float) -> float:
	if not _core_heights.is_empty():
		var fx := (x - core_rect.position.x) / core_cell_m
		var fz := (z - core_rect.position.y) / core_cell_m
		var i := roundi(fx)
		var k := roundi(fz)
		if (
			absf(fx - i) < GRID_EPS
			and absf(fz - k) < GRID_EPS
			and i >= 0
			and k >= 0
			and i < _core_n.x
			and k < _core_n.y
		):
			return _core_heights[k * _core_n.x + i]
	return height_at(x, z)


## Ground height (m above datum) at world (x, z).
func height_at(x: float, z: float) -> float:
	var d := inland_m(x, z)
	var n := _noise.get_noise_2d(x, z) * noise_amp_m
	var h: float
	if d >= 0.0:
		var t := clampf(d / beach_width_m, 0.0, 1.0)
		h = beach_head_y_m * (t * t * (3.0 - 2.0 * t) * 0.35 + t * 0.65)
		h += maxf(d - beach_width_m, 0.0) * terrace_slope
		h += interior_rise_m * smoothstep(interior_start_m, interior_start_m + 120.0, d)
		h += n * smoothstep(0.0, beach_width_m, d)
		h = lerpf(h, -reef_depth_m, smoothstep(west_coast_m, west_coast_m + 70.0, d))
	else:
		var s := -d
		var along := _noise.get_noise_2d(-41.0, z * noise_period_m / shelf_variation_period_m)
		var shelf := lagoon_shelf_m * (1.0 + shelf_variation * along)
		h = -s * lagoon_slope * (1.0 + shelf_variation * along) - shelf * (1.0 - exp(-s / 25.0)) + n * 0.6
		var edge := reef_edge_m + _noise.get_noise_2d(z * 0.31, 17.0) * 35.0
		var r := clampf((s - edge) / reef_width_m, 0.0, 1.0)
		h = lerpf(h, -reef_depth_m, r * r * (3.0 - 2.0 * r))
	for il: Vector4 in islets:
		var dd := Vector2(x - il.x, z - il.y).length()
		var k := 1.0 - smoothstep(il.z * 0.6, il.z * 1.6, dd)
		h = lerpf(h, il.w + n * 0.3, k)
	for p: Vector3 in pads:
		var dp := Vector2(x - p.x, z - p.y).length()
		if dp < p.z * 1.6:
			var flat := _base_height(p.x, p.y)
			h = lerpf(h, flat, 1.0 - smoothstep(p.z, p.z * 1.6, dp))
	return h


func _base_height(x: float, z: float) -> float:
	var d := inland_m(x, z)
	var t := clampf(d / beach_width_m, 0.0, 1.0)
	var h := beach_head_y_m * (t * t * (3.0 - 2.0 * t) * 0.35 + t * 0.65)
	h += maxf(d - beach_width_m, 0.0) * terrace_slope
	h += interior_rise_m * smoothstep(interior_start_m, interior_start_m + 120.0, d)
	return h


func lane_at(x: float, z: float) -> float:
	if _mask_size.x == 0:
		return 0.0
	var gx := int((x - _mask_origin.x) / _mask_cell)
	var gz := int((z - _mask_origin.y) / _mask_cell)
	if gx < 0 or gz < 0 or gx >= _mask_size.x or gz >= _mask_size.y:
		return 0.0
	return _lane_mask[gz * _mask_size.x + gx]


func _masks(x: float, z: float, h: float) -> Color:
	var d := inland_m(x, z)
	var lane := lane_at(x, z)
	var nb := _noise.get_noise_2d(x * 2.7 + 91.0, z * 2.7)
	var turf := smoothstep(beach_width_m + 2.0, beach_width_m + 14.0, d) * clampf(0.75 + nb * 0.5, 0.0, 1.0)
	var sg := 0.0
	if d < -10.0:
		sg = smoothstep(0.05, 0.35, _noise.get_noise_2d(x * 0.6, z * 0.6 + 400.0)) * smoothstep(-10.0, -30.0, d)
	var rubble := 0.0
	if d < 0.0:
		var s := -d
		rubble = smoothstep(reef_edge_m - 30.0, reef_edge_m + 5.0, s) * 0.9
		rubble = maxf(rubble, smoothstep(0.25, 0.55, _noise.get_noise_2d(x * 0.9 + 5.0, z * 0.9)) * 0.7)
	if h < -0.4:
		turf = 0.0
	return Color(lane, turf * (1.0 - lane), sg, rubble)


func _rasterise_lanes() -> void:
	_mask_origin = core_rect.position
	_mask_cell = 0.5
	_mask_size = Vector2i(int(core_rect.size.x / _mask_cell) + 1, int(core_rect.size.y / _mask_cell) + 1)
	_lane_mask = PackedFloat32Array()
	_lane_mask.resize(_mask_size.x * _mask_size.y)
	var half := lane_width_m * 0.5
	for lane: PackedVector2Array in lanes:
		for i in lane.size() - 1:
			var a := lane[i]
			var b := lane[i + 1]
			var lo := Vector2(minf(a.x, b.x), minf(a.y, b.y)) - Vector2.ONE * (half + 1.0)
			var hi := Vector2(maxf(a.x, b.x), maxf(a.y, b.y)) + Vector2.ONE * (half + 1.0)
			var g0 := Vector2i(((lo - _mask_origin) / _mask_cell).floor())
			var g1 := Vector2i(((hi - _mask_origin) / _mask_cell).ceil())
			for gz in range(maxi(g0.y, 0), mini(g1.y, _mask_size.y)):
				for gx in range(maxi(g0.x, 0), mini(g1.x, _mask_size.x)):
					var p := _mask_origin + Vector2(gx, gz) * _mask_cell
					var q := Geometry2D.get_closest_point_to_segment(p, a, b)
					var dist := p.distance_to(q)
					var wobble := _noise.get_noise_2d(p.x * 3.0, p.y * 3.0) * 0.35
					var v := 1.0 - smoothstep(half - 0.4 + wobble, half + 0.5 + wobble, dist)
					var idx := gz * _mask_size.x + gx
					_lane_mask[idx] = maxf(_lane_mask[idx], v)


func _add_mesh(mesh_name: String, rect: Rect2, cell: float, sink_inside_core: float) -> void:
	var nx := int(rect.size.x / cell) + 1
	var nz := int(rect.size.y / cell) + 1
	var inner := core_rect.grow(-cell * 1.5)
	# M2-ENV-05: the rows are independent (height_at and _masks only read this node's settings, the noise
	# and the lane mask), so they are computed in parallel, each into its own holder (no shared writes).
	# The values and their order are the same as a single loop's.
	var rows: Array[Row] = []
	for j in nz:
		rows.append(Row.new())
	var fill := func(j: int) -> void:
		var row := rows[j]
		row.verts.resize(nx)
		row.colors.resize(nx)
		for i in nx:
			var x := rect.position.x + i * cell
			var z := rect.position.y + j * cell
			var h := height_at(x, z)
			if sink_inside_core > 0.0 and inner.has_point(Vector2(x, z)):
				h -= sink_inside_core
			row.verts[i] = Vector3(x, h, z)
			row.colors[i] = _masks(x, z, h)
	var task := WorkerThreadPool.add_group_task(fill, nz, -1, true, "HalunaTerrain %s" % mesh_name)
	WorkerThreadPool.wait_for_group_task_completion(task)
	var verts := PackedVector3Array()
	var colors := PackedColorArray()
	for row in rows:
		verts.append_array(row.verts)
		colors.append_array(row.colors)
	if rect == core_rect:
		_core_n = Vector2i(nx, nz)
		_core_heights.resize(nx * nz)
		for k in verts.size():
			_core_heights[k] = verts[k].y
	var normals := PackedVector3Array()
	normals.resize(nx * nz)
	var tangents := PackedFloat32Array()
	tangents.resize(nx * nz * 4)
	for j in nz:
		for i in nx:
			var l := verts[j * nx + maxi(i - 1, 0)]
			var r := verts[j * nx + mini(i + 1, nx - 1)]
			var d := verts[maxi(j - 1, 0) * nx + i]
			var u := verts[mini(j + 1, nz - 1) * nx + i]
			var n := (u - d).cross(r - l).normalized()
			normals[j * nx + i] = n
			var t := (r - l).normalized()
			var k := (j * nx + i) * 4
			tangents[k] = t.x
			tangents[k + 1] = t.y
			tangents[k + 2] = t.z
			tangents[k + 3] = 1.0
	var indices := PackedInt32Array()
	indices.resize((nx - 1) * (nz - 1) * 6)
	var w := 0
	for j in nz - 1:
		for i in nx - 1:
			var a := j * nx + i
			indices[w] = a
			indices[w + 1] = a + 1
			indices[w + 2] = a + nx
			indices[w + 3] = a + 1
			indices[w + 4] = a + nx + 1
			indices[w + 5] = a + nx
			w += 6
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TANGENT] = tangents
	arrays[Mesh.ARRAY_COLOR] = colors
	arrays[Mesh.ARRAY_INDEX] = indices
	var m := ArrayMesh.new()
	m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var mi := MeshInstance3D.new()
	mi.name = mesh_name
	mi.mesh = m
	mi.material_override = material
	add_child(mi)


func _add_far_island(index: int, isl: Vector4) -> void:
	var n := far_island_cells
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var pts: Array[Vector3] = []
	for j in n + 1:
		for i in n + 1:
			var u := (float(i) / n) * 2.0 - 1.0
			var v := (float(j) / n) * 2.0 - 1.0
			var r := sqrt(u * u + v * v)
			var x := isl.x + u * isl.z
			var z := isl.y + v * isl.z
			var bump := 0.5 + 0.5 * _noise.get_noise_2d(x * 0.02, z * 0.02 + index * 50.0)
			var dome := pow(maxf(0.0, 1.0 - r), 0.7) * (0.55 + 0.9 * bump)
			pts.append(Vector3(x, isl.w * dome - 6.0 * smoothstep(0.85, 1.0, r), z))
	for j in n:
		for i in n:
			var a := j * (n + 1) + i
			for idx: int in [a, a + 1, a + n + 1, a + 1, a + n + 2, a + n + 1]:
				st.set_color(Color(0.0, 0.9, 0.0, 0.0))
				st.add_vertex(pts[idx])
	st.generate_normals()
	var mi := MeshInstance3D.new()
	mi.name = "FarIsland%d" % index
	mi.mesh = st.commit()
	mi.material_override = material
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)


## One row of a mesh grid, filled by its own WorkerThreadPool task (M2-ENV-05).
class Row:
	extends RefCounted
	var verts := PackedVector3Array()
	var colors := PackedColorArray()
