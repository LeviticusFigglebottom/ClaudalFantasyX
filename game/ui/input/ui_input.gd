extends Node
## The UiInput autoload (M2-UI-26, ADR 0036): input every screen shares, so keyboard, mouse and
## controller work the same everywhere without each screen re-implementing it.
## - **Mouse cancel:** a right click or the mouse's back button becomes a `ui_cancel` press, and its
##   release a `ui_cancel` release, delivered through the normal input path, so every screen that
##   backs out on Cancel also backs out on them, including over a menu whose controls stop the
##   click, and holding the button holds Cancel (a cutscene's hold to skip, M2-UI-26).
## - **Pad defaults everywhere:** ControlsModel.defaults() runs here, at startup, so pad A and B
##   confirm and cancel (controls.json pad_defaults) in every scene, not only after boot.tscn.
## - **Pad repeat (the Lead's Act I menu pass, controller only):** a key held on a list repeats (the OS's echo) but a
##   held d-pad button or stick did not, so a pad player tapped through every row of a long list. A held pad direction
##   (repeat_actions) now repeats after repeat_delay_sec, every repeat_rate_sec, as a press and release of the action
##   marked with repeat_device. Whether it is still held is read from the pad itself, never the action, so a repeat
##   can never leave an action stuck down.
## - **Last device:** remembers whether the pad or the keyboard and mouse was used last
##   (InputNames.using_pad), so key glyphs and prompts switch with the player's hands.
## - **Debug launch options (M2-UI-28):** in debug builds, `--pseudo-loc` or HYMN_PSEUDO_LOC turns
##   on the pseudo-localisation here, before the first scene builds its text. The tool is loaded by
##   path (DEBUG_PSEUDO_LOC), so release exports can leave game/core/debug/ out.
## Data: game/data/ui/ui_input.json.

## Emitted when the last device used changes (true: the pad).
signal device_changed(pad: bool)

const DATA_PATH := "res://game/data/ui/ui_input.json"
const DEBUG_PSEUDO_LOC := "res://game/core/debug/pseudo_loc.gd"

var _d: Dictionary = {}
var _cancel_buttons: Array[int] = []
## The pad direction being held for repeat: its action, the pad event that pressed it, and how long it has been held.
var _held_action: StringName = &""
var _held_event: InputEvent
var _held_sec := 0.0
var _next_repeat_sec := 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS  # menus pause the tree
	_d = load_data()
	for b: Variant in _d.get("cancel_mouse_buttons", []):
		_cancel_buttons.append(int(b))
	ControlsModel.defaults()  # the pad's Confirm and Cancel buttons, before any scene asks
	_debug_launch_options()


## Debug builds: the pseudo-localisation when the launch asks for it (M2-UI-28).
static func _debug_launch_options() -> void:
	if OS.is_debug_build() and ResourceLoader.exists(DEBUG_PSEUDO_LOC):
		(load(DEBUG_PSEUDO_LOC) as GDScript).call(&"apply_launch_options")


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("ui_input")) != TYPE_DICTIONARY:
		push_error("UiInput: could not read 'ui_input' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["ui_input"] as Dictionary


func _input(event: InputEvent) -> void:
	var was := InputNames.using_pad
	InputNames.note(event, float(_d.get("pad_deadzone", 0.5)))
	if InputNames.using_pad != was:
		device_changed.emit(InputNames.using_pad)
	if is_cancel_button(event):
		get_viewport().set_input_as_handled()
		send_cancel_edge(get_viewport(), event.is_pressed())
	note_pad_hold(event)


## Starts or ends a pad direction's hold (repeat_actions) from a pad event; other events are ignored.
func note_pad_hold(event: InputEvent) -> void:
	if not (event is InputEventJoypadButton or event is InputEventJoypadMotion):
		return
	for a: Variant in _d.get("repeat_actions", []):
		var action := StringName(str(a))
		if not InputMap.has_action(action):
			continue
		if event.is_action_pressed(action) and _held_action != action:
			_held_action = action
			_held_event = event
			_held_sec = 0.0
			_next_repeat_sec = float(_d.get("repeat_delay_sec", 0.0))
		elif event.is_action_released(action) and _held_action == action:
			_held_action = &""


func _process(delta: float) -> void:
	advance_repeat(delta)


## Moves the held pad direction's clock on by `delta` seconds and sends its repeats that are due. Returns how many.
func advance_repeat(delta: float, held: Callable = Callable()) -> int:
	if _held_action == &"":
		return 0
	var still := bool(held.call()) if held.is_valid() else pad_still_holds(_held_event)
	if not still:
		_held_action = &""
		return 0
	_held_sec += delta
	var sent := 0
	var rate := maxf(float(_d.get("repeat_rate_sec", 0.0)), 0.01)
	while _held_sec >= _next_repeat_sec:
		send_repeat(get_viewport(), _held_action)
		_next_repeat_sec += rate
		sent += 1
	return sent


## The action being repeated (&"" when no pad direction is held).
func held_action() -> StringName:
	return _held_action


## True while the pad still holds what `event` pressed: its button, or its stick past the deadzone the same way.
func pad_still_holds(event: InputEvent) -> bool:
	if event is InputEventJoypadButton:
		var b := event as InputEventJoypadButton
		return Input.is_joy_button_pressed(b.device, b.button_index)
	if event is InputEventJoypadMotion:
		var m := event as InputEventJoypadMotion
		var now := Input.get_joy_axis(m.device, m.axis)
		return absf(now) >= float(_d.get("pad_deadzone", 0.5)) and signf(now) == signf(m.axis_value)
	return false


## Delivers one repeat of `action` to `vp`: a press, then its release, marked with the data's repeat_device.
static func send_repeat(vp: Viewport, action: StringName) -> void:
	for down: bool in [true, false]:
		var a := InputEventAction.new()
		a.action = action
		a.pressed = down
		a.device = int(load_data().get("repeat_device", 0))
		vp.push_input(a)


## True for a mouse button press that stands for Cancel.
func is_cancel_click(event: InputEvent) -> bool:
	return is_cancel_button(event) and event.is_pressed()


## True for a press or a release of a mouse button that stands for Cancel.
func is_cancel_button(event: InputEvent) -> bool:
	var mb := event as InputEventMouseButton
	return mb != null and _cancel_buttons.has(int(mb.button_index))


## Delivers a ui_cancel press and release to `vp` (the press first, so is_action_pressed sees it),
## marked with the data's `cancel_device`, so a screen can tell a mouse Cancel from a plain one.
static func send_cancel(vp: Viewport) -> void:
	send_cancel_edge(vp, true)
	send_cancel_edge(vp, false)


## Delivers one ui_cancel press (`down`) or release to `vp`, marked as send_cancel marks it: the
## cancel button's own press and release, so holding it holds Cancel.
static func send_cancel_edge(vp: Viewport, down: bool) -> void:
	var a := InputEventAction.new()
	a.action = &"ui_cancel"
	a.pressed = down
	a.device = mouse_cancel_device()
	vp.push_input(a)


## The device id a mouse Cancel carries (ui_input.json cancel_device).
static func mouse_cancel_device() -> int:
	return int(load_data().get("cancel_device", 0))


## True when `event` is the ui_cancel a right click or the mouse's back button made.
static func is_mouse_cancel(event: InputEvent) -> bool:
	return event is InputEventAction and event.device == mouse_cancel_device() and event.is_action(&"ui_cancel")
