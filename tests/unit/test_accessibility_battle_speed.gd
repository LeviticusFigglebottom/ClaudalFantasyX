extends TestCase
## M2-UI-23: the battle speed and Vowbound call cinematic settings. battle_speed divides every
## battle presentation duration (the controller's waits, the floats, the shake, the recoil) and never
## changes what the engine does; summon_cinematic answers which cut a call cinematic plays. Both are
## rows on the Accessibility page and are saved in settings.cfg.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const EPS := 0.001
const ACTIONS := 6

var cfg_path := ""


func before_each() -> void:
	cfg_path = "user://test_battle_speed_%d.cfg" % Time.get_ticks_usec()


func test_battle_speed_defaults_to_normal_and_scales_time() -> void:
	var s := UiSettings.new()
	assert_eq(s.battle_speed(), 1.0, "normal by default")
	assert_eq(s.battle_time_scale(), 1.0)
	assert_eq(s.options(UiSettings.BATTLE_SPEED), [0.75, 1.0, 1.5, 2.0], "the same values as BattleChoreo's speed")
	assert_true(s.set_value(UiSettings.BATTLE_SPEED, 2.0))
	assert_eq(s.battle_time_scale(), 0.5, "twice as fast: every beat takes half as long")
	assert_true(s.set_value(UiSettings.BATTLE_SPEED, 0.75))
	assert_true(s.battle_time_scale() > 1.0, "slower: every beat takes longer")
	assert_false(s.set_value(UiSettings.BATTLE_SPEED, 0.0), "only the listed speeds")


func test_summon_cinematic_cuts_follow_the_spec() -> void:
	var s := UiSettings.new()
	# SPEC §6.3: full on first use, then shortened.
	assert_eq(s.get_value(UiSettings.SUMMON_CINEMATIC), "short")
	assert_eq(s.summon_cinematic_cut(true), UiSettings.CUT_FULL)
	assert_eq(s.summon_cinematic_cut(false), UiSettings.CUT_SHORT)
	s.set_value(UiSettings.SUMMON_CINEMATIC, "full")
	assert_eq(s.summon_cinematic_cut(false), UiSettings.CUT_FULL)
	s.set_value(UiSettings.SUMMON_CINEMATIC, "off")
	assert_eq(s.summon_cinematic_cut(true), UiSettings.CUT_NONE, "off skips straight to the effect")
	assert_eq(s.summon_cinematic_cut(false), UiSettings.CUT_NONE)


func test_both_are_rows_on_the_accessibility_page_and_are_saved() -> void:
	var s := UiSettings.new()
	var m := AccessibilityMenuModel.new(s, cfg_path)
	assert_true(m.row_ids().has(UiSettings.BATTLE_SPEED))
	assert_true(m.row_ids().has(UiSettings.SUMMON_CINEMATIC))
	assert_eq(m.value_text(UiSettings.BATTLE_SPEED), tr("SET_BATTLE_SPEED_100"))
	assert_eq(m.value_text(UiSettings.SUMMON_CINEMATIC), tr("SET_SUMMON_CINEMATIC_SHORT"))
	m.set_cursor(m.row_ids().find(UiSettings.BATTLE_SPEED))
	assert_true(m.cycle(1))
	assert_eq(m.value_text(UiSettings.BATTLE_SPEED), tr("SET_BATTLE_SPEED_150"))
	assert_eq(m.help_key(), "SET_BATTLE_SPEED_HELP")
	m.set_cursor(m.row_ids().find(UiSettings.SUMMON_CINEMATIC))
	assert_true(m.cycle(1))
	assert_eq(m.value_text(UiSettings.SUMMON_CINEMATIC), tr("SET_SUMMON_CINEMATIC_OFF"))
	var back := UiSettings.new()
	back.load_from(cfg_path)
	assert_eq(back.battle_speed(), 1.5, "saved in settings.cfg")
	assert_eq(back.get_value(UiSettings.SUMMON_CINEMATIC), "off")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(cfg_path))


func test_the_controller_waits_scale_with_the_speed() -> void:
	var ctl := _sandbox(2.0)
	var base := HudLayout.num(HudLayout.section(&"pacing"), "action_hold_sec")
	assert_true(is_equal_approx(ctl._pace(&"action_hold_sec"), base * 0.5), "Fastest halves the hold")
	ctl.hud.settings.set_value(UiSettings.BATTLE_SPEED, 0.75)
	assert_true(is_equal_approx(ctl._pace(&"action_hold_sec"), base / 0.75), "Slower lengthens it")
	ctl.pacing_scale = 0.0
	assert_eq(ctl._pace(&"action_hold_sec"), 0.0, "instant pacing (tests, captures) stays instant")
	_free(ctl)


func test_the_speed_never_changes_the_battle() -> void:
	var slow := _play(0.75)
	var fast := _play(2.0)
	assert_eq(slow.size(), ACTIONS, "both played the same number of actions")
	assert_eq(fast, slow, "the same actors, HP and order at every speed")


func test_floats_shake_and_recoil_play_at_the_speed() -> void:
	var ctl := _sandbox(2.0)
	_start(ctl)
	var n := DamageNumber.new()
	ctl.hud.add_child(n)
	var m := HudLayout.section(&"damage")
	n.pop("12", Vector2.ZERO, DamageNumber.KIND_DAMAGE, false, false, m, 1.0, &"", ctl.hud.battle_speed())
	var life := HudLayout.num(m, "rise_sec") + HudLayout.num(m, "fade_sec")
	n.tween.custom_step(life * 0.5 + EPS)
	assert_false(n.tween.is_running(), "at Fastest the number is gone in half its time")
	var cfg: Dictionary = BattleStage.config().get("shake", {})
	var steps := maxi(int(cfg.get("steps", 1)), 1)
	var shake_sec := float(cfg.get("sec", 0.0)) * (steps + 1) / steps
	ctl.stage.shake(1.0)
	ctl.stage._shake_tween.custom_step(shake_sec * 0.5 + EPS)
	assert_true(ctl.stage._shake_tween.is_running(), "normal speed: the shake is still going")
	ctl.stage.shake(ctl.hud.battle_speed())
	ctl.stage._shake_tween.custom_step(shake_sec * 0.5 + EPS)
	assert_false(ctl.stage._shake_tween.is_running(), "Fastest: done in half the time")
	_free(ctl)


# --- helpers -----------------------------------------------------------------------------


## A sandbox controller with readable pacing at battle speed `speed` (its own UiSettings).
func _sandbox(speed: float) -> BattleController:
	var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var s := UiSettings.new()
	s.set_value(UiSettings.BATTLE_SPEED, speed)
	ctl.hud.apply_settings(s)
	ctl.pacing_scale = 1.0
	return ctl


func _start(ctl: BattleController) -> void:
	var p := LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	for cid: StringName in [&"rhen", &"asha", &"toma", &"ysolde"]:
		p.add_character(cid)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	ctl.start_battle(active, reserve, &"sandbox_reef", SEED, p)


## Plays at `speed` with the same inputs (Confirm through the first command and target; the waits
## ticked through) and records [actor, every fighter's HP] each time the turn passes, ACTIONS times.
func _play(speed: float) -> Array:
	var ctl := _sandbox(speed)
	_start(ctl)
	var seen: Array = []
	var last: StringName = &""
	var guard := 0
	while seen.size() < ACTIONS and ctl.engine.outcome == &"" and guard < 2000:
		guard += 1
		if ctl.current_actor_id() != last:
			last = ctl.current_actor_id()
			seen.append(_snapshot(ctl))
		if ctl.state == BattleController.STATE_BUSY:
			ctl.tick(0.05)
		elif ctl.state == BattleController.STATE_RESULT:
			break
		else:
			ctl.handle_input(_ev(&"ui_accept"))
	_free(ctl)
	return seen


func _snapshot(ctl: BattleController) -> Array:
	var hp: Array = []
	for c in ctl.engine.party_active + ctl.engine.enemies:
		hp.append([c.id, c.hp])
	return [ctl.current_actor_id(), hp]


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _free(ctl: BattleController) -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
