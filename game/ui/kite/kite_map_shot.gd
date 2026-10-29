class_name KiteMapShot
extends Control
## Capture driver for the kite_map shot (M3-UI-205, tests/screenshots/shots.json): the Kite's world map
## on fixed flags (every Act I place it can land at, the party in Haluna), the cursor on Tamsule, so the
## player's save never moves a baseline.

const FLAGS: Array[StringName] = [
	&"kite_flying", &"ch02_met_asha", &"ch05_arrived", &"ch07_arrived", &"ch08_arrived_corrow"
]
const HERE := &"ch02/haluna"
const CURSOR := &"tamsule"

var menu: KiteMapMenu


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var model := fixed_model()
	menu = KiteMapMenu.create(model)
	menu.pause_tree = false
	FieldSubmenu.mount(menu, self)
	menu.rows_page().set_cursor(model.ids().find(CURSOR), false)
	menu.rows_page().row_hovered.emit(model.ids().find(CURSOR))  # the line and the chart ring follow it


## The shot's model: kite.json on FLAGS, standing in HERE; it flies nowhere and writes no flag.
static func fixed_model() -> KiteMapModel:
	var model := KiteMapModel.new(
		KiteMapModel.load_data(),
		func(f: StringName) -> Variant: return FLAGS.has(f),
		func(_f: StringName, _v: Variant) -> void: pass
	)
	model.here = HERE
	return model
