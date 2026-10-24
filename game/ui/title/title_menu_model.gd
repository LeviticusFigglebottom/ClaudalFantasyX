class_name TitleMenuModel
extends RefCounted
## Logic of the minimal title menu (M1-ARC-06): Continue / New Game / Load / Settings, no nodes.
## Continue and Load need a readable record (TitleSaveEntry.can_continue); New Game and Settings
## (the Graphics page, M1-UI-10) always work.
## The cursor starts on Continue when it is available, otherwise on New Game, and skips rows that
## are not available. Every row has a help line, including why a row is unavailable (pillar 4).
##
## New Game confirm (M1-ARC-08, ADR 0018): a new run's first chapter autosave writes over slot 0.
## When slot 0 holds a readable (or newer-build) autosave, New Game first asks: the rows become
## [Go back, Begin anew] with "Go back" first and the default, and the help line says what would
## be lost. Manual records are never touched by a new run.

signal changed

const CHOICE_CONTINUE := &"continue"
const CHOICE_NEW_GAME := &"new_game"
const CHOICE_LOAD := &"load"
const CHOICE_SETTINGS := &"settings"
const CHOICES: Array[StringName] = [CHOICE_CONTINUE, CHOICE_NEW_GAME, CHOICE_LOAD, CHOICE_SETTINGS]
const LABEL_KEYS := {
	CHOICE_CONTINUE: "TITLE_CONTINUE",
	CHOICE_NEW_GAME: "TITLE_NEW_GAME",
	CHOICE_LOAD: "TITLE_LOAD",
	CHOICE_SETTINGS: "TITLE_SETTINGS",
}
const HELP_KEYS := {
	CHOICE_CONTINUE: "TITLE_HELP_CONTINUE",
	CHOICE_NEW_GAME: "TITLE_HELP_NEW_GAME",
	CHOICE_LOAD: "TITLE_HELP_LOAD",
	CHOICE_SETTINGS: "TITLE_HELP_SETTINGS",
}
const HELP_NO_RECORD_KEY := "TITLE_HELP_NO_RECORD"
const CHOICE_CONFIRM_BACK := &"confirm_back"
const CHOICE_CONFIRM_BEGIN := &"confirm_begin"
## The New Game question's rows: "Go back" first, so the default keeps the old run's autosave.
const CONFIRM_CHOICES: Array[StringName] = [CHOICE_CONFIRM_BACK, CHOICE_CONFIRM_BEGIN]
const CONFIRM_LABEL_KEYS := {
	CHOICE_CONFIRM_BACK: "TITLE_CONFIRM_BACK",
	CHOICE_CONFIRM_BEGIN: "TITLE_CONFIRM_BEGIN",
}
const CONFIRM_HELP_KEY := "TITLE_CONFIRM_NEW_GAME"

var save_system: Node
var cursor := 0
var has_record := false
## True when slot 0 holds an autosave a new run would write over (TitleSaveEntry).
var autosave_at_risk := false
## True while the New Game question is open; confirm_cursor is its row.
var confirming := false
var confirm_cursor := 0


func _init(saves: Node = null) -> void:
	save_system = saves
	refresh()


## Re-reads the slots (after a load menu closes, a record may have appeared or broken).
func refresh() -> void:
	has_record = TitleSaveEntry.can_continue(save_system)
	autosave_at_risk = TitleSaveEntry.new_game_overwrites_autosave(save_system)
	if not is_enabled(CHOICES[cursor]):
		cursor = initial_cursor()
	changed.emit()


func initial_cursor() -> int:
	return CHOICES.find(CHOICE_CONTINUE) if has_record else CHOICES.find(CHOICE_NEW_GAME)


func is_enabled(choice: StringName) -> bool:
	if CONFIRM_CHOICES.has(choice):
		return confirming
	if confirming:
		return false
	return choice == CHOICE_NEW_GAME or choice == CHOICE_SETTINGS or has_record


func current() -> StringName:
	return CONFIRM_CHOICES[confirm_cursor] if confirming else CHOICES[cursor]


## The rows shown now: the title choices, or the New Game question's two rows.
func row_ids() -> Array[StringName]:
	return CONFIRM_CHOICES if confirming else CHOICES


## The cursor over row_ids().
func row_cursor() -> int:
	return confirm_cursor if confirming else cursor


## True when choosing New Game must ask first (see the class comment).
func needs_new_game_confirm() -> bool:
	return autosave_at_risk


## Opens the New Game question with the cursor on "Go back".
func begin_confirm() -> void:
	confirming = true
	confirm_cursor = CONFIRM_CHOICES.find(CHOICE_CONFIRM_BACK)
	changed.emit()


## Closes the question; the cursor is back on New Game.
func end_confirm() -> void:
	if not confirming:
		return
	confirming = false
	cursor = CHOICES.find(CHOICE_NEW_GAME)
	changed.emit()


## Moves to the next available row, wrapping. Returns true if the cursor moved.
func move(delta: int) -> bool:
	if confirming:
		confirm_cursor = posmod(confirm_cursor + delta, CONFIRM_CHOICES.size())
		changed.emit()
		return true
	var i := cursor
	for _n in CHOICES.size():
		i = posmod(i + delta, CHOICES.size())
		if is_enabled(CHOICES[i]):
			break
	if i == cursor:
		return false
	cursor = i
	changed.emit()
	return true


func set_cursor(index: int) -> bool:
	if confirming:
		if index < 0 or index >= CONFIRM_CHOICES.size():
			return false
		confirm_cursor = index
		changed.emit()
		return true
	if index < 0 or index >= CHOICES.size() or not is_enabled(CHOICES[index]):
		return false
	cursor = index
	changed.emit()
	return true


## The chosen row's id, or &"" when it is unavailable.
func accept() -> StringName:
	return current() if is_enabled(current()) else &""


func label_key(choice: StringName) -> String:
	return str(LABEL_KEYS.get(choice, CONFIRM_LABEL_KEYS.get(choice, "")))


## The help line: what the row does, or (with no record yet) that Continue and Load are waiting
## for one, so a greyed row is never a mystery.
func help_key() -> String:
	if confirming:
		return CONFIRM_HELP_KEY
	if not has_record and current() == CHOICE_NEW_GAME:
		return HELP_NO_RECORD_KEY
	return str(HELP_KEYS.get(current(), ""))
