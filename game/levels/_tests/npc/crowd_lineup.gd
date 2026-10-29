extends Node3D
## M3-CRE-659 review stage (ADR 0152): Act I's crowd. `Lineup`: every crowd body in a row (by age band), each in
## its first wearer's tints, idling out of step (crowd_lineup_a/b/c). `Crowd`: a market of people from several
## zones, each in their own tints and at their work, seen at walking distance as the Haluna shots see the villagers
## (crowd_market, crowd_work). Everything comes from game/data/world/npc/crowd.json through the same FieldNpc
## set-up the VillagerLayer gives a crowd row.

const CROWD := "res://game/data/world/npc/crowd.json"
const BAND_ORDER: Array[String] = ["child", "adult", "elder"]
## Lineup spacing (m) and the gap between the three groups of the row.
@export var spacing_m := 0.95
@export var group_gap_m := 3.0
@export var group_size := 8
## The market: [person id, x, z, yaw_deg] (z negative is away from the lineup; FieldNpc yaw: 0 faces -Z, 180
## faces the cameras).
@export var market: Array = [
	["tamsule_vendor", -1.6, -9.0, 200.0],
	["tamsule_board", -0.4, -9.6, 165.0],
	["pemakar_boat_seller", 1.2, -8.6, 150.0],
	["corrow_townsfolk_a", 2.6, -10.2, 120.0],
	["corrow_townsfolk_b", 3.4, -9.4, 250.0],
	["oruvel_netmender", -3.4, -8.2, 225.0],
	["oruvel_netmender_2", -4.4, -9.4, 205.0],
	["pemakar_sweeper", 0.6, -12.0, 200.0],
	["tamsule_child", -2.2, -11.6, 140.0],
	["corrow_child_a", -1.4, -12.4, 210.0],
	["brightwater_ferry_trader_a", 4.6, -12.0, 215.0],
	["corrow_night_mourner_2", -0.6, -14.4, 180.0],
	["corrow_night_mourner_3", 0.6, -14.6, 180.0],
	["pemakar_folder", 2.2, -13.6, 160.0],
	["tamsule_bell_galleries_sorrin_diver_1", -3.8, -13.0, 190.0],
	["coilspire_tender", 5.4, -14.0, 225.0],
]

var people: Dictionary = {}


func _ready() -> void:
	var data := VillagerLayer.load_data(CROWD)
	for p: Variant in data.get("people", []):
		people[str(p["id"])] = p
	_lineup(data)
	_market()


func _first_wearers(data: Dictionary) -> Array:
	var bodies: Array = (data.get("bodies", {}) as Dictionary).keys()
	bodies.sort_custom(
		func(a: String, b: String) -> bool:
			var ba := BAND_ORDER.find(str(data["bodies"][a]["age_band"]))
			var bb := BAND_ORDER.find(str(data["bodies"][b]["age_band"]))
			return ba < bb if ba != bb else a < b
	)
	var out: Array = []
	for body: String in bodies:
		for p: Variant in data.get("people", []):
			if str(p["body"]) == body:
				out.append(p)
				break
	return out


func _lineup(data: Dictionary) -> void:
	var row := Node3D.new()
	row.name = "Lineup"
	add_child(row)
	var wearers := _first_wearers(data)
	for i in wearers.size():
		var group := floori(float(i) / group_size)
		var k := i % group_size
		var x := (k - (group_size - 1) * 0.5) * spacing_m + group * (group_size * spacing_m + group_gap_m)
		var npc := _person(wearers[i], false)
		npc.position = Vector3(x, 0.0, 0.0)
		npc.rotation.y = PI  # FieldNpc faces -Z; the lineup cameras look from +Z
		row.add_child(npc)


func _market() -> void:
	var square := Node3D.new()
	square.name = "Crowd"
	add_child(square)
	for spot: Array in market:
		if not people.has(str(spot[0])):
			push_warning("crowd_lineup: no crowd person %s" % spot[0])
			continue
		var npc := _person(people[str(spot[0])], true)
		npc.position = Vector3(float(spot[1]), 0.0, float(spot[2]))
		npc.rotation.y = deg_to_rad(float(spot[3]))
		square.add_child(npc)


## A FieldNpc dressed as the VillagerLayer dresses a crowd row; `working` keeps the person's work clip.
func _person(p: Dictionary, working: bool) -> FieldNpc:
	var body := str(p["body"])
	var npc := FieldNpc.new()
	npc.name = str(p["id"])
	npc.npc_id = StringName(str(p["id"]))
	npc.actor_scene = load(VillagerLayer.CROWD_ACTOR_PATH % [body, body]) as PackedScene
	npc.tints = (p["tints"] as Dictionary).duplicate()
	var person := p.duplicate()
	if not working:
		person["work"] = ""
	npc.tuning_over = VillagerLayer.crowd_tuning(person)
	return npc
