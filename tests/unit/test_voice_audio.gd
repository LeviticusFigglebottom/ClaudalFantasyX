extends TestCase
## M3-AUD-07: the dialogue voices (game/audio/voice_audio.gd, game/data/audio/voices.json). Every speakers.json id
## has a voice whose blip rows exist on the Voice bus; an unknown voice falls back to the default; the listener plays
## the speaker's blips for the box's own blips (and keeps the box's player silent), drops blips closer than the
## voice's rate, takes the voice from the sequencer's line, and prefers a recorded line (a fixture stream) to blips.
## M3-AUD-21: paced by syllable (the default), a voice blips once per vowel group as the mouth opens, so it rests
## where the reveal rests, and stays silent for narration without narration blips and for a skipped reveal.

const SCENE := "res://game/ui/dialogue/dialogue_box.tscn"
const SPEAKERS := "res://game/data/dialogue/speakers.json"
const LINE_KEY := &"DLG_CH02_BEACH_004"
const VO_PATH := "res://assets/audio/vo/asha/ch02_test_001.ogg"
const TABLE := {
	"pace": "letter",
	"default": {"blips": ["voice_soft"], "pitch": 1.0, "rate_ms": 0, "jitter": 0.0, "volume_db": 0.0},
	"vo": {"pattern": "res://assets/audio/vo/{speaker}/{line_id}.ogg", "narrator": "narrator", "suppress_blips": true},
	"speakers":
	{
		"toma": {"blips": ["voice_low", "voice_soft"], "pitch": 1.1, "jitter": 0.0, "volume_db": -2.0},
		"asha": {"blips": ["voice_bright"], "pitch": 1.0, "rate_ms": 150, "jitter": 0.05},
	},
}

var box: DialogueBox
var voice: VoiceAudio
var calls: Array = []
var fixture: AudioStreamWAV


func before_each() -> void:
	calls = []
	box = (load(SCENE) as PackedScene).instantiate() as DialogueBox
	box.settings = (
		DialogueTextSettings
		. from_dict(
			{
				"chars_per_sec": 10.0,
				"min_chars_per_sec": 1.0,
				"max_chars_per_sec": 100.0,
				"blip_every_n_chars": 1,
				"blip_volume_db": -8.0,
				"narration_blip": false,
				"flap_vowels": "aeiouAEIOU",
			}
		)
	)
	_host().add_child(box)
	box.set_process(false)
	fixture = AudioStreamWAV.new()
	fixture.data = PackedByteArray([0, 0, 0, 0])
	voice = VoiceAudio.new(TABLE)
	voice.player = func(id: StringName, opts: Dictionary) -> void: calls.append([id, opts])
	voice.vo_loader = func(path: String) -> AudioStream: return fixture if path == VO_PATH else null
	_host().add_child(voice)
	voice.attach(box)


func test_every_speaker_has_a_voice_on_the_voice_bus() -> void:
	var table := AudioData.table(AudioData.VOICES)
	var rows := AudioData.sfx_rows()
	var speakers: Array = (JSON.parse_string(FileAccess.get_file_as_string(SPEAKERS)) as Dictionary)["speakers"]
	assert_false(speakers.is_empty())
	for s: Dictionary in speakers:
		var id := str(s["id"])
		assert_true((table["speakers"] as Dictionary).has(id), "speaker %s has a voice" % id)
		var row := VoiceAudio.voice_row(table, StringName(id))
		assert_false((row["blips"] as Array).is_empty(), "%s has blips" % id)
		assert_true(float(row["rate_ms"]) >= 50.0, "%s: at most one blip per ~55 ms (mix.md §4)" % id)
		for b: Variant in row["blips"]:
			var sfx := rows.get(str(b), {}) as Dictionary
			assert_eq(str(sfx.get("bus", "")), "Voice", "%s: blip row %s plays on Voice" % [id, b])
			for f: Variant in sfx.get("files", []):
				assert_true(ResourceLoader.exists(str(f)), "%s exists" % f)
	_done()


func test_unknown_voice_falls_back_to_the_default() -> void:
	var row := VoiceAudio.voice_row(TABLE, &"nobody")
	assert_eq(row["blips"], ["voice_soft"])
	var toma := VoiceAudio.voice_row(TABLE, &"toma")
	assert_eq(toma["blips"], ["voice_low", "voice_soft"], "a speaker's keys win")
	assert_eq(float(toma["rate_ms"]), 0.0, "and the default fills the rest")
	_done()


func test_box_blips_play_the_speakers_voice_and_the_box_is_silent() -> void:
	voice.on_line(_line(&"toma", &"ch02_test_002"))
	box.show_line(_line(&"toma", &"ch02_test_002"))
	_reveal(0.4, 0.1)  # "That" -> 4 blips
	assert_eq(box.blips_played, 4)
	assert_eq(voice.blips, 4, "one voice blip per box blip")
	assert_eq(calls[0][0], &"voice_low")
	assert_eq(calls[1][0], &"voice_soft", "the set cycles")
	assert_between(float(calls[0][1]["pitch"]), 1.099, 1.101, "toma's pitch, no jitter")
	assert_between(float(calls[0][1]["volume_db"]), -10.01, -9.99, "the box's blip level plus the voice's")
	assert_eq((box.get_node(^"Blip") as AudioStreamPlayer).volume_db, VoiceAudio.MUTE_DB, "the shared blip is silent")
	_done()


func test_rate_limit_drops_close_blips() -> void:
	voice.on_line(_line(&"asha", &""))
	box.show_line(_line(&"asha", &""))
	_reveal(0.6, 0.1)  # "That's" -> 6 blips 100 ms apart; asha's rate is 150 ms
	assert_eq(box.blips_played, 6)
	assert_eq(voice.blips, 3, "every other blip")
	assert_eq(voice.dropped, 3)
	for c: Array in calls:
		assert_between(float(c[1]["pitch"]), 0.95, 1.05, "within asha's jitter")
	box.advance(0.5)  # five blips inside one frame
	voice.advance(0.2)
	assert_eq(voice.blips, 4, "a frame plays one blip at most")
	_done()


func test_the_voice_comes_from_the_line_then_the_flaps() -> void:
	voice.on_line(_line(&"", &"", &"toma"))
	assert_eq(voice.voice, &"toma", "narration speaks in its narrator identity")
	box.show_text(&"asha", LINE_KEY)  # no step: the first vowel's flap names the speaker
	_reveal(0.3, 0.1)  # "Tha"
	assert_eq(voice.voice, &"asha")
	_done()


func test_recorded_line_plays_and_silences_blips() -> void:
	var step := _line(&"asha", &"ch02_test_001")
	assert_eq(VoiceAudio.vo_file(TABLE, step), VO_PATH)
	voice.on_line(step)
	box.show_line(step)
	assert_true(voice.has_vo(), "the fixture stream is found")
	assert_eq(voice.vo.stream, fixture)
	assert_eq(voice.vo.bus, &"Voice")
	_reveal(0.6, 0.1)
	assert_eq(voice.blips, 0, "a voiced line plays no blips")
	assert_eq(voice.dropped, 6)
	var next := _line(&"asha", &"ch02_test_009")
	voice.on_line(next)
	box.show_line(next)
	assert_false(voice.has_vo(), "a missing file falls back")
	_reveal(0.2, 0.2)
	assert_eq(voice.blips, 1, "to the blips")
	_done()


func test_vo_paths_from_the_voice_field_pattern_and_narration() -> void:
	var s := _line(&"", &"ch02_beach_035", &"rhen")
	assert_eq(VoiceAudio.vo_file(TABLE, s), "res://assets/audio/vo/rhen/ch02_beach_035.ogg")
	s.narrator = &""
	assert_eq(VoiceAudio.vo_file(TABLE, s), "res://assets/audio/vo/narrator/ch02_beach_035.ogg", "a caption")
	s.voice = VO_PATH
	assert_eq(VoiceAudio.vo_file(TABLE, s), VO_PATH, "the compiled voice field wins")
	assert_eq(VoiceAudio.vo_file(TABLE, _line(&"asha", &"")), "", "no line id, no file")
	_done()


func test_vo_stops_when_the_box_closes() -> void:
	voice.on_line(_line(&"asha", &"ch02_test_001"))
	assert_true(voice.has_vo())
	box.visible = false
	voice.advance(0.1)
	assert_false(voice.has_vo(), "a closed box stops its line")
	_done()


func test_director_attaches_one_voice_per_box_and_hears_the_sequencer() -> void:
	var dir := AudioDirector.new()
	_host().add_child(dir)
	dir.set_process(false)
	var seq := CutsceneSequencer.new()
	_host().add_child(seq)
	var b := seq.overlay.box
	var l := dir.attach_voice(b)
	assert_true(l != null)
	assert_eq(dir.attach_voice(b), l, "one listener per box")
	seq.line_shown.emit(_line(&"kerrid", &""))
	assert_eq(l.voice, &"kerrid", "the sequencer's line names the voice")
	b.visible = true
	b.settings.chars_per_sec = 10.0
	b.show_line(_line(&"kerrid", &""))
	b.advance(0.3)  # "Tha": the first syllable opens on its vowel
	dir.advance(0.3)
	assert_eq(l.blips, 1)
	assert_eq(StringName(str(dir.sfx.history[-1][0])), &"voice_low", "kerrid's row through the SFX bank")
	seq.free()
	dir.free()
	_done()


func test_syllable_pace_blips_once_per_vowel_group() -> void:
	voice.data = _syllable_table()
	voice.on_line(_line(&"toma", &""))
	box.show_line(_line(&"toma", &""))
	_reveal(0.3, 0.1)  # "Tha"
	assert_eq(voice.blips, 1, "the mouth opens on the first vowel")
	_reveal(0.5, 0.1)  # "t's a"
	assert_eq(voice.blips, 2, "nothing for the consonants, one for the next vowel")
	_reveal(10.0, 0.1)
	assert_eq(box.shown_text(), "That's a very big spear for a very small conversation.")
	assert_eq(voice.blips, _vowel_groups(box.shown_text()), "one blip per vowel group (13), not per letter")
	assert_true(box.blips_played > voice.blips * 3, "the box counted letters")
	_done()


func test_syllable_pace_rests_with_the_reveal() -> void:
	voice.data = _syllable_table()
	voice.on_line(_line(&"toma", &""))
	box.show_line(_line(&"toma", &""))
	_reveal(0.3, 0.1)
	var before := voice.blips
	voice.advance(1.0)  # the reveal holds (a pause): no characters, no mouth, no blips
	assert_eq(voice.blips, before, "a pause is silent")
	box.skip_reveal()
	voice.advance(0.1)
	assert_eq(voice.blips, before, "a skipped reveal adds no blips")
	voice.on_line(_line(&"", &"", &"toma"))
	box.show_line(_line(&"", &"", &"toma"))
	_reveal(1.0, 0.1)
	assert_eq(voice.blips, before, "narration stays silent without narration_blip")
	_done()


func _syllable_table() -> Dictionary:
	var t := TABLE.duplicate(true)
	t["pace"] = "syllable"
	return t


func _vowel_groups(text: String) -> int:
	var n := 0
	var inside := false
	for ch in text:
		var v := box.settings.flap_vowels.contains(ch)
		if v and not inside:
			n += 1
		inside = v
	return n


func _line(speaker: StringName, line_id: StringName, narrator: StringName = &"") -> DialogueStep:
	return DialogueStep.from_line_op(
		{"id": String(line_id), "key": String(LINE_KEY), "speaker": String(speaker), "narrator": String(narrator)}
	)


## Reveals for `sec` in steps of `step`, the listener reading the box after each.
func _reveal(sec: float, step: float) -> void:
	var t := 0.0
	while t < sec - 1e-6:
		box.advance(step)
		voice.advance(step)
		t += step


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _done() -> void:
	voice.free()
	box.free()
