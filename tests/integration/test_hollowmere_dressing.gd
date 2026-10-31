extends KitWalkProbe
## M4-A2P-045 (env-art-b): Hollowmere's first visit dressed in the greybox's frame
## (tools/act2/ch15_hollowmere_dressing.py). The greybox keeps the collision: the party walks the dock from its spawn
## past the ship's gangway and the supper to the pyre-raft, and out a jetty to Liss's father's door; the kit covers
## every greybox mesh; every oil lamp carries its light.

const HOLLOWMERE := "res://game/levels/ch17/hollowmere/hollowmere.tscn"
const FLOOR_Y := 0.0


func before_each() -> void:
	open(HOLLOWMERE)


func _at(id: StringName) -> Vector3:
	return zone.stage.mark(id).position


func test_the_dock_reaches_the_pyre_and_the_fathers_door() -> void:
	var start := zone.spawn_marker(&"Dock").position
	# the north half, past the supper mark (the table stands by the father's place on the south rail)
	var pts: Array[Vector3] = [start, Vector3(30.0, 0.0, -0.8), _at(&"supper"), _at(&"pyre_raft")]
	var end := walk("along the dock", pts, start.y)
	assert_true(absf(end - FLOOR_Y) < 0.05, "on the dock at the pyre (y %.2f)" % end)
	pts = [Vector3(28.0, 0.0, 0.0), Vector3(28.0, 0.0, -8.0), _at(&"fathers_door")]
	end = walk("out the jetty", pts, FLOOR_Y)
	assert_true(absf(end - FLOOR_Y) < 0.05, "at the father's door (y %.2f)" % end)
	close()


func test_the_kit_covers_the_greybox_and_the_lamps_are_lit() -> void:
	var shown: Array[String] = []
	for n: Node in zone.get_node(^"Greybox").get_children():
		for c: Node in n.get_children():
			if c is MeshInstance3D and (c as MeshInstance3D).is_visible_in_tree():
				shown.append(String(n.name))
	assert_eq(shown, [] as Array[String], "no greybox mesh shows")
	var lamps := 0
	for n: Node in zone.get_node(^"Dressing").get_children():
		if n is Node3D and (n as Node3D).scene_file_path.get_file() in ["hm_oil_lamp.glb", "hm_signal_lamp.glb"]:
			lamps += 1
	var lights := zone.get_node(^"Dressing").find_children("*", "OmniLight3D", true, false).size()
	assert_eq(lights, lamps + 2, "a light for every lamp, the supper's and the dock-master's table lamp (Ch17)")
	close()
