class_name CutsceneSequencer
extends Node
## Plays a compiled `.dlg` scene on a CutsceneStage (M2-FP-01; docs/kb/tech/cutscenes.md).
## API STUB: the public surface below is the contract other streams build against; the body is
## filled in by M2-FP-01. Until then play() runs the script's flow (flags, branches, events) with
## no presentation and picks option `auto_choice`.
##
## Usage:
##   var seq := CutsceneSequencer.new()
##   add_child(seq)
##   await seq.play(&"ch02_girl_on_the_beach", stage)
##   # act on the <<event>>s it reported (seq.events, or the event_requested signal) afterwards
##
## <<event start_battle x>> and <<event zone_unlock x>> are reported, never acted on here: the host
## (zone or flow code) decides what they mean once play() returns.

signal finished(scene_id: StringName)
signal event_requested(event_name: StringName, args: Array)

## Tests and captures: no waits, no typewriter, lines advance by themselves.
var instant := false
## The option index chosen when `instant` (or in the stub).
var auto_choice := 0
## Every <<event>> of the last play(), in order: [{"name": StringName, "args": Array}].
var events: Array[Dictionary] = []

var _playing := false


func is_playing() -> bool:
	return _playing


## Plays `scene_id` (a compiled scene under game/data/dialogue/compiled/) to its end on `stage`.
## Returns false when the scene could not be loaded. Await it.
func play(scene_id: StringName, _stage: CutsceneStage) -> bool:
	var runner := DialogueRunner.new()
	if not runner.load_scene(scene_id) or not runner.start():
		return false
	_playing = true
	events.clear()
	runner.event_triggered.connect(_on_event)
	var step := runner.next()
	while not step.is_end():
		if step.is_options():
			runner.choose(step.options[mini(auto_choice, step.options.size() - 1)].index)
		elif step.is_music_wait():
			runner.release_wait()
		step = runner.next()
	_playing = false
	finished.emit(scene_id)
	return true


func _on_event(event_name: StringName, args: Array) -> void:
	events.append({"name": event_name, "args": args})
	event_requested.emit(event_name, args)
