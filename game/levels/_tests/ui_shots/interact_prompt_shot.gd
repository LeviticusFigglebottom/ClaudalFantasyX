class_name InteractPromptShot
extends Node3D
## Capture driver for the interaction prompt (M2-UI-20, tests/screenshots/shots.json
## `field_interact_prompt`): Haluna's mood scene (its H02 camera, down Tidewall lane) with a scratch
## "Listen" interactable a few steps ahead on the lane and the prompt faded in over it.

const MOOD_SCENE := "res://game/levels/_tests/haluna_mood/haluna_mood.tscn"
## Where the scratch interactable stands, in the camera's frame (metres: right, up, ahead).
const SPOT := Vector3(0.6, -1.5, 9.0)

var prompt: InteractPrompt
var it: Interactable


func _ready() -> void:
	var mood := (load(MOOD_SCENE) as PackedScene).instantiate()
	mood.name = &"Haluna"
	add_child(mood)
	UiSettings.set_shared(UiSettings.new())
	FieldInput.ensure_actions()
	it = Interactable.new()
	it.name = &"Listen"
	it.prompt_key = "FIELD_PROMPT_LISTEN"
	add_child(it)
	var layer := CanvasLayer.new()
	add_child(layer)
	var theme_root := Control.new()
	theme_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	theme_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	theme_root.theme = load("res://game/ui/theme/hymn_theme.tres") as Theme
	layer.add_child(theme_root)
	prompt = InteractPrompt.new()
	prompt.pick = func() -> Interactable: return it
	theme_root.add_child(prompt)


func _process(_delta: float) -> void:
	var cam := get_viewport().get_camera_3d()
	if cam != null:
		var b := cam.global_transform.basis
		it.global_position = cam.global_position + b.x * SPOT.x + Vector3.UP * SPOT.y - b.z * SPOT.z
