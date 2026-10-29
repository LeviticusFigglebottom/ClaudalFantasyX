class_name CreaturePortraits
extends RefCounted
## Creature portrait lookup for the bestiary (M2-MNU-302, ADR 0120). Node-free. The pictures are PNGs baked
## by tools/portraits/render.sh, one per creatures.json row; an enemy finds its picture through its
## enemies.json `model` (CreatureModels) and that actor scene's creatures.json id, so two enemies sharing a
## model share a picture. game/data/ui/creature_portraits.json says where the PNGs are and how the frame
## looks. An enemy who is a person (data 'people': the Inquisitor) shows that character's menu portrait. An
## enemy without a model, or whose creature has no PNG, has none (null).

const DATA_PATH := "res://game/data/ui/creature_portraits.json"
const SECTION := "creature_portraits"

static var _cache: Dictionary = {}


static func data() -> Dictionary:
	if _cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if not parsed is Dictionary or not (parsed as Dictionary).get(SECTION) is Dictionary:
			push_error("CreaturePortraits: could not read '%s' from %s" % [SECTION, DATA_PATH])
			return {}
		_cache = (parsed as Dictionary)[SECTION] as Dictionary
	return _cache


## The PNG path for creatures.json row `creature` (whether or not it exists).
static func path_for(creature: StringName) -> String:
	var d := data()
	return str(d.get("dir", "")).path_join(str(d.get("file_fmt", "")).format({"creature": creature}))


## The creatures.json id of enemy `enemy_id`'s model (&"" when it has no model).
static func creature_for(enemy_id: StringName) -> StringName:
	var scene := str(CreatureModels.models().get(String(enemy_id), ""))
	return CreatureModels.creature_for_scene(scene) if scene != "" else &""


## True when enemy `enemy_id` has a baked portrait (its creature's, or the person's it is).
static func has(enemy_id: StringName) -> bool:
	if _person(enemy_id) != &"":
		return HeroPortraits.texture(_person(enemy_id)) != null
	var creature := creature_for(enemy_id)
	return creature != &"" and ResourceLoader.exists(path_for(creature))


## Enemy `enemy_id`'s portrait, or null.
static func texture(enemy_id: StringName) -> Texture2D:
	if _person(enemy_id) != &"":
		return HeroPortraits.texture(_person(enemy_id))
	return load(path_for(creature_for(enemy_id))) as Texture2D if has(enemy_id) else null


## The character whose portrait enemy `enemy_id` shows (data 'people'), or &"".
static func _person(enemy_id: StringName) -> StringName:
	return StringName(str((data().get("people", {}) as Dictionary).get(String(enemy_id), "")))


## Whether a foe logged but never Read shows as a silhouette.
static func silhouette_unread() -> bool:
	return bool(data().get("silhouette_unread", false))
