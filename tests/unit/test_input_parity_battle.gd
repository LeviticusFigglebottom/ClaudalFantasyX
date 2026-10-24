extends TestCase
## M2-UI-26 (input parity): the battle's command menus and sub-menus, targeting (foes and allies,
## by the fighter or its party row), the Read panel, the result panel and the battle pause, each
## walked with the keyboard, the controller and the mouse through real InputEvents (InputDriver).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"

var ctl: BattleController
var resolved: Array[ActionResult] = []


func before_each() -> void:
	InputDriver.clear_screen()
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.hud.apply_settings(UiSettings.new())
	resolved.clear()


func test_attack_a_chosen_foe_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		_start(&"player_preview", &"rhen")
		_choose_root(d, BattleMenus.ROW_ATTACK)
		assert_eq(ctl.state, BattleController.STATE_TARGET, "%s: Attack asks for a target" % d.label())
		var first := ctl.picked_ids()[0]
		var other := _other_candidate(first)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover_at(_fighter_point(other))
		else:
			while ctl.picked_ids()[0] != other:
				d.press(&"ui_right")
		assert_eq(ctl.picked_ids(), [other] as Array[StringName], "%s: the cursor moves to the other foe" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click_at(_fighter_point(other))
		else:
			d.press(&"ui_accept")
		assert_true(_acted(&"rhen", other), "%s: Rhen attacks the chosen foe" % d.label())
		_free()
		before_each()
	_free()


func test_cancel_backs_out_of_a_sub_menu_and_the_target_pick() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		_start(&"player_preview", &"rhen")
		_choose_root(d, BattleMenus.ROW_SKILLS)
		assert_eq(ctl.hud.commands.depth(), 2, "%s: Skills opens its page" % d.label())
		_cancel(d)
		assert_eq(ctl.hud.commands.depth(), 1, "%s: Cancel goes back to the root" % d.label())
		assert_eq(ctl.state, BattleController.STATE_COMMAND)
		_choose_root(d, BattleMenus.ROW_SKILLS)
		_choose_row(d, &"quick_hit")
		assert_eq(ctl.state, BattleController.STATE_TARGET, "%s: a skill asks for a target" % d.label())
		_cancel(d)
		assert_eq(ctl.state, BattleController.STATE_SKILLS, "%s: Cancel goes back to the skills" % d.label())
		assert_true(ctl.candidate_ids().is_empty(), "%s: nothing is aimed at any more" % d.label())
		_cancel(d)
		assert_eq(ctl.state, BattleController.STATE_COMMAND, "%s: and on to the root" % d.label())
		assert_true(resolved.is_empty(), "%s: nothing was spent" % d.label())
		_free()
		before_each()
	_free()


func test_an_ally_is_chosen_by_fighter_or_party_row() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		_start(&"player_preview", &"asha")
		_choose_root(d, BattleMenus.ROW_SKILLS)
		_choose_row(d, &"mend")
		assert_eq(ctl.state, BattleController.STATE_TARGET, "%s: Mend asks for an ally" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover_at(_fighter_point(&"asha"))
			assert_eq(ctl.picked_ids(), [&"asha"] as Array[StringName], "mouse: hovering Asha aims at her")
			var row := ctl.hud.party.row_for(&"rhen")
			InputDriver.hover(row)
			assert_eq(ctl.picked_ids(), [&"rhen"] as Array[StringName], "mouse: hovering Rhen's row aims at him")
			InputDriver.click(row)
		else:
			while ctl.picked_ids()[0] != &"rhen":
				d.press(&"ui_down")
			d.press(&"ui_accept")
		assert_true(_acted(&"asha", &"rhen"), "%s: Asha mends Rhen" % d.label())
		_free()
		before_each()
	_free()


func test_the_mouse_off_every_candidate_leaves_the_aim_alone() -> void:
	_start(&"player_preview", &"rhen")
	_choose_root(InputDriver.new(InputDriver.Kind.MOUSE), BattleMenus.ROW_ATTACK)
	var aimed := ctl.picked_ids()
	InputDriver.hover_at(Vector2.ZERO)
	assert_eq(ctl.picked_ids(), aimed, "a pointer over empty sky aims at nothing new")
	InputDriver.click_at(Vector2.ZERO)
	assert_eq(ctl.state, BattleController.STATE_TARGET, "and a click there chooses nothing")
	_free()


func test_the_read_panel_closes_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		ctl.run_script(BattleCaptureScript.SCRIPT_READ_PANEL)
		var panel := ctl.hud.read_panel()
		assert_true(panel.is_open(), "%s: the Read panel is up" % d.label())
		var state := ctl.state
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.wheel(panel, 1)
		else:
			d.press(&"ui_down")
		assert_true(panel.is_open(), "%s: other input does not close it" % d.label())
		assert_eq(ctl.state, state, "%s: nor reaches the battle" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(panel)
		else:
			d.press(&"ui_accept")
		assert_false(panel.is_open(), "%s: Confirm (a click) closes it" % d.label())
		_free()
		before_each()
		ctl.run_script(BattleCaptureScript.SCRIPT_READ_PANEL)
		panel = ctl.hud.read_panel()
		_cancel(d, panel)
		assert_false(panel.is_open(), "%s: Cancel closes it too" % d.label())
		_free()
		before_each()
	_free()


func test_the_result_panel_chooses_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		ctl.run_script(BattleController.SCRIPT_DEFEAT)
		assert_eq(ctl.state, BattleController.STATE_RESULT, "%s: the defeat screen" % d.label())
		var started := ctl.battles_started
		var page := ctl.hud.result._choices
		var retry := _row_index(page, BattleController.CHOICE_RETRY)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(page.row_node(retry))
			assert_eq(page.cursor, retry, "mouse: hover moves the cursor")
			InputDriver.click(page.row_node(retry))
		else:
			while page.cursor != retry:
				d.press(&"ui_down")
			d.press(&"ui_accept")
		assert_eq(ctl.battles_started, started + 1, "%s: Retry starts the fight again" % d.label())
		assert_ne(ctl.state, BattleController.STATE_RESULT)
		_free()
		before_each()
	_free()


func test_the_battle_pause_with_each_device() -> void:
	var pauser := ctl.get_node("BattlePause") as BattlePause
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		_start(&"player_preview", &"rhen")
		pauser = ctl.get_node("BattlePause") as BattlePause
		# The mouse has no pause key of its own: it opens with the keyboard's (a finding, noted).
		var opener := d if kind != InputDriver.Kind.MOUSE else InputDriver.new(InputDriver.Kind.KEYS)
		opener.press(BattlePauseMenu.PAUSE_ACTION)
		assert_true(pauser.is_paused(), "%s: the pause action opens the page" % d.label())
		var page := pauser.menu
		var rows := page.rows_page()
		var settings_at := _row_index(rows, BattlePauseMenu.ROW_SETTINGS)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(rows.row_node(settings_at))
			assert_eq(rows.cursor, settings_at, "mouse: hover moves the cursor")
			InputDriver.click(rows.row_node(settings_at))
		else:
			d.press(&"ui_down")
			d.press(&"ui_accept")
		assert_true(page.settings_menu != null and page.settings_menu.is_open(), "%s: Settings opens" % d.label())
		_cancel(d, page.settings_menu)
		assert_true(page.settings_menu == null, "%s: Cancel closes Settings" % d.label())
		assert_true(pauser.is_paused(), "%s: back on the pause page" % d.label())
		var at := rows.cursor
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(rows.row_node(_row_index(rows, BattlePauseMenu.ROW_RESUME)))
		else:
			d.press(&"ui_up")
		assert_ne(rows.cursor, at, "%s: the pause page has the input again" % d.label())
		_cancel(d, page)
		assert_false(pauser.is_paused(), "%s: Cancel resumes" % d.label())
		assert_false(ctl.get_tree().paused)
		assert_eq(ctl.state, BattleController.STATE_COMMAND, "%s: the command menu is where it was" % d.label())
		var before := ctl.hud.commands.top_page().cursor
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(ctl.hud.commands.top_page().row_node(before + 1))
		else:
			d.press(&"ui_down")
		assert_ne(ctl.hud.commands.top_page().cursor, before, "%s: and takes the input again" % d.label())
		_free()
		before_each()
	_free()


func test_the_wheel_steps_the_command_menu() -> void:
	_start(&"player_preview", &"rhen")
	var page := ctl.hud.commands.top_page()
	var at := page.cursor
	InputDriver.wheel(page.row_node(at), 1)
	assert_ne(page.cursor, at, "the wheel moves the cursor")
	InputDriver.wheel(page.row_node(page.cursor), -1)
	assert_eq(page.cursor, at, "and back")
	_free()


# --- helpers --------------------------------------------------------------------------------------


func _start(fixture: StringName, cid: StringName) -> void:
	ctl.start_fixture(BattleFixture.load_fixture(fixture))
	var guard := 0
	while ctl.current_actor_id() != cid and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_eq(ctl.current_actor_id(), cid)
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	ctl.engine.action_resolved.connect(func(r: ActionResult) -> void: resolved.append(r))


## Chooses root row `rid` with `d`'s device.
func _choose_root(d: InputDriver, rid: StringName) -> void:
	_choose_row(d, rid)


## Chooses row `rid` on the command menu's top page: hover and click, or Down until it, then Confirm.
func _choose_row(d: InputDriver, rid: StringName) -> void:
	var page := ctl.hud.commands.top_page()
	var i := _row_index(page, rid)
	assert_true(i >= 0, "row %s is listed" % rid)
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.hover(page.row_node(i))
		assert_eq(page.cursor, i, "mouse: hover moves the cursor to %s" % rid)
		InputDriver.click(page.row_node(i))
		return
	var guard := 0
	while page.cursor != i and guard < page.row_count():
		guard += 1
		d.press(&"ui_down")
	assert_eq(page.cursor, i, "%s: Down reaches %s" % [d.label(), rid])
	d.press(&"ui_accept")


## Cancel with `d`'s device: ui_cancel, or a right click (over `over`, the HUD by default).
func _cancel(d: InputDriver, over: Control = null) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.right_click(over if over != null else ctl.hud)
	else:
		d.press(&"ui_cancel")


func _row_index(page: MenuPage, rid: StringName) -> int:
	for i in page.rows.size():
		if StringName(str(page.rows[i].get("id", ""))) == rid:
			return i
	return -1


func _other_candidate(not_this: StringName) -> StringName:
	for cid in ctl.candidate_ids():
		if cid != not_this:
			return cid
	return not_this


## A point on `cid`'s fighter, a quarter of the way down from its marker point.
func _fighter_point(cid: StringName) -> Vector2:
	var r := BattlePointer.fighter_rect(ctl, cid)
	return Vector2(r.get_center().x, r.position.y + r.size.y * 0.25)


func _acted(actor: StringName, target: StringName) -> bool:
	for r in resolved:
		if r.actor_id == actor and r.ok:
			for h in r.hits:
				if StringName(str(h.get("target_id", ""))) == target:
					return true
	return false


func _free() -> void:
	if is_instance_valid(ctl):
		ctl.get_tree().paused = false
		if ctl.get_parent() != null:
			ctl.get_parent().remove_child(ctl)
		ctl.free()
