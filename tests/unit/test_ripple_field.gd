extends TestCase
## M4-A2P-047 (env-art-b): RippleField sends rings across a still water (ripple_field.gd; the shader's ring_slope).
## A strike adds a source on the field's clock; a wake target drops one every wake_spacing_m; old sources age out
## and the count is capped; the uniforms reach the field's own copy of the material, never the shared resource.

const STILL := "res://game/levels/ch13/ansedra/ansedra_still_water_material.tres"

var _root: Node3D
var _water: WaterSurface
var _field: RippleField
var _shared: ShaderMaterial


func before_each() -> void:
	_root = Node3D.new()
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(_root)
	_shared = load(STILL) as ShaderMaterial
	_water = WaterSurface.new()
	_water.material = _shared
	_root.add_child(_water)
	_field = RippleField.new()
	_field.water = _water
	_field.set_process(false)
	_root.add_child(_field)


## The runner has no after_each: each test frees its root at its end.
func _close() -> void:
	_root.free()


func test_a_strike_reaches_the_fields_own_material() -> void:
	assert_true(_water.material != _shared, "the field's own copy of the material")
	_field.advance(2.0)
	_field.strike(Vector3(3.0, 0.0, -4.0))
	var mat := _water.material
	assert_eq(int(mat.get_shader_parameter(&"ripple_count")), 1)
	var src: Vector4 = (mat.get_shader_parameter(&"ripple_sources") as PackedVector4Array)[0]
	assert_true(src.is_equal_approx(Vector4(3.0, -4.0, 2.0, float(RippleField.data()["strike_height_m"]))), str(src))
	assert_eq(float(mat.get_shader_parameter(&"ripple_now_s")), 2.0)
	assert_true(_shared.get_shader_parameter(&"ripple_count") in [null, 0], "the shared material is untouched")
	_close()


func test_sources_age_out_and_are_capped() -> void:
	var d := RippleField.data()
	for i in int(d["max_sources"]) + 3:
		_field.strike(Vector3(float(i), 0.0, 0.0))
	assert_eq(_field.sources.size(), int(d["max_sources"]), "capped")
	assert_eq(_field.sources[0].x, 3.0, "the oldest went first")
	_field.advance(float(d["life_s"]) + 0.1)
	assert_eq(_field.sources.size(), 0, "aged out")
	assert_eq(int(_water.material.get_shader_parameter(&"ripple_count")), 0)
	_close()


func test_a_wake_drops_a_ring_every_spacing() -> void:
	var boat := Node3D.new()
	_root.add_child(boat)
	_field.wake_target = boat
	var spacing := float(RippleField.data()["wake_spacing_m"])
	_field.advance(0.1)
	assert_eq(_field.sources.size(), 1, "the first ring where it starts")
	boat.position.x = spacing * 0.5
	_field.advance(0.1)
	assert_eq(_field.sources.size(), 1, "not yet a spacing on")
	boat.position.x = spacing * 1.01
	_field.advance(0.1)
	assert_eq(_field.sources.size(), 2, "a ring each spacing")
	assert_eq(RippleField.find(_root.get_tree()), _field, "cinematics find the zone's field")
	_close()
