extends TestCase
## M3-AUD-861 (the Lead's 08:59; M3-HER-1146): every `@music` id in an Act I script resolves to real audio the way
## the runtime plays it. CutsceneSound.music (M2-AUD-07) hands a music.json cue to Audio's deck, stems and LFS files
## and all, so its files must exist; only an id with no cue falls back to the sequencer's own
## `<music_dir><id>.ogg` and then its music_stand_ins file, and none may fall that far (a stand-in is a placeholder).

const ACT1 := ["prologue", "ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "ch08", "ch09"]
const DIALOGUE_DIR := "res://game/data/dialogue/"
const SEQ_CONFIG := "res://game/data/cutscene/sequencer.json"


func _music_ids() -> Dictionary:
	var ids: Dictionary = {}  # id -> the first script that names it
	var re := RegEx.new()
	re.compile("(?m)^\\s*@music\\s+([A-Za-z0-9_]+)")
	for d: String in ACT1:
		for f: String in DirAccess.get_files_at(DIALOGUE_DIR + d):
			if not f.ends_with(".dlg"):
				continue
			var text := FileAccess.get_file_as_string(DIALOGUE_DIR + d + "/" + f)
			for m: RegExMatch in re.search_all(text):
				var id := m.get_string(1)
				if id != String(AudioData.SILENCE) and not ids.has(id):
					ids[id] = d + "/" + f
	return ids


func test_every_act1_music_id_is_a_cue_with_real_files() -> void:
	var music := AudioData.table(AudioData.MUSIC)
	var ids := _music_ids()
	assert_true(ids.size() > 20, "the Act I scripts name their music (%d ids)" % ids.size())
	for id: String in ids:
		var row := AudioData.cue(music, StringName(id))
		assert_false(row.is_empty(), "@music %s (%s) is a music.json cue, played on the deck" % [id, ids[id]])
		for f: String in AudioData.cue_files(row):
			assert_true(ResourceLoader.exists(f), "@music %s: %s exists" % [id, f])


func test_no_act1_music_id_falls_back_to_a_stand_in() -> void:
	var music := AudioData.table(AudioData.MUSIC)
	var cfg := JSON.parse_string(FileAccess.get_file_as_string(SEQ_CONFIG)) as Dictionary
	var stand_ins := cfg.get("music_stand_ins", {}) as Dictionary
	for id: String in _music_ids():
		if AudioData.cue(music, StringName(id)).is_empty() and stand_ins.has(id):
			assert_true(false, "@music %s would play the stand-in %s" % [id, stand_ins[id]])


## The runtime path itself: CutsceneSequencer._cue_music calls CutsceneSound.music for each @music step, and that
## must leave Audio's deck playing the cue with its real file loaded (stems as one synchronized stream).
func test_every_act1_music_id_plays_its_real_file_on_the_deck() -> void:
	var music := AudioData.table(AudioData.MUSIC)
	for id: String in _music_ids():
		assert_true(CutsceneSound.music(StringName(id), 0.0), "@music %s is handed to Audio" % id)
		assert_eq(Audio.music.current, StringName(id), "the deck is playing %s" % id)
		var p := Audio.music.player()
		assert_true(p != null and p.stream != null and p.playing, "@music %s: a stream is playing" % id)
		if p == null or p.stream == null:
			continue
		var files := AudioData.cue_files(AudioData.cue(music, StringName(id)))
		if p.stream is AudioStreamSynchronized:
			var sync := p.stream as AudioStreamSynchronized
			assert_eq(sync.stream_count, files.size(), "@music %s: all its stems" % id)
			for i in sync.stream_count:
				assert_eq(sync.get_sync_stream(i).resource_path, files[i], "@music %s stem %d" % [id, i])
		else:
			assert_eq(p.stream.resource_path, files[0], "@music %s loads its own file" % id)
	CutsceneSound.music(AudioData.SILENCE, 0.0)
	Audio.stop_all_players()
