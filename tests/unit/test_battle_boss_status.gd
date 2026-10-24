extends TestCase
## M2-FP-12: the Drownbell's standing read-out (BattleBossStatus) on the real battle scene and data,
## and the defeat → Fight again loop starting the bell over.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261023
const FLAG := &"ch03_ilun_bound"
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]

var ctl: BattleController
var saved_state: GameStateData


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)


func test_the_read_out_names_the_bell_and_its_opening_phase() -> void:
	_start()
	var s := ctl.boss.status
	assert_true(s != null and s.visible, "a boss fight shows the read-out")
	assert_eq(s.title.text, "%s · %s" % [tr("ENEMY_DROWNBELL"), tr("PHASE_DROWNBELL_TOLL")])
	assert_false(s.field.visible, "no field before the flood")
	assert_eq(ctl.hud.get_children().filter(func(n: Node) -> bool: return n is BattleBossStatus).size(), 1)
	_free()


func test_the_toll_counts_down_and_the_rim_counts_up_with_damage_numbers_off() -> void:
	ctl.show_damage_numbers = false
	_start()
	var bell := ctl.engine.enemies[0]
	var s := ctl.boss.status
	var guard := 0
	while not bell.is_charging() and guard < 20:
		guard += 1
		_attack()
	assert_true(bell.is_charging())
	assert_true(s.charge.visible and s.weak.visible, "the telegraph stands while it is gathering")
	var toll := ctl.menus.skill_name(ctl.engine, &"toll")
	var want := (
		tr("HUD_BOSS_CHARGE_NEXT_FMT").format({"skill": toll})
		if bell.charge_left <= 1
		else tr("HUD_BOSS_CHARGE_IN_FMT").format({"skill": toll, "turns": bell.charge_left})
	)
	assert_eq(s.charge.text, want)
	var named := 0
	for chip: TimelineChip in ctl.hud.timeline._chips.values():
		if chip.visible and chip.intent_label != "":
			named += 1
			assert_eq((chip._name as Label).text, toll, "the toll's chip names the skill alone, so it fits")
	assert_eq(named, 1, "one chip for the toll")
	assert_eq(
		s.weak.text,
		tr("HUD_WEAK_POINT_FMT").format({"part": tr("PART_DROWNBELL_RIM"), "hits": bell.weak_hits, "need": 3})
	)
	# Rhen's attacks are fast enough for the rim: the count follows each landed hit.
	var before := bell.weak_hits
	guard = 0
	while bell.is_charging() and bell.weak_hits == before and guard < 12:
		guard += 1
		_attack()
	if bell.is_charging():
		assert_true(s.weak.text.contains("%d/3" % bell.weak_hits), s.weak.text)
	else:
		assert_false(s.charge.visible, "a fired or broken toll leaves the read-out")
	_free()


func test_the_flood_names_its_phase_and_counts_its_polyps() -> void:
	_start()
	var bell := ctl.engine.enemies[0]
	bell.hp = bell.max_hp * 40 / 100
	BossMechanics.check_phases(ctl.engine)
	var s := ctl.boss.status
	assert_eq(s.title.text, "%s · %s" % [tr("ENEMY_DROWNBELL"), tr("PHASE_DROWNBELL_FLOOD")])
	assert_true(s.field.visible)
	assert_eq(s.field.text, tr("HUD_BOSS_FIELD_FMT").format({"field": tr("FIELD_DROWNBELL_FLOOD"), "count": 2}))
	ctl.engine.fields.clear()
	ctl.boss.refresh()
	assert_false(s.field.visible, "the read-out drops the field once it is gone")
	_free()


func test_a_battle_without_a_boss_has_no_read_out() -> void:
	ctl.start_battle(PARTY, [], &"ch02_tideline", SEED)
	assert_true(ctl.boss.status == null or not ctl.boss.status.visible)
	_free()


func test_fight_again_starts_the_bell_over_with_ilun_still_known() -> void:
	Game.set_flag(FLAG, true)
	ctl.persist_progress = true
	_start()
	assert_true(ctl.engine.vowbound.known.has(&"ilun"), "the live flag binds Ilun (M2-UI-05)")
	var bell := ctl.engine.enemies[0]
	bell.hp = bell.max_hp * 40 / 100
	BossMechanics.check_phases(ctl.engine)
	assert_eq(ctl.engine.enemies.size(), 3, "the flood's polyps")
	for c in ctl.engine.party_active:
		c.hp = 0
	ctl.engine.battle_finished.emit(&"defeat")
	assert_false(ctl.boss.status.visible, "the read-out leaves with the fight")
	var first_status := ctl.boss.status
	ctl._on_result_choice(BattleController.CHOICE_RETRY)
	var again := ctl.engine.enemies[0]
	assert_true(again != bell, "a new engine")
	assert_eq(again.phase_index, -1, "back to the Toll")
	assert_eq(again.hp, again.max_hp)
	assert_eq(ctl.engine.enemies.size(), 1, "no polyps carried over")
	assert_true(ctl.engine.fields.is_empty())
	assert_true(ctl.engine.vowbound.known.has(&"ilun"), "Ilun is still bound")
	assert_true(ctl.boss.status == first_status, "the read-out is reused, not stacked")
	assert_true(ctl.boss.status.visible)
	assert_eq(ctl.boss.status.title.text, "%s · %s" % [tr("ENEMY_DROWNBELL"), tr("PHASE_DROWNBELL_TOLL")])
	assert_eq(ctl.hud.help_text(), tr("TUT_DROWNBELL_TOLL"), "the opening prompt again")
	_free()


func _start() -> void:
	ctl.start_battle(PARTY, [], &"drownbell", SEED)


## The current party member attacks the bell (enemy turns play out instantly in between).
func _attack() -> void:
	ctl.act(&"attack", [ctl.engine.enemies[0].id] as Array[StringName])


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
	Game.state = saved_state
