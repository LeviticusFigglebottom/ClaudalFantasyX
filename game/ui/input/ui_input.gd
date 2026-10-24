extends Node
## The UiInput autoload (M2-UI-26, ADR 0036): input every screen shares, so keyboard, mouse and
## controller work the same everywhere without each screen re-implementing it.
## - **Mouse cancel:** a right click or the mouse's back button becomes a `ui_cancel` press (and
##   release), delivered through the normal input path, so every screen that backs out on Cancel
##   also backs out on them, including over a menu whose controls stop the click.
## - **Pad defaults everywhere:** ControlsModel.defaults() runs here, at startup, so pad A and B
##   confirm and cancel (controls.json pad_defaults) in every scene, not only after boot.tscn.
## - **Last device:** remembers whether the pad or the keyboard and mouse was used last
##   (InputNames.using_pad), so key glyphs and prompts switch with the player's hands.
## Data: game/data/ui/ui_input.json.

## Emitted when the last device used changes (true: the pad).
signal device_changed(pad: bool)

const DATA_PATH := "res://game/data/ui/ui_input.json"

var _d: Dictionary = {}
var _cancel_buttons: Array[int] = []


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS  # menus pause the tree
	_d = load_data()
	for b: Variant in _d.get("cancel_mouse_buttons", []):
		_cancel_buttons.append(int(b))
	ControlsModel.defaults()  # the pad's Confirm and Cancel buttons, before any scene asks


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
	if is_cancel_click(event):
		get_viewport().set_input_as_handled()
		send_cancel(get_viewport())


## True for a mouse button press (or its release) that stands for Cancel.
func is_cancel_click(event: InputEvent) -> bool:
	var mb := event as InputEventMouseButton
	return mb != null and _cancel_buttons.has(int(mb.button_index)) and mb.pressed


## Delivers a ui_cancel press and release to `vp` (the press first, so is_action_pressed sees it).
static func send_cancel(vp: Viewport) -> void:
	for down in [true, false]:
		var a := InputEventAction.new()
		a.action = &"ui_cancel"
		a.pressed = down
		vp.push_input(a)
