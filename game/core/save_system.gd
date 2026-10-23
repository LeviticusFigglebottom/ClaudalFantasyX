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
##
## M1-ARC-06 (v4): party vitals, attuned shrines and the respawn point (GameStateData). Every
## load (load_from_slot, deserialize) then runs the post-load step: joined heroes get any missing
## starting gear (PartyGoods.ensure_starting_gear, M1-PRG-03). EventBus.game_loaded is emitted by
## load_into_game once the save IS the live state (WorldReturn routes on it); a plain
## load_from_slot (menus, tools, tests) only reads.
##
## M1-ARC-08 (robustness, after QA review-sweep-C):
##   - A write is checked before the rename: store result, flush, get_error(), then the temp file
##     is read back and compared. On any failure the temp file is deleted, the slot keeps its old
##     save and save_to_slot returns the error (ERR_FILE_CANT_WRITE when Godot reported none).
##     `store_text` is the injectable writer that tests use to simulate a failed or short write.
##   - Every load and listing deep-checks the migrated state (SaveShape) and requires a whole
##     version number: malformed data reads as corrupt, never as a crash or a half-loaded state.
##     load_from_slot, deserialize and slot_info share one reader (_read_save).
##   - The chapter autosave is deferred: chapter_changed only requests it (request_autosave), and
##     it is written on a later frame at the first safe point: no autosave hold (hold_autosave;
##     a cutscene sequencer holds for the whole cutscene, and FieldCameraDirector holds while a
##     scripted shot has the camera), no scene change in progress and the tree not paused. New
##     Game and load_into_game drop a pending request.

const SAVE_VERSION := 4
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
## Writes `text` into an open file and returns true on success (FileAccess.store_string). Tests
## replace it to simulate a full disk or a short write; save_to_slot must then keep the old save.
var store_text: Callable = _store_text

## Migrations keyed by the version they upgrade FROM. Each takes and returns a save dict.
var _migrations: Dictionary = {
	0: _migrate_v0_to_v1,
	1: _migrate_v1_to_v2,
	2: _migrate_v2_to_v3,
	3: _migrate_v3_to_v4,
}
## Item tables for the post-load starting-gear step (loaded on first use).
var _item_db: ItemDB
## The reason of the autosave waiting for a safe point, or &"" when none waits.
var _pending_reason: StringName = &""
## The process frame the pending request was made on; it is written on a later frame.
var _pending_frame := 0
## Objects holding the autosave back, by instance id (WeakRef, so a freed holder never blocks).
var _holds: Dictionary = {}


func _ready() -> void:
	EventBus.chapter_changed.connect(_on_chapter_changed)
	EventBus.new_game_started.connect(cancel_pending_autosave)
	set_process(false)


func _process(_delta: float) -> void:
	if Engine.get_process_frames() > _pending_frame:
		poll_pending_autosave()


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
	var data := serialize(state)
	data["meta"] = make_meta(state, reason, extra_meta)
	var err := _write_checked(tmp, JSON.stringify(data, "\t"))
	if err != OK:
		DirAccess.remove_absolute(tmp)
		push_warning("SaveSystem: writing slot %d failed (%s); the old save is kept" % [slot, error_string(err)])
		return err
	err = DirAccess.rename_absolute(tmp, path)
	if err != OK:
		DirAccess.remove_absolute(tmp)
		return err
	EventBus.game_saved.emit(slot)
	return OK


## Opens, writes, flushes and closes `path`, checking each step, then reads the file back and
## compares it with `text`. Returns OK only when the whole text is on disk.
func _write_checked(path: String, text: String) -> Error:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		var open_err := FileAccess.get_open_error()
		return open_err if open_err != OK else ERR_FILE_CANT_OPEN
	var stored := bool(store_text.call(f, text))
	f.flush()
	var err := f.get_error()
	f.close()
	if err == OK and not stored:
		err = ERR_FILE_CANT_WRITE
	if err == OK and FileAccess.get_file_as_string(path) != text:
		err = ERR_FILE_CANT_WRITE
	return err


static func _store_text(f: FileAccess, text: String) -> bool:
	return f.store_string(text)


func load_from_slot(slot: int) -> GameStateData:
	if not FileAccess.file_exists(slot_path(slot)):
		return null
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(slot_path(slot)))
	var read := _read_save(parsed)
	if read["status"] != STATUS_OK:
		push_error("SaveSystem: slot %d is unreadable (%s): %s" % [slot, read["status"], read["problem"]])
		return null
	return _post_load(GameStateData.from_dict(read["state"] as Dictionary))


func serialize(state: GameStateData) -> Dictionary:
	return {"version": SAVE_VERSION, "state": state.to_dict()}


## A save dict -> GameStateData, or null when it is newer, has no migration path or is malformed.
func deserialize(data: Dictionary) -> GameStateData:
	var read := _read_save(data)
	if read["status"] != STATUS_OK:
		push_error("SaveSystem: unreadable save (%s): %s" % [read["status"], read["problem"]])
		return null
	return _post_load(GameStateData.from_dict(read["state"] as Dictionary))


## The one reader behind load_from_slot, deserialize and slot_info. Never pushes errors.
## Returns {status: STATUS_OK | STATUS_CORRUPT | STATUS_NEWER, version: int (-1 when unknown),
## state: the migrated state ({} unless OK), problem: why it is not OK}.
func _read_save(parsed: Variant) -> Dictionary:
	var out := {"status": STATUS_CORRUPT, "version": -1, "state": {}, "problem": ""}
	if typeof(parsed) != TYPE_DICTIONARY:
		out["problem"] = "not a JSON object"
		return out
	var d := parsed as Dictionary
	out["problem"] = _version_problem(d, out)
	if out["problem"] != "":
		return out
	var migrated := migrate(d)
	var problem := "migration failed" if migrated.is_empty() else SaveShape.problem(migrated.get("state"))
	if problem != SaveShape.OK_SHAPE:
		out["problem"] = problem
		return out
	out["status"] = STATUS_OK
	out["state"] = migrated["state"]
	return out


## Why a parsed save cannot be migrated ("" when it can). Fills out.version, and out.status
## with STATUS_NEWER for a save from a newer build.
func _version_problem(d: Dictionary, out: Dictionary) -> String:
	var raw_version: Variant = d.get("version", 0)
	if not SaveShape.is_whole(raw_version):
		return "version is not a whole number"
	var version := int(raw_version)
	out["version"] = version
	if version > SAVE_VERSION:
		out["status"] = STATUS_NEWER
		return "saved by a newer build (v%d > v%d)" % [version, SAVE_VERSION]
	if version < 0 or not _has_migration_path(version):
		return "no migration path from v%d" % version
	if not _state_is_dict(d):
		return "state: expected a Dictionary"
	return ""


## Runs after every load: joined heroes receive any missing starting gear (a v2 save migrated to
## v3 has an empty bag, and "weapon" is a required slot). Idempotent.
func _post_load(state: GameStateData) -> GameStateData:
	if state == null:
		return null
	if _item_db == null:
		_item_db = ItemDB.load_default()
	PartyGoods.from_state(_item_db, state).ensure_starting_gear(state)
	return state


## Runs migrations until the save reaches SAVE_VERSION. Returns {} if a step is missing
## or the save comes from a newer build.
func migrate(data: Dictionary) -> Dictionary:
	var d := data.duplicate(true)
	if not SaveShape.is_whole(d.get("version", 0)):
		push_error("SaveSystem: save version %s is not a whole number" % str(d.get("version")))
		return {}
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


## v3 (M1-PRG-02) adds equipment pieces and loadouts. A v2 save predates equipment, so it gets an
## empty bag; heroes receive their starting gear (EquipmentBag.grant_starting) when they next
## join. Inventory counts are made whole ints and empty stacks dropped, because JSON numbers load
## as floats and v2 never normalized them. The literal is frozen on purpose.
static func _migrate_v2_to_v3(d: Dictionary) -> Dictionary:
	var st: Dictionary = (d.get("state", {}) as Dictionary).duplicate(true)
	if not st.has("equipment"):
		st["equipment"] = {"next_uid": 1, "owned": {}, "loadout": {}}
	var inv: Dictionary = {}
	var old: Variant = st.get("inventory", {})
	if old is Dictionary:
		for k: Variant in old:
			var n := int(old[k])
			if n > 0:
				inv[str(k)] = n
	st["inventory"] = inv
	return {"version": 3, "state": st}


## v4 (M1-ARC-06) adds party vitals, attuned shrines and the respawn point. A v3 save predates
## them: everyone is at full HP and MP with no statuses (empty party_vitals), nothing is attuned,
## and the respawn is the save's location_id with the location's own spawn (an empty location
## resolves to locations.json "default_location" at load time). The literal is frozen on purpose.
static func _migrate_v3_to_v4(d: Dictionary) -> Dictionary:
	var st: Dictionary = (d.get("state", {}) as Dictionary).duplicate(true)
	if not st.has("party_vitals"):
		st["party_vitals"] = {}
	if not st.has("attuned_shrines"):
		st["attuned_shrines"] = []
	if not st.has("respawn"):
		st["respawn"] = {"location_id": str(st.get("location_id", "")), "spawn": ""}
	return {"version": 4, "state": st}


# --- M1-ARC-03: autosave, slot listing, load into the live game ---------------------------------


## Saves the live Game.state to the autosave slot (0). Returns the Error and also reports it on
## EventBus.autosave_finished. ERR_UNAVAILABLE when autosave_enabled is off.
## Writes at once: callers are responsible for the timing. The chapter boundary goes through
## request_autosave instead, so it never snapshots a cutscene in progress.
func autosave(reason: StringName = REASON_CHAPTER) -> Error:
	var err: Error = ERR_UNAVAILABLE
	if autosave_enabled:
		err = save_to_slot(AUTOSAVE_SLOT, Game.state, reason)
		if err != OK:
			push_warning("SaveSystem: autosave (%s) failed: %s" % [reason, error_string(err)])
	EventBus.autosave_finished.emit(reason, err)
	return err


func _on_chapter_changed(_chapter: int, _previous: int) -> void:
	request_autosave(REASON_CHAPTER)


## Asks for an autosave at the next safe point (see is_safe_point) on a later frame. A second
## request before it is written replaces the reason: one write covers both, with the state as
## it is at that point.
func request_autosave(reason: StringName = REASON_CHAPTER) -> void:
	_pending_reason = reason
	_pending_frame = Engine.get_process_frames()
	set_process(true)


func has_pending_autosave() -> bool:
	return _pending_reason != &""


## Drops a waiting autosave (New Game, a load: the state it was asked for is gone).
func cancel_pending_autosave() -> void:
	_pending_reason = &""
	set_process(false)


## Writes the pending autosave if this is a safe point. Returns ERR_DOES_NOT_EXIST when nothing
## waits, ERR_BUSY when it must keep waiting, otherwise autosave()'s result. _process calls it on
## every frame after the request; tests call it directly.
func poll_pending_autosave() -> Error:
	if not has_pending_autosave():
		set_process(false)
		return ERR_DOES_NOT_EXIST
	if not is_safe_point():
		return ERR_BUSY
	var reason := _pending_reason
	cancel_pending_autosave()
	return autosave(reason)


## True when an autosave may snapshot the game: nothing holds it, SceneRouter is not changing
## scene, and the tree is not paused (a menu is open).
func is_safe_point() -> bool:
	if not autosave_holders().is_empty():
		return false
	var tree := get_tree()
	if tree == null:
		return true
	if tree.paused:
		return false
	var router := tree.root.get_node_or_null(^"SceneRouter")
	return router == null or not bool(router.call(&"is_busy"))


## Holds the autosave back until release_autosave(holder) (or until `holder` is freed). A
## cutscene sequencer holds it from the first beat to the last; a request made meanwhile is
## written after the release. Holding twice with the same object is one hold.
func hold_autosave(holder: Object) -> void:
	if holder != null:
		_holds[holder.get_instance_id()] = weakref(holder)


func release_autosave(holder: Object) -> void:
	if holder != null:
		_holds.erase(holder.get_instance_id())


## The live objects holding the autosave back (freed holders are dropped here).
func autosave_holders() -> Array[Object]:
	var out: Array[Object] = []
	for id: Variant in _holds.keys():
		var o: Variant = (_holds[id] as WeakRef).get_ref()
		if o == null:
			_holds.erase(id)
		else:
			out.append(o as Object)
	return out


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
	if json.parse(FileAccess.get_file_as_string(path)) != OK:
		return info
	var read := _read_save(json.data)
	info["status"] = read["status"]
	info["version"] = read["version"]
	if info["status"] == STATUS_OK:
		_fill_info(info, json.data as Dictionary, read["state"] as Dictionary)
	return info


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


## Loads `slot`, makes it the live Game.state, restarts the play clock and emits
## EventBus.game_loaded. Moving to the respawn point is WorldReturn's job (it listens there).
func load_into_game(slot: int) -> Error:
	if not slot_exists(slot):
		return ERR_FILE_NOT_FOUND
	var st := load_from_slot(slot)
	if st == null:
		return ERR_FILE_CORRUPT
	cancel_pending_autosave()
	Game.state = st
	Game.start_play_clock()
	EventBus.game_loaded.emit(slot)
	return OK


## True when a migrated "state" value has the shape GameStateData.from_dict and the domain
## objects expect, down to element types (SaveShape, M1-ARC-08).
static func state_shape_ok(st: Variant) -> bool:
	return SaveShape.is_ok(st)


## Localization key of a location's display name: "ch02/haluna" -> "LOCATION_CH02_HALUNA".
## Empty for an empty id.
static func location_name_key(location_id: StringName) -> String:
	if location_id == &"":
		return ""
	return LOCATION_KEY_PREFIX + String(location_id).to_upper().replace("/", "_").replace("-", "_")


## Migrations cast "state" to a Dictionary, so anything else must be rejected before them.
## (A v0 save is flat and has no "state" key.)
static func _state_is_dict(d: Dictionary) -> bool:
	return not d.has("state") or typeof(d["state"]) == TYPE_DICTIONARY


func _has_migration_path(version: int) -> bool:
	for v in range(version, SAVE_VERSION):
		if not _migrations.has(v):
			return false
	return true


static func _is_number(v: Variant) -> bool:
	return typeof(v) == TYPE_INT or typeof(v) == TYPE_FLOAT
