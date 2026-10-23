extends TestCase
## M1-CMB-03: the bestiary log (Bestiary) and its battle glue (BattleBestiary): Read and victories
## are logged, live battles roll their opening and log into Game.state, tests and fixtures do not.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const ENCOUNTER := &"sandbox_reef"

var ctl: BattleController
var _saved_state: GameStateData


func before_each() -> void:
	_saved_state = Game.state
	Game.state = GameStateData.new()
	ctl = null


# --- Bestiary ------------------------------------------------------------------------------------


func test_a_read_is_logged_once_and_defeats_add_up() -> void:
	var backing := {}
	var b := Bestiary.new(backing)
	assert_true(b.record_read(&"reef_crab"))
	assert_false(b.record_read(&"reef_crab"), "already read")
	assert_false(b.record_read(&""), "no id, nothing logged")
	b.record_defeated(&"reef_crab")
	b.record_defeated(&"reef_crab", 2)
	b.record_defeated(&"gull_harrier")
	b.record_defeated(&"gull_harrier", 0)
	b.record_defeated(&"gull_harrier", -3)
	b.record_defeated(&"", 4)
	assert_eq(backing, {"reef_crab": {"read": true, "defeated": 3}, "gull_harrier": {"defeated": 1}}, "in place")
	assert_true(b.is_read(&"reef_crab"))
	assert_false(b.is_read(&"gull_harrier"), "defeated but never read")
	assert_eq(b.defeated(&"reef_crab"), 3)
	assert_eq(b.defeated(&"lantern_eel"), 0)
	assert_eq(b.known_ids(), [&"gull_harrier", &"reef_crab"] as Array[StringName])
	var copy := b.entry(&"reef_crab")
	copy["defeated"] = 99
	assert_eq(b.defeated(&"reef_crab"), 3, "entry() is a copy")
	assert_eq(b.entry(&"nobody"), {})
	_done()


func test_a_damaged_entry_is_replaced_when_written() -> void:
	var b := Bestiary.new({"reef_crab": "junk"})
	assert_false(b.is_read(&"reef_crab"))
	assert_true(b.record_read(&"reef_crab"))
	assert_eq(b.entries["reef_crab"], {"read": true})
	_done()


func test_from_saved_makes_counts_ints_and_keeps_unknown_ids() -> void:
	var saved := {"reef_crab": {"read": true, "defeated": 3.0}, "retired_foe": {"read": false}, "bad": 7}
	var live := Bestiary.from_saved(saved)
	assert_eq(live, {"reef_crab": {"read": true, "defeated": 3}, "retired_foe": {"read": false}})
	assert_eq(typeof(live["reef_crab"]["defeated"]), TYPE_INT)
	assert_eq(Bestiary.from_saved("nope"), {})
	live["reef_crab"]["read"] = false
	assert_true(bool(saved["reef_crab"]["read"]), "a deep copy")

# --- BattleBestiary on a bare engine -------------------------------------------------------------
	_done()


func test_a_test_battle_opens_normally_and_logs_into_a_scratch_book() -> void:
	var e := _engine()
	var bb := BattleBestiary.new()
	bb.attach(e, false)
	assert_eq(e.opening, BattleOpening.NORMAL)
	e.begin()
	_read_first_foe(e)
	assert_eq(bb.last_reveal["enemy_id"], "reef_crab")
	assert_true(bb.book.is_read(&"reef_crab"))
	assert_eq(Game.state.bestiary, {}, "Game.state untouched")
	_done()


func test_a_live_battle_rolls_its_opening_and_logs_into_game_state() -> void:
	var e := _engine()
	var twin := _engine()
	var want := BattleOpening.choose(twin)
	var bb := BattleBestiary.new()
	bb.attach(e, true)
	assert_eq(e.opening, want, "BattleOpening.choose on the engine's rng")
	assert_eq(e.rng.state, twin.rng.state)
	e.begin()
	_read_first_foe(e)
	assert_true(Bestiary.new(Game.state.bestiary).is_read(&"reef_crab"))
	_done()


func test_a_live_battle_with_rolls_off_opens_normally_but_still_logs() -> void:
	var e := _engine()
	var before := e.rng.state
	var bb := BattleBestiary.new()
	bb.roll_openings = false
	bb.attach(e, true)
	assert_eq(e.opening, BattleOpening.NORMAL)
	assert_eq(e.rng.state, before, "no draw")
	assert_true(bb.book.entries == Game.state.bestiary, "logs into Game.state")
	_done()


func test_victory_logs_each_foe_and_other_endings_log_nothing() -> void:
	var e := _engine()
	var bb := BattleBestiary.new()
	bb.attach(e, true)
	e.battle_finished.emit(BattleEngine.OUTCOME_DEFEAT)
	e.battle_finished.emit(BattleEngine.OUTCOME_ESCAPED)
	assert_eq(Game.state.bestiary, {})
	e.battle_finished.emit(BattleEngine.OUTCOME_VICTORY)
	var b := Bestiary.new(Game.state.bestiary)
	for eid: StringName in [&"reef_crab", &"lantern_eel", &"gull_harrier"]:
		assert_eq(b.defeated(eid), 1, "%s" % eid)
	_done()


func test_weakness_text_names_the_elements() -> void:
	assert_eq(BattleBestiary.weakness_text({"affinities": {"weak": ["fire", "ice"]}}), "Weak to Fire, Ice")
	assert_eq(BattleBestiary.weakness_text({"affinities": {"weak": []}}), "No weakness found")
	assert_eq(BattleBestiary.weakness_text({}), "No weakness found")
	for el in BattleRead.ELEMENT_ORDER:
		var key := BattleBestiary.ELEMENT_KEY_PREFIX + String(el).to_upper()
		assert_ne(TranslationServer.translate(key), key, "%s is localized" % key)

# --- the live controller -------------------------------------------------------------------------
	_done()


func test_a_live_controller_logs_a_read_and_floats_the_weakness() -> void:
	_controller(true)
	assert_true(ctl.bestiary.engine == ctl.engine)
	_swap_in_ysolde()
	var foe := ctl.engine.enemies[0]
	var before := ctl.hud.recent_numbers.size()
	var r := ctl.act(&"read", [foe.id])
	assert_true(r.ok, "Ysolde reads %s" % foe.id)
	assert_true(Bestiary.new(Game.state.bestiary).is_read(&"reef_crab"))
	assert_eq(ctl.bestiary.last_reveal["lore_key"], "LORE_REEF_CRAB")
	var texts: Array = []
	for n: Dictionary in ctl.hud.recent_numbers.slice(before):
		texts.append(n["text"])
	assert_true(texts.has("Weak to Lightning"), "floated: %s" % [texts])
	_done()


func test_a_test_controller_keeps_the_normal_opening_and_the_save_clean() -> void:
	_controller(false)
	assert_eq(ctl.engine.opening, BattleOpening.NORMAL)
	_swap_in_ysolde()
	assert_true(ctl.act(&"read", [ctl.engine.enemies[0].id]).ok)
	assert_eq(Game.state.bestiary, {})
	_done()


func test_the_opening_caption_floats_once_over_the_first_to_act() -> void:
	_controller(true)
	var bb := ctl.bestiary
	var e := ctl.engine
	var key := str(BattleOpening.CAPTION_KEYS.get(e.opening, ""))
	assert_eq(_floated(TranslationServer.translate(key)), 1 if key != "" else 0, "live opening %s" % e.opening)
	# Force each special opening's caption on the started stage.
	for opening: StringName in [BattleOpening.PREEMPTIVE, BattleOpening.AMBUSH]:
		var text := TranslationServer.translate(str(BattleOpening.CAPTION_KEYS[opening]))
		var before := _floated(text)
		e.opening = opening
		bb._opening_shown = false
		bb._on_turn_started(e.current)
		bb._on_turn_started(e.current)
		assert_eq(_floated(text), before + 1, "%s floats once" % opening)
	e.opening = BattleOpening.NORMAL
	bb._opening_shown = false
	var count := ctl.hud.recent_numbers.size()
	bb._on_turn_started(e.current)
	assert_eq(ctl.hud.recent_numbers.size(), count, "a normal opening floats nothing")
	_done()


func test_nothing_floats_without_a_controller_or_with_numbers_off() -> void:
	var bb := BattleBestiary.new()
	bb.attach(_engine(), false)
	bb.engine.opening = BattleOpening.AMBUSH
	bb.engine.begin()  # turn_started: no controller, no float, no error
	_controller(false)
	ctl.show_damage_numbers = false
	var count := ctl.hud.recent_numbers.size()
	ctl.bestiary._opening_shown = false
	ctl.engine.opening = BattleOpening.AMBUSH
	ctl.bestiary._on_turn_started(ctl.engine.current)
	assert_eq(ctl.hud.recent_numbers.size(), count)
	_done()


func _floated(text: String) -> int:
	var n := 0
	for rec: Dictionary in ctl.hud.recent_numbers:
		if rec["text"] == text:
			n += 1
	return n


# --- helpers -------------------------------------------------------------------------------------


func _engine() -> BattleEngine:
	var e := BattleEngine.new()
	var active: Array[StringName] = [&"ysolde", &"asha"]
	var reserve: Array[StringName] = [&"rhen", &"toma"]
	e.setup(BattleDB.load_default(), active, reserve, ENCOUNTER, SEED)
	return e


## Plays turns until Ysolde reads the first living foe (others attack it; foes act on their own).
func _read_first_foe(e: BattleEngine) -> void:
	var guard := 0
	while e.outcome == &"" and guard < 50:
		guard += 1
		if not e.is_party_turn():
			e.run_enemy_turn()
			continue
		var crab: Array[BattleCombatant] = [e.enemies[0]]
		if e.current.id == &"ysolde":
			assert_true(e.perform(&"read", crab).ok)
			return
		e.perform(&"attack", [e.living_foes_of(e.current)[-1]] as Array[BattleCombatant])
	fail("Ysolde never got a turn")


## Swaps Ysolde in on the first party turn and plays on until it is hers.
func _swap_in_ysolde() -> void:
	var guard := 0
	while guard < 50:
		guard += 1
		var e := ctl.engine
		if e.current != null and e.current.id == &"ysolde" and e.is_party_turn():
			return
		if e.is_party_turn() and e.find(&"ysolde") in e.party_reserve:
			ctl.swap_members(e.current.id, &"ysolde")
			continue
		if e.is_party_turn():
			ctl.act(&"attack", [e.living_foes_of(e.current)[-1].id])
	fail("Ysolde never got a turn")


func _controller(persist: bool, start: bool = true) -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = persist
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	if not start:
		return
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	ctl.start_battle(active, reserve, ENCOUNTER, SEED, null)


func _done() -> void:
	if ctl != null:
		ctl.get_parent().remove_child(ctl)
		ctl.free()
		ctl = null
	Game.state = _saved_state
