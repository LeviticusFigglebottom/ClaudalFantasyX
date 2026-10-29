extends TestCase
## M2-FP-02: the playable Haluna zone (game/levels/ch02/haluna/). It loads with the mood scene
## instanced, builds its walk collision, frames Rhen under a camera volume at every spawn, keeps
## him on the ground and out of buildings and the sea, and authors the villagers, the two story
## triggers and Cutscene A's stage for the first-playable story driver.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const LOCATION := &"ch02/haluna"
const DT := 1.0 / 60.0
const SPAWNS: Array[StringName] = [
	&"Beach", &"Village", &"Shrine", &"BattleReturn", &"BeforeBattle", &"CausewayHead", &"DockNight"
]
## Collision build budget on the shared CI CPU (the brief asks for under about a second).
const BUILD_BUDGET_MSEC := 1000
## How far a spawn marker may sit from the floor found under it.
const GROUND_TOLERANCE_M := 0.1
const NPCS := {
	&"npc_market": "ch02_bark_market",
	&"npc_chapel": "ch02_bark_chapel",
	&"npc_dock": "ch02_bark_dock",
	&"npc_lane": "ch02_bark_lane",
}
const BARKS: Array[StringName] = [&"ch02_bark_market", &"ch02_bark_chapel", &"ch02_bark_dock", &"ch02_bark_lane"]
const STAGE_SHOTS: Array[StringName] = [&"H05", &"H05_up", &"H06", &"H01", &"H08", &"H08_hand", &"H03", &"B02_bag"]
## In front of the chapel door (order_chapel at (-118, 27.5), 9.25 m deep: its south face is z 32.1).
const CHAPEL_FRONT := Vector3(-119.5, 0.0, 35.0)
const CHAPEL_SOUTH_WALL_Z := 32.0
const STAGE_MARKS: Array[StringName] = [&"kneel_beside_rhen", &"beach_path", &"rhen_shallows", &"rhen_lantern"]

var zone: HalunaZone
var saved_flags: Dictionary


func before_each() -> void:
	saved_flags = Game.state.flags.duplicate(true)


func _load_into_tree() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)


func _done() -> void:
	if zone != null:
		_host().remove_child(zone)
		zone.free()
		zone = null
	Game.state.flags = saved_flags


func test_the_zone_walks_frames_and_holds_rhen() -> void:
	_load_into_tree()
	assert_true(zone.player != null and zone.player.is_in_group(&"player"), "Rhen is the FieldController")
	assert_eq(zone.player.name, &"Player")
	assert_true(zone.director != null and zone.director.hub_orbit_enabled, "the hub may orbit")
	assert_true(zone.stage != null)
	assert_true(zone.get_viewport().get_camera_3d() == zone.field_camera, "no mood camera holds the view")
	var col := zone.collision
	print("    haluna collision: %d ms, %d shapes" % [col.build_msec, col.shape_count])
	assert_true(col.build_msec < BUILD_BUDGET_MSEC, "collision built in %d ms" % col.build_msec)
	for kind: String in ["house_tile_a", "order_chapel", "tidewall_straight", "dock_haluna", "banyan_hero"]:
		assert_true(int(col.kinds.get(kind, 0)) > 0, "%s has collision" % kind)
	assert_false(col.kinds.has("tidewall_gate"), "the lane gates stay open")

	for spawn in SPAWNS:
		var marker := zone.spawn_marker(spawn)
		assert_true(marker != null, "spawn %s" % spawn)
		if marker == null:
			continue
		var p := marker.global_position
		var floor_y := _floor_y(p)
		assert_between(floor_y, p.y - GROUND_TOLERANCE_M, p.y + GROUND_TOLERANCE_M, "ground under %s" % spawn)
		if spawn != &"DockNight":  # M2-FP-15: on the dock deck, over the water, not the terrain
			assert_between(col.ground_height(p.x, p.z), floor_y - 0.05, floor_y + 0.05, "height_at agrees (%s)" % spawn)
		assert_true(zone.place_at(spawn, zone.spawn_yaw_deg(spawn)), "place_at %s" % spawn)
		var at := zone.player.global_position
		assert_true(Vector2(at.x - p.x, at.z - p.z).length() < 0.01, "Rhen stands on %s" % spawn)
		assert_ne(zone.director.active_shot_id(), &"", "a shot frames %s" % spawn)
		_assert_framed("at %s" % spawn)
	assert_false(zone.place_at(&"Nowhere"), "an unknown spawn is refused")

	# A few metres from the beach and the village: he stays on the ground the whole way.
	_walk_from(&"Beach", Vector3.LEFT, 2.5)
	_walk_from(&"Village", Vector3(0.94, 0.0, 0.34), 2.5)
	_walk_from(&"Shrine", Vector3.RIGHT, 1.5)
	# Buildings are solid: walking north into the chapel's door front stops at its wall.
	zone.place_at(&"Village")
	zone.player.global_position = CHAPEL_FRONT + Vector3.UP * (col.ground_height(CHAPEL_FRONT.x, CHAPEL_FRONT.z) + 0.02)
	_walk(Vector3.FORWARD, 3.0)
	assert_true(
		zone.player.global_position.z > CHAPEL_SOUTH_WALL_Z, "the chapel holds (z %.2f)" % zone.player.global_position.z
	)
	# The sea wall: walking out to sea from the beach stops in the shallows.
	zone.place_at(&"Beach")
	_walk(Vector3.RIGHT, 6.0)
	var x_sea := col.terrain.inland_m(0.0, zone.player.global_position.z) + col.wade_m
	assert_true(
		zone.player.global_position.x < x_sea, "kept out of deep water (x %.1f)" % zone.player.global_position.x
	)
	assert_true(col.ground_height(zone.player.global_position.x, zone.player.global_position.z) > -1.0, "shallows")
	_done()


func test_villagers_and_triggers_fire_their_payloads() -> void:
	_load_into_tree()
	var fired: Array[StringName] = []
	var found := {}
	for n in zone.get_tree().get_nodes_in_group(Interactable.GROUP):
		var it := n as Interactable
		if it != null and zone.is_ancestor_of(it):
			found[it.id] = it
			# M2-FP-13's overheard fragments sit along these walks; they block nothing, so not counted.
			if not bool(it.payload.get("overheard", false)):
				it.used.connect(func(i: Interactable) -> void: fired.append(i.id))
	for id: StringName in NPCS:
		var it := found.get(id) as Interactable
		assert_true(it != null, "villager %s" % id)
		if it == null:
			continue
		assert_eq(it.activation, Interactable.Activation.INTERACT)
		assert_eq(it.payload, {"dialogue": NPCS[id]}, "%s plays its bark" % id)
		# Stand within reach, beside the villager, and listen.
		zone.player.global_position = it.global_position + Vector3(0.0, -0.8, 0.0) + _beside(it)
		assert_eq(zone.player.interact(), it, "%s answers the interact button" % id)
	assert_eq(fired, NPCS.keys() as Array[StringName], "each villager fired once")

	var battle := found.get(&"tideline_battle") as Interactable
	var causeway := found.get(&"causeway_head") as Interactable
	assert_true(battle != null and causeway != null, "both story triggers exist")
	if battle == null or causeway == null:
		_done()
		return
	assert_eq(battle.activation, Interactable.Activation.TOUCH)
	assert_eq(battle.payload, {"battle": "ch02_tideline"})
	assert_eq(battle.requires_flag, &"ch02_met_asha")
	assert_eq(battle.blocked_by_flag, &"ch02_tideline_won")
	assert_eq(causeway.activation, Interactable.Activation.TOUCH)
	assert_eq(causeway.payload, {"cutscene": "ch03_the_first_verse"})
	assert_eq(causeway.requires_flag, &"ch02_saved_once")
	assert_false(battle.contains_point(zone.spawn_marker(&"BattleReturn").global_position), "returns beside it")
	assert_false(causeway.contains_point(zone.spawn_marker(&"CausewayHead").global_position), "arrives short of it")

	# The way up from the beach to the lane crosses the battle strip once Asha has been met.
	fired.clear()
	Game.set_flag(&"ch02_met_asha", false)
	Game.set_flag(&"ch02_tideline_won", false)
	zone.place_at(&"Beach")
	_walk(Vector3.LEFT, 3.0)
	assert_false(fired.has(&"tideline_battle"), "no battle before Cutscene A")
	Game.set_flag(&"ch02_met_asha", true)
	zone.place_at(&"Beach")
	_walk(Vector3.LEFT, 6.0)
	assert_eq(fired, [&"tideline_battle"] as Array[StringName], "the beach path starts the tideline battle")
	Game.set_flag(&"ch02_tideline_won", true)
	zone.place_at(&"Beach")
	_walk(Vector3.LEFT, 6.0)
	assert_eq(fired.size(), 1, "won once, it stays quiet")
	# M2-FP-05: an escape returns the party to BeforeBattle, on the beach side: clear of the strip,
	# and the way on to the village crosses it again.
	assert_false(battle.contains_point(zone.spawn_marker(&"BeforeBattle").global_position), "escape lands clear")
	Game.set_flag(&"ch02_tideline_won", false)
	fired.clear()
	zone.place_at(&"BeforeBattle", zone.spawn_yaw_deg(&"BeforeBattle"))
	_walk(Vector3.LEFT, 6.0)
	assert_eq(fired, [&"tideline_battle"] as Array[StringName], "from BeforeBattle the way on is the fight")
	# The causeway head waits for the first save.
	Game.set_flag(&"ch02_saved_once", false)
	zone.place_at(&"CausewayHead")
	_walk(Vector3.FORWARD, 2.5)
	assert_false(fired.has(&"causeway_head"))
	Game.set_flag(&"ch02_saved_once", true)
	zone.place_at(&"CausewayHead")
	_walk(Vector3.FORWARD, 2.5)
	assert_true(fired.has(&"causeway_head"), "the causeway head plays The First Verse")
	_done()


func test_the_cutscene_stage_resolves_cutscene_a() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	var stage := zone.get_node("CutsceneStage") as CutsceneStage
	for id in STAGE_SHOTS:
		var shot := stage.shot(id)
		assert_true(shot != null, "shot %s" % id)
		if shot != null:
			assert_eq(shot.id, id)
	assert_eq(stage.shot_ids(), STAGE_SHOTS)
	assert_between(stage.shot(&"H05").fov_deg, 37.7, 37.9, "35 mm")
	assert_between(stage.shot(&"H06").fov_deg, 26.9, 27.1, "50 mm")
	assert_eq(stage.shot(&"H01").position, Vector3(120.0, 8.0, -5.0), "the mood scene's H01")
	assert_true(stage.actor(&"asha") != null, "asha")
	assert_true(stage.actor(&"toma") != null, "toma")
	assert_true(stage.actor(&"rhen") == zone.get_node("Player"), "the player stands in for rhen")
	assert_true(stage.director() == zone.get_node("CameraDirector"))
	for id in STAGE_MARKS:
		assert_true(stage.mark(id) != null, "mark %s" % id)
	# Every cue target Cutscene A names resolves on this stage.
	var runner := DialogueRunner.new(DialogueFlagAccess.new())
	runner.forward_events_to_bus = false
	assert_true(runner.load_scene(&"ch02_girl_on_the_beach") and runner.start())
	var missing: Array[String] = []
	for _i in 400:
		var step := runner.next()
		if step.is_end():
			break
		if step.is_options():
			runner.choose(step.options[0].index)
		elif step.is_cue():
			_check_cue(stage, step, missing)
	assert_eq(missing, [] as Array[String], "every @camera/@anim/@mark/@vfx target is on the stage")
	# M2-FP-11: the zone leaves the mood sun's bias (1.0) alone; close shots use the key light instead.
	assert_eq(zone.face_key_shadow_normal_bias, 0.0)
	# M2-FP-10: the close shots of Asha key her with the mood sun's short-range copy; H01 does not.
	assert_true(stage.sun() == zone.get_node("HalunaMood").get(&"sun"), "the stage keys from the mood scene's sun")
	var key_cfg: Dictionary = CutsceneSequencer.load_config().get("key_light", {})
	for id: StringName in STAGE_SHOTS:
		# The rail root is the zone root, at the origin.
		var shot := stage.shot(id)
		var close := CutsceneKeyLight.is_close(shot.position, shot.look_at, shot.fov_deg, key_cfg)
		assert_eq(close, id not in [&"H01", &"H03"], "%s keyed: %s" % [id, close])  # the wides (H03: a roof gull)
	# The PC's FP-10 check: under the 74° noon sun the close shots lower the key 30°.
	for id: StringName in [&"H05", &"H06"]:
		assert_eq(stage.shot_node(id).key_pitch_deg, 30.0, "%s key pitch" % id)
	zone.free()
	zone = null


func test_the_barks_play_to_the_end() -> void:
	var speakers := DialogueSpeakers.load_default()
	for scene in BARKS:
		var runner := DialogueRunner.new(DialogueFlagAccess.new())
		runner.forward_events_to_bus = false
		assert_true(runner.load_scene(scene) and runner.start(), "loads %s" % scene)
		var lines := 0
		var rhen := 0
		var ended := false
		for _i in 50:
			var step := runner.next()
			if step.is_end():
				ended = true
				break
			assert_false(step.is_cue() and step.cue == &"camera", "%s: barks play on the field camera" % scene)
			if step.is_line():
				lines += 1
				rhen += 1 if step.speaker == &"rhen" else 0
				assert_true(speakers.has(step.speaker), "%s: speaker %s" % [scene, step.speaker])
		assert_true(ended, "%s ends" % scene)
		assert_between(lines, 2, 4, "%s is a bark" % scene)
		assert_eq(rhen, 1, "%s: Rhen answers once" % scene)


func test_the_registry_enters_the_playable_zone() -> void:
	var reg := LocationRegistry.load_default()
	assert_eq(reg.scene_of(LOCATION), ZONE)
	assert_true(reg.can_enter(LOCATION), "ch02/haluna is playable")
	assert_eq(reg.spawn_of(LOCATION), &"Shrine")
	assert_eq(
		reg.shrine_point(&"haluna_shrine"),
		{LocationRegistry.KEY_LOCATION: LOCATION, LocationRegistry.KEY_SPAWN: &"Shrine"}
	)


## M2-FP-05: the prebuild (what SceneRouter's worker thread runs at instantiate time) gives the same
## zone as building in the tree, and nothing is built twice when the prebuilt zone enters it. The
## runner is synchronous, so prebuild() is called here on the main thread; the threaded path itself
## is measured by the swap probe (README, "Entry hitch").
func test_the_prebuild_matches_the_in_tree_build() -> void:
	_load_into_tree()
	var built := _build_snapshot(zone)
	assert_false(zone.prebuilt, "a main-thread instance is not prebuilt")
	_done()

	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	assert_false(zone.prebuilt)
	zone.prebuild()
	assert_true(zone.prebuilt)
	var dresser := zone.get_node("HalunaMood/Dresser")
	assert_true(dresser is HalunaZoneDresser, "the dresser no longer dresses in _ready")
	var dressed := dresser.get_child_count()
	assert_true(dressed > 0, "dressed off the tree")
	assert_true((zone.get_node("Collision") as HalunaCollision).shape_count > 0, "collision built off the tree")
	print("    haluna prebuild: %d ms" % zone.prebuild_msec)
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	assert_eq(dresser.get_child_count(), dressed, "entering the tree dressed nothing again")
	var pre := _build_snapshot(zone)
	assert_eq(pre["shapes"], built["shapes"], "same shape count")
	assert_eq(pre["kinds"], built["kinds"], "same pieces given collision")
	assert_eq(pre["pieces"], built["pieces"], "same dressing")
	assert_eq(pre["terrain"], built["terrain"], "same terrain meshes")
	assert_true(pre["water_mesh"] and built["water_mesh"], "the sea has its grid")
	assert_between(float(pre["asha_y"]), float(built["asha_y"]) - 1e-4, float(built["asha_y"]) + 1e-4, "Asha posed")
	var a: Array = pre["xforms"]
	var b: Array = built["xforms"]
	var worst := 0.0
	for i in mini(a.size(), b.size()):
		worst = maxf(worst, ((a[i] as Transform3D).origin - (b[i] as Transform3D).origin).length())
	assert_true(worst < 1e-3, "every shape where the in-tree build put it (worst %.5f m)" % worst)
	assert_true(zone.place_at(&"Beach", zone.spawn_yaw_deg(&"Beach")))
	_done()


static func _build_snapshot(z: HalunaZone) -> Dictionary:
	var xforms: Array[Transform3D] = []
	for cs in z.collision.find_children("*", "CollisionShape3D", true, false):
		xforms.append((cs as CollisionShape3D).transform)
	var water := z.get_node("HalunaMood/Water") as WaterSurface
	var asha := z.stage.get_node("Actors/asha") as HalunaActorPose
	return {
		"shapes": z.collision.shape_count,
		"kinds": z.collision.kinds.duplicate(),
		"pieces": z.get_node("HalunaMood/Dresser").get_child_count(),
		"terrain": z.get_node("HalunaMood/Terrain").get_child_count(),
		"water_mesh": water.get_child_count(true) > 0,
		"asha_y": asha.model.position.y if asha.model != null else INF,
		"xforms": xforms,
	}


## The floor under a point: where Rhen's capsule lands when dropped from 1 m above it (a shape cast
## with the real body; ray queries see runtime-built shapes only after a physics step).
func _floor_y(p: Vector3) -> float:
	var body := zone.player
	var saved := body.global_transform
	body.global_position = p + Vector3.UP * 1.0
	var hit := body.move_and_collide(Vector3.DOWN * 4.0, true)
	var y := (body.global_position + hit.get_travel()).y if hit != null else -INF
	body.global_transform = saved
	return y


## Rhen is in front of the camera and inside its frame.
func _assert_framed(where: String) -> void:
	zone.director.update(DT)
	var cam := zone.field_camera
	var head := zone.player.global_position + Vector3.UP * 1.0
	assert_false(
		cam.is_position_behind(head), "Rhen is in front of the camera %s (%s)" % [where, zone.director.active_shot_id()]
	)
	var size := Vector2(1920.0, 1080.0)
	var dir := cam.global_basis.inverse() * (head - cam.global_position)
	if dir.z >= 0.0:
		return
	var half_v := tan(deg_to_rad(cam.fov) * 0.5)
	var ndc := Vector2(dir.x / -dir.z / (half_v * size.x / size.y), dir.y / -dir.z / half_v)
	assert_true(absf(ndc.x) < 1.0 and absf(ndc.y) < 1.0, "Rhen is on screen %s (ndc %s)" % [where, ndc])


func _walk_from(spawn: StringName, world_dir: Vector3, seconds: float) -> void:
	zone.place_at(spawn, zone.spawn_yaw_deg(spawn))
	var start := zone.player.global_position
	_walk(world_dir, seconds)
	var p := zone.player.global_position
	var moved := Vector2(p.x - start.x, p.z - start.z).length()
	assert_true(moved > 2.0, "walked from %s (%.1f m)" % [spawn, moved])
	assert_true(zone.player.grounded(), "on the ground after walking from %s" % spawn)
	assert_between(p.y, _floor_y(p) - 0.15, _floor_y(p) + 0.15, "not through the floor near %s" % spawn)
	_assert_framed("walking from %s" % spawn)


## Holds the stick so Rhen walks along `world_dir` under the live camera.
func _walk(world_dir: Vector3, seconds: float) -> void:
	var d := Vector3(world_dir.x, 0.0, world_dir.z).normalized()
	for _i in int(seconds / DT):
		var basis := Basis(Vector3.UP, zone.director.camera_yaw())
		var forward := basis * Vector3.FORWARD
		var right := basis * Vector3.RIGHT
		zone.player.input_override = Vector2(d.dot(right), -d.dot(forward))
		zone.player.step(DT)
		zone.director.update(DT)
	zone.player.input_override = Vector2.ZERO
	zone.player.step(DT)


## An offset from a villager to a free spot within their listening sphere (toward the camera side).
func _beside(it: Interactable) -> Vector3:
	var shape := it.get_child(0) as CollisionShape3D
	var r := (shape.shape as SphereShape3D).radius if shape != null else 1.0
	return Vector3(0.0, 0.0, minf(0.9, r * 0.5))


func _check_cue(stage: CutsceneStage, step: DialogueStep, missing: Array[String]) -> void:
	var first := str(step.args[0]) if not step.args.is_empty() else ""
	match step.cue:
		&"camera":
			if not step.is_camera_release() and stage.shot(StringName(first)) == null:
				missing.append("shot " + first)
		&"anim", &"mark", &"face":
			if stage.actor(StringName(first)) == null:
				missing.append("actor " + first)
			if step.cue == &"mark" and stage.mark(StringName(str(step.args[1]))) == null:
				missing.append("mark " + str(step.args[1]))
		&"vfx":
			var at := str(step.kwargs.get("at", ""))
			if at != "" and stage.place(StringName(at)) == null:
				missing.append("place " + at)


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func test_asha_faces_her_roots_forward() -> void:
	# hero-integration's catch: her glTF model faces +Z, but the cutscene sequencer turns an actor's
	# root -Z toward a target, so a look_at or @mark left her back to it. The Model child turns 180
	# degrees and the root compensates (her pose and placement are unchanged in the world).
	_load_into_tree()
	var asha := zone.get_node("CutsceneStage/Actors/asha") as Node3D
	var model := asha.get_node("Model") as Node3D
	var face := model.global_basis.z.normalized()  # glTF forward
	assert_true(face.dot(-asha.global_basis.z.normalized()) > 0.99, "her face is her root's forward")
	_done()
