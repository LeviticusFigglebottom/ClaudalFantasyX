extends TestCase
## M2-HER-1104: HeroMotion, the cutscene entry point on a hero body. play() reaches a body's play_clip
## (duck-typed) with the cross-fade, else the actor's AnimationPlayer; a walk's start and stop blend
## through idle -> walk -> idle; set_locomotion_speed reaches the body and fades the idle micro-motion;
## add_micro_motion is a soft no-op on a capsule. And the turn strip's eased turn never snaps.

const ASHA := "res://assets/characters/asha/asha.glb"
const STRIP := "res://game/levels/_tests/hero_motion/cutscene_turn_strip.tscn"
const BLEND := 0.25
const DT := 1.0 / 60.0
const EPS := 0.0001
## At rest: under 1°/s (the strip reads its rate off the curve by a finite difference).
const REST_RAD_S := 0.02
## The head over the body: within 0.1°.
const ALIGNED_RAD := 0.002


## A stand-in for a hero body (HeroFieldActor's AnimationTree): records every call.
class FakeBody:
	extends Node3D
	var calls: Array = []
	var speeds: Array[float] = []
	var clips: Array[StringName] = [&"idle", &"walk"]

	func play_clip(clip: StringName, blend: float) -> bool:
		calls.append([clip, blend])
		return clip in clips

	func set_locomotion_speed(mps: float) -> void:
		speeds.append(mps)


func _asha() -> Node3D:
	var a := (load(ASHA) as PackedScene).instantiate() as Node3D
	_host().add_child(a)
	return a


func _actor_with_body() -> Array:
	var actor := Node3D.new()
	var body := FakeBody.new()
	body.name = "Body"
	actor.add_child(body)
	_host().add_child(actor)
	return [actor, body]


func test_play_goes_to_the_body_with_the_blend() -> void:
	var pair := _actor_with_body()
	var actor := pair[0] as Node3D
	var body := pair[1] as FakeBody
	assert_eq(HeroMotion.body_of(actor), body, "the body child is found by its play_clip")
	assert_true(HeroMotion.play(actor, &"walk", BLEND), "the body plays a clip it has")
	assert_false(HeroMotion.play(actor, &"kneel", BLEND), "and says false for one it lacks")
	assert_eq(body.calls, [[&"walk", BLEND], [&"kneel", BLEND]], "each call carries its clip and blend")
	actor.free()


func test_a_walk_start_and_stop_blend_through_the_gait() -> void:
	var pair := _actor_with_body()
	var actor := pair[0] as Node3D
	var body := pair[1] as FakeBody
	# What the patched sequencer does over a @move: walk in, the ramp's speeds, idle out.
	HeroMotion.play(actor, &"walk", BLEND, false)
	for mps: float in [0.0, 0.4, 1.3, 1.3, 0.5, 0.0]:
		HeroMotion.set_locomotion_speed(actor, mps)
	HeroMotion.play(actor, &"idle", BLEND, false)
	assert_eq(body.calls, [[&"walk", BLEND], [&"idle", BLEND]], "idle -> walk -> idle, each cross-faded")
	assert_eq(body.speeds, [0.0, 0.4, 1.3, 1.3, 0.5, 0.0] as Array[float], "the ramp's speeds reach the gait")
	actor.free()


func test_the_animation_player_fallback_cross_fades_and_keeps_a_playing_clip() -> void:
	var a := _asha()
	var ap := HeroMotion.player_of(a)
	assert_true(ap != null, "the hero import rule gives an AnimationPlayer")
	assert_eq(HeroMotion.body_of(a), null, "a bare glTF has no body")
	assert_true(HeroMotion.play(a, &"idle", 0.0), "idle")
	ap.advance(0.5)
	var seq: Array[StringName] = [ap.assigned_animation]
	assert_true(HeroMotion.play(a, &"walk", BLEND), "walk")
	seq.append(ap.assigned_animation)
	ap.advance(0.5)
	var walk_pos := ap.current_animation_position
	assert_true(HeroMotion.play(a, &"walk", BLEND, false), "walk again, no restart")
	assert_between(ap.current_animation_position, walk_pos - EPS, walk_pos + EPS, "the walk carried on")
	assert_true(HeroMotion.play(a, &"idle", BLEND), "idle")
	seq.append(ap.assigned_animation)
	assert_eq(seq, [&"idle", &"walk", &"idle"] as Array[StringName], "the clip sequence")
	assert_false(HeroMotion.play(a, &"no_such_clip", BLEND), "a missing clip is a no-op false")
	assert_eq(ap.assigned_animation, &"idle", "and leaves the clip alone")
	a.free()


func test_locomotion_speed_fades_the_micro_motion() -> void:
	var a := _asha()
	var micro := HeroMotion.add_micro_motion(a, &"asha")
	assert_true(micro != null, "a hero with a skeleton gets micro-motion")
	assert_eq(HeroMotion.add_micro_motion(a, &"asha"), micro, "once")
	HeroMotion.set_locomotion_speed(a, 1.3)
	assert_eq(micro.amount, 0.0, "walking: no idle breathing or sway")
	micro.advance(DT)
	assert_true(micro.amount_now > 0.0 and micro.amount_now < 1.0, "it fades out, not off")
	HeroMotion.set_locomotion_speed(a, 0.0)
	assert_eq(micro.amount, 1.0, "standing again")
	a.free()


func test_a_capsule_gets_no_micro_motion_and_no_errors() -> void:
	var capsule := Node3D.new()
	capsule.add_child(MeshInstance3D.new())
	_host().add_child(capsule)
	assert_eq(HeroMotion.add_micro_motion(capsule), null, "no skeleton: nothing added")
	assert_false(HeroMotion.play(capsule, &"idle", BLEND), "no clips: false")
	HeroMotion.set_locomotion_speed(capsule, 1.0)
	HeroMotion.set_idle_amount(capsule, 0.0)
	assert_eq(capsule.get_child_count(), 1, "nothing was added")
	capsule.free()


func test_the_strip_turn_eases_without_snapping_and_lands() -> void:
	var strip := (load(STRIP) as PackedScene).instantiate()
	var dur: float = strip.turn_duration()
	assert_true(dur > 0.0, "the turn takes time")
	var steps := ceili(dur / DT)
	var prev: float = strip.yaw_at(0.0)
	var first := 0.0
	var peak := 0.0
	for i in range(1, steps + 1):
		var y: float = strip.yaw_at(minf(float(i) * DT / dur, 1.0))
		var d := absf(y - prev)
		if i == 1:
			first = d
		peak = maxf(peak, d)
		assert_true(y >= prev - EPS, "frame %d turns one way" % i)
		prev = y
	var total := deg_to_rad(float(strip.turn_deg))
	assert_true(peak < total * 0.25, "no frame snaps a quarter of the turn")
	assert_true(first < peak * 0.5, "it eases in")
	var end_step := absf(strip.yaw_at(1.0) - strip.yaw_at(1.0 - DT / dur))
	assert_true(end_step < peak * 0.5, "and eases out")
	assert_between(prev, deg_to_rad(strip.start_yaw_deg) + total - EPS, deg_to_rad(strip.start_yaw_deg) + total + EPS)
	assert_between(strip.rate_at(0.0, dur), -REST_RAD_S, REST_RAD_S, "it sets off from rest")
	assert_between(strip.rate_at(1.0, dur), -REST_RAD_S, REST_RAD_S, "and lands at rest")
	strip.free()


func test_the_strip_builds_its_frames_with_a_leading_head() -> void:
	var strip := (load(STRIP) as PackedScene).instantiate()
	_host().add_child(strip)
	var actors: Array[Node3D] = strip.actors
	assert_eq(actors.size(), int(strip.frames), "one copy per frame")
	var mid := HeroMotion.micro_of(actors[actors.size() / 2])
	var last := HeroMotion.micro_of(actors[actors.size() - 1])
	assert_true(mid != null and last != null, "each copy breathes")
	assert_true(mid.head_lead() > 0.0, "mid-turn the head is ahead of the body, the way it turns")
	assert_between(last.head_lead(), -ALIGNED_RAD, ALIGNED_RAD, "landed: the head is back over the body")
	strip.free()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
