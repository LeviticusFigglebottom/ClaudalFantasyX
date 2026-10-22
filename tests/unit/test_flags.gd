extends TestCase


func test_registry_loads_and_declares_test_flag() -> void:
	var reg := load("res://game/data/flags.tres") as FlagRegistry
	assert_true(reg != null, "flags.tres loads as FlagRegistry")
	assert_true(reg.is_declared(&"test_flag"))
	assert_false(reg.is_declared(&"definitely_not_a_flag"))
	assert_ne(reg.description(&"test_flag"), "")


func test_game_state_set_flag_round_trip() -> void:
	var game: Node = (load("res://game/core/game.gd") as GDScript).new()
	game.registry = load("res://game/data/flags.tres") as FlagRegistry
	game.state = GameStateData.new()
	game.state.flags["test_flag"] = 5
	assert_eq(game.get_flag(&"test_flag"), 5)
	game.free()
