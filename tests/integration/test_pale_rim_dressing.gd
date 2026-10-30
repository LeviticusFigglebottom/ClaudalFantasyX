extends KitWalkProbe
## M4-A2P-046 (env-art-b): the Pale Rim dressed in the greybox's frame (tools/act2/ch16_pale_rim_dressing.py). The
## greybox keeps the collision: the wade runs from the ship past the cairns to the Choir's edge; the kit covers every
## greybox mesh; a cairn stands on every cairn block.

const RIM := "res://game/levels/ch16/pale_rim/pale_rim.tscn"
const FLOOR_Y := 0.0


func before_each() -> void:
	open(RIM)


func test_the_wade_reaches_the_choirs_edge() -> void:
	var start := zone.spawn_marker(&"Rim").position
	var choir: Vector3 = zone.stage.mark(&"choir_edge").position
	var end := walk("the wade", [start, Vector3(100.0, 0.0, 8.0), choir] as Array[Vector3], start.y)
	assert_true(absf(end - FLOOR_Y) < 0.05, "on the sand at the Choir's edge (y %.2f)" % end)
	close()


func test_the_kit_covers_the_greybox() -> void:
	var shown: Array[String] = []
	var blocks := 0
	for n: Node in zone.get_node(^"Greybox").get_children():
		if String(n.name).begins_with("Cairn"):
			blocks += 1
		for c: Node in n.get_children():
			if c is MeshInstance3D and (c as MeshInstance3D).is_visible_in_tree():
				shown.append(String(n.name))
	assert_eq(shown, [] as Array[String], "no greybox mesh shows")
	var cairns := 0
	for n: Node in zone.get_node(^"Dressing").get_children():
		if n is Node3D and (n as Node3D).scene_file_path.get_file() == "cairn.glb":
			cairns += 1
	assert_eq(cairns, blocks, "a cairn on every cairn block")
	close()
