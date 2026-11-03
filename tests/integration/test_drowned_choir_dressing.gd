extends KitWalkProbe
## M4-A2P-046 (env-art-b): the Drowned Choir dressed over chapters' relayout
## (tools/act2/ch16_drowned_choir_dressing.py).
## The greybox keeps the collision: the walk comes in from the approach through the south gap and over the bridge to
## the dais, then up the north aisle's ramp to Kesh's mark; the kit covers every greybox mesh; a singer stands on every
## Mouth block.

const CHOIR := "res://game/levels/ch16/drowned_choir/drowned_choir.tscn"
const DAIS_Y := 0.0


func before_each() -> void:
	open(CHOIR)


func test_the_walk_through_the_gap_and_up_the_aisle() -> void:
	var start := zone.spawn_marker(&"Approach").position
	var dais := walk("the gap", [start, Vector3(0.0, 0.0, 12.0), Vector3(0.0, 0.0, 2.0)] as Array[Vector3], start.y)
	assert_true(absf(dais - DAIS_Y) < 0.05, "on the dais (y %.2f)" % dais)
	var kesh: Vector3 = zone.stage.mark(&"kesh").position
	var top := walk("the aisle", [Vector3(0.0, 0.0, 2.0), Vector3(0.0, 0.0, -9.0), kesh] as Array[Vector3], DAIS_Y)
	assert_true(absf(top - kesh.y) < 0.15, "at Kesh's mark on the rim (y %.2f, mark %.2f)" % [top, kesh.y])
	close()


func test_the_kit_covers_the_greybox() -> void:
	var shown: Array[String] = []
	var mouths := 0
	for n: Node in zone.get_node(^"Greybox").get_children():
		if String(n.name).begins_with("Mouth"):
			mouths += 1
		for c: Node in n.get_children():
			if c is MeshInstance3D and (c as MeshInstance3D).is_visible_in_tree():
				shown.append(String(n.name))
	assert_eq(shown, [] as Array[String], "no greybox mesh shows")
	var singers := 0
	var walked := 0
	for n: Node in zone.get_node(^"Dressing").get_children():
		if not n is Node3D:
			continue
		match (n as Node3D).scene_file_path.get_file():
			"choir_singer.glb":
				singers += 1
			"choir_amphitheatre_walked.glb":
				walked += 1
	assert_eq(singers, mouths, "a singer on every Mouth block")
	assert_eq(walked, 1, "the walked amphitheatre")
	close()
