extends TestCase
## M3-CMB-01: the set-piece pieces (BattleSetPiece; set_piece_battles.md) on a small fixture DB, so
## tuning Ch8's real fights never breaks these:
##   scripted timeline entries (no HP, never a target but of a ward skill, never counted for the
##   outcome), objective victory and the scripted_escape outcome, untargetable and damage-immune
##   phases, the HP floor, party locks (a locked slot, an unavailable hero, an Attack override), the
##   cover (Hold the Stair), the counter stance (Stand Firm), Haul, field rules (storm_dark), the
##   Surge's cap and late join, Pell's telegraphed Storm-Call, and the AI's ward selector.

const SEED := 7
const STEPS := 400

var engine: BattleEngine


func before_each() -> void:
	engine = _engine(
		&"stair", [&"guard", &"hero", &"liss"] as Array[StringName], [&"kerrid", &"scout"] as Array[StringName]
	)


# --- scripted entries ----------------------------------------------------------------------------


func test_entries_are_on_the_timeline_with_no_hp_and_never_a_target() -> void:
	var climb := engine.ward()
	assert_true(climb != null, "the ward entry")
	assert_eq(climb.id, &"the_climb")
	assert_eq(climb.entry_role, BattleSetPiece.ROLE_WARD)
	assert_eq(engine.entries.size(), 2, "the Climb and the Surge")
	assert_eq(engine.find(&"the_surge").team, BattleCombatant.TEAM_ENEMY)
	var on_timeline := {}
	for e in engine.preview():
		on_timeline[e.combatant_id] = true
	assert_true(on_timeline.has(&"the_climb") and on_timeline.has(&"the_surge"), "both show on the order")
	assert_eq(climb.apply_damage(500), 0, "no HP to lose")
	climb.fall()
	assert_true(climb.is_alive(), "it can't be KO'd")
	var hero := engine.find(&"hero")
	assert_false(engine.living_foes_of(hero).has(engine.find(&"the_surge")), "the Surge is no foe to strike")
	assert_false(engine.living_allies_of(hero).has(climb), "nor the Climb an ally to heal")
	assert_eq(engine._valid_targets(hero, engine.db.skill(&"attack"), [engine.find(&"the_surge")]).size(), 0)


func test_an_entry_turn_is_never_the_players_and_plays_its_own_ai() -> void:
	_to_turn_of(&"the_climb")
	assert_false(engine.is_party_turn(), "the Climb is not commanded")
	assert_false(engine.is_player_side_turn())
	var before := engine.objective_count
	var res := engine.run_enemy_turn()
	assert_true(res.ok)
	assert_eq(res.skill_id, &"climb")
	assert_eq(engine.objective_count, before + 1, "a group reached the top")


func test_the_objective_wins_on_its_quota_and_the_standing_foes_withdraw_for_nothing() -> void:
	engine.objective["quota"] = 2
	var felled := engine.enemies[0]
	felled.apply_damage(felled.max_hp)
	assert_eq(engine.outcome, &"", "felling a foe ends nothing yet")
	_play_out()
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_eq(engine.objective_count, 2, "two groups up")
	var standing := engine.enemies[1]
	assert_true(standing.withdrawn, "the rest pull back down the wall")
	assert_false(standing.is_alive())
	assert_true(standing.hp > 0, "withdrawn, not felled")
	assert_eq(engine.xp_awards().get(&"hero", -1), felled.xp_reward, "XP counts only the felled")


func test_felling_every_foe_does_not_end_an_objective_fight() -> void:
	for e in engine.enemies:
		e.apply_damage(e.max_hp)
	assert_false(engine._check_outcome(), "the climbers are still on the stair")
	_to_turn_of(&"hero")
	for e in engine.enemies:
		e.apply_damage(e.max_hp)  # and whatever the Surge brought up meanwhile
	assert_true(engine.living_foes_of(engine.current).is_empty())
	var hero := engine.current
	var turns := hero.turns_taken
	SimPolicyNaive.new().take_turn(engine)
	assert_eq(hero.turns_taken, turns + 1, "the sim takes a lawful turn, never a stall")


func test_a_scripted_escape_counts_only_from_its_phase_and_awards_the_felled() -> void:
	engine = _engine(&"reach", [&"guard", &"hero"] as Array[StringName], [] as Array[StringName])
	assert_true(engine.find(&"the_surge") == null or not engine.entries.has(engine.find(&"the_surge")))
	assert_eq(engine.pending_entries.size(), 1, "the Surge waits for the breach")
	_to_turn_of(&"the_climb")
	engine.run_enemy_turn()
	assert_eq(engine.objective_count, 0, "before the breach the climb does not count")
	var boss := engine.enemies[0]
	boss.apply_damage(boss.max_hp)
	assert_eq(boss.hp, boss.max_hp * 30 / Formulas.PCT, "the floor holds it at 30%")
	_to_turn_of(&"hero", true)
	assert_eq(BossMechanics.phase_id(boss), "breach")
	assert_true(boss.untargetable and boss.damage_immune)
	assert_true(engine.entries.has(engine.find(&"the_surge")), "the Surge joined at the breach")
	_play_out()
	assert_eq(engine.outcome, BattleEngine.OUTCOME_SCRIPTED_ESCAPE)
	assert_true(BattleSpoils.SPOILS_OUTCOMES.has(engine.outcome))
	assert_eq(engine.xp_awards().get(&"hero", -1), 0, "the Reach withdrew; nothing felled")


# --- phases --------------------------------------------------------------------------------------


func test_an_untargetable_damage_immune_phase_cannot_be_touched() -> void:
	engine = _engine(&"reach", [&"guard", &"hero"] as Array[StringName], [] as Array[StringName])
	engine.objective["quota"] = 99
	var boss := engine.enemies[0]
	boss.apply_damage(boss.max_hp)
	_to_turn_of(&"hero", true)
	for e in engine.enemies:
		if e != boss:
			e.apply_damage(e.max_hp)  # the Dark's wing and the Surge's spawn
	assert_true(engine.living_foes_of(engine.current).is_empty(), "nothing to target")
	var res := engine.perform(&"attack", [boss] as Array[BattleCombatant])
	assert_eq(res.fail_reason, &"no_valid_target")
	var hp := boss.hp
	assert_eq(boss.apply_damage(100), 0, "and nothing wounds it")
	assert_eq(boss.hp, hp)


func test_the_hp_floor_holds_a_hit_but_not_a_heal() -> void:
	engine = _engine(&"reach", [&"hero"] as Array[StringName], [] as Array[StringName])
	var boss := engine.enemies[0]
	boss.hp = 200
	boss.apply_damage(-50)
	assert_eq(boss.hp, 250, "below the floor a heal still heals")
	boss.apply_damage(100)
	assert_eq(boss.hp, 250, "and a hit can't take it lower")


func test_storm_dark_rules_darken_the_party_and_slow_the_ward_until_lit() -> void:
	engine = _engine(&"reach", [&"guard", &"hero"] as Array[StringName], [] as Array[StringName])
	var boss := engine.enemies[0]
	boss.apply_damage(boss.max_hp / 2)
	_to_turn_of(&"hero", true)
	assert_eq(BossMechanics.phase_id(boss), "dark")
	assert_true(engine.fields.has(&"dark"))
	assert_true(engine.current.has_status(&"darkness"), "darkened at the start of its turn")
	var wing: BattleCombatant = null
	for e in engine.enemies:
		if e != boss:
			wing = e
	assert_eq(wing.field, &"dark", "spawn_bound: the phase's spawn are bound to the field")
	_to_turn_of(&"the_climb")
	assert_true(engine.ward().has_status(&"slow"), "the climbers can't see the stair")
	_to_turn_of(&"hero")
	assert_true(engine.perform(&"flare", engine.living_foes_of(engine.current)).ok)
	assert_false(engine.fields.has(&"dark"), "the wall is lit")
	assert_false(engine.field_rules.has(&"dark"))
	assert_false(wing.is_alive(), "its bound spawn fall")
	_to_turn_of(&"guard", true)
	_to_turn_of(&"guard", true)
	assert_false(engine.current.has_status(&"darkness"), "no more darkness once its last turn wore off")


# --- party rules ---------------------------------------------------------------------------------


func test_a_locked_hero_cannot_be_swapped_out_and_kerrid_is_not_here() -> void:
	assert_eq(engine.find(&"kerrid"), null, "unavailable: left out")
	assert_eq(engine.unavailable, [&"kerrid"] as Array[StringName])
	assert_eq(engine.unavailable_key, "TEST_NOT_HERE")
	_to_turn_of(&"guard")
	assert_eq(engine.swap_refusal(&"guard"), BattleSetPiece.FAIL_LOCKED)
	assert_false(engine.swap(&"guard", &"scout"), "Toma holds the stair")
	assert_eq(engine.locked_key, "TEST_LOCKED")
	assert_eq(engine.preview_swap(&"guard", &"scout").size(), 0)
	_to_turn_of(&"hero")
	assert_eq(engine.swap_refusal(&"hero"), &"")
	assert_true(engine.swap(&"hero", &"scout"), "the others swap as ever")


func test_a_fallen_locked_hero_may_be_replaced() -> void:
	var g := engine.find(&"guard")
	g.apply_damage(g.max_hp)
	assert_eq(engine.swap_refusal(&"guard"), &"", "the lock holds a standing hero only")


func test_a_locked_hero_set_in_reserve_takes_a_slot() -> void:
	engine = _engine(&"stair", [&"hero", &"liss", &"scout"] as Array[StringName], [&"guard"] as Array[StringName])
	assert_true(engine.party_active.has(engine.find(&"guard")), "seated at the stair-head")
	assert_eq(engine.party_active.size(), 3)
	assert_true(engine.party_reserve.has(engine.find(&"scout")), "the last unlocked slot stepped back")
	engine = _engine(&"stair", [&"hero"] as Array[StringName], [&"guard"] as Array[StringName])
	assert_eq(engine.party_active.size(), 2, "with room it simply joins")


func test_the_attack_override_replaces_attack_with_stand_firm() -> void:
	var g := engine.find(&"guard")
	assert_eq(g.attack_skill, &"firm")
	assert_false(g.skills.has(&"attack"))
	assert_eq(g.skills.count(&"firm"), 1, "known once, not twice")
	assert_eq(engine.find(&"hero").attack_skill, &"attack")
	var row := {"attack_override": {"liss": "firm", "scout": "firm"}}
	var liss := engine.find(&"liss")
	liss.skills.erase(&"attack")
	BattleSetPiece._override_attacks(engine, row["attack_override"])
	assert_eq(liss.skills[0], &"firm", "with no Attack to replace it comes first")
	assert_eq(engine.find(&"scout").skills[0], &"firm", "in Attack's place")


# --- the ward's guard ----------------------------------------------------------------------------


func test_hold_the_stair_covers_the_climb() -> void:
	_to_turn_of(&"guard")
	assert_true(engine.perform(&"hold", [engine.current] as Array[BattleCombatant]).ok)
	assert_eq(engine.ward().covered_by, &"guard")


func test_a_covered_grip_lands_as_a_blow_and_the_climb_is_not_pushed() -> void:
	var climb := engine.ward()
	var g := engine.find(&"guard")
	var mite := engine.enemies[0]
	_to_turn_of(mite.id)
	climb.covered_by = &"guard"
	var t := climb.next_time
	var hp := g.hp
	var res := engine.perform(&"grip", [climb] as Array[BattleCombatant])
	assert_true(res.ok)
	assert_eq(res.intercepted_by, &"guard")
	assert_eq(res.hits[0]["target_id"], &"guard", "the blow lands on him")
	assert_true(g.hp < hp, "as a physical hit (grip_blow)")
	assert_eq(climb.next_time, t, "the Climb is not pushed")
	assert_eq(climb.covered_by, &"", "the cover is spent")
	_to_turn_of(engine.enemies[1].id)
	var t2 := climb.next_time
	assert_true(engine.perform(&"grip", [climb] as Array[BattleCombatant]).ok)
	assert_true(climb.next_time > t2, "the next grip lands on the stair")


func test_the_cover_ends_at_the_coverers_next_turn() -> void:
	_to_turn_of(&"guard")
	engine.perform(&"hold", [engine.current] as Array[BattleCombatant])
	_to_turn_of(&"guard")
	assert_eq(engine.ward().covered_by, &"")


func test_a_provoked_foe_grips_its_provoker_instead() -> void:
	var mite := engine.enemies[0]
	mite.add_status(&"provoke", 3)
	mite.provoker_id = &"hero"
	_to_turn_of(mite.id)
	var res := engine.perform(&"grip", [engine.ward()] as Array[BattleCombatant])
	assert_eq(res.intercepted_by, &"hero")


func test_stand_firm_takes_a_counter_stance_until_his_next_turn() -> void:
	_to_turn_of(&"guard")
	var g := engine.current
	assert_true(engine.perform(&"firm", [g] as Array[BattleCombatant]).ok)
	assert_eq(g.counter_skill, &"riposte")
	assert_true(g.has_status(&"protect"))
	_to_turn_of(&"guard")
	assert_eq(g.counter_skill, &"", "the stance ends at his next turn")


func test_the_stance_answers_a_landed_blow_but_not_magic() -> void:
	var g := engine.find(&"guard")
	var mite := engine.enemies[0]
	_to_turn_of(mite.id)
	g.counter_skill = &"riposte"
	var hp := mite.hp
	var res := engine.perform(&"attack", [g] as Array[BattleCombatant])
	assert_eq(res.hits.size(), 2, "the blow and the answer")
	assert_eq(res.hits[1]["counter_by"], &"guard")
	assert_true(mite.hp < hp)
	_to_turn_of(engine.enemies[1].id)
	g.counter_skill = &"riposte"
	var magic := engine.perform(&"bolt", [g] as Array[BattleCombatant])
	assert_eq(magic.hits.size(), 1, "magic is not countered")


func test_haul_hastes_the_climb_and_a_rope_dive_strips_it() -> void:
	_to_turn_of(&"liss")
	assert_true(engine.current.skills.has(&"haul"), "lent, with the hoist flag set")
	var climb := engine.ward()
	assert_true(engine.perform(&"haul", [climb] as Array[BattleCombatant]).ok)
	assert_true(climb.has_status(&"haste"))
	_to_turn_of(engine.enemies[0].id)
	engine.perform(&"dive", [climb] as Array[BattleCombatant])
	assert_false(climb.has_status(&"haste"), "the rope is dived")


func test_a_lent_skill_keeps_its_flag_lock() -> void:
	var e := BattleEngine.new()
	e.setup(_db(), [&"liss"] as Array[StringName], [] as Array[StringName], &"stair", SEED)
	assert_false(e.find(&"liss").skills.has(&"haul"), "no hoist rigged, no Haul")


func test_ward_skills_target_only_the_ward() -> void:
	var liss := engine.find(&"liss")
	var haul := engine.db.skill(&"haul")
	assert_eq(engine._valid_targets(liss, haul, [liss] as Array[BattleCombatant]).size(), 0)
	assert_eq(engine._valid_targets(liss, haul, [engine.ward()] as Array[BattleCombatant]).size(), 1)
	var mite := engine.enemies[0]
	assert_eq(EnemyAI.select_targets(engine, mite, &"ward"), [engine.ward()] as Array[BattleCombatant])


func test_ai_reads_the_wards_status_and_likely_skills_follow_the_first_rule() -> void:
	var mite := engine.enemies[0]
	assert_false(EnemyAI._holds(engine, mite, &"ward_has_status", "haste"))
	engine.ward().add_status(&"haste", 2)
	assert_true(EnemyAI._holds(engine, mite, &"ward_has_status", "haste"))
	assert_eq(EnemyAI.likely_skills(engine, mite), [&"dive"] as Array[StringName], "it dives a hauled rope")
	engine.ward().statuses.clear()
	assert_eq(EnemyAI.likely_skills(engine, mite), [&"attack"] as Array[StringName])


func test_a_telegraphed_grip_lands_on_the_ward_through_the_charge() -> void:
	var mite := engine.enemies[0]
	_to_turn_of(mite.id)
	engine.perform(&"reach", [mite] as Array[BattleCombatant])
	assert_eq(mite.charge_skill, &"grip")
	_to_turn_of(mite.id)
	var t := engine.ward().next_time
	var res := engine.run_enemy_turn()
	assert_eq(res.skill_id, &"grip")
	assert_true(engine.ward().next_time > t, "pushed back")


func test_a_breach_pushes_the_opposing_ward() -> void:
	var mite := engine.enemies[0]
	_to_turn_of(mite.id)
	var t := engine.ward().next_time
	var res := engine.perform(&"smash", engine.living_foes_of(mite))
	assert_true(engine.ward().next_time > t)
	assert_eq(res.hits[-1]["target_id"], &"the_climb")


# --- the Surge and Pell --------------------------------------------------------------------------


func test_the_surge_adds_spawn_up_to_its_cap() -> void:
	var surge := engine.find(&"the_surge")
	assert_eq(surge.summon_cap, 2)
	assert_false(BattleSetPiece.may_summon(engine, surge), "two stand already")
	engine.enemies[0].apply_damage(engine.enemies[0].max_hp)
	assert_true(BattleSetPiece.may_summon(engine, surge))
	_to_turn_of(&"the_surge")
	engine.run_enemy_turn()
	assert_eq(engine.enemies.size(), 3, "a fresh mite climbs the wall")
	_to_turn_of(&"the_surge")
	engine.run_enemy_turn()
	assert_eq(engine.enemies.size(), 3, "capped")


func test_storm_call_draws_off_a_mover_and_spares_the_rooted() -> void:
	engine = _engine(&"pell", [&"hero"] as Array[StringName], [] as Array[StringName])
	var pell := engine.find(&"the_kirru")
	assert_eq(pell.entry_role, BattleSetPiece.ROLE_GUEST)
	_to_turn_of(&"the_kirru")
	engine.run_enemy_turn()
	assert_eq(pell.charge_skill, &"call", "telegraphed one turn ahead")
	var intent := false
	for e in engine.preview():
		intent = intent or e.combatant_id == &"the_kirru" and e.intent == &"call"
	assert_true(intent, "the timeline shows it")
	_to_turn_of(&"the_kirru")
	var res := engine.run_enemy_turn()
	assert_eq(res.skill_id, &"call")
	var mover := engine.enemies[0]
	var rooted := engine.enemies[1]
	assert_true(mover.withdrawn, "it follows the sound")
	assert_true(rooted.is_alive(), "the rooted polyp can't follow")
	assert_true(BattleSetPiece.spares(engine.db.skill(&"call"), rooted))
	assert_eq(engine._valid_targets(pell, engine.db.skill(&"call"), [rooted] as Array[BattleCombatant]).size(), 0)
	rooted.apply_damage(rooted.max_hp)
	engine.objective_count = 99
	_to_turn_of(&"hero", true)
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_eq(engine.xp_awards()[&"hero"], rooted.xp_reward, "the withdrawn gives no XP")
	assert_eq(engine.currency_award(), 5, "nor lume: only the felled polyp's")


func test_vowbound_previews_keep_the_climb_on_the_order() -> void:
	engine.vowbound = BattleVowbound.new([_virel_row()], [&"spirit"] as Array[StringName])
	_to_turn_of(&"hero")
	var ids := {}
	for e in engine.vowbound.preview_call(engine, &"spirit"):
		ids[e.combatant_id] = true
	assert_true(ids.has(&"the_climb"))


# --- helpers -------------------------------------------------------------------------------------


func _engine(enc: StringName, active: Array[StringName], reserve: Array[StringName]) -> BattleEngine:
	var e := BattleEngine.new()
	e.story_flags.append(&"hoist")
	e.setup(_db(), active, reserve, enc, SEED)
	e.begin()
	return e


## Plays turns (the party guards) until `cid` holds the turn. With `next`, skips the current one first.
func _to_turn_of(cid: StringName, next: bool = false) -> void:
	if next:
		_step()
	for _i in STEPS:
		if engine.outcome != &"" or engine.current != null and engine.current.id == cid:
			return
		_step()


func _step() -> void:
	if engine.is_party_turn():
		engine.perform(&"guard", [engine.current] as Array[BattleCombatant])
	else:
		engine.run_enemy_turn()


func _play_out() -> void:
	for _i in STEPS:
		if engine.outcome != &"":
			return
		_step()


static func _virel_row() -> Dictionary:
	var base := {}
	var scale := {}
	for k: String in BattleVowbound.STAT_FIELDS:
		base[k] = 10
		scale[k] = 0
	return {
		"id": "spirit",
		"caller": "hero",
		"call_rank": 3,
		"base": base,
		"scale_pct": scale,
		"skills": ["attack"],
		"swell": {"rate": 100, "technique": "flare"}
	}


static func _db() -> BattleDB:
	var stats := {
		"level": 5,
		"hp": 1000,
		"mp": 50,
		"strength": 1,
		"magic": 1,
		"defense": 0,
		"magic_defense": 0,
		"agility": 10,
		"accuracy": 100,
		"evasion": 0,
		"luck": 0,
	}
	var skills: Array = [
		{"id": "attack", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "target": "single_foe"},
		{"id": "bolt", "kind": "magical", "power": 1, "rank": 3, "target": "single_foe"},
		{"id": "guard", "kind": "support", "rank": 3, "target": "self"},
		{"id": "taunt", "kind": "support", "rank": 2, "target": "single_foe", "statuses": [{"id": "provoke"}]},
		{"id": "hold", "kind": "support", "rank": 2, "target": "self", "covers": "ward"},
		{
			"id": "firm",
			"kind": "support",
			"rank": 3,
			"target": "self",
			"counter": "riposte",
			"statuses": [{"id": "protect", "duration": 2}]
		},
		{"id": "riposte", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "target": "single_foe"},
		{
			"id": "haul",
			"kind": "support",
			"rank": 3,
			"target": "ward",
			"requires_flag": "hoist",
			"statuses": [{"id": "haste", "duration": 3}]
		},
		{"id": "grip", "kind": "support", "rank": 3, "target": "ward", "delay_ranks": 2, "on_cover": "grip_blow"},
		{"id": "grip_blow", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "target": "single_foe"},
		{"id": "dive", "kind": "support", "rank": 3, "target": "ward", "cleanses": ["haste"], "delay_ranks": 1},
		{"id": "reach", "kind": "support", "rank": 2, "target": "self", "charge": {"skill": "grip", "turns": 1}},
		{
			"id": "smash",
			"kind": "physical",
			"power": 1,
			"rank": 3,
			"accuracy": 100,
			"target": "all_foes",
			"pushes_ward": 2
		},
		{"id": "climb", "kind": "support", "rank": 3, "target": "self"},
		{"id": "rise", "kind": "support", "rank": 3, "target": "self", "summon": "mite"},
		{"id": "call_sound", "kind": "support", "rank": 3, "target": "self", "charge": {"skill": "call", "turns": 1}},
		{"id": "call", "kind": "support", "rank": 3, "target": "single_foe", "withdraws": true, "spares_tag": "rooted"},
		{
			"id": "flare",
			"kind": "magical",
			"power": 1,
			"rank": 3,
			"target": "all_foes",
			"clears_field": "dark",
			"swell": true
		},
	]
	var statuses: Array = []
	for sid: String in ["haste", "slow", "darkness", "protect", "provoke"]:
		statuses.append({"id": sid, "default_duration": 3})
	var mite := {
		"stats": stats,
		"skills": ["attack", "bolt", "grip", "reach", "dive", "smash"],
		"xp": 10,
		"currency": 5,
		"tags": ["spawn"],
		"ai":
		[
			{"if": {"ward_has_status": "haste"}, "pick": [{"skill": "dive", "target": "ward"}]},
			{"pick": [{"skill": "attack", "target": "random_foe"}]}
		],
	}
	var rooted := mite.duplicate(true)
	rooted["tags"] = ["spawn", "rooted"]
	rooted["xp"] = 7
	var boss := {
		"stats": stats,
		"skills": ["attack"],
		"xp": 100,
		"delay_immune": true,
		"hp_floor_pct": 30,
		"ai": [{"pick": [{"skill": "attack", "target": "random_foe"}]}],
		"phases":
		[
			{
				"id": "dark",
				"at_hp_pct": 60,
				"field": "dark",
				"spawn": ["mite"],
				"spawn_bound": true,
				"field_rules":
				[{"on": "party", "status": "darkness", "duration": 2}, {"on": "ward", "status": "slow", "duration": 1}]
			},
			{"id": "breach", "at_hp_pct": 30, "untargetable": true, "damage_immune": true},
		],
	}
	var hero_skills := ["attack", "bolt", "guard", "flare"]
	var climb := {
		"id": "the_climb",
		"name_key": "TEST_CLIMB",
		"side": "party",
		"role": "ward",
		"agility": 10,
		"skills": ["climb"],
		"ai": [{"pick": [{"skill": "climb", "target": "self"}]}]
	}
	var surge := {
		"id": "the_surge",
		"name_key": "TEST_SURGE",
		"side": "enemy",
		"role": "tide",
		"agility": 10,
		"delay_immune": true,
		"summon_cap": 2,
		"skills": ["rise"],
		"ai": [{"pick": [{"skill": "rise", "target": "self"}]}]
	}
	var pell := {
		"id": "the_kirru",
		"name_key": "TEST_PELL",
		"side": "party",
		"role": "guest",
		"agility": 30,
		"skills": ["call_sound", "call"],
		"ai": [{"pick": [{"skill": "call_sound", "target": "self"}]}]
	}
	var late_surge := surge.duplicate(true)
	late_surge["joins_at_phase"] = "breach"
	var party := {
		"locked_active": ["guard"],
		"locked_key": "TEST_LOCKED",
		"unavailable": ["kerrid"],
		"unavailable_key": "TEST_NOT_HERE",
		"attack_override": {"guard": "firm"},
		"party_skills": {"liss": ["haul"]},
	}
	var stair := {"id": "stair", "enemies": ["mite", "mite"], "entries": [climb, surge]}
	stair["objective"] = {"ward": "the_climb", "quota": 99}
	stair.merge(party)
	var reach := {"id": "reach", "enemies": ["boss"], "entries": [climb, late_surge]}
	reach["objective"] = {"ward": "the_climb", "quota": 1, "from_phase": "breach", "outcome": "scripted_escape"}
	var pell_enc := {"id": "pell", "enemies": ["mite", "rooted"], "entries": [climb, pell]}
	pell_enc["objective"] = {"ward": "the_climb", "quota": 99}
	return (
		BattleDB
		. from_tables(
			{
				"skills": skills,
				"statuses": statuses,
				"characters":
				[
					{"id": "hero", "stats": stats, "skills": hero_skills},
					{"id": "guard", "stats": stats, "skills": ["attack", "hold", "firm", "guard", "bolt", "taunt"]},
					{"id": "liss", "stats": stats, "skills": ["attack", "guard"]},
					{"id": "scout", "stats": stats, "skills": ["attack", "guard"]},
					{"id": "kerrid", "stats": stats, "skills": ["attack", "guard"]},
				],
				"enemies":
				[
					_with_id(mite, "mite"),
					_with_id(rooted, "rooted"),
					_with_id(boss, "boss"),
				],
				"encounters": [stair, reach, pell_enc],
			}
		)
	)


static func _with_id(row: Dictionary, eid: String) -> Dictionary:
	var out := row.duplicate(true)
	out["id"] = eid
	return out


func test_field_rules_pick_their_side_and_an_entry_never_withdraws() -> void:
	var mite := engine.enemies[0]
	var hero := engine.find(&"hero")
	assert_true(BattleSetPiece._rule_applies(BattleSetPiece.RULE_ON_ENEMY, mite))
	assert_false(BattleSetPiece._rule_applies(BattleSetPiece.RULE_ON_ENEMY, hero))
	assert_false(BattleSetPiece._rule_applies(BattleSetPiece.RULE_ON_ENEMY, engine.find(&"the_surge")))
	assert_false(BattleSetPiece._rule_applies("nobody", hero))
	engine.ward().withdraw()
	assert_false(engine.ward().withdrawn, "the Climb never leaves")
	assert_true(engine.ward().is_alive())
