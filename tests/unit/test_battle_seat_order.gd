extends TestCase
## The encounter sweep (10-30): on the causeway the 2.9 m Lantern Eel, first in its encounter's list, took the slot
## nearest the camera and hid the Gull Harrier behind it at rest. With spacing.tall_to_back the tallest foes take the
## slots farthest from the camera, and no foe's middle is behind another foe's body from the rest frame.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"

var ctl: BattleController


func _start(encounter: StringName) -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle([&"rhen", &"asha"] as Array[StringName], [] as Array[StringName], encounter, 20261030)


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()


func test_the_tallest_foe_stands_farthest_back() -> void:
	_start(&"ch03_causeway_shore")
	var eye := ctl.stage.camera.global_position
	var far := -1.0
	var tallest := &""
	var top := -1.0
	for e in ctl.engine.enemies:
		var spec := BattleStage.stand_in_spec(e.id)
		var h := float(spec.get("height", 0.0)) + float(spec.get("hover", 0.0))
		if h > top:
			top = h
			tallest = e.id
		far = maxf(far, ctl.stage.stand_in(e.id).global_position.distance_to(eye))
	var d := ctl.stage.stand_in(tallest).global_position.distance_to(eye)
	assert_true(d >= far - 0.7, "%s, the tallest, stands at the back (%.2f m of %.2f)" % [tallest, d, far])
	_free()


func test_no_foe_hides_behind_another_at_rest() -> void:
	for enc: StringName in [&"ch03_causeway_shore", &"ch03_causeway_harrier", &"sandbox_reef"]:
		_start(enc)
		var dir := ctl.stage.choreo.camera
		var inv := dir._parent_inverse()
		var lens := {"pos": dir.default_transform.origin}
		for a in ctl.engine.enemies:
			var box := dir._body_box(a.id)
			for b in ctl.engine.enemies:
				if a == b:
					continue
				var f := ctl.stage.stand_in(b.id)
				var mid := inv * f.global_position.lerp(f.head_position(), 0.5)
				var behind := (
					(inv * f.global_position).distance_to(lens["pos"])
					> (inv * ctl.stage.stand_in(a.id).global_position).distance_to(lens["pos"])
				)
				if behind:
					assert_false(
						BattleCameraDirector._blocked(lens, box, [mid]), "%s: %s hidden by %s" % [enc, b.id, a.id]
					)
		_free()
