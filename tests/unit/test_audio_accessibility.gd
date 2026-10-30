extends TestCase
## The Lead's 10-30 21:25 accessibility pass: the volume sliders reach every sound (a player another track adds with
## no bus is moved off Master; the townsfolk's chatter follows the voice slider and still ducks under a line, since
## Walla sends through World), and the mono setting folds Master to (L + R) / 2 live and lets go when turned off.
## Nothing is heard: the test reads the buses and the players.

var dir: AudioDirector
var settings: UiSettings


func before_each() -> void:
	dir = AudioDirector.new()
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(dir)
	dir.set_process(false)
	settings = UiSettings.new()


func _done() -> void:
	AudioDirector.apply_mono(false)
	for bus: StringName in [&"Voice", &"Walla", &"Music", &"SFX", &"Ambience", &"Master"]:
		dir.set_user_volume(bus, 0.0)
	dir.stop_all_players()
	dir.free()


func test_a_player_left_on_master_comes_under_the_effects_slider() -> void:
	var host := Node.new()
	dir.add_child(host)
	var stray := AudioStreamPlayer3D.new()
	host.add_child(stray)
	assert_eq(String(stray.bus), "Master", "a player that never names a bus starts on Master")
	dir.route_stray(stray)
	assert_eq(String(stray.bus), "SFX", "moved under the effects slider (mix.json stray_bus)")
	var voiced := AudioStreamPlayer.new()
	voiced.bus = &"Voice"
	host.add_child(voiced)
	dir.route_stray(voiced)
	assert_eq(String(voiced.bus), "Voice", "a player with its own bus is left alone")
	host.free()
	_done()


func test_the_townsfolks_chatter_follows_the_voice_slider_and_ducks_under_a_line() -> void:
	assert_true(AudioServer.get_bus_index(&"Walla") >= 0, "the Walla bus is built")
	assert_eq(String(AudioServer.get_bus_send(AudioServer.get_bus_index(&"Walla"))), "World", "it sends through World")
	var rows := AudioData.sfx_rows()
	for id: String in ["villager_murmur_low", "villager_murmur_high"]:
		assert_eq(str((rows.get(id, {}) as Dictionary).get("bus", "")), "Walla", "%s plays on Walla" % id)
	dir.follow_settings(settings)
	assert_true(settings.set_value(&"voice_volume", 0.0))
	assert_eq(float(dir.user_db[&"Walla"]), -80.0, "voice at 0 silences the chatter too")
	assert_eq(float(dir.user_db[&"Voice"]), -80.0, "and the voices")
	var duck := (dir.mix.get("ducks", {}) as Dictionary).get("dialogue", {}) as Dictionary
	var world_db := float((duck.get("buses", {}) as Dictionary).get("World", 0.0))
	assert_true(world_db < 0.0, "World (so Walla) ducks under a line")
	_done()


func test_mono_folds_master_live_and_lets_go() -> void:
	dir.follow_settings(settings)
	assert_eq(AudioDirector.mono_effect_index(), -1, "stereo by default")
	assert_true(settings.set_value(&"mono_audio", true))
	var idx := AudioDirector.mono_effect_index()
	assert_true(idx >= 0, "turning it on folds Master")
	var fx := AudioServer.get_bus_effect(0, idx) as AudioEffectStereoEnhance
	assert_eq(fx.pan_pullout, 0.0, "to (L + R) / 2")
	settings.set_value(&"mono_audio", true)
	var count := 0
	for i in AudioServer.get_bus_effect_count(0):
		if AudioServer.get_bus_effect(0, i) is AudioEffectStereoEnhance:
			count += 1
	assert_eq(count, 1, "once")
	assert_true(settings.set_value(&"mono_audio", false))
	assert_eq(AudioDirector.mono_effect_index(), -1, "and off again is stereo")
	_done()
