class_name KiteMapModel
extends RefCounted
## The Kite's world map, node-free (SPEC §6.6, Act III; act_outline.md Ch18; M3-UI-205). Data:
## game/data/world/kite.json. It lists the places the Kite can land (a destination shows once its
## requires_flag is set; a secret once its found_flag is), the region each lies in, and the chart cell
## under each; it searches a cell for a secret (finding one sets its found_flag, and it joins the
## destinations); and it flies through `travel` ((location_id, spawn) -> bool; the game's is the
## SceneRouter through the location registry). The Kite itself needs open_flag. The view is KiteMapMenu.

const DATA_PATH := "res://game/data/world/kite.json"
const UNKNOWN_KEY := "KITE_UNKNOWN_PLACE"

var data: Dictionary = {}
## (flag: StringName) -> Variant, and (flag: StringName, value: Variant) -> void.
var get_flag: Callable
var set_flag: Callable
## (location_id: StringName, spawn: StringName) -> bool.
var travel: Callable
## The location the party stands in (its destination is marked Here and can't be flown to).
var here: StringName = &""


func _init(table: Dictionary, read_flag: Callable, write_flag: Callable, fly: Callable = Callable()) -> void:
	data = table
	get_flag = read_flag
	set_flag = write_flag
	travel = fly


static func load_data(path: String = DATA_PATH) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return (parsed as Dictionary).get("kite", {}) as Dictionary if typeof(parsed) == TYPE_DICTIONARY else {}


static func from_game() -> KiteMapModel:
	var m := KiteMapModel.new(
		load_data(),
		func(f: StringName) -> Variant: return Game.get_flag(f, false),
		func(f: StringName, v: Variant) -> void: Game.set_flag(f, v),
		func(loc: StringName, spawn: StringName) -> bool: return ShrineNetwork.travel_to(loc, spawn)
	)
	m.here = Game.state.location_id
	return m


## True when the Kite can fly at all (open_flag).
func is_open() -> bool:
	return _flag(StringName(str(data.get("open_flag", ""))))


## The destination rows that can be flown to or stood at, in data order, then the found secrets.
func destinations() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for row: Variant in data.get("destinations", []):
		var d := row as Dictionary
		if _flag(StringName(str(d.get("requires_flag", "")))):
			out.append(d)
	for row: Variant in data.get("secrets", []):
		var s := row as Dictionary
		if _flag(StringName(str(s.get("found_flag", "")))):
			out.append(s)
	return out


func ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for d in destinations():
		out.append(StringName(str(d["id"])))
	return out


func row_of(id: StringName) -> Dictionary:
	for d in destinations():
		if StringName(str(d["id"])) == id:
			return d
	return {}


## A destination's name: its own name_key, else its location's (locations.json name_key).
func place_name(id: StringName) -> String:
	var row := row_of(id)
	var key := str(row.get("name_key", ""))
	if key == "":
		key = ShrineNetwork.registry_name_key(StringName(str(row.get("location_id", ""))))
	return TranslationServer.translate(key if key != "" else UNKNOWN_KEY)


func region_name(id: StringName) -> String:
	var region := str(row_of(id).get("region", ""))
	for r: Variant in data.get("regions", []):
		if str((r as Dictionary).get("id", "")) == region:
			return TranslationServer.translate(str((r as Dictionary).get("name_key", "")))
	return ""


func is_here(id: StringName) -> bool:
	return here != &"" and StringName(str(row_of(id).get("location_id", ""))) == here


## The chart cell under a destination ("C4"): its column letter and row number.
func cell_of(id: StringName) -> String:
	var at: Array = row_of(id).get("at", [0.0, 0.0])
	return cell_at(Vector2(float(at[0]), float(at[1])))


func cell_at(at: Vector2) -> String:
	var cols: Array = data.get("columns", [])
	var rows := int(data.get("rows", 1))
	var c := clampi(int(at.x * cols.size()), 0, maxi(cols.size() - 1, 0))
	var r := clampi(int(at.y * rows), 0, maxi(rows - 1, 0))
	return "%s%d" % [str(cols[c]) if not cols.is_empty() else "", r + 1]


func columns() -> Array:
	return data.get("columns", [])


func row_count() -> int:
	return int(data.get("rows", 1))


## Searches chart cell `cell` ("F2"). A secret there not yet found is found now (its found_flag set)
## and returned; a found one is returned again; nothing there returns {}.
func search(cell: String) -> Dictionary:
	for row: Variant in data.get("secrets", []):
		var s := row as Dictionary
		if str(s.get("cell", "")) == cell:
			var flag := StringName(str(s.get("found_flag", "")))
			if not _flag(flag):
				set_flag.call(flag, true)
			return s
	return {}


## Why the Kite can't land at `id` ("" when it can): a destination with `refused_flag` set says its `refused_key`
## (M5-A3P-1702, act3_ch18 §4: Ansedra is closed to heretics; the party see it from the air and fly on).
func refusal(id: StringName) -> String:
	var row := row_of(id)
	var flag := StringName(str(row.get("refused_flag", "")))
	if flag == &"" or not _flag(flag):
		return ""
	return TranslationServer.translate(str(row.get("refused_key", "")))


## Flies to `id`. False (nothing happens) when the Kite is grounded, the place is unknown or is here,
## or the trip is refused.
func fly(id: StringName) -> bool:
	var row := row_of(id)
	if not is_open() or row.is_empty() or is_here(id) or not travel.is_valid() or refusal(id) != "":
		return false
	return bool(travel.call(StringName(str(row["location_id"])), StringName(str(row.get("spawn", "")))))


func _flag(flag: StringName) -> bool:
	if flag == &"":
		return true
	var v: Variant = get_flag.call(flag)
	return typeof(v) == TYPE_BOOL and bool(v)
