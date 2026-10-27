extends KitWalkProbe
## M3-C09-1209, ADR 0200: ch09/corrow_night on the Corrow kit's fallen wall is walkable where the story walks
## (KitWalkProbe): the strand of the drowned from its spawn to the landing; the strand's east end over the bridge to
## the mole and up its ramp onto the walk, then west to Liss at her cut hoist; and at dawn, the coast road from the
## wall-gate to the milestone. Every mark the party stands on is on a floor.

const NIGHT := "res://game/levels/ch09/corrow_night/corrow_night.tscn"
const STRAND_Y := 0.6
const MOLE_S := 15.0
const BRIDGE_Z := 28.0


func before_each() -> void:
	open(NIGHT)


func _at(id: StringName) -> Vector3:
	var m := zone.stage.mark(id)
	return m.position if m != null else zone.stage.actor(id).position


func _trigger(id: String) -> Vector3:
	return (zone.get_node(NodePath("Triggers/%s" % id)) as Node3D).position


func test_the_strand_runs_from_the_spawn_to_the_landing() -> void:
	var start := zone.spawn_marker(&"Strand").position
	var end := walk("strand", [start, _trigger("hobb_overheard"), _trigger("landing")] as Array[Vector3], start.y)
	assert_true(absf(end - STRAND_Y) < 0.05, "on the strand at the landing (y %.2f)" % end)
	close()


func test_the_strand_reaches_liss_over_the_mole() -> void:
	var pts: Array[Vector3] = [
		_trigger("toma"),
		arc(-2.0, 0.0, BRIDGE_Z),
		arc(MOLE_S, 0.0, BRIDGE_Z),
		arc(MOLE_S, 0.0, 4.2),
		arc(MOLE_S, 0.0, 3.0),
		arc(MOLE_S, 0.0, 0.5),
		arc(0.0, 0.0, 0.3),
		arc(-14.0, 0.0, 0.3),
		_trigger("npc_liss")
	]
	var end := walk("to Liss", pts, STRAND_Y)
	assert_true(
		end > WALK_Y - 0.05 and end < WALK_Y + 0.6,
		"on the walk or the stair head's approach by the hoist (y %.2f)" % end
	)
	close()


func test_the_coast_road_runs_from_the_gate_to_the_milestone() -> void:
	var gate := zone.spawn_marker(&"RoadGate").position
	var end := walk("road", [gate, _trigger("milestone"), _at(&"line_1")] as Array[Vector3], gate.y)
	assert_true(absf(end - WALK_Y) < 0.05, "the road is the walk (y %.2f)" % end)
	close()


func test_the_party_marks_stand_on_a_floor() -> void:
	for m: Node in zone.stage.get_node(^"Marks").get_children():
		var p := (m as Node3D).position
		if p.x > 1000.0 or String(m.name).ends_with("_motes") or p.z > 40.0 or String(m.name).begins_with("sea_"):
			continue  # Iskarra's set; the motes' and the sea's points float
		var f := floor_y(p.x, p.z, p.y + 0.3)
		assert_true(absf(f - p.y) < 0.35, "%s stands on a floor (mark y %.2f, floor %.2f)" % [m.name, p.y, f])
	close()


func test_the_strand_and_the_vigil_are_kit_pieces() -> void:
	var counts: Dictionary = {}
	var squat: Node3D = null
	for n: Node in zone.get_node(^"Dressing").get_children():
		var kind := (n as Node3D).scene_file_path.get_file().get_basename() if n is Node3D else ""
		counts[kind] = int(counts.get(kind, 0)) + 1
		if kind == "iskarra_tower_broken":
			squat = n as Node3D
	assert_true(int(counts.get("shroud_a", 0)) + int(counts.get("shroud_b", 0)) > 20, "the drowned lie in their rows")
	assert_true(int(counts.get("strand_lamp", 0)) > 20, "a clay lamp under each vigil light")
	assert_true(counts.has("iskarra_plaza"), "the vigil stands in Iskarra's plaza")
	assert_true(squat != null, "Iskarra's broken tower")
	var s := squat.basis.get_scale()
	assert_true(absf(s.x - 0.8) < 0.01 and absf(s.y - 0.6) < 0.01, "scale_y: squat, not uniform (%s)" % s)
	close()
