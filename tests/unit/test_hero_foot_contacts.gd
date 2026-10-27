extends TestCase
## M3-AUD-810: HeroFootContacts, the footfalls a clip's foot_l_down / foot_r_down markers mark, and
## HeroFieldActor.foot_contact, the signal audio's footsteps listen to.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const DT := 1.0 / 60.0
const WALK_FRAMES := 150

var c: HeroFootContacts


func before_each() -> void:
	c = HeroFootContacts.new(HeroFieldActor.field_data()["foot_contacts"] as Dictionary)


func test_markers_name_the_feet() -> void:
	assert_eq(c.foot_of(&"foot_l_down"), HeroFootContacts.LEFT)
	assert_eq(c.foot_of(&"foot_r_down_2"), HeroFootContacts.RIGHT, "a repeat (_2) is the same foot")
	assert_eq(c.foot_of(&"contact"), &"", "other markers are not footfalls")


func test_crossing_reports_each_foot_once_in_order() -> void:
	var a := _cycle(1.0)
	assert_eq(c.crossed(a, 0.0, 0.2), [HeroFootContacts.LEFT] as Array[StringName])
	assert_eq(c.crossed(a, 0.2, 0.4), [] as Array[StringName], "no marker between")
	assert_eq(c.crossed(a, 0.0, 0.9), [HeroFootContacts.LEFT, HeroFootContacts.RIGHT] as Array[StringName])


func test_a_loop_wrap_counts_the_markers_on_both_sides() -> void:
	var a := _cycle(1.0)
	var feet := c.crossed(a, 0.8, 0.15)
	assert_eq(feet, [HeroFootContacts.LEFT] as Array[StringName], "0.8 -> wrap -> 0.15 crosses the left at 0.1")
	assert_eq(c.crossed(a, 0.55, 0.15), [HeroFootContacts.RIGHT, HeroFootContacts.LEFT] as Array[StringName])


func test_a_new_clip_does_not_replay_a_footfall() -> void:
	var a := _cycle(1.0)
	assert_eq(c.step(&"walk", a, 0.5), [] as Array[StringName], "the first frame of a clip only anchors")
	assert_eq(c.step(&"walk", a, 0.7), [HeroFootContacts.RIGHT] as Array[StringName])
	assert_eq(c.step(&"run", a, 0.65), [] as Array[StringName], "a switch to another clip re-anchors")
	assert_true(c.is_run(&"run") and c.is_run(&"run_stop") and not c.is_run(&"walk"))


func test_the_field_body_emits_alternating_footfalls_while_walking() -> void:
	var zone := (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	var player := zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	var body := player.get_node_or_null(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
	assert_true(body != null, "the player has a hero body")
	if body == null:
		zone.free()
		return
	var walk := body.tree.get_animation(&"walk")
	var added := _ensure_markers(walk)
	var feet: Array[StringName] = []
	var runs: Array[bool] = []
	body.foot_contact.connect(
		func(foot: StringName, run: bool) -> void:
			feet.append(foot)
			runs.append(run)
	)
	body.snap()
	for i in WALK_FRAMES:
		player.global_position += Vector3(0.0, 0.0, -body.loco.walk_clip_mps * DT)
		body.advance(DT)
	for m in added:
		walk.remove_marker(m)
	assert_true(
		feet.size() >= 2, "a walk of %d frames touches down at least twice (got %d)" % [WALK_FRAMES, feet.size()]
	)
	for i in range(1, feet.size()):
		assert_ne(feet[i], feet[i - 1], "feet alternate")
	assert_false(true in runs, "walk steps are not run steps")
	zone.free()


## A 1 s loop with the left foot down at 0.1 and the right at 0.6.
func _cycle(length: float) -> Animation:
	var a := Animation.new()
	a.length = length
	a.loop_mode = Animation.LOOP_LINEAR
	a.add_marker(&"foot_l_down", 0.1)
	a.add_marker(&"foot_r_down", 0.6)
	return a


## Our branch's walk has no footfall markers until characters' M2-CHR-12 merges: add a pair for the test and
## return them so the test can take them off again. With the real markers present it adds nothing.
func _ensure_markers(a: Animation) -> Array[StringName]:
	var added: Array[StringName] = []
	for m: StringName in a.get_marker_names():
		if c.foot_of(m) != &"":
			return added
	for pair: Array in [[&"foot_l_down", 0.1], [&"foot_r_down", 0.5]]:
		a.add_marker(pair[0] as StringName, a.length * float(pair[1]))
		added.append(pair[0] as StringName)
	return added


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
