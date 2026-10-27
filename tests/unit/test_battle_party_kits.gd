extends TestCase
## M3-BPR-412: the Act I party kits read on stage. Every skill in every hero's kit (characters.json) resolves to a
## real choreography style with a contract clip and camera shots; a ranged skill never runs to its target (Liss's
## Reel Shot casts her line from range); a heavy high-rank blow plays the finisher (Kerrid's Anchor Fall).

const RANGED: Array[String] = ["reel_shot"]
const HEAVY: Array[String] = ["anchor_fall"]
## The foes' heaviest blows (Hullgnaw's Gnaw, the Matron's Ladle Swing, the hound's Pounce) play the finisher.
const HEAVY_FOE: Array[String] = ["gnaw", "ladle_swing", "pounce"]


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


## M3-BPR-412/413/414 (the Lead's 19:35 items 1-3): every Swell technique, every Vowbound skill and every enemy skill
## resolves, through the real BattleChoreoPlan.style_id_for, to a style with a contract clip and camera shots.
func test_every_swell_vowbound_and_enemy_skill_has_a_real_style() -> void:
	var data := BattleChoreo.load_data()
	var engine := BattleEngine.new()
	engine.db = BattleDB.load_default()
	var cases: Array = []  # [[actor id, skill id], ...]
	for sid: StringName in engine.db.skills:
		if bool((engine.db.skills[sid] as Dictionary).get("swell", false)):
			cases.append([&"asha", sid])
	for row: Dictionary in BattleVowbound.load_config():
		for sid: Variant in row.get("skills", []):
			cases.append([StringName(str(row["id"])), StringName(str(sid))])
	for eid: StringName in engine.db.enemies:
		for sid: Variant in (engine.db.enemies[eid] as Dictionary).get("skills", []):
			cases.append([StringName("%s#1" % eid), StringName(str(sid))])
	var cam := data["camera"]["by_style"] as Dictionary
	for c: Array in cases:
		var r := ActionResult.new()
		r.actor_id = c[0]
		r.skill_id = c[1]
		var style_id := BattleChoreoPlan.style_id_for(data, engine, r)
		assert_true((data["styles"] as Dictionary).has(style_id), "%s %s: a style (%s)" % [c[0], c[1], style_id])
		var st := BattleChoreoPlan.style(data, style_id)
		assert_true(BattleClips.ALL.has(StringName(str(st["clip"]))), "%s %s: a contract clip" % c)
		assert_true(cam.has(style_id), "%s %s: camera shots for %s" % [c[0], c[1], style_id])
	assert_true(cases.size() > 60, "the Swells, Vowbound and foes are checked (%d)" % cases.size())


## The audit's fill (the Lead, 20:26): a foe never runs at one hero for a blow that is ranged (its creature row plays
## the cast clip: the crab's Brine Spit) or that strikes the whole party (the Spar-Wraith's Shroud Sweep, the Reach's
## Undertow Pull); it stays in its place. A foe's heaviest blow plays the finisher.
func test_foes_stage_ranged_sweeping_and_heavy_blows_by_their_reach() -> void:
	var data := BattleChoreo.load_data()
	var engine := BattleEngine.new()
	engine.db = BattleDB.load_default()
	var creatures := CreatureActor.data().get("creatures", {}) as Dictionary
	var checked := 0
	for eid: StringName in engine.db.enemies:
		var by_skill := (creatures.get(String(eid), {}) as Dictionary).get("clip_by_skill", {}) as Dictionary
		for sid: Variant in (engine.db.enemies[eid] as Dictionary).get("skills", []):
			var row := engine.db.skill(StringName(str(sid)))
			var r := ActionResult.new()
			r.actor_id = StringName("%s#1" % eid)
			r.skill_id = StringName(str(sid))
			var style_id := BattleChoreoPlan.style_id_for(data, engine, r)
			var travel := str(BattleChoreoPlan.style(data, style_id).get("travel", ""))
			var ranged := str(by_skill.get(str(sid), "")) == "cast"
			var sweep := str(row.get("kind", "")) == "physical" and str(row.get("target", "")) == "all_foes"
			if ranged or sweep:
				assert_ne(travel, "target", "%s %s: no run at one hero (%s)" % [eid, sid, style_id])
				checked += 1
			if HEAVY_FOE.has(str(sid)):
				assert_eq(style_id, "finisher", "%s %s: the heavy blow plays the finisher" % [eid, sid])
	assert_true(checked >= 4, "ranged and sweeping foe skills are checked (%d)" % checked)


## The staging audit's "parts look primitive" pass: every hero has its own stand-in until its model lands (Kerrid's and
## Liss's sheets give their height), and its own timeline tint, never the shared default nor another hero's.
func test_every_hero_has_its_own_stand_in_and_tint() -> void:
	var db := BattleDB.load_default()
	var rows := BattleStage.config()["stand_ins"] as Dictionary
	var seen: Dictionary = {}
	for cid: StringName in db.characters:
		assert_true(rows.has(String(cid)), "%s has a stand-in row" % cid)
		var tint := str(BattleStage.stand_in_spec(cid).get("tint", "")).to_upper()
		assert_ne(tint, "", "%s has a tint" % cid)
		assert_false(seen.has(tint), "%s's tint %s is its own (also %s)" % [cid, tint, seen.get(tint, "")])
		seen[tint] = cid


func _style_for(data: Dictionary, db: BattleDB, r: ActionResult) -> String:
	var by_skill := data["style_by_skill"] as Dictionary
	if by_skill.has(String(r.skill_id)):
		return str(by_skill[String(r.skill_id)])
	var row := db.skill(r.skill_id)
	var by_target := data["style_by_target"] as Dictionary
	if by_target.has(str(row.get("target", ""))):
		return str(by_target[str(row["target"])])
	return str((data["style_by_kind"] as Dictionary).get(str(row.get("kind", "")), "melee"))
