extends TestCase
## The battle result's pacing (the "parts look primitive" pass): the panel opens, each fighter's row arrives in
## turn, then the choices; the whole open ends inside the victory capture's settle frames; Reduced motion shows the
## rows and choices at once. The numbers count up as their rows arrive (M3-BPR-415's panel: EXP, movement, lume and
## drops), eased; the first Confirm while they count shows them all instead of choosing.

## capture.sh runs the capture at --fixed-fps 60.
const CAPTURE_FPS := 60.0
const ROWS: Array[Dictionary] = [
	{
		"label": "Rhen",
		"xp_text": "+12 XP",
		"count": [{"cell": "xp", "key": "HUD_RESULT_XP_FMT", "arg": "xp", "n": 12}],
	},
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


func test_the_numbers_count_up_and_confirm_skips_the_count_first() -> void:
	var chosen: Array[StringName] = []
	panel.choice_made.connect(func(c: StringName) -> void: chosen.append(c))
	panel.show_result(&"victory", "Victory", "", ROWS, CHOICES)
	var xp := _xp_cell(0)
	assert_eq(xp.text, tr("HUD_RESULT_XP_FMT").format({"xp": 0}), "it starts from nothing")
	assert_true(panel.is_counting())
	panel.handle_input(_ev(&"ui_accept"))
	assert_true(chosen.is_empty(), "the first Confirm only skips the count")
	assert_eq(xp.text, tr("HUD_RESULT_XP_FMT").format({"xp": 12}), "every number at once")
	assert_false(panel.is_counting())
	panel.handle_input(_ev(&"ui_accept"))
	assert_eq(chosen, [&"continue"] as Array[StringName], "the next one chooses")
	_done()


## act1_gpu_qa row 33: a result left (or shown again) while it still counts never writes into freed rows.
func test_a_count_never_writes_into_freed_rows() -> void:
	panel.show_result(&"victory", "Victory", "", ROWS, CHOICES)
	var first := panel.get(&"_open_tween") as Tween
	var row := _xp_cell(0)
	panel.show_result(&"victory", "Victory", "", ROWS, CHOICES)
	assert_false(first.is_valid(), "the last open's tween is killed with its rows")
	row.free()
	# A freed row is skipped, not cast (the runner fails the test on a script error).
	panel.call(&"_set_count", 5.0, {"label": row, "key": "HUD_RESULT_XP_FMT", "arg": "xp", "n": 12})
	panel.finish_open()
	assert_false(panel.is_counting(), "the new open ends at rest")
	_done()


func test_reduced_motion_shows_the_final_numbers_at_once() -> void:
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	panel.show_result(&"victory", "Victory", "", ROWS, CHOICES)
	assert_eq(_xp_cell(0).text, "+12 XP", "no count")
	assert_false(panel.is_counting())
	_done()


func _xp_cell(row: int) -> Label:
	return _list().get_child(row).get_child(2) as Label  # after the picture and the name


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _list() -> VBoxContainer:
	return panel.get(&"_list") as VBoxContainer


## The victory shot's settle frames (its own, else the manifest default).
func _settle() -> int:
	var shots := JSON.parse_string(FileAccess.get_file_as_string("res://tests/screenshots/shots.json")) as Dictionary
	for shot: Variant in shots["shots"]:
		if str((shot as Dictionary)["id"]) == "battle_victory" and (shot as Dictionary).has("settle_frames"):
			return int(shot["settle_frames"])
	return int((shots["defaults"] as Dictionary)["settle_frames"])


func _done() -> void:
	panel.get_parent().remove_child(panel)
	panel.free()
	UiSettings.set_shared(_saved_settings)
