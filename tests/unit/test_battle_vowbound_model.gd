extends TestCase
## M3-BPR-417 (the Lead, 20:54: Ilun is still a teal capsule while creatures builds the model): the summon
## choreography is ready for it. A creatures.json row keyed by a Vowbound's id with a `scene` replaces the capsule
## (BattleStage.vowbound_model), and the call, the C10 rise and the call frame play on that creature actor. Here a
## stand-in row borrows an existing creature scene; nobody else's stand-in changes.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const ILUN := &"ilun"
const FLAG := &"ch03_ilun_first_call_seen"
const SCENE := "res://game/creatures/spawn_polyp/spawn_polyp_battle.tscn"

var ctl: BattleController
var choreo: BattleChoreo
var _flag_was: Variant
var _row_was: Variant  # the creatures track's real row, when this branch has it (M3-CRE-638)


func before_each() -> void:
	_row_was = (CreatureActor.data()["creatures"] as Dictionary).get(String(ILUN), null)
	(CreatureActor.data()["creatures"] as Dictionary)[String(ILUN)] = {
		"scene": SCENE, "vowbound": true, "stand_in": {"yaw_deg": 15.0}
	}
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	_flag_was = Game.get_flag(FLAG)
	Game.set_flag(FLAG, false)
	ctl.start_fixture(BattleFixture.load_fixture(&"choreo_vowbound_rise"))
	choreo = ctl.stage.choreo
	choreo.live = false
	choreo.summon.live = false
	choreo.reduced_motion = false
	choreo.skip = false
	choreo.speed = 1.0


func test_only_a_vowbound_takes_its_own_row() -> void:
	var spec := BattleStage.stand_in_spec(ILUN)
	assert_eq(str(spec.get("scene", "")), SCENE, "Ilun's model replaces the capsule")
	assert_eq(float(spec.get("yaw_deg", 0.0)), 15.0, "with its row's stand_in keys")
	assert_eq(BattleStage.vowbound_model("spawn_polyp"), {}, "a foe keeps the enemies.json model path")
	assert_eq(BattleStage.vowbound_model("rhen"), {}, "a hero is untouched")
	_free()


func test_the_first_call_rises_on_the_model() -> void:
	var guard := 0
	while ctl.current_actor_id() != &"asha" and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	ctl.pacing_scale = 1.0
	ctl.persist_progress = true
	ctl.fixture = null
	assert_true(ctl.vow.call_vowbound(ILUN), "called")
	var f := ctl.stage.stand_in(ILUN)
	assert_true(f != null and f.has_actor(), "Ilun stands as its creature actor")
	assert_true(choreo.summon.playing(), "C10 plays on the model")
	assert_false(choreo.entering(ILUN).is_empty(), "and it rises")
	choreo.summon.advance(choreo.summon.total_sec() + 0.1)
	choreo.advance(choreo.summon.total_sec() + 1.0)
	assert_true(choreo.entering(ILUN).is_empty(), "on its mark")
	assert_true(f.head_position().y > f.global_position.y, "a head for the call frame and the floats")
	_free()


func test_a_row_without_the_vowbound_mark_is_not_taken() -> void:
	(CreatureActor.data()["creatures"] as Dictionary)[String(ILUN)] = {"scene": SCENE}
	assert_eq(BattleStage.vowbound_model(String(ILUN)), {}, "only a row marked vowbound (M3-CRE-638's rule)")
	_free()


## Every Vowbound that has its real creature actor (creatures' M3-CRE-638 row; Ilun first) plays each of its skills and
## its Swell finisher on that actor, with the reaction on the clip's own contact marker. A Vowbound still a capsule is
## skipped; the borrowed stand-in row above is put back to the real one (or none) first.
func test_a_real_vowbound_lands_each_action_on_its_clip_contact() -> void:
	_restore_row()
	var checked := 0
	for row: Dictionary in BattleVowbound.load_config():
		var vid := StringName(str(row["id"]))
		var real := str(BattleStage.stand_in_spec(vid).get("scene", "")) != ""
		if not real:
			continue
		var skills: Array = (row.get("skills", []) as Array).duplicate()
		skills.append(str((row.get("swell", {}) as Dictionary).get("technique", "")))
		for sid: Variant in skills:
			checked += _contact_lands(vid, StringName(str(sid)))
	print("vowbound actors checked: %d actions" % checked)
	_free()


func _contact_lands(vid: StringName, sk: StringName) -> int:
	var data := BattleChoreo.load_data()
	var r := ActionResult.new()
	r.actor_id = vid
	r.skill_id = sk
	var style := BattleChoreoPlan.style(data, BattleChoreoPlan.style_id_for(data, ctl.engine, r))
	var f := FighterStandIn.new()
	f.setup(vid, BattleStage.stand_in_spec(vid), BattleStage.config().get("ring", {}) as Dictionary)
	ctl.add_child(f)
	var kind := StringName(str(ctl.engine.db.skill(sk).get("kind", "")))
	var clip := BattleClips.action_clip(f, sk, kind)
	assert_ne(clip, &"", "%s %s: its own clip" % [vid, sk])
	assert_true(BattleClips.contact_sec(f, clip) >= 0.0, "%s %s: a contact time on %s" % [vid, sk, clip])
	assert_false(style.is_empty(), "%s %s: a style" % [vid, sk])
	f.queue_free()
	return 1


func _restore_row() -> void:
	var rows := CreatureActor.data()["creatures"] as Dictionary
	if _row_was == null:
		rows.erase(String(ILUN))
	else:
		rows[String(ILUN)] = _row_was


func _free() -> void:
	_restore_row()
	Game.set_flag(FLAG, _flag_was)
	ctl.persist_progress = false
	ctl.get_parent().remove_child(ctl)
	ctl.free()
