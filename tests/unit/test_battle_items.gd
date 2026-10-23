extends TestCase
## M1-CMB-06: item use as a battle action (BattleEngine.use_item / preview_item) on the real
## items.json through InventoryItemSource, plus battle rewards (lume and drops).

var engine: BattleEngine
var items_db: ItemDB


class FakeItems:
	extends BattleItemSource
	var actions: Dictionary = {}
	var counts: Dictionary = {}

	func action_for(item_id: StringName) -> ItemBattleAction:
		return actions.get(item_id, null)

	func count(item_id: StringName) -> int:
		return int(counts.get(item_id, 0))

	func consume(item_id: StringName) -> bool:
		if count(item_id) <= 0:
			return false
		counts[item_id] = count(item_id) - 1
		return true


func before_each() -> void:
	engine = BattleEngine.new()
	items_db = ItemDB.load_default()


# --- the item source ---------------------------------------------------------------------


func test_inventory_item_source_wraps_the_bag() -> void:
	var src := _bag({"salt_tonic": 2, "crab_carapace": 3})
	assert_eq(src.count(&"salt_tonic"), 2)
	assert_eq(src.action_for(&"crab_carapace"), null, "materials have no battle use")
	assert_eq(src.action_for(&"salt_tonic").rank, 2)
	assert_eq(src.usable(), [&"salt_tonic"] as Array[StringName])
	assert_true(src.consume(&"salt_tonic"))
	assert_eq(src.count(&"salt_tonic"), 1)


func test_base_source_has_nothing() -> void:
	var src := BattleItemSource.new()
	assert_eq(src.action_for(&"salt_tonic"), null)
	assert_eq(src.count(&"salt_tonic"), 0)
	assert_false(src.consume(&"salt_tonic"))


# --- use_item ----------------------------------------------------------------------------


func test_heal_item_heals_consumes_and_ends_the_turn_at_its_rank() -> void:
	_start(&"one")
	var actor := engine.current
	var ally := _other(actor)
	ally.hp = 100
	var src := _bag({"salt_tonic": 2})
	var now := engine.now
	var r := engine.use_item(&"salt_tonic", _one(ally), src)
	assert_true(r.ok)
	assert_eq(r.item_id, &"salt_tonic")
	assert_eq(r.skill_id, &"")
	assert_eq(ally.hp, 300)
	assert_eq(r.hits[0]["amount"], -200, "healing is a negative amount")
	assert_eq(src.count(&"salt_tonic"), 1, "exactly one used")
	assert_eq(actor.next_time, now + Formulas.action_delay(actor.agility, 2), "the item's rank sets the delay")


func test_use_item_refusals_cost_nothing() -> void:
	_start(&"one")
	var actor := engine.current
	var src := _bag({"salt_tonic": 1})
	assert_eq(engine.use_item(&"salt_tonic", _one(actor), null).fail_reason, &"unknown_item")
	assert_eq(engine.use_item(&"crab_carapace", _one(actor), src).fail_reason, &"unknown_item")
	assert_eq(engine.use_item(&"reef_draught", _one(actor), src).fail_reason, &"no_item")
	var foe := engine.enemies[0]
	var r := engine.use_item(&"salt_tonic", _one(foe), src)
	assert_eq(r.fail_reason, &"no_valid_target", "a heal can't go to a foe")
	assert_eq(r.item_id, &"salt_tonic")
	assert_eq(
		engine.use_item(&"relighting_wick", _one(actor), _bag({"relighting_wick": 1})).fail_reason, &"no_valid_target"
	)
	assert_eq(src.count(&"salt_tonic"), 1)
	assert_eq(engine.current, actor, "still this turn")


func test_use_item_off_turn_and_after_battle() -> void:
	_start(&"one")
	var src := _bag({"salt_tonic": 1})
	engine.current.add_status(&"berserk", -1)
	assert_eq(engine.use_item(&"salt_tonic", _one(engine.current), src).fail_reason, &"not_your_turn")
	engine.current.statuses.clear()
	engine.enemies[0].hp = 1
	engine.perform(&"wallop", _one(engine.enemies[0]))
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_eq(engine.use_item(&"salt_tonic", [] as Array[BattleCombatant], src).fail_reason, &"battle_over")


func test_items_ignore_silence() -> void:
	_start(&"one")
	engine.current.add_status(&"silence", 3)
	engine.current.hp = 10
	assert_true(engine.use_item(&"salt_tonic", _one(engine.current), _bag({"salt_tonic": 1})).ok)


func test_mp_cure_haste_delay_and_damage_items() -> void:
	_start(&"one")
	var src := _bag({"quiet_tea": 1, "bitterleaf": 1, "quickwater": 1, "drag_net": 1, "ember_pot": 1})
	var a := engine.current
	a.mp = 0
	assert_eq(engine.use_item(&"quiet_tea", _one(a), src).hits[0]["mp_amount"], 30)
	_to_party_turn()
	var b := engine.current
	b.add_status(&"poison", -1)
	assert_eq(engine.use_item(&"bitterleaf", _one(b), src).hits[0]["statuses_removed"], [&"poison"])
	_to_party_turn()
	var c := engine.current
	engine.use_item(&"quickwater", _one(c), src)
	assert_true(c.has_status(&"haste"))
	_to_party_turn()
	var foe := engine.enemies[0]
	var t0 := foe.next_time
	var r := engine.use_item(&"drag_net", _one(foe), src)
	assert_eq(foe.next_time, t0 + Formulas.base_delay(foe.agility) * 2)
	assert_eq(r.hits[0]["delay_ticks"], Formulas.base_delay(foe.agility) * 2)
	_to_party_turn()
	var hp := foe.hp
	engine.use_item(&"ember_pot", _one(foe), src)
	assert_eq(hp - foe.hp, Formulas.item_damage(150, &"weak"), "the dummy is weak to fire: 225")


func test_revive_brings_back_a_ko_ally_without_rewinding_time() -> void:
	_start(&"one")
	var actor := engine.current
	var fallen := _other(actor)
	fallen.hp = 0
	fallen.next_time = 0  # stale slot from long ago
	var now := engine.now
	var src := _bag({"relighting_wick": 1})
	var predicted := _entries(engine.preview_item(&"relighting_wick", fallen, src, 12))
	var r := engine.use_item(&"relighting_wick", _one(fallen), src)
	assert_true(r.hits[0]["revived"])
	assert_eq(fallen.hp, Formulas.revive_hp(fallen.max_hp, 25))
	assert_eq(fallen.next_time, now + Formulas.action_delay(fallen.agility, Formulas.DEFAULT_RANK))
	assert_eq(_entries(engine.preview(&"", null, 12)), predicted, "the preview showed the rejoin")
	assert_true(predicted.any(func(s: String) -> bool: return s.begins_with(String(fallen.id))))


func test_revive_can_not_reach_stone() -> void:
	_start(&"one")
	var ally := _other(engine.current)
	ally.add_status(&"petrify", -1)
	var r := engine.use_item(&"relighting_wick", _one(ally), _bag({"relighting_wick": 1}))
	assert_eq(r.fail_reason, &"no_valid_target", "petrified is neither alive nor fallen")
	assert_eq(engine.use_item(&"salt_tonic", _one(ally), _bag({"salt_tonic": 1})).fail_reason, &"no_valid_target")


func test_revive_fells_a_zombie() -> void:
	_start(&"one")
	var ally := _other(engine.current)
	ally.add_status(&"zombie", -1)
	var hp := ally.hp
	var src := _bag({"relighting_wick": 1})
	var predicted := engine.preview_item(&"relighting_wick", ally, src, 10)
	for e in predicted:
		assert_ne(e.combatant_id, ally.id, "the preview drops the zombie")
	var r := engine.use_item(&"relighting_wick", _one(ally), src)
	assert_false(ally.is_alive())
	assert_true(r.hits[0]["zombie_felled"])
	assert_eq(r.hits[0]["amount"], hp)
	assert_eq(src.count(&"relighting_wick"), 0)


func test_zombie_heal_item_harms() -> void:
	_start(&"one")
	var ally := _other(engine.current)
	ally.add_status(&"zombie", -1)
	ally.hp = 250
	var r := engine.use_item(&"salt_tonic", _one(ally), _bag({"salt_tonic": 1}))
	assert_eq(ally.hp, 50)
	assert_eq(r.hits[0]["amount"], 200, "positive: HP lost")


func test_preview_item_matches_play() -> void:
	for item: StringName in [&"salt_tonic", &"drag_net", &"quickwater"]:
		engine = BattleEngine.new()
		_start(&"one")
		var target := engine.enemies[0] if item == &"drag_net" else _other(engine.current)
		var src := _bag({item: 1})
		var predicted := _entries(engine.preview_item(item, target, src, 14))
		assert_true(engine.use_item(item, _one(target), src).ok)
		assert_eq(_entries(engine.preview(&"", null, 14)), predicted, "%s preview is honest" % item)


func test_preview_item_without_an_item_is_the_plain_order() -> void:
	_start(&"one")
	var plain := _entries(engine.preview())
	assert_eq(_entries(engine.preview_item(&"crab_carapace", null, _bag({}))), plain)
	assert_eq(_entries(engine.preview_item(&"salt_tonic", null, null)), plain)
	var none := _entries(engine.preview_item(&"salt_tonic", null, _bag({"salt_tonic": 1}), 16))
	assert_eq(none.size(), 16, "no target: only the rank is previewed")


func test_self_and_group_items_and_target_rules() -> void:
	_start(&"two")
	var src := FakeItems.new()
	src.actions[&"flare"] = _action(&"flare", &"all_foes", 3, [{"type": "damage", "amount": 10, "element": "none"}])
	src.actions[&"chant"] = _action(&"chant", &"all_allies", 3, [{"type": "heal_hp", "amount": 5}])
	src.actions[&"gulp"] = _action(&"gulp", &"self", 1, [{"type": "restore_mp", "amount": 1}])
	src.actions[&"pebble"] = _action(&"pebble", &"single_foe", 1, [{"type": "damage", "amount": 1}])
	src.counts = {&"flare": 1, &"chant": 1, &"gulp": 1, &"pebble": 1}
	var both: Array[BattleCombatant] = [engine.enemies[0], engine.enemies[1], engine.enemies[0]]
	assert_eq(engine.use_item(&"flare", both, src).hits.size(), 2, "group item, deduplicated")
	_to_party_turn()
	var party: Array[BattleCombatant] = engine.party_active.duplicate()
	party.append(engine.enemies[0])
	assert_eq(engine.use_item(&"chant", party, src).hits.size(), 2, "ally group skips the foe")
	_to_party_turn()
	var actor := engine.current
	assert_eq(engine.use_item(&"gulp", _one(_other(actor)), src).fail_reason, &"no_valid_target")
	assert_true(engine.use_item(&"gulp", _one(actor), src).ok)
	_to_party_turn()
	var r := engine.use_item(&"pebble", both, src)
	assert_eq(r.hits.size(), 1, "single-target items keep the first target")
	assert_eq(src.count(&"pebble"), 0)


func test_item_battles_stay_deterministic() -> void:
	var a := _item_log(31)
	var b := _item_log(31)
	assert_eq(a, b)


# --- rewards -----------------------------------------------------------------------------


func test_currency_award_and_multiplier_on_real_data() -> void:
	_win_sandbox(4)
	assert_eq(engine.currency_award(), 24 + 20 + 18)
	var seen: Array = []
	engine.currency_multiplier = func(ids: Array[StringName]) -> int:
		seen.append(ids)
		return 2
	assert_eq(engine.currency_award(), 124, "Full Net doubles battle lume")
	assert_eq(seen[0], engine.credited_ids())
	assert_true(engine.credited_ids().has(&"rhen"))


func test_no_rewards_without_victory() -> void:
	var e := BattleEngine.new()
	var active: Array[StringName] = [&"rhen"]
	e.setup(BattleDB.load_default(), active, [] as Array[StringName], &"sandbox_reef", 1)
	e.begin()
	assert_eq(e.currency_award(), 0)
	assert_eq(e.drop_awards(), {})
	assert_eq(e.credited_ids(), [] as Array[StringName])


func test_drops_are_seeded_known_and_rolled_once() -> void:
	var seen: Dictionary = {}
	for s in range(1, 30):
		engine = BattleEngine.new()
		_win_sandbox(s)
		var d := engine.drop_awards()
		assert_eq(engine.drop_awards(), d, "rolled once, at victory")
		for iid: StringName in d:
			assert_true(items_db.has_item(iid), "%s is a real item" % iid)
			seen[iid] = true
		engine = BattleEngine.new()
		_win_sandbox(s)
		assert_eq(engine.drop_awards(), d, "same seed, same drops")
	assert_true(seen.has(&"crab_carapace") and seen.has(&"salt_tonic"), str(seen.keys()))


func test_certain_and_impossible_drops() -> void:
	_start(&"one")
	for e in engine.enemies:
		e.hp = 0
	engine.enemies[0].hp = 1
	engine.perform(&"wallop", _one(engine.enemies[0]))
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_eq(engine.drop_awards(), {&"bitterleaf": 1}, "chance 100 always drops, 0 never")
	assert_eq(engine.currency_award(), 7)


# --- formulas ----------------------------------------------------------------------------


func test_item_formulas_match_progression_reference() -> void:
	assert_eq(Formulas.revive_hp(420, 25), 105)
	assert_eq(Formulas.revive_hp(3, 25), 1, "never below 1")
	assert_eq(Formulas.item_damage(150, &"weak"), 225)
	assert_eq(Formulas.item_damage(150, &"absorb"), -150)
	assert_eq(Formulas.item_damage(150, &"immune"), 0)
	assert_eq(Formulas.item_damage(20000, &"normal"), Formulas.DAMAGE_CAP)
	for pair: Array in [[420, 25], [3, 25], [1000, 100]]:
		assert_eq(Formulas.revive_hp(pair[0], pair[1]), ItemBattleAction.revive_hp(pair[0], pair[1]))
	for aff: StringName in [&"normal", &"weak", &"resist", &"immune", &"absorb"]:
		assert_eq(Formulas.item_damage(150, aff), ItemBattleAction.fixed_damage(150, aff))


# --- helpers -----------------------------------------------------------------------------


func _bag(counts: Dictionary) -> InventoryItemSource:
	var inv := Inventory.new(items_db, {})
	for iid: Variant in counts:
		inv.add(StringName(str(iid)), int(counts[iid]))
	return InventoryItemSource.new(items_db, inv)


static func _action(iid: StringName, target: StringName, rank: int, effects: Array) -> ItemBattleAction:
	var a := ItemBattleAction.new()
	a.item_id = iid
	a.target = target
	a.rank = rank
	for e: Variant in effects:
		a.effects.append(e as Dictionary)
	return a


func _item_log(rng_seed: int) -> Array[String]:
	engine = BattleEngine.new()
	_start(&"two", rng_seed)
	var src := _bag({"salt_tonic": 5, "drag_net": 5, "ember_pot": 5})
	var out: Array[String] = []
	var guard := 0
	var plan: Array[StringName] = [&"drag_net", &"ember_pot", &"salt_tonic"]
	while engine.outcome == &"" and guard < 60:
		guard += 1
		if engine.is_party_turn():
			var item := plan[guard % plan.size()]
			var t := engine.current if item == &"salt_tonic" else engine.living_foes_of(engine.current)[0]
			var r := engine.use_item(item, _one(t), src)
			if not r.ok:
				r = engine.perform(&"attack", _one(engine.living_foes_of(engine.current)[0]))
			out.append("%s:%s" % [r.actor_id, str(r.hits.map(func(h: Dictionary) -> int: return h["amount"]))])
		else:
			var r2 := engine.run_enemy_turn()
			out.append("%s@%d" % [r2.actor_id, engine.now])
	return out


func _win_sandbox(rng_seed: int) -> void:
	var active: Array[StringName] = [&"rhen", &"asha"]
	engine.setup(BattleDB.load_default(), active, [] as Array[StringName], &"sandbox_reef", rng_seed)
	engine.begin()
	for e in engine.enemies:
		e.hp = 0
	var last := engine.enemies[0]
	last.hp = 1
	last.evasion = 0
	var guard := 0
	while engine.outcome == &"" and guard < 20:
		guard += 1
		if engine.is_party_turn():
			engine.perform(&"attack", _one(last))
		else:
			engine.run_enemy_turn()
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)


func _entries(list: Array[TurnEntry]) -> Array[String]:
	var out: Array[String] = []
	for e in list:
		out.append("%s@%d" % [e.combatant_id, e.time])
	return out


func _start(encounter: StringName, rng_seed: int = 1) -> void:
	var active: Array[StringName] = [&"hero", &"helper"]
	engine.setup(_db(), active, [] as Array[StringName], encounter, rng_seed)
	engine.begin()
	_to_party_turn()


func _to_party_turn() -> void:
	var guard := 0
	while not engine.is_party_turn() and engine.outcome == &"" and guard < 50:
		guard += 1
		engine.run_enemy_turn()


func _one(c: BattleCombatant) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [c]
	return out


func _other(c: BattleCombatant) -> BattleCombatant:
	return engine.party_active[1] if engine.party_active[0] == c else engine.party_active[0]


static func _db() -> BattleDB:
	var hero := {
		"level": 5,
		"hp": 300,
		"mp": 40,
		"strength": 10,
		"magic": 10,
		"defense": 5,
		"magic_defense": 5,
		"agility": 30,
		"accuracy": 0,
		"evasion": 0,
		"luck": 0,
	}
	var helper := hero.duplicate()
	helper["agility"] = 20
	var foe := hero.duplicate()
	foe["agility"] = 6
	foe["hp"] = 9000
	var ai := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	var drops := [{"item": "bitterleaf", "chance": 100}, {"item": "salt_tonic", "chance": 0}]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "attack", "kind": "physical", "power": 2, "rank": 3, "accuracy": 100},
					{"id": "wallop", "kind": "physical", "power": 50, "rank": 3, "accuracy": 100},
				],
				"statuses": [],
				"characters":
				[
					{"id": "hero", "stats": hero, "skills": ["attack", "wallop"]},
					{"id": "helper", "stats": helper, "skills": ["attack", "wallop"]},
				],
				"enemies":
				[
					{
						"id": "dummy",
						"stats": foe,
						"skills": ["attack"],
						"ai": ai,
						"affinities": {"fire": "weak"},
						"currency": 7,
						"drops": drops,
					},
				],
				"encounters": [{"id": "one", "enemies": ["dummy"]}, {"id": "two", "enemies": ["dummy", "dummy"]}],
			}
		)
	)
