class_name SettingsPageModel
extends RefCounted
## The logic every settings page shares (M2-UI-09), no nodes: a list of rows, each with a label
## and a value, a wrapping cursor, cycle() to step the value under it, and a help line for the
## row. GraphicsMenuModel and AccessibilityMenuModel extend it; SettingsPage is the view of either.
## Every change is saved and applied by the subclass's cycle() as it happens.

signal changed

## The controls line of a page of values (Up and Down, Left and Right, Cancel).
const CONTROLS_KEY := "SET_MENU_CONTROLS_PAGE"

var cursor := 0


## Override: the row ids in display order.
func row_ids() -> Array[StringName]:
	return []


## Override: the page title's loc key.
func title_key() -> String:
	return ""


## Override: the row's label, in words.
func label(_row: StringName) -> String:
	return ""


## Override: the row's value as shown.
func value_text(_row: StringName) -> String:
	return ""


## Override: steps the current row's value by `delta` (wrapping), saves and applies it. Returns
## true when the value changed.
func cycle(_delta: int) -> bool:
	return false


## Override: the help line's loc key for the current row.
func help_key() -> String:
	return ""


## The controls line under the help: how to move, change a value and go back ("" hides it).
func controls_key() -> String:
	return CONTROLS_KEY


## The layout (game/data/ui/graphics_menu.json: page metrics, help rect, backdrop); every settings
## page uses the same one, so they read as one family.
func layout() -> Dictionary:
	return GraphicsMenuModel.load_data()


func current() -> StringName:
	var ids := row_ids()
	return ids[clampi(cursor, 0, ids.size() - 1)] if not ids.is_empty() else &""


## Moves the cursor (wrapping). Returns true.
func move(delta: int) -> bool:
	var n := row_ids().size()
	if n == 0:
		return false
	cursor = posmod(cursor + delta, n)
	changed.emit()
	return true


func set_cursor(index: int) -> bool:
	if index < 0 or index >= row_ids().size():
		return false
	cursor = index
	changed.emit()
	return true
