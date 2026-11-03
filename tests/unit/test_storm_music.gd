extends TestCase
## M3-AUD-865 (the human's playtest FAST-TRACK, 2026-11-03): inside the Undertow's storm the fights play
## battle_storm, never the uplifting default, and the field between them is the storm's (undertow_storm), not the
## town's bed. The battle cue's order (encounter, arena, the field zone's `battle`, default), the director keeping the
## field's storm cue across the swap into the battle scene, and a `from_loop` cue starting at its loop, not its intro.

const MUSIC := AudioData.MUSIC
const MIX := AudioData.MIX
const ORUVEL := "res://game/levels/ch01/oruvel/oruvel.tscn"
const CORROW := "res://game/levels/ch08/corrow/corrow.tscn"
const COILSPIRE := "res://game/levels/ch08/coilspire/coilspire.tscn"
const BATTLE_SCENE := "res://game/flow/field_battle.tscn"
const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const RISING_SIDECAR := "res://assets/audio/music/undertow_rising_p1.loop.json"
const TABLE := {
	"cues": {"d": {}, "boss": {}, "storm": {}},
	"battle": {"default": "d", "encounters": {"bell": "boss"}, "arenas": {"wall_storm": "storm"}},
}


func test_the_battle_cue_order() -> void:
	assert_eq(AudioData.battle_cue(TABLE, &"bell", "wall_storm", &"storm"), &"boss", "a boss's own cue first")
	assert_eq(AudioData.battle_cue(TABLE, &"crab", "wall_storm"), &"storm", "then its arena's")
	assert_eq(AudioData.battle_cue(TABLE, &"crab", "beach", &"storm"), &"storm", "then the field zone's")
	assert_eq(AudioData.battle_cue(TABLE, &"crab", "beach"), &"d", "else the default")
	assert_eq(AudioData.battle_cue(TABLE, &"crab"), &"d", "an arena-less call as before")


func test_the_storm_fights_never_play_the_default() -> void:
	var music := AudioData.table(MUSIC)
	var default := StringName(str((music["battle"] as Dictionary)["default"]))
	assert_eq(AudioData.battle_cue(music, &"ch01_scuttlers", "oruvel_raft_morning"), &"battle_storm")
	assert_eq(AudioData.battle_cue(music, &"ch01_hullgnaw", "oruvel_raft_morning", &"battle_storm"), &"hullgnaw")
	assert_eq(AudioData.battle_cue(music, &"ch08_stair_hold_1", "seawall_stairhead_storm"), &"seawall_hold")
	assert_eq(
		AudioData.battle_cue(music, &"ch08_headland_gulls", "coilspire_headland_path", &"battle_storm"),
		&"battle_storm",
		"the stormgulls after the beacon"
	)
	assert_eq(
		AudioData.battle_cue(music, &"ch08_headland_gulls", "coilspire_headland_path"),
		default,
		"before it, an ordinary fight"
	)
	assert_true(AudioData.cue_files(AudioData.cue(music, &"battle_storm"))[0].ends_with("storm_battle.ogg"))


func test_the_storm_variants() -> void:
	var music := AudioData.table(MUSIC)
	var none := func(_f: StringName) -> bool: return false
	var gulls := func(f: StringName) -> bool: return f == &"ch01_gulls_cried"
	var beacon := func(f: StringName) -> bool: return f == &"ch08_beacon_opened"
	var fell := func(f: StringName) -> bool: return f in [&"ch08_beacon_opened", &"ch08_wall_fell"]
	assert_eq(str(AudioData.zone_for(music, ORUVEL, none)["music"]), "oruvel", "the raft-town before the gulls")
	assert_false(AudioData.zone_for(music, ORUVEL, none).has("battle"), "and its fights are ordinary")
	var storm := AudioData.zone_for(music, ORUVEL, gulls)
	assert_eq(str(storm["music"]), "undertow_storm", "after the gulls the field is the storm's")
	assert_eq(str(storm["battle"]), "battle_storm", "and so are its fights")
	for scene: String in [CORROW, COILSPIRE]:
		var row := AudioData.zone_for(music, scene, beacon)
		assert_eq(str(row["music"]), "undertow_storm", scene)
		assert_eq(str(row["battle"]), "battle_storm", scene)
	assert_eq(str(AudioData.zone_for(music, CORROW, fell)["music"]), "corrow_aftermath", "after the wall falls")


func test_the_director_keeps_the_field_storm_across_the_battle_swap() -> void:
	var dir := AudioDirector.new()
	_host().add_child(dir)
	dir.setup(AudioData.table(MIX), AudioData.table(MUSIC), {"sfx": AudioData.sfx_rows()})
	dir.set_process(false)
	dir.flag_reader = func(f: StringName) -> bool: return f == &"ch01_gulls_cried"
	dir.apply_zone(ORUVEL)
	assert_eq(dir.field_battle_cue, &"battle_storm", "the storm variant's fights")
	dir.apply_zone(BATTLE_SCENE)
	assert_eq(dir.field_battle_cue, &"battle_storm", "the battle scene's row (no music) keeps the field's")
	dir.flush_pending()
	dir.apply_zone(ORUVEL)
	dir.flush_pending()
	assert_eq(dir.music.current, &"undertow_storm", "back in the field: the storm, not the town's bed")
	assert_between(dir.music.started_from, 17.0, 18.0, "from the Rising's loop, not its town-tune intro")
	dir.flag_reader = func(_f: StringName) -> bool: return false
	dir.apply_zone(HALUNA)
	assert_eq(dir.field_battle_cue, &"", "a calm zone clears it")
	dir.stop_all_players()
	dir.free()


func test_from_loop_starts_at_the_sidecar_loop() -> void:
	var meta: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(RISING_SIDECAR))
	var row := AudioData.cue(AudioData.table(MUSIC), &"undertow_storm")
	assert_true(bool(row.get("from_loop", false)))
	assert_between(
		MusicDeck.loop_start_of(row),
		float(meta["loop_offset_seconds"]) - 0.001,
		float(meta["loop_offset_seconds"]) + 0.001,
		"the loop start"
	)
	assert_eq(MusicDeck.loop_start_of({"file": "res://assets/audio/music/hush_coda.ogg"}), 0.0, "no sidecar: 0")
	var deck := MusicDeck.new()
	_host().add_child(deck)
	assert_true(deck.play(&"undertow_storm", row, 0.0))
	assert_true(deck.started_from > 17.0, "a fresh start skips the intro")
	deck.stop(0.0)
	deck.positions[&"undertow_storm"] = 40.0
	deck.play(&"undertow_storm", row, 0.0)
	assert_true(deck.started_from > 30.0, "a resume carries on where it stopped")
	deck.stop(0.0)
	deck.free()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
