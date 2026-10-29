extends KitWalkProbe
## M3-ENV-1303, ADR 0200 / ADR 0193: ch05/ashcrown on env-art's Ashcrown kit in the kit's own frame
## (tools/act1/ch05_ashcrown_dressing.py). Its floors are the kit's (the forecourt, the tiers' ambulatories, the anvil
## hall), its steep flights (the causeway's, the flying stair, the vein stairs) are HeroStairs rows over blocking
## slabs, and the story walks: across the forecourt round the flying stair's foot into the hall to the court; along
## each trial tier from where the stair from above lands to its catch-rod; every spawn, mark and person on a floor; the
## chained stair heads blocked.

const ASHCROWN := "res://game/levels/ch05/ashcrown/ashcrown.tscn"
const COURT_Y := -4.0
const FLOOR_TOL := 0.35
## Marks in the air or in the loggia's view by design: the sea beyond the door, Kahre's light.
const OFF_FLOOR: Array[StringName] = [&"sea", &"kahre_heart", &"matron_heart"]


func before_each() -> void:
	open(ASHCROWN)


func _trigger(id: String) -> Vector3:
	return (zone.get_node(NodePath("Triggers/%s" % id)) as Node3D).position


func _flat(route: String, pts: Array[Vector3]) -> void:
	var end := walk(route, pts, pts[0].y)
	assert_true(absf(end - pts[-1].y) < 0.05, "%s ends at y %.2f (floor %.2f)" % [route, pts[-1].y, end])


func test_the_forecourt_leads_round_the_stair_foot_into_the_court() -> void:
	var pts: Array[Vector3] = [
		Vector3(0, COURT_Y, 45.0),
		Vector3(7.0, COURT_Y, 41.0),
		Vector3(5.0, COURT_Y, 24.0),
		Vector3(0, COURT_Y, 20.5),
		Vector3(0, COURT_Y, 14.0),
		Vector3(0, COURT_Y, 1.6)
	]
	_flat("forecourt to the court", pts)
	close()


func test_each_trial_tier_walks_from_its_landing_to_its_rod() -> void:
	for t: String in ["t1", "t2", "t3", "t4"]:
		var release := _trigger("release_%s" % t)
		var rod := _trigger("rod_%s" % t)
		# the clear side of the band: the standing pieces keep to its inner side
		var lane := Vector3(1.75, 0, 0)
		_flat("tier %s" % t, [release + lane + Vector3(0, 0, 1.0), rod + lane] as Array[Vector3])
	close()


func test_the_flights_are_walked_on_their_profiles() -> void:
	var rows: Array = zone.layout.get("stairs", [])
	assert_true(rows.size() >= 20, "the causeway's flights, the flying stair and the vein stairs (%d)" % rows.size())
	var ids: Array[String] = []
	for r: Dictionary in rows:
		ids.append(str(r["id"]))
	for id: String in ["flying_stair", "vein_stair_t6_e", "vein_stair_t5_e", "vein_stair_t4_e"]:
		assert_true(id in ids, "%s is a HeroStairs row" % id)
	close()


func test_the_chains_close_the_way_down() -> void:
	for id: String in ["Stair_t2", "Stair_t3", "Stair_t4", "StairDownChained"]:
		var b := zone.get_node(NodePath("Greybox/%s" % id)) as Node3D
		assert_ne(blocked_by(Vector3(b.position.x, b.position.y - 0.9, b.position.z)), "", "%s blocks its stair" % id)
	close()


func test_people_and_marks_stand_on_floors() -> void:
	var pts: Dictionary = {}
	for key: String in (zone.layout.get("spawns", {}) as Dictionary).keys():
		pts["spawn " + key] = zone.spawn_marker(StringName(key)).position
	for key: String in (zone.layout.get("marks", {}) as Dictionary).keys():
		if StringName(key) not in OFF_FLOOR:
			pts["mark " + key] = zone.stage.mark(StringName(key)).position
	for key: String in (zone.layout.get("actors", {}) as Dictionary).keys():
		pts["actor " + key] = zone.stage.actor(StringName(key)).position
	for what: String in pts.keys():
		var p: Vector3 = pts[what]
		var f := floor_y(p.x, p.z, p.y + 0.3)
		assert_true(absf(f - p.y) < FLOOR_TOL, "%s stands on a floor (y %.2f, floor %.2f)" % [what, p.y, f])
	close()
