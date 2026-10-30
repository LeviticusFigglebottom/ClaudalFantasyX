extends TestCase
## M4-CIN-1304: cinematics' staging file adds a zone's cutscene shots and marks to its stage, and never overrides the
## chapter layout's own ids.


class FakeZone:
	extends Node3D
	var location_id := &"test/staging"


func test_staging_adds_what_the_layout_lacks_and_keeps_what_it_has() -> void:
	var zone := FakeZone.new()
	var stage := CutsceneStage.new()
	stage.name = "CutsceneStage"
	zone.add_child(stage)
	var shots := Node.new()
	shots.name = "Shots"
	stage.add_child(shots)
	var layout_shot := CutsceneShotNode.new()
	layout_shot.name = "kept"
	layout_shot.shot = CameraShot.new()
	layout_shot.shot.id = &"kept"
	layout_shot.shot.position = Vector3(1, 1, 1)
	shots.add_child(layout_shot)
	var swapped := CutsceneShotNode.new()
	swapped.name = "swapped"
	swapped.shot = CameraShot.new()
	swapped.shot.id = &"swapped"
	swapped.shot.position = Vector3(2, 2, 2)
	shots.add_child(swapped)
	var marks := Node3D.new()
	marks.name = "Marks"
	stage.add_child(marks)
	var gate := Marker3D.new()
	gate.name = "pell_gate"
	gate.position = Vector3(3, 0, 3)
	marks.add_child(gate)
	var added := CutsceneStaging.apply(stage)
	assert_eq(added, [&"swapped", &"T01", &"shore_front"] as Array[StringName], "the missing ids and the replaced")
	assert_eq(stage.shot(&"swapped").position, Vector3(5, 5, 5), "a replace-listed id is cinematics'")
	var t01 := stage.shot(&"T01")
	assert_true(t01 != null and t01.id == &"T01")
	assert_eq(t01.position, Vector3(0, 2, 6))
	assert_eq(t01.look_at, Vector3(0, 1, 0))
	assert_eq(t01.fov_deg, 40.0)
	assert_eq(stage.shot(&"kept").position, Vector3(1, 1, 1), "the layout's shot is the layout's")
	assert_eq(stage.mark(&"pell_gate").position, Vector3(3, 0, 3), "and so is its mark")
	var front := stage.mark(&"shore_front")
	assert_eq(front.position, Vector3(1, 0, -2))
	assert_between(front.rotation_degrees.y, 89.999, 90.001)
	assert_eq(CutsceneStaging.apply(stage).size(), 0, "a second play adds nothing")
	zone.free()


func test_a_zone_with_no_staging_file_is_left_alone() -> void:
	var zone := FakeZone.new()
	zone.location_id = &"test/none"
	var stage := CutsceneStage.new()
	zone.add_child(stage)
	assert_eq(CutsceneStaging.apply(stage).size(), 0)
	assert_eq(stage.get_child_count(), 0)
	zone.free()
