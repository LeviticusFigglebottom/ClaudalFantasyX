class_name BattleBossHeroShot
extends RefCounted
## M3-BPR-423 (the Lead, 03:41: "each boss intro needs a hero shot of the boss, not a wide view of the arena"): the
## boss intro's camera, as data in choreo.json boss_intro.hero. A low camera looks up at the boss from the viewer's
## side of the battle axis (yaw_deg from the boss toward the party, turned toward the viewer, so the line is never
## crossed and the party can stand at the frame's edge), at the distance where the boss's bounds fill `fill` of the
## screen's height. The first pose, biggest fill first, that holds wins:
## - the boss's top inside the HUD-safe frame and its upper body (head_frac of its height) clear of the title card
##   (its feet may pass behind the card, as on a poster);
## - its middle inside the safe frame's sides;
## - nothing of the arena between the lens and the boss (each arena mesh's bounds against sight lines to the boss: the
##   Hullgnaw raft's rail had cut the frame in half), and the lens inside no arena mesh;
## - no party member crowding the frame (_party_small) or standing in front of the boss.
## One with a party member in frame is preferred (the Drownbell's intro had lost the party). None holding: {}.

const SIGHT_FRACS: Array[float] = [0.3, 0.55, 0.8]
## Nothing may stand this far straight over the lens (a lens under the Wraith's deck saw its edge blot half the frame).
const HEADROOM_M := 4.0
## Rays cast across the frame's lower half (NDC x, y; y up): a near surface filling more than FOREGROUND_MAX of them
## within FOREGROUND_NEAR of the way to the boss rejects the pose.
const FOREGROUND_RAYS: Array[Vector2] = [
	Vector2(-0.6, -0.15),
	Vector2(0.0, -0.15),
	Vector2(0.6, -0.15),
	Vector2(-0.6, -0.45),
	Vector2(0.0, -0.45),
	Vector2(0.6, -0.45),
	Vector2(-0.6, -0.75),
	Vector2(0.0, -0.75),
	Vector2(0.6, -0.75),
]
const FOREGROUND_NEAR := 0.45
const FOREGROUND_MAX := 0.34
## How far either side of its middle (of the body's narrower width) the sight lines across the boss reach.
const SIGHT_SPREAD := 0.35

## Mesh -> its TriangleMesh, built once (the arena's meshes repeat across intros and retries).
static var _tri_cache: Dictionary = {}


## The hero pose {pos, look, fov} for `intro`'s boss, whose bounds (camera parent space) are `bounds`, standing on
## `slot`. {} when no candidate holds (the intro then falls back to the fitted shot).
static func search(intro: BattleBossIntro, bounds: AABB, slot: Vector3) -> Dictionary:
	var hc := intro.cfg.get("hero", {}) as Dictionary
	var director := intro._choreo.camera
	if hc.is_empty() or director == null or bounds.size == Vector3.ZERO:
		return {}
	var occluders := _occluders(intro, bounds)
	var fovs: Variant = hc.get("fov", [40.0])
	var h := bounds.size.y
	var mid := bounds.get_center()
	var toward_party := -director.axis()
	var without_party := {}
	for fill: Variant in hc.get("fill", [0.6]):
		for fov: Variant in fovs if fovs is Array else [fovs]:
			for yaw: Variant in hc.get("yaw_deg", [30.0]):
				for up: Variant in hc.get("cam_height_m", [1.0]):
					var dir := toward_party.rotated(Vector3.UP, _toward_viewer(director, float(yaw)))
					var look := Vector3(mid.x, bounds.position.y + h * float(hc.get("look_frac", 0.5)), mid.z)
					var dist := h / maxf(float(fill), 0.05) * 0.5 / tan(deg_to_rad(float(fov)) * 0.5)
					dist = clampf(dist, float(hc.get("min_m", 1.5)), float(hc.get("max_m", 40.0)))
					dist += maxf(bounds.size.x, bounds.size.z) * 0.5  # from the boss's near face, not its centre
					var pos := Vector3(mid.x, slot.y + float(up), mid.z) + dir * dist
					var pose := {"pos": pos, "look": look, "fov": float(fov)}
					if not _holds(intro, pose, bounds, occluders):
						continue
					if _party_in_frame(intro, pose):
						return pose
					if without_party.is_empty():
						without_party = pose
	return without_party


## `yaw` degrees, signed to turn from the boss-to-party direction toward the viewer's side.
static func _toward_viewer(director: BattleCameraDirector, yaw: float) -> float:
	var to_party := -director.axis()
	var probe := to_party.rotated(Vector3.UP, deg_to_rad(absf(yaw)))
	var side := signf(probe.dot(director.viewer_side()))
	return deg_to_rad(absf(yaw)) * (side if side != 0.0 else 1.0)


static func _holds(intro: BattleBossIntro, pose: Dictionary, bounds: AABB, occluders: Array[Dictionary]) -> bool:
	var director := intro._choreo.camera
	var hc := intro.cfg.get("hero", {}) as Dictionary
	var pos: Vector3 = pose["pos"]
	var xform := Transform3D(Basis.looking_at((pose["look"] as Vector3) - pos, Vector3.UP), pos)
	var safe := director.data.get("safe_frame", {}) as Dictionary
	var mid := bounds.get_center()
	var top := Vector3(mid.x, bounds.end.y, mid.z)
	var centre := Vector3(mid.x, bounds.position.y + bounds.size.y * 0.5, mid.z)
	var sides := {"left": safe.get("left", 0.0), "right": safe.get("right", 0.0)}
	if not director.in_frame(xform, float(pose["fov"]), top, {"top": safe.get("top", 0.0)}):
		return false
	if not director.in_frame(xform, float(pose["fov"]), centre, sides):
		return false
	var chest := Vector3(mid.x, bounds.position.y + bounds.size.y * float(hc.get("head_frac", 0.7)), mid.z)
	if not intro._clears_card(pose, chest) or not _party_small(intro, pose):
		return false
	if sight_blocked(occluders, pos, pos + Vector3.UP * HEADROOM_M):
		return false  # under a deck or an overhang
	if foreground_share(occluders, pose, bounds) > FOREGROUND_MAX:
		return false  # a near wall or bulwark fills the frame's foot (the Wraith's deck cut the party at the waist)
	for p in sight_points(bounds, xform):  # last: the dearest test
		if sight_blocked(occluders, pos, p):
			return false
	return true


## The points of the boss a hero shot must see: up its middle, and across its body at mid-height (Toma's shield
## stood before the Matron, off her middle). `xform` is the lens.
static func sight_points(bounds: AABB, xform: Transform3D) -> Array[Vector3]:
	var mid := bounds.get_center()
	var out: Array[Vector3] = []
	for f in SIGHT_FRACS:
		out.append(Vector3(mid.x, bounds.position.y + bounds.size.y * f, mid.z))
	var across := BattleChoreo._flat(xform.basis.x) * minf(bounds.size.x, bounds.size.z) * SIGHT_SPREAD
	var waist := Vector3(mid.x, bounds.position.y + bounds.size.y * 0.55, mid.z)
	out.append(waist - across)
	out.append(waist + across)
	return out


## True when some occluder's surface crosses the segment `from`..`to` (camera parent space). Each occluder's bounds
## filter first; then its mesh's triangles decide (big14's raft and deck are merged meshes whose bounds take in the
## boss: bounds alone had to skip them, and the rail and the deck's edge came back into the frame).
static func sight_blocked(occluders: Array[Dictionary], from: Vector3, to: Vector3) -> bool:
	for o in occluders:
		var box: AABB = o["box"]
		if not box.has_point(from) and box.intersects_segment(from, to) == null:
			continue
		var inv := (o["xform"] as Transform3D).affine_inverse()
		var tm := _triangles(o["mesh"] as Mesh)
		if tm != null and not tm.intersect_segment(inv * from, inv * to).is_empty():
			return true
	return false


## The share of FOREGROUND_RAYS that meet a surface nearer than FOREGROUND_NEAR of the lens's distance to the boss.
static func foreground_share(occluders: Array[Dictionary], pose: Dictionary, bounds: AABB) -> float:
	var pos: Vector3 = pose["pos"]
	var basis := Basis.looking_at((pose["look"] as Vector3) - pos, Vector3.UP)
	var half := tan(deg_to_rad(float(pose["fov"])) * 0.5)
	var aspect := (
		float(ProjectSettings.get_setting("display/window/size/viewport_width", 16))
		/ maxf(float(ProjectSettings.get_setting("display/window/size/viewport_height", 9)), 1.0)
	)
	var reach := pos.distance_to(bounds.get_center()) * FOREGROUND_NEAR
	var hits := 0
	for ndc in FOREGROUND_RAYS:
		var dir := (basis * Vector3(ndc.x * half * aspect, ndc.y * half, -1.0)).normalized()
		if sight_blocked(occluders, pos, pos + dir * reach):
			hits += 1
	return float(hits) / float(FOREGROUND_RAYS.size())


static func _triangles(mesh: Mesh) -> TriangleMesh:
	if not _tri_cache.has(mesh):
		_tri_cache[mesh] = mesh.generate_triangle_mesh()
	return _tri_cache[mesh] as TriangleMesh


## True when each party member (its body, _body) is off screen, or inside the safe frame's top and sides (clear of
## the timeline; the command menu is hidden through the intro, so a hero may stand at the frame's foot) and at most
## hero.party_max_h (else fit.party_max_h) of the screen tall: the party is welcome at the foot of a hero shot.
## Unlike corner tests, a fighter filling the lens (every corner off screen) counts as on screen: its projected
## rectangle is what is checked, and a box reaching behind the lens fails outright.
static func _party_small(intro: BattleBossIntro, pose: Dictionary) -> bool:
	var director := intro._choreo.camera
	var pos: Vector3 = pose["pos"]
	var inv := Transform3D(Basis.looking_at((pose["look"] as Vector3) - pos, Vector3.UP), pos).affine_inverse()
	var half := tan(deg_to_rad(float(pose["fov"])) * 0.5)
	var aspect := director._aspect()
	var safe := director.data.get("safe_frame", {}) as Dictionary
	var fit_max := float((intro.cfg.get("fit", {}) as Dictionary).get("party_max_h", 1.0))
	var hero_cfg := intro.cfg.get("hero", {}) as Dictionary
	var max_h := float(hero_cfg.get("party_max_h", fit_max))
	for c in intro._engine.party_active:
		var f := intro._ctl.stage.stand_in(c.id)
		if f == null or not f.is_visible_in_tree():
			continue
		var b := _body(intro, f)
		var lo := Vector2(INF, INF)
		var hi := Vector2(-INF, -INF)
		var behind := false
		for i in 8:
			var q := inv * b.get_endpoint(i)
			if -q.z <= 0.05:
				behind = true
				continue
			var p := Vector2(q.x / (-q.z * half * aspect), q.y / (-q.z * half))
			lo = lo.min(p)
			hi = hi.max(p)
		if lo.x > hi.x:
			continue  # wholly behind the lens
		var on_screen := hi.x >= -1.0 and lo.x <= 1.0 and hi.y >= -1.0 and lo.y <= 1.0
		if not on_screen:
			continue
		if behind:
			return false  # reaches past the lens while on screen: it fills the frame
		var inside := (
			lo.x >= -1.0 + 2.0 * float(safe.get("left", 0.0))
			and hi.x <= 1.0 - 2.0 * float(safe.get("right", 0.0))
			and hi.y <= 1.0 - 2.0 * float(safe.get("top", 0.0))
		)
		if not inside or (hi.y - lo.y) * 0.5 > max_h:
			return false
	return true


## A hero's body (camera parent space): its stand-in's height and radius over its feet. Not its meshes' bounds: big14's
## actors carry their props (Toma's spear and shield span 1.8 m), which made every hero look in the way.
static func _body(intro: BattleBossIntro, f: FighterStandIn) -> AABB:
	var feet := intro._choreo.camera._parent_inverse() * f.global_position
	var r := float(f.spec.get("radius", 0.3))
	var h := float(f.spec.get("height", 1.7))
	return AABB(feet + Vector3(-r, float(f.spec.get("hover", 0.0)), -r), Vector3(r * 2.0, h, r * 2.0))


## True when some party member is (at least partly) on screen in `pose`.
static func _party_in_frame(intro: BattleBossIntro, pose: Dictionary) -> bool:
	var director := intro._choreo.camera
	var pos: Vector3 = pose["pos"]
	var xform := Transform3D(Basis.looking_at((pose["look"] as Vector3) - pos, Vector3.UP), pos)
	for c in intro._engine.party_active:
		var f := intro._ctl.stage.stand_in(c.id)
		if f != null and f.is_visible_in_tree():
			var b := _body(intro, f)
			if director.in_frame(xform, float(pose["fov"]), b.get_center(), {}):
				return true
	return false


## What could stand between the lens and the boss, as {box, xform, mesh} in the camera's parent space: every visible
## mesh (and each multimesh instance) under the battle's Arena node, and each party member's meshes (Toma's shield
## counts). Bounds lying wholly below the boss's feet are left out.
static func _occluders(intro: BattleBossIntro, boss: AABB) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var inv := intro._choreo.camera._parent_inverse()
	var feet := boss.position.y + 0.05
	var roots: Array[Node] = []
	for c in intro._engine.party_active:
		var hero := intro._ctl.stage.stand_in(c.id)
		if hero != null and hero.is_visible_in_tree():
			roots.append(hero)
	var arena := intro._ctl.get_node_or_null(NodePath(String(BattleArena.ARENA_NODE)))
	if arena != null:
		roots.append(arena)
	for root in roots:
		for n in root.find_children("*", "GeometryInstance3D", true, false):
			var gi := n as GeometryInstance3D
			if not gi.is_visible_in_tree():
				continue
			var mmi := gi as MultiMeshInstance3D
			var mi := gi as MeshInstance3D
			if mmi != null and mmi.multimesh != null and mmi.multimesh.mesh != null:
				var count := mmi.multimesh.visible_instance_count
				for i in count if count >= 0 else mmi.multimesh.instance_count:
					var x := inv * mmi.global_transform * mmi.multimesh.get_instance_transform(i)
					_add(out, x, mmi.multimesh.mesh, feet)
			elif mi != null and mi.mesh != null:
				_add(out, inv * mi.global_transform, mi.mesh, feet)
	return out


static func _add(out: Array[Dictionary], xform: Transform3D, mesh: Mesh, feet: float) -> void:
	var box := xform * mesh.get_aabb()
	if box.end.y > feet:
		out.append({"box": box, "xform": xform, "mesh": mesh})
