extends TestCase
## M3-RND-03: RevenantTells. Engaging puts the actor's meshes on the still layer, takes him off the key's
## shadow casters and adds the cancelling spot pair; the capsule reaches the still-actor globals; disengaging
## puts everything back. (The look itself: revenant_tells_* shots, viewed on the PC.)

const EPS := 0.001

var root: Node3D
var key: DirectionalLight3D
var actor: Node3D
var mesh: MeshInstance3D
var tells: RevenantTells


func before_each() -> void:
	root = Node3D.new()
	root.name = "RevenantFixture"
	_host().add_child(root)
	key = DirectionalLight3D.new()
	key.name = "Key"
	key.shadow_enabled = true
	key.light_energy = 2.4
	key.light_color = Color(1.0, 0.7, 0.5)
	root.add_child(key)
	key.look_at_from_position(Vector3(0, 4, 0), Vector3(1, 0, -1))
	actor = Node3D.new()
	actor.name = "Sefir"
	root.add_child(actor)
	actor.position = Vector3(2, 0, 1)
	mesh = MeshInstance3D.new()
	var capsule := CapsuleMesh.new()
	capsule.radius = 0.3
	capsule.height = 1.8
	mesh.mesh = capsule
	mesh.position = Vector3(0, 0.9, 0)
	mesh.layers = 1
	actor.add_child(mesh)
	tells = _tells(actor, [key])


func _tells(target: Node3D, keys: Array, shadow: bool = true) -> RevenantTells:
	var t := RevenantTells.new()
	t.sharp_shadow = shadow
	root.add_child(t)
	t.actor_path = t.get_path_to(target)
	var paths: Array[NodePath] = []
	for k: DirectionalLight3D in keys:
		paths.append(t.get_path_to(k))
	t.lights = paths
	t.engage()
	return t


## The runner has no teardown: every test ends here.
func _free() -> void:
	root.free()


func test_the_actor_joins_the_still_layer_and_leaves_the_keys_casters() -> void:
	var still := tells.still_mask()
	assert_eq(mesh.layers, 1 | still, "the actor keeps his layer and joins the still one")
	assert_eq(key.shadow_caster_mask & still, 0, "the key no longer casts the actor")
	var full := DirectionalLight3D.new()
	assert_eq(key.shadow_caster_mask | still, full.shadow_caster_mask, "the key still casts everything else")
	full.free()
	_free()


func test_a_cancelling_pair_of_spots_stands_in_for_the_key() -> void:
	assert_eq(tells.pairs.size(), 1)
	var sharp := tells.pairs[0][2] as SpotLight3D
	var cancel := tells.pairs[0][3] as SpotLight3D
	assert_false(sharp.light_negative, "the shadowed spot adds light")
	assert_true(sharp.shadow_enabled)
	assert_eq(sharp.shadow_caster_mask, tells.still_mask(), "it shadows the actor only")
	assert_true(sharp.shadow_blur < key.shadow_blur, "its shadow is sharper than the key's")
	assert_true(cancel.light_negative, "its twin takes the same light away")
	assert_false(cancel.shadow_enabled)
	for s: SpotLight3D in [sharp, cancel]:
		assert_eq(s.light_color, key.light_color)
		assert_eq(s.light_energy, sharp.light_energy, "the pair cancels exactly")
		assert_true(s.light_energy >= key.light_energy, "the range window is compensated")
		assert_eq(s.light_cull_mask, key.light_cull_mask)
	_free()


func test_the_spots_sit_up_the_keys_direction_and_aim_at_the_actor() -> void:
	var sharp := tells.pairs[0][2] as SpotLight3D
	var dist := float(tells.config.get("spot_distance_m", 0.0))
	var to_spot := sharp.global_position - actor.global_position
	assert_between(to_spot.length(), dist - 2.0, dist + 2.0, "spot_distance_m from the actor")
	assert_between(to_spot.normalized().dot(key.global_basis.z.normalized()), 0.999, 1.001, "along the key")
	var aim := -sharp.global_basis.z.normalized()
	assert_between(aim.dot(-to_spot.normalized()), 0.999, 1.001, "the cone points at the actor")
	_free()


func test_the_capsule_reaches_the_still_actor_globals() -> void:
	assert_eq(tells.slot, 0)
	var c: Vector4 = ShaderGlobals.get_value(RevenantTells.SLOT_GLOBALS[0], Vector4.ZERO)
	assert_between(c.x, 2.0 - EPS, 2.0 + EPS, "base under the actor")
	assert_between(c.z, 1.0 - EPS, 1.0 + EPS)
	assert_between(c.y, -0.1, 0.0, "base at his feet, padded")
	assert_between(c.w, 0.3, 0.4, "radius from the mesh, padded")
	var h: Vector2 = ShaderGlobals.get_value(RevenantTells.HEIGHTS_GLOBAL, Vector2.ZERO)
	assert_between(h.x, 1.8, 2.0, "height from the mesh, padded")
	actor.position = Vector3(-3, 0, 0)
	tells._process(0.0)
	c = ShaderGlobals.get_value(RevenantTells.SLOT_GLOBALS[0], Vector4.ZERO)
	assert_between(c.x, -3.0 - EPS, -3.0 + EPS, "the capsule follows him")
	_free()


func test_disengage_puts_everything_back() -> void:
	var caster := key.shadow_caster_mask | tells.still_mask()
	var sharp := tells.pairs[0][2] as SpotLight3D
	tells.disengage()
	assert_eq(mesh.layers, 1)
	assert_eq(key.shadow_caster_mask, caster)
	assert_true(sharp.is_queued_for_deletion())
	assert_eq(tells.slot, -1)
	var c: Vector4 = ShaderGlobals.get_value(RevenantTells.SLOT_GLOBALS[0], Vector4.ONE)
	assert_eq(c.w, 0.0, "the slot's radius is back to 0 (free)")
	_free()


func test_each_tell_switches_off_on_its_own() -> void:
	tells.disengage()
	tells.still_reflection = false
	tells.engage()
	assert_eq(tells.slot, -1, "no capsule without the reflection")
	assert_eq(tells.pairs.size(), 1)
	tells.still_reflection = true
	tells.sharp_shadow = false
	tells.engage()
	assert_true(tells.pairs.is_empty(), "no spots without the shadow")
	assert_eq(key.shadow_caster_mask & tells.still_mask(), tells.still_mask(), "the key casts him again")
	assert_eq(tells.slot, 0)
	_free()


func test_two_still_actors_take_the_two_slots_and_a_third_ripples() -> void:
	var others: Array[RevenantTells] = []
	for i in 2:
		var a := Node3D.new()
		root.add_child(a)
		others.append(_tells(a, [], false))
	assert_eq(others[0].slot, 1)
	assert_eq(others[1].slot, -1, "no slot left: his reflection ripples like anyone's")
	_free()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
