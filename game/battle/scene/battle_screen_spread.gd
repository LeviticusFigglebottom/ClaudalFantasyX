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
## toward the screen's middle. A step that would bring two footprints closer than BattleLineup keeps them takes the
## neighbour along, else goes straight back from the lens, else is not taken; a foe the line-up left too close at its
## cap keeps its seat. No foe moves more than max_shift_m from its mark. choreo.json spacing.screen.

const REF := Vector2(1920.0, 1080.0)


## Spreads `fighters` (FighterStandIns, one side) on screen. `cam` is the camera, `xf` and `fov` the rest frame
## (the camera's parent space).
static func apply(fighters: Array, cam: Camera3D, xf: Transform3D, fov: float, data: Dictionary) -> void:
	var sc := (data.get("spacing", {}) as Dictionary).get("screen", {}) as Dictionary
	if sc.is_empty() or cam == null or fighters.size() < 2:
		return  # a lone foe (a boss on its mark) keeps its seat
	var parent := cam.get_parent() as Node3D
	var lens := (parent.global_transform if parent != null else Transform3D.IDENTITY) * xf
	var side := Vector3(lens.basis.x.x, 0.0, lens.basis.x.z).normalized()
	var back := Vector3(-lens.basis.z.x, 0.0, -lens.basis.z.z).normalized()  # away from the lens
	var avoid := HudLayout.rect_of(HudLayout.section(&"commands"))
	var shapes: Array[AABB] = []  # each body's box about its own origin
	var homes: Array[Vector3] = []
	var radii: Array[float] = []  # BattleLineup's footprints: no step brings two closer than they keep on the ground
	for f: FighterStandIn in fighters:
		shapes.append(_shape(f))
		homes.append(f.global_position)
		var r := BattleChoreoPlan.footprint(f, data)
		radii.append(r if r > 0.0 else float(f.spec.get("radius", 0.0)))
	var clear := float((data.get("spacing", {}) as Dictionary).get("clearance_m", 0.0))
	var pinned: Array[bool] = []  # one the line-up left too close at its cap: its seat stays as BattleLineup left it
	for i in fighters.size():
		pinned.append(_crowded(fighters, radii, clear, i))
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
			if moves[i] == 0.0 or pinned[i]:
				continue
			var f := fighters[i] as Node3D
			var p := f.global_position + side * moves[i]
			var off := p - homes[i]
			if off.length() > cap:
				p = homes[i] + off.normalized() * cap
			if _crowds(fighters, radii, clear, i, p) and not _carry(fighters, radii, clear, i, p, homes, cap):
				p = f.global_position + back * absf(moves[i])  # boxed in on the ground: a step back from the lens
				off = p - homes[i]
				if off.length() > cap or _crowds(fighters, radii, clear, i, p):
					continue
			moved = moved or not p.is_equal_approx(f.global_position)
			f.global_position = p
		if not moved:
			return


## True when fighter `i` at `p` would stand closer to another than both footprints and `clear` (on the ground),
## where it is not that close already.
static func _crowds(fighters: Array, radii: Array[float], clear: float, i: int, p: Vector3) -> bool:
	var here := (fighters[i] as Node3D).global_position
	for j in fighters.size():
		if j == i:
			continue
		var o := (fighters[j] as Node3D).global_position
		var need := radii[i] + radii[j] + clear
		var now := Vector2(here.x - o.x, here.z - o.z).length()
		var then := Vector2(p.x - o.x, p.z - o.z).length()
		if then < need and then < now:
			return true
	return false


## True when fighter `i` already stands closer to another than both footprints and `clear`.
static func _crowded(fighters: Array, radii: Array[float], clear: float, i: int) -> bool:
	var here := (fighters[i] as Node3D).global_position
	for j in fighters.size():
		var o := (fighters[j] as Node3D).global_position
		if j != i and Vector2(here.x - o.x, here.z - o.z).length() < radii[i] + radii[j] + clear - 0.01:
			return true
	return false


## Fighter `i` stepping to `p` takes along each neighbour it would crowd, by the same step, when every one of them
## can go (within `cap` of its mark, crowding no one). True when they moved (`i` itself is left to the caller).
static func _carry(
	fighters: Array, radii: Array[float], clear: float, i: int, p: Vector3, homes: Array[Vector3], cap: float
) -> bool:
	var here := (fighters[i] as Node3D).global_position
	var delta := p - here
	var carried: Array[int] = []
	for j in fighters.size():
		if j == i:
			continue
		var o := (fighters[j] as Node3D).global_position
		var then := Vector2(p.x - o.x, p.z - o.z).length()
		if then < radii[i] + radii[j] + clear and then < Vector2(here.x - o.x, here.z - o.z).length():
			carried.append(j)
	if carried.is_empty():
		return false
	for j in carried:
		if _crowded(fighters, radii, clear, j):
			return false
		var q := (fighters[j] as Node3D).global_position + delta
		if (q - homes[j]).length() > cap:
			return false
		for k in fighters.size():
			if k == j or k == i or carried.has(k):
				continue
			var o := (fighters[k] as Node3D).global_position
			if Vector2(q.x - o.x, q.z - o.z).length() < radii[j] + radii[k] + clear:
				return false
	for j in carried:
		(fighters[j] as Node3D).global_position += delta
	return true


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
	var meshes: Array[Node] = []
	if f.has_actor():
		meshes = f.actor().find_children("*", "MeshInstance3D", true, false)
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
