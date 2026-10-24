class_name CharacterNames
extends RefCounted
## The one resolver for the name a character is shown by (M3-C09-05; act1_ch09.md §9 UI 3). A
## character whose name the party doesn't know yet goes by another (Pell is "The Kirru" until
## ch09_pell_named). The dialogue box, the field menu, the party pages and the battle HUD all ask
## here, so a name changes everywhere at once. Data: game/data/ui/character_names.json. Flags are
## read through Game.get_flag unless a reader is passed (tests, captures and replays).

const DATA_PATH := "res://game/data/ui/character_names.json"

static var _rows: Dictionary = {}
static var _loaded := false


## The until_named rows: {id: {name_key, until_flag}}.
static func rows() -> Dictionary:
	if not _loaded:
		_loaded = true
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		var sec: Variant = (parsed as Dictionary).get("character_names") if parsed is Dictionary else null
		if not sec is Dictionary:
			push_error("CharacterNames: could not read 'character_names' from %s" % DATA_PATH)
		else:
			_rows = (sec as Dictionary).get("until_named", {}) as Dictionary
	return _rows


## The loc key to show for character `id`, whose own name key is `own_key`: the until_named key
## while its flag is unset, else `own_key`. `flags` (Callable(StringName) -> Variant) reads a flag;
## empty means Game.get_flag.
static func key_for(id: StringName, own_key: String, flags: Callable = Callable()) -> String:
	var row: Variant = rows().get(String(id))
	if not row is Dictionary:
		return own_key
	var flag := StringName(str((row as Dictionary).get("until_flag", "")))
	if flag == &"" or _flag(flag, flags):
		return own_key
	return str((row as Dictionary).get("name_key", own_key))


## The translated name for `id` (key_for), or the id itself when there is no key.
static func display(id: StringName, own_key: String, flags: Callable = Callable()) -> String:
	var key := key_for(id, own_key, flags)
	return TranslationServer.translate(key) if key != "" else String(id)


static func _flag(flag: StringName, flags: Callable) -> bool:
	if flags.is_valid():
		return bool(flags.call(flag))
	return bool(Game.get_flag(flag))
