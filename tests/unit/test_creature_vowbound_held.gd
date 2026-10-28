extends TestCase
## M3-CRE-647: the six Vowbound as foes for their Ch20 release fights (docs/kb/art/creatures/act3_roster.md, "The
## Vowbound as foes"). Each `<id>_held` scene loads headless on the same GLB as the ally, wears the held material set
## (CreatureActor.material_dir: glimmer_held on every emissive slot, never glimmer_bound, at the ally's energy) while
## the ally scene keeps glimmer_bound; has the `release` clip, which is its KO and lifts it up and back, away from the
## party; faces the party (the foes' yaw); and its `release` phase holds the clip's last frame, which the KO does not
## replay.

const IDS: Array[StringName] = [&"ilun", &"kahre", &"virel", &"hesk", &"nhoa", &"ethren"]
const HELD_SCENE := "res://game/creatures/%s/%s_held_battle.tscn"
const ALLY_SCENE := "res://game/creatures/%s/%s_battle.tscn"
const GLIMMER_HELD := Color("#7FC6D9")
const GLIMMER_BOUND := Color("#4FB3B0")
const COLOR_TOL := 0.002
## About 3.0-3.5 s: the last unfurling, a hold, the lift.
const MIN_RELEASE_SEC := 3.0
const MAX_RELEASE_SEC := 3.5
## The release carries the root at least this far up, and back (-z, away from the party in the model's frame).
const MIN_LIFT_M := 1.0
const MIN_BACK_M := 0.2
const FOE_YAW_DEG := 90.0
const END_SEC := 0.001

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_each_held_scene_loads_with_the_release_clip() -> void:
	for id in IDS:
		var a := _actor(HELD_SCENE % [id, id])
		assert_eq(a.creature_id, StringName("%s_held" % id))
		assert_eq(a.current_clip, &"idle", "%s idles" % id)
		assert_true(a.has_clip(&"release"), "%s has the release" % id)
		var length := a.clip_length(&"release")
		assert_true(length >= MIN_RELEASE_SEC and length <= MAX_RELEASE_SEC, "%s release %.2f s" % [id, length])
		var row := CreatureActor.row_for(StringName("%s_held" % id))
		assert_false(row.has("vowbound"), "%s_held is a foe row" % id)
		assert_eq(str(row["ko"]), "release", "%s: the KO is the release" % id)
		assert_true(is_equal_approx(float(row["stand_in"]["yaw_deg"]), FOE_YAW_DEG), "%s faces the party" % id)
		for clip: StringName in [&"attack", &"cast", &"hit", &"ko"]:
			assert_true(a.has_clip(clip), "%s_held plays %s" % [id, clip])
	before_each()


func test_the_held_scene_wears_glimmer_held_and_the_ally_keeps_glimmer_bound() -> void:
	for id in IDS:
		var held := _emissive_colors(_actor(HELD_SCENE % [id, id]))
		var ally := _emissive_colors(_actor(ALLY_SCENE % [id, id]))
		assert_true(held.size() > 0, "%s has lit surfaces" % id)
		assert_eq(held.size(), ally.size(), "%s: the same lit surfaces" % id)
		for c: Color in held:
			assert_true(_near(c, GLIMMER_HELD), "%s held light is glimmer_held (%s)" % [id, c])
			assert_false(_near(c, GLIMMER_BOUND), "%s held light is not glimmer_bound" % id)
		for c: Color in ally:
			assert_true(_near(c, GLIMMER_BOUND), "%s ally light stays glimmer_bound" % id)
		var he := _emissive_energies(_actor(HELD_SCENE % [id, id]))
		var ae := _emissive_energies(_actor(ALLY_SCENE % [id, id]))
		assert_eq(he, ae, "%s: the same energies (steady, as bound)" % id)
	before_each()


func test_the_release_lifts_up_and_away() -> void:
	for id in IDS:
		var a := _actor(HELD_SCENE % [id, id])
		var start := _bone_at(_pose(a, &"release", 0.0), "root")
		var end := _bone_at(_pose(a, &"release", a.clip_length(&"release")), "root")
		assert_true(end.y - start.y > MIN_LIFT_M, "%s rises (%.2f m)" % [id, end.y - start.y])
		assert_true(start.z - end.z > MIN_BACK_M, "%s goes back, away from the party" % id)
	before_each()


func test_the_release_phase_holds_and_the_ko_does_not_replay_it() -> void:
	var a := _actor(HELD_SCENE % [&"ilun", &"ilun"])
	assert_true(a.enter_phase(&"release"))
	assert_eq(a.current_clip, &"release")
	a._on_clip_finished(&"release")
	assert_eq(a.current_clip, &"release", "a held phase does not go back to idle")
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.seek(1.0, true)
	a.set_ko(true, 0.0)
	assert_eq(a.current_clip, &"release")
	assert_true(player.current_animation_position >= 1.0, "the KO does not restart the release")
	var b := _actor(HELD_SCENE % [&"kahre", &"kahre"])
	assert_true(b.enter_phase(&"release", true))
	b.settle()
	var pb := b.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	assert_true(is_equal_approx(pb.current_animation_position, b.clip_length(&"release")), "settled on the last frame")
	var c := _actor(HELD_SCENE % [&"hesk", &"hesk"])
	c.set_ko(true, 0.0)
	assert_eq(c.current_clip, &"release", "a plain KO plays the release")
	before_each()


func _actor(path: String) -> CreatureActor:
	var a := (load(path) as PackedScene).instantiate() as CreatureActor
	_add(a)
	return a


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


func _lit_materials(a: CreatureActor) -> Array[ShaderMaterial]:
	var out: Array[ShaderMaterial] = []
	for n in a.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		for i in mi.mesh.get_surface_count():
			var m := mi.get_active_material(i) as ShaderMaterial
			if m != null and float(m.get_shader_parameter("emission_energy")) > 0.0:
				out.append(m)
	return out


func _emissive_colors(a: CreatureActor) -> Array[Color]:
	var out: Array[Color] = []
	for m in _lit_materials(a):
		out.append(m.get_shader_parameter("emission_color") as Color)
	return out


func _emissive_energies(a: CreatureActor) -> Array[float]:
	var out: Array[float] = []
	for m in _lit_materials(a):
		out.append(float(m.get_shader_parameter("emission_energy")))
	return out


func _near(a: Color, b: Color) -> bool:
	return absf(a.r - b.r) < COLOR_TOL and absf(a.g - b.g) < COLOR_TOL and absf(a.b - b.b) < COLOR_TOL


## Poses the actor's model at `sec` into `clip` (clamped to just before its end) and returns its skeleton.
func _pose(a: CreatureActor, clip: StringName, sec: float) -> Skeleton3D:
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.play(clip)
	player.seek(minf(sec, player.get_animation(clip).length - END_SEC), true)
	return a.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D


func _bone_at(skel: Skeleton3D, bone: String) -> Vector3:
	return skel.get_bone_global_pose(skel.find_bone(bone)).origin
