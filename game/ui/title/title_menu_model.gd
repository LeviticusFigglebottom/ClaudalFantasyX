class_name TitleMenuModel
extends RefCounted
## Logic of the minimal title menu (M1-ARC-06): Continue / New Game / Load, no nodes.
## Continue and Load need a readable record (TitleSaveEntry.can_continue); New Game always works.
## The cursor starts on Continue when it is available, otherwise on New Game, and skips rows that
## are not available. Every row has a help line, including why a row is unavailable (pillar 4).

signal changed

const CHOICE_CONTINUE := &"continue"
const CHOICE_NEW_GAME := &"new_game"
const CHOICE_LOAD := &"load"
const CHOICES: Array[StringName] = [CHOICE_CONTINUE, CHOICE_NEW_GAME, CHOICE_LOAD]
const LABEL_KEYS := {
	CHOICE_CONTINUE: "TITLE_CONTINUE",
	CHOICE_NEW_GAME: "TITLE_NEW_GAME",
	CHOICE_LOAD: "TITLE_LOAD",
}
const HELP_KEYS := {
	CHOICE_CONTINUE: "TITLE_HELP_CONTINUE",
	CHOICE_NEW_GAME: "TITLE_HELP_NEW_GAME",
	CHOICE_LOAD: "TITLE_HELP_LOAD",
}
const HELP_NO_RECORD_KEY := "TITLE_HELP_NO_RECORD"

var save_system: Node
var cursor := 0
var has_record := false


func _init(saves: Node = null) -> void:
	save_system = saves
	refresh()


## Re-reads the slots (after a load menu closes, a record may have appeared or broken).
func refresh() -> void:
	has_record = TitleSaveEntry.can_continue(save_system)
	if not is_enabled(CHOICES[cursor]):
		cursor = initial_cursor()
	changed.emit()


func initial_cursor() -> int:
	return CHOICES.find(CHOICE_CONTINUE) if has_record else CHOICES.find(CHOICE_NEW_GAME)


func is_enabled(choice: StringName) -> bool:
	return choice == CHOICE_NEW_GAME or has_record


func current() -> StringName:
	return CHOICES[cursor]


## Moves to the next available row, wrapping. Returns true if the cursor moved.
func move(delta: int) -> bool:
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
	if index < 0 or index >= CHOICES.size() or not is_enabled(CHOICES[index]):
		return false
	cursor = index
	changed.emit()
	return true


## The chosen row's id, or &"" when it is unavailable.
func accept() -> StringName:
	return current() if is_enabled(current()) else &""


func label_key(choice: StringName) -> String:
	return str(LABEL_KEYS.get(choice, ""))


## The help line: what the row does, or (with no record yet) that Continue and Load are waiting
## for one, so a greyed row is never a mystery.
func help_key() -> String:
	if not has_record:
		return HELP_NO_RECORD_KEY
	return str(HELP_KEYS.get(current(), ""))
