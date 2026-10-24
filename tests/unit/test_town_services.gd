extends TestCase
## M2-UI-06: TownServices, the zone-agnostic hook. An Interactable whose payload is
## {"shop": id} opens ShopMenu and one with {"inn": id} opens InnMenu, in any zone with a
## FieldController (here the plain field test zone, which knows nothing about shops). Any other
## payload is ignored, and only one town menu is open at a time.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"

var zone: Node3D
var player: FieldController
var services: TownServices
var _saved_state: GameStateData


func before_each() -> void:
	_saved_state = Game.state
	Game.state = GameStateData.new()
	Game.set_flag(&"ch02_met_asha", true)
	Game.state.currency = 200
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_root().add_child(zone)
	player = zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	services = player.get_node("TownServices") as TownServices


func test_every_field_player_brings_the_hook() -> void:
	assert_true(services != null, "FieldController adds TownServices")
	assert_true(EventBus.is_connected(FieldEvents.INTERACTED, services._on_interacted), "listening on the bus")
	_done()


func test_a_shop_payload_opens_that_shop_over_the_live_save() -> void:
	var it := _interactable(&"test_stall", {"shop": "haluna_forge"})
	assert_true(it.try_interact())
	var m := services.menu as ShopMenu
	assert_true(m != null and m.is_open(), "the shop menu is open")
	assert_eq(m.model.shop.id, &"haluna_forge", "the payload's shop")
	assert_eq(m.title_text(), tr("SHOP_HALUNA_FORGE"))
	assert_true(m.model.party.wallet.state == Game.state, "over Game.state")
	assert_true(zone.get_tree().paused, "the field stops")
	assert_true(m.get_parent() is CanvasLayer and m.get_parent().get_parent() == services, "its layer hangs here")
	assert_true(it.try_interact(), "the interactable still fires")
	assert_true(services.menu == m, "but a second menu does not open")
	m.close()
	assert_true(services.menu == null)
	assert_false(zone.get_tree().paused)
	_done()


func test_an_inn_payload_opens_the_inn_and_resting_heals() -> void:
	Game.state.party_vitals = {"rhen": {"hp": 5}}
	var it := _interactable(&"test_bed", {"inn": "haluna_inn"})
	assert_true(it.try_interact())
	var m := services.menu as InnMenu
	assert_true(m != null and m.is_open(), "the inn menu is open")
	assert_eq(m.model.inn.id, &"haluna_inn")
	m.accept()
	assert_eq(Game.state.party_vitals, {}, "the rest healed the live party")
	assert_eq(Game.state.currency, 200 - m.model.inn.price())
	m.close()
	_done()


func test_other_payloads_are_ignored_and_a_factory_supplies_models() -> void:
	var it := _interactable(&"test_barrel", {"dialogue": "some_bark"})
	assert_true(it.try_interact())
	assert_true(services.menu == null, "not ours")
	assert_true(services.handle({}) == null)
	var asked: Array = []
	var db := ItemDB.load_default()
	services.model_factory = func(key: String, id: StringName) -> RefCounted:
		asked.append([key, id])
		var flags := FlagReader.new()
		return ShopMenuModel.new(db, Shop.new(db, id), PartyGoods.from_state(db, GameStateData.new()), flags)
	var m := services.handle({"shop": "haluna_market"})
	assert_eq(asked, [["shop", &"haluna_market"]])
	assert_true(m is ShopMenu)
	assert_eq((m as ShopMenu).model.closed_reason(), Shop.ERR_CLOSED, "the factory's own flags")
	m.close()
	_done()


func _interactable(iid: StringName, payload: Dictionary) -> Interactable:
	var it := Interactable.new()
	it.id = iid
	it.payload = payload
	zone.add_child(it)
	return it


func _done() -> void:
	zone.get_tree().paused = false
	_root().remove_child(zone)
	zone.free()
	Game.state = _saved_state


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root
