extends TestCase
## Act I final pass (ADR 0041): the battle HUD shows faces, not letters. BattlePortraits gives a hero's face crop
## (worried while down) and an enemy's bestiary picture; a fighter with neither (a Vowbound) keeps its initial.


func test_heroes_and_foes_have_pictures() -> void:
	for hero: StringName in [&"rhen", &"asha", &"toma", &"ysolde", &"liss", &"kerrid"]:
		assert_true(BattlePortraits.texture(hero) != null, "%s has a battle face" % hero)
	var up := BattlePortraits.texture(&"rhen")
	var down := BattlePortraits.texture(&"rhen", true)
	assert_ne((up as AtlasTexture).atlas, (down as AtlasTexture).atlas, "a fallen hero looks worried")
	assert_true(BattlePortraits.texture(&"tide_crawler#2") != null, "a numbered foe finds its base's picture")
	assert_true(
		BattlePortraits.texture(&"stillguard_inquisitor") != null, "a foe who is a person shows his face (Moll)"
	)
	assert_eq(BattlePortraits.texture(&"nobody"), null)


func test_every_act_one_enemy_with_a_model_has_a_picture() -> void:
	var missing: Array[String] = []
	for eid: Variant in BattleDB.load_default().enemies:
		if (
			CreaturePortraits.creature_for(StringName(str(eid))) != &""
			and BattlePortraits.texture(StringName(str(eid))) == null
		):
			missing.append(str(eid))
	assert_eq(missing, [] as Array[String], "every enemy with a model shows its picture in battle")


func test_the_row_and_chip_hide_the_initial_behind_a_face() -> void:
	var c := BattleCombatant.new()
	c.id = &"asha"
	c.max_hp = 10
	c.hp = 10
	var row := PartyRow.new()
	row.setup(HudLayout.section(&"party"), c, "Asha")
	var initial := row.get_child(0) as Label
	assert_false(initial.visible, "Asha's face, not 'A'")
	c.id = &"ilun"
	var row2 := PartyRow.new()
	row2.setup(HudLayout.section(&"party"), c, "Ilun")
	assert_true((row2.get_child(0) as Label).visible, "no picture yet: the initial stays")
	row.free()
	row2.free()
	var chip := TimelineChip.new()
	chip.setup(HudLayout.section(&"timeline"))
	chip.apply(
		{"id": &"tide_crawler", "team": &"enemy", "ghost": false, "skipped": false, "moved": 0},
		{"label": "Tide Crawler"},
		false
	)
	assert_false((chip.get_child(0) as Label).visible, "the foe's picture, not 'T'")
	chip.free()
