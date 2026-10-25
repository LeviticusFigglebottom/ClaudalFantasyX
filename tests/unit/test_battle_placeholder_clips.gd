extends TestCase
## M2-BPR-10: placeholder hero battle clips. A synthetic MPFB2-named skeleton with an AnimationPlayer holding only
## "idle" gets every contract clip, on tracks that target its bones; a real clip of the same name is kept; a model
## without a skeleton (or a skeleton that is not a humanoid) gets nothing; the data's poses come out as turns on
## top of what each bone inherits.

const EPS := 0.001
## The synthetic rig: bone, parent, rest offset from the parent (metres), rest turn (degrees, YXZ).
const RIG := [
	["DEF-spine", "", Vector3(0.0, 0.9, 0.0), Vector3.ZERO],
	["DEF-spine.001", "DEF-spine", Vector3(0.0, 0.1, 0.0), Vector3(5.0, 0.0, 0.0)],
	["DEF-spine.002", "DEF-spine.001", Vector3(0.0, 0.1, 0.0), Vector3.ZERO],
	["DEF-spine.003", "DEF-spine.002", Vector3(0.0, 0.12, 0.0), Vector3(-5.0, 0.0, 0.0)],
	["DEF-spine.004", "DEF-spine.003", Vector3(0.0, 0.16, 0.0), Vector3.ZERO],
	["DEF-spine.005", "DEF-spine.004", Vector3(0.0, 0.05, 0.0), Vector3.ZERO],
	["DEF-spine.006", "DEF-spine.005", Vector3(0.0, 0.05, 0.0), Vector3.ZERO],
	["DEF-shoulder.L", "DEF-spine.003", Vector3(0.05, 0.12, 0.0), Vector3(0.0, 0.0, -80.0)],
	["DEF-upper_arm.L", "DEF-shoulder.L", Vector3(0.0, 0.15, 0.0), Vector3(0.0, 0.0, 30.0)],
	["DEF-forearm.L", "DEF-upper_arm.L", Vector3(0.0, 0.28, 0.0), Vector3(10.0, 0.0, 0.0)],
	["DEF-hand.L", "DEF-forearm.L", Vector3(0.0, 0.25, 0.0), Vector3.ZERO],
	["DEF-shoulder.R", "DEF-spine.003", Vector3(-0.05, 0.12, 0.0), Vector3(0.0, 0.0, 80.0)],
	["DEF-upper_arm.R", "DEF-shoulder.R", Vector3(0.0, 0.15, 0.0), Vector3(0.0, 0.0, -30.0)],
	["DEF-forearm.R", "DEF-upper_arm.R", Vector3(0.0, 0.28, 0.0), Vector3(10.0, 0.0, 0.0)],
	["DEF-hand.R", "DEF-forearm.R", Vector3(0.0, 0.25, 0.0), Vector3.ZERO],
	["DEF-thigh.L", "DEF-spine", Vector3(0.1, 0.0, 0.0), Vector3(0.0, 0.0, 180.0)],
	["DEF-shin.L", "DEF-thigh.L", Vector3(0.0, 0.45, 0.0), Vector3.ZERO],
	["DEF-foot.L", "DEF-shin.L", Vector3(0.0, 0.42, 0.0), Vector3(-90.0, 0.0, 0.0)],
	["DEF-thigh.R", "DEF-spine", Vector3(-0.1, 0.0, 0.0), Vector3(0.0, 0.0, 180.0)],
	["DEF-shin.R", "DEF-thigh.R", Vector3(0.0, 0.45, 0.0), Vector3.ZERO],
	["DEF-foot.R", "DEF-shin.R", Vector3(0.0, 0.42, 0.0), Vector3(-90.0, 0.0, 0.0)],
]

var _nodes: Array[Node] = []


func _skeleton(rows: Array) -> Skeleton3D:
	var s := Skeleton3D.new()
	s.name = "Skeleton3D"
	for row: Array in rows:
		var i := s.add_bone(str(row[0]))
		if str(row[1]) != "":
			s.set_bone_parent(i, s.find_bone(str(row[1])))
		var e: Vector3 = row[3]
		var basis := Basis.from_euler(Vector3(deg_to_rad(e.x), deg_to_rad(e.y), deg_to_rad(e.z)))
		s.set_bone_rest(i, Transform3D(basis, row[2]))
	s.reset_bone_poses()
	return s


## A fighter root -> Model (the player's root) -> rig/Skeleton3D and an AnimationPlayer with `clips` (and its idle
## playing), in the tree.
func _fighter(skel: Skeleton3D, clips: Array[StringName]) -> Node3D:
	var f := Node3D.new()
	var model := Node3D.new()
	model.name = "Model"
	f.add_child(model)
	if skel != null:
		var rig := Node3D.new()
		rig.name = "rig"
		model.add_child(rig)
		rig.add_child(skel)
	var player := AnimationPlayer.new()
	var lib := AnimationLibrary.new()
	for clip in clips:
		var a := Animation.new()
		a.length = 1.0
		lib.add_animation(clip, a)
	player.add_animation_library(&"", lib)
	model.add_child(player)
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(f)
	_nodes.append(f)
	if player.has_animation(BattleClips.IDLE):
		player.play(BattleClips.IDLE)
	return f


func _player(f: Node) -> AnimationPlayer:
	return f.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer


func _free() -> void:
	for n in _nodes:
		n.queue_free()
	_nodes.clear()


func _cfg() -> Dictionary:
	return BattleChoreo.load_data().get(BattlePlaceholderClips.SECTION, {}) as Dictionary


func test_every_contract_clip_becomes_playable_on_bones_the_skeleton_has() -> void:
	var f := _fighter(_skeleton(RIG), [BattleClips.IDLE])
	var player := _player(f)
	var idle := player.get_animation(BattleClips.IDLE)
	assert_false(player.get_animation_library(&"").has_animation(BattleClips.CAST), "before anyone looks")
	var shared := player.get_animation_library(&"")
	for clip in BattleClips.ALL:
		assert_true(BattleClips.has_clip(f, clip), "%s is playable" % clip)
	assert_eq(player.get_animation(BattleClips.IDLE), idle, "the real idle is kept")
	assert_false(shared.has_animation(BattleClips.CAST), "the model's own library is not changed")
	assert_eq(str(player.current_animation), str(BattleClips.IDLE), "idle keeps playing")
	var root := player.get_node(player.root_node)
	for clip in BattleClips.ALL:
		if clip == BattleClips.IDLE:
			continue
		var a := player.get_animation(clip)
		assert_true(a.get_track_count() > 0, "%s has tracks" % clip)
		assert_true(a.length > 0.0)
		for t in a.get_track_count():
			var path := a.track_get_path(t)
			var skel := root.get_node_or_null(NodePath(str(path.get_concatenated_names()))) as Skeleton3D
			assert_true(skel != null, "%s track %d reaches the skeleton" % [clip, t])
			if skel != null:
				assert_true(skel.find_bone(str(path.get_concatenated_subnames())) >= 0, "%s: %s" % [clip, path])
			for k in a.track_get_key_count(t):
				assert_between(a.track_get_key_time(t, k), 0.0, a.length + EPS)
	assert_eq(player.get_animation(BattleClips.KO).loop_mode, Animation.LOOP_NONE, "the KO holds")
	assert_eq(player.get_animation(BattleClips.VICTORY).loop_mode, Animation.LOOP_LINEAR)
	assert_true(BattleClips.play(f, BattleClips.ATTACK))
	assert_eq(str(player.current_animation), str(BattleClips.ATTACK))
	assert_eq(str(player.get_queue()), str([BattleClips.IDLE]), "idle after the placeholder")
	_free()


func test_a_real_clip_of_the_same_name_wins() -> void:
	var f := _fighter(_skeleton(RIG), [BattleClips.IDLE, BattleClips.ATTACK])
	var player := _player(f)
	var real := player.get_animation(BattleClips.ATTACK)
	assert_true(BattleClips.has_clip(f, BattleClips.CAST))
	assert_eq(player.get_animation(BattleClips.ATTACK), real, "the real attack is kept")
	assert_eq(real.get_track_count(), 0)
	var added: Array[StringName] = player.get_meta(BattlePlaceholderClips.META)
	assert_false(added.has(BattleClips.ATTACK))
	assert_false(added.has(BattleClips.IDLE))
	assert_eq(added.size(), BattleClips.ALL.size() - 2)
	assert_eq(BattlePlaceholderClips.ensure(f, player), [] as Array[StringName], "once per player")
	_free()


func test_no_skeleton_or_not_a_humanoid_gets_nothing() -> void:
	var bare := _fighter(null, [BattleClips.IDLE])
	assert_false(BattleClips.has_clip(bare, BattleClips.CAST), "no skeleton: the stand-in moves procedurally")
	var few := _skeleton([["root", "", Vector3.ZERO, Vector3.ZERO], ["head", "root", Vector3.UP, Vector3.ZERO]])
	var creature := _fighter(few, [BattleClips.IDLE])
	assert_false(BattleClips.has_clip(creature, BattleClips.ATTACK), "fewer than min_roles roles")
	assert_eq(_player(creature).get_animation_list().size(), 1)
	_free()


func test_the_mpfb2_default_names_resolve_too() -> void:
	var names := {
		"DEF-spine": "root",
		"DEF-spine.001": "spine04",
		"DEF-spine.003": "spine02",
		"DEF-spine.004": "neck01",
		"DEF-spine.006": "head",
		"DEF-upper_arm.L": "upperarm01.L",
		"DEF-forearm.L": "lowerarm01.L",
		"DEF-hand.L": "wrist.L",
		"DEF-upper_arm.R": "upperarm01.R",
		"DEF-forearm.R": "lowerarm01.R",
		"DEF-hand.R": "wrist.R",
		"DEF-thigh.L": "upperleg01.L",
		"DEF-shin.L": "lowerleg01.L",
		"DEF-thigh.R": "upperleg01.R",
		"DEF-shin.R": "lowerleg01.R",
	}
	var rows: Array = []
	for row: Array in RIG:
		var r := row.duplicate()
		r[0] = names.get(r[0], r[0])
		r[1] = names.get(r[1], r[1])
		rows.append(r)
	var skel := _skeleton(rows)
	var roles := BattlePlaceholderClips.resolve(skel, _cfg())
	assert_eq(skel.get_bone_name(int(roles["upper_arm_r"])), "upperarm01.R")
	assert_eq(skel.get_bone_name(int(roles["head"])), "head")
	var f := _fighter(skel, [BattleClips.IDLE])
	assert_true(BattleClips.has_clip(f, BattleClips.DEFEND))
	_free()


func test_a_pose_is_a_turn_on_top_of_what_the_bone_inherits() -> void:
	var skel := _skeleton(RIG)
	var arm := skel.find_bone("DEF-upper_arm.R")
	var fore := skel.find_bone("DEF-forearm.R")
	var chest := skel.find_bone("DEF-spine.003")
	var t_arm := BattlePlaceholderClips.turn_of([-80.0, 0.0, 30.0])
	var t_chest := BattlePlaceholderClips.turn_of([0.0, 20.0, 0.0])
	var local := BattlePlaceholderClips.local_rotations(skel, {arm: t_arm, chest: t_chest})
	# Compose the locals back down the chain: the arm's global is its turn on top of what it inherits.
	var g := Quaternion.IDENTITY
	var chain: Array[int] = []
	var b := fore
	while b >= 0:
		chain.push_front(b)
		b = skel.get_bone_parent(b)
	var inherited := Quaternion.IDENTITY
	for i in chain:
		if i == arm:
			inherited = g * skel.get_bone_rest(i).basis.get_rotation_quaternion()
		g = g * (local[i] as Quaternion)
		if i == arm:
			assert_true(g.is_equal_approx(t_arm * inherited) or g.is_equal_approx(-(t_arm * inherited)))
	var unturned := local[fore] as Quaternion
	var rest := skel.get_bone_rest(fore).basis.get_rotation_quaternion()
	assert_true(unturned.is_equal_approx(rest) or unturned.is_equal_approx(-rest), "an unturned child keeps its rest")
	var hips := BattlePlaceholderClips.hips_position(skel, skel.find_bone("DEF-spine"), Vector3(0.0, -0.1, 0.0))
	assert_true(hips.is_equal_approx(Vector3(0.0, 0.8, 0.0)), "hips_m moves the hips")
	skel.free()


func test_every_contract_name_has_placeholder_data() -> void:
	var clips := _cfg().get("clips", {}) as Dictionary
	for clip in BattleClips.ALL:
		assert_true(clips.has(str(clip)), "%s has a placeholder row" % clip)


func test_a_hero_model_plays_and_holds_its_ko_then_idles_on_revive() -> void:
	var f := _fighter(_skeleton(RIG), [BattleClips.IDLE])
	var player := _player(f)
	assert_true(BattleClips.play_ko(f, 1.0), "the KO clip (a placeholder) replaces the procedural collapse")
	assert_eq(str(player.current_animation), str(BattleClips.KO))
	assert_eq(player.get_queue().size(), 0, "a KO holds: no idle after it")
	BattleClips.ko_changed(f, true)
	assert_eq(str(player.assigned_animation), str(BattleClips.KO), "still down")
	BattleClips.ko_changed(f, false)
	assert_eq(str(player.current_animation), str(BattleClips.IDLE), "revived: idle again")
	assert_false(BattleClips.play_ko(_fighter(null, [BattleClips.IDLE])), "no skeleton, no KO clip")
	_free()
