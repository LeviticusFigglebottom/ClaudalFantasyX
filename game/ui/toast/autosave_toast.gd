class_name AutosaveToast
extends CanvasLayer
## Tells the player when a chapter boundary was not autosaved (M1-UI-09, pillar 4). ADR 0018
## Amendment 1 skips the chapter autosave when slot 0 holds a journey further along than the live
## run, and reports it as EventBus.autosave_finished(reason, ERR_ALREADY_EXISTS). This layer shows a
## short, non-blocking notice for that error only: never for OK, never for ERR_UNAVAILABLE (autosave
## off) or any other result. While something holds the autosave (a cutscene sequencer, the camera
## director: SaveSystem.autosave_holders()), the notice waits and shows once the hold is released.
##
## boot.gd installs one under the tree root (AutosaveToast.install), where it survives scene changes.
## It ignores input (mouse_filter IGNORE everywhere) and keeps running while the tree is paused.
## Layout and timing: game/data/ui/toast.json. Text: loc key AUTOSAVE_SKIPPED_TOAST.

const DATA_PATH := "res://game/data/ui/toast.json"
const NODE_NAME := "AutosaveToast"
const TEXT_KEY := "AUTOSAVE_SKIPPED_TOAST"

## The SaveSystem whose holds delay the notice (null: the SaveSystem autoload).
var save_system: Node
## The EventBus to listen on (null: the EventBus autoload).
var event_bus: Node

var _d: Dictionary = {}
var _panel: Panel
var _label: Label
var _pending := false
var _age := -1.0


## Adds the toast layer under `root` once (not while `root` is setting up its children: boot.gd
## defers the call). Returns the existing one when already installed.
static func install(root: Node) -> AutosaveToast:
	var existing := root.get_node_or_null(NODE_NAME) as AutosaveToast
	if existing != null:
		return existing
	var toast := AutosaveToast.new()
	toast.name = NODE_NAME
	root.add_child(toast)
	return toast


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("toast")) != TYPE_DICTIONARY:
		push_error("AutosaveToast: could not read 'toast' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["toast"] as Dictionary


func _ready() -> void:
	_d = load_data()
	layer = int(_d.get("canvas_layer", 1))
	process_mode = Node.PROCESS_MODE_ALWAYS
	_build()
	var bus := event_bus if event_bus != null else _autoload(&"EventBus")
	if bus != null and not bus.is_connected(&"autosave_finished", _on_autosave_finished):
		bus.connect(&"autosave_finished", _on_autosave_finished)
	set_process(false)


## True while the notice is on screen (fading in, holding or fading out).
func is_showing() -> bool:
	return _age >= 0.0


## True while a notice waits for an autosave hold to be released.
func is_pending() -> bool:
	return _pending


## The notice's opacity now (0 when hidden).
func opacity() -> float:
	return _panel.modulate.a if _panel != null and _panel.visible else 0.0


## Steps the notice by `delta` seconds (what _process does each frame; tests call it directly).
func advance(delta: float) -> void:
	if _pending and not _held():
		_pending = false
		_show()
	if _age < 0.0:
		set_process(_pending)
		return
	_age += delta
	var m := _d.get("motion", {}) as Dictionary
	var fade_in := float(m.get("fade_in_sec", 0.0))
	var hold := float(m.get("hold_sec", 0.0))
	var fade_out := float(m.get("fade_out_sec", 0.0))
	if _age >= fade_in + hold + fade_out:
		_hide()
		return
	var a := 1.0
	if _age < fade_in:
		a = _age / fade_in
	elif _age > fade_in + hold:
		a = 1.0 - (_age - fade_in - hold) / fade_out
	_panel.modulate.a = clampf(a, 0.0, 1.0)


func _process(delta: float) -> void:
	advance(delta)


func _on_autosave_finished(_reason: StringName, error: int) -> void:
	if error != ERR_ALREADY_EXISTS:
		return
	if _held():
		_pending = true
		set_process(true)
		return
	_show()


func _show() -> void:
	_label.text = tr(TEXT_KEY)
	_panel.visible = true
	_panel.modulate.a = 0.0
	_age = 0.0
	set_process(true)


func _hide() -> void:
	_age = -1.0
	_panel.visible = false
	_panel.modulate.a = 0.0
	set_process(_pending)


func _held() -> bool:
	var saves := save_system if save_system != null else _autoload(&"SaveSystem")
	if saves == null or not saves.has_method(&"autosave_holders"):
		return false
	return not (saves.call(&"autosave_holders") as Array).is_empty()


func _build() -> void:
	var p := _d.get("panel", {}) as Dictionary
	_panel = Panel.new()
	var r: Array = p.get("rect", [0, 0, 0, 0])
	_panel.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_panel.position = Vector2(float(r[0]), float(r[1]))
	_panel.size = Vector2(float(r[2]), float(r[3]))
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.visible = false
	add_child(_panel)
	var pad := float(p.get("pad", 0.0))
	_label = Label.new()
	_label.theme_type_variation = &"BodyLabel"
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_label.position = Vector2(pad, pad)
	_label.size = _panel.size - Vector2(pad, pad) * 2.0
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.add_child(_label)


static func _autoload(autoload_name: StringName) -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.root.get_node_or_null(NodePath(String(autoload_name))) if tree != null else null
