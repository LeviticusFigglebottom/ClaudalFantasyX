extends TestCase
## M2-UI-16: the objective tracker over game/data/flow/objectives.json and the zone maps. The
## slice is walked flag by flag (a scratch flag set; Game is never touched) and each step must
## name the objective the beat sheet expects, with a target the map knows.

const HALUNA := &"ch02/haluna"
const SHRINE := &"ch03/shell_shrine"

var flags: Dictionary = {}
var t: ObjectiveTracker


func before_each() -> void:
	flags = {}
	t = ObjectiveTracker.new(func(f: StringName) -> bool: return bool(flags.get(f, false)))


func test_the_slice_steps_name_their_objectives() -> void:
	assert_eq(t.current(HALUNA), {}, "before the beach cutscene nothing calls")
	assert_eq(t.line(HALUNA), tr("OBJ_NONE"))
	var steps := [
		[&"ch02_met_asha", HALUNA, &"up_the_beach"],
		[&"ch02_tideline_won", HALUNA, &"to_nemes"],
		[&"ch02_ate_at_nemes", HALUNA, &"save_at_shrine"],
		[&"ch02_saved_once", HALUNA, &"to_causeway_head"],
	]
	for s: Array in steps:
		flags[s[0]] = true
		assert_eq(StringName(str(t.current(s[1]).get("id", ""))), s[2], "after %s" % s[0])
	assert_eq(StringName(str(t.current(SHRINE).get("id", ""))), &"shrine_trial", "in the shrine: the trial")
	flags[&"ch03_shrine_door_open"] = true
	assert_eq(StringName(str(t.current(SHRINE).get("id", ""))), &"shrine_door")
	assert_eq(t.current(HALUNA), {}, "the causeway head is done once the trial opened the door")
	flags[&"ch03_first_verse_sung"] = true
	flags[&"ch03_drownbell_defeated"] = true
	assert_eq(StringName(str(t.current(HALUNA).get("id", ""))), &"find_asha_on_dock")
	flags[&"ch03_rhen_sworn_guardian"] = true
	assert_eq(t.current(HALUNA), {}, "the slice ends with nothing left to do")


func test_zone_rows_stay_in_their_zone_and_side_rows_list_apart() -> void:
	flags[&"ch02_ate_at_nemes"] = true
	assert_eq(StringName(str(t.current(SHRINE).get("id", ""))), &"shrine_trial", "Haluna's row is not the shrine's")
	var side := t.side(HALUNA)
	assert_eq(side.size(), 1)
	assert_eq(StringName(str(side[0]["id"])), &"side_market_fragments")
	assert_eq(t.current(&"").get("id"), "save_at_shrine", "no zone asked: the first row that applies anywhere")


func test_every_target_resolves_to_a_map_point_in_bounds() -> void:
	var maps := ZoneMaps.new()
	for row: Dictionary in t.rows:
		assert_ne(tr(str(row["line_key"])), str(row["line_key"]), "%s has its line" % row["id"])
		var target: Dictionary = row.get("target", {})
		if target.is_empty():
			continue
		var at := maps.poi_position(StringName(str(target["zone"])), StringName(str(target["poi"])))
		assert_ne(at, Vector3.INF, "%s points at a known POI" % row["id"])


func test_zone_maps_find_zones_by_scene() -> void:
	var maps := ZoneMaps.new()
	assert_eq(maps.zone_for_scene("res://game/levels/ch02/haluna/haluna.tscn"), HALUNA)
	assert_eq(maps.zone_for_scene("res://nowhere.tscn"), &"")
	assert_eq(maps.route().size(), 3, "Haluna, the causeway, the Shell Shrine")
	assert_eq(maps.poi_position(HALUNA, &"shrine"), Vector3(-67.0, 0.0, 44.3))
