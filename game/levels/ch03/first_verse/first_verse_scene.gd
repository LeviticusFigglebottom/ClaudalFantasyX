class_name FirstVerseScene
extends Node3D
## Ch3 Cutscene B, "The First Verse", on a placeholder Shell Shrine set (M2-FP-04): CSG stone, the
## outer steps, the chamber with its pool, and the Drownbell's hood offshore, at sunset. The shots
## follow haluna.md §5 (S06–S10, C08) as closely as primitives allow.
##
## The cutscene ends on `<<event start_battle drownbell>>`: that opens the Drownbell (M2-FP-06)
## through BattleRequest with the party, victory flag and following scene of first_playable.json
## "first_verse" (the end card). A script with no start_battle event goes straight to that scene.
##
## No player: the camera director runs without one (M1-ARC-09), and Rhen is an actor here.
## `place_at` makes the scene a valid location for LocationRegistry should it ever get a row.

const SCENE_ID := &"ch03_the_first_verse"
const EVENT_START_BATTLE := &"start_battle"

## Off in tests: they call run() with an instant sequencer.
@export var autoplay := true

var sequencer: CutsceneSequencer
## Tests record the scene change here instead of swapping scenes.
var change_scene := Callable()
## Tests record the battle request here instead of submitting it (BattleRequest.submit).
var start_battle := Callable()

@onready var stage: CutsceneStage = $CutsceneStage


func _ready() -> void:
	sequencer = CutsceneSequencer.new()
	sequencer.name = "Sequencer"
	add_child(sequencer)
	if autoplay:
		run.call_deferred()


## Plays the cutscene, then the fight it calls, or the following scene. The screen stays black from
## the scene's last fade into whichever comes next.
func run() -> void:
	sequencer.restore_fade = false
	await sequencer.play(SCENE_ID, stage)
	if not is_inside_tree() and not change_scene.is_valid():
		return
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_FIRST_VERSE)
	var after := str(cfg.get("after_scene", ""))
	for e: Dictionary in sequencer.events:
		if e["name"] == EVENT_START_BATTLE:
			_battle(StringName(str((e["args"] as Array)[0])), cfg, after)
			return
	if change_scene.is_valid():
		change_scene.call(after)
	else:
		SceneRouter.change_scene(after)


func place_at(_spawn: StringName, _yaw_deg: float = 0.0) -> bool:
	return true


func _battle(encounter: StringName, cfg: Dictionary, after: String) -> void:
	var r := BattleRequest.make(encounter, &"", &"", StringName(str(cfg.get("victory_flag", ""))))
	r.active = FirstPlayableConfig.ids(cfg.get("battle_active", []))
	r.reserve = FirstPlayableConfig.ids(cfg.get("battle_reserve", []))
	r.return_scene = after
	if start_battle.is_valid():
		start_battle.call(r)
	else:
		BattleRequest.submit(r)
