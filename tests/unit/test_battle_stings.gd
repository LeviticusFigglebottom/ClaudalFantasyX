extends TestCase
## M3-AUD-18: stings on the battle presentation's announcements. StingAudio plays battle_stings.json's row for an
## EventBus.dialogue_event (the encounter's own row first), swaps in the version without sub-bass under reduced
## audio, holds the boss intro's music duck for its time and lets it go, ignores events with no row; every row
## resolves and imports; and the director listens to EventBus and drives its ducks.

var played: Array[StringName] = []
var duck_calls: Array = []
var reduced := false


func before_each() -> void:
	super()
	played.clear()
	duck_calls.clear()
	reduced = false


func test_every_row_resolves_and_imports() -> void:
	var table := AudioData.table(AudioData.BATTLE_STINGS)
	var rows := AudioData.sfx_rows()
	var ids: Array[String] = []
	for row: Variant in (table.get("events", {}) as Dictionary).values():
		ids.append(str((row as Dictionary).get("sfx", "")))
		for v: Variant in ((row as Dictionary).get("by_arg", {}) as Dictionary).values():
			ids.append(str(v))
	for v: Variant in (table.get("reduced", {}) as Dictionary).values():
		ids.append(str(v))
	assert_true(ids.size() >= 6, "the tide line, the bark, two boss stings and their soft versions")
	for id in ids:
		assert_true(rows.has(id), "%s is an sfx row" % id)
		var files := (rows.get(id, {}) as Dictionary).get("files", []) as Array
		for f: Variant in files:
			assert_true(load(str(f)) is AudioStream, "%s imports" % f)
	_done()


func test_events_play_their_rows() -> void:
	var s := _listener()
	assert_eq(s.on_event(&"battle_stinger", ["ch01_tideline"]), &"sting_tideline", "the tide line rises")
	assert_eq(s.on_event(&"battle_bark", ["ch01_tideline", "LINE", "SPEAKER"]), &"sting_bark", "the bark's breath")
	assert_eq(s.on_event(&"boss_intro", ["unnamed_boss", "TITLE"]), &"sting_boss", "a boss with no sting of its own")
	assert_eq(s.on_event(&"boss_intro", ["ch01_hullgnaw", "TITLE"]), &"sting_boss_hullgnaw", "Hullgnaw has its own")
	assert_eq(s.on_event(&"boss_intro", ["drownbell", "TITLE"]), &"sting_boss_bell", "the Drownbell has its own")
	assert_eq(s.on_event(&"line_shown", []), &"", "an event with no row plays nothing")
	assert_eq(
		played,
		(
			[&"sting_tideline", &"sting_bark", &"sting_boss", &"sting_boss_hullgnaw", &"sting_boss_bell"]
			as Array[StringName]
		)
	)
	_done()


## M4-A2P-092: an Act II boss staged before its encounter exists (choreo.json boss_intro.by_enemy) is named by its
## intro's title key; a written encounter's own row still wins over the title key.
func test_a_staged_boss_is_named_by_its_title_key() -> void:
	var s := _listener()
	var staged := ["mangrove_drowner", "lamp_engine", "avalanche_ram", "wakefin"]
	for boss: String in staged:
		var title := "BOSS_TITLE_%s" % boss.to_upper()
		assert_eq(s.on_event(&"boss_intro", ["ch1x_unwritten", title]), StringName("sting_boss_" + boss), boss)
	assert_eq(
		s.on_event(&"boss_intro", ["ch01_hullgnaw", "BOSS_TITLE_WAKEFIN"]),
		&"sting_boss_hullgnaw",
		"the encounter's own row wins"
	)
	reduced = true
	assert_eq(s.on_event(&"boss_intro", ["x", "BOSS_TITLE_WAKEFIN"]), &"sting_boss_wakefin_soft", "reduced audio")
	reduced = false
	_done()


func test_reduced_audio_swaps_the_boss_stings() -> void:
	var s := _listener()
	reduced = true
	assert_eq(s.on_event(&"boss_intro", ["unnamed_boss", "TITLE"]), &"sting_boss_soft", "no sub-bass")
	assert_eq(
		s.on_event(&"boss_intro", ["ch05_cinder_matron", "TITLE"]),
		&"sting_boss_cinder_matron_soft",
		"nor in a boss's own"
	)
	assert_eq(s.on_event(&"boss_intro", ["drownbell", "TITLE"]), &"sting_boss_bell_soft", "nor for the bell")
	assert_eq(s.on_event(&"battle_stinger", ["x"]), &"sting_tideline", "a row without a soft version stays")
	_done()


func test_the_boss_intro_holds_its_duck_then_lets_go() -> void:
	var s := _listener()
	var sec := float(((s.data["events"] as Dictionary)["boss_intro"] as Dictionary)["duck_sec"])
	s.on_event(&"boss_intro", ["ch04_spar_wraith", "TITLE"])
	assert_eq(duck_calls, [[&"boss_intro", true]], "the music dips under the card")
	s.advance(sec * 0.5)
	assert_eq(duck_calls.size(), 1, "held while the card shows")
	s.advance(sec)
	assert_eq(duck_calls, [[&"boss_intro", true], [&"boss_intro", false]], "and let go after duck_sec")
	assert_true(s.held.is_empty(), "nothing left held")
	s.on_event(&"battle_stinger", ["x"])
	assert_eq(duck_calls.size(), 2, "the tide line ducks nothing")
	_done()


func test_the_director_listens_and_ducks() -> void:
	var dir := AudioDirector.new()
	_host().add_child(dir)
	dir.set_process(false)
	assert_true(EventBus.dialogue_event.is_connected(dir.stings.on_event), "the director hears dialogue_event")
	dir.stings.player = func(id: StringName) -> void: played.append(id)
	dir.stings.on_event(&"boss_intro", ["ch01_hullgnaw", "TITLE"])
	assert_eq(played, [&"sting_boss_hullgnaw"] as Array[StringName], "the boss's own sting")
	assert_true(dir.ducks.has(&"boss_intro"), "the director's boss_intro duck is on")
	assert_true(dir.duck_target_db(&"Music") < 0.0, "and dips the music")
	dir.advance(10.0)
	assert_false(dir.ducks.has(&"boss_intro"), "released in advance()")
	var stings := dir.stings
	_host().remove_child(dir)
	assert_false(EventBus.dialogue_event.is_connected(stings.on_event), "and stops listening when it leaves")
	dir.free()
	_done()


# --------------------------------------------------------------------------- helpers


func _listener() -> StingAudio:
	var s := StingAudio.new(AudioData.table(AudioData.BATTLE_STINGS))
	s.player = func(id: StringName) -> void: played.append(id)
	s.ducker = func(reason: StringName, on: bool) -> void: duck_calls.append([reason, on])
	s.reduced = func() -> bool: return reduced
	return s


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _done() -> void:
	pass
