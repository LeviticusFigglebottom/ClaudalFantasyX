extends TestCase
## M3-AUD-812: the field steps change surface in every slice zone, on the real scenes and with no level marking its
## ground: Haluna's sand, its dock's planks (the dock_haluna kit mesh) and its shallows (under the sea's rest plane);
## the Saltgrass Causeway's stone slabs over its sand flats and the sea between them, and its tide pool
## (env-art's final route, M2-FP-108); the Shell Shrine's stone. When the player carries
## hero-integration's HeroBody (HeroFieldActor), a walk steps from its foot_contact signal. Sounds are recorded
## through the listener's player Callable, so nothing plays.

const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const CAUSEWAY := "res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn"
const TIDEPOOL := Vector3(64.69, -0.85, -22.96)
const SHRINE := "res://game/levels/ch03/shell_shrine/shell_shrine.tscn"
const DT := 1.0 / 60.0
## Frames of walking for the hero-body check (3 s).
const WALK_FRAMES := 180

var played: Array = []
var saved_state: GameStateData
var zone: Node3D


func before_each() -> void:
	played = []
	saved_state = Game.state
	Game.state = GameStateData.new()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _load(path: String) -> Node3D:
	zone = (load(path) as PackedScene).instantiate() as Node3D
	if zone is ShellShrineLevel:
		(zone as ShellShrineLevel).autostart = false
		(zone as ShellShrineLevel).hand_off = func(_target: String) -> void: pass
	_host().add_child(zone)
	var director := zone.find_child("CameraDirector", true, false)
	if director != null:
		director.set(&"auto_update", false)
	var player := _player()
	if player != null:
		player.set_physics_process(false)
		player.set_process_unhandled_input(false)
	return zone


func _player() -> Node3D:
	return zone.find_child("Player", true, false) as Node3D


func _done() -> void:
	if zone != null:
		_host().remove_child(zone)
		zone.free()
		zone = null
	Game.state = saved_state


func _listener(path: String) -> FootstepAudio:
	var f := FootstepAudio.new((AudioData.table(AudioData.FOOTSTEPS) as Dictionary).duplicate(true))
	f.player = func(id: StringName, at: Vector3, opts: Dictionary) -> void: played.append([id, at, opts])
	zone.add_child(f)
	f.attach(_player(), path)
	return f


func _marker(name: String) -> Vector3:
	var m := zone.find_child(name, true, false) as Node3D
	assert_true(m != null, "%s is in the zone" % name)
	return m.global_position if m != null else Vector3.ZERO


func test_haluna_is_sand_with_a_wooden_dock_and_shallows() -> void:
	_load(HALUNA)
	var f := _listener(HALUNA)
	var terrain := zone.find_children("*", "HalunaTerrain", true, false)
	assert_false(terrain.is_empty(), "the zone has its terrain")
	var ground := func(x: float, z: float) -> Vector3: return Vector3(x, float(terrain[0].call("height_at", x, z)), z)
	assert_eq(String(f._ground(_marker("Village"))), "sand", "the village spawn")
	assert_eq(String(f._ground(ground.call(-12.0, 8.0))), "sand", "the dry beach above the waterline")
	# The Lead's beach re-stage (93d0741e) moved Rhen's marks 3 m up the beach, where the wash is a film: sand there.
	assert_eq(String(f._ground(ground.call(2.5, 8.0))), "water", "the shallows")
	assert_eq(String(f._ground(ground.call(6.0, 8.0))), "water", "knee-deep off the beach")
	var docks := zone.find_children("dock_haluna", "MeshInstance3D", true, false)
	assert_false(docks.is_empty(), "the dock kit piece is dressed")
	if not docks.is_empty():
		var dock := docks[0] as MeshInstance3D
		var deck := dock.global_transform * Vector3(dock.get_aabb().get_center().x, 1.0, 0.0)
		assert_eq(String(f._ground(deck)), "wood", "halfway along the dock")
	_done()


func test_the_causeway_is_stone_slabs_over_sand_flats_and_the_sea() -> void:
	_load(CAUSEWAY)
	var f := _listener(CAUSEWAY)
	assert_eq(String(f.surface), "sand", "the flats are the causeway's own ground")
	var slabs := zone.find_children("causeway_slab_flat", "MeshInstance3D", true, false)
	assert_true(slabs.size() > 10, "env-art's final route is dressed (%d slabs)" % slabs.size())
	var slab := slabs[0] as MeshInstance3D
	var aabb := slab.get_aabb()
	var top := slab.global_transform * (aabb.get_center() + Vector3(0.0, aabb.size.y * 0.5, 0.0))
	assert_eq(String(f._ground(top)), "stone", "on a slab of the path")
	var off := top + Vector3(0.0, 0.0, 6.0)
	assert_eq(String(f._ground(Vector3(off.x, 0.0, off.z))), "sand", "off the path, on the flats")
	assert_eq(String(f._ground(Vector3(off.x, -0.9, off.z))), "water", "down in the sea (under its rest plane)")
	# M2-FP-108's final route: the tide pools lie off the railed path, under the sea that fills them (env-art's
	# first pool, as the wildlife file's tidepool shoal places it), so a foot in one wades.
	assert_eq(String(f._ground(TIDEPOOL)), "water", "in the tidepool")
	_done()


func test_the_shrine_is_stone() -> void:
	_load(SHRINE)
	var f := _listener(SHRINE)
	assert_eq(String(f._ground(_marker("Entry"))), "stone", "the entry")
	_done()


## Runs only once hero-integration's HeroFieldActor is on the player (it is on claude/hero-integration).
func test_a_walk_in_haluna_steps_from_the_hero_bodys_foot_contacts() -> void:
	_load(HALUNA)
	var player := _player()
	var body := player.get_node_or_null(^"HeroBody") as Node3D
	if body == null or not body.has_signal(&"foot_contact") or not body.has_method(&"advance"):
		assert_true(true, "no hero body on this branch yet")
		_done()
		return
	var f := _listener(HALUNA)
	var added := _ensure_markers(body)
	body.call(&"snap")
	# _load turns the controller's physics off, so it never measures its floor: stand it on the sand.
	player.set(&"_grounded", true)
	player.global_position = _marker("Village")
	# The test runs no physics, so the controller never lands; contacts off the ground are rightly ignored. The
	# floor would set this on the first step in play.
	player.set(&"_grounded", true)
	for i in WALK_FRAMES:
		player.global_position += Vector3(0.0, 0.0, -1.0 * DT)
		body.call(&"advance", DT)
		f.advance(DT)
	for pair: Array in added:
		(pair[0] as Animation).remove_marker(pair[1] as StringName)
	assert_eq(f.contact_source, &"signal", "foot_contact is the step source")
	var steps := played.filter(func(p: Array) -> bool: return String(p[0]).begins_with("hero_step_sand_"))
	assert_true(steps.size() >= 3, "a 3 s walk on the sand steps (%d)" % steps.size())
	_done()


## Runs only with hero-integration's HeroFieldActor. Its clips have no footfall markers until characters' M2-CHR-12
## lands, so the body never emits: after stall_m the listener must step by distance, not once per stall_m.
func test_a_hero_body_without_footfall_markers_still_walks_at_stride() -> void:
	_load(HALUNA)
	var player := _player()
	var body := player.get_node_or_null(^"HeroBody") as Node3D
	if body == null or not body.has_signal(&"foot_contact") or not body.has_method(&"advance"):
		assert_true(true, "no hero body on this branch yet")
		_done()
		return
	var f := _listener(HALUNA)
	body.call(&"snap")
	player.global_position = _marker("Village")
	player.set(&"_grounded", true)  # no physics in tests (see above)
	for i in WALK_FRAMES * 2:  # 6 m at 1 m/s
		player.global_position += Vector3(0.0, 0.0, -1.0 * DT)
		body.call(&"advance", DT)
		f.advance(DT)
	var steps := played.filter(func(p: Array) -> bool: return String(p[0]).begins_with("hero_step_"))
	assert_true(steps.size() >= 8, "6 m of walking steps at about walk_step_m (%d)" % steps.size())
	_done()


## The walk clip may have no footfall markers until characters' M2-CHR-12 merges: add a pair for the test and
## return them to take off again ([[animation, marker], ...]).
func _ensure_markers(body: Node3D) -> Array:
	var out: Array = []
	var tree := body.get(&"tree") as AnimationTree
	if tree == null or not tree.has_animation(&"walk"):
		return out
	var walk := tree.get_animation(&"walk")
	for m: Array in [[&"foot_l_down", 0.1], [&"foot_r_down", 0.6]]:
		if not walk.has_marker(m[0] as StringName):
			walk.add_marker(m[0] as StringName, minf(float(m[1]), walk.length * 0.9))
			out.append([walk, m[0]])
	return out
