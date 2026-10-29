extends KitWalkProbe
## ADR 0200: ch07/tamsule dressed with env-art's port pieces (tools/act1/ch07_tamsule_port_dressing.py) keeps its
## greybox decks as the walk, and its river is water now, not a floor 1 m down: rails on the decks' open edges
## (tamsule_collision.json) keep the player out of it. The story's routes walk from the river-mouth quay through the
## market to the stilt lane, the gantry foot and its way to the Bell, Tavi's boats and the harbour; every actor and
## story mark a person stands on is on a deck.

const PORT := "res://game/levels/ch07/tamsule/tamsule.tscn"
const DECK_Y := 0.0
## Marks in the water by design: the barge's look-at by the Bell, the trader's stern and the boat going east.
const OFF_DECK: Array[StringName] = [&"bell_moorings", &"rhen_stern", &"east_water"]
const ACTORS: Array[StringName] = [
	&"liss",
	&"ysolde",
	&"asha",
	&"toma",
	&"kerrid",
	&"tavi",
	&"vendor",
	&"board",
	&"child",
	&"fisher",
	&"netmender",
	&"boatman",
	&"trader_boatman",
]


func before_each() -> void:
	open(PORT)


func _trigger(id: String) -> Vector3:
	return (zone.get_node(NodePath("Triggers/%s" % id)) as Node3D).position


func _on_deck(route: String, pts: Array[Vector3]) -> void:
	var end := walk(route, pts, DECK_Y)
	assert_true(absf(end - DECK_Y) < 0.05, "%s ends on a deck (y %.2f)" % [route, end])


func test_the_quay_reaches_the_market_and_the_stilt_lane() -> void:
	var start := zone.spawn_marker(&"RiverMouth").position
	_on_deck("quay to lane", [start, Vector3(0, 0, 13.0), Vector3(-4.0, 0, 4.0), Vector3(-20.0, 0, 4.0)])
	close()


func test_the_market_reaches_the_gantry_foot_and_the_way_to_the_bell() -> void:
	_on_deck("market to the Bell", [Vector3(0, 0, 4.0), Vector3(0, 0, -6.0), _trigger("to_bell")])
	close()


func test_the_gantry_foot_reaches_tavis_boats() -> void:
	var start := zone.spawn_marker(&"FromBell").position
	_on_deck("gantry to the boats", [start, Vector3(6.0, 0, -12.0), _trigger("tavi")])
	close()


func test_the_market_reaches_the_harbour() -> void:
	var end := zone.spawn_marker(&"Harbour").position
	_on_deck("market to the harbour", [Vector3(4.0, 0, 8.0), Vector3(15.5, 0, 8.0), end, _trigger("harbour")])
	close()


func test_people_stand_on_the_decks() -> void:
	for id in ACTORS:
		var p := zone.stage.actor(id).position
		var f := floor_y(p.x, p.z, p.y + 0.3)
		assert_true(absf(f - p.y) < 0.35, "%s stands on a deck (y %.2f, floor %.2f)" % [id, p.y, f])
	for key: String in (zone.layout.get("marks", {}) as Dictionary).keys():
		var id := StringName(key)
		if id in OFF_DECK:
			continue
		var m := zone.stage.mark(id).position
		assert_true(absf(floor_y(m.x, m.z, m.y + 0.3) - m.y) < 0.35, "mark %s is on a deck" % id)
	close()


func test_rails_keep_the_player_out_of_the_river() -> void:
	# A body stepping past the quay's river edge, the market's west edge and the harbour's east edge meets a rail.
	for feet: Vector3 in [Vector3(0, 0, 24.1), Vector3(-12.1, 0, 10.0), Vector3(29.1, 0, 10.0)]:
		assert_true(blocked_by(feet).begins_with("Rail"), "a rail at %s" % feet)
	close()
