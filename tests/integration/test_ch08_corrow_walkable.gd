extends KitWalkProbe
## M3-C08-1202, ADR 0200: ch08/corrow on the kit's heights is walkable end to end: the mole's pier and ramp over
## the parapet onto the walk, the walk from the mole past the stair head to the Bastion, the stair's head landing
## and both flights down to the low town, and the town lane (KitWalkProbe).

const CORROW := "res://game/levels/ch08/corrow/corrow.tscn"


func before_each() -> void:
	open(CORROW)


func test_the_mole_climbs_over_the_parapet_onto_the_walk() -> void:
	var mole := zone.spawn_marker(&"Mole").position
	var pts: Array[Vector3] = [
		mole, arc(15.0, 0.0, 26.0), arc(15.0, 0.0, 4.2), arc(15.0, 0.0, 3.0), arc(15.0, 0.0, 0.5)
	]
	var end := walk("mole", pts, mole.y)
	assert_true(absf(end - WALK_Y) < 0.05, "on the walk at the top (y %.2f)" % end)
	close()


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
	close()


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
	close()


func test_the_town_lane_is_clear_from_the_stair_foot_north() -> void:
	var foot := zone.stage.mark(&"foot_kerrid").position
	var pts: Array[Vector3] = [foot]
	for m: StringName in [&"kerrid_gone"]:
		pts.append(zone.stage.mark(m).position)
	pts.append(zone.stage.actor(&"netmender").position + Vector3(1.0, 0.0, 1.0))
	pts.append(zone.stage.actor(&"marra").position + Vector3(1.0, 0.0, 0.0))
	walk("town", pts, TOWN_Y)
	close()


func test_story_marks_stand_on_a_floor() -> void:
	for m: Node in zone.stage.get_node(^"Marks").get_children():
		var p := (m as Node3D).position
		if p.y > WALK_Y + 0.6 or p.z > 12.0:  # the parapet: the Watchers' mouths, Pell's perch; the sea
			continue
		var f := floor_y(p.x, p.z, p.y + 0.3)
		assert_true(absf(f - p.y) < 0.35, "%s stands on a floor (mark y %.2f, floor %.2f)" % [m.name, p.y, f])
	close()
