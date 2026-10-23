extends Node
## Autoload "SaveSystem": versioned JSON saves with forward migrations.
## Saving is only offered at save shrines and chapter-boundary autosaves (genre convention).
##
## M1-ARC-03 APIs (docs/kb/tech/architecture.md, "Saves"):
##   save_to_slot(slot, state, reason, extra_meta)  atomic write (temp file + rename) with a "meta"
##                                                  block beside "version" and "state"
##   autosave(reason)                               Game.state -> slot 0; runs on EventBus.chapter_changed
##   slot_info(slot) / list_slots(slots)            what a save menu shows; never pushes errors
##   load_into_game(slot)                           load_from_slot + make it the live Game.state
##   delete_slot(slot), slot_exists(slot), location_name_key(id)
## The "meta" block is display data only (timestamp, reason, location key, shrine id). It is not
## part of GameStateData and is never needed to restore a game, so it needs no SAVE_VERSION bump.

const SAVE_VERSION := 2
const SAVE_DIR := "user://saves"
const AUTOSAVE_SLOT := 0
## slot_path() formats two digits.
const MAX_SLOT := 99
const TEMP_SUFFIX := ".tmp"
const REASON_MANUAL := &"manual"
const REASON_CHAPTER := &"chapter_boundary"
const STATUS_EMPTY := &"empty"
const STATUS_OK := &"ok"
const STATUS_CORRUPT := &"corrupt"
## Written by a newer build than this one: readable only after updating.
const STATUS_NEWER := &"newer"
const LOCATION_KEY_PREFIX := "LOCATION_"

## Where slots live. Tests and capture scenes point it at their own user:// folder.
var save_dir := SAVE_DIR
## Returns the current Unix time in seconds; tests and captures replace it for fixed timestamps.
var clock: Callable = Time.get_unix_time_from_system
## Off during tests and scripted sequences that must not touch slot 0.
var autosave_enabled := true

## Migrations keyed by the version they upgrade FROM. Each takes and returns a save dict.
var _migrations: Dictionary = {
	0: _migrate_v0_to_v1,
	1: _migrate_v1_to_v2,
}


func _ready() -> void:
	EventBus.chapter_changed.connect(_on_chapter_changed)


func slot_path(slot: int) -> String:
	return "%s/slot_%02d.json" % [save_dir, slot]


## Writes `state` to `slot`. The file is written beside the slot and renamed over it, so a crash
## mid-write leaves the old save intact. `reason` and `extra_meta` (e.g. {"shrine_id": ...}) go
## into the display-only "meta" block.
func save_to_slot(
	slot: int, state: GameStateData, reason: StringName = REASON_MANUAL, extra_meta: Dictionary = {}
) -> Error:
	if slot < 0 or slot > MAX_SLOT:
		push_error("SaveSystem: slot %d is out of range 0..%d" % [slot, MAX_SLOT])
		return ERR_PARAMETER_RANGE_ERROR
	DirAccess.make_dir_recursive_absolute(save_dir)
	var path := slot_path(slot)
	var tmp := path + TEMP_SUFFIX
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		return FileAccess.get_open_error()
	var data := serialize(state)
	data["meta"] = make_meta(state, reason, extra_meta)
	f.store_string(JSON.stringify(data, "\t"))
	f.close()
	var err := DirAccess.rename_absolute(tmp, path)
	if err != OK:
		DirAccess.remove_absolute(tmp)
		return err
	EventBus.game_saved.emit(slot)
	return OK


func load_from_slot(slot: int) -> GameStateData:
	if not FileAccess.file_exists(slot_path(slot)):
		return null
	var text := FileAccess.get_file_as_string(slot_path(slot))
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("SaveSystem: corrupt save in slot %d" % slot)
		return null
	var migrated := migrate(parsed as Dictionary)
	if migrated.is_empty() or not state_shape_ok(migrated.get("state", {})):
		push_error("SaveSystem: unreadable save in slot %d" % slot)
		return null
	var state := GameStateData.from_dict(migrated.get("state", {}) as Dictionary)
	if state != null:
		EventBus.game_loaded.emit(slot)
	return state


func serialize(state: GameStateData) -> Dictionary:
	return {"version": SAVE_VERSION, "state": state.to_dict()}


func deserialize(data: Dictionary) -> GameStateData:
	var migrated := migrate(data)
	if migrated.is_empty():
		return null
	return GameStateData.from_dict(migrated.get("state", {}) as Dictionary)


## Runs migrations until the save reaches SAVE_VERSION. Returns {} if a step is missing
## or the save comes from a newer build.
func migrate(data: Dictionary) -> Dictionary:
	var d := data.duplicate(true)
	var version := int(d.get("version", 0))
	if version > SAVE_VERSION:
		push_error("SaveSystem: save version %d is newer than build (%d)" % [version, SAVE_VERSION])
		return {}
	while version < SAVE_VERSION:
		if not _migrations.has(version):
			push_error("SaveSystem: no migration from version %d" % version)
			return {}
		d = (_migrations[version] as Callable).call(d)
		version += 1
		d["version"] = version
	return d


## v0 was the pre-release format: flat state with "coin" instead of "currency".
static func _migrate_v0_to_v1(d: Dictionary) -> Dictionary:
	var st: Dictionary = d.get("state", d).duplicate(true)
	st.erase("version")
	if st.has("coin"):
		st["currency"] = st["coin"]
		st.erase("coin")
	return {"version": 1, "state": st}


## v2 (M1-PRG-01) adds Lattice progress. A v1 save predates the Lattice, so it gets empty
## progress on the standard board; heroes are placed on their starts when they next join.
## The literal is frozen on purpose: later LatticeProgress changes need their own migration.
static func _migrate_v1_to_v2(d: Dictionary) -> Dictionary:
	var st: Dictionary = (d.get("state", {}) as Dictionary).duplicate(true)
	if not st.has("lattice"):
		st["lattice"] = {"board": "standard", "characters": {}, "opened_gates": []}
	return {"version": 2, "state": st}


# --- M1-ARC-03: autosave, slot listing, load into the live game ---------------------------------


## Saves the live Game.state to the autosave slot (0). Returns the Error and also reports it on
## EventBus.autosave_finished. ERR_UNAVAILABLE when autosave_enabled is off.
func autosave(reason: StringName = REASON_CHAPTER) -> Error:
	var err: Error = ERR_UNAVAILABLE
	if autosave_enabled:
		err = save_to_slot(AUTOSAVE_SLOT, Game.state, reason)
		if err != OK:
			push_warning("SaveSystem: autosave (%s) failed: %s" % [reason, error_string(err)])
	EventBus.autosave_finished.emit(reason, err)
	return err


func _on_chapter_changed(_chapter: int, _previous: int) -> void:
	autosave(REASON_CHAPTER)


## The display-only block written beside "state".
func make_meta(state: GameStateData, reason: StringName, extra: Dictionary = {}) -> Dictionary:
	var meta := extra.duplicate(true)
	meta["saved_at"] = int(clock.call())
	meta["reason"] = String(reason)
	meta["chapter"] = state.chapter
	meta["play_time_sec"] = state.play_time_sec
	meta["location_id"] = String(state.location_id)
	meta["location_key"] = location_name_key(state.location_id)
	return meta


## What a save menu needs about one slot, without loading it into the game and without pushing
## errors: {slot, status (STATUS_*), version, chapter, play_time_sec, location_id, location_key,
## saved_at (Unix s, from meta or else the file's modified time), reason}.
func slot_info(slot: int) -> Dictionary:
	var info := {
		"slot": slot,
		"status": STATUS_EMPTY,
		"version": -1,
		"chapter": 0,
		"play_time_sec": 0.0,
		"location_id": "",
		"location_key": "",
		"saved_at": 0,
		"reason": "",
	}
	var path := slot_path(slot)
	if not FileAccess.file_exists(path):
		return info
	info["status"] = STATUS_CORRUPT
	info["saved_at"] = int(FileAccess.get_modified_time(path))
	var json := JSON.new()
	if json.parse(FileAccess.get_file_as_string(path)) != OK or typeof(json.data) != TYPE_DICTIONARY:
		return info
	var d := json.data as Dictionary
	var st := _readable_state(d, info)
	if info["status"] == STATUS_OK:
		_fill_info(info, d, st)
	return info


## The migrated state of a parsed save, or {} (with info.status set to CORRUPT or NEWER).
func _readable_state(d: Dictionary, info: Dictionary) -> Dictionary:
	if not _is_number(d.get("version", 0)):
		return {}
	var version := int(d.get("version", 0))
	info["version"] = version
	if version > SAVE_VERSION:
		info["status"] = STATUS_NEWER
		return {}
	if version < 0 or not _has_migration_path(version):
		return {}
	var migrated := migrate(d)
	if migrated.is_empty() or not state_shape_ok(migrated.get("state")):
		return {}
	info["status"] = STATUS_OK
	return migrated["state"] as Dictionary


func _fill_info(info: Dictionary, d: Dictionary, st: Dictionary) -> void:
	info["chapter"] = int(st.get("chapter", 0))
	info["play_time_sec"] = float(st.get("play_time_sec", 0.0))
	info["location_id"] = str(st.get("location_id", ""))
	info["location_key"] = location_name_key(StringName(str(info["location_id"])))
	var meta: Variant = d.get("meta")
	if typeof(meta) == TYPE_DICTIONARY:
		var m := meta as Dictionary
		if _is_number(m.get("saved_at")):
			info["saved_at"] = int(m["saved_at"])
		info["reason"] = str(m.get("reason", ""))
		if typeof(m.get("location_key")) == TYPE_STRING and str(m["location_key"]) != "":
			info["location_key"] = str(m["location_key"])


func list_slots(slots: Array[int]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for s in slots:
		out.append(slot_info(s))
	return out


func slot_exists(slot: int) -> bool:
	return FileAccess.file_exists(slot_path(slot))


func delete_slot(slot: int) -> Error:
	if not slot_exists(slot):
		return ERR_FILE_NOT_FOUND
	return DirAccess.remove_absolute(slot_path(slot))


## Loads `slot` and makes it the live Game.state (and restarts the play clock). Moving to the
## saved location is the listener's job (EventBus.game_loaded): there is no location registry yet.
func load_into_game(slot: int) -> Error:
	if not slot_exists(slot):
		return ERR_FILE_NOT_FOUND
	var st := load_from_slot(slot)
	if st == null:
		return ERR_FILE_CORRUPT
	Game.state = st
	Game.start_play_clock()
	return OK


## True when a migrated "state" value has the types GameStateData.from_dict expects.
static func state_shape_ok(st: Variant) -> bool:
	if typeof(st) != TYPE_DICTIONARY:
		return false
	var d := st as Dictionary
	for k: String in ["flags", "inventory", "lattice"]:
		if d.has(k) and typeof(d[k]) != TYPE_DICTIONARY:
			return false
	for k: String in ["party_ids", "reserve_ids"]:
		if d.has(k) and typeof(d[k]) != TYPE_ARRAY:
			return false
	for k: String in ["currency", "play_time_sec", "chapter"]:
		if d.has(k) and not _is_number(d[k]):
			return false
	return true


## Localization key of a location's display name: "ch02/haluna" -> "LOCATION_CH02_HALUNA".
## Empty for an empty id.
static func location_name_key(location_id: StringName) -> String:
	if location_id == &"":
		return ""
	return LOCATION_KEY_PREFIX + String(location_id).to_upper().replace("/", "_").replace("-", "_")


func _has_migration_path(version: int) -> bool:
	for v in range(version, SAVE_VERSION):
		if not _migrations.has(v):
			return false
	return true


static func _is_number(v: Variant) -> bool:
	return typeof(v) == TYPE_INT or typeof(v) == TYPE_FLOAT
