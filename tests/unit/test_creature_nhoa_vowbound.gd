extends TestCase
## M3-CRE-642: Nhoa, the Rootlight, Asha's Ice Vowbound, as a creature actor (docs/kb/art/creatures/vowbound/nhoa.md).
## Her stand-in resolves to the model through creatures.json's `vowbound` row (CreatureModels; her vowbound.json row is
## Combat's, still pending), faces the foes as the heroes do, and carries her own height and ring radius (she has no
## battle_sandbox.json row); the scene loads headless with every clip the stage plays; the name-shell is never lit; and
## the clips do what the sheet says (she hovers, the strands sway, the strike sweeps forward, the cast pushes both hands
## out, the blow snaps her head back, her arms cross to defend, the rise starts bowed, the KO bows her, and
## Farewell-Tide lifts her arms high and draws the strands up).

const SCENE := "res://game/creatures/nhoa/nhoa_battle.tscn"
const RING := {"radius_factor": 1.4, "inner_soft_m": 0.25, "notches": 6}
## Every clip the sheet lists, plus the kit's variety clips (hit_b is authored, rolled to the other side).
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
const HEIGHT_M := 3.2
const RADIUS_M := 0.5
## Her surfaces that are never lit: the keepsake (the name-shell and its cord) and the dark inner body.
const SHELL_MATERIAL := "res://assets/creatures/nhoa/materials/shell.tres"
const BODY_MATERIAL := "res://assets/creatures/nhoa/materials/body.tres"
## Tall: the head bone (the top of the neck) at least this high at rest.
const HEAD_MIN_Y := 2.3
## Built hovering: the strands' last bones start at least this high over the water at rest.
const STRAND_MIN_Y := 0.25
const STRANDS: Array[String] = ["strand_l2", "strand_r2", "strand_b2"]
## The idle's slow current: a strand's last bone moves at least this far between the start and the quarter beat.
const IDLE_SWAY_M := 0.03
const IDLE_QUARTER_SEC := 1.0
## The strike sweeps the near hand at least this far forward from the wind-up to the contact.
const ATTACK_WIND_SEC := 0.32
const SWEEP_M := 0.8
## The cast: both hands drawn up, then pushed at least this far forward by the contact.
const CAST_DRAWN_SEC := 0.42
const PUSH_M := 0.3
## The blow snaps her head back at least this far at its peak.
const HIT_PEAK_SEC := 0.1
const SNAP_M := 0.2
const DEFEND_HELD_SEC := 0.5
## The rise starts bowed, and the KO bows her: the head at least this far under its rest height.
const BOWED_DROP_M := 0.3
const KO_DROP_M := 0.4
## Farewell-Tide at the contact: the wrists at least head height, the strands drawn up at least this far.
const STRANDS_DRAWN_M := 0.5
const END_SEC := 0.001

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_the_vowbound_stand_in_resolves_to_the_model() -> void:
	var spec := BattleStage.stand_in_spec(&"nhoa")
	assert_eq(str(spec.get("scene", "")), SCENE, "the stand-in shows the model, not the capsule")
	assert_eq(CreatureModels.vowbound_creature("nhoa"), &"nhoa")
	assert_true(is_equal_approx(float(spec["yaw_deg"]), YAW_DEG), "she faces the foes, as the heroes do")
	assert_false(spec.has("hover"), "built hovering: the stand-in adds no hover")
	assert_true(is_equal_approx(float(spec["height"]), HEIGHT_M), "her own height drives the VFX anchors")
	assert_true(is_equal_approx(float(spec["radius"]), RADIUS_M), "and her ring fits her narrow footprint")
	assert_false(CreatureModels.models().has("nhoa"), "she is no enemy")
	assert_eq(CreatureModels.stand_in_overrides("ilun").get("scene", ""), "res://game/creatures/ilun/ilun_battle.tscn")
	before_each()


func test_the_scene_loads_headless_with_its_clips() -> void:
	var a := _actor()
	assert_eq(a.creature_id, &"nhoa")
	assert_eq(a.current_clip, &"idle", "it idles")
	for clip in CLIPS:
		assert_true(a.has_clip(clip), "nhoa has %s" % clip)
	assert_eq(a.clip_for(&"attack", &"physical"), &"attack", "the sweeping open-handed strike")
	assert_eq(a.clip_for(&"brine_lash", &"magical"), &"cast", "a spell is the ice cast until Combat names her skills")
	for clip: StringName in [&"attack", &"cast", &"special"]:
		var t := a.contact_time(clip)
		assert_true(t > 0.0 and t < a.clip_length(clip), "%s lands inside the clip" % clip)
	var skel := _pose(a, &"idle", 0.0)
	assert_true(_bone_at(skel, "head").y > HEAD_MIN_Y, "she is tall, her head high on the heron neck")
	for bone in STRANDS:
		assert_true(_bone_at(skel, bone).y > STRAND_MIN_Y, "%s hangs over the water, not in it" % bone)
	before_each()


func test_the_name_shell_never_glows() -> void:
	for path in [SHELL_MATERIAL, BODY_MATERIAL]:
		var m := load(path) as ShaderMaterial
		assert_true(m != null, "%s loads" % path)
		if m != null:
			assert_eq(float(m.get_shader_parameter("emission_energy")), 0.0, "%s is never lit" % path)
	before_each()


func test_the_stand_in_plays_the_stage_clips_on_the_model() -> void:
	var f := FighterStandIn.new()
	f.setup(&"nhoa", BattleStage.stand_in_spec(&"nhoa"), RING)
	_add(f)
	assert_true(f.has_actor() and f.creature() != null, "the model, not the capsule")
	assert_true(is_equal_approx(f.actor().rotation.y, deg_to_rad(YAW_DEG)))
	assert_true(BattleClips.play(f, &"ready"), "the entry and the dismissal's clip (choreo.json vowbound)")
	assert_eq(f.creature().current_clip, &"ready")
	assert_eq(BattleClips.action_clip(f, &"attack", &"physical"), &"attack")
	assert_true(BattleClips.play(f, &"ko"), "the fall's clip")
	f.set_ko(true, 0.25, 0.35)
	assert_true(f.creature().is_ko())
	before_each()


func test_the_clips_follow_the_sheet() -> void:
	var a := _actor()
	var skel := _pose(a, &"idle", 0.0)
	var head0 := _bone_at(skel, "head")
	var strand0 := _bone_at(skel, "strand_l2")
	var strands0: Array[Vector3] = []
	for bone in STRANDS:
		strands0.append(_bone_at(skel, bone))
	skel = _pose(a, &"idle", IDLE_QUARTER_SEC)
	assert_true(strand0.distance_to(_bone_at(skel, "strand_l2")) > IDLE_SWAY_M, "the strands sway in a slow current")
	skel = _pose(a, &"attack", ATTACK_WIND_SEC)
	var wound := _bone_at(skel, "hand_l")
	skel = _pose(a, &"attack", a.contact_time(&"attack"))
	assert_true(_bone_at(skel, "hand_l").z - wound.z > SWEEP_M, "the open hand sweeps forward")
	skel = _pose(a, &"cast", CAST_DRAWN_SEC)
	var drawn := _bone_at(skel, "hand_l")
	skel = _pose(a, &"cast", a.contact_time(&"cast"))
	for bone in ["hand_l", "hand_r"]:
		assert_true(_bone_at(skel, bone).z - drawn.z > PUSH_M, "%s pushes the ice forward" % bone)
	skel = _pose(a, &"hit", HIT_PEAK_SEC)
	assert_true(head0.z - _bone_at(skel, "head").z > SNAP_M, "the blow snaps her neck back")
	skel = _pose(a, &"defend", DEFEND_HELD_SEC)
	assert_true(_bone_at(skel, "hand_l").x < 0.0 and _bone_at(skel, "hand_r").x > 0.0, "her arms cross before her")
	skel = _pose(a, &"rise", 0.0)
	assert_true(_bone_at(skel, "head").y < head0.y - BOWED_DROP_M, "the rise starts bowed")
	skel = _pose(a, &"dismiss", INF)
	assert_true(_bone_at(skel, "head").y < head0.y - BOWED_DROP_M, "the dismissal ends bowed")
	skel = _pose(a, &"ko", INF)
	assert_true(_bone_at(skel, "head").y < head0.y - KO_DROP_M, "the KO bows her")
	skel = _pose(a, &"special", a.contact_time(&"special"))
	for bone in ["hand_l", "hand_r"]:
		assert_true(_bone_at(skel, bone).y > head0.y, "Farewell-Tide lifts %s high" % bone)
	for i in STRANDS.size():
		assert_true(_bone_at(skel, STRANDS[i]).y > strands0[i].y + STRANDS_DRAWN_M, "%s is drawn up" % STRANDS[i])
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
