extends TestCase
## M1-CMB-08: live battles start from Game.state.party_vitals and write them back
## (BattleVitals; ARC-06's EventBus.battle_party_returned is consumed). The battle-start lineup
## rule for carried KO and stone is in docs/kb/design/battle_ctb.md "Carried vitals".

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const ENCOUNTER := &"sandbox_reef"

var ctl: BattleController
var bdb: BattleDB
var _saved_state: GameStateData
var _returned: Array = []


func before_each() -> void:
	bdb = BattleDB.load_default()
	_saved_state = Game.state
	Game.state = GameStateData.new()
	_returned = []
	EventBus.battle_party_returned.connect(_on_returned)
	ctl = null


func _on_returned(encounter: StringName, outcome: StringName, party: Array) -> void:
	_returned.append([encounter, outcome, party.size()])


# --- the lineup rule (pure) --------------------------------------------------------------


func test_a_standing_party_keeps_its_lineup() -> void:
	var e := _engine({})
	assert_eq(BattleVitals.line_up(e.party_active, e.party_reserve), {})
	_done()


func test_a_fallen_active_member_trades_places_with_the_first_living_reserve() -> void:
	var e := _engine({"asha": {"hp": 0}, "toma": {"hp": 0}})
	var order := BattleVitals.line_up(e.party_active, e.party_reserve)
	assert_eq(order[BattleVitals.KEY_ACTIVE], [&"rhen", &"ysolde"] as Array[StringName], "toma is down too")
	assert_eq(order[BattleVitals.KEY_RESERVE], [&"toma", &"asha"] as Array[StringName], "asha takes ysolde's place")
	assert_true((order[BattleVitals.KEY_RAISE] as Array).is_empty())
	_done()


func test_stone_counts_as_fallen_and_each_reserve_is_used_once() -> void:
	var e := _engine({"rhen": {"statuses": ["petrify"]}, "asha": {"hp": 0}})
	var order := BattleVitals.line_up(e.party_active, e.party_reserve)
	assert_eq(order[BattleVitals.KEY_ACTIVE], [&"toma", &"ysolde"] as Array[StringName])
	assert_eq(order[BattleVitals.KEY_RESERVE], [&"rhen", &"asha"] as Array[StringName])
	_done()


func test_a_fallen_member_with_no_living_reserve_keeps_its_slot() -> void:
	var e := _engine({"asha": {"hp": 0}, "toma": {"hp": 0}, "ysolde": {"hp": 0}})
	assert_eq(BattleVitals.line_up(e.party_active, e.party_reserve), {}, "rhen stands, so nothing moves")
	_done()


func test_a_party_with_nobody_standing_gets_up_with_one_hp() -> void:
	var vitals := {"rhen": {"hp": 0}, "asha": {"statuses": ["petrify"]}, "toma": {"hp": 0}, "ysolde": {"hp": 0}}
	var e := _engine(vitals)
	var order := BattleVitals.line_up(e.party_active, e.party_reserve)
	assert_eq(order[BattleVitals.KEY_RAISE], [&"rhen", &"asha"] as Array[StringName])
	Game.state.party_vitals = vitals
	var live := BattleEngine.new()
	BattleVitals.setup(live, bdb, _plan(), null, true)
	assert_eq(live.find(&"rhen").hp, 1)
	assert_eq(live.find(&"asha").hp, live.find(&"asha").max_hp, "stone breaks; HP was never lost")
	assert_false(live.find(&"asha").has_status(&"petrify"))
	assert_eq(live.find(&"toma").hp, 0, "the reserve stays down")
	live.begin()
	assert_eq(live.outcome, &"", "the fight does not open already lost")
	_done()


# --- BattleVitals.setup on a bare engine ------------------------------------------------


func test_setup_without_carry_ignores_saved_vitals() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 5}}
	var e := BattleEngine.new()
	BattleVitals.setup(e, bdb, _plan(), null, false)
	assert_eq(e.find(&"rhen").hp, e.find(&"rhen").max_hp)
	_done()


func test_setup_with_carry_reads_saved_hp_and_lines_up() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 5, "mp": 1}, "asha": {"hp": 0}}
	var e := BattleEngine.new()
	BattleVitals.setup(e, bdb, _plan(), null, true)
	assert_eq(_ids(e.party_active), [&"rhen", &"toma"] as Array[StringName])
	assert_eq(_ids(e.party_reserve), [&"asha", &"ysolde"] as Array[StringName])
	assert_eq(e.find(&"rhen").hp, 5)
	assert_eq(e.find(&"rhen").mp, 1)
	assert_false(e.find(&"asha").is_alive(), "asha waits in the reserve, still KO'd")
	_done()


func test_send_back_only_after_victory_or_escape() -> void:
	var e := _engine({})
	assert_false(BattleVitals.send_back(e), "an unfinished battle sends nothing")
	e.outcome = BattleEngine.OUTCOME_DEFEAT
	assert_false(BattleVitals.send_back(e), "a defeat sends nothing")
	e.outcome = BattleEngine.OUTCOME_ESCAPED
	e.find(&"rhen").hp = 7
	assert_true(BattleVitals.send_back(e))
	assert_eq(_returned, [[ENCOUNTER, BattleEngine.OUTCOME_ESCAPED, 4]])
	assert_eq(Game.state.vitals_of(&"rhen"), {"hp": 7}, "Game recorded the escape")
	_done()


# --- the live controller ----------------------------------------------------------------


func test_live_battle_starts_from_carried_vitals() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 40, "statuses": ["poison"]}, "asha": {"mp": 0}}
	_controller(true)
	var rhen := ctl.engine.find(&"rhen")
	assert_eq(rhen.hp, 40)
	assert_true(rhen.has_status(&"poison"), "poison follows the party in")
	assert_eq(ctl.engine.find(&"asha").mp, 0)
	assert_eq(ctl.engine.find(&"toma").hp, ctl.engine.find(&"toma").max_hp, "no entry = full")
	_done()


func test_a_ko_carried_into_a_live_battle_is_swapped_out_before_the_first_turn() -> void:
	Game.state.party_vitals = {"asha": {"hp": 0}}
	_controller(true)
	assert_eq(_ids(ctl.engine.party_active), [&"rhen", &"toma"] as Array[StringName])
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	assert_eq(ctl.hud.party.rows().size(), 2, "the panel shows the lined-up party")
	_done()


func test_victory_writes_vitals_back_and_a_shrine_heals_them() -> void:
	_controller(true)
	_play_elegant_answer()
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_eq(_returned.size(), 1, "battle_party_returned once per battle")
	for c in ctl.engine.party_active + ctl.engine.party_reserve:
		var v := Game.state.vitals_of(c.id)
		assert_eq(int(v.get("hp", c.max_hp)), c.hp, "%s HP saved" % c.id)
		assert_eq(int(v.get("mp", c.max_mp)), c.mp, "%s MP saved" % c.id)
	assert_false(Game.state.party_vitals.is_empty(), "the reef leaves marks")
	# The next battle (Retry) starts from what was saved.
	var hurt := _hp_by_id()
	ctl.hud.result.finish_open()  # the numbers finish counting first (a first Confirm would only skip the count)
	_press(&"ui_accept")
	assert_eq(ctl.battles_started, 2)
	for cid: StringName in hurt:
		var c := ctl.engine.find(cid)
		if c.is_alive():
			assert_eq(c.hp, int(hurt[cid]), "%s starts the next fight as it ended the last" % cid)
	# A shrine rest fills everyone again. Swell gauges and modes stay (M2-ARC-01: a rest is not a battle).
	EventBus.party_full_heal_requested.emit(&"test_shrine")
	for key: Variant in Game.state.party_vitals:
		var left: Array = (Game.state.party_vitals[key] as Dictionary).keys()
		left.sort()
		assert_true(left.all(func(k: Variant) -> bool: return k in ["swell", "swell_mode"]), "%s: %s" % [key, left])
	_done()


func test_defeat_records_nothing_and_retry_replays_the_same_start() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 300}}
	_controller(true)
	var guard := 0
	while ctl.engine.outcome == &"" and guard < 200:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_DEFEAT)
	assert_true(_returned.is_empty(), "a defeat is not written back")
	assert_eq(Game.state.party_vitals, {"rhen": {"hp": 300}})
	_press(&"ui_accept")
	assert_eq(ctl.engine.find(&"rhen").hp, 300, "Retry starts from the same vitals")
	_done()


func test_tests_and_previews_never_touch_vitals() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 40}}
	_controller(false)
	assert_eq(ctl.engine.find(&"rhen").hp, ctl.engine.find(&"rhen").max_hp)
	_play_elegant_answer()
	assert_true(_returned.is_empty())
	assert_eq(Game.state.party_vitals, {"rhen": {"hp": 40}})
	_done()


func test_capture_fixtures_ignore_vitals() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 40}}
	_controller(true, false)
	ctl.start_fixture(BattleFixture.load_fixture(&"victory"))
	assert_eq(ctl.engine.find(&"rhen").hp, ctl.engine.find(&"rhen").max_hp, "fixtures set their own opening")
	_done()


# --- helpers -----------------------------------------------------------------------------


func _plan() -> Dictionary:
	return {
		"active": [&"rhen", &"asha"] as Array[StringName],
		"reserve": [&"toma", &"ysolde"] as Array[StringName],
		"encounter": ENCOUNTER,
		"seed": SEED,
	}


func _engine(vitals: Dictionary) -> BattleEngine:
	var st := GameStateData.new()
	st.party_vitals = vitals
	var e := BattleEngine.new()
	e.party_modifier = Game.vitals_modifier(st)
	var plan := _plan()
	e.setup(bdb, plan["active"], plan["reserve"], ENCOUNTER, SEED)
	return e


func _controller(persist: bool, start: bool = true) -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = persist
	# Vitals, not openings (M1-CMB-03): a rolled ambush would play enemy turns before the checks.
	ctl.bestiary.roll_openings = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	if not start:
		return
	var p := LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	for cid: StringName in [&"rhen", &"asha", &"toma", &"ysolde"]:
		p.add_character(cid)
	var plan := _plan()
	ctl.start_battle(plan["active"], plan["reserve"], ENCOUNTER, SEED, p)


func _play_elegant_answer() -> void:
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


func _hp_by_id() -> Dictionary:
	var out := {}
	for c in ctl.engine.party_active + ctl.engine.party_reserve:
		out[c.id] = c.hp
	return out


func _ids(list: Array[BattleCombatant]) -> Array[StringName]:
	var out: Array[StringName] = []
	for c in list:
		out.append(c.id)
	return out


func _press(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	ctl.handle_input(ev)


func _done() -> void:
	EventBus.battle_party_returned.disconnect(_on_returned)
	if ctl != null:
		ctl.get_parent().remove_child(ctl)
		ctl.free()
		ctl = null
	Game.state = _saved_state
