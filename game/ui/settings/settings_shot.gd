class_name SettingsShot
extends Control
## Capture driver for the settings shots (M2-UI-09, tests/screenshots/shots.json). It opens the
## Settings hub on its own UiSettings at the defaults, so the player's settings.cfg never moves a
## baseline, and saves nothing:
##   - "hub": the hub, the cursor on Accessibility;
##   - "accessibility": the Accessibility page with the text size at 130%, the cursor on Text size
##     (the page re-themes itself, so the shot shows the larger text the setting gives);
##   - "controls" (M2-UI-13): the Controls page at the default bindings, listening for a new
##     Confirm key (the wait mark in the keyboard column and the listening help line).

## Which view to stage: &"hub", &"accessibility" or &"controls".
@export var view: StringName = &"hub"

var hub: SettingsMenu


func _ready() -> void:
	var settings := UiSettings.new()
	UiSettings.set_shared(settings)
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	hub = SettingsMenu.new()
	hub.ui_settings = settings
	hub.save_path = ""
	add_child(hub)
	_go_to(SettingsMenu.ROW_ACCESSIBILITY)  # by id: the hub's rows depend on the data (Audio, M3-UI-02)
	if view == &"controls":
		_stage_controls()
	if view != &"accessibility":
		return
	hub.handle_input(_ev(&"ui_accept"))
	hub.handle_input(_ev(&"ui_down"))  # Reduced motion -> Text size
	hub.handle_input(_ev(&"ui_right"))  # 115%
	hub.handle_input(_ev(&"ui_right"))  # 130%


func _stage_controls() -> void:
	_go_to(SettingsMenu.ROW_CONTROLS)
	hub.handle_input(_ev(&"ui_accept"))
	var page := hub.page as ControlsMenu
	page.model.set_cursor(page.model.row_ids().find(&"ui_accept"))
	hub.handle_input(_ev(&"ui_accept"))  # listen for a new Confirm key


## Steps the hub's cursor down to `row`.
func _go_to(row: StringName) -> void:
	for i in hub.row_ids().size():
		if hub.current() == row:
			return
		hub.handle_input(_ev(&"ui_down"))


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
