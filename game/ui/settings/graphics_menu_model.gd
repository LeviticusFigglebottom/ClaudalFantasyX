class_name GraphicsMenuModel
extends RefCounted
## Logic of the Graphics settings page (M1-UI-10; graphics_settings.md, "The Graphics menu"), no
## nodes. Row 0 is the preset ("Custom" once a setting differs from it); then one row per setting
## of graphics_presets.json, in its order. cycle() steps the row's value and goes through
## GraphicsRuntime, which saves user://settings.cfg and applies the change at once:
##   the preset row  GraphicsRuntime.select_preset(id, viewport) (clears every override)
##   a setting row   GraphicsRuntime.set_override(key, value, viewport)
## Display text comes from game/data/ui/graphics_menu.json (value_keys, on/off, percentages).
## A preset change may spawn the resident shader warm-up (GraphicsRuntime armed, M1-RND-22): cycle()
## keeps it in `warmup`, and the view holds its fade until warmup_done() (M1-UI-11). A setting row
## never spawns one (graphics_settings.md, "The Graphics menu").

signal changed

const DATA_PATH := "res://game/data/ui/graphics_menu.json"
const ROW_PRESET := &"preset"

var data: Dictionary = {}
var cursor := 0
## Where cycle() applies (the game's root viewport; tests pass their own or null).
var viewport: Viewport
## The warm-up the last preset change spawned (null when none, or when GraphicsRuntime is disarmed).
var warmup: ShaderPrewarm

var _warmup_finished := false


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("graphics_menu")) != TYPE_DICTIONARY:
		push_error("GraphicsMenuModel: could not read 'graphics_menu' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["graphics_menu"] as Dictionary


func _init(vp: Viewport = null) -> void:
	viewport = vp
	data = load_data()


func settings() -> GraphicsSettings:
	return GraphicsRuntime.settings()


## The row ids: ROW_PRESET, then each setting key.
func row_ids() -> Array[StringName]:
	var out: Array[StringName] = [ROW_PRESET]
	for key: String in (settings().data.get("settings", {}) as Dictionary).keys():
		out.append(StringName(key))
	return out


func current() -> StringName:
	var ids := row_ids()
	return ids[clampi(cursor, 0, ids.size() - 1)]


func label(row: StringName) -> String:
	if row == ROW_PRESET:
		return tr("GFX_MENU_PRESET")
	return tr(str(_setting(row).get("label_key", row)))


## The value as shown: the preset's name or "Custom", or the setting's resolved value.
func value_text(row: StringName) -> String:
	var gs := settings()
	if row == ROW_PRESET:
		return tr(str(data.get("custom_key", ""))) if gs.is_custom() else tr(_preset_name_key(gs.preset_id))
	return format_value(String(row), gs.resolve().get(String(row)))


func format_value(key: String, value: Variant) -> String:
	if value is bool:
		return tr(str(data.get("on_key" if value else "off_key", "")))
	if value is String:
		return tr(str((data.get("value_keys", {}) as Dictionary).get(value, value)))
	if key in (data.get("percent_settings", []) as Array):
		return "%d%%" % roundi(float(value) * 100.0)
	if key in (data.get("multiplier_settings", []) as Array):
		return "×%s" % str(value)
	return str(value)


## Moves the cursor (wrapping). Returns true.
func move(delta: int) -> bool:
	cursor = posmod(cursor + delta, row_ids().size())
	changed.emit()
	return true


func set_cursor(index: int) -> bool:
	if index < 0 or index >= row_ids().size():
		return false
	cursor = index
	changed.emit()
	return true


## Steps the current row's value by `delta` (wrapping through its options), saves and applies it.
## Returns true when the value changed.
func cycle(delta: int) -> bool:
	var gs := settings()
	var row := current()
	var ok := false
	if row == ROW_PRESET:
		var ids := gs.preset_ids()
		var at := ids.find(gs.preset_id)
		var before := GraphicsRuntime.last_warmup
		var before_id := before.get_instance_id() if is_instance_valid(before) else 0
		ok = GraphicsRuntime.select_preset(ids[posmod(at + delta, ids.size())], viewport)
		var spawned := GraphicsRuntime.last_warmup
		if ok and is_instance_valid(spawned) and spawned.get_instance_id() != before_id:
			_track_warmup(spawned)
	else:
		var options := gs.setting_options(String(row))
		if options.is_empty():
			return false
		var at := options.find(gs.resolve().get(String(row)))
		var next: Variant = options[posmod(at + delta, options.size())]
		ok = GraphicsRuntime.set_override(String(row), next, viewport)
	if ok:
		changed.emit()
	return ok


## True once the tracked warm-up finished, freed or stopped running (and when there is none). A
## warm-up whose start() failed never runs, so it counts as done rather than holding the veil.
func warmup_done() -> bool:
	if warmup == null:
		return true
	if _warmup_finished or not is_instance_valid(warmup) or warmup.is_queued_for_deletion() or not warmup.is_running():
		warmup = null
		return true
	return false


func _track_warmup(node: ShaderPrewarm) -> void:
	warmup = node
	_warmup_finished = false
	node.finished.connect(_on_warmup_finished, CONNECT_ONE_SHOT)


func _on_warmup_finished(_stats: Dictionary) -> void:
	_warmup_finished = true


## The help line for the current row.
func help_key() -> String:
	return "GFX_MENU_HELP_PRESET" if current() == ROW_PRESET else "GFX_MENU_HELP_SETTING"


func _setting(row: StringName) -> Dictionary:
	return (settings().data.get("settings", {}) as Dictionary).get(String(row), {})


func _preset_name_key(id: String) -> String:
	for p: Variant in settings().data.get("presets", []):
		if str((p as Dictionary).get("id", "")) == id:
			return str((p as Dictionary).get("name_key", id))
	return id
