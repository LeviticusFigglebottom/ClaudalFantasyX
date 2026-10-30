extends TestCase
## M3-CRE-643: Hesk, the Cord-Keeper, Asha's Holy Vowbound, as a creature actor
## (docs/kb/art/creatures/vowbound/hesk.md). Her stand-in resolves to the model through creatures.json's `vowbound`
## row (CreatureModels, no enemies.json model), faces the foes as the heroes do and gives its own height and radius
## (UI's battle_sandbox.json has no row for her); the scene loads headless with every clip the stage plays; she stands
## on the water; and the clips do what the sheet says (half-folded at rest, the full span only when she spreads, the
## buffet swung forward, Pass-Cord swept down and forward, the KO settled on the water). Her light is the cords' and
## the eyes', glimmer_bound; the keth bundle is an object and never glows.

const SCENE := "res://game/creatures/hesk/hesk_battle.tscn"
const MATERIALS := "res://assets/creatures/hesk/materials/%s.tres"
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
## The stand-in's own size (creatures.json `stand_in`): about her perched height, and a ring round her talons.
const MIN_HEIGHT := 2.0
const MAX_RADIUS := 1.0
## Perched on the water: the planted talon's bone never rises above this, in any clip.
const PLANTED_Y := 0.15
const SAMPLES := 8
## Half-folded at rest: the two cord chains this close (x), and at least this much wider spread in Pass-Cord.
const REST_GAP_M := 2.2
const SPREAD_GAIN_M := 1.2
const SPREAD_SEC := 0.8
## The buffet: the near wing's hand swings at least this far forward from the draw-back to the contact.
const ATTACK_DRAW_SEC := 0.32
const BUFFET_M := 0.8
## Pass-Cord: from the spread to the contact the cords sweep at least this far down, and the head comes forward.
const SWEEP_DOWN_M := 0.8
const HEAD_FORWARD_M := 0.4
## The flinch draws the head down into the ruff by at least this much at its peak (0.1 s).
const FLINCH_M := 0.04
const HIT_PEAK_SEC := 0.1
## The KO settles her onto the water, the head bowed at least this far below its rest; the rise starts hunched.
const KO_BOW_M := 0.7
const HUNCH_M := 0.5
const FOLDED_GAP_M := 1.5
## The keth bundle hangs from the held talon: its lower bone's down axis this close to straight down in the idle.
const BUNDLE_HANG_Y := -0.9
const GLIMMER_BOUND := Color("#4FB3B0")
const BOUND_ENERGY := 1.2
const END_SEC := 0.001

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_the_vowbound_stand_in_resolves_to_the_model() -> void:
	var spec := BattleStage.stand_in_spec(&"hesk")
	assert_eq(str(spec.get("scene", "")), SCENE, "the stand-in shows the model, not the placeholder")
	assert_eq(CreatureModels.vowbound_creature("hesk"), &"hesk")
	assert_true(is_equal_approx(float(spec["yaw_deg"]), YAW_DEG), "she faces the foes, as the heroes do")
	assert_false(spec.has("hover"), "she stands on the water: no hover")
	assert_true(float(spec.get("height", 0.0)) > MIN_HEIGHT, "her own height for the VFX anchors")
	var r := float(spec.get("radius", 0.0))
	assert_true(r > 0.0 and r < MAX_RADIUS, "a ring round her talons")
	assert_false(CreatureModels.models().has("hesk"), "she is no enemy")
	assert_eq(CreatureModels.stand_in_overrides("ilun").get("scene", ""), "res://game/creatures/ilun/ilun_battle.tscn")
	before_each()


func test_the_scene_loads_headless_with_its_clips() -> void:
	var a := _actor()
	assert_eq(a.creature_id, &"hesk")
	assert_eq(a.current_clip, &"idle", "she idles")
	for clip in CLIPS:
		assert_true(a.has_clip(clip), "hesk has %s" % clip)
	assert_eq(a.clip_for(&"attack", &"physical"), &"attack", "the wing-buffet")
	for clip: StringName in [&"attack", &"cast", &"special"]:
		var t := a.contact_time(clip)
		assert_true(t > 0.0 and t < a.clip_length(clip), "%s lands inside the clip" % clip)
	before_each()


func test_the_stand_in_plays_the_stage_clips_on_the_model() -> void:
	var f := FighterStandIn.new()
	f.setup(&"hesk", BattleStage.stand_in_spec(&"hesk"), RING)
	_add(f)
	assert_true(f.has_actor() and f.creature() != null, "the model, not the placeholder")
	assert_true(is_equal_approx(f.actor().rotation.y, deg_to_rad(YAW_DEG)))
	assert_true(BattleClips.play(f, &"ready"), "the entry and the dismissal's clip (choreo.json vowbound)")
	assert_eq(f.creature().current_clip, &"ready")
	assert_true(BattleClips.play(f, &"ko"), "the fall's clip")
	f.set_ko(true, 0.25, 0.35)
	assert_true(f.creature().is_ko())
	before_each()


func test_she_stands_on_the_water_in_every_clip() -> void:
	var a := _actor()
	for clip in CLIPS:
		if clip == &"release":
			continue  # M3-CRE-647: the release is the one clip where she lifts off the water, by design
		var length := a.clip_length(clip)
		for k in SAMPLES + 1:
			var skel := _pose(a, clip, length * k / SAMPLES)
			assert_true(_bone_at(skel, "talon_r").y < PLANTED_Y, "%s keeps her talon on the water" % clip)
	before_each()


func test_the_clips_follow_the_sheet() -> void:
	var a := _actor()
	var skel := _pose(a, &"idle", 0.0)
	var head0 := _bone_at(skel, "head")
	var rest_gap := _cord_gap(skel)
	assert_true(rest_gap < REST_GAP_M, "half-folded at rest")
	assert_true(_turned(skel, "bundle_1", Vector3.DOWN).y < BUNDLE_HANG_Y, "the keth bundle hangs")
	skel = _pose(a, &"special", SPREAD_SEC)
	assert_true(_cord_gap(skel) > rest_gap + SPREAD_GAIN_M, "Pass-Cord opens the full span")
	var spread_cord := _bone_at(skel, "cord_l1")
	var spread_head := _bone_at(skel, "head")
	skel = _pose(a, &"special", a.contact_time(&"special"))
	assert_true(spread_cord.y - _bone_at(skel, "cord_l1").y > SWEEP_DOWN_M, "the wings sweep down")
	assert_true(_bone_at(skel, "head").z - spread_head.z > HEAD_FORWARD_M, "and she leans into it")
	skel = _pose(a, &"attack", ATTACK_DRAW_SEC)
	var drawn := _bone_at(skel, "wing_l2")
	skel = _pose(a, &"attack", a.contact_time(&"attack"))
	assert_true(_bone_at(skel, "wing_l2").z - drawn.z > BUFFET_M, "the near wing swings forward at the foes")
	skel = _pose(a, &"hit", HIT_PEAK_SEC)
	assert_true(head0.y - _bone_at(skel, "head").y > FLINCH_M, "the head drawn into the ruff")
	skel = _pose(a, &"ko", INF)
	assert_true(_bone_at(skel, "head").y < head0.y - KO_BOW_M, "the KO settles her onto the water")
	skel = _pose(a, &"rise", 0.0)
	assert_true(_bone_at(skel, "head").y < head0.y - HUNCH_M, "the rise starts hunched")
	assert_true(_cord_gap(skel) < FOLDED_GAP_M, "and folded")
	before_each()


func test_only_the_cords_and_eyes_carry_the_bound_light() -> void:
	for slot: String in ["cord", "ruff", "eye"]:
		var m := load(MATERIALS % slot) as ShaderMaterial
		assert_true(m != null, "%s has its material" % slot)
		if m == null:
			continue
		assert_true((m.get_shader_parameter("emission_color") as Color).is_equal_approx(GLIMMER_BOUND), slot)
		assert_true(is_equal_approx(float(m.get_shader_parameter("emission_energy")), BOUND_ENERGY), "steady")
	for slot: String in ["bundle", "plumage", "head"]:
		var m := load(MATERIALS % slot) as ShaderMaterial
		assert_true(
			m != null and is_zero_approx(float(m.get_shader_parameter("emission_energy"))), "%s is unlit" % slot
		)
	before_each()


func _cord_gap(skel: Skeleton3D) -> float:
	return _bone_at(skel, "cord_l1").x - _bone_at(skel, "cord_r1").x


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
