class_name WaterSphereRig
extends Node3D
## The Reefball arena's suspended water sphere (M3-RND-01, SPEC §6.10). Docs: docs/kb/tech/water_sphere.md. Data:
## game/data/vfx/water_sphere.json. Put one where the ball hangs (this node is its centre); it builds:
## - the ball's surface (water_sphere_surface.gdshader on a sphere mesh): refraction and the sky's reflection
##   from outside, the Snell window and total internal reflection from inside;
## - two full-screen passes drawn after everything (water_sphere_post_mul / _add): absorption and in-scatter along
##   each view ray's water, from outside, inside or across the wall (a meniscus line where the lens meets it);
## - god rays inside the ball: an ellipsoid FogVolume with the underwater shafts (tiers with "god_rays");
## - caustic light on what's inside the ball, in the multiply pass, projected along the sun (tiers with "caustics",
##   M3-RND-04).
## Tiers: set_quality(preset id) picks a row of the data's "quality" (Low: no refraction, a tinted Fresnel shell).
## A `profile` (a row of the data's "profiles", M3-RND-26) overrides sections key by key for one use: the Tamsule
## Bell's held drop is a flattened, still, cyan "tamsule_drop" that glows with its bound light and throws its caustic
## web on the catch-pool, the posts and the bell's underside.

const DATA_PATH := "res://game/data/vfx/water_sphere.json"
const SURFACE_SHADER := "res://game/shaders/water/sphere/water_sphere_surface.gdshader"
const POST_MUL_SHADER := "res://game/shaders/water/sphere/water_sphere_post_mul.gdshader"
const POST_ADD_SHADER := "res://game/shaders/water/sphere/water_sphere_post_add.gdshader"
const SHAFTS_SHADER := "res://game/shaders/water/underwater_shafts.gdshader"
## The post draws after every other transparent: the multiply pass, then the add pass (as UnderwaterRig's).
const PRIORITY_MUL := 126
const PRIORITY_ADD := 127
const POST_CULL_MARGIN := 16384.0
## The data's optics keys each material takes as float uniforms of the same name.
const OPTICS_POST: Array[String] = ["scatter_strength", "depth_falloff_m", "down_darkening", "lens_m", "meniscus_px"]
## The data's caustics keys, the multiply pass's "caustic_<key>" uniforms (M3-RND-04).
const CAUSTIC_KEYS: Array[String] = [
	"strength", "scale_per_m", "speed", "width", "blur_per_m", "fade_in_m", "falloff_m", "view_fade_m", "wall_soft_m"
]
## The data's "under" keys, both passes' "under_<key>" uniforms (the light through the drop under it, M3-RND-26).
const UNDER_KEYS: Array[String] = [
	"strength", "reach_m", "lens_m", "reflect", "reflect_radius_m", "top_m", "floor_m", "scale_per_m", "radius_m"
]
const OPTICS_SURFACE: Array[String] = [
	"ior",
	"refraction_strength",
	"window_soft_deg",
	"tir_gain",
	"tir_alpha",
	"roughness",
	"swell_m",
	"swell_scale_m",
	"swell_speed"
]

static var _data_cache: Dictionary = {}

## The ball's own night sea-glow energy (colour script rule 3: 0.04-0.15, >= 0.08 at night); 0 uses the zone's
## (hymn_zone_sea_glow, GlimmerField.set_scene_sea_glow), as a WaterSurface's does (M3-RND-05).
@export_range(0.0, 0.15, 0.001) var sea_glow_energy: float = 0.0:
	set(value):
		sea_glow_energy = value
		if post_add_material != null:
			post_add_material.set_shader_parameter(&"sea_glow_energy", value)

## A row of the data's "profiles" (empty: the Reefball arena's ball). Set before the rig enters the tree.
@export var profile: String = ""

## A preset id (low, medium, high, ultra).
@export var quality: String = "high":
	set(value):
		quality = value
		if is_inside_tree():
			_apply_quality()

var data: Dictionary = {}
var surface: MeshInstance3D
var surface_material: ShaderMaterial
var post_mul: MeshInstance3D
var post_add: MeshInstance3D
var post_mul_material: ShaderMaterial
var post_add_material: ShaderMaterial
var fog: FogVolume
var shafts_material: ShaderMaterial
var _lights: Array[DirectionalLight3D] = []
var _fog_env: Environment


static func load_data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_data_cache = parsed as Dictionary
		else:
			push_warning("WaterSphereRig: cannot read %s" % DATA_PATH)
	return _data_cache


## GraphicsRuntime-style hook: false when the preset has no quality row.
func set_quality(preset_id: String) -> bool:
	if not (load_data().get("quality", {}) as Dictionary).has(preset_id):
		return false
	quality = preset_id
	return true


func get_quality() -> String:
	return quality


## The data with a profile's sections laid over it key by key (the base for an unknown or empty profile).
static func profile_data(profile_id: String) -> Dictionary:
	var base := load_data()
	var over := (base.get("profiles", {}) as Dictionary).get(profile_id, {}) as Dictionary
	if over.is_empty():
		return base
	var out := base.duplicate(true)
	for section: String in over:
		if section.begins_with("_"):
			continue
		var row: Variant = over[section]
		if typeof(row) == TYPE_DICTIONARY and typeof(out.get(section)) == TYPE_DICTIONARY:
			(out[section] as Dictionary).merge(row as Dictionary, true)
		else:
			out[section] = row
	return out


func plan() -> Dictionary:
	return (data.get("quality", {}) as Dictionary).get(quality, {}) as Dictionary


func radius_m() -> float:
	return float((data.get("sphere", {}) as Dictionary).get("radius_m", 16.0))


## The vertical semi-axis (the radius for a ball).
func semi_axis_y_m() -> float:
	return float((data.get("sphere", {}) as Dictionary).get("semi_axis_y_m", radius_m()))


func _ready() -> void:
	if not profile.is_empty() and not (load_data().get("profiles", {}) as Dictionary).has(profile):
		push_warning("WaterSphereRig: no profile %s in %s" % [profile, DATA_PATH])
	data = profile_data(profile)
	_build()
	_apply_quality()
	var root := _scene_root()
	if root != null:
		for l in root.find_children("*", "DirectionalLight3D", true, false):
			_lights.append(l as DirectionalLight3D)
		var envs := root.find_children("*", "WorldEnvironment", true, false)
		var env := (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null
		if env != null and not env.volumetric_fog_enabled:
			# Only the shafts' FogVolume shows (as UnderwaterRig authors it); presets gate it.
			env.volumetric_fog_density = 0.0
			_fog_env = env
			GraphicsSettings.set_authored(env, "volumetric_fog_enabled", bool(plan().get("god_rays", false)))


func _scene_root() -> Node:
	var n := get_parent()
	while n != null:
		if not n.find_children("*", "WorldEnvironment", true, false).is_empty():
			return n
		n = n.get_parent()
	return null


## The scene's daylight over a noon sun, at least light_floor (as UnderwaterRig.light_level).
func light_level() -> float:
	var optics := data.get("optics", {}) as Dictionary
	var total := 0.0
	for l: DirectionalLight3D in _lights:
		if is_instance_valid(l) and l.is_visible_in_tree():
			total += l.light_energy * l.light_color.get_luminance()
	return maxf(total / float(optics.get("light_reference", 1.0)), float(optics.get("light_floor", 0.0)))


func _process(_delta: float) -> void:
	var level := light_level()
	var c := global_position
	for m: ShaderMaterial in [surface_material, post_mul_material, post_add_material]:
		m.set_shader_parameter(&"sphere_center", c)
		m.set_shader_parameter(&"light_level", level)
	shafts_material.set_shader_parameter(&"water_rest_y", c.y + semi_axis_y_m())
	var sun := _sun()
	if sun != null:
		post_mul_material.set_shader_parameter(&"sun_dir", sun.global_basis.z.normalized())
		post_add_material.set_shader_parameter(&"sun_dir", sun.global_basis.z.normalized())


## The scene's first visible DirectionalLight3D, the sun the caustics fall along (null when there's none).
func _sun() -> DirectionalLight3D:
	for l: DirectionalLight3D in _lights:
		if is_instance_valid(l) and l.is_visible_in_tree():
			return l
	return null


func _build() -> void:
	var colors := data.get("colors", {}) as Dictionary
	var optics := data.get("optics", {}) as Dictionary
	var sp := data.get("sphere", {}) as Dictionary
	var transmit := Color(str(colors.get("transmit", "#1FA3A6"))).srgb_to_linear()
	var dist := float(optics.get("transmit_distance_m", 40.0))
	var sigma := Vector3(
		-log(maxf(transmit.r, 1e-3)) / dist, -log(maxf(transmit.g, 1e-3)) / dist, -log(maxf(transmit.b, 1e-3)) / dist
	)
	surface_material = _material(SURFACE_SHADER, 0)
	post_mul_material = _material(POST_MUL_SHADER, PRIORITY_MUL)
	post_add_material = _material(POST_ADD_SHADER, PRIORITY_ADD)
	for m: ShaderMaterial in [surface_material, post_mul_material, post_add_material]:
		m.set_shader_parameter(&"sphere_radius_m", radius_m())
		m.set_shader_parameter(&"sphere_flatten", semi_axis_y_m() / radius_m())
		m.set_shader_parameter(&"sigma", sigma)
		m.set_shader_parameter(&"col_scatter", Color(str(colors.get("scatter", "#1FA3A6"))))
		m.set_shader_parameter(&"col_deep", Color(str(colors.get("deep", "#0E4A55"))))
		for key in OPTICS_POST:
			m.set_shader_parameter(StringName(key), float(optics.get(key, 0.0)))
	for key in OPTICS_SURFACE:
		surface_material.set_shader_parameter(StringName(key), float(optics.get(key, 0.0)))
	surface_material.set_shader_parameter(&"col_tir", Color(str(colors.get("tir", "#0E4A55"))))
	post_add_material.set_shader_parameter(&"sea_glow_energy", sea_glow_energy)
	post_add_material.set_shader_parameter(&"sea_glow_strength", float(optics.get("sea_glow_strength", 1.0)))
	var caustics := data.get("caustics", {}) as Dictionary
	var under := data.get("under", {}) as Dictionary
	for m: ShaderMaterial in [post_mul_material, post_add_material]:
		for key in CAUSTIC_KEYS:
			m.set_shader_parameter(StringName("caustic_" + key), float(caustics.get(key, 0.0)))
		for key in UNDER_KEYS:
			m.set_shader_parameter(StringName("under_" + key), float(under.get(key, 0.0)))
		m.set_shader_parameter(&"under_color", Color(str(colors.get("under", "#FFFFFF"))))
	var bound := data.get("bound_glow", {}) as Dictionary
	post_add_material.set_shader_parameter(&"bound_glow_color", Color(str(colors.get("bound", "#000000"))))
	post_add_material.set_shader_parameter(&"bound_glow_energy", float(bound.get("energy", 0.0)))
	var mesh := SphereMesh.new()
	mesh.radial_segments = int(sp.get("radial_segments", 64))
	mesh.rings = int(sp.get("rings", 32))
	# The full-screen passes use the exact sphere; the mesh's silhouette must enclose it, or a sliver of sky inside
	# the ball (between the swell's troughs and the facets' sag) is absorbed in stripes at the rim.
	var sag := radius_m() * (1.0 - cos(PI / float(mini(mesh.radial_segments, 2 * mesh.rings))))
	var grow := float(optics.get("swell_m", 0.0)) + sag
	mesh.radius = radius_m() + grow
	mesh.height = 2.0 * (semi_axis_y_m() + grow)
	surface = MeshInstance3D.new()
	surface.name = "SphereSurface"
	surface.mesh = mesh
	surface.material_override = surface_material
	surface.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(surface)
	post_mul = _post_quad("SpherePostMul", post_mul_material)
	post_add = _post_quad("SpherePostAdd", post_add_material)
	_build_fog(colors)


func _material(path: String, priority: int) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(path) as Shader
	m.render_priority = priority
	return m


func _post_quad(node_name: String, mat: ShaderMaterial) -> MeshInstance3D:
	var q := MeshInstance3D.new()
	q.name = node_name
	var mesh := QuadMesh.new()
	mesh.size = Vector2.ONE
	q.mesh = mesh
	q.material_override = mat
	q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	q.extra_cull_margin = POST_CULL_MARGIN
	q.ignore_occlusion_culling = true
	add_child(q)
	return q


func _build_fog(colors: Dictionary) -> void:
	var gr := data.get("god_rays", {}) as Dictionary
	shafts_material = ShaderMaterial.new()
	shafts_material.shader = load(SHAFTS_SHADER) as Shader
	for key in ["density", "shaft_scale_m", "shaft_contrast", "drift_m_s", "depth_falloff_m"]:
		shafts_material.set_shader_parameter(StringName(key), float(gr.get(key, 0.0)))
	var scatter := Color(str(colors.get("scatter", "#1FA3A6")))
	shafts_material.set_shader_parameter(
		&"col_scatter", scatter.lerp(Color.WHITE, float(gr.get("albedo_white_mix", 0.0)))
	)
	fog = FogVolume.new()
	fog.name = "SphereShafts"
	fog.size = 2.0 * Vector3(radius_m(), semi_axis_y_m(), radius_m())
	fog.shape = RenderingServer.FOG_VOLUME_SHAPE_ELLIPSOID
	fog.material = shafts_material
	add_child(fog)


func _apply_quality() -> void:
	if surface_material == null:
		return
	var p := plan()
	surface_material.set_shader_parameter(&"use_refraction", bool(p.get("refraction", true)))
	post_mul_material.set_shader_parameter(&"use_caustics", bool(p.get("caustics", false)))
	post_add_material.set_shader_parameter(&"use_caustics", bool(p.get("caustics", false)))
	fog.visible = bool(p.get("god_rays", false))
	if _fog_env != null:
		GraphicsSettings.set_authored(_fog_env, "volumetric_fog_enabled", bool(p.get("god_rays", false)))
