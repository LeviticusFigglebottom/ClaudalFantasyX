class_name UnderwaterRig
extends Node3D
## The underwater look (M2-RND-02, SPEC signature R&D: Rhen the lamp-diver's world). Docs:
## docs/kb/tech/underwater.md. Data: game/data/vfx/underwater.json. Put one in a zone with a WaterSurface;
## it builds, around the game camera:
## - the post: two full-screen passes drawn after everything (underwater_post_mul / _add). Per-channel
##   absorption over the water each ray crosses, and in-scatter that darkens with depth. Per pixel, so a
##   half-submerged camera gets a clean waterline.
## - the surface from below (water_underside.gdshader on a copy of the water's surface mesh): the Snell
##   window and total internal reflection.
## - god rays: a FogVolume with underwater_shafts.gdshader (tiers with "god_rays", under volumetric fog).
## - marine snow: particles in a box around the camera, shown only while the camera is underwater.
## - Rhen's lantern: an oil-lamp OmniLight3D on `lantern_target`, with a volumetric halo.
## Tiers: graphics_presets.json presets[].tiers.underwater picks a row of the data's "quality"
## (GraphicsRuntime.apply_system_tiers calls set_quality with the preset id).

const DATA_PATH := "res://game/data/vfx/underwater.json"
const POST_MUL_SHADER := "res://game/shaders/water/underwater_post_mul.gdshader"
const POST_ADD_SHADER := "res://game/shaders/water/underwater_post_add.gdshader"
const UNDERSIDE_SHADER := "res://game/shaders/water/water_underside.gdshader"
const SHAFTS_SHADER := "res://game/shaders/water/underwater_shafts.gdshader"
const SNOW_DRAW := "res://game/world/water/underwater/underwater_snow_draw.tres"
const TIER_SYSTEM := "underwater"
const POST_SIMPLE := "simple"
## The post draws after every other transparent: the multiply pass, then the add pass.
const PRIORITY_MUL := 126
const PRIORITY_ADD := 127
## The post quads must never be culled (their vertex stage covers the screen).
const POST_CULL_MARGIN := 16384.0
## Snow is shown once the camera is this far below the rest plane (it would hang in the air above).
const SNOW_SHOW_DEPTH_M := 0.1
## The data's optics keys each shader takes as float uniforms of the same name.
const OPTICS_POST: Array[String] = [
	"scatter_strength",
	"depth_falloff_m",
	"down_darkening",
	"meniscus_px",
	"lens_m",
	"max_distance_m",
	"camera_light_weight"
]
const OPTICS_UNDERSIDE: Array[String] = [
	"ior", "window_soft_deg", "window_alpha", "tir_alpha", "sun_disc", "sun_halo", "tir_gain", "lens_m"
]

static var _data_cache: Dictionary = {}

## The zone's water: its wave field, rest plane and surface mesh.
@export var water: WaterSurface
## Where Rhen's lantern hangs (his hand or lamp node); null: no lantern.
@export var lantern_target: Node3D
## A preset id (low, medium, high, ultra); set_quality() maps it through graphics_presets.json.
@export var quality: String = "high":
	set(value):
		quality = value
		if is_inside_tree():
			_apply_quality()

## The zone's water look (underwater.json "looks"): its colours override the defaults (M2-RND-09:
## "night_sea" keeps the abyss_navy deep for ch20, ch21 and night dives). "" = the defaults (Act I).
@export var look: String = "":
	set(value):
		look = value
		if is_inside_tree():
			_build_colors()

## false switches every part off (the post, the underside, god rays, snow, the lantern): the A/B for
## cost, and a zone's way to drop the look without removing the node.
@export var active := true:
	set(value):
		active = value
		if is_inside_tree():
			_apply_quality()

var data: Dictionary = {}
var post_mul_material: ShaderMaterial
var post_add_material: ShaderMaterial
var underside_material: ShaderMaterial
var shafts_material: ShaderMaterial
var post_mul: MeshInstance3D
var post_add: MeshInstance3D
var underside: MeshInstance3D
var fog: FogVolume
var snow: GPUParticles3D
var lantern: OmniLight3D
# The Environment whose volumetric fog this rig authored (null when the zone authored fog itself).
var _fog_env: Environment
# The scene's directional lights (the daylight that reaches the water).
var _lights: Array[DirectionalLight3D] = []
# The zone's glimmer fields, whose motes get their underwater path back (M2-RND-09 item 5).
var _fields: Array[GlimmerField] = []
var _sigma := Vector3.ZERO


static func load_data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_data_cache = parsed as Dictionary
		else:
			push_warning("UnderwaterRig: cannot read %s" % DATA_PATH)
	return _data_cache


## The data's quality row for a preset (graphics_presets.json tiers.underwater; the id itself as a fallback).
static func tier_for_preset(preset_id: String) -> String:
	var tier := GraphicsSettings.preset_tier(preset_id, TIER_SYSTEM)
	return tier if tier != "" else preset_id


## GraphicsRuntime.apply_system_tiers: returns false when the preset maps to no quality row.
func set_quality(preset_id: String) -> bool:
	var tier := tier_for_preset(preset_id)
	if not (load_data().get("quality", {}) as Dictionary).has(tier):
		return false
	quality = tier
	return true


func get_quality() -> String:
	return quality


## The quality row in use.
func plan() -> Dictionary:
	return (data.get("quality", {}) as Dictionary).get(quality, {}) as Dictionary


func _ready() -> void:
	data = load_data()
	_build()
	_apply_quality()
	_author_volumetric_fog()
	var root := _scene_root()
	if root != null:
		for l in root.find_children("*", "DirectionalLight3D", true, false):
			_lights.append(l as DirectionalLight3D)
		# find_children's type matches engine classes only, not a script's class_name.
		for f in root.find_children("*", "Node3D", true, false):
			if f is GlimmerField:
				_fields.append(f as GlimmerField)
	get_tree().node_added.connect(_on_node_added)


func _on_node_added(node: Node) -> void:
	if node is GlimmerField and not _fields.has(node):
		_fields.append(node as GlimmerField)


## God rays draw in Godot's volumetric fog, which the presets only gate (they turn it off where a scene
## authored it on, never on). A zone that didn't author fog gets it authored here, with no global density,
## so only the shafts' FogVolume shows; High and Ultra then keep it, Low and Medium gate it off.
func _author_volumetric_fog() -> void:
	var env := _environment()
	if env == null or env.volumetric_fog_enabled:
		return
	env.volumetric_fog_density = 0.0
	_fog_env = env
	GraphicsSettings.set_authored(env, "volumetric_fog_enabled", active and bool(plan().get("god_rays", false)))


## The nearest ancestor holding a WorldEnvironment: the zone (its environment and its lights).
## Searching from the current scene instead found another scene's environment under tools and tests.
## The deferred half of _build_lantern: the scene root as it is now, if the rig is still in one.
func _refresh_bounce_passes() -> void:
	var root := _scene_root()
	if root != null and is_instance_valid(root):
		CharacterShaderTiers.refresh_bounce_passes(root)


func _scene_root() -> Node:
	var n := get_parent()
	while n != null:
		if not n.find_children("*", "WorldEnvironment", true, false).is_empty():
			return n
		n = n.get_parent()
	return null


func _environment() -> Environment:
	var root := _scene_root()
	if root == null:
		return null
	var envs := root.find_children("*", "WorldEnvironment", true, false)
	return (envs[0] as WorldEnvironment).environment if envs.size() > 0 else null


## The scene's daylight: its visible directional lights (energy x colour luminance) over the data's
## light_reference (a noon sun), at least light_floor. Day ~1; a moonlit night ~0.06.
func light_level() -> float:
	var optics := data.get("optics", {}) as Dictionary
	var total := 0.0
	for l: DirectionalLight3D in _lights:
		if is_instance_valid(l) and l.is_visible_in_tree():
			total += l.light_energy * l.light_color.get_luminance()
	return maxf(total / float(optics.get("light_reference", 1.0)), float(optics.get("light_floor", 0.0)))


## The underside lives under the water's surface mesh, outside this node: it leaves with the rig.
func _exit_tree() -> void:
	if underside != null and is_instance_valid(underside):
		if underside.is_inside_tree():
			underside.queue_free()
		else:
			underside.free()
		underside = null


func _process(_delta: float) -> void:
	var cam := get_viewport().get_camera_3d() if is_inside_tree() else null
	if water == null:
		return
	var rest_y := water.global_position.y
	var level := light_level()
	for m: ShaderMaterial in [post_mul_material, post_add_material]:
		m.set_shader_parameter(&"water_rest_y", rest_y)
	post_add_material.set_shader_parameter(&"light_level", level)
	underside_material.set_shader_parameter(&"light_level", level)
	var glow := water.sea_glow_energy * float((data.get("optics", {}) as Dictionary).get("sea_glow_strength", 1.0))
	post_add_material.set_shader_parameter(&"sea_glow_energy", glow)
	underside_material.set_shader_parameter(&"sea_glow_energy", glow)
	shafts_material.set_shader_parameter(&"water_rest_y", rest_y)
	_compensate_glimmer(rest_y)
	_update_lamp_halo()
	if underside != null:
		_follow_surface()
	if cam == null:
		return
	var c := cam.global_position
	var gr := data.get("god_rays", {}) as Dictionary
	var depth := float(gr.get("volume_depth_m", 30.0))
	fog.global_position = Vector3(c.x, rest_y - 0.5 * depth, c.z)
	snow.global_position = c
	snow.visible = active and int(plan().get("particles", 0)) > 0 and c.y < rest_y - SNOW_SHOW_DEPTH_M


## The colours in use: the data's, with the zone look's on top (M2-RND-09).
func colors() -> Dictionary:
	var out := (data.get("colors", {}) as Dictionary).duplicate()
	var over := (data.get("looks", {}) as Dictionary).get(look, {}) as Dictionary
	for key: String in over:
		if not key.begins_with("_") and over[key] is String:
			out[key] = over[key]
	return out


## Re-applies the colour uniforms (a look change at runtime).
func _build_colors() -> void:
	if post_mul_material == null:
		return
	var c := colors()
	for m: ShaderMaterial in [post_mul_material, post_add_material]:
		m.set_shader_parameter(&"col_scatter", Color(str(c.get("scatter", "#1FA3A6"))))
		m.set_shader_parameter(&"col_deep", Color(str(c.get("deep", "#0E4A55"))))
		m.set_shader_parameter(&"col_sea_glow", Color(str(c.get("sea_glow", "#1C6B78"))))
	underside_material.set_shader_parameter(&"col_tir", Color(str(c.get("tir", "#0E4A55"))))
	underside_material.set_shader_parameter(&"col_sea_glow", Color(str(c.get("sea_glow", "#1C6B78"))))


func _build() -> void:
	var palette := colors()
	var optics := data.get("optics", {}) as Dictionary
	var transmit := Color(str(palette.get("transmit", "#1FA3A6"))).srgb_to_linear()
	var dist := float(optics.get("transmit_distance_m", 9.0))
	var sigma := Vector3(
		-log(maxf(transmit.r, 1e-3)) / dist, -log(maxf(transmit.g, 1e-3)) / dist, -log(maxf(transmit.b, 1e-3)) / dist
	)
	_sigma = sigma
	post_mul_material = _post_material(POST_MUL_SHADER, PRIORITY_MUL)
	post_add_material = _post_material(POST_ADD_SHADER, PRIORITY_ADD)
	for m: ShaderMaterial in [post_mul_material, post_add_material]:
		m.set_shader_parameter(&"sigma", sigma)
		m.set_shader_parameter(&"col_scatter", Color(str(palette.get("scatter", "#3FD0C9"))))
		m.set_shader_parameter(&"col_deep", Color(str(palette.get("deep", "#061A2B"))))
		for key in OPTICS_POST:
			m.set_shader_parameter(StringName(key), float(optics.get(key, 0.0)))
	post_mul = _post_quad("UnderwaterPostMul", post_mul_material)
	post_add = _post_quad("UnderwaterPostAdd", post_add_material)
	underside_material = ShaderMaterial.new()
	underside_material.shader = load(UNDERSIDE_SHADER) as Shader
	underside_material.set_shader_parameter(&"col_window", Color(str(palette.get("window", "#2E7FD6"))))
	underside_material.set_shader_parameter(&"col_tir", Color(str(palette.get("tir", "#0E4A55"))))
	var ln := data.get("lantern", {}) as Dictionary
	post_add_material.set_shader_parameter(&"lamp_range_m", float(ln.get("halo_range_m", ln.get("range_m", 9.0))))
	post_add_material.set_shader_parameter(&"lamp_attenuation", float(ln.get("attenuation", 1.4)))
	post_add_material.set_shader_parameter(&"lamp_core_m", float(ln.get("halo_core_m", 0.6)))
	post_add_material.set_shader_parameter(&"lamp_scatter", float(ln.get("halo_strength", 0.0)))
	post_add_material.set_shader_parameter(&"lamp_steps", int(ln.get("halo_steps", 16)))
	post_add_material.set_shader_parameter(&"lamp_absorption", float(ln.get("halo_absorption", 1.0)))
	for key in OPTICS_UNDERSIDE:
		underside_material.set_shader_parameter(StringName(key), float(optics.get(key, 0.0)))
	underside = MeshInstance3D.new()
	underside.name = "WaterUnderside"
	underside.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	underside.material_override = underside_material
	_build_fog(palette)
	_build_snow(palette)
	_build_colors()
	_sync_water_uniforms()


func _post_material(path: String, priority: int) -> ShaderMaterial:
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
	# A FogVolume takes a ShaderMaterial whose shader is a fog shader.
	shafts_material = ShaderMaterial.new()
	shafts_material.shader = load(SHAFTS_SHADER) as Shader
	for key in ["density", "shaft_scale_m", "shaft_contrast", "drift_m_s", "depth_falloff_m"]:
		shafts_material.set_shader_parameter(StringName(key), float(gr.get(key, 0.0)))
	var scatter := Color(str(colors.get("scatter", "#3FD0C9")))
	shafts_material.set_shader_parameter(
		&"col_scatter", scatter.lerp(Color.WHITE, float(gr.get("albedo_white_mix", 0.0)))
	)
	fog = FogVolume.new()
	fog.name = "UnderwaterShafts"
	var half := float(gr.get("volume_half_extent_m", 40.0))
	fog.size = Vector3(2.0 * half, float(gr.get("volume_depth_m", 30.0)), 2.0 * half)
	fog.shape = RenderingServer.FOG_VOLUME_SHAPE_BOX
	fog.material = shafts_material
	add_child(fog)


func _build_snow(colors: Dictionary) -> void:
	var pt := data.get("particulate", {}) as Dictionary
	var mat := ParticleProcessMaterial.new()
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	var half := float(pt.get("box_half_m", 7.0))
	mat.emission_box_extents = Vector3(half, half, half)
	mat.direction = Vector3(0.0, -1.0, 0.0)
	mat.spread = 180.0
	var drift := float(pt.get("drift_m_s", 0.06))
	mat.initial_velocity_min = 0.0
	mat.initial_velocity_max = drift
	mat.gravity = Vector3(0.0, -0.2 * drift, 0.0)
	var size: Array = pt.get("size_m", [0.012, 0.03])
	mat.scale_min = float(size[0])
	mat.scale_max = float(size[1])
	var c := Color(str(colors.get("snow", "#EEF6F4")))
	mat.color = Color(c.r, c.g, c.b, float(pt.get("alpha", 0.5)))
	snow = GPUParticles3D.new()
	snow.name = "MarineSnow"
	snow.local_coords = false
	snow.lifetime = float(pt.get("lifetime_s", 9.0))
	snow.preprocess = snow.lifetime
	snow.process_material = mat
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE
	quad.material = load(SNOW_DRAW) as Material
	snow.draw_pass_1 = quad
	snow.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var box := 2.0 * half + 2.0
	snow.visibility_aabb = AABB(-0.5 * Vector3(box, box, box), Vector3(box, box, box))
	add_child(snow)


func _apply_quality() -> void:
	if post_mul == null:
		return
	var p := plan()
	var full := str(p.get("post", "full")) != POST_SIMPLE
	for m: ShaderMaterial in [post_mul_material, post_add_material]:
		m.set_shader_parameter(&"use_waves", full)
	post_mul.visible = active
	post_add.visible = active
	underside.visible = active
	fog.visible = active and bool(p.get("god_rays", false))
	var n := int(p.get("particles", 0)) if active else 0
	snow.amount = maxi(n, 1)
	snow.emitting = n > 0
	_build_lantern(bool(p.get("lantern_shadows", false)))
	if lantern != null:
		lantern.visible = active
	if _fog_env != null:
		# Only a tier that draws the shafts pays for the fog's froxel pass.
		GraphicsSettings.set_authored(_fog_env, "volumetric_fog_enabled", active and bool(p.get("god_rays", false)))


func _build_lantern(shadows: bool) -> void:
	if lantern_target == null:
		return
	if lantern == null:
		lantern = OmniLight3D.new()
		lantern.name = "RhenLantern"
		lantern_target.add_child(lantern)
		# A positional light near the cast: the mouths' bounce passes now draw (M1-RND-26). Deferred through the rig,
		# so a rig (or a scene) freed before the flush drops the call instead of handing a freed root on.
		_refresh_bounce_passes.call_deferred()
	var ln := data.get("lantern", {}) as Dictionary
	lantern.light_color = Color(str(colors().get("lantern", "#FFB16E")))
	lantern.light_energy = float(ln.get("energy", 5.0))
	lantern.omni_range = float(ln.get("range_m", 9.0))
	lantern.omni_attenuation = float(ln.get("attenuation", 1.4))
	lantern.light_volumetric_fog_energy = float(ln.get("fog_energy", 3.0))
	lantern.light_specular = float(ln.get("specular", 0.4))
	lantern.shadow_enabled = shadows


## The post's lantern halo follows the lamp; dark when there is no lantern or the rig is off.
func _update_lamp_halo() -> void:
	var on := active and lantern != null and is_instance_valid(lantern) and lantern.is_visible_in_tree()
	var ln := data.get("lantern", {}) as Dictionary
	var col := Color(str(colors().get("lantern", "#FFB16E"))).srgb_to_linear()
	var e := float(ln.get("energy", 0.0)) if on else 0.0
	post_add_material.set_shader_parameter(&"lamp_color", Vector3(col.r, col.g, col.b) * e)
	if on:
		post_add_material.set_shader_parameter(&"lamp_pos", lantern.global_position)


## Glimmer motes seen from underwater get their path's absorption back (underwater.json glimmer): released
## fully, held partly, times each field's underwater_compensation. Off when the rig is inactive.
func _compensate_glimmer(rest_y: float) -> void:
	var g := data.get("glimmer", {}) as Dictionary
	var cam := get_viewport().get_camera_3d()
	var cam_under := cam != null and cam.global_position.y < rest_y
	for i in range(_fields.size() - 1, -1, -1):
		var f := _fields[i]
		if not is_instance_valid(f):
			_fields.remove_at(i)
			continue
		if f.draw_material == null:
			continue
		var k := f.underwater_compensation if active else 0.0
		# While the camera is underwater the post absorbs these motes: the field's own model would twice.
		f.set_underwater_absorb_scale(0.0 if k > 0.0 and cam_under else 1.0)
		f.draw_material.set_shader_parameter(&"uw_comp_lift", float(g.get("lift", 0.0)) * k)
		f.draw_material.set_shader_parameter(&"uw_comp_held", float(g.get("held", 0.0)) * k)
		f.draw_material.set_shader_parameter(&"uw_sigma", _sigma)
		f.draw_material.set_shader_parameter(&"uw_rest_y", rest_y)
		f.draw_material.set_shader_parameter(&"uw_max_gain", float(g.get("max_gain", 1.0)))


## The water's wave field and time base onto the post and underside (the same surface in all three).
func _sync_water_uniforms() -> void:
	if water == null:
		return
	var params := water.waves().shader_parameters()
	var mat := water.material
	var time_scale: Variant = mat.get_shader_parameter(&"time_scale") if mat != null else null
	var lod: Variant = mat.get_shader_parameter(&"lod_fade_wavelengths") if mat != null else null
	for m: ShaderMaterial in [post_mul_material, post_add_material, underside_material]:
		for key: StringName in params:
			m.set_shader_parameter(key, params[key])
		m.set_shader_parameter(&"water_time_scale", float(time_scale) if time_scale != null else 1.0)
	underside_material.set_shader_parameter(&"lod_fade_wavelengths", float(lod) if lod != null else 60.0)


## The underside rides on the water's surface mesh (which follows its target and is rebuilt on edits).
func _follow_surface() -> void:
	var surf := water.surface()
	if surf == null:
		return
	if underside.get_parent() != surf:
		if underside.get_parent() != null:
			underside.get_parent().remove_child(underside)
		surf.add_child(underside)
	if underside.mesh != surf.mesh:
		underside.mesh = surf.mesh
		_sync_water_uniforms()
	underside.custom_aabb = surf.custom_aabb
