extends TestCase
## M2-UI-17/19: the objective line and the destination cue. The line is driven by advance() on a
## scratch flag set (Game untouched); the cue's placement is the pure place() over synthetic
## screen points.

const HALUNA := &"ch02/haluna"

var flags: Dictionary = {}
var hud: ObjectiveHud
var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	(Engine.get_main_loop() as SceneTree).paused = false
	UiSettings.set_shared(UiSettings.new())
	flags = {&"ch02_met_asha": true, &"ch02_tideline_won": true, &"ch02_ate_at_nemes": true}
	hud = ObjectiveHud.new()
	hud.tracker = ObjectiveTracker.new(func(f: StringName) -> bool: return bool(flags.get(f, false)))
	hud.zone = HALUNA
	_add(hud)


func test_it_shows_once_when_the_field_first_takes_input_then_fades() -> void:
	var d := ObjectiveHud.load_data()
	assert_false(hud.is_showing())
	hud.advance(0.0)
	assert_true(hud.is_showing(), "first allowed frame: the objective slides in")
	assert_eq(hud.line_text(), tr("OBJ_SAVE_AT_SHRINE"))
	hud.advance(float(d["in_sec"]) + 0.01)
	hud.advance(float(d["hold_sec"]) + 0.01)
	assert_eq(hud.phase, ObjectiveHud.Phase.OUT)
	hud.advance(float(d["out_sec"]) + 0.01)
	assert_false(hud.is_showing(), "then it fades away")
	_done()


func test_the_line_has_height_and_wraps_inside_the_panel() -> void:
	hud.advance(0.0)
	var line: Label = hud._line
	assert_true(line.get_line_count() >= 1)
	assert_true(line.get_minimum_size().y >= line.get_line_height(), "the line asks for its height")
	var panel: PanelContainer = hud._panel
	assert_true(panel.get_combined_minimum_size().y <= panel.size.y, "the panel holds every line")
	_done()


func test_a_new_objective_shows_and_on_demand_shows_again() -> void:
	hud.advance(100.0)
	hud.advance(100.0)
	hud.advance(100.0)
	assert_false(hud.is_showing())
	flags[&"ch02_saved_once"] = true
	EventBus.flag_changed.emit(&"ch02_saved_once", true)
	assert_true(hud.is_showing(), "the objective changed")
	assert_eq(hud.line_text(), tr("OBJ_TO_CAUSEWAY_HEAD"))
	hud.advance(100.0)
	hud.advance(100.0)
	hud.advance(100.0)
	var ev := InputEventAction.new()
	ev.action = ObjectiveHud.ACTION
	ev.pressed = true
	hud._unhandled_input(ev)
	assert_true(hud.is_showing(), "the button brings it back")
	_done()


func test_it_hides_in_cutscenes_and_menus_and_waits_for_them() -> void:
	var c := FieldController.new()
	made.append(c)
	hud.controller = c
	c.accepts_input = false
	hud.advance(0.0)
	assert_false(hud.is_showing(), "a cutscene holds the field: no line")
	flags[&"ch02_saved_once"] = true
	EventBus.flag_changed.emit(&"ch02_saved_once", true)
	assert_false(hud.is_showing(), "still held")
	c.accepts_input = true
	hud.advance(0.0)
	assert_true(hud.is_showing(), "the new objective shows once the field is back")
	(Engine.get_main_loop() as SceneTree).paused = true
	hud.advance(0.1)
	assert_false(hud.is_showing(), "a menu pauses the tree: hidden")
	(Engine.get_main_loop() as SceneTree).paused = false
	hud.controller = null
	_done()


func test_the_action_is_remappable() -> void:
	ObjectiveHud.ensure_action()
	assert_true(InputMap.has_action(ObjectiveHud.ACTION))
	var ids: Array = []
	for a: Dictionary in (ControlsModel.load_data() as Dictionary).get("actions", []):
		ids.append(str(a.get("id", "")))
	assert_true(ids.has(String(ObjectiveHud.ACTION)), "on the Controls page")
	_done()


func test_the_target_is_the_poi_in_this_zone_only() -> void:
	assert_eq(hud.target_position(), Vector3(-67.0, 0.0, 44.3), "the save shrine")
	hud.zone = &"ch03/shell_shrine"
	assert_ne(hud.target_position(), Vector3(-67.0, 0.0, 44.3))
	hud.zone = HALUNA
	_done()


func test_the_cue_marks_on_screen_and_points_from_the_edge() -> void:
	var cue := hud.cue
	var size := Vector2(1920, 1080)
	var from := Vector3.ZERO
	var far := Vector3(100, 0, 0)
	var on := cue.place(false, Vector2(960, 400), size, from, far)
	assert_true(on["visible"] and on["on_screen"])
	assert_eq(on["words"], tr("OBJ_CUE_FAR"))
	var right := cue.place(false, Vector2(5000, 540), size, from, far)
	assert_false(right["on_screen"])
	var edge := float((ObjectiveHud.load_data()["cue"] as Dictionary)["edge_px"])
	assert_true(is_equal_approx((right["at"] as Vector2).x, size.x - edge), "clamped to the right edge")
	assert_true(absf(float(right["angle"])) < 0.01, "pointing right")
	var behind := cue.place(true, Vector2(1200, 540), size, from, far)
	assert_true((behind["at"] as Vector2).x < size.x * 0.5, "behind the camera: the arrow flips")
	assert_false(cue.place(false, Vector2(960, 540), size, from, Vector3(2, 0, 0))["visible"], "near: hidden")
	assert_eq(cue.distance_words(30.0), tr("OBJ_CUE_WALK"))
	UiSettings.shared().set_value(UiSettings.OBJECTIVE_CUE, false)
	cue.refresh()
	assert_false(cue.placement["visible"], "the setting turns it off")
	_done()


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


func _done() -> void:
	UiSettings.set_shared(null)
