extends KitWalkProbe
## M5-A3P-1011: Ch20's stair of floors is walkable where the story walks (KitWalkProbe on its boxes and ramps): from
## the first floor down every veiled flight (all open) through the six layers and the rests to the Cage's line.

const LAYERS := "res://game/levels/ch20/undertow_layers/undertow_layers.tscn"
const OPENERS: Array[StringName] = [
	&"ch20_started",
	&"ch20_ilun_released",
	&"ch20_kahre_released",
	&"ch20_virel_released",
	&"ch20_rest_one",
	&"ch20_hesk_released",
	&"ch20_nhoa_released",
	&"ch20_ethren_released",
	&"ch20_rest_two",
]
const FLOORS: Array[StringName] = [
	&"FirstFloor", &"Oruvel", &"Lanternfall", &"Kitchen", &"RestOne", &"Tidecup", &"Lowlight", &"Ansedra", &"RestTwo"
]


func test_the_first_floor_to_the_cage() -> void:
	open(LAYERS)
	for f in OPENERS:
		Game.set_flag(f)
	(zone as Ch05Zone).apply_variant()
	read_boxes()
	var pts: Array[Vector3] = []
	for f in FLOORS:
		pts.append(zone.spawn_marker(f).position)
	pts.append(zone.spawn_marker(&"CageFloor").position)
	pts.append(zone.stage.mark(&"cage_line").position)
	var end := walk("the first floor to the Cage", pts, 0.0)
	assert_true(absf(end - zone.stage.mark(&"cage_line").position.y) < 0.1, "on the Cage's floor (y %.2f)" % end)
	close()


func test_a_closed_veil_stops_the_walk() -> void:
	open(LAYERS)
	Game.set_flag(&"ch20_started")
	(zone as Ch05Zone).apply_variant()
	assert_true((zone as Ch05Zone).block_shown("Veil2"), "Oruvel's flight waits on Ilun's release")
	close()
