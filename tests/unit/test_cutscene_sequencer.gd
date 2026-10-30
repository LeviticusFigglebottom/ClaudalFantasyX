extends TestCase
## M2-FP-01: CutsceneSequencer over the field test zone, with a CutsceneStage built in code.
## `instant` plays whole scenes synchronously; the real-time tests drive the director and the
## sequencer by hand with a fixed dt (director.auto_update off), so every await resumes inside
## a call made here.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const FIXTURE := &"test_cutscene_fixture"
const BEACH := &"ch02_girl_on_the_beach"
const DT := 1.0 / 30.0
const MAX_FRAMES := 3000
const SPOT := Vector3(2.0, 0.0, 6.0)

var zone: Node3D
var director: FieldCameraDirector
var player: FieldController
var stage: CutsceneStage
var seq: CutsceneSequencer
var asha: Node3D
var saved_state: GameStateData
var finished_ids: Array[StringName] = []
var lines_pending := 0
var lines_seen := 0
var play_result := false


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	director = zone.get_node("CameraDirector") as FieldCameraDirector
	player = zone.get_node("Player") as FieldController
	director.auto_update = false
	player.set_physics_process(false)
	zone.call("place_at", &"Lane")
	stage = _build_stage(true)
	seq = CutsceneSequencer.new()
	seq.set_process(false)
	zone.add_child(seq)
	seq.finished.connect(func(id: StringName) -> void: finished_ids.append(id))
	seq.line_shown.connect(_on_line)


func _on_line(_step: DialogueStep) -> void:
	lines_pending += 1
	lines_seen += 1


func _build_stage(with_close: bool) -> CutsceneStage:
	var s := CutsceneStage.new()
	s.name = "CutsceneStage"
	s.director_path = ^"../CameraDirector"
	s.player_path = ^"../Player"
	zone.add_child(s)
	var shots := Node.new()
	shots.name = "Shots"
	s.add_child(shots)
	_add_shot(shots, &"wide", Vector3(0, 6, 14), Vector3(0, 1, 0))
	if with_close:
		_add_shot(shots, &"close", Vector3(1, 1.6, 9), Vector3(0, 1.4, 6))
	var actors := Node3D.new()
	actors.name = "Actors"
	s.add_child(actors)
	asha = Node3D.new()
	asha.name = "asha"
	actors.add_child(asha)
	asha.global_position = Vector3(-2, 0, 8)
	var marks := Node3D.new()
	marks.name = "Marks"
	s.add_child(marks)
	var spot := Marker3D.new()
	spot.name = "spot"
	marks.add_child(spot)
	spot.global_position = SPOT
	return s


func _add_shot(folder: Node, id: StringName, pos: Vector3, aim: Vector3) -> void:
	var sn := CutsceneShotNode.new()
	sn.name = String(id)
	var shot := CameraShot.new()
	shot.id = id
	shot.position = pos
	shot.look_at = aim
	sn.shot = shot
	folder.add_child(sn)


# --- instant ---------------------------------------------------------------------------------


func test_instant_play_runs_every_cue_and_ends_clean() -> void:
	seq.instant = true
	var cues: Array[StringName] = []
	seq.cue_played.connect(func(c: StringName, _a: Array, _k: Dictionary) -> void: cues.append(c))
	_start(FIXTURE)
	assert_false(seq.is_playing(), "an instant play finishes synchronously")
	assert_eq(finished_ids, [FIXTURE] as Array[StringName])
	for c: StringName in [
		&"camera", &"fade", &"letterbox", &"mark", &"anim", &"face", &"wait", &"vfx", &"music", &"sfx"
	]:
		assert_true(c in cues, "cue @%s reached the sequencer" % c)
	assert_true(bool(Game.get_flag(&"test_flag")), "option 0 ran its body")
	assert_eq(seq.events.size(), 1)
	assert_eq(seq.events[0]["name"], &"fixture_event")
	assert_eq(seq.faces.size(), 1, "@face is recorded")
	assert_true(asha.global_position.distance_to(SPOT) < 0.01, "@mark moved asha onto the mark")
	var to_rhen := player.global_position - asha.global_position
	assert_between(angle_difference(asha.rotation.y, atan2(-to_rhen.x, -to_rhen.z)), -0.01, 0.01, "look_at rhen")
	assert_eq(stage.get_node("Marks/spot").get_child_count(), 1, "@vfx left motes at the mark")
	# M2-AUD-07: hush_first_verse is a music.json cue, so Audio's deck plays it (and carries it past the scene).
	assert_true(seq.music_by_audio and Audio.music.current == &"hush_first_verse", "Audio plays the cue")
	assert_eq(seq.music_track, &"", "and the sequencer's own player stays out of it")
	_assert_clean()
	_free()


func test_leaving_mid_line_returns_to_the_host() -> void:
	_start(FIXTURE)
	_drive_until(func() -> bool: return lines_pending > 0)
	play_result = true
	zone.remove_child(seq)
	assert_false(play_result, "released from the line's advance")
	assert_false(seq.overlay.box.advance_requested.is_connected(seq._on_awaited_plain), "no stale hook left")
	zone.add_child(seq)
	seq.instant = true
	finished_ids.clear()
	_start(FIXTURE)
	assert_true(play_result, "the next play works normally")
	_free()


func test_a_glimmer_cue_is_a_real_field_with_its_drift() -> void:
	seq.instant = true
	_start(FIXTURE)
	var w := seq.warnings.filter(func(x: String) -> bool: return x.contains("not performed yet"))
	assert_eq(w, [], "drift, motion and rate are performed now (CutsceneVfx)")
	var field := stage.get_node("Marks/spot").get_child(0) as GlimmerField
	assert_true(field != null and field.get_mode() == GlimmerState.Mode.HELD, "a held GlimmerField at the mark")
	assert_eq(field.fixed_count, 4, "count=4 is its fixed count")
	_free()


func test_instant_second_option_takes_the_other_branch() -> void:
	seq.instant = true
	seq.auto_choice = 1
	_start(FIXTURE)
	assert_false(bool(Game.get_flag(&"test_flag")))
	assert_eq(int(Game.get_flag(&"test_counter", 0)), 2)
	_free()


func test_clip_marks_stand_in_for_missing_animations() -> void:
	var spot := stage.get_node("Marks/spot") as Marker3D
	spot.rotation.y = PI / 2.0
	stage.clip_marks = {"asha/look_at": "spot"}
	seq.instant = true
	_start(FIXTURE)
	assert_true(asha.global_position.distance_to(SPOT) < 0.01, "on the clip's mark")
	assert_between(angle_difference(asha.rotation.y, PI / 2.0), -0.01, 0.01, "facing the mark's -Z, not rhen")
	_free()


func test_missing_shot_is_a_soft_failure() -> void:
	stage.free()
	stage = _build_stage(false)
	seq.instant = true
	_start(FIXTURE)
	assert_false(seq.is_playing())
	assert_eq(finished_ids.size(), 1, "the scene still plays to its end")
	assert_true(seq.warnings.any(func(w: String) -> bool: return w.contains("no shot 'close'")), str(seq.warnings))
	_free()


func test_unknown_scene_refuses() -> void:
	_start(&"no_such_scene")
	assert_false(play_result)
	assert_false(seq.is_playing())
	assert_false(seq in SaveSystem.autosave_holders(), "no hold taken")
	_free()


func test_beach_cutscene_plays_both_choice_paths_on_a_bare_stage() -> void:
	seq.instant = true
	_start(BEACH)
	assert_true(bool(Game.get_flag(&"ch02_met_asha")))
	assert_true(bool(Game.get_flag(&"ch02_rhen_named_lantern")))
	assert_true(bool(Game.get_flag(&"ch02_rhen_stayed_with_dead")))
	assert_eq(seq.events.size(), 1)
	assert_eq(seq.events[0]["name"], &"zone_unlock")
	Game.state = GameStateData.new()
	seq.auto_choice = 1
	_start(BEACH)
	assert_true(bool(Game.get_flag(&"ch02_met_asha")))
	assert_false(bool(Game.get_flag(&"ch02_rhen_named_lantern")))
	assert_false(bool(Game.get_flag(&"ch02_rhen_stayed_with_dead")))
	_assert_clean()
	_free()


# --- real time -------------------------------------------------------------------------------


func test_real_time_play_holds_the_autosave_and_freezes_the_player() -> void:
	_start(FIXTURE)
	assert_true(seq.is_playing(), "suspended on the first camera move")
	assert_eq(seq.overlay.fade_alpha(), 1.0, "a scene that opens on @fade in starts black")
	assert_true(seq in SaveSystem.autosave_holders(), "autosave held")
	assert_false(player.accepts_input, "player frozen")
	_drive()
	assert_false(seq.is_playing(), "the scene ran to its end")
	assert_eq(lines_seen, 2, "both lines were shown and advanced")
	assert_true(bool(Game.get_flag(&"test_flag")))
	assert_eq(director.active_shot_id(), &"lane_fixed", "released back to the volume shot")
	_assert_clean()
	_free()


func test_the_interact_key_advances_lines_too() -> void:
	_start(FIXTURE)
	_drive_until(func() -> bool: return lines_pending > 0)
	var e := InputEventAction.new()
	e.action = FieldInput.INTERACT
	e.pressed = true
	var advanced := [false]
	seq.overlay.box.advance_requested.connect(func() -> void: advanced[0] = true)
	seq._unhandled_input(e)
	assert_false(seq.overlay.box.is_revealing(), "first press finishes the reveal")
	assert_false(advanced[0])
	seq._unhandled_input(e)
	assert_true(advanced[0], "second press advances")
	lines_pending = 0
	_drive()
	_free()


func test_skip_fast_forwards_to_the_choice_then_to_the_end() -> void:
	_start(FIXTURE)
	_drive_until(func() -> bool: return lines_pending > 0)
	lines_pending = 0
	var skips := [0]
	seq.skipped.connect(func(_id: StringName) -> void: skips[0] += 1)
	assert_true(seq.skip(), "skips from the first line")
	assert_eq(skips[0], 1)
	assert_true(seq.overlay.choices.visible, "the skip stopped at the choice")
	assert_false(seq.is_skipping(), "and is over")
	assert_eq(asha.global_position.distance_to(SPOT) < 0.01, true, "the walk before the choice completed")
	assert_false(seq.skip(), "no skip while a choice is open")
	seq.overlay.choices.pick(1)
	assert_true(seq.is_playing(), "after the choice the scene plays on at its own pace")
	assert_true(seq.skip())
	_drive()
	assert_false(seq.is_playing())
	assert_eq(int(Game.get_flag(&"test_counter", 0)), 2, "the player's choice stood")
	assert_eq(seq.events.size(), 1, "events after the choice still ran")
	_assert_clean()
	_free()


func test_holding_cancel_skips_after_the_hold_time() -> void:
	_start(FIXTURE)
	_drive_until(func() -> bool: return lines_pending > 0)
	var need := float(seq.config["skip_hold_sec"])
	seq.set_skip_held(true)
	seq.advance(need * 0.5)
	assert_true(seq.overlay.skip_prompt.visible, "the fill shows while held")
	assert_false(seq.overlay.choices.visible, "not yet skipped")
	seq.set_skip_held(false)
	assert_false(seq.overlay.skip_prompt.visible, "letting go resets it")
	seq.set_skip_held(true)
	seq.advance(need * 0.6)
	assert_false(seq.overlay.choices.visible, "the hold restarted from zero")
	seq.advance(need * 0.6)
	assert_true(seq.overlay.choices.visible, "a full hold skipped to the choice")
	seq.overlay.choices.pick(0)
	lines_pending = 0
	_drive()
	_free()


func test_real_time_blend_runs_and_fade_takes_its_time() -> void:
	_start(FIXTURE)
	var frames := _drive_until(func() -> bool: return director.active_shot_id() == &"close")
	assert_true(director.is_blending(), "@camera close blend=0.5 blends")
	assert_between(frames * DT, 0.9, 1.3, "the 1 s fade in ran before the first line and the blend")
	_drive()
	_free()


func test_a_walk_sets_off_and_settles_instead_of_starting_at_full_speed() -> void:
	# M2-FP-29, the human's playtest: walks started and stopped instantly and turns snapped.
	asha.global_position = SPOT + Vector3(-1.2, 0.0, 0.0)  # a walk short enough to end inside the scene
	_start(FIXTURE)
	_drive_until(func() -> bool: return seq.has_motion(&"move:asha"))
	var yaw0 := asha.rotation.y
	var steps: Array[float] = []
	var last: Array[Vector3] = [asha.global_position]
	_drive_until(
		func() -> bool:
			steps.append(asha.global_position.distance_to(last[0]))
			last[0] = asha.global_position
			return not seq.has_motion(&"move:asha")
	)
	assert_true(asha.global_position.distance_to(SPOT) < 0.01, "it arrives on its mark")
	assert_true(absf(angle_difference(yaw0, asha.rotation.y)) > 0.0, "it turned")
	var moving := steps.filter(func(d: float) -> bool: return d > 0.0)
	assert_true(moving.size() > 4)
	assert_eq(steps[0], 0.0, "a beat of anticipation before it moves")
	var peak: float = moving.max()
	assert_true(moving[0] < peak * 0.5, "it speeds up as it sets off")
	assert_true(moving[-1] < peak * 0.5, "and slows as it settles")
	_drive()
	_free()


func test_a_turn_is_never_a_snap() -> void:
	_start(FIXTURE)
	_drive_until(func() -> bool: return seq.has_motion(&"turn:asha"))
	var yaws: Array[float] = [asha.rotation.y]
	_drive_until(
		func() -> bool:
			yaws.append(asha.rotation.y)
			return not seq.has_motion(&"turn:asha")
	)
	var biggest := 0.0
	var total := 0.0
	for i in range(1, yaws.size()):
		var step := absf(angle_difference(yaws[i - 1], yaws[i]))
		biggest = maxf(biggest, step)
		total += step
	assert_true(yaws.size() > 4, "it takes several frames")
	assert_true(biggest < total * 0.5, "no single frame does most of the turn")
	_drive()
	_free()


func test_director_leaving_mid_blend_ends_the_cutscene() -> void:
	_start(FIXTURE)
	_drive_until(func() -> bool: return director.is_blending())
	assert_true(director.is_blending(), "reached the blend")
	zone.remove_child(director)
	assert_false(seq.is_playing(), "the owed blend_finished woke the sequencer, which stopped")
	assert_eq(finished_ids, [FIXTURE] as Array[StringName])
	assert_false(director.is_scripted(), "the director dropped the scripted shot")
	_assert_clean()
	zone.add_child(director)
	_free()


func test_sequencer_freed_mid_scene_releases_its_hold() -> void:
	_start(FIXTURE)
	assert_true(seq in SaveSystem.autosave_holders())
	play_result = true
	zone.remove_child(seq)
	assert_false(seq.is_playing(), "the await in progress was released")
	assert_false(play_result, "play() returned false to its host instead of hanging")
	assert_eq(finished_ids, [FIXTURE] as Array[StringName], "finished still fires once")
	assert_false(seq in SaveSystem.autosave_holders(), "leaving the tree drops the hold")
	assert_true(player.accepts_input, "and gives the player back")
	seq.free()
	seq = null
	_free()


# --- helpers ---------------------------------------------------------------------------------


## Starts a play without awaiting it: the test runner is synchronous, so a suspended play resumes
## inside the director.update() / seq.advance() / signal emits the test makes. `play_result` holds
## play()'s result once it returns.
func _start(scene_id: StringName) -> void:
	play_result = false
	play_result = await seq.play(scene_id, stage)


func _frame() -> void:
	director.update(DT)
	seq.advance(DT)


## Plays frames until the scene ends: reveals and advances each line, picks option 0.
func _drive() -> void:
	_drive_until(func() -> bool: return false)


## Plays frames (advancing lines, picking option 0) until `done` is true or the scene ends.
## Returns the frames played.
func _drive_until(done: Callable) -> int:
	var frames := 0
	while seq.is_playing() and not done.call() and frames < MAX_FRAMES:
		if seq.overlay.choices.visible:
			seq.overlay.choices.pick(0)
		elif lines_pending > 0:
			lines_pending = 0
			seq.overlay.box.skip_reveal()
			seq.overlay.box.advance_requested.emit()
		else:
			_frame()
			frames += 1
	return frames


func _assert_clean() -> void:
	assert_false(seq in SaveSystem.autosave_holders(), "autosave hold released")
	assert_true(player.accepts_input, "player input restored")
	assert_false(director.is_scripted(), "camera handed back")
	assert_eq(seq.overlay.letterbox(), 0.0, "letterbox off")
	assert_eq(seq.overlay.fade_alpha(), 0.0, "screen clear")
	assert_false(seq.overlay.box.visible, "dialogue box hidden")


func _free() -> void:
	if zone != null:
		zone.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
