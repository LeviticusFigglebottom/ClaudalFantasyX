extends TestCase
## ItemBattleAction: the battle-use API Combat consumes in M1-CMB-06 (M1-PRG-02).

var db: ItemDB


func before_each() -> void:
	db = ItemDB.load_default()


func _hero(hp: int = 100, max_hp: int = 400) -> BattleCombatant:
	var c := BattleCombatant.new()
	c.id = &"rhen"
	c.max_hp = max_hp
	c.hp = hp
	c.max_mp = 50
	c.mp = 10
	c.agility = 10
	return c


func test_non_battle_items_have_no_action() -> void:
	assert_true(ItemBattleAction.for_item(db, &"ember_coral") == null)
	assert_true(ItemBattleAction.for_item(db, &"brass_lantern") == null)
	assert_true(ItemBattleAction.for_item(db, &"no_such_item") == null)


func test_tonic_describes_its_action() -> void:
	var a := ItemBattleAction.for_item(db, &"salt_tonic")
	assert_eq(a.target, &"single_ally")
	assert_true(a.rank > 0)
	assert_true(a.targets_allies())
	assert_false(a.targets_fallen)
	assert_eq(a.effects.size(), 1)
	assert_eq(a.name_key, "ITEM_SALT_TONIC")


func test_heal_is_fixed_and_clamped_to_max() -> void:
	var c := _hero(100, 250)
	var r := ItemBattleAction.for_item(db, &"salt_tonic").resolve_on(c)
	assert_eq(c.hp, 250)
	assert_eq(r["amount"], -150, "engine convention: healing is negative HP lost")


func test_mp_restore_clamps() -> void:
	var c := _hero()
	var r := ItemBattleAction.for_item(db, &"quiet_tea").resolve_on(c)
	assert_eq(c.mp, 40)
	assert_eq(r["mp_amount"], 30)


func test_cure_removes_only_listed_statuses() -> void:
	var c := _hero()
	c.add_status(&"poison", -1)
	c.add_status(&"haste", 3)
	var r := ItemBattleAction.for_item(db, &"bitterleaf").resolve_on(c)
	assert_false(c.has_status(&"poison"))
	assert_true(c.has_status(&"haste"))
	assert_eq(r["statuses_removed"], [&"poison"])


func test_revive_targets_only_the_fallen() -> void:
	var a := ItemBattleAction.for_item(db, &"relighting_wick")
	assert_true(a.targets_fallen)
	var alive := _hero(50, 400)
	assert_false(a.can_target(alive))
	a.resolve_on(alive)
	assert_eq(alive.hp, 50, "a living ally is untouched")
	var down := _hero(0, 400)
	assert_true(a.can_target(down))
	var r := a.resolve_on(down)
	assert_eq(down.hp, 100, "25% of 400")
	assert_true(r["revived"])
	var still_down := _hero(0, 400)
	var tonic := ItemBattleAction.for_item(db, &"salt_tonic")
	assert_false(tonic.can_target(still_down), "tonics can't raise the dead")
	tonic.resolve_on(still_down)
	assert_eq(still_down.hp, 0)


func test_revive_hp_formula() -> void:
	assert_eq(ItemBattleAction.revive_hp(400, 25), 100)
	assert_eq(ItemBattleAction.revive_hp(3, 25), 1, "never revives at 0")
	assert_eq(ItemBattleAction.revive_hp(421, 25), 105)


func test_drag_net_delays_by_ranks() -> void:
	var c := _hero()
	c.next_time = 50
	var r := ItemBattleAction.for_item(db, &"drag_net").resolve_on(c)
	assert_eq(r["delay_ticks"], Formulas.base_delay(10) * 2)
	assert_eq(c.next_time, 250)


func test_quickwater_adds_haste() -> void:
	var c := _hero()
	var r := ItemBattleAction.for_item(db, &"quickwater").resolve_on(c)
	assert_true(c.has_status(&"haste"))
	assert_eq(r["statuses_added"], [&"haste"])


func test_fixed_damage_uses_element_ratio() -> void:
	assert_eq(ItemBattleAction.fixed_damage(150, &"normal"), 150)
	assert_eq(ItemBattleAction.fixed_damage(150, &"weak"), 225)
	assert_eq(ItemBattleAction.fixed_damage(150, &"resist"), 75)
	assert_eq(ItemBattleAction.fixed_damage(150, &"immune"), 0)
	assert_eq(ItemBattleAction.fixed_damage(150, &"absorb"), -150)
	assert_eq(ItemBattleAction.fixed_damage(20000, &"normal"), Formulas.DAMAGE_CAP)
	var c := _hero(400, 400)
	c.affinities[&"fire"] = &"weak"
	var r := ItemBattleAction.for_item(db, &"ember_pot").resolve_on(c)
	assert_eq(c.hp, 175)
	assert_eq(r["amount"], 225)


func test_usable_items_and_consume() -> void:
	var inv := Inventory.new(db)
	inv.add(&"ember_coral", 3)
	inv.add(&"relighting_wick", 1)
	inv.add(&"salt_tonic", 2)
	inv.add(&"brass_lantern", 1)
	assert_eq(ItemBattleAction.usable_items(db, inv), [&"salt_tonic", &"relighting_wick"] as Array[StringName])
	var a := ItemBattleAction.for_item(db, &"relighting_wick")
	assert_true(a.consume(inv))
	assert_false(a.consume(inv))
	assert_eq(inv.count(&"relighting_wick"), 0)


func test_resolution_is_deterministic() -> void:
	var a := _hero(10, 400)
	var b := _hero(10, 400)
	var act := ItemBattleAction.for_item(db, &"reef_draught")
	assert_eq(act.resolve_on(a), act.resolve_on(b))
