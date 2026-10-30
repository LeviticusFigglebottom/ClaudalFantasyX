extends TestCase
## M4-A2P-045 (env-art-b): the Ebbing's rig reads a zone's own data (EbbingMotes.data_path; ZoneKitDressing's
## `"ebbing": {"data": ...}`). Ch15's held dead: one HELD field under the barge, its attractor following Kerrid, and
## Ch9's data unchanged beside it.

const CH15 := "res://game/data/vfx/ebbing_ch15_open_sea.json"
const OPEN_SEA_DRESSING := "res://game/levels/ch15/open_sea/open_sea_dressing.json"


func test_ch15_reads_its_own_data_and_ch9_keeps_its_own() -> void:
	var ch15 := EbbingMotes.load_data(CH15)
	var ch9 := EbbingMotes.load_data()
	assert_true((ch15["fields"] as Dictionary).has("shoal"), "the shoal's field")
	assert_eq(str((ch15["staff"] as Dictionary)["actor"]), "kerrid", "the dead drift toward Kerrid")
	assert_true((ch9["fields"] as Dictionary).has("strand_motes"), "Ch9's fields stay its own")
	assert_eq(str((ch9["staff"] as Dictionary)["actor"]), "asha")


func test_the_rig_builds_held_fields_from_the_zone_data() -> void:
	var ebb := EbbingMotes.new()
	ebb.data_path = CH15
	ebb.data = EbbingMotes.load_data(CH15)
	var field := ebb.build_field((ebb.data["fields"] as Dictionary)["shoal"] as Dictionary)
	assert_eq(field.mode, GlimmerState.Mode.HELD, "held: nothing rises")
	assert_eq(field.water_height_m, float(ebb.data["water_height_m"]))
	field.free()
	ebb.free()
	var dressing := JSON.parse_string(FileAccess.get_file_as_string(OPEN_SEA_DRESSING)) as Dictionary
	assert_eq(str((dressing["ebbing"] as Dictionary)["data"]), CH15, "the open sea's dressing names its data")
