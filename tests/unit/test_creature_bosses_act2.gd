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
## Its full clip set: the contract clips, one clip per skill on the sheet's move list, and the `opened` versions that
## phase plays through its `clips` map.
const LAMP_ENGINE_CLIPS: Array[StringName] = [
	&"idle",
	&"idle_b",
	&"ready",
	&"intro",
	&"attack",
	&"cast",
	&"lamp_gather",
	&"lamp_burn",
	&"call",
	&"twin_trim",
	&"hit",
	&"hit_b",
	&"ko",
	&"phase_change",
	&"idle_opened",
	&"ready_opened",
	&"attack_opened",
	&"cast_opened",
	&"lamp_gather_opened",
	&"lamp_burn_opened",
	&"call_opened",
	&"twin_trim_opened",
	&"hit_opened",
	&"hit_b_opened",
	&"ko_opened"
]
## The striking clips (each with a contact beat) and what the `opened` phase plays for them.
const LAMP_ENGINE_STRIKES: Array[StringName] = [&"attack", &"cast", &"lamp_gather", &"lamp_burn", &"call", &"twin_trim"]
const LAMP_ENGINE_ANCHORS: Array[StringName] = [&"vfx_wound", &"vfx_core", &"vfx_phase"]
## The intro plays under the boss_tall hold (choreo.json by_enemy lamp_engine, 2.4 s, plus its ease-in).
const LAMP_ENGINE_INTRO_MIN_SEC := 1.5
const LAMP_ENGINE_INTRO_MAX_SEC := 3.5
## The move-pass rule: a wind-up of at least this long reads before contact.
const LAMP_ENGINE_WIND_UP_SEC := 0.45
## M4-CRB-002: the Mangrove Drowner (Ch10; docs/kb/plan/act2/bosses/mangrove_drowner.md "Move list").
const MANGROVE_DROWNER := &"mangrove_drowner"
const MANGROVE_DROWNER_CLIPS: Array[StringName] = [
	&"idle",
	&"idle_b",
	&"ready",
	&"intro",
	&"attack",
	&"cast",
	&"rising_water",
	&"snag",
	&"hit",
	&"hit_b",
	&"snag_break",
	&"ko",
	&"phase_change",
	&"idle_risen",
	&"ready_risen",
	&"attack_risen",
	&"cast_risen",
	&"rising_water_risen",
	&"snag_risen",
	&"root_stamp_risen",
	&"hit_risen",
	&"hit_b_risen",
	&"snag_break_risen",
	&"ko_risen"
]
## Each striking clip and its contact (creatures.json `contact`): the wind-up before it is at least the move rule's.
const MANGROVE_DROWNER_STRIKES: Array[StringName] = [
	&"attack",
	&"rising_water",
	&"snag",
	&"attack_risen",
	&"cast_risen",
	&"rising_water_risen",
	&"snag_risen",
	&"root_stamp_risen"
]
const MANGROVE_DROWNER_PHASE := &"uprooted"
## The two snag roots (the break parts): each part's whole and broken nodes.
const MANGROVE_DROWNER_PARTS: Array[StringName] = [&"SnagA", &"SnagABroken", &"SnagB", &"SnagBBroken"]
## M4-CRB-005, the Avalanche Ram (docs/kb/plan/act2/bosses/avalanche_ram.md): its skills' clips (combat maps the skills
## to them), the torn_fleece phase's stance clips through its `clips` map, and the KO.
const AVALANCHE_RAM: StringName = &"avalanche_ram"
const AVALANCHE_RAM_CLIPS: Array[StringName] = [
	&"idle",
	&"idle_b",
	&"ready",
	&"intro",
	&"charge_gather",
	&"attack",
	&"cast",
	&"neck_sweep",
	&"fleece_shake",
	&"hit",
	&"hit_b",
	&"ko",
	&"phase_tear",
	&"idle_torn",
]
const AVALANCHE_RAM_PHASE: StringName = &"torn_fleece"
## The torn stance plays these in place of the whole fleece's (its `clips` map).
const AVALANCHE_RAM_TORN: Array[StringName] = [
	&"attack", &"cast", &"charge_gather", &"neck_sweep", &"fleece_shake", &"hit", &"hit_b", &"ready", &"ko"
]
## The striking clips (each has a `contact`): the charge, the bellow, the sweep, the shake, and the tear's slam.
const AVALANCHE_RAM_STRIKES: Array[StringName] = [&"attack", &"cast", &"neck_sweep", &"fleece_shake", &"phase_tear"]
## Clips that start or end away from their idle's first frame: the intro starts at the seep pool, phase_tear ends on
## the torn idle's (checked as such), the KOs end lying down, and `ready` is a loop entered by the row's blend.
const AVALANCHE_RAM_FREE_START: Array[StringName] = [&"intro", &"ready", &"ready_torn"]
const AVALANCHE_RAM_FREE_END: Array[StringName] = [&"ko", &"ko_torn", &"ready", &"ready_torn"]
## Clips whose hooves never leave the ground (only the charge, the stamp, the paw and the rear lift one).
const AVALANCHE_RAM_PLANTED: Array[StringName] = [
	&"idle", &"idle_b", &"cast", &"neck_sweep", &"fleece_shake", &"hit", &"hit_b", &"idle_torn", &"cast_torn"
]
const AVALANCHE_RAM_POSE_TOL_M := 0.01
const AVALANCHE_RAM_HOOF_TOL_M := 0.02
const FLAT_ENGINE: StringName = &"flat_engine"
## Its clip set: running, the flat pulse (`cast`; `attack` is its copy), the hits, the stop, and the broken stance
## its `broken` phase plays through its `clips` map.
const FLAT_ENGINE_CLIPS: Array[StringName] = [
	&"idle",
	&"idle_b",
	&"intro",
	&"ready",
	&"attack",
	&"cast",
	&"hit",
	&"hit_b",
	&"ko",
	&"break",
	&"idle_broken",
	&"hit_broken",
	&"hit_b_broken",
	&"ko_broken",
]
const FLAT_ENGINE_PHASE: StringName = &"broken"
const FLAT_ENGINE_BROKEN_MAP := {
	&"hit": &"hit_broken", &"hit_b": &"hit_b_broken", &"ko": &"ko_broken", &"ready": &"idle_broken"
}
const FLAT_ENGINE_STRIKES: Array[StringName] = [&"attack", &"cast", &"break"]
## Clips that start on the running idle's first frame and end there (`break` starts there and ends on the broken
## stance); the broken stance's clips start (and the hits end) on idle_broken's first frame.
const FLAT_ENGINE_WHOLE: Array[StringName] = [&"idle_b", &"intro", &"ready", &"attack", &"cast", &"hit", &"hit_b"]
const FLAT_ENGINE_BROKEN: Array[StringName] = [&"hit_broken", &"hit_b_broken"]
const FLAT_ENGINE_POSE_TOL_M := 0.01
## The broken stance reads as broken at battle distance: each drum half tipped out at least this far, the stack
## knocked over at least this far, and the two jammed paddles up off the water at least this far (degrees).
const FLAT_ENGINE_SPLIT_MIN_DEG := 12.0
const FLAT_ENGINE_STACK_MIN_DEG := 20.0
const FLAT_ENGINE_JAMMED: Array[String] = ["paddle1", "paddle6"]
const FLAT_ENGINE_JAM_MIN_DEG := 20.0
const FLAT_ENGINE_WATER_TOL_M := 0.02
## M4: every skill combat gives an Act II boss (enemies.json, its phases, and each charge's release) plays a clip the
## model has, in every phase that can use it (creatures.json clip_by_skill, then the phase's `clips` map).
const ACT2_BOSSES: Array[StringName] = [&"mangrove_drowner", &"lamp_engine", &"avalanche_ram", &"wakefin"]
const ACT2_ENEMIES_PATH := "res://game/data/battle/enemies.json"
const ACT2_SKILLS_PATH := "res://game/data/battle/skills.json"
## ADR 0204 §5: the Act II people bosses stand in through the characters track's battle actors, as Moll does. Once
## the actor is on the branch, the fight seats it as a real body, not a capsule.
const ACT2_PEOPLE_BOSSES := {&"malcor_venn": "res://game/characters/foes/venn_battle.tscn"}

var made: Array[Node] = []
var lamp_engine_made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()
	for n in lamp_engine_made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	lamp_engine_made.clear()


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


func test_lamp_engine_has_the_full_clip_set() -> void:
	var a := _lamp_engine_actor()
	for clip in LAMP_ENGINE_CLIPS:
		assert_true(a.has_clip(clip), "the Lamp Engine has %s" % clip)
	before_each()


func test_lamp_engine_intro_fits_the_camera_hold() -> void:
	var sec := _lamp_engine_actor().clip_length(&"intro")
	assert_between(sec, LAMP_ENGINE_INTRO_MIN_SEC, LAMP_ENGINE_INTRO_MAX_SEC, "its intro is %.2f s" % sec)
	before_each()


func test_lamp_engine_has_its_vfx_anchor_bones() -> void:
	var a := _lamp_engine_actor()
	var found := a.find_children("*", "Skeleton3D", true, false)
	assert_false(found.is_empty(), "it has a skeleton")
	if found.is_empty():
		return
	var skel := found[0] as Skeleton3D
	var weighted := _lamp_engine_weighted_bones(skel)
	assert_false(weighted.is_empty(), "its mesh is weighted to some bones (the check is live)")
	for bone in LAMP_ENGINE_ANCHORS:
		assert_true(skel.find_bone(String(bone)) >= 0, "it has the %s bone" % bone)
		assert_false(weighted.has(String(bone)), "%s carries no vertices" % bone)
	assert_true(a.vfx_anchor(&"wound").is_finite(), "spawn and death effects find its wound")
	before_each()


func test_lamp_engine_strikes_wind_up_before_contact() -> void:
	var a := _lamp_engine_actor()
	for clip in LAMP_ENGINE_STRIKES:
		var c := a.contact_time(clip)
		assert_true(c >= LAMP_ENGINE_WIND_UP_SEC, "%s lands at %.2f s, after its wind-up" % [clip, c])
		assert_true(c < a.clip_length(clip), "%s lands inside its clip" % clip)
	before_each()


func test_lamp_engine_plays_every_move_from_its_open_stance() -> void:
	var a := _lamp_engine_actor()
	assert_true(a.enter_phase(&"opened"))
	a.settle()
	assert_eq(a.current_clip, &"idle_opened")
	var mapped: Array[StringName] = []
	mapped.append_array(LAMP_ENGINE_STRIKES)
	mapped.append_array([&"hit", &"hit_b", &"ready", &"ko"] as Array[StringName])
	for clip in mapped:
		assert_eq(a.phase_clip(clip), StringName("%s_opened" % clip), "open, %s plays from the open stance" % clip)
	for clip in LAMP_ENGINE_STRIKES:
		var c := a.contact_time(clip)
		assert_true(c >= LAMP_ENGINE_WIND_UP_SEC, "open, %s lands at %.2f s, after its wind-up" % [clip, c])
	before_each()


func _lamp_engine_actor() -> CreatureActor:
	var row := CreatureActor.row_for(&"lamp_engine")
	var a := (load(str(row.get("scene", ""))) as PackedScene).instantiate() as CreatureActor
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(a)
	lamp_engine_made.append(a)
	return a


## Names of the bones some vertex actually weights (> 0) in any skinned mesh under the skeleton (the kit binds every
## bone in the skin, so the binds alone say nothing; the vertex arrays do).
func _lamp_engine_weighted_bones(skel: Skeleton3D) -> Dictionary:
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


func test_mangrove_drowner_has_the_full_clip_set() -> void:
	var a := _mangrove_drowner_actor(MANGROVE_DROWNER)
	for clip in MANGROVE_DROWNER_CLIPS:
		assert_true(a.has_clip(clip), "mangrove_drowner has %s" % clip)
	before_each()


func test_mangrove_drowner_intro_fits_the_camera_hold() -> void:
	var sec := _mangrove_drowner_actor(MANGROVE_DROWNER).clip_length(&"intro")
	assert_true(sec >= INTRO_MIN_SEC and sec <= INTRO_MAX_SEC, "mangrove_drowner intro is %.2f s" % sec)
	before_each()


func test_mangrove_drowner_strikes_wind_up_before_contact() -> void:
	var a := _mangrove_drowner_actor(MANGROVE_DROWNER)
	var contact := CreatureActor.row_for(MANGROVE_DROWNER).get("contact", {}) as Dictionary
	for clip in MANGROVE_DROWNER_STRIKES:
		var at := float(contact.get(String(clip), -1.0))
		assert_true(at >= WIND_UP_MIN_SEC, "%s lands at %.2f s, after a %.2f s wind-up" % [clip, at, WIND_UP_MIN_SEC])
		assert_true(at < a.clip_length(clip), "%s lands inside its %.2f s" % [clip, a.clip_length(clip)])
	before_each()


func test_mangrove_drowner_phase_maps_every_clip_to_its_risen_stance() -> void:
	var a := _mangrove_drowner_actor(MANGROVE_DROWNER)
	assert_true(a.enter_phase(MANGROVE_DROWNER_PHASE, true), "it enters uprooted")
	for clip: StringName in [&"attack", &"cast", &"hit", &"hit_b", &"ready", &"ko", &"snag", &"rising_water"]:
		var mapped := a.phase_clip(clip)
		assert_eq(String(mapped), "%s_risen" % clip, "uprooted plays %s for %s" % [mapped, clip])
		assert_true(a.has_clip(mapped), "it has %s" % mapped)
	before_each()


func test_mangrove_drowner_has_its_vfx_anchor_bones() -> void:
	var skel := _mangrove_drowner_skeleton(_mangrove_drowner_actor(MANGROVE_DROWNER))
	assert_true(skel != null, "mangrove_drowner has a skeleton")
	if skel == null:
		return
	var weighted := _mangrove_drowner_weighted_bones(skel)
	assert_false(weighted.is_empty(), "its mesh is weighted to some bones (the check is live)")
	for bone in BOSS_ANCHORS:
		assert_true(skel.find_bone(String(bone)) >= 0, "mangrove_drowner has the %s bone" % bone)
		assert_false(weighted.has(String(bone)), "its %s carries no vertices" % bone)
	before_each()


func test_mangrove_drowner_snag_roots_start_whole() -> void:
	var a := _mangrove_drowner_actor(MANGROVE_DROWNER)
	for part in MANGROVE_DROWNER_PARTS:
		var node := a.find_child(String(part), true, false) as Node3D
		assert_true(node != null, "it has the %s node" % part)
		if node != null:
			assert_eq(node.visible, not String(part).ends_with("Broken"), "%s starts %s" % [part, node.visible])
	before_each()


func _mangrove_drowner_actor(id: StringName) -> CreatureActor:
	var row := CreatureActor.row_for(id)
	var a := (load(str(row.get("scene", ""))) as PackedScene).instantiate() as CreatureActor
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(a)
	made.append(a)
	return a


func _mangrove_drowner_skeleton(a: Node) -> Skeleton3D:
	var found := a.find_children("*", "Skeleton3D", true, false)
	return found[0] as Skeleton3D if not found.is_empty() else null


## Bones some skinned vertex is bound to (as in test_creature_bosses_act1.gd).
func _mangrove_drowner_weighted_bones(skel: Skeleton3D) -> Dictionary:
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
					out[_mangrove_drowner_bind_bone_name(skel, mi.skin, bones[i])] = true
	return out


func _mangrove_drowner_bind_bone_name(skel: Skeleton3D, skin: Skin, bind: int) -> String:
	var b := skin.get_bind_name(bind)
	return String(b) if b != &"" else skel.get_bone_name(skin.get_bind_bone(bind))


func test_avalanche_ram_has_the_full_clip_set_and_its_torn_stance() -> void:
	var a := _avalanche_ram_actor()
	for clip in AVALANCHE_RAM_CLIPS:
		assert_true(a.has_clip(clip), "the Avalanche Ram has %s" % clip)
	for clip in AVALANCHE_RAM_TORN:
		assert_true(a.has_clip(StringName("%s_torn" % clip)), "the torn stance has its %s" % clip)
	before_each()


func test_avalanche_ram_intro_fits_the_camera_hold() -> void:
	var sec := _avalanche_ram_actor().clip_length(&"intro")
	assert_true(sec >= INTRO_MIN_SEC and sec <= INTRO_MAX_SEC, "the Avalanche Ram's intro is %.2f s" % sec)
	before_each()


func test_avalanche_ram_strikes_wind_up_before_contact() -> void:
	var a := _avalanche_ram_actor()
	for phase: StringName in [&"", AVALANCHE_RAM_PHASE]:
		if phase != &"":
			assert_true(a.enter_phase(phase, true))
		for clip in AVALANCHE_RAM_STRIKES:
			if phase != &"" and clip == &"phase_tear":
				continue
			var c := a.contact_time(clip)
			var played := a.phase_clip(clip)
			assert_true(
				c >= WIND_UP_MIN_SEC and c < a.clip_length(played),
				"%s lands at %.2f s, after its wind-up" % [played, c]
			)
	before_each()


func test_avalanche_ram_has_its_vfx_anchor_bones_unweighted() -> void:
	var a := _avalanche_ram_actor()
	var skel := _wakefin_skeleton(a)
	for bone in BOSS_ANCHORS:
		assert_true(skel.find_bone(String(bone)) >= 0, "the Avalanche Ram has the %s bone" % bone)
	var weighted := _wakefin_weighted_bones(skel)
	assert_true(weighted.has("spine3"), "its mesh is weighted to its spine (the check is live)")
	for bone in BOSS_ANCHORS:
		assert_false(weighted.has(String(bone)), "the Avalanche Ram's %s carries no vertices" % bone)
	assert_true(weighted.has("cord"), "the herd-cord's frayed end swings on its cord bone")
	assert_true(weighted.has("plate"), "the felted shoulder plate rides its own bone, so it can tear off")
	assert_true(a.vfx_anchor(&"core") != Vector3.INF and a.vfx_anchor(&"wound") != Vector3.INF, "anchors resolve")
	before_each()


func test_avalanche_ram_torn_fleece_plays_its_stance_and_tears_the_plate() -> void:
	var a := _avalanche_ram_actor()
	var plate := a.find_child("ShoulderPlate", true, false) as Node3D
	var torn := a.find_child("TornShoulder", true, false) as Node3D
	assert_true(plate != null and plate.visible, "the fleece is whole before the tear")
	assert_true(torn != null and not torn.visible, "the torn shoulder waits for its phase")
	assert_true(a.enter_phase(AVALANCHE_RAM_PHASE, true))
	for clip in AVALANCHE_RAM_TORN:
		assert_eq(a.phase_clip(clip), StringName("%s_torn" % clip), "the torn stance's %s" % clip)
	assert_true(is_equal_approx(a.contact_time(&"attack"), 0.75), "the charge still lands at 0.75 s")
	assert_false(plate.visible, "the plate tore off and lies hidden")
	assert_true(torn.visible, "the torn shoulder shows the seep")
	before_each()


func test_avalanche_ram_clips_start_and_end_on_their_idle() -> void:
	# docs/kb/plan/act2/bosses/README.md, the standard, item 4: nothing pops back to another pose
	var a := _avalanche_ram_actor()
	var skel := _wakefin_skeleton(a)
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var idle := _avalanche_ram_pose(player, skel, &"idle", 0.0)
	var idle_torn := _avalanche_ram_pose(player, skel, &"idle_torn", 0.0)
	for clip: StringName in player.get_animation_list():
		var torn := String(clip).ends_with("_torn")
		var length := player.get_animation(clip).length
		if not AVALANCHE_RAM_FREE_START.has(clip):
			var off := _avalanche_ram_pose_gap(
				_avalanche_ram_pose(player, skel, clip, 0.0), idle_torn if torn else idle
			)
			assert_true(off < AVALANCHE_RAM_POSE_TOL_M, "%s starts on its idle (%.3f m off)" % [clip, off])
		if not AVALANCHE_RAM_FREE_END.has(clip):
			var end_on := idle_torn if torn or clip == &"phase_tear" else idle
			var off := _avalanche_ram_pose_gap(_avalanche_ram_pose(player, skel, clip, length), end_on)
			assert_true(off < AVALANCHE_RAM_POSE_TOL_M, "%s ends on its idle (%.3f m off)" % [clip, off])
	before_each()


func test_avalanche_ram_keeps_its_hooves_planted() -> void:
	var a := _avalanche_ram_actor()
	var skel := _wakefin_skeleton(a)
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	for clip in AVALANCHE_RAM_PLANTED:
		for k in 9:
			player.play(clip, 0.0)
			player.seek(player.get_animation(clip).length * k / 8.0, true)
			for leg in ["fl", "fr", "bl", "br"]:
				var b := skel.find_bone("%s_foot" % leg)
				var moved := skel.get_bone_global_pose(b).origin.distance_to(skel.get_bone_global_rest(b).origin)
				assert_true(
					moved < AVALANCHE_RAM_HOOF_TOL_M, "%s keeps the %s hoof planted (%.3f m)" % [clip, leg, moved]
				)
	before_each()


func _avalanche_ram_actor() -> CreatureActor:
	var row := CreatureActor.row_for(AVALANCHE_RAM)
	var a := (load(str(row.get("scene", ""))) as PackedScene).instantiate() as CreatureActor
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(a)
	made.append(a)
	return a


## Every bone's position (model space) at `t` into `clip`, the shoulder plate's left out (it is hidden once torn).
func _avalanche_ram_pose(player: AnimationPlayer, skel: Skeleton3D, clip: StringName, t: float) -> Dictionary:
	player.play(clip, 0.0)
	player.seek(t, true)
	var out: Dictionary = {}
	for b in skel.get_bone_count():
		if skel.get_bone_name(b) != "plate":
			var g := skel.get_bone_global_pose(b)
			out[b] = [g.origin, g.origin + g.basis.y * 0.25]  # its head and a point along it (its turn shows)
	return out


func _avalanche_ram_pose_gap(a: Dictionary, b: Dictionary) -> float:
	var worst := 0.0
	for k: Variant in a:
		for i in 2:
			worst = maxf(worst, (a[k][i] as Vector3).distance_to(b[k][i] as Vector3))
	return worst


func test_flat_engine_has_the_full_clip_set() -> void:
	var a := _flat_engine_actor()
	for clip in FLAT_ENGINE_CLIPS:
		assert_true(a.has_clip(clip), "the flat-engine has %s" % clip)
	var sec := a.clip_length(&"intro")
	assert_between(sec, INTRO_MIN_SEC, INTRO_MAX_SEC, "its intro is %.2f s" % sec)
	before_each()


func test_flat_engine_pulse_winds_up_before_contact() -> void:
	var a := _flat_engine_actor()
	for clip in FLAT_ENGINE_STRIKES:
		var c := a.contact_time(clip)
		assert_true(
			c >= WIND_UP_MIN_SEC and c < a.clip_length(clip), "%s lands at %.2f s, after its wind-up" % [clip, c]
		)
	before_each()


func test_flat_engine_has_its_vfx_anchor_bones_unweighted() -> void:
	var a := _flat_engine_actor()
	var skel := _wakefin_skeleton(a)
	for bone in BOSS_ANCHORS:
		assert_true(skel.find_bone(String(bone)) >= 0, "the flat-engine has the %s bone" % bone)
	var weighted := _wakefin_weighted_bones(skel)
	assert_true(weighted.has("half_a"), "its drum is weighted to its halves (the check is live)")
	for bone in BOSS_ANCHORS:
		assert_false(weighted.has(String(bone)), "the flat-engine's %s carries no vertices" % bone)
	assert_true(a.vfx_anchor(&"core") != Vector3.INF and a.vfx_anchor(&"wound") != Vector3.INF, "anchors resolve")
	before_each()


func test_flat_engine_broken_phase_swaps_the_lights_and_holds_the_broken_stance() -> void:
	var a := _flat_engine_actor()
	var whole := a.find_child("Engine", true, false) as Node3D
	var broken := a.find_child("EngineBroken", true, false) as Node3D
	assert_true(whole.visible and not broken.visible, "it runs whole: the lit window and hinge marks")
	assert_true(a.enter_phase(FLAT_ENGINE_PHASE))
	assert_eq(a.current_clip, &"break", "the break plays")
	assert_true(broken.visible and not whole.visible, "the window goes dark on the break's first frame")
	for clip: StringName in FLAT_ENGINE_BROKEN_MAP:
		assert_eq(a.phase_clip(clip), FLAT_ENGINE_BROKEN_MAP[clip], "the broken stance's %s" % clip)
	var skel := _wakefin_skeleton(a)
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	for clip: StringName in [&"idle_broken", &"hit_broken", &"ko_broken"]:
		player.play(clip, 0.0)
		player.seek(0.0, true)
		for h in ["half_a", "half_b"]:
			assert_true(_flat_engine_turn(skel, h) > FLAT_ENGINE_SPLIT_MIN_DEG, "%s: the drum split (%s)" % [clip, h])
		assert_true(_flat_engine_turn(skel, "chimney") > FLAT_ENGINE_STACK_MIN_DEG, "%s: the stack over" % clip)
		for p in FLAT_ENGINE_JAMMED:
			assert_true(_flat_engine_turn(skel, p) > FLAT_ENGINE_JAM_MIN_DEG, "%s: %s jammed up" % [clip, p])
		for b in skel.get_bone_count():
			var y := (skel.global_transform * skel.get_bone_global_pose(b)).origin.y
			assert_true(y > -FLAT_ENGINE_WATER_TOL_M, "%s: %s stays on the water" % [clip, skel.get_bone_name(b)])
	before_each()


func test_flat_engine_clips_start_and_end_on_their_stance() -> void:
	var a := _flat_engine_actor()
	var skel := _wakefin_skeleton(a)
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var idle := _avalanche_ram_pose(player, skel, &"idle", 0.0)
	var idle_broken := _avalanche_ram_pose(player, skel, &"idle_broken", 0.0)
	var cases: Array = []
	for clip in FLAT_ENGINE_WHOLE:
		cases.append([clip, idle, idle])
	for clip in FLAT_ENGINE_BROKEN:
		cases.append([clip, idle_broken, idle_broken])
	cases.append([&"break", idle, idle_broken])
	cases.append([&"ko", idle, null])
	cases.append([&"ko_broken", idle_broken, null])
	for c: Array in cases:
		var clip: StringName = c[0]
		var length := player.get_animation(clip).length
		var off := _avalanche_ram_pose_gap(_avalanche_ram_pose(player, skel, clip, 0.0), c[1])
		assert_true(off < FLAT_ENGINE_POSE_TOL_M, "%s starts on its stance (%.3f m off)" % [clip, off])
		if c[2] != null:
			off = _avalanche_ram_pose_gap(_avalanche_ram_pose(player, skel, clip, length), c[2])
			assert_true(off < FLAT_ENGINE_POSE_TOL_M, "%s ends on its stance (%.3f m off)" % [clip, off])
	before_each()


func _flat_engine_actor() -> CreatureActor:
	var row := CreatureActor.row_for(FLAT_ENGINE)
	var a := (load(str(row.get("scene", ""))) as PackedScene).instantiate() as CreatureActor
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(a)
	made.append(a)
	return a


## How far a bone is turned from its rest (degrees).
func _flat_engine_turn(skel: Skeleton3D, bone: String) -> float:
	var b := skel.find_bone(bone)
	return rad_to_deg(skel.get_bone_rest(b).basis.get_rotation_quaternion().angle_to(skel.get_bone_pose_rotation(b)))


func test_act2_boss_skills_each_play_a_clip_the_model_has() -> void:
	var skills := {}
	for row: Dictionary in _act2_json(ACT2_SKILLS_PATH).get("skills", []) as Array:
		skills[str(row.get("id", ""))] = row
	for row: Dictionary in _act2_json(ACT2_ENEMIES_PATH).get("enemies", []) as Array:
		var id := StringName(str(row.get("id", "")))
		if not ACT2_BOSSES.has(id):
			continue
		var a := _act2_actor(id)
		var phases: Array[StringName] = [&""]
		var used: Array = (row.get("skills", []) as Array).duplicate()
		for ph: Dictionary in row.get("phases", []) as Array:
			phases.append(StringName(str(ph.get("id", ""))))
			used.append_array(ph.get("skills", []) as Array)
		for sid: Variant in used.duplicate():
			var release := str(
				((skills.get(str(sid), {}) as Dictionary).get("charge", {}) as Dictionary).get("skill", "")
			)
			if release != "":
				used.append(release)
		for sid: Variant in used:
			var skill: Dictionary = skills.get(str(sid), {})
			assert_false(skill.is_empty(), "%s's %s is a skill" % [id, sid])
			var clip := a.clip_for(StringName(str(sid)), StringName(str(skill.get("kind", ""))))
			assert_true(clip != &"", "%s's %s names a clip" % [id, sid])
			for ph in phases:
				if ph != &"":
					a.enter_phase(ph, true)
				assert_true(
					a.has_clip(a.phase_clip(clip)), "%s's %s plays %s in %s" % [id, sid, a.phase_clip(clip), ph]
				)
	before_each()


func _act2_json(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed as Dictionary if parsed is Dictionary else {}


func _act2_actor(id: StringName) -> CreatureActor:
	var row := CreatureActor.row_for(id)
	var a := (load(str(row.get("scene", ""))) as PackedScene).instantiate() as CreatureActor
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(a)
	made.append(a)
	return a


func test_act2_people_bosses_stand_in_through_their_battle_actors() -> void:
	for id: StringName in ACT2_PEOPLE_BOSSES:
		var scene := str(BattleStage.stand_in_spec(id).get("scene", ""))
		assert_eq(scene, ACT2_PEOPLE_BOSSES[id], "%s stands in through its battle actor" % id)
		if not ResourceLoader.exists(scene):
			continue
		var f := FighterStandIn.new()
		var tree := Engine.get_main_loop() as SceneTree
		(tree.current_scene if tree.current_scene != null else tree.root).add_child(f)
		f.setup(id, BattleStage.stand_in_spec(id), {})
		assert_true(f.has_actor(), "%s is drawn as its model, not a capsule" % id)
		f.get_parent().remove_child(f)
		f.free()
