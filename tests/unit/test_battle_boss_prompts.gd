extends TestCase
## BattleBossHud's turn prompt never replaces the opening prompt: when the named hero has the very first turn, the
## encounter's opening prompt shows and the hero's line waits for the hero's next turn (Ch6: TUT_CH06_HOUND and
## Toma's "No. Not them.").

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"

var ctl: BattleController


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var party: Array[StringName] = [&"rhen", &"asha", &"toma"]
	var empty: Array[StringName] = []
	ctl.start_battle(party, empty, &"ch06_inquisitor", 7)


func test_a_turn_prompt_waits_while_the_opening_prompt_is_unshown() -> void:
	var boss := ctl.boss
	var toma := ctl.engine.find(&"toma")
	boss.pending_prompt = tr("TUT_CH06_HOUND")
	boss.turn_prompt_hero = &"toma"
	boss._on_turn_started(toma)
	assert_eq(boss.pending_prompt, tr("TUT_CH06_HOUND"), "the opening prompt is kept")
	assert_eq(boss.turn_prompt_hero, &"toma", "Toma's line still waits")
	assert_true(boss.show_prompt(), "the opening prompt shows")
	boss._on_turn_started(toma)
	assert_eq(boss.pending_prompt, boss.turn_prompt, "his next turn queues his line")
	assert_eq(boss.turn_prompt_hero, &"", "once")
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
