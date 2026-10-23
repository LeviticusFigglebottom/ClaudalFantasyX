class_name LagoonSeabed
extends MeshInstance3D
## Procedural lagoon floor for the water test scene (M1-RND-01): dry beach to the south (+Z),
## a gently shelving sand lagoon, then a reef drop-off to open sea in the north (-Z).
## Heights are metres relative to mean sea level (tide datum 0, haluna.md). Deterministic.

@export var size_m := Vector2(300.0, 220.0)
## Centre of the grid in world XZ.
@export var centre_m := Vector2(0.0, -50.0)
@export_range(0.25, 8.0, 0.25, "suffix:m") var cell_m: float = 1.0
@export var shore_z_m: float = 18.0
## Shoreline wobble along X.
@export var shore_wobble_m: float = 5.0
@export var shore_wobble_period_m: float = 70.0
@export var land_slope: float = 0.07
@export var land_max_m: float = 2.5
@export var lagoon_width_m: float = 70.0
@export var lagoon_slope: float = 0.035
@export var reef_width_m: float = 35.0
@export var reef_depth_m: float = 32.0
## The reef edge meanders this far (m) along X so the drop-off is not a ruler line.
@export var reef_edge_wobble_m: float = 14.0
@export var noise_amplitude_m: float = 0.35
@export var noise_period_m: float = 24.0
@export var noise_seed: int = 7

var _noise := FastNoiseLite.new()


func _ready() -> void:
	_noise.seed = noise_seed
	_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	_noise.frequency = 1.0 / noise_period_m
	_noise.fractal_octaves = 3
	mesh = _build()


## Seabed height (m) at world XZ.
func height_at(x: float, z: float) -> float:
	var shore := shore_z_m + shore_wobble_m * sin(TAU * x / shore_wobble_period_m)
	var s := shore - z  # metres offshore (negative = on land)
	var n := _noise.get_noise_2d(x, z) * noise_amplitude_m
	if s < 0.0:
		return minf(-s * land_slope, land_max_m) + n * 0.5
	var h := -s * lagoon_slope + n
	var edge := (
		lagoon_width_m
		+ _noise.get_noise_2d(x * 0.37, 11.0) * reef_edge_wobble_m
		+ _noise.get_noise_2d(x * 2.3, z * 0.5 + 37.0) * reef_edge_wobble_m * 0.35
	)
	var reef := clampf((s - edge) / reef_width_m, 0.0, 1.0)
	reef = reef * reef * (3.0 - 2.0 * reef)
	return lerpf(h, -reef_depth_m, reef)


func _build() -> ArrayMesh:
	var nx := int(size_m.x / cell_m) + 1
	var nz := int(size_m.y / cell_m) + 1
	var origin := centre_m - size_m * 0.5
	var verts := PackedVector3Array()
	verts.resize(nx * nz)
	for j in nz:
		for i in nx:
			var x := origin.x + i * cell_m
			var z := origin.y + j * cell_m
			verts[j * nx + i] = Vector3(x, height_at(x, z), z)
	var normals := PackedVector3Array()
	normals.resize(nx * nz)
	for j in nz:
		for i in nx:
			var l := verts[j * nx + maxi(i - 1, 0)]
			var r := verts[j * nx + mini(i + 1, nx - 1)]
			var d := verts[maxi(j - 1, 0) * nx + i]
			var u := verts[mini(j + 1, nz - 1) * nx + i]
			normals[j * nx + i] = (u - d).cross(r - l).normalized()
	var indices := PackedInt32Array()
	for j in nz - 1:
		for i in nx - 1:
			var a := j * nx + i
			indices.append_array([a, a + 1, a + nx, a + 1, a + nx + 1, a + nx])
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_INDEX] = indices
	var m := ArrayMesh.new()
	m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return m
