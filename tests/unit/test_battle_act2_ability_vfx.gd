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
			for sid: Variant in (db.enemies[StringName(str(eid))] as Dictionary).get("skills", []):
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
