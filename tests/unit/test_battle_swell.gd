extends TestCase
## M1-CMB-04: Swell gauges (BattleSwell, formulas.md § Swell). Headless on a fixture DB and a
## fixture config, so tuning swell.json or the sandbox tables never breaks these rules. The
## interactive input's result is passed in, exactly as the HUD's timing ring hands it over.

const BALLAST := &"ballast"
const WAKE := &"wake"
const TETHER := &"tether"
const SALVE := &"salve"
const DIVE := &"lamp_dive"
const ALL_PERFECT := {"cancelled": false, "grades": [&"perfect", &"perfect", &"perfect"]}
const ALL_MISS := {"cancelled": false, "grades": [&"miss", &"miss", &"miss"]}

var engine: BattleEngine
var swell: BattleSwell


class FakeItems:
	extends BattleItemSource
	var actions: Dictionary = {}

	func action_for(item_id: StringName) -> ItemBattleAction:
		return actions.get(item_id, null)

	func count(item_id: StringName) -> int:
		return 1 if actions.has(item_id) else 0

	func consume(_item_id: StringName) -> bool:
		return true


func before_each() -> void:
	engine = BattleEngine.new()
	swell = null


# --- setup and modes ----------------------------------------------------------------------


func test_attach_gives_swell_heroes_the_default_mode_and_nobody_else() -> void:
	_start()
	assert_eq(_rhen().swell_mode, BALLAST)
	assert_eq(engine.find(&"spare").swell_mode, BALLAST, "reserve heroes too")
	assert_eq(engine.find(&"mate").swell_mode, &"", "no swell.json row, no gauge")
	assert_eq(engine.enemies[0].swell_mode, &"", "enemies have no Swell")
	assert_false(swell.has_swell(engine.enemies[0]))
	assert_false(swell.has_swell(null))


func test_attach_keeps_a_mode_already_chosen_and_connects_once() -> void:
	engine.setup(_db(), _ids([&"rhen", &"mate"]), _ids([&"spare"]), &"brutes", 1)
	_rhen().swell_mode = WAKE
	swell = BattleSwell.new(_config())
	swell.attach(engine)
	swell.attach(engine)
	engine.begin()
	assert_eq(_rhen().swell_mode, WAKE)
	_emit(&"brute#1", [_hit(&"rhen", 40)])
	assert_eq(_rhen().swell, 0, "Wake ignores damage taken")
	assert_eq(engine.action_resolved.get_connections().size(), 1)


func test_set_mode_takes_only_unlocked_modes_and_keeps_the_points() -> void:
	_start()
	_rhen().swell = 40
	assert_true(swell.set_mode(_rhen(), WAKE))
	assert_eq(_rhen().swell, 40, "changing mode keeps the gauge")
	assert_false(swell.set_mode(_rhen(), TETHER), "locked until unlocked through play")
	assert_false(swell.set_mode(engine.find(&"mate"), WAKE), "no Swell")
	assert_false(swell.unlock_mode(&"nonsense"))
	assert_true(swell.unlock_mode(TETHER))
	assert_false(swell.unlock_mode(TETHER), "already unlocked")
	assert_true(swell.set_mode(_rhen(), TETHER))
	assert_eq(_rhen().swell_mode, TETHER)


# --- fill modes ---------------------------------------------------------------------------


func test_ballast_fills_from_hp_the_owner_loses() -> void:
	_start()
	_emit(&"brute#1", [_hit(&"rhen", 95)])
	assert_eq(_rhen().swell, Formulas.swell_gain(95, _rhen().max_hp, 120))
	_emit(&"brute#1", [_hit(&"mate", 95)])
	assert_eq(_rhen().swell, Formulas.swell_gain(95, _rhen().max_hp, 120), "an ally's hurt is not Ballast")
	_emit(&"brute#1", [_hit(&"rhen", 0, false)])
	assert_eq(_rhen().swell, Formulas.swell_gain(95, _rhen().max_hp, 120), "a miss feeds nothing")


func test_wake_fills_from_hp_the_owner_takes_from_foes() -> void:
	_start()
	swell.set_mode(_rhen(), WAKE)
	var foe := engine.enemies[0]
	_emit(&"rhen", [_hit(foe.id, 152)])
	assert_eq(_rhen().swell, Formulas.swell_gain(152, foe.max_hp, 50))
	_emit(&"mate", [_hit(foe.id, 152)])
	assert_eq(_rhen().swell, Formulas.swell_gain(152, foe.max_hp, 50), "only the owner's own blows")


func test_wake_fills_from_a_real_attack() -> void:
	_start()
	swell.set_mode(_rhen(), WAKE)
	assert_eq(engine.current, _rhen(), "the fast hero opens")
	var foe := engine.enemies[0]
	var r := engine.perform(&"attack", _one(foe))
	assert_true(r.ok)
	var dealt := int(r.hits[0]["amount"])
	assert_true(dealt > 0)
	assert_eq(_rhen().swell, Formulas.swell_gain(dealt, foe.max_hp, 50))


func test_tether_fills_when_another_active_ally_is_hurt() -> void:
	_start()
	swell.unlock_mode(TETHER)
	swell.set_mode(_rhen(), TETHER)
	_emit(&"brute#1", [_hit(&"rhen", 95)])
	assert_eq(_rhen().swell, 0, "the owner's own hurt is not Tether")
	var mate := engine.find(&"mate")
	_emit(&"brute#1", [_hit(&"mate", 95)])
	assert_eq(_rhen().swell, Formulas.swell_gain(95, mate.max_hp, 60))
	_rhen().swell = 0
	_rhen().hp = 0
	_emit(&"brute#1", [_hit(&"mate", 95)])
	assert_eq(_rhen().swell, 0, "a fallen owner feels nothing")


func test_salve_fills_a_flat_amount_per_healing_item_use() -> void:
	_start()
	swell.unlock_mode(SALVE)
	swell.set_mode(_rhen(), SALVE)
	_rhen().hp = 100
	var bag := FakeItems.new()
	bag.actions[&"tonic"] = _item(&"tonic", [{"type": "heal_hp", "amount": 50}])
	bag.actions[&"spark"] = _item(&"spark", [{"type": "restore_mp", "amount": 5}])
	var r := engine.use_item(&"tonic", _one(_rhen()), bag)
	assert_true(r.ok)
	assert_eq(_rhen().swell, 20, "one heal item: the mode's flat points")
	_emit(&"rhen", [_hit(&"rhen", -50)])
	assert_eq(_rhen().swell, 20, "a heal skill is not an item")
	var revive := ActionResult.new()
	revive.actor_id = &"rhen"
	revive.item_id = &"wick"
	revive.hits.append({"target_id": &"mate", "hit": true, "amount": 0, "revived": true})
	engine.action_resolved.emit(revive)
	assert_eq(_rhen().swell, 40, "a revive counts as healing")
	var mp_only := ActionResult.new()
	mp_only.actor_id = &"rhen"
	mp_only.item_id = &"spark"
	mp_only.hits.append({"target_id": &"rhen", "hit": true, "amount": 0})
	engine.action_resolved.emit(mp_only)
	assert_eq(_rhen().swell, 40, "an item that restores no HP is not a heal")


func test_the_gauge_never_passes_its_maximum_and_unknown_actors_are_ignored() -> void:
	_start()
	_rhen().swell = Formulas.SWELL_MAX - 1
	_emit(&"brute#1", [_hit(&"rhen", 300)])
	assert_eq(_rhen().swell, Formulas.SWELL_MAX)
	_rhen().swell = 0
	_emit(&"ghost", [_hit(&"rhen", 300)])
	_emit(&"brute#1", [_hit(&"ghost", 300)])
	assert_eq(_rhen().swell, 0)


# --- techniques ---------------------------------------------------------------------------


func test_a_technique_needs_a_full_gauge_and_a_refusal_costs_nothing() -> void:
	_start()
	var actor := _rhen()
	actor.swell = Formulas.SWELL_MAX - 1
	assert_false(swell.is_ready(actor))
	var r := swell.perform(DIVE, _one(engine.enemies[0]), ALL_PERFECT)
	assert_eq(r.fail_reason, BattleSwell.FAIL_NOT_FULL)
	assert_eq(engine.current, actor, "the turn is still Rhen's")
	assert_eq(swell.refusal(&"attack"), BattleSwell.FAIL_UNKNOWN, "a plain skill is not a technique")
	assert_eq(swell.perform(&"attack", _one(engine.enemies[0]), ALL_PERFECT).fail_reason, BattleSwell.FAIL_UNKNOWN)


func test_a_cancelled_input_keeps_the_gauge_and_the_turn() -> void:
	_start()
	var actor := _rhen()
	actor.swell = Formulas.SWELL_MAX
	assert_true(swell.is_ready(actor))
	var r := swell.perform(DIVE, _one(engine.enemies[0]), {"cancelled": true, "grades": []})
	assert_false(r.ok)
	assert_eq(r.fail_reason, BattleSwell.FAIL_CANCELLED)
	assert_eq(actor.swell, Formulas.SWELL_MAX)
	assert_eq(engine.current, actor)
	assert_eq(engine.enemies[0].hp, engine.enemies[0].max_hp)


func test_the_input_bonus_scales_the_technique_exactly() -> void:
	var dealt_perfect := _dive_damage(ALL_PERFECT)
	var dealt_miss := _dive_damage(ALL_MISS)
	var expected := _row_damage(Formulas.swell_power(12, 90))
	assert_eq(dealt_perfect, expected, "three perfect beats: power 12 -> 22")
	assert_eq(dealt_miss, _row_damage(12), "a missed input keeps the base power")
	assert_true(dealt_perfect > dealt_miss)


func test_a_technique_empties_the_gauge_ends_the_turn_and_feeds_nothing() -> void:
	_start()
	swell.set_mode(_rhen(), WAKE)
	var actor := _rhen()
	actor.swell = Formulas.SWELL_MAX
	var now := engine.now
	var r := swell.perform(DIVE, _one(engine.enemies[0]), ALL_PERFECT)
	assert_true(r.ok)
	assert_eq(r.skill_id, DIVE)
	assert_eq(r.swell_bonus_pct, 90)
	assert_true(int(r.hits[0]["amount"]) > 0)
	assert_eq(actor.swell, 0, "spent, and its own damage does not refill Wake")
	assert_eq(actor.turns_taken, 1, "the turn ended")
	assert_eq(actor.next_time, now + Formulas.action_delay(actor.agility, 2), "the technique's rank")
	assert_eq(engine.db.skill(DIVE)["power"], 12, "the table row is never scaled in place")


func test_a_technique_is_refused_off_turn_on_auto_turns_and_after_the_battle() -> void:
	_start()
	_rhen().swell = Formulas.SWELL_MAX
	engine.perform(&"attack", _one(engine.enemies[0]))
	while engine.is_party_turn():
		engine.perform(&"attack", _one(engine.enemies[0]))
	assert_eq(swell.refusal(DIVE), &"not_your_turn")
	assert_eq(swell.perform(DIVE, _one(engine.enemies[0]), ALL_PERFECT).fail_reason, &"not_your_turn")
	_start()
	_rhen().swell = Formulas.SWELL_MAX
	_rhen().add_status(&"berserk", -1)
	assert_eq(swell.refusal(DIVE), &"auto_turn")
	engine.outcome = BattleEngine.OUTCOME_VICTORY
	assert_eq(swell.perform(DIVE, _one(engine.enemies[0]), ALL_PERFECT).fail_reason, &"battle_over")
	assert_eq(BattleSwell.new(_config()).refusal(DIVE), &"battle_over", "not attached")


func test_perform_row_keeps_the_engine_checks() -> void:
	_start()
	var row := engine.db.skill(DIVE)
	assert_eq(engine.perform_row(DIVE, row, [] as Array[BattleCombatant]).fail_reason, &"no_valid_target")
	var spell := row.duplicate()
	spell["magic"] = true
	_rhen().add_status(&"silence", 2)
	assert_eq(engine.perform_row(DIVE, spell, _one(engine.enemies[0])).fail_reason, &"silenced")
	engine.outcome = BattleEngine.OUTCOME_DEFEAT
	assert_eq(engine.perform_row(DIVE, row, _one(engine.enemies[0])).fail_reason, &"battle_over")


func test_perform_row_refuses_an_enemy_turn() -> void:
	_start()
	while engine.is_party_turn():
		engine.perform(&"attack", _one(engine.enemies[0]))
	assert_eq(engine.perform_row(DIVE, engine.db.skill(DIVE), _one(engine.enemies[0])).fail_reason, &"not_your_turn")


# --- queries ------------------------------------------------------------------------------


func test_techniques_are_only_those_the_tables_define() -> void:
	_start()
	assert_eq(swell.techniques(_rhen()), [DIVE] as Array[StringName])
	assert_true(swell.is_technique(_rhen(), DIVE))
	assert_eq(swell.techniques(engine.find(&"spare")), [] as Array[StringName], "its technique is not in the DB")
	engine.find(&"spare").swell = Formulas.SWELL_MAX
	assert_false(swell.is_ready(engine.find(&"spare")), "a full gauge with nothing to unleash")
	assert_eq(swell.techniques(engine.find(&"mate")), [] as Array[StringName])
	_rhen().swell = Formulas.SWELL_MAX
	_rhen().hp = 0
	assert_false(swell.is_ready(_rhen()), "the fallen cannot unleash")


func test_input_rows_and_the_bonus_table() -> void:
	_start()
	var ring := swell.input_for(_rhen())
	assert_eq(str(ring["kind"]), "timing_ring")
	assert_eq(swell.input_for(engine.find(&"mate")), {})
	assert_eq(BattleSwell.bonus_pct(ring, ALL_PERFECT), 90)
	assert_eq(BattleSwell.bonus_pct(ring, {"grades": [&"perfect", &"good", &"miss"]}), 45)
	assert_eq(BattleSwell.bonus_pct(ring, {"grades": ["perfect", "perfect", "perfect", "perfect"]}), 90, "beats cap it")
	assert_eq(BattleSwell.bonus_pct(ring, {"grades": [&"wild"]}), 0, "unknown grades earn nothing")
	assert_eq(BattleSwell.bonus_pct(ring, {}), 0)


func test_the_fixture_opening_can_set_a_gauge() -> void:
	engine.setup(_db(), _ids([&"rhen", &"mate"]), _ids([&"spare"]), &"brutes", 1)
	engine.apply_fixture({"rhen": {"swell": 250}, "mate": {"swell": -4}, "spare": {"swell": 30}})
	assert_eq(_rhen().swell, Formulas.SWELL_MAX)
	assert_eq(engine.find(&"mate").swell, 0)
	assert_eq(engine.find(&"spare").swell, 30)


func test_an_unreadable_config_is_empty_and_gives_nobody_a_swell() -> void:
	var cfg := BattleSwell.load_config("res://tests/unit/no_such_swell.json")
	assert_eq(cfg, {}, "a missing file reads as no config (and logs an error)")
	var none := BattleSwell.new(cfg)
	assert_true(none.modes.is_empty())
	assert_true(none.unlocked.is_empty())
	assert_false(none.has_swell(BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, {})))


func test_the_live_config_has_at_least_three_modes_and_rhens_input() -> void:
	var cfg := BattleSwell.load_config()
	assert_true(cfg == BattleSwell.load_config(), "parsed once")
	var live := BattleSwell.new(cfg)
	assert_true(live.modes.size() >= 3, "SPEC §6.2: several fill modes")
	for mid: StringName in live.modes:
		assert_true(
			BattleSwell.TRIGGERS.has(StringName(str(live.modes[mid]["trigger"]))), "%s has a known trigger" % mid
		)
	assert_true(live.modes.has(live.default_mode))
	assert_true(live.unlocked.has(live.default_mode), "the default mode starts unlocked")
	assert_true(live.heroes.has(&"rhen"))
	var db := BattleDB.load_default()
	for tid: Variant in live.heroes[&"rhen"]["techniques"]:
		assert_true(bool(db.skill(StringName(str(tid))).get("swell", false)), "%s is a Swell row" % tid)


# --- helpers ------------------------------------------------------------------------------


func _start() -> void:
	engine = BattleEngine.new()
	engine.setup(_db(), _ids([&"rhen", &"mate"]), _ids([&"spare"]), &"brutes", 1)
	swell = BattleSwell.new(_config())
	swell.attach(engine)
	engine.begin()


func _rhen() -> BattleCombatant:
	return engine.find(&"rhen")


## Damage Lamp Dive deals on the opening turn with `input`, on a fresh battle (same seed).
func _dive_damage(input: Dictionary) -> int:
	_start()
	_rhen().swell = Formulas.SWELL_MAX
	var r := swell.perform(DIVE, _one(engine.enemies[0]), input)
	return int(r.hits[0]["amount"])


## Damage the Lamp Dive row at `power` deals through perform_row on the same opening.
func _row_damage(power: int) -> int:
	_start()
	var row := engine.db.skill(DIVE).duplicate()
	row["power"] = power
	return int(engine.perform_row(DIVE, row, _one(engine.enemies[0])).hits[0]["amount"])


func _emit(actor_id: StringName, hits: Array) -> void:
	var r := ActionResult.new()
	r.actor_id = actor_id
	for h: Variant in hits:
		r.hits.append(h as Dictionary)
	engine.action_resolved.emit(r)


static func _hit(target_id: StringName, amount: int, landed: bool = true) -> Dictionary:
	return {"target_id": target_id, "hit": landed, "crit": false, "amount": amount, "statuses_added": []}


static func _item(iid: StringName, effects: Array) -> ItemBattleAction:
	var a := ItemBattleAction.new()
	a.item_id = iid
	a.target = ItemBattleAction.TARGET_SINGLE_ALLY
	a.rank = Formulas.DEFAULT_RANK
	for e: Variant in effects:
		a.effects.append(e as Dictionary)
	return a


static func _one(c: BattleCombatant) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [c]
	return out


static func _ids(list: Array) -> Array[StringName]:
	var out: Array[StringName] = []
	for v: Variant in list:
		out.append(StringName(str(v)))
	return out


static func _config() -> Dictionary:
	return {
		"default_mode": "ballast",
		"modes":
		[
			{"id": "ballast", "trigger": "damage_taken", "rate": 120, "starts_unlocked": true},
			{"id": "wake", "trigger": "damage_dealt", "rate": 50, "starts_unlocked": true},
			{"id": "tether", "trigger": "ally_hurt", "rate": 60, "starts_unlocked": false},
			{"id": "salve", "trigger": "heal_item", "flat": 20},
		],
		"inputs":
		[
			{
				"id": "ring",
				"kind": "timing_ring",
				"beats": 3,
				"grades": {"perfect": 30, "good": 15, "miss": 0},
			}
		],
		"heroes":
		[
			{"id": "rhen", "input": "ring", "techniques": ["lamp_dive"]},
			{"id": "spare", "input": "ring", "techniques": ["not_in_the_db"]},
		],
	}


static func _db() -> BattleDB:
	var hero := {
		"level": 5,
		"hp": 400,
		"mp": 20,
		"strength": 20,
		"magic": 10,
		"defense": 10,
		"magic_defense": 10,
		"agility": 60,
		"accuracy": 100,
		"evasion": 0,
		"luck": 0
	}
	var mate := hero.duplicate()
	mate["hp"] = 300
	mate["agility"] = 20
	var brute := hero.duplicate()
	brute["hp"] = 5000
	brute["agility"] = 1
	brute["strength"] = 5
	var ai := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{
						"id": "attack",
						"kind": "physical",
						"power": 8,
						"rank": 3,
						"accuracy": 100,
						"target": "single_foe"
					},
					{
						"id": "lamp_dive",
						"kind": "physical",
						"power": 12,
						"rank": 2,
						"accuracy": 100,
						"target": "single_foe",
						"swell": true,
					},
				],
				"statuses": [{"id": "silence", "default_duration": 3}, {"id": "berserk", "default_duration": -1}],
				"characters":
				[
					{"id": "rhen", "stats": hero, "skills": ["attack"]},
					{"id": "mate", "stats": mate, "skills": ["attack"]},
					{"id": "spare", "stats": mate, "skills": ["attack"]},
				],
				"enemies": [{"id": "brute", "stats": brute, "skills": ["attack"], "ai": ai}],
				"encounters": [{"id": "brutes", "enemies": ["brute", "brute"]}],
			}
		)
	)
