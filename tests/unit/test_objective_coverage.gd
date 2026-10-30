extends TestCase
## The Lead's objective check (2026-10-30, M4-A2P-1708): cloud-qa found Ch6's objective line reading "No errand calls
## just now" with no marker, because Brine Shoals had no objective rows. Every Act I and Act II location with a zone
## map has at least one main objective row, so the line and the Where-to-next card always have something to say on
## the main path. The empty line (OBJ_NONE, or a zone's idle_keys line) is then only for when nothing calls, and the
## line never slides in by itself to say so (ObjectiveHud: "nothing to do" waits for the button).
## A zone still waiting for its rows is listed in KNOWN_EMPTY (reported, not failed); once its rows land the run says
## the entry is stale (not a failure, so another track's fix never turns this red).

const CHAPTERS: Array[String] = [
	"prologue", "ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "ch08", "ch09", "ch10", "ch11", "ch12", "ch13"
]
## Zones whose rows are on their way: zone id -> the task.
const KNOWN_EMPTY := {
	"ch06/brine_shoals": "act1-chapters, adding Ch6's rows (the Lead 10-30 21:46)",
	"ch08/corrow": "act1-chapters, adding Ch8's rows (the Lead 10-30 21:46)",
	"ch08/coilspire": "act1-chapters, adding Ch8's rows (the Lead 10-30 21:46)",
}


func test_every_mapped_zone_has_a_main_objective() -> void:
	var maps := ZoneMaps.new()
	var rows: Array = (_json(ObjectiveTracker.DATA_PATH).get("objectives", {}) as Dictionary).get("rows", [])
	var main := {}
	for r: Variant in rows:
		var row := r as Dictionary
		if not bool(row.get("side", false)):
			main[str(row.get("zone", ""))] = int(main.get(str(row.get("zone", "")), 0)) + 1
	var checked := 0
	for loc: Variant in (_json("res://game/data/world/locations.json")).get("locations", []):
		var id := str((loc as Dictionary).get("id", ""))
		if not CHAPTERS.has(id.get_slice("/", 0)) or maps.zone(StringName(id)).is_empty():
			continue
		checked += 1
		var has_rows := int(main.get(id, 0)) > 0
		if KNOWN_EMPTY.has(id):
			if has_rows:
				print("  KNOWN_EMPTY is stale: %s has its objective rows now; drop it from the list" % id)
			else:
				print("  KNOWN empty objectives: %s (%s)" % [id, KNOWN_EMPTY[id]])
			continue
		assert_true(has_rows, "%s has a map but no main objective row: its line would only ever say OBJ_NONE" % id)
	assert_true(checked >= 20, "the mapped locations were found (%d)" % checked)


## A zone where nothing calls: the line holds the zone's idle words, and it does not slide in by itself on arrival.
func test_the_empty_line_waits_for_the_button() -> void:
	UiSettings.set_shared(UiSettings.new())
	var hud := ObjectiveHud.new()
	hud.tracker = ObjectiveTracker.new(func(_f: StringName) -> bool: return false)
	hud.zone = &"ch02/haluna"
	ParityHost.scene_root().add_child(hud)
	hud.advance(0.0)
	assert_false(hud.is_showing(), "nothing calls: no line on arrival")
	assert_eq(hud.tracker.line(&"ch02/haluna"), tr("OBJ_NONE_HALUNA"), "the zone's own idle words")
	hud.get_parent().remove_child(hud)
	hud.free()
	UiSettings.set_shared(null)


static func _json(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed if parsed is Dictionary else {}
