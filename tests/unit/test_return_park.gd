extends TestCase
## ReturnPark (PC pass 7 row 74: a fight's cross-zone return built while the fight runs). The runner steps no frame,
## so the build itself is measured in a child process (test_battle_return); here: what take(), holds() and drop() do
## with a parked root, and that a scene that doesn't exist parks nothing.


func _park() -> ReturnPark:
	return ReturnPark.new(Engine.get_main_loop() as SceneTree)


func test_take_hands_over_the_parked_root_once() -> void:
	var park := _park()
	var root := Node3D.new()
	park.node = root
	park.path = "res://a.tscn"
	assert_true(park.holds("res://a.tscn"), "a parked scene is held")
	assert_false(park.holds("res://b.tscn"), "another scene is not")
	assert_eq(await park.take("res://b.tscn"), null, "another scene's change gets nothing")
	assert_eq(await park.take("res://a.tscn"), root, "the change to it takes the parked root")
	assert_false(park.holds("res://a.tscn"), "the park is empty after")
	assert_eq(await park.take("res://a.tscn"), null, "and hands it over only once")
	root.free()


func test_drop_frees_the_parked_root() -> void:
	var park := _park()
	var root := Node3D.new()
	park.node = root
	park.path = "res://a.tscn"
	park.drop()
	assert_false(is_instance_valid(root), "the parked root is freed")
	assert_false(park.holds("res://a.tscn"), "nothing is held")


func test_a_missing_scene_parks_nothing() -> void:
	var park := _park()
	await park.start("res://no/such/scene.tscn", null, null, "")
	assert_eq(park.building, "", "nothing is being built")
	assert_false(park.holds("res://no/such/scene.tscn"), "nothing is held")
