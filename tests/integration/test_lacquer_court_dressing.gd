extends KitWalkProbe
## M4-A2P-044 (env-art-b): the Lacquer Court dressed in the greybox's frame (tools/act2/ch14_lacquer_court_dressing.py).
## The greybox keeps the collision: the party walks from the entry to the vows and down the water-steps onto the
## barge; the kit covers every greybox mesh; every lamp-stand's light sits on its stand; the columns are solid.

const COURT := "res://game/levels/ch13/ansedra_lacquer_court/ansedra_lacquer_court.tscn"
const FLOOR_Y := 0.0
const DECK_Y := -0.6
const FLAME_Y := 1.75


func before_each() -> void:
	open(COURT)


func _at(id: StringName) -> Vector3:
	return zone.stage.mark(id).position


func test_the_entry_reaches_the_vows_and_the_barge() -> void:
	var start := zone.spawn_marker(&"CourtEntry").position
	var end := walk("to the vows", [start, Vector3(8.5, 0.0, -2.0), _at(&"vows")] as Array[Vector3], start.y)
	assert_true(absf(end - FLOOR_Y) < 0.05, "on the court at the vows (y %.2f)" % end)
	var pts: Array[Vector3] = [_at(&"vows"), _at(&"kerrid_steps"), Vector3(0.0, 0.0, 4.5), _at(&"barge_deck")]
	end = walk("down the water-steps", pts, FLOOR_Y)
	assert_true(absf(end - DECK_Y) < 0.05, "on the barge's deck (y %.2f)" % end)
	close()


func test_the_kit_covers_the_greybox_and_the_lamps_sit_on_their_stands() -> void:
	var shown: Array[String] = []
	for n: Node in zone.get_node(^"Greybox").get_children():
		for c: Node in n.get_children():
			if c is MeshInstance3D and (c as MeshInstance3D).is_visible_in_tree():
				shown.append(String(n.name))
	assert_eq(shown, [] as Array[String], "no greybox mesh shows")
	var stands: Array[Vector3] = []
	var columns := 0
	for n: Node in zone.get_node(^"Dressing").get_children():
		if not n is Node3D:
			continue
		var kind := (n as Node3D).scene_file_path.get_file()
		if kind == "gilt_lamp_stand.glb":
			stands.append((n as Node3D).position)
		elif kind == "court_column.glb":
			columns += 1
			assert_true(n.find_children("*", "StaticBody3D", true, false).size() > 0, "%s is solid" % n.name)
	assert_eq(columns, 17, "a column on every column block")
	var lights := zone.get_node(^"Dressing").find_children("*", "OmniLight3D", true, false)
	assert_eq(lights.size(), stands.size(), "one light per lamp-stand")
	for l: Node in lights:
		var p := (l as Node3D).position
		var near := false
		for s: Vector3 in stands:
			near = near or Vector2(p.x - s.x, p.z - s.z).length() < 0.05 and absf(p.y - s.y - FLAME_Y) < 0.2
		assert_true(near, "%s sits on a stand's flame" % l.name)
	close()
