class_name FieldInput
extends RefCounted
## Runtime InputMap actions from data (M1-ARC-01). project.godot stays untouched: an action that
## already exists there wins, so the Lead can move bindings into the project later without code
## changes. Data: game/data/world/field_input.json (the debug overlay uses the same format).

const DATA_PATH := "res://game/data/world/field_input.json"
const MOVE_LEFT := &"field_move_left"
const MOVE_RIGHT := &"field_move_right"
const MOVE_FORWARD := &"field_move_forward"
const MOVE_BACK := &"field_move_back"
const WALK := &"field_walk"
const INTERACT := &"field_interact"
const CAMERA_LEFT := &"field_camera_left"
const CAMERA_RIGHT := &"field_camera_right"
const KEY_KEYS := "keys"
const KEY_AXES := "joy_axes"
const KEY_BUTTONS := "joy_buttons"


static func load_json(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("FieldInput: cannot parse %s" % path)
		return {}
	return parsed as Dictionary


## Adds the field actions from field_input.json. Returns the names that were added.
static func ensure_actions(path: String = DATA_PATH) -> PackedStringArray:
	var data := load_json(path)
	return add_actions(data.get("actions", {}) as Dictionary, float(data.get("deadzone", 0.0)))


## Adds every action in `actions` ({name: {keys, joy_axes, joy_buttons}}) that the InputMap lacks.
static func add_actions(actions: Dictionary, deadzone: float) -> PackedStringArray:
	var added := PackedStringArray()
	for name: String in actions:
		var action := StringName(name)
		if InputMap.has_action(action):
			continue
		InputMap.add_action(action, deadzone)
		for ev in events_for(actions[name] as Dictionary):
			InputMap.action_add_event(action, ev)
		added.append(name)
	return added


## Builds the InputEvents for one action spec. Unknown key names are reported and skipped.
static func events_for(spec: Dictionary) -> Array[InputEvent]:
	var out: Array[InputEvent] = []
	for key_name: Variant in spec.get(KEY_KEYS, []):
		var code := OS.find_keycode_from_string(str(key_name))
		if code == KEY_NONE:
			push_warning("FieldInput: unknown key name '%s'" % key_name)
			continue
		var k := InputEventKey.new()
		k.physical_keycode = code
		out.append(k)
	for axis_spec: Variant in spec.get(KEY_AXES, []):
		var pair := axis_spec as Array
		var m := InputEventJoypadMotion.new()
		m.axis = int(pair[0]) as JoyAxis
		m.axis_value = float(pair[1])
		out.append(m)
	for button: Variant in spec.get(KEY_BUTTONS, []):
		var b := InputEventJoypadButton.new()
		b.button_index = int(button) as JoyButton
		out.append(b)
	return out


## The move stick in action space: x right, y back (Input.get_vector convention).
static func move_vector() -> Vector2:
	return Input.get_vector(MOVE_LEFT, MOVE_RIGHT, MOVE_FORWARD, MOVE_BACK)
