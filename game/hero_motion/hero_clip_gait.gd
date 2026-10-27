class_name HeroClipGait
extends RefCounted
## Measures an in-place locomotion clip's natural ground speed (M2-HER-1101, ADR 0190): the speed the
## body must travel for the feet to look planted. Reads the Animation's bone tracks directly (no tree,
## no AnimationPlayer playback), so a test and a tuning pass get the same number.
##
## Method (game/data/hero_motion/hero_motion.json "field.gait_measure"): the clip is sampled `samples`
## times over one cycle and each named foot bone's model-space position is built from the bone poses
## (track value, else rest). A foot is in contact while it is within `contact_tol_m` of its lowest
## height in the cycle; its backward speed relative to the model (models face +Z, so backward is -Z)
## during contact is the ground speed that keeps it still on the floor. The result is the mean over
## the contact samples of every foot.


## The measured ground speed (m/s) of `clip` on the model under `model_root`, or 0.0 when the clip,
## the skeleton or the bones are missing. `cfg` is hero_motion.json "field.gait_measure".
static func clip_speed(model_root: Node, clip: StringName, cfg: Dictionary) -> float:
	var ap := model_root.find_child("AnimationPlayer", true, false) as AnimationPlayer
	var sk := model_root.find_child("Skeleton3D", true, false) as Skeleton3D
	if ap == null or sk == null or not ap.has_animation(clip):
		return 0.0
	var an := ap.get_animation(clip)
	var samples := maxi(int(cfg.get("samples", 0)), 2)
	var tol := float(cfg.get("contact_tol_m", 0.0))
	var to_model := _to_root(sk, model_root)
	var bones: Array[int] = []
	for b: Variant in cfg.get("bones", []):
		var i := sk.find_bone(str(b))
		if i >= 0:
			bones.append(i)
	if bones.is_empty() or an.length <= 0.0:
		return 0.0
	var dt := an.length / samples
	var tracks := _bone_tracks(an, sk)
	# paths[k][s] = foot k at sample s, model space
	var paths: Array[Array] = []
	for b in bones:
		paths.append([])
	for s in samples + 1:
		var local := _pose_at(an, sk, tracks, s * dt)
		for k in bones.size():
			paths[k].append((to_model * _global(sk, local, bones[k])).origin)
	var total := 0.0
	var count := 0
	for k in bones.size():
		var p := paths[k]
		var low := INF
		for v: Vector3 in p:
			low = minf(low, v.y)
		for s in samples:
			var a := p[s] as Vector3
			var vz := ((p[s + 1] as Vector3).z - a.z) / dt
			if a.y <= low + tol and vz < 0.0:
				total += -vz
				count += 1
	return total / count if count > 0 else 0.0


## bone index -> {position, rotation, scale} track indices (-1 when the clip does not key it).
static func _bone_tracks(an: Animation, sk: Skeleton3D) -> Dictionary:
	var out: Dictionary = {}
	for t in an.get_track_count():
		var bone := sk.find_bone(String(an.track_get_path(t).get_concatenated_subnames()))
		if bone < 0:
			continue
		if not out.has(bone):
			out[bone] = [-1, -1, -1]
		match an.track_get_type(t):
			Animation.TYPE_POSITION_3D:
				(out[bone] as Array)[0] = t
			Animation.TYPE_ROTATION_3D:
				(out[bone] as Array)[1] = t
			Animation.TYPE_SCALE_3D:
				(out[bone] as Array)[2] = t
	return out


## Every bone's local pose at time `at`: the keyed value where the clip keys it, else the rest.
static func _pose_at(an: Animation, sk: Skeleton3D, tracks: Dictionary, at: float) -> Array[Transform3D]:
	var out: Array[Transform3D] = []
	for b in sk.get_bone_count():
		var rest := sk.get_bone_rest(b)
		var pos := rest.origin
		var rot := rest.basis.get_rotation_quaternion()
		var scl := rest.basis.get_scale()
		if tracks.has(b):
			var t := tracks[b] as Array
			if int(t[0]) >= 0:
				pos = an.position_track_interpolate(int(t[0]), at)
			if int(t[1]) >= 0:
				rot = an.rotation_track_interpolate(int(t[1]), at)
			if int(t[2]) >= 0:
				scl = an.scale_track_interpolate(int(t[2]), at)
		out.append(Transform3D(Basis(rot).scaled(scl), pos))
	return out


static func _global(sk: Skeleton3D, local: Array[Transform3D], bone: int) -> Transform3D:
	var t := Transform3D.IDENTITY
	var b := bone
	while b >= 0:
		t = local[b] * t
		b = sk.get_bone_parent(b)
	return t


## The skeleton's transform in `root`'s space (works outside the scene tree).
static func _to_root(n: Node3D, root: Node) -> Transform3D:
	var t := Transform3D.IDENTITY
	var c: Node = n
	while c != null and c != root and c is Node3D:
		t = (c as Node3D).transform * t
		c = c.get_parent()
	return t
