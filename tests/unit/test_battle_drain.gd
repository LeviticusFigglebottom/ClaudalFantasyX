extends TestCase
## M4-CMB-1001: a skill row's `drain_pct` heals its user by that share of the HP its hit took (formulas.md § Damage,
## "Drain"). The fen leech's bite is the first user.

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	var active: Array[StringName] = [&"hero"]
	engine.setup(_db(), active, [] as Array[StringName], &"one", 1)
	engine.begin()


func test_a_drain_hit_heals_its_user_by_its_share() -> void:
	var foe := engine.enemies[0]
	var hero := engine.party_active[0]
	foe.hp = foe.max_hp / 2
	var hit := BattleHits.resolve(engine, foe, hero, engine.db.skill(&"bite"))
	var lost := int(hit["amount"])
	assert_true(lost > 0, "the bite lands")
	assert_eq(int(hit["drained"]), Formulas.drain_heal(lost, 50), "half of what it took")
	assert_eq(foe.hp, foe.max_hp / 2 + int(hit["drained"]), "the leech is healed by it")


func test_a_full_user_drains_nothing_and_a_plain_hit_never_drains() -> void:
	var foe := engine.enemies[0]
	var hero := engine.party_active[0]
	var hit := BattleHits.resolve(engine, foe, hero, engine.db.skill(&"bite"))
	assert_eq(int(hit["drained"]), 0, "at full HP there is nothing to win back")
	assert_eq(foe.hp, foe.max_hp)
	var plain := BattleHits.resolve(engine, foe, hero, engine.db.skill(&"attack"))
	assert_false(plain.has("drained"), "only a drain_pct skill drains")


func test_a_drain_on_an_absorbing_target_drains_nothing() -> void:
	var foe := engine.enemies[0]
	var hero := engine.party_active[0]
	foe.hp = 10
	hero.affinities[&"water"] = &"absorb"
	var hit := BattleHits.resolve(engine, foe, hero, engine.db.skill(&"wet_bite"))
	assert_true(int(hit["amount"]) <= 0, "the hero drinks the water")
	assert_false(hit.has("drained"))
	assert_eq(foe.hp, 10)


static func _db() -> BattleDB:
	var hero := {
		"level": 5,
		"hp": 400,
		"mp": 20,
		"strength": 10,
		"magic": 10,
		"defense": 5,
		"magic_defense": 5,
		"agility": 30,
		"accuracy": 0,
		"evasion": 0,
		"luck": 0,
	}
	var foe := hero.duplicate()
	foe["agility"] = 5
	foe["hp"] = 900
	foe["mp"] = 0
	foe["strength"] = 30
	var basic := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "attack", "kind": "physical", "power": 4, "rank": 3, "accuracy": 100},
					{"id": "bite", "kind": "physical", "power": 6, "rank": 3, "accuracy": 100, "drain_pct": 50},
					{
						"id": "wet_bite",
						"kind": "magical",
						"power": 6,
						"rank": 3,
						"element": "water",
						"magic": true,
						"drain_pct": 50
					},
				],
				"statuses": [],
				"characters": [{"id": "hero", "stats": hero, "skills": ["attack"]}],
				"enemies": [{"id": "leech", "stats": foe, "skills": ["attack", "bite", "wet_bite"], "ai": basic}],
				"encounters": [{"id": "one", "enemies": ["leech"]}],
			}
		)
	)
