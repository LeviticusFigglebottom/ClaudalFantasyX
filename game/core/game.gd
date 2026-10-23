extends Node
## Autoload "Game": owns the live GameStateData, the flag registry, the play-time clock and the
## chapter counter.
##
## Play time (M1-ARC-03): `state.play_time_sec` grows by each frame's delta while the clock runs.
## Game processes with PROCESS_MODE_ALWAYS, so menus that pause the tree still count, as players
## expect. All logic is in advance_play_time(delta), which tests drive directly: the same
## deltas always give the same total. A single step is clamped to [0, PLAY_TIME_MAX_STEP_SEC],
## so a debugger break or a dragged window cannot add minutes at once. The title screen calls
## stop_play_clock(); new_game() and SaveSystem.load_into_game() start it again.

const FLAGS_PATH := "res://game/data/flags.tres"
## The largest single frame step counted towards play time, in seconds.
const PLAY_TIME_MAX_STEP_SEC := 1.0

var state: GameStateData = GameStateData.new()
var registry: FlagRegistry
var play_clock_running := true


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	registry = load(FLAGS_PATH) as FlagRegistry
	if registry == null:
		push_error("Game: failed to load flag registry at %s" % FLAGS_PATH)
		registry = FlagRegistry.new()


func _process(delta: float) -> void:
	advance_play_time(delta)


func get_flag(flag: StringName, default: Variant = false) -> Variant:
	_check_declared(flag)
	return state.flags.get(String(flag), default)


func set_flag(flag: StringName, value: Variant = true) -> void:
	_check_declared(flag)
	state.flags[String(flag)] = value
	EventBus.flag_changed.emit(flag, value)


func new_game() -> void:
	state = GameStateData.new()
	start_play_clock()


## Moves the story to `chapter`. Emits EventBus.chapter_changed (which triggers the slot-0
## autosave) only when the chapter actually changes. Returns true when it changed.
func set_chapter(chapter: int) -> bool:
	var previous := state.chapter
	if chapter == previous:
		return false
	state.chapter = chapter
	EventBus.chapter_changed.emit(chapter, previous)
	return true


# --- Play time ---------------------------------------------------------------------------------


## Adds one frame step to the play time when the clock runs. Returns the seconds counted.
func advance_play_time(delta: float) -> float:
	if not play_clock_running:
		return 0.0
	var step := clampf(delta, 0.0, PLAY_TIME_MAX_STEP_SEC)
	state.play_time_sec += step
	return step


func start_play_clock() -> void:
	play_clock_running = true


func stop_play_clock() -> void:
	play_clock_running = false


func play_time_sec() -> float:
	return state.play_time_sec


func _check_declared(flag: StringName) -> void:
	if not registry.is_declared(flag):
		push_error("Undeclared story flag '%s' (declare it in %s)" % [flag, FLAGS_PATH])
