extends TestCase
## M2-UI-06's last criterion, placed by the m2-slice track: Haluna's market stall, the Net-Rack Forge
## and the Mooring Lamp inn in the zone. Their prompts wait for Cutscene A, open the right menu over
## TownServices, and the keepers are gone home at night.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const KEEPERS := {
	&"npc_shop_market": {"shop": "haluna_market"},
	&"npc_shop_forge": {"shop": "haluna_forge"},
	&"npc_inn": {"inn": "haluna_inn"},
}

var zone: HalunaZone
var saved_state: GameStateData


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	(zone.get_node("Story") as HalunaStory).autostart = false
	_host().add_child(zone)
	zone.player.set_physics_process(false)


func test_each_keeper_opens_their_menu_after_cutscene_a() -> void:
	var services := zone.player.find_children("*", "TownServices", true, false)
	assert_eq(services.size(), 1, "the player brings TownServices")
	var town := services[0] as TownServices
	for id: StringName in KEEPERS:
		var it := _interactable(id)
		assert_true(it != null, "%s placed" % id)
		assert_eq(it.payload, KEEPERS[id])
		assert_false(it.is_available(), "%s waits for Cutscene A" % id)
	Game.set_flag(&"ch02_met_asha", true)
	for id: StringName in KEEPERS:
		assert_true(_interactable(id).try_interact(), "%s answers" % id)
		var m := town.menu
		assert_true(m != null and m.is_open(), "%s opens a menu" % id)
		if KEEPERS[id].has("shop"):
			assert_true(m is ShopMenu and (m as ShopMenu).model.shop.id == StringName(KEEPERS[id]["shop"]))
		else:
			assert_true(m is InnMenu and (m as InnMenu).model.inn.id == &"haluna_inn")
		m.close()
	assert_false(zone.get_tree().paused)
	_done()


func test_the_keepers_go_home_at_night() -> void:
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_HALUNA)
	zone.set_night(cfg.get("night", {}), cfg.get("night_hide", []))
	for id: StringName in KEEPERS:
		var it := _interactable(id)
		# Hidden and stopped, not freed (the VillagerLayer still holds them): no prompt, nothing to see.
		assert_true(it == null or (not it.is_visible_in_tree() and not it.can_process()), "%s gone at night" % id)
	_done()


func _interactable(id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if is_instance_valid(n) and not n.is_queued_for_deletion() and (n as Interactable).id == id:
			return n as Interactable
	return null


func _done() -> void:
	if zone != null and is_instance_valid(zone):
		_host().remove_child(zone)
		zone.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
