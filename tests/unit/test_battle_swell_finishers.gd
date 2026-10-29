extends TestCase
## M3-BPR-422 (ADR 0041): every Act I party member's Swell plays a finisher of its own: its own style (a "shot" style,
## not the plain melee or cast), its camera framing and its own effect. Rhen, Asha, Toma and Ysolde have their
## techniques (swell.json); Kerrid's weighted swing and Liss's reel-stop wait on combat (M3-C05-06, M3-C06-05), so their
## finishers play from swell_style_by_hero and map.swell_by_hero for any technique of theirs marked "swell".

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const ACT1_HEROES: Array[StringName] = [&"rhen", &"asha", &"toma", &"ysolde", &"kerrid", &"liss"]
## A stand-in technique: the real ids are combat's to write.
const PROBE := &"_probe_swell"

var ctl: BattleController


## The runner has no after_each: each test frees its controller itself (a leftover one takes later tests' clicks).
func _free() -> void:
	if ctl != null:
		ctl.engine.db.skills.erase(PROBE)  # the db may be shared: leave no stand-in technique behind
		ctl.get_parent().remove_child(ctl)
		ctl.free()
		ctl = null


func _start(party: Array[StringName]) -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle(party, [], &"sandbox_reef", 20261028)


func _vfx() -> BattleVfx:
	return ctl.stage.get_node(^"BattleVfx") as BattleVfx


## The hero's Swell techniques, or the probe (added to the db as a "swell" skill) for a hero with none yet.
func _techniques(hero: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	var swell := (
		(JSON.parse_string(FileAccess.get_file_as_string("res://game/data/battle/swell.json")) as Dictionary)["swell"]
		as Dictionary
	)
	for row: Dictionary in swell["heroes"]:
		if StringName(str(row["id"])) == hero:
			for sid: Variant in row["techniques"]:
				out.append(StringName(str(sid)))
	if out.is_empty():
		ctl.engine.db.skills[PROBE] = {
			"id": String(PROBE), "kind": "physical", "target": "one_foe", "element": "none", "swell": true, "power": 30
		}
		out.append(PROBE)
	return out


func test_every_act_one_hero_has_a_swell_finisher() -> void:
	_start([&"rhen", &"asha", &"toma"] as Array[StringName])
	var data := BattleChoreo.load_data()
	var by_style := data["camera"]["by_style"] as Dictionary
	var fx := _vfx().data["effects"] as Dictionary
	for hero in ACT1_HEROES:
		for sid in _techniques(hero):
			var r := ActionResult.new()
			r.actor_id = hero
			r.skill_id = sid
			r.hits = [{"target_id": ctl.engine.enemies[0].id, "hit": true, "crit": false, "amount": 10}]
			var style_id := BattleChoreoPlan.style_id_for(data, ctl.engine, r)
			var st := BattleChoreoPlan.style(data, style_id)
			assert_ne(str(st.get("shot", "")), "", "%s %s: a finisher style of its own (%s)" % [hero, sid, style_id])
			assert_eq(str(st.get("clip", "")), "finisher", "%s %s: the finisher clip" % [hero, sid])
			assert_true(by_style.has(style_id), "%s %s: camera framing for %s" % [hero, sid, style_id])
			var own := ""
			for e: Dictionary in _vfx().effects_for(r):
				if fx.has(String(e["effect"])) and not String(e["effect"]).begins_with("hit_"):
					own = String(e["effect"])
			assert_ne(own, "", "%s %s: an effect of its own" % [hero, sid])
	_free()


func test_the_new_finishers_read_apart() -> void:
	_start([&"rhen", &"asha", &"toma"] as Array[StringName])
	var data := BattleChoreo.load_data()
	var swing := BattleChoreoPlan.style(data, "swing")
	var finisher := BattleChoreoPlan.style(data, "finisher")
	assert_eq(float(swing.get("lift_m", 1.0)), 0.0, "the weighted swing stays low (never overhead)")
	assert_true(float(swing["strike_sec"]) > float(finisher["strike_sec"]), "the swing holds its coil longer")
	assert_ne(str(BattleChoreoPlan.style(data, "reel").get("travel", "")), "target", "the reel-stop is thrown")
	_free()


func test_a_finisher_is_prebuilt_only_when_its_hero_fights() -> void:
	_start([&"rhen", &"asha", &"toma"] as Array[StringName])
	var unused := _vfx()._unused_specials()
	assert_true(unused.has("swell_weighted_swing"), "no Kerrid: his finisher is not built")
	assert_true(unused.has("swell_reel_stop"), "no Liss: hers is not built")
	_free()
	_start([&"rhen", &"kerrid", &"liss"] as Array[StringName])
	unused = _vfx()._unused_specials()
	assert_false(unused.has("swell_weighted_swing"), "Kerrid fights: his finisher is built")
	assert_false(unused.has("swell_reel_stop"), "Liss fights: hers is built")
	_free()
