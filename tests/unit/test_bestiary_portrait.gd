extends TestCase
## M2-UI-1000: the bestiary page's portrait (BestiaryPortraitSlot over the baked CreaturePortraits PNGs, ADR 0110):
## a Read foe in colour, a never-Read one as a silhouette, a foe with no picture as nothing; it follows the cursor,
## sits square in the page's leftover corner between min_px and max_px, and empties when the page closes.

const LOG := {
	"reef_crab": {"read": false, "defeated": 2},
	"lantern_eel": {"read": true, "defeated": 1},
	"gull_harrier": {"read": true, "defeated": 4},
}

var menu: BestiaryMenu
var made: Array[Node] = []


func before_each() -> void:
	_free()


func test_a_read_foe_shows_in_colour_and_an_unread_one_as_a_silhouette() -> void:
	_open()
	var slot := menu.portrait_slot()
	assert_eq(menu.current_id, &"reef_crab")
	assert_true(slot.has_creature(), "the crab has a picture")
	assert_eq(slot.portrait().texture, CreaturePortraits.texture(&"reef_crab"), "its baked PNG")
	assert_true(slot.silhouette, "never Read: a silhouette")
	var mat := slot.portrait().material as ShaderMaterial
	assert_true(mat != null and mat.shader == BestiaryPortraitSlot.SILHOUETTE_SHADER)
	var tint := mat.get_shader_parameter(&"tint") as Color
	var d: Dictionary = BestiaryMenu.load_data()["portrait"]
	assert_true(is_equal_approx(tint.a, float(d["silhouette_alpha"])), "silhouette_alpha")
	var role := _theme_color(str(d["silhouette_role"]))
	assert_true(Color(tint, 1.0).is_equal_approx(Color(role, 1.0)), "the theme's role colour")
	menu.select(1)
	assert_eq(slot.enemy_id, &"lantern_eel", "the portrait follows the cursor")
	assert_eq(slot.portrait().texture, CreaturePortraits.texture(&"lantern_eel"))
	assert_false(slot.silhouette)
	assert_true(slot.portrait().material == null, "a Read foe in its own colours")
	assert_false(slot.portrait().texture is ViewportTexture, "a small texture, no live viewport (ADR 0110)")
	_free()


func test_a_foe_with_no_picture_shows_nothing() -> void:
	_open()
	var slot := menu.portrait_slot()
	assert_false(slot.show_enemy(&"no_such_enemy", true))
	assert_false(slot.has_creature())
	assert_false(slot.is_showing())
	assert_eq(slot.enemy_id, &"")
	_free()


func test_closing_the_page_clears_the_portrait() -> void:
	_open()
	var slot := menu.portrait_slot()
	assert_true(slot.has_creature())
	menu.close()
	assert_false(slot.has_creature(), "clear() on close")
	assert_false(slot.is_showing())
	_free()


func test_an_empty_book_has_no_portrait() -> void:
	menu = (load(BestiaryMenu.SCENE_PATH) as PackedScene).instantiate() as BestiaryMenu
	menu.pause_tree = false
	menu.configure(BestiaryMenuModel.new(Bestiary.new({}), BattleFixture.load_fixture(&"read_panel").db.enemies))
	_root().add_child(menu)
	assert_false(menu.portrait_slot().has_creature())
	_free()


func test_the_portrait_is_square_in_the_slot_corner_between_its_bounds() -> void:
	var d: Dictionary = BestiaryMenu.load_data()["portrait"]
	var slot := BestiaryPortraitSlot.new(d)
	_root().add_child(slot)
	made.append(slot)
	assert_true(slot.show_enemy(&"lantern_eel", true))
	var max_px := float(d["max_px"])
	var min_px := float(d["min_px"])
	var p := slot.portrait()
	slot.size = Vector2(max_px * 2.0, min_px + 10.0)
	assert_eq(p.size, Vector2(min_px + 10.0, min_px + 10.0), "the slot's smaller side")
	assert_eq(p.position + p.size, slot.size, "bottom-right corner, inside the slot")
	assert_true(slot.is_showing())
	slot.size = Vector2(max_px * 3.0, max_px * 3.0)
	assert_eq(p.size, Vector2(max_px, max_px), "never past max_px")
	assert_eq(p.position + p.size, slot.size)
	slot.size = Vector2(max_px, min_px - 1.0)
	assert_false(slot.is_showing(), "too little room: hidden rather than squeezed")
	assert_true(slot.has_creature(), "still loaded, shown again when the room comes back")
	slot.clear()
	_free()


func _open() -> void:
	menu = (load(BestiaryMenu.SCENE_PATH) as PackedScene).instantiate() as BestiaryMenu
	menu.pause_tree = false
	var fx := BattleFixture.load_fixture(&"read_panel")
	menu.configure(BestiaryMenuModel.new(Bestiary.new(LOG.duplicate(true)), fx.db.enemies))
	_root().add_child(menu)


func _theme_color(role: String) -> Color:
	return menu.get_theme_color(StringName(role), HymnThemeBuilder.PALETTE_TYPE)


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _free() -> void:
	if menu != null and is_instance_valid(menu):
		menu.get_parent().remove_child(menu)
		menu.free()
	menu = null
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
