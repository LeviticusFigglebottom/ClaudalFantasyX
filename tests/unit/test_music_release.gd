extends TestCase
## The Lead's 10-30 19:25 item (Act I's emotional beats, as played): a cue with a `release` row (music.json) is let go
## by its own ending, not a plain fade, wherever a scene silences it. The Ebbing's dance is paced by the player's held
## input, so the scene can reach its letting-down at any point of the cue; its release is the last chord and the motes
## falling away. A cue with no release still fades to silence. And the Act I end's vigil plays the piano coda the
## beat sheet names, resuming across the act card into the end card instead of starting twice. Nothing is heard.

var dir: AudioDirector


func before_each() -> void:
	dir = AudioDirector.new()
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(dir)
	dir.set_process(false)


func _done() -> void:
	dir.stop_all_players()
	dir.free()


func test_silencing_the_ebbing_plays_its_release() -> void:
	assert_true(dir.play_music(&"the_ebbing", 3.0), "the dance")
	assert_true(dir.play_music(AudioData.SILENCE, 3.0), "@music silence at the letting-down")
	assert_eq(dir.music.current, &"the_ebbing_release", "it lets go by its own ending")
	assert_false(dir.music.is_silent(), "heard, not faded out")
	_done()


func test_a_cue_with_no_release_fades_as_before() -> void:
	assert_true(dir.play_music(&"haluna_night", 1.0))
	dir.play_music(AudioData.SILENCE, 1.0)
	assert_ne(dir.music.current, &"haluna_night_release", "no release")
	assert_true(AudioData.cue(dir.music_data, &"haluna_night").get("release", "") == "", "it has none")
	_done()


func test_every_release_is_a_cue_with_a_file() -> void:
	for id: String in dir.music_data.get("cues", {}) as Dictionary:
		var rel := str(AudioData.cue(dir.music_data, StringName(id)).get("release", ""))
		if rel == "":
			continue
		var row := AudioData.cue(dir.music_data, StringName(rel))
		assert_false(row.is_empty(), "%s's release %s is a cue" % [id, rel])
		for f: String in AudioData.cue_files(row):
			assert_true(ResourceLoader.exists(f), "%s exists" % f)
	_done()


func test_the_vigil_plays_the_piano_coda_and_it_resumes_into_the_end_card() -> void:
	var text := FileAccess.get_file_as_string("res://game/data/dialogue/ch09/ch09_the_road_out.dlg")
	assert_true(text.contains("@music hush_coda"), "the vigil names the coda (act1_ch09.md B10: the piano coda)")
	assert_true(bool(AudioData.cue(dir.music_data, &"hush_coda").get("resume", false)), "and the coda resumes")
	_done()
