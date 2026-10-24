class_name PemakarKitPreview
extends Node3D
## The Pemakar kit preview (M3-ENV-03, docs/kb/art/environments/pemakar.md): dresses the town's ten
## tiers from a generated layout (assets_src/environments/kits/pemakar/pemakar_layout.py) and lights it
## in one of two sub-frames, `dusk` (ch05_dusk) or `night` (the color script's ch05), from
## pemakar_preview_moods.json. Everything is placed from data and is deterministic, so the composed
## shots in pemakar_kit_shots.json are reproducible.
##
## Kit pieces are assets/environments/kits/pemakar/*.glb (`<piece>` + `<piece>-lod1`, chained so one LOD
## draws at every distance, LodChain); every glTF slot maps to `<materials_dir>/<slot>.tres` unless the
## placement overrides it. The Lanternfall leaf-boats are one MultiMesh, the distant festival lights on
## the massif another (env_far_lights), and the lamps are OmniLight3Ds whose energy the mood scales.

signal dressed

const LOD_SUFFIX := "-lod1"
const BASE_ENERGY_META := &"pemakar_base_energy"
const GLOBAL_SUN := &"hymn_sun_direction"
const GLOBAL_TIME_OF_DAY := &"hymn_time_of_day"
const GLOBAL_GLIMMER := &"hymn_glimmer"
const WRITTEN_GLOBALS: Array[StringName] = [GLOBAL_SUN, GLOBAL_TIME_OF_DAY, GLOBAL_GLIMMER]
const FAR_LIGHT_SHADER := "res://game/shaders/environment/env_far_lights.gdshader"
## The distance (m from the town's foot) at which a far light reaches the largest size in the layout.
const FAR_SIZE_RANGE_M := 700.0

@export_file("*.json") var layout_path: String = "res://game/levels/_tests/pemakar_kit/pemakar_preview_layout.json"
@export_file("*.json") var moods_path: String = "res://game/levels/_tests/pemakar_kit/pemakar_preview_moods.json"
## &"dusk" or &"night". Takes effect at once when set in the tree (the shot manifest sets it per shot,
## every frame, so setting the mood already applied does nothing).
@export var mood: StringName = &"night":
	set(value):
		mood = value
		if is_node_ready() and mood != _applied_mood:
			apply_mood()
@export var world_environment: WorldEnvironment
@export var water: WaterSurface
@export var lights_root: Node3D

var layout: Dictionary = {}
var placed: Dictionary = {}  ## piece name -> count
var lamps: Array[OmniLight3D] = []
var boats: MultiMeshInstance3D
var far_lights: MultiMeshInstance3D
var sea_lights: MultiMeshInstance3D

var _scene_cache: Dictionary = {}
var _material_cache: Dictionary = {}
var _applied_mood: StringName = &""
var _wrote_globals := false


func _ready() -> void:
	dress()
	apply_mood()


func _exit_tree() -> void:
	restore_globals()


## Places everything in the layout under this node. Safe to call once.
func dress() -> void:
	layout = load_json(layout_path)
	if layout.is_empty():
		push_error("PemakarKitPreview: cannot read %s" % layout_path)
		return
	var root := Node3D.new()
	root.name = "Pieces"
	add_child(root)
	for spec: Dictionary in layout.get("pieces", []):
		var node := instance_piece(String(spec["piece"]), spec.get("materials", {}))
		if node != null:
			node.transform = spec_transform(spec)
			root.add_child(node)
	boats = make_boats(layout.get("boats", {}))
	if boats != null:
		add_child(boats)
	var lamp_root := Node3D.new()
	lamp_root.name = "Lamps"
	add_child(lamp_root)
	for spec: Dictionary in layout.get("lights", []):
		var lamp := make_lamp(spec)
		lamp_root.add_child(lamp)
		lamps.append(lamp)
	far_lights = make_far_lights(layout.get("far_lights", {}), "FarLights")
	if far_lights != null:
		add_child(far_lights)
	sea_lights = make_far_lights(layout.get("sea_lights", {}), "SeaLights")
	if sea_lights != null:
		add_child(sea_lights)
	for spec: Dictionary in layout.get("plants", []):
		_place_plant(spec)
	dressed.emit()


## A kit piece with its slot materials and its LOD chain (`<piece>` drawn as the visibility child of
## `<piece>-lod1`), or null if the kit has no such piece.
func instance_piece(piece: String, overrides: Dictionary = {}) -> Node3D:
	var packed := _load_scene(String(layout.get("kit_dir", "")) + piece + ".glb")
	if packed == null:
		push_warning("PemakarKitPreview: no kit piece '%s'" % piece)
		return null
	var node := packed.instantiate() as Node3D
	node.name = piece
	var ends := PackedFloat32Array([float(layout.get("lod1_from_m", 70.0)), float(layout.get("lod_end_m", 4000.0))])
	var margin := float(layout.get("lod_margin_m", 2.0))
	for child: Node in node.find_children("*", "MeshInstance3D", true, false):
		var mi := child as MeshInstance3D
		_apply_materials(mi, overrides)
		var lod := 1 if String(mi.name).ends_with(LOD_SUFFIX) else 0
		LodChain.apply(mi, lod, ends, margin, 0.0, LodChain.sibling(mi, lod + 1))
	placed[piece] = int(placed.get(piece, 0)) + 1
	return node


## The leaf-boats as one MultiMesh of the kit's leaf_boat_lit (LOD0) with its slot materials.
func make_boats(spec: Dictionary) -> MultiMeshInstance3D:
	var transforms: Array = spec.get("transforms", [])
	var mesh := kit_mesh(String(spec.get("piece", "")))
	if mesh == null or transforms.is_empty():
		return null
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = mesh
	mm.instance_count = transforms.size()
	for i in transforms.size():
		var t: Array = transforms[i]
		mm.set_instance_transform(
			i, Transform3D(Basis(Vector3.UP, float(t[3])), Vector3(float(t[0]), float(t[1]), float(t[2])))
		)
	var mmi := MultiMeshInstance3D.new()
	mmi.name = "LeafBoats"
	mmi.multimesh = mm
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mmi


## A copy of a kit piece's LOD0 mesh with its slot materials set on the surfaces (for MultiMesh use).
func kit_mesh(piece: String) -> Mesh:
	var packed := _load_scene(String(layout.get("kit_dir", "")) + piece + ".glb")
	if packed == null:
		return null
	var inst := packed.instantiate()
	var mi := inst.find_child(piece, true, false) as MeshInstance3D
	var mesh: Mesh = null
	if mi != null and mi.mesh != null:
		mesh = mi.mesh.duplicate() as Mesh
		for i in mesh.get_surface_count():
			var src := mesh.surface_get_material(i)
			var mat := _kit_material(String(src.resource_name)) if src != null else null
			if mat != null:
				mesh.surface_set_material(i, mat)
	inst.free()
	return mesh


func make_lamp(spec: Dictionary) -> OmniLight3D:
	var lamp := OmniLight3D.new()
	var at: Array = spec["at"]
	lamp.position = Vector3(float(at[0]), float(at[1]), float(at[2]))
	lamp.light_color = Color.html(String(spec.get("color", "#FFFFFF")))
	lamp.omni_range = float(spec.get("range", 3.0))
	lamp.shadow_enabled = bool(spec.get("shadow", false))
	lamp.set_meta(BASE_ENERGY_META, float(spec.get("energy", 1.0)))
	lamp.light_energy = float(spec.get("energy", 1.0))
	return lamp


## Lights too small to model at their range (the distant festival lights on the massif, the boats that
## reached the sea): one MultiMesh of camera-facing quads, larger with distance from the town's foot.
func make_far_lights(spec: Dictionary, node_name: String = "FarLights") -> MultiMeshInstance3D:
	var points: Array = spec.get("points", [])
	if points.is_empty():
		return null
	var sizes: Array = spec.get("size_m", [1.0, 1.0])
	var quad := QuadMesh.new()
	quad.size = Vector2(2.0, 2.0)  # half-size 1, so an instance's scale is its radius
	var mat := ShaderMaterial.new()
	mat.shader = load(FAR_LIGHT_SHADER) as Shader
	mat.set_shader_parameter(&"col_light", Color.html(String(spec.get("color", "#FFFFFF"))))
	mat.set_shader_parameter(&"energy", float(spec.get("energy", 1.0)))
	quad.material = mat
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = quad
	mm.instance_count = points.size()
	for i in points.size():
		var p: Array = points[i]
		var pos := Vector3(float(p[0]), float(p[1]), float(p[2]))
		var k := clampf(Vector2(pos.x, pos.z).length() / FAR_SIZE_RANGE_M, 0.0, 1.0)
		var s := lerpf(float(sizes[0]), float(sizes[1]), k)
		mm.set_instance_transform(i, Transform3D(Basis().scaled(Vector3.ONE * s), pos))
	var mmi := MultiMeshInstance3D.new()
	mmi.name = node_name
	mmi.multimesh = mm
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mmi


## Lights the scene in `mood` (pemakar_preview_moods.json) and writes the sun, time and glimmer globals.
func apply_mood() -> void:
	var table: Dictionary = load_json(moods_path).get("moods", {})
	if not table.has(String(mood)):
		push_error("PemakarKitPreview: unknown mood '%s'" % mood)
		return
	var m: Dictionary = table[String(mood)]
	if world_environment != null:
		world_environment.environment = load(String(m["environment"])) as Environment
	if lights_root != null:
		var specs: Dictionary = m.get("lights", {})
		for light_name: String in specs:
			var light := lights_root.get_node_or_null(light_name) as DirectionalLight3D
			if light == null:
				continue
			var s: Dictionary = specs[light_name]
			light.visible = bool(s.get("visible", true))
			light.light_color = Color.html(String(s.get("color", "#FFFFFF")))
			light.light_energy = float(s.get("energy", 1.0))
			aim_light(light, float(s.get("elevation_deg", 45.0)), float(s.get("azimuth_deg", 180.0)))
	if water != null:
		water.sea_glow_energy = float(m.get("sea_glow", 0.0))
	var lamp_scale := float(m.get("lamp_scale", 1.0))
	for lamp in lamps:
		lamp.light_energy = float(lamp.get_meta(BASE_ENERGY_META, 1.0)) * lamp_scale
	if far_lights != null:
		var mat := (far_lights.multimesh.mesh as QuadMesh).material as ShaderMaterial
		mat.set_shader_parameter(&"energy", float(m.get("far_lights_energy", 1.0)))
	if sea_lights != null:
		var sea_mat := (sea_lights.multimesh.mesh as QuadMesh).material as ShaderMaterial
		sea_mat.set_shader_parameter(&"energy", float(m.get("sea_lights_energy", 1.0)))
	var sun: Dictionary = m.get("sun", {})
	ShaderGlobals.set_value(
		GLOBAL_SUN, direction_from_angles(float(sun.get("elevation_deg", 45.0)), float(sun.get("azimuth_deg", 180.0)))
	)
	ShaderGlobals.set_value(GLOBAL_TIME_OF_DAY, float(m.get("time_of_day_h", 12.0)))
	var g: Array = m.get("glimmer", [1.0, 1.0, 1.0, 0.0])
	ShaderGlobals.set_value(GLOBAL_GLIMMER, Vector4(float(g[0]), float(g[1]), float(g[2]), float(g[3])))
	_wrote_globals = true
	_applied_mood = mood


## Puts back the project defaults of the globals apply_mood wrote.
func restore_globals() -> void:
	if not _wrote_globals:
		return
	for g in WRITTEN_GLOBALS:
		ShaderGlobals.reset(g)
	_wrote_globals = false


func applied_mood() -> StringName:
	return _applied_mood


## Unit vector toward a source at `elevation_deg` above the horizon and compass `azimuth_deg`
## (0 north = -Z, 90 east = +X).
static func direction_from_angles(elevation_deg: float, azimuth_deg: float) -> Vector3:
	var el := deg_to_rad(elevation_deg)
	var az := deg_to_rad(azimuth_deg)
	return Vector3(sin(az) * cos(el), sin(el), -cos(az) * cos(el))


## Turns a directional light so it shines from that source (a DirectionalLight3D shines along its -Z).
static func aim_light(light: DirectionalLight3D, elevation_deg: float, azimuth_deg: float) -> void:
	var to_source := direction_from_angles(elevation_deg, azimuth_deg)
	light.basis = Basis.looking_at(-to_source, Vector3.UP if absf(to_source.y) < 0.99 else Vector3.FORWARD)


static func spec_transform(spec: Dictionary) -> Transform3D:
	var at: Array = spec.get("at", [0.0, 0.0, 0.0])
	var yaw := deg_to_rad(float(spec.get("yaw_deg", 0.0)))
	return Transform3D(Basis(Vector3.UP, yaw), Vector3(float(at[0]), float(at[1]), float(at[2])))


static func load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed if parsed is Dictionary else {}


func _place_plant(spec: Dictionary) -> void:
	var kinds: Dictionary = layout.get("plant_kinds", {})
	var kind_name := String(spec.get("plant", ""))
	if not kinds.has(kind_name):
		push_warning("PemakarKitPreview: unknown plant '%s'" % kind_name)
		return
	var kind: Dictionary = kinds[kind_name]
	var packed := _load_scene(String(kind["glb"]))
	if packed == null:
		return
	var plant := VegetationPlant.new()
	plant.name = kind_name
	var mats: Dictionary[StringName, Material] = {}
	var kmats: Dictionary = kind.get("materials", {})
	for slot: String in kmats:
		mats[StringName(slot)] = load(String(kmats[slot])) as Material
	plant.materials = mats
	plant.add_child(packed.instantiate())
	var s := float(spec.get("scale", 1.0))
	var xf := spec_transform(spec)
	plant.transform = Transform3D(xf.basis.scaled(Vector3.ONE * s), xf.origin)
	add_child(plant)
	placed[kind_name] = int(placed.get(kind_name, 0)) + 1


func _apply_materials(mi: MeshInstance3D, overrides: Dictionary) -> void:
	if mi.mesh == null:
		return
	for i in mi.mesh.get_surface_count():
		var src := mi.mesh.surface_get_material(i)
		if src == null:
			continue
		var slot := String(src.resource_name)
		var mat := _kit_material(String(overrides.get(slot, slot)))
		if mat != null:
			mi.set_surface_override_material(i, mat)


func _kit_material(mat_name: String) -> Material:
	if _material_cache.has(mat_name):
		return _material_cache[mat_name]
	var path := String(layout.get("materials_dir", "")) + mat_name + ".tres"
	var mat: Material = load(path) as Material if ResourceLoader.exists(path) else null
	if mat == null:
		push_warning("PemakarKitPreview: missing material %s" % path)
	_material_cache[mat_name] = mat
	return mat


func _load_scene(path: String) -> PackedScene:
	if not _scene_cache.has(path):
		_scene_cache[path] = load(path) as PackedScene if ResourceLoader.exists(path) else null
	return _scene_cache[path]
