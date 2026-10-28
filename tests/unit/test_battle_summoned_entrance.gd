extends TestCase
## M3-BPR-411 (the VFX audit's fill on stage): a foe that joins mid-battle (the flood's polyps, Rouse Polyp, the
## Reach's surges) walks onto its mark (choreo.json enter) instead of appearing; at instant pacing it is there at once.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261027

var ctl: BattleController


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [], &"drownbell", SEED)


func test_a_summoned_foe_walks_onto_its_mark() -> void:
	ctl.pacing_scale = 1.0
	var polyp := BossMechanics.spawn(ctl.engine, &"spawn_polyp")
	ctl.boss._on_joined([polyp] as Array[BattleCombatant])
	assert_true(ctl.stage.has_fighter(polyp.id), "seated")
	assert_false(ctl.stage.choreo.entering(polyp.id).is_empty(), "its entrance plays")
	ctl.stage.choreo.advance(float(ctl.stage.choreo.data["enter"]["sec"]) + 0.5)
	assert_true(ctl.stage.choreo.entering(polyp.id).is_empty(), "and ends on its mark")
	_free()


func test_at_instant_pacing_it_is_there_at_once() -> void:
	var polyp := BossMechanics.spawn(ctl.engine, &"spawn_polyp")
	ctl.boss._on_joined([polyp] as Array[BattleCombatant])
	assert_true(ctl.stage.choreo.entering(polyp.id).is_empty(), "no entrance at instant pacing")
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
