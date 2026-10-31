class_name KiteLogShot
extends Control
## Capture driver for the kite_log shot (M5-A3P-1703, tests/screenshots/shots.json): the Kite's log page on fixed
## Act III flags (every revisit on the chart; Oruvel, Corrow and Ansedra seen; Rhen's and Toma's heirlooms carried),
## the party in Haluna, the cursor on Oruvel, so the player's save never moves a baseline.

const FLAGS: Array[StringName] = [
	&"kite_flying",
	&"ch01_started",
	&"ch02_met_asha",
	&"ch05_arrived",
	&"ch07_arrived",
	&"ch08_arrived_corrow",
	&"ch10_reached_reedhollow",
	&"ch12_reached_quellan",
	&"ch13_started",
	&"ch14_declared_heretics",
	&"ch15_reached_hollowmere",
	&"ch18_pell_named",
	&"ch18_revisit_oruvel",
	&"ch18_revisit_corrow",
	&"ch18_revisit_ansedra",
	&"ch18_heirloom_rhen",
	&"ch18_heirloom_toma",
]
const HERE := &"ch02/haluna"
const CURSOR := &"oruvel"

var menu: KiteMapMenu


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var model := KiteMapModel.new(
		KiteMapModel.load_data(),
		func(f: StringName) -> Variant: return FLAGS.has(f),
		func(_f: StringName, _v: Variant) -> void: pass
	)
	model.here = HERE
	menu = KiteMapMenu.create(model)
	menu.pause_tree = false
	FieldSubmenu.mount(menu, self)
	menu.open_log()
	var at := 0
	for i in menu.rows_page().rows.size():
		if menu.rows_page().rows[i]["id"] == CURSOR:
			at = i
	menu.rows_page().set_cursor(at, false)
	menu.rows_page().row_hovered.emit(at)  # the line and the chart ring follow it
