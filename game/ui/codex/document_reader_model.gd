class_name DocumentReaderModel
extends RefCounted
## The words and the marks of the document reader (M4-A2P-080; docs/kb/plan/act2/ui/screens.md section 1), Node-free.
## The view is DocumentReader. A record (game/data/lore/records.json) is two or three panes laid side by side (one
## for a found record the codex opens), each a title and its lines, one loc key per line (a ledger entry, a roll's
## name, a sentence). A "hand" is a group of lines, at most one per pane, written by the same hand.
##
## Play: each pane holds at most one mark. Marking a line moves the pane's mark to it; marking the marked line
## clears it. When every line of a hand not yet found is its pane's mark, that hand is found: its lines stay gold and
## the marks in those panes clear for the next. Once every hand is found the record's `flag` is set (the scene goes
## on). Marks and found hands are kept while the reader is open and in `state` for its next opening.

const DATA_PATH := "res://game/data/lore/records.json"
const TITLE_FMT_KEY := "READER_TITLE_FMT"
const HANDS_LEFT_FMT_KEY := "READER_HANDS_LEFT_FMT"
const ALL_FOUND_KEY := "READER_ALL_FOUND"
const PANE_FMT_KEY := "READER_PANE_FMT"
const NO_MARK := -1

## Where row_of reads records by default (tests point it at their fixture).
static var records_path := DATA_PATH

## The record row: {id, title_key, panes: [{title_key, lines: [key]}], hands: [{id, lines: [[pane, line]]}], flag}.
var record: Dictionary = {}
## Each pane's mark (a line index, or NO_MARK).
var marks: Array[int] = []
## The hands found so far, in the order found.
var found: Array[StringName] = []
## Sets a flag when the last hand is found: Callable(flag: StringName) (default: Game.set_flag).
var set_flag: Callable

var _tr: Callable


## `row`: a records.json row. `flag_setter` defaults to Game.set_flag; `translate` to tr (tests pass their own).
func _init(row: Dictionary, flag_setter: Callable = Callable(), translate: Callable = Callable()) -> void:
	record = row
	set_flag = flag_setter if flag_setter.is_valid() else func(f: StringName) -> void: Game.set_flag(f)
	_tr = translate if translate.is_valid() else func(k: String) -> String: return TranslationServer.translate(k)
	for i in pane_count():
		marks.append(NO_MARK)


## The records.json row with id `record_id` from `path` (records_path when ""), or {}.
static func row_of(record_id: StringName, path: String = "") -> Dictionary:
	var from := path if path != "" else records_path
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(from))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("DocumentReaderModel: could not read %s" % from)
		return {}
	for r: Variant in (parsed as Dictionary).get("records", []):
		if r is Dictionary and StringName(str((r as Dictionary).get("id", ""))) == record_id:
			return r as Dictionary
	return {}


func id() -> StringName:
	return StringName(str(record.get("id", "")))


func title() -> String:
	return _tr.call(TITLE_FMT_KEY).format({"record": _tr.call(str(record.get("title_key", "")))})


func pane_count() -> int:
	return (record.get("panes", []) as Array).size()


func pane_title(pane: int) -> String:
	return _tr.call(str(_pane(pane).get("title_key", "")))


## "2 of 3" over a pane when there are more than one ("" for a single pane).
func pane_label(pane: int) -> String:
	if pane_count() < 2:
		return ""
	return _tr.call(PANE_FMT_KEY).format({"n": pane + 1, "count": pane_count()})


## The pane's lines, translated.
func lines(pane: int) -> Array[String]:
	var out: Array[String] = []
	for k: Variant in _pane(pane).get("lines", []):
		out.append(_tr.call(str(k)))
	return out


func hand_count() -> int:
	return (record.get("hands", []) as Array).size()


## True when the record asks the player to find its hands (a found record read alone has none).
func has_hands() -> bool:
	return hand_count() > 0


func hands_left() -> int:
	return hand_count() - found.size()


func all_found() -> bool:
	return has_hands() and hands_left() == 0


## The line under the panes: how many hands are still to find, or that all are ("" for a record with none).
func hands_text() -> String:
	if not has_hands():
		return ""
	if all_found():
		return _tr.call(ALL_FOUND_KEY)
	return _tr.call(HANDS_LEFT_FMT_KEY).format({"n": hands_left(), "count": hand_count()})


## The found hand line `line` of `pane` belongs to (&"" when none).
func found_hand_at(pane: int, line: int) -> StringName:
	for h: Dictionary in _hands():
		var hid := StringName(str(h.get("id", "")))
		if found.has(hid) and _cells(h).has(Vector2i(pane, line)):
			return hid
	return &""


## The found hands' lines as [Vector2i(pane, line)], one array per hand, in the order found (the view's gold rules).
func found_links() -> Array[Array]:
	var out: Array[Array] = []
	for hid in found:
		for h: Dictionary in _hands():
			if StringName(str(h.get("id", ""))) == hid:
				out.append(_cells(h))
	return out


## Marks `line` of `pane` (or clears it when it is the mark). A line of a found hand takes no mark. Returns the hand
## this found (&"" when none); finding the last sets the record's flag.
func toggle(pane: int, line: int) -> StringName:
	if pane < 0 or pane >= pane_count() or line < 0 or line >= lines(pane).size():
		return &""
	if found_hand_at(pane, line) != &"":
		return &""
	marks[pane] = NO_MARK if marks[pane] == line else line
	for h: Dictionary in _hands():
		var hid := StringName(str(h.get("id", "")))
		var cells := _cells(h)
		if found.has(hid) or cells.is_empty():
			continue
		var all_marked := true
		for c: Vector2i in cells:
			all_marked = all_marked and c.x < marks.size() and marks[c.x] == c.y
		if all_marked:
			found.append(hid)
			for c: Vector2i in cells:
				marks[c.x] = NO_MARK
			var flag := StringName(str(record.get("flag", "")))
			if all_found() and flag != &"":
				set_flag.call(flag)
			return hid
	return &""


## The marks and found hands, to keep for the next opening.
func state() -> Dictionary:
	return {"marks": marks.duplicate(), "found": found.duplicate()}


func restore(saved: Dictionary) -> void:
	var m: Array = saved.get("marks", [])
	for i in mini(m.size(), marks.size()):
		marks[i] = int(m[i])
	for h: Variant in saved.get("found", []):
		if not found.has(StringName(str(h))):
			found.append(StringName(str(h)))


func _pane(pane: int) -> Dictionary:
	var panes: Array = record.get("panes", [])
	return panes[pane] as Dictionary if pane >= 0 and pane < panes.size() else {}


func _hands() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for h: Variant in record.get("hands", []):
		if h is Dictionary:
			out.append(h as Dictionary)
	return out


static func _cells(hand: Dictionary) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for c: Variant in hand.get("lines", []):
		var pair := c as Array
		if pair != null and pair.size() == 2:
			out.append(Vector2i(int(pair[0]), int(pair[1])))
	return out
