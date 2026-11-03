extends TestCase
## FAST-TRACK (the human's 2026-11-03 playtest): "the walk animation stops playing for the main character
## randomly": Rhen slides with no walk cycle. The cause was a cutscene clip left on the field body: a line's
## `talk` (a loop) that an overheard bark, an auto-advanced or a skipped line never sends back to idle, or a
## held pose (kneel, spear_level) at a scene's end. A loop or a held clip stayed until the next play_clip, and
## it held the gait off, so the player walked a talking or kneeling Rhen across the field.
## HeroFieldActor now lets the player's stick take the body back to locomotion, and lets any body that travels
## at walking pace drop a loop nobody asked it to hold. These walk the real Rhen through the paths the playtest
## named (a bark mid-walk, a held pose after a scene, stop and start, reversals, a teleport) and check that the
## walk cycle shows and that his legs swing.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const DT := 1.0 / 60.0
const SETTLE_FRAMES := 90
const WALK_FRAMES := 60
const UP := Vector2(0, -1)
const DOWN := Vector2(0, 1)
const LEFT := Vector2(-1, 0)
const RIGHT := Vector2(1, 0)
## The walk shows when the blend gives the walk and run at least this much weight.
const MIN_GAIT_WEIGHT := 0.5
## Over a second of walking a thigh swings through at least this many degrees.
const MIN_SWING_DEG := 15.0
const THIGH := "DEF-thigh.L"

var zone: Node3D
var player: FieldController
var _party_was: Array[StringName] = []


func before_each() -> void:
	_party_was = Game.state.party_ids.duplicate()
	Game.state.party_ids.clear()
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	player = zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)


func test_a_line_s_talk_left_on_rhen_gives_way_to_the_walk() -> void:
	var body := _body()
	# What an overheard bark does to its speaker (CutsceneSequencer._line, auto_advance): talk, and no idle after.
	assert_true(HeroMotion.play(player, &"talk", 0.1), "the line's talk plays on the body")
	_still(body, SETTLE_FRAMES)
	assert_eq(body.action, &"talk", "standing, the talk stays (a loop)")
	player.input_override = UP
	_steps(body, WALK_FRAMES)
	assert_eq(body.action, &"", "the stick takes the body back to its locomotion")
	_assert_walking(body, "after a bark")
	_done()


func test_a_held_pose_at_a_scene_s_end_stands_up_when_the_player_walks() -> void:
	var body := _body()
	var clip := _held_clip(body)
	assert_true(clip != &"", "Rhen has a hold clip")
	assert_true(body.play_clip(clip, 0.1, true), "a scene leaves him held in '%s'" % clip)
	_still(body, SETTLE_FRAMES)
	assert_eq(body.action, clip, "with no input the pose holds")
	player.accepts_input = false
	player.input_override = UP
	_steps(body, SETTLE_FRAMES)
	assert_eq(body.action, clip, "a player whose input is held (a scene running) keeps the pose")
	player.accepts_input = true
	_steps(body, WALK_FRAMES)
	assert_eq(body.action, &"", "the player's own walk stands him up")
	_assert_walking(body, "after a held pose")
	_done()


func test_a_follower_left_talking_walks_when_it_trails() -> void:
	var body := _body()
	var anchor := Node3D.new()  # a source that cannot tell its intent: a follower's anchor, a stage root
	zone.add_child(anchor)
	anchor.global_position = player.global_position
	body.bind(anchor)
	assert_true(body.play_clip(&"talk", 0.1))
	for i in SETTLE_FRAMES:
		body.advance(DT)
	assert_eq(body.action, &"talk")
	var speed := body.loco.walk_clip_mps
	for i in WALK_FRAMES:
		anchor.global_position += Vector3(0.0, 0.0, -speed * DT)
		body.advance(DT)
	assert_eq(body.action, &"", "travelling at a walk drops a loop nobody holds")
	assert_true(_gait_weight(body) >= MIN_GAIT_WEIGHT, "the walk shows")
	var held := _held_clip(body)
	assert_true(body.play_clip(held, 0.1, true), "a held clip")
	for i in WALK_FRAMES:
		anchor.global_position += Vector3(0.0, 0.0, -speed * DT)
		body.advance(DT)
	assert_eq(body.action, held, "a scene's explicit hold glides (a stand-in mark) and stays")
	_done()


func test_stop_start_and_reversals_always_show_the_walk_while_he_travels() -> void:
	var body := _body()
	zone.call("place_at", &"Court")
	body.snap()
	var pattern: Array[Vector2] = [UP, Vector2.ZERO, UP, LEFT, Vector2.ZERO, DOWN, RIGHT, UP, Vector2.ZERO, DOWN]
	var lengths: Array[int] = [40, 6, 25, 30, 20, 45, 12, 35, 3, 50]
	var bad := 0
	var checked := 0
	for k in pattern.size():
		player.input_override = pattern[k]
		for i in lengths[k]:
			_step(body)
			if pattern[k] != Vector2.ZERO and i >= 20:  # past the start: the walk has to show
				checked += 1
				if not _shows_gait(body):
					bad += 1
	assert_true(checked > 0)
	assert_eq(bad, 0, "%d of %d travelling frames showed no walk" % [bad, checked])
	_done()


func test_a_teleport_mid_walk_keeps_the_walk() -> void:
	var body := _body()
	player.input_override = UP
	_steps(body, WALK_FRAMES)
	player.global_position += Vector3(10.0, 0.0, 0.0)  # a door, a stair landing, a zone spawn
	_steps(body, WALK_FRAMES)
	_assert_walking(body, "after a teleport")
	_done()


## The walk shows (the blend or a start or stop clip) and the thigh swings over a second of it.
func _assert_walking(body: HeroFieldActor, why: String) -> void:
	assert_true(
		_shows_gait(body), "%s: the gait shows (weight %.2f, clip '%s')" % [why, _gait_weight(body), _shown(body)]
	)
	var skel := HeroMotion.skeleton_of(body.model)
	var bone := skel.find_bone(THIGH)
	assert_true(bone >= 0, "Rhen has %s" % THIGH)
	var lo := INF
	var hi := -INF
	for i in WALK_FRAMES:
		_step(body)
		var q := skel.get_bone_pose_rotation(bone)
		var pitch := rad_to_deg(q.get_euler().x)
		lo = minf(lo, pitch)
		hi = maxf(hi, pitch)
	assert_true(hi - lo >= MIN_SWING_DEG, "%s: the thigh swings %.1f deg (>= %.1f)" % [why, hi - lo, MIN_SWING_DEG])


## True when the body shows a gait: the locomotion blend weighted to the walk or run, or a start or stop clip.
func _shows_gait(body: HeroFieldActor) -> bool:
	if body.action != &"":
		return false
	if body.gait != null and body.gait.clip != &"":
		var p := body.gait.phase
		return p == HeroGaitClips.Phase.START or p == HeroGaitClips.Phase.STOP
	return _gait_weight(body) >= MIN_GAIT_WEIGHT


func _gait_weight(body: HeroFieldActor) -> float:
	var w := body.gait_weights()
	return w[1] + w[2]


func _shown(body: HeroFieldActor) -> StringName:
	if body.action != &"":
		return body.action
	return body.gait.clip if body.gait != null else &""


## A hold clip (sequencer.json hold_clips) Rhen's model has.
func _held_clip(body: HeroFieldActor) -> StringName:
	var cfg := JSON.parse_string(FileAccess.get_file_as_string("res://game/data/cutscene/sequencer.json")) as Dictionary
	for c: Variant in cfg.get("hold_clips", []):
		if body.tree.has_animation(StringName(str(c))):
			return StringName(str(c))
	return &""


func _still(body: HeroFieldActor, n: int) -> void:
	player.input_override = Vector2.ZERO
	_steps(body, n)


func _steps(body: HeroFieldActor, n: int) -> void:
	for i in n:
		_step(body)


func _step(body: HeroFieldActor) -> void:
	player.step(DT)
	body.advance(DT)


func _body() -> HeroFieldActor:
	var b := player.get_node_or_null(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
	if b != null:
		b.set_process(false)
	return b


func _done() -> void:
	zone.free()
	Game.state.party_ids = _party_was


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
