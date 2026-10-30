extends TestCase
## M2-ENV-11: the battle arenas (docs/kb/tech/battle_arenas.md). Each arena scene loads as a BattleArenaRoot with
## its own WorldEnvironment and Sun and no camera; the floor under every battle sandbox slot (read from
## battle_sandbox.tscn, so a moved slot is checked where it now is) is flat and clear; nothing stands between
## the BattleCamera and a fighter; and the arena sea stops publishing the water level while hidden.

const ARENAS: Array[StringName] = [
	&"tideline_dawn",
	&"causeway_disc_sunset",
	&"causeway_route_afternoon",
	&"derelict_deck_night",
	&"ash_terrace_lanternfall",
	&"underway_tower",
	&"oruvel_raft_morning",
	&"seawall_stairhead_storm",
	&"seawall_stairhead_hoist",
	&"seawall_stairhead_surge",
	&"coilspire_headland_path",
	&"coilspire_tier_landing",
	&"ashcrown_forecourt_day",
	&"ashcrown_anvil_court",
	&"keth_seep_terrace",
	&"lowlight_engine_hall",
	&"ossa_fen_roots",
	&"bridal_barge_night",
	&"ansedra_lagoon_escape",
	&"drowned_choir_ring",
	&"iskarra_spire_crown",
	&"undertow_cage",
	&"undertow_heart",
	&"undertow_heart_letting",
	&"lacquer_court_steps",
]
## The clear floor (arenas.py FLOOR_Y / FLOOR_TOLERANCE_M / FLOOR_CLEAR_M): within this radius of a slot,
## nothing rises above the floor by more than the tolerance, and most of the ground is the floor itself
## (a paving joint may drop a ray into the bed below).
const FLOOR_Y := 0.0
const FLOOR_TOLERANCE_M := 0.05
const FLOOR_CLEAR_M := 1.0
const FLOOR_RING_RAYS := 8
const FLOOR_MIN_SHARE := 0.7
## The floor rays start at the fighters' head-room: a ceiling above it (the drowned tower's gallery, M3-ENV-06
## `underway_tower`, 6 m clear) is not on the floor. Open-air arenas have nothing between this and the floor anyway.
const RAY_FROM_M := 5.5
## A fighter's chest, for the camera's line of sight (the stand-ins are 0.6-2.4 m tall).
const CHEST_M := 0.9


func test_every_arena_is_a_battle_arena_with_its_grade_and_no_camera() -> void:
	for id in ARENAS:
		var root := _instance(id)
		assert_true(root is BattleArenaRoot, "%s: root is a BattleArenaRoot" % id)
		if not root is BattleArenaRoot:
			continue
		var arena := root as BattleArenaRoot
		assert_eq(arena.arena_id, id, "%s: arena_id" % id)
		assert_true(arena.world_environment() != null and arena.world_environment().environment != null, "%s env" % id)
		assert_true(arena.sun() != null, "%s: has a Sun" % id)
		assert_true(arena.sea() is ArenaSea, "%s: its Sea is an ArenaSea" % id)
		assert_eq(_count(arena, "Camera3D"), 0, "%s: no camera (the battle scene owns the BattleCamera)" % id)
		assert_eq(_count(arena, "WorldEnvironment"), 1, "%s: one WorldEnvironment" % id)
		assert_eq(_count(arena, "DirectionalLight3D"), 1, "%s: one sun" % id)
		assert_true(not arena.camera_hints().is_empty(), "%s: camera hints for the presentation track" % id)
		arena.free()


func test_the_floor_under_every_slot_is_flat_and_clear() -> void:
	var slots := BattleArenaLayout.slot_points(BattleArenaLayout.read())
	assert_eq(slots.size(), 6, "the sandbox has six slots")
	for id in ARENAS:
		var root := _instance(id) as Node3D
		var meshes := _meshes(root)
		for s in slots:
			var hits := 0
			var floor_hits := 0
			for p in _floor_samples(s):
				var y := _top(meshes, p)
				if is_nan(y):
					continue
				hits += 1
				assert_true(
					y <= FLOOR_Y + FLOOR_TOLERANCE_M, "%s: something stands %.2f m up near slot %s" % [id, y, s]
				)
				if absf(y - FLOOR_Y) <= FLOOR_TOLERANCE_M:
					floor_hits += 1
			assert_true(hits > 0, "%s: ground under slot %s" % [id, s])
			assert_true(float(floor_hits) / maxf(hits, 1) >= FLOOR_MIN_SHARE, "%s: floor at slot %s" % [id, s])
		root.free()


func test_nothing_stands_between_the_battle_camera_and_a_fighter() -> void:
	var layout := BattleArenaLayout.read()
	var eye: Vector3 = (layout["camera"] as Transform3D).origin
	for id in ARENAS:
		var root := _instance(id) as Node3D
		var meshes := _meshes(root)
		for s in BattleArenaLayout.slot_points(layout):
			var target := Vector3(s.x, CHEST_M, s.y)
			for m: Array in meshes:
				var xf: Transform3D = m[1]
				var hit: Dictionary = (m[0] as TriangleMesh).intersect_segment(xf * eye, xf * target)
				assert_true(hit.is_empty(), "%s: %s blocks the camera's view of slot %s" % [id, m[2], s])
		root.free()


func test_the_disc_leaves_room_for_the_boss_and_the_flood() -> void:
	var arena := _instance(&"causeway_disc_sunset") as Node3D
	var boss := arena.get_node_or_null(NodePath(BattleArenaRoot.BOSS_ANCHOR)) as Marker3D
	var flood := arena.get_node_or_null(NodePath(BattleArenaRoot.FLOOD_ANCHOR)) as Marker3D
	assert_true(boss != null and flood != null, "BossAnchor and FloodAnchor")
	if boss != null and flood != null:
		assert_true(boss.position.y < flood.position.y, "the sunk pool's floor is under low water (it holds water)")
		assert_eq(Vector2(flood.position.x, flood.position.z), Vector2.ZERO, "the flood rig's water origin")
		var sea := (arena as BattleArenaRoot).sea()
		assert_between(sea.position.y, flood.position.y - 0.01, flood.position.y + 0.01, "the sea starts at low water")
	arena.free()


func test_the_arena_sea_publishes_only_while_visible() -> void:
	var tree := Engine.get_main_loop() as SceneTree
	var holder := Node3D.new()
	var sea := ArenaSea.new()
	holder.add_child(sea)
	tree.current_scene.add_child(holder)
	assert_true(sea.is_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP), "visible: publishes")
	holder.visible = false
	assert_false(sea.is_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP), "hidden (by a parent): stops")
	holder.visible = true
	assert_true(sea.is_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP), "shown again: publishes again")
	holder.free()


## Every arena's own Sea (its night look and sea-glow included) publishes only while visible: taken out of its
## arena into a holder in the tree, hiding the holder stops it and showing it again restarts it.
func test_every_arena_sea_publishes_only_while_visible() -> void:
	var tree := Engine.get_main_loop() as SceneTree
	for id in ARENAS:
		var arena := _instance(id)
		var sea := arena.get_node_or_null(NodePath(BattleArenaRoot.SEA)) as ArenaSea
		assert_true(sea != null, "%s: a Sea" % id)
		if sea == null:
			arena.free()
			continue
		sea.owner = null
		arena.remove_child(sea)
		var holder := Node3D.new()
		holder.add_child(sea)
		tree.current_scene.add_child(holder)
		assert_true(sea.is_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP), "%s: visible, publishes" % id)
		holder.visible = false
		assert_false(sea.is_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP), "%s: hidden, stops" % id)
		holder.visible = true
		assert_true(sea.is_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP), "%s: shown again, publishes" % id)
		holder.free()
		arena.free()


func test_the_layout_follows_the_sandbox_scene() -> void:
	var layout := BattleArenaLayout.read()
	assert_eq((layout["party"] as Array).size(), 3, "three party slots")
	assert_eq((layout["enemy"] as Array).size(), 3, "three enemy slots")
	assert_true(float(layout["fov"]) > 0.0, "the camera's fov")
	assert_true((layout["camera"] as Transform3D).origin.y > FLOOR_Y, "the camera is above the floor")


func test_a_grounded_scatter_sits_on_its_ground() -> void:
	var tree := Engine.get_main_loop() as SceneTree
	var root := Node3D.new()
	var ground := MeshInstance3D.new()
	ground.name = "Ground"
	var plane := PlaneMesh.new()
	plane.size = Vector2(20.0, 20.0)
	ground.mesh = plane
	ground.position = Vector3(0.0, 2.0, 0.0)
	root.add_child(ground)
	tree.current_scene.add_child(root)
	var scatter := VegetationScatter.new()
	scatter.source_scene = load("res://assets/environments/vegetation/saltgrass_clumps.glb")
	scatter.count = 40
	scatter.half_extents_m = Vector2(4.0, 4.0)
	scatter.patch_strength = 0.0
	scatter.ground = ground
	root.add_child(scatter)
	assert_true(scatter.placed.size() > 0, "instances placed")
	for xf in scatter.placed:
		assert_between(xf.origin.y, 1.99, 2.01, "on the ground")
	scatter.height_min_m = 3.0
	scatter.rebuild()
	assert_eq(scatter.placed.size(), 0, "out of the height range: skipped")
	root.free()


## M3-ENV-06 `underway_tower`: the arena carries its own underwater look on its Sea, Rhen's lantern target, and held
## motes at their own energy (a day battle keeps the hymn_glimmer gate shut).
func test_the_underwater_arena_carries_its_rig_lantern_and_held_motes() -> void:
	var arena := _instance(&"underway_tower") as BattleArenaRoot
	var rig := arena.get_node_or_null(^"Underwater") as ArenaUnderwater
	assert_true(rig != null, "an ArenaUnderwater")
	if rig != null:
		assert_eq(rig.water, arena.sea(), "the rig's water is the arena's Sea")
		assert_eq(rig.lantern_target, arena.get_node_or_null(^"Lantern"), "Rhen's lantern target")
		assert_between(rig.light_scale, 0.05, 0.99, "the gallery scales the in-scatter down")
		assert_true(arena.sea().position.y > 20.0, "the surface is 22 m over the gallery's floor")
	var motes := arena.get_node_or_null(^"HeldMotes") as GlimmerField
	assert_true(motes != null, "held motes")
	if motes != null:
		assert_eq(motes.mode, GlimmerState.Mode.HELD)
		assert_false(motes.follow_scene_intensity, "their own energy, not the day's shut gate")
	arena.free()


## ArenaUnderwater scales the rig's in-scatter light level (the stand-in for M3-RND-24's per-area scale) without
## touching the rig's shared data cache.
func test_arena_underwater_scales_the_light_level() -> void:
	var tree := Engine.get_main_loop() as SceneTree
	var host := Node3D.new()
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	host.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.light_energy = 3.0
	host.add_child(sun)
	var water := WaterSurface.new()
	host.add_child(water)
	var plain := UnderwaterRig.new()
	plain.water = water
	host.add_child(plain)
	var scaled := ArenaUnderwater.new()
	scaled.water = water
	scaled.light_scale = 0.33
	host.add_child(scaled)
	tree.current_scene.add_child(host)
	var reference := float((UnderwaterRig.load_data()["optics"] as Dictionary)["light_reference"])
	assert_between(scaled.light_level(), plain.light_level() * 0.33 - 1e-4, plain.light_level() * 0.33 + 1e-4)
	assert_eq(float((UnderwaterRig.load_data()["optics"] as Dictionary)["light_reference"]), reference, "cache intact")
	host.free()


func _instance(id: StringName) -> Node:
	var scene := load(BattleArenaRoot.path_for(id)) as PackedScene
	assert_true(scene != null, "%s loads" % id)
	return scene.instantiate() if scene != null else Node3D.new()


func _count(n: Node, cls: String) -> int:
	var c := 1 if n.is_class(cls) else 0
	for k in n.get_children():
		c += _count(k, cls)
	return c


## [TriangleMesh, root-to-mesh Transform3D, name] for every mesh in the arena (scatters and the sea build
## theirs at _ready, outside the tree here; neither may stand on the floor anyway).
func _meshes(root: Node3D) -> Array:
	var out: Array = []
	_collect(root, Transform3D.IDENTITY, out)
	return out


func _collect(n: Node, parent_xf: Transform3D, out: Array) -> void:
	var xf := parent_xf
	if n is Node3D:
		xf = parent_xf * (n as Node3D).transform
	if n is MeshInstance3D and (n as MeshInstance3D).mesh != null:
		out.append([(n as MeshInstance3D).mesh.generate_triangle_mesh(), xf.affine_inverse(), n.name])
	for c in n.get_children():
		_collect(c, xf, out)


func _floor_samples(s: Vector2) -> Array[Vector2]:
	var out: Array[Vector2] = [s]
	for r in [FLOOR_CLEAR_M * 0.5, FLOOR_CLEAR_M]:
		for k in FLOOR_RING_RAYS:
			var a := TAU * k / FLOOR_RING_RAYS
			out.append(s + Vector2(cos(a), sin(a)) * r)
	return out


## The highest surface over (x, z) across the meshes, or NAN when nothing is there.
func _top(meshes: Array, p: Vector2) -> float:
	var best := NAN
	var from := Vector3(p.x, RAY_FROM_M, p.y)
	for m: Array in meshes:
		var xf: Transform3D = m[1]
		var hit: Dictionary = (m[0] as TriangleMesh).intersect_ray(xf * from, xf.basis * Vector3.DOWN)
		if hit.is_empty():
			continue
		var y := (xf.affine_inverse() * (hit["position"] as Vector3)).y
		if is_nan(best) or y > best:
			best = y
	return best
