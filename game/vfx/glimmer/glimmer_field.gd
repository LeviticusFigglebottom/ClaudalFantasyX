class_name GlimmerField
extends Node3D
## Glimmer motes: the luminous remains of the dead (M1-RND-02, SPEC §8.2 item 3).
##
## Drop one into a scene, size its emission volume, pick a mode, and it builds a GPUParticles3D
## child driven by game/shaders/glimmer/glimmer_motes_process.gdshader. All tunables come from
## game/data/vfx/glimmer.json. Docs and the meaning rules: docs/kb/tech/glimmer.md.
##
##   RELEASED  warm gold, rising in slow spirals (the dead leaving)
##   HELD      cool cyan, drifting sideways and down towards the sea (the dead anchored by grief)
##   MACHINE   bound teal, perfectly still (salt-glass lamps, Lit Age conduits)
##
## API (typed; logic is headless-testable, rendering is not required):
##   set_mode(mode) / get_mode()                 immediate switch
##   release(duration_s, origin)                 held/machine -> released over 1.5 s by default, as a
##                                               wave spreading out from origin (default: the field)
##   add_attractor(node, strength, radius_m, ...) motes gather and orbit around a living node
##   remove_attractor(node) / clear_attractors()
##   set_quality(preset_id)                      "low" .. "ultra" (GraphicsSettings preset ids)
##   refresh()                                   re-apply after changing exports at runtime
##   apply_cue(effect, kwargs) / cue_parameters() a .dlg @vfx cue (count, drift, motion, rate)
##   GlimmerField.set_global_focus(pos, radius)  writes hymn_glimmer_focus (every field follows it)
##   GlimmerField.set_scene_glimmer(tint, a)     writes hymn_glimmer (a = scene mote intensity)
##   GlimmerField.set_scene_sea_glow(energy)     writes hymn_zone_sea_glow (zone night sea-glow, rule 3)
##   GlimmerField.sea_glow_violation(...)        checks a frame's sea-glow against rule 3

signal mode_changed(mode: GlimmerState.Mode)
signal release_started(duration_s: float)
signal release_finished

enum EmissionShape { BOX, DISC }

const CONFIG_PATH := "res://game/data/vfx/glimmer.json"
const PROCESS_SHADER := preload("res://game/shaders/glimmer/glimmer_motes_process.gdshader")
const DRAW_SHADER := preload("res://game/shaders/glimmer/glimmer_motes_draw.gdshader")
const REFLECT_SHADER := preload("res://game/shaders/glimmer/glimmer_motes_reflect.gdshader")
const GLOBAL_GLIMMER := &"hymn_glimmer"
const GLOBAL_FOCUS := &"hymn_glimmer_focus"
const GLOBAL_SEA_GLOW := &"hymn_zone_sea_glow"
const MOTES_NODE_NAME := "Motes"
const LIGHT_NODE_NAME := "GlimmerLight"
## = HYMN_GLIMMER_MAX_SPAWN_POINTS in glimmer_motes_process.gdshader (tested).
const MAX_SPAWN_POINTS := 16
## Pass to add_attractor() to take that parameter from glimmer.json.
const USE_DEFAULT := -1.0

@export var mode: GlimmerState.Mode = GlimmerState.Mode.HELD:
	set = set_mode,
	get = get_mode
## Graphics preset id ("low", "medium", "high", "ultra"); empty = glimmer.json default_quality.
@export var quality: String = ""

@export_group("Emission")
@export var emission_shape: EmissionShape = EmissionShape.BOX
## Box: half-extents. Disc: x = outer radius, y = half height (z unused).
@export var emission_extents_m: Vector3 = Vector3(3.0, 1.0, 3.0)
@export var emission_inner_radius_m: float = 0.0
## Scales glimmer.json emitter.amount before the quality tier (density per field).
@export var amount_multiplier: float = 1.0
## Exactly this many motes on every tier (bypasses emitter.amount, amount_multiplier and the tier
## scale). 0 = off. For counted beats (H06: exactly 9 held motes).
@export var fixed_count: int = 0
## false: spawn every mote at once and keep it (no respawn, no fade-out; emitter.persist_*).
@export var respawn: bool = true
## Optional authored spawn points (local to the field, up to MAX_SPAWN_POINTS): mote i starts at
## spawn_points[i % size]. Empty = random in the emission volume.
@export var spawn_points: PackedVector3Array = PackedVector3Array()
## Vertical density gradient of the emission volume: > 1 packs motes low (near the water and the
## figure), < 1 high. 1 = uniform.
@export_range(0.1, 8.0, 0.05) var height_bias: float = 1.0
## Disc emission: > 1 clusters motes toward the centre (near the figure), sparse at the rim.
@export_range(0.1, 8.0, 0.05) var center_bias: float = 1.0
## Motes live in this node's space and move with it (bound light on a moving host: Ilun, a summon,
## the Kite's lamps). Off = world space (free motes left behind by a moving emitter).
@export var local_space: bool = false
## Motion preset from glimmer.json cues.rates ("slow", "normal", "fast"): overrides of the
## released/held motion (the .dlg rate= kwarg).
@export var motion_rate: String = "normal"

@export_group("Scene")
## Seaward direction for held motes (only xz is used).
@export var sea_direction: Vector3 = Vector3(0.0, 0.0, 1.0)
## World height of the water surface: held motes sink through it and are absorbed.
@export var water_height_m: float = 0.0
## Mirror motes in still water at water_height_m (a second draw pass; off on the Low tier).
@export var still_water_reflection: bool = false
## Use hymn_glimmer.a (the colour-script energy the zone writes) as the mote energy instead of
## glimmer.json modes.<mode>.energy. intensity multiplies either.
@export var follow_scene_intensity: bool = true
@export var intensity: float = 1.0
## Treat hymn_glimmer_focus as an extra attractor.
@export var follow_global_focus: bool = true
## Energy of an OmniLight3D that follows the mote colour (0 = no light).
@export var fill_light_energy: float = 0.0
@export var fill_light_offset_m: Vector3 = Vector3.ZERO

@export_group("Determinism")
## Fixed seed + preprocess make captures and cutscenes repeatable.
@export var use_fixed_seed: bool = false
@export var fixed_seed: int = 0
## Seconds pre-simulated on start; negative = glimmer.json emitter.preprocess_s.
@export var preprocess_s: float = -1.0

var config: Dictionary = {}
var state: GlimmerState
var motes: GPUParticles3D
var process_material: ShaderMaterial
var draw_material: ShaderMaterial
var reflect_material: ShaderMaterial
var fill_light: OmniLight3D
var flow_time_s: float = 0.0

var _mirror_quad: QuadMesh
var _release_origin: Vector3 = Vector3.ZERO
var _release_origin_set: bool = false

var _attractors: Array[Dictionary] = []
var _quality_id: String = ""
var _colors: Dictionary = {}


func _init() -> void:
	config = load_config()
	_colors = _parse_colors(config.get("colors", {}) as Dictionary)
	state = GlimmerState.new()
	state.mode_changed.connect(func(m: GlimmerState.Mode) -> void: mode_changed.emit(m))
	state.release_started.connect(func(d: float) -> void: release_started.emit(d))
	state.release_finished.connect(func() -> void: release_finished.emit())


func _ready() -> void:
	_build()
	if not set_quality(quality if quality != "" else str(config.get("default_quality", ""))):
		push_warning("GlimmerField: unknown quality '%s', using default" % quality)
		set_quality(str(config.get("default_quality", "")))
	_push_dynamic()


func _process(delta: float) -> void:
	state.advance(delta)
	flow_time_s += delta
	_push_dynamic()


# --- Modes -------------------------------------------------------------------------------------


func set_mode(new_mode: GlimmerState.Mode) -> void:
	state.set_mode(new_mode)
	_push_dynamic()


func get_mode() -> GlimmerState.Mode:
	return state.mode


## Held (or bound) -> released. Returns false when already released. Default: release_duration_s.
## The change spreads outward from origin (a living node: the singer, the dancer); null = this field.
func release(duration_s: float = USE_DEFAULT, origin: Node3D = null) -> bool:
	var d := duration_s if duration_s >= 0.0 else float(config.get("release_duration_s", 0.0))
	if state.mode == GlimmerState.Mode.RELEASED:
		return false
	_release_origin_set = origin != null
	if origin != null:
		_release_origin = origin.global_position if origin.is_inside_tree() else origin.position
	var ok := state.release(d)
	_push_dynamic()
	return ok


func is_releasing() -> bool:
	return state.is_releasing()


func get_release_progress() -> float:
	return state.release_progress()


## The current mote colour (sRGB Color, linear blend of the palette colours).
func current_color() -> Color:
	return state.blend_color(_colors["held"], _colors["released"], _colors["machine"])


# --- Attractors --------------------------------------------------------------------------------


## Motes within radius_m * influence_scale gather onto an orbit shell of radius_m around node and
## swirl about the vertical axis (half_height_m > 0 makes the axis a segment: a standing figure).
## Re-adding a node updates it. Returns false for a null node or when the list is full.
func add_attractor(
	node: Node3D,
	strength: float = USE_DEFAULT,
	radius_m: float = USE_DEFAULT,
	swirl: float = USE_DEFAULT,
	half_height_m: float = USE_DEFAULT
) -> bool:
	if node == null:
		return false
	_prune_attractors()
	var a := config.get("attractor", {}) as Dictionary
	var entry := {
		"node": node,
		"strength": _or_default(strength, a, "default_strength"),
		"radius_m": _or_default(radius_m, a, "default_radius_m"),
		"swirl": _or_default(swirl, a, "default_swirl"),
		"half_height_m": _or_default(half_height_m, a, "default_half_height_m"),
	}
	var i := _attractor_index(node)
	if i >= 0:
		_attractors[i] = entry
		return true
	if _attractors.size() >= max_attractors():
		return false
	_attractors.append(entry)
	return true


func remove_attractor(node: Node3D) -> bool:
	var i := _attractor_index(node)
	if i < 0:
		return false
	_attractors.remove_at(i)
	return true


func clear_attractors() -> void:
	_attractors.clear()


func get_attractor_count() -> int:
	_prune_attractors()
	return _attractors.size()


func max_attractors() -> int:
	return int((config.get("attractor", {}) as Dictionary).get("max", 0))


## Packs live attractors into the shader layout: {"count", "pos_radius", "params"}, both arrays
## padded to max_attractors(). Freed nodes are dropped first.
func pack_attractors() -> Dictionary:
	_prune_attractors()
	var influence := float((config.get("attractor", {}) as Dictionary).get("influence_scale", 1.0))
	var pos_radius := PackedVector4Array()
	var params := PackedVector4Array()
	pos_radius.resize(max_attractors())
	params.resize(max_attractors())
	for i in _attractors.size():
		var e := _attractors[i]
		var n := e["node"] as Node3D
		var p := n.global_position if n.is_inside_tree() else n.position
		var r := float(e["radius_m"])
		pos_radius[i] = Vector4(p.x, p.y, p.z, r)
		params[i] = Vector4(float(e["strength"]), float(e["swirl"]), float(e["half_height_m"]), r * influence)
	return {"count": _attractors.size(), "pos_radius": pos_radius, "params": params}


# --- Global uniforms ---------------------------------------------------------------------------


## Every GlimmerField with follow_global_focus gathers around this point. radius_m <= 0 turns it off.
static func set_global_focus(position: Vector3, radius_m: float) -> void:
	RenderingServer.global_shader_parameter_set(GLOBAL_FOCUS, Vector4(position.x, position.y, position.z, radius_m))


static func clear_global_focus() -> void:
	RenderingServer.global_shader_parameter_set(GLOBAL_FOCUS, Vector4.ZERO)


## hymn_glimmer: rgb = linear tint (for other shaders; motes keep their meaning colours), a = scene
## glimmer intensity (the colour script's mote emission energy). a = 0 also turns sea-glow off.
static func set_scene_glimmer(tint: Color, scene_intensity: float) -> void:
	var lin := tint.srgb_to_linear()
	RenderingServer.global_shader_parameter_set(GLOBAL_GLIMMER, Vector4(lin.r, lin.g, lin.b, scene_intensity))


## Writes the zone's night sea-glow energy (hymn_zone_sea_glow), independent of the mote energy. 0 = off
## (ending_dock). Clamped to [0, rule-3 ceiling]; it does not enforce the night minimum, so scene
## exceptions (the Ending's E4 0.07, E5 0.06) pass. Check frames with sea_glow_violation().
static func set_scene_sea_glow(energy: float) -> void:
	var rule := load_config().get("sea_glow", {}) as Dictionary
	RenderingServer.global_shader_parameter_set(GLOBAL_SEA_GLOW, clampf(energy, 0.0, float(rule.get("ceiling", 1.0))))


## "" if a frame's sea-glow energy obeys colour script rule 3 (glimmer.json "sea_glow", mirrored
## from palette.json), else the reason. Day frames (sun above the horizon) may be 0; night frames
## need [floor, ceiling], and >= night_min once the sun is below night_min_below_sun_deg, unless
## (scene_id, beat) is a named exception (exact value) or the scene is an off scene (0).
static func sea_glow_violation(
	energy: float, sun_elevation_deg: float, scene_id: String = "", beat: String = ""
) -> String:
	var rule := load_config().get("sea_glow", {}) as Dictionary
	if (rule.get("off_scenes", []) as Array).has(scene_id):
		return "" if is_zero_approx(energy) else "%s has no sea-glow (0)" % scene_id
	var exceptions := rule.get("night_exceptions", {}) as Dictionary
	if exceptions.has(scene_id) and (exceptions[scene_id] as Dictionary).has(beat):
		var want := float((exceptions[scene_id] as Dictionary)[beat])
		return "" if is_equal_approx(energy, want) else "%s %s is %.2f by exception" % [scene_id, beat, want]
	if sun_elevation_deg >= 0.0:
		return "" if energy <= float(rule.get("ceiling", 1.0)) else "above the ceiling"
	if energy < float(rule.get("floor", 0.0)) or energy > float(rule.get("ceiling", 1.0)):
		return "night sea-glow outside [floor, ceiling]"
	if (
		sun_elevation_deg < float(rule.get("night_min_below_sun_deg", 0.0))
		and energy < float(rule.get("night_min", 0.0))
	):
		return (
			"below the night minimum once the sun is below %.0f deg" % float(rule.get("night_min_below_sun_deg", 0.0))
		)
	return ""


# --- Quality -----------------------------------------------------------------------------------


## Applies a quality tier from glimmer.json "quality" (ids match GraphicsSettings presets). Tiers
## scale count, trails, curl octaves and the reflection pass; no tier removes the motes.
## Changing the particle count restarts the emitter, so call it behind a fade (with the presets).
func set_quality(preset_id: String) -> bool:
	var tiers := config.get("quality", {}) as Dictionary
	if not tiers.has(preset_id):
		return false
	_quality_id = preset_id
	if motes != null:
		_apply_static()
	return true


func get_quality() -> String:
	return _quality_id


## Re-applies config, quality and the exported properties after changing any of them at runtime.
func refresh() -> void:
	if motes != null:
		_apply_static()
		_push_dynamic()


func apply_graphics_settings(settings: GraphicsSettings) -> bool:
	return set_quality(settings.preset_id)


## Particle count for the current tier (always >= 1).
func planned_amount() -> int:
	if fixed_count > 0:
		return fixed_count
	var emitter := config.get("emitter", {}) as Dictionary
	var scale := float(_tier().get("amount_scale", 1.0))
	return maxi(1, roundi(float(emitter.get("amount", 1)) * scale * amount_multiplier))


func reflection_active() -> bool:
	return still_water_reflection and bool(_tier().get("reflection", false))


# --- Shader parameters (pure; tested headlessly) -----------------------------------------------


## Every process-shader uniform that changes only with config, quality or exports.
func static_process_parameters() -> Dictionary:
	var m := config.get("modes", {}) as Dictionary
	var rates := (config.get("cues", {}) as Dictionary).get("rates", {}) as Dictionary
	var rate := rates.get(motion_rate, {}) as Dictionary
	var rel := (m.get("released", {}) as Dictionary).merged(rate, true)
	var held := (m.get("held", {}) as Dictionary).merged(rate, true)
	var mach := m.get("machine", {}) as Dictionary
	var mo := config.get("motion", {}) as Dictionary
	var a := config.get("attractor", {}) as Dictionary
	var lk := config.get("look", {}) as Dictionary
	var wave := config.get("release_wave", {}) as Dictionary
	return {
		"col_released": _colors["released"],
		"col_released_hi": _colors["released_hi"],
		"col_held": _colors["held"],
		"col_machine": _colors["machine"],
		"energy_released": float(rel.get("energy", 0.0)),
		"energy_held": float(held.get("energy", 0.0)),
		"energy_machine": float(mach.get("energy", 0.0)),
		"released_hi_shift": float(rel.get("hi_shift", 0.0)),
		"follow_scene_intensity": follow_scene_intensity,
		"intensity": intensity,
		"brightness_min": float(lk.get("brightness_min", 1.0)),
		"brightness_power": float(lk.get("brightness_power", 1.0)),
		"release_wave_radius_m": float(wave.get("radius_m", 1.0)),
		"release_wave_fraction": float(wave.get("fraction", 0.0)),
		"release_wave_jitter": float(wave.get("jitter", 0.0)),
		"emission_shape": int(emission_shape),
		"emission_extents_m": emission_extents_m,
		"emission_inner_radius_m": emission_inner_radius_m,
		"emission_height_bias": height_bias,
		"emission_center_bias": center_bias,
		"spawn_point_count": mini(spawn_points.size(), MAX_SPAWN_POINTS),
		"spawn_points": _padded_spawn_points(),
		"persistent": not respawn,
		"persist_fade_in_s": float((config.get("emitter", {}) as Dictionary).get("persist_fade_in_s", 1.0)),
		"size_min_m": float(lk.get("size_min_m", 0.0)),
		"size_max_m": float(lk.get("size_max_m", 0.0)),
		"size_power": float(lk.get("size_power", 1.0)),
		"sea_direction": sea_direction,
		"water_height_m": water_height_m,
		"rise_min_mps": float(rel.get("rise_min_mps", 0.0)),
		"rise_max_mps": float(rel.get("rise_max_mps", 0.0)),
		"spiral_radius_min_m": float(rel.get("spiral_radius_min_m", 0.0)),
		"spiral_radius_max_m": float(rel.get("spiral_radius_max_m", 0.0)),
		"spiral_rate_rad_s": float(rel.get("spiral_rate_rad_s", 0.0)),
		"released_curl_scale": float(rel.get("curl_scale", 0.0)),
		"drift_min_mps": float(held.get("drift_min_mps", 0.0)),
		"drift_max_mps": float(held.get("drift_max_mps", 0.0)),
		"down_bias_min_deg": float(held.get("down_bias_min_deg", 0.0)),
		"down_bias_max_deg": float(held.get("down_bias_max_deg", 0.0)),
		"heading_spread_deg": float(held.get("heading_spread_deg", 0.0)),
		"held_curl_scale": float(held.get("curl_scale", 0.0)),
		"curl_frequency": float(mo.get("curl_frequency", 0.0)),
		"curl_strength_mps": float(mo.get("curl_strength_mps", 0.0)),
		"curl_evolve": float(mo.get("curl_evolve", 0.0)),
		"curl_octaves": int(_tier().get("curl_octaves", 1)),
		"response_rate": float(mo.get("response_rate", 0.0)),
		"underwater_drag": float(mo.get("underwater_drag", 0.0)),
		"underwater_absorb_per_m": float(mo.get("underwater_absorb_per_m", 0.0)),
		"breath_rate_hz": float(lk.get("breath_rate_hz", 0.0)),
		"breath_depth": float(lk.get("breath_depth", 0.0)),
		"fade_in_fraction": float(lk.get("fade_in_fraction", 0.0)),
		"fade_out_fraction": float(lk.get("fade_out_fraction", 0.0)),
		"attractor_pull_mps": float(a.get("pull_mps", 0.0)),
		"attractor_swirl_mps": float(a.get("swirl_mps", 0.0)),
		"attractor_keep_drift": float(a.get("keep_drift", 0.0)),
		"attractor_influence_scale": float(a.get("influence_scale", 1.0)),
		"follow_global_focus": follow_global_focus,
		"focus_strength": float(a.get("focus_strength", 0.0)),
		"focus_half_height_m": float(a.get("focus_half_height_m", 0.0)),
	}


## Per-frame process-shader uniforms: state, clock and attractors.
func dynamic_process_parameters() -> Dictionary:
	var packed := pack_attractors()
	var out := state.shader_state()
	(
		out
		. merge(
			{
				"transition_progress": out["progress"],
				"release_origin": release_origin(),
				"flow_time_s": flow_time_s,
				"attractor_count": packed["count"],
				"attractor_pos_radius": packed["pos_radius"],
				"attractor_params": packed["params"],
				"field_to_world": field_to_world(),
				"world_to_field_basis": field_to_world().basis.inverse(),
			}
		)
	)
	out.erase("progress")
	return out


## Particle space -> world: this node's transform in local space, identity in world space.
func field_to_world() -> Transform3D:
	if not local_space:
		return Transform3D.IDENTITY
	return global_transform if is_inside_tree() else transform


## Field parameters for a .dlg @vfx cue (dialogue_format.md: effect, count, drift, motion, rate,
## form) through glimmer.json "cues": {mode, fixed_count, respawn, motion_rate, local_space}. Keys
## the cue does not set are absent. Unknown effects return {}.
static func cue_parameters(effect: String, kwargs: Dictionary, cfg: Dictionary = {}) -> Dictionary:
	var cues := (cfg if not cfg.is_empty() else load_config()).get("cues", {}) as Dictionary
	var effects := cues.get("effects", {}) as Dictionary
	if not effects.has(effect):
		return {}
	var out := {"mode": _mode_from_id(str(effects[effect]))}
	if kwargs.has("drift") and (cues.get("drift", {}) as Dictionary).has(str(kwargs["drift"])):
		out["mode"] = _mode_from_id(str((cues["drift"] as Dictionary)[str(kwargs["drift"])]))
	if kwargs.has("motion") and (cues.get("motion", {}) as Dictionary).has(str(kwargs["motion"])):
		out["mode"] = _mode_from_id(str((cues["motion"] as Dictionary)[str(kwargs["motion"])]))
	if kwargs.has("count"):
		out["fixed_count"] = maxi(1, int(kwargs["count"]))
		out["respawn"] = false
	if kwargs.has("rate") and (cues.get("rates", {}) as Dictionary).has(str(kwargs["rate"])):
		out["motion_rate"] = str(kwargs["rate"])
	if out["mode"] == GlimmerState.Mode.MACHINE:
		out["local_space"] = true
	return out


## Applies cue_parameters() to this field (rebuilds the emitter: call it when the beat starts).
func apply_cue(effect: String, kwargs: Dictionary) -> bool:
	var p := cue_parameters(effect, kwargs, config)
	if p.is_empty():
		return false
	fixed_count = int(p.get("fixed_count", fixed_count))
	respawn = bool(p.get("respawn", respawn))
	motion_rate = str(p.get("motion_rate", motion_rate))
	local_space = bool(p.get("local_space", local_space))
	set_mode(p["mode"] as GlimmerState.Mode)
	if motes != null:
		_apply_emitter()
		refresh()
	return true


## Where the current (or next) release wave starts: the origin given to release(), else this field.
func release_origin() -> Vector3:
	if _release_origin_set:
		return _release_origin
	return global_position if is_inside_tree() else position


## Draw-pass uniforms (direct pass; the reflection pass adds mirror_plane_y and its gain).
func draw_parameters() -> Dictionary:
	var lk := config.get("look", {}) as Dictionary
	return {
		"halo_chroma_gain": float(lk.get("halo_chroma_gain", 1.0)),
		"halo_scale": float(lk.get("halo_scale", 1.0)),
		"core_gain": float(lk.get("core_gain", 0.0)),
		"halo_gain": float(lk.get("halo_gain", 0.0)),
		"halo_falloff": float(lk.get("halo_falloff", 1.0)),
		"streak_gain": float(lk.get("streak_gain", 0.0)),
		"streak_width": float(lk.get("streak_width", 1.0)),
		"soft_depth_m": float(lk.get("soft_depth_m", 0.0)),
		"near_fade_start_m": float(lk.get("near_fade_start_m", 0.0)),
		"near_fade_end_m": float(lk.get("near_fade_end_m", 0.0)),
		"trail_time_s": float(lk.get("trail_time_s", 0.0)),
		"trail_max_ratio": float(lk.get("trail_max_ratio", 0.0)),
		"trail_scale": float(_tier().get("trail_scale", 0.0)),
	}


func reflect_parameters() -> Dictionary:
	var lk := config.get("look", {}) as Dictionary
	var p := draw_parameters()
	p["mirror_plane_y"] = water_height_m
	p["reflection_gain"] = float(lk.get("reflection_gain", 0.0))
	p["reflection_softness"] = float(lk.get("reflection_softness", 1.0))
	return p


# --- Config ------------------------------------------------------------------------------------


static func load_config(path: String = CONFIG_PATH) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("GlimmerField: cannot parse %s" % path)
		return {}
	return parsed as Dictionary


# --- Internals ---------------------------------------------------------------------------------


func _build() -> void:
	process_material = ShaderMaterial.new()
	process_material.shader = PROCESS_SHADER
	draw_material = ShaderMaterial.new()
	draw_material.shader = DRAW_SHADER
	reflect_material = ShaderMaterial.new()
	reflect_material.shader = REFLECT_SHADER
	motes = GPUParticles3D.new()
	motes.name = MOTES_NODE_NAME
	motes.process_material = process_material
	var quad := QuadMesh.new()
	quad.material = draw_material
	motes.draw_pass_1 = quad
	_mirror_quad = QuadMesh.new()
	_mirror_quad.material = reflect_material
	motes.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_apply_emitter()
	add_child(motes)
	if fill_light_energy > 0.0:
		var fl := config.get("fill_light", {}) as Dictionary
		fill_light = OmniLight3D.new()
		fill_light.name = LIGHT_NODE_NAME
		fill_light.position = fill_light_offset_m
		fill_light.omni_range = float(fl.get("range_m", 1.0))
		fill_light.omni_attenuation = float(fl.get("attenuation", 1.0))
		fill_light.shadow_enabled = false
		add_child(fill_light)


## Lifetime, respawn and space: changing them restarts the emitter.
func _apply_emitter() -> void:
	var emitter := config.get("emitter", {}) as Dictionary
	motes.lifetime = float(emitter.get("lifetime_s" if respawn else "persist_lifetime_s", 1.0))
	motes.one_shot = not respawn
	motes.explosiveness = 0.0 if respawn else 1.0
	motes.fixed_fps = int(emitter.get("fixed_fps", 0))
	motes.preprocess = preprocess_s if preprocess_s >= 0.0 else float(emitter.get("preprocess_s", 0.0))
	motes.use_fixed_seed = use_fixed_seed
	motes.seed = fixed_seed
	motes.local_coords = local_space


func _padded_spawn_points() -> PackedVector3Array:
	var out := PackedVector3Array()
	out.resize(MAX_SPAWN_POINTS)
	for i in mini(spawn_points.size(), MAX_SPAWN_POINTS):
		out[i] = spawn_points[i]
	return out


static func _mode_from_id(id: String) -> GlimmerState.Mode:
	match id:
		"released":
			return GlimmerState.Mode.RELEASED
		"machine":
			return GlimmerState.Mode.MACHINE
	return GlimmerState.Mode.HELD


func _apply_static() -> void:
	var amount := planned_amount()
	if motes.amount != amount:
		motes.amount = amount
	if reflection_active():
		motes.draw_passes = 2
		motes.draw_pass_2 = _mirror_quad
	else:
		motes.draw_passes = 1
	var margin := float((config.get("emitter", {}) as Dictionary).get("aabb_margin_m", 0.0))
	var half := emission_extents_m.abs() + Vector3.ONE * margin
	if emission_shape == EmissionShape.DISC:
		half = Vector3(emission_extents_m.x, emission_extents_m.y, emission_extents_m.x).abs() + Vector3.ONE * margin
	motes.visibility_aabb = AABB(-half, half * 2.0)
	_set_all(process_material, static_process_parameters())
	_set_all(draw_material, draw_parameters())
	_set_all(reflect_material, reflect_parameters())


func _push_dynamic() -> void:
	if process_material != null:
		_set_all(process_material, dynamic_process_parameters())
	if fill_light != null:
		fill_light.light_color = current_color()
		fill_light.light_energy = fill_light_energy * intensity


func _set_all(material: ShaderMaterial, params: Dictionary) -> void:
	for key: String in params:
		material.set_shader_parameter(key, params[key])


func _tier() -> Dictionary:
	return (config.get("quality", {}) as Dictionary).get(_quality_id, {}) as Dictionary


func _prune_attractors() -> void:
	for i in range(_attractors.size() - 1, -1, -1):
		if not is_instance_valid(_attractors[i]["node"]):
			_attractors.remove_at(i)


func _attractor_index(node: Node3D) -> int:
	for i in _attractors.size():
		if is_instance_valid(_attractors[i]["node"]) and _attractors[i]["node"] == node:
			return i
	return -1


static func _or_default(value: float, section: Dictionary, key: String) -> float:
	return value if value >= 0.0 else float(section.get(key, 0.0))


static func _parse_colors(raw: Dictionary) -> Dictionary:
	var out := {}
	for key: String in ["released", "released_hi", "held", "machine"]:
		out[key] = Color.from_string(str(raw.get(key, "")), Color.MAGENTA)
	return out
