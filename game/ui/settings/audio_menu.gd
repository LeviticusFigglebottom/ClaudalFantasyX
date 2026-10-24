class_name AudioMenu
extends SettingsPage
## The Audio settings page (M3-UI-02; SPEC §6.11): a SettingsPage over AudioMenuModel (master,
## music, effects and voice volume, and the Audio track's other sound settings). Each step applies
## at once (AudioDirector follows UiSettings) and saves. Opened from the Settings hub.
## Layout: game/data/ui/graphics_menu.json.

var model: AudioMenuModel


## `with_settings` defaults to UiSettings.shared(); `save_path` "" saves nothing (tests).
func _init(with_settings: UiSettings = null, save_path: String = UiSettings.CONFIG_PATH) -> void:
	model = AudioMenuModel.new(with_settings, save_path)
	page_model = model
	ui_settings = model.settings
	name = &"AudioMenu"
