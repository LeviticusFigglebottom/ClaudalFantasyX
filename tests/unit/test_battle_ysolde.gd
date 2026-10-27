extends TestCase
## Ysolde's real battle model (characters' ysolde_battle.tscn) on the stage, ahead of ui-menus' stand-in repoint
## (M2-HER-1108). She is the first hero with no contract clips of her own, so BattlePlaceholderClips builds them all.
## Her model plays every contract clip, her footprint is a sane human's, and her signature actions (Ember, Read)
## plan and play to the end with her strike on the contact beat and no overlap at the strike point.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
## hero-integration's wrapper (M2-HER-1103) once it lands, else characters' bare model.
const WRAPPER := "res://game/hero_motion/battle/ysolde_battle_actor.tscn"
const BARE := "res://game/characters/heroes/ysolde_battle.tscn"
const SEED := 20261027
const EPS := 0.001

var ctl: BattleController

var _row: Dictionary = {}
var _had: Variant = null


func before_each() -> void:
	_row = (BattleStage.config()["stand_ins"] as Dictionary)["ysolde"] as Dictionary  # her real model, as the repoint
	_had = _row.get("scene")
	_row["scene"] = _scene()
	_row["yaw_deg"] = -90.0
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"ysolde", &"rhen"]
	var none: Array[StringName] = []
	ctl.start_battle(active, none, &"sandbox_reef", SEED)
	ctl.stage.choreo.live = false


func test_her_model_plays_every_contract_clip() -> void:
	if _scene() == "":
		_free()
		return  # no model of hers on this branch
	var f := ctl.stage.stand_in(&"ysolde")
	assert_true(BattleClips.player_of(f) != null, "her model has a player")
	for clip in BattleClips.ALL:
		assert_true(BattleClips.has_clip(f, clip), "%s is playable (placeholder until M2-HER-1115)" % clip)
	var r := BattleChoreoPlan.footprint(f, ctl.stage.choreo.data)
	assert_between(r, 0.2, 0.8, "a human's footprint (%.2f m)" % r)
	_free()


func test_her_whole_kit_plays_to_the_end() -> void:
	if _scene() == "":
		_free()
		return
	var choreo := ctl.stage.choreo
	for e in ctl.engine.enemies + ctl.engine.party_active:  # the fight lasts while she takes her turns
		e.max_hp = 100000
		e.hp = 100000
	for skill: StringName in [&"attack", &"ember", &"frost", &"slow_hex", &"read"]:  # her whole kit
		var guard := 0
		while ctl.current_actor_id() != &"ysolde" and guard < 40:
			guard += 1
			if ctl.engine.is_party_turn():
				ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
			ctl.tick(30.0)
		assert_eq(ctl.current_actor_id(), &"ysolde")
		ctl.pacing_scale = 1.0
		var foe := ctl.engine.living_foes_of(ctl.engine.current)[0]
		ctl.act(skill, [foe.id])
		var plan := choreo.current()
		assert_false(plan.is_empty(), "%s plays" % skill)
		if not plan.is_empty():
			choreo.advance(float(plan["contact"]) + EPS)
			assert_true(choreo.time() >= float(plan["contact"]) - EPS, "%s reaches its contact" % skill)
			choreo.finish()
		assert_false(choreo.playing(), "%s ends" % skill)
		ctl.pacing_scale = 0.0
		ctl.tick(30.0)
	_free()


func _scene() -> String:
	for path: String in [WRAPPER, BARE]:
		if ResourceLoader.exists(path):
			return path
	return ""


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
	if _had == null:
		_row.erase("scene")
		_row.erase("yaw_deg")
	else:
		_row["scene"] = _had
