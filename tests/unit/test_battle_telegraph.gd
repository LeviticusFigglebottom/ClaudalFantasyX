extends TestCase
## M3-BPR-413: any foe's gathering charge reads on stage (Pillar 4). A foe that starts a charge plays the telegraph's
## gather accent on that action's contact and on each later turn of the charge; the Drownbell's own row keeps its
## toll; a party member's or an entry's charge plays nothing here.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261027

var ctl: BattleController


func _start(encounter: StringName) -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 1.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var party: Array[StringName] = [&"rhen", &"asha", &"toma"]
	var none: Array[StringName] = []
	ctl.start_battle(party, none, encounter, SEED)
	ctl.stage.choreo.live = false


func test_a_regular_foes_charge_gathers_on_stage() -> void:
	_start(&"ch04_spar_wraith")
	var tg := ctl.stage.choreo.telegraph
	var foe := ctl.engine.enemies[0]
	ctl.engine.charge_started.emit(foe, &"lines_taut", 2)
	assert_eq(tg.played.size(), 1, "the gathering action's own gather")
	foe.charge_skill = &"lines_taut"
	foe.charge_left = 2
	ctl.engine.turn_started.emit(foe)
	assert_eq(tg.played.size(), 2, "and again on the next turn of the charge")
	foe.charge_left = 1
	ctl.engine.turn_started.emit(foe)
	assert_eq(tg.played.size(), 2, "the turn it fires plays the skill instead")
	_free()


func test_the_drownbell_keeps_its_own_and_the_party_none() -> void:
	_start(&"drownbell")
	var tg := ctl.stage.choreo.telegraph
	ctl.engine.charge_started.emit(ctl.engine.enemies[0], &"toll", 3)
	assert_true(tg.played.is_empty(), "the bell's toll is BattleBossChoreo's")
	ctl.engine.charge_started.emit(ctl.engine.party_active[0], &"anything", 2)
	assert_true(tg.played.is_empty(), "a party member's charge plays nothing here")
	_free()


func test_every_telegraphing_foe_is_covered() -> void:
	var db := BattleDB.load_default()
	var bosses := BattleChoreo.load_data()["bosses"] as Dictionary
	for eid: StringName in db.enemies:
		var row := db.enemies[eid] as Dictionary
		var skills: Array = (row.get("skills", []) as Array).duplicate()
		for ph: Variant in row.get("phases", []):
			skills.append_array((ph as Dictionary).get("skills", []))
		for sid: Variant in skills:
			if (db.skill(StringName(str(sid))).get("charge", {}) as Dictionary).is_empty():
				continue
			# BattleTelegraph covers it unless the foe's boss row owns it (and then that row has a gather).
			if bosses.has(String(eid)) and str((bosses[String(eid)] as Dictionary).get("charge_skill", "")) != "":
				assert_true((bosses[String(eid)] as Dictionary).has("gather"), "%s: its boss row gathers" % eid)


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
