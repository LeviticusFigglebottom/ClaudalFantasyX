class_name AccessibilityMenu
extends SettingsPage
## The Accessibility settings page (M2-UI-09; SPEC §6.11): a SettingsPage over
## AccessibilityMenuModel (reduced motion, text size, color palette, timing assist). Every change
## saves at once, and every view following UiSettings (this page included) re-themes as it
## happens, so the page previews a text size or palette the moment it is chosen.
## The text speed and battle speed rows show a live preview beside the page (SpeedPreview).
## Opened from the Settings hub (SettingsMenu). Layout: game/data/ui/graphics_menu.json.

var model: AccessibilityMenuModel
var preview: SpeedPreview


## `with_settings` defaults to UiSettings.shared(); `save_path` "" saves nothing (tests).
func _init(with_settings: UiSettings = null, save_path: String = UiSettings.CONFIG_PATH) -> void:
	model = AccessibilityMenuModel.new(with_settings, save_path)
	page_model = model
	ui_settings = model.settings
	name = &"AccessibilityMenu"


func _ready() -> void:
	preview = SpeedPreview.new()
	preview.name = &"SpeedPreview"
	preview.setup(page_model.layout().get("speed_preview", {}) as Dictionary, ui_settings)
	super()
	add_child(preview)


func _render() -> void:
	super()
	if preview != null:
		preview.show_for(page_model.current())
