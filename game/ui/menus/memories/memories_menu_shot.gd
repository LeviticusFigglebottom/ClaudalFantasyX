class_name MemoriesMenuShot
extends Control
## Capture driver for the Memories gallery (M3-MNU-02, tests/screenshots/shots.json). It opens
## MemoriesMenu on a fixed scratch record, so the player's saves never move a baseline: the
## prologue, two of Ch1's three memories and one of Ch2's two are remembered, Ch3's none (so Ch3 is
## not named). The cursor rests on Chapter 1's "The Rising", as when a replay of it has just ended.

const REMEMBERED: Array[StringName] = [
	&"prologue_seen", &"ch01_kell_side_scene", &"ch01_hullgnaw_defeated", &"ch02_met_asha"
]
const ON_MEMORY := &"ch01_the_rising"

var menu: MemoriesMenu


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var record := GameStateData.new()
	for f in REMEMBERED:
		record.flags[String(f)] = true
	var records: Array[GameStateData] = [record]
	menu = MemoriesMenu.create(MemoriesModel.new(MemoriesModel.load_data(), records), ON_MEMORY)
	menu.pause_tree = false
	menu.play_memory = func(_id: StringName) -> void: pass
	add_child(menu)
