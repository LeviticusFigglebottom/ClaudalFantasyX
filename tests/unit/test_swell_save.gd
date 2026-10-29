extends TestCase
## M2-ARC-01: Swell across battles and in saves (save v6; ADR 0018 Amendment 6). Gauges and modes
## ride in party_vitals entries (out through EventBus.battle_party_returned, in through
## Game.vitals_modifier), the party's unlocked modes and unlock counts in GameStateData.swell (out
## through EventBus.battle_swell_returned). A v5 save migrates to an empty record, SaveShape checks
## the new fields, and the data-tables gate's `swell` check closes saving while swell.json is broken.

const TEST_DIR := "user://test_swell_save"
const T_SAVED := 1792489500
const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const ENCOUNTER := &"sandbox_reef"
const RECORD := {"unlocked": ["tether", "retired_mode"], "progress": {"salve_from_items": 2, "old_rule": 7}}
const VITALS := {"rhen": {"hp": 40, "swell": 60, "swell_mode": "wake"}, "asha": {"swell": 100}}

var ctl: BattleController
var _saved_dir := ""
var _saved_clock: Callable
var _saved_enabled := true
var _saved_state: GameStateData
var _swell_returned: Array = []


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	_saved_clock = SaveSystem.clock
	_saved_enabled = SaveSystem.autosave_enabled
	_saved_state = Game.state
	SaveSystem.save_dir = TEST_DIR
	SaveSystem.clock = func() -> int: return T_SAVED
	SaveSystem.autosave_enabled = true
	SaveSystem._health = null
	_clear(TEST_DIR)
	Game.state = GameStateData.new()
	_swell_returned = []
	EventBus.battle_swell_returned.connect(_on_swell_returned)
	ctl = null


func _on_swell_returned(record: Dictionary) -> void:
	_swell_returned.append(record)


# --- GameStateData ----------------------------------------------------------------------------


func test_state_round_trips_gauges_modes_and_the_record() -> void:
	var st := GameStateData.new()
	st.party_vitals = VITALS.duplicate(true)
	st.swell = RECORD.duplicate(true)
	var d := st.to_dict()
	assert_eq(d["swell"], RECORD)
	var back := GameStateData.from_dict(_norm(d))
	assert_eq(back.party_vitals, VITALS, "swell and swell_mode survive the vitals clean-up")
	assert_eq(typeof(back.party_vitals["rhen"]["swell"]), TYPE_INT, "JSON floats come back as ints")
	assert_eq(back.swell, RECORD)
	assert_eq(typeof(back.swell["progress"]["old_rule"]), TYPE_INT)
	assert_eq(GameStateData.from_dict({}).swell, {}, "no record: empty")
	var junk := GameStateData.from_dict(
		{"party_vitals": {"rhen": {"swell": "full", "swell_mode": 3}, "asha": {"swell": 0}}, "swell": "x"}
	)
	assert_eq(junk.party_vitals, {}, "badly typed or empty Swell values are dropped, not crashed on")
	assert_eq(junk.swell, {})
	_done()


func test_record_vitals_keeps_a_gauge_and_a_chosen_mode() -> void:
	var st := GameStateData.new()
	var none: Array[StringName] = []
	st.record_vitals(&"rhen", 100, 100, 10, 10, none, none, 0, &"ballast", &"ballast")
	assert_eq(st.party_vitals, {}, "full, empty gauge, default mode: no entry")
	st.record_vitals(&"rhen", 100, 100, 10, 10, none, none, 35, &"wake", &"ballast")
	assert_eq(st.vitals_of(&"rhen"), {"swell": 35, "swell_mode": "wake"})
	assert_eq(st.swell_of(&"rhen"), 35)
	assert_eq(st.swell_mode_of(&"rhen", &"ballast"), &"wake")
	assert_eq(st.swell_mode_of(&"asha", &"ballast"), &"ballast", "no entry: the default")
	st.record_vitals(&"toma", 50, 100, 10, 10, none, none)
	assert_eq(st.vitals_of(&"toma"), {"hp": 50}, "callers that pass no Swell store none")
	_done()


func test_apply_puts_the_gauge_and_mode_back_and_clamps_the_gauge() -> void:
	var st := GameStateData.new()
	st.party_vitals = {"rhen": {"swell": 150, "swell_mode": "wake"}, "asha": {"hp": 0, "swell": 40}}
	var rhen := BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, {"hp": 100})
	st.apply_vitals_to(rhen, 3)
	assert_eq(rhen.swell, Formulas.SWELL_MAX)
	assert_eq(rhen.swell_mode, &"wake")
	var asha := BattleCombatant.from_dict(&"asha", BattleCombatant.TEAM_PARTY, {"hp": 100})
	st.apply_vitals_to(asha, 3)
	assert_eq(asha.swell, 40, "a fallen hero keeps its points (formulas.md § Swell)")
	_done()


func test_a_shrine_rest_keeps_gauges_and_modes() -> void:
	var st := GameStateData.new()
	st.party_vitals = {"rhen": {"hp": 10, "mp": 0, "swell": 70, "swell_mode": "wake"}, "toma": {"hp": 3}}
	assert_eq(st.full_heal([] as Array[StringName]), [&"rhen", &"toma"] as Array[StringName])
	assert_eq(st.party_vitals, {"rhen": {"swell": 70, "swell_mode": "wake"}}, "HP and MP fill, Swell stays")
	_done()


func test_set_swell_mode_leaves_the_rest_of_the_entry_alone() -> void:
	var st := GameStateData.new()
	st.party_vitals = {"rhen": {"hp": 10}}
	st.set_swell_mode(&"rhen", &"wake", &"ballast")
	assert_eq(st.vitals_of(&"rhen"), {"hp": 10, "swell_mode": "wake"})
	st.set_swell_mode(&"rhen", &"ballast", &"ballast")
	assert_eq(st.vitals_of(&"rhen"), {"hp": 10}, "the default is stored as no value")
	st.set_swell_mode(&"asha", &"wake", &"ballast")
	st.set_swell_mode(&"asha", &"", &"ballast")
	assert_false(st.party_vitals.has("asha"), "an entry left empty is removed")
	_done()


# --- Game: out through EventBus -------------------------------------------------------------


func test_game_records_gauges_from_the_party_and_the_record_from_its_signal() -> void:
	var rhen := BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, {"hp": 100, "mp": 10})
	rhen.swell = 55
	rhen.swell_mode = &"wake"
	var asha := BattleCombatant.from_dict(&"asha", BattleCombatant.TEAM_PARTY, {"hp": 100, "mp": 10})
	asha.swell_mode = BattleSwell.load_config()["default_mode"]
	EventBus.battle_party_returned.emit(ENCOUNTER, BattleEngine.OUTCOME_VICTORY, [rhen, asha])
	assert_eq(Game.state.party_vitals, {"rhen": {"swell": 55, "swell_mode": "wake"}})
	EventBus.battle_swell_returned.emit(RECORD.duplicate(true))
	assert_eq(Game.state.swell, RECORD)
	_done()


func test_game_writes_no_record_while_swell_json_is_broken() -> void:
	Game.state.swell = RECORD.duplicate(true)
	var kept: Dictionary = BattleSwell._cache.get(BattleSwell.DATA_PATH, {})
	BattleSwell._cache[BattleSwell.DATA_PATH] = {}
	Game.record_swell({"unlocked": [], "progress": {}})
	BattleSwell._cache[BattleSwell.DATA_PATH] = kept
	assert_eq(Game.state.swell, RECORD, "a broken table never empties the record")
	_done()


## M2-NIT-03 (review-sweep-M on M2-ARC-01 S2): both halves refuse alike. While swell.json is broken,
## record_party still writes HP and MP but keeps each member's saved gauge and mode.
func test_game_keeps_the_saved_gauges_while_swell_json_is_broken() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 50, "swell": 30, "swell_mode": "tether"}}
	var rhen := BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, {"stats": {"hp": 100, "mp": 10}})
	rhen.hp = 70
	rhen.swell = 80
	rhen.swell_mode = &"wake"
	var asha := BattleCombatant.from_dict(&"asha", BattleCombatant.TEAM_PARTY, {"hp": 100, "mp": 10})
	asha.swell = 40
	var kept: Dictionary = BattleSwell._cache.get(BattleSwell.DATA_PATH, {})
	BattleSwell._cache[BattleSwell.DATA_PATH] = {}
	Game.record_party(ENCOUNTER, BattleEngine.OUTCOME_VICTORY, [rhen, asha])
	BattleSwell._cache[BattleSwell.DATA_PATH] = kept
	assert_eq(
		Game.state.party_vitals, {"rhen": {"hp": 70, "swell": 30, "swell_mode": "tether"}}, "HP moves, Swell stays"
	)
	_done()


# --- saves -----------------------------------------------------------------------------------


func test_save_and_load_keep_swell() -> void:
	var st := GameStateData.new()
	st.party_ids = [&"rhen"] as Array[StringName]
	st.party_vitals = VITALS.duplicate(true)
	st.swell = RECORD.duplicate(true)
	assert_eq(SaveSystem.save_to_slot(1, st), OK)
	var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SaveSystem.slot_path(1)))
	assert_eq(int(raw["version"]), 6)
	var back := SaveSystem.load_from_slot(1)
	assert_true(back != null)
	if back != null:
		assert_eq(back.party_vitals, VITALS)
		assert_eq(back.swell, RECORD)
	_done()


func test_a_v5_save_migrates_to_an_empty_record() -> void:
	var v5 := {"version": 5, "state": {"party_vitals": {"rhen": {"hp": 7}}, "bestiary": {}}}
	var migrated := SaveSystem.migrate(v5)
	assert_eq(int(migrated["version"]), SaveSystem.SAVE_VERSION)
	assert_eq(migrated["state"]["swell"], {"unlocked": [], "progress": {}})
	assert_eq(migrated["state"]["party_vitals"], {"rhen": {"hp": 7}}, "vitals need no change")
	var kept := SaveSystem._migrate_v5_to_v6({"version": 5, "state": {"swell": RECORD}})
	assert_eq(kept["state"]["swell"], RECORD, "an existing record is not replaced")
	var v4 := {"version": 4, "state": {"currency": 5}}
	var chained := SaveSystem.migrate(v4)
	assert_eq(int(chained["version"]), 6, "v4 -> v5 -> v6")
	assert_eq(chained["state"]["bestiary"], {})
	assert_eq(chained["state"]["swell"], {"unlocked": [], "progress": {}})
	var back: GameStateData = SaveSystem.deserialize(v5)
	assert_true(back != null)
	if back != null:
		assert_eq(back.vitals_of(&"rhen"), {"hp": 7})
		assert_eq(back.swell, {"unlocked": [], "progress": {}})
	_done()


func test_shape_rejects_malformed_swell_fields() -> void:
	assert_eq(SaveShape.problem({"swell": RECORD, "party_vitals": VITALS}), "")
	assert_eq(SaveShape.problem({"swell": {}}), "")
	assert_eq(SaveShape.problem({"swell": {"note": 1}}), "", "other keys are ignored")
	var bad := {
		"swell: expected a Dictionary": {"swell": []},
		"swell.unlocked: expected an Array": {"swell": {"unlocked": "tether"}},
		"swell.unlocked[0]: expected a String": {"swell": {"unlocked": [3]}},
		"swell.progress: expected a Dictionary": {"swell": {"progress": []}},
		"swell.progress.r: expected a whole number": {"swell": {"progress": {"r": -1}}},
		"swell.progress.q: expected a whole number": {"swell": {"progress": {"q": 1.5}}},
		"party_vitals.rhen.swell: expected a whole number": {"party_vitals": {"rhen": {"swell": -5}}},
		"party_vitals.asha.swell_mode: expected a String": {"party_vitals": {"asha": {"swell_mode": 2}}},
	}
	for want: String in bad:
		var got := SaveShape.problem(bad[want])
		assert_true(got.begins_with(want), "%s (got %s)" % [want, got])
	_write_raw(SaveSystem.slot_path(2), JSON.stringify({"version": 6, "state": {"swell": {"unlocked": [1]}}}))
	assert_eq(SaveSystem.load_from_slot(2), null, "a malformed record reads as corrupt")
	_done()


func test_the_gate_checks_swell_json_for_saved_swell() -> void:
	assert_true(SaveSystem.data_health().tables().has(DataHealth.SWELL))
	assert_eq(SaveSystem.data_health().problem_of(DataHealth.SWELL), "", "the shipped swell.json is sound")
	var st := GameStateData.new()
	st.party_vitals = VITALS.duplicate(true)
	st.swell = RECORD.duplicate(true)
	assert_eq(SaveSystem.save_to_slot(1, st), OK)
	var slot_text := FileAccess.get_file_as_string(SaveSystem.slot_path(1))
	var broken := {"torn or missing": {}, "hollow": {"modes": [], "default_mode": "ballast"}}
	broken["no default"] = {"modes": [{"id": "ballast"}], "default_mode": "gone"}
	for how: String in broken:
		SaveSystem.data_health().swell_config = broken[how]
		SaveSystem.data_health().swell_loaded = true
		assert_ne(SaveSystem.data_health().problem_of(DataHealth.SWELL, st), "", "%s: the swell check fails" % how)
		assert_true(SaveSystem.data_tables_problem(st).contains("swell: "), "%s: the gate names it" % how)
		var back := SaveSystem.load_from_slot(1)
		assert_true(back != null, "%s: the save still loads" % how)
		if back != null:
			assert_eq(back.party_vitals, VITALS, "%s: loaded exactly as saved" % how)
			assert_eq(back.swell, RECORD)
			assert_eq(SaveSystem.save_to_slot(1, back), ERR_UNCONFIGURED, "%s: saving is refused" % how)
		assert_eq(FileAccess.get_file_as_string(SaveSystem.slot_path(1)), slot_text, "%s: slot untouched" % how)
		SaveSystem._health = null
		assert_eq(SaveSystem.data_tables_problem(st), "", "%s: mended" % how)
	assert_eq(SaveSystem.save_to_slot(1, SaveSystem.load_from_slot(1)), OK, "saves again once mended")
	_done()


# --- BattleSwellCarry: the field API ---------------------------------------------------------


func test_field_menus_list_and_choose_modes_from_the_saved_record() -> void:
	var st := GameStateData.new()
	var ids: Callable = func(rows: Array[Dictionary]) -> Array:
		return rows.map(func(r: Dictionary) -> StringName: return r["id"])
	assert_eq(ids.call(BattleSwellCarry.mode_rows(&"rhen", st)), [&"ballast", &"wake"], "the starting modes")
	assert_false(BattleSwellCarry.set_mode(&"rhen", &"tether", st), "locked: refused")
	assert_eq(st.party_vitals, {}, "a refusal saves nothing")
	st.swell = {"unlocked": ["tether"]}
	assert_eq(ids.call(BattleSwellCarry.mode_rows(&"rhen", st)), [&"ballast", &"wake", &"tether"])
	assert_true(BattleSwellCarry.set_mode(&"rhen", &"tether", st))
	assert_eq(st.swell_mode_of(&"rhen"), &"tether")
	var rows := BattleSwellCarry.mode_rows(&"rhen", st)
	assert_eq(rows.map(func(r: Dictionary) -> bool: return r["current"]), [false, false, true])
	assert_true(BattleSwellCarry.set_mode(&"rhen", &"ballast", st))
	assert_eq(st.party_vitals, {}, "back to the default: no entry")
	assert_false(BattleSwellCarry.set_mode(&"kerrid", &"wake", st), "no Swell row")
	assert_eq(BattleSwellCarry.mode_rows(&"kerrid", st), [] as Array[Dictionary])
	Game.state.swell = {"unlocked": ["salve"]}
	assert_true(BattleSwellCarry.rules().unlocked.has(&"salve"), "defaults to the live Game.state")
	_done()


func test_attach_loads_the_record_only_when_carrying() -> void:
	var st := GameStateData.new()
	st.swell = {"unlocked": ["tether"], "progress": {"salve_from_items": 3}}
	var e := BattleEngine.new()
	e.setup(BattleDB.load_default(), [&"rhen"] as Array[StringName], [] as Array[StringName], ENCOUNTER, SEED)
	var carried := BattleSwell.new(BattleSwell.load_config())
	BattleSwellCarry.attach(carried, e, true, st)
	assert_true(carried.unlocked.has(&"tether"))
	assert_eq(carried.progress_toward(&"salve")["count"], 3)
	assert_true(carried.engine == e)
	var scratch := BattleSwell.new(BattleSwell.load_config())
	BattleSwellCarry.attach(scratch, e, false, st)
	assert_false(scratch.unlocked.has(&"tether"), "tests and fixtures start from the data")
	_done()


# --- the live controller ---------------------------------------------------------------------


func test_a_live_battle_carries_gauges_modes_and_unlocks_through_a_victory() -> void:
	Game.state.party_vitals = {"rhen": {"swell": 60, "swell_mode": "tether"}, "toma": {"swell": 20}}
	Game.state.swell = {"unlocked": ["tether"], "progress": {"old_rule": 7}}
	_controller(true)
	var rhen := ctl.engine.find(&"rhen")
	assert_eq(rhen.swell, 60, "the gauge comes back in through Game.vitals_modifier")
	assert_eq(rhen.swell_mode, &"tether", "and the mode, choosable because the record unlocked it")
	assert_eq(ctl.engine.find(&"toma").swell, 20, "reserve heroes too")
	assert_true(ctl.swell.unlocked.has(&"tether"))
	assert_true(ctl.hud.party.row_for(&"rhen").swell_gauge() != null)
	_play_to_victory()
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_eq(_swell_returned.size(), 1, "the record goes out once, with the party")
	for c in ctl.engine.party_active + ctl.engine.party_reserve:
		assert_eq(Game.state.swell_of(c.id), c.swell, "%s's gauge is saved as it ended" % c.id)
	assert_eq(Game.state.swell_mode_of(&"rhen"), &"tether")
	assert_eq(Game.state.swell["unlocked"], ["tether"] as Array[String])
	assert_eq(int(Game.state.swell["progress"]["old_rule"]), 7, "unknown rule ids are kept")
	var ended := Game.state.swell_of(&"rhen")
	ctl.hud.result.finish_open()  # the numbers finish counting first (a first Confirm would only skip the count)
	_press(&"ui_accept")
	assert_eq(ctl.battles_started, 2)
	assert_eq(ctl.engine.find(&"rhen").swell, ended, "Retry starts from the saved gauge")
	_done()


## M2-NIT-03 (review-sweep-M on M2-ARC-01 S1): an escape writes gauges, modes and the record back,
## as a victory does (formulas.md § Swell: "a won or escaped battle").
func test_an_escape_carries_gauges_modes_and_the_record() -> void:
	Game.state.party_vitals = {"rhen": {"swell": 60, "swell_mode": "tether"}, "toma": {"swell": 20}}
	Game.state.swell = {"unlocked": ["tether"], "progress": {"old_rule": 7}}
	_controller(true)
	var guard := 0
	while ctl.engine.outcome == &"" and guard < 200:
		guard += 1
		if not ctl.try_escape() and ctl.engine.outcome == &"" and not ctl.engine.is_party_turn():
			ctl.engine.run_enemy_turn()
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_ESCAPED)
	assert_eq(_swell_returned.size(), 1, "the record goes out on an escape too")
	for c in ctl.engine.party_active + ctl.engine.party_reserve:
		assert_eq(Game.state.swell_of(c.id), c.swell, "%s's gauge is saved as it ended" % c.id)
	assert_eq(Game.state.swell_mode_of(&"rhen"), &"tether")
	assert_eq(Game.state.swell["unlocked"], ["tether"] as Array[String])
	assert_eq(int(Game.state.swell["progress"]["old_rule"]), 7)
	_done()


func test_a_defeat_carries_nothing_and_tests_never_touch_swell() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 300, "swell": 10}}
	Game.state.swell = {"unlocked": [], "progress": {}}
	_controller(true)
	var guard := 0
	while ctl.engine.outcome == &"" and guard < 200:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_DEFEAT)
	assert_true(_swell_returned.is_empty(), "a defeat is not written back")
	assert_eq(Game.state.party_vitals, {"rhen": {"hp": 300, "swell": 10}})
	assert_eq(Game.state.swell, {"unlocked": [], "progress": {}})
	_free()
	Game.state.party_vitals = {"rhen": {"swell": 90}}
	_controller(false)
	assert_eq(ctl.engine.find(&"rhen").swell, 0, "persist_progress off: the saved gauge is not read")
	_play_to_victory()
	assert_true(_swell_returned.is_empty())
	assert_eq(Game.state.party_vitals, {"rhen": {"swell": 90}})
	_done()


# --- helpers ---------------------------------------------------------------------------------


func _controller(persist: bool) -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = persist
	ctl.bestiary.roll_openings = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var p := LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	for cid: StringName in [&"rhen", &"asha", &"toma", &"ysolde"]:
		p.add_character(cid)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	ctl.start_battle(active, reserve, ENCOUNTER, SEED, p)


## Toma in for Asha, then attack the weakest foe (test_battle_vitals.gd's elegant answer).
func _play_to_victory() -> void:
	var guard := 0
	while ctl.engine.outcome == &"" and guard < 300:
		guard += 1
		var e := ctl.engine
		if e.find(&"asha") in e.party_active and e.find(&"toma") in e.party_reserve:
			ctl.swap_members(&"asha", &"toma")
			continue
		var foes := e.living_foes_of(e.current)
		var weakest := foes[0]
		for f in foes:
			if f.hp < weakest.hp:
				weakest = f
		ctl.act(&"attack", [weakest.id])


func _press(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	ctl.handle_input(ev)


func _norm(v: Variant) -> Variant:
	return JSON.parse_string(JSON.stringify(v))


func _write_raw(path: String, text: String) -> void:
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()


func _free() -> void:
	if ctl != null:
		ctl.get_parent().remove_child(ctl)
		ctl.free()
		ctl = null


func _done() -> void:
	_free()
	EventBus.battle_swell_returned.disconnect(_on_swell_returned)
	SaveSystem.cancel_pending_autosave()
	SaveSystem._health = null
	_clear(TEST_DIR)
	SaveSystem.save_dir = _saved_dir
	SaveSystem.clock = _saved_clock
	SaveSystem.autosave_enabled = _saved_enabled
	Game.state = _saved_state


func _clear(dir_path: String) -> void:
	if not DirAccess.dir_exists_absolute(dir_path):
		return
	for sub in DirAccess.get_directories_at(dir_path):
		_clear(dir_path.path_join(sub))
	for f in DirAccess.get_files_at(dir_path):
		DirAccess.remove_absolute(dir_path.path_join(f))
	DirAccess.remove_absolute(dir_path)
