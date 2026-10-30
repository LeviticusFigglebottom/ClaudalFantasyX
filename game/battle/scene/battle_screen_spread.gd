class_name BattleScreenSpread
extends RefCounted
## Creatures' as-played audit (10-30, pillar 4): two foes seated one behind the other overlapped on screen (the
## Lantern Eel and the Reef Crab at the tideline, two Slag Tortoises on the stair, two Wickfry under the tower), and
## the bottom-left foe of the underway fights sat partly under the command menu. BattleLineup keeps footprints apart
## on the ground, which does not stop one body covering another from the lens.
##
## At spawn, after the line-up, each foe's screen box is taken from the fight's rest frame (the authored camera, fitted
## by camera.rest_by_enemy). While two foes' boxes share more than max_share of the smaller one, they step apart
## (step_m each pass, iters passes): the left one further from the party (on the battle axis the screen's right is
## toward the party), the right one back from the lens. A foe whose box meets the command menu's rect steps back (up
## the screen), else toward the middle. No step brings two footprints closer than BattleLineup keeps them (a first cut
## carried the causeway's Gull into Rhen's melee lane); a foe the line-up left too close at its cap keeps its seat. No
## foe moves more than max_shift_m from its mark. choreo.json spacing.screen.

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
	var avoid := menu_rect(data)
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
		# Each foe's steps, most wanted first: a pair's left one further left (away from the party, out of the heroes'
		# melee lanes) else back, its right one back from the lens; a foe on the command menu back (up the screen), else
		# right. None steps onto the menu.
		var wants: Array = []
		for i in fighters.size():
			wants.append([])
		for i in fighters.size():
			for j in range(i + 1, fighters.size()):
				if share(boxes[i], boxes[j]) > max_share:
					var left := i if boxes[i].get_center().x <= boxes[j].get_center().x else j
					var right := j if left == i else i
					(wants[left] as Array).append_array([-side * step, back * step])
					(wants[right] as Array).append(back * step)
			if boxes[i].intersects(avoid):
				(wants[i] as Array).append_array([back * step, (back + side).normalized() * step, side * step])
		var moved := false
		for i in fighters.size():
			if pinned[i]:
				continue
			var f := fighters[i] as Node3D
			for d: Vector3 in wants[i]:
				var p := f.global_position + d
				if (p - homes[i]).length() > cap or _crowds(fighters, radii, clear, i, p):
					continue
				if screen_box(lens, fov, shapes[i], p).intersects(avoid) and not boxes[i].intersects(avoid):
					continue  # never onto the command menu
				f.global_position = p
				moved = true
				break
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


## The sweep (10-30, ch04_derelict_leeches): Ilun's net, on the middle party slot, reached under the timeline when he
## acted. A fighter `f` whose box on the rest frame meets one of `rects` (1920x1080) steps toward the screen's left
## (toward the foes and the middle), step_m at a time, up to spacing.screen.hud_shift_m from where it stands.
static func clear_of_hud(
	f: FighterStandIn, cam: Camera3D, xf: Transform3D, fov: float, rects: Array, data: Dictionary
) -> void:
	var sc := (data.get("spacing", {}) as Dictionary).get("screen", {}) as Dictionary
	if sc.is_empty() or cam == null or f == null:
		return
	var parent := cam.get_parent() as Node3D
	var lens := (parent.global_transform if parent != null else Transform3D.IDENTITY) * xf
	var left := -Vector3(lens.basis.x.x, 0.0, lens.basis.x.z).normalized()
	var shape := _shape(f)
	var home := f.global_position
	var step := float(sc.get("step_m", 0.1))
	var cap := float(sc.get("hud_shift_m", 0.0))
	var p := home
	while (p - home).length() + step <= cap + 0.001:
		var box := screen_box(lens, fov, shape, p)
		var hit := false
		for r: Rect2 in rects:
			hit = hit or box.intersects(r)
		if not hit:
			break
		p += left * step
	f.global_position = p


## The command menu's rect, less its top spacing.screen.menu_edge_px: a foe's leg tips may reach that far over the
## menu's top edge when every step off it would push two footprints together (the causeway's and the flats' Crabs,
## boxed in by the Eel behind and the Gull beside). Its body may not.
static func menu_rect(data: Dictionary) -> Rect2:
	var r := HudLayout.rect_of(HudLayout.section(&"commands"))
	var edge := float(
		((data.get("spacing", {}) as Dictionary).get("screen", {}) as Dictionary).get("menu_edge_px", 0.0)
	)
	return Rect2(r.position + Vector2(0.0, edge), r.size - Vector2(0.0, edge))


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
