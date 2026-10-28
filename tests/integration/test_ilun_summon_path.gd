extends TestCase
## M3-CRE-638: Ilun's model in the real summon path, not only in the stand-in lookup. The battle sandbox (the scene
## the shots battle_vowbound_call/out, battle_choreo_vowbound_rise and battle_choreo_summon capture) calls him the
## way the shots do (BattleVowbound call_vowbound, then the stage re-seats); his stand-in shows the creature actor,
## not the capsule, through the short entry and with the first-call cinematic forced.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SCENE := "res://game/creatures/ilun/ilun_battle.tscn"
const ILUN := &"ilun"
const CALLER := &"asha"
const FLAG := &"ch03_ilun_first_call_seen"
const MAX_TURNS := 16

var ctl: BattleController
var _flag_was: Variant


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	_flag_was = Game.get_flag(FLAG)
	ctl.start_fixture(BattleFixture.load_fixture(&"choreo_vowbound_rise"))


func test_the_called_vowbound_stands_as_the_model() -> void:
	_to_turn_of(CALLER)
	assert_true(ctl.vow.call_vowbound(ILUN), "Asha calls Ilun")
	_assert_model("after the call")
	_free()


func test_the_first_call_cinematic_also_shows_the_model() -> void:
	var choreo := ctl.stage.choreo
	choreo.live = false
	choreo.summon.live = false
	choreo.summon.force_full = true
	_to_turn_of(CALLER)
	assert_true(ctl.vow.call_vowbound(ILUN))
	_assert_model("with the first-call cinematic forced")
	_free()


func _assert_model(when: String) -> void:
	var f := ctl.stage.stand_in(ILUN)
	assert_true(f != null, "Ilun has a stand-in %s" % when)
	if f == null:
		return
	assert_eq(str(f.spec.get("scene", "")), SCENE, "his spec names the model %s" % when)
	assert_true(f.has_actor(), "the stand-in shows the actor, not the capsule, %s" % when)


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < MAX_TURNS:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


func _free() -> void:
	Game.set_flag(FLAG, _flag_was)
	ctl.persist_progress = false
	ctl.get_parent().remove_child(ctl)
	ctl.free()
