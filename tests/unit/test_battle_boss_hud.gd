extends TestCase
## The Drownbell on the real battle scene and data (M2-FP-06): BattleBossHud's prompts, the toll's
## timeline label, the flood's polyps seated on the stage, and the flag-locked Call Ilun.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261023
const FLAG := &"ch03_ilun_bound"

var ctl: BattleController


func before_each() -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)


func test_the_fight_opens_with_the_toll_prompt_once() -> void:
	_start()
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	assert_eq(ctl.hud.help_text(), tr("TUT_DROWNBELL_TOLL"))
	assert_eq(ctl.boss.pending_prompt, "")
	_act_once()
	assert_ne(ctl.hud.help_text(), tr("TUT_DROWNBELL_TOLL"), "one prompt per phase")
	_free()


func test_the_toll_turn_is_labelled_on_the_timeline() -> void:
	_start()
	var bell := ctl.engine.enemies[0]
	var guard := 0
	while not bell.is_charging() and guard < 20:
		guard += 1
		_act_once()
	assert_true(bell.is_charging())
	var label := ctl.menus.skill_name(ctl.engine, &"toll")
	var marked := 0
	for s in ctl.hud.timeline.slots:
		if str(s.get("intent_label", "")) == label:
			marked += 1
			assert_eq(s["id"], bell.id)
	assert_eq(marked, 1, "exactly the turn the toll fires on")
	_free()


func test_the_flood_seats_its_polyps_and_queues_its_prompt() -> void:
	_start()
	var bell := ctl.engine.enemies[0]
	bell.hp = bell.max_hp * 40 / 100
	BossMechanics.check_phases(ctl.engine)
	assert_eq(ctl.boss.pending_prompt, tr("TUT_DROWNBELL_FLOOD"))
	for p in ctl.engine.enemies.slice(1):
		assert_true(ctl.stage.has_fighter(p.id), "%s is on the stage" % p.id)
	ctl.engine.enemies[1].fall()
	var again := BossMechanics.spawn(ctl.engine, &"spawn_polyp")
	ctl.boss._on_joined([again] as Array[BattleCombatant])
	assert_true(ctl.stage.has_fighter(again.id))
	assert_false(ctl.stage.has_fighter(ctl.engine.enemies[1].id), "the new polyp takes the fallen one's place")
	assert_true(ctl.boss.show_prompt())
	assert_eq(ctl.hud.help_text(), tr("TUT_DROWNBELL_FLOOD"))
	assert_false(ctl.boss.show_prompt())
	_free()


func test_call_ilun_follows_the_story_flag() -> void:
	var db := BattleDB.load_default()
	assert_eq(BattleBossHud.story_flags(db, func(_f: StringName) -> bool: return false), [] as Array[StringName])
	var set_flags := BattleBossHud.story_flags(db, func(f: StringName) -> bool: return f == FLAG)
	assert_eq(set_flags, [FLAG] as Array[StringName])
	var had: Variant = Game.get_flag(FLAG)
	Game.set_flag(FLAG, true)
	assert_true(BattleBossHud.live_flags(db).has(FLAG))
	Game.set_flag(FLAG, had)
	_start()
	assert_false(ctl.engine.find(&"asha").skills.has(&"call_ilun"), "tests and fixtures pass no story flags")
	assert_eq(ctl.menus.fail_text(BossMechanics.FAIL_NO_FIELD, ctl.engine.party_active[0]), tr("HUD_FAIL_NO_FIELD"))
	_free()


func _start() -> void:
	ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [], &"drownbell", SEED)


## The current party member attacks the bell (enemy turns play out instantly in between).
func _act_once() -> void:
	ctl.act(&"attack", [ctl.engine.enemies[0].id] as Array[StringName])


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
