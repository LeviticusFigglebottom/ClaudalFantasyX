extends TestCase
## M3-C04-02: Ch4's fights on the derelict (act1_ch04.md C4-12, C4-13, §5) on the real battle tables:
## the first four-member party (Rhen, Asha and Toma active, Ysolde in reserve); the sail-leeches' ambush
## opening; the bottle-hermit's glass (blows and fire turned aside, cracked by ice) and its two prompts
## in sequence (the swap, then Read on the turn of the hero swapped in); and the Spar-Wraith, whose weak
## point moves from Fire (the shroud) to Ice (hauled down, sheathed in sea-water) at its phase.

const ACTIVE: Array[StringName] = [&"rhen", &"asha", &"toma"]
const RESERVE: Array[StringName] = [&"ysolde"]
const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 11
## Far more actions than any Ch4 fight takes.
const MAX_ACTIONS := 600
const ENCOUNTERS: Array[StringName] = [
	&"ch04_sail_leeches", &"ch04_bottle_hermit", &"ch04_spar_wraith", &"ch04_derelict_leeches", &"ch04_derelict_glass"
]

var db: BattleDB
var engine: BattleEngine


func before_each() -> void:
	db = BattleDB.load_default()
	engine = BattleEngine.new()


func test_the_four_member_party_plays_every_ch4_fight_to_an_outcome() -> void:
	for enc: StringName in ENCOUNTERS:
		engine = BattleEngine.new()
		engine.setup(db, ACTIVE, RESERVE, enc, SEED)
		assert_eq(engine.party_active.size(), 3, "%s: three active" % enc)
		assert_eq(engine.party_reserve.size(), 1, "%s: Ysolde in reserve" % enc)
		engine.begin()
		var steps := 0
		while engine.outcome == &"" and steps < MAX_ACTIONS:
			steps += 1
			if engine.is_party_turn():
				var foe := engine.living_foes_of(engine.current)[0]
				assert_true(engine.perform(&"attack", [foe] as Array[BattleCombatant]).ok, "%s: the party acts" % enc)
			else:
				engine.run_enemy_turn()
		assert_ne(engine.outcome, &"", "%s ends" % enc)


func test_the_leeches_drop_first_and_the_lessons_open_normally() -> void:
	assert_eq(BattleOpening.setting(db.encounters[&"ch04_sail_leeches"]), BattleOpening.AMBUSH, "ADR 0023's ambush")
	for enc: StringName in [&"ch04_bottle_hermit", &"ch04_spar_wraith"]:
		assert_eq(BattleOpening.setting(db.encounters[enc]), BattleOpening.NORMAL, "%s opens normally" % enc)
	for enc: StringName in [&"ch04_derelict_leeches", &"ch04_derelict_glass"]:
		assert_eq(BattleOpening.setting(db.encounters[enc]), BattleOpening.ROLL, "%s is a random fight" % enc)
	engine.setup(db, ACTIVE, RESERVE, &"ch04_sail_leeches", SEED)
	engine.opening = BattleOpening.AMBUSH
	engine.begin()
	assert_eq(engine.current.team, BattleCombatant.TEAM_ENEMY, "a leech acts first")


func test_the_glass_turns_fire_and_blows_aside_and_cracks_in_the_cold() -> void:
	engine.setup(db, ACTIVE, RESERVE, &"ch04_bottle_hermit", SEED)
	var hermit := engine.enemies[0]
	assert_eq(hermit.affinity_for(&"fire"), &"immune")
	assert_eq(hermit.affinity_for(&"none"), &"resist")
	assert_eq(hermit.affinity_for(&"ice"), &"weak")
	assert_eq(db.enemies[&"bottle_hermit"].get("role_answer"), "ysolde", "Ysolde answers the glass")
	var ysolde := engine.party_reserve[0]
	assert_true(ysolde.skills.has(&"read") and ysolde.skills.has(&"frost"), "she can Read it and crack it")


func test_the_wraiths_weak_point_moves_from_fire_to_ice() -> void:
	engine.setup(db, ACTIVE, RESERVE, &"ch04_spar_wraith", SEED)
	var wraith := engine.enemies[0]
	assert_eq(wraith.affinity_for(&"fire"), &"weak", "the shroud burns")
	assert_eq(wraith.affinity_for(&"none"), &"resist", "blows slide off the shroud")
	wraith.hp = wraith.max_hp / 2
	BossMechanics.check_phases(engine)
	assert_eq(wraith.affinity_for(&"ice"), &"weak", "hauled down, sheathed in sea-water")
	assert_eq(wraith.affinity_for(&"fire"), &"resist")
	assert_eq(wraith.affinity_for(&"water"), &"absorb")
	assert_true(wraith.skills.has(&"haul"), "it hauls a line")
	assert_eq(int(db.skill(&"haul").get("delay_ranks", 0)), 2, "the haul pushes a hero back on the timeline")
	assert_eq(str(db.skill(&"lines_taut").get("charge", {}).get("skill", "")), "haul", "and telegraphs it")


func test_the_hermit_teaches_the_swap_then_read_on_ysoldes_first_turn() -> void:
	var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle(ACTIVE, RESERVE, &"ch04_bottle_hermit", SEED)
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	assert_eq(ctl.hud.help_text(), tr("TUT_CH04_SWAP"), "the swap prompt opens the fight")
	assert_eq(ctl.boss.pending_prompt, "")
	var first := ctl.engine.current.id
	assert_true(ctl.engine.swap(first, &"ysolde"), "swap her in on anyone's turn")
	assert_eq(ctl.boss.pending_prompt, tr("TUT_CH04_READ"), "then Read, on her first turn")
	assert_true(ctl.boss.show_prompt())
	assert_eq(ctl.hud.help_text(), tr("TUT_CH04_READ"))
	assert_true(ctl.engine.swap(&"ysolde", first))
	assert_true(ctl.engine.swap(first, &"ysolde"))
	assert_eq(ctl.boss.pending_prompt, "", "once a fight")
	ctl.get_parent().remove_child(ctl)
	ctl.free()
