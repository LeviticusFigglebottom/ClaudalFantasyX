extends KitWalkProbe
## M4-A2P-045 (env-art-b): Ch15's open sea dressed in the greybox's frame (tools/act2/ch15_open_sea_dressing.py). The
## greybox deck keeps the collision: the party walks from Kerrid's seat past the bier to the bow; the barge covers
## every greybox mesh; no warm source anywhere (no light at all: the moon and the sea).

const OPEN_SEA := "res://game/levels/ch15/open_sea/open_sea.tscn"
const FLOOR_Y := 0.0


func before_each() -> void:
	open(OPEN_SEA)


func _at(id: StringName) -> Vector3:
	return zone.stage.mark(id).position


func test_the_stern_reaches_the_bow_past_the_bier() -> void:
	var start := zone.spawn_marker(&"Deck").position
	var pts: Array[Vector3] = [start, Vector3(-1.4, 0.0, 3.3), Vector3(-1.4, 0.0, 0.0), _at(&"bow")]
	var end := walk("to the bow", pts, start.y)
	assert_true(absf(end - FLOOR_Y) < 0.05, "on the deck at the bow (y %.2f)" % end)
	close()


func test_the_barge_covers_the_greybox_and_nothing_is_lit() -> void:
	var shown: Array[String] = []
	for n: Node in zone.get_node(^"Greybox").get_children():
		for c: Node in n.get_children():
			if c is MeshInstance3D and (c as MeshInstance3D).is_visible_in_tree():
				shown.append(String(n.name))
	assert_eq(shown, [] as Array[String], "no greybox mesh shows")
	assert_eq(zone.get_node(^"Dressing").find_children("*", "Light3D", true, false).size(), 0, "no lamp, no flame")
	close()
