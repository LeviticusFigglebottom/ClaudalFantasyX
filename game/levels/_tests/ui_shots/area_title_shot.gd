class_name AreaTitleShot
extends Node3D
## Capture driver for the area title card (M2-UI-21, tests/screenshots/shots.json `field_area_title`):
## Haluna's mood scene (its H02 camera, down Tidewall lane) with Haluna's card held in.

const MOOD_SCENE := "res://game/levels/_tests/haluna_mood/haluna_mood.tscn"

var card: AreaTitleCard


func _ready() -> void:
	var mood := (load(MOOD_SCENE) as PackedScene).instantiate()
	mood.name = &"Haluna"
	add_child(mood)
	UiSettings.set_shared(UiSettings.new())
	AreaTitleCard.forget()
	var layer := CanvasLayer.new()
	add_child(layer)
	var theme_root := Control.new()
	theme_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	theme_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	theme_root.theme = load("res://game/ui/theme/hymn_theme.tres") as Theme
	layer.add_child(theme_root)
	card = AreaTitleCard.new()
	card.location = &"ch02/haluna"
	theme_root.add_child(card)
	card.advance(0.0)
	card.advance(float(AreaTitleCard.load_data()["in_sec"]))  # held in
	card.set_process(false)  # stays held for the capture
