extends TestCase
## M2-MNU-08: Light Step (encounter_rate_pct) reaches the field encounter meter. The rate counts the
## field heroes when nobody has joined, a gear change rescales the gap in progress (no new draw), and
## closing the Equip page refreshes every live meter.

const LIGHT_STEP := &"light_step"

var _saved: GameStateData


func before_each() -> void:
	_saved = Game.state
	Game.state = GameStateData.new()


func _teardown() -> void:
	Game.state = _saved


func test_light_step_on_worn_armor_halves_the_rate_even_before_anyone_joins() -> void:
	assert_eq(FieldEncounters.party_rate_pct(), FieldEncounters.FULL_RATE_PCT, "no gear: normal")
	var hero: StringName = FieldMenuModel.field_heroes()[0]
	_wear_light_step(hero)
	var effect := float(
		(ItemDB.load_default().ability(LIGHT_STEP).get("effect", {}) as Dictionary)["encounter_rate_pct"]
	)
	assert_eq(FieldEncounters.party_rate_pct(), effect, "the stand-in party's worn Light Step counts")
	_teardown()


func test_refresh_rescales_the_rest_of_the_gap_without_a_new_draw() -> void:
	var meter := FieldEncounters.new()
	meter.rate_pct = FieldEncounters.FULL_RATE_PCT
	meter.walked_m = 10.0
	meter.next_m = 30.0
	assert_eq(meter.refresh_rate(50.0), 50.0)
	assert_eq(meter.next_m, 50.0, "20 m left at full rate is 40 m at half")
	assert_eq(meter.refresh_rate(50.0), 50.0)
	assert_eq(meter.next_m, 50.0, "the same rate changes nothing")
	meter.walked_m = 60.0
	meter.refresh_rate(100.0)
	assert_eq(meter.next_m, 60.0, "a gap already passed stays due")
	meter.free()
	_teardown()


func test_closing_the_equip_page_refreshes_live_meters() -> void:
	var host := _host()
	var meter := FieldEncounters.new()
	meter.rate_pct = FieldEncounters.FULL_RATE_PCT
	meter.next_m = 40.0
	host.add_child(meter)
	meter.add_to_group(FieldEncounters.GROUP)
	_wear_light_step(FieldMenuModel.field_heroes()[0])
	var page := EquipMenu.create(PartySheet.new(Game.state, FieldMenuModel.field_heroes()))
	page.pause_tree = false
	host.add_child(page)
	page.close()
	assert_true(meter.rate_pct < FieldEncounters.FULL_RATE_PCT, "the meter took Light Step: %s" % meter.rate_pct)
	assert_true(meter.next_m > 40.0, "and the gap in progress grew")
	host.remove_child(page)
	page.free()
	host.remove_child(meter)
	meter.free()
	_teardown()


## A meter kept across a battle (M2-FP-28) keeps the rate its gap was scaled at, so gear changed while away
## still rescales the rest of the gap when the zone comes back.
func test_a_kept_meter_rescales_to_the_rate_on_return() -> void:
	var zone := GreyboxZone.new()
	zone.location_id = &"test_light_step_zone"
	FieldEncounters.meters[String(zone.location_id)] = {
		"walked_m": 10.0, "next_m": 30.0, "grace_m": 0.0, "rng_state": 1, "rate_pct": FieldEncounters.FULL_RATE_PCT
	}
	_wear_light_step(FieldMenuModel.field_heroes()[0])
	var meter := FieldEncounters.new()
	meter.setup(zone, {"min_m": 5.0, "max_m": 5.0})
	assert_true(meter.rate_pct < FieldEncounters.FULL_RATE_PCT, "the new rate: %s" % meter.rate_pct)
	var left := 20.0 * FieldEncounters.FULL_RATE_PCT / meter.rate_pct
	assert_true(is_equal_approx(meter.next_m, 10.0 + left), "20 m left grew to %s: %s" % [left, meter.next_m])
	FieldEncounters.meters.erase(String(zone.location_id))
	meter.free()
	zone.free()
	_teardown()


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _wear_light_step(hero: StringName) -> void:
	var db := ItemDB.load_default()
	var goods := PartyGoods.from_state(db, Game.state)
	var armor := StringName()
	for eid: StringName in db.equipment_order:
		if (
			db.slot_of(eid) == ItemDB.SLOT_ARMOR
			and db.character_of(eid) == hero
			and int(db.equipment_row(eid).get("slots", 0)) > 0
		):
			armor = eid
			break
	assert_ne(armor, &"", "an armor piece with a slot for %s" % hero)
	var uid := goods.equipment.add_piece(armor)
	var slot := goods.equipment.first_empty_slot(uid)
	assert_true(slot >= 0, "an empty slot")
	assert_true(goods.equipment.set_slot(uid, slot, LIGHT_STEP))
	assert_eq(goods.equipment.equip(hero, uid), EquipmentBag.RESULT_OK)
