extends TestCase
## M1-CMB-02: Petrify, Berserk, Confuse, Doom, Zombie, Reflect and Provoke (formulas.md
## § Statuses), on a fixture DB so tuning the real tables never breaks these rules.

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()


# --- formulas ----------------------------------------------------------------------------


func test_berserk_strength_formula() -> void:
	assert_eq(Formulas.berserk_strength(16), 24)
	assert_eq(Formulas.berserk_strength(15), 22, "15 x 3/2 = 22.5 floors")
	assert_eq(Formulas.berserk_strength(0), 0)


func test_berserk_applies_after_power_break() -> void:
	var c := BattleCombatant.new()
	c.hp = 10
	c.strength = 16
	c.add_status(&"berserk", -1)
	assert_eq(c.effective_strength(), 24)
	c.add_status(&"power_break", -1)
	assert_eq(c.effective_strength(), 12, "floor(16 x 0.5) = 8, then x3/2")


# --- Petrify -----------------------------------------------------------------------------


func test_petrify_counts_as_ko_and_leaves_timeline() -> void:
	_start(&"pair")
	var foe := engine.enemies[0]
	var r := engine.perform(&"stone_gaze", _one(foe))
	assert_eq(r.hits[0]["statuses_added"], [&"petrify"])
	assert_true(foe.is_petrified())
	assert_false(foe.is_alive(), "stone is out of the fight")
	assert_true(foe.hp > 0, "petrify is not HP loss")
	for e in engine.preview(&"", null, 20):
		assert_ne(e.combatant_id, foe.id, "petrified units never act")
	assert_false(engine.living_foes_of(engine.find(&"hero")).has(foe))


func test_petrified_target_is_rejected() -> void:
	_start(&"pair")
	var foe := engine.enemies[0]
	foe.add_status(&"petrify", -1)
	var actor := engine.current
	assert_eq(engine.perform(&"attack", _one(foe)).fail_reason, &"no_valid_target")
	assert_eq(engine.current, actor, "costs nothing")


func test_petrify_clears_other_statuses_and_blocks_new_ones() -> void:
	var c := BattleCombatant.new()
	c.hp = 10
	c.add_status(&"poison", -1)
	c.add_status(&"doom", 3)
	c.add_status(&"petrify", -1)
	assert_eq(c.statuses.keys(), [&"petrify"])
	assert_false(c.add_status(&"haste", 4))


func test_petrifying_the_last_foe_is_victory() -> void:
	_start(&"plain")
	engine.perform(&"stone_gaze", _first_foe())
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	var xp := engine.xp_awards()
	assert_eq(xp.get(&"hero", 0), 1, "a petrified foe still pays out")


func test_petrified_party_is_defeat() -> void:
	_start(&"plain")
	var actor := engine.current
	var other := _other_active(actor)
	other.add_status(&"petrify", -1)
	var me: Array[BattleCombatant] = [actor]
	engine.perform(&"stone_self", me)
	assert_eq(engine.outcome, BattleEngine.OUTCOME_DEFEAT, "every active member stone = game over")


func test_petrified_member_earns_no_xp() -> void:
	_start(&"pair")
	var actor := engine.current
	_other_active(actor).add_status(&"petrify", -1)
	engine.enemies[1].hp = 0
	engine.perform(&"stone_gaze", _one(engine.enemies[0]))
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	var xp := engine.xp_awards()
	assert_true(xp.has(actor.id))
	assert_false(xp.has(_other_active(actor).id), "stone at victory = not alive for the XP rule")


func test_petrified_member_can_be_swapped_out_like_ko() -> void:
	_start(&"plain")
	var other := _other_active(engine.current)
	other.add_status(&"petrify", -1)
	var now := engine.now
	assert_true(engine.swap(other.id, &"bench"))
	var bench := engine.find(&"bench")
	assert_eq(bench.next_time, now + Formulas.action_delay(bench.agility, Formulas.DEFAULT_RANK))
	assert_false(engine.swap(bench.id, other.id), "stone cannot come back in")


func test_preview_honest_for_petrify() -> void:
	_start(&"pair")
	_assert_preview_matches_play(&"stone_gaze", engine.enemies[1])


# --- Berserk -----------------------------------------------------------------------------


func test_berserk_party_member_acts_on_its_own() -> void:
	_start(&"pair")
	var actor := engine.current
	actor.add_status(&"berserk", -1)
	assert_false(engine.is_party_turn())
	assert_true(engine.is_auto_turn())
	assert_true(engine.is_player_side_turn())
	assert_eq(engine.perform(&"attack", _first_foe()).fail_reason, &"auto_turn")
	assert_false(engine.swap(actor.id, &"bench"), "no menu, so no swap on its own turn")
	assert_false(engine.escape())
	var r := engine.run_enemy_turn()
	assert_true(r.ok)
	assert_eq(r.actor_id, actor.id)
	assert_eq(r.auto_reason, &"berserk")
	assert_eq(r.skill_id, &"attack")
	assert_eq(engine.find(r.hits[0]["target_id"]).team, BattleCombatant.TEAM_ENEMY)
	assert_ne(engine.current, actor, "the auto turn ended")


func test_berserk_targets_follow_the_seed() -> void:
	var picks: Array[String] = []
	for rng_seed in range(1, 25):
		picks.append(_berserk_pick(rng_seed))
	var again: Array[String] = []
	for rng_seed in range(1, 25):
		again.append(_berserk_pick(rng_seed))
	assert_eq(picks, again, "deterministic per seed")
	assert_true(picks.has("pair_a#1") and picks.has("pair_b#2"), "random over the foes: %s" % str(picks))


func test_berserk_enemy_without_attack_uses_first_physical_skill() -> void:
	_start(&"clawed")
	var foe := engine.enemies[0]
	foe.add_status(&"berserk", -1)
	foe.next_time = engine.now  # its turn comes next
	engine.perform(&"jab", _first_foe())
	var guard := 0
	while engine.current != foe and guard < 20:
		guard += 1
		_step(&"jab")
	var r := engine.run_enemy_turn()
	assert_eq(r.skill_id, &"claw")
	assert_eq(r.auto_reason, &"berserk")


func test_berserk_raises_damage() -> void:
	var plain := 0
	var mad := 0
	for rng_seed in range(1, 11):
		plain += _damage_of_attack(false, rng_seed)
		mad += _damage_of_attack(true, rng_seed)
	assert_true(mad > plain, "berserk %d vs plain %d" % [mad, plain])


# --- Confuse -----------------------------------------------------------------------------


func test_confuse_hits_random_sides_never_itself() -> void:
	var allies := 0
	var foes := 0
	var log_a: Array[String] = []
	for rng_seed in range(1, 41):
		var r := _confused_hit(rng_seed)
		log_a.append(str(r))
		assert_ne(r[0], r[1], "a confused unit never targets itself")
		if r[2]:
			allies += 1
		else:
			foes += 1
	assert_true(allies > 0 and foes > 0, "%d ally / %d foe hits" % [allies, foes])
	var log_b: Array[String] = []
	for rng_seed in range(1, 41):
		log_b.append(str(_confused_hit(rng_seed)))
	assert_eq(log_a, log_b, "deterministic per seed")


func test_physical_hit_cures_confuse() -> void:
	_start(&"plain")
	var foe := _first_foe()[0]
	foe.add_status(&"confuse", 3)
	engine.perform(&"attack", _first_foe())
	assert_false(foe.has_status(&"confuse"))


func test_magic_does_not_cure_confuse() -> void:
	_start(&"plain")
	var foe := _first_foe()[0]
	foe.add_status(&"confuse", 3)
	engine.perform(&"zap", _first_foe())
	assert_true(foe.has_status(&"confuse"))


func test_confuse_wins_over_berserk() -> void:
	var c := BattleCombatant.new()
	c.hp = 1
	c.add_status(&"berserk", -1)
	c.add_status(&"confuse", 2)
	assert_eq(BattleEngine.auto_reason(c), &"confuse")


func test_confused_enemy_turn_is_automatic() -> void:
	_start(&"pair")
	var foe := engine.enemies[1]  # the party jabs enemies[0]; a physical hit would cure it
	foe.add_status(&"confuse", 3)
	foe.next_time = engine.now
	engine.perform(&"jab", _first_foe())
	var guard := 0
	while engine.current != foe and guard < 20:
		guard += 1
		_step(&"jab")
	var r := engine.run_enemy_turn()
	assert_eq(r.auto_reason, &"confuse")
	assert_eq(r.skill_id, &"attack")


# --- Doom --------------------------------------------------------------------------------


func test_doom_counts_down_on_the_timeline_and_falls() -> void:
	_start(&"plain")
	var foe := _first_foe()[0]
	var counts: Array[int] = []
	var last_time := -1
	for e in engine.preview(&"doom_toll", foe, 30):
		if e.combatant_id == foe.id:
			counts.append(e.doom)
			last_time = e.time
	assert_eq(counts, [3, 2, 1] as Array[int], "three more turns, then no entry")
	engine.perform(&"doom_toll", _one(foe))
	assert_eq(foe.doom_count(), 3)
	var acted: Array[int] = []
	var guard := 0
	while foe.is_alive() and guard < 100:
		guard += 1
		if engine.current == foe:
			acted.append(engine.now)
		_step(&"jab")
	assert_false(foe.is_alive())
	assert_eq(acted.size(), 3)
	assert_eq(acted[-1], last_time, "falls at the end of the turn the timeline marked 1")
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)


func test_doom_counts_lost_turns() -> void:
	_start(&"plain")
	var foe := _first_foe()[0]
	foe.add_status(&"stop", 2)
	foe.add_status(&"doom", 2)
	var entries: Array[TurnEntry] = []
	for e in engine.preview(&"", null, 20):
		if e.combatant_id == foe.id:
			entries.append(e)
	assert_eq(entries.size(), 2)
	assert_true(entries[0].skipped and entries[1].skipped)
	assert_eq([entries[0].doom, entries[1].doom], [2, 1])
	var guard := 0
	while engine.outcome == &"" and guard < 100:
		guard += 1
		_step(&"jab")
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY, "Doom on a lost turn still ends the fight")
	assert_eq(foe.turns_taken, 0, "it never acted")


func test_preview_honest_for_doom() -> void:
	_start(&"pair")
	_assert_preview_matches_play(&"doom_toll", engine.enemies[1])


func test_turn_entry_doom_zero_without_doom() -> void:
	_start(&"plain")
	for e in engine.preview():
		assert_eq(e.doom, 0)


# --- Zombie ------------------------------------------------------------------------------


func test_zombie_heal_harms() -> void:
	_start(&"plain")
	var target := _other_active(engine.current)
	target.add_status(&"zombie", -1)
	target.hp = 200
	var r := engine.perform(&"mend", _one(target))
	var lost := 200 - target.hp
	var lo := Formulas.heal_amount(5, 10, 5, Formulas.VARIANCE_MIN_PCT, false)
	var hi := Formulas.heal_amount(5, 10, 5, Formulas.VARIANCE_MAX_PCT, false)
	assert_between(lost, lo, hi, "the heal amount, dealt as damage")
	assert_eq(r.hits[0]["amount"], lost, "amount is positive: HP lost")


func test_zombie_heal_can_ko() -> void:
	_start(&"plain")
	var target := _other_active(engine.current)
	target.add_status(&"zombie", -1)
	target.hp = 1
	engine.perform(&"mend", _one(target))
	assert_false(target.is_alive())


func test_zombie_regen_harms() -> void:
	_start(&"plain")
	var actor := engine.current
	actor.add_status(&"zombie", -1)
	actor.add_status(&"regen", -1)
	actor.hp = 200
	engine.perform(&"jab", _first_foe())
	assert_eq(actor.hp, 200 - Formulas.regen_heal(actor.max_hp))


func test_zombie_still_takes_normal_damage() -> void:
	var c := BattleCombatant.new()
	c.max_hp = 100
	c.hp = 100
	c.add_status(&"zombie", -1)
	assert_eq(c.apply_damage(10), -10)
	assert_eq(c.restore_hp(5), -5)


# --- Reflect -----------------------------------------------------------------------------


func test_reflect_bounces_single_target_magic_to_lowest_hp_on_other_side() -> void:
	_start(&"pair")
	var mirror := engine.enemies[0]
	mirror.add_status(&"reflect", 4)
	var actor := engine.current
	var weak := _other_active(actor)
	weak.hp = 200
	var mirror_hp := mirror.hp
	var r := engine.perform(&"zap", _one(mirror))
	assert_eq(r.hits[0]["target_id"], weak.id, "lowest-HP living unit on the caster's side")
	assert_eq(r.hits[0]["reflected_from"], mirror.id)
	assert_true(weak.hp < 200)
	assert_eq(mirror.hp, mirror_hp)


func test_reflect_cannot_chain() -> void:
	_start(&"pair")
	var mirror := engine.enemies[0]
	mirror.add_status(&"reflect", 4)
	var weak := _other_active(engine.current)
	weak.hp = 200
	weak.add_status(&"reflect", 4)
	var r := engine.perform(&"zap", _one(mirror))
	assert_eq(r.hits[0]["target_id"], weak.id, "a bounced spell lands even on a reflector")
	assert_true(weak.hp < 200)


func test_reflect_ignores_physical_self_and_group_skills() -> void:
	_start(&"pair")
	var mirror := engine.enemies[0]
	mirror.add_status(&"reflect", 4)
	var r := engine.perform(&"attack", _one(mirror))
	assert_eq(r.hits[0]["target_id"], mirror.id, "physical is not reflected")
	assert_false(r.hits[0].has("reflected_from"))
	_to_party_turn()
	var both: Array[BattleCombatant] = [engine.enemies[0], engine.enemies[1]]
	var g := engine.perform(&"zap_all", both)
	for h in g.hits:
		assert_false(h.has("reflected_from"), "group magic is not reflected")
	_to_party_turn()
	var actor := engine.current
	actor.add_status(&"reflect", 4)
	var me: Array[BattleCombatant] = [actor]
	engine.perform(&"quicken", me)
	assert_true(actor.has_status(&"haste"), "self-cast is not reflected")


func test_reflect_bounces_heal_onto_the_enemy() -> void:
	_start(&"pair")
	var ally := _other_active(engine.current)
	ally.add_status(&"reflect", 4)
	var hurt := engine.enemies[1]
	hurt.hp = 1000
	var r := engine.perform(&"mend", _one(ally))
	assert_eq(r.hits[0]["target_id"], hurt.id)
	assert_true(hurt.hp > 1000, "the bounce heals the lowest-HP foe")


func test_preview_honest_for_reflected_time_status() -> void:
	_start(&"pair")
	var mirror := engine.enemies[0]
	mirror.add_status(&"reflect", 4)
	_other_active(engine.current).hp = 200
	var predicted := engine.preview(&"slow_zap", mirror, 16)
	var landed_on := engine.reflect_recipient(engine.current, mirror, engine.db.skill(&"slow_zap"))
	assert_eq(landed_on, _other_active(engine.current))
	_assert_preview_matches_play(&"slow_zap", mirror, predicted)
	assert_true(landed_on.has_status(&"slow"))
	assert_false(mirror.has_status(&"slow"))


# --- Provoke -----------------------------------------------------------------------------


func test_provoke_forces_enemy_ai_target() -> void:
	_start(&"pair")
	var hero := engine.current
	var foe := engine.enemies[0]
	var r := engine.perform(&"taunt", _one(foe))
	assert_eq(r.hits[0]["statuses_added"], [&"provoke"])
	assert_eq(foe.provoker_id, hero.id)
	for i in 30:
		var choice := EnemyAI.choose(engine, foe)
		assert_eq(choice["targets"], [hero] as Array[BattleCombatant], "random_foe forced to the provoker")


func test_provoke_forces_player_target() -> void:
	_start(&"pair")
	var actor := engine.current
	var provoker := engine.enemies[1]
	actor.add_status(&"provoke", 3)
	actor.provoker_id = provoker.id
	assert_eq(engine.forced_target(actor, &"attack"), provoker)
	assert_eq(engine.forced_target(actor, &"sweep"), null, "group skills are free")
	assert_eq(engine.forced_target(actor, &"mend"), null, "ally skills are free")
	actor.mp = 10
	var r := engine.perform(&"zap", _one(engine.enemies[0]))
	assert_eq(r.fail_reason, &"provoked")
	assert_eq(actor.mp, 10, "a rejected target costs nothing")
	assert_eq(engine.current, actor)
	assert_true(engine.perform(&"attack", _one(provoker)).ok)


func test_provoke_allows_group_skills() -> void:
	_start(&"pair")
	var actor := engine.current
	actor.add_status(&"provoke", 3)
	actor.provoker_id = engine.enemies[1].id
	var both: Array[BattleCombatant] = [engine.enemies[0], engine.enemies[1]]
	assert_true(engine.perform(&"sweep", both).ok)


func test_provoke_ends_when_provoker_falls() -> void:
	_start(&"pair")
	var actor := engine.current
	var provoker := engine.enemies[1]
	actor.add_status(&"provoke", 3)
	actor.provoker_id = provoker.id
	provoker.hp = 0
	assert_eq(engine.forced_target(actor, &"attack"), null)
	assert_true(engine.perform(&"jab", _one(engine.enemies[0])).ok)
	assert_false(actor.has_status(&"provoke"), "pruned once the provoker is gone")


func test_provoke_ends_when_provoker_leaves_the_field() -> void:
	_start(&"pair")
	var hero := engine.current
	var foe := engine.enemies[0]
	engine.perform(&"taunt", _one(foe))
	_to_party_turn()
	assert_true(foe.has_status(&"provoke"))
	assert_true(engine.swap(hero.id, &"bench"))
	assert_false(foe.has_status(&"provoke"), "the provoker left the field")
	assert_eq(engine.forced_target(foe, &"attack"), null)


func test_berserk_respects_provoke() -> void:
	for rng_seed in range(1, 15):
		engine = BattleEngine.new()
		_start(&"pair", rng_seed)
		var actor := engine.current
		actor.add_status(&"berserk", -1)
		actor.add_status(&"provoke", 3)
		actor.provoker_id = engine.enemies[1].id
		var r := engine.run_enemy_turn()
		assert_eq(r.hits[0]["target_id"], engine.enemies[1].id)


# --- determinism -------------------------------------------------------------------------


func test_status_battles_stay_deterministic() -> void:
	var a := _chaos_log(77)
	var b := _chaos_log(77)
	assert_eq(a, b)
	assert_true(a[-1] in ["victory", "defeat"], "ended: %s" % a[-1])


# --- helpers -----------------------------------------------------------------------------


func _assert_preview_matches_play(skill: StringName, target: BattleCombatant, predicted: Array[TurnEntry] = []) -> void:
	if predicted.is_empty():
		predicted = engine.preview(skill, target, 16)
	var want: Array[String] = []
	for e in predicted:
		want.append("%s@%d/%d" % [e.combatant_id, e.time, e.doom])
	var r := engine.perform(skill, _one(target))
	assert_true(r.ok, "%s failed: %s" % [skill, r.fail_reason])
	var got: Array[String] = []
	for e in engine.preview(&"", null, 16):
		got.append("%s@%d/%d" % [e.combatant_id, e.time, e.doom])
	assert_eq(got, want, "preview of %s matches the order after it lands" % skill)


func _berserk_pick(rng_seed: int) -> String:
	engine = BattleEngine.new()
	_start(&"pair", rng_seed)
	engine.current.add_status(&"berserk", -1)
	return String(engine.run_enemy_turn().hits[0]["target_id"])


## [actor id, target id, hit own side].
func _confused_hit(rng_seed: int) -> Array:
	engine = BattleEngine.new()
	_start(&"pair", rng_seed)
	var actor := engine.current
	actor.add_status(&"confuse", 3)
	var r := engine.run_enemy_turn()
	var t := engine.find(r.hits[0]["target_id"])
	return [actor.id, t.id, t.team == actor.team]


func _damage_of_attack(berserk: bool, rng_seed: int) -> int:
	engine = BattleEngine.new()
	_start(&"plain", rng_seed)
	var foe := _first_foe()[0]
	var before := foe.hp
	if berserk:
		engine.current.add_status(&"berserk", -1)
		engine.run_enemy_turn()
	else:
		engine.perform(&"attack", _first_foe())
	return before - foe.hp


## A messy fight: every new status in play at once. Returns a compact log.
func _chaos_log(rng_seed: int) -> Array[String]:
	engine = BattleEngine.new()
	_start(&"pair", rng_seed)
	engine.enemies[0].add_status(&"reflect", 6)
	engine.enemies[0].add_status(&"confuse", 3)
	engine.enemies[1].add_status(&"berserk", -1)
	engine.enemies[1].add_status(&"doom", 6)
	_other_active(engine.current).add_status(&"zombie", -1)
	var out: Array[String] = []
	var guard := 0
	while engine.outcome == &"" and guard < 400:
		guard += 1
		if engine.is_party_turn():
			var r := engine.perform(&"zap", _first_foe())
			out.append("%s:%s" % [r.actor_id, str(r.hits.map(func(h: Dictionary) -> String: return h["target_id"]))])
		else:
			var r2 := engine.run_enemy_turn()
			out.append("%s:%s:%s" % [r2.actor_id, r2.skill_id, r2.auto_reason])
	out.append(String(engine.outcome))
	return out


func _to_party_turn() -> void:
	var guard := 0
	while not engine.is_party_turn() and engine.outcome == &"" and guard < 50:
		guard += 1
		engine.run_enemy_turn()


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
	_to_party_turn()


func _first_foe() -> Array[BattleCombatant]:
	var foes := engine.living_foes_of(engine.current)
	var out: Array[BattleCombatant] = [foes[0]]
	return out


func _one(c: BattleCombatant) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [c]
	return out


func _other_active(c: BattleCombatant) -> BattleCombatant:
	return engine.party_active[1] if engine.party_active[0] == c else engine.party_active[0]


static func _fixture_db() -> BattleDB:
	var hero := _stats(300, 30, 20)
	hero["mp"] = 99
	var helper := hero.duplicate()
	helper["agility"] = 15
	var bench := hero.duplicate()
	bench["agility"] = 30
	var party_skills := [
		"attack",
		"jab",
		"zap",
		"zap_all",
		"slow_zap",
		"mend",
		"sweep",
		"quicken",
		"stone_gaze",
		"stone_self",
		"doom_toll",
		"taunt",
	]
	var sturdy := _stats(9000, 5, 8)
	var basic_ai := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	var claw_ai := [{"pick": [{"skill": "claw", "target": "random_foe"}]}]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "attack", "kind": "physical", "power": 8, "rank": 3, "accuracy": 100},
					{"id": "jab", "kind": "physical", "power": 1, "rank": 1, "accuracy": 100},
					{"id": "claw", "kind": "physical", "power": 3, "rank": 3, "accuracy": 100},
					{"id": "spit", "kind": "magical", "power": 3, "rank": 3, "magic": true},
					{"id": "zap", "kind": "magical", "power": 8, "rank": 3, "mp_cost": 1, "magic": true},
					{"id": "zap_all", "kind": "magical", "power": 2, "rank": 3, "magic": true, "target": "all_foes"},
					{
						"id": "slow_zap",
						"kind": "support",
						"rank": 3,
						"magic": true,
						"statuses": [{"id": "slow", "chance": 100, "duration": 3}],
					},
					{"id": "mend", "kind": "heal", "power": 5, "rank": 3, "target": "single_ally", "magic": true},
					{"id": "sweep", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "target": "all_foes"},
					{
						"id": "quicken",
						"kind": "support",
						"rank": 3,
						"magic": true,
						"target": "self",
						"statuses": [{"id": "haste", "chance": 100, "duration": 4}],
					},
					{"id": "stone_gaze", "kind": "support", "rank": 3, "statuses": [{"id": "petrify", "chance": 100}]},
					{
						"id": "stone_self",
						"kind": "support",
						"rank": 3,
						"target": "self",
						"statuses": [{"id": "petrify", "chance": 100}],
					},
					{"id": "doom_toll", "kind": "support", "rank": 2, "statuses": [{"id": "doom", "chance": 100}]},
					{"id": "taunt", "kind": "support", "rank": 2, "statuses": [{"id": "provoke", "chance": 100}]},
				],
				"statuses":
				[
					{"id": "petrify", "default_duration": -1},
					{"id": "doom", "default_duration": 3},
					{"id": "provoke", "default_duration": 3},
				],
				"characters":
				[
					{"id": "hero", "stats": hero, "skills": party_skills},
					{"id": "helper", "stats": helper, "skills": party_skills},
					{"id": "bench", "stats": bench, "skills": party_skills},
				],
				"enemies":
				[
					{"id": "plain", "stats": sturdy, "skills": ["attack"], "ai": basic_ai, "xp": 1},
					{"id": "pair_a", "stats": sturdy, "skills": ["attack"], "ai": basic_ai, "xp": 1},
					{"id": "pair_b", "stats": sturdy, "skills": ["attack"], "ai": basic_ai, "xp": 1},
					{"id": "clawed", "stats": sturdy, "skills": ["spit", "claw"], "ai": claw_ai, "xp": 1},
				],
				"encounters":
				[
					{"id": "plain", "enemies": ["plain"]},
					{"id": "pair", "enemies": ["pair_a", "pair_b"]},
					{"id": "clawed", "enemies": ["clawed"]},
				],
			}
		)
	)


static func _stats(hp: int, strength: int, agility: int) -> Dictionary:
	return {
		"level": 5,
		"hp": hp,
		"mp": 0,
		"strength": strength,
		"magic": 10,
		"defense": 10,
		"magic_defense": 10,
		"agility": agility,
		"accuracy": 0,
		"evasion": 0,
		"luck": 0,
	}
