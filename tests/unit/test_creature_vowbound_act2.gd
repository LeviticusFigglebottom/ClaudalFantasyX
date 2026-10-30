extends TestCase
## The Act II Vowbound at final quality (ADR 0041 §3, ADR 0205) keep the hook contract battle presentation builds on,
## as the Act I Vowbound do (test_creature_bosses_act1.gd): the Vowbound clip set, one clip per skill on the design
## sheet with a wind-up before its contact, every clip played from idle's first frame, and the unweighted anchor
## bones `vfx_core` and `vfx_keepsake`. Each Vowbound's declarations and checks are prefixed with its id, helpers
## included, and no check relies on before_each, so the passes merge without touching each other.

## A strike's wind-up reads before its blow (docs/kb/plan/act2/bosses/README.md, the standard, item 3).
const VOWBOUND_WIND_UP_MIN_SEC := 0.45
const VOWBOUND_ACT2_ANCHORS: Array[StringName] = [&"vfx_core", &"vfx_keepsake"]

# --- Nhoa, the Ice Vowbound (M4-CRB-006, docs/kb/plan/act2/bosses/nhoa.md) ----------------------------------------

const NHOA: StringName = &"nhoa"
const NHOA_HELD: StringName = &"nhoa_held"
## The Vowbound contract, the held form's release, and one clip per skill on her move list: the sweep (`attack`),
## Silt-Fall (`cast`), Deep Well, the echo, and Farewell-Tide (`special`).
const NHOA_CLIPS: Array[StringName] = [
	&"idle",
	&"idle_b",
	&"ready",
	&"rise",
	&"dismiss",
	&"attack",
	&"cast",
	&"deep_well",
	&"echo",
	&"hit",
	&"hit_b",
	&"defend",
	&"ko",
	&"victory",
	&"special",
	&"release",
]
## Her striking clips, each with a creatures.json `contact` (both forms play the same GLB).
const NHOA_STRIKES: Array[StringName] = [&"attack", &"cast", &"deep_well", &"echo", &"special"]
## Clips that start where the idle starts (rise starts folded: it is the call, and nothing plays before it).
const NHOA_FROM_IDLE: Array[StringName] = [
	&"idle_b",
	&"ready",
	&"dismiss",
	&"attack",
	&"cast",
	&"deep_well",
	&"echo",
	&"hit",
	&"hit_b",
	&"defend",
	&"ko",
	&"victory",
	&"special",
	&"release",
]
## The one-shots that come back to where the idle starts (ko, dismiss and release end elsewhere by design).
const NHOA_BACK_TO_IDLE: Array[StringName] = [
	&"idle_b",
	&"ready",
	&"rise",
	&"attack",
	&"cast",
	&"deep_well",
	&"echo",
	&"hit",
	&"hit_b",
	&"defend",
	&"victory",
	&"special",
]
## The bones compared for "the same frame" (the far ends of every chain), and how close they must be.
const NHOA_ENDS: Array[String] = [
	"head", "antler_l1", "antler_r1", "hand_l", "hand_r", "strand_l2", "strand_r2", "strand_b2", "spine_2"
]
const NHOA_SAME_M := 0.005
const NHOA_STRANDS: Array[String] = ["strand_l2", "strand_r2", "strand_b2"]
## Farewell-Tide is the only finisher whose motes go up: at its contact she is lifted at least this far and every
## strand's end is drawn up above the hem.
const NHOA_TIDE_LIFT_M := 0.15
const NHOA_HEM_Y := 0.75
## Deep Well: she sinks at least this far by the end of the wind-up (0.9 s), then her hands sweep up from below at
## least this far by the contact.
const NHOA_WELL_LOW_SEC := 0.9
const NHOA_WELL_SINK_M := 0.2
const NHOA_WELL_SWEEP_M := 0.6
## The echo: from 0.3 s to 0.5 s she is mirror-still (the near hand moves less than this), her head cocked; then the
## near hand thrusts at least this far toward the foes (+z in her own frame) by the contact.
const NHOA_ECHO_STILL := Vector2(0.3, 0.5)
const NHOA_ECHO_STILL_M := 0.05
const NHOA_ECHO_COCK_DEG := 8.0
const NHOA_ECHO_THRUST_M := 0.25
const NHOA_END_SEC := 0.001


func test_nhoa_has_the_vowbound_clip_set_and_a_clip_per_skill() -> void:
	var made: Array[Node] = []
	for id: StringName in [NHOA, NHOA_HELD]:
		var a := _nhoa_actor(id, made)
		for clip in NHOA_CLIPS:
			assert_true(a.has_clip(clip), "%s has %s" % [id, clip])
		_nhoa_free(made)


func test_nhoa_each_strike_winds_up_before_its_contact() -> void:
	var made: Array[Node] = []
	for id: StringName in [NHOA, NHOA_HELD]:
		var a := _nhoa_actor(id, made)
		for clip in NHOA_STRIKES:
			var t := a.contact_time(clip)
			assert_true(t >= VOWBOUND_WIND_UP_MIN_SEC, "%s's %s winds up %.2f s before contact" % [id, clip, t])
			assert_true(t < a.clip_length(clip), "%s's %s lands inside the clip" % [id, clip])
		_nhoa_free(made)


func test_nhoa_has_her_unweighted_anchor_bones() -> void:
	var made: Array[Node] = []
	for id: StringName in [NHOA, NHOA_HELD]:
		var skel := _nhoa_skeleton(_nhoa_actor(id, made))
		for bone in VOWBOUND_ACT2_ANCHORS:
			assert_true(skel.find_bone(String(bone)) >= 0, "%s has the %s bone" % [id, bone])
		var weighted := _nhoa_weighted_bones(skel)
		assert_true(weighted.has("spine_2"), "%s's mesh is weighted (the check is live)" % id)
		for bone in VOWBOUND_ACT2_ANCHORS:
			assert_false(weighted.has(String(bone)), "%s's %s carries no vertices" % [id, bone])
	# where they sit: the core in her chest, the keepsake at the name-shell (under the head, on the throat's front)
	var skel := _nhoa_pose(_nhoa_actor(NHOA, made), &"idle", 0.0)
	var core := _nhoa_bone_at(skel, "vfx_core")
	var keep := _nhoa_bone_at(skel, "vfx_keepsake")
	assert_true(core.y > 1.4 and core.y < 1.8, "the core is in her chest (y %.2f)" % core.y)
	assert_true(keep.y > core.y and keep.y < _nhoa_bone_at(skel, "head").y, "the keepsake hangs at her throat")
	_nhoa_free(made)


func test_nhoa_every_clip_starts_where_the_idle_starts() -> void:
	var made: Array[Node] = []
	var a := _nhoa_actor(NHOA, made)
	var idle0 := _nhoa_ends_at(a, &"idle", 0.0)
	for clip in NHOA_FROM_IDLE:
		_nhoa_assert_same(_nhoa_ends_at(a, clip, 0.0), idle0, "%s starts on idle's first frame" % clip)
	for clip in NHOA_BACK_TO_IDLE:
		_nhoa_assert_same(_nhoa_ends_at(a, clip, INF), idle0, "%s ends on idle's first frame" % clip)
	_nhoa_free(made)


func test_nhoa_farewell_tide_lifts_her_and_draws_the_motes_up() -> void:
	var made: Array[Node] = []
	var a := _nhoa_actor(NHOA, made)
	var root0 := _nhoa_bone_at(_nhoa_pose(a, &"idle", 0.0), "root")
	var skel := _nhoa_pose(a, &"special", a.contact_time(&"special"))
	assert_true(_nhoa_bone_at(skel, "root").y > root0.y + NHOA_TIDE_LIFT_M, "Farewell-Tide lifts her")
	for bone in NHOA_STRANDS:
		assert_true(_nhoa_bone_at(skel, bone).y > NHOA_HEM_Y, "%s is drawn up over the hem" % bone)
	_nhoa_free(made)


func test_nhoa_deep_well_sinks_then_sweeps_up_from_below() -> void:
	var made: Array[Node] = []
	var a := _nhoa_actor(NHOA, made)
	var root0 := _nhoa_bone_at(_nhoa_pose(a, &"idle", 0.0), "root")
	var low := _nhoa_pose(a, &"deep_well", NHOA_WELL_LOW_SEC)
	assert_true(_nhoa_bone_at(low, "root").y < root0.y - NHOA_WELL_SINK_M, "she sinks in the wind-up")
	var hands_low := _nhoa_bone_at(low, "hand_l").y + _nhoa_bone_at(low, "hand_r").y
	var hit := _nhoa_pose(a, &"deep_well", a.contact_time(&"deep_well"))
	var hands_hit := _nhoa_bone_at(hit, "hand_l").y + _nhoa_bone_at(hit, "hand_r").y
	assert_true(hands_hit > hands_low + 2.0 * NHOA_WELL_SWEEP_M, "her arms sweep up from below by the contact")
	_nhoa_free(made)


func test_nhoa_echo_holds_mirror_still_then_thrusts() -> void:
	var made: Array[Node] = []
	var a := _nhoa_actor(NHOA, made)
	var basis := (_nhoa_skeleton(a).global_transform.basis).inverse()
	var h0 := _nhoa_bone_at(_nhoa_pose(a, &"echo", NHOA_ECHO_STILL.x), "hand_l")
	var skel := _nhoa_pose(a, &"echo", NHOA_ECHO_STILL.y)
	var h1 := _nhoa_bone_at(skel, "hand_l")
	assert_true(h0.distance_to(h1) < NHOA_ECHO_STILL_M, "the pause is mirror-still")
	var roll := rad_to_deg(skel.get_bone_pose_rotation(skel.find_bone("head")).get_euler().z)
	assert_true(absf(roll) > NHOA_ECHO_COCK_DEG, "her head is cocked toward the foe (%.1f deg)" % roll)
	var h2 := _nhoa_bone_at(_nhoa_pose(a, &"echo", a.contact_time(&"echo")), "hand_l")
	assert_true((basis * (h2 - h1)).z > NHOA_ECHO_THRUST_M, "the palm thrusts toward the foes by the contact")
	_nhoa_free(made)


func _nhoa_actor(id: StringName, made: Array[Node]) -> CreatureActor:
	var row := CreatureActor.row_for(id)
	var a := (load(str(row.get("scene", ""))) as PackedScene).instantiate() as CreatureActor
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(a)
	made.append(a)
	return a


func _nhoa_free(made: Array[Node]) -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()


func _nhoa_skeleton(a: Node) -> Skeleton3D:
	return a.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D


## Poses the actor's model at `sec` into `clip` (clamped to just before its end) and returns its skeleton.
func _nhoa_pose(a: CreatureActor, clip: StringName, sec: float) -> Skeleton3D:
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.play(clip)
	player.seek(minf(sec, player.get_animation(clip).length - NHOA_END_SEC), true)
	return _nhoa_skeleton(a)


func _nhoa_bone_at(skel: Skeleton3D, bone: String) -> Vector3:
	return (skel.global_transform * skel.get_bone_global_pose(skel.find_bone(bone))).origin


func _nhoa_ends_at(a: CreatureActor, clip: StringName, sec: float) -> Array[Vector3]:
	var skel := _nhoa_pose(a, clip, sec)
	var out: Array[Vector3] = []
	for bone in NHOA_ENDS:
		out.append(_nhoa_bone_at(skel, bone))
	return out


func _nhoa_assert_same(got: Array[Vector3], want: Array[Vector3], what: String) -> void:
	var worst := 0.0
	for i in got.size():
		worst = maxf(worst, got[i].distance_to(want[i]))
	assert_true(worst < NHOA_SAME_M, "%s (off by %.3f m)" % [what, worst])


## Names of the bones some vertex actually weights (> 0) in any skinned mesh under the skeleton.
func _nhoa_weighted_bones(skel: Skeleton3D) -> Dictionary:
	var out: Dictionary = {}
	for n: Node in skel.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.skin == null or mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var arrays := mi.mesh.surface_get_arrays(s)
			var bones: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
			var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
			for i in mini(bones.size(), weights.size()):
				if weights[i] > 0.0:
					var b := mi.skin.get_bind_name(bones[i])
					out[String(b) if b != &"" else skel.get_bone_name(mi.skin.get_bind_bone(bones[i]))] = true
	return out
