extends TestCase
## M2-UI-07: FighterStandIn instances a hero actor scene when its spec names one ("scene"), keeps
## the ring, the head position and the flinch, plays "idle", and shows Petrify and KO on every
## surface; a missing scene falls back to the primitive. A tiny test actor stands in for the
## characters track's battle-scale heroes (tests/fixtures/battle_actor/test_actor.tscn).

const ACTOR := "res://tests/fixtures/battle_actor/test_actor.tscn"
const RING := {"radius_factor": 1.4, "inner_soft_m": 0.25, "notches": 6}

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_a_scene_spec_shows_the_actor_instead_of_the_primitive() -> void:
	var f := _stand_in({"scene": ACTOR, "height": 1.6, "hover": 0.1, "yaw_deg": 180.0, "radius": 0.3})
	assert_true(f.has_actor())
	assert_eq(f.actor().get_meta(&"hymn_battle_actor"), &"test")
	assert_true(f.find_children("*", "MeshInstance3D", true, false).size() == 3, "two actor surfaces and the ring")
	assert_true(is_equal_approx(f.actor().position.y, 0.1), "its feet on the ground at hover")
	assert_true(is_equal_approx(f.actor().rotation_degrees.y, 180.0), "turned by yaw_deg")
	assert_true(is_equal_approx(f.head_position().y, 1.7), "the head still comes from the spec's height")
	var player := f.actor().find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	assert_eq(StringName(player.current_animation), FighterStandIn.IDLE_CLIP, "idle plays while it waits")
	f.set_ring(FighterStandIn.RING_ALLY, Color.WHITE)
	assert_true(f.ring_mode_visible(), "the ring is kept")


func test_petrify_and_ko_reach_every_surface() -> void:
	var f := _stand_in({"scene": ACTOR, "height": 1.6})
	var surfaces: Array[MeshInstance3D] = []
	for n in f.actor().find_children("*", "MeshInstance3D", true, false):
		surfaces.append(n as MeshInstance3D)
	f.set_stone(true, Color(0.5, 0.5, 0.5), 0.9)
	assert_true(f.is_stone())
	for m in surfaces:
		var mat := m.material_override as StandardMaterial3D
		assert_true(mat != null and mat.albedo_color == Color(0.5, 0.5, 0.5), "stone on %s" % m.name)
	f.set_stone(false, Color.BLACK, 1.0)
	for m in surfaces:
		assert_true(m.material_override == null, "its own materials back")
	f.set_ko(true, 0.4, 0.35)
	assert_true(is_equal_approx(f.actor().position.y, -0.4), "sinks")
	for m in surfaces:
		assert_true(is_equal_approx(m.transparency, 0.65), "fades")
	f.set_ko(false, 0.4, 0.35)
	assert_true(is_equal_approx(f.actor().position.y, 0.0))
	for m in surfaces:
		assert_eq(m.transparency, 0.0)


func test_an_actor_with_a_ko_clip_does_not_sink() -> void:
	var f := _stand_in({"scene": ACTOR, "height": 1.6})
	var player := BattleClips.player_of(f)
	player.get_animation_library(&"").add_animation(BattleClips.KO, Animation.new())
	f.set_ko(true, 0.4, 0.35)
	assert_true(is_equal_approx(f.actor().position.y, 0.0), "the KO clip lays it down; no sink through the floor")
	for n in f.actor().find_children("*", "MeshInstance3D", true, false):
		assert_true(is_equal_approx((n as MeshInstance3D).transparency, 0.65), "it still fades")


func test_a_missing_scene_falls_back_to_the_primitive() -> void:
	var f := _stand_in({"scene": "res://no/such_actor.tscn", "height": 1.6, "shape": "box"})
	assert_false(f.has_actor())
	assert_true(f.find_children("*", "MeshInstance3D", true, false).size() == 2, "the box and the ring")
	f.set_ko(true, 0.4, 0.35)  # the primitive path still works
	f.set_stone(true, Color.GRAY, 1.0)
	assert_true(f.is_stone())


func test_a_plain_spec_is_unchanged() -> void:
	var f := _stand_in({"height": 1.6, "radius": 0.3})
	assert_false(f.has_actor())
	assert_true(is_equal_approx(f.head_position().y, 1.6))


func _stand_in(spec: Dictionary) -> FighterStandIn:
	var f := FighterStandIn.new()
	f.setup(&"tester#1", spec, RING)
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(f)
	made.append(f)
	return f
