class_name InputNames
extends RefCounted
## The names of an action's bindings for on-screen hints (M2-UI-20/24): its first key, or its first
## pad button once the pad was the last device used (generic names from controls.json
## pad_button_keys, no console-brand glyphs). Field UI calls note() from _input to track the device.

## True once the pad was the last device used.
static var using_pad := false


## Remembers whether the pad or the keyboard and mouse was used last. `deadzone`: stick motion
## below it is ignored (resting sticks drift).
static func note(event: InputEvent, deadzone: float) -> void:
	if event is InputEventJoypadButton and (event as InputEventJoypadButton).pressed:
		using_pad = true
	elif event is InputEventJoypadMotion:
		if absf((event as InputEventJoypadMotion).axis_value) >= deadzone:
			using_pad = true
	elif event is InputEventKey or event is InputEventMouseButton:
		using_pad = false


## `action`'s binding by name: its first pad button when `pad`, else its first key (either falls
## back to the other; "" when the action is unbound or missing).
static func first_name(action: StringName, pad: bool = using_pad) -> String:
	var events: Array[InputEvent] = []
	if InputMap.has_action(action):
		events = InputMap.action_get_events(action)
	var key_name := ""
	var pad_name := ""
	for ev: InputEvent in events:
		if ev is InputEventKey and key_name == "":
			var k := ev as InputEventKey
			key_name = OS.get_keycode_string(k.physical_keycode if k.physical_keycode != KEY_NONE else k.keycode)
		elif ev is InputEventJoypadButton and pad_name == "":
			var b := str(int((ev as InputEventJoypadButton).button_index))
			var keys := ControlsModel.load_data().get("pad_button_keys", {}) as Dictionary
			pad_name = TranslationServer.translate(str(keys[b])) if keys.has(b) else b
	if pad and pad_name != "":
		return pad_name
	return key_name if key_name != "" else pad_name


## `text` with every {action} replaced by that action's binding name (unknown names stay).
static func fill(text: String, pad: bool = using_pad) -> String:
	var re := RegEx.create_from_string("\\{([a-z_]+)\\}")
	var out := text
	for m in re.search_all(text):
		var n := first_name(StringName(m.get_string(1)), pad)
		if n != "":
			out = out.replace(m.get_string(0), n)
	return out
