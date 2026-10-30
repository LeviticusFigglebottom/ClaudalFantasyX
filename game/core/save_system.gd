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
##
## Review-sweep-E (M1-ARC-08 S4, M1-ARC-10; ADR 0018 amendment):
##   - The chapter autosave keeps a further-along autosave: when slot 0 holds a later chapter (or
##     the same chapter with more play time, or a newer build's save) than the live state, the
##     pending write is skipped (ERR_ALREADY_EXISTS on autosave_finished), unless New Game
##     started this run (the player confirmed replacing it). Loading an older record and crossing
##     its next boundary therefore never overwrites the run that got further.
##   - A downward Game.set_chapter (debug only) requests no autosave unless
##     autosave_on_chapter_regress is set.
##   - A leftover .tmp that is a complete, readable save newer than its slot (a crash, or a failed
##     rename, between the write and the rename) is never silently discarded: it is logged at
##     startup (report_leftover_temps), described by leftover_temp_info, restorable with
##     recover_temp, and set aside as `.recovered` before the next write to that slot would reuse
##     the temp name. A failed rename keeps the temp file for the same reason.
##   - FileAccess.flush() is a stdio flush, not an fsync: a power cut right after the rename can
##     still lose the newest write on some filesystems (architecture.md, Save robustness).
##
## Review-sweep-G (M1-ARC-11 rework; ADR 0018 Amendment 3):
##   - A loadout that no longer fits the item tables (a piece renamed or removed, or moved to
##     another hero or slot by a later equipment.json) is repaired on load, never read as corrupt:
##     the piece is taken off into the bag, or dropped when its base is unknown, with a warning
##     (EquipmentBag.repair_loadout), and grant_starting refills the weapon.
##   - No write replaces a non-empty slot that reads as corrupt: save_to_slot and recover_temp
##     first move it to a numbered `.corrupt` copy (corrupt_path, free_corrupt_path).
##   - A leftover temp that is not provably older than its slot (a newer build's temp included) is
##     set aside before the next write, and logged at startup (kept_leftover_temps).
##
## Review-sweep-H (M1-ARC-12; ADR 0018 Amendment 4):
##   - While the item tables are missing or failed to parse (item_tables_problem), a load keeps
##     the equipment exactly as saved (no repair, no starting gear) and save_to_slot refuses every
##     write with ERR_UNCONFIGURED and a push_error: a broken data build can never wipe the bag.
##   - A piece whose base the tables do not know stays in the bag, unworn (repair_loadout).
##   - A slot written by a newer build is moved to a numbered `.newer` copy before a write
##     replaces it (the confirmed manual save, a New Game autosave), as a corrupt slot is.
##
## Review-sweep-I (M1-ARC-13; ADR 0018 Amendment 5):
##   - The item-table guard above is now one of several checks behind a single data-tables gate,
##     data_health() (DataHealth): the item tables, the Lattice board the save names and
##     facets.json, the battle characters and statuses, locations.json, flags.tres and
##     party_rest.json. While data_tables_problem() is non-empty, a load runs no post-load step
##     and save_to_slot refuses every write with ERR_UNCONFIGURED. It is logged once at startup.
##   - The tables are loaded on first use and cached on the DataHealth (the item tables stay in
##     _item_db); tests replace one to simulate a broken build and set `_health` back to null to
##     reload. Flags and party_rest are read from Game, which owns them.
##
## M1-CMB-03 (v5): the bestiary log (GameStateData.bestiary, Bestiary). Its enemy ids are judged
## against battle/enemies.json by the data-tables gate's `bestiary` check.
##
## M2-ARC-01 (v6; ADR 0018 Amendment 6): Swell. Gauges and modes ride in party_vitals entries
## (`swell`, `swell_mode`), and the party's unlocked modes and unlock counts in GameStateData.swell.
## Their mode and rule ids are judged against battle/swell.json by the gate's `swell` check.

const SAVE_VERSION := 6
const SAVE_DIR := "user://saves"
const AUTOSAVE_SLOT := 0
## slot_path() formats two digits.
const MAX_SLOT := 99
const TEMP_SUFFIX := ".tmp"
## A valid leftover temp file is moved here (beside the slot) before a new write reuses its name.
const RECOVERED_SUFFIX := ".recovered"
## How many set-aside copies one slot keeps (`.recovered`, `.recovered.2`, ...) before the next
## leftover is replaced instead (each is a whole save; this only bounds a pathological loop).
const MAX_RECOVERED := 99
## A non-empty slot that reads as corrupt is moved here before a write replaces it (numbered like
## RECOVERED_SUFFIX: `.corrupt`, `.corrupt.2`, ... up to MAX_CORRUPT).
const CORRUPT_SUFFIX := ".corrupt"
const MAX_CORRUPT := 99
## A slot a newer build wrote is moved here before a write replaces it (numbered the same way:
## `.newer`, `.newer.2`, ... up to MAX_CORRUPT).
const NEWER_SUFFIX := ".newer"
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
## Debug only: let a downward Game.set_chapter request the chapter autosave (off: it never does,
## so a debug jump back never writes an earlier chapter over slot 0).
var autosave_on_chapter_regress := false

## Migrations keyed by the version they upgrade FROM. Each takes and returns a save dict.
var _migrations: Dictionary = {
	0: _migrate_v0_to_v1,
	1: _migrate_v1_to_v2,
	2: _migrate_v2_to_v3,
	3: _migrate_v3_to_v4,
	4: _migrate_v4_to_v5,
	5: _migrate_v5_to_v6,
}
## Item tables for the post-load starting-gear step (loaded on first use).
var _item_db: ItemDB
## The data-tables gate (built on first use by data_health(); M1-ARC-13).
var _health: DataHealth
## The reason of the autosave waiting for a safe point, or &"" when none waits.
var _pending_reason: StringName = &""
## The process frame the pending request was made on; it is written on a later frame.
var _pending_frame := 0
## Objects holding the autosave back, by instance id (WeakRef, so a freed holder never blocks).
var _holds: Dictionary = {}
## True from New Game until this run's first autosave is written: the player confirmed that the
## new run replaces slot 0 (ADR 0018), so the further-along rule does not protect the old run.
var _new_run := false


func _ready() -> void:
	EventBus.chapter_changed.connect(_on_chapter_changed)
	EventBus.new_game_started.connect(_on_new_game_started)
	set_process(false)
	report_leftover_temps.call_deferred()
	report_data_tables.call_deferred()


func _on_new_game_started() -> void:
	cancel_pending_autosave()
	_new_run = true


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
	var tables := data_tables_problem(state)
	if tables != "":
		push_error(
			(
				"SaveSystem: not saving slot %d: the data tables are broken (%s); every save on disk is kept as it is"
				% [slot, tables]
			)
		)
		return ERR_UNCONFIGURED
	DirAccess.make_dir_recursive_absolute(save_dir)
	var path := slot_path(slot)
	var tmp := path + TEMP_SUFFIX
	_set_aside_leftover_temp(slot)
	var data := serialize(state)
	data["meta"] = make_meta(state, reason, extra_meta)
	var err := _write_checked(tmp, JSON.stringify(data, "\t"))
	if err != OK:
		DirAccess.remove_absolute(tmp)
		push_warning("SaveSystem: writing slot %d failed (%s); the old save is kept" % [slot, error_string(err)])
		return err
	err = _set_aside_corrupt_slot(slot)
	if err != OK:
		DirAccess.remove_absolute(tmp)
		return err
	err = DirAccess.rename_absolute(tmp, path)
	if err != OK:
		# The temp file is a complete, checked save: keep it for recovery (leftover_temp_info).
		push_warning(
			(
				"SaveSystem: renaming the new save over slot %d failed (%s); the old save is kept and the new one is at %s"
				% [slot, error_string(err), tmp]
			)
		)
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


# --- Leftover temp files (M1-ARC-10) -------------------------------------------------------------


## What a leftover `slot_NN.json.tmp` holds, or {} when there is none: {status (STATUS_*),
## version, chapter, play_time_sec, saved_at, recoverable}. `recoverable` is true when it is a
## readable save and the slot is missing or damaged, or holds an older save (temp_is_newer).
## A slot written by a newer build (STATUS_NEWER) is never recovered over (M1-ARC-11): this build
## cannot read it, so it cannot know the temp file is newer, and replacing it after a downgrade
## would lose the newer build's save.
func leftover_temp_info(slot: int) -> Dictionary:
	var tmp := slot_path(slot) + TEMP_SUFFIX
	if not FileAccess.file_exists(tmp):
		return {}
	var info := _file_info(tmp)
	var main := slot_info(slot)
	info["recoverable"] = info["status"] == STATUS_OK and temp_is_newer(info, main)
	info["keep"] = temp_worth_keeping(info, main)
	return info


## M1-ARC-11 (review-sweep-G S2): true when a leftover temp file (`tmp`, a _file_info) must be set
## aside rather than overwritten: it is recoverable, or it is a save this build cannot compare
## with the slot (a newer build's temp, or a readable temp beside a newer build's slot). Only a
## torn temp (unreadable) and one provably older than a readable slot are overwritten.
static func temp_worth_keeping(tmp: Dictionary, main: Dictionary) -> bool:
	var status := StringName(str(tmp["status"]))
	if status == STATUS_NEWER:
		return true
	if status != STATUS_OK:
		return false
	return StringName(str(main["status"])) == STATUS_NEWER or temp_is_newer(tmp, main)


## True when a readable temp file (`tmp`, a _file_info) should replace the slot (`main`, a
## slot_info): the slot is empty or damaged, or it is a readable save of the same or an older
## version that was saved earlier. A save in the same second (two quick saves, then a failed
## rename) is newer when it has at least the slot's play time. A STATUS_NEWER slot, or a slot of a
## newer save version than the temp file, is never older.
static func temp_is_newer(tmp: Dictionary, main: Dictionary) -> bool:
	var status := StringName(str(main["status"]))
	if status == STATUS_EMPTY or status == STATUS_CORRUPT:
		return true
	if status != STATUS_OK or int(main["version"]) > int(tmp["version"]):
		return false
	var tmp_at := int(tmp["saved_at"])
	var main_at := int(main["saved_at"])
	if tmp_at != main_at:
		return tmp_at > main_at
	return float(tmp["play_time_sec"]) >= float(main["play_time_sec"])


## Restores a recoverable leftover temp file over its slot. ERR_FILE_NOT_FOUND when there is
## none, ERR_FILE_CORRUPT when it is not recoverable (see leftover_temp_info).
func recover_temp(slot: int) -> Error:
	var info := leftover_temp_info(slot)
	if info.is_empty():
		return ERR_FILE_NOT_FOUND
	if not bool(info["recoverable"]):
		return ERR_FILE_CORRUPT
	var err := _set_aside_corrupt_slot(slot)
	if err != OK:
		return err
	err = DirAccess.rename_absolute(slot_path(slot) + TEMP_SUFFIX, slot_path(slot))
	if err == OK:
		EventBus.game_saved.emit(slot)
	return err


## Logs every leftover temp file worth keeping (runs once at startup). Returns the slots whose
## temp is recoverable. A kept temp that is not recoverable (one this build cannot compare, such
## as a newer build's) is logged too: the next write to its slot sets it aside.
func report_leftover_temps() -> Array[int]:
	var found: Array[int] = []
	for slot in kept_leftover_temps():
		var info := leftover_temp_info(slot)
		var tmp := slot_path(slot) + TEMP_SUFFIX
		if bool(info["recoverable"]):
			found.append(slot)
			push_warning(
				(
					"SaveSystem: %s is a complete save newer than slot %d (chapter %d); recover_temp(%d) restores it"
					% [tmp, slot, int(info["chapter"]), slot]
				)
			)
		else:
			push_warning(
				(
					"SaveSystem: %s (%s, v%d) cannot be compared with slot %d by this build; kept, set aside on the next write"
					% [tmp, info["status"], int(info["version"]), slot]
				)
			)
	return found


## Slots whose leftover temp file is worth keeping (temp_worth_keeping), ascending.
func kept_leftover_temps() -> Array[int]:
	var out: Array[int] = []
	if not DirAccess.dir_exists_absolute(save_dir):
		return out
	for slot in range(0, MAX_SLOT + 1):
		var info := leftover_temp_info(slot)
		if not info.is_empty() and bool(info["keep"]):
			out.append(slot)
	return out


## Before a write reuses the temp name: a leftover worth keeping (temp_worth_keeping) is moved to
## `.recovered` (and logged) instead of being overwritten. An unreadable one is a torn write with
## nothing to keep, and a readable one older than a readable slot is superseded. An earlier
## set-aside is never replaced: the next free name is used (recovered_path).
func _set_aside_leftover_temp(slot: int) -> void:
	var info := leftover_temp_info(slot)
	if info.is_empty() or not bool(info["keep"]):
		return
	var tmp := slot_path(slot) + TEMP_SUFFIX
	var aside := free_recovered_path(slot)
	if aside != "" and DirAccess.rename_absolute(tmp, aside) == OK:
		push_warning("SaveSystem: a newer unsaved write for slot %d was moved to %s before saving" % [slot, aside])
	else:
		push_warning("SaveSystem: could not move %s aside; it will be replaced" % tmp)


## The set-aside file name for slot `slot`, n-th copy: `slot_NN.json.recovered` for n = 1, then
## `slot_NN.json.recovered.2`, `.recovered.3`, ...
func recovered_path(slot: int, n: int = 1) -> String:
	var base := slot_path(slot) + RECOVERED_SUFFIX
	return base if n <= 1 else "%s.%d" % [base, n]


## The first recovered_path that does not exist yet, or "" when all MAX_RECOVERED are taken.
func free_recovered_path(slot: int) -> String:
	for n in range(1, MAX_RECOVERED + 1):
		var path := recovered_path(slot, n)
		if not FileAccess.file_exists(path):
			return path
	return ""


## The copy a corrupt slot is moved to: `slot_NN.json.corrupt` for n = 1, then `.corrupt.2`, ...
func corrupt_path(slot: int, n: int = 1) -> String:
	return _copy_path(slot, CORRUPT_SUFFIX, n)


## The first corrupt_path that does not exist yet, or "" when all MAX_CORRUPT are taken.
func free_corrupt_path(slot: int) -> String:
	return _free_copy_path(slot, CORRUPT_SUFFIX)


## The copy a newer build's slot is moved to: `slot_NN.json.newer` for n = 1, then `.newer.2`, ...
func newer_path(slot: int, n: int = 1) -> String:
	return _copy_path(slot, NEWER_SUFFIX, n)


## The first newer_path that does not exist yet, or "" when all MAX_CORRUPT are taken.
func free_newer_path(slot: int) -> String:
	return _free_copy_path(slot, NEWER_SUFFIX)


func _copy_path(slot: int, suffix: String, n: int) -> String:
	var base := slot_path(slot) + suffix
	return base if n <= 1 else "%s.%d" % [base, n]


func _free_copy_path(slot: int, suffix: String) -> String:
	for n in range(1, MAX_CORRUPT + 1):
		var path := _copy_path(slot, suffix, n)
		if not FileAccess.file_exists(path):
			return path
	return ""


## M1-ARC-11 (review-sweep-G B1): before anything replaces a slot, a non-empty slot that reads as
## corrupt is moved to the next free `.corrupt` copy, so a save this build cannot read (damaged,
## or failing a check that a later build relaxes) is never destroyed. M1-ARC-12 (review-sweep-H
## S2): a slot a newer build wrote is moved to the next free `.newer` copy the same way, so the
## confirmed overwrite after a downgrade keeps the newer run for when the player updates again.
## Returns OK when there was nothing to keep or it was moved; otherwise the error, and the caller
## must not replace the slot.
func _set_aside_corrupt_slot(slot: int) -> Error:
	var path := slot_path(slot)
	if not FileAccess.file_exists(path):
		return OK
	var status: StringName = slot_info(slot)["status"]
	if status != STATUS_CORRUPT and status != STATUS_NEWER:
		return OK
	if FileAccess.get_file_as_bytes(path).is_empty():
		return OK
	var what := "unreadable" if status == STATUS_CORRUPT else "from a newer build"
	var aside := free_corrupt_path(slot) if status == STATUS_CORRUPT else free_newer_path(slot)
	if aside == "":
		push_warning("SaveSystem: slot %d is %s and all %d copies are taken; it is kept" % [slot, what, MAX_CORRUPT])
		return ERR_ALREADY_EXISTS
	var err := DirAccess.rename_absolute(path, aside)
	if err != OK:
		push_warning(
			"SaveSystem: could not move slot %d (%s) to %s (%s); it is kept" % [slot, what, aside, error_string(err)]
		)
		return err
	push_warning("SaveSystem: slot %d was %s; it was moved to %s before the new save" % [slot, what, aside])
	return OK


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


func _items() -> ItemDB:
	if _item_db == null:
		_item_db = ItemDB.load_default()
	return _item_db


## Why the item tables cannot be trusted to judge saved equipment right now ("" when they can;
## ItemDB.integrity_problem). While this is non-empty, loads skip the equipment repair and
## save_to_slot refuses to write (M1-ARC-12).
func item_tables_problem() -> String:
	var db := _items()
	if db == null:
		return "the item tables could not be built"
	return db.integrity_problem()


# --- The data-tables gate (M1-ARC-13) -------------------------------------------------------------


## The one gate every save write and every post-load step asks (DataHealth.standard: a check per
## table that saved state refers to; the item check is item_tables_problem, so `_item_db` stays
## the item tables' injection point). Tests replace a table on it, or set `_health` to null to
## rebuild it from the shipped files.
func data_health() -> DataHealth:
	if _health == null:
		_health = DataHealth.standard(func(_st: GameStateData) -> String: return item_tables_problem())
	return _health


## Why the data tables cannot be trusted with `state` right now ("" when they can). While this is
## non-empty, loads skip the post-load step and save_to_slot refuses to write.
func data_tables_problem(state: GameStateData = null) -> String:
	return data_health().problem(state)


## Pushes one error naming every broken table (runs once at startup, review-sweep-I S2 for
## ARC-12): a build that can never save says so before the player has played a session.
## Returns the problem ("" when healthy).
func report_data_tables() -> String:
	var problem := data_tables_problem()
	if problem != "":
		push_error("SaveSystem: saving is off until the data tables are fixed: %s" % problem)
	return problem


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


## Runs after every load. First, a worn piece that no longer fits the item tables is taken off
## into the bag, with a warning (EquipmentBag.repair_loadout; review-sweep-G B1: a balance patch
## must never brick a save). A piece of unknown equipment stays in the bag, unworn, with one
## warning per load. Then joined heroes receive any missing starting gear (a v2 save migrated to
## v3 has an empty bag, "weapon" is a required slot, and a repaired slot is empty). Idempotent.
## M1-ARC-12 (review-sweep-H S1): while the item tables are broken (item_tables_problem) every
## piece would read as unknown, so nothing here runs: the equipment stays exactly as saved, with
## a push_error, and save_to_slot refuses to write until the tables load again.
## M1-ARC-13: the check is the whole data-tables gate (data_tables_problem), not only the items.
func _post_load(state: GameStateData) -> GameStateData:
	if state == null:
		return null
	var tables := data_tables_problem(state)
	if tables != "":
		push_error(
			(
				"SaveSystem: the data tables are broken (%s); the save is loaded as saved, unrepaired, and saving is off"
				% tables
			)
		)
		return state
	var goods := PartyGoods.from_state(_items(), state)
	for note in goods.equipment.repair_loadout():
		push_warning("SaveSystem: equipment.%s" % note)
	var unknown := goods.equipment.unknown_uids()
	if not unknown.is_empty():
		push_warning(
			(
				"SaveSystem: equipment.owned: %d piece(s) of unknown equipment %s are kept unworn as saved"
				% [unknown.size(), unknown]
			)
		)
	goods.ensure_starting_gear(state)
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
## M1-ARC-11 (review-sweep-F): this runs before SaveShape, so it converts only what is already a
## whole number (SaveShape.is_whole). Anything else (a non-Dictionary inventory, a string, a huge
## count, a fraction, a nested value) is passed through untouched, and the shape check that
## follows reads the save as corrupt: never a crash (int() of a Dictionary) or a silent coercion.
## A whole count <= 0 is an empty stack and is dropped, as this step always did (review-sweep-G
## S1: v2 never normalized its counts, so a negative one is legacy data, not damage); a negative
## count also warns. From v3 on a negative count is corrupt (SaveShape).
static func _migrate_v2_to_v3(d: Dictionary) -> Dictionary:
	var st: Dictionary = (d.get("state", {}) as Dictionary).duplicate(true)
	if not st.has("equipment"):
		st["equipment"] = {"next_uid": 1, "owned": {}, "loadout": {}}
	var old: Variant = st.get("inventory", {})
	if old is Dictionary:
		var inv: Dictionary = {}
		for k: Variant in old:
			var v: Variant = old[k]
			if not SaveShape.is_whole(v):
				inv[k] = v
			elif int(v) > 0:
				inv[str(k)] = int(v)
			elif int(v) < 0:
				push_warning(
					"SaveSystem: v2 inventory '%s' had a negative count (%d); the stack is dropped" % [k, int(v)]
				)
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


## v5 (M1-CMB-03) adds the bestiary log. A v4 save predates Read, so nothing is logged yet. The
## literal is frozen on purpose.
static func _migrate_v4_to_v5(d: Dictionary) -> Dictionary:
	var st: Dictionary = (d.get("state", {}) as Dictionary).duplicate(true)
	if not st.has("bestiary"):
		st["bestiary"] = {}
	return {"version": 5, "state": st}


## v6 (M2-ARC-01): Swell. A v5 save predates carried gauges: every gauge is empty and every mode
## the default (party_vitals entries need no change), and nothing is unlocked through play yet.
## The literal is frozen.
static func _migrate_v5_to_v6(d: Dictionary) -> Dictionary:
	var st: Dictionary = (d.get("state", {}) as Dictionary).duplicate(true)
	if not st.has("swell"):
		st["swell"] = {"unlocked": [], "progress": {}}
	return {"version": 6, "state": st}


# --- M1-ARC-03: autosave, slot listing, load into the live game ---------------------------------


## Saves the live Game.state to the autosave slot (0). Returns the Error and also reports it on
## EventBus.autosave_finished. ERR_UNAVAILABLE when autosave_enabled is off.
## Writes at once: callers are responsible for the timing. The chapter boundary goes through
## request_autosave instead, so it never snapshots a cutscene in progress.
func autosave(reason: StringName = REASON_CHAPTER) -> Error:
	var err: Error = ERR_UNAVAILABLE
	if autosave_enabled:
		err = save_to_slot(AUTOSAVE_SLOT, autosave_state(Game.state, reason), reason)
		if err != OK:
			push_warning("SaveSystem: autosave (%s) failed: %s" % [reason, error_string(err)])
	EventBus.autosave_finished.emit(reason, err)
	return err


## The state a chapter autosave records (ADR 0121): Continue from it starts in the zone the chapter began in, where the
## slot says it is, not at the last shrine, which is in the chapter before (the Lead's save pass, 2026-10-30: a Ch4
## autosave read "Haluna's wake" and continued at the Shell Shrine). The respawn becomes that zone at its own spawn, on
## a copy: Game.state keeps its shrine. Other reasons (a shrine's own save) are written as they are.
static func autosave_state(state: GameStateData, reason: StringName) -> GameStateData:
	if reason != REASON_CHAPTER or state == null or state.location_id == &"":
		return state
	if state.respawn_location_id == state.location_id:
		return state
	var copy := GameStateData.from_dict(state.to_dict())
	copy.respawn_location_id = state.location_id
	copy.respawn_spawn = &""
	return copy


func _on_chapter_changed(chapter: int, previous: int) -> void:
	if chapter < previous and not autosave_on_chapter_regress:
		push_warning(
			(
				"SaveSystem: chapter %d -> %d goes backwards (debug); no autosave (autosave_on_chapter_regress)"
				% [previous, chapter]
			)
		)
		return
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
	if not _new_run and autosave_is_further_along(Game.state):
		push_warning("SaveSystem: slot 0 holds a further-along journey; the %s autosave is skipped" % reason)
		EventBus.autosave_finished.emit(reason, ERR_ALREADY_EXISTS)
		return ERR_ALREADY_EXISTS
	var err := autosave(reason)
	if err == OK:
		_new_run = false
	return err


## True when slot 0 holds a journey further along than `state` (ADR 0018 amendment): a later
## chapter, the same chapter with more play time, or a save from a newer build. An empty or
## damaged slot 0 is never further along.
func autosave_is_further_along(state: GameStateData) -> bool:
	var info := slot_info(AUTOSAVE_SLOT)
	if info["status"] == STATUS_NEWER:
		return true
	if info["status"] != STATUS_OK:
		return false
	var chapter := int(info["chapter"])
	if chapter != state.chapter:
		return chapter > state.chapter
	return float(info["play_time_sec"]) > state.play_time_sec


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
		"party": [],
	}
	var path := slot_path(slot)
	if not FileAccess.file_exists(path):
		return info
	info.merge(_file_info(path), true)
	return info


## slot_info's reading of one file (a slot or a temp file) that exists.
func _file_info(path: String) -> Dictionary:
	var info := {
		"status": STATUS_CORRUPT,
		"version": -1,
		"chapter": 0,
		"play_time_sec": 0.0,
		"location_id": "",
		"location_key": "",
		"saved_at": int(FileAccess.get_modified_time(path)),
		"reason": "",
		"party": [],
	}
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
	# Act II (M4-A2P-082): a save made after the trap carries its heretic tag on the slot row.
	info["heretic"] = bool((st.get("flags", {}) as Dictionary).get("ch14_declared_heretics", false))
	var party: Variant = st.get("party_ids", [])  # the active line, for the save rows' faces
	info["party"] = (party as Array).map(func(v: Variant) -> String: return str(v)) if party is Array else []
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
	_new_run = false
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
