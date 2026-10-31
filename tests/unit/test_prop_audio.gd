extends TestCase
## Cinematics' staged practicals that sound (prop_sfx.json; the Lead's 10-30 18:45 item): a prop whose scene is a row
## gets its loop as it enters the tree (Quellan's inn hearth for ch12_forty_seven_voices), the loop goes with the prop,
## and a prop with no row, or any other node, gets nothing. Nothing is heard: the test only reads the players.

const HEARTH := "res://game/data/cutscene/ch12/inn_fire.tscn"


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _prop(scene: String) -> Node3D:
	var n := Node3D.new()
	n.scene_file_path = scene
	_host().add_child(n)
	return n


func test_the_inn_hearth_sounds_and_its_loop_goes_with_it() -> void:
	var props := PropAudio.new(AudioData.table(AudioData.PROP_SFX))
	var fire := _prop(HEARTH)
	assert_true(props.wants(fire), "the hearth is a row")
	var p := props.attach(fire)
	assert_true(p != null and p.get_parent() == fire, "its loop is under the prop")
	assert_eq(String(p.bus), "World", "on World (ducked under a line)")
	var stream := p.stream as AudioStreamOggVorbis
	assert_true(stream != null and stream.loop, "a loop (its .import loops)")
	assert_true(p.playing, "playing from the start")
	assert_true(props.attach(fire) == null, "attached once")
	p.stop()
	fire.free()
	var other := _prop("res://game/data/cutscene/ch11/nothing.tscn")
	assert_false(props.wants(other), "a prop with no row gets nothing")
	other.free()
	var plain := Node3D.new()
	assert_false(props.wants(plain), "nor does a node with no scene")
	plain.free()


func test_the_director_builds_its_prop_listener_and_routes_props_to_it() -> void:
	# the director routes an entering node to props.attach (deferred: the runner steps no frame, so this calls the
	# director's own listener the way _on_node_added's deferred call does)
	var dir := AudioDirector.new()
	_host().add_child(dir)
	dir.set_process(false)
	assert_true(dir.props != null, "the director has its prop listener")
	var fire := _prop(HEARTH)
	assert_true(dir.props.wants(fire), "and it wants the staged hearth")
	var p := dir.props.attach(fire)
	assert_true(p != null and p.playing, "whose loop starts")
	if p != null:
		p.stop()
	fire.free()
	dir.stop_all_players()
	dir.free()


func test_the_archive_lamp_goes_out_with_its_light() -> void:
	# Ch13 R10: the scene's silence, then `@light archive_lamp off 1.0`; the flame's breath follows the light down
	var props := PropAudio.new(AudioData.table(AudioData.PROP_SFX))
	var lamp := _prop("res://game/data/cutscene/ch13/archive_lamp.tscn")
	var light := OmniLight3D.new()
	light.name = "archive_lamp"
	light.light_energy = 1.8
	lamp.add_child(light)
	var p := props.attach(lamp)
	assert_true(p != null and p.playing, "the lamp's flame sounds")
	var full := p.volume_db
	props.step()
	assert_between(p.volume_db, full - 0.01, full + 0.01, "at its own level while lit")
	light.light_energy = 0.9
	props.step()
	assert_between(p.volume_db, full - 6.1, full - 5.9, "half the light, about 6 dB down")
	light.light_energy = 0.0
	props.step()
	assert_false(p.playing, "out with the light")
	assert_eq(props.followers.size(), 0, "and no longer followed")
	lamp.free()
