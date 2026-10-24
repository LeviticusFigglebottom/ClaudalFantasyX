class_name MemoryReplay
extends Node
## The Memories gallery's replay host (M3-MNU-02, SPEC §6.11): the scene the gallery changes to
## (memory_replay.tscn, through FlowRouting.change_scene as the title's other choices do). It plays
## one memory of game/data/memories/memories.json and goes back to the title with the gallery open
## on that memory.
##
## The run (run(), started on _ready when `autostart`):
##   1. The record. Game.state becomes a copy of the record that remembers the memory
##      (MemoriesModel.record_for), with the memory's `replay_flags` set on the copy: the zone is
##      built and the scene plays on the flags that player saw. The real Game.state comes back at
##      the end, untouched.
##   2. The stage. Its scene is loaded and instanced off the main thread (as SceneRouter does) while
##      the router's fade stays opaque (SceneRouter.hold_reveal), then ReplayStage.prepare() turns
##      its story autostarts off and removes its field encounters, before it enters the tree.
##   3. The staging: `spawn` places the player, `night` gives the zone first_playable.json haluna's
##      night (set_night and place_cast, as HalunaStory._night).
##   4. The scene: this node's own CutsceneSequencer with `replay` on (flags read live, <<set>>s
##      kept inside the replay, <<event>>s recorded in `sequencer.events` but never emitted). Holding
##      Cancel is the sequencer's own skip, which runs the scene to its end (it still stops for a
##      choice, which the player makes again).
##   5. The end: the screen goes black, the stage is freed, Game.state is put back, an autosave the
##      stage asked for while it stood is dropped, and the title opens with the gallery on this
##      memory (take_gallery_request, last_memory).
## The autosave is held from _ready to the end (the sequencer also holds it while it plays).
## Tests set `threaded` false and `sequencer.instant` true and call run() themselves: the whole run
## is then synchronous. They set FlowRouting.record to catch the change back to the title.

signal ended(memory_id: StringName, played: bool)

const SCENE_PATH := "res://game/ui/menus/memories/memory_replay.tscn"
const TITLE_SCENE := "res://game/core/boot.tscn"

## The memory the next replay plays (set by start()).
static var pending: StringName = &""
## The memory replayed last (the gallery opens on it).
static var last_memory: StringName = &""
static var _gallery_requested := false

## Run on _ready (the game). Tests turn it off and call run().
@export var autostart := true
## Load and instance the stage off the main thread. Tests turn it off.
@export var threaded := true

var memory_id: StringName = &""
var model: MemoriesModel
var sequencer: CutsceneSequencer
## The stage scene's instance while it stands.
var zone: Node
var return_scene := TITLE_SCENE
## True once the scene has played to its end (false when it was cut short or could not start).
var played := false

var _saved_state: GameStateData
var _swapped := false
var _autosave_was_pending := false
var _started := false
var _ended := false
var _made: Node


## Changes to the replay scene for memory `id`.
static func start(id: StringName) -> void:
	pending = id
	FlowRouting.change_scene(SCENE_PATH)


## True once, after a replay has ended: the title opens the gallery (on last_memory).
static func take_gallery_request() -> bool:
	var asked := _gallery_requested
	_gallery_requested = false
	return asked


func _ready() -> void:
	if memory_id == &"":
		memory_id = pending
	pending = &""
	if model == null:
		model = MemoriesModel.from_game()
	sequencer = CutsceneSequencer.new()
	sequencer.name = "Sequencer"
	sequencer.replay = true
	sequencer.restore_fade = false  # the end stays black into the title
	add_child(sequencer)
	Game.stop_play_clock()
	SaveSystem.hold_autosave(self)
	_autosave_was_pending = SaveSystem.has_pending_autosave()
	if autostart:
		SceneRouter.hold_reveal(self)
		run.call_deferred()


func _exit_tree() -> void:
	_restore()


func is_ended() -> bool:
	return _ended


## Plays the memory and returns to the title. Returns true when the scene played to its end. Await
## it (synchronous with `threaded` off and an instant sequencer).
func run() -> bool:
	if _started:
		return false
	_started = true
	var mem := model.memory(memory_id)
	var record := model.record_for(memory_id)
	if mem.is_empty() or record == null:
		push_warning("MemoryReplay: '%s' is not a remembered memory" % memory_id)
		_end(false)
		return false
	_enter_record(record, mem.get("replay_flags", {}) as Dictionary)
	var packed: PackedScene = await _load(str(mem.get("stage", "")))
	if packed == null or _ended:
		_end(false)
		return false
	zone = await _instance(packed)
	if zone == null or _ended:
		_end(false)
		return false
	ReplayStage.prepare(zone)
	add_child(zone)
	var stage := stage_of(zone, mem)
	_stage_memory(mem)
	if stage != null and stage.player() != null:
		stage.player().accepts_input = false  # the sequencer gives back what it found: still nothing
	SceneRouter.release_reveal(self)
	var through: bool = await sequencer.play(StringName(str(mem.get("scene", ""))), stage)
	_end(through)
	return through


## The memory's CutsceneStage: its `stage_node` path, else the root's `stage` property.
static func stage_of(root: Node, mem: Dictionary) -> CutsceneStage:
	var path := str(mem.get("stage_node", ""))
	if path != "":
		return root.get_node_or_null(NodePath(path)) as CutsceneStage
	return root.get(&"stage") as CutsceneStage if &"stage" in root else null


## Ends the replay now (black, the stage gone, back to the title). Safe to call twice.
func end() -> void:
	_end(false)


func _enter_record(record: GameStateData, replay_flags: Dictionary) -> void:
	_saved_state = Game.state
	Game.state = GameStateData.from_dict(record.to_dict())
	_swapped = true
	for f: String in replay_flags:
		Game.set_flag(StringName(f), replay_flags[f])


func _stage_memory(mem: Dictionary) -> void:
	var spawn := StringName(str(mem.get("spawn", "")))
	if spawn != &"" and zone.has_method(&"place_at"):
		var yaw: Variant = zone.call(&"spawn_yaw_deg", spawn) if zone.has_method(&"spawn_yaw_deg") else 0.0
		zone.call(&"place_at", spawn, yaw)
	if bool(mem.get("night", false)) and zone.has_method(&"set_night"):
		var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_HALUNA)
		zone.call(&"set_night", cfg.get("night", {}), cfg.get("night_hide", []))
		if zone.has_method(&"place_cast"):
			zone.call(&"place_cast", cfg.get("night_cast", {}), cfg.get("night_marks", {}))


func _load(path: String) -> PackedScene:
	if not threaded:
		return load(path) as PackedScene
	if ResourceLoader.load_threaded_request(path) != OK:
		return null
	while ResourceLoader.load_threaded_get_status(path) == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
		await get_tree().process_frame
	return ResourceLoader.load_threaded_get(path) as PackedScene


## Instances `packed` on a WorkerThreadPool thread (a zone dresses itself there, as under the
## router), the main thread waiting a frame at a time.
func _instance(packed: PackedScene) -> Node:
	if not threaded:
		return packed.instantiate()
	_made = null
	var task := WorkerThreadPool.add_task(func() -> void: _made = packed.instantiate())
	while not WorkerThreadPool.is_task_completed(task):
		await get_tree().process_frame
	WorkerThreadPool.wait_for_task_completion(task)
	return _made


func _end(through: bool) -> void:
	if _ended:
		return
	_ended = true
	played = through
	if sequencer != null and sequencer.is_playing():
		remove_child(sequencer)  # a sequencer leaving the tree cuts its scene short (play() returns false)
		sequencer.queue_free()
	elif sequencer != null and sequencer.overlay != null:
		sequencer.overlay.set_fade(1.0)
	if zone != null and is_instance_valid(zone):
		if zone.get_parent() == self:
			remove_child(zone)
		zone.free()
	zone = null
	_restore()
	last_memory = memory_id
	_gallery_requested = true
	ended.emit(memory_id, through)
	FlowRouting.change_scene(return_scene)


## Puts the real Game.state back and lets the autosave and the router go (once).
func _restore() -> void:
	if _swapped:
		Game.state = _saved_state
		_swapped = false
	if not _autosave_was_pending and SaveSystem.has_pending_autosave():
		SaveSystem.cancel_pending_autosave()
	SaveSystem.release_autosave(self)
	SceneRouter.release_reveal(self)
