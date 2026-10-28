extends TestCase
## ADR 0041 (Act I at final quality): every Act I ability plays its own battle VFX, not only its element's generic
## hit: every party kit skill, Swell, Vowbound skill, Act I creature skill and battle item
## (tools/vfx/gen_act1_ability_vfx.py). The only exceptions are skills aimed at the stair entry (`ward`): an entry
## has no fighter to play on, and its own motion is the push reaction. Every effect has a sound (validate_data).

const WARD := "ward"
## The Drownbell's toll and its gather are played by its boss view (BattleBossVfx, boss_vfx.json), not the skills map.
const BOSS_OWN: Array[String] = ["toll", "toll_gather"]

var _fx: Dictionary
var _map: Dictionary


func before_each() -> void:
	_fx = JSON.parse_string(FileAccess.get_file_as_string("res://game/data/vfx/battle/effects.json")) as Dictionary
	_map = _fx["map"] as Dictionary


func _assert_own(table: String, id: String, who: String) -> void:
	var eid := str((_map[table] as Dictionary).get(id, ""))
	assert_ne(eid, "", "%s %s has its own effect" % [who, id])
	assert_true((_fx["effects"] as Dictionary).has(eid), "%s %s: effect %s exists" % [who, id, eid])


func test_every_act_one_skill_has_its_own_effect() -> void:
	var db := BattleDB.load_default()
	var ids: Dictionary = {}
	for cid: StringName in db.characters:
		for sid: Variant in (db.characters[cid] as Dictionary).get("skills", []):
			ids[str(sid)] = String(cid)
	for sid: StringName in db.skills:
		if bool((db.skills[sid] as Dictionary).get("swell", false)):
			ids[String(sid)] = "swell"
	for row: Dictionary in BattleVowbound.load_config():
		for sid: Variant in row.get("skills", []):
			ids[str(sid)] = str(row["id"])
	for eid: StringName in db.enemies:
		for sid: Variant in (db.enemies[eid] as Dictionary).get("skills", []):
			ids[str(sid)] = String(eid)
	var checked := 0
	for sid: String in ids:
		if sid == "attack" or BOSS_OWN.has(sid) or str(db.skill(StringName(sid)).get("target", "")) == WARD:
			continue  # the plain attack is the element hit; a ward-aimed skill has no fighter to play on
		_assert_own("skills", sid, str(ids[sid]))
		checked += 1
	assert_true(checked > 60, "the Act I abilities are covered (%d)" % checked)


func test_every_battle_item_has_its_own_or_a_heal_effect() -> void:
	var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://game/data/items/items.json"))
	var items: Variant = (raw as Dictionary)["items"]
	var list: Array = (
		items
		if items is Array
		else (items as Dictionary).keys().map(
			func(k: Variant) -> Dictionary: return (items as Dictionary)[k].merged({"id": k})
		)
	)
	for row: Dictionary in list:
		var effects: Array = (row.get("battle", {}) as Dictionary).get("effects", [])
		if effects.is_empty():
			continue
		var heals := effects.any(
			func(e: Dictionary) -> bool: return str(e.get("type", "")) in ["heal_hp", "add_status", "damage"]
		)
		if not heals:
			_assert_own("items", str(row["id"]), "item")


func test_a_battle_prebuilds_only_the_effects_it_can_play() -> void:
	# 85 abilities' effects would all be built at the battle's hidden entry; only this fight's are.
	var ctl := (load("res://game/battle/scene/battle_sandbox.tscn") as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle([&"rhen", &"asha"] as Array[StringName], [], &"sandbox_reef", 20261028)
	var vfx := ctl.stage.get_node(^"BattleVfx") as BattleVfx
	assert_true(vfx.has_node(^"quick_hit#0_0"), "Rhen's Quick Hit is built")
	assert_true(vfx.has_node(^"pinch#0_0"), "the reef crab's Pinch is built")
	assert_true(vfx.has_node(^"lamp_dive#0_0"), "the Swells are built")
	assert_false(vfx.has_node(^"ladle_swing#0_0"), "the Cinder Matron's Ladle Swing isn't (not in this fight)")
	assert_true(vfx.has_node(^"hit_fire#0_0"), "every element hit is built")
	ctl.get_parent().remove_child(ctl)
	ctl.free()


func test_a_vowbound_plays_its_call_dismissal_and_fall() -> void:
	# The Lead (ADR 0041): Vowbound summons have their real VFX. Bound light, never a release.
	var ctl := (load("res://game/battle/scene/battle_sandbox.tscn") as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle([&"rhen", &"asha"] as Array[StringName], [], &"sandbox_reef", 20261028)
	var vfx := ctl.stage.get_node(^"BattleVfx") as BattleVfx
	for ev: String in ["vowbound_call", "vowbound_dismiss", "vowbound_fell"]:
		assert_eq(str((_map["events"] as Dictionary).get(ev, "")), ev, "%s is an event" % ev)
		var def := (_fx["effects"] as Dictionary)[ev] as Dictionary
		for l: Dictionary in def["layers"]:
			assert_false((l["swatches"] as Array).has("glimmer_lift"), "%s never rises gold (not a release)" % ev)
	var linked := ctl.engine.vowbound.called.get_connections().any(
		func(c: Dictionary) -> bool: return (c["callable"] as Callable).get_object() == vfx
	)
	assert_true(linked, "the call plays its effect (deferred, once the stage has seated it)")
	var vb := ctl.engine.party_active[0]
	ctl.engine.vowbound.departed.emit(vb, false)
	assert_true(vfx.played.has(&"vowbound_dismiss"), "a dismissal settles")
	ctl.engine.vowbound.departed.emit(vb, true)
	assert_true(vfx.played.has(&"vowbound_fell"), "a fall sinks")
	ctl.get_parent().remove_child(ctl)
	ctl.free()
