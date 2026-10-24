extends TestCase
## M1-UI-11: with GraphicsRuntime armed, a preset change on the Graphics page spawns the resident
## shader warm-up, so it applies behind a veil: the page is inert until the warm-up is done, then the
## veil lifts. A TestCase cannot await, so the veil (GraphicsMenu.advance) and the warm-up
## (ShaderPrewarm.tick) are stepped by hand. The settings file and viewport are the test's own.

const CONFIG := "user://test_graphics_menu_apply.cfg"
const FRAME_SEC := 1.0 / 60.0
const FRAME_MS := 1000.0 / 60.0
const GUARD := 2000

var vp: SubViewport
var menu: GraphicsMenu


func before_each() -> void:
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CONFIG))
	GraphicsRuntime.config_path = CONFIG
	GraphicsRuntime.set_settings(null)
	GraphicsRuntime.armed = true
	vp = SubViewport.new()
	_host().add_child(vp)
	menu = GraphicsMenu.new(vp)
	_host().add_child(menu)


func _action(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


## Steps the veil until the preset has been selected (FADE_OUT, then the settle frame). Returns frames.
func _advance_until_selected(before: String) -> int:
	var frames := 0
	while GraphicsRuntime.settings().preset_id == before and frames < GUARD:
		menu.advance(FRAME_SEC)
		frames += 1
	return frames


func test_a_preset_change_waits_behind_the_veil_until_the_warmup_finishes() -> void:
	var before := GraphicsRuntime.settings().preset_id
	assert_eq(menu.model.current(), GraphicsMenuModel.ROW_PRESET)
	assert_true(menu.handle_input(_action(&"ui_right")))
	assert_true(menu.is_applying(), "the veil goes up")
	assert_eq(GraphicsRuntime.settings().preset_id, before, "nothing applies before the screen is covered")
	assert_true(menu.model.warmup == null, "no warm-up tracked")
	_advance_until_selected(before)
	assert_ne(GraphicsRuntime.settings().preset_id, before, "the preset applied behind the veil")
	assert_eq(menu.veil_alpha(), 1.0, "under a fully opaque veil")
	var warmup := menu.model.warmup
	assert_true(is_instance_valid(warmup), "select_preset spawned the resident warm-up")
	assert_eq(warmup.get_parent(), vp)
	assert_true(warmup.resident_only)
	assert_eq(menu.card_text(), tr("GFX_MENU_APPLYING"))
	var chosen := GraphicsRuntime.settings().preset_id
	# Inert while the warm-up lives: frames pass, input and clicks change nothing, cancel doesn't close.
	for _i in 30:
		menu.advance(FRAME_SEC)
	assert_true(menu.is_applying())
	assert_eq(menu.veil_alpha(), 1.0, "held while the warm-up lives")
	assert_true(menu.handle_input(_action(&"ui_down")), "input is swallowed")
	assert_true(menu.handle_input(_action(&"ui_right")))
	assert_true(menu.handle_input(_action(&"ui_cancel")))
	menu.close()
	menu._on_row_clicked(0)
	assert_eq(menu.model.cursor, 0, "the cursor did not move")
	assert_eq(GraphicsRuntime.settings().preset_id, chosen, "no second preset change")
	assert_true(menu.is_open(), "cancel waits too")
	# The warm-up runs to its end (finished, then queue_free).
	var done := [false]
	warmup.finished.connect(func(_s: Dictionary) -> void: done[0] = true)
	var ticks := 0
	while not done[0] and ticks < GUARD:
		warmup.tick(FRAME_MS)
		menu.advance(FRAME_SEC)
		ticks += 1
		if not done[0]:
			assert_eq(menu.veil_alpha(), 1.0, "still held at warm-up frame %d" % ticks)
	assert_true(done[0], "the warm-up finished")
	_lift_and_check(chosen)


func test_the_veil_lifts_when_the_warmup_node_frees() -> void:
	var before := GraphicsRuntime.settings().preset_id
	menu.handle_input(_action(&"ui_left"))
	_advance_until_selected(before)
	var warmup := menu.model.warmup
	assert_true(is_instance_valid(warmup))
	menu.advance(FRAME_SEC)
	assert_true(menu.is_applying())
	assert_true(menu.handle_input(_action(&"ui_down")))
	assert_eq(menu.model.cursor, 0, "inert while it lives")
	warmup.get_parent().remove_child(warmup)
	warmup.free()
	_lift_and_check(GraphicsRuntime.settings().preset_id)


func test_a_setting_row_spawns_no_warmup_and_no_veil() -> void:
	var prior := GraphicsRuntime.last_warmup
	var prior_id := prior.get_instance_id() if is_instance_valid(prior) else 0
	menu.model.set_cursor(menu.model.row_ids().find(&"ssr"))
	var before: Variant = GraphicsRuntime.settings().resolve()["ssr"]
	assert_true(menu.handle_input(_action(&"ui_right")))
	assert_ne(GraphicsRuntime.settings().resolve()["ssr"], before, "applied at once")
	assert_false(menu.is_applying(), "no veil for a setting row")
	var now := GraphicsRuntime.last_warmup
	assert_eq(now.get_instance_id() if is_instance_valid(now) else 0, prior_id, "no warm-up spawned")
	assert_true(menu.model.warmup == null, "no warm-up tracked")
	_done()


func _lift_and_check(chosen: String) -> void:
	menu.advance(FRAME_SEC)
	assert_true(menu.model.warmup_done())
	var frames := 0
	while menu.is_applying() and frames < GUARD:
		menu.advance(FRAME_SEC)
		frames += 1
	assert_false(menu.is_applying(), "the veil lifted")
	assert_eq(menu.veil_alpha(), 0.0)
	assert_eq(menu.card_text(), "")
	assert_eq(GraphicsRuntime.settings().preset_id, chosen)
	assert_true(menu.handle_input(_action(&"ui_down")))
	assert_eq(menu.model.cursor, 1, "the page takes input again")
	_done()


func _done() -> void:
	if is_instance_valid(menu) and is_instance_valid(menu.model.warmup):
		menu.model.warmup.free()
	if is_instance_valid(menu):
		if menu.get_parent() != null:
			menu.get_parent().remove_child(menu)
		menu.free()
	if is_instance_valid(vp):
		vp.get_parent().remove_child(vp)
		vp.free()
	GraphicsRuntime.armed = false
	GraphicsRuntime.set_settings(null)
	GraphicsRuntime.config_path = GraphicsSettings.CONFIG_PATH
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CONFIG))


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root
