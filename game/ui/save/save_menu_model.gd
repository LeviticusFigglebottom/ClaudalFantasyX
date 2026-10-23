class_name SaveMenuModel
extends RefCounted
## The save/load menu's logic without nodes (M1-ARC-03), so tests drive it directly.
##
## Phases: BROWSE (cursor over the slot list) -> CONFIRM (overwrite question, "Keep it" is the
## default) -> RESULT (one message and "Continue") -> CLOSED. Rows that can't be used (the
## autosave slot when saving, empty or unreadable slots when loading) are still visited by the
## cursor, so the help line can say why (pillar 4); accepting on one changes nothing.
##
## `saves` is the SaveSystem autoload (or a stand-in with the same methods). Saving writes the
## live Game.state; loading replaces it (SaveSystem.load_into_game).

signal changed

enum Mode { SAVE, LOAD }
enum Phase { BROWSE, CONFIRM, RESULT, CLOSED }
enum Outcome { NONE, MOVED, REFUSED, ASK_OVERWRITE, KEPT, SAVED, SAVE_FAILED, LOADED, LOAD_FAILED, CLOSED }

## Dialog choice ids.
const CHOICE_YES := &"yes"
const CHOICE_NO := &"no"
const CHOICE_CONTINUE := &"continue"
## Help-line loc keys by slot status (SaveSystem.STATUS_*).
const SAVE_HELP_KEYS := {
	&"empty": "SAVE_HELP_EMPTY",
	&"ok": "SAVE_HELP_OVERWRITE",
	&"corrupt": "SAVE_HELP_CORRUPT",
	&"newer": "SAVE_HELP_NEWER",
}
const LOAD_HELP_KEYS := {
	&"empty": "LOAD_HELP_EMPTY",
	&"ok": "LOAD_HELP_READY",
	&"corrupt": "LOAD_HELP_CORRUPT",
	&"newer": "LOAD_HELP_NEWER",
}

var mode: Mode = Mode.SAVE
var phase: Phase = Phase.BROWSE
var saves: Node
var slot_ids: Array[int] = []
var slots: Array[SaveSlotInfo] = []
var cursor := 0
## Merged into the save's meta block (e.g. {"shrine_id": "haluna_shrine"}).
var extra_meta: Dictionary = {}
## Index into dialog_choices() while a dialog is open.
var dialog_cursor := 0
## Loc key of the open dialog's message ("" when none).
var dialog_key := ""
var last_error: Error = OK
var last_outcome: Outcome = Outcome.NONE
## The slot the last save or load touched (-1 = none).
var last_slot := -1


func _init(menu_mode: Mode = Mode.SAVE, save_system: Node = null, ids: Array[int] = []) -> void:
	mode = menu_mode
	saves = save_system
	slot_ids = ids.duplicate()


## The slot ids a menu lists: the autosave slot, then `manual_slots` manual slots.
static func default_slot_ids(manual_slots: int) -> Array[int]:
	var ids: Array[int] = [SaveSystem.AUTOSAVE_SLOT]
	for i in manual_slots:
		ids.append(SaveSystem.AUTOSAVE_SLOT + 1 + i)
	return ids


## Re-reads every slot from disk. Keeps the cursor on the same row.
func refresh() -> void:
	slots.clear()
	for d: Dictionary in saves.call(&"list_slots", slot_ids) as Array:
		slots.append(SaveSlotInfo.from_dict(d))
	cursor = clampi(cursor, 0, maxi(slots.size() - 1, 0))
	changed.emit()


## Puts the cursor on the first usable row (the newest record when loading).
func place_initial_cursor() -> void:
	cursor = 0
	if mode == Mode.LOAD:
		var newest := -1
		for i in slots.size():
			if slots[i].is_loadable() and (newest < 0 or slots[i].saved_at > slots[newest].saved_at):
				newest = i
		cursor = maxi(newest, 0)
	else:
		for i in slots.size():
			if is_usable(i):
				cursor = i
				break
	changed.emit()


func current() -> SaveSlotInfo:
	return slots[cursor] if cursor >= 0 and cursor < slots.size() else null


func is_usable(index: int) -> bool:
	if index < 0 or index >= slots.size():
		return false
	var s := slots[index]
	if mode == Mode.SAVE:
		return not s.is_autosave()
	return s.is_loadable()


## The help line for the current row: a loc key per mode and slot status.
func help_key() -> String:
	var s := current()
	if s == null:
		return ""
	if mode == Mode.SAVE and s.is_autosave():
		return "SAVE_HELP_AUTOSAVE_LOCKED"
	var keys := SAVE_HELP_KEYS if mode == Mode.SAVE else LOAD_HELP_KEYS
	return str(keys.get(s.status, ""))


## Moves the cursor (BROWSE) or the dialog choice (CONFIRM). Wraps. Returns true if it moved.
func move(delta: int) -> bool:
	if phase == Phase.CONFIRM or phase == Phase.RESULT:
		var n := dialog_choices().size()
		if n <= 1:
			return false
		dialog_cursor = posmod(dialog_cursor + delta, n)
		changed.emit()
		return true
	if phase != Phase.BROWSE or slots.size() <= 1:
		return false
	cursor = posmod(cursor + delta, slots.size())
	last_outcome = Outcome.MOVED
	changed.emit()
	return true


func set_cursor(index: int) -> void:
	if phase == Phase.BROWSE and index >= 0 and index < slots.size():
		cursor = index
		changed.emit()


## Choice ids of the open dialog: CONFIRM = [no, yes] ("Keep it" first and default), RESULT = [continue].
func dialog_choices() -> Array[StringName]:
	if phase == Phase.CONFIRM:
		return [CHOICE_NO, CHOICE_YES]
	if phase == Phase.RESULT:
		return [CHOICE_CONTINUE]
	return []


func accept() -> Outcome:
	match phase:
		Phase.BROWSE:
			return _finish(_accept_slot())
		Phase.CONFIRM:
			var yes := dialog_choices()[dialog_cursor] == CHOICE_YES
			_close_dialog()
			return _finish(_write(cursor) if yes else Outcome.KEPT)
		Phase.RESULT:
			var was_success := last_outcome == Outcome.SAVED
			_close_dialog()
			if was_success:
				phase = Phase.CLOSED
				return _finish(Outcome.CLOSED)
			return _finish(Outcome.NONE)
	return Outcome.NONE


## Back out one step: a dialog closes (keeping the record), a result is dismissed, the list closes.
func cancel() -> Outcome:
	match phase:
		Phase.CONFIRM:
			_close_dialog()
			return _finish(Outcome.KEPT)
		Phase.RESULT:
			return accept()
		Phase.BROWSE:
			phase = Phase.CLOSED
			return _finish(Outcome.CLOSED)
	return Outcome.NONE


func _accept_slot() -> Outcome:
	var s := current()
	if s == null or not is_usable(cursor):
		return Outcome.REFUSED
	if mode == Mode.LOAD:
		last_slot = s.slot
		last_error = int(saves.call(&"load_into_game", s.slot)) as Error
		if last_error == OK:
			phase = Phase.CLOSED
			return Outcome.LOADED
		_open_dialog(Phase.RESULT, "LOAD_FAILED")
		refresh()
		return Outcome.LOAD_FAILED
	if s.has_file():
		var key := "SAVE_CONFIRM_OVERWRITE"
		if s.status == SaveSystem.STATUS_CORRUPT:
			key = "SAVE_CONFIRM_OVERWRITE_CORRUPT"
		elif s.status == SaveSystem.STATUS_NEWER:
			key = "SAVE_CONFIRM_OVERWRITE_NEWER"
		_open_dialog(Phase.CONFIRM, key)
		return Outcome.ASK_OVERWRITE
	return _write(cursor)


func _write(index: int) -> Outcome:
	var s := slots[index]
	last_slot = s.slot
	last_error = int(saves.call(&"save_to_slot", s.slot, Game.state, SaveSystem.REASON_MANUAL, extra_meta)) as Error
	refresh()
	if last_error == OK:
		_open_dialog(Phase.RESULT, "SAVE_DONE")
		return Outcome.SAVED
	_open_dialog(Phase.RESULT, "SAVE_FAILED")
	return Outcome.SAVE_FAILED


func _open_dialog(p: Phase, key: String) -> void:
	phase = p
	dialog_key = key
	dialog_cursor = 0


func _close_dialog() -> void:
	phase = Phase.BROWSE
	dialog_key = ""
	dialog_cursor = 0


func _finish(o: Outcome) -> Outcome:
	if o != Outcome.NONE:
		last_outcome = o
	changed.emit()
	return o
