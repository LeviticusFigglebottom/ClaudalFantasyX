extends TestCase
## M3-C08-1202, ADR 0200: ch08/corrow on the kit's heights is walkable end to end. The field controller has no
## step-up, so every route the story sends Rhen along must be a floor that never rises more than a slope's worth
## between two samples, with a body's clearance above it: the mole's pier and ramp over the parapet onto the walk,
## the walk from the mole past the stair head to the Bastion, the stair's head landing and both flights down to the
## low town, and the town lane. The probe reads the zone's built collision (Greybox blocks and ramps, oriented
## boxes) analytically, so it needs no physics frame.

const CORROW := "res://game/levels/ch08/corrow/corrow.tscn"
## The kit's frame (tools/act1/corrow_frame.py, cw_common.py): the walk's arc and heights.
const ARC_R := 300.0
const WALK_Y := 12.0
const TOWN_Y := 1.0
const STEP_M := 0.25
## The steepest rise between two samples STEP_M apart: tan(40 deg) * STEP_M, under the controller's 45 deg floor.
const MAX_RISE := 0.21
const BODY_R := 0.3
const BODY_H := 1.6

var zone: Ch08Zone
var boxes: Array[Array] = []  # [Transform3D global, Vector3 half size, String id]


func before_each() -> void:
	_close()
	Game.new_game()
	zone = (load(CORROW) as PackedScene).instantiate() as Ch08Zone
	zone.story.autostart = false
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(zone)
	boxes.clear()
	for b: Node in zone.get_node(^"Greybox").get_children():
		var cs := b.get_node_or_null(^"Shape") as CollisionShape3D
		if cs == null or cs.disabled or not (cs.shape is BoxShape3D):
			continue
		boxes.append([(b as Node3D).transform * cs.transform, (cs.shape as BoxShape3D).size * 0.5, String(b.name)])


func _close() -> void:
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


func test_the_mole_climbs_over_the_parapet_onto_the_walk() -> void:
	var mole := zone.spawn_marker(&"Mole").position
	var pts: Array[Vector3] = [
		mole, arc(15.0, 0.0, 26.0), arc(15.0, 0.0, 4.2), arc(15.0, 0.0, 3.0), arc(15.0, 0.0, 0.5)
	]
	var end := walk("mole", pts, mole.y)
	assert_true(absf(end - WALK_Y) < 0.05, "on the walk at the top (y %.2f)" % end)
	_close()


func test_the_walk_runs_from_the_gate_to_the_bastion() -> void:
	var pts: Array[Vector3] = []
	var s := 32.0
	while s > -95.0:
		pts.append(arc(s, 0.0, 0.3))
		s -= 4.0
	var end := walk("walk", pts, WALK_Y)
	assert_true(absf(end - WALK_Y) < 0.05, "still on the walk at the Bastion's end")
	var bastion := zone.spawn_marker(&"Bastion").position
	walk("bastion", [arc(-70.0, 0.0, 0.3), Vector3(bastion.x, 0.0, bastion.z)] as Array[Vector3], WALK_Y)
	_close()


func test_the_fisher_stair_goes_down_to_the_low_town_and_back() -> void:
	var ramps: Dictionary = {}
	for r: Variant in GreyboxZone.read_json(zone.layout["collision_path"]).get("ramps", []):
		ramps[(r as Dictionary)["id"]] = r
	var down: Array[Vector3] = [arc(-16.3, 0.0, 1.0)]
	for id: String in [
		"StairApproach", "StairHeadLanding", "StairFlight2", "StairLanding", "StairFlight1Upper", "StairFoot"
	]:
		var r: Dictionary = ramps[id]
		var a := GreyboxZone._vec3(r["from"])
		var b := GreyboxZone._vec3(r["to"])
		if id == "StairApproach":
			down.append(b)
		elif id == "StairHeadLanding":
			down.append_array([b.lerp(a, 0.2), a.lerp(b, 0.05)])
		else:
			down.append_array([b, a])
	var foot := down.back() as Vector3
	down.append(foot + Vector3(-2.0, 0.0, -4.0))
	var end := walk("stair down", down, WALK_Y)
	assert_true(absf(end - TOWN_Y) < 0.1, "in the low town at the foot (y %.2f)" % end)
	var up := down.duplicate()
	up.reverse()
	end = walk("stair up", up, TOWN_Y)
	assert_true(absf(end - WALK_Y) < 0.05, "back on the walk (y %.2f)" % end)
	_close()


func test_the_town_lane_is_clear_from_the_stair_foot_north() -> void:
	var foot := zone.stage.mark(&"foot_kerrid").position
	var pts: Array[Vector3] = [foot]
	for m: StringName in [&"kerrid_gone"]:
		pts.append(zone.stage.mark(m).position)
	pts.append(zone.stage.actor(&"netmender").position + Vector3(1.0, 0.0, 1.0))
	pts.append(zone.stage.actor(&"marra").position + Vector3(1.0, 0.0, 0.0))
	walk("town", pts, TOWN_Y)
	_close()


func test_story_marks_stand_on_a_floor() -> void:
	for m: Node in zone.stage.get_node(^"Marks").get_children():
		var p := (m as Node3D).position
		if p.y > WALK_Y + 0.6 or p.z > 12.0:  # the parapet: the Watchers' mouths, Pell's perch; the sea
			continue
		var f := floor_y(p.x, p.z, p.y + 0.3)
		assert_true(absf(f - p.y) < 0.35, "%s stands on a floor (mark y %.2f, floor %.2f)" % [m.name, p.y, f])
	_close()
