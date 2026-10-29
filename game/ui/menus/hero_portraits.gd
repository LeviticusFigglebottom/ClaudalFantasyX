class_name HeroPortraits
extends RefCounted
## Hero portrait lookup for the menus (M2-MNU-301, ADR 0120). Node-free. The pictures are PNGs baked by
## tools/portraits/render.sh; game/data/ui/hero_portraits.json says where they are and which emotion
## each page shows. texture(hero, emotion) falls back to the neutral portrait, then to null: a caller
## then shows the hero's initial (HeroPortraitFrame does).

const DATA_PATH := "res://game/data/ui/hero_portraits.json"
const SECTION := "hero_portraits"

static var _cache: Dictionary = {}


static func data() -> Dictionary:
	if _cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if not parsed is Dictionary or not (parsed as Dictionary).get(SECTION) is Dictionary:
			push_error("HeroPortraits: could not read '%s' from %s" % [SECTION, DATA_PATH])
			return {}
		_cache = (parsed as Dictionary)[SECTION] as Dictionary
	return _cache


## The PNG path for `hero` in `emotion` (whether or not it exists).
static func path_for(hero: StringName, emotion: StringName) -> String:
	var d := data()
	var file := str(d.get("file_fmt", "")).format({"hero": hero, "emotion": emotion})
	return str(d.get("dir", "")).path_join(file)


static func fallback_emotion() -> StringName:
	return StringName(str(data().get("fallback_emotion", "")))


## True when `hero` has a portrait in exactly `emotion`.
static func has(hero: StringName, emotion: StringName) -> bool:
	return hero != &"" and emotion != &"" and ResourceLoader.exists(path_for(hero, emotion))


## `hero`'s portrait in `emotion`, else the fallback emotion's, else null.
static func texture(hero: StringName, emotion: StringName = &"") -> Texture2D:
	for e: StringName in [emotion, fallback_emotion()]:
		if has(hero, e):
			return load(path_for(hero, e)) as Texture2D
	return null


## The head crop of texture(hero, emotion) for small slots (face_region), or null.
static func face(hero: StringName, emotion: StringName = &"") -> Texture2D:
	var full := texture(hero, emotion)
	if full == null:
		return null
	var r: Array = (data().get("face_regions", {}) as Dictionary).get(String(hero), data().get("face_region", []))
	if r.size() != 4:
		return full
	var atlas := AtlasTexture.new()
	atlas.atlas = full
	atlas.region = Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3]))
	return atlas


## The emotion `page` shows (pages.<page>.emotion, or its .fallen, when it has one, for a fallen hero); the
## fallback emotion for a page the data does not name.
static func page_emotion(page: StringName, fallen: bool = false) -> StringName:
	var p: Dictionary = (data().get("pages", {}) as Dictionary).get(String(page), {})
	var e := str(p.get("emotion", ""))
	if fallen:
		e = str(p.get("fallen", e))
	return StringName(e) if e != "" else fallback_emotion()
