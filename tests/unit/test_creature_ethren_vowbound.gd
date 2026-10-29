extends TestCase
## M3-CRE-644: Ethren, the Level Saint, Asha's Glimmer Vowbound, as a creature actor
## (docs/kb/art/creatures/vowbound/ethren.md). His stand-in resolves to the model through creatures.json's `vowbound`
## row (his vowbound.json row is pending: `vowbound_pending`), faces the foes as the heroes do and carries his own
## height and ring radius; the scene loads headless with every clip; and the clips do what the sheet says (built
## hovering, an idle that barely moves, a veil that never moves on the head, wings closed except in ready, cast, special
## and victory, a kneel that telescopes the robe, the halo tipping in the KO, the level press, Still Water's press).

const SCENE := "res://game/creatures/ethren/ethren_battle.tscn"
const RING := {"radius_factor": 1.4, "inner_soft_m": 0.25, "notches": 6}
## Every clip the sheet lists (hit_b and idle_b are authored, not the kit's copies).
const CLIPS: Array[StringName] = [
	&"idle",
	&"ready",
	&"attack",
	&"cast",
	&"hit",
	&"hit_b",
	&"defend",
	&"ko",
	&"victory",
	&"rise",
	&"dismiss",
	&"special",
	&"idle_b",
	&"release",  # M3-CRE-647: the held form's release (its KO as a foe)
]
const YAW_DEG := -90.0
## creatures.json stand_in: the height the VFX anchors are fractions of, and the ring's radius.
const HEIGHT_M := 2.5
const RADIUS_M := 0.6
## Built hovering: the hips' rest height (the build's HIP).
const HIP_Y := 1.30
const HIP_TOL_M := 0.02
## The idle is almost still: the head moves less than this over the loop (a 1 cm rise and fall).
const IDLE_STILL_M := 0.012
const IDLE_TIMES: Array[float] = [1.0, 2.0, 3.0]
## The veil is rigid on the head in every clip: its bone's local pose stays at rest within this.
const VEIL_TOL := 0.0001
## The outer wings' hinges, left to right: closed this close at most, open this far at least.
const CLOSED_M := 0.4
const OPEN_M := 0.9
## Clips (and times) in which the wings must stay closed.
const CLOSED_IN: Dictionary = {&"idle": 2.0, &"attack": 0.55, &"hit": 0.1, &"hit_b": 0.1, &"idle_b": 0.7}
## Clips (and times) in which they open.
const OPEN_IN: Dictionary = {&"ready": 0.55, &"cast": 0.8, &"special": 1.45, &"victory": 2.2}
## The kneel: the hips sink at least this far (KO end, rise start, dismiss end).
const KNEEL_M := 0.35
## The halo tips in the KO: its axis turns at least this much against the head's.
const HALO_TIP_DOT := 0.99
## The level press: the right hand rises at least this far, then presses down at least this far by the contact.
const ATTACK_RAISED_SEC := 0.32
const RAISE_M := 0.2
const PRESS_M := 0.15
## Still Water: the hands are raised before the contact and pressed down at it, at least this far.
const SPECIAL_RAISED_SEC := 1.2
const SPECIAL_PRESS_M := 0.2
const END_SEC := 0.001

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_the_vowbound_stand_in_resolves_to_the_model() -> void:
	var spec := BattleStage.stand_in_spec(&"ethren")
	assert_eq(str(spec.get("scene", "")), SCENE, "the stand-in shows the model, not the capsule")
	assert_eq(CreatureModels.vowbound_creature("ethren"), &"ethren")
	assert_true(is_equal_approx(float(spec["yaw_deg"]), YAW_DEG), "he faces the foes, as the heroes do")
	assert_false(spec.has("hover"), "built hovering: the stand-in adds no hover")
	assert_true(is_equal_approx(float(spec["height"]), HEIGHT_M), "his own height drives the VFX anchors")
	assert_true(is_equal_approx(float(spec["radius"]), RADIUS_M), "and his ring fits the robe's hem")
	assert_false(CreatureModels.models().has("ethren"), "he is no enemy")
	before_each()


func test_the_scene_loads_headless_with_its_clips() -> void:
	var a := _actor()
	assert_eq(a.creature_id, &"ethren")
	assert_eq(a.current_clip, &"idle", "it idles")
	for clip in CLIPS:
		assert_true(a.has_clip(clip), "ethren has %s" % clip)
	assert_eq(a.clip_for(&"attack", &"physical"), &"attack", "the level press")
	for clip: StringName in [&"attack", &"cast", &"special"]:
		var t := a.contact_time(clip)
		assert_true(t > 0.0 and t < a.clip_length(clip), "%s lands inside the clip" % clip)
	var skel := _pose(a, &"idle", 0.0)
	assert_true(absf(_bone_at(skel, "body").y - HIP_Y) < HIP_TOL_M, "he hovers at his rest height")
	assert_true(skel.find_bone("finger_l1") >= 0, "the ring hand's ring-finger group")
	var veil := a.find_children("ethren_veil", "MeshInstance3D", true, false)
	assert_eq(veil.size(), 1, "the veil is its own mesh, so cinematics can drop it")
	before_each()


func test_the_stand_in_plays_the_stage_clips_on_the_model() -> void:
	var f := FighterStandIn.new()
	f.setup(&"ethren", BattleStage.stand_in_spec(&"ethren"), RING)
	_add(f)
	assert_true(f.has_actor() and f.creature() != null, "the model, not the capsule")
	assert_true(is_equal_approx(f.actor().rotation.y, deg_to_rad(YAW_DEG)))
	assert_true(BattleClips.play(f, &"ready"), "the entry and the dismissal's clip (choreo.json vowbound)")
	assert_eq(f.creature().current_clip, &"ready")
	assert_true(BattleClips.play(f, &"ko"), "the fall's clip")
	f.set_ko(true, 0.25, 0.35)
	assert_true(f.creature().is_ko())
	before_each()


func test_the_idle_is_still_and_the_veil_never_moves() -> void:
	var a := _actor()
	var skel := _pose(a, &"idle", 0.0)
	var head0 := _bone_at(skel, "head")
	for t in IDLE_TIMES:
		skel = _pose(a, &"idle", t)
		assert_true(head0.distance_to(_bone_at(skel, "head")) < IDLE_STILL_M, "the idle barely moves (%.1f s)" % t)
	var veil := skel.find_bone("veil")
	for clip in CLIPS:
		var length := (
			(a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer).get_animation(clip).length
		)
		for t: float in [0.0, length * 0.5, length]:
			skel = _pose(a, clip, t)
			var pose := skel.get_bone_pose(veil)
			var rest := skel.get_bone_rest(veil)
			assert_true(
				pose.origin.distance_to(rest.origin) < VEIL_TOL and pose.basis.is_equal_approx(rest.basis),
				"the veil is still on the head in %s at %.2f s" % [clip, t]
			)
	before_each()


func test_the_wings_open_only_when_he_acts() -> void:
	var a := _actor()
	for clip: StringName in CLOSED_IN:
		var skel := _pose(a, clip, float(CLOSED_IN[clip]))
		assert_true(_wing_span(skel) < CLOSED_M, "the wings stay folded in %s" % clip)
	for clip: StringName in OPEN_IN:
		var skel := _pose(a, clip, float(OPEN_IN[clip]))
		assert_true(_wing_span(skel) > OPEN_M, "the wings open in %s" % clip)
	before_each()


func test_the_clips_follow_the_sheet() -> void:
	var a := _actor()
	var skel := _pose(a, &"idle", 0.0)
	var hip0 := _bone_at(skel, "body")
	var hand0 := _bone_at(skel, "hand_r")
	var hands0 := _bone_at(skel, "hand_l").y
	skel = _pose(a, &"ko", INF)
	assert_true(hip0.y - _bone_at(skel, "body").y > KNEEL_M, "the KO kneels")
	assert_true(
		_turned(skel, "halo", Vector3.UP).dot(_turned(skel, "head", Vector3.UP)) < HALO_TIP_DOT, "the halo tips"
	)
	skel = _pose(a, &"rise", 0.0)
	assert_true(hip0.y - _bone_at(skel, "body").y > KNEEL_M, "the rise starts kneeling")
	skel = _pose(a, &"dismiss", INF)
	assert_true(hip0.y - _bone_at(skel, "body").y > KNEEL_M, "the dismissal ends kneeling")
	skel = _pose(a, &"attack", ATTACK_RAISED_SEC)
	var raised := _bone_at(skel, "hand_r")
	assert_true(raised.y - hand0.y > RAISE_M, "the hand rises, palm out")
	skel = _pose(a, &"attack", a.contact_time(&"attack"))
	assert_true(raised.y - _bone_at(skel, "hand_r").y > PRESS_M, "and presses down at the contact")
	skel = _pose(a, &"special", SPECIAL_RAISED_SEC)
	var held := _bone_at(skel, "hand_l").y
	skel = _pose(a, &"special", a.contact_time(&"special"))
	var pressed := _bone_at(skel, "hand_l").y
	assert_true(held - pressed > SPECIAL_PRESS_M, "Still Water presses both hands down at the contact")
	assert_true(pressed < hands0, "below where they rest")
	before_each()


func _wing_span(skel: Skeleton3D) -> float:
	return _bone_at(skel, "wing_lo_1").distance_to(_bone_at(skel, "wing_ro_1"))


func _actor() -> CreatureActor:
	var a := (load(SCENE) as PackedScene).instantiate() as CreatureActor
	_add(a)
	return a


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


## Poses the actor's model at `sec` into `clip` (clamped to just before its end) and returns its skeleton.
func _pose(a: CreatureActor, clip: StringName, sec: float) -> Skeleton3D:
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.play(clip)
	player.seek(minf(sec, player.get_animation(clip).length - END_SEC), true)
	return a.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D


func _bone_at(skel: Skeleton3D, bone: String) -> Vector3:
	return (skel.global_transform * skel.get_bone_global_pose(skel.find_bone(bone))).origin


## `axis` (in the rest pose's frame) as the bone's pose has turned it, in the skeleton's frame.
func _turned(skel: Skeleton3D, bone: String, axis: Vector3) -> Vector3:
	var i := skel.find_bone(bone)
	var turn := skel.get_bone_global_pose(i).basis * skel.get_bone_global_rest(i).basis.inverse()
	return (turn * axis).normalized()
