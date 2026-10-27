extends KitWalkProbe
## M4-C10-02: Ch10's greybox zones are walkable where the story walks (KitWalkProbe on their boxes): Ossa Fen from the
## fen's edge along the root-walks through the Drowner's clearing to the way on to Reedhollow, and into the side
## pocket; Reedhollow from the gate over the causeway and round the lagoon's ring to the shore.

const FEN := "res://game/levels/ch10/ossa_fen/ossa_fen.tscn"
const REEDHOLLOW := "res://game/levels/ch10/reedhollow/reedhollow.tscn"
const FEN_ROUTE: Array[Vector3] = [
	Vector3(-8, 0, 0),
	Vector3(0, 0, 0),
	Vector3(24, 0, 5),
	Vector3(40, 0, -9),
	Vector3(62, 0, -6),
	Vector3(84, 0, 8),
	Vector3(104, 0, 1),
	Vector3(112, 0, 0),
	Vector3(138, 0, 0)
]
const POCKET: Array[Vector3] = [Vector3(62, 0, -6), Vector3(66, 0, -24), Vector3(66, 0, -27)]
const LAGOON := Vector3(44, 0, 0)
const RING_R := 14.0
const RING_N := 12


func test_the_root_walks_run_from_the_edge_to_reedhollow() -> void:
	open(FEN)
	var end := walk("the root-walks", FEN_ROUTE, 0.0)
	assert_true(absf(end) < 0.05, "on the walks at the way on (y %.2f)" % end)
	walk("the side pocket", POCKET, 0.0)
	close()


func test_the_village_ring_goes_round_to_the_shore() -> void:
	open(REEDHOLLOW)
	var pts: Array[Vector3] = [Vector3(2, 0, 0), Vector3(LAGOON.x - RING_R, 0, 0)]
	# round the north side of the ring from the causeway (west, segment 6) to the shore (east, segment 0)
	for i in range(RING_N / 2, RING_N + 1):
		var a := TAU * i / RING_N
		pts.append(Vector3(LAGOON.x + RING_R * cos(a), 0, LAGOON.z - RING_R * sin(a)))
	pts.append(zone.spawn_marker(&"Shore").position)
	var end := walk("round the lagoon", pts, 0.0)
	assert_true(absf(end) < 0.05, "on the shore (y %.2f)" % end)
	close()
