class_name BattleScreenSpread
extends RefCounted
## Creatures' as-played audit (10-30, pillar 4): two foes seated one behind the other overlapped on screen (the
## Lantern Eel and the Reef Crab at the tideline, two Slag Tortoises on the stair, two Wickfry under the tower), and
## the bottom-left foe of the underway fights sat partly under the command menu. BattleLineup keeps footprints apart
## on the ground, which does not stop one body covering another from the lens.
##
## At spawn, after the line-up, each foe's screen box is taken from the fight's rest frame (the authored camera, fitted
## by camera.rest_by_enemy). While two foes' boxes share more than max_share of the smaller one, they step apart along
## the screen's sideways axis (step_m each pass, iters passes); a foe whose box meets the command menu's rect steps
## toward the screen's middle. No foe moves more than max_shift_m from its mark. choreo.json spacing.screen.

const REF := Vector2(1920.0, 1080.0)


## Spreads `fighters` (FighterStandIns, one side) on screen. `cam` is the camera, `xf` and `fov` the rest frame
## (the camera's parent space).
static func apply(fighters: Array, cam: Camera3D, xf: Transform3D, fov: float, data: Dictionary) -> void:
	var sc := (data.get("spacing", {}) as Dictionary).get("screen", {}) as Dictionary
	if sc.is_empty() or cam == null or fighters.size() < 1:
		return
	var parent := cam.get_parent() as Node3D
	var lens := (parent.global_transform if parent != null else Transform3D.IDENTITY) * xf
	var side := Vector3(lens.basis.x.x, 0.0, lens.basis.x.z).normalized()
	var avoid := HudLayout.rect_of(HudLayout.section(&"commands"))
	var shapes: Array[AABB] = []  # each body's box about its own origin
	var homes: Array[Vector3] = []
	for f: FighterStandIn in fighters:
		shapes.append(_shape(f))
		homes.append(f.global_position)
	var step := float(sc.get("step_m", 0.1))
	var cap := float(sc.get("max_shift_m", 1.0))
	var max_share := float(sc.get("max_share", 0.2))
	for _pass in int(sc.get("iters", 0)):
		var boxes: Array[Rect2] = []
		for i in fighters.size():
			boxes.append(screen_box(lens, fov, shapes[i], (fighters[i] as Node3D).global_position))
		var moves: Array[float] = []
		moves.resize(fighters.size())
		moves.fill(0.0)
		for i in fighters.size():
			for j in range(i + 1, fighters.size()):
				if share(boxes[i], boxes[j]) > max_share:
					var left := i if boxes[i].get_center().x <= boxes[j].get_center().x else j
					var right := j if left == i else i
					moves[left] -= step * 0.5
					moves[right] += step * 0.5
			if boxes[i].intersects(avoid):
				moves[i] += step if boxes[i].get_center().x < REF.x * 0.5 else -step
		var moved := false
		for i in fighters.size():
			if moves[i] == 0.0:
				continue
			var f := fighters[i] as Node3D
			var p := f.global_position + side * moves[i]
			var off := p - homes[i]
			if off.length() > cap:
				p = homes[i] + off.normalized() * cap
			moved = moved or not p.is_equal_approx(f.global_position)
			f.global_position = p
		if not moved:
			return


## The share of the smaller box that two screen boxes have in common.
static func share(a: Rect2, b: Rect2) -> float:
	var inter := a.intersection(b)
	var small := minf(a.get_area(), b.get_area())
	return inter.get_area() / small if inter.has_area() and small > 0.0 else 0.0


## `shape` (a body's box about its origin) at `at`, on the 1920x1080 screen of the lens `lens` at `fov`.
static func screen_box(lens: Transform3D, fov: float, shape: AABB, at: Vector3) -> Rect2:
	var inv := lens.affine_inverse()
	var half := tan(deg_to_rad(fov) * 0.5)
	var aspect := REF.x / REF.y
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for i in 8:
		var q := inv * (at + shape.get_endpoint(i))
		var depth := maxf(-q.z, 0.05)
		var p := Vector2(
			(q.x / (depth * half * aspect) + 1.0) * 0.5 * REF.x, (1.0 - q.y / (depth * half)) * 0.5 * REF.y
		)
		lo = lo.min(p)
		hi = hi.max(p)
	return Rect2(lo, hi - lo)


## A fighter's visible body about its origin: its actor's meshes (not the stand-in's ring), else its stand-in's
## height and radius.
static func _shape(f: FighterStandIn) -> AABB:
	var out := AABB()
	var first := true
	var meshes: Array[Node] = f.actor().find_children("*", "MeshInstance3D", true, false) if f.has_actor() else []
	for n in meshes:
		var mi := n as MeshInstance3D
		if mi.mesh == null or not mi.is_visible_in_tree():
			continue
		var box := mi.global_transform * mi.get_aabb()
		box.position -= f.global_position
		out = box if first else out.merge(box)
		first = false
	if first:
		var r := float(f.spec.get("radius", 0.3))
		var h := float(f.spec.get("height", 1.7))
		out = AABB(Vector3(-r, float(f.spec.get("hover", 0.0)), -r), Vector3(r * 2.0, h, r * 2.0))
	return out
