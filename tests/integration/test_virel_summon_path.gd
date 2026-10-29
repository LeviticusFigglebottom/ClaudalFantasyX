extends TestCase
## M3-CRE-641: Virel's model in the real summon path, not only in the stand-in lookup. The battle sandbox calls her
## the way the Vowbound shots call Ilun (BattleVowbound call_vowbound, then the stage re-seats), from the same fixture
## with Virel as the bound Vowbound instead (no fixture names her yet); her stand-in shows the creature actor, not the
## placeholder, through the short entry and with the first-call cinematic forced.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SCENE := "res://game/creatures/virel/virel_battle.tscn"
const FIXTURE := &"choreo_vowbound_rise"
const VIREL := &"virel"
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
	ctl.start_fixture(_virel_fixture())


func test_the_called_vowbound_stands_as_the_model() -> void:
	_to_turn_of(CALLER)
	assert_true(ctl.vow.call_vowbound(VIREL), "Asha calls Virel")
	_assert_model("after the call")
	_free()


func test_the_first_call_cinematic_also_shows_the_model() -> void:
	var choreo := ctl.stage.choreo
	choreo.live = false
	choreo.summon.live = false
	choreo.summon.force_full = true
	_to_turn_of(CALLER)
	assert_true(ctl.vow.call_vowbound(VIREL))
	_assert_model("with the first-call cinematic forced")
	_free()


func _assert_model(when: String) -> void:
	var f := ctl.stage.stand_in(VIREL)
	assert_true(f != null, "Virel has a stand-in %s" % when)
	if f == null:
		return
	assert_eq(str(f.spec.get("scene", "")), SCENE, "her spec names the model %s" % when)
	assert_true(f.has_actor(), "the stand-in shows the actor, not the placeholder, %s" % when)


## The Vowbound fixture with Virel bound in Ilun's place: her game row (vowbound.json) and her skills (skills.json)
## join the fixture's frozen tables, which hold only Ilun's.
func _virel_fixture() -> BattleFixture:
	var fx := BattleFixture.load_fixture(FIXTURE)
	fx.vowbound = [VIREL] as Array[StringName]
	var rows := fx.vowbound_rows.duplicate()
	for row: Variant in BattleVowbound.load_config():
		if StringName(str((row as Dictionary).get("id", ""))) == VIREL:
			rows.append(row)
			var game := BattleDB.load_default()
			for skill: Variant in (row as Dictionary).get("skills", []):
				fx.db.skills[StringName(str(skill))] = game.skill(StringName(str(skill)))
			var finisher := StringName(str(((row as Dictionary).get("swell", {}) as Dictionary).get("technique", "")))
			fx.db.skills[finisher] = game.skill(finisher)
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
