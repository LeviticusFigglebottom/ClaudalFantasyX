extends TestCase
## M2-MNU-04: the battle pause. The pause action opens BattlePauseMenu over the HUD and pauses
## the whole tree; Resume, Cancel or the action again lift it; Quit asks first (Stay under the
## cursor) and then returns to the title; nothing pauses on the result panel or with no fight on.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"

var ctl: BattleController
var pauser: BattlePause


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	_root().add_child(ctl)
	ctl.hud.apply_settings(UiSettings.new())
	pauser = ctl.get_node("BattlePause") as BattlePause


func _teardown() -> void:
	FlowRouting.record = Callable()
	if pauser.menu != null:
		pauser.menu.close()
	ctl.get_tree().paused = false
	_root().remove_child(ctl)
	ctl.free()


func test_the_action_exists_and_nothing_pauses_before_a_fight() -> void:
	assert_true(InputMap.has_action(BattlePauseMenu.PAUSE_ACTION), "added at runtime")
	assert_false(pauser.can_pause(), "no fight on (idle)")
	assert_false(pauser.pause())
	_teardown()


func test_pause_freezes_the_tree_and_resume_lifts_it() -> void:
	_start()
	var tree := ctl.get_tree()
	pauser._unhandled_input(_ev(BattlePauseMenu.PAUSE_ACTION))
	assert_true(pauser.is_paused(), "the pause action opens the page")
	assert_true(tree.paused, "and the whole tree holds still")
	var page := pauser.menu
	assert_eq(page.rows_page().current_row()["id"], BattlePauseMenu.ROW_RESUME, "Resume first")
	assert_eq(page.desc_text(), tr("BATTLE_PAUSE_RESUME_DESC"))
	assert_false(pauser.pause(), "no second page")
	page.accept()
	assert_false(pauser.is_paused())
	assert_false(tree.paused, "Resume lifts it")
	assert_true(pauser.pause())
	assert_true(pauser.menu.handle_input(_ev(BattlePauseMenu.PAUSE_ACTION)), "the action again resumes")
	assert_false(tree.paused)
	assert_true(pauser.pause())
	assert_true(pauser.menu.handle_input(_ev(&"ui_cancel")), "so does Cancel")
	assert_false(tree.paused)
	_teardown()


func test_the_battle_does_not_move_while_paused() -> void:
	_start()
	var before := ctl.engine.current.id
	var state := ctl.state
	assert_true(pauser.pause())
	assert_false(ctl.is_processing() and ctl.can_process(), "the controller is frozen")
	assert_eq(ctl.engine.current.id, before)
	assert_eq(ctl.state, state)
	_teardown()


func test_quit_asks_first_then_returns_to_the_title() -> void:
	var went: Array = []
	FlowRouting.record = func(args: Array) -> void: went.append(args)
	_start()
	assert_true(pauser.pause())
	var page := pauser.menu
	page.handle_input(_ev(&"ui_down"))
	page.handle_input(_ev(&"ui_down"))
	assert_eq(page.rows_page().current_row()["id"], BattlePauseMenu.ROW_QUIT)
	page.accept()
	assert_eq(page.level, BattlePauseMenu.Level.QUIT)
	assert_eq(page.rows_page().current_row()["id"], FieldMenuModel.QUIT_STAY, "Stay first")
	page.handle_input(_ev(&"ui_cancel"))
	assert_eq(page.level, BattlePauseMenu.Level.ROOT, "Cancel backs out of the question")
	assert_eq(page.rows_page().current_row()["id"], BattlePauseMenu.ROW_QUIT, "onto Quit")
	assert_true(pauser.is_paused(), "still paused")
	page.accept()
	page.handle_input(_ev(&"ui_down"))
	assert_eq(page.desc_text(), tr("FIELD_MENU_QUIT_WARN"))
	page.accept()
	assert_false(pauser.is_paused())
	assert_false(ctl.get_tree().paused)
	assert_eq(went, [[FieldMenu.TITLE_SCENE]])
	_teardown()


func test_settings_opens_over_the_pause_and_hands_back() -> void:
	_start()
	assert_true(pauser.pause())
	var page := pauser.menu
	page.handle_input(_ev(&"ui_down"))
	page.accept()
	assert_true(page.settings_menu != null and page.settings_menu.is_open())
	assert_false(page.visible)
	assert_false(page.handle_input(_ev(&"ui_down")), "the hub takes the input")
	page.settings_menu.close()
	assert_true(page.visible)
	assert_true(ctl.get_tree().paused, "still paused under the page")
	_teardown()


func test_no_pause_on_the_result_panel() -> void:
	_start()
	ctl.state = BattleController.STATE_RESULT
	assert_false(pauser.can_pause())
	ctl.state = BattleController.STATE_COMMAND
	assert_true(pauser.can_pause())
	ctl.get_tree().paused = true
	assert_false(pauser.can_pause(), "another menu holds the pause")
	ctl.get_tree().paused = false
	_teardown()


func _start() -> void:
	ctl.start_fixture(BattleFixture.load_fixture(&"read_panel"))


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
