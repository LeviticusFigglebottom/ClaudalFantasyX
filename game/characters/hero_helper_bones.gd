class_name HeroHelperBones
extends RefCounted
## M1-CHR-15: poses a hero's helper bones (the shoulder correctives and the skirt panels) from the rest of the
## skeleton's pose. The clips carry these bones baked (assets_src/characters/asha/hero_clips.py, the same solve);
## call this after setting a pose by hand instead (the character stages' world_pose, a cutscene placeholder pose).
## The parameters are game/data/characters/helper_bones.json. A skeleton without helper bones is left alone.

const DATA_PATH := "res://game/data/characters/helper_bones.json"

static var _data: Dictionary = {}


static func data() -> Dictionary:
	if _data.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		_data = parsed if parsed is Dictionary else {}
	return _data


## Sets the helper bones' pose rotations (and the lower skirt panels' floor gathers, as scales) on `skel` from its
## current pose. The floor is the skeleton's y = 0.
static func drive(skel: Skeleton3D) -> void:
	var d := data()
	if d.is_empty():
		return
	skel.force_update_all_bone_transforms()
	_drive_armpits(skel, d["armpit"])
	_drive_skirt(skel, d["skirt"])
	skel.force_update_all_bone_transforms()


## True when the skeleton has any helper bone.
static func has_helpers(skel: Skeleton3D) -> bool:
	var d := data()
	if d.is_empty():
		return false
	for i: int in skel.get_bone_count():
		var n := skel.get_bone_name(i)
		if n.begins_with(d["armpit"]["bone_prefix"]) or n.begins_with(d["skirt"]["bone_prefix"]):
			return true
	return false


static func _rest_q(skel: Skeleton3D, bone: int) -> Quaternion:
	return skel.get_bone_rest(bone).basis.get_rotation_quaternion()


static func _drive_armpits(skel: Skeleton3D, a: Dictionary) -> void:
	for side: String in ["L", "R"]:
		var h := skel.find_bone(String(a["bone_prefix"]) + side)
		var drv := skel.find_bone(String(a["driver_prefix"]) + side)
		if h < 0 or drv < 0:
			continue
		var turn := (skel.get_bone_pose_rotation(drv) * _rest_q(skel, drv).inverse()).normalized()
		var q := Quaternion.IDENTITY.slerp(turn, float(a["share"])) * _rest_q(skel, h)
		skel.set_bone_pose_rotation(h, q.normalized())


static func _drive_skirt(skel: Skeleton3D, s: Dictionary) -> void:
	var prefix := String(s["bone_prefix"])
	var names: Array[String] = []
	for i: int in skel.get_bone_count():
		var n := skel.get_bone_name(i)
		if n.begins_with(prefix) and not n.contains("."):
			names.append(n)
	if names.is_empty():
		return
	names.sort()
	var hips := skel.get_bone_parent(skel.find_bone(names[0]))
	var cloth := _panel_cloth(skel, s, names, hips)
	var hips_rest := skel.get_bone_global_rest(hips)
	var hips_pose := skel.get_bone_global_pose(hips)
	var rq_h := hips_rest.basis.get_rotation_quaternion()
	var inv_dp := (hips_pose.basis.get_rotation_quaternion() * rq_h.inverse()).inverse()
	var legs := _leg_segments(skel, s, hips_pose.origin, inv_dp, false)
	var legs0 := _leg_segments(skel, s, hips_rest.origin, Quaternion.IDENTITY, true)
	var down := Vector3(0.0, -1.0, 0.0)
	var tops: Array[Vector3] = []
	var knees: Array[Vector3] = []
	var axes: Array[Vector3] = []
	var us: Array[Vector3] = []
	for n: String in names:
		var top := skel.get_bone_global_rest(skel.find_bone(n)).origin - hips_rest.origin
		tops.append(top)
		knees.append(skel.get_bone_global_rest(skel.find_bone(n + ".001")).origin - hips_rest.origin)
		var u := Vector3(top.x, 0.0, top.z).normalized()
		us.append(u)
		axes.append(down.cross(u).normalized())
	var lag := deg_to_rad(float(s["lag_deg_per_45"])) / (PI / 4.0)
	var top_swing := deg_to_rad(float(s["max_swing_deg"]))
	var a1: Array[float] = []
	for k: int in names.size():
		a1.append(_swing(cloth[names[k]], tops[k], axes[k], Vector3.ZERO, legs, legs0, s))
	a1 = _limit_lag(a1, us, lag, top_swing)
	var a2: Array[float] = []
	for k: int in names.size():
		var tip := tops[k] + Basis(axes[k], a1[k]) * (knees[k] - tops[k])
		a2.append(_swing(cloth[names[k] + ".001"], knees[k], axes[k], tip - knees[k], legs, legs0, s))
	a2 = _limit_lag(a2, us, lag, top_swing)
	var flare := float(s["gather_flare"])
	for k: int in names.size():
		var h := skel.find_bone(names[k])
		var lo := skel.find_bone(names[k] + ".001")
		var g1 := rq_h * _rest_q(skel, h)
		var loc1 := rq_h.inverse() * Quaternion(axes[k], a1[k]) * g1
		skel.set_bone_pose_rotation(h, loc1.normalized())
		var loc2 := g1.inverse() * Quaternion(axes[k], a2[k] - a1[k]) * g1 * _rest_q(skel, lo)
		skel.set_bone_pose_rotation(lo, loc2.normalized())
		var tip := tops[k] + Basis(axes[k], a1[k]) * (knees[k] - tops[k])
		var axis := g1 * _rest_q(skel, lo) * Vector3.UP
		var sc := _overhang(cloth[names[k] + ".001"], knees[k], axis, axes[k], a2[k], tip, legs, s)
		sc = _gather(
			cloth[names[k] + ".001"],
			knees[k],
			axis,
			axes[k],
			a2[k],
			tip - knees[k],
			inv_dp.inverse(),
			hips_pose.origin.y,
			sc,
			s
		)
		skel.set_bone_pose_scale(lo, Vector3(1.0 + flare * (1.0 - sc), sc, 1.0 + flare * (1.0 - sc)))


## The lower panel's gather: the largest length scale in [gather_min, 1] (`bisect` halvings) at which its cloth (scaled
## along `along` about `knee`, turned `ang` about `axis`, shifted by `shift`, then out of the pelvis's frame by `dp`)
## stays floor_clear_m above the floor, for a hips joint `base_y` above it.
static func _gather(
	cloth: PackedVector3Array,
	knee: Vector3,
	along: Vector3,
	axis: Vector3,
	ang: float,
	shift: Vector3,
	dp: Quaternion,
	base_y: float,
	start: float,
	s: Dictionary
) -> float:
	var floor_y := float(s["floor_clear_m"])
	if cloth.is_empty() or _low(cloth, knee, along, axis, ang, shift, dp, base_y, start) >= floor_y:
		return start
	var lo := float(s["gather_min"])
	if _low(cloth, knee, along, axis, ang, shift, dp, base_y, lo) < floor_y:
		return lo
	var hi := start
	for _i: int in int(s["bisect"]):
		var mid := 0.5 * (lo + hi)
		if _low(cloth, knee, along, axis, ang, shift, dp, base_y, mid) >= floor_y:
			lo = mid
		else:
			hi = mid
	return lo


## The overhang gather: a lower panel swung out past overhang_from_deg lies over the legs; the cloth that would run on
## past them falls, so the panel ends overhang_margin_m past the farthest leg point beside it (eased in by swing).
static func _overhang(
	cloth: PackedVector3Array,
	knee: Vector3,
	along: Vector3,
	axis: Vector3,
	ang: float,
	tip: Vector3,
	legs: Array[PackedVector3Array],
	s: Dictionary
) -> float:
	var from := deg_to_rad(float(s["overhang_from_deg"]))
	if cloth.is_empty() or ang <= from:
		return 1.0
	var d := Basis(axis, ang) * along
	var steps := int(s["support_samples"])
	var side_max := float(s["support_lateral_m"])
	var reach := 0.0
	for f: int in steps + 1:
		for j: int in legs[0].size():
			var q := legs[0][j] + (legs[1][j] - legs[0][j]) * (float(f) / steps) - tip
			if absf(q.dot(axis)) < side_max:
				reach = maxf(reach, q.dot(d))
	var full := 0.0
	for c: Vector3 in cloth:
		full = maxf(full, (c - knee).dot(along))
	var want := clampf((reach + float(s["overhang_margin_m"])) / maxf(full, 1e-6), float(s["gather_min"]), 1.0)
	return 1.0 - smoothstep(0.0, 1.0, (ang - from) / deg_to_rad(float(s["overhang_ease_deg"]))) * (1.0 - want)


static func _low(
	cloth: PackedVector3Array,
	knee: Vector3,
	along: Vector3,
	axis: Vector3,
	ang: float,
	shift: Vector3,
	dp: Quaternion,
	base_y: float,
	sc: float
) -> float:
	var rot := Basis(axis, ang)
	var low := INF
	for c: Vector3 in cloth:
		var v := c - knee
		v += along * (v.dot(along) * (sc - 1.0))
		low = minf(low, base_y + (dp * (knee + rot * v + shift)).y)
	return low


## Neighbouring panels may not lag each other by more than `lag` radians per radian between them.
static func _limit_lag(a: Array[float], us: Array[Vector3], lag: float, top: float) -> Array[float]:
	var out: Array[float] = []
	for i: int in a.size():
		var best := -INF
		for j: int in a.size():
			var apart := acos(clampf(us[i].dot(us[j]), -1.0, 1.0))
			best = maxf(best, a[j] - lag * apart)
		out.append(minf(best, top))
	return out


## bone -> rest positions (relative to the hips joint) of the cloth vertices with at least cloth_min_weight on it.
static func _panel_cloth(skel: Skeleton3D, s: Dictionary, names: Array[String], hips: int) -> Dictionary:
	var out := {}
	var want := {}
	for n: String in names:
		out[n] = PackedVector3Array()
		out[n + ".001"] = PackedVector3Array()
		want[skel.find_bone(n)] = n
		want[skel.find_bone(n + ".001")] = n + ".001"
	var mi := skel.find_child(String(s["cloth_mesh"]), true, false) as MeshInstance3D
	if mi == null or mi.mesh == null or mi.skin == null:
		return out
	var to_skel := skel.global_transform.affine_inverse() * mi.global_transform
	var origin := skel.get_bone_global_rest(hips).origin
	var lim := float(s["cloth_min_weight"])
	var binds: Array[int] = []
	for b: int in mi.skin.get_bind_count():
		var bone := mi.skin.get_bind_bone(b)
		if bone < 0:
			bone = skel.find_bone(String(mi.skin.get_bind_name(b)))
		binds.append(bone)
	for surf: int in mi.mesh.get_surface_count():
		var arr := mi.mesh.surface_get_arrays(surf)
		var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
		var bones: PackedInt32Array = arr[Mesh.ARRAY_BONES]
		var weights: PackedFloat32Array = arr[Mesh.ARRAY_WEIGHTS]
		if verts.is_empty() or bones.is_empty():
			continue
		var per := bones.size() / verts.size()
		for i: int in verts.size():
			for k: int in per:
				var w := weights[i * per + k]
				if w < lim:
					continue
				var bone := binds[bones[i * per + k]]
				if want.has(bone):
					var arr_out: PackedVector3Array = out[want[bone]]
					arr_out.append(to_skel * verts[i] - origin)
					out[want[bone]] = arr_out
	return out


## [heads, tails] of the leg segments of both legs, relative to `origin`, turned by `turn` (the pelvis's frame).
static func _leg_segments(
	skel: Skeleton3D, s: Dictionary, origin: Vector3, turn: Quaternion, rest: bool
) -> Array[PackedVector3Array]:
	var heads := PackedVector3Array()
	var tails := PackedVector3Array()
	for side: String in ["L", "R"]:
		for seg: Variant in s["leg_segments"]:
			var a := skel.find_bone("%s.%s" % [seg[0], side])
			var b := skel.find_bone("%s.%s" % [seg[1], side])
			var pa := skel.get_bone_global_rest(a).origin if rest else skel.get_bone_global_pose(a).origin
			var pb := skel.get_bone_global_rest(b).origin if rest else skel.get_bone_global_pose(b).origin
			heads.append(turn * (pa - origin))
			tails.append(turn * (pb - origin))
	return [heads, tails]


static func _seg_dist(c: Vector3, a: Vector3, b: Vector3) -> float:
	var ab := b - a
	var t := clampf((c - a).dot(ab) / maxf(ab.length_squared(), 1e-12), 0.0, 1.0)
	return c.distance_to(a + ab * t)


## Least angle in [0, max_swing_deg] at which the cloth (turned about `pivot` along `axis`, then shifted by `shift`)
## keeps its rest clearance from the legs: coarse steps, then bisection; when no angle clears, the nearest.
static func _swing(
	cloth: PackedVector3Array,
	pivot: Vector3,
	axis: Vector3,
	shift: Vector3,
	legs: Array[PackedVector3Array],
	legs0: Array[PackedVector3Array],
	s: Dictionary
) -> float:
	if cloth.is_empty():
		return 0.0
	var clear := float(s["clear_m"])
	var slack := float(s["slack_m"])
	var nseg := legs[0].size()
	var need := PackedFloat32Array()
	need.resize(cloth.size() * nseg)
	for i: int in cloth.size():
		for j: int in nseg:
			need[i * nseg + j] = minf(_seg_dist(cloth[i], legs0[0][j], legs0[1][j]), clear) - slack
	if _margin(cloth, pivot, axis, shift, 0.0, legs, need, true) >= 0.0:
		return 0.0
	var top := deg_to_rad(float(s["max_swing_deg"]))
	var step := deg_to_rad(float(s["grid_deg"]))
	var best := 0.0
	var best_m := _margin(cloth, pivot, axis, shift, 0.0, legs, need, false)
	var lo := 0.0
	var ang := step
	while ang <= top + 1e-9:
		var m := _margin(cloth, pivot, axis, shift, ang, legs, need, false)
		if m >= 0.0:
			var hi := ang
			for _i: int in int(s["bisect"]):
				var mid := 0.5 * (lo + hi)
				if _margin(cloth, pivot, axis, shift, mid, legs, need, true) >= 0.0:
					hi = mid
				else:
					lo = mid
			return hi
		if m > best_m:
			best = ang
			best_m = m
		lo = ang
		ang += step
	return best


## The least (distance - need) over cloth and leg segments; with `early`, any negative value as soon as one is found.
static func _margin(
	cloth: PackedVector3Array,
	pivot: Vector3,
	axis: Vector3,
	shift: Vector3,
	ang: float,
	legs: Array[PackedVector3Array],
	need: PackedFloat32Array,
	early: bool
) -> float:
	var rot := Basis(axis, ang)
	var nseg := legs[0].size()
	var worst := INF
	for i: int in cloth.size():
		var c := pivot + rot * (cloth[i] - pivot) + shift
		for j: int in nseg:
			var m := _seg_dist(c, legs[0][j], legs[1][j]) - need[i * nseg + j]
			if m < worst:
				worst = m
				if early and worst < 0.0:
					return worst
	return worst
