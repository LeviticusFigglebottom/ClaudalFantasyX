class_name BattlePlaceholderClips
extends RefCounted
## Placeholder hero battle clips (M2-BPR-10; docs/kb/tech/battle_presentation.md "Clip contract"). Until the
## heroes' real battle clips land (M2-CHR-07), a fighter's model with a Skeleton3D and an AnimationPlayer gets a
## short generated pose clip for every contract clip (BattleClips.ALL) it lacks, keyed on its main bones from
## choreo.json `placeholder_clips`. A real clip of the same name always wins: only missing names are added, so the
## real library replaces them with no code change. BattleClips.player_of calls ensure() the first time it finds a
## model's player; a primitive stand-in (no player), a creature actor or a skeleton that is not a humanoid gets
## nothing. Presentation only.

const SECTION := "placeholder_clips"
## Set on the AnimationPlayer once it has been looked at (the names added, possibly none).
const META := &"hymn_placeholder_clips"
## The role whose position hips_m moves.
const HIPS_ROLE := "hips"
const DEG_AXES := 3


## Adds the missing contract clips to `player` once; the names added (empty on every later call).
static func ensure(f: Node, player: AnimationPlayer) -> Array[StringName]:
	var none: Array[StringName] = []
	if player == null or player.has_meta(META):
		return none
	player.set_meta(META, none)
	if BattleClips.creature_of(f) != null:
		return none  # a creature actor plays its own clips (M2-CRE-03)
	var skel := skeleton_of(f, player)
	if skel == null:
		return none
	var added := apply(player, skel, BattleChoreo.load_data().get(SECTION, {}) as Dictionary)
	player.set_meta(META, added)
	return added


## The model's skeleton: the first Skeleton3D under the player's root node, else under the fighter.
static func skeleton_of(f: Node, player: AnimationPlayer) -> Skeleton3D:
	for host: Node in [player.get_node_or_null(player.root_node), f]:
		if host == null:
			continue
		var found := host.find_children("*", "Skeleton3D", true, false)
		if not found.is_empty():
			return found[0] as Skeleton3D
	return null


## Role -> bone index on `skel` (the first candidate name it has), for the roles it resolves.
static func resolve(skel: Skeleton3D, cfg: Dictionary) -> Dictionary:
	var out := {}
	var bones := cfg.get("bones", {}) as Dictionary
	for role: String in bones:
		for name: Variant in bones[role]:
			var i := skel.find_bone(str(name))
			if i >= 0:
				out[role] = i
				break
	return out


## Builds and adds every contract clip `player` lacks; the names added. Nothing when the skeleton resolves fewer
## than min_roles roles.
static func apply(player: AnimationPlayer, skel: Skeleton3D, cfg: Dictionary) -> Array[StringName]:
	var added: Array[StringName] = []
	var roles := resolve(skel, cfg)
	if roles.is_empty() or roles.size() < int(cfg.get("min_roles", 0)):
		return added
	var clips := cfg.get("clips", {}) as Dictionary
	var root := player.get_node_or_null(player.root_node)
	if root == null:
		return added
	var skel_path := str(root.get_path_to(skel))
	var keyed := keyed_roles(cfg, roles)
	var built: Dictionary = {}
	for clip: StringName in BattleClips.ALL:
		if player.has_animation(clip) or not clips.has(str(clip)):
			continue
		built[clip] = build(skel, skel_path, roles, keyed, cfg, clips[str(clip)] as Dictionary)
		added.append(clip)
	if added.is_empty():
		return added
	_install(player, built)
	return added


## Every role the clips key: those named in base or in any clip's poses (and the hips, for hips_m), that resolve.
static func keyed_roles(cfg: Dictionary, roles: Dictionary) -> Array[String]:
	var seen := {}
	for role: String in cfg.get("base", {}) as Dictionary:
		seen[role] = true
	var clips := cfg.get("clips", {}) as Dictionary
	for name: String in clips:
		for key: Dictionary in (clips[name] as Dictionary).get("keys", []):
			for role: String in key.get("pose", {}) as Dictionary:
				seen[role] = true
			if key.has("hips_m"):
				seen[HIPS_ROLE] = true
	var out: Array[String] = []
	for role: String in seen:
		if roles.has(role):
			out.append(role)
	out.sort()
	return out


## One placeholder Animation: a rotation track per keyed role (and a position track on the hips), every key a pose.
static func build(
	skel: Skeleton3D, skel_path: String, roles: Dictionary, keyed: Array[String], cfg: Dictionary, clip: Dictionary
) -> Animation:
	var a := Animation.new()
	a.length = float(clip.get("length_sec", 0.0))
	a.loop_mode = Animation.LOOP_LINEAR if bool(clip.get("loop", false)) else Animation.LOOP_NONE
	var base := cfg.get("base", {}) as Dictionary
	var tracks := {}
	for role in keyed:
		var t := a.add_track(Animation.TYPE_ROTATION_3D)
		a.track_set_path(t, NodePath("%s:%s" % [skel_path, skel.get_bone_name(int(roles[role]))]))
		tracks[role] = t
	var hips_track := -1
	if roles.has(HIPS_ROLE) and keyed.has(HIPS_ROLE):
		hips_track = a.add_track(Animation.TYPE_POSITION_3D)
		a.track_set_path(hips_track, NodePath("%s:%s" % [skel_path, skel.get_bone_name(int(roles[HIPS_ROLE]))]))
	var last := {}  # track -> [time, quaternion] of its previous key
	var max_deg := maxf(float(cfg.get("max_key_deg", 180.0)), 1.0)
	for key: Dictionary in clip.get("keys", []):
		var time := float(key.get("t", 0.0))
		var pose := base.duplicate()
		pose.merge(key.get("pose", {}) as Dictionary, true)
		var turns := {}
		for role in keyed:
			if pose.has(role):
				turns[int(roles[role])] = turn_of(pose[role])
		var local := local_rotations(skel, turns)
		for role in keyed:
			_rotation_key(a, int(tracks[role]), time, local[int(roles[role])] as Quaternion, last, max_deg)
		if hips_track >= 0:
			var hips := int(roles[HIPS_ROLE])
			a.position_track_insert_key(hips_track, time, hips_position(skel, hips, _vec(key.get("hips_m", []))))
	return a


## Inserts rotation key `q` at `time` on `track` (M2-HER-1114): on the previous key's hemisphere, so a blend never
## takes the long way round, and with slerped keys between when the two are more than `max_deg` apart
## (placeholder_clips.max_key_deg; a near-antipodal pair flipped an arm mid cross-fade).
static func _rotation_key(
	a: Animation, track: int, time: float, q: Quaternion, last: Dictionary, max_deg: float
) -> void:
	if last.has(track):
		var prev_t := float(last[track][0])
		var prev := last[track][1] as Quaternion
		if prev.dot(q) < 0.0:
			q = -q
		var steps := ceili(rad_to_deg(prev.angle_to(q)) / max_deg)
		for i in range(1, steps):
			var u := float(i) / steps
			a.rotation_track_insert_key(track, lerpf(prev_t, time, u), prev.slerp(q, u))
	a.rotation_track_insert_key(track, time, q)
	last[track] = [time, q]


## [x, y, z] degrees in the model's axes -> a turn (YXZ, as Basis.from_euler and the characters' hero_clips.py).
static func turn_of(deg: Variant) -> Quaternion:
	var v := _vec(deg)
	return Quaternion.from_euler(Vector3(deg_to_rad(v.x), deg_to_rad(v.y), deg_to_rad(v.z)))


## Bone index -> its local rotation when each bone in `turns` takes that turn (model axes) on top of what it
## inherits and every other bone stays at rest: local = parent_global^-1 * turn * parent_global * rest.
static func local_rotations(skel: Skeleton3D, turns: Dictionary) -> Dictionary:
	var glob := {}
	var out := {}
	for i in skel.get_bone_count():
		_global_of(skel, i, turns, glob, out)
	return out


static func _global_of(skel: Skeleton3D, i: int, turns: Dictionary, glob: Dictionary, out: Dictionary) -> Quaternion:
	if glob.has(i):
		return glob[i]
	var parent := skel.get_bone_parent(i)
	var pg := Quaternion.IDENTITY if parent < 0 else _global_of(skel, parent, turns, glob, out)
	var g := pg * skel.get_bone_rest(i).basis.get_rotation_quaternion()
	if turns.has(i):
		g = (turns[i] as Quaternion) * g
	glob[i] = g
	out[i] = (pg.inverse() * g).normalized()
	return g


## The hips bone's local position moved by `offset` metres in the model's axes.
static func hips_position(skel: Skeleton3D, hips: int, offset: Vector3) -> Vector3:
	var parent := skel.get_bone_parent(hips)
	var rest := skel.get_bone_rest(hips).origin
	if parent < 0:
		return rest + offset
	return rest + skel.get_bone_global_rest(parent).basis.inverse() * offset


static func _vec(v: Variant) -> Vector3:
	var arr := v as Array if v is Array else []
	if arr.size() < DEG_AXES:
		return Vector3.ZERO
	return Vector3(float(arr[0]), float(arr[1]), float(arr[2]))


## Puts the built clips in the player's default library ("" — the names BattleClips plays) beside its own clips. The
## default library may be an imported resource the model shares, so the player gets its own copy with the clips
## added; what was playing keeps playing.
static func _install(player: AnimationPlayer, built: Dictionary) -> void:
	var lib := AnimationLibrary.new()
	var old: AnimationLibrary = player.get_animation_library(&"") if player.has_animation_library(&"") else null
	if old != null:
		for name: StringName in old.get_animation_list():
			lib.add_animation(name, old.get_animation(name))
	for name: StringName in built:
		lib.add_animation(name, built[name] as Animation)
	var current := player.current_animation
	var at := player.current_animation_position if current != "" else 0.0
	var playing := player.is_playing()
	if playing:
		player.stop()  # swapping the library under a playing player segfaults Godot 4.6.3 (M2-HER-1114)
	if old != null:
		player.remove_animation_library(&"")
	player.add_animation_library(&"", lib)
	if playing and current != "" and player.has_animation(current):
		player.play(current)
		player.seek(at, true)
