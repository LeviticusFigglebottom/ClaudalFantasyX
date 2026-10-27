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
## Story flags set before the level is instanced (so its arrival logic sees them).
@export var flags: PackedStringArray = PackedStringArray()
## The option every choice takes.
@export var choice: int = 0

var level: Node3D
var sequencer: CutsceneSequencer


func _ready() -> void:
	_start.call_deferred()


func _start() -> void:
	Game.state = GameStateData.new()
	for f: String in flags:
		Game.set_flag(StringName(f))
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
	if scene_id == &"":
		return
	var stage := level.get(&"stage") as CutsceneStage
	sequencer = CutsceneSequencer.new()
	sequencer.name = "ShotSequencer"
	sequencer.auto_advance = true
	sequencer.auto_choice = choice
	add_child(sequencer)
	sequencer.play(scene_id, stage)


func _exit_tree() -> void:
	SaveSystem.release_autosave(self)
