class_name SliceCutsceneShot
extends Node3D
## The slice's screenshot rig (M2-FP-109; the human's directive: every render is the PC's, from shots.json).
## A shot's setup.nodes "." sets these exports; one frame later the rig instances `level_path` as Level, sets
## `flags` on a fresh game state (and nothing else), places the party at `spawn`, and, when `scene_id` is set,
## plays that cutscene on the level's stage in real time with dialogue advancing by itself (option `choice` at
## every choice). The shot's settle_frames then pick the moment: at the capture's fixed 60 fps, frame N is N/60
## seconds into the scene. Autosaves are held; nothing is saved. The level's own camera is used (the stage
## director's in a cutscene), so the shot's camera stays "default".

## The level scene to stage (prologue.tscn, haluna.tscn, a GreyboxZone).
@export_file("*.tscn") var level_path: String = ""
## The cutscene to play on the level's stage; empty = just the level at `spawn` (a field view).
@export var scene_id: StringName = &""
## The spawn to place the party at first (place_at); empty = the level's own.
@export var spawn: StringName = &""
## Story flags set before the level is instanced (so its arrival logic sees them). A plain Array: a shot's
## setup sets it from JSON, and CaptureSetup won't put a JSON array into a PackedStringArray.
@export var flags: Array = []
## The option every choice takes.
@export var choice: int = 0
## A story method to run instead of `scene_id` (e.g. HalunaStory's `_night`: B11's night mood, cast and scene),
## on the level's `Story` node with its dialogue advancing by itself; its hand-off is recorded, never travelled.
@export var story_call: StringName = &""
## The line (its #line id) the scene stops on: once it shows, lines stop advancing, so the shot holds that line on
## its own camera whatever the frame count (a slower or faster capture can't land on the wrong line). Empty = run on.
@export var hold_line: StringName = &""

var level: Node3D
var sequencer: CutsceneSequencer


func _ready() -> void:
	start.call_deferred()  # after CaptureSetup has set the exports


## Stages the level and starts its scene (once). Deferred from _ready; tests, which never step a frame, call it.
func start() -> void:
	if level != null:
		return
	Game.state = GameStateData.new()
	for f: Variant in flags:
		Game.set_flag(StringName(str(f)))
	SaveSystem.hold_autosave(self)
	var packed := load(level_path) as PackedScene
	if packed == null:
		push_error("SliceCutsceneShot: cannot load %s" % level_path)
		return
	level = packed.instantiate() as Node3D
	if &"autoplay" in level:
		level.set(&"autoplay", false)
	level.name = "Level"
	add_child(level)
	if spawn != &"" and level.has_method(&"place_at"):
		level.call(&"place_at", spawn)
	if story_call != &"":
		var story := level.get_node_or_null(^"Story")
		if story != null and story.has_method(story_call):
			story.set(&"hand_off", func(_kind: StringName, _target: String) -> void: pass)
			sequencer = story.get(&"sequencer") as CutsceneSequencer
			sequencer.auto_advance = true
			_hold(sequencer)
			sequencer.auto_choice = choice
			story.call(story_call)
		return
	if scene_id == &"":
		return
	var stage := level.get(&"stage") as CutsceneStage
	sequencer = CutsceneSequencer.new()
	sequencer.name = "ShotSequencer"
	sequencer.auto_advance = true
	sequencer.auto_choice = choice
	_hold(sequencer)
	# Under the level, as a zone's own sequencer is: HeroFieldParty finds it there and hides the followers while
	# a held scene plays (B02 showed Asha at Neme's table, who is "at the market").
	level.add_child(sequencer)
	sequencer.play(scene_id, stage)


func _hold(seq: CutsceneSequencer) -> void:
	if hold_line != &"":
		seq.line_shown.connect(_on_line_shown)


func _on_line_shown(step: DialogueStep) -> void:
	if step.line_id == hold_line:
		sequencer.auto_advance = false


func _exit_tree() -> void:
	SaveSystem.release_autosave(self)
