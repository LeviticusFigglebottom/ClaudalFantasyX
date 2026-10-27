extends TestCase
## M3-BPR-412: the Act I party kits read on stage. Every skill in every hero's kit (characters.json) resolves to a
## real choreography style with a contract clip and camera shots; a ranged skill never runs to its target (Liss's
## Reel Shot casts her line from range); a heavy high-rank blow plays the finisher (Kerrid's Anchor Fall).

const RANGED: Array[String] = ["reel_shot"]
const HEAVY: Array[String] = ["anchor_fall"]


func test_every_kit_skill_has_a_real_style() -> void:
	var data := BattleChoreo.load_data()
	var db := BattleDB.load_default()
	var cam := data["camera"]["by_style"] as Dictionary
	var checked := 0
	for cid: StringName in db.characters:
		for sid: Variant in (db.characters[cid] as Dictionary).get("skills", []):
			var r := ActionResult.new()
			r.actor_id = cid
			r.skill_id = StringName(str(sid))  # style_by_skill, then by target, then by kind (BattleChoreoPlan)
			var engine_style := _style_for(data, db, r)
			assert_true(
				(data["styles"] as Dictionary).has(engine_style), "%s %s: a style (%s)" % [cid, sid, engine_style]
			)
			var st := BattleChoreoPlan.style(data, engine_style)
			assert_true(BattleClips.ALL.has(StringName(str(st["clip"]))), "%s %s: a contract clip" % [cid, sid])
			assert_true(cam.has(engine_style), "%s %s: camera shots for %s" % [cid, sid, engine_style])
			if RANGED.has(str(sid)):
				assert_ne(str(st.get("travel", "")), "target", "%s: cast from range, never a run" % sid)
			if HEAVY.has(str(sid)):
				assert_eq(engine_style, "finisher", "%s: the heavy blow plays the finisher" % sid)
			checked += 1
	assert_true(checked > 20, "the kits are checked (%d)" % checked)


func _style_for(data: Dictionary, db: BattleDB, r: ActionResult) -> String:
	var by_skill := data["style_by_skill"] as Dictionary
	if by_skill.has(String(r.skill_id)):
		return str(by_skill[String(r.skill_id)])
	var row := db.skill(r.skill_id)
	var by_target := data["style_by_target"] as Dictionary
	if by_target.has(str(row.get("target", ""))):
		return str(by_target[str(row["target"])])
	return str((data["style_by_kind"] as Dictionary).get(str(row.get("kind", "")), "melee"))
