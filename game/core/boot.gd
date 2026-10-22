extends Node
## Boot scene. Until the title screen exists (M1 UI task) it shows the project name.
## Debug builds: F9 opens the battle sandbox (temporary, until the M1-ARC-02 debug overlay).

const DEBUG_SANDBOX_KEY := KEY_F9
const SANDBOX_SCENE := "res://game/battle/scene/battle_sandbox.tscn"

@onready var _label: Label = $Label


func _ready() -> void:
	_label.text = "%s\n%s" % [ProjectSettings.get_setting("application/config/name"), "bootstrap build"]


func _unhandled_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key != null and key.pressed and not key.echo and key.keycode == DEBUG_SANDBOX_KEY and OS.is_debug_build():
		get_viewport().set_input_as_handled()
		SceneRouter.change_scene(SANDBOX_SCENE)
