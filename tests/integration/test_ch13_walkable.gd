extends KitWalkProbe
## M4-C13-02: Ch13's greybox zones are walkable where the story walks (KitWalkProbe on their boxes): Ansedra from the
## moorings over the causeways to Sefir's door, Corran's old house, the archive's isle and the Sanctum's; the
## Sanctum from the gate round the basin's ledge to Ethren's place; the archive to both reading tables.

const CITY := "res://game/levels/ch13/ansedra/ansedra.tscn"
const SANCTUM := "res://game/levels/ch13/sanctum/sanctum.tscn"
const ARCHIVE := "res://game/levels/ch13/lamp_archive/lamp_archive.tscn"


func _mark(id: StringName) -> Vector3:
	return zone.stage.mark(id).position


func test_the_causeways_reach_every_door() -> void:
	open(CITY)
	var moorings := zone.spawn_marker(&"Moorings").position
	walk("to the moorings' edge", [moorings, _mark(&"kerrid_moorings")] as Array[Vector3], 0.0)
	walk("to Sefir's door", [moorings, Vector3(0, 0, -40), _mark(&"sefir_door")] as Array[Vector3], 0.0)
	walk(
		"to Corran's house",
		[moorings, Vector3(0, 0, -40), Vector3(-40, 0, -40), _mark(&"corran_house")] as Array[Vector3],
		0.0
	)
	walk("to the archive", [moorings, Vector3(0, 0, -40), Vector3(46, 0, -40)] as Array[Vector3], 0.0)
	var end := walk("to the Sanctum", [moorings, Vector3(0, 0, -40), Vector3(0, 0, -84)] as Array[Vector3], 0.0)
	assert_true(absf(end) < 0.05, "on the Sanctum's isle (y %.2f)" % end)
	close()


func test_the_sanctum_goes_round_the_basin_to_ethren() -> void:
	open(SANCTUM)
	var pts: Array[Vector3] = [zone.spawn_marker(&"Gate").position, Vector3(0, 0, -14), Vector3(8, 0, -18)]
	pts.append_array([Vector3(8, 0, -42), _mark(&"ethren")] as Array[Vector3])
	walk("round the basin", pts, 0.0)
	close()


func test_the_archive_reaches_both_tables() -> void:
	open(ARCHIVE)
	var door := zone.spawn_marker(&"Door").position
	walk("to the ledgers", [door, Vector3(-3.2, 0, -8), _mark(&"ledgers")] as Array[Vector3], 0.0)
	walk("to the roll", [door, Vector3(3.2, 0, -8), _mark(&"cantor_roll")] as Array[Vector3], 0.0)
	close()
