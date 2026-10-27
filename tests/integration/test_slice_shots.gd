extends TestCase
## M2-FP-109: every slice_* shot in tests/screenshots/shots.json boots its SliceCutsceneShot rig headless: the
## level is staged, its camera is current, and a shot with a scene_id is playing it a few frames in. The PC
## renders them (TRACK-RULES "RENDERING GOES TO THE PC"); this catches a broken request before it gets there.

const SHOTS := "res://tests/screenshots/shots.json"
const PREFIX := "slice_"
const WARMUP_FRAMES := 3


func _slice_shots() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SHOTS))
	for s: Dictionary in data.get("shots", []):
		if str(s.get("id", "")).begins_with(PREFIX):
			out.append(s)
	return out


func test_every_slice_shot_boots_its_rig() -> void:
	var saved := Game.state
	var shots := _slice_shots()
	assert_true(shots.size() >= 6, "the slice shots are in the manifest")
	var tree := Engine.get_main_loop() as SceneTree
	for shot in shots:
		var rig := (load(str(shot["scene"])) as PackedScene).instantiate() as SliceCutsceneShot
		tree.root.add_child(rig)
		var props: Dictionary = ((shot.get("setup", {}) as Dictionary).get("nodes", {}) as Dictionary).get(".", {})
		# The capture's own setup path, so a property it can't set fails here, not on the PC.
		var setup := CaptureSetup.new({"nodes": {".": props}})
		assert_eq(setup.attach(rig), "", "%s's setup applies" % shot["id"])
		for i in WARMUP_FRAMES:
			await tree.process_frame
		var id := str(shot["id"])
		assert_true(rig.level != null and rig.level.is_inside_tree(), "%s staged its level" % id)
		var cam := rig.get_viewport().get_camera_3d()
		assert_true(cam != null and rig.level.is_ancestor_of(cam), "%s looks through the level's camera" % id)
		if StringName(str(props.get("scene_id", ""))) != &"":
			assert_true(rig.sequencer != null and rig.sequencer.is_playing(), "%s is playing its scene" % id)
		setup.end()
		tree.root.remove_child(rig)
		rig.free()
	Game.state = saved
