class_name HeroHelperBones
extends RefCounted
## M1-CHR-15: poses a hero's helper bones (the shoulder correctives and the skirt panels) from the rest of the
## skeleton's pose. The clips carry these bones baked (assets_src/characters/asha/hero_clips.py, the same solve);
## call this after setting a pose by hand instead (the character stages' world_pose, a cutscene placeholder pose).
## The parameters are game/data/characters/helper_bones.json. A skeleton without helper bones is left alone.

const DATA_PATH := "res://game/data/characters/helper_bones.json"
## M2-CHR-515: the held props (Asha's staff, Toma's spear), written by hero_clips.py.
const GRIP_PATH := "res://game/data/characters/grips.json"

static var _data: Dictionary = {}
static var _grips: Dictionary = {}


static func data() -> Dictionary:
	if _data.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		_data = parsed if parsed is Dictionary else {}
	return _data


## Sets the helper bones' pose rotations (and the lowest skirt panel bones' floor gathers, as scales) on `skel` from its
## current pose. The floor is the skeleton's y = 0.
static func drive(skel: Skeleton3D) -> void:
	var d := data()
	if d.is_empty():
		return
	skel.force_update_all_bone_transforms()
	_drive_armpits(skel, d["armpit"])
	_drive_skirt(skel, d["skirt"])
	_drive_prop(skel)
	skel.force_update_all_bone_transforms()


static func grips() -> Dictionary:
	if _grips.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(GRIP_PATH))
		_grips = parsed if parsed is Dictionary else {}
	return _grips


## The held-prop entry for this skeleton (keyed by its armature node's name), or an empty Dictionary.
static func prop_entry(skel: Skeleton3D) -> Dictionary:
	var g := grips()
	if g.is_empty() or skel.get_parent() == null:
		return {}
	var e: Variant = (g["skeletons"] as Dictionary).get(String(skel.get_parent().name), {})
	return e if e is Dictionary else {}


static func _quat(a: Array) -> Quaternion:
	return Quaternion(float(a[0]), float(a[1]), float(a[2]), float(a[3]))


## M2-CHR-515: the hand closes round its prop and turns it upright in the hand's posed frame (the hold), and the prop
## slides through the fist so that, standing near upright, its foot rests on the floor (the skeleton's y = 0).
static func _drive_prop(skel: Skeleton3D) -> void:
	var e := prop_entry(skel)
	if e.is_empty():
		return
	var g := grips()
	var hand := skel.find_bone(String(e["hand"]))
	var bone := skel.find_bone(String(e["bone"]))
	if hand < 0 or bone < 0:
		return
	skel.force_update_all_bone_transforms()
	var rest_g := skel.get_bone_global_rest(hand).basis.get_rotation_quaternion()
	var cur_g := skel.get_bone_global_pose(hand).basis.get_rotation_quaternion()
	var target := cur_g * rest_g.inverse() * _quat(e["hold"]) * rest_g
	var parent := skel.get_bone_parent(hand)
	var parent_g := skel.get_bone_global_pose(parent).basis.get_rotation_quaternion()
	skel.set_bone_pose_rotation(hand, (parent_g.inverse() * target).normalized())
	var fingers: Dictionary = e["fingers"]
	for name: Variant in fingers:
		var f := skel.find_bone(String(name))
		if f >= 0:
			skel.set_bone_pose_rotation(f, _quat(fingers[name]).normalized())
	skel.force_update_all_bone_transforms()
	var rest_local := skel.get_bone_rest(bone)
	var off: Array = e.get("offset", [0.0, 0.0, 0.0])  # M2-CHR-544: the shaft through the closed fist
	var origin := rest_local.origin + Vector3(float(off[0]), float(off[1]), float(off[2]))
	skel.set_bone_pose_rotation(bone, rest_local.basis.get_rotation_quaternion())
	skel.set_bone_pose_position(bone, origin)
	skel.force_update_all_bone_transforms()
	var pose := skel.get_bone_global_pose(bone)
	var axis := pose.basis.y.normalized()
	var slide := 0.0
	if axis.y > 0.2:
		var foot_y := pose.origin.y + axis.y * float(e["foot"])
		var to_floor := (float(g["floor_m"]) - foot_y) / axis.y
		var up: Array = g["upright_deg"]
		var tilt := rad_to_deg(acos(clampf(axis.y, -1.0, 1.0)))
		var w := 1.0 - smoothstep(0.0, 1.0, (tilt - float(up[0])) / (float(up[1]) - float(up[0])))
		slide = w * to_floor
		if foot_y + slide * axis.y < float(g["floor_m"]):
			slide = to_floor
		slide = clampf(slide, -float(g["slide_max_m"]), float(g["slide_max_m"]))
	skel.set_bone_pose_position(bone, origin + rest_local.basis.get_rotation_quaternion() * Vector3(0.0, slide, 0.0))


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


## M2-CHR-522: each panel is a chain of bones (the data's `levels` suffixes, from the hips down), solved from the hips
## down as hero_clips.skirt_solve does: each bone's least swing from the vertical, about its head where the bones above
## put it, then the lag limit at that level. The upper bone clears its own cloth; a middle one its own and all the
## cloth below it carried straight; the lowest its own, up to the middle one's swing (it hangs back from the knee). The
## lowest bone takes the overhang gather, the floor drape, then the floor gather.
static func _drive_skirt(skel: Skeleton3D, s: Dictionary) -> void:
	var prefix := String(s["bone_prefix"])
	var levels: Array = s["levels"]
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
	var heads: Array = []  # per panel: its bones' heads at rest, relative to the hips joint
	var rests: Array = []  # per panel: its bones' rest rotations in the pelvis's frame
	var axes: Array[Vector3] = []
	var us: Array[Vector3] = []
	for n: String in names:
		var hs: Array[Vector3] = []
		var gs: Array[Quaternion] = []
		var g := rq_h
		for x: String in levels:
			var b := skel.find_bone(n + x)
			hs.append(skel.get_bone_global_rest(b).origin - hips_rest.origin)
			g = g * _rest_q(skel, b)
			gs.append(g)
		heads.append(hs)
		rests.append(gs)
		var u := Vector3(hs[0].x, 0.0, hs[0].z).normalized()
		us.append(u)
		axes.append(down.cross(u).normalized())
	var lag := deg_to_rad(float(s["lag_deg_per_45"])) / (PI / 4.0)
	var top_swing := deg_to_rad(float(s["max_swing_deg"]))
	var angs: Array = []  # per panel: each bone's swing from the vertical
	for k: int in names.size():
		angs.append([] as Array[float])
	for lv: int in levels.size():
		var a: Array[float] = []
		var last_lv := lv == levels.size() - 1
		for k: int in names.size():
			var hk: Vector3 = heads[k][lv]
			var at := _head_posed(heads[k], axes[k], angs[k], lv)
			var c := PackedVector3Array()
			for y: int in range(lv, levels.size() if lv > 0 and not last_lv else lv + 1):
				c.append_array(cloth[names[k] + String(levels[y])])
			var cap: float = angs[k][lv - 1] if last_lv and lv > 0 else top_swing
			a.append(_swing(c, hk, axes[k], at - hk, legs, legs0, s, cap))
		a = _limit_lag(a, us, lag, top_swing)
		for k: int in names.size():
			(angs[k] as Array[float]).append(a[k])
	var flare := float(s["gather_flare"])
	var last := levels.size() - 1
	for k: int in names.size():
		var lo_name := names[k] + String(levels[last])
		var head: Vector3 = heads[k][last]
		var tip := _head_posed(heads[k], axes[k], angs[k], last)
		var axis: Vector3 = (rests[k][last] as Quaternion) * Vector3.UP
		var a_lo: float = angs[k][last]
		var sc := _overhang(cloth[lo_name], head, axis, axes[k], a_lo, tip, legs, s)
		var c_lo: PackedVector3Array = cloth[lo_name]
		var dp := inv_dp.inverse()
		var base_y := hips_pose.origin.y
		var sg := _gather(c_lo, head, axis, axes[k], a_lo, tip - head, dp, base_y, sc, s)
		if sg < float(s["drape_below_gather"]):
			a_lo = _drape(c_lo, head, axis, axes[k], a_lo, tip - head, dp, base_y, sc, s)
			angs[k][last] = a_lo
			sg = _gather(c_lo, head, axis, axes[k], a_lo, tip - head, dp, base_y, sc, s)
		sc = sg
		var gp := rq_h
		var prev := 0.0
		for lv: int in levels.size():
			var gr: Quaternion = rests[k][lv]
			var ang: float = angs[k][lv]
			var loc := gp.inverse() * Quaternion(axes[k], ang - prev) * gr
			skel.set_bone_pose_rotation(skel.find_bone(names[k] + String(levels[lv])), loc.normalized())
			gp = gr
			prev = ang
		skel.set_bone_pose_scale(
			skel.find_bone(lo_name), Vector3(1.0 + flare * (1.0 - sc), sc, 1.0 + flare * (1.0 - sc))
		)
	apply_folds(skel, fold_rig(skel))


## ADR 0140: what the even-numbered panels need to be derived from their odd neighbours (HeroSkirtFolds caches it):
## per even panel, its own and its two neighbours' bone indices per level, and each panel's rest rotations (in the
## pelvis's frame) and swing axis. Empty when the skeleton has no derived panels.
static func fold_rig(skel: Skeleton3D) -> Dictionary:
	var s: Dictionary = data().get("skirt", {})
	if s.is_empty():
		return {}
	var prefix := String(s["bone_prefix"])
	var levels: Array = s["levels"]
	var panels := {}  # number -> {bones, rests, axis}
	for i: int in skel.get_bone_count():
		var n := skel.get_bone_name(i)
		if not n.begins_with(prefix) or n.contains("."):
			continue
		var hips := skel.get_bone_parent(i)
		var hips_rest := skel.get_bone_global_rest(hips)
		var g := hips_rest.basis.get_rotation_quaternion()
		var bones: Array[int] = []
		var rests: Array[Quaternion] = []
		for x: Variant in levels:
			var b := skel.find_bone(n + String(x))
			bones.append(b)
			g = g * _rest_q(skel, b)
			rests.append(g)
		var h0 := skel.get_bone_global_rest(i).origin - hips_rest.origin
		var u := Vector3(h0.x, 0.0, h0.z).normalized()
		panels[int(n.substr(prefix.length()))] = {
			"bones": bones,
			"rests": rests,
			"axis": Vector3(0.0, -1.0, 0.0).cross(u).normalized(),
			"hips_q": hips_rest.basis.get_rotation_quaternion()
		}
	var count := panels.size()
	var derived: Array = []
	for k: int in panels:
		if k % 2 == 0 and panels.has((k + count - 1) % count) and panels.has((k + 1) % count):
			derived.append([panels[k], panels[(k + count - 1) % count], panels[(k + 1) % count]])
	if derived.is_empty():
		return {}
	return {
		"derived": derived,
		"fold": deg_to_rad(float(s["fold_deg"])),
		"from": deg_to_rad(float(s["fold_from_deg"])),
		"ease": deg_to_rad(float(s["fold_ease_deg"])),
		"tuck": deg_to_rad(float(s["fold_tuck_deg"])),
		"top": deg_to_rad(float(s["max_swing_deg"]))
	}


## ADR 0140: sets each even-numbered panel from its odd neighbours' current pose: the larger of their swings (read
## back out of their rotations; at the hem, their mean) and the mean of their gathers (scales), the lowest bone `fold`
## further out once that lies past `from` (hero_clips.derive_folds, the same rule).
static func apply_folds(skel: Skeleton3D, rig: Dictionary) -> void:
	if rig.is_empty():
		return
	for trio: Array in rig["derived"]:
		var own: Dictionary = trio[0]
		var a := _swings(skel, trio[1])
		var b := _swings(skel, trio[2])
		var last := a.size() - 1
		var gp: Quaternion = own["hips_q"]
		var prev := 0.0
		for lv: int in a.size():
			var ang := maxf(a[lv], b[lv])  # the outer of the two: the mean cut into a thigh between them
			if lv == last:
				ang = 0.5 * (a[lv] + b[lv])  # but the hem their mean: the outer of the two folded it into spikes
				ang = maxf(ang, prev - float(rig["tuck"]))  # row 56: never tucked under the knee (cloud pass 6's notch)
				var t := (ang - float(rig["from"])) / float(rig["ease"])
				ang = minf(ang + float(rig["fold"]) * smoothstep(0.0, 1.0, t), float(rig["top"]))
			var gr: Quaternion = own["rests"][lv]
			var loc := gp.inverse() * Quaternion(own["axis"], ang - prev) * gr
			skel.set_bone_pose_rotation(own["bones"][lv], loc.normalized())
			gp = gr
			prev = ang
		var lo_a := skel.get_bone_pose_scale((trio[1] as Dictionary)["bones"][last])
		var lo_b := skel.get_bone_pose_scale((trio[2] as Dictionary)["bones"][last])
		skel.set_bone_pose_scale(own["bones"][last], 0.5 * (lo_a + lo_b))


## A panel's cumulative swing from the vertical at each level, read back out of its bones' pose rotations.
static func _swings(skel: Skeleton3D, panel: Dictionary) -> Array[float]:
	var out: Array[float] = []
	var gp: Quaternion = panel["hips_q"]
	var axis: Vector3 = panel["axis"]
	var prev := 0.0
	var rests: Array = panel["rests"]
	var bones: Array = panel["bones"]
	for lv: int in bones.size():
		var gr: Quaternion = rests[lv]
		var q := gp * skel.get_bone_pose_rotation(bones[lv]) * gr.inverse()
		prev += 2.0 * atan2(Vector3(q.x, q.y, q.z).dot(axis), q.w)
		out.append(prev)
		gp = gr
	return out


## Where a panel's bones above level `lv` put its head: each bone `i` swung angs[i] about `axis` (from the vertical).
static func _head_posed(heads: Array, axis: Vector3, angs: Array, lv: int) -> Vector3:
	var p: Vector3 = heads[0]
	for i: int in range(1, lv + 1):
		p += Basis(axis, float(angs[i - 1])) * ((heads[i] as Vector3) - (heads[i - 1] as Vector3))
	return p


## The floor drape (hero_clips.skirt_solve): a lowest bone whose cloth (at length scale `sc`) would gather shorter
## than drape_below_gather first swings out onto the floor, by the least swing in (ang, drape_max_deg] (grid_deg
## steps, then `bisect` halvings) at which it stays floor_clear_m above the floor; drape_max_deg when none does.
static func _drape(
	cloth: PackedVector3Array,
	knee: Vector3,
	along: Vector3,
	axis: Vector3,
	ang: float,
	shift: Vector3,
	dp: Quaternion,
	base_y: float,
	sc: float,
	s: Dictionary
) -> float:
	var floor_y := float(s["floor_clear_m"])
	var top := deg_to_rad(float(s["drape_max_deg"]))
	if cloth.is_empty() or ang >= top or _low(cloth, knee, along, axis, ang, shift, dp, base_y, sc) >= floor_y:
		return ang
	var step := deg_to_rad(float(s["grid_deg"]))
	var lo := ang
	var a := minf(lo + step, top)
	while _low(cloth, knee, along, axis, a, shift, dp, base_y, sc) < floor_y:
		if a >= top - 1e-9:
			return top
		lo = a
		a = minf(a + step, top)
	var hi := a
	for _i: int in int(s["bisect"]):
		var mid := 0.5 * (lo + hi)
		if _low(cloth, knee, along, axis, mid, shift, dp, base_y, sc) >= floor_y:
			hi = mid
		else:
			lo = mid
	return hi


## The lowest bone's gather: the largest length scale in [gather_min, 1] (`bisect` halvings) at which its cloth (scaled
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


## The overhang gather: a lowest bone swung out past overhang_from_deg lies over the legs; the cloth that would run on
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
		for x: Variant in s["levels"]:
			out[n + String(x)] = PackedVector3Array()
			want[skel.find_bone(n + String(x))] = n + String(x)
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


## Least angle in [0, top] at which the cloth (turned about `pivot` along `axis`, then shifted by `shift`) keeps its
## rest clearance from the legs: coarse steps (the last one at `top`), then bisection; when no angle clears, the
## nearest.
static func _swing(
	cloth: PackedVector3Array,
	pivot: Vector3,
	axis: Vector3,
	shift: Vector3,
	legs: Array[PackedVector3Array],
	legs0: Array[PackedVector3Array],
	s: Dictionary,
	top: float
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
	var step := deg_to_rad(float(s["grid_deg"]))
	var best := 0.0
	var best_m := _margin(cloth, pivot, axis, shift, 0.0, legs, need, false)
	var lo := 0.0
	var ang := minf(step, top)
	while true:
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
		if ang >= top - 1e-9:
			break
		ang = minf(ang + step, top)
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
