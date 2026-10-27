extends TestCase
## M2-ENV-02: the Haluna world's night mood (HalunaMood `mood`, color script `ch02_night`) on the
## shipped dressing: the moon at 38 deg, the night sky, sea-glow 0.12 on a copy of the sea material,
## the oil lamps in every house, and a clean return to the authored day.

const DRESSING := "res://game/levels/ch02/haluna/haluna_dressing.tscn"
const LAYOUT := "res://game/levels/ch02/haluna/haluna_layout.json"
const EPS := 0.001

var world: HalunaMood


func before_each() -> void:
	world = (load(DRESSING) as PackedScene).instantiate() as HalunaMood
	_host().add_child(world)


func _done() -> void:
	if world != null and is_instance_valid(world):
		_host().remove_child(world)
		world.free()


func test_day_is_the_scene_as_authored() -> void:
	assert_eq(world.mood, HalunaMood.MOOD_DAY)
	assert_true(world.sun.visible)
	assert_false(world.moon.visible)
	assert_false(world.dresser.night_lamps().visible, "the lamps are out by day")
	assert_eq(world.water.sea_glow_energy, 0.0)
	assert_ne(world.world_environment.environment, world.night_environment)
	_done()


func test_night_switches_the_light_sky_sea_and_lamps() -> void:
	var day_env := world.world_environment.environment
	var day_mat := world.water.material
	var day_deep: Variant = day_mat.get_shader_parameter(HalunaMood.PARAM_DEEP)
	world.mood = HalunaMood.MOOD_NIGHT
	assert_false(world.sun.visible)
	assert_true(world.moon.visible)
	assert_between(world.moon.light_energy, 0.25 - EPS, 0.25 + EPS, "moon 0.25 (color script rule 3: <= 2.5 x 0.12)")
	var toward := world.moon.global_basis.z  # a DirectionalLight3D shines along -Z, away from the body
	var want := HalunaMood.direction_from_angles(38.0, 200.0)
	assert_true(toward.distance_to(want) < 0.01, "the moon at 38 deg, azimuth 200")
	assert_eq(world.world_environment.environment, world.night_environment)
	assert_between(world.night_environment.tonemap_exposure, 1.1 - EPS, 1.1 + EPS, "exposure 1.1")
	assert_between(world.water.sea_glow_energy, 0.12 - EPS, 0.12 + EPS, "sea-glow 0.12")
	assert_ne(world.water.material, day_mat, "night works on a copy of the sea material")
	assert_eq(day_mat.get_shader_parameter(HalunaMood.PARAM_DEEP), day_deep, "the shared material is untouched")
	assert_eq(world.water.material.get_shader_parameter(HalunaMood.PARAM_DEEP), Color("#061A2B"))
	assert_true(world.glimmer().w > 0.0, "the glimmer gate is open (it gates sea-glow)")
	assert_true(world.dresser.night_lamps().visible)
	world.mood = HalunaMood.MOOD_DAY
	assert_true(world.sun.visible and not world.moon.visible, "back to day")
	assert_eq(world.world_environment.environment, day_env)
	assert_eq(world.water.material, day_mat)
	assert_eq(world.water.sea_glow_energy, 0.0)
	assert_false(world.dresser.night_lamps().visible)
	assert_eq(world.glimmer().w, 0.0, "the gate shut again")
	_done()


func test_every_house_has_an_oil_lamp() -> void:
	var layout := HalunaDresser._load_json(LAYOUT)
	var per_piece: Dictionary = layout["night_lamps"]["per_piece"]
	var want := 0
	for spec: Dictionary in layout["pieces"]:
		want += (per_piece.get(String(spec["piece"]), []) as Array).size()
	assert_true(want >= 30, "about forty houses: %d" % want)
	var lights := world.dresser.night_lamps().find_children("*", "OmniLight3D", true, false)
	assert_eq(lights.size(), want)
	var light := lights[0] as OmniLight3D
	assert_eq(light.light_color, Color("#FFB16E"), "oil lamps #FFB16E")
	assert_false(light.shadow_enabled, "lamp pools without shadows (cost)")
	_done()


func test_a_night_mood_set_before_ready_applies_on_entry() -> void:
	var w := (load(DRESSING) as PackedScene).instantiate() as HalunaMood
	w.mood = HalunaMood.MOOD_NIGHT
	_host().add_child(w)
	assert_true(w.moon.visible and not w.sun.visible)
	assert_between(w.water.sea_glow_energy, 0.12 - EPS, 0.12 + EPS)
	_host().remove_child(w)
	w.free()
	_done()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


## M3-ENV-709 (Ch4 C4-01): one house's lamps go out without touching its neighbours'.
func test_a_house_lamp_turns_off_alone() -> void:
	world.mood = HalunaMood.MOOD_NIGHT
	var houses := world.dresser.night_lamp_houses()
	assert_true(houses.size() > 30, "every house hangs a lamp")
	var lamps := world.dresser.night_lamps()
	world.dresser.set_night_lamp(houses[0], false)
	var off := 0
	var lit := 0
	for child in lamps.get_children():
		var house := int(child.get_meta(HalunaDresser.LAMP_HOUSE_META, -1))
		if house == houses[0]:
			off += 0 if (child as Node3D).visible else 1
		elif (child as Node3D).visible:
			lit += 1
	assert_eq(off, 2, "its flame and its light are out")
	assert_eq(lit, (houses.size() - 1) * 2, "every other house is still lit")
	world.dresser.set_night_lamp(houses[0], true)
	_done()
