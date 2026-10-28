extends TestCase
## M3-CRE-640: Kahre's model in the real summon path, not only in the stand-in lookup. The battle sandbox calls him
## the way the Vowbound shots call Ilun (BattleVowbound call_vowbound, then the stage re-seats); his stand-in shows the
## creature actor, not the capsule, through the short entry and with the first-call cinematic forced. No fixture names
## him yet (battle_fixtures.json is UI's), so the test takes the choreo_vowbound_rise fixture and binds him in it from
## the live tables: his vowbound.json row and the skills it names.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SCENE := "res://game/creatures/kahre/kahre_battle.tscn"
const FIXTURE := &"choreo_vowbound_rise"
const KAHRE := &"kahre"
const CALLER := &"asha"
const MAX_TURNS := 16

var ctl: BattleController


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_fixture(_fixture_with_kahre())


func test_the_called_vowbound_stands_as_the_model() -> void:
	_to_turn_of(CALLER)
	assert_true(ctl.vow.call_vowbound(KAHRE), "Asha calls Kahre")
	_assert_model("after the call")
	_free()


func test_the_first_call_cinematic_also_shows_the_model() -> void:
	var choreo := ctl.stage.choreo
	choreo.live = false
	choreo.summon.live = false
	choreo.summon.force_full = true
	_to_turn_of(CALLER)
	assert_true(ctl.vow.call_vowbound(KAHRE))
	_assert_model("with the first-call cinematic forced")
	_free()


## The fixture with Kahre bound: his live vowbound.json row, and every live skill the frozen tables lack.
func _fixture_with_kahre() -> BattleFixture:
	var fx := BattleFixture.load_fixture(FIXTURE)
	var live := BattleDB.load_default()
	for sid: StringName in live.skills:
		if not fx.db.skills.has(sid):
			fx.db.skills[sid] = live.skills[sid]
	var rows: Array = []
	for row: Variant in BattleVowbound.load_config():
		if str((row as Dictionary).get("id", "")) == String(KAHRE):
			rows.append(row)
	fx.vowbound_rows = rows
	fx.vowbound = [KAHRE] as Array[StringName]
	return fx


func _assert_model(when: String) -> void:
	var f := ctl.stage.stand_in(KAHRE)
	assert_true(f != null, "Kahre has a stand-in %s" % when)
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
	ctl.persist_progress = false
	ctl.get_parent().remove_child(ctl)
	ctl.free()
