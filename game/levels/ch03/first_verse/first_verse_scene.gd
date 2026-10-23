class_name FirstVerseScene
extends Node3D
## Ch3 Cutscene B, "The First Verse", on a placeholder Shell Shrine set (M2-FP-04): CSG stone, the
## outer steps, the chamber with its pool, and the Drownbell's hood offshore, at sunset. The shots
## follow haluna.md §5 (S06–S10, C08) as closely as primitives allow. It is the last scene of the
## first playable: when the cutscene ends (its closing `<<event start_battle drownbell>>` names a
## fight that is not built yet) the end card follows.
##
## No player: the camera director runs without one (M1-ARC-09), and Rhen is an actor here.
## `place_at` makes the scene a valid location for LocationRegistry should it ever get a row.

const SCENE_ID := &"ch03_the_first_verse"
const END_CARD_SCENE := "res://game/flow/end_card.tscn"

## Off in tests: they call run() with an instant sequencer.
@export var autoplay := true

var sequencer: CutsceneSequencer
## Tests record the scene change here instead of swapping scenes.
var change_scene := Callable()

@onready var stage: CutsceneStage = $CutsceneStage


func _ready() -> void:
	sequencer = CutsceneSequencer.new()
	sequencer.name = "Sequencer"
	add_child(sequencer)
	if autoplay:
		run.call_deferred()


## Plays the cutscene, then goes to the end card (still black: the scene ends on a fade out).
func run() -> void:
	sequencer.restore_fade = false
	await sequencer.play(SCENE_ID, stage)
	if not is_inside_tree() and not change_scene.is_valid():
		return
	if change_scene.is_valid():
		change_scene.call(END_CARD_SCENE)
	else:
		SceneRouter.change_scene(END_CARD_SCENE)


func place_at(_spawn: StringName, _yaw_deg: float = 0.0) -> bool:
	return true
