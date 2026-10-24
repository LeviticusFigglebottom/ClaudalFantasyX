class_name MemoriesModel
extends RefCounted
## The Memories gallery's words and unlocks (M3-MNU-02, SPEC §6.11), no nodes. Data:
## game/data/memories/memories.json (chapters in order; memories in order, each a dialogue scene, a
## stage scene and an unlock flag; see its "doc").
##
## Where the unlocks come from (the title decides with this, before any run is loaded): the
## "records", which are the live run (Game.state, which still holds a run after the end card or Quit
## to Title) and the newest readable save (the record Continue would load, read without loading
## it). A memory is remembered when its unlock flag is set in either. A replay plays on the record
## that remembers it (the live run first), so its branches read the flags that player saw.
## Records are read straight from their flags: a save that is not loaded has no Game API.

const DATA_PATH := "res://game/data/memories/memories.json"

var chapters: Array[Dictionary] = []
var memories: Array[Dictionary] = []
var records: Array[GameStateData] = []


func _init(data: Dictionary = {}, with_records: Array[GameStateData] = []) -> void:
	for c: Variant in data.get("chapters", []):
		if c is Dictionary:
			chapters.append(c as Dictionary)
	for m: Variant in data.get("memories", []):
		if m is Dictionary:
			memories.append(m as Dictionary)
	records = with_records


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("MemoriesModel: could not read %s" % DATA_PATH)
		return {}
	return parsed as Dictionary


## The gallery over the live run and the newest readable save in `save_system` (default: the
## SaveSystem autoload).
static func from_game(save_system: Node = null) -> MemoriesModel:
	return MemoriesModel.new(load_data(), game_records(save_system))


## [Game.state, the newest readable save's state] (the save left out when there is none).
static func game_records(save_system: Node = null) -> Array[GameStateData]:
	var out: Array[GameStateData] = [Game.state]
	var saved := newest_record(save_system)
	if saved != null:
		out.append(saved)
	return out


## The state of the newest readable slot (TitleSaveEntry.continue_slot), read without loading it.
static func newest_record(save_system: Node = null) -> GameStateData:
	var saves := save_system
	if saves == null:
		var tree := Engine.get_main_loop() as SceneTree
		saves = tree.root.get_node_or_null(^"SaveSystem") if tree != null else null
	if saves == null:
		return null
	var slot := TitleSaveEntry.continue_slot(saves)
	return saves.call(&"load_from_slot", slot) as GameStateData if slot >= 0 else null


func memory(id: StringName) -> Dictionary:
	for m in memories:
		if StringName(str(m.get("id", ""))) == id:
			return m
	return {}


## The record that remembers memory `id` (the live run first), or null while it is locked.
func record_for(id: StringName) -> GameStateData:
	var flag := str(memory(id).get("unlock_flag", ""))
	if flag == "":
		return null
	for r in records:
		if r != null and bool(r.flags.get(flag, false)):
			return r
	return null


func is_unlocked(id: StringName) -> bool:
	return record_for(id) != null


func any_unlocked() -> bool:
	for m in memories:
		if is_unlocked(StringName(str(m.get("id", "")))):
			return true
	return false


## Every memory of `chapter`, in file order.
func memories_in(chapter: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for m in memories:
		if StringName(str(m.get("chapter", ""))) == chapter:
			out.append(m)
	return out


## The remembered memories of `chapter`, in file order (locked ones are never listed).
func unlocked_in(chapter: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for m in memories_in(chapter):
		if is_unlocked(StringName(str(m.get("id", "")))):
			out.append(m)
	return out


## The chapters with at least one memory remembered, in order:
## [{id, name_key, found, total}]. A chapter nothing is remembered from is not named yet.
func chapter_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for c in chapters:
		var cid := StringName(str(c.get("id", "")))
		var found := unlocked_in(cid).size()
		if found > 0:
			out.append(
				{"id": cid, "name_key": str(c.get("name_key", "")), "found": found, "total": memories_in(cid).size()}
			)
	return out


## "2 of 3" (the chapters' right column) or "2 of 3 remembered" (the memories' header).
static func count_text(found: int, total: int, remembered: bool = false) -> String:
	var key := "MEMORIES_REMEMBERED_FMT" if remembered else "MEMORIES_COUNT_FMT"
	return TranslationServer.translate(key).format({"n": found, "m": total})
