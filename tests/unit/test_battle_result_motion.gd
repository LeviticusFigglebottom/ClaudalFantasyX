extends TestCase
## The battle result's pacing (the "parts look primitive" pass): the panel opens, each fighter's row arrives in
## turn, then the choices; the whole open ends inside a capture's settle frames; Reduced motion shows the rows and
## choices at once.

## capture.sh runs the capture at --fixed-fps 60.
const CAPTURE_FPS := 60.0
const ROWS: Array[Dictionary] = [
	{"label": "Rhen", "xp": 12, "moves": 1},
	{"label": "Asha", "xp": 12, "moves": 1},
	{"label": "Toma", "xp": 12, "moves": 0}
]
const CHOICES: Array[Dictionary] = [{"id": &"continue", "label": "Continue", "enabled": true}]

var panel: BattleResultPanel
var _saved_settings: UiSettings


func before_each() -> void:
	_saved_settings = UiSettings.shared()
	UiSettings.set_shared(UiSettings.new())
	panel = BattleResultPanel.new()
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(panel)


func test_the_rows_arrive_in_turn_then_the_choices() -> void:
	panel.show_result(&"victory", "Victory", "", ROWS, CHOICES)
	var list := _list()
	assert_eq(list.get_child_count(), ROWS.size())
	for row in list.get_children():
		assert_eq((row as CanvasItem).modulate.a, 0.0, "each row waits its turn")
	assert_true(panel.open_duration() < float(_settle()) / CAPTURE_FPS, "the open ends before a capture's settle")
	panel.finish_open()
	for row in list.get_children():
		assert_eq((row as CanvasItem).modulate.a, 1.0, "all in")
	_done()


func test_reduced_motion_shows_the_rows_at_once() -> void:
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	panel.show_result(&"victory", "Victory", "", ROWS, CHOICES)
	for row in _list().get_children():
		assert_eq((row as CanvasItem).modulate.a, 1.0, "no stagger")
	_done()


func _list() -> VBoxContainer:
	return panel.get(&"_list") as VBoxContainer


func _settle() -> int:
	var shots := JSON.parse_string(FileAccess.get_file_as_string("res://tests/screenshots/shots.json")) as Dictionary
	return int((shots["defaults"] as Dictionary)["settle_frames"])


func _done() -> void:
	panel.get_parent().remove_child(panel)
	panel.free()
	UiSettings.set_shared(_saved_settings)
