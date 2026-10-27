extends TestCase
## M2-MNU-304: the field menu's root shows the active line as cards (portrait, name, HP and MP), so it
## opens on the party; they hide off the root and follow changes made on the party pages.

const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}
const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]


func test_a_card_per_place_with_portrait_name_and_vitals() -> void:
	var menu := _open(GameStateData.new())
	var cards := menu.party_cards()
	assert_eq(cards.size(), FormationMenuModel.places(), "one card per place in the active line")
	var line := FormationMenuModel.new(PartySheet.new(menu.model.state, menu.model.heroes))
	for i in cards.size():
		var cid := line.active[i]
		assert_eq(cards[i].hero(), cid, "in line order")
		assert_true(cards[i].visible, "shown on the root")
		assert_true(cards[i].portrait().picture().texture != null, "%s: the baked portrait" % cid)
		var v := line.vitals(cid)
		var words := cards[i].shown_text()
		assert_eq(words[0], line.sheet.hero_name(cid))
		assert_eq(words[1], tr("FIELD_MENU_PARTY_HP_FMT").format({"hp": v["hp"], "max": v["max_hp"]}))
		assert_eq(words[2], tr("FIELD_MENU_PARTY_MP_FMT").format({"mp": v["mp"], "max": v["max_mp"]}))
	assert_true(cards[1].position.x > cards[0].position.x, "side by side")
	menu.free()


func test_cards_hide_off_the_root() -> void:
	var menu := _open(GameStateData.new())
	menu.root_page().set_cursor(FieldMenuModel.ROOT_IDS.find(FieldMenuModel.ROW_QUIT), false)
	menu.accept()
	for card: PartyCard in menu.party_cards():
		assert_false(card.visible, "the Quit question has the right column")
	menu.back()
	assert_true(menu.party_cards()[0].visible, "back on the root")
	menu.free()


func test_a_fallen_hero_looks_worried_and_dim() -> void:
	var state := GameStateData.new()
	var menu := _open(state)
	var line := FormationMenuModel.new(PartySheet.new(state, menu.model.heroes))
	var cid := line.active[0]
	menu.free()
	state.party_vitals[String(cid)] = {"hp": 0, "mp": 0}
	menu = _open(state)
	var card := menu.party_cards()[0]
	assert_eq(card.hero(), cid)
	assert_eq(card.portrait().emotion(), HeroPortraits.page_emotion(PartyCard.PAGE, true), "worried when fallen")
	assert_true(card.modulate.a < 1.0, "a fallen hero's card is dimmed")
	menu.free()


func _open(state: GameStateData) -> FieldMenu:
	var menu := (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(FieldMenuModel.new(state, HEROES, NAMES))
	_root().add_child(menu)
	return menu


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root
