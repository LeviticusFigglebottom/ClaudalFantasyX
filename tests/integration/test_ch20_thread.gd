extends Act2GreyboxCase
## M5-A3P-1011: Ch20 "The Undertow" on the real chapter data (chapters/ch20.json), headless: down the eye (U00), the six
## memory layers in vowbound.md's order (each its scene, its fight with the answering hero active, and on the return
## its release, which lifts the veil to the next floor), the two rests, the Cage (U07) and "Thank you." (U08).

const LAYERS := "res://game/levels/ch20/undertow_layers/undertow_layers.tscn"
const ORDER: Array[Array] = [
	[&"ilun", &"ysolde", "Veil2"],
	[&"kahre", &"kerrid", "Veil3"],
	[&"virel", &"toma", "Veil4"],
	[&"hesk", &"toma", "Veil6"],
	[&"nhoa", &"ysolde", "Veil7"],
	[&"ethren", &"ysolde", "Veil8"],
]


func test_the_ch19_engine_hands_off_to_the_dive() -> void:
	Game.set_flag(&"ch19_started")
	Game.set_flag(&"ch19_abiding_beaten")
	visit("res://game/levels/ch19/iskarra_spire/iskarra_spire.tscn")
	assert_true(bool(Game.get_flag(&"ch19_complete")))
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch20/undertow_layers", "spawn": "FirstFloor"}])
	after_visits()


func test_the_undertow_plays_in_order() -> void:
	Game.set_flag(&"ch19_complete")
	visit(LAYERS)
	assert_eq(Game.state.chapter, 20, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch20_started")), "U00: down the eye")
	assert_false((zone as Ch05Zone).block_shown("Veil1"), "the first flight opens once the Kite is down")
	assert_false(trigger_named(&"kahre").is_available(), "the layers go in order")
	for row in ORDER:
		_layer(row[0], row[1], row[2])
		if row[0] == &"virel":
			_rest(&"rest_one", &"ch20_rest_one", "Veil5")
		elif row[0] == &"ethren":
			_rest(&"rest_two", &"ch20_rest_two", "Veil9")
	assert_true(trigger_named(&"the_cage").on_touched())
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, &"ch20_the_cage", "U07: the Cage")
	assert_eq(r.victory_flag, &"ch20_cage_broken")
	assert_eq(r.active[0], &"toma", "Toma holds the line")
	Game.set_flag(&"ch20_cage_broken")
	visit(LAYERS)
	assert_true(bool(Game.get_flag(&"ch20_complete")), "U08: thank you")
	after_visits()


func _layer(v: StringName, hero: StringName, veil: String) -> void:
	assert_true(trigger_named(v).on_touched(), "%s's layer" % v)
	assert_true(not hand_offs.is_empty() and hand_offs.back()[0] == ZoneStory.KIND_BATTLE, "%s's fight" % v)
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, StringName("ch20_%s" % v))
	assert_eq(r.victory_flag, StringName("ch20_%s_beaten" % v))
	assert_eq(r.active[0], hero, "%s is answered by %s" % [v, hero])
	Game.set_flag(r.victory_flag)
	visit(LAYERS)
	assert_true(bool(Game.get_flag(StringName("ch20_%s_released" % v))), "%s's release" % v)
	assert_false((zone as Ch05Zone).block_shown(veil), "the flight down from %s's layer opens" % v)


func _rest(beat: StringName, flag: StringName, veil: String) -> void:
	assert_true(trigger_named(beat).on_touched(), "%s" % beat)
	assert_true(bool(Game.get_flag(flag)), "%s plays" % beat)
	assert_false((zone as Ch05Zone).block_shown(veil), "the flight down from the rest opens")
