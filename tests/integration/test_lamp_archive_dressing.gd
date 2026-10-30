extends KitWalkProbe
## M4-A2P-043 (env-art-b): ch13/lamp_archive dressed in the greybox's frame (tools/act2/ch13_archive_dressing.py). The
## greybox keeps the collision: the party walks from the door down the aisle to the ledgers and the Cantor roll; a
## ledger case stands on every Stack block; the kit covers every greybox mesh; no lamp is lit.

const ARCHIVE := "res://game/levels/ch13/lamp_archive/lamp_archive.tscn"
const FLOOR_Y := 0.0


func before_each() -> void:
	open(ARCHIVE)


func _at(id: StringName) -> Vector3:
	return zone.stage.mark(id).position


func test_the_door_reaches_the_ledgers_and_the_roll() -> void:
	var start := zone.spawn_marker(&"Door").position
	var pts: Array[Vector3] = [
		start,
		Vector3(-3.2, 0.0, -9.0),
		_at(&"ledgers"),
		Vector3(-3.2, 0.0, -18.0),
		Vector3(3.2, 0.0, -20.0),
		_at(&"cantor_roll")
	]
	var end := walk("down the aisle", pts, start.y)
	assert_true(absf(end - FLOOR_Y) < 0.05, "on the floor at the roll (y %.2f)" % end)
	close()


func test_a_case_on_every_stack_and_no_greybox_shows() -> void:
	var stacks := 0
	var shown: Array[String] = []
	for n: Node in zone.get_node(^"Greybox").get_children():
		if String(n.name).begins_with("Stack"):
			stacks += 1
		for c: Node in n.get_children():
			if c is MeshInstance3D and (c as MeshInstance3D).is_visible_in_tree():
				shown.append(String(n.name))
	assert_eq(shown, [] as Array[String], "no greybox mesh shows")
	var cases := 0
	for n: Node in zone.get_node(^"Dressing").get_children():
		if n is Node3D and (n as Node3D).scene_file_path.get_file() == "archive_case.glb":
			cases += 1
	assert_eq(cases, stacks, "a ledger case on every Stack block")
	assert_eq(zone.get_node(^"Dressing").find_children("*", "OmniLight3D", true, false).size(), 0, "no lamp is lit")
	close()
