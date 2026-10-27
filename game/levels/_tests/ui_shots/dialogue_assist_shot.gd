class_name DialogueAssistShot
extends Node3D
## Capture driver for the dialogue assist (M2-UI-25, tests/screenshots/shots.json): Haluna's mood
## scene (its H02 camera, down Tidewall lane) under a letterboxed cutscene overlay.
##   - "continue" (`dialogue_continue`): Rhen's line fully shown, the continue glyph waiting;
##   - "backlog" (`dialogue_backlog`): the first beach lines said, then the Backlog page open over
##     the box (not pausing the tree, so the capture's frames still run);
##   - "voice_over" (`dialogue_voice_over`): the prologue's narrated line, drawn as a subtitle (M2-UI-100).

const MOOD_SCENE := "res://game/levels/_tests/haluna_mood/haluna_mood.tscn"
const SEQUENCER_CONFIG := "res://game/data/cutscene/sequencer.json"
## [speaker, line key] of the beach scene's opening (ch02_girl_on_the_beach.dlg); &"" = narration.
const BEACH := [
	[&"", &"DLG_CH02_BEACH_001"],
	[&"asha", &"DLG_CH02_BEACH_002"],
	[&"toma", &"DLG_CH02_BEACH_003"],
	[&"rhen", &"DLG_CH02_BEACH_004"],
	[&"asha", &"DLG_CH02_BEACH_005"],
	[&"toma", &"DLG_CH02_BEACH_017"],
	[&"asha", &"DLG_CH02_BEACH_006"],
	[&"asha", &"DLG_CH02_BEACH_007"],
]
const CONTINUE_LINE := 3
## The prologue's narrated line (prologue_dead_city.dlg, Narrator(rhen) ... #vo).
const VOICE_OVER_KEY := &"DLG_PROLOGUE_DEAD_CITY_001"
const VOICE_OVER_NARRATOR := &"rhen"

## Which view to stage: &"continue", &"backlog" or &"voice_over".
@export var view: StringName = &"continue"

var overlay: CutsceneOverlay


func _ready() -> void:
	var mood := (load(MOOD_SCENE) as PackedScene).instantiate()
	mood.name = &"Haluna"
	add_child(mood)
	UiSettings.set_shared(UiSettings.new())
	DialogueBacklog.forget()
	var cfg: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SEQUENCER_CONFIG))
	overlay = CutsceneOverlay.new(cfg)
	add_child(overlay)
	overlay.set_letterbox(1.0)
	var box := overlay.box
	box.visible = true
	if view == &"continue":
		_say(box, BEACH[CONTINUE_LINE])
		return
	if view == &"voice_over":
		box.show_text(&"", VOICE_OVER_KEY, &"", false, VOICE_OVER_NARRATOR, true)
		box.skip_reveal()
		return
	for line: Array in BEACH:
		_say(box, line)
	var assist := box.get_node(^"DialogueAssist") as DialogueAssist
	assist.pause_backlog = false
	assist.open_backlog()


func _say(box: DialogueBox, line: Array) -> void:
	box.show_text(line[0] as StringName, line[1] as StringName)
	box.skip_reveal()
