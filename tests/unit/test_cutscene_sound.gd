extends TestCase
## M2-FP-118: `@sfx` plays Audio's sfx row when audio has one (its bus, variation and cooldown), from the cue's
## `at` place when it names one, and falls back to the cutscene's <sfx_dir>/<id>.ogg; an unknown id reports false.

const ROW := &"drownbell_toll"


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func test_a_table_row_plays_through_audio() -> void:
	assert_true(Audio.sfx != null and Audio.sfx.has(ROW), "the toll is a row in audio's table")
	var before := Audio.sfx.history.size()
	var mark := Node3D.new()
	_host().add_child(mark)
	mark.position = Vector3(3.0, 0.0, -4.0)
	var clock := Audio.sfx.clock
	Audio.sfx.clock = func() -> int: return clock.call() + 600000  # past any earlier play's cooldown
	assert_true(CutsceneSound.play(_host(), "res://nowhere/", ROW, 0.5, mark))
	assert_eq(Audio.sfx.history.size(), before + 1, "played by audio, not from the cutscene's folder")
	assert_eq(StringName(str(Audio.sfx.history.back()[0])), ROW)
	Audio.sfx.clock = clock
	mark.free()


func test_an_unknown_sound_reports_false() -> void:
	assert_false(CutsceneSound.play(_host(), "res://assets/audio/sfx/", &"no_such_sound_anywhere", 1.0, null))


## M3-AUD-829: `@music undertow_rising stem=1` brings the run's pulse in on the cue already playing (the cue starts
## on its first stem only); a second `@music` of the same cue without stem= leaves it as it is.
func test_a_music_stem_comes_in_on_the_playing_cue() -> void:
	var cue := &"undertow_rising"
	assert_true(CutsceneSound.music(cue, 0.0))
	assert_eq(Audio.music.current, cue)
	assert_eq(Audio.music.stem_gain(1), 0.0, "the pulse is out at the start")
	assert_true(CutsceneSound.music(cue, 0.0, 1))
	assert_eq(Audio.music.current, cue, "the cue carries on")
	assert_eq(Audio.music.stem_gain(1), 1.0, "the pulse is in")
	CutsceneSound.music(AudioData.SILENCE, 0.0)
