extends TestCase
## M3-CRE-641: Virel, the Kite-Serpent, Asha's Fire Vowbound, as a creature actor
## (docs/kb/art/creatures/vowbound/virel.md). Her stand-in resolves to the model through creatures.json's `vowbound`
## row (CreatureModels, no enemies.json model) and faces the foes as the heroes do; the scene loads headless with every
## clip the stage and her skills play; and the clips do what the sheet says (the idle undulates, the rise starts
## furled, the KO droops her head with the key still hanging, Flare Line pulls her taut in one long rising line).

const SCENE := "res://game/creatures/virel/virel_battle.tscn"
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
## Built hovering: the body bone (the S's forward swing, mid-body) this high over the water at rest, at least.
const BODY_MIN_Y := 0.9
## The head bone (the back of the head) moves at least this far between the idle's start and its quarter beat.
const IDLE_SWAY_M := 0.1
const IDLE_QUARTER_SEC := 1.0
## The rise starts furled: the head tucked at least this far below where it rests.
const FURLED_DROP_M := 0.5
## The KO lets the head droop at least this far, and the key still hangs (its down axis this close to straight down).
const KO_DROOP_M := 0.3
const KEY_HANG_Y := -0.9
## Flare Line: at the contact the head is at least this far from the tail end (the S pulled out into a line: her body
## is 4.85 m since M3-CRB-008) and higher than it; while she winds in before it, the two are drawn close.
const LINE_M := 4.5
const WOUND_M := 2.5
const SPECIAL_WOUND_SEC := 1.0
## The whipping strike: from the rear to the contact the head lashes at least this far forward and down.
const ATTACK_REAR_SEC := 0.3
const LASH_M := 0.25
const END_SEC := 0.001

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_the_vowbound_stand_in_resolves_to_the_model() -> void:
	var spec := BattleStage.stand_in_spec(&"virel")
	assert_eq(str(spec.get("scene", "")), SCENE, "the stand-in shows the model, not the placeholder")
	assert_eq(CreatureModels.vowbound_creature("virel"), &"virel")
	assert_true(is_equal_approx(float(spec["yaw_deg"]), YAW_DEG), "she faces the foes, as the heroes do")
	assert_false(spec.has("hover"), "built hovering: the stand-in adds no hover")
	assert_false(CreatureModels.models().has("virel"), "she is no enemy")
	assert_eq(CreatureModels.stand_in_overrides("ilun").get("scene", ""), "res://game/creatures/ilun/ilun_battle.tscn")
	before_each()


func test_the_scene_loads_headless_with_its_clips() -> void:
	var a := _actor()
	assert_eq(a.creature_id, &"virel")
	assert_eq(a.current_clip, &"idle", "it idles")
	for clip in CLIPS:
		assert_true(a.has_clip(clip), "virel has %s" % clip)
	assert_eq(a.clip_for(&"kite_flare", &"magical"), &"cast", "Kite Flare is the flare and the jabs")
	assert_eq(a.clip_for(&"flare_line", &"magical"), &"special", "Flare Line")
	assert_eq(a.clip_for(&"attack", &"physical"), &"attack", "the whipping strike")
	for clip: StringName in [&"attack", &"cast", &"special"]:
		var t := a.contact_time(clip)
		assert_true(t > 0.0 and t < a.clip_length(clip), "%s lands inside the clip" % clip)
	var skel := _pose(a, &"idle", 0.0)
	assert_true(_bone_at(skel, "body").y > BODY_MIN_Y, "she flies over the water")
	before_each()


func test_the_stand_in_plays_the_stage_clips_on_the_model() -> void:
	var f := FighterStandIn.new()
	f.setup(&"virel", BattleStage.stand_in_spec(&"virel"), RING)
	_add(f)
	assert_true(f.has_actor() and f.creature() != null, "the model, not the placeholder")
	assert_true(is_equal_approx(f.actor().rotation.y, deg_to_rad(YAW_DEG)))
	assert_true(BattleClips.play(f, &"ready"), "the entry and the dismissal's clip (choreo.json vowbound)")
	assert_eq(f.creature().current_clip, &"ready")
	assert_eq(BattleClips.action_clip(f, &"flare_line", &"magical"), &"special")
	assert_eq(BattleClips.action_clip(f, &"kite_flare", &"magical"), &"cast")
	assert_true(BattleClips.play(f, &"ko"), "the fall's clip")
	f.set_ko(true, 0.25, 0.35)
	assert_true(f.creature().is_ko())
	before_each()


func test_the_clips_follow_the_sheet() -> void:
	var a := _actor()
	var skel := _pose(a, &"idle", 0.0)
	var head0 := _bone_at(skel, "head")
	skel = _pose(a, &"idle", IDLE_QUARTER_SEC)
	assert_true(head0.distance_to(_bone_at(skel, "head")) > IDLE_SWAY_M, "she undulates")
	skel = _pose(a, &"rise", 0.0)
	assert_true(_bone_at(skel, "head").y < head0.y - FURLED_DROP_M, "the rise starts furled")
	skel = _pose(a, &"ko", INF)
	assert_true(_bone_at(skel, "head").y < head0.y - KO_DROOP_M, "the KO lets her head droop")
	assert_true(_turned(skel, "key", Vector3.DOWN).y < KEY_HANG_Y, "the keepsake still hangs")
	skel = _pose(a, &"attack", ATTACK_REAR_SEC)
	var reared := _bone_at(skel, "head")
	skel = _pose(a, &"attack", a.contact_time(&"attack"))
	var lashed := _bone_at(skel, "head")
	assert_true(lashed.z - reared.z > LASH_M and reared.y - lashed.y > LASH_M, "the head lashes forward and down")
	skel = _pose(a, &"special", SPECIAL_WOUND_SEC)
	assert_true(_bone_at(skel, "head").distance_to(_bone_at(skel, "streamer")) < WOUND_M, "she winds in first")
	skel = _pose(a, &"special", a.contact_time(&"special"))
	var head := _bone_at(skel, "head")
	var tail := _bone_at(skel, "streamer")
	assert_true(head.distance_to(tail) > LINE_M, "Flare Line pulls the whole kite-string taut")
	assert_true(head.y > tail.y and head.z > tail.z, "the line rises toward the foes")
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
