extends TestCase
## The human's playtest: "primitive moments" (M2-FP-116). No scene in the M2 slice (or Ch1's two zones, M3-C01-100
## and 101) shows a visible PrimitiveMesh (a box, cylinder, sphere, capsule or torus standing in for a model) except
## the ones listed below, each waiting on its request. A new stand-in fails here until it is listed with the
## request that replaces it.

const SCENES: Array[String] = [
	"res://game/levels/prologue/prologue.tscn",
	"res://game/levels/ch02/haluna/haluna.tscn",
	"res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn",
	"res://game/levels/ch03/shell_shrine/shell_shrine.tscn",
	"res://game/levels/ch03/first_verse/first_verse.tscn",
	"res://game/levels/ch01/oruvel/oruvel.tscn",
	"res://game/levels/ch01/oruvel_underway/oruvel_underway.tscn",
]
## The battle arenas these zones fight in, by their arenas.json id (env-art's kits; the greybox ones under
## game/battle/arenas/ were retired, M3-ENV-737).
const ARENAS: Array[StringName] = [
	&"tideline_dawn",
	&"causeway_route_afternoon",
	&"causeway_disc_sunset",
	&"oruvel_raft_morning",
	&"underway_tower",
]
const ARENAS_JSON := "res://game/data/battle/arenas.json"
## Path prefixes (from the scene root) still allowed, and why.
const KNOWN: Dictionary = {
	"City/Vigils/": "Kerrid, Pell and Liss: each takes its hero body when it lands (M3-CHR-505/506, Liss)",
	"NPCs/Neme/Bag": "Neme's bag, a creatures prop",
	"Set/ChamberPassage": "env-art's passage behind the shrine's east door (part of its dressing)",
	"Dressing/ChamberPassage": "the same, in the shrine level",
	"Room/InnerPoolWater/": "the First Verse's pool water (a flat octagon, the shrine level's own shape)",
	"Underwater/UnderwaterPost": "the UnderwaterRig's full-screen post passes (quads, never seen as shapes)",
}


func test_no_unlisted_primitive_shows_in_the_slice() -> void:
	var tree := Engine.get_main_loop() as SceneTree
	var host: Node = tree.current_scene if tree.current_scene != null else tree.root
	var saved_flags := Game.state.flags.duplicate(true)
	Game.state.flags.erase(&"ch01_gulls_cried")  # an earlier test's storm brings Oruvel up in it (its StormWall)
	var paths: Array[String] = SCENES.duplicate()
	var arenas: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ARENAS_JSON))["arenas"]["scenes"]
	for id in ARENAS:
		assert_true(arenas.has(String(id)), "%s is in arenas.json" % id)
		paths.append(str(arenas.get(String(id), "")))
	for path in paths:
		if not ResourceLoader.exists(path):
			assert_true(false, "%s exists" % path)
			continue
		var root := (load(path) as PackedScene).instantiate()
		if root.has_method(&"prebuild"):
			root.call(&"prebuild")
		if root.get(&"autoplay") != null:
			root.set(&"autoplay", false)
		host.add_child(root)  # the runner calls tests without awaiting them: everything here is synchronous
		for m: Node in root.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi.mesh is PrimitiveMesh and mi.is_visible_in_tree():
				var at := str(root.get_path_to(mi))
				assert_true(_known(at), "%s shows a %s at %s" % [path.get_file(), mi.mesh.get_class(), at])
		host.remove_child(root)
		root.free()
	Game.state.flags = saved_flags


func _known(at: String) -> bool:
	for prefix: String in KNOWN:
		if at.begins_with(prefix):
			return true
	return false
