class_name ZoneMaps
extends RefCounted
## The zones the objectives and the map know (M2-UI-16/18; game/data/ui/zone_maps.json): each
## zone's scene, name, map bounds, shape source and points of interest, and the pilgrimage route.

const DATA_PATH := "res://game/data/ui/zone_maps.json"

var data: Dictionary = {}


func _init(path: String = DATA_PATH) -> void:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("zone_maps")) != TYPE_DICTIONARY:
		push_error("ZoneMaps: could not read 'zone_maps' from %s" % path)
		return
	data = (parsed as Dictionary)["zone_maps"] as Dictionary


## The zone row with id `zone_id`, or {}.
func zone(zone_id: StringName) -> Dictionary:
	for z: Variant in data.get("zones", []):
		if StringName(str((z as Dictionary).get("id", ""))) == zone_id:
			return z as Dictionary
	return {}


## The id of the zone whose scene is `scene_path` (&"" when the scene has no map).
func zone_for_scene(scene_path: String) -> StringName:
	for z: Variant in data.get("zones", []):
		if str((z as Dictionary).get("scene", "")) == scene_path:
			return StringName(str((z as Dictionary).get("id", "")))
	return &""


## POI `poi` of zone `zone_id`, or {}.
func poi(zone_id: StringName, poi_id: StringName) -> Dictionary:
	for p: Variant in zone(zone_id).get("pois", []):
		if StringName(str((p as Dictionary).get("id", ""))) == poi_id:
			return p as Dictionary
	return {}


## The world position (x, 0, z) of POI `poi_id` in `zone_id`; null-like Vector3.INF when unknown.
func poi_position(zone_id: StringName, poi_id: StringName) -> Vector3:
	var p := poi(zone_id, poi_id)
	if p.is_empty():
		return Vector3.INF
	var at: Array = p.get("at", [0, 0])
	return Vector3(float(at[0]), 0.0, float(at[1]))


func route() -> Array:
	return data.get("route", []) as Array
