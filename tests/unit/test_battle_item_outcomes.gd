extends TestCase
## M1-CMB-07 and M1-UI-04 sweep E: who an item leaves standing (BattleEngine.item_downs /
## item_leaves_standing), the defeat prediction that rests on it (a heal that KOs the last
## Zombie, a group revive that fells one ally and revives another), and the delay count
## reset when a unit rejoins the field. Runs headless on the live sandbox tables.

const SEED := 20261022
const WICK := &"relighting_wick"
const TONIC := &"salt_tonic"
const LOW_HP := 50

var engine: BattleEngine
var item_db: ItemDB


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
	item_db = ItemDB.load_default()


# --- a heal item that KOs a Zombie ---------------------------------------------------------


func test_a_zombie_healing_itself_to_a_ko_as_the_last_one_standing_is_a_defeat() -> void:
	_engine_turn()
	var actor := engine.current
	_other(actor).fall()
	actor.add_status(&"zombie", -1)
	actor.hp = LOW_HP
	var bag := _bag({"salt_tonic": 1})
	var tonic := bag.action_for(TONIC)
	assert_false(BattleEngine.item_fells(tonic, actor), "a heal is not a revive")
	assert_true(BattleEngine.item_downs(tonic, actor), "but 200 HP of harm KOs a 50 HP Zombie")
	assert_eq(actor.hp, LOW_HP, "the prediction mutates nothing")
	assert_true(actor.has_status(&"zombie"))
	assert_true(engine.item_defeats_party(TONIC, _one(actor), bag), "predicted")
	assert_false(_ids(engine.preview_item(TONIC, actor, bag)).has(actor.id), "the preview drops the user")
	var r := engine.use_item(TONIC, _one(actor), bag)
	assert_true(r.ok, "the use is legal")
	assert_eq(r.hits[0]["amount"], LOW_HP, "HP lost")
	assert_eq(engine.outcome, BattleEngine.OUTCOME_DEFEAT, "the prediction is what play does")


func test_the_preview_drops_a_zombie_ally_the_heal_kos_and_matches_play() -> void:
	_engine_turn()
	var actor := engine.current
	var ally := _other(actor)
	ally.add_status(&"zombie", -1)
	ally.hp = LOW_HP
	var bag := _bag({"salt_tonic": 1})
	var predicted := _entries(engine.preview_item(TONIC, ally, bag, 12))
	assert_false(_ids(engine.preview_item(TONIC, ally, bag)).has(ally.id))
	assert_false(engine.item_defeats_party(TONIC, _one(ally), bag), "the user still stands")
	assert_true(engine.use_item(TONIC, _one(ally), bag).ok)
	assert_false(ally.is_alive())
	assert_eq(engine.outcome, &"")
	assert_eq(_entries(engine.preview(&"", null, 12)), predicted, "preview equals play")


func test_a_heal_a_zombie_survives_is_neither_a_ko_nor_a_defeat() -> void:
	_engine_turn()
	var actor := engine.current
	_other(actor).fall()
	actor.add_status(&"zombie", -1)
	var bag := _bag({"salt_tonic": 1})
	assert_true(actor.hp > 200, "full HP soaks the harm")
	assert_false(BattleEngine.item_downs(bag.action_for(TONIC), actor))
	assert_false(engine.item_defeats_party(TONIC, _one(actor), bag))
	assert_true(_ids(engine.preview_item(TONIC, actor, bag)).has(actor.id))


func test_effects_run_in_order_so_a_cure_first_makes_the_heal_real() -> void:
	_engine_turn()
	var actor := engine.current
	_other(actor).fall()
	actor.add_status(&"zombie", -1)
	actor.hp = LOW_HP
	var src := FakeItems.new()
	src.actions[&"cure_then_heal"] = _action(
		&"cure_then_heal",
		&"single_ally",
		[{"type": "cure", "statuses": ["zombie"]}, {"type": "heal_hp", "amount": 200}]
	)
	src.actions[&"heal_then_cure"] = _action(
		&"heal_then_cure",
		&"single_ally",
		[{"type": "heal_hp", "amount": 200}, {"type": "cure", "statuses": ["zombie"]}]
	)
	assert_false(engine.item_defeats_party(&"cure_then_heal", _one(actor), src))
	assert_true(engine.item_defeats_party(&"heal_then_cure", _one(actor), src))
	assert_true(engine.use_item(&"cure_then_heal", _one(actor), src).ok)
	assert_eq(actor.hp, LOW_HP + 200, "play agrees: cured, then healed")
	assert_eq(engine.outcome, &"")


func test_an_item_that_turns_the_last_one_standing_to_stone_is_a_defeat() -> void:
	_engine_turn()
	var actor := engine.current
	_other(actor).fall()
	var src := FakeItems.new()
	src.actions[&"medusa"] = _action(&"medusa", &"self", [{"type": "add_status", "status": "petrify", "duration": -1}])
	assert_true(BattleEngine.item_downs(src.actions[&"medusa"], actor), "stone is down")
	assert_true(engine.item_defeats_party(&"medusa", _one(actor), src))
	engine.use_item(&"medusa", _one(actor), src)
	assert_eq(engine.outcome, BattleEngine.OUTCOME_DEFEAT)


# --- group revives -----------------------------------------------------------------------


func test_a_group_revive_that_fells_the_last_zombie_but_revives_an_ally_is_not_a_defeat() -> void:
	_engine_turn()
	var actor := engine.current
	var ally := _other(actor)
	ally.fall()
	actor.add_status(&"zombie", -1)
	var src := _group_revive()
	var both := engine.party_active.duplicate()
	assert_false(engine.item_defeats_party(&"chorus_wick", both, src), "the fallen ally comes back")
	var r := engine.use_item(&"chorus_wick", both, src)
	assert_true(r.ok)
	assert_eq(r.hits.size(), 2)
	assert_false(actor.is_alive(), "the Zombie user is felled")
	assert_true(ally.is_alive(), "the ally is revived")
	assert_eq(engine.outcome, &"", "and the battle goes on")


func test_a_group_revive_that_fells_every_zombie_is_a_defeat() -> void:
	_engine_turn()
	for c in engine.party_active:
		c.add_status(&"zombie", -1)
	var src := _group_revive()
	var both := engine.party_active.duplicate()
	assert_true(engine.item_defeats_party(&"chorus_wick", both, src))
	engine.use_item(&"chorus_wick", both, src)
	assert_eq(engine.outcome, BattleEngine.OUTCOME_DEFEAT)


func test_felling_the_last_foe_is_never_a_defeat() -> void:
	_engine_turn()
	for e in engine.enemies:
		e.hp = 1
	var src := FakeItems.new()
	src.actions[&"blast"] = _action(&"blast", &"all_foes", [{"type": "damage", "amount": 50, "element": "none"}])
	assert_false(engine.item_defeats_party(&"blast", engine.enemies.duplicate(), src))
	engine.use_item(&"blast", engine.enemies.duplicate(), src)
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)


# --- delays_taken on rejoin --------------------------------------------------------------


func test_a_revived_ally_rejoins_with_a_fresh_delay_count() -> void:
	_engine_turn()
	var ally := _other(engine.current)
	ally.delays_taken = 3
	ally.fall()
	assert_true(engine.use_item(WICK, _one(ally), _bag({"relighting_wick": 1})).ok)
	assert_true(ally.is_alive())
	assert_eq(ally.delays_taken, 0)


func test_a_stone_cured_ally_rejoins_with_a_fresh_delay_count() -> void:
	_engine_turn()
	var ally := _other(engine.current)
	ally.delays_taken = 2
	assert_true(ally.add_status(&"petrify", -1))
	var src := FakeItems.new()
	src.actions[&"soft"] = _action(&"soft", &"single_ally", [{"type": "cure", "statuses": ["petrify"]}])
	var now := engine.now
	assert_true(engine.use_item(&"soft", _one(ally), src).ok)
	assert_eq(ally.delays_taken, 0)
	assert_eq(ally.next_time, now + Formulas.action_delay(ally.agility, Formulas.DEFAULT_RANK, ally.speed_mult()))


func test_a_stone_cure_with_haste_rejoins_at_the_hasted_delay() -> void:
	_engine_turn()
	var ally := _other(engine.current)
	assert_true(ally.add_status(&"petrify", -1))
	var src := FakeItems.new()
	src.actions[&"quick_soft"] = _action(
		&"quick_soft",
		&"single_ally",
		[{"type": "cure", "statuses": ["petrify"]}, {"type": "add_status", "status": "haste", "duration": 3}]
	)
	var now := engine.now
	assert_true(engine.use_item(&"quick_soft", _one(ally), src).ok)
	var hasted := Formulas.action_delay(ally.agility, Formulas.DEFAULT_RANK, Formulas.HASTE_SPEED_MULT)
	assert_ne(hasted, Formulas.action_delay(ally.agility, Formulas.DEFAULT_RANK), "haste matters here")
	assert_eq(ally.next_time, now + hasted, "the speed term (economy.md § Targeting in battle)")


func test_a_swap_in_takes_a_living_slots_delay_count_and_starts_fresh_for_the_fallen() -> void:
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	engine.setup(BattleDB.load_default(), active, reserve, &"sandbox_reef", SEED)
	engine.begin()
	_to_party_turn()
	var leaver := _other(engine.current)
	var toma := engine.find(&"toma")
	var ysolde := engine.find(&"ysolde")
	leaver.delays_taken = 2
	toma.delays_taken = 5
	assert_true(engine.swap(leaver.id, &"toma"))
	assert_eq(toma.delays_taken, 2, "the slot's count comes with it")
	toma.fall()
	ysolde.delays_taken = 4
	assert_true(engine.swap(&"toma", &"ysolde"))
	assert_eq(ysolde.delays_taken, 0, "replacing the fallen starts fresh")


# --- sim_copy ----------------------------------------------------------------------------


func test_sim_copy_is_detached() -> void:
	_engine_turn()
	var c := engine.current
	c.add_status(&"zombie", -1)
	var affinities := c.affinities.duplicate()
	var copy := c.sim_copy()
	assert_eq(copy.hp, c.hp)
	assert_eq(copy.statuses, c.statuses)
	assert_eq(copy.equipment(), c.equipment())
	copy.fall()
	copy.affinities[&"probe"] = &"weak"
	assert_true(c.is_alive(), "felling the copy leaves the original")
	assert_true(c.has_status(&"zombie"))
	assert_eq(c.affinities, affinities, "the copy's affinities are its own")


# --- helpers -----------------------------------------------------------------------------


func _engine_turn() -> void:
	var active: Array[StringName] = [&"rhen", &"asha"]
	engine.setup(BattleDB.load_default(), active, [] as Array[StringName], &"sandbox_reef", SEED)
	engine.begin()
	_to_party_turn()


func _to_party_turn() -> void:
	var guard := 0
	while not engine.is_party_turn() and engine.outcome == &"" and guard < 50:
		guard += 1
		engine.run_enemy_turn()


func _group_revive() -> FakeItems:
	var src := FakeItems.new()
	src.actions[&"chorus_wick"] = _action(&"chorus_wick", &"all_allies", [{"type": "revive", "hp_pct": 25}])
	return src


func _bag(counts: Dictionary) -> InventoryItemSource:
	var inv := Inventory.new(item_db, {})
	for iid: Variant in counts:
		inv.add(StringName(str(iid)), int(counts[iid]))
	return InventoryItemSource.new(item_db, inv)


static func _action(iid: StringName, target: StringName, effects: Array) -> ItemBattleAction:
	var a := ItemBattleAction.new()
	a.item_id = iid
	a.target = target
	a.rank = 2
	for e: Variant in effects:
		var eff: Dictionary = e
		a.effects.append(eff)
		if StringName(str(eff.get("type", ""))) == ItemBattleAction.EFFECT_REVIVE:
			a.targets_fallen = true
	return a


func _entries(list: Array[TurnEntry]) -> Array[String]:
	var out: Array[String] = []
	for e in list:
		out.append("%s@%d%s" % [e.combatant_id, e.time, "z" if e.skipped else ""])
	return out


func _ids(list: Array[TurnEntry]) -> Array[StringName]:
	var out: Array[StringName] = []
	for e in list:
		out.append(e.combatant_id)
	return out


func _one(c: BattleCombatant) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [c]
	return out


func _other(c: BattleCombatant) -> BattleCombatant:
	return engine.party_active[1] if engine.party_active[0] == c else engine.party_active[0]
