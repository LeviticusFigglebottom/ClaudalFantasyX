class_name TipCardShot
extends Node3D
## Capture driver for the first-time tip card (M2-UI-24, tests/screenshots/shots.json
## `field_tip_card`): Haluna's mood scene (its H02 camera) with the objective tip held in, on a
## scratch flag set (Asha has joined), so the player's save never moves a baseline.

const MOOD_SCENE := "res://game/levels/_tests/haluna_mood/haluna_mood.tscn"

var card: TipCard
var flags: Dictionary = {&"ch02_met_asha": true}


func _ready() -> void:
	var mood := (load(MOOD_SCENE) as PackedScene).instantiate()
	mood.name = &"Haluna"
	add_child(mood)
	UiSettings.set_shared(UiSettings.new())
	FieldInput.ensure_actions()
	ObjectiveHud.ensure_action()
	InputNames.using_pad = false
	var layer := CanvasLayer.new()
	add_child(layer)
	var theme_root := Control.new()
	theme_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	theme_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	theme_root.theme = load("res://game/ui/theme/hymn_theme.tres") as Theme
	layer.add_child(theme_root)
	card = TipCard.new()
	card.tips = TutorialTips.new(
		func(f: StringName) -> bool: return bool(flags.get(f, false)),
		func(f: StringName) -> void: flags[f] = true,
		func() -> bool: return true
	)
	theme_root.add_child(card)
	card.advance(0.0)
	card.advance(float(TutorialTips.load_data()["fade_sec"]))  # held in
	card.set_process(false)
	card.set_process_input(false)
