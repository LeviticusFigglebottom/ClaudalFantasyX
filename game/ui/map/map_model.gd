class_name MapModel
extends RefCounted
## The zone map's words and places (M2-UI-18), node-free: one zone of game/data/ui/zone_maps.json
## (ZoneMaps) read against story flags (ObjectiveTracker), plus where the player stands and faces.
## The view is ZoneMapView inside ZoneMapMenu; the field menu's Map row opens it. Tests build it
## with their own zone, position, yaw and flag check; ZoneMapMenu.live_model reads the live field.
##
## World coordinates: x east, z south (north is -z, the top of the map). A yaw is the field's
## (FieldMotor): forward is -Z turned by the yaw, so yaw 0 faces north and PI/2 faces west.

const DATA_PATH := "res://game/data/ui/zone_map_menu.json"
## Compass words, clockwise from north, one per 45 degrees.
const DIRECTION_KEYS: Array[String] = [
	"MAP_DIR_N", "MAP_DIR_NE", "MAP_DIR_E", "MAP_DIR_SE", "MAP_DIR_S", "MAP_DIR_SW", "MAP_DIR_W", "MAP_DIR_NW"
]
const POI_LINE_KEY := "MAP_POI_LINE_FMT"
const POI_HERE_KEY := "MAP_POI_HERE_FMT"
const POI_GOAL_KEY := "MAP_POI_GOAL"
const NO_ERRANDS_KEY := "MAP_ERRANDS_NONE"
## An Order shrine's POI ("order": true in zone_maps.json) once the party are heretics: the hollow glyph, and its
## name in this format in the legend and the line under the map (heresy.md section 1).
const DARK_FMT_KEY := "MAP_POI_SHRINE_DARK_FMT"

var zone_id: StringName = &""
var maps: ZoneMaps
var tracker: ObjectiveTracker
## The player's world position (x, z); Vector2.INF when unknown (no player in the scene).
var player_at := Vector2.INF
var player_yaw := 0.0
## Closer than this (metres), a place reads "you are here".
var near_m := 0.0

var _shapes_source: Dictionary = {}
var _pois: Array[Dictionary] = []


## `zone`: a zone_maps.json id. `at`: the player's world position (Vector3.INF = unknown).
## `flag_check`: Callable(flag: StringName) -> bool (default: Game.get_flag).
func _init(
	zone: StringName,
	at: Vector3 = Vector3.INF,
	yaw: float = 0.0,
	flag_check: Callable = Callable(),
	with_maps: ZoneMaps = null
) -> void:
	zone_id = zone
	maps = with_maps if with_maps != null else ZoneMaps.new()
	tracker = ObjectiveTracker.new(flag_check)
	if at.is_finite():
		player_at = Vector2(at.x, at.z)
	player_yaw = yaw
	near_m = float((load_data().get("map", {}) as Dictionary).get("near_m", 0.0))
	for p: Variant in zone().get("pois", []):
		var row := p as Dictionary
		var w: Array = row.get("at", [0.0, 0.0])
		var kind := StringName(str(row.get("kind", "")))
		var dark := kind == MapGlyphs.KIND_SHRINE and bool(row.get("order", false))
		dark = dark and bool(tracker.is_set.call(SaveShrine.HERETIC_FLAG))
		(
			_pois
			. append(
				{
					"id": StringName(str(row.get("id", ""))),
					"name":
					_dark_name(_tr(str(row.get("name_key", "")))) if dark else _tr(str(row.get("name_key", ""))),
					"kind": MapGlyphs.KIND_SHRINE_DARK if dark else kind,
					"at": Vector2(float(w[0]), float(w[1])),
				}
			)
		)


func _dark_name(place: String) -> String:
	return _tr(DARK_FMT_KEY).format({"place": place})


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("zone_map_menu")) != TYPE_DICTIONARY:
		push_error("MapModel: could not read 'zone_map_menu' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["zone_map_menu"] as Dictionary


## The transform that fits world rectangle `bounds` (x, z) into `view` (px): one scale for both
## axes (the smaller fit), centred, so the zone is letterboxed and never stretched.
static func fit(bounds: Rect2, view: Rect2) -> Transform2D:
	if bounds.size.x <= 0.0 or bounds.size.y <= 0.0:
		return Transform2D.IDENTITY
	var s := minf(view.size.x / bounds.size.x, view.size.y / bounds.size.y)
	var origin := view.get_center() - bounds.get_center() * s
	return Transform2D(Vector2(s, 0.0), Vector2(0.0, s), origin)


## The compass word key for the way from `from` to `to` (world x, z; north is -z).
static func direction_key(from: Vector2, to: Vector2) -> String:
	var d := to - from
	var bearing := fposmod(atan2(d.x, -d.y), TAU)
	return DIRECTION_KEYS[posmod(roundi(bearing / (TAU / DIRECTION_KEYS.size())), DIRECTION_KEYS.size())]


## The world (x, z) direction a field yaw faces (FieldMotor: forward is -Z turned by the yaw).
static func facing(yaw: float) -> Vector2:
	return Vector2(-sin(yaw), -cos(yaw))


func zone() -> Dictionary:
	return maps.zone(zone_id)


func has_map() -> bool:
	return not zone().is_empty()


func zone_name() -> String:
	return _tr(str(zone().get("name_key", "")))


## The world rectangle the map shows (x, z, width, depth).
func bounds() -> Rect2:
	var b: Array = zone().get("bounds", [0.0, 0.0, 0.0, 0.0])
	return Rect2(float(b[0]), float(b[1]), float(b[2]), float(b[3]))


## How the zone's shapes are read (zone_maps.json shape_kind): &"haluna_layout",
## &"shell_shrine_trial" or &"greybox_layout".
func shape_kind() -> StringName:
	return StringName(str(zone().get("shape_kind", "")))


## The zone's shape_hints (a greybox layout's blocks named by layer; ZoneMapShapes.greybox_layer).
func shape_hints() -> Dictionary:
	return zone().get("shape_hints", {}) as Dictionary


## The zone's shape source, parsed (a trial file's single top-level object is unwrapped).
func shape_source() -> Dictionary:
	if _shapes_source.is_empty() and has_map():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(str(zone().get("shapes", ""))))
		if typeof(parsed) == TYPE_DICTIONARY:
			var d := parsed as Dictionary
			_shapes_source = d[d.keys()[0]] as Dictionary if d.size() == 1 and d.values()[0] is Dictionary else d
	return _shapes_source


## The points of interest in zone_maps.json order: {id, name, kind, at: Vector2 (world x, z)}.
func pois() -> Array[Dictionary]:
	return _pois.duplicate()


func poi_index(poi_id: StringName) -> int:
	for i in _pois.size():
		if _pois[i]["id"] == poi_id:
			return i
	return -1


## MenuPage rows for the legend: one per POI, in order.
func poi_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for p in _pois:
		out.append({"id": p["id"], "label": p["name"], "enabled": true})
	return out


## The current objective's line (ObjectiveTracker.line: OBJ_NONE's words when nothing calls).
func objective_line() -> String:
	return tracker.line(zone_id)


## The POI the current objective points at in this zone (&"" when it has none here).
func objective_poi() -> StringName:
	var t := tracker.target(zone_id)
	if StringName(str(t.get("zone", ""))) != zone_id:
		return &""
	var pid := StringName(str(t.get("poi", "")))
	return pid if poi_index(pid) >= 0 else &""


## The objective's world position (x, z), or Vector2.INF when it has none in this zone.
func objective_at() -> Vector2:
	var i := poi_index(objective_poi())
	return _pois[i]["at"] if i >= 0 else Vector2.INF


## The side errands that apply here, as lines (none: one line saying so).
func errand_lines() -> Array[String]:
	var out: Array[String] = []
	for row in tracker.side(zone_id):
		out.append(_tr(str(row.get("line_key", ""))))
	return out


func errands_text() -> String:
	var lines := errand_lines()
	return "\n".join(lines) if not lines.is_empty() else _tr(NO_ERRANDS_KEY)


## The pilgrimage strip: {id, name, current} per stop, in route order. Only the stops near this
## one show (zone_map_menu.json route "before" and "after"), so the strip stays readable and the
## road far ahead stays unnamed; a zone not on the route shows the route's first stops.
func route_stops() -> Array[Dictionary]:
	var route := maps.route()
	var here := -1
	for i in route.size():
		if StringName(str((route[i] as Dictionary).get("id", ""))) == zone_id:
			here = i
	var r: Dictionary = load_data().get("route", {})
	var before := int(r.get("before", route.size()))
	var after := int(r.get("after", route.size()))
	var first := maxi(here - before, 0) if here >= 0 else 0
	var last := mini(here + after if here >= 0 else before + after, route.size() - 1)
	var out: Array[Dictionary] = []
	for i in range(first, last + 1):
		var row := route[i] as Dictionary
		var rid := StringName(str(row.get("id", "")))
		out.append({"id": rid, "name": _tr(str(row.get("name_key", ""))), "current": rid == zone_id})
	return out


func has_player() -> bool:
	return player_at.is_finite()


## The world (x, z) direction the player faces.
func player_facing() -> Vector2:
	return facing(player_yaw)


## The line under the map for POI `poi_id`: its name, and how far and which way it lies from the
## player ("you are here" when near), plus a note when the objective leads there.
func poi_line(poi_id: StringName) -> String:
	var i := poi_index(poi_id)
	if i < 0:
		return ""
	var p := _pois[i]
	var line := str(p["name"])
	if has_player():
		var d := (p["at"] as Vector2).distance_to(player_at)
		if d < near_m:
			line = _tr(POI_HERE_KEY).format({"name": p["name"]})
		else:
			var dir := _tr(direction_key(player_at, p["at"]))
			line = _tr(POI_LINE_KEY).format({"name": p["name"], "m": roundi(d), "dir": dir})
	if poi_id == objective_poi():
		line += " " + _tr(POI_GOAL_KEY)
	return line


## The legend row the cursor starts on: the objective's place, else the first.
func first_index() -> int:
	return maxi(poi_index(objective_poi()), 0)


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""
