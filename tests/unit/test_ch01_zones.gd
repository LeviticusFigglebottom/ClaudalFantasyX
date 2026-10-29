extends TestCase
## M3-C01-02: the Ch1 zone roots (game/levels/ch01/): Ch01Zone's story calls (a rest, items
## and lume in and out, one-time prompts, blocks gone and back), the Underway's lantern shutter (the
## light, the encounter-rate multiplier, the reveal) and Oruvel's storm variant (up from the flag on
## entry, the light and the cast, the lashed low hull).

const UNDERWAY := "res://game/levels/ch01/oruvel_underway/oruvel_underway.tscn"
const ORUVEL := "res://game/levels/ch01/oruvel/oruvel.tscn"

var zone: Ch01Zone
var saved_state: GameStateData
var heals: Array[StringName] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	heals.clear()


func test_the_zone_calls_change_the_game() -> void:
	_open(UNDERWAY)
	zone.give({"salt_tonic": 3, "lit_age_brass": 1}, 25)
	assert_eq(_count(&"salt_tonic"), 3)
	assert_eq(Game.state.currency, 25)
	zone.give({"salt_tonic": -1, "lit_age_brass": -5}, 0)
	assert_eq(_count(&"salt_tonic"), 2, "a negative count takes items away")
	assert_eq(_count(&"lit_age_brass"), 0, "never more than the bag holds")
	var on_heal := func(source: StringName) -> void: heals.append(source)
	EventBus.party_full_heal_requested.connect(on_heal)
	zone.rest("ch01_bell_room_1")
	EventBus.party_full_heal_requested.disconnect(on_heal)
	assert_eq(heals, [&"ch01_bell_room_1"] as Array[StringName], "a rest is the shrine's full heal")
	assert_eq(zone.rests, 1)
	_done()


func test_a_prompt_plays_once_by_its_seen_flag() -> void:
	_open(UNDERWAY)
	var shown: Array[StringName] = []
	zone.hint.line_shown.connect(func(s: DialogueStep) -> void: shown.append(s.line_id))
	assert_false(zone.hint.hold_player, "a prompt never holds the player")
	assert_true(zone.prompt("shutter"))
	assert_true(bool(Game.get_flag(&"tut_shutter_seen")))
	assert_eq(shown, [&"ch01_tut_003"] as Array[StringName])
	# M2-FP-30: the line names the shutter's binding, so it follows a rebind and the last device.
	var filled := InputNames.fill(tr("DLG_CH01_TUT_003"), false)
	assert_false(filled.contains("{"), "the shutter's action is named: %s" % filled)
	assert_false(zone.prompt("shutter"), "only once")
	assert_false(zone.prompt("no_such_prompt"))
	assert_eq(shown.size(), 1)
	_done()


func test_a_block_goes_with_its_collision() -> void:
	_open(UNDERWAY)
	var shape := zone.get_node("Greybox/CoralCurtain/Shape") as CollisionShape3D
	assert_true(zone.block_shown("CoralCurtain") and not shape.disabled)
	zone.hide_block("CoralCurtain")
	assert_false(zone.block_shown("CoralCurtain"))
	assert_true(shape.disabled, "and no longer blocks")
	zone.show_block("CoralCurtain")
	assert_true(zone.block_shown("CoralCurtain") and not shape.disabled)
	_done()


func test_the_shutter_widens_the_light_and_finds_the_tin() -> void:
	_open(UNDERWAY)
	var uw := zone as Ch01UnderwayZone
	var lamp: Dictionary = uw.field["lantern"]
	assert_true(uw.lantern.get_parent() == uw.player, "the lamp rides on Rhen")
	assert_false(uw.shutter_open)
	assert_eq(uw.lantern.omni_range, float(lamp["narrow"]["range_m"]))
	assert_eq(uw.encounter_rate_mult(), float(lamp["narrow"]["encounter_rate_mult"]))
	var tin := zone.get_node("Triggers/old_tin") as Interactable
	assert_false(tin.is_in_group(Interactable.GROUP), "hidden until the light finds it")
	uw.set_shutter(true)
	assert_eq(uw.lantern.omni_range, float(lamp["open"]["range_m"]))
	assert_true(uw.lantern.omni_range > float(lamp["narrow"]["range_m"]), "open is wider")
	assert_true(uw.encounter_rate_mult() > 1.0, "and draws more")
	assert_true(tin.is_in_group(Interactable.GROUP) and not uw.block_shown("CoralCurtain"))
	uw.set_shutter(false)
	assert_eq(uw.encounter_rate_mult(), float(lamp["narrow"]["encounter_rate_mult"]))
	assert_true(tin.is_in_group(Interactable.GROUP), "a found way stays found")
	assert_true(InputMap.has_action(StringName(str(lamp["action"]))), "the shutter's input is bound")
	_done()


func test_oruvel_comes_up_in_the_storm_once_the_gulls_have_cried() -> void:
	_open(ORUVEL)
	var town := zone as Ch01OruvelZone
	var day_energy := town.sun.light_energy
	assert_false(town.storm)
	assert_true(town.block_shown("SeventhTerrace") and town.block_shown("cook"), "the day's town")
	assert_false(town.block_shown("StormWall") or town.block_shown("pen_child_2"), "no storm yet")
	town.set_storm(true)
	assert_true(town.sun.light_energy < day_energy, "the storm light")
	assert_false(town.block_shown("SeventhTerrace") or town.block_shown("cook") or town.block_shown("DiveBridge"))
	var undertow := town.get_node_or_null(^"Undertow") as Node3D
	var wall := town.block_shown("StormWall") or (undertow != null and undertow.visible)
	assert_true(wall and town.block_shown("pen_child_2"), "the storm stands up (the Undertow, or its greybox wall)")
	_done()
	Game.set_flag(&"ch01_gulls_cried")
	_open(ORUVEL)
	assert_true((zone as Ch01OruvelZone).storm, "a zone entered after the gulls is in the storm")
	_done()


func test_the_low_hull_drifts_clear_after_both_lashings() -> void:
	_open(ORUVEL)
	var town := zone as Ch01OruvelZone
	town.refresh_rig()
	assert_true(town.block_shown("LowHull"))
	Game.set_flag(&"ch01_cut_lashing_a")
	town.refresh_rig()
	assert_true(town.block_shown("LowHull"), "one lashing holds it")
	Game.set_flag(&"ch01_cut_lashing_b")
	town.refresh_rig()
	assert_false(town.block_shown("LowHull"), "two and it drifts clear")
	_done()


func _open(path: String) -> void:
	zone = (load(path) as PackedScene).instantiate() as Ch01Zone
	zone.story.autostart = false
	_host().add_child(zone)
	zone.set_process(false)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.hint.instant = true


func _count(item: StringName) -> int:
	return Inventory.new(ItemDB.load_default(), Game.state.inventory).count(item)


func _done() -> void:
	if zone != null:
		_host().remove_child(zone)
		zone.free()
		zone = null
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
