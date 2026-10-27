extends TestCase
## M3-C09-05: Pell's label (act1_ch09.md §9 UI 3). "The Kirru" until ch09_pell_named (Ch9 B09),
## then "Pell", through the one resolver (CharacterNames) in every UI that names him: the dialogue
## box's speaker name (and the backlog, which records it), the field menu, the party pages
## (PartySheet.hero_name: formation, status) and the battle HUD and menus (BattleMenus).

const BOX_SCENE := "res://game/ui/dialogue/dialogue_box.tscn"
const PELL := &"pell"
const FLAG := &"ch09_pell_named"
const LINE_KEY := &"DLG_CH09_ROAD_005"

var made: Array[Node] = []
var _saved: GameStateData


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	_saved = Game.state
	Game.state = GameStateData.new()


func test_the_resolver_follows_the_flag() -> void:
	assert_eq(tr("CHAR_PELL_UNNAMED"), "The Kirru")
	assert_eq(CharacterNames.key_for(PELL, "CHAR_PELL"), "CHAR_PELL_UNNAMED", "before B09")
	assert_eq(CharacterNames.display(PELL, "CHAR_PELL"), "The Kirru")
	assert_eq(CharacterNames.key_for(&"rhen", "CHAR_RHEN"), "CHAR_RHEN", "everyone else keeps their name")
	Game.set_flag(FLAG)
	assert_eq(CharacterNames.key_for(PELL, "CHAR_PELL"), "CHAR_PELL", "after B09")
	assert_eq(CharacterNames.display(PELL, "CHAR_PELL"), "Pell")
	var unset := func(_f: StringName) -> bool: return false
	assert_eq(CharacterNames.key_for(PELL, "CHAR_PELL", unset), "CHAR_PELL_UNNAMED", "a passed reader wins")
	_done()


func test_every_until_named_row_is_declared_and_keyed() -> void:
	for id: Variant in CharacterNames.rows():
		var row := CharacterNames.rows()[id] as Dictionary
		assert_ne(tr(str(row["name_key"])), str(row["name_key"]), "%s has an English name" % id)
		Game.get_flag(StringName(str(row["until_flag"])))  # an undeclared flag fails the run
	_done()


func test_the_dialogue_box_names_him() -> void:
	var box := (load(BOX_SCENE) as PackedScene).instantiate() as DialogueBox
	_keep(box)
	box.show_text(PELL, LINE_KEY)
	assert_eq(box.speaker_name(), "The Kirru", "'Pell.' is said by the Kirru: the flag is set after")
	Game.set_flag(FLAG)
	box.show_text(PELL, LINE_KEY)
	assert_eq(box.speaker_name(), "Pell")
	box.show_text(PELL, LINE_KEY, &"CHAR_RHEN")
	assert_eq(box.speaker_name(), tr("CHAR_RHEN"), "a line's own alias still wins")
	_done()


func test_the_menus_and_the_battle_name_him() -> void:
	var heroes: Array[StringName] = [&"rhen", PELL]
	var model := FieldMenuModel.new(GameStateData.new(), heroes, {&"rhen": "CHAR_RHEN", PELL: "CHAR_PELL"})
	var db := BattleDB.load_default()
	db.characters[PELL] = {"name_key": "CHAR_PELL", "stats": {"hp": 1}}  # until M3-C09-07's row lands
	var sheet := PartySheet.new(GameStateData.new(), heroes, db)
	var menus := BattleMenus.new()
	var ally := BattleCombatant.from_dict(PELL, BattleCombatant.TEAM_PARTY, db.characters[PELL])
	assert_eq(model.hero_name(PELL), "The Kirru", "field menu")
	assert_eq(sheet.hero_name(PELL), "The Kirru", "party pages (formation, status)")
	assert_eq(menus.display_name(ally), "The Kirru", "battle")
	assert_eq(model.hero_name(&"rhen"), tr("CHAR_RHEN"))
	Game.set_flag(FLAG)
	assert_eq(model.hero_name(PELL), "Pell")
	assert_eq(sheet.hero_name(PELL), "Pell")
	assert_eq(menus.display_name(ally), "Pell")
	_done()


func _keep(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


func _done() -> void:
	Game.state = _saved
