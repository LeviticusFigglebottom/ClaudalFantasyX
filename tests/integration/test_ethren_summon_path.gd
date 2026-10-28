extends TestCase
## M3-CRE-644: Ethren's model in the real summon path, not only in the stand-in lookup. The battle sandbox calls him
## the way the Vowbound shots call Ilun (BattleVowbound call_vowbound, then the stage re-seats), from the same fixture
## with Ethren as the bound Vowbound instead; his stand-in shows the creature actor, not the placeholder, through the
## short entry and with the first-call cinematic forced. He has no vowbound.json row yet (Combat's; creatures.json
## `vowbound_pending`), so the test binds a minimal stand-in row of its own: Ilun's row under Ethren's id, with the
## skills the fixture already holds. The row is presentation scaffolding only, never game data.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SCENE := "res://game/creatures/ethren/ethren_battle.tscn"
const FIXTURE := &"choreo_vowbound_rise"
const ETHREN := &"ethren"
const CALLER := &"asha"
const MAX_TURNS := 16
## The row his in-test row copies.
const STAND_IN_ROW := &"ilun"

var ctl: BattleController


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_fixture(_ethren_fixture())


func test_the_called_vowbound_stands_as_the_model() -> void:
	_to_turn_of(CALLER)
	assert_true(ctl.vow.call_vowbound(ETHREN), "Asha calls Ethren")
	_assert_model("after the call")
	_free()


func test_the_first_call_cinematic_also_shows_the_model() -> void:
	var choreo := ctl.stage.choreo
	choreo.live = false
	choreo.summon.live = false
	choreo.summon.force_full = true
	_to_turn_of(CALLER)
	assert_true(ctl.vow.call_vowbound(ETHREN))
	_assert_model("with the first-call cinematic forced")
	_free()


func _assert_model(when: String) -> void:
	var f := ctl.stage.stand_in(ETHREN)
	assert_true(f != null, "Ethren has a stand-in %s" % when)
	if f == null:
		return
	assert_eq(str(f.spec.get("scene", "")), SCENE, "his spec names the model %s" % when)
	assert_true(f.has_actor(), "the stand-in shows the actor, not the placeholder, %s" % when)


## The Vowbound fixture with Ethren bound in Ilun's place, on a minimal in-test row (a copy of Ilun's, whose skills the
## fixture already holds) until Combat writes his.
func _ethren_fixture() -> BattleFixture:
	var fx := BattleFixture.load_fixture(FIXTURE)
	fx.vowbound = [ETHREN] as Array[StringName]
	var rows := fx.vowbound_rows.duplicate()
	for row: Variant in fx.vowbound_rows:
		if StringName(str((row as Dictionary).get("id", ""))) == STAND_IN_ROW:
			var own := (row as Dictionary).duplicate(true)
			own["id"] = String(ETHREN)
			rows.append(own)
	fx.vowbound_rows = rows
	return fx


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < MAX_TURNS:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


func _free() -> void:
	ctl.persist_progress = false
	ctl.get_parent().remove_child(ctl)
	ctl.free()
