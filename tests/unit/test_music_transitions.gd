extends TestCase
## M3-AUD-864: music changes between zones, battles and cutscenes crossfade on the beat, never as a hard cut.
## MusicDeck holds a change with a fade until the next beat of the cue sounding (its grid halved until it is no
## longer than beat_sync_max_wait_sec), picks a resumed cue up on a beat of its own, and every music fade the game
## asks for (mix.json, the sequencer's default, the cutscene hold, battle phases, every Act I `@music fade=`) is at
## least mix.json min_fade_sec. Every Act I cue has a beat grid, or says it is unmetered ("free").

const CUE_A := "res://assets/audio/music/temple_trial.ogg"
const CUE_B := "res://assets/audio/music/battle_standard.ogg"
## 60 BPM, downbeat at 0.25 s: a beat of 1.0 s, halved to 0.5 s under the 0.6 s cap.
const ROW_A := {"file": CUE_A, "resume": true, "beat": {"bpm": 60.0, "downbeat_offset_s": 0.25}}
const ROW_B := {"file": CUE_B, "beat": {"bpm": 60.0, "downbeat_offset_s": 0.25}}
const ROW_FREE := {"file": CUE_B, "beat": "free"}
const MAX_WAIT := 0.6
const MIX := "res://game/data/audio/mix.json"
const SEQUENCER := "res://game/data/cutscene/sequencer.json"

var deck: MusicDeck
var pos := 0.0


func before_each() -> void:
	deck = MusicDeck.new()
	_host().add_child(deck)
	deck.beat_max_wait_sec = MAX_WAIT
	deck.position_source = func(_p: AudioStreamPlayer) -> float: return pos


func test_a_change_waits_for_the_next_beat_of_the_cue_sounding() -> void:
	assert_true(deck.play(&"a", ROW_A, 0.0), "a starts at once (no fade asked)")
	var a := deck.player()
	pos = 0.35  # 0.1 s past a half-beat line (0.25 + k * 0.5)
	assert_between(deck.wait_for_beat(0.5), 0.39, 0.41, "0.4 s to the next half-beat")
	assert_true(deck.play(&"b", ROW_B, 0.5))
	assert_eq(deck.current, &"b", "the deck names the new cue at once")
	assert_eq(deck.queued_cue(), &"b", "but it waits for the beat")
	_run(0.38)
	assert_true(deck.has_queued(), "still waiting just before the beat")
	assert_true(a.playing and absf(a.volume_db) < 0.01, "the old cue plays on at full level until then")
	_run(0.04)
	assert_false(deck.has_queued(), "the change lands on the beat")
	assert_true(deck.player() != null and deck.player() != a, "the new cue enters on the other slot")
	_run(0.6)
	assert_false(a.playing, "the old cue has faded from the beat and stopped")
	assert_true(deck.positions.has(&"a"), "the resumable cue kept its place")
	_done()


func test_a_stop_waits_for_the_beat_too() -> void:
	deck.play(&"a", ROW_A, 0.0)
	var a := deck.player()
	pos = 0.30
	deck.stop(0.5)
	assert_eq(deck.current, &"", "nothing is named once stopped")
	assert_true(deck.has_queued(), "the fade out waits for the beat")
	_run(0.4)
	assert_true(a.playing, "it started fading on the beat, not before")
	_run(0.7)
	assert_false(a.playing, "then it is silent")
	_done()


func test_going_back_before_the_beat_keeps_the_cue_sounding() -> void:
	deck.play(&"a", ROW_A, 0.0)
	var a := deck.player()
	pos = 0.30
	deck.play(&"b", ROW_B, 0.5)
	assert_true(deck.play(&"a", ROW_A, 0.5), "back to a before the change landed")
	assert_false(deck.has_queued(), "the change is dropped")
	assert_eq(deck.current, &"a")
	_run(1.0)
	assert_true(a.playing and deck.player() == a, "a never stopped")
	_done()


func test_an_immediate_or_unmetered_change_lands_at_once() -> void:
	deck.play(&"a", ROW_A, 0.0)
	pos = 0.30
	deck.play(&"b", ROW_B, 0.0)
	assert_false(deck.has_queued(), "a fade of 0 is a deliberate cut, not held")
	deck.play(&"f", ROW_FREE, 0.0)
	deck.play(&"a", ROW_A, 0.5)
	assert_false(deck.has_queued(), "a free piece has no beat to wait for")
	assert_eq(MusicDeck.grid_of(ROW_FREE), {}, "free means no grid, whatever the file has")
	_done()


func test_a_resumed_cue_picks_up_on_a_beat_of_its_own() -> void:
	deck.play(&"a", ROW_A, 0.0)
	deck.positions[&"a"] = 3.71
	deck.play(&"b", ROW_B, 0.0)
	deck.positions[&"a"] = 3.71
	deck.play(&"a", ROW_A, 0.0)
	assert_between(deck.started_from, 3.249, 3.251, "back to the beat at 3.25 s (0.25 + 3 x 1.0)")
	_done()


func test_no_music_change_in_the_game_is_a_hard_cut() -> void:
	var music := (AudioData.table(AudioData.MIX).get("music", {})) as Dictionary
	var floor_sec := float(music.get("min_fade_sec", 0.0))
	assert_true(floor_sec > 0.0, "mix.json music.min_fade_sec is set")
	assert_true(float(music.get("beat_sync_max_wait_sec", 0.0)) > 0.0, "beat sync is on")
	for k: String in ["crossfade_sec", "battle_in_sec", "battle_out_sec", "cutscene_release_sec"]:
		assert_true(float(music.get(k, 0.0)) >= floor_sec, "mix.json music.%s is no hard cut" % k)
	assert_true(AudioDirector.CUTSCENE_TAKE_SEC >= floor_sec, "a cutscene takes the bed with a fade")
	var seq := JSON.parse_string(FileAccess.get_file_as_string(SEQUENCER)) as Dictionary
	assert_true(float(seq.get("music_fade_default_sec", 0.0)) >= floor_sec, "a bare @music fades")
	var phases := (AudioData.table(AudioData.MUSIC)["battle"] as Dictionary).get("phases", {}) as Dictionary
	for ph: String in phases:
		assert_true(float((phases[ph] as Dictionary).get("sec", 0.0)) >= floor_sec, "phase %s brings stems in" % ph)
	var re := RegEx.create_from_string("@music\\s+\\S+.*\\bfade=([0-9.]+)")
	for path: String in _act1_dlgs():
		var lines := FileAccess.get_file_as_string(path).split("\n")
		for i in lines.size():
			var m := re.search(lines[i])
			if m != null:
				assert_true(float(m.get_string(1)) >= floor_sec, "%s:%d fades the music" % [path, i + 1])
	_done()


func test_every_act1_cue_has_a_beat_grid_or_is_free() -> void:
	var music := AudioData.table(AudioData.MUSIC)
	for id: StringName in _act1_cues(music):
		var row := AudioData.cue(music, id)
		assert_false(row.is_empty(), "cue %s exists" % id)
		var free := row.get("beat", null) is String and str(row["beat"]) == "free"
		assert_true(free or not MusicDeck.grid_of(row).is_empty(), "cue %s has a beat grid or is free" % id)
	_done()


func _act1_cues(music: Dictionary) -> Array[StringName]:
	var out: Array[StringName] = []
	var later := RegEx.create_from_string("^ch(1[0-9]|2[0-9])_")
	for z: Dictionary in music["zones"]:
		if RegEx.create_from_string("levels/(prologue|ch0[1-9])/").search(str(z["scene"])) == null:
			continue
		for row: Dictionary in [z] + Array(z.get("variants", [])):
			if row.has("music") and not out.has(StringName(str(row["music"]))):
				out.append(StringName(str(row["music"])))
	var battle := music["battle"] as Dictionary
	out.append(StringName(str(battle["default"])))
	for enc: String in battle["encounters"]:
		if later.search(enc) == null:
			out.append(StringName(str(battle["encounters"][enc])))
	var re := RegEx.create_from_string("@music\\s+([A-Za-z0-9_]+)")
	for path: String in _act1_dlgs():
		for m: RegExMatch in re.search_all(FileAccess.get_file_as_string(path)):
			var id := StringName(m.get_string(1))
			if id != AudioData.SILENCE and not out.has(id):
				out.append(id)
	return out


func _act1_dlgs() -> Array[String]:
	var out: Array[String] = []
	for d: String in ["prologue", "ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "ch08", "ch09"]:
		var base := "res://game/data/dialogue/%s/" % d
		for f: String in DirAccess.get_files_at(base):
			if f.ends_with(".dlg"):
				out.append(base + f)
	return out


func _run(sec: float) -> void:
	var step := 1.0 / 60.0
	var t := 0.0
	while t < sec - 1e-6:
		deck.advance(minf(step, sec - t))
		t += step


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _done() -> void:
	deck.stop(0.0)
	deck.free()
