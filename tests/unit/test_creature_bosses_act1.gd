extends TestCase
## M3-CRB-001..008 (ADR 0041): the Act I bosses and Vowbound at final quality keep the hook contract that battle
## presentation builds on (M3-CRB-009/010). Every Act I boss model has the full clip set, an `intro` for the boss
## intro camera, and unweighted anchor bones `vfx_wound`, `vfx_core` and `vfx_phase`; every Act I Vowbound has
## `vfx_core` and `vfx_keepsake`. Anchor bones carry no vertices, so moving them never moves the mesh.

const BOSSES: Array[StringName] = [
	&"hullgnaw", &"drownbell", &"bottle_hermit", &"spar_wraith", &"cinder_matron", &"undertows_reach"
]
## Bosses who are people (the characters track's actors, battle_sandbox.json stand_ins `scene`).
const PEOPLE_BOSSES: Array[StringName] = [&"stillguard_inquisitor"]
const VOWBOUND: Array[StringName] = [&"ilun", &"kahre", &"virel"]
const BOSS_CLIPS: Array[StringName] = [&"idle", &"ready", &"intro", &"attack", &"cast", &"hit", &"hit_b", &"ko"]
const VOWBOUND_CLIPS: Array[StringName] = [&"idle", &"ready", &"rise", &"attack", &"cast", &"hit", &"special", &"ko"]
const BOSS_ANCHORS: Array[StringName] = [&"vfx_wound", &"vfx_core", &"vfx_phase"]
const VOWBOUND_ANCHORS: Array[StringName] = [&"vfx_core", &"vfx_keepsake"]
## The intro is a display for the camera's hold (choreo.json boss_intro hold_sec 1.6–2.4 plus its ease-in).
const SKILLS_PATH := "res://game/data/battle/skills.json"
const VOWBOUND_PATH := "res://game/data/battle/vowbound.json"
const ENCOUNTERS_PATH := "res://game/data/battle/encounters.json"
const INTRO_MIN_SEC := 1.5
const INTRO_MAX_SEC := 3.5

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_every_act1_boss_has_the_full_clip_set() -> void:
	for id in BOSSES:
		var a := _actor(id)
		for clip in BOSS_CLIPS:
			assert_true(a.has_clip(clip), "%s has %s" % [id, clip])
	before_each()


func test_every_act1_boss_intro_fits_the_camera_hold() -> void:
	for id in BOSSES:
		var sec := _actor(id).clip_length(&"intro")
		assert_true(sec >= INTRO_MIN_SEC and sec <= INTRO_MAX_SEC, "%s intro is %.2f s" % [id, sec])
	before_each()


func test_every_act1_boss_has_its_vfx_anchor_bones() -> void:
	for id in BOSSES:
		_assert_anchors(id, BOSS_ANCHORS)
	before_each()


func test_every_act1_vowbound_has_its_clips_and_anchor_bones() -> void:
	for id in VOWBOUND:
		var a := _actor(id)
		for clip in VOWBOUND_CLIPS:
			assert_true(a.has_clip(clip), "%s has %s" % [id, clip])
		_assert_anchors(id, VOWBOUND_ANCHORS)
	before_each()


func test_every_act1_boss_and_vowbound_stands_in_as_a_real_body() -> void:
	var ids: Array[StringName] = []
	ids.append_array(BOSSES)
	ids.append_array(PEOPLE_BOSSES)
	ids.append_array(VOWBOUND)
	for id in ids:
		var scene := str(BattleStage.stand_in_spec(id).get("scene", ""))
		assert_true(
			scene != "" and ResourceLoader.exists(scene), "%s draws its model (%s), not a capsule" % [id, scene]
		)


## GPU QA rows 12/35: the battle builds each boss encounter's foes through BattleStage.stand_in_spec into a
## FighterStandIn; one whose scene is missing or empty falls back to the capsule. Build them the same way.
func test_every_act1_boss_encounter_seats_real_bodies_not_capsules() -> void:
	var bosses: Array[StringName] = []
	bosses.append_array(BOSSES)
	bosses.append_array(PEOPLE_BOSSES)
	var seen := {}
	for row: Dictionary in _json(ENCOUNTERS_PATH).get("encounters", []) as Array:
		for eid: Variant in row.get("enemies", []) as Array:
			var cid := StringName(str(eid))
			if not bosses.has(StringName(String(cid).get_slice("#", 0))):
				continue
			seen[String(cid).get_slice("#", 0)] = true
			var f := FighterStandIn.new()
			(Engine.get_main_loop() as SceneTree).root.add_child(f)
			made.append(f)
			f.setup(cid, BattleStage.stand_in_spec(cid), {})
			assert_true(f.has_actor(), "%s in %s is drawn as its model, not a capsule" % [cid, row.get("id", "")])
	for id in bosses:
		assert_true(seen.has(String(id)), "%s is fought in some encounter (the check is live)" % id)
	before_each()


func test_every_act1_vowbound_skill_and_finisher_has_its_clip() -> void:
	var skills := {}
	for row: Dictionary in _json(SKILLS_PATH).get("skills", []) as Array:
		skills[str(row.get("id", ""))] = row
	for row: Dictionary in _json(VOWBOUND_PATH).get("vowbound", []) as Array:
		var id := StringName(str(row.get("id", "")))
		if not VOWBOUND.has(id):
			continue
		var a := _actor(id)
		var ids: Array = (row.get("skills", []) as Array).duplicate()
		ids.append(str((row.get("swell", {}) as Dictionary).get("technique", "")))
		for sid: Variant in ids:
			var kind := StringName(str((skills.get(str(sid), {}) as Dictionary).get("kind", "")))
			var clip := a.clip_for(StringName(str(sid)), kind)
			assert_true(a.has_clip(clip), "%s's %s plays a clip it has (%s)" % [id, sid, clip])


func _json(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed as Dictionary if parsed is Dictionary else {}


func _assert_anchors(id: StringName, anchors: Array[StringName]) -> void:
	var skel := _skeleton(_actor(id))
	assert_true(skel != null, "%s has a skeleton" % id)
	if skel == null:
		return
	for bone in anchors:
		assert_true(skel.find_bone(String(bone)) >= 0, "%s has the %s bone" % [id, bone])
	var weighted := _weighted_bones(skel)
	assert_false(weighted.is_empty(), "%s's mesh is weighted to some bones (the check is live)" % id)
	for bone in anchors:
		assert_false(weighted.has(String(bone)), "%s's %s carries no vertices" % [id, bone])


func _actor(id: StringName) -> CreatureActor:
	var row := CreatureActor.row_for(id)
	var a := (load(str(row.get("scene", ""))) as PackedScene).instantiate() as CreatureActor
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(a)
	made.append(a)
	return a


func _skeleton(a: Node) -> Skeleton3D:
	var found := a.find_children("*", "Skeleton3D", true, false)
	return found[0] as Skeleton3D if not found.is_empty() else null


## Names of the bones some vertex actually weights (> 0) in any skinned mesh under the skeleton. The kit binds every
## bone in the skin, so the binds alone say nothing; the vertex arrays do.
func _weighted_bones(skel: Skeleton3D) -> Dictionary:
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
					out[_bind_bone_name(skel, mi.skin, bones[i])] = true
	return out


func _bind_bone_name(skel: Skeleton3D, skin: Skin, bind: int) -> String:
	var b := skin.get_bind_name(bind)
	return String(b) if b != &"" else skel.get_bone_name(skin.get_bind_bone(bind))
