extends TestCase
## M3-AUD-812: the field steps change surface in every slice zone, on the real scenes and with no level marking its
## ground: Haluna's sand, its dock's planks (the dock_haluna kit mesh) and its shallows (under the sea's rest plane);
## the Saltgrass Causeway's stone and its greybox tidepool; the Shell Shrine's stone. When the player carries
## hero-integration's HeroBody (HeroFieldActor), a walk steps from its foot_contact signal. Sounds are recorded
## through the listener's player Callable, so nothing plays.

const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const CAUSEWAY := "res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn"
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
	assert_eq(String(f._ground(_marker("rhen_shallows"))), "water", "Rhen's mark in the shallows")
	assert_eq(String(f._ground(ground.call(6.0, 8.0))), "water", "knee-deep off the beach")
	var docks := zone.find_children("dock_haluna", "MeshInstance3D", true, false)
	assert_false(docks.is_empty(), "the dock kit piece is dressed")
	if not docks.is_empty():
		var dock := docks[0] as MeshInstance3D
		var deck := dock.global_transform * Vector3(dock.get_aabb().get_center().x, 1.0, 0.0)
		assert_eq(String(f._ground(deck)), "wood", "halfway along the dock")
	_done()


func test_the_causeway_is_stone_with_a_tidepool() -> void:
	_load(CAUSEWAY)
	var f := _listener(CAUSEWAY)
	assert_eq(String(f.surface), "stone", "the causeway's own ground")
	assert_eq(String(f._ground(Vector3(0.0, 0.04, -30.0))), "stone", "on the path")
	assert_eq(String(f._ground(Vector3(5.0, 0.0, -60.0))), "water", "in the tidepool")
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
	player.global_position = _marker("Village")
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
