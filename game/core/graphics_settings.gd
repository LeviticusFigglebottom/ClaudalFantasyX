class_name GraphicsSettings
extends RefCounted
## Graphics quality presets (SPEC §4.2, task M1-RND-05).
##
## Data: game/data/settings/graphics_presets.json defines every setting, its allowed options, the
## Low/Medium/High/Ultra presets and the engine constants each option maps to. This class layers
## per-player overrides on top of the chosen preset, persists both to user://settings.cfg, and turns
## a settings dictionary into engine calls in two steps:
##   plan()    -> pure: settings in, Array of operation dictionaries out (unit-tested headlessly)
##   execute() -> performs those operations on a Viewport, an Environment and the RenderingServer
## Operation shape: {"target": viewport|environment|rendering_server|group, "op": set|gate|call, ...}.
## A "gate" never turns on a feature the zone did not author: the final value is
## authored_value AND allowed, with the authored value captured once in object metadata
## (see set_authored()). Environment feature toggles and VoxelGI node visibility are gates.

const DATA_PATH := "res://game/data/settings/graphics_presets.json"
const CONFIG_PATH := "user://settings.cfg"
const CONFIG_SECTION := "graphics"
const KEY_VERSION := "version"
const KEY_PRESET := "preset"
const KEY_OVERRIDES := "overrides"

const TARGET_VIEWPORT := &"viewport"
const TARGET_ENVIRONMENT := &"environment"
const TARGET_SERVER := &"rendering_server"
const TARGET_GROUP := &"group"
const OP_SET := &"set"
const OP_GATE := &"gate"
const OP_CALL := &"call"
const AUTHORED_META_PREFIX := "hymn_authored_"

const GI_OFF := "off"
const GI_SDFGI := "sdfgi"
const QUALITY_OFF := "off"
const TYPE_INT_NAME := "int"
const TYPE_FLOAT_NAME := "float"
const TYPE_BOOL_NAME := "bool"
const TYPE_ENUM_NAME := "enum"

var data: Dictionary = {}
var preset_id: String = ""
var overrides: Dictionary = {}


func _init(data_path: String = DATA_PATH) -> void:
	var text := FileAccess.get_file_as_string(data_path)
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("GraphicsSettings: cannot parse %s" % data_path)
		return
	data = parsed as Dictionary
	preset_id = str(data.get("default_preset", ""))


# --- Presets and the override layer ------------------------------------------------------------


func preset_ids() -> PackedStringArray:
	var out := PackedStringArray()
	for p: Variant in data.get("presets", []):
		out.append(str((p as Dictionary).get("id", "")))
	return out


## Full, type-normalized settings of a preset ({} if the id is unknown).
func preset_settings(id: String) -> Dictionary:
	for p: Variant in data.get("presets", []):
		var preset := p as Dictionary
		if str(preset.get("id", "")) != id:
			continue
		var out := {}
		var raw := preset.get("settings", {}) as Dictionary
		for key: String in raw:
			out[key] = _coerce(key, raw[key])
		return out
	return {}


## Allowed values for one setting, in display order.
func setting_options(key: String) -> Array:
	var spec := (data.get("settings", {}) as Dictionary).get(key, {}) as Dictionary
	var out: Array = []
	for v: Variant in spec.get("options", []):
		out.append(_coerce(key, v))
	return out


func is_valid_value(key: String, value: Variant) -> bool:
	var spec := (data.get("settings", {}) as Dictionary).get(key, {}) as Dictionary
	if spec.is_empty() or not _type_ok(str(spec.get("type", "")), value):
		return false
	var coerced: Variant = _coerce(key, value)
	for option: Variant in spec.get("options", []):
		if _same(_coerce(key, option), coerced):
			return true
	return false


## Selects a preset. Overrides are cleared unless keep_overrides is set.
func set_preset(id: String, keep_overrides: bool = false) -> bool:
	if not preset_ids().has(id):
		push_warning("GraphicsSettings: unknown preset '%s'" % id)
		return false
	preset_id = id
	if not keep_overrides:
		overrides.clear()
	else:
		_prune_overrides()
	return true


## Overrides one setting on top of the preset. An override equal to the preset value is dropped.
func set_override(key: String, value: Variant) -> bool:
	if not is_valid_value(key, value):
		push_warning("GraphicsSettings: invalid value <%s> for '%s'" % [str(value), key])
		return false
	overrides[key] = _coerce(key, value)
	_prune_overrides()
	return true


func clear_override(key: String) -> void:
	overrides.erase(key)


func clear_overrides() -> void:
	overrides.clear()


## True when the player has changed anything away from the selected preset ("Custom" in the UI).
func is_custom() -> bool:
	return not overrides.is_empty()


## Resolves to a complete, validated settings dictionary.
##   null                  -> the current preset plus the current overrides
##   "low" / &"high"       -> that preset, no overrides
##   {"preset": "low", ..} -> that preset (or the current one) with the given keys layered on top
## Invalid keys or values are ignored with a warning; missing keys come from the base preset.
func resolve(preset_or_dict: Variant = null) -> Dictionary:
	var base_id := preset_id
	var layer: Dictionary = overrides
	if preset_or_dict is String or preset_or_dict is StringName:
		base_id = str(preset_or_dict)
		layer = {}
	elif preset_or_dict is Dictionary:
		var d := preset_or_dict as Dictionary
		base_id = str(d.get(KEY_PRESET, preset_id))
		layer = d
	var out := preset_settings(base_id)
	if out.is_empty():
		push_warning("GraphicsSettings: unknown preset '%s', using default" % base_id)
		out = preset_settings(str(data.get("default_preset", "")))
	for key: Variant in layer:
		var k := str(key)
		if k == KEY_PRESET:
			continue
		if is_valid_value(k, layer[key]):
			out[k] = _coerce(k, layer[key])
		else:
			push_warning("GraphicsSettings: ignoring invalid '%s' = <%s>" % [k, str(layer[key])])
	return out


# --- Mapping to the engine ---------------------------------------------------------------------


## Pure mapping: settings (see resolve()) -> ordered list of engine operations. No side effects.
func plan(preset_or_dict: Variant = null) -> Array[Dictionary]:
	var s := resolve(preset_or_dict)
	var ops: Array[Dictionary] = []
	_plan_gi(s, ops)
	_plan_shadows(s, ops)
	_plan_fog(s, ops)
	_plan_ssr(s, ops)
	_plan_ambient(s, "ssao_quality", "ssao_enabled", "environment_set_ssao_quality", ops)
	_plan_ambient(s, "ssil_quality", "ssil_enabled", "environment_set_ssil_quality", ops)
	_plan_scaling_and_aa(s, ops)
	ops.append(_op_set(TARGET_VIEWPORT, "mesh_lod_threshold", s["lod_threshold"]))
	ops.append(_op_set(TARGET_VIEWPORT, "anisotropic_filtering_level", _enum_value("anisotropic_filtering", s)))
	return ops


## Plans and executes. viewport and environment may be null (their operations are skipped);
## RenderingServer operations always run. Returns the operations that were planned.
func apply(preset_or_dict: Variant, viewport: Viewport, environment: Environment) -> Array[Dictionary]:
	var ops := plan(preset_or_dict)
	execute(ops, viewport, environment)
	return ops


## Applies the current preset plus overrides.
func apply_current(viewport: Viewport, environment: Environment) -> Array[Dictionary]:
	return apply(null, viewport, environment)


## Performs planned operations. Returns how many were actually applied.
static func execute(ops: Array[Dictionary], viewport: Viewport, environment: Environment) -> int:
	var applied := 0
	for op in ops:
		var target: StringName = op["target"]
		var name := str(op.get("name", ""))
		match target:
			TARGET_VIEWPORT:
				if viewport != null:
					viewport.set(name, op["value"])
					applied += 1
			TARGET_ENVIRONMENT:
				if environment != null:
					_apply_property(environment, op)
					applied += 1
			TARGET_SERVER:
				RenderingServer.callv(name, op["args"] as Array)
				applied += 1
			TARGET_GROUP:
				if viewport != null and viewport.is_inside_tree():
					for node in viewport.get_tree().get_nodes_in_group(StringName(str(op["group"]))):
						_apply_property(node, op)
					applied += 1
	return applied


## Records what a zone/cutscene wants for a gated property (e.g. a cutscene turning fog on), then
## sets it; the player's setting still wins on the next apply.
static func set_authored(obj: Object, property: String, value: Variant) -> void:
	obj.set_meta(StringName(AUTHORED_META_PREFIX + property), value)
	obj.set(property, value)


# --- Persistence (user://settings.cfg, section [graphics]) -------------------------------------


## Saves preset and overrides. Other sections of the file (audio, controls...) are preserved.
func save_config(path: String = CONFIG_PATH) -> Error:
	var cfg := ConfigFile.new()
	if FileAccess.file_exists(path):
		cfg.load(path)
	cfg.set_value(CONFIG_SECTION, KEY_VERSION, int(data.get(KEY_VERSION, 0)))
	cfg.set_value(CONFIG_SECTION, KEY_PRESET, preset_id)
	cfg.set_value(CONFIG_SECTION, KEY_OVERRIDES, overrides.duplicate())
	return cfg.save(path)


## Loads preset and overrides; unknown presets fall back to the default, invalid overrides are dropped.
func load_config(path: String = CONFIG_PATH) -> Error:
	var cfg := ConfigFile.new()
	var err := cfg.load(path)
	if err != OK:
		return err
	var id := str(cfg.get_value(CONFIG_SECTION, KEY_PRESET, data.get("default_preset", "")))
	if not set_preset(id):
		set_preset(str(data.get("default_preset", "")))
	var raw: Variant = cfg.get_value(CONFIG_SECTION, KEY_OVERRIDES, {})
	if raw is Dictionary:
		for key: Variant in raw:
			set_override(str(key), (raw as Dictionary)[key])
	return OK


# --- Planning helpers --------------------------------------------------------------------------


func _plan_gi(s: Dictionary, ops: Array[Dictionary]) -> void:
	var mode := str(s["gi_mode"])
	var lvl := _level("sdfgi_quality", s)
	ops.append(_op_gate(TARGET_ENVIRONMENT, "sdfgi_enabled", mode == GI_SDFGI))
	ops.append(_op_set(TARGET_ENVIRONMENT, "sdfgi_cascades", int(lvl["cascades"])))
	ops.append(_op_set(TARGET_ENVIRONMENT, "sdfgi_use_occlusion", bool(lvl["use_occlusion"])))
	ops.append(_op_call("environment_set_sdfgi_ray_count", [_constant(str(lvl["ray_count"]))]))
	ops.append(_op_call("environment_set_sdfgi_frames_to_converge", [_constant(str(lvl["frames_to_converge"]))]))
	ops.append(
		_op_call("environment_set_sdfgi_frames_to_update_light", [_constant(str(lvl["frames_to_update_light"]))])
	)
	var voxel_gate := _op_gate(TARGET_GROUP, "visible", mode != GI_OFF)
	voxel_gate["group"] = str(data.get("voxel_gi_group", ""))
	ops.append(voxel_gate)
	ops.append(_op_call("voxel_gi_set_quality", [_enum_value("voxel_gi_quality", s)]))
	ops.append(_op_call("gi_set_use_half_resolution", [bool(s["gi_half_resolution"])]))


func _plan_shadows(s: Dictionary, ops: Array[Dictionary]) -> void:
	var soft := _enum_value("soft_shadow_quality", s)
	ops.append(_op_set(TARGET_VIEWPORT, "positional_shadow_atlas_size", int(s["shadow_atlas_size"])))
	ops.append(_op_set(TARGET_VIEWPORT, "positional_shadow_atlas_16_bits", bool(s["shadow_16_bits"])))
	ops.append(
		_op_call("directional_shadow_atlas_set_size", [int(s["directional_shadow_size"]), bool(s["shadow_16_bits"])])
	)
	ops.append(_op_call("directional_soft_shadow_filter_set_quality", [soft]))
	ops.append(_op_call("positional_soft_shadow_filter_set_quality", [soft]))


func _plan_fog(s: Dictionary, ops: Array[Dictionary]) -> void:
	ops.append(_op_gate(TARGET_ENVIRONMENT, "volumetric_fog_enabled", bool(s["volumetric_fog"])))
	var size := int(s["volumetric_fog_volume_size"])
	var depth := int(s["volumetric_fog_volume_depth"])
	ops.append(_op_call("environment_set_volumetric_fog_volume_size", [size, depth]))
	ops.append(_op_call("environment_set_volumetric_fog_filter_active", [bool(s["volumetric_fog_filter"])]))


func _plan_ssr(s: Dictionary, ops: Array[Dictionary]) -> void:
	ops.append(_op_gate(TARGET_ENVIRONMENT, "ssr_enabled", bool(s["ssr"])))
	ops.append(_op_set(TARGET_ENVIRONMENT, "ssr_max_steps", int(s["ssr_max_steps"])))
	ops.append(_op_call("environment_set_ssr_roughness_quality", [_enum_value("ssr_roughness_quality", s)]))


func _plan_ambient(s: Dictionary, key: String, env_prop: String, method: String, ops: Array[Dictionary]) -> void:
	var quality := str(s[key])
	ops.append(_op_gate(TARGET_ENVIRONMENT, env_prop, quality != QUALITY_OFF))
	if quality == QUALITY_OFF:
		return
	var lvl := _level(key, s)
	var args: Array = [
		_constant(str(lvl["quality"])),
		bool(lvl["half_size"]),
		float(lvl["adaptive_target"]),
		int(lvl["blur_passes"]),
		float(lvl["fadeout_from"]),
		float(lvl["fadeout_to"]),
	]
	ops.append(_op_call(method, args))


func _plan_scaling_and_aa(s: Dictionary, ops: Array[Dictionary]) -> void:
	var rules := data.get("rules", {}) as Dictionary
	var temporal_upscaler := (rules.get("temporal_upscaler_modes", []) as Array).has(str(s["scaling_mode"]))
	var aa := _level("aa", s)
	ops.append(_op_set(TARGET_VIEWPORT, "scaling_3d_mode", _enum_value("scaling_mode", s)))
	ops.append(_op_set(TARGET_VIEWPORT, "scaling_3d_scale", float(s["render_scale"])))
	ops.append(_op_set(TARGET_VIEWPORT, "fsr_sharpness", float(s["fsr_sharpness"])))
	ops.append(_op_set(TARGET_VIEWPORT, "use_taa", bool(aa["use_taa"]) and not temporal_upscaler))
	ops.append(_op_set(TARGET_VIEWPORT, "screen_space_aa", _constant(str(aa["screen_space_aa"]))))
	ops.append(_op_set(TARGET_VIEWPORT, "msaa_3d", _constant(str(aa["msaa_3d"]))))


func _level(key: String, s: Dictionary) -> Dictionary:
	var table := (data.get("levels", {}) as Dictionary).get(key, {}) as Dictionary
	return table.get(str(s[key]), {}) as Dictionary


func _enum_value(key: String, s: Dictionary) -> int:
	var table := (data.get("enums", {}) as Dictionary).get(key, {}) as Dictionary
	return _constant(str(table.get(str(s[key]), "")))


# --- Small pure helpers ------------------------------------------------------------------------


func _prune_overrides() -> void:
	var base := preset_settings(preset_id)
	for key: Variant in overrides.keys():
		if base.has(key) and _same(base[key], overrides[key]):
			overrides.erase(key)


func _coerce(key: String, value: Variant) -> Variant:
	var spec := (data.get("settings", {}) as Dictionary).get(key, {}) as Dictionary
	match str(spec.get("type", "")):
		TYPE_INT_NAME:
			return int(value) if _is_number(value) else value
		TYPE_FLOAT_NAME:
			return float(value) if _is_number(value) else value
		TYPE_ENUM_NAME:
			return str(value) if (value is String or value is StringName) else value
	return value


static func _type_ok(type_name: String, value: Variant) -> bool:
	match type_name:
		TYPE_INT_NAME, TYPE_FLOAT_NAME:
			return _is_number(value)
		TYPE_BOOL_NAME:
			return value is bool
		TYPE_ENUM_NAME:
			return value is String or value is StringName
	return false


static func _is_number(value: Variant) -> bool:
	return typeof(value) == TYPE_INT or typeof(value) == TYPE_FLOAT


static func _same(a: Variant, b: Variant) -> bool:
	if _is_number(a) and _is_number(b):
		return is_equal_approx(float(a), float(b))
	return typeof(a) == typeof(b) and a == b


## Resolves "Class.CONSTANT" (e.g. "Viewport.MSAA_4X") through ClassDB.
static func _constant(qualified: String) -> int:
	var cls := qualified.get_slice(".", 0)
	var constant := qualified.get_slice(".", 1)
	if not ClassDB.class_has_integer_constant(cls, constant):
		push_error("GraphicsSettings: unknown engine constant '%s'" % qualified)
	return ClassDB.class_get_integer_constant(cls, constant)


static func _op_set(target: StringName, name: String, value: Variant) -> Dictionary:
	return {"target": target, "op": OP_SET, "name": name, "value": value}


static func _op_gate(target: StringName, name: String, allowed: bool) -> Dictionary:
	return {"target": target, "op": OP_GATE, "name": name, "value": allowed}


static func _op_call(method: String, args: Array) -> Dictionary:
	return {"target": TARGET_SERVER, "op": OP_CALL, "name": method, "args": args}


static func _apply_property(obj: Object, op: Dictionary) -> void:
	var name := str(op["name"])
	if op["op"] != OP_GATE:
		obj.set(name, op["value"])
		return
	var meta := StringName(AUTHORED_META_PREFIX + name)
	if not obj.has_meta(meta):
		obj.set_meta(meta, obj.get(name))
	obj.set(name, bool(obj.get_meta(meta)) and bool(op["value"]))
