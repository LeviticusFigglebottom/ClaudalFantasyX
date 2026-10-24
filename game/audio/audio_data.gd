class_name AudioData
extends RefCounted
## The audio tables under game/data/audio/ (M2-AUD-02; docs/kb/tech/audio_runtime.md): mix.json (buses, ducks,
## music timing), music.json (cues, zones, battle music) and sfx.json (sound rows). Read once and cached; tests
## pass their own dictionaries to the pure lookups below instead.

const DIR := "res://game/data/audio/"
const MIX := "mix"
const MUSIC := "music"
const SFX := "sfx"
## The reserved music id meaning "fade the bed out" (the .dlg format's `@music silence`).
const SILENCE := &"silence"

static var _cache: Dictionary = {}


## The parsed table `name` (mix, music, sfx, battle_sfx, ...): {} when it is missing or not an object.
static func table(name: String) -> Dictionary:
	if _cache.has(name):
		return _cache[name]
	var out: Dictionary = {}
	var path := "%s%s.json" % [DIR, name]
	if FileAccess.file_exists(path):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		if parsed is Dictionary:
			out = parsed
	_cache[name] = out
	return out


## Drops the cache (tests that swap a table).
static func reload() -> void:
	_cache.clear()


## The zone row for `scene_path` with its first matching variant applied, or {} when no row names the scene.
## `flag_set` is (flag: StringName) -> bool.
static func zone_for(music: Dictionary, scene_path: String, flag_set: Callable) -> Dictionary:
	for row: Variant in music.get("zones", []):
		if not row is Dictionary or str((row as Dictionary).get("scene", "")) != scene_path:
			continue
		var out := (row as Dictionary).duplicate(true)
		out.erase("variants")
		for v: Variant in (row as Dictionary).get("variants", []):
			if v is Dictionary and bool(flag_set.call(StringName(str((v as Dictionary).get("flag", ""))))):
				out.merge(v as Dictionary, true)
				out.erase("flag")
				break
		return out
	return {}


## The cue a battle against `encounter` plays: battle.encounters[encounter], else battle.default.
static func battle_cue(music: Dictionary, encounter: StringName) -> StringName:
	var battle := music.get("battle", {}) as Dictionary
	var by_enc := battle.get("encounters", {}) as Dictionary
	return StringName(str(by_enc.get(String(encounter), battle.get("default", ""))))


## The cue row `cue` ({} when the table has none).
static func cue(music: Dictionary, cue_id: StringName) -> Dictionary:
	return (music.get("cues", {}) as Dictionary).get(String(cue_id), {}) as Dictionary


## The streams a cue row names: one file, or its stems in order.
static func cue_files(row: Dictionary) -> Array[String]:
	var out: Array[String] = []
	if row.has("stems"):
		for f: Variant in row.get("stems", []):
			out.append(str(f))
	elif row.has("file"):
		out.append(str(row["file"]))
	return out
