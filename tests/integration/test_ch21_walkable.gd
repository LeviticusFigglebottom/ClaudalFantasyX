extends KitWalkProbe
## M5-A3P-1015: Ch21's heart is walkable where the story walks (KitWalkProbe on its boxes): down the last layer to the
## heart's mouth, to Rhen's place at arm's length from the two lamps, and to the Choir-stone.

const HEART := "res://game/levels/ch21/heart/heart.tscn"


func test_the_last_layer_to_the_lamps() -> void:
	open(HEART)
	var pts: Array[Vector3] = [
		zone.spawn_marker(&"LastLayer").position,
		zone.spawn_marker(&"HeartFloor").position,
		zone.stage.mark(&"arms_length").position,
		zone.spawn_marker(&"ChoirStone").position,
	]
	var end := walk("the last layer to the lamps", pts, 0.0)
	assert_true(absf(end) < 0.1, "on the heart's floor (y %.2f)" % end)
	close()
