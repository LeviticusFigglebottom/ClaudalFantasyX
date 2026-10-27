extends TestCase
## M3-CRE-643: Hesk's model in the real summon path, not only in the stand-in lookup. The battle sandbox calls her
## the way the Vowbound shots call Ilun (BattleVowbound call_vowbound, then the stage re-seats); her stand-in shows the
## creature actor, not the placeholder, through the short entry and with the first-call cinematic forced. She has no
## vowbound.json row yet (Combat's) and no fixture names her (battle_fixtures.json is UI's), so the test takes the
## choreo_vowbound_rise fixture and binds a minimal row for her in it: Ilun's live row under her id (existing skills
## only; her own stats and skills are Combat's to write).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SCENE := "res://game/creatures/hesk/hesk_battle.tscn"
const FIXTURE := &"choreo_vowbound_rise"
const HESK := &"hesk"
const TEMPLATE := &"ilun"
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
	ctl.start_fixture(_fixture_with_hesk())


func test_the_called_vowbound_stands_as_the_model() -> void:
	_to_turn_of(CALLER)
	assert_true(ctl.vow.call_vowbound(HESK), "Asha calls Hesk")
	_assert_model("after the call")
	_free()


func test_the_first_call_cinematic_also_shows_the_model() -> void:
	var choreo := ctl.stage.choreo
	choreo.live = false
	choreo.summon.live = false
	choreo.summon.force_full = true
	_to_turn_of(CALLER)
	assert_true(ctl.vow.call_vowbound(HESK))
	_assert_model("with the first-call cinematic forced")
	_free()


## The fixture with Hesk bound: a minimal row (the template's live row under her id), and every live skill the frozen
## tables lack.
func _fixture_with_hesk() -> BattleFixture:
	var fx := BattleFixture.load_fixture(FIXTURE)
	var live := BattleDB.load_default()
	for sid: StringName in live.skills:
		if not fx.db.skills.has(sid):
			fx.db.skills[sid] = live.skills[sid]
	var rows: Array = []
	for row: Variant in BattleVowbound.load_config():
		if str((row as Dictionary).get("id", "")) == String(TEMPLATE):
			var mine := (row as Dictionary).duplicate(true)
			mine["id"] = String(HESK)
			rows.append(mine)
	assert_eq(rows.size(), 1, "the template row exists")
	fx.vowbound_rows = rows
	fx.vowbound = [HESK] as Array[StringName]
	return fx


func _assert_model(when: String) -> void:
	var f := ctl.stage.stand_in(HESK)
	assert_true(f != null, "Hesk has a stand-in %s" % when)
	if f == null:
		return
	assert_eq(str(f.spec.get("scene", "")), SCENE, "her spec names the model %s" % when)
	assert_true(f.has_actor(), "the stand-in shows the actor, not the placeholder, %s" % when)


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < MAX_TURNS:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


func _free() -> void:
	ctl.persist_progress = false
	ctl.get_parent().remove_child(ctl)
	ctl.free()
