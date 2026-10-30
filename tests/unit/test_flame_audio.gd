extends TestCase
## env-art-b's Act II ambient life (the Lead's 10-30 21:05 item; prop_sfx.json `flames`): a zone dressing's warm
## flickering flames each get a small close loop under their light, once the lights are placed; a steady light and
## the bound-teal lamps (they flicker, but aren't flames) stay silent. The dressing is built by hand outside the tree
## (its _ready would dress a real zone), so nothing plays: the test only reads the players.

const WARM := Color(1.0, 0.69, 0.43)
const TEAL := Color(0.31, 0.7, 0.69)


func _dressing(rows: Array, place_lights: bool) -> ZoneKitDressing:
	var d := ZoneKitDressing.new()
	d.layout = {"fire_lights": rows}
	if place_lights:
		_place(d)
	return d


## Mirrors ZoneKitDressing._place_fire_lights: one OmniLight3D per row, in row order, under FireLights.
func _place(d: ZoneKitDressing) -> void:
	var root := Node3D.new()
	root.name = PropAudio.FIRE_LIGHTS
	d.add_child(root)
	for r: Dictionary in d.layout["fire_lights"]:
		var light := OmniLight3D.new()
		light.light_color = Color.html(str(r["color"])) if r.has("color") else WARM
		var at: Array = r["at"]
		light.position = Vector3(float(at[0]), float(at[1]), float(at[2]))
		root.add_child(light)


func _flames(d: ZoneKitDressing) -> Array[Node]:
	return (d.get_node(NodePath(String(PropAudio.FIRE_LIGHTS))).get_children()).filter(
		func(l: Node) -> bool: return l.has_node(NodePath(String(PropAudio.FLAME_PLAYER)))
	)


func test_warm_flickering_flames_sound_and_the_teal_and_steady_lights_dont() -> void:
	var props := PropAudio.new(AudioData.table(AudioData.PROP_SFX))
	var d := _dressing(
		[
			{"at": [-3.4, 2.65, -20.0], "flicker": 0.15},  # a Lacquer Court lantern
			{"at": [12.0, 1.55, -16.95], "flicker": 0.3},  # a Hollowmere lamp
			{"at": [8.15, 3.0, -15.6], "color": "#4FB3B0", "flicker": 0.12},  # a bound-teal conduit
			{"at": [0.0, 2.0, 0.0]},  # a steady light
		],
		true
	)
	assert_true(props.wants(d), "the director routes a zone dressing to the prop listener")
	var started := props.attach_flames(d)
	assert_eq(started.size(), 2, "the lantern and the lamp")
	var lights := d.get_node(NodePath(String(PropAudio.FIRE_LIGHTS))).get_children()
	assert_true(lights[0].has_node(NodePath(String(PropAudio.FLAME_PLAYER))), "the lantern's loop is under its light")
	assert_false(lights[2].has_node(NodePath(String(PropAudio.FLAME_PLAYER))), "the teal conduit is no flame")
	assert_false(lights[3].has_node(NodePath(String(PropAudio.FLAME_PLAYER))), "a steady light is silent")
	var p := started[0]
	assert_eq(String(p.bus), "World", "on World (ducked under a line)")
	var stream := p.stream as AudioStreamOggVorbis
	assert_true(stream != null and stream.loop, "a loop (its .import loops)")
	assert_true(p.max_distance > 0.0 and p.max_distance < 15.0, "a close sound, not heard across the zone")
	assert_eq(props.attach_flames(d).size(), 0, "attached once")
	d.free()


func test_a_dressing_not_yet_dressed_gets_its_flames_when_it_is() -> void:
	var props := PropAudio.new(AudioData.table(AudioData.PROP_SFX))
	var d := _dressing([{"at": [1.0, 2.0, 3.0], "flicker": 0.3}], false)
	assert_eq(props.attach_flames(d).size(), 0, "no lights placed yet")
	assert_eq(props.attach_flames(d).size(), 0, "and asking twice waits once")
	_place(d)
	d.dressed.emit()
	assert_eq(_flames(d).size(), 1, "its flame sounds once it is dressed")
	d.dressed.emit()
	assert_eq(_flames(d).size(), 1, "and only once")
	d.free()


func test_the_flame_is_one_of_ours() -> void:
	assert_true(PropAudio.is_flame(WARM), "the zone's fire colour is a flame")
	assert_false(PropAudio.is_flame(TEAL), "the bound teal is not")
	var row: Dictionary = AudioData.table(AudioData.PROP_SFX)["flames"]
	assert_true(ResourceLoader.exists(str(row["file"])), "its loop is rendered")
