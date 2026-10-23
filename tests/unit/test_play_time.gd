extends TestCase
## M1-ARC-03: play time is tracked by Game, deterministically (same deltas, same total).

const FRAME := 1.0 / 60.0
const FRAMES_PER_10_SEC := 600

var _saved_state: GameStateData
var _saved_running := true


func before_each() -> void:
	_saved_state = Game.state
	_saved_running = Game.play_clock_running
	Game.state = GameStateData.new()
	Game.start_play_clock()


func test_advance_accumulates_the_same_total_every_run() -> void:
	for i in FRAMES_PER_10_SEC:
		Game.advance_play_time(FRAME)
	var first := Game.play_time_sec()
	assert_between(first, 10.0 - 1e-6, 10.0 + 1e-6, "600 frames of 1/60 s")
	Game.state = GameStateData.new()
	for i in FRAMES_PER_10_SEC:
		Game.advance_play_time(FRAME)
	assert_eq(Game.play_time_sec(), first, "bit-identical on a second run")
	_done()


func test_stopped_clock_does_not_count() -> void:
	Game.advance_play_time(2.0 * FRAME)
	Game.stop_play_clock()
	assert_eq(Game.advance_play_time(0.5), 0.0)
	assert_between(Game.play_time_sec(), 2.0 * FRAME - 1e-9, 2.0 * FRAME + 1e-9)
	Game.start_play_clock()
	Game.advance_play_time(0.5)
	assert_between(Game.play_time_sec(), 0.5 + 2.0 * FRAME - 1e-9, 0.5 + 2.0 * FRAME + 1e-9)
	_done()


func test_negative_and_huge_steps_are_clamped() -> void:
	assert_eq(Game.advance_play_time(-3.0), 0.0, "time never runs backwards")
	assert_eq(Game.advance_play_time(120.0), Game.PLAY_TIME_MAX_STEP_SEC, "a hitch counts one max step")
	assert_eq(Game.play_time_sec(), Game.PLAY_TIME_MAX_STEP_SEC)
	_done()


func test_new_game_resets_and_starts_the_clock() -> void:
	Game.advance_play_time(0.5)
	Game.stop_play_clock()
	Game.new_game()
	assert_eq(Game.play_time_sec(), 0.0)
	assert_true(Game.play_clock_running)
	_done()


func test_game_counts_while_the_tree_is_paused() -> void:
	assert_eq(Game.process_mode, Node.PROCESS_MODE_ALWAYS, "menus pause the tree but play time runs")
	_done()


func test_play_time_round_trips_through_a_save() -> void:
	Game.advance_play_time(0.75)
	Game.state.play_time_sec += 3600.0
	var saves: Node = (load("res://game/core/save_system.gd") as GDScript).new()
	var back: GameStateData = saves.deserialize(JSON.parse_string(JSON.stringify(saves.serialize(Game.state))))
	assert_eq(back.play_time_sec, 3600.75)
	saves.free()
	_done()


func test_play_time_text_is_hours_minutes_seconds() -> void:
	var info := SaveSlotInfo.new()
	assert_eq(info.format_play_time(0.0), "0:00:00")
	assert_eq(info.format_play_time(59.99), "0:00:59", "seconds are floored")
	assert_eq(info.format_play_time(3725.5), "1:02:05")
	assert_eq(info.format_play_time(-4.0), "0:00:00")
	assert_eq(info.format_play_time(1.0e9), "999:59:59", "capped")
	_done()


func _done() -> void:
	Game.state = _saved_state
	Game.play_clock_running = _saved_running
