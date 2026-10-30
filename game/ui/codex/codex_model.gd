class_name CodexModel
extends RefCounted
## The lore codex (M3-UI-03, SPEC §6.11), node-free: which entries are unlocked, which are new,
## and their words. Rows: game/data/lore/codex.json; text: game/data/loc/codex.csv. CodexMenu is
## the view; CodexNotice uses add_record() for records found in the field.
##
## An entry is unlocked by its `unlock`: {"flag": f} once story flag f is set, {"record": true}
## once its record has been found (flag codex_<id>_found, set by add_record), {"always": true}.
## Locked entries are never listed; a category still counts them ("3 of 8 found").
## Read state: one declared flag per entry, codex_<id>_read, set when the entry is opened. The flags
## already live in the save (GameStateData.flags), so nothing new is saved, an old save simply has
## every entry new, and validate_data.py checks each flag is declared (docs/kb/tech/ui.md).
## Tests build it with their own document and flag reader and writer.

const DATA_PATH := "res://game/data/lore/codex.json"
const UNLOCK_FLAG := "flag"
const UNLOCK_RECORD := "record"
const UNLOCK_ALWAYS := "always"

var data: Dictionary = {}
## Category rows in data order: {id, name_key, desc_key}.
var category_rows: Array[Dictionary] = []
## Entry rows in data order: {id, category, title_key, body_key, unlock}.
var entry_rows: Array[Dictionary] = []

var _is_set: Callable
var _mark: Callable


## `doc`: the "codex" object (default: codex.json). `flag_check`: Callable(flag) -> bool (default
## Game.get_flag); `flag_mark`: Callable(flag) (default Game.set_flag).
func _init(doc: Dictionary = {}, flag_check: Callable = Callable(), flag_mark: Callable = Callable()) -> void:
	_is_set = flag_check if flag_check.is_valid() else func(f: StringName) -> bool: return bool(Game.get_flag(f))
	_mark = flag_mark if flag_mark.is_valid() else func(f: StringName) -> void: Game.set_flag(f, true)
	data = doc if not doc.is_empty() else load_data()
	for c: Variant in data.get("categories", []):
		category_rows.append(c as Dictionary)
	for e: Variant in data.get("entries", []):
		entry_rows.append(e as Dictionary)


## The live codex over Game's flags.
static func from_game() -> CodexModel:
	return CodexModel.new()


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("codex")) != TYPE_DICTIONARY:
		push_error("CodexModel: could not read 'codex' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["codex"] as Dictionary


## The flag a found record sets (declared in flags.tres).
static func found_flag(id: StringName) -> StringName:
	return StringName("codex_%s_found" % id)


## The flag an opened entry sets (declared in flags.tres).
static func read_flag(id: StringName) -> StringName:
	return StringName("codex_%s_read" % id)


## The entry row for `id` ({} when there is none).
func entry(id: StringName) -> Dictionary:
	for e in entry_rows:
		if StringName(str(e.get("id", ""))) == id:
			return e
	return {}


func is_record(id: StringName) -> bool:
	return bool((entry(id).get("unlock", {}) as Dictionary).get(UNLOCK_RECORD, false))


## The records.json id a record entry opens in the document reader (its "reader" field; &"" when it has none).
func reader_of(id: StringName) -> StringName:
	return StringName(str(entry(id).get("reader", "")))


func is_unlocked(id: StringName) -> bool:
	var e := entry(id)
	if e.is_empty():
		return false
	var unlock: Dictionary = e.get("unlock", {})
	if bool(unlock.get(UNLOCK_ALWAYS, false)):
		return true
	if bool(unlock.get(UNLOCK_RECORD, false)):
		return bool(_is_set.call(found_flag(id)))
	var f := str(unlock.get(UNLOCK_FLAG, ""))
	return f != "" and bool(_is_set.call(StringName(f)))


func is_read(id: StringName) -> bool:
	return bool(_is_set.call(read_flag(id)))


## Marks an unlocked entry read. Returns true when it was new.
func mark_read(id: StringName) -> bool:
	if not is_unlocked(id) or is_read(id):
		return false
	_mark.call(read_flag(id))
	return true


## Marks record `id` found (the field hook). Returns true when this found it: false for an id that
## is not a record, or one already found.
func add_record(id: StringName) -> bool:
	if not is_record(id) or is_unlocked(id):
		return false
	_mark.call(found_flag(id))
	return true


## [{id, title, read, record}] for the unlocked entries of category `cat`, in data order.
func entries_in(cat: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for e in entry_rows:
		var id := StringName(str(e.get("id", "")))
		if StringName(str(e.get("category", ""))) != cat or not is_unlocked(id):
			continue
		out.append({"id": id, "title": title(id), "read": is_read(id), "record": is_record(id)})
	return out


## How many entries category `cat` has, locked or not.
func total_in(cat: StringName) -> int:
	var n := 0
	for e in entry_rows:
		if StringName(str(e.get("category", ""))) == cat:
			n += 1
	return n


## [{id, name, found, total, new}] for every category in data order (`new`: unread entries).
func categories() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for c in category_rows:
		var cid := StringName(str(c.get("id", "")))
		var shown := entries_in(cid)
		var unread := 0
		for e in shown:
			if not bool(e["read"]):
				unread += 1
		out.append(
			{
				"id": cid,
				"name": _tr(str(c.get("name_key", ""))),
				"found": shown.size(),
				"total": total_in(cid),
				"new": unread
			}
		)
	return out


func category_name(cat: StringName) -> String:
	return _tr(str(_category(cat).get("name_key", "")))


func category_desc(cat: StringName) -> String:
	return _tr(str(_category(cat).get("desc_key", "")))


func title(id: StringName) -> String:
	return _tr(str(entry(id).get("title_key", "")))


func body(id: StringName) -> String:
	return _tr(str(entry(id).get("body_key", "")))


## "6 of 10 entries found" (the header).
func summary() -> String:
	var found := 0
	for c in categories():
		found += int(c["found"])
	return _tr("CODEX_TOTAL_FMT").format({"found": found, "total": entry_rows.size()})


## "3 of 8" (a category row's right column).
func count_text(cat_row: Dictionary) -> String:
	return _tr("CODEX_ROW_COUNT_FMT").format({"found": cat_row.get("found", 0), "total": cat_row.get("total", 0)})


## "Places · 2 of 3 found" (the entry list's header).
func entries_header(cat_row: Dictionary) -> String:
	return _tr("CODEX_ENTRIES_HEAD_FMT").format(
		{"category": cat_row.get("name", ""), "found": cat_row.get("found", 0), "total": cat_row.get("total", 0)}
	)


func _category(cat: StringName) -> Dictionary:
	for c in category_rows:
		if StringName(str(c.get("id", ""))) == cat:
			return c
	return {}


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""
