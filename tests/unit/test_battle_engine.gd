extends TestCase
## Engine rules against a small fixture DB, so tests do not break when real data is tuned.

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()


func test_party_acts_first_when_faster() -> void:
	_start(&"dummies")
	assert_true(engine.is_party_turn())


func test_swap_costs_no_time_and_inherits_slot() -> void:
	_start(&"dummies")
	var leaving := engine.current
	var slot := leaving.next_time
	var now := engine.now
	assert_true(engine.swap(leaving.id, &"bench"))
	assert_eq(engine.current.id, &"bench")
	assert_eq(engine.current.next_time, slot)
	assert_eq(engine.now, now)
	assert_true(engine.party_reserve.has(leaving))
	assert_true(engine.current.participated)
	assert_eq(engine.preview()[0].combatant_id, &"bench")


func test_swap_rejects_unknown_members() -> void:
	_start(&"dummies")
	assert_false(engine.swap(&"nobody", &"bench"))
	assert_false(engine.swap(engine.current.id, &"nobody"))


func test_silence_blocks_magic_without_ending_turn() -> void:
	_start(&"dummies")
	var actor := engine.current
	actor.add_status(&"silence", 2)
	var r := engine.perform(&"zap", _first_foe())
	assert_false(r.ok)
	assert_eq(r.fail_reason, &"silenced")
	assert_eq(engine.current, actor)


func test_not_enough_mp() -> void:
	_start(&"dummies")
	engine.current.mp = 0
	var r := engine.perform(&"zap", _first_foe())
	assert_eq(r.fail_reason, &"no_mp")


func test_rank_sets_next_delay() -> void:
	_start(&"sturdy")
	var actor := engine.current
	var now := engine.now
	engine.perform(&"jab", _first_foe())
	assert_eq(actor.next_time, now + Formulas.action_delay(actor.agility, 1))


func test_delay_skill_pushes_target_back() -> void:
	_start(&"sturdy")
	var target := _first_foe()[0]
	var before := target.next_time
	var r := engine.perform(&"delay_hit", _first_foe())
	assert_true(r.hits[0]["hit"])
	assert_eq(target.next_time, before + Formulas.base_delay(target.agility) * 2)


func test_haste_applies_before_own_delay() -> void:
	_start(&"sturdy")
	var actor := engine.current
	var now := engine.now
	var me: Array[BattleCombatant] = [actor]
	engine.perform(&"quicken", me)
	assert_true(actor.has_status(&"haste"))
	assert_eq(actor.next_time, now + Formulas.action_delay(actor.agility, 3, Formulas.HASTE_SPEED_MULT))


func test_poison_ticks_at_end_of_own_turn() -> void:
	_start(&"sturdy")
	var actor := engine.current
	actor.add_status(&"poison", -1)
	var hp := actor.hp
	engine.perform(&"jab", _first_foe())
	assert_eq(actor.hp, hp - Formulas.poison_damage(actor.max_hp))


func test_victory_awards_xp_to_participants_only() -> void:
	_start(&"dummies")
	_auto_play(200)
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	var xp := engine.xp_awards()
	assert_eq(xp.get(&"hero", 0), 20)
	assert_eq(xp.get(&"helper", 0), 20)
	assert_false(xp.has(&"bench"), "reserve that never entered earns nothing")


func test_escape_forbidden_in_scripted_fight() -> void:
	_start(&"scripted")
	assert_false(engine.escape())
	assert_eq(engine.outcome, &"")


func test_same_seed_same_battle() -> void:
	_start(&"dummies", 99)
	var a := _auto_play(200)
	engine = BattleEngine.new()
	_start(&"dummies", 99)
	var b := _auto_play(200)
	assert_eq(a, b)


func test_enemy_ai_turn_mod_rule() -> void:
	_start(&"sturdy")
	var foe := _first_foe()[0]
	foe.turns_taken = 1
	var choice := EnemyAI.choose(engine, foe)
	assert_eq(choice["skill"], &"jab", "turn_mod [2, 1] rule fires on odd turns")
	foe.turns_taken = 2
	choice = EnemyAI.choose(engine, foe)
	assert_eq(choice["skill"], &"attack")


func test_swap_in_for_ko_never_rewinds_time() -> void:
	_start(&"plain")
	var ko := engine.party_active[1] if engine.current == engine.party_active[0] else engine.party_active[0]
	ko.hp = 0
	ko.next_time = 0  # stale slot from long ago
	var now := engine.now
	assert_true(engine.swap(ko.id, &"bench"))
	var bench := engine.find(&"bench")
	assert_eq(bench.next_time, now + Formulas.action_delay(bench.agility, Formulas.DEFAULT_RANK))
	var last := engine.now
	for i in 30:
		_step(&"attack")
		assert_true(engine.now >= last, "time went backwards at step %d" % i)
		last = engine.now


func test_swap_of_non_current_member_keeps_current() -> void:
	_start(&"plain")
	var actor := engine.current
	var other := engine.party_active[1] if actor == engine.party_active[0] else engine.party_active[0]
	assert_true(engine.swap(other.id, &"bench"))
	assert_eq(engine.current, actor)
	assert_eq(engine.find(&"bench").next_time, maxi(other.next_time, engine.now))


func test_dead_target_is_rejected_without_cost() -> void:
	_start(&"dummies")
	var actor := engine.current
	var foe := _first_foe()[0]
	foe.hp = 0
	var dead: Array[BattleCombatant] = [foe]
	actor.mp = 10
	var r := engine.perform(&"zap", dead)
	assert_eq(r.fail_reason, &"no_valid_target")
	assert_eq(actor.mp, 10)
	assert_eq(engine.current, actor)


func test_ally_skill_rejects_foe_target() -> void:
	_start(&"plain")
	var r := engine.perform(&"mend", _first_foe())
	assert_eq(r.fail_reason, &"no_valid_target")


func test_duplicate_targets_hit_once() -> void:
	_start(&"plain")
	var foe := _first_foe()[0]
	var twice: Array[BattleCombatant] = [foe, foe]
	var r := engine.perform(&"sweep", twice)
	assert_eq(r.hits.size(), 1)


func test_statuses_not_reported_on_killing_blow() -> void:
	_start(&"dummies")
	var r := engine.perform(&"hex_strike", _first_foe())
	assert_eq(r.hits[0]["amount"] > 0, true)
	assert_eq(r.hits[0]["statuses_added"], [])


func test_heal_restores_hp_up_to_max() -> void:
	_start(&"plain")
	var actor := engine.current
	actor.hp = 10
	var me: Array[BattleCombatant] = [actor]
	var r := engine.perform(&"mend", me)
	assert_true(r.ok)
	assert_true(actor.hp > 10 and actor.hp <= actor.max_hp)
	assert_eq(r.hits[0]["amount"], 10 - actor.hp, "amount is the signed HP change (negative = healed)")


func test_absorb_heals_the_target() -> void:
	_start(&"sponge")
	var foe := _first_foe()[0]
	foe.hp = 100
	engine.perform(&"splash", _first_foe())
	assert_true(foe.hp > 100)


func test_regen_ticks_at_end_of_own_turn() -> void:
	_start(&"plain")
	var actor := engine.current
	actor.hp = 100
	actor.add_status(&"regen", -1)
	engine.perform(&"jab", _first_foe())
	assert_eq(actor.hp, 100 + Formulas.regen_heal(actor.max_hp))


func test_stop_loses_exactly_its_turns() -> void:
	_start(&"plain")
	var foe := _first_foe()[0]
	foe.add_status(&"stop", 2)
	var foe_times: Array[int] = []
	for e in engine.preview(&"", null, 40):
		if e.combatant_id == foe.id:
			foe_times.append(e.time)
	var acted_at := -1
	var guard := 0
	while acted_at < 0 and guard < 200:
		guard += 1
		if engine.is_party_turn():
			engine.perform(&"jab", _first_foe())
		else:
			acted_at = engine.now
			engine.run_enemy_turn()
	assert_eq(acted_at, foe_times[2], "first real turn is the third predicted slot")
	assert_false(foe.has_status(&"stop"))


func test_sleep_wakes_on_damage() -> void:
	_start(&"plain")
	var foe := _first_foe()[0]
	foe.add_status(&"sleep", -1)
	engine.perform(&"jab", _first_foe())
	assert_false(foe.has_status(&"sleep"))


func test_everyone_asleep_forever_ends_instead_of_hanging() -> void:
	var active: Array[StringName] = [&"hero", &"helper"]
	var reserve: Array[StringName] = []
	engine.setup(_fixture_db(), active, reserve, &"plain", 1)
	for c in engine.party_active + engine.enemies:
		c.add_status(&"sleep", -1)
	engine.begin()
	assert_eq(engine.outcome, BattleEngine.OUTCOME_DEFEAT)


func test_escape_can_succeed_and_fail() -> void:
	var successes := 0
	var failures := 0
	for rng_seed in range(1, 40):
		engine = BattleEngine.new()
		_start(&"plain", rng_seed)
		var actor := engine.current
		if engine.escape():
			assert_eq(engine.outcome, BattleEngine.OUTCOME_ESCAPED)
			successes += 1
		else:
			assert_ne(engine.current, actor, "failed escape costs the turn")
			failures += 1
	assert_true(successes > 0 and failures > 0, "%d ok / %d failed" % [successes, failures])


func test_preview_shows_haste_from_candidate_skill() -> void:
	_start(&"plain")
	var actor := engine.current
	var plain := engine.preview(&"attack", _first_foe()[0])
	var hasted := engine.preview(&"quicken", null)
	var plain_t := -1
	var hasted_t := -1
	for e in plain:
		if e.is_preview:
			plain_t = e.time
	for e in hasted:
		if e.is_preview:
			hasted_t = e.time
	assert_eq(plain_t, engine.now + Formulas.action_delay(actor.agility, 3))
	assert_eq(hasted_t, engine.now + Formulas.action_delay(actor.agility, 3, Formulas.HASTE_SPEED_MULT))


func test_prediction_matches_play_with_expiring_haste() -> void:
	_start(&"plain", 5)
	engine.current.add_status(&"haste", 2)
	var predicted: Array[String] = []
	for e in engine.preview(&"", null, 12):
		predicted.append("%s@%d" % [e.combatant_id, e.time])
	var played: Array[String] = []
	while played.size() < 12:
		played.append("%s@%d" % [engine.current.id, engine.now])
		_step(&"attack")
	assert_eq(played, predicted)


func test_enemy_ai_conditions_and_selectors() -> void:
	_start(&"tacticians")
	var t1 := engine.enemies[0]
	var hero := engine.find(&"hero")
	var helper := engine.find(&"helper")
	hero.hp = 50
	var default_pick := EnemyAI.choose(engine, t1)
	assert_eq(default_pick["targets"][0].team, BattleCombatant.TEAM_ENEMY, "random_ally targets own side")
	helper.add_status(&"poison", -1)
	assert_eq(EnemyAI.choose(engine, t1)["targets"][0], hero, "foe_has_status -> lowest_hp_foe")
	t1.hp = t1.max_hp / 4
	assert_eq(EnemyAI.choose(engine, t1)["targets"][0], helper, "self_hp_below_pct -> highest_hp_foe")
	t1.hp = t1.max_hp
	helper.statuses.clear()
	engine.enemies[1].hp = 0
	var alone := EnemyAI.choose(engine, t1)
	assert_eq(alone["skill"], &"jab")
	assert_eq(alone["targets"][0], t1, "allies_alive_below -> self")


func test_turn_mod_zero_is_false_not_a_crash() -> void:
	_start(&"plain")
	var foe := _first_foe()[0]
	foe.ai_rules = [{"if": {"turn_mod": [0, 0]}, "pick": [{"skill": "attack"}]}, {"pick": [{"skill": "attack"}]}]
	assert_eq(EnemyAI.choose(engine, foe)["skill"], &"attack")


func test_find_and_side_queries() -> void:
	_start(&"dummies")
	assert_eq(engine.find(&"bench").id, &"bench")
	assert_eq(engine.find(&"nobody"), null)
	assert_eq(engine.living_allies_of(engine.find(&"hero")).size(), 2)
	assert_eq(engine.living_foes_of(engine.find(&"hero")).size(), 2)
	assert_eq(engine.living_allies_of(engine.enemies[0]).size(), 2)


# --- helpers -----------------------------------------------------------------------------


## One action for whoever's turn it is (party uses `skill` on the first living foe).
func _step(skill: StringName) -> void:
	if engine.is_party_turn():
		engine.perform(skill, _first_foe())
	else:
		engine.run_enemy_turn()


func _start(encounter: StringName, rng_seed: int = 1) -> void:
	var active: Array[StringName] = [&"hero", &"helper"]
	var reserve: Array[StringName] = [&"bench"]
	engine.setup(_fixture_db(), active, reserve, encounter, rng_seed)
	engine.begin()
	var guard := 0
	while not engine.is_party_turn() and engine.outcome == &"" and guard < 50:
		engine.run_enemy_turn()
		guard += 1


func _first_foe() -> Array[BattleCombatant]:
	var foes := engine.living_foes_of(engine.current)
	var out: Array[BattleCombatant] = [foes[0]]
	return out


## Party always attacks the first living foe. Returns a compact action log.
func _auto_play(max_actions: int) -> Array[String]:
	var entries: Array[String] = []
	var n := 0
	while engine.outcome == &"" and n < max_actions:
		n += 1
		if engine.is_party_turn():
			var actor := engine.current.id
			var r := engine.perform(&"attack", _first_foe())
			entries.append("%s:%s" % [actor, str(r.hits.map(func(h: Dictionary) -> int: return h["amount"]))])
		else:
			var r2 := engine.run_enemy_turn()
			entries.append("%s:%s" % [r2.actor_id, r2.skill_id])
	entries.append(String(engine.outcome))
	return entries


static func _fixture_db() -> BattleDB:
	var hero_stats := _stats(300, 30, 20)
	hero_stats["mp"] = 10
	hero_stats["accuracy"] = 50
	var helper_stats := hero_stats.duplicate()
	helper_stats["agility"] = 15
	var bench_stats := hero_stats.duplicate()
	bench_stats["agility"] = 30
	var skills := [&"attack", &"zap", &"jab", &"delay_hit", &"quicken", &"mend", &"splash", &"hex_strike", &"sweep"]
	var foe_stats := _stats(40, 5, 1)
	var sturdy_stats := _stats(9000, 5, 1)
	var basic_ai := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	var sturdy_ai := [
		{"if": {"turn_mod": [2, 1]}, "pick": [{"skill": "jab", "target": "random_foe"}]},
		{"pick": [{"skill": "attack", "target": "random_foe"}]},
	]
	var tactician_ai := [
		{"if": {"self_hp_below_pct": 50}, "pick": [{"skill": "attack", "target": "highest_hp_foe"}]},
		{"if": {"foe_has_status": "poison"}, "pick": [{"skill": "attack", "target": "lowest_hp_foe"}]},
		{"if": {"allies_alive_below": 2}, "pick": [{"skill": "jab", "target": "self"}]},
		{"pick": [{"skill": "attack", "target": "random_ally"}]},
	]
	var skill_rows := [
		{"id": "attack", "kind": "physical", "power": 8, "rank": 3, "accuracy": 100, "target": "single_foe"},
		{"id": "jab", "kind": "physical", "power": 2, "rank": 1, "accuracy": 100, "target": "single_foe"},
		{"id": "delay_hit", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "delay_ranks": 2},
		{"id": "zap", "kind": "magical", "power": 8, "rank": 3, "mp_cost": 5, "magic": true},
		{"id": "mend", "kind": "heal", "power": 5, "rank": 3, "target": "single_ally", "magic": true},
		{"id": "splash", "kind": "physical", "power": 4, "rank": 3, "accuracy": 100, "element": "water"},
		{"id": "sweep", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "target": "all_foes"},
		{
			"id": "hex_strike",
			"kind": "physical",
			"power": 50,
			"rank": 3,
			"accuracy": 100,
			"statuses": [{"id": "slow", "chance": 100, "duration": 3}],
		},
		{
			"id": "quicken",
			"kind": "support",
			"rank": 3,
			"magic": true,
			"target": "self",
			"statuses": [{"id": "haste", "chance": 100, "duration": 4}],
		},
	]
	var enemy_rows := [
		{"id": "dummy", "stats": foe_stats, "skills": ["attack"], "ai": basic_ai, "xp": 10},
		{"id": "sturdy", "stats": sturdy_stats, "skills": ["attack", "jab"], "ai": sturdy_ai, "xp": 1},
		{"id": "plain", "stats": sturdy_stats, "skills": ["attack"], "ai": basic_ai, "xp": 1},
		{
			"id": "sponge",
			"stats": sturdy_stats,
			"skills": ["attack"],
			"ai": basic_ai,
			"affinities": {"water": "absorb"},
		},
		{"id": "tactician", "stats": sturdy_stats, "skills": ["attack", "jab"], "ai": tactician_ai},
	]
	return (
		BattleDB
		. from_tables(
			{
				"skills": skill_rows,
				"statuses": [{"id": "haste", "default_duration": 4}, {"id": "slow", "default_duration": 4}],
				"characters":
				[
					{"id": "hero", "stats": hero_stats, "skills": skills},
					{"id": "helper", "stats": helper_stats, "skills": skills},
					{"id": "bench", "stats": bench_stats, "skills": skills},
				],
				"enemies": enemy_rows,
				"encounters":
				[
					{"id": "dummies", "enemies": ["dummy", "dummy"]},
					{"id": "sturdy", "enemies": ["sturdy"]},
					{"id": "plain", "enemies": ["plain"]},
					{"id": "sponge", "enemies": ["sponge"]},
					{"id": "tacticians", "enemies": ["tactician", "tactician"]},
					{"id": "scripted", "enemies": ["sturdy"], "scripted": true},
				],
			}
		)
	)


static func _stats(hp: int, strength: int, agility: int) -> Dictionary:
	return {
		"level": 5 if agility > 1 else 1,
		"hp": hp,
		"mp": 0,
		"strength": strength,
		"magic": 10,
		"defense": 0 if agility <= 1 else 10,
		"magic_defense": 10,
		"agility": agility,
		"accuracy": 0,
		"evasion": 0,
		"luck": 0,
	}


# --- party_modifier hook (M1-CMB-01: Lattice gains in battle) ----------------------------


func test_party_modifier_defaults_to_no_op() -> void:
	assert_false(engine.party_modifier.is_valid())
	_start(&"dummies")
	var hero := engine.find(&"hero")
	assert_eq(hero.strength, 30)
	assert_eq(hero.max_hp, 300)


func test_party_modifier_runs_once_per_party_member_only() -> void:
	var seen: Array[StringName] = []
	engine.party_modifier = func(c: BattleCombatant) -> void:
		seen.append(c.id)
		c.strength += 1
	_start(&"dummies")
	assert_eq(seen, [&"hero", &"helper", &"bench"] as Array[StringName], "active then reserve, once each")
	assert_eq(engine.find(&"hero").strength, 31)
	assert_eq(engine.find(&"bench").strength, 31, "reserves are modified too")
	for e in engine.enemies:
		assert_eq(e.strength, 5, "enemies are never modified")


func test_party_modifier_applies_lattice_progress() -> void:
	var p := LatticeFixture.progress()
	var inv := FacetInventory.new({"facet_power": 2, "facet_ability": 1})
	p.traveler(&"rhen").movement_points = 3
	p.move(&"rhen", &"s_str")
	p.activate(&"rhen", inv)
	p.move(&"rhen", &"s_hp")
	p.activate(&"rhen", inv)
	p.move(&"rhen", &"ab_kick")
	p.activate(&"rhen", inv)
	engine.party_modifier = p.apply_to
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma"]
	var db := BattleDB.load_default()
	engine.setup(db, active, reserve, &"sandbox_reef", 7)
	var rhen := engine.find(&"rhen")
	var base: Dictionary = db.characters[&"rhen"]["stats"]
	assert_eq(rhen.strength, int(base["strength"]) + 3)
	assert_eq(rhen.max_hp, int(base["hp"]) + 40)
	assert_eq(rhen.hp, rhen.max_hp, "HP bonus raises current HP too")
	assert_true(rhen.skills.has(&"kick_off"), "ability node grants its skill")
	assert_eq(rhen.skills.count(&"kick_off"), 1)
	var asha := engine.find(&"asha")
	assert_eq(asha.strength, int(db.characters[&"asha"]["stats"]["strength"]), "only the activator gains")
	assert_eq(engine.find(&"toma").skills.size(), (db.characters[&"toma"]["skills"] as Array).size())


func test_party_modifier_keeps_battles_deterministic() -> void:
	var p := LatticeFixture.progress()
	engine.party_modifier = p.apply_to
	_start(&"dummies", 5)
	var first := _auto_play(60)
	engine = BattleEngine.new()
	engine.party_modifier = p.apply_to
	_start(&"dummies", 5)
	assert_eq(_auto_play(60), first)


# --- preview_swap (M1-CMB-02 follow-up for the Swap menu) -----------------------------------


func test_preview_swap_matches_swap_of_current_member() -> void:
	_start(&"plain")
	_assert_swap_preview_matches(engine.current.id, &"bench")


func test_preview_swap_matches_swap_of_other_member() -> void:
	_start(&"plain")
	var other := engine.party_active[1] if engine.current == engine.party_active[0] else engine.party_active[0]
	_assert_swap_preview_matches(other.id, &"bench")


func test_preview_swap_matches_swap_for_ko_member() -> void:
	_start(&"plain")
	var other := engine.party_active[1] if engine.current == engine.party_active[0] else engine.party_active[0]
	other.hp = 0
	_assert_swap_preview_matches(other.id, &"bench")


func test_preview_swap_keeps_reserve_statuses() -> void:
	_start(&"plain")
	engine.find(&"bench").add_status(&"haste", 3)
	_assert_swap_preview_matches(engine.current.id, &"bench")


func test_preview_swap_mutates_nothing() -> void:
	_start(&"plain")
	var before := _snapshot()
	var base := _entries(engine.preview())
	engine.preview_swap(engine.current.id, &"bench")
	assert_eq(_snapshot(), before)
	assert_eq(_entries(engine.preview()), base)
	assert_true(engine.find(&"bench") in engine.party_reserve)


func test_preview_swap_empty_when_swap_would_refuse() -> void:
	_start(&"plain")
	assert_eq(engine.preview_swap(&"nobody", &"bench").size(), 0)
	assert_eq(engine.preview_swap(engine.current.id, &"nobody").size(), 0)
	engine.find(&"bench").hp = 0
	assert_eq(engine.preview_swap(engine.current.id, &"bench").size(), 0, "a fallen reserve cannot enter")


func test_preview_swap_length() -> void:
	_start(&"plain")
	assert_eq(engine.preview_swap(engine.current.id, &"bench").size(), CtbTimeline.PREVIEW_LENGTH)
	assert_eq(engine.preview_swap(engine.current.id, &"bench", 5).size(), 5)


func _assert_swap_preview_matches(out_id: StringName, in_id: StringName) -> void:
	var predicted := _entries(engine.preview_swap(out_id, in_id, 20))
	assert_true(engine.swap(out_id, in_id))
	assert_eq(_entries(engine.preview(&"", null, 20)), predicted)
	var played: Array[String] = []
	while played.size() < 20 and engine.outcome == &"":
		played.append("%s@%d" % [engine.current.id, engine.now])
		_step(&"attack")
	assert_eq(played, predicted.slice(0, played.size()), "and with what actually happens")


func _entries(list: Array[TurnEntry]) -> Array[String]:
	var out: Array[String] = []
	for e in list:
		out.append("%s@%d" % [e.combatant_id, e.time])
	return out


func _snapshot() -> Array[String]:
	var out: Array[String] = []
	for c in engine.party_active + engine.party_reserve + engine.enemies:
		out.append("%s:%d:%d:%s" % [c.id, c.next_time, c.hp, str(c.statuses)])
	out.append("current=%s now=%d" % [engine.current.id, engine.now])
	return out


# --- hero level (ADR 0012) ---------------------------------------------------------------


func test_hero_level_comes_from_data() -> void:
	_start(&"dummies")
	assert_eq(engine.find(&"hero").level, 5)


func test_party_modifier_cannot_change_hero_level() -> void:
	engine.party_modifier = func(c: BattleCombatant) -> void:
		c.level += 10
		c.strength += 1
	_start(&"dummies")
	var hero := engine.find(&"hero")
	assert_eq(hero.level, 5, "level is fixed; growth is Lattice stats only")
	assert_eq(hero.strength, 31, "other gains still apply")


func test_real_heroes_share_one_level_and_lattice_keeps_it() -> void:
	var db := BattleDB.load_default()
	var levels: Dictionary = {}
	for cid: StringName in db.characters:
		levels[int(db.characters[cid]["stats"]["level"])] = true
	assert_eq(levels.size(), 1, "one fixed hero level")
	var p := LatticeFixture.progress()
	var inv := FacetInventory.new({"facet_power": 2, "facet_ability": 1})
	p.traveler(&"rhen").movement_points = 3
	p.move(&"rhen", &"s_str")
	p.activate(&"rhen", inv)
	engine.party_modifier = p.apply_to
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = []
	engine.setup(db, active, reserve, &"sandbox_reef", 1)
	assert_eq(engine.find(&"rhen").level, int(levels.keys()[0]))
