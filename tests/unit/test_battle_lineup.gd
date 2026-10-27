extends TestCase
## M3-BPR-403: the opening line-up keeps the real models' footprints apart. BattleLineup.spread pushes overlapping
## neighbours apart on the ground, sideways on screen, each at most lineup_max_shift_m off its mark; at spawn no two
## fighters on one side overlap in any encounter (unless both were pushed their full allowance), and a line-up with
## room moves nobody.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261025
const EPS := 0.001

var ctl: BattleController


func test_overlapping_neighbours_are_pushed_apart_evenly() -> void:
	var pts: Array[Vector3] = [Vector3.ZERO, Vector3(1.0, 0.0, 0.0)]
	var radii: Array[float] = [0.6, 0.6]
	var offs := BattleLineup.spread(pts, radii, 0.1, 5.0, 8)
	var a := pts[0] + (offs[0] as Vector3)
	var b := pts[1] + (offs[1] as Vector3)
	assert_between(a.distance_to(b), 1.3 - EPS, 1.3 + EPS, "both footprints and the clearance")
	assert_between((offs[0] as Vector3).length(), 0.15 - EPS, 0.15 + EPS, "half each")
	assert_eq((offs[0] as Vector3).y, 0.0, "on the ground")


func test_a_line_up_with_room_moves_nobody() -> void:
	var pts: Array[Vector3] = [Vector3.ZERO, Vector3(3.0, 0.0, 0.0), Vector3(0.0, 0.0, 3.0)]
	var radii: Array[float] = [0.5, 0.5, 0.5]
	for o: Vector3 in BattleLineup.spread(pts, radii, 0.1, 1.0, 8):
		assert_eq(o, Vector3.ZERO)


func test_the_push_is_sideways_on_screen_never_toward_the_camera() -> void:
	# Two foes one behind the other in depth (z) but overlapping: they slide apart along the axis (x) only.
	var pts: Array[Vector3] = [Vector3.ZERO, Vector3(0.2, 0.0, 0.6)]
	var radii: Array[float] = [0.6, 0.6]
	var offs := BattleLineup.spread(pts, radii, 0.1, 5.0, 8, Vector3.RIGHT)
	for o: Vector3 in offs:
		assert_eq(o.z, 0.0, "no step toward the camera")
	var a := pts[0] + (offs[0] as Vector3)
	var b := pts[1] + (offs[1] as Vector3)
	assert_true(a.distance_to(b) >= 1.3 - EPS, "apart by both footprints and the clearance")
	assert_true((offs[1] as Vector3).x > 0.0 and (offs[0] as Vector3).x < 0.0, "each away from the other")


func test_the_shift_is_capped() -> void:
	var pts: Array[Vector3] = [Vector3.ZERO, Vector3(0.1, 0.0, 0.0)]
	var radii: Array[float] = [2.0, 2.0]
	for o: Vector3 in BattleLineup.spread(pts, radii, 0.1, 0.4, 8):
		assert_true(o.length() <= 0.4 + EPS, "never further than max_shift from its mark")


func test_no_encounter_opens_with_overlapping_fighters() -> void:
	var data := BattleChoreo.load_data()
	var sp := data["spacing"] as Dictionary
	var cap := float(sp["lineup_max_shift_m"])
	var db := BattleDB.load_default()
	var party: Array[StringName] = [&"rhen", &"asha", &"toma"]
	var none: Array[StringName] = []
	for enc: StringName in db.encounters:
		_make()
		ctl.start_battle(party, none, enc, SEED)
		for side: Array in [ctl.engine.party_active, ctl.engine.enemies]:
			var fs: Array = []
			for c: BattleCombatant in side:
				if ctl.stage.stand_in(c.id) != null:
					fs.append(ctl.stage.stand_in(c.id))
			for i in fs.size():
				for j in range(i + 1, fs.size()):
					var a := fs[i] as FighterStandIn
					var b := fs[j] as FighterStandIn
					var need := _r(a, data) + _r(b, data) + float(sp["clearance_m"])
					var d := Vector2(a.position.x - b.position.x, a.position.z - b.position.z).length()
					var capped := _shift(a) >= cap - EPS and _shift(b) >= cap - EPS
					assert_true(
						d >= need - 0.01 or capped,
						"%s: %s and %s %.2f apart, need %.2f" % [enc, a.name, b.name, d, need]
					)
		_free()


func _r(f: FighterStandIn, data: Dictionary) -> float:
	var r := BattleChoreoPlan.footprint(f, data)
	return r if r > 0.0 else float(f.spec.get("radius", 0.0))


## How far `f` stands from the nearest slot marker (its shift off its mark).
func _shift(f: FighterStandIn) -> float:
	var best := INF
	for slots: Node in [ctl.stage.get_node("%PartySlots"), ctl.stage.get_node("%EnemySlots")]:
		for m: Node in slots.get_children():
			var p := (m as Marker3D).global_position - f.global_position
			best = minf(best, Vector2(p.x, p.z).length())
	return best


func _make() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
