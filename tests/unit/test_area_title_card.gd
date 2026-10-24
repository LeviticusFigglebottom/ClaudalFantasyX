extends TestCase
## M2-UI-21: the area title card. Driven by advance() with the location set directly (no field
## controller); the session memory (AreaTitleCard.last_shown) is reset around every test.

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	(Engine.get_main_loop() as SceneTree).paused = false
	UiSettings.set_shared(UiSettings.new())
	AreaTitleCard.forget()


func test_it_cards_the_location_once_then_fades() -> void:
	var d := AreaTitleCard.load_data()
	var card := _card(&"ch02/haluna")
	assert_eq(card.name_text(), tr("LOCATION_CH02_HALUNA"))
	assert_false(card.is_showing(), "waits for the first frame the field takes input")
	card.advance(0.0)
	assert_true(card.is_showing())
	assert_eq(AreaTitleCard.last_shown, &"ch02/haluna")
	card.advance(float(d["in_sec"]) + 0.01)
	assert_eq(card.phase, AreaTitleCard.Phase.HOLD)
	assert_between(card.visibility(), 0.999, 1.001)
	card.advance(float(d["hold_sec"]) + 0.01)
	card.advance(float(d["out_sec"]) + 0.01)
	assert_false(card.is_showing(), "then it is gone")
	var again := _card(&"ch02/haluna")
	again.advance(0.0)
	assert_false(again.is_showing(), "the same location again (a reload, a door back): no card")
	var next := _card(&"ch03/shell_shrine")
	next.advance(0.0)
	assert_true(next.is_showing(), "a new location: its card")
	AreaTitleCard.forget()
	var fresh := _card(&"ch03/shell_shrine")
	fresh.advance(0.0)
	assert_true(fresh.is_showing(), "after the title screen: shown again")
	_done()


func test_test_rooms_and_unknown_scenes_get_none() -> void:
	var skip := _card(&"field_test")
	skip.advance(0.0)
	assert_false(skip.is_showing(), "skip_locations")
	var none := _card(&"")
	none.advance(0.0)
	assert_false(none.is_showing(), "a scene that is no location")
	_done()


func test_a_menu_ends_it_and_reduced_motion_does_not_rise() -> void:
	var card := _card(&"ch02/haluna")
	card.advance(0.0)
	assert_true(card.position.y > 0.0, "it rises into place")
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	card.advance(0.01)
	assert_eq(card.position.y, 0.0, "reduced motion: no rise")
	(Engine.get_main_loop() as SceneTree).paused = true
	card.advance(0.01)
	assert_false(card.is_showing(), "a menu took over: gone")
	(Engine.get_main_loop() as SceneTree).paused = false
	card.advance(0.01)
	assert_false(card.is_showing(), "and it does not come back")
	_done()


func test_the_location_comes_from_the_scene_path() -> void:
	assert_eq(AreaTitleCard.location_for_scene("res://game/levels/ch02/haluna/haluna.tscn"), &"ch02/haluna")
	assert_eq(AreaTitleCard.location_for_scene("res://nowhere.tscn"), &"")
	_done()


func _card(loc: StringName) -> AreaTitleCard:
	var c := AreaTitleCard.new()
	c.location = loc
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(c)
	made.append(c)
	return c


func _done() -> void:
	AreaTitleCard.forget()
	UiSettings.set_shared(null)
