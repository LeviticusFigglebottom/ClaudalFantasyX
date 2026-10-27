class_name KitWalkProbe
extends TestCase
## A walkability probe for zones on a kit's heights (ADR 0200): it reads a zone's built collision (the Greybox
## blocks and ramps, oriented boxes) analytically, so it needs no physics frame. The field controller has no
## step-up, so a route is walkable when its floor never rises more than a slope's worth between two samples and a
## body fits above it. Subclasses open their zone with `open(scene)` and walk their story's routes.

## The Corrow kit's frame (tools/act1/corrow_frame.py, cw_common.py): the walk's arc and heights.
const ARC_R := 300.0
const WALK_Y := 12.0
const TOWN_Y := 1.0
const STEP_M := 0.25
## The steepest rise between two samples STEP_M apart: tan(40 deg) * STEP_M, under the controller's 45 deg floor.
const MAX_RISE := 0.21
const BODY_R := 0.3
const BODY_H := 1.6

var zone: GreyboxZone
var boxes: Array[Array] = []  # [Transform3D global, Vector3 half size, String id]


## Instances `scene` with its story held, and reads its collision boxes.
func open(scene: String) -> void:
	close()
	Game.new_game()
	zone = (load(scene) as PackedScene).instantiate() as GreyboxZone
	zone.story.autostart = false
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(zone)
	read_boxes()


## Re-reads the zone's enabled box shapes (after hiding or showing blocks).
func read_boxes() -> void:
	boxes.clear()
	for b: Node in zone.get_node(^"Greybox").get_children():
		var cs := b.get_node_or_null(^"Shape") as CollisionShape3D
		if cs == null or cs.disabled or not (cs.shape is BoxShape3D):
			continue
		boxes.append([(b as Node3D).transform * cs.transform, (cs.shape as BoxShape3D).size * 0.5, String(b.name)])


func close() -> void:
	if zone != null and is_instance_valid(zone):
		zone.get_parent().remove_child(zone)
		zone.free()
	zone = null


static func arc(s: float, y: float, zl: float) -> Vector3:
	return Vector3((ARC_R - zl) * sin(s / ARC_R), y, ARC_R - (ARC_R - zl) * cos(s / ARC_R))


## The highest box top under (x, z) at or below `below`, or -INF.
func floor_y(x: float, z: float, below: float) -> float:
	var best := -INF
	for b: Array in boxes:
		var t: Transform3D = b[0]
		var h: Vector3 = b[1]
		var inv := t.affine_inverse()
		var p0 := inv * Vector3(x, 0.0, z)
		var dy := inv.basis * Vector3.UP  # local change per world metre up
		if absf(dy.y) < 1e-4:
			continue
		var ty := (h.y - p0.y) / dy.y  # the world height where the line meets the top face
		var lp := p0 + dy * ty
		if absf(lp.x) <= h.x + 1e-3 and absf(lp.z) <= h.z + 1e-3 and ty <= below + 1e-3:
			best = maxf(best, ty)
	return best


## The id of a box a standing body at `feet` would be inside, or "".
func blocked_by(feet: Vector3) -> String:
	for b: Array in boxes:
		var inv := (b[0] as Transform3D).affine_inverse()
		var h: Vector3 = b[1]
		for k in 4:
			var lp := inv * (feet + Vector3.UP * (0.25 + (BODY_H - 0.3) * k / 3.0))
			if absf(lp.x) < h.x + BODY_R * 0.5 and absf(lp.y) < h.y and absf(lp.z) < h.z + BODY_R * 0.5:
				return String(b[2])
	return ""


## Walks the polyline of world (x, z) points from `start_y`, sampling every STEP_M; fails at the first sample with
## no floor, a rise too steep, or a body that doesn't fit. Returns the floor height at the end.
func walk(route: String, pts: Array[Vector3], start_y: float) -> float:
	var y := start_y
	for i in range(1, pts.size()):
		var a := pts[i - 1]
		var b := pts[i]
		var n := maxi(1, ceili(Vector2(b.x - a.x, b.z - a.z).length() / STEP_M))
		for k in range(1, n + 1):
			var p := a.lerp(b, float(k) / n)
			var f := floor_y(p.x, p.z, y + MAX_RISE)
			if f == -INF:
				fail("%s: no floor at (%.1f, %.1f) from y %.2f" % [route, p.x, p.z, y])
				return y
			if y - f > 1.0:
				fail("%s: a drop of %.2f m at (%.1f, %.1f)" % [route, y - f, p.x, p.z])
				return f
			var hit := blocked_by(Vector3(p.x, f, p.z))
			if hit != "":
				fail("%s: %s blocks a body at (%.1f, %.2f, %.1f)" % [route, hit, p.x, f, p.z])
				return f
			y = f
	return y
