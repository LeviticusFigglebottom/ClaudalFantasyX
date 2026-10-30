extends TestCase
## The Act II bosses at final quality (ADR 0041 §3, ADR 0205) keep the hook contract battle presentation builds on,
## as the Act I bosses do (test_creature_bosses_act1.gd): the full clip set, an `intro` for the boss intro camera,
## one clip per skill with a wind-up before its contact, each phase's stance clips, and unweighted anchor bones.
## Each boss's checks are prefixed with its id.

const INTRO_MIN_SEC := 1.5
const INTRO_MAX_SEC := 3.5
## A strike's wind-up reads before its blow (docs/kb/plan/act2/bosses/README.md, the standard, item 3).
const WIND_UP_MIN_SEC := 0.45
const BOSS_ANCHORS: Array[StringName] = [&"vfx_wound", &"vfx_core", &"vfx_phase"]

## M4-CRB-004, the Wakefin (docs/kb/plan/act2/bosses/wakefin.md): one whole animal (ADR 0204: no fin target, no
## deck adds). Its skills' clips (combat maps the skills to them), the close circle's stance clips, and the KO.
const WAKEFIN: StringName = &"wakefin"
const WAKEFIN_CLIPS: Array[StringName] = [
	&"idle",
	&"idle_b",
	&"ready",
	&"intro",
	&"attack",
	&"cast",
	&"dive",
	&"rise_strike",
	&"wake_wash",
	&"hit",
	&"hit_b",
	&"ko",
	&"phase_close",
	&"idle_close",
	&"bill_strike_close",
]
const WAKEFIN_PHASE: StringName = &"close_circle"
## The close circle plays these in place of the wide circle's (its `clips` map).
const WAKEFIN_CLOSE: Array[StringName] = [
	&"attack", &"cast", &"dive", &"rise_strike", &"wake_wash", &"hit", &"hit_b", &"ready", &"ko"
]
## The striking clips (each has a `contact`).
const WAKEFIN_STRIKES: Array[StringName] = [
	&"attack", &"dive", &"rise_strike", &"wake_wash", &"bill_strike_close", &"phase_close"
]
## Sound Dive is evasion up, never untargetable (ADR 0204): through its hold the blade's top stays above the water
## (y 0 is the water line) by at least this much.
const WAKEFIN_DIVE_HOLD := Vector2(1.0, 2.0)
const WAKEFIN_DIVE_BLADE_MIN_Y := 0.3

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_wakefin_has_the_full_clip_set_and_its_close_circle_stance() -> void:
	var a := _wakefin_actor()
	for clip in WAKEFIN_CLIPS:
		assert_true(a.has_clip(clip), "the Wakefin has %s" % clip)
	for clip in WAKEFIN_CLOSE:
		assert_true(a.has_clip(StringName("%s_close" % clip)), "the close circle has its %s" % clip)
	before_each()


func test_wakefin_intro_fits_the_camera_hold() -> void:
	var sec := _wakefin_actor().clip_length(&"intro")
	assert_true(sec >= INTRO_MIN_SEC and sec <= INTRO_MAX_SEC, "the Wakefin's intro is %.2f s" % sec)
	before_each()


func test_wakefin_strikes_wind_up_before_contact() -> void:
	var a := _wakefin_actor()
	for clip in WAKEFIN_STRIKES:
		var c := a.contact_time(clip)
		assert_true(
			c >= WIND_UP_MIN_SEC and c < a.clip_length(clip), "%s lands at %.2f s, after its wind-up" % [clip, c]
		)
	before_each()


func test_wakefin_has_its_vfx_anchor_bones_unweighted() -> void:
	var a := _wakefin_actor()
	var skel := _wakefin_skeleton(a)
	for bone in BOSS_ANCHORS:
		assert_true(skel.find_bone(String(bone)) >= 0, "the Wakefin has the %s bone" % bone)
	var weighted := _wakefin_weighted_bones(skel)
	assert_true(weighted.has("spine_3"), "its mesh is weighted to its spine (the check is live)")
	for bone in BOSS_ANCHORS:
		assert_false(weighted.has(String(bone)), "the Wakefin's %s carries no vertices" % bone)
	assert_true(skel.find_bone("breach") >= 0, "its travel runs on a breach root")
	assert_true(a.vfx_anchor(&"core") != Vector3.INF and a.vfx_anchor(&"wound") != Vector3.INF, "anchors resolve")
	before_each()


func test_wakefin_is_one_animal_with_no_breakable_part() -> void:
	# ADR 0204: the fin is never a separate target; nothing of it breaks off as a part
	var a := _wakefin_actor()
	assert_true((CreatureActor.row_for(WAKEFIN).get("break_parts", {}) as Dictionary).is_empty(), "no parts")
	assert_false(a.set_part_broken(&"fin", true), "no fin part to break")
	before_each()


func test_wakefin_close_circle_plays_its_stance_and_tears_the_tip() -> void:
	var a := _wakefin_actor()
	var tip := a.find_child("BladeTip", true, false) as Node3D
	assert_true(tip != null and tip.visible, "the blade is whole in the wide circle")
	assert_true(a.enter_phase(WAKEFIN_PHASE, true))
	for clip in WAKEFIN_CLOSE:
		assert_eq(a.phase_clip(clip), StringName("%s_close" % clip), "the close circle's %s" % clip)
	assert_true(is_equal_approx(a.contact_time(&"attack"), a.contact_time(&"attack_close")), "the cut lands the same")
	assert_false(tip.visible, "the tip tore off on the hull")
	before_each()


func test_wakefin_dive_keeps_the_blade_in_view() -> void:
	var a := _wakefin_actor()
	var skel := _wakefin_skeleton(a)
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var tip := skel.find_bone("blade_tip")
	for clip: StringName in [&"dive", &"dive_close"]:
		player.play(clip)
		for k in 5:
			player.seek(lerpf(WAKEFIN_DIVE_HOLD.x, WAKEFIN_DIVE_HOLD.y, k / 4.0), true)
			var y := (skel.global_transform * skel.get_bone_global_pose(tip)).origin.y
			assert_true(
				y > WAKEFIN_DIVE_BLADE_MIN_Y, "%s: the blade's top cuts the water while under (%.2f)" % [clip, y]
			)
	before_each()


func _wakefin_actor() -> CreatureActor:
	var row := CreatureActor.row_for(WAKEFIN)
	var a := (load(str(row.get("scene", ""))) as PackedScene).instantiate() as CreatureActor
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(a)
	made.append(a)
	return a


func _wakefin_skeleton(a: Node) -> Skeleton3D:
	return a.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D


## Names of the bones some vertex actually weights (> 0) in any skinned mesh under the skeleton.
func _wakefin_weighted_bones(skel: Skeleton3D) -> Dictionary:
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
