extends KitWalkProbe
## M5-A3P-1007: Ch19's spire is walkable where the story walks (KitWalkProbe on its boxes and ramps): from the plaza
## through the spire's foot (its gate open after the hitch), up the four flights to the antechamber and onto the crown.

const SPIRE := "res://game/levels/ch19/iskarra_spire/iskarra_spire.tscn"


func test_the_plaza_to_the_crown() -> void:
	open(SPIRE)
	Game.set_flag(&"ch19_learned_the_hitch")
	(zone as Ch19Zone).apply_variant()
	read_boxes()
	var start := zone.spawn_marker(&"Plaza").position
	var pts: Array[Vector3] = [
		start,
		Vector3(0, 0, 6),
		Vector3(4.5, 0, -8),
		Vector3(4.5, 6, -22),
		Vector3(-4.5, 6, -22),
		Vector3(-4.5, 12, -8),
		Vector3(4.5, 12, -8),
		Vector3(4.5, 18, -22),
		Vector3(-4.5, 18, -22),
		Vector3(-4.5, 24, -8),
		Vector3(0, 24, -4),
		zone.stage.mark(&"engine_lever").position,
	]
	var end := walk("the plaza to the crown", pts, 0.0)
	assert_true(absf(end - 24.0) < 0.1, "on the crown (y %.2f)" % end)
	close()
