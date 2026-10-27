extends TestCase
## M3-AUD-812: FootstepAudio reads the ground without any level marking it (game/data/audio/footsteps.json
## `mesh_surfaces`, `water_level`). A kit mesh named like a dock is wood while the feet are on its deck; a pool mesh
## is water while the feet are in it; feet under the zone sea's rest plane wade; a level's own surface area still
## wins; LOD meshes are skipped. Stand-in nodes only; sounds are recorded through the listener's player Callable.

const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const DT := 1.0 / 60.0
const SEA_GROUP := &"hymn_water_level_publishers"

var played: Array = []
var nodes: Array[Node] = []


func before_each() -> void:
	played = []
	nodes = []


func _data() -> Dictionary:
	return (AudioData.table(AudioData.FOOTSTEPS) as Dictionary).duplicate(true)


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _add(n: Node) -> Node:
	_host().add_child(n)
	nodes.append(n)
	return n


func _done() -> void:
	for n in nodes:
		if is_instance_valid(n):
			n.free()
	nodes = []


## A piece named `piece` holding a box mesh named `mesh_name` of `size`, centred at `at` and turned `yaw_deg`.
func _piece(piece: String, mesh_name: String, size: Vector3, at: Vector3, yaw_deg: float = 0.0) -> MeshInstance3D:
	var root := Node3D.new()
	root.name = piece
	root.position = at
	root.rotation_degrees.y = yaw_deg
	var mi := MeshInstance3D.new()
	mi.name = mesh_name
	var box := BoxMesh.new()
	box.size = size
	mi.mesh = box
	root.add_child(mi)
	_add(root)
	return mi


func _sea(y: float) -> Node3D:
	var sea := Node3D.new()
	sea.name = "Sea"
	sea.position.y = y
	_add(sea)
	sea.add_to_group(SEA_GROUP)
	return sea


func _walker(at: Vector3) -> Node3D:
	var w := Node3D.new()
	w.position = at
	_add(w)
	return w


func _listener(w: Node3D) -> FootstepAudio:
	var f := FootstepAudio.new(_data())
	f.player = func(id: StringName, at: Vector3, opts: Dictionary) -> void: played.append([id, at, opts])
	_add(f)
	f.attach(w, HALUNA)
	return f


func _ground_at(at: Vector3) -> StringName:
	var w := _walker(at)
	var f := _listener(w)
	return f._ground(at)


func test_the_data_names_the_dock_the_pools_and_the_sea() -> void:
	var d := _data()
	var rules := (d.get("mesh_surfaces", {}) as Dictionary).get("rules", []) as Array
	var surfaces: Array = rules.map(func(r: Dictionary) -> String: return str(r.get("surface", "")))
	assert_true("wood" in surfaces and "water" in surfaces, "a wood rule and a water rule")
	assert_eq(str((d.get("water_level", {}) as Dictionary).get("group", "")), String(SEA_GROUP), "WaterSurface's group")
	assert_eq(String(FootstepAudio.surface_for(d, HALUNA)), "sand", "Haluna's own ground is sand")


func test_a_dock_deck_is_wood_and_the_sand_beside_it_is_not() -> void:
	# a 4 x 0.4 x 12 m deck whose top is at 1.0 m, turned like Haluna's (35 degrees)
	_piece("Piece", "dock_haluna", Vector3(4.0, 0.4, 12.0), Vector3(-6.0, 0.8, 60.0), 35.0)
	var along := Basis(Vector3.UP, deg_to_rad(35.0)) * Vector3(0.0, 0.0, 5.0)
	assert_eq(String(_ground_at(Vector3(-6.0, 1.0, 60.0) + along)), "wood", "on the deck, near its far end")
	assert_eq(String(_ground_at(Vector3(-6.0, 1.0, 60.0) + Vector3(5.0, 0.0, 0.0))), "sand", "beside it")
	assert_eq(String(_ground_at(Vector3(-6.0, 2.5, 60.0))), "sand", "far above the deck is not on it")
	_done()


func test_lod_meshes_are_skipped() -> void:
	var mi := _piece("dock_haluna", "dock_haluna-lod1", Vector3(4.0, 0.4, 12.0), Vector3(0.0, 0.8, 0.0))
	var found := FootstepAudio.mesh_candidates(_data(), _host())
	assert_false(found.any(func(c: Array) -> bool: return c[0] == mi), "the LOD mesh is no candidate")
	_done()


func test_a_greybox_tidepool_is_water() -> void:
	# the causeway's greybox block: a StaticBody3D named by its layout id holding a Mesh (3 x 0.02 x 2.4 m)
	_piece("Tidepool", "Mesh", Vector3(3.0, 0.02, 2.4), Vector3(5.0, 0.01, -60.0))
	assert_eq(String(_ground_at(Vector3(5.0, 0.0, -60.0))), "water", "in the pool")
	assert_eq(String(_ground_at(Vector3(5.0, 0.0, -55.0))), "sand", "past it")
	_done()


func test_wading_under_the_sea_plane() -> void:
	_sea(0.15)
	assert_eq(String(_ground_at(Vector3(40.0, -0.3, 0.0))), "water", "0.45 m under the rest plane wades")
	assert_eq(String(_ground_at(Vector3(40.0, 0.18, 0.0))), "water", "at the waterline (within above_m)")
	assert_eq(String(_ground_at(Vector3(20.0, 0.6, 0.0))), "sand", "the dry beach")
	assert_eq(String(_ground_at(Vector3(40.0, -3.0, 0.0))), "sand", "deeper than wade_m is not a wade")
	_done()


func test_a_dock_over_the_sea_is_wood_not_water() -> void:
	_sea(0.15)
	_piece("dock_haluna", "dock_haluna", Vector3(4.0, 0.4, 12.0), Vector3(0.0, 0.8, 0.0))
	assert_eq(String(_ground_at(Vector3(0.0, 1.0, 0.0))), "wood")
	_done()


func test_a_level_surface_area_still_wins() -> void:
	_piece("dock_haluna", "dock_haluna", Vector3(4.0, 0.4, 12.0), Vector3(0.0, 0.8, 0.0))
	var area := Area3D.new()
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(2.0, 2.0, 2.0)
	cs.shape = box
	area.add_child(cs)
	area.position = Vector3(0.0, 1.0, 0.0)
	_add(area)
	area.add_to_group(&"audio_surface_stone")
	assert_eq(String(_ground_at(Vector3(0.0, 1.0, 0.0))), "stone", "the level's own mark wins")
	assert_eq(String(_ground_at(Vector3(0.0, 1.0, 4.0))), "wood", "outside it the dock is wood again")
	_done()


func test_walking_onto_the_dock_changes_the_steps() -> void:
	_piece("dock_haluna", "dock_haluna", Vector3(4.0, 0.4, 12.0), Vector3(0.0, 0.8, 6.0))
	var w := _walker(Vector3(0.0, 1.0, -6.0))
	var f := _listener(w)
	for i in 720:  # 12 s at 1 m/s along +z: 6 m of sand, then the deck
		w.position.z += 1.0 * DT
		f.advance(DT)
	var rows: Array = played.map(func(p: Array) -> String: return String(p[0]))
	var sand := rows.filter(func(r: String) -> bool: return r == "hero_step_sand_walk").size()
	var wood := rows.filter(func(r: String) -> bool: return r == "hero_step_wood_walk").size()
	assert_true(sand >= 8, "steps on the sand first (%d)" % sand)
	assert_true(wood >= 8, "then steps on the planks (%d)" % wood)
	assert_eq(rows.find("hero_step_wood_walk") > rows.rfind("hero_step_sand_walk"), true, "sand, then wood, no mix")
	_done()
