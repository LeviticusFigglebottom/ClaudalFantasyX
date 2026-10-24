extends TestCase
## M2-UI-02: the bestiary menu out of battle (BestiaryMenuModel over the saved log and
## enemies.json, and its view BestiaryMenu), on the frozen capture enemies (battle_fixtures.json).

const LOG := {
	"gull_harrier": {"read": true, "defeated": 4},
	"reef_crab": {"read": false, "defeated": 2},
	"no_longer_listed": {"read": true, "defeated": 1},
}

var enemies: Dictionary
var menu: BestiaryMenu


func before_each() -> void:
	enemies = BattleFixture.load_fixture(&"read_panel").db.enemies
	menu = null


func test_entries_follow_the_table_order_and_skip_ids_it_no_longer_lists() -> void:
	var book := Bestiary.new(LOG.duplicate(true))
	var m := BestiaryMenuModel.new(book, enemies)
	var shown := m.entries()
	var ids: Array[StringName] = []
	for e in shown:
		ids.append(StringName(str(e["id"])))
	assert_eq(ids, [&"reef_crab", &"gull_harrier"] as Array[StringName], "enemies.json order, unknown foes absent")
	assert_eq(shown[0]["name"], tr("ENEMY_REEF_CRAB"))
	assert_false(shown[0]["read"])
	assert_eq(shown[1]["defeated"], 4)
	assert_eq(m.skipped_ids(), [&"no_longer_listed"] as Array[StringName])
	assert_true(book.entries.has("no_longer_listed"), "skipped on screen, never removed from the save")
	assert_eq(m.count_text(shown[1]), tr("BESTIARY_ROW_COUNT_FMT").format({"n": 4}))


func test_a_read_foe_has_its_full_page_and_an_unread_one_its_name_and_count() -> void:
	var m := BestiaryMenuModel.new(Bestiary.new(LOG.duplicate(true)), enemies)
	var read := m.page(&"gull_harrier")
	assert_true(read["read"])
	assert_eq((read["stats"] as Array).size(), 8)
	assert_eq(read["lore"], tr("LORE_GULL_HARRIER"))
	assert_eq(read["defeated"], tr("BESTIARY_DEFEATED_FMT").format({"n": 4}))
	var unread := m.page(&"reef_crab")
	assert_false(unread["read"])
	assert_eq(unread["title"], tr("ENEMY_REEF_CRAB"))
	assert_true((unread["stats"] as Array).is_empty(), "no stats before a Read")
	assert_true((unread["affinities"] as Array).is_empty(), "no weaknesses before a Read")
	assert_eq(unread["defeated"], tr("BESTIARY_DEFEATED_FMT").format({"n": 2}))
	assert_eq(m.page(&"no_longer_listed"), {}, "nothing to show")
	assert_eq(m.page(&"lantern_eel"), {}, "never met")


func test_the_summary_counts_reads_or_says_the_book_is_empty() -> void:
	var m := BestiaryMenuModel.new(Bestiary.new(LOG.duplicate(true)), enemies)
	assert_eq(m.summary(), tr("BESTIARY_COUNT_FMT").format({"read": 1, "known": 2}))
	assert_eq(BestiaryMenuModel.new(Bestiary.new({}), enemies).summary(), tr("BESTIARY_EMPTY"))


func test_from_game_reads_the_live_log() -> void:
	var saved := Game.state
	Game.state = GameStateData.new()
	Bestiary.new(Game.state.bestiary).record_defeated(&"reef_crab", 3)
	var m := BestiaryMenuModel.from_game()
	assert_true(m.book.entries == Game.state.bestiary, "the save's own dictionary")
	assert_eq(m.entries().size(), 1)
	Game.state = saved


func test_the_menu_lists_the_entries_and_shows_the_page_under_the_cursor() -> void:
	_open()
	var page := menu.page_view()
	assert_eq(menu.current_id, &"reef_crab", "the first entry is on show")
	var rows := menu._list.rows
	assert_eq(str(rows[0]["mp"]), tr("BESTIARY_UNREAD_TAG"), "an unread row says so in words, not hue alone")
	assert_eq(str(rows[1]["mp"]), "")
	assert_eq(str(rows[1]["right"]), tr("BESTIARY_ROW_COUNT_FMT").format({"n": 4}))
	# M2-UI-08: focus means the cursor, so a Read foe's count is plain text and an unread one dim.
	assert_eq(StringName(str(rows[1]["right_role"])), &"text")
	assert_eq(StringName(str(rows[0]["right_role"])), &"text_dim")
	assert_true(page.shown_text().has(tr("BESTIARY_UNREAD")), "an unread foe says how to learn more")
	assert_false(page.shown_text().has(tr("STAT_STRENGTH")), "and shows no stats")
	assert_true(menu.handle_input(_ev(&"ui_down")))
	assert_eq(menu.current_id, &"gull_harrier")
	assert_true(page.shown_text().has(tr("LORE_GULL_HARRIER")))
	assert_true(page.shown_text().has(tr("STAT_STRENGTH")))
	assert_eq(menu.summary_text(), tr("BESTIARY_COUNT_FMT").format({"read": 1, "known": 2}))
	menu.select(0)
	assert_eq(menu.current_id, &"reef_crab", "a click or hover selects too")
	assert_true(menu.handle_input(_ev(&"ui_accept")), "confirm is taken (and does nothing more)")
	assert_eq(menu.current_id, &"reef_crab")
	_free()


func test_cancel_closes_and_unpauses() -> void:
	_open(true)
	var tree := menu.get_tree()
	assert_true(tree.paused, "the field stops under the menu")
	var closed := [false]
	menu.closed.connect(func() -> void: closed[0] = true)
	assert_true(menu.handle_input(_ev(&"ui_cancel")))
	assert_true(closed[0])
	assert_false(menu.is_open())
	assert_false(tree.paused, "and moves again after")
	assert_false(menu.handle_input(_ev(&"ui_down")), "closed: it takes nothing")
	_free()


func test_an_empty_book_shows_the_empty_line_and_no_page() -> void:
	menu = (load(BestiaryMenu.SCENE_PATH) as PackedScene).instantiate() as BestiaryMenu
	menu.pause_tree = false
	menu.configure(BestiaryMenuModel.new(Bestiary.new({}), enemies))
	_root().add_child(menu)
	assert_eq(menu.summary_text(), tr("BESTIARY_EMPTY"))
	assert_eq(menu.current_id, &"")
	assert_false(menu.page_view().visible)
	assert_true(menu.handle_input(_ev(&"ui_down")), "moving an empty list is harmless")
	_free()


func test_open_in_brings_its_own_layer_and_frees_it_on_close() -> void:
	var host := Node.new()
	_root().add_child(host)
	var m := BestiaryMenu.open_in(host, BestiaryMenuModel.new(Bestiary.new(LOG.duplicate(true)), enemies))
	var layer := m.get_parent() as CanvasLayer
	assert_true(layer != null, "on a CanvasLayer")
	assert_eq(layer.layer, int(BestiaryMenu.load_data()["canvas_layer"]))
	m.close()
	assert_true(layer.is_queued_for_deletion())
	host.get_tree().paused = false
	_root().remove_child(host)
	host.free()


func _open(pause: bool = false) -> void:
	menu = (load(BestiaryMenu.SCENE_PATH) as PackedScene).instantiate() as BestiaryMenu
	menu.pause_tree = pause
	menu.configure(BestiaryMenuModel.new(Bestiary.new(LOG.duplicate(true)), enemies))
	_root().add_child(menu)


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _free() -> void:
	if menu != null:
		if menu.get_tree() != null:
			menu.get_tree().paused = false
		menu.get_parent().remove_child(menu)
		menu.free()
		menu = null
