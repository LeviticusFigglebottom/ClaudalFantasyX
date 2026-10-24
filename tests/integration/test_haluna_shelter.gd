extends TestCase
## M1-ENV-11 (Haluna side): the AUTO plants' shelter probe against the zone's runtime walk collision.
## The bodies are on layer 1 (the plants' shelter_mask), every plant has a probe scheduled once the
## zone is in, and a plant in a house's shadow from the ch02_noon sun reads as sheltered.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"

var zone: HalunaZone


func before_each() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	(zone.get_node("Story") as HalunaStory).autostart = false


func test_walk_collision_is_on_the_shelter_layer() -> void:
	_host().add_child(zone)
	for body: StaticBody3D in [zone.collision.ground, zone.collision.props, zone.collision.bounds]:
		assert_true(body.collision_layer & 1 != 0, "%s on layer 1" % body.name)
	var plants := zone.mood.find_children("*", "VegetationPlant", true, false)
	assert_true(plants.size() > 10, "the dressed plants: %d" % plants.size())
	for p in plants:
		var plant := p as VegetationPlant
		assert_eq(plant.shelter_mask, 1)
		assert_true(
			plant.get_tree().physics_frame.is_connected(plant.probe_shelter), "%s probes after entry" % plant.name
		)
	_done()


func test_a_plant_in_a_houses_shadow_reads_as_sheltered() -> void:
	var dresser := zone.get_node("HalunaMood/Dresser") as HalunaDresser
	# Main-thread instance: the dresser dresses in its own _ready, so the probe plants go in after
	# the zone enters (as the dresser's own plants do), and are probed as the first physics frame would.
	_host().add_child(zone)
	var house := _first(dresser, "house_tile_b")
	assert_true(house != null)
	var box := HalunaCollision.local_bounds(house)
	# The noon sun is high (74 deg) and to the south (+Z), so only a plant right against the house's north
	# face is in its shadow: 0.2 m outside its collision box (the mesh bounds inset 0.5 m, piece_rules).
	var shade := house.transform * Vector3(0.0, 0.0, box.position.z + 0.5 - 0.2)
	var open := Vector3(-5.0, 0.0, 10.0)  # the beach below the village
	var under := _plant(dresser, shade)
	var out := _plant(dresser, open)
	under.probe_shelter()
	out.probe_shelter()
	assert_true(under.is_sheltered(), "a plant north of the house, toward the sun, is sheltered")
	assert_false(out.is_sheltered(), "a plant on the open beach is not")
	_done()


func _plant(dresser: HalunaDresser, at: Vector3) -> VegetationPlant:
	var plant := VegetationPlant.new()
	var mesh := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(0.4, 1.2, 0.4)
	mesh.mesh = box
	mesh.position = Vector3(0.0, 0.6, 0.0)
	plant.add_child(mesh)
	plant.position = Vector3(at.x, dresser.ground_y(at.x, at.z), at.z)
	dresser.add_child(plant)
	return plant


func _first(dresser: HalunaDresser, prefix: String) -> Node3D:
	for c in dresser.get_children():
		if String(c.name).begins_with(prefix):
			return c as Node3D
	return null


func _done() -> void:
	if zone != null and is_instance_valid(zone):
		if zone.is_inside_tree():
			_host().remove_child(zone)
		zone.free()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
