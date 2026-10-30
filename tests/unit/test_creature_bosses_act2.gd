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

# --- The Lamp Engine (M4-CRB-003, docs/kb/plan/act2/bosses/lamp_engine.md) -----------------------------------------

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
