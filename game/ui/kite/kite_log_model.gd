class_name KiteLogModel
extends RefCounted
## The Kite's log, Node-free (M5-A3P-1703; ADR 0207; act3_ch18 §4 and §5): what Act III offers, set down quietly. It
## holds the revisits (a place once the chart lists it; Seen once its side scene has played, with what changed there)
## and the heirloom errands (one per hero, for someone they lost; where it waits, then what is carried). No counts
## and no percentages: a town's grief is not a quest log (act3_ch18 rule 3). Data: game/data/world/kite_log.json.
## The view is KiteMapMenu's log page; `kite` is its chart, which says which places are listed and names them.

const DATA_PATH := "res://game/data/world/kite_log.json"
const KIND_PLACE := &"place"
const KIND_HEIRLOOM := &"heirloom"

var data: Dictionary = {}
var kite: KiteMapModel


func _init(table: Dictionary, chart: KiteMapModel) -> void:
	data = table
	kite = chart


static func load_data(path: String = DATA_PATH) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return (parsed as Dictionary).get("kite_log", {}) as Dictionary if parsed is Dictionary else {}


## The log's rows, places then heirlooms, each {id, kind, label, done, right, line, destination}. `destination` is
## the chart place the row points at (&"" when the chart doesn't list it yet).
func entries() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var listed := kite.ids()
	for r: Variant in data.get("places", []):
		var row := r as Dictionary
		var dest := StringName(str(row.get("destination", "")))
		if not listed.has(dest):
			continue
		var seen := _flag(StringName(str(row.get("seen_flag", ""))))
		var line_key := str(row.get("changed_key", "")) if seen else "KITE_LOG_NOT_YET"
		(
			out
			. append(
				{
					"id": dest,
					"kind": KIND_PLACE,
					"label": kite.place_name(dest),
					"done": seen,
					"right": _tr("KITE_LOG_SEEN") if seen else "",
					"line": _tr(line_key),
					"destination": dest,
				}
			)
		)
	for r: Variant in data.get("heirlooms", []):
		var row := r as Dictionary
		var needs := StringName(str(row.get("requires_flag", "")))
		if needs != &"" and not _flag(needs):
			continue
		var found := _flag(StringName(str(row.get("flag", ""))))
		var where := StringName(str(row.get("where", "")))
		(
			out
			. append(
				{
					"id": StringName("heirloom_" + str(row.get("id", ""))),
					"kind": KIND_HEIRLOOM,
					"label": _tr(str(row.get("label_key", ""))),
					"done": found,
					"right": _tr("KITE_LOG_CARRIED") if found else "",
					"line": _tr(str(row.get("found_key" if found else "where_key", ""))),
					"destination": where if listed.has(where) else &"",
				}
			)
		)
	return out


func entry(id: StringName) -> Dictionary:
	for e in entries():
		if e["id"] == id:
			return e
	return {}


func _flag(flag: StringName) -> bool:
	if flag == &"":
		return false
	var v: Variant = kite.get_flag.call(flag)
	return typeof(v) == TYPE_BOOL and bool(v)


static func _tr(key: String) -> String:
	return TranslationServer.translate(key)
