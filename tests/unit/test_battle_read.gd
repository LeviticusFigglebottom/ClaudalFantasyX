extends TestCase
## M1-CMB-03: the Read ability (BattleRead, SPEC §6.1). Headless on a fixture DB, plus a check
## that the live tables give Read to someone and every sandbox foe something to reveal.

const SEED := 11

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()


func test_read_reveals_stats_weaknesses_and_lore_and_costs_a_light_turn() -> void:
	_start()
	var crab := engine.enemies[0]
	crab.hp = 300
	crab.add_status(&"slow", 3)
	var now := engine.now
	var rng_before := engine.rng.state
	var r := engine.perform(&"read", _one(crab))
	assert_true(r.ok)
	assert_eq(engine.rng.state, rng_before, "Read rolls nothing")
	var hit: Dictionary = r.hits[0]
	assert_eq(int(hit["amount"]), 0, "no damage")
	assert_true(bool(hit["hit"]), "Read always lands")
	var rev: Dictionary = hit["read"]
	assert_eq(rev["enemy_id"], "crab", "the enemies.json id, not the field id")
	assert_eq(rev["target_id"], "crab#1")
	assert_eq(rev["name_key"], "ENEMY_CRAB")
	assert_eq(rev["lore_key"], "LORE_CRAB")
	assert_eq(rev["level"], 4)
	assert_eq([rev["hp"], rev["max_hp"], rev["mp"], rev["max_mp"]], [300, 380, 6, 6])
	var stats: Dictionary = rev["stats"]
	assert_eq(stats.keys().size(), BattleRead.STAT_KEYS.size())
	assert_eq(stats["defense"], 40)
	assert_eq(stats["agility"], 8)
	assert_eq(rev["affinities"]["weak"], ["lightning"] as Array[String])
	assert_eq(rev["affinities"]["absorb"], ["water"] as Array[String])
	assert_eq(rev["affinities"]["resist"], [] as Array[String])
	assert_eq(rev["delay_immune"], true)
	assert_eq(rev["statuses"], ["slow"] as Array[String])
	var reader := engine.find(&"reader")
	assert_eq(reader.next_time, now + Formulas.action_delay(reader.agility, 2), "rank 2")


func test_read_is_not_magic_so_silence_and_reflect_do_not_stop_it() -> void:
	_start()
	engine.find(&"reader").add_status(&"silence", 3)
	var crab := engine.enemies[0]
	crab.add_status(&"reflect", 3)
	var r := engine.perform(&"read", _one(crab))
	assert_true(r.ok)
	assert_eq(r.hits[0]["target_id"], crab.id)
	assert_false(r.hits[0].has("reflected_from"))


func test_a_plain_support_skill_reveals_nothing() -> void:
	_start()
	var r := engine.perform(&"guard", _one(engine.find(&"reader")))
	assert_true(r.ok)
	assert_false(r.hits[0].has("read"))


func test_a_party_member_has_no_enemy_row_to_reveal() -> void:
	var c := BattleCombatant.from_dict(&"rhen", BattleCombatant.TEAM_PARTY, {"name_key": "CHAR_RHEN"})
	var rev := BattleRead.reveal(c, {})
	assert_eq(rev["enemy_id"], "")
	assert_eq(rev["lore_key"], "")
	assert_eq(rev["name_key"], "CHAR_RHEN")


func test_affinities_list_in_spec_order_then_other_elements_sorted() -> void:
	var groups := BattleRead.affinity_groups(
		{
			&"ice": &"weak",
			&"fire": &"weak",
			&"zeta": &"weak",
			&"alpha": &"weak",
			&"holy": &"immune",
			&"water": &"normal"
		}
	)
	assert_eq(groups["weak"], ["fire", "ice", "alpha", "zeta"] as Array[String])
	assert_eq(groups["immune"], ["holy"] as Array[String])
	assert_eq(groups.keys(), ["weak", "resist", "immune", "absorb"], "normal is never listed")
	assert_true(BattleRead.is_read({"read": true}))
	assert_false(BattleRead.is_read({}))


func test_the_live_tables_teach_read_and_every_foe_has_lore() -> void:
	var db := BattleDB.load_default()
	var read := db.skill(&"read")
	assert_true(BattleRead.is_read(read))
	assert_eq(read["kind"], "support")
	assert_eq(read["target"], "single_foe")
	assert_eq(int(read["mp_cost"]), 0)
	var learned := false
	for cid: StringName in db.characters:
		learned = learned or (db.characters[cid]["skills"] as Array).has("read")
	assert_true(learned, "a hero knows Read")
	assert_true((db.characters[&"ysolde"]["skills"] as Array).has("read"), "Ysolde, Asha's tutor")
	for eid: StringName in db.enemies:
		var key := str(db.enemies[eid].get("lore_key", ""))
		assert_ne(key, "", "%s has a lore_key" % eid)
		assert_ne(TranslationServer.translate(key), key, "%s's lore is localized" % eid)


# --- helpers -------------------------------------------------------------------------------------


func _start() -> void:
	engine.setup(_db(), _ids(["reader"]), _ids([]), &"reef", SEED)
	engine.opening = BattleOpening.PREEMPTIVE  # the reader acts first
	engine.begin()
	assert_eq(engine.current.id, &"reader")


static func _one(c: BattleCombatant) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [c]
	return out


static func _ids(list: Array) -> Array[StringName]:
	var out: Array[StringName] = []
	for v: Variant in list:
		out.append(StringName(str(v)))
	return out


static func _db() -> BattleDB:
	var crab_stats := {
		"level": 4,
		"hp": 380,
		"mp": 6,
		"strength": 12,
		"magic": 2,
		"defense": 40,
		"magic_defense": 4,
		"agility": 8,
		"accuracy": 8,
		"evasion": 2,
		"luck": 4,
	}
	var reader_stats := crab_stats.duplicate()
	reader_stats["agility"] = 13
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "attack", "kind": "physical", "power": 1, "rank": 3, "target": "single_foe"},
					{"id": "read", "kind": "support", "rank": 2, "target": "single_foe", "read": true},
					{"id": "guard", "kind": "support", "rank": 2, "target": "self"},
				],
				"statuses":
				[
					{"id": "slow", "default_duration": 3},
					{"id": "silence", "default_duration": 3},
					{"id": "reflect", "default_duration": 3},
				],
				"characters": [{"id": "reader", "stats": reader_stats, "skills": ["attack", "read", "guard"]}],
				"enemies":
				[
					{
						"id": "crab",
						"name_key": "ENEMY_CRAB",
						"lore_key": "LORE_CRAB",
						"stats": crab_stats,
						"skills": ["attack"],
						"affinities": {"lightning": "weak", "water": "absorb"},
						"delay_immune": true,
						"ai": [{"pick": [{"skill": "attack", "target": "random_foe"}]}],
					}
				],
				"encounters": [{"id": "reef", "enemies": ["crab"]}],
			}
		)
	)
