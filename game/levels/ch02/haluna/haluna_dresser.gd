class_name HalunaDresser
extends Node3D
## Dresses the Haluna mood zone from a layout JSON (M1-ENV-01): terrain, kit pieces, wall runs,
## lintel-gulls, vegetation and grass scatter. Everything is placed from data (no positions in code)
## and is deterministic, so the five screenshot shots are reproducible.
##
## Kit pieces are the .glb files of assets/environments/kits/haluna/ (assets_src/.../build.py). Each
## holds `<piece>` and `<piece>-lod1`; the dresser turns them into visibility-range LODs and maps
## every glTF material slot to `<materials_dir>/<slot>.tres` (or a per-placement override).

signal dressed

const LOD_SUFFIX := "-lod1"
const GROUND_KEY := "ground"
## M2-ENV-02: the night lamps' container (hidden by day) and their flame mesh's name. HalunaCollision
## keys pieces by their first mesh name, and the zone's piece_rules give this one no shape.
const NIGHT_LAMPS := &"NightLamps"
const LAMP_FLAME := &"night_lamp_flame"
const SEA_NORMAL := Vector2(1.0, 0.0)

@export_file("*.json") var layout_path: String = "res://game/levels/ch02/haluna/haluna_layout.json"
@export var terrain: HalunaTerrain
@export var tide: WeatheringTide
@export var ground_material: ShaderMaterial

var layout: Dictionary = {}
var placed: Dictionary = {}  ## piece name -> count (for the review's budget table)

var _scene_cache: Dictionary = {}
var _material_cache: Dictionary = {}
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	dress()


func dress() -> void:
	layout = _load_json(layout_path)
	if layout.is_empty():
		push_error("HalunaDresser: cannot read %s" % layout_path)
		return
	_rng.seed = int(layout.get("seed", 1))
	_build_terrain()
	for spec: Dictionary in layout.get("runs", []):
		_place_run(spec)
	var pieces: Array[Node3D] = []
	var kinds: Array[String] = []
	for spec: Dictionary in layout.get("pieces", []):
		var piece := _place_piece(spec)
		if piece != null:
			pieces.append(piece)
			kinds.append(String(spec["piece"]))
	for spec: Dictionary in layout.get("plants", []):
		_place_plant(spec)
	for spec: Dictionary in layout.get("scatter", []):
		_scatter(spec)
	_place_night_lamps(pieces, kinds, layout.get("night_lamps", {}))
	_place_yard_sets(pieces, kinds, layout.get("yard_sets", {}))
	dressed.emit()


## M3-ENV-701: the lived-in clutter round each house (crates, laundry, rope, jars), from the layout's
## "yard_sets". House i of a listed kind takes variant (i + offset) % n; each entry's local offset is
## `edge` x the kind's half size plus `at`, in the house's frame, on the ground (`dy` above it). An entry
## that would land within `lane_clear_m` of a lane's centre line is left out (the lanes stay walkable).
## Deterministic and draws nothing from the scatter rng, so the rest of the dressing is unchanged.
func _place_yard_sets(pieces: Array[Node3D], kinds: Array[String], cfg: Dictionary) -> void:
	var variants: Array = cfg.get("variants", [])
	var per_kind: Dictionary = cfg.get("per_kind", {})
	if variants.is_empty():
		return
	var offset := int(cfg.get("variant_offset", 0))
	var clear := float(cfg.get("lane_clear_m", 0.0))
	for i in pieces.size():
		if not per_kind.has(kinds[i]):
			continue
		var half: Array = per_kind[kinds[i]]
		var house := pieces[i].transform
		var variant: Array = variants[(i + offset) % variants.size()]
		for entry: Dictionary in variant:
			var edge: Array = entry.get("edge", [0.0, 0.0])
			var at: Array = entry.get("at", [0.0, 0.0])
			var local := Vector3(
				float(edge[0]) * float(half[0]) + float(at[0]), 0.0, float(edge[1]) * float(half[1]) + float(at[1])
			)
			var world := house * local
			if clear > 0.0 and lane_distance(world.x, world.z) < clear:
				continue
			var node := instance_piece(String(entry["piece"]), entry.get("materials", {}))
			if node == null:
				continue
			var yaw := house.basis.get_euler().y + deg_to_rad(float(entry.get("yaw_deg", 0.0)))
			world.y = ground_y(world.x, world.z) + float(entry.get("dy", 0.0))
			node.transform = Transform3D(Basis(Vector3.UP, yaw), world)
			add_child(node)


## The night lamps (`NightLamps`, hidden): an oil lamp, an OmniLight3D and a small emissive flame, at
## each local offset that the layout's "night_lamps" "per_piece" lists for a placed piece's kind.
## HalunaMood shows them in the night mood. Deterministic and draws nothing from the scatter rng, so
## the day dressing is unchanged.
func _place_night_lamps(pieces: Array[Node3D], kinds: Array[String], cfg: Dictionary) -> void:
	var per_piece: Dictionary = cfg.get("per_piece", {})
	if per_piece.is_empty():
		return
	var lamps := Node3D.new()
	lamps.name = NIGHT_LAMPS
	lamps.visible = false
	add_child(lamps)
	var color := Color.html(str(cfg.get("color", "#FFFFFF")))
	var flame_mat := StandardMaterial3D.new()
	flame_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	flame_mat.albedo_color = color
	flame_mat.emission_enabled = true
	flame_mat.emission = color
	flame_mat.emission_energy_multiplier = float(cfg.get("flame_energy", 1.0))
	var flame_mesh := SphereMesh.new()
	flame_mesh.material = flame_mat
	flame_mesh.radius = float(cfg.get("flame_radius_m", 0.05))
	flame_mesh.height = flame_mesh.radius * 2.0
	for i in pieces.size():
		for at: Array in per_piece.get(kinds[i], []):
			var p := pieces[i].transform * Vector3(float(at[0]), float(at[1]), float(at[2]))
			var flame := MeshInstance3D.new()
			flame.name = LAMP_FLAME
			flame.mesh = flame_mesh
			flame.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			flame.position = p
			lamps.add_child(flame)
			var light := OmniLight3D.new()
			light.light_color = color
			light.light_energy = float(cfg.get("energy", 1.0))
			light.omni_range = float(cfg.get("range_m", 5.0))
			light.omni_attenuation = float(cfg.get("attenuation", 1.0))
			light.shadow_enabled = false
			light.position = p
			lamps.add_child(light)


## Distance from (x, z) to the nearest lane centre line of the layout.
func lane_distance(x: float, z: float) -> float:
	var p := Vector2(x, z)
	var best := INF
	for lane: Array in layout.get("lanes", []):
		for k in lane.size() - 1:
			var a := Vector2(float(lane[k][0]), float(lane[k][1]))
			var b := Vector2(float(lane[k + 1][0]), float(lane[k + 1][1]))
			best = minf(best, p.distance_to(Geometry2D.get_closest_point_to_segment(p, a, b)))
	return best


## The night lamps' container, or null when the layout has none.
func night_lamps() -> Node3D:
	return get_node_or_null(NodePath(String(NIGHT_LAMPS))) as Node3D


static func _load_json(path: String) -> Dictionary:
	var text := FileAccess.get_file_as_string(path)
	var parsed: Variant = JSON.parse_string(text)
	return parsed if parsed is Dictionary else {}


# ---- terrain ---------------------------------------------------------------------------------


func _build_terrain() -> void:
	if terrain == null:
		return
	terrain.configure(layout.get("terrain", {}))
	terrain.lanes.clear()
	for lane: Array in layout.get("lanes", []):
		var pts := PackedVector2Array()
		for p: Array in lane:
			pts.append(Vector2(float(p[0]), float(p[1])))
		terrain.lanes.append(pts)
	terrain.pads.clear()
	for p: Array in layout.get("pads", []):
		terrain.pads.append(Vector3(float(p[0]), float(p[1]), float(p[2])))
	terrain.islets.clear()
	for p: Array in layout.get("islets", []):
		terrain.islets.append(Vector4(float(p[0]), float(p[1]), float(p[2]), float(p[3])))
	terrain.material = ground_material
	terrain.build()
	if tide != null and ground_material != null:
		tide.register(ground_material)


func ground_y(x: float, z: float) -> float:
	return terrain.height_at(x, z) if terrain != null else 0.0


# ---- kit pieces ------------------------------------------------------------------------------


func _place_piece(spec: Dictionary) -> Node3D:
	var at: Array = spec.get("at", [0.0, 0.0])
	var x := float(at[0])
	var z := float(at[1])
	var y_v: Variant = spec.get("y", GROUND_KEY)
	var y := ground_y(x, z) if (y_v is String and y_v == GROUND_KEY) else float(y_v)
	y += float(spec.get("dy", 0.0))
	var yaw := deg_to_rad(float(spec.get("yaw_deg", 0.0)))
	var tilt: Array = spec.get("tilt_deg", [0.0, 0.0])
	var s := float(spec.get("scale", 1.0))
	var basis := (
		Basis(Vector3.UP, yaw) * Basis.from_euler(Vector3(deg_to_rad(float(tilt[0])), 0.0, deg_to_rad(float(tilt[1]))))
	)
	var node := instance_piece(String(spec["piece"]), spec.get("materials", {}), float(spec.get("lod1_from_m", -1.0)))
	if node == null:
		return null
	node.transform = Transform3D(basis.scaled(Vector3.ONE * s), Vector3(x, y, z))
	add_child(node)
	if spec.has("gull"):
		_place_gull(node, String(spec["piece"]), String(spec["gull"]))
	return node


## Instances a kit piece with materials and LOD ranges applied (not yet added to the tree).
func instance_piece(piece: String, overrides: Dictionary = {}, lod1_from_m: float = -1.0) -> Node3D:
	var packed := _load_scene(String(layout.get("kit_dir", "")) + piece + ".glb")
	if packed == null:
		push_warning("HalunaDresser: no kit piece '%s'" % piece)
		return null
	var node := packed.instantiate() as Node3D
	node.name = piece
	var lod_from := lod1_from_m if lod1_from_m > 0.0 else float(layout.get("lod1_from_m", 70.0))
	var lod_end := float(layout.get("lod_end_m", 2000.0))
	# M3-ENV-701: small props switch and cull close ([lod1_from, end] in "prop_lods"), and the smallest
	# cast no shadow ("prop_no_shadow"), so the set dressing stays inside the draw and shadow budgets.
	var prop_lod: Array = layout.get("prop_lods", {}).get(piece, [])
	if prop_lod.size() == 2:
		lod_from = float(prop_lod[0]) if lod1_from_m <= 0.0 else lod_from
		lod_end = float(prop_lod[1])
	var no_shadow: bool = layout.get("prop_no_shadow", []).has(piece)
	var ends := PackedFloat32Array([lod_from, lod_end])
	var margin := float(layout.get("lod_margin_m", 2.0))
	for child: Node in node.find_children("*", "MeshInstance3D", true, false):
		var mi := child as MeshInstance3D
		_apply_materials(mi, overrides)
		if no_shadow:
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		# M1-ENV-10: `<piece>` is the visibility child of `<piece>-lod1`, so exactly one draws.
		var lod := 1 if String(mi.name).ends_with(LOD_SUFFIX) else 0
		LodChain.apply(mi, lod, ends, margin, 0.0, LodChain.sibling(mi, lod + 1))
	placed[piece] = int(placed.get(piece, 0)) + 1
	return node


func _apply_materials(mi: MeshInstance3D, overrides: Dictionary) -> void:
	if mi.mesh == null:
		return
	for i in mi.mesh.get_surface_count():
		var src := mi.mesh.surface_get_material(i)
		if src == null:
			continue
		var slot := String(src.resource_name)
		var name_used := String(overrides.get(slot, slot))
		var mat := _kit_material(name_used)
		if mat != null:
			mi.set_surface_override_material(i, mat)


func _kit_material(mat_name: String) -> Material:
	if _material_cache.has(mat_name):
		return _material_cache[mat_name]
	var path := String(layout.get("materials_dir", "")) + mat_name + ".tres"
	var mat: Material = load(path) as Material if ResourceLoader.exists(path) else null
	if mat == null:
		push_warning("HalunaDresser: missing material %s" % path)
	elif tide != null and mat is ShaderMaterial:
		tide.register(mat as ShaderMaterial)
	_material_cache[mat_name] = mat
	return mat


func _load_scene(path: String) -> PackedScene:
	if not _scene_cache.has(path):
		_scene_cache[path] = load(path) as PackedScene if ResourceLoader.exists(path) else null
	return _scene_cache[path]


## A lintel-gull on the house's ridge, facing the sea (haluna.md: yaw toward the nearest sea normal
## +-10 deg; the scatter rule). The kit models the gull facing +X.
func _place_gull(house: Node3D, piece: String, gull: String) -> void:
	var ridges: Dictionary = layout.get("ridges", {})
	if not ridges.has(piece):
		return
	var r: Array = ridges[piece]
	var local := Vector3(float(r[0]), float(r[1]), float(r[2]))
	var world := house.transform * local
	var sea := sea_normal_at(world.x, world.z)
	var jitter := deg_to_rad(float(layout.get("gull_jitter_deg", 10.0))) * (_rng.randf() * 2.0 - 1.0)
	var yaw := atan2(-sea.y, sea.x) + jitter
	var node := instance_piece(gull)
	if node == null:
		return
	node.transform = Transform3D(Basis(Vector3.UP, yaw), world)
	add_child(node)


## Unit (x, z) direction from the land towards the sea at a point: the crescent's normal.
func sea_normal_at(x: float, z: float) -> Vector2:
	if terrain == null:
		return SEA_NORMAL
	var e := 1.0
	var gx := terrain.inland_m(x - e, z) - terrain.inland_m(x + e, z)
	var gz := terrain.inland_m(x, z - e) - terrain.inland_m(x, z + e)
	var g := Vector2(gx, gz)
	return g.normalized() if g.length() > 0.0 else SEA_NORMAL


# ---- wall runs -------------------------------------------------------------------------------


## Lays straight kit segments of `spacing` metres along a polyline, following the ground. `cycle`
## repeats a piece pattern (e.g. two plain segments, then a wind-gap); `gates` replaces segment
## indices with a gate; `skip` leaves gaps (yard entrances). Segments face +Z to the run's right.
func _place_run(spec: Dictionary) -> void:
	var pts := PackedVector2Array()
	for p: Array in spec.get("path", []):
		pts.append(Vector2(float(p[0]), float(p[1])))
	if pts.size() < 2:
		return
	var spacing := float(spec.get("spacing", 2.0))
	var cycle: Array = spec.get("cycle", ["tidewall_straight"])
	var gates: Array = spec.get("gates", [])
	var skip: Array = spec.get("skip", [])
	var gate_piece := String(spec.get("gate_piece", "tidewall_gate"))
	var flip := bool(spec.get("flip", false))
	var dy := float(spec.get("dy", 0.0))
	var total := 0.0
	for i in pts.size() - 1:
		total += pts[i].distance_to(pts[i + 1])
	var n := int(floor(total / spacing))
	# Gates and skips may also be given as world points: the nearest segment takes them.
	for g: Array in spec.get("gates_near", []):
		gates.append(_nearest_segment(pts, spacing, n, Vector2(float(g[0]), float(g[1]))))
	for g: Array in spec.get("skip_near", []):
		skip.append(_nearest_segment(pts, spacing, n, Vector2(float(g[0]), float(g[1]))))
	for k in n:
		if skip.has(k):
			continue
		var a := _along(pts, k * spacing)
		var b := _along(pts, (k + 1) * spacing)
		var mid := (a + b) * 0.5
		var dir := (b - a).normalized()
		var yaw := atan2(-dir.y, dir.x) + (PI if flip else 0.0)
		var piece := gate_piece if gates.has(k) else String(cycle[k % cycle.size()])
		var node := instance_piece(piece)
		if node == null:
			continue
		var y := minf(ground_y(a.x, a.y), ground_y(b.x, b.y)) + dy
		node.transform = Transform3D(Basis(Vector3.UP, yaw), Vector3(mid.x, y, mid.y))
		add_child(node)


static func _nearest_segment(pts: PackedVector2Array, spacing: float, n: int, p: Vector2) -> int:
	var best := 0
	var best_d := INF
	for k in n:
		var mid := (_along(pts, k * spacing) + _along(pts, (k + 1) * spacing)) * 0.5
		var d := mid.distance_squared_to(p)
		if d < best_d:
			best_d = d
			best = k
	return best


static func _along(pts: PackedVector2Array, dist: float) -> Vector2:
	var left := dist
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		if left <= seg:
			return pts[i].lerp(pts[i + 1], left / maxf(seg, 0.0001))
		left -= seg
	return pts[pts.size() - 1]


# ---- vegetation ------------------------------------------------------------------------------


func _place_plant(spec: Dictionary) -> void:
	var kinds: Dictionary = layout.get("plant_kinds", {})
	var kind_name := String(spec.get("plant", ""))
	if not kinds.has(kind_name):
		push_warning("HalunaDresser: unknown plant '%s'" % kind_name)
		return
	var kind: Dictionary = kinds[kind_name]
	var packed := _load_scene(String(kind["glb"]))
	if packed == null:
		return
	var node := packed.instantiate() as Node3D
	var plant := VegetationPlant.new()
	plant.name = kind_name
	var mats: Dictionary[StringName, Material] = {}
	var kmats: Dictionary = kind.get("materials", {})
	for slot: String in kmats:
		mats[StringName(slot)] = load(String(kmats[slot])) as Material
	plant.materials = mats
	var lods: Array = kind.get("lod_end_m", [45.0, 120.0, 400.0])
	plant.lod_end_m = PackedFloat32Array(lods)
	plant.small_foliage = bool(kind.get("small_foliage", false))
	plant.add_child(node)
	var at: Array = spec.get("at", [0.0, 0.0])
	var x := float(at[0])
	var z := float(at[1])
	var yaw := deg_to_rad(float(spec.get("yaw_deg", 0.0)))
	if bool(spec.get("lean_to_sea", false)):
		var sea := sea_normal_at(x, z)
		yaw = atan2(-sea.y, sea.x) + deg_to_rad(float(spec.get("yaw_deg", 0.0)))
	var s := float(spec.get("scale", 1.0))
	plant.transform = Transform3D(Basis(Vector3.UP, yaw).scaled(Vector3.ONE * s), Vector3(x, ground_y(x, z), z))
	add_child(plant)
	placed[kind_name] = int(placed.get(kind_name, 0)) + 1


## Seeded MultiMesh scatter of a vegetation card mesh over a rectangle, kept to an inland band and
## off the lanes, each instance set on the terrain.
func _scatter(spec: Dictionary) -> void:
	var packed := _load_scene(String(spec["glb"]))
	if packed == null:
		return
	var src := packed.instantiate()
	var mi_src := src.find_child(String(spec.get("mesh_node", "")), true, false) as MeshInstance3D
	if mi_src == null:
		src.free()
		return
	var rng := RandomNumberGenerator.new()
	rng.seed = int(spec.get("seed", 1))
	var rect: Array = spec.get("rect", [0.0, 0.0, 10.0, 10.0])
	var count := int(spec.get("count", 100))
	var band: Array = spec.get("inland_m", [-1000.0, 1000.0])
	var scale_r: Array = spec.get("scale", [0.8, 1.2])
	var max_lane := float(spec.get("max_lane", 0.2))
	var noise := FastNoiseLite.new()
	noise.seed = int(spec.get("seed", 1))
	noise.frequency = float(spec.get("patch_frequency", 0.1))
	var patch := float(spec.get("patch_threshold", -0.2))
	var xforms: Array[Transform3D] = []
	var attempts := 0
	while xforms.size() < count and attempts < count * 8:
		attempts += 1
		var x := float(rect[0]) + rng.randf() * float(rect[2])
		var z := float(rect[1]) + rng.randf() * float(rect[3])
		var yaw := rng.randf() * TAU
		var s := rng.randf_range(float(scale_r[0]), float(scale_r[1]))
		var d := terrain.inland_m(x, z) if terrain != null else 0.0
		if d < float(band[0]) or d > float(band[1]):
			continue
		if terrain != null and terrain.lane_at(x, z) > max_lane:
			continue
		if noise.get_noise_2d(x, z) < patch:
			continue
		xforms.append(Transform3D(Basis(Vector3.UP, yaw).scaled(Vector3.ONE * s), Vector3(x, ground_y(x, z), z)))
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = mi_src.mesh
	mm.instance_count = xforms.size()
	for i in xforms.size():
		mm.set_instance_transform(i, xforms[i])
	var mmi := MultiMeshInstance3D.new()
	mmi.name = String(spec.get("name", "Scatter"))
	mmi.multimesh = mm
	mmi.material_override = load(String(spec["material"])) as Material
	mmi.visibility_range_end = float(spec.get("visibility_end_m", 0.0))
	VegetationScatter.tag(mmi)
	add_child(mmi)
	src.free()
	placed[mmi.name] = xforms.size()
