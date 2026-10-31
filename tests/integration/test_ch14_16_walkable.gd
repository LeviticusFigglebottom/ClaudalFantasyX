extends KitWalkProbe
## M4-C14-02 .. M4-C16-02: the Act II greybox zones of Ch14-16 are walkable where the story walks (KitWalkProbe on
## their boxes and ramps): the Lacquer Court from its entry to the vows and down the water-steps onto the barge; the
## barge's deck from the stern to the bow; Hollowmere's dock to the ship, a hull-house and the pyre-raft's end; the Pale
## Rim's wade to the Choir's edge; the Choir's floor to Kesh's place.

const COURT := "res://game/levels/ch13/ansedra_lacquer_court/ansedra_lacquer_court.tscn"
const SEA := "res://game/levels/ch15/open_sea/open_sea.tscn"
const HOLLOWMERE := "res://game/levels/ch17/hollowmere/hollowmere.tscn"
const RIM := "res://game/levels/ch16/pale_rim/pale_rim.tscn"
const CHOIR := "res://game/levels/ch16/drowned_choir/drowned_choir.tscn"


func _mark(id: StringName) -> Vector3:
	return zone.stage.mark(id).position


func _spawn(id: StringName) -> Vector3:
	return zone.spawn_marker(id).position


func test_the_court_to_the_barge() -> void:
	open(COURT)
	walk("to the vows", [_spawn(&"CourtEntry"), Vector3(0, 0, -2.5), _mark(&"vows")] as Array[Vector3], 0.0)
	var pts: Array[Vector3] = [
		_spawn(&"CourtEntry"), Vector3(0, 0, -2.5), _mark(&"kerrid_steps"), Vector3(0, -0.6, 4.5)
	]
	pts.append(_mark(&"barge_deck"))
	var end := walk("down the water-steps to the barge", pts, 0.0)
	assert_true(absf(end + 0.6) < 0.1, "on the barge's deck (y %.2f)" % end)
	close()


func test_the_barge_deck() -> void:
	open(SEA)
	walk(
		"stern to bow, past the bier",
		[_mark(&"kerrid_sits"), Vector3(1.4, 0, 3.0), Vector3(1.4, 0, 0.0), _mark(&"bow")] as Array[Vector3],
		0.0
	)
	close()


func test_hollowmeres_dock() -> void:
	open(HOLLOWMERE)
	walk("to the ship", [_spawn(&"Dock"), Vector3(30, 0, 0), Vector3(30, 0, 1.6)] as Array[Vector3], 0.0)
	walk("to a hull-house", [_spawn(&"Dock"), Vector3(28, 0, 0), _mark(&"fathers_door")] as Array[Vector3], 0.0)
	walk("to the dock's end", [_spawn(&"Dock"), _mark(&"supper"), _mark(&"pyre_raft")] as Array[Vector3], 0.0)
	close()


## M5-A3P-1001: in Ch17 the dock's east end opens onto the gangway to the berths and the walk along their heads.
func test_hollowmeres_dry_dock_in_ch17() -> void:
	open(HOLLOWMERE)
	Game.set_flag(&"ch17_started")
	(zone as Ch17Zone).apply_variant()
	read_boxes()
	var berths := _spawn(&"Berths")
	var dock_way: Array[Vector3] = [
		_spawn(&"Dock"), Vector3(38, 0, -1.2), Vector3(47, 0, -1.2), Vector3(59, 0, 0), berths
	]
	walk("to the berths", dock_way, 0.0)
	walk("to Tobin's post", [berths, _mark(&"first_berth")] as Array[Vector3], 0.0)
	walk("along the berths", [berths, _mark(&"berth_walk")] as Array[Vector3], 0.0)
	close()


func test_the_rim_wade_and_the_choir() -> void:
	open(RIM)
	walk("the wade", [_spawn(&"Rim"), Vector3(100, 0, 0), _mark(&"choir_edge")] as Array[Vector3], 0.0)
	# M4-A2P-1500: the exit to the Choir stands on the sand, reachable from where the montage sets the party down
	var exit := (zone.get_node(^"Triggers/to_choir") as Node3D).position
	walk("to the Choir's edge", [_spawn(&"ChoirEdge"), exit] as Array[Vector3], 0.0)
	close()
	open(CHOIR)
	walk("to Kesh", [_spawn(&"Approach"), _mark(&"kerrid_line"), _mark(&"kesh")] as Array[Vector3], 0.0)
	close()
