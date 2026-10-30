class_name AudioData
extends RefCounted
## The audio tables under game/data/audio/ (M2-AUD-02; docs/kb/tech/audio_runtime.md): mix.json (buses, ducks,
## music timing), music.json (cues, zones, battle music) and sfx.json (sound rows). Read once and cached; tests
## pass their own dictionaries to the pure lookups below instead.

const DIR := "res://game/data/audio/"
const MIX := "mix"
const MUSIC := "music"
const SFX := "sfx"
const AMBIENCE := "ambience"
const UI_SFX := "ui_sfx"
const FOOTSTEPS := "footsteps"
const VOICES := "voices"
const REEFBALL_HOOKS := "reefball_hooks"
const BATTLE_STINGS := "battle_stings"
const LIFE := "life"
const IMPACT := "impact_audio"
const CUTSCENE_FOLEY := "cutscene_foley"
const ASHCROWN_SFX := "ashcrown_sfx"
const COILSPIRE_SFX := "coilspire_sfx"
const INTERACT_SFX := "interact_sfx"
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


## Every sfx row: sfx.json plus each sfx_<domain>.json (battle, field, ui, shrine, ...), so parallel work never
## shares one file. A row id defined twice keeps the first file's (sfx.json, then the others by name).
static func sfx_rows() -> Dictionary:
	if _cache.has("@sfx_rows"):
		return _cache["@sfx_rows"]
	var out: Dictionary = {}
	var names: Array[String] = [SFX]
	var listing := DirAccess.get_files_at(DIR)
	listing.sort()
	for f in listing:
		if f.begins_with("sfx_") and f.ends_with(".json"):
			names.append(f.get_basename())
	for name in names:
		var rows := table(name).get("sfx", {}) as Dictionary
		for id: String in rows:
			if not out.has(id):
				out[id] = rows[id]
	_cache["@sfx_rows"] = out
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


## The ambience bed rows: music.json's `ambience` plus ambience.json's (M2-AUD-05); music.json's win on a clash.
static func bed_rows(music: Dictionary, amb: Dictionary) -> Dictionary:
	var out := (amb.get("ambience", {}) as Dictionary).duplicate(true)
	out.merge(music.get("ambience", {}) as Dictionary, true)
	return out


## `row` (music.json's zone row for `scene_path`, maybe {}) with ambience.json's beds for the scene when the row
## names none (no ambience key, or an empty list): the day list, or the night list once night_flag is set, plus
## the wind bed when the zone has wind. `flag_set` is (flag: StringName) -> bool.
static func merge_zone_beds(row: Dictionary, amb: Dictionary, scene_path: String, flag_set: Callable) -> Dictionary:
	var z := (amb.get("zones", {}) as Dictionary).get(scene_path, {}) as Dictionary
	if z.is_empty() or not (row.get("ambience", []) as Array).is_empty():
		return row
	var night := StringName(str(z.get("night_flag", "")))
	var key := "night" if night != &"" and z.has("night") and bool(flag_set.call(night)) else "day"
	var beds: Array = (z.get(key, []) as Array).duplicate()
	var wind_bed := str((amb.get("wind", {}) as Dictionary).get("bed", ""))
	if bool(z.get("wind", false)) and wind_bed != "" and not beds.has(wind_bed):
		beds.append(wind_bed)
	var out := row.duplicate(true)
	out["ambience"] = beds
	return out


## The wind bed's level offset (dB) for a wind of `speed` m/s: ambience.json `wind` maps min_m_s..max_m_s
## linearly onto min_db..max_db, clamped.
static func wind_db(amb: Dictionary, speed: float) -> float:
	var w := amb.get("wind", {}) as Dictionary
	var lo := float(w.get("min_m_s", 0.0))
	var hi := float(w.get("max_m_s", 1.0))
	var u := clampf((speed - lo) / (hi - lo), 0.0, 1.0) if hi > lo else (1.0 if speed >= hi else 0.0)
	return lerpf(float(w.get("min_db", 0.0)), float(w.get("max_db", 0.0)), u)
