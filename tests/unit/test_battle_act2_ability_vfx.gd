extends TestCase
## ADR 0205 (Act II per track): every Act II foe's ability plays its own battle VFX, as Act I's do
## (tools/vfx/gen_act2_ability_vfx.py). ADR 0204: nothing in a Ch12..Ch15 foe's effect is ice (salt-glass or
## moon-blue crystals); Ch12's scree is snow and grit.

const ICE: Array[String] = ["salt_glass", "moon_blue"]

var _fx: Dictionary


func before_each() -> void:
	_fx = JSON.parse_string(FileAccess.get_file_as_string("res://game/data/vfx/battle/effects.json")) as Dictionary


func test_every_act_two_foe_skill_has_its_own_effect() -> void:
	var db := BattleDB.load_default()
	var checked := 0
	for enc_id: StringName in db.encounters:
		var ch := _chapter(enc_id)
		if ch < 10 or ch > 16:
			continue
		for eid: Variant in (db.encounters[enc_id] as Dictionary).get("enemies", []):
			var row := db.enemies[StringName(str(eid))] as Dictionary
			var ids: Array = (row.get("skills", []) as Array).duplicate()
			for phase: Dictionary in row.get("phases", []):  # a boss's phase skills
				ids.append_array(phase.get("skills", []))
			for sid: Variant in ids:
				if str(sid) == "attack":
					continue  # the plain attack is the element hit
				var effect := str(((_fx["map"] as Dictionary)["skills"] as Dictionary).get(str(sid), ""))
				assert_ne(effect, "", "%s %s has its own effect" % [eid, sid])
				assert_true((_fx["effects"] as Dictionary).has(effect), "%s: effect %s exists" % [sid, effect])
				if ch >= 12 and ch <= 15 and effect != "":
					for l: Dictionary in ((_fx["effects"] as Dictionary)[effect] as Dictionary).get("layers", []):
						for sw: Variant in l.get("swatches", []):
							assert_false(ICE.has(str(sw)), "%s (Ch%d) has no ice: %s" % [sid, ch, sw])
				checked += 1
	assert_true(checked >= 8, "the Act II regulars' skills are covered (%d)" % checked)


static func _chapter(enc_id: StringName) -> int:
	var s := String(enc_id)
	return int(s.substr(2, 2)) if s.begins_with("ch") and s.substr(2, 2).is_valid_int() else 0


## M4-A2P-062: the Wakefin's fight is lit by the sea-glow alone. A hit's white core is dimmed there (dark_arenas),
## the sea-glow is not, and Sound Dive's glow rises at the fin's crest (on the water it was under the barge's rail).
func test_the_wakefin_fight_is_lit_by_the_sea_glow() -> void:
	var ctl := (load("res://game/battle/scene/battle_sandbox.tscn") as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle([&"rhen", &"toma"] as Array[StringName], [] as Array[StringName], &"ch15_wakefin", 20261030)
	var vfx := ctl.stage.get_node(^"BattleVfx") as BattleVfx
	var effects := _fx["effects"] as Dictionary
	var core := ((effects["hit_none"] as Dictionary)["layers"] as Array)[0] as Dictionary
	var glow := ((effects["sound_dive"] as Dictionary)["layers"] as Array)[0] as Dictionary
	assert_true(vfx.dark_scale(core) < 0.5, "the white core is dimmed in the dark (%.2f)" % vfx.dark_scale(core))
	assert_eq(vfx.dark_scale(glow), 1.0, "the sea-glow keeps its light")
	var fin := ctl.engine.enemies[0].id
	var at := vfx.anchor(fin, str((effects["sound_dive"] as Dictionary)["at"]))
	var home := ctl.stage.stand_in(fin).global_position
	assert_true(at.y >= home.y + 1.0, "the glow rises off the water at the fin's crest, over the barge's rail")
	assert_true(Vector2(at.x - home.x, at.z - home.z).length() < 0.1, "on the fin, not its near face against the hull")
	ctl.get_parent().remove_child(ctl)
	ctl.free()
	var lit := (load("res://game/battle/scene/battle_sandbox.tscn") as PackedScene).instantiate() as BattleController
	lit.auto_start = false
	lit.pacing_scale = 0.0
	lit.persist_progress = false
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(lit)
	lit.start_battle([&"rhen"] as Array[StringName], [] as Array[StringName], &"ch12_avalanche_ram", 20261030)
	assert_eq((lit.stage.get_node(^"BattleVfx") as BattleVfx).dark_scale(core), 1.0, "a lit fight keeps its cores")
	lit.get_parent().remove_child(lit)
	lit.free()
