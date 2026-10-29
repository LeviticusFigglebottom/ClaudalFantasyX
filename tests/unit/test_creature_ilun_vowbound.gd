extends TestCase
## M3-CRE-638: Ilun, Asha's Vowbound, as a creature actor (docs/kb/art/creatures/vowbound/ilun.md). His stand-in
## resolves to the model through creatures.json's `vowbound` row (CreatureModels, no enemies.json model), faces the
## foes as the heroes do and keeps battle_sandbox.json's height; the scene loads headless with every clip the stage and
## his skills play; and the clips do what the sheet says (the idle undulates, the rise starts folded, the KO tips him
## back with the float still hanging, Floodnet sweeps the wings down).

const SCENE := "res://game/creatures/ilun/ilun_battle.tscn"
const RING := {"radius_factor": 1.4, "inner_soft_m": 0.25, "notches": 6}
## Every clip the sheet lists, plus the kit's variety clips.
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
const SANDBOX_HEIGHT_M := 2.3
## The disc's mid-plane above the water at rest (the build's HOVER_Y), and how close the body bone must sit to it.
const HOVER_Y := 1.35
const HOVER_TOL_M := 0.02
## How far the outer wing joint moves between the idle's start and its quarter beat, at least.
const STROKE_M := 0.1
const IDLE_QUARTER_SEC := 1.0
## The rise starts with the wings folded up over his back: the outer wing joints this far over the body, at least.
const FOLDED_OVER_M := 1.0
## The KO tips him back: his nose rises at least this much (the y of his turned forward axis).
const KO_NOSE_UP := 0.35
## The float still hangs at the end of the KO: its down axis at least this close to straight down.
const FLOAT_HANG_Y := -0.9
## Floodnet: from the held breath to the contact the outer wing joints sweep down at least this far.
const SWEEP_M := 0.5
const SPECIAL_HELD_SEC := 1.0
const END_SEC := 0.001

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_the_vowbound_stand_in_resolves_to_the_model() -> void:
	var spec := BattleStage.stand_in_spec(&"ilun")
	assert_eq(str(spec.get("scene", "")), SCENE, "the stand-in shows the model, not the capsule")
	assert_eq(CreatureModels.vowbound_creature("ilun"), &"ilun")
	assert_true(is_equal_approx(float(spec["yaw_deg"]), YAW_DEG), "he faces the foes, as the heroes do")
	assert_false(spec.has("hover"), "built hovering: the stand-in adds no hover under the VFX anchors")
	assert_true(
		is_equal_approx(float(spec["height"]), SANDBOX_HEIGHT_M),
		"battle_sandbox.json's height still drives the anchors"
	)
	assert_false(CreatureModels.models().has("ilun"), "he is no enemy")
	assert_eq(CreatureModels.vowbound_creature("gallery_ray"), &"", "a creature row without `vowbound` is no Vowbound")
	assert_eq(CreatureModels.stand_in_overrides("asha"), {}, "the heroes keep their own actors")
	assert_eq(CreatureModels.vowbound_creature("no_such_vowbound"), &"")
	before_each()


func test_the_scene_loads_headless_with_its_clips() -> void:
	var a := _actor()
	assert_eq(a.creature_id, &"ilun")
	assert_eq(a.current_clip, &"idle", "it idles")
	for clip in CLIPS:
		assert_true(a.has_clip(clip), "ilun has %s" % clip)
	assert_eq(a.clip_for(&"brine_lash", &"magical"), &"attack", "the brine lash is the wing sweep")
	assert_eq(a.clip_for(&"tidal_ward", &"support"), &"cast", "the tidal ward is the shield")
	assert_eq(a.clip_for(&"floodnet", &"magical"), &"special", "Floodnet")
	assert_eq(a.clip_for(&"attack", &"physical"), &"attack")
	for clip: StringName in [&"attack", &"cast", &"special"]:
		var t := a.contact_time(clip)
		assert_true(t > 0.0 and t < a.clip_length(clip), "%s lands inside the clip" % clip)
	var skel := _pose(a, &"idle", 0.0)
	assert_true(absf(_bone_at(skel, "body").y - HOVER_Y) < HOVER_TOL_M, "he hovers over the water")
	before_each()


func test_the_stand_in_plays_the_stage_clips_on_the_model() -> void:
	var f := FighterStandIn.new()
	f.setup(&"ilun", BattleStage.stand_in_spec(&"ilun"), RING)
	_add(f)
	assert_true(f.has_actor() and f.creature() != null, "the model, not the capsule")
	assert_true(is_equal_approx(f.actor().rotation.y, deg_to_rad(YAW_DEG)))
	assert_true(BattleClips.play(f, &"ready"), "the entry and the dismissal's clip (choreo.json vowbound)")
	assert_eq(f.creature().current_clip, &"ready")
	assert_eq(BattleClips.action_clip(f, &"floodnet", &"magical"), &"special")
	assert_true(BattleClips.play(f, &"ko"), "the fall's clip")
	f.set_ko(true, 0.25, 0.35)
	assert_true(f.creature().is_ko())
	before_each()


func test_the_clips_follow_the_sheet() -> void:
	var a := _actor()
	var skel := _pose(a, &"idle", 0.0)
	var tip0 := _bone_at(skel, "wing_l2")
	skel = _pose(a, &"idle", IDLE_QUARTER_SEC)
	assert_true(tip0.distance_to(_bone_at(skel, "wing_l2")) > STROKE_M, "the wings undulate")
	skel = _pose(a, &"rise", 0.0)
	var body := _bone_at(skel, "body")
	for side in ["l", "r"]:
		assert_true(_bone_at(skel, "wing_%s2" % side).y > body.y + FOLDED_OVER_M, "the rise starts folded (%s)" % side)
	skel = _pose(a, &"ko", INF)
	assert_true(_turned(skel, "body", Vector3.BACK).y > KO_NOSE_UP, "the KO tips him back, nose up")
	assert_true(_turned(skel, "float", Vector3.DOWN).y < FLOAT_HANG_Y, "the keepsake still hangs")
	skel = _pose(a, &"special", SPECIAL_HELD_SEC)
	var held := _bone_at(skel, "wing_l2").y
	skel = _pose(a, &"special", a.contact_time(&"special"))
	assert_true(held - _bone_at(skel, "wing_l2").y > SWEEP_M, "Floodnet sweeps the wings down on the contact")
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


## `axis` (in the rest pose's frame) as the bone's pose has turned it, in the skeleton's frame.
func _turned(skel: Skeleton3D, bone: String, axis: Vector3) -> Vector3:
	var i := skel.find_bone(bone)
	var turn := skel.get_bone_global_pose(i).basis * skel.get_bone_global_rest(i).basis.inverse()
	return (turn * axis).normalized()
