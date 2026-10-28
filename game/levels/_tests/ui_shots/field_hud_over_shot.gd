class_name FieldHudOverShot
extends Node3D
## Capture driver for the field HUD legibility shots (Lead 2026-10-28, tests/screenshots/shots.json
## `field_hud_over_*`): one dressed Act I area (bright sand, open water, night) with all four field
## overlays held in at once: the objective line, the area title card, the interaction prompt over a
## scratch interactable a few steps ahead, and the first-time tip card. Flags are a scratch set, so
## the player's save never moves a baseline. Each .tscn sets the backdrop, its location and flags.

## The dressed area's preview scene; it is added as `Backdrop`, so the shot's camera is
## `Backdrop/<its camera path>`.
@export_file("*.tscn") var backdrop := ""
## The locations.json id: the title card's name and the objective line's zone.
@export var location: StringName = &""
## Scratch story flags that pick the objective line.
@export var flags: Array[StringName] = []
## Where the scratch interactable stands, in the camera's frame (metres: right, up, ahead): left of
## centre, so its plate does not cover the destination cue over Haluna's lane or Corrow's strand.
@export var spot := Vector3(-2.4, -1.5, 9.0)

var objective: ObjectiveHud
var title: AreaTitleCard
var prompt: InteractPrompt
var tip: TipCard
var it: Interactable
var _seen: Dictionary = {}


func _ready() -> void:
	var scene := (load(backdrop) as PackedScene).instantiate()
	scene.name = &"Backdrop"
	add_child(scene)
	UiSettings.set_shared(UiSettings.new())
	FieldInput.ensure_actions()
	ObjectiveHud.ensure_action()
	InputNames.using_pad = false
	AreaTitleCard.forget()
	it = Interactable.new()
	it.name = &"Listen"
	it.prompt_key = "FIELD_PROMPT_LISTEN"
	add_child(it)
	var theme_root := _layer()
	objective = ObjectiveHud.new()
	objective.tracker = ObjectiveTracker.new(func(f: StringName) -> bool: return flags.has(f))
	objective.zone = location
	theme_root.add_child(objective)
	objective.show_now()
	objective.advance(float(ObjectiveHud.load_data()["in_sec"]))  # held in
	title = AreaTitleCard.new()
	title.location = location
	theme_root.add_child(title)
	title.advance(0.0)
	title.advance(float(AreaTitleCard.load_data()["in_sec"]))  # held in
	title.set_process(false)
	prompt = InteractPrompt.new()
	prompt.pick = func() -> Interactable: return it
	theme_root.add_child(prompt)
	tip = TipCard.new()
	_seen[&"ch02_met_asha"] = true  # raises the objective tip, the first one a player meets
	tip.tips = TutorialTips.new(
		func(f: StringName) -> bool: return bool(_seen.get(f, false)),
		func(f: StringName) -> void: _seen[f] = true,
		func() -> bool: return true
	)
	theme_root.add_child(tip)
	tip.advance(0.0)
	tip.advance(float(TutorialTips.load_data()["fade_sec"]))  # held in
	tip.set_process(false)
	tip.set_process_input(false)


func _process(_delta: float) -> void:
	var cam := get_viewport().get_camera_3d()
	if cam != null:
		var b := cam.global_transform.basis
		it.global_position = cam.global_position + b.x * spot.x + Vector3.UP * spot.y - b.z * spot.z


func _layer() -> Control:
	var layer := CanvasLayer.new()
	add_child(layer)
	var theme_root := Control.new()
	theme_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	theme_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	theme_root.theme = load("res://game/ui/theme/hymn_theme.tres") as Theme
	layer.add_child(theme_root)
	return theme_root
