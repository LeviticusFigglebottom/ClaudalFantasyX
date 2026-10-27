extends TestCase
## M3-C08-100: battle barks (BattleBarks; act1_ch08.md §5). Toma says "Hold." on Hold the Stair, Asha names
## Virel as she calls him, and a skill or Vowbound without a bark_key says nothing. A bark floats over the speaker
## even with damage numbers off (it is speech, not a number). The runner runs no frames and has no after_each.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261027

var ctl: BattleController
var saved_state: GameStateData


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)


func test_toma_says_hold_on_hold_the_stair_even_with_damage_numbers_off() -> void:
	_start(&"ch08_stair_hold_1")
	_to_turn_of(&"toma")
	var floats := ctl.hud.damage_numbers_shown
	ctl.act(&"hold_the_stair", [&"toma"] as Array[StringName])
	assert_eq(_barks().said.back(), {"speaker": &"toma", "text": tr("BARK_SKILL_HOLD_THE_STAIR")})
	assert_eq(tr("BARK_SKILL_HOLD_THE_STAIR"), "Hold.")
	assert_true(ctl.hud.damage_numbers_shown > floats, "it floats over him")
	assert_eq(str(ctl.hud.recent_numbers.back()["text"]), "Hold.")
	_free()


func test_a_skill_without_a_bark_says_nothing() -> void:
	_start(&"sandbox_reef")
	for i in 4:
		_attack()
	assert_true(_barks().said.is_empty(), "Attack has no bark")
	assert_eq(_barks().skill_bark(&"flare_line"), "", "nobody speaks on Flare Line")
	_free()


func test_asha_names_virel_as_she_calls_him_and_ilun_comes_unnamed() -> void:
	ctl.start_fixture(BattleFixture.load_fixture(&"vowbound_call"))
	for row: Variant in BattleVowbound.load_config():  # the fixture binds Ilun only: lend it Virel's row
		if str((row as Dictionary)["id"]) == "virel":
			ctl.engine.vowbound.rows[&"virel"] = row
	assert_eq(_barks().call_bark(&"virel"), tr("BARK_CALL_VIREL"))
	assert_eq(tr("BARK_CALL_VIREL"), "Virel.")
	assert_eq(_barks().call_bark(&"ilun"), "", "Ilun's call has no line")
	ctl.engine.vowbound.known.append(&"virel")
	_to_turn_of(&"asha")
	assert_true(ctl.vow.call_vowbound(&"virel"), "Asha calls Virel")
	var last: Dictionary = _barks().said.back()
	assert_eq(str(last["text"]), "Virel.")
	assert_true([&"asha", &"virel"].has(last["speaker"]), "the caller speaks (or, stepped off, over Virel)")
	_free()


func test_a_retry_replaces_the_view() -> void:
	_start(&"sandbox_reef")
	var first := _barks()
	BattleBarks.attached(ctl, ctl.engine)
	assert_true(first.is_queued_for_deletion(), "the old view goes")
	assert_true(ctl.hud.get_node(^"BattleBarks") != first)
	first.free()  # no frame runs to finish the queue_free
	_free()


func _barks() -> BattleBarks:
	return ctl.hud.get_node(NodePath(BattleBarks.NODE_NAME)) as BattleBarks


func _start(encounter: StringName) -> void:
	var active: Array[StringName] = [&"rhen", &"asha", &"toma"]
	var reserve: Array[StringName] = [&"ysolde", &"kerrid"]
	ctl.start_battle(active, reserve, encounter, SEED)
	ctl.stage.choreo.live = false


func _attack() -> void:
	var foes := ctl.engine.living_foes_of(ctl.engine.current)
	if ctl.engine.outcome == &"" and not foes.is_empty():
		ctl.act(BattleMenus.ATTACK_SKILL, [foes[0].id])


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.engine.outcome == &"" and ctl.current_actor_id() != cid and guard < 30:
		guard += 1
		_attack()
	assert_eq(ctl.current_actor_id(), cid, "reached %s's turn" % cid)


func _free() -> void:
	Game.state = saved_state
	ctl.get_tree().paused = false
	ctl.get_parent().remove_child(ctl)
	ctl.free()
