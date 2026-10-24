class_name GraphicsMenu
extends SettingsPage
## The Graphics settings page (M1-UI-10; graphics_settings.md, "The Graphics menu"): a
## SettingsPage over GraphicsMenuModel. Every change saves and applies at once (GraphicsRuntime).
## Opened from the Settings hub (SettingsMenu), which the title and the field menu open (M2-UI-09).
## Layout: game/data/ui/graphics_menu.json.

var model: GraphicsMenuModel


func _init(vp: Viewport = null) -> void:
	model = GraphicsMenuModel.new(vp)
	page_model = model
	name = &"GraphicsMenu"


func _ready() -> void:
	if model.viewport == null:
		model.viewport = get_viewport()
	super()
