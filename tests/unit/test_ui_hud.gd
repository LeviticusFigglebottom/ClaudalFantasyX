extends TestCase
## HUD layout data and components (M1-UI-01): CommandMenu navigation, gauges, glyphs.

const THEME_PATH := "res://game/ui/theme/hymn_theme.tres"
const REF := Vector2(1920, 1080)
const SAFE := 48.0

var host: Control


func before_each() -> void:
	host = Control.new()
	host.theme = load(THEME_PATH) as Theme
	host.size = REF
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(host)


func test_hud_rects_sit_inside_the_safe_margin() -> void:
	var data := HudLayout.data()
	var safe := Rect2(Vector2(SAFE, SAFE), REF - Vector2(SAFE, SAFE) * 2.0)
	for sname: String in data:
		var sec: Variant = data[sname]
		if sec is Dictionary and (sec as Dictionary).has("rect"):
			var r := HudLayout.rect_of(sec as Dictionary)
			assert_true(safe.encloses(r), "%s %s is inside the 48 px safe margin" % [sname, r])
	_free()


func test_timeline_fits_sixteen_turns() -> void:
	var tl := TurnTimeline.new()
	host.add_child(tl)
	var last := tl.slot_rect(CtbTimeline.PREVIEW_LENGTH - 1)
	assert_true(last.end.y <= tl.size.y, "slot 15 ends inside the panel (%s vs %s)" % [last.end.y, tl.size.y])
	assert_true(tl.slot_rect(1).position.y >= tl.slot_rect(0).end.y, "slot 0 and 1 do not overlap")
	_free()


func test_command_menu_navigation_wraps_and_skips_disabled() -> void:
	var menu := _menu()
	var seen: Array[StringName] = []
	menu.highlighted.connect(func(_p: StringName, row: Dictionary) -> void: seen.append(row["id"]))
	var rows: Array[Dictionary] = [_row(&"a", true), _row(&"b", false), _row(&"c", true)]
	menu.open_root(&"root", "Rhen", rows)
	assert_eq(menu.current_row()["id"], &"a")
	_input(menu, &"ui_down")
	assert_eq(menu.current_row()["id"], &"c", "disabled rows are skipped")
	_input(menu, &"ui_down")
	assert_eq(menu.current_row()["id"], &"a", "wraps around")
	_input(menu, &"ui_up")
	assert_eq(menu.current_row()["id"], &"c")
	assert_eq(seen, [&"a", &"c", &"a", &"c"] as Array[StringName], "each move is announced for the preview")
	_free()


func test_command_menu_accept_cancel_and_submenus() -> void:
	var menu := _menu()
	var chosen: Array[StringName] = []
	var cancelled: Array[StringName] = []
	menu.chosen.connect(func(_p: StringName, row: Dictionary) -> void: chosen.append(row["id"]))
	menu.cancelled.connect(func(p: StringName) -> void: cancelled.append(p))
	menu.open_root(&"root", "Rhen", [_row(&"skills", true)] as Array[Dictionary])
	_input(menu, &"ui_accept")
	assert_eq(chosen, [&"skills"] as Array[StringName])
	menu.push(&"sub", "Skills", [_row(&"x", true), _row(&"y", true)] as Array[Dictionary])
	assert_eq(menu.depth(), 2)
	assert_eq(menu.page_id(), &"sub")
	_input(menu, &"ui_cancel")
	assert_eq(cancelled, [&"sub"] as Array[StringName], "cancel is reported; the owner decides to pop")
	assert_true(menu.pop())
	assert_false(menu.pop(), "the root never pops")
	menu.active = false
	assert_false(menu.handle_input(_ev(&"ui_down")), "an inactive menu ignores input")
	_free()


func test_disabled_rows_cannot_be_accepted() -> void:
	var menu := _menu()
	var chosen: Array[StringName] = []
	menu.chosen.connect(func(_p: StringName, row: Dictionary) -> void: chosen.append(row["id"]))
	menu.open_root(&"root", "", [_row(&"off", false)] as Array[Dictionary])
	menu.accept()
	assert_true(chosen.is_empty())
	_free()


func test_gauge_low_state_needs_the_threshold() -> void:
	var g := HudGauge.new(&"hp")
	host.add_child(g)
	g.low_fraction = 0.25
	g.set_value(100, 400)
	assert_false(g.is_low(), "exactly 25% is not low")
	g.set_value(99, 400)
	assert_true(g.is_low())
	g.set_value(0, 400)
	assert_false(g.is_low(), "KO is its own state, not low HP")
	_free()


func test_party_row_reads_but_never_writes() -> void:
	var c := BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, {"stats": {"hp": 420, "mp": 24}})
	c.hp = 50
	c.add_status(&"haste", 2)
	c.add_status(&"poison", 3)
	var row := PartyRow.new()
	row.size = Vector2(560, 72)
	host.add_child(row)
	row.setup(HudLayout.section(&"party"), c, "Rhen")
	assert_eq(row.hp_text(), "50/420")
	assert_eq(row.status_ids(), [&"haste", &"poison"] as Array[StringName])
	assert_eq(c.hp, 50, "untouched")
	assert_eq(c.statuses.size(), 2)
	_free()


func test_status_glyph_polarity() -> void:
	assert_true(StatusGlyph.is_buff(&"haste"))
	assert_true(StatusGlyph.is_buff(&"protect"))
	assert_false(StatusGlyph.is_buff(&"poison"))
	assert_false(StatusGlyph.is_buff(&"slow"))
	_free()


func _menu() -> CommandMenu:
	var m := CommandMenu.new()
	host.add_child(m)
	return m


func _row(rid: StringName, enabled: bool) -> Dictionary:
	return {"id": rid, "label": String(rid), "right": "", "enabled": enabled}


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _input(menu: CommandMenu, action: StringName) -> void:
	menu.handle_input(_ev(action))


func _free() -> void:
	host.get_parent().remove_child(host)
	host.free()


# --- M1-UI-02 ----------------------------------------------------------------------------


func test_every_status_has_its_own_glyph_shape() -> void:
	var raw := FileAccess.get_file_as_string("res://game/data/battle/statuses.json")
	var rows: Array = (JSON.parse_string(raw) as Dictionary)["statuses"]
	assert_eq(rows.size(), 21, "SPEC §6.8 statuses")
	for row: Variant in rows:
		var sid := StringName(str((row as Dictionary)["id"]))
		assert_true(StatusGlyph.has_shape(sid), "%s has a dedicated vector glyph (no fallback diamond)" % sid)
	_free()


func test_glyph_polarity_is_coded_by_backing_shape_too() -> void:
	var buff := StatusGlyph.new(&"reflect")
	var ailment := StatusGlyph.new(&"doom")
	assert_true(buff.shows_buff(), "Reflect sits on a disc")
	assert_false(ailment.shows_buff(), "Doom sits on a diamond")
	var flipped := StatusGlyph.new(&"regen", true)
	assert_false(flipped.shows_buff(), "Regen under Zombie reads as an ailment")
	var zombie := BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, {"stats": {"hp": 10}})
	zombie.add_status(&"regen", 3)
	assert_false(StatusGlyph.inverted_for(zombie, &"regen"))
	zombie.add_status(&"zombie", -1)
	assert_true(StatusGlyph.inverted_for(zombie, &"regen"))
	assert_false(StatusGlyph.inverted_for(zombie, &"zombie"))
	for g: StatusGlyph in [buff, ailment, flipped]:
		g.free()
	_free()


func test_party_row_shows_stone_and_the_doom_count() -> void:
	var c := BattleCombatant.from_dict(&"asha", BattleCombatant.TEAM_PARTY, {"stats": {"hp": 300, "mp": 60}})
	c.add_status(&"doom", 4)
	var row := PartyRow.new()
	row.size = Vector2(560, 72)
	host.add_child(row)
	row.setup(HudLayout.section(&"party"), c, "Asha", Color.ROYAL_BLUE)
	assert_eq(row.doom_text(), "4")
	assert_false(row.is_stone())
	c.add_status(&"petrify", -1)
	row.refresh(false)
	assert_true(row.is_stone(), "petrified: the portrait turns to stone")
	assert_eq(row.status_ids(), [&"petrify"] as Array[StringName], "stone clears every other status")
	assert_eq(row.doom_text(), "", "and with it the countdown")
	assert_eq(row.hp_text(), "300/300", "HP is kept under stone")
	_free()


func test_party_row_marks_an_automatic_turn() -> void:
	var panel := PartyPanel.new()
	host.add_child(panel)
	var c := BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, {"stats": {"hp": 420}})
	var members: Array[BattleCombatant] = [c]
	panel.show_members(members, {&"rhen": "Rhen"})
	panel.set_current(&"rhen", &"berserk")
	assert_true(panel.row_for(&"rhen").is_current)
	assert_eq(panel.row_for(&"rhen").auto_reason, &"berserk")
	panel.set_current(&"rhen")
	assert_eq(panel.row_for(&"rhen").auto_reason, &"", "a player turn clears it")
	_free()


func test_new_hud_metrics_and_text_styles_exist() -> void:
	var tl := HudLayout.section(&"timeline")
	for k: String in ["current_frame_px", "current_glow_px", "caption_height", "doom_glyph_px", "doom_label_width"]:
		assert_true(tl.has(k), "timeline.%s" % k)
	var marker := HudLayout.section(&"actor_marker")
	assert_true(HudLayout.num(marker, "size_px") > 18.0, "the current-actor marker grew (UI-01 lead review)")
	for k: String in ["lift_px", "stem_px", "frame_px"]:
		assert_true(marker.has(k), "actor_marker.%s" % k)
	var theme := host.theme
	for v: StringName in [&"FloatText", &"BadgeNumber"]:
		assert_true(theme.get_font_size(&"font_size", v) >= 22, "%s keeps the 22 px minimum" % v)
	for role: StringName in [&"stone", &"stone_crack"]:
		assert_true(theme.has_color(role, &"Hymn"), "theme role %s" % role)
	_free()
