extends TestCase
## M3-CRE-640: Kahre, Asha's Lightning Vowbound, as a creature actor (docs/kb/art/creatures/vowbound/kahre.md). His
## stand-in resolves to the model through creatures.json's `vowbound` row (CreatureModels), faces the foes as the
## heroes do, and carries his own height and ring radius (he has no battle_sandbox.json row); the scene loads headless
## with every clip the stage and his skills play; and the clips do what the sheet says (the feet stay planted while
## he breathes, the casque strike drives the head down and forward, the rise starts crouched, the KO lies him down,
## Last Strike brings the hammer from high over his back down to the water).

const SCENE := "res://game/creatures/kahre/kahre_battle.tscn"
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
const HEIGHT_M := 3.3
const RADIUS_M := 0.75
## The hips' rest height (the build's HIP) and how close the body bone must sit to it.
const HIP_Y := 1.38
const HIP_TOL_M := 0.02
## A planted foot moves less than this between two idle frames (the solve holds it in its leg's plane; the idle's
## slight roll lets it give a few millimetres sideways).
const PLANTED_TOL_M := 0.015
const IDLE_SAMPLE_SEC := 1.7
const FEET: Array[String] = ["hand_l", "hand_r", "foot_l", "foot_r"]
## The casque strike: at the contact the head is at least this much lower and further forward than at rest.
const STRIKE_DROP_M := 0.7
const STRIKE_REACH_M := 0.4
## The rise starts crouched: the hips at least this much under their rest height.
const RISE_CROUCH_M := 0.3
## The KO lies him down: the hips at least this much under their rest height at the end.
const KO_DROP_M := 0.6
## Last Strike: the head falls at least this far from the held rear to the contact, and ends near the water.
const SPECIAL_HELD_SEC := 1.1
const SPECIAL_FALL_M := 2.0
const SPECIAL_HEAD_MAX_Y := 0.9
const END_SEC := 0.001

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_the_vowbound_stand_in_resolves_to_the_model() -> void:
	var spec := BattleStage.stand_in_spec(&"kahre")
	assert_eq(str(spec.get("scene", "")), SCENE, "the stand-in shows the model, not the capsule")
	assert_eq(CreatureModels.vowbound_creature("kahre"), &"kahre")
	assert_true(is_equal_approx(float(spec["yaw_deg"]), YAW_DEG), "he faces the foes, as the heroes do")
	assert_false(spec.has("hover"), "he stands on the water")
	assert_true(is_equal_approx(float(spec["height"]), HEIGHT_M), "his own height drives the VFX anchors")
	assert_true(is_equal_approx(float(spec["radius"]), RADIUS_M), "and his ring fits his footprint")
	assert_false(CreatureModels.models().has("kahre"), "he is no enemy")
	assert_eq(CreatureModels.stand_in_overrides("ilun").get("scene", ""), "res://game/creatures/ilun/ilun_battle.tscn")
	before_each()


func test_the_scene_loads_headless_with_its_clips() -> void:
	var a := _actor()
	assert_eq(a.creature_id, &"kahre")
	assert_eq(a.current_clip, &"idle", "it idles")
	for clip in CLIPS:
		assert_true(a.has_clip(clip), "kahre has %s" % clip)
	assert_eq(a.clip_for(&"forge_bolt", &"magical"), &"cast", "Forge Bolt calls the strike down")
	assert_eq(a.clip_for(&"last_strike", &"magical"), &"special", "Last Strike")
	assert_eq(a.clip_for(&"attack", &"physical"), &"attack", "the casque strike")
	for clip: StringName in [&"attack", &"cast", &"special"]:
		var t := a.contact_time(clip)
		assert_true(t > 0.0 and t < a.clip_length(clip), "%s lands inside the clip" % clip)
	var skel := _pose(a, &"idle", 0.0)
	assert_true(absf(_bone_at(skel, "body").y - HIP_Y) < HIP_TOL_M, "he stands on the water at his rest height")
	before_each()


func test_the_stand_in_plays_the_stage_clips_on_the_model() -> void:
	var f := FighterStandIn.new()
	f.setup(&"kahre", BattleStage.stand_in_spec(&"kahre"), RING)
	_add(f)
	assert_true(f.has_actor() and f.creature() != null, "the model, not the capsule")
	assert_true(is_equal_approx(f.actor().rotation.y, deg_to_rad(YAW_DEG)))
	assert_true(BattleClips.play(f, &"ready"), "the entry and the dismissal's clip (choreo.json vowbound)")
	assert_eq(f.creature().current_clip, &"ready")
	assert_eq(BattleClips.action_clip(f, &"last_strike", &"magical"), &"special")
	assert_true(BattleClips.play(f, &"ko"), "the fall's clip")
	f.set_ko(true, 0.25, 0.35)
	assert_true(f.creature().is_ko())
	before_each()


func test_the_clips_follow_the_sheet() -> void:
	var a := _actor()
	var skel := _pose(a, &"idle", 0.0)
	var feet: Array[Vector3] = []
	for b in FEET:
		feet.append(_bone_at(skel, b))
	var rest_head := _bone_at(skel, "head")
	var hip0 := _bone_at(skel, "body")
	skel = _pose(a, &"idle", IDLE_SAMPLE_SEC)
	for i in FEET.size():
		assert_true(feet[i].distance_to(_bone_at(skel, FEET[i])) < PLANTED_TOL_M, "%s stays planted" % FEET[i])
	skel = _pose(a, &"attack", a.contact_time(&"attack"))
	var head := _bone_at(skel, "head")
	assert_true(rest_head.y - head.y > STRIKE_DROP_M, "the casque strike drives the head down")
	assert_true(head.z - rest_head.z > STRIKE_REACH_M, "and forward, at the foes")
	skel = _pose(a, &"rise", 0.0)
	assert_true(hip0.y - _bone_at(skel, "body").y > RISE_CROUCH_M, "the rise starts crouched")
	skel = _pose(a, &"ko", INF)
	assert_true(hip0.y - _bone_at(skel, "body").y > KO_DROP_M, "the KO lies him down")
	skel = _pose(a, &"special", SPECIAL_HELD_SEC)
	var held := _bone_at(skel, "head").y
	skel = _pose(a, &"special", a.contact_time(&"special"))
	var struck := _bone_at(skel, "head").y
	assert_true(held - struck > SPECIAL_FALL_M, "Last Strike brings the hammer down from high over his back")
	assert_true(struck < SPECIAL_HEAD_MAX_Y, "onto the water in front of him")
	before_each()


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
