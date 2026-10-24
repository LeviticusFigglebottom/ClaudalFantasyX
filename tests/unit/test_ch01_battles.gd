extends TestCase
## M3-C01-02: Ch1's fights on the real battle tables. Rhen fights alone all chapter (act1_ch01.md §9
## Combat 1), so a one-hero party with no reserve must set up, take its turns, refuse a swap and play
## to an outcome. Hullgnaw's encounter lends Rhen Kick Off for that fight only ("party_skills",
## BossMechanics.lend_skills, ADR 0034), and its half-HP phase is the breaking raft.

const SOLO: Array[StringName] = [&"rhen"]
const NO_RESERVE: Array[StringName] = []
const SEED := 11
## Far more actions than any Ch1 fight takes.
const MAX_ACTIONS := 400

var db: BattleDB
var engine: BattleEngine


func before_each() -> void:
	db = BattleDB.load_default()
	engine = BattleEngine.new()


func test_a_one_hero_party_plays_every_ch1_fight_to_an_outcome() -> void:
	for enc: StringName in [&"ch01_wickfry", &"ch01_oil_slug", &"ch01_shaft_limpet", &"ch01_scuttlers", &"ch01_hullgnaw"]:
		engine = BattleEngine.new()
		engine.setup(db, SOLO, NO_RESERVE, enc, SEED)
		assert_eq(engine.party_active.size(), 1, "%s: Rhen alone" % enc)
		assert_eq(engine.party_reserve.size(), 0, "%s: no reserve" % enc)
		engine.begin()
		var steps := 0
		while engine.outcome == &"" and steps < MAX_ACTIONS:
			steps += 1
			if engine.is_party_turn():
				assert_false(engine.swap(&"rhen", &"asha"), "%s: nobody to swap in" % enc)
				var foe := engine.living_foes_of(engine.current)[0]
				assert_true(engine.perform(&"attack", [foe] as Array[BattleCombatant]).ok, "%s: Rhen acts" % enc)
			else:
				engine.run_enemy_turn()
		assert_ne(engine.outcome, &"", "%s ends" % enc)


func test_hullgnaw_lends_rhen_kick_off_for_that_fight_only() -> void:
	engine.setup(db, SOLO, NO_RESERVE, &"ch01_hullgnaw", SEED)
	assert_true(engine.party_active[0].skills.has(&"kick_off"), "the boss fight teaches Kick Off")
	assert_eq(engine.party_active[0].skills.count(&"kick_off"), 1)
	engine = BattleEngine.new()
	engine.setup(db, SOLO, NO_RESERVE, &"ch01_scuttlers", SEED)
	assert_false(engine.party_active[0].skills.has(&"kick_off"), "other fights lend nothing")


func test_a_lent_skill_is_never_added_twice() -> void:
	engine.party_modifier = func(c: BattleCombatant) -> void: c.skills.append(&"kick_off")
	engine.setup(db, SOLO, NO_RESERVE, &"ch01_hullgnaw", SEED)
	assert_eq(engine.party_active[0].skills.count(&"kick_off"), 1, "already learned on the Lattice")
	var c := engine.party_active[0]
	BossMechanics.lend_skills(engine, {"party_skills": {"asha": ["mend"]}})
	assert_false(c.skills.has(&"mend"), "a row for another hero lends Rhen nothing")


func test_hullgnaw_breaks_free_at_half_hp() -> void:
	engine.setup(db, SOLO, NO_RESERVE, &"ch01_hullgnaw", SEED)
	var boss := engine.enemies[0]
	var agility := boss.agility
	var defense := boss.defense
	assert_true(boss.skills.has(&"gnaw_coil") and boss.skills.has(&"rib_lash"), "phase 1: the ribs")
	boss.hp = boss.max_hp / 2
	BossMechanics.check_phases(engine)
	assert_eq(boss.phase_index, 0, "the breaking raft")
	assert_true(boss.skills.has(&"thrash") and not boss.skills.has(&"rib_lash"), "the ribs fall away")
	assert_true(boss.agility > agility, "free of the ribs, faster")
	assert_true(boss.defense < defense, "and softer")
	var row: Dictionary = db.enemies[&"hullgnaw"]["phases"][0]
	assert_eq(str(row.get("prompt_key", "")), "TUT_HULLGNAW_KICK_OFF")
	assert_ne(tr("TUT_HULLGNAW_KICK_OFF"), "TUT_HULLGNAW_KICK_OFF", "the prompt is translated (ch01.csv)")


func test_the_tutorial_fights_carry_their_prompts() -> void:
	var want := {
		&"ch01_wickfry": "TUT_CH01_COMMANDS",
		&"ch01_oil_slug": "TUT_CH01_ITEMS",
		&"ch01_shaft_limpet": "TUT_CH01_ESCAPE",
		&"ch01_hullgnaw": "TUT_HULLGNAW_TIMELINE",
	}
	for enc: StringName in want:
		assert_eq(str(db.encounters[enc].get("prompt_key", "")), want[enc], "%s prompt" % enc)
		assert_ne(tr(want[enc]), want[enc], "%s prompt is translated" % enc)
	assert_false(bool(db.encounters[&"ch01_shaft_limpet"].get("scripted", true)), "the limpet can be fled")
	assert_true(bool(db.encounters[&"ch01_hullgnaw"].get("scripted", false)), "Hullgnaw cannot")
