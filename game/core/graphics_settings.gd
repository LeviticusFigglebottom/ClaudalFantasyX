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
## Operation shape: {"target": viewport|environment|rendering_server|group|sky, "op": set|gate|call, ...}.
## A sky op sets a uniform on the Environment's sky material, if its shader declares it (M1-RND-12).
## A "gate" never turns on a feature the zone did not author: the final value is
## authored_value AND allowed, with the authored value captured once in object metadata
## (see set_authored()). Environment feature toggles and VoxelGI node visibility are gates.

const DATA_PATH := "res://game/data/settings/graphics_presets.json"
const CONFIG_PATH := "user://settings.cfg"
const CONFIG_SECTION := "graphics"
const KEY_VERSION := "version"
const KEY_PRESET := "preset"
const KEY_OVERRIDES := "overrides"
const KEY_TIERS := "tiers"
const KEY_FAMILIES := "shader_families"
const FAMILY_FALLBACK_TIER := "high"

const TARGET_VIEWPORT := &"viewport"
const TARGET_ENVIRONMENT := &"environment"
const TARGET_SERVER := &"rendering_server"
const TARGET_GROUP := &"group"
const TARGET_SKY := &"sky"
const OP_SET := &"set"
const OP_GATE := &"gate"
const OP_CALL := &"call"
## Group ops of vegetation_detail (M1-RND-07): scale an authored float, set a MultiMesh visible
## fraction, gate cast_shadow off.
const OP_SCALE := &"scale"
const OP_FRACTION := &"fraction"
const OP_SHADOW_GATE := &"shadow_gate"
const KEY_VEG_GROUPS := "vegetation_groups"
const AUTHORED_META_PREFIX := "hymn_authored_"
## vegetation_groups keys (the group names are data): GraphicsSettings.vegetation_group(VEG_GROUP_LOD).
const VEG_GROUP_LOD := "lod"
const VEG_GROUP_MULTIMESH := "multimesh"
const VEG_GROUP_SMALL_SHADOWS := "small_shadows"
## M1-RND-16 scoped overrides: rules.override_keys lists the settings an override may name.
const KEY_OVERRIDE_KEYS := "override_keys"
## Told on_viewport_state_changed() right after an override is applied or restored, so per-frame
## gates (UndertowStorm's temporal jitter) follow it in the same frame.
const VIEWPORT_STATE_GROUP := &"hymn_viewport_state_listeners"
const VIEWPORT_STATE_METHOD := &"on_viewport_state_changed"
## The viewport properties an override writes, snapshots and restores.
const OVERRIDE_VIEWPORT_PROPS: Array[String] = [
	"scaling_3d_mode", "scaling_3d_scale", "fsr_sharpness", "use_taa", "screen_space_aa", "msaa_3d"
]

const GI_OFF := "off"
const GI_SDFGI := "sdfgi"
const QUALITY_OFF := "off"
const TYPE_INT_NAME := "int"
const TYPE_FLOAT_NAME := "float"
const TYPE_BOOL_NAME := "bool"
const TYPE_ENUM_NAME := "enum"

## Parsed presets data shared by the static helpers (preset_tier).
static var _data_cache: Dictionary = {}
## Scoped override stack (M1-RND-16): {handle, owner (WeakRef), values, on_exit}, oldest first.
static var _override_stack: Array[Dictionary] = []
## The overridden viewport's state before the first override (restored by the last pop).
static var _override_base: Dictionary = {}
static var _override_viewport: Object = null
## The base settings the whole stack layers on: a copy of the first push's (M2-NIT-03), kept until the
## last pop, so a caller that changes its own `base` later cannot move the stack under it.
static var _override_settings: GraphicsSettings = null
## user://settings.cfg as last read for an override with no base, and its modified time (M1-NIT-02).
## Private and read-only: it never leaves this class except as a copy (push_override stores one).
## mtime has 1 s granularity, so a write that bypasses save_config within the same second is missed
## until the next change; save_config itself invalidates it.
static var _player_settings: GraphicsSettings = null
static var _player_settings_mtime := -1
static var _next_override_handle := 1

var data: Dictionary = {}
var preset_id: String = ""
var overrides: Dictionary = {}


## `data_path` "" builds an empty instance for copy() (no table is read).
func _init(data_path: String = DATA_PATH) -> void:
	if data_path == "":
		return
	var text := FileAccess.get_file_as_string(data_path)
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("GraphicsSettings: cannot parse %s" % data_path)
		return
	data = parsed as Dictionary
	preset_id = str(data.get("default_preset", ""))


## An independent copy: the same presets table (never mutated), its own preset and override layer.
func copy() -> GraphicsSettings:
	var out := GraphicsSettings.new("")
	out.data = data
	out.preset_id = preset_id
	out.overrides = overrides.duplicate(true)
	return out


## True when `other` selects the same preset and override layer (copy() of this is the same).
func same_as(other: GraphicsSettings) -> bool:
	return other != null and other.preset_id == preset_id and other.overrides == overrides


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
	_plan_vegetation(s, ops)
	_plan_sky(s, ops)
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
			TARGET_SKY:
				if _apply_sky_uniform(environment, name, op["value"]):
					applied += 1
	return applied


## Sets a sky_detail uniform on the environment's sky material when its shader declares it; int
## uniforms get an int (JSON numbers parse as floats). False when there is nothing to set.
static func _apply_sky_uniform(environment: Environment, name: String, value: Variant) -> bool:
	if environment == null or environment.sky == null or not (environment.sky.sky_material is ShaderMaterial):
		return false
	var mat := environment.sky.sky_material as ShaderMaterial
	if mat.shader == null:
		return false
	for u: Dictionary in mat.shader.get_shader_uniform_list():
		if str(u["name"]) == name:
			mat.set_shader_parameter(name, int(value) if int(u["type"]) == TYPE_INT else value)
			return true
	return false


## Quality tier of `system` ("water", "vegetation", ...) for a preset (presets[].tiers; "" if the
## preset or system is unknown). Static and cached: systems ask it without a GraphicsSettings.
static func preset_tier(preset: String, system: String) -> String:
	for p: Dictionary in _shared_data().get("presets", []):
		if str(p.get("id", "")) == preset:
			return str((p.get(KEY_TIERS, {}) as Dictionary).get(system, ""))
	return ""


## Tree group a zone tags for a vegetation_detail role (VEG_GROUP_LOD / _MULTIMESH / _SMALL_SHADOWS;
## graphics_presets.json vegetation_groups). &"" if the role is unknown.
static func vegetation_group(role: String) -> StringName:
	return StringName(str((_shared_data().get(KEY_VEG_GROUPS, {}) as Dictionary).get(role, "")))


## Swaps every ShaderMaterial under `root` whose shader belongs to a shader family
## (graphics_presets.json "shader_families") to the variant of the current preset's tier. Each
## material is visited once; shared materials change for every user, which is the intent. Call it
## after a zone loads and after a preset change, like apply(). Returns the number of swaps.
func apply_tiers(root: Node, preset: String = "") -> int:
	var pid := preset if preset != "" else preset_id
	var families := data.get(KEY_FAMILIES, {}) as Dictionary
	var member_of := {}
	for fam: String in families:
		if fam.begins_with("_"):
			continue
		for tier: String in families[fam]:
			if tier != "system":
				member_of[str(families[fam][tier])] = fam
	var seen := {}
	var swaps := 0
	for mat in _materials_under(root):
		if seen.has(mat) or not (mat is ShaderMaterial) or (mat as ShaderMaterial).shader == null:
			continue
		seen[mat] = true
		var sm := mat as ShaderMaterial
		var fam := str(member_of.get(sm.shader.resource_path, ""))
		if fam == "":
			continue
		var f := families[fam] as Dictionary
		var tier := preset_tier(pid, str(f.get("system", "")))
		var want := str(f.get(tier, f.get(FAMILY_FALLBACK_TIER, "")))
		if want != "" and want != sm.shader.resource_path:
			sm.shader = load(want) as Shader
			swaps += 1
	return swaps


static func _materials_under(root: Node) -> Array[Material]:
	var out: Array[Material] = []
	for n in root.find_children("*", "GeometryInstance3D", true, false) + [root]:
		if not (n is GeometryInstance3D):
			continue
		var g := n as GeometryInstance3D
		if g.material_override != null:
			out.append(g.material_override)
		var mesh: Mesh = null
		if g is MeshInstance3D:
			mesh = (g as MeshInstance3D).mesh
			for i in (g as MeshInstance3D).get_surface_override_material_count():
				var m := (g as MeshInstance3D).get_surface_override_material(i)
				if m != null:
					out.append(m)
		elif g is MultiMeshInstance3D and (g as MultiMeshInstance3D).multimesh != null:
			mesh = (g as MultiMeshInstance3D).multimesh.mesh
		if mesh != null:
			for i in mesh.get_surface_count():
				var m := mesh.surface_get_material(i)
				if m != null:
					out.append(m)
	return out


static func _shared_data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		_data_cache = parsed as Dictionary if parsed is Dictionary else {}
	return _data_cache


## Records what a zone/cutscene wants for a gated property (e.g. a cutscene turning fog on), then
## sets it; the player's setting still wins on the next apply.
static func set_authored(obj: Object, property: String, value: Variant) -> void:
	obj.set_meta(StringName(AUTHORED_META_PREFIX + property), value)
	obj.set(property, value)


# --- Scoped overrides (M1-RND-16) --------------------------------------------------------------
# A cutscene (or any scene-owned moment) can switch the game viewport's AA and 3D scaling for its
# duration without touching the player's settings: push_override() at a cut, pop_override() (or
# the owner leaving the tree) restores the state below. Storm close-ups on High use it to swap FSR2,
# which cannot integrate the Undertow body's dither, for FSR1 + native TAA (docs/kb/tech/undertow.md).


## Applies `values` (settings keys from graphics_presets.json rules.override_keys, e.g.
## {"aa": "taa", "scaling_mode": "fsr"}) on top of the player's settings to `viewport` (default: the
## owner's viewport), until pop_override(handle) or until `owner` leaves the tree. Overrides stack:
## the last pushed wins key by key, and popping any of them re-applies the rest. When the last one
## goes, the viewport gets back exactly the values it had before the first. `base` is the player's
## settings the overrides layer on (default: user://settings.cfg, or the default preset); it is never
## saved. The first push's base holds for the whole stack: a later push with another base is applied
## on the first one's, with a warning, so it never re-bases an earlier owner's layer (M1-NIT-02).
## The exception is a scene swap (M2-NIT-03): when every older owner has already left the tree (its
## deferred pop is still pending), nobody's layer is left to protect, so the push re-bases the stack on
## its own base, or on the player's settings when it gives none. The stack keeps a copy of the base.
## The owner leaving the tree pops its entry at the end of that frame, unless it is back in a tree
## by then: a reparent (remove_child then add_child, or Node.reparent) keeps the override. Call it at
## a cut: the pipeline switches on the next frame drawn. Returns the handle, or 0 when nothing was
## applied (invalid key or value, no viewport, or a second viewport).
static func push_override(
	owner: Node, values: Dictionary, viewport: Viewport = null, base: GraphicsSettings = null
) -> int:
	if owner == null:
		push_warning("GraphicsSettings: push_override needs an owner")
		return 0
	var vp := viewport if viewport != null else (owner.get_viewport() if owner.is_inside_tree() else null)
	if vp == null:
		push_warning("GraphicsSettings: push_override(%s) has no viewport" % owner.name)
		return 0
	var fresh := _override_stack.is_empty() or _older_owners_left()
	var settings: GraphicsSettings = null
	if base != null and fresh:
		settings = base
	else:
		settings = _player_config() if fresh else _override_settings_or_player()
	if base != null and base != settings and not base.same_as(settings):
		push_warning("GraphicsSettings: push_override(%s): keeping the first override's base settings" % owner.name)
	var invalid := settings.invalid_override(values)
	if invalid != "":
		push_warning("GraphicsSettings: push_override(%s): %s" % [owner.name, invalid])
		return 0
	if _override_stack.is_empty():
		_override_viewport = vp
		_override_base = _viewport_state(vp)
	elif not is_instance_valid(_override_viewport) or _override_viewport != vp:
		push_error("GraphicsSettings: push_override(%s): overrides already target another viewport" % owner.name)
		return 0
	if fresh:
		_override_settings = settings.copy()
	var handle := _next_override_handle
	_next_override_handle += 1
	var on_exit := func() -> void: GraphicsSettings._owner_left.call_deferred(handle)
	owner.tree_exiting.connect(on_exit)
	_override_stack.append(
		{"handle": handle, "owner": weakref(owner), "values": values.duplicate(), "on_exit": on_exit}
	)
	_apply_override_state(override_state())
	return handle


## Removes one override (any position in the stack). False when the handle is not active.
static func pop_override(handle: int) -> bool:
	for i in _override_stack.size():
		var entry := _override_stack[i]
		if int(entry["handle"]) != handle:
			continue
		_override_stack.remove_at(i)
		var owner := (entry["owner"] as WeakRef).get_ref() as Node
		var on_exit: Callable = entry["on_exit"]
		if owner != null and owner.tree_exiting.is_connected(on_exit):
			owner.tree_exiting.disconnect(on_exit)
		if _override_stack.is_empty():
			_apply_override_state(_override_base)
			_override_base = {}
			_override_viewport = null
			_override_settings = null
		else:
			_apply_override_state(override_state())
		return true
	return false


## The deferred end of an owner's tree_exiting: pops `handle` unless its owner is alive and in a tree
## again (a reparent). A no-op for a handle that is no longer active.
static func _owner_left(handle: int) -> void:
	for entry in _override_stack:
		if int(entry["handle"]) != handle:
			continue
		var owner := (entry["owner"] as WeakRef).get_ref() as Node
		if owner == null or not owner.is_inside_tree():
			pop_override(handle)
		return


## Number of active overrides.
static func active_overrides() -> int:
	return _override_stack.size()


## The viewport state (property -> value: scaling_3d_mode, scaling_3d_scale, fsr_sharpness, use_taa,
## screen_space_aa, msaa_3d) the active overrides give, plus `extra` on top, without applying it.
## A cutscene hands this to ShaderPrewarm.viewport_state before the cut, so the stage compiles the
## pipeline the override will select. With no overrides and no `extra`: the base settings' state.
static func override_state(extra: Dictionary = {}, base: GraphicsSettings = null) -> Dictionary:
	var settings := base if base != null else _override_settings_or_player()
	var layer := settings.overrides.duplicate()
	layer[KEY_PRESET] = settings.preset_id
	for entry in _override_stack:
		layer.merge(entry["values"] as Dictionary, true)
	layer.merge(extra, true)
	var out := {}
	for op in settings.plan(layer):
		if op["target"] == TARGET_VIEWPORT and OVERRIDE_VIEWPORT_PROPS.has(str(op["name"])):
			out[str(op["name"])] = op["value"]
	return out


## "" when every key of `values` may be overridden (rules.override_keys) and every value is one of
## the setting's options; otherwise what is wrong.
func invalid_override(values: Dictionary) -> String:
	var allowed := (data.get("rules", {}) as Dictionary).get(KEY_OVERRIDE_KEYS, []) as Array
	if values.is_empty():
		return "no values"
	for key: Variant in values:
		if not allowed.has(str(key)):
			return "'%s' cannot be overridden (rules.%s: %s)" % [key, KEY_OVERRIDE_KEYS, str(allowed)]
		if not is_valid_value(str(key), values[key]):
			return "invalid value <%s> for '%s'" % [str(values[key]), key]
	return ""


## True when the stack has entries and every one's owner is freed or outside the tree, i.e. only
## deferred pops are left (a scene swap between the old scene leaving and its pops running).
static func _older_owners_left() -> bool:
	for entry in _override_stack:
		var owner := (entry["owner"] as WeakRef).get_ref() as Node
		if owner != null and owner.is_inside_tree():
			return false
	return not _override_stack.is_empty()


## The stack's base, else the player's settings (_player_config). Private and read-only: callers
## outside this class only ever see the copy push_override stores.
static func _override_settings_or_player() -> GraphicsSettings:
	if _override_settings != null:
		return _override_settings
	return _player_config()


## user://settings.cfg, read again only when its modified time changes or save_config wrote it, not
## on every push, pop and plan (M1-NIT-02). The cached instance itself: never mutate it.
static func _player_config() -> GraphicsSettings:
	var mtime := FileAccess.get_modified_time(CONFIG_PATH) if FileAccess.file_exists(CONFIG_PATH) else 0
	if _player_settings == null or mtime != _player_settings_mtime:
		_player_settings = GraphicsSettings.new()
		_player_settings.load_config(CONFIG_PATH)
		_player_settings_mtime = mtime
	return _player_settings


static func _viewport_state(vp: Viewport) -> Dictionary:
	var out := {}
	for prop in OVERRIDE_VIEWPORT_PROPS:
		out[prop] = vp.get(prop)
	return out


## Writes the state, then tells the listeners (VIEWPORT_STATE_GROUP) in the same frame.
static func _apply_override_state(state: Dictionary) -> void:
	if not is_instance_valid(_override_viewport):
		return
	var vp := _override_viewport as Viewport
	for prop: String in state:
		vp.set(prop, state[prop])
	if vp.is_inside_tree():
		vp.get_tree().call_group(VIEWPORT_STATE_GROUP, VIEWPORT_STATE_METHOD)


# --- Persistence (user://settings.cfg, section [graphics]) -------------------------------------


## Saves preset and overrides. Other sections of the file (audio, controls...) are preserved.
func save_config(path: String = CONFIG_PATH) -> Error:
	var cfg := ConfigFile.new()
	if FileAccess.file_exists(path):
		cfg.load(path)
	cfg.set_value(CONFIG_SECTION, KEY_VERSION, int(data.get(KEY_VERSION, 0)))
	cfg.set_value(CONFIG_SECTION, KEY_PRESET, preset_id)
	cfg.set_value(CONFIG_SECTION, KEY_OVERRIDES, overrides.duplicate())
	if path == CONFIG_PATH:
		_player_settings = null
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


## vegetation_detail: visibility-range LOD scale, MultiMesh density and small-foliage shadows, on
## the node groups zones tag (graphics_presets.json "vegetation_groups").
func _plan_vegetation(s: Dictionary, ops: Array[Dictionary]) -> void:
	var lvl := _level("vegetation_detail", s)
	var groups := data.get(KEY_VEG_GROUPS, {}) as Dictionary
	for prop in ["visibility_range_begin", "visibility_range_end"]:
		ops.append(
			_op_group(OP_SCALE, str(groups.get("lod", "")), "GeometryInstance3D", prop, float(lvl["visibility_scale"]))
		)
	ops.append(
		_op_group(
			OP_FRACTION,
			str(groups.get("multimesh", "")),
			"MultiMesh",
			"visible_instance_count",
			float(lvl["multimesh_fraction"])
		)
	)
	ops.append(
		_op_group(
			OP_SHADOW_GATE,
			str(groups.get("small_shadows", "")),
			"GeometryInstance3D",
			"cast_shadow",
			bool(lvl["small_foliage_shadows"])
		)
	)


## sky_detail: the procedural sky's quality uniforms (graphics_presets.json levels.sky_detail).
func _plan_sky(s: Dictionary, ops: Array[Dictionary]) -> void:
	var lvl := _level("sky_detail", s)
	for key: String in lvl:
		ops.append({"target": TARGET_SKY, "op": OP_SET, "name": key, "value": lvl[key]})


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


## The zone's own value of a property, captured on first use (as gates do).
static func _authored(obj: Object, name: String) -> Variant:
	var meta := StringName(AUTHORED_META_PREFIX + name)
	if not obj.has_meta(meta):
		obj.set_meta(meta, obj.get(name))
	return obj.get_meta(meta)


static func _op_group(kind: StringName, group: String, cls: String, name: String, value: Variant) -> Dictionary:
	return {"target": TARGET_GROUP, "op": kind, "group": group, "class": cls, "name": name, "value": value}


static func _op_gate(target: StringName, name: String, allowed: bool) -> Dictionary:
	return {"target": target, "op": OP_GATE, "name": name, "value": allowed}


static func _op_call(method: String, args: Array) -> Dictionary:
	return {"target": TARGET_SERVER, "op": OP_CALL, "name": method, "args": args}


static func _apply_property(obj: Object, op: Dictionary) -> void:
	var name := str(op["name"])
	match op["op"]:
		OP_SCALE:
			obj.set(name, float(_authored(obj, name)) * float(op["value"]))
			return
		OP_FRACTION:
			if obj is MultiMeshInstance3D and (obj as MultiMeshInstance3D).multimesh != null:
				var mm := (obj as MultiMeshInstance3D).multimesh
				var f := float(op["value"])
				mm.visible_instance_count = -1 if f >= 1.0 else roundi(mm.instance_count * f)
			return
		OP_SHADOW_GATE:
			var authored: Variant = _authored(obj, name)
			obj.set(name, authored if bool(op["value"]) else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
			return
	if op["op"] != OP_GATE:
		obj.set(name, op["value"])
		return
	var meta := StringName(AUTHORED_META_PREFIX + name)
	if not obj.has_meta(meta):
		obj.set_meta(meta, obj.get(name))
	obj.set(name, bool(obj.get_meta(meta)) and bool(op["value"]))
