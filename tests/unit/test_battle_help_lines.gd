extends TestCase
## The skill help line says what a skill does (M4-A2P-1007, the Lead's Act II tutorial clarity pass): Nhoa's Echo
## names the action it will copy and reads as that copy, or says there is nothing to echo yet (A8); Hesk's Cord Lift
## names what it cures (A13).

const REEF := &"sandbox_reef"

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	engine.setup(
		BattleDB.load_default(), [&"rhen", &"asha"] as Array[StringName], [&"toma"] as Array[StringName], REEF, 3
	)
	engine.begin()


func test_echo_names_what_it_copies() -> void:
	var menus := BattleMenus.new()
	engine.last_foe_skill = &""
	assert_true(menus.skill_help(engine, &"nhoa_echo", -1).begins_with(tr("HUD_HELP_ECHO_NONE")), "nothing yet")
	engine.last_foe_skill = &"attack"
	var line := menus.skill_help(engine, &"nhoa_echo", -1)
	var copied := tr(str(engine.db.skill(&"attack")["name_key"]))
	assert_true(line.begins_with(tr("HUD_HELP_ECHO_FMT").format({"skill": copied})), line)
	assert_true(line.contains(tr("HUD_KIND_PHYSICAL")), "it reads as the copy (a strike), not as Echo's own support")
	assert_false(line.contains(tr("HUD_KIND_SUPPORT")))


func test_cord_lift_names_what_it_cures() -> void:
	var menus := BattleMenus.new()
	var line := menus.skill_help(engine, &"cord_lift", -1)
	for sid: Variant in engine.db.skill(&"cord_lift")["cleanses"]:
		var key := str((engine.db.statuses.get(StringName(str(sid)), {}) as Dictionary).get("name_key", ""))
		assert_true(line.contains(tr(key)), "%s is named in: %s" % [sid, line])
	assert_true(line.contains(tr("HUD_HELP_CURES_FMT").get_slice("{", 0)), "as a cure")
