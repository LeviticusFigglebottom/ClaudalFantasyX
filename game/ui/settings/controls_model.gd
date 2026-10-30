class_name ControlsModel
extends SettingsPageModel
## Logic of the Controls page (M2-UI-13, SPEC §6.11; tech/ui.md § Controls), no nodes. Rows: the
## column row (which device Confirm rebinds: keyboard or pad), one row per remappable action of
## game/data/ui/controls.json, then "Reset to defaults". An action's value shows its key and its
## pad binding ("Enter · A"), the active column in brackets.
## Rebinding: start_listen(action, kind), then feed() each input event. The first pressed key (or
## pad button, for the pad column) binds; keyboard Escape or pad button B cancels, hard-wired from
## the data (never read from ui_cancel, which can be rebound), and so does a mouse click. A binding
## replaces all the action's keys (or pad buttons) with the one pressed; its stick axes are fixed.
## A key or button already used by an action sharing a context is swapped: that action takes the
## rebound action's old one. A result that would leave an action with no key or no pad input, put
## one input on two actions in a context, or use a reserved key is rejected, and listening goes on.
## Every bind saves user://settings.cfg [controls] (other sections kept) and applies to InputMap.
## Defaults are the InputMap at boot (with the data's pad_defaults), captured before saved bindings
## apply; ControlsModel.apply_saved runs once at boot (game/core/boot.gd).

enum Feed { IGNORED, BOUND, CANCELLED, REJECTED }

const DATA_PATH := "res://game/data/ui/controls.json"
const ROW_DEVICE := &"device"
const ROW_RESET := &"reset"
const KIND_KEYS := &"keys"
const KIND_PAD := &"pad"
const KINDS: Array[StringName] = [KIND_KEYS, KIND_PAD]
## The controls line while choosing a binding (Confirm changes it).
const REBIND_CONTROLS_KEY := "SET_MENU_CONTROLS_REBIND"

## {action: Array[InputEvent]}: every remappable action's events at boot (defaults()).
static var _defaults: Dictionary = {}

var data: Dictionary = {}
## Where a change saves ("" = nowhere; tests and captures).
var config_path := UiSettings.CONFIG_PATH
## The column Confirm rebinds: KIND_KEYS or KIND_PAD.
var device: StringName = KIND_KEYS
## {action: {keys: Array of key ids, pad: Array of button indexes}}: what is shown and applied.
var bindings: Dictionary = {}

var _listen_action: StringName = &""
var _listen_kind: StringName = &""
var _rejected := false
var _notice := ""


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("controls")) != TYPE_DICTIONARY:
		push_error("ControlsModel: could not read 'controls' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["controls"] as Dictionary


## The remappable action ids, in display order.
static func action_ids(d: Dictionary) -> Array[StringName]:
	var out: Array[StringName] = []
	for row: Variant in d.get("actions", []):
		out.append(StringName(str((row as Dictionary).get("id", ""))))
	return out


## The default events of every remappable action, captured on the first call: the field actions
## are added (FieldInput) and the data's pad_defaults given to an action with no pad button first.
static func defaults() -> Dictionary:
	if _defaults.is_empty():
		_capture_defaults(load_data())
	return _defaults


## Loads the [controls] section of `path` and applies it to InputMap. Returns true when saved
## bindings were applied (false: none saved, or they were invalid and the defaults stay).
static func apply_saved(path: String = UiSettings.CONFIG_PATH) -> bool:
	var d := load_data()
	defaults()
	var saved := read_saved(path, d)
	if saved.is_empty():
		return false
	apply_bindings(saved, d)
	return true


## The full bindings saved in `path` (unsaved actions keep their defaults), or {} when there are
## none or they break a rule (check), so a hand-edited file can never lock the player out.
static func read_saved(path: String, d: Dictionary) -> Dictionary:
	var cfg := ConfigFile.new()
	var section := str(d.get("config_section", ""))
	if cfg.load(path) != OK or not cfg.has_section(section):
		return {}
	var out := default_bindings(d)
	for action: StringName in action_ids(d):
		if not cfg.has_section_key(section, String(action)):
			continue
		var v: Variant = cfg.get_value(section, String(action))
		if typeof(v) != TYPE_DICTIONARY:
			continue
		for kind in KINDS:
			var codes := _ints((v as Dictionary).get(String(kind), []))
			if not codes.is_empty():
				(out[action] as Dictionary)[kind] = codes
	if not check(out, d):
		push_warning("ControlsModel: the saved bindings in %s break a rule; using the defaults" % path)
		return {}
	return out


## The default bindings ({action: {keys, pad}}).
static func default_bindings(d: Dictionary) -> Dictionary:
	var out := {}
	for action: StringName in action_ids(d):
		out[action] = bindings_of(defaults().get(action, []) as Array)
	return out


## The bindings InputMap holds now.
static func current_bindings(d: Dictionary) -> Dictionary:
	var out := {}
	for action: StringName in action_ids(d):
		out[action] = bindings_of(InputMap.action_get_events(action) if InputMap.has_action(action) else [])
	return out


## {keys, pad} of a list of events: key ids and pad button indexes, in order, without repeats.
static func bindings_of(events: Array) -> Dictionary:
	var keys: Array = []
	var pad: Array = []
	for ev: Variant in events:
		if ev is InputEventKey and not keys.has(key_id(ev as InputEventKey)):
			keys.append(key_id(ev as InputEventKey))
		elif ev is InputEventJoypadButton and not pad.has(int((ev as InputEventJoypadButton).button_index)):
			pad.append(int((ev as InputEventJoypadButton).button_index))
	return {KIND_KEYS: keys, KIND_PAD: pad}


## A key event's id: its physical keycode, or its keycode when it has none (Godot's ui_* defaults).
static func key_id(ev: InputEventKey) -> int:
	return int(ev.physical_keycode) if ev.physical_keycode != KEY_NONE else int(ev.keycode)


## True when `b` keeps every rule: each action has a key and a pad input (a button or a fixed
## axis), no key is reserved, and no key or button is on two actions that share a context (the
## fixed actions of a context count as holding theirs).
static func check(b: Dictionary, d: Dictionary) -> bool:
	var reserved := _reserved_keys(d)
	var held := {}  # "context/kind/code" -> action
	var fixed := d.get("fixed_actions", {}) as Dictionary
	for context: String in fixed:
		for name: Variant in fixed[context]:
			var action := StringName(str(name))
			if not InputMap.has_action(action):
				continue
			var own := bindings_of(InputMap.action_get_events(action))
			for kind in KINDS:
				for code: int in own[kind]:
					held["%s/%s/%d" % [context, kind, code]] = action
	for row: Variant in d.get("actions", []):
		var action := StringName(str((row as Dictionary).get("id", "")))
		var own := b.get(action, {}) as Dictionary
		var keys := own.get(KIND_KEYS, []) as Array
		var pad := own.get(KIND_PAD, []) as Array
		if keys.is_empty() or (pad.is_empty() and axes_of(action).is_empty()):
			return false
		for code: Variant in keys:
			if reserved.has(int(code)):
				return false
		for context: Variant in (row as Dictionary).get("contexts", []):
			for kind in KINDS:
				for code: Variant in own.get(kind, []):
					var slot := "%s/%s/%d" % [context, kind, int(code)]
					if held.has(slot) and held[slot] != action:
						return false
					held[slot] = action
	return true


## Writes `b` into InputMap: each action's keys, its pad buttons, then its fixed stick axes. A key
## or button that is one of the action's defaults keeps that default event (keycode or modifiers).
static func apply_bindings(b: Dictionary, d: Dictionary) -> void:
	var all_devices := int(d.get("device_all", 0))
	for action: Variant in b:
		var name := StringName(str(action))
		if not InputMap.has_action(name):
			continue
		var defs := defaults().get(name, []) as Array
		InputMap.action_erase_events(name)
		for code: Variant in (b[action] as Dictionary).get(KIND_KEYS, []):
			InputMap.action_add_event(name, _key_event(int(code), defs))
		for button: Variant in (b[action] as Dictionary).get(KIND_PAD, []):
			InputMap.action_add_event(name, _button_event(int(button), defs, all_devices))
		for ev: InputEventJoypadMotion in axes_of(name):
			InputMap.action_add_event(name, ev.duplicate() as InputEvent)


## Puts every remappable action back to its default events (Reset, and tests).
static func restore_defaults() -> void:
	for action: StringName in defaults():
		if not InputMap.has_action(action):
			continue
		InputMap.action_erase_events(action)
		for ev: InputEvent in defaults()[action]:
			InputMap.action_add_event(action, ev.duplicate() as InputEvent)


## The fixed stick axes of `action` (from its defaults).
static func axes_of(action: StringName) -> Array[InputEventJoypadMotion]:
	var out: Array[InputEventJoypadMotion] = []
	for ev: Variant in defaults().get(action, []):
		if ev is InputEventJoypadMotion:
			out.append(ev as InputEventJoypadMotion)
	return out


static func _capture_defaults(d: Dictionary) -> void:
	FieldInput.ensure_actions()
	ObjectiveHud.ensure_action()  # M2-UI-17: show the objective
	DialogueAssist.ensure_action()  # M2-UI-25: the dialogue backlog
	LatticeMenu.ensure_action()  # M3-MNU-04: the Lattice overview
	# M2-MNU-04: the battle pause (BattlePause adds it in battle; it must exist to be remapped)
	var pause := FieldInput.load_json(BattlePauseMenu.DATA_PATH).get("battle_pause", {}) as Dictionary
	FieldInput.add_actions(pause.get("action", {}) as Dictionary, 0.0)
	var pad_defaults := d.get("pad_defaults", {}) as Dictionary
	var all_devices := int(d.get("device_all", 0))
	for action: StringName in action_ids(d):
		if not InputMap.has_action(action):
			push_warning("ControlsModel: '%s' is not an InputMap action" % action)
			continue
		_give_pad_defaults(action, pad_defaults, all_devices)
		var events: Array[InputEvent] = []
		for ev in InputMap.action_get_events(action):
			events.append(ev.duplicate() as InputEvent)
		_defaults[action] = events
	# The fixed actions (Page Up / Down) take theirs too, so a pad reaches every page jump (M2-UI-26).
	var fixed := d.get("fixed_actions", {}) as Dictionary
	for context: String in fixed:
		for name: Variant in fixed[context]:
			if InputMap.has_action(StringName(str(name))):
				_give_pad_defaults(StringName(str(name)), pad_defaults, all_devices)


## Adds `action`'s pad_defaults buttons when it has no pad button yet.
static func _give_pad_defaults(action: StringName, pad_defaults: Dictionary, device: int) -> void:
	for ev in InputMap.action_get_events(action):
		if ev is InputEventJoypadButton:
			return
	for button: Variant in pad_defaults.get(String(action), []):
		InputMap.action_add_event(action, _button_event(int(button), [], device))


static func _key_event(code: int, defs: Array) -> InputEventKey:
	for ev: Variant in defs:
		if ev is InputEventKey and key_id(ev as InputEventKey) == code:
			return (ev as InputEventKey).duplicate() as InputEventKey
	var k := InputEventKey.new()
	k.physical_keycode = code as Key
	return k


static func _button_event(button: int, defs: Array, all_devices: int) -> InputEventJoypadButton:
	for ev: Variant in defs:
		if ev is InputEventJoypadButton and int((ev as InputEventJoypadButton).button_index) == button:
			return (ev as InputEventJoypadButton).duplicate() as InputEventJoypadButton
	var b := InputEventJoypadButton.new()
	b.button_index = button as JoyButton
	b.device = all_devices
	return b


static func _reserved_keys(d: Dictionary) -> Array[int]:
	var out: Array[int] = []
	for name: Variant in d.get("reserved_keys", []):
		out.append(int(OS.find_keycode_from_string(str(name))))
	return out


static func _ints(v: Variant) -> Array:
	var out: Array = []
	if typeof(v) != TYPE_ARRAY and typeof(v) != TYPE_PACKED_INT32_ARRAY and typeof(v) != TYPE_PACKED_INT64_ARRAY:
		return out
	for x: Variant in v:
		if typeof(x) == TYPE_INT and not out.has(int(x)):
			out.append(int(x))
	return out


## `save_path` "" saves nothing (tests, captures).
func _init(save_path: String = UiSettings.CONFIG_PATH) -> void:
	data = load_data()
	config_path = save_path
	defaults()
	bindings = current_bindings(data)


# --- SettingsPageModel ---------------------------------------------------------------------


func row_ids() -> Array[StringName]:
	var out: Array[StringName] = [ROW_DEVICE]
	out.append_array(action_ids(data))
	out.append(ROW_RESET)
	return out


func title_key() -> String:
	return str(data.get("title_key", ""))


func label(row: StringName) -> String:
	if row == ROW_DEVICE:
		return tr(str(data.get("device_label_key", "")))
	if row == ROW_RESET:
		return tr(str(data.get("reset_label_key", "")))
	return tr(str(_action_row(row).get("label_key", row)))


## The column row: the device; an action: "<key> · <pad>", the active column in brackets and the
## listened-for cell as a wait mark; the reset row: nothing.
func value_text(row: StringName) -> String:
	if row == ROW_DEVICE:
		return tr(str((data.get("device_keys", {}) as Dictionary).get(String(device), "")))
	if not bindings.has(row):
		return ""
	var cells := {KIND_KEYS: key_name(row), KIND_PAD: pad_name(row)}
	if row == _listen_action:
		cells[_listen_kind] = tr(str(data.get("waiting_key", "")))
	cells[device] = tr(str(data.get("active_fmt_key", ""))).format({"v": cells[device]})
	return tr(str(data.get("value_fmt_key", ""))).format({"key": cells[KIND_KEYS], "pad": cells[KIND_PAD]})


## Left / Right on any row: switches the column Confirm rebinds.
func cycle(delta: int) -> bool:
	if is_listening():
		return false
	device = KINDS[posmod(KINDS.find(device) + delta, KINDS.size())]
	_notice = ""
	changed.emit()
	return true


func move(delta: int) -> bool:
	_notice = ""
	return super(delta)


func set_cursor(index: int) -> bool:
	_notice = ""
	return super(index)


## Rebinding: Confirm changes a binding; while listening the help says what to press, so no controls line.
func controls_key() -> String:
	return "" if is_listening() else REBIND_CONTROLS_KEY


func help_key() -> String:
	var keys := data.get("help_keys", {}) as Dictionary
	if is_listening():
		if _rejected:
			return str(keys.get("rejected", ""))
		return str(keys.get("listen_keys" if _listen_kind == KIND_KEYS else "listen_pad", ""))
	match current():
		ROW_DEVICE:
			return str(keys.get("device", ""))
		ROW_RESET:
			return str(keys.get("reset", ""))
	return str(keys.get("action_keys" if device == KIND_KEYS else "action_pad", ""))


## The help line: a swap or reset notice once, else the help for the row or the listening state.
func help_text() -> String:
	return _notice if _notice != "" and not is_listening() else tr(help_key())


# --- Rebinding -----------------------------------------------------------------------------


## Confirm on the current row: the column row switches, an action listens on the active column,
## the reset row resets. Returns true when something happened.
func activate() -> bool:
	match current():
		ROW_DEVICE:
			return cycle(1)
		ROW_RESET:
			reset_to_defaults()
			return true
	return start_listen(current(), device)


func start_listen(action: StringName, kind: StringName) -> bool:
	if not bindings.has(action) or not KINDS.has(kind):
		return false
	_listen_action = action
	_listen_kind = kind
	_rejected = false
	_notice = ""
	changed.emit()
	return true


func is_listening() -> bool:
	return _listen_action != &""


func listening_action() -> StringName:
	return _listen_action


func listening_kind() -> StringName:
	return _listen_kind


func cancel_listen() -> void:
	if not is_listening():
		return
	_listen_action = &""
	_listen_kind = &""
	_rejected = false
	changed.emit()


## Takes one event while listening. Keyboard Escape and pad B cancel on either column (hard-wired,
## controls.json listen_cancel), as does a mouse click. Otherwise the first pressed key (keyboard
## column) or pad button (pad column) binds; anything else is ignored.
func feed(event: InputEvent) -> Feed:
	if not is_listening() or event == null or not event.is_pressed() or event.is_echo():
		return Feed.IGNORED
	if is_listen_cancel(event):
		cancel_listen()
		return Feed.CANCELLED
	var kind := KIND_KEYS if event is InputEventKey else (KIND_PAD if event is InputEventJoypadButton else &"")
	var code := _code_of(event)
	if kind != _listen_kind or (kind == KIND_KEYS and code == KEY_NONE):
		return Feed.IGNORED
	if not bind(_listen_action, _listen_kind, code):
		_rejected = true
		changed.emit()
		return Feed.REJECTED
	_listen_action = &""
	_listen_kind = &""
	_rejected = false
	changed.emit()
	return Feed.BOUND


## True for the hard-wired ways out of listening: keyboard Escape, pad B (controls.json
## listen_cancel) and any mouse button.
func is_listen_cancel(event: InputEvent) -> bool:
	var cancel := data.get("listen_cancel", {}) as Dictionary
	if event is InputEventMouseButton:
		return true
	if event is InputEventKey:
		return key_id(event as InputEventKey) == int(OS.find_keycode_from_string(str(cancel.get("key", ""))))
	if event is InputEventJoypadButton:
		return int((event as InputEventJoypadButton).button_index) == int(cancel.get("pad_button", JOY_BUTTON_INVALID))
	return false


## A key event's id or a pad button's index (0 for anything else).
static func _code_of(event: InputEvent) -> int:
	if event is InputEventKey:
		return key_id(event as InputEventKey)
	if event is InputEventJoypadButton:
		return int((event as InputEventJoypadButton).button_index)
	return 0


## Binds `code` (a key id or a pad button) as `action`'s only `kind` input, swapping it with any
## action of a shared context that held it. Applies and saves. Returns false (nothing changed)
## when the result would break a rule (check).
func bind(action: StringName, kind: StringName, code: int) -> bool:
	if not bindings.has(action) or not KINDS.has(kind):
		return false
	var trial := bindings.duplicate(true)
	var mine := (trial[action] as Dictionary)[kind] as Array
	var had_old := not mine.is_empty()
	var old := int(mine[0]) if had_old else 0
	var swapped: Array[StringName] = []
	for other: StringName in trial:
		if other == action or not _shares_context(action, other):
			continue
		var theirs := (trial[other] as Dictionary)[kind] as Array
		var at := theirs.find(code)
		if at < 0:
			continue
		if had_old and not theirs.has(old):
			theirs[at] = old
		else:
			theirs.remove_at(at)
		swapped.append(other)
	(trial[action] as Dictionary)[kind] = [code]
	if not check(trial, data):
		return false
	bindings = trial
	apply_bindings(bindings, data)
	save()
	var names: PackedStringArray = []
	for other in swapped:
		names.append(label(other))
	var fmt := str((data.get("help_keys", {}) as Dictionary).get("swapped", ""))
	_notice = tr(fmt).format({"action": ", ".join(names)}) if not names.is_empty() else ""
	return true


## Puts every action back to its default binding, applies it and clears the saved section.
func reset_to_defaults() -> void:
	cancel_listen()
	restore_defaults()
	bindings = default_bindings(data)
	save()
	_notice = tr(str((data.get("help_keys", {}) as Dictionary).get("was_reset", "")))
	changed.emit()


## Saves the bindings to config_path's [controls] section (other sections kept). At the defaults
## the section is removed. Returns OK when there is nothing to save to.
func save() -> Error:
	if config_path == "":
		return OK
	var cfg := ConfigFile.new()
	cfg.load(config_path)  # keep the other sections; a missing file is fine
	var section := str(data.get("config_section", ""))
	if cfg.has_section(section):
		cfg.erase_section(section)
	if bindings != default_bindings(data):
		for action: StringName in action_ids(data):
			var own := bindings[action] as Dictionary
			cfg.set_value(section, String(action), {String(KIND_KEYS): own[KIND_KEYS], String(KIND_PAD): own[KIND_PAD]})
	return cfg.save(config_path)


# --- Display -------------------------------------------------------------------------------


## The action's first key, by name.
func key_name(action: StringName) -> String:
	var keys := (bindings.get(action, {}) as Dictionary).get(KIND_KEYS, []) as Array
	return OS.get_keycode_string(int(keys[0]) as Key) if not keys.is_empty() else ""


## The action's first pad button by name, else its fixed stick direction.
func pad_name(action: StringName) -> String:
	var pad := (bindings.get(action, {}) as Dictionary).get(KIND_PAD, []) as Array
	if not pad.is_empty():
		var key: Variant = (data.get("pad_button_keys", {}) as Dictionary).get(str(pad[0]))
		if key != null:
			return tr(str(key))
		return tr(str(data.get("button_fmt_key", ""))).format({"n": int(pad[0])})
	for ev in axes_of(action):
		var dir := "%d%s" % [int(ev.axis), "-" if ev.axis_value < 0.0 else "+"]
		return tr(str((data.get("pad_axis_keys", {}) as Dictionary).get(dir, dir)))
	return ""


func _action_row(action: StringName) -> Dictionary:
	for row: Variant in data.get("actions", []):
		if StringName(str((row as Dictionary).get("id", ""))) == action:
			return row as Dictionary
	return {}


func _shares_context(a: StringName, b: StringName) -> bool:
	var theirs := _action_row(b).get("contexts", []) as Array
	for context: Variant in _action_row(a).get("contexts", []):
		if theirs.has(context):
			return true
	return false
