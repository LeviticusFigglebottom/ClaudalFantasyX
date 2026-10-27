class_name BattleLineup
extends RefCounted
## M3-BPR-403: the opening line-up spaced by the real models' footprints. The slot markers were laid out for
## primitive stand-ins; a creature model (or a real hero) can overlap its neighbour on its mark. Each side's
## fighters are pushed apart on the ground until every pair keeps both footprints + spacing.clearance_m between
## centres, each moving at most spacing.lineup_max_shift_m from its mark (the camera's safe frames stay valid).
## Deterministic (fixed pair order and iteration count). Presentation only.


## Ground offsets (Vector3, y 0) for `points` with footprint `radii`: pairwise relaxation along `axis` only (the
## camera's screen-horizontal on the ground, so nobody moves toward the camera and behind the HUD), `iters` passes,
## each point's total shift clamped to `max_shift`. A pair already far enough apart in depth is left alone.
static func spread(
	points: Array[Vector3], radii: Array[float], clear: float, max_shift: float, iters: int, axis := Vector3.RIGHT
) -> Array:
	var n := points.size()
	var ax := Vector3(axis.x, 0.0, axis.z).normalized()
	if ax == Vector3.ZERO:
		ax = Vector3.RIGHT
	var at: Array[Vector3] = []
	at.assign(points)
	for _pass in iters:
		var moved := false
		for i in n:
			for j in range(i + 1, n):
				var d := at[j] - at[i]
				d.y = 0.0
				var need := radii[i] + radii[j] + clear
				var along := d.dot(ax)
				var depth := (d - ax * along).length()
				if depth >= need:
					continue
				var want := sqrt(need * need - depth * depth)
				if absf(along) >= want - 0.0001:
					continue
				var sgn := 1.0 if along >= 0.0 else -1.0
				var push := ax * sgn * (want - absf(along)) * 0.5
				at[i] = _clamped(points[i], at[i] - push, max_shift)
				at[j] = _clamped(points[j], at[j] + push, max_shift)
				moved = true
		if not moved:
			break
	var out: Array = []
	for i in n:
		out.append(at[i] - points[i])
	return out


static func _clamped(home: Vector3, p: Vector3, max_shift: float) -> Vector3:
	var off := p - home
	off.y = 0.0
	if off.length() > max_shift:
		off = off.normalized() * max_shift
	return home + off


## Spaces `fighters` (FighterStandIns on one side, already on their marks) by their footprints along `axis`
## (`data` is choreo.json: spacing.clearance_m, lineup_max_shift_m, lineup_iters). A primitive uses its spec radius.
static func apply(fighters: Array, data: Dictionary, axis := Vector3.RIGHT) -> void:
	var sp := data.get("spacing", {}) as Dictionary
	var pts: Array[Vector3] = []
	var radii: Array[float] = []
	for f: FighterStandIn in fighters:
		pts.append(f.global_position)
		var r := BattleChoreoPlan.footprint(f, data)
		radii.append(r if r > 0.0 else float(f.spec.get("radius", 0.0)))
	var offs := spread(
		pts,
		radii,
		float(sp.get("clearance_m", 0.0)),
		float(sp.get("lineup_max_shift_m", 0.0)),
		int(sp.get("lineup_iters", 0)),
		axis
	)
	for i in fighters.size():
		(fighters[i] as FighterStandIn).global_position += offs[i] as Vector3
