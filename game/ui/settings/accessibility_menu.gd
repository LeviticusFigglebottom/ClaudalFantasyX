class_name AccessibilityMenu
extends SettingsPage
## The Accessibility settings page (M2-UI-09; SPEC §6.11): a SettingsPage over
## AccessibilityMenuModel (reduced motion, text size, color palette, timing assist). Every change
## saves at once, and every view following UiSettings (this page included) re-themes as it
## happens, so the page previews a text size or palette the moment it is chosen.
## Opened from the Settings hub (SettingsMenu). Layout: game/data/ui/graphics_menu.json.

var model: AccessibilityMenuModel


## `with_settings` defaults to UiSettings.shared(); `save_path` "" saves nothing (tests).
func _init(with_settings: UiSettings = null, save_path: String = UiSettings.CONFIG_PATH) -> void:
	model = AccessibilityMenuModel.new(with_settings, save_path)
	page_model = model
	ui_settings = model.settings
	name = &"AccessibilityMenu"
