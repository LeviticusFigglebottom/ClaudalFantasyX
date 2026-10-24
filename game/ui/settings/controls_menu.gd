class_name ControlsMenu
extends SettingsPage
## The Controls settings page (M2-UI-13, SPEC §6.11; tech/ui.md § Controls): a SettingsPage over
## ControlsModel. The first row and Left / Right pick the column Confirm rebinds (keyboard or pad);
## Confirm (or a click) on an action listens for the next key or pad button; Confirm on the last
## row resets every binding. While it listens the page is busy (SettingsPage.is_busy): every event
## goes to the model's feed, so a rebound ui_cancel or ui_accept cannot interfere, and keyboard
## Escape, pad B or a mouse click backs out. The page cannot close while it listens.
## Usable by keyboard alone, pad alone (both column choice and listening) and mouse (click the
## column row to switch, click an action to listen, click anywhere to stop listening).
## Opened from the Settings hub (SettingsMenu). Layout: game/data/ui/graphics_menu.json.

var model: ControlsModel


## `save_path` "" saves nothing (tests, captures).
func _init(save_path: String = UiSettings.CONFIG_PATH) -> void:
	model = ControlsModel.new(save_path)
	page_model = model
	name = &"ControlsMenu"


func is_busy() -> bool:
	return model.is_listening()


## While listening every event goes to the model (and is used); otherwise Confirm activates the
## row, and the rest is SettingsPage's (Up / Down move, Left / Right switch the column, Cancel closes).
func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if model.is_listening():
		model.feed(event)
		return true
	if event.is_action_pressed(&"ui_accept"):
		model.activate()
		return true
	return super(event)


func _gui_input(event: InputEvent) -> void:
	if model.is_listening() and event is InputEventMouseButton and event.is_pressed():
		model.cancel_listen()
		accept_event()


func _render() -> void:
	super()
	_help.text = model.help_text()


func _on_row_hovered(index: int) -> void:
	if not model.is_listening():
		super(index)


func _on_row_clicked(index: int) -> void:
	if model.is_listening():
		model.cancel_listen()
	elif model.cursor == index:
		model.activate()
	else:
		model.set_cursor(index)
