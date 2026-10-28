extends TestCase
## Act I final pass (ADR 0041): every item, piece of equipment and skill a player meets has an icon (MenuGlyph,
## menu_glyphs.json), and a menu row carries it before its label.


func test_every_item_equipment_and_skill_has_an_icon() -> void:
	var db := ItemDB.load_default()
	for iid: Variant in db.items:
		assert_false(MenuGlyph.for_goods(StringName(str(iid))).is_empty(), "item %s has an icon" % iid)
	for eid: Variant in db.equipment:
		assert_false(MenuGlyph.for_goods(StringName(str(eid))).is_empty(), "equipment %s has an icon" % eid)
	var skills := BattleDB.load_default().skills
	for sid: Variant in skills:
		assert_false(MenuGlyph.for_skill_row(skills[sid] as Dictionary).is_empty(), "skill %s has an icon" % sid)


func test_every_named_glyph_is_drawn() -> void:
	var g := MenuGlyph.new()
	g.size = Vector2(48.0, 48.0)
	for e in MenuGlyphsShot.glyphs():
		assert_true(MenuGlyph.DRAWN.has(e["glyph"]), "%s has a drawing" % e["glyph"])
	g.free()


func test_a_row_puts_its_icon_before_the_label() -> void:
	var page := MenuPage.new()
	page.size = Vector2(540.0, 200.0)
	ParityHost.scene_root().add_child(page)
	var m := HudLayout.section(&"commands")
	page.setup(m, &"test", "", [{"id": &"a", "label": "Salt Tonic", "glyph": MenuGlyph.for_goods(&"salt_tonic")}])
	var row := page.row_node(0)
	var label := row.get_child(0) as Label
	var icon := row.get_child(row.get_child_count() - 1) as MenuGlyph
	assert_true(icon != null, "the icon is the row's last child")
	assert_true(label.position.x >= icon.position.x + icon.size.x, "the label starts right of it")
	page.settle()
	assert_true(label.position.x >= icon.position.x + icon.size.x, "and stays there under the cursor's nudge")
	page.get_parent().remove_child(page)
	page.free()
