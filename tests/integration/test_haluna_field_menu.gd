extends TestCase
## M2-UI-04 in the Haluna zone (the M2 slice): Asha and Toma join after Cutscene A, so the field
## menu's Heroes page lists the real party (no fallback), and Escape opens the menu in free play
## but never while a scene holds Rhen.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"

var zone: HalunaZone
var story: HalunaStory
var saved_state: GameStateData


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	story = zone.get_node("Story") as HalunaStory
	story.autostart = false
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	story.active = true
	story.sequencer.instant = true
	story.hand_off = func(_kind: StringName, _target: String) -> void: pass


func test_asha_and_toma_join_after_cutscene_a() -> void:
	assert_eq(Game.state.party_ids, [] as Array[StringName], "nobody before the beach")
	story.begin()
	assert_true(bool(Game.get_flag(&"ch02_met_asha")), "Cutscene A played")
	assert_eq(Game.state.party_ids, [&"rhen", &"asha"] as Array[StringName])
	assert_eq(Game.state.reserve_ids, [&"toma"] as Array[StringName])
	assert_eq(FieldMenuModel.from_game().heroes, [&"rhen", &"asha", &"toma"] as Array[StringName])
	story.begin()
	assert_eq(Game.state.party_ids.size(), 2, "joining is once")
	_done()


func test_a_save_from_after_the_beach_gets_its_party_on_arrival() -> void:
	Game.set_flag(&"ch02_met_asha", true)
	story.begin()
	assert_eq(Game.state.party_ids, [&"rhen", &"asha"] as Array[StringName])
	_done()


func test_escape_opens_the_field_menu_in_free_play_but_not_in_a_scene() -> void:
	story.begin()
	var player := zone.player
	assert_true(player.accepts_input, "free play after Cutscene A")
	player.accepts_input = false  # as a scene holds him
	player._unhandled_input(_ev(FieldMenu.OPEN_ACTION))
	assert_eq(_menus_under(player).size(), 0, "no menu while a scene holds Rhen")
	player.accepts_input = true
	player._unhandled_input(_ev(FieldMenu.OPEN_ACTION))
	var found := _menus_under(player)
	assert_eq(found.size(), 1, "Escape opens the field menu in Haluna")
	if found.size() == 1:
		assert_true(zone.get_tree().paused)
		found[0].close()
	assert_false(zone.get_tree().paused)
	zone.get_tree().paused = false
	_done()


func _menus_under(n: Node) -> Array[FieldMenu]:
	var out: Array[FieldMenu] = []
	for child in n.get_children():
		if child is CanvasLayer:
			for m in child.get_children():
				if m is FieldMenu:
					out.append(m as FieldMenu)
	return out


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _done() -> void:
	if zone != null:
		_host().remove_child(zone)
		zone.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
