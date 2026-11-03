extends TestCase
## M3-CMB-03 (the human's playtest, 2026-11-03): the revive item, the Relighting Wick, is in the
## Act I economy: sold at Haluna's market from the first visit, dropped by the Ch1 and Ch4 bosses
## and (rarely) by the Gull Harrier, usable in battle and from the field menu.

const WICK := &"relighting_wick"

var db: ItemDB


func before_each() -> void:
	db = ItemDB.load_default()


func test_the_wick_is_a_field_usable_revive_priced_for_act_one() -> void:
	var row := db.item(WICK)
	assert_eq(row.get("category"), "consumable")
	assert_true(bool(row.get("field", false)), "usable from the field menu")
	assert_eq(int(row["price"]), 240, "four early fights (economy.md)")
	var act := ItemBattleAction.for_item(db, WICK)
	assert_true(act.targets_fallen)
	assert_true(act.targets_allies())
	assert_eq(tr("ITEM_RELIGHTING_WICK"), "Relighting Wick")


func test_haluna_market_sells_it_from_the_first_visit() -> void:
	var flags := FlagReader.new()
	flags.values["ch02_met_asha"] = true
	assert_true(Shop.new(db, &"haluna_market").stock(flags).has(WICK))


func test_the_ch1_and_ch4_bosses_always_drop_one() -> void:
	for pair: Array in [[&"ch01_hullgnaw", [&"rhen"]], [&"ch04_spar_wraith", [&"rhen", &"asha"]]]:
		var engine := BattleEngine.new()
		var active: Array[StringName] = []
		active.assign(pair[1])
		engine.setup(BattleDB.load_default(), active, [] as Array[StringName], pair[0], 7)
		engine.outcome = BattleEngine.OUTCOME_VICTORY
		assert_eq(int(BattleSpoils.roll_drops(engine).get(WICK, 0)), 1, str(pair[0]))


func test_the_gull_harrier_drops_it_rarely() -> void:
	var drops: Array = BattleDB.load_default().enemies[&"gull_harrier"]["drops"]
	var chance := 0
	for d: Variant in drops:
		if str((d as Dictionary)["item"]) == String(WICK):
			chance = int(d["chance"])
	assert_true(chance > 0 and chance <= 10, "a rare find: %d%%" % chance)
