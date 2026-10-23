extends TestCase
## M2-CMB-01: Swell mode unlocks through play (swell.json "unlocks", formulas.md § Swell), the
## saved record BattleSwell hands to save v6 (load_saved / to_saved), and the mode API the Swell
## mode menu uses (mode_rows, progress_toward, mode_unlocked). Headless on test_battle_swell.gd's
## fixture DB and a fixture config, so tuning swell.json never breaks these rules.

const Fixture := preload("res://tests/unit/test_battle_swell.gd")
const BALLAST := &"ballast"
const WAKE := &"wake"
const TETHER := &"tether"
const SALVE := &"salve"

var engine: BattleEngine
var swell: BattleSwell
var _unlocked: Array[StringName] = []


func before_each() -> void:
	engine = null
	swell = null
	_unlocked = []


# --- counting -------------------------------------------------------------------------------


func test_hits_taken_in_ballast_unlock_tether_at_the_count() -> void:
	_start()
	_hit_rhen()
	_hit_rhen()
	assert_false(swell.unlocked.has(TETHER))
	assert_eq(swell.progress, {"tether_from_ballast": 2})
	assert_eq(swell.progress_toward(TETHER), {"count": 2, "need": 3})
	_hit_rhen()
	assert_true(swell.unlocked.has(TETHER), "the third hit unlocks it")
	assert_eq(_unlocked, [TETHER] as Array[StringName], "mode_unlocked fires once")
	_hit_rhen()
	assert_eq(swell.progress, {"tether_from_ballast": 3}, "an unlocked mode stops counting")
	assert_eq(swell.progress_toward(TETHER), {"count": 3, "need": 3})
	assert_true(swell.set_mode(_rhen(), TETHER), "now choosable")


func test_while_mode_counts_only_in_that_mode_and_only_swell_heroes_count() -> void:
	_start()
	assert_true(swell.set_mode(_rhen(), WAKE))
	for i in 5:
		_hit_rhen()
	assert_false(swell.unlocked.has(TETHER), "hits taken in Wake do not count towards Tether")
	_emit(&"brute#1", [_hit(&"mate", 10)])
	assert_eq(swell.progress, {}, "mate has no Swell, so its hits count for nobody")
	assert_true(swell.set_mode(_rhen(), BALLAST))
	_emit(&"brute#1", [_hit(&"rhen", 0, false)])
	assert_eq(swell.progress, {}, "a miss is not a hit taken")
	_hit_rhen()
	assert_eq(swell.progress, {"tether_from_ballast": 1})


func test_healing_items_unlock_salve_in_any_mode() -> void:
	_start()
	assert_true(swell.set_mode(_rhen(), WAKE))
	_heal_item(&"rhen")
	assert_eq(swell.progress_toward(SALVE), {"count": 1, "need": 2})
	_heal_item(&"mate")
	assert_eq(swell.progress_toward(SALVE), {"count": 1, "need": 2}, "only a Swell hero's item counts")
	_heal_item(&"rhen")
	assert_true(swell.unlocked.has(SALVE))
	assert_eq(swell.progress_toward(&"ballast"), {"count": 0, "need": 0}, "no rule unlocks a starting mode")


func test_unlock_mode_notifies_but_loading_a_record_does_not() -> void:
	_start()
	assert_true(swell.unlock_mode(SALVE))
	assert_eq(_unlocked, [SALVE] as Array[StringName])
	var other := BattleSwell.new(_config())
	other.mode_unlocked.connect(func(m: StringName) -> void: _unlocked.append(m))
	other.load_saved({"unlocked": ["tether"]})
	assert_true(other.unlocked.has(TETHER))
	assert_eq(_unlocked, [SALVE] as Array[StringName], "a loaded record is not a new unlock")


# --- the saved record -----------------------------------------------------------------------


func test_the_record_round_trips_and_keeps_ids_the_data_no_longer_knows() -> void:
	var s := BattleSwell.new(_config())
	assert_eq(s.to_saved(), {"unlocked": [], "progress": {}}, "starting modes are not listed")
	s.load_saved(
		{"unlocked": ["tether", "retired_mode", "tether"], "progress": {"salve_from_items": 1.0, "old_rule": 4.0}}
	)
	assert_eq(s.unlocked, [BALLAST, WAKE, TETHER] as Array[StringName], "known ids become choosable")
	assert_eq(s.progress_toward(SALVE), {"count": 1, "need": 2}, "JSON float counts come back as ints")
	assert_eq(typeof(s.progress["salve_from_items"]), TYPE_INT)
	var out := s.to_saved()
	assert_eq(out["unlocked"], ["tether", "retired_mode"] as Array[String])
	assert_eq(out["progress"], {"salve_from_items": 1, "old_rule": 4}, "unknown rule ids are kept as saved")
	s.load_saved({"unlocked": "not a list", "progress": []})
	assert_eq(s.to_saved()["unlocked"], ["tether", "retired_mode"] as Array[String], "a malformed record adds nothing")


func test_attach_keeps_a_carried_mode_only_while_it_is_choosable() -> void:
	engine = BattleEngine.new()
	engine.setup(Fixture._db(), Fixture._ids([&"rhen", &"mate"]), Fixture._ids([&"spare"]), &"brutes", 1)
	_rhen().swell_mode = TETHER
	engine.find(&"spare").swell_mode = &"no_such_mode"
	swell = BattleSwell.new(_config())
	swell.attach(engine)
	assert_eq(_rhen().swell_mode, BALLAST, "a locked mode falls back to the default")
	assert_eq(engine.find(&"spare").swell_mode, BALLAST, "so does an unknown one")
	engine = BattleEngine.new()
	engine.setup(Fixture._db(), Fixture._ids([&"rhen", &"mate"]), Fixture._ids([&"spare"]), &"brutes", 1)
	_rhen().swell_mode = TETHER
	swell = BattleSwell.new(_config())
	swell.load_saved({"unlocked": ["tether"]})
	swell.attach(engine)
	assert_eq(_rhen().swell_mode, TETHER, "an unlocked carried mode is kept")


# --- the menu API ---------------------------------------------------------------------------


func test_mode_rows_list_the_choosable_modes_in_data_order() -> void:
	_start()
	swell.unlock_mode(SALVE)
	var rows := swell.mode_rows(_rhen())
	var ids: Array = rows.map(func(r: Dictionary) -> StringName: return r["id"])
	assert_eq(ids, [BALLAST, WAKE, SALVE], "data order, locked Tether left out")
	assert_eq(rows[0]["name_key"], "K_BALLAST")
	assert_eq(rows[0]["desc_key"], "K_BALLAST_DESC")
	assert_eq(rows[0]["trigger"], &"damage_taken")
	assert_eq(rows.map(func(r: Dictionary) -> bool: return r["current"]), [true, false, false])
	assert_eq(swell.mode_rows(engine.find(&"mate")), [] as Array[Dictionary], "no Swell, no modes")
	assert_eq(swell.mode_rows_for(&"nobody", BALLAST), [] as Array[Dictionary])
	assert_eq(swell.mode_rows_for(&"rhen", WAKE)[1]["current"], true, "out of battle: the saved mode")


func test_config_problem_names_a_broken_swell_table() -> void:
	assert_eq(BattleSwell.config_problem(_config()), "")
	assert_eq(BattleSwell.config_problem(BattleSwell.load_config()), "", "the shipped swell.json is sound")
	assert_true(BattleSwell.config_problem({}).contains("lists no modes"), "missing or torn")
	assert_true(BattleSwell.config_problem({"modes": []}).contains("lists no modes"), "hollow")
	var cfg := _config()
	cfg["default_mode"] = "gone"
	assert_true(BattleSwell.config_problem(cfg).contains("default_mode"))
	cfg["modes"] = "not a list"
	assert_true(BattleSwell.config_problem(cfg).contains("lists no modes"))


func test_input_row_of_finds_a_heros_input() -> void:
	var live := BattleSwell.load_config()
	assert_eq(BattleSwell.input_row_of(live, &"rhen")["kind"], "timing_ring")
	assert_eq(BattleSwell.input_row_of(live, &"asha")["kind"], "chant")
	assert_eq(BattleSwell.input_row_of(live, &"toma")["kind"], "brace")
	assert_eq(BattleSwell.input_row_of(live, &"ysolde")["kind"], "glyph")
	assert_eq(BattleSwell.input_row_of(live, &"nobody"), {})
	var cfg := _config()
	(cfg["heroes"] as Array).append({"id": "lost", "input": "no_such_input"})
	assert_eq(BattleSwell.input_row_of(cfg, &"lost"), {})


func test_bonus_counts_at_most_the_grades_an_input_can_give() -> void:
	var ring := {"kind": "timing_ring", "beats": 2, "grades": {"perfect": 30}}
	var three := {"grades": [&"perfect", &"perfect", &"perfect"]}
	assert_eq(BattleSwell.bonus_pct(ring, three), 60, "a ring of two beats counts two grades")
	var brace := {"kind": "brace", "impacts": [0.1], "grades": {"braced": 10, "perfect": 60}}
	var many := {"grades": [&"braced", &"perfect", &"perfect", &"perfect"]}
	assert_eq(BattleSwell.bonus_pct(brace, many), 70, "one blow and the release")
	var odd := {"kind": "mystery", "beats": 1, "grades": {"perfect": 30}}
	assert_eq(BattleSwell.bonus_pct(odd, three), 30, "an unknown kind falls back to beats")


# --- helpers --------------------------------------------------------------------------------


func _start() -> void:
	engine = BattleEngine.new()
	engine.setup(Fixture._db(), Fixture._ids([&"rhen", &"mate"]), Fixture._ids([&"spare"]), &"brutes", 1)
	swell = BattleSwell.new(_config())
	swell.attach(engine)
	swell.mode_unlocked.connect(func(m: StringName) -> void: _unlocked.append(m))
	engine.begin()


func _rhen() -> BattleCombatant:
	return engine.find(&"rhen")


func _hit_rhen() -> void:
	_emit(&"brute#1", [_hit(&"rhen", 10)])


func _heal_item(actor_id: StringName) -> void:
	var r := ActionResult.new()
	r.actor_id = actor_id
	r.item_id = &"salt_tonic"
	r.hits.append(_hit(actor_id, -20))
	engine.action_resolved.emit(r)


func _emit(actor_id: StringName, hits: Array) -> void:
	var r := ActionResult.new()
	r.actor_id = actor_id
	for h: Variant in hits:
		r.hits.append(h as Dictionary)
	engine.action_resolved.emit(r)


static func _hit(target_id: StringName, amount: int, landed: bool = true) -> Dictionary:
	return {"target_id": target_id, "hit": landed, "crit": false, "amount": amount if landed else 0}


static func _config() -> Dictionary:
	var cfg := Fixture._config()
	for m: Dictionary in cfg["modes"]:
		m["name_key"] = "K_" + str(m["id"]).to_upper()
		m["desc_key"] = "K_" + str(m["id"]).to_upper() + "_DESC"
	cfg["unlocks"] = [
		{"id": "tether_from_ballast", "mode": "tether", "event": "damage_taken", "while_mode": "ballast", "count": 3},
		{"id": "salve_from_items", "mode": "salve", "event": "heal_item", "count": 2},
	]
	return cfg
