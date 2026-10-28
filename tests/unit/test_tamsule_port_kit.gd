extends TestCase
## M3-C07-04: the Tamsule port kit preview (game/levels/_tests/tamsule_port_kit/, tamsule.md): the market's pieces
## (decks, bridges, stalls, boats, bunting) import with the Tamsule Bell kit's materials on every surface, and the
## port stands round the greybox's blocks with the Bell's ring to the north.

const SCENE := "res://game/levels/_tests/tamsule_port_kit/tamsule_port_kit.tscn"
const MATERIAL_DIR := "res://assets/environments/kits/tamsule_bell/materials/"
const MARKET: Array[String] = [
	"port_deck_8m",
	"port_deck_8m_rail",
	"plank_bridge_4m",
	"market_stall",
	"market_boat_a",
	"market_boat_b",
	"bunting_12m"
]


func test_the_market_pieces_wear_the_kit_materials() -> void:
	for piece in MARKET:
		var packed := load("res://assets/environments/kits/tamsule_bell/%s.glb" % piece) as PackedScene
		assert_true(packed != null, "%s imports" % piece)
		if packed == null:
			continue
		var root := packed.instantiate()
		var meshes := root.find_children("*", "MeshInstance3D", true, false)
		assert_true(not meshes.is_empty(), "%s has meshes" % piece)
		for n in meshes:
			var mi := n as MeshInstance3D
			for i in mi.mesh.get_surface_count():
				var mat := mi.get_active_material(i)
				assert_true(
					mat != null and mat.resource_path.begins_with(MATERIAL_DIR), "%s wears a kit material" % mi.name
				)
		root.free()


func test_the_port_preview_places_the_port_and_the_bell() -> void:
	var scene := (load(SCENE) as PackedScene).instantiate()
	var port := scene.get_node("Port")
	assert_true(port.get_child_count() > 200, "the port and the reach are dressed (%d)" % port.get_child_count())
	assert_true(port.get_node_or_null("ReachBell") != null, "the Bell stands north of the port")
	assert_eq(scene.get_node("Cameras").get_child_count(), 9, "tamsule.md §3's shots TP01-TP09")
	scene.free()
