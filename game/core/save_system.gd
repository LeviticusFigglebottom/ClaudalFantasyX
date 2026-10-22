extends Node
## Autoload "SaveSystem": versioned JSON saves with forward migrations.
## Saving is only offered at save shrines and chapter-boundary autosaves (genre convention).

const SAVE_VERSION := 2
const SAVE_DIR := "user://saves"
const AUTOSAVE_SLOT := 0

## Migrations keyed by the version they upgrade FROM. Each takes and returns a save dict.
var _migrations: Dictionary = {
	0: _migrate_v0_to_v1,
	1: _migrate_v1_to_v2,
}


func slot_path(slot: int) -> String:
	return "%s/slot_%02d.json" % [SAVE_DIR, slot]


func save_to_slot(slot: int, state: GameStateData) -> Error:
	DirAccess.make_dir_recursive_absolute(SAVE_DIR)
	var f := FileAccess.open(slot_path(slot), FileAccess.WRITE)
	if f == null:
		return FileAccess.get_open_error()
	f.store_string(JSON.stringify(serialize(state), "\t"))
	f.close()
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
	var state := deserialize(parsed as Dictionary)
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
