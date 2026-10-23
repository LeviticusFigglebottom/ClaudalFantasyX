extends TestCase
## M1-CMB-06 follow-ups: end-of-turn and lost-turn reports for the HUD, apply_fixture, the
## Sleep-wake preview, delay diminishing returns and immunity, a Drag Net lock check, the
## Petrify cure, and the sim's loadouts and smart item rule.

var engine: BattleEngine
var ended: Array = []
var lost: Array = []


class FakeItems:
	extends BattleItemSource
	var actions: Dictionary = {}
	var counts: Dictionary = {}

	func action_for(item_id: StringName) -> ItemBattleAction:
		return actions.get(item_id, null)

	func count(item_id: StringName) -> int:
		return int(counts.get(item_id, 0))

	func consume(item_id: StringName) -> bool:
		counts[item_id] = count(item_id) - 1
		return true


class DragLock:
	extends SimPolicy

	## Every party turn: a Drag Net on the slowest living foe while nets last.
	func decide(engine: BattleEngine) -> void:
		var slow := engine.living_foes_of(engine.current)[0]
		for f in engine.living_foes_of(engine.current):
			if f.agility < slow.agility:
				slow = f
		if engine.use_item(&"drag_net", _one(slow), items).ok:
			items_used += 1
		else:
			_basic(engine)


func before_each() -> void:
	engine = BattleEngine.new()
	ended = []
	lost = []
	engine.turn_ended.connect(func(a: BattleCombatant, ch: Array[Dictionary]) -> void: ended.append([a.id, ch]))
	engine.turn_lost.connect(
		func(a: BattleCombatant, why: StringName, ch: Array[Dictionary]) -> void: lost.append([a.id, why, ch])
	)


# --- turn_ended / turn_lost --------------------------------------------------------------


func test_turn_ended_reports_poison_and_regen() -> void:
	_start(&"one")
	var actor := engine.current
	actor.hp = 100
	actor.add_status(&"poison", -1)
	actor.add_status(&"regen", -1)
	ended.clear()
	var r := engine.perform(&"jab", _foe())
	var want: Array[Dictionary] = [
		{"target_id": actor.id, "cause": &"poison", "amount": Formulas.poison_damage(actor.max_hp), "doom": 0},
		{"target_id": actor.id, "cause": &"regen", "amount": -Formulas.regen_heal(actor.max_hp), "doom": 0},
	]
	assert_eq(r.end_of_turn, want)
	assert_eq(ended[0], [actor.id, want], "the signal carries the same list")


func test_turn_ended_reports_zombie_regen_as_damage() -> void:
	_start(&"one")
	var actor := engine.current
	actor.add_status(&"zombie", -1)
	actor.add_status(&"regen", -1)
	var r := engine.perform(&"jab", _foe())
	assert_eq(r.end_of_turn[0]["cause"], &"regen")
	assert_eq(r.end_of_turn[0]["amount"], Formulas.regen_heal(actor.max_hp), "positive: Regen harms a Zombie")


func test_turn_ended_reports_doom_ticks_and_the_fall() -> void:
	_start(&"one")
	var actor := engine.current
	actor.add_status(&"doom", 2)
	var r := engine.perform(&"jab", _foe())
	assert_eq(
		r.end_of_turn, [{"target_id": actor.id, "cause": &"doom_tick", "amount": 0, "doom": 1}] as Array[Dictionary]
	)
	_to_turn_of(actor)
	var hp := actor.hp
	var r2 := engine.perform(&"jab", _foe())
	assert_eq(r2.end_of_turn, [{"target_id": actor.id, "cause": &"doom", "amount": hp, "doom": 0}] as Array[Dictionary])
	assert_false(actor.is_alive())


func test_quiet_turns_report_nothing_and_failures_carry_no_end_of_turn() -> void:
	_start(&"one")
	assert_eq(engine.perform(&"nope", _foe()).end_of_turn, [] as Array[Dictionary])
	ended.clear()
	assert_eq(engine.perform(&"jab", _foe()).end_of_turn, [] as Array[Dictionary])
	assert_eq(ended.size(), 1, "turn_ended fires on every acted turn")


func test_turn_lost_for_stop_and_sleep_with_doom() -> void:
	_start(&"one")
	var foe := engine.enemies[0]
	foe.add_status(&"stop", 1)
	foe.add_status(&"doom", 3)
	_run_until(func() -> bool: return not lost.is_empty())
	assert_eq(lost[0][0], foe.id)
	assert_eq(lost[0][1], &"stop")
	assert_eq(lost[0][2], [{"target_id": foe.id, "cause": &"doom_tick", "amount": 0, "doom": 2}] as Array[Dictionary])
	lost.clear()
	foe.add_status(&"sleep", 2)
	foe.statuses[&"doom"] = 1
	var hp := foe.hp
	_run_until(func() -> bool: return not lost.is_empty())
	assert_eq(lost[0][1], &"sleep")
	assert_eq(lost[0][2], [{"target_id": foe.id, "cause": &"doom", "amount": hp, "doom": 0}] as Array[Dictionary])
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY, "Doom on a lost turn ends the fight")


func test_turn_lost_without_doom_reports_no_changes() -> void:
	_start(&"one")
	engine.enemies[0].add_status(&"stop", 1)
	_run_until(func() -> bool: return not lost.is_empty())
	assert_eq(lost[0][2], [] as Array[Dictionary])


# --- apply_fixture -----------------------------------------------------------------------


func test_apply_fixture_sets_opening_state() -> void:
	var active: Array[StringName] = [&"hero", &"helper"]
	engine.setup(_db(), active, [] as Array[StringName], &"two", 1)
	engine.party_active[1].set_meta(BattleCombatant.EQUIPMENT_META, {"status_wards": [&"poison"]})
	(
		engine
		. apply_fixture(
			{
				"hero":
				{
					"hp": 0,
					"statuses": [{"id": "haste", "duration": 3}, {"id": "provoke", "duration": 3}],
					"provoked_by": "dummy#2"
				},
				"helper": {"hp": 99999, "statuses": [{"id": "poison"}]},
				"dummy": {"statuses": [{"id": "slow", "duration": 2}]},
			}
		)
	)
	var hero := engine.find(&"hero")
	assert_eq(hero.hp, 1, "clamped to at least 1")
	assert_eq(hero.statuses, {&"haste": 3, &"provoke": 3})
	assert_eq(hero.provoker_id, &"dummy#2")
	var helper := engine.find(&"helper")
	assert_eq(helper.hp, helper.max_hp, "clamped to max")
	assert_false(helper.has_status(&"poison"), "wards still hold")
	for e in engine.enemies:
		assert_eq(e.statuses, {&"slow": 2}, "a base id applies to every copy")
	engine.begin()
	assert_eq(engine.forced_target(hero, &"jab"), engine.find(&"dummy#2"))


# --- Sleep wakes in the preview ----------------------------------------------------------


func test_preview_wakes_a_sleeping_target_hit_by_damage() -> void:
	_start(&"one")
	var foe := engine.enemies[0]
	foe.add_status(&"sleep", 3)
	_assert_preview_matches(&"jab", foe)
	assert_false(foe.has_status(&"sleep"))


func test_preview_keeps_sleep_for_non_damaging_and_immune_hits() -> void:
	_start(&"one")
	var foe := engine.enemies[0]
	foe.add_status(&"sleep", 3)
	_assert_preview_matches(&"lull", foe)
	assert_true(foe.has_status(&"sleep"))
	_to_turn_of(engine.party_active[0])
	_assert_preview_matches(&"spark", foe)
	assert_true(foe.has_status(&"sleep"), "immune: no damage, no wake")


func test_preview_wakes_every_sleeper_a_group_hit_damages() -> void:
	_start(&"two")
	for e in engine.enemies:
		e.add_status(&"sleep", 3)
	var predicted := _entries(engine.preview(&"sweep", null, 14))
	assert_true(engine.perform(&"sweep", engine.enemies.duplicate()).ok)
	assert_eq(_entries(engine.preview(&"", null, 14)), predicted)


func test_preview_wakes_a_sleeping_zombie_healed() -> void:
	_start(&"one")
	var ally := _other(engine.current)
	ally.add_status(&"zombie", -1)
	ally.add_status(&"sleep", 3)
	_assert_preview_matches(&"mend", ally)
	assert_false(ally.has_status(&"sleep"))


func test_preview_wakes_a_sleeping_zombie_in_a_group_heal() -> void:
	_start(&"one")
	var ally := _other(engine.current)
	ally.add_status(&"zombie", -1)
	ally.add_status(&"sleep", 3)
	var predicted := _entries(engine.preview(&"chorus", null, 14))
	assert_true(engine.perform(&"chorus", engine.party_active.duplicate()).ok)
	assert_eq(_entries(engine.preview(&"", null, 14)), predicted)
	assert_false(ally.has_status(&"sleep"))


func test_item_preview_wakes_on_damage_and_on_cure() -> void:
	_start(&"one")
	var src := FakeItems.new()
	src.actions[&"pot"] = _action(&"pot", &"single_foe", [{"type": "damage", "amount": 5, "element": "none"}])
	src.actions[&"salts"] = _action(&"salts", &"single_ally", [{"type": "cure", "statuses": ["sleep"]}])
	src.counts = {&"pot": 1, &"salts": 1}
	var foe := engine.enemies[0]
	foe.add_status(&"sleep", 3)
	var predicted := _entries(engine.preview_item(&"pot", foe, src, 12))
	assert_true(engine.use_item(&"pot", _one(foe), src).ok)
	assert_eq(_entries(engine.preview(&"", null, 12)), predicted)
	_to_party_turn()
	var ally := _other(engine.current)
	ally.add_status(&"sleep", 3)
	predicted = _entries(engine.preview_item(&"salts", ally, src, 12))
	assert_true(engine.use_item(&"salts", _one(ally), src).ok)
	assert_eq(_entries(engine.preview(&"", null, 12)), predicted)


# --- delay -------------------------------------------------------------------------------


func test_delay_halves_for_each_delay_before_the_target_acts() -> void:
	_start(&"one")
	var foe := engine.enemies[0]
	var base := Formulas.base_delay(foe.agility)
	var r := engine.perform(&"shove", _one(foe))
	assert_eq(r.hits[0]["delay_ticks"], base * 2)
	_to_party_turn()
	var predicted := _entries(engine.preview(&"shove", foe, 12))
	r = engine.perform(&"shove", _one(foe))
	assert_eq(r.hits[0]["delay_ticks"], base * 2 / 2, "the second delay before it acts is halved")
	assert_eq(_entries(engine.preview(&"", null, 12)), predicted, "and the preview knew")
	_to_turn_of(foe)
	engine.run_enemy_turn()
	assert_eq(foe.delays_taken, 0, "acting resets the count")


func test_delay_immune_target_and_counting() -> void:
	_start(&"anchor")
	var boss := engine.enemies[0]
	assert_true(boss.delay_immune)
	var t0 := boss.next_time
	var r := engine.perform(&"shove", _one(boss))
	assert_eq(r.hits[0]["delay_ticks"], 0)
	assert_eq(boss.next_time, t0)
	assert_eq(boss.delays_taken, 0)


func test_drag_net_can_not_lock_the_slowest_foe() -> void:
	var sim := BattleSim.new()
	var kit := sim.loadout(&"m1_starting")
	kit["items"] = {"drag_net": 99}
	var active: Array[StringName] = [&"rhen", &"asha"]
	var policy := DragLock.new()
	for s in range(1, 6):
		var e := BattleEngine.new()
		var crab_turns := [0]
		var party_turns := [0]
		e.turn_ended.connect(
			func(a: BattleCombatant, _c: Array[Dictionary]) -> void:
				if a.team == BattleCombatant.TEAM_PARTY:
					party_turns[0] += 1
				elif String(a.id).begins_with("reef_crab"):
					crab_turns[0] += 1
		)
		e.setup(sim.db, active, [] as Array[StringName], &"sandbox_reef", s)
		policy.items = InventoryItemSource.new(sim.items_db(), _bag(sim, {"drag_net": 99}))
		e.begin()
		var guard := 0
		while e.outcome == &"" and guard < 300 and party_turns[0] < 40:
			guard += 1
			if e.is_party_turn():
				policy.take_turn(e)
			else:
				e.run_enemy_turn()
		assert_true(policy.items_used > 0)
		assert_true(
			crab_turns[0] * 10 >= party_turns[0],  # unbounded stacking would hold it forever
			"seed %d: crab %d turns vs party %d" % [s, crab_turns[0], party_turns[0]]
		)


# --- Petrify cure ------------------------------------------------------------------------


func test_petrify_cure_reaches_stone_and_rejoins_without_rewinding() -> void:
	_start(&"one")
	var ally := _other(engine.current)
	ally.add_status(&"petrify", -1)
	ally.next_time = 0
	var src := FakeItems.new()
	var cure := _action(&"soft", &"single_ally", [{"type": "cure", "statuses": ["petrify"]}])
	src.actions[&"soft"] = cure
	src.counts = {&"soft": 1}
	assert_true(cure.cures(&"petrify"))
	assert_true(cure.can_target(ally))
	assert_false(_action(&"x", &"single_ally", [{"type": "heal_hp", "amount": 1}]).can_target(ally))
	var predicted := _entries(engine.preview_item(&"soft", ally, src, 12))
	var now := engine.now
	var r := engine.use_item(&"soft", _one(ally), src)
	assert_true(r.ok)
	assert_true(ally.is_alive())
	assert_eq(ally.next_time, now + Formulas.action_delay(ally.agility, Formulas.DEFAULT_RANK))
	assert_eq(_entries(engine.preview(&"", null, 12)), predicted)


# --- sim loadouts and the smart item rule ------------------------------------------------


func test_sim_loadouts_equip_and_stock() -> void:
	var sim := BattleSim.new()
	assert_eq(sim.loadout(&"nowhere"), {})
	var kit := sim.loadout(&"m1_tier1")
	var active: Array[StringName] = [&"rhen", &"asha"]
	var none: Array[StringName] = []
	var bare := sim.run_many(&"sandbox_reef", active, none, &"naive", 40)
	var geared := sim.run_many(&"sandbox_reef", active, none, &"naive", 40, 1, Callable(), kit)
	assert_true(float(geared["win_pct"]) > float(bare["win_pct"]), "tier-1 gear helps")
	var res := sim.run_cli({"encounter": "sandbox_reef", "active": "rhen,asha", "seeds": "2", "loadout": "m1_tier1"})
	assert_true(res["ok"])
	assert_true((res["results"] as Array)[0].has("mean_lume"))
	var bad := sim.run_cli({"encounter": "sandbox_reef", "active": "rhen", "seeds": "1", "loadout": "nowhere"})
	assert_false(bad["ok"])
	var wrong := {"gear": {"rhen": ["asha_vigil_staff"]}}
	var r := sim.run_one(
		&"sandbox_reef", active, [] as Array[StringName], sim.make_policy(&"naive"), 3, Callable(), wrong
	)
	assert_true(r["outcome"] in ["victory", "defeat"], "a bad piece is reported, not fatal")


func test_smart_uses_a_heal_item_without_a_healer() -> void:
	var sim := BattleSim.new()
	var e := BattleEngine.new()
	var active: Array[StringName] = [&"rhen", &"toma"]
	e.setup(sim.db, active, [] as Array[StringName], &"sandbox_reef", 2)
	e.begin()
	var guard := 0
	while not e.is_party_turn() and guard < 20:
		guard += 1
		e.run_enemy_turn()
	var hurt := e.current
	hurt.hp = 10
	var smart := sim.make_policy(&"smart")
	smart.items = InventoryItemSource.new(sim.items_db(), _bag(sim, {"salt_tonic": 1}))
	smart.take_turn(e)
	assert_eq(smart.items_used, 1)
	assert_true(hurt.hp > 10)


func test_smart_revives_a_fallen_member_when_no_reserve_is_left() -> void:
	var sim := BattleSim.new()
	var e := BattleEngine.new()
	var active: Array[StringName] = [&"rhen", &"toma"]
	e.setup(sim.db, active, [] as Array[StringName], &"sandbox_reef", 2)
	e.begin()
	var guard := 0
	while not e.is_party_turn() and guard < 20:
		guard += 1
		e.run_enemy_turn()
	var down := e.party_active[1] if e.party_active[0] == e.current else e.party_active[0]
	down.hp = 0
	var smart := sim.make_policy(&"smart")
	smart.items = InventoryItemSource.new(sim.items_db(), _bag(sim, {"relighting_wick": 1}))
	smart.take_turn(e)
	assert_true(down.is_alive())
	assert_eq(smart.items_used, 1)


# --- helpers -----------------------------------------------------------------------------


static func _bag(sim: BattleSim, counts: Dictionary) -> Inventory:
	var inv := Inventory.new(sim.items_db(), {})
	for iid: Variant in counts:
		inv.add(StringName(str(iid)), int(counts[iid]))
	return inv


static func _action(iid: StringName, target: StringName, effects: Array) -> ItemBattleAction:
	var a := ItemBattleAction.new()
	a.item_id = iid
	a.target = target
	a.rank = 2
	for e: Variant in effects:
		a.effects.append(e as Dictionary)
	return a


func _assert_preview_matches(skill: StringName, target: BattleCombatant) -> void:
	var predicted := _entries(engine.preview(skill, target, 14))
	assert_true(engine.perform(skill, _one(target)).ok)
	assert_eq(_entries(engine.preview(&"", null, 14)), predicted, "%s preview matches play" % skill)


func _entries(list: Array[TurnEntry]) -> Array[String]:
	var out: Array[String] = []
	for e in list:
		out.append("%s@%d%s" % [e.combatant_id, e.time, "z" if e.skipped else ""])
	return out


## Plays turns (the party uses the harmless Lull, which wakes nobody) until `done` holds.
func _run_until(done: Callable) -> void:
	var guard := 0
	while not done.call() and engine.outcome == &"" and guard < 100:
		guard += 1
		if engine.is_party_turn():
			engine.perform(&"lull", _foe())
		else:
			engine.run_enemy_turn()


func _to_turn_of(c: BattleCombatant) -> void:
	var guard := 0
	while engine.current != c and engine.outcome == &"" and guard < 100:
		guard += 1
		if engine.is_party_turn():
			engine.perform(&"lull", _foe())
		else:
			engine.run_enemy_turn()


func _to_party_turn() -> void:
	var guard := 0
	while not engine.is_party_turn() and engine.outcome == &"" and guard < 50:
		guard += 1
		engine.run_enemy_turn()


func _start(encounter: StringName) -> void:
	var active: Array[StringName] = [&"hero", &"helper"]
	engine.setup(_db(), active, [] as Array[StringName], encounter, 1)
	engine.begin()
	_to_party_turn()


func _foe() -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [engine.living_foes_of(engine.current)[0]]
	return out


func _one(c: BattleCombatant) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [c]
	return out


func _other(c: BattleCombatant) -> BattleCombatant:
	return engine.party_active[1] if engine.party_active[0] == c else engine.party_active[0]


static func _db() -> BattleDB:
	var hero := {
		"level": 5,
		"hp": 300,
		"mp": 99,
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
	foe["strength"] = 1
	var ai := [{"pick": [{"skill": "jab", "target": "random_foe"}]}]
	var skills := ["jab", "lull", "spark", "sweep", "mend", "shove", "chorus"]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "jab", "kind": "physical", "power": 1, "rank": 1, "accuracy": 100},
					{"id": "lull", "kind": "support", "rank": 3, "target": "single_foe"},
					{"id": "spark", "kind": "magical", "power": 3, "rank": 3, "element": "lightning", "magic": true},
					{"id": "sweep", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "target": "all_foes"},
					{"id": "mend", "kind": "heal", "power": 2, "rank": 3, "target": "single_ally", "magic": true},
					{"id": "chorus", "kind": "heal", "power": 2, "rank": 3, "target": "all_allies", "magic": true},
					{"id": "shove", "kind": "physical", "power": 1, "rank": 2, "accuracy": 100, "delay_ranks": 2},
				],
				"statuses": [],
				"characters":
				[
					{"id": "hero", "stats": hero, "skills": skills},
					{"id": "helper", "stats": helper, "skills": skills},
				],
				"enemies":
				[
					{"id": "dummy", "stats": foe, "skills": ["jab"], "ai": ai, "affinities": {"lightning": "immune"}},
					{"id": "anchor", "stats": foe, "skills": ["jab"], "ai": ai, "delay_immune": true},
				],
				"encounters":
				[
					{"id": "one", "enemies": ["dummy"]},
					{"id": "two", "enemies": ["dummy", "dummy"]},
					{"id": "anchor", "enemies": ["anchor"]},
				],
			}
		)
	)
