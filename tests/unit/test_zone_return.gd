extends TestCase
## M3-AUD-864 (the as-played pass): the zone returns on release. A scene that ends on `@music silence` or on a one-shot
## cue, or a battle that ends where it started, must not leave the field silent until the next scene swap: once nothing
## plays, no cutscene runs, no battle is in the tree and no cue is loading, the zone's own cue comes back after
## mix.json music.zone_return_sec. Anything that takes the music itself first (a swap, a battle) is never doubled.

const ZONE_CUE := &"oruvel"
const ONE_SHOT := &"tidecup_after"

var dir: AudioDirector
var wait := 0.0


func before_each() -> void:
	dir = AudioDirector.new()
	_host().add_child(dir)
	dir.set_process(false)
	dir.zone = {"music": String(ZONE_CUE)}
	wait = float(dir.music_cfg().get("zone_return_sec", 0.0))


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _done() -> void:
	dir.stop_all_players()
	dir.free()


func _run(sec: float) -> void:
	var t := 0.0
	while t < sec:
		dir.advance(0.05)
		t += 0.05


func test_mix_sets_a_return_after_the_release() -> void:
	assert_true(wait >= float(dir.music_cfg().get("cutscene_release_sec", 0.0)), "it waits out the cutscene release")
	_done()


func test_a_scene_that_ends_in_silence_hands_back_to_the_zone() -> void:
	assert_true(dir.play_music(&"undertow_rising", 0.2), "a scene's cue")
	_run(0.5)
	dir.stop_music(0.2)
	_run(0.5)
	assert_true(dir.music.is_silent(), "@music silence: the field is quiet")
	_run(wait - 0.6)
	assert_true(dir.music.is_silent(), "and stays quiet through the release")
	_run(0.5)
	assert_eq(dir.music.current, ZONE_CUE, "then the zone's own cue comes back")
	assert_false(dir.music.is_silent(), "and is heard")
	_done()


func test_a_one_shot_that_ends_hands_back_to_the_zone() -> void:
	assert_true(dir.play_music(ONE_SHOT, 0.2))
	_run(0.5)
	dir.music.player().stop()  # the one-shot reaches its end (headless playback does not advance)
	_run(wait + 0.2)
	assert_eq(dir.music.current, ZONE_CUE, "the zone follows a cue that has run out")
	_done()


func test_nothing_returns_while_a_battle_is_in_the_tree() -> void:
	var battle := Node.new()
	_host().add_child(battle)
	dir._battles.append(battle)
	dir.stop_music(0.2)
	_run(wait + 1.0)
	assert_true(dir.music.is_silent(), "battle_out's silence holds while the battle is up (the victory screen)")
	battle.free()
	_run(wait + 0.2)
	assert_eq(dir.music.current, ZONE_CUE, "a battle that ends where it started hands back to the zone")
	_done()


func test_after_a_battle_the_field_comes_back_at_once_under_the_sting() -> void:
	# the human's playtest: the return to the field after a victory is under 1 s; the field's cue must neither leave a
	# gap nor clip the victory sting (2.4 s), so it comes back battle_return_sec after the battle leaves, fading in long
	var back := float(dir.music_cfg().get("battle_return_sec", 0.0))
	var fade := float(dir.music_cfg().get("battle_return_fade_sec", 0.0))
	assert_true(back < 1.0 and back < wait, "sooner than the scene release (%s s)" % back)
	assert_true(fade >= 1.5, "and fading in long enough to sit under the sting's tail (%s s)" % fade)
	var battle := Node.new()
	_host().add_child(battle)
	dir._battles.append(battle)
	assert_true(dir.play_music(&"battle_standard_v2", 0.0))
	_run(0.5)
	dir.stop_music(float(dir.music_cfg().get("battle_out_sec", 0.0)))  # battle_finished
	_run(0.5)
	battle.free()  # the victory screen ends: back to the resident field, with no swap
	_run(back + 0.1)
	assert_eq(dir.music.current, ZONE_CUE, "the field's own cue is back within %s s" % (back + 0.1))
	assert_true(dir.music.gain() < 0.5, "and still fading in under the sting")
	_run(fade)
	assert_true(dir.music.gain() > 0.99, "then at full level")
	_done()


func test_a_swap_after_a_battle_keeps_its_own_cue() -> void:
	var battle := Node.new()
	_host().add_child(battle)
	dir._battles.append(battle)
	dir.stop_music(0.2)
	battle.free()
	assert_true(dir.play_music(&"tidecup_after", 0.2), "the next scene starts its own cue first")
	_run(float(dir.music_cfg().get("battle_return_sec", 0.0)) + 1.0)
	assert_eq(dir.music.current, &"tidecup_after", "and the zone's is not laid over it")
	_done()


func test_a_cue_loading_is_never_doubled() -> void:
	dir.stop_music(0.2)
	dir._pending = {"cue": &"battle_standard_v2", "sec": 0.3, "files": []}  # loaded at the next poll
	_run(wait + 1.0)
	assert_eq(dir.music.current, &"battle_standard_v2", "the cue on its way (a swap, a battle) is the one that plays")
	assert_false(dir.music.is_silent(), "and the zone was never started under it")
	_done()


func test_a_zone_with_no_music_stays_silent() -> void:
	dir.zone = {}
	dir.stop_music(0.2)
	_run(wait + 1.0)
	assert_true(dir.music.is_silent(), "a zone scored by its own cutscene (first_verse) gets nothing back")
	_done()
