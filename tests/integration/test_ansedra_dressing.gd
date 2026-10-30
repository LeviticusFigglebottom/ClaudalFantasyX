extends KitWalkProbe
## M4-A2P-043 / M4-A2P-047 (env-art-b): ch13/ansedra dressed on the Haluna kit in the greybox's frame
## (tools/act2/ch13_ansedra_dressing.py). The greybox keeps the collision, so the story's routes still walk; the
## kit covers every greybox mesh; every causeway lamp block has its gold lamp-post; the lagoon is the still mirror.

const ANSEDRA := "res://game/levels/ch13/ansedra/ansedra.tscn"
const FLOOR_Y := 0.0
const LAMP_PIECE := "gold_lamp_post.glb"


func before_each() -> void:
	open(ANSEDRA)


func _trigger(id: String) -> Vector3:
	return (zone.get_node(NodePath("Triggers/%s" % id)) as Node3D).position


func _pieces(kind: String) -> Array[Node3D]:
	var out: Array[Node3D] = []
	for n: Node in zone.get_node(^"Dressing").get_children():
		if n is Node3D and (n as Node3D).scene_file_path.get_file() == kind:
			out.append(n as Node3D)
	return out


func test_the_moorings_reach_the_sanctum() -> void:
	var start := zone.spawn_marker(&"Moorings").position
	var pts: Array[Vector3] = [start, Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, -40.0), _trigger("to_sanctum")]
	var end := walk("to the sanctum", pts, start.y)
	assert_true(absf(end - FLOOR_Y) < 0.05, "on the sanctum isle (y %.2f)" % end)
	close()


func test_the_centre_reaches_corrans_isle_and_the_archive() -> void:
	var centre := Vector3(0.0, 0.0, -40.0)
	var end := walk("to Corran's isle", [centre, Vector3(-40.0, 0.0, -40.0)] as Array[Vector3], FLOOR_Y)
	assert_true(absf(end - FLOOR_Y) < 0.05, "on Corran's isle (y %.2f)" % end)
	var pts: Array[Vector3] = [
		centre, Vector3(36.0, 0.0, -40.0), Vector3(36.0, 0.0, -46.5), Vector3(46.0, 0.0, -46.5), _trigger("to_archive")
	]
	end = walk("to the archive", pts, FLOOR_Y)
	assert_true(absf(end - FLOOR_Y) < 0.05, "at the archive's door (y %.2f)" % end)
	close()


func test_the_kit_covers_the_greybox() -> void:
	var shown: Array[String] = []
	for n: Node in zone.get_node(^"Greybox").get_children():
		for c: Node in n.get_children():
			if c is MeshInstance3D and (c as MeshInstance3D).is_visible_in_tree():
				shown.append(String(n.name))
	assert_eq(shown, [] as Array[String], "no greybox mesh shows")
	var lamps := 0
	for n: Node in zone.get_node(^"Greybox").get_children():
		if String(n.name).begins_with("Causeway") and String(n.name).contains("Lamp"):
			lamps += 1
	assert_true(lamps > 20, "the causeways' lamp blocks (%d)" % lamps)
	assert_eq(_pieces(LAMP_PIECE).size(), lamps, "a gold lamp-post on every lamp block")
	assert_eq(_pieces("lacquer_hall.glb").size(), 2, "Sefir's house and Corran's")
	assert_true(_pieces("bowl_dome.glb").size() >= 10, "the domes round the walk")
	close()


func test_the_lagoon_is_a_still_mirror() -> void:
	var water := zone.get_node(^"Water") as WaterSurface
	assert_true(water != null and water.publishes_water_level, "the lagoon publishes the water level")
	assert_eq(water.wave_set.amplitude_scale, 0.0, "no waves")
	assert_eq(float(water.material.get_shader_parameter(&"roughness_near")), 0.0, "a mirror near the walk")
	assert_eq(float(water.material.get_shader_parameter(&"detail_strength")), 0.0, "no ripples")
	close()
