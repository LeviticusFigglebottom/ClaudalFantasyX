extends TestCase
## M3-CMB-01: Ch8's set-piece battles on the real battle tables (act1_ch08.md §5, §5a): the three
## waves on the Fisher Stair and the Undertow's Reach. The party rules (Toma locked at the stair-head
## with Stand Firm for Attack, Kerrid not with the party, Haul once the hoist is rigged), the entries,
## the objectives, the Reach's three phases and Virel's Flare Line. Bands: tools/balance/targets.json.

const WAVES: Array[StringName] = [&"ch08_stair_hold_1", &"ch08_stair_hold_2", &"ch08_stair_hold_3"]
const REACH := &"undertows_reach"
const FLAGS: Array[StringName] = [&"ch08_hoist_rigged", &"ch08_virel_bound"]
const SEED := 5
## Far more actions than any Ch8 fight takes.
const MAX_ACTIONS := 1500

var db: BattleDB


func before_each() -> void:
	db = BattleDB.load_default()


func test_every_ch8_fight_holds_the_stair_rules() -> void:
	for enc: StringName in WAVES + [REACH]:
		var e := _engine(enc, FLAGS)
		assert_eq(e.find(&"kerrid"), null, "%s: Kerrid is not with the party" % enc)
		var toma := e.find(&"toma")
		assert_true(e.party_active.has(toma), "%s: Toma is seated at the stair-head" % enc)
		assert_eq(e.locked_active, [&"toma"] as Array[StringName])
		assert_ne(e.locked_key, "")
		assert_eq(toma.attack_skill, &"stand_firm", "%s: his Attack is Stand Firm" % enc)
		assert_false(toma.skills.has(&"attack"))
		assert_true(toma.skills.has(&"hold_the_stair"), "%s: and he can hold the stair" % enc)
		assert_eq(toma.forbidden_tag, &"undertow_spawn", "%s: he does not go on the offensive" % enc)
		assert_eq(e.ward().id, &"the_climb", "%s: the Fisher Stair is on the timeline" % enc)
		assert_false(e.objective.is_empty(), "%s: won on its objective" % enc)
		assert_true(e.scripted, "%s: no Escape" % enc)


func test_haul_waits_for_the_hoist() -> void:
	assert_false(_engine(&"ch08_stair_hold_2", [] as Array[StringName]).find(&"liss").skills.has(&"hoist_haul"))
	assert_true(_engine(&"ch08_stair_hold_2", FLAGS).find(&"liss").skills.has(&"hoist_haul"))
	assert_false(_engine(&"ch08_stair_hold_1", FLAGS).find(&"liss").skills.has(&"hoist_haul"), "not lent in Wave 1")


func test_every_ch8_fight_plays_to_an_outcome_under_the_guard() -> void:
	for enc: StringName in WAVES + [REACH]:
		var e := _engine(enc, FLAGS)
		var p := SimPolicyRoleAnswer.new()
		p.config = {"guard_ward": true}
		var steps := 0
		while e.outcome == &"" and steps < MAX_ACTIONS:
			steps += 1
			if e.is_party_turn():
				p.take_turn(e)
			else:
				e.run_enemy_turn()
		assert_ne(e.outcome, &"", "%s ends" % enc)
		var won := BattleEngine.OUTCOME_SCRIPTED_ESCAPE if enc == REACH else BattleEngine.OUTCOME_VICTORY
		assert_true(e.outcome in [won, BattleEngine.OUTCOME_DEFEAT], "%s: %s" % [enc, e.outcome])


func test_wave_three_has_the_kirru_whose_call_spares_the_rooted_polyp() -> void:
	var e := _engine(&"ch08_stair_hold_3", FLAGS)
	var pell := e.find(&"the_kirru")
	assert_eq(pell.entry_role, BattleSetPiece.ROLE_GUEST)
	assert_eq(pell.team, BattleCombatant.TEAM_PARTY)
	var call := db.skill(&"storm_call")
	for f in e.enemies:
		var rooted := BattleEngine.enemy_id(f) == &"wall_polyp"
		assert_eq(BattleSetPiece.spares(call, f), rooted, "%s" % f.id)


func test_the_reach_can_only_be_survived() -> void:
	var e := _engine(REACH, FLAGS)
	var reach := e.enemies[0]
	assert_eq(reach.hp_floor_pct, 30)
	assert_eq(e.objective.get("outcome"), "scripted_escape")
	assert_eq(e.objective.get("from_phase"), "breach")
	assert_eq(e.pending_entries.size(), 1, "the Surge waits for the Breach")
	reach.apply_damage(reach.max_hp)
	assert_eq(reach.hp, reach.max_hp * 30 / Formulas.PCT, "it never falls before the Breach")
	BossMechanics.check_phases(e)
	assert_eq(BossMechanics.phase_id(reach), "breach")
	assert_true(reach.untargetable and reach.damage_immune)
	assert_true(e.fields.has(&"storm_dark"), "the Dark rose on the way down")
	assert_true(e.field_rules.has(&"storm_dark"))
	var wings := 0
	for f in e.enemies:
		if BattleEngine.enemy_id(f) == &"squall_wing":
			wings += 1
			assert_eq(f.field, &"storm_dark", "bound to the dark")
	assert_eq(wings, 2)
	assert_eq(e.entries.size(), 2, "the Surge joined")


func test_flare_line_lights_the_wall() -> void:
	var row := db.skill(&"flare_line")
	assert_eq(row.get("clears_field"), "storm_dark")
	assert_true(bool(row.get("swell")) and bool(row.get("vowbound")))
	var vb := BattleVowbound.new(BattleVowbound.load_config(), [&"virel"] as Array[StringName])
	assert_eq(vb.finisher_of(&"virel"), &"flare_line")
	assert_eq(str((vb.rows[&"virel"] as Dictionary).get("caller")), "asha")
	assert_eq(str((vb.rows[&"virel"] as Dictionary).get("bound_flag")), "ch08_virel_bound")


func test_a_seeded_wave_replays_identically() -> void:
	var sim := BattleSim.new()
	var kit := sim.loadout(&"ch08_seawall")
	var active: Array[StringName] = [&"toma", &"rhen", &"liss"]
	var reserve: Array[StringName] = [&"asha", &"ysolde"]
	var a := sim.run_one(&"ch08_stair_hold_2", active, reserve, sim.make_policy(&"role_answer"), SEED, Callable(), kit)
	var b := sim.run_one(&"ch08_stair_hold_2", active, reserve, sim.make_policy(&"role_answer"), SEED, Callable(), kit)
	assert_eq(a, b)
	assert_ne(a["outcome"], "timeout")


func test_the_menus_play_stand_firm_from_attack_and_aim_haul_at_the_stair() -> void:
	var e := _engine(&"ch08_stair_hold_2", FLAGS)
	var menus := BattleMenus.new()
	for _i in MAX_ACTIONS:
		if e.is_party_turn() and e.current.id == &"toma":
			break
		if e.is_party_turn():
			e.perform(&"stand_fast", [e.current] as Array[BattleCombatant])
		else:
			e.run_enemy_turn()
	var row: Dictionary = menus.root_rows(e)[0]
	assert_eq(row.get("id"), BattleMenus.ROW_ATTACK)
	assert_true(bool(row.get("enabled", false)), "Toma's Attack row is open")
	assert_eq(menus.root_skill(e, BattleMenus.ROW_ATTACK), &"stand_firm")
	assert_false(menus.skill_ids(e.current).has(&"stand_firm"), "not listed twice")
	assert_eq(menus.default_targets(e, &"hoist_haul", &""), [e.ward()] as Array[BattleCombatant])
	assert_eq(menus.skill_candidates(e, &"hoist_haul"), [e.ward()] as Array[BattleCombatant])


func _engine(enc: StringName, flags: Array[StringName]) -> BattleEngine:
	var e := BattleEngine.new()
	e.story_flags = flags.duplicate()
	var active: Array[StringName] = [&"rhen", &"asha", &"liss"]
	var reserve: Array[StringName] = [&"toma", &"ysolde", &"kerrid"]
	e.setup(db, active, reserve, enc, SEED)
	e.begin()
	return e
