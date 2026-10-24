extends TestCase
## M2-AUD-02: the audio runtime (game/audio/). The tables name real files, scenes and flags; zone rows and their
## flag variants resolve; buses are built from mix.json; the music deck crossfades, holds, resumes and fades stems;
## ducks ramp the buses; the SFX bank keeps its cooldowns, voices and no-repeat picks; and the listen-only hooks
## route a cutscene sequencer's players and hold the bed while its music plays.

const CUE_A := "res://assets/audio/music/temple_trial.ogg"
const CUE_B := "res://assets/audio/music/battle_standard.ogg"
const BLIP := "res://assets/audio/sfx/text_blip.ogg"
const MIX := {
	"buses": [{"name": "Music", "send": "Master"}, {"name": "UI", "send": "SFX"}, {"name": "SFX", "send": "Master"}],
	"ducks": {"dialogue": {"sec": 0.25, "buses": {"Music": -4.0}}},
	"music": {"crossfade_sec": 1.0, "floor_db": -60.0, "cutscene_release_sec": 2.0},
}
const MUSIC := {
	"cues":
	{
		"a": {"file": CUE_A, "resume": true},
		"b": {"file": CUE_B},
		"layers": {"stems": [CUE_A, CUE_B], "start_stems": [0]},
	},
	"zones":
	[
		{
			"scene": "res://x.tscn",
			"music": "a",
			"ambience": [],
			"variants": [{"flag": "night", "music": "b"}],
		},
	],
	"battle": {"default": "b", "encounters": {"boss": "layers"}},
}
const SFX := {
	"sfx":
	{
		"tick": {"files": [BLIP], "bus": "UI", "cooldown_ms": 50, "voices": 2},
		"pick": {"files": [BLIP, CUE_A, CUE_B], "voices": 1},
	},
}

var dir: AudioDirector
var now_ms := 0


func before_each() -> void:
	dir = AudioDirector.new()
	_host().add_child(dir)
	dir.setup(MIX, MUSIC, SFX)
	dir.set_process(false)
	dir.sfx.clock = func() -> int: return now_ms


func test_tables_name_real_files_scenes_and_flags() -> void:
	var music := AudioData.table(AudioData.MUSIC)
	var sfx := {"sfx": AudioData.sfx_rows()}
	var mix := AudioData.table(AudioData.MIX)
	assert_false(music.is_empty() or sfx.is_empty() or mix.is_empty(), "the three tables load")
	for id: String in music["cues"]:
		var files := AudioData.cue_files(music["cues"][id])
		assert_false(files.is_empty(), "cue %s names a stream" % id)
		for f in files:
			assert_true(ResourceLoader.exists(f), "cue %s: %s exists" % [id, f])
	for id: String in music.get("ambience", {}):
		for f in AudioData.cue_files(music["ambience"][id]):
			assert_true(ResourceLoader.exists(f), "bed %s: %s exists" % [id, f])
	var buses: Array[String] = ["Master"]
	for row: Dictionary in mix["buses"]:
		assert_true(buses.has(str(row["send"])), "bus %s sends to a bus defined before it" % row["name"])
		buses.append(str(row["name"]))
	for row: Dictionary in music["zones"]:
		assert_true(ResourceLoader.exists(str(row["scene"])), "zone %s exists" % row["scene"])
		if row.has("music") and str(row["music"]) != String(AudioData.SILENCE):
			assert_true((music["cues"] as Dictionary).has(str(row["music"])), "zone cue %s" % row["music"])
		for a: Variant in row.get("ambience", []):
			assert_true((music.get("ambience", {}) as Dictionary).has(str(a)), "zone bed %s" % a)
		for v: Dictionary in row.get("variants", []):
			assert_true(
				Game.registry.is_declared(StringName(str(v["flag"]))), "variant flag %s is declared" % v["flag"]
			)
	var battle := music["battle"] as Dictionary
	assert_true((music["cues"] as Dictionary).has(str(battle["default"])), "the default battle cue")
	for enc: String in battle["encounters"]:
		assert_true((music["cues"] as Dictionary).has(str(battle["encounters"][enc])), "battle cue for %s" % enc)
	for id: String in sfx["sfx"]:
		var row := sfx["sfx"][id] as Dictionary
		assert_true(buses.has(str(row.get("bus", "SFX"))), "%s plays on a real bus" % id)
		for f: Variant in row["files"]:
			assert_true(ResourceLoader.exists(str(f)), "sfx %s: %s exists" % [id, f])
	_done()


func test_zone_rows_resolve_with_flag_variants() -> void:
	var day := AudioData.zone_for(MUSIC, "res://x.tscn", func(_f: StringName) -> bool: return false)
	assert_eq(str(day["music"]), "a", "the row by day")
	assert_false(day.has("variants"), "variants are resolved away")
	var night := AudioData.zone_for(MUSIC, "res://x.tscn", func(f: StringName) -> bool: return f == &"night")
	assert_eq(str(night["music"]), "b", "the flag variant replaces the cue")
	assert_true(AudioData.zone_for(MUSIC, "res://y.tscn", func(_f: StringName) -> bool: return true).is_empty())
	assert_eq(AudioData.battle_cue(MUSIC, &"boss"), &"layers", "an encounter's own cue")
	assert_eq(AudioData.battle_cue(MUSIC, &"reef"), &"b", "else the default")
	_done()


func test_buses_are_built_once_with_their_sends() -> void:
	var before := AudioServer.bus_count
	AudioDirector.build_buses(MIX)
	assert_eq(AudioServer.bus_count, before, "building again adds nothing")
	var ui := AudioServer.get_bus_index(&"UI")
	assert_true(ui >= 0 and AudioServer.get_bus_index(&"SFX") >= 0, "UI and SFX exist")
	assert_eq(AudioServer.get_bus_send(ui), &"SFX", "UI sends to SFX")
	_done()


func test_music_crossfades_and_stops_the_old_cue() -> void:
	dir.flag_reader = func(_f: StringName) -> bool: return false
	dir.apply_zone("res://x.tscn")
	dir.flush_pending()  # zone music loads on a worker thread
	assert_eq(dir.music.current, &"a", "the zone's cue")
	assert_between(dir.music.gain(), 0.0, 0.01, "it fades in")
	var first := dir.music.player()
	_run(1.0)
	assert_between(dir.music.gain(), 0.99, 1.0, "in after crossfade_sec")
	assert_true(dir.play_music(&"b", 0.5))
	assert_eq(dir.music.current, &"b")
	assert_true(dir.music.player() != first, "the new cue plays on the other slot")
	assert_true(first.playing, "the old cue is still fading out")
	_run(0.6)
	assert_false(first.playing, "the old cue stops once silent")
	assert_true(dir.music.positions.has(&"a"), "a resumable cue keeps its place")
	assert_true(dir.play_music(&"b", 0.5), "the same cue again is left be")
	assert_false(dir.play_music(&"nope"), "an unknown cue is refused")
	dir.stop_music(0.2)
	_run(0.3)
	assert_eq(dir.music.current, &"")
	assert_false(dir.music.player() != null, "nothing plays after silence")
	_done()


func test_zone_music_loads_off_the_main_thread_then_plays() -> void:
	dir.play_music_async(&"b", 0.0)
	if dir.pending_cue() != &"":
		assert_eq(dir.music.current, &"", "nothing plays until the file has loaded")
		dir.flush_pending()
	assert_eq(dir.pending_cue(), &"", "nothing left waiting")
	assert_eq(dir.music.current, &"b", "then the cue plays")
	dir.play_music_async(&"a", 0.0)
	dir.stop_music(0.0)
	assert_eq(dir.pending_cue(), &"", "a stop drops a pending cue")
	_done()


func test_stems_fade_inside_one_synchronized_stream() -> void:
	assert_true(dir.play_music(&"layers", 0.0))
	var stream := dir.music.player().stream as AudioStreamSynchronized
	assert_true(stream != null and stream.stream_count == 2, "stems play as one synchronized stream")
	assert_eq(dir.music.stem_gain(0), 1.0, "start_stems are in")
	assert_eq(dir.music.stem_gain(1), 0.0, "the others wait")
	assert_eq(stream.get_sync_stream_volume(1), -80.0)
	dir.music.set_stem(1, true, 2.0)
	_run(1.0)
	assert_between(dir.music.stem_gain(1), 0.45, 0.55, "half way after half the fade")
	_run(1.1)
	assert_eq(dir.music.stem_gain(1), 1.0)
	assert_between(stream.get_sync_stream_volume(1), -0.01, 0.01, "the stem is at full level")
	assert_eq(dir.music.stem_gain(5), -1.0, "no such stem")
	_done()


func test_hold_silences_the_bed_and_lets_it_back() -> void:
	dir.play_music(&"a", 0.0)
	dir.music.set_hold(true, 0.0)
	_run(0.1)
	assert_eq(dir.music.player().volume_db, -80.0, "held silent")
	assert_true(dir.music.player().playing, "a hold keeps the cue running")
	dir.music.set_hold(false, 1.0)
	_run(0.5)
	assert_between(dir.music.hold, 0.45, 0.55)
	_run(0.6)
	assert_between(dir.music.player().volume_db, -0.01, 0.01, "back to full")
	_done()


func test_ducks_ramp_the_bus_and_release() -> void:
	dir.set_duck(AudioDirector.REASON_DIALOGUE, true)
	_run(0.125)
	assert_between(float(dir.bus_duck_db[&"Music"]), -2.05, -1.95, "half the duck in half its time")
	_run(0.2)
	assert_eq(float(dir.bus_duck_db[&"Music"]), -4.0)
	assert_between(AudioServer.get_bus_volume_db(AudioServer.get_bus_index(&"Music")), -4.01, -3.99, "on the bus")
	dir.set_user_volume(&"Music", -6.0)
	assert_between(AudioServer.get_bus_volume_db(AudioServer.get_bus_index(&"Music")), -10.01, -9.99, "adds")
	dir.set_duck(AudioDirector.REASON_DIALOGUE, false)
	_run(0.3)
	assert_eq(float(dir.bus_duck_db[&"Music"]), 0.0, "released")
	dir.set_user_volume(&"Music", 0.0)
	_done()


func test_volume_settings_scale_their_buses_live() -> void:
	var real := AudioData.table(AudioData.MIX)
	dir.mix = MIX.duplicate(true)
	dir.mix["volume_settings"] = real.get("volume_settings", {})
	var s := UiSettings.new()
	dir.follow_settings(s)
	assert_eq(float(dir.user_db.get(&"Music", 99.0)), 0.0, "1.0 is the asset's own level")
	assert_true(s.set_value(&"music_volume", 0.5))
	assert_between(float(dir.user_db[&"Music"]), -6.03, -6.0, "half is -6 dB, applied on change")
	assert_true(s.set_value(&"sfx_volume", 0.0))
	assert_eq(float(dir.user_db[&"SFX"]), -80.0, "0 is silence")
	assert_eq(float(dir.user_db[&"Ambience"]), -80.0, "the effects slider carries the ambience")
	for key: String in dir.mix["volume_settings"]:
		assert_true(s.settings().has(StringName(key)), "%s is an accessibility setting" % key)
	for bus: StringName in [&"Music", &"SFX", &"Ambience"]:
		dir.set_user_volume(bus, 0.0)
	_done()


func test_sfx_cooldown_voices_and_no_repeat() -> void:
	assert_true(dir.play_sfx(&"tick") != null, "plays")
	assert_true(dir.play_sfx(&"tick") == null, "a replay inside the cooldown is dropped")
	now_ms += 60
	var p := dir.play_sfx(&"tick")
	assert_true(p != null and p.bus == &"UI", "after the cooldown, on the row's bus")
	assert_true(dir.play_sfx(&"nope") == null, "unknown rows are refused")
	var last := ""
	for i in 12:
		now_ms += 1
		dir.play_sfx(&"pick")
		var f := str((dir.sfx.history.back() as Array)[1])
		assert_ne(f, last, "never the same file twice running")
		last = f
	var players := dir.sfx.get_children().filter(func(n: Node) -> bool: return n.name.begins_with("pick"))
	assert_eq(players.size(), 1, "voices = 1 keeps one player")
	_done()


func test_sequencer_players_route_and_hold_the_bed() -> void:
	dir.play_music(&"a", 0.0)
	var seq := CutsceneSequencer.new()
	_host().add_child(seq)
	var p := seq.music
	assert_true(p != null and p.name == &"Music", "the sequencer builds its music player on _ready")
	p.stream = load(CUE_B)
	var fx := AudioStreamPlayer.new()
	seq.add_child(fx)
	assert_eq(p.bus, &"Music", "the sequencer's music goes to the Music bus")
	assert_eq(fx.bus, &"SFX", "its @sfx players go to SFX")
	p.play()
	_run(0.6)
	assert_true(dir.music.is_held(), "the zone bed holds while the cutscene's music plays")
	p.stop()
	_run(2.1)
	assert_false(dir.music.is_held(), "and comes back when it stops")
	assert_between(dir.music.hold, 0.99, 1.0)
	seq.free()
	_done()


func _run(sec: float) -> void:
	var step := 1.0 / 60.0
	var t := 0.0
	while t < sec - 1e-6:
		dir.advance(minf(step, sec - t))
		t += step


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _done() -> void:
	dir.free()
