class_name ObjectiveShot
extends Node3D
## Capture driver for the objective line and the destination cue (M2-UI-17/19,
## tests/screenshots/shots.json `field_objective_line`): Haluna's mood scene (its H02 camera, down
## Tidewall lane) with the objective line held in and the cue pointing at its target, on a scratch
## flag set (Neme's table done: "find the save shrine"), so the player's save never moves a baseline.

const MOOD_SCENE := "res://game/levels/_tests/haluna_mood/haluna_mood.tscn"
const ZONE := &"ch02/haluna"
const FLAGS: Array[StringName] = [&"ch02_met_asha", &"ch02_tideline_won", &"ch02_ate_at_nemes"]

var hud: ObjectiveHud


func _ready() -> void:
	var mood := (load(MOOD_SCENE) as PackedScene).instantiate()
	mood.name = &"Haluna"
	add_child(mood)
	UiSettings.set_shared(UiSettings.new())
	var layer := CanvasLayer.new()
	add_child(layer)
	var theme_root := Control.new()
	theme_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	theme_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	theme_root.theme = load("res://game/ui/theme/hymn_theme.tres") as Theme
	layer.add_child(theme_root)
	hud = ObjectiveHud.new()
	hud.tracker = ObjectiveTracker.new(func(f: StringName) -> bool: return FLAGS.has(f))
	hud.zone = ZONE
	theme_root.add_child(hud)
	hud.show_now()
	hud.advance(float(ObjectiveHud.load_data()["in_sec"]))  # held in, no slide in the capture
