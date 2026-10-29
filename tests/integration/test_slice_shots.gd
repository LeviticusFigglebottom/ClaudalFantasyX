extends TestCase
## M2-FP-109: every shot in tests/screenshots/shots.json on the SliceCutsceneShot rig (the slice_* and Ch1 shots)
## boots headless: the level is staged, its camera is current, and a shot with a scene_id is playing it. The PC
## renders them (TRACK-RULES "RENDERING GOES TO THE PC"); this catches a broken request before it gets there.

const SHOTS := "res://tests/screenshots/shots.json"
const RIG := "res://game/levels/_tests/slice_shots/slice_cutscene_shot.tscn"
const COMPILED := "res://game/data/dialogue/compiled/%s.json"


func _slice_shots() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SHOTS))
	for s: Dictionary in data.get("shots", []):
		if str(s.get("scene", "")) == RIG:
			out.append(s)
	return out


func test_every_slice_shot_boots_its_rig() -> void:
	var saved := Game.state
	var shots := _slice_shots()
	assert_true(shots.size() >= 6, "the slice shots are in the manifest")
	var tree := Engine.get_main_loop() as SceneTree
	var host: Node = tree.current_scene if tree.current_scene != null else tree.root  # the root is busy in the runner
	for shot in shots:
		var rig := (load(str(shot["scene"])) as PackedScene).instantiate() as SliceCutsceneShot
		host.add_child(rig)
		var props: Dictionary = ((shot.get("setup", {}) as Dictionary).get("nodes", {}) as Dictionary).get(".", {})
		# The capture's own setup path, so a property it can't set fails here, not on the PC.
		var setup := CaptureSetup.new({"nodes": {".": props}})
		assert_eq(setup.attach(rig), "", "%s's setup applies" % shot["id"])
		rig.start()  # the runner never steps a frame, so the rig's deferred start is called here
		var id := str(shot["id"])
		assert_true(rig.level != null and rig.level.is_inside_tree(), "%s staged its level" % id)
		var cam := rig.get_viewport().get_camera_3d()
		assert_true(cam != null and rig.level.is_ancestor_of(cam), "%s looks through the level's camera" % id)
		if StringName(str(props.get("scene_id", ""))) != &"" or StringName(str(props.get("story_call", ""))) != &"":
			assert_true(rig.sequencer != null and rig.sequencer.is_playing(), "%s is playing its scene" % id)
		var hold := StringName(str(props.get("hold_line", "")))
		if hold != &"":
			# The held line is one of the scene's (a typo would let the shot run on), and showing it stops the scene.
			var compiled := FileAccess.get_file_as_string(COMPILED % str(props.get("scene_id", "")))
			assert_true(compiled.contains('"id": "%s"' % hold), "%s holds a line of its scene (%s)" % [id, hold])
			var step := DialogueStep.new()
			step.line_id = hold
			rig.call(&"_on_line_shown", step)
			assert_false(rig.sequencer.auto_advance, "%s stops on %s" % [id, hold])
		setup.end()
		host.remove_child(rig)
		rig.free()
	Game.state = saved
