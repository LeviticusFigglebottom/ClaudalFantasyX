class_name HalunaCollision
extends Node3D
## Walk collision for the playable Haluna zone (M2-FP-02), built at runtime from the instanced mood
## scene, which has none (game/levels/_tests/haluna_mood is Environment's and is never edited):
##   Ground  one HeightMapShape3D sampled from HalunaTerrain.height_at over `walk_rect`, on the
##           terrain mesh's own 1 m grid, so the feet meet the drawn sand and turf.
##   Props   a shape per placed kit piece and plant, chosen by `piece_rules` (keyed by the piece's
##           first mesh name, e.g. "house_tile_a"): an oriented box from the piece's mesh bounds
##           (inset), a trunk cylinder, a trimesh (the dock deck), or nothing (gates, garlands,
##           awnings, gulls). A rule may add `extra_boxes` and `ramps` in the piece's frame (the
##           dock's rails, and the slope from the sand up onto its deck).
##   Bounds  an invisible wall `wade_m` out from the shoreline (left open at `shore_gaps`, where the
##           dock crosses it) and walls on the other three edges of `walk_rect`.
## Deterministic (the terrain and the dresser are seeded) and built once, after the dresser.

signal built

const KIND_NONE := "none"
const KIND_BOX := "box"
const KIND_CYLINDER := "cylinder"
const KIND_TRIMESH := "trimesh"
const LOD_SUFFIX := "-lod1"

@export var terrain: HalunaTerrain
@export var dresser: HalunaDresser
## Walkable ground (x, z, width, depth) in metres. Corners sit on whole metres (the terrain grid).
@export var walk_rect: Rect2 = Rect2(-160.0, -130.0, 200.0, 260.0)
@export var cell_m: float = 1.0
## How far past the waterline (where the ground meets the tide datum) the sea wall stands.
@export var wade_m: float = 5.0
## Spacing of the sea wall's points along the shore (z).
@export var shore_step_m: float = 4.0
@export var wall_height_m: float = 6.0
@export var wall_thickness_m: float = 1.0
## Openings in the sea wall: Vector3(x, z, radius). A wall segment whose middle lies inside is skipped.
@export var shore_gaps: Array[Vector3] = []
## Piece kind -> {"shape": box|cylinder|trimesh|none, "inset_m", "radius_m", "height_m",
## "extra_boxes": [[cx, cy, cz, sx, sy, sz], ...] in the piece's frame}. Unlisted kinds use
## `default_rule`.
@export var piece_rules: Dictionary = {}
@export var default_rule: Dictionary = {"shape": "box", "inset_m": 0.0}
## Thickness of a rule's "ramps" slabs ([x0, y0, x1, y1, width] in the piece's frame, top surface).
@export var ramp_thickness_m: float = 0.3
## Pieces whose origin lies outside walk_rect grown by this much are skipped (far ruins, the islet).
@export var piece_margin_m: float = 20.0

var ground: StaticBody3D
var props: StaticBody3D
var bounds: StaticBody3D
var heightmap: HeightMapShape3D
var shape_count := 0
var build_msec := 0
## Piece kind -> number of pieces given collision (tests, README).
var kinds: Dictionary = {}
## The sea wall's points (x, z), north to south.
var shore_line := PackedVector2Array()


func build() -> void:
	var t0 := Time.get_ticks_msec()
	for child in get_children():
		remove_child(child)
		child.free()
	shape_count = 0
	kinds.clear()
	ground = _body(&"Ground")
	props = _body(&"Props")
	bounds = _body(&"Bounds")
	_build_ground()
	_build_props()
	_build_bounds()
	build_msec = Time.get_ticks_msec() - t0
	built.emit()


## Ground height at (x, z), as the heightmap sees it (exact on grid points).
func ground_height(x: float, z: float) -> float:
	return terrain.height_at(x, z) if terrain != null else 0.0


## True when (x, z) is over the walkable heightmap.
func covers(x: float, z: float) -> bool:
	return walk_rect.has_point(Vector2(x, z))


func _body(body_name: StringName) -> StaticBody3D:
	var b := StaticBody3D.new()
	b.name = body_name
	add_child(b)
	return b


func _build_ground() -> void:
	if terrain == null:
		push_error("HalunaCollision: no terrain")
		return
	var nx := int(round(walk_rect.size.x / cell_m)) + 1
	var nz := int(round(walk_rect.size.y / cell_m)) + 1
	var heights := PackedFloat32Array()
	heights.resize(nx * nz)
	for j in nz:
		var z := walk_rect.position.y + j * cell_m
		for i in nx:
			heights[j * nx + i] = terrain.height_at(walk_rect.position.x + i * cell_m, z)
	heightmap = HeightMapShape3D.new()
	heightmap.map_width = nx
	heightmap.map_depth = nz
	heightmap.map_data = heights
	var cs := CollisionShape3D.new()
	cs.name = &"Heightmap"
	cs.shape = heightmap
	# A heightmap is centred on its shape origin with one unit per cell; scale XZ to the cell size.
	var centre := walk_rect.position + walk_rect.size * 0.5
	cs.transform = Transform3D(Basis.from_scale(Vector3(cell_m, 1.0, cell_m)), Vector3(centre.x, 0.0, centre.y))
	ground.add_child(cs)
	shape_count += 1


func _build_props() -> void:
	if dresser == null:
		push_error("HalunaCollision: no dresser")
		return
	var reach := walk_rect.grow(piece_margin_m)
	for child in dresser.get_children():
		var piece := child as Node3D
		if piece == null or piece is MultiMeshInstance3D:
			continue
		var p := piece.global_position
		if not reach.has_point(Vector2(p.x, p.z)):
			continue
		var kind := piece_kind(piece)
		var rule: Dictionary = piece_rules.get(kind, default_rule)
		var shape := String(rule.get("shape", KIND_BOX))
		if shape == KIND_NONE:
			continue
		var before := shape_count
		match shape:
			KIND_CYLINDER:
				_add_cylinder(piece, float(rule.get("radius_m", 0.5)), float(rule.get("height_m", 3.0)))
			KIND_TRIMESH:
				_add_trimesh(piece)
			_:
				_add_box(piece, float(rule.get("inset_m", 0.0)))
		for e: Array in rule.get("extra_boxes", []):
			_add_local_box(piece, Vector3(e[0], e[1], e[2]), Vector3(e[3], e[4], e[5]))
		for r: Array in rule.get("ramps", []):
			_add_ramp(piece, Vector2(r[0], r[1]), Vector2(r[2], r[3]), float(r[4]))
		if shape_count > before:
			kinds[kind] = int(kinds.get(kind, 0)) + 1


## A dressed piece's kind: the name of its first mesh (the kit names meshes after the piece).
static func piece_kind(piece: Node) -> String:
	for mi in piece.find_children("*", "MeshInstance3D", true, false):
		return String(mi.name).trim_suffix(LOD_SUFFIX)
	return ""


## The piece's mesh bounds in its own (unscaled) frame, LOD meshes left out.
static func local_bounds(piece: Node3D) -> AABB:
	var out := AABB()
	var first := true
	var to_local := piece.global_transform.orthonormalized().affine_inverse()
	for n in piece.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null or String(mi.name).ends_with(LOD_SUFFIX):
			continue
		var a := (to_local * mi.global_transform) * mi.get_aabb()
		out = a if first else out.merge(a)
		first = false
	return out


func _add_box(piece: Node3D, inset: float) -> void:
	var a := local_bounds(piece)
	if a.size == Vector3.ZERO:
		return
	var size := Vector3(maxf(a.size.x - inset * 2.0, 0.1), a.size.y, maxf(a.size.z - inset * 2.0, 0.1))
	_add_local_box(piece, a.get_center(), size)


func _add_local_box(piece: Node3D, centre: Vector3, size: Vector3) -> void:
	var box := BoxShape3D.new()
	box.size = size
	var frame := piece.global_transform.orthonormalized()
	_add_shape(props, box, Transform3D(frame.basis, frame * centre))


## A walkable slab whose top runs from (x0, y0) to (x1, y1) along the piece's local X, `width` wide.
func _add_ramp(piece: Node3D, from: Vector2, to: Vector2, width: float) -> void:
	var run := to - from
	var box := BoxShape3D.new()
	box.size = Vector3(run.length(), ramp_thickness_m, width)
	var pitch := Basis(Vector3.BACK, atan2(run.y, run.x))
	var centre := (
		Vector3((from.x + to.x) * 0.5, (from.y + to.y) * 0.5, 0.0) + pitch * (Vector3.DOWN * ramp_thickness_m * 0.5)
	)
	var frame := piece.global_transform.orthonormalized()
	_add_shape(props, box, Transform3D(frame.basis * pitch, frame * centre))


func _add_cylinder(piece: Node3D, radius: float, height: float) -> void:
	var cyl := CylinderShape3D.new()
	cyl.radius = radius
	cyl.height = height
	_add_shape(props, cyl, Transform3D(Basis.IDENTITY, piece.global_position + Vector3.UP * height * 0.5))


func _add_trimesh(piece: Node3D) -> void:
	for n in piece.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null or String(mi.name).ends_with(LOD_SUFFIX):
			continue
		var shape := mi.mesh.create_trimesh_shape()
		if shape != null:
			_add_shape(props, shape, mi.global_transform)


func _add_shape(body: StaticBody3D, shape: Shape3D, xf: Transform3D) -> void:
	var cs := CollisionShape3D.new()
	cs.shape = shape
	cs.transform = xf
	body.add_child(cs)
	shape_count += 1


func _build_bounds() -> void:
	shore_line = PackedVector2Array()
	var z0 := walk_rect.position.y
	var z1 := walk_rect.end.y
	var steps := int(ceil((z1 - z0) / shore_step_m))
	for k in steps + 1:
		var z := minf(z0 + k * shore_step_m, z1)
		var x := minf(terrain.inland_m(0.0, z) + wade_m, walk_rect.end.x) if terrain != null else walk_rect.end.x
		shore_line.append(Vector2(x, z))
	for k in shore_line.size() - 1:
		var a := shore_line[k]
		var b := shore_line[k + 1]
		if _in_gap((a + b) * 0.5):
			continue
		_wall(a, b)
	var nw := walk_rect.position
	var ne := Vector2(walk_rect.end.x, walk_rect.position.y)
	var sw := Vector2(walk_rect.position.x, walk_rect.end.y)
	var se := walk_rect.end
	_wall(nw, Vector2(shore_line[0].x, nw.y))
	_wall(sw, Vector2(shore_line[shore_line.size() - 1].x, se.y))
	_wall(nw, sw)


func _in_gap(p: Vector2) -> bool:
	for g: Vector3 in shore_gaps:
		if p.distance_to(Vector2(g.x, g.y)) <= g.z:
			return true
	return false


## A wall from a to b (x, z), standing on the ground at its middle.
func _wall(a: Vector2, b: Vector2) -> void:
	var mid := (a + b) * 0.5
	var along := b - a
	if along.length() <= 0.0:
		return
	var box := BoxShape3D.new()
	box.size = Vector3(along.length() + wall_thickness_m, wall_height_m, wall_thickness_m)
	var yaw := atan2(-along.y, along.x)
	var y := ground_height(mid.x, mid.y)
	_add_shape(bounds, box, Transform3D(Basis(Vector3.UP, yaw), Vector3(mid.x, y, mid.y)))
