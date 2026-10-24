extends TestCase
## M2-AUD-10: the area reverb (game/audio/world_verb.gd). mix.json's presets are complete and in range, every zone's
## `reverb` names one, the World and Combat buses carry an AudioEffectReverb, a zone swap ramps both to the zone's
## preset (a row without one gets the default), a dry preset switches the effects off, and the shrine stays drier
## than a cave because its SFX carry their own room.

const MIX := {
	"buses": [{"name": "SFX", "send": "Master"}, {"name": "World", "send": "SFX"}, {"name": "Combat", "send": "SFX"}],
	"reverb": {"buses": ["World", "Combat"], "default": "dry", "ramp_sec": 1.0},
	"reverb_presets":
	{
		"dry": {"room_size": 0.2, "damping": 0.5, "dry": 1.0, "wet": 0.0},
		"cave": {"room_size": 0.9, "damping": 0.4, "dry": 1.0, "wet": 0.3, "predelay_msec": 40.0},
		"lanes": {"room_size": 0.4, "damping": 0.6, "dry": 1.0, "wet": 0.1},
	},
}
const MUSIC := {
	"zones":
	[
		{"scene": "res://cave.tscn", "reverb": "cave"},
		{"scene": "res://lanes.tscn", "reverb": "lanes"},
		{"scene": "res://title.tscn"},
	],
}

var dir: AudioDirector


func before_each() -> void:
	var game_audio := (Engine.get_main_loop() as SceneTree).root.get_node_or_null(^"Audio") as AudioDirector
	if game_audio != null:
		game_audio.verb.stop()  # the buses are shared: the game's director must not ramp them meanwhile
	dir = AudioDirector.new()
	_host().add_child(dir)
	dir.setup(MIX, MUSIC, {"sfx": {}})
	dir.set_process(false)


func test_repo_presets_are_complete_in_range_and_named_by_zones() -> void:
	var mix := AudioData.table(AudioData.MIX)
	var presets := mix["reverb_presets"] as Dictionary
	assert_true(presets.has(str(mix["reverb"]["default"])), "the default preset exists")
	for want in ["open_sea", "village_lanes", "stone_shrine", "drowned_cave", "battle_beach"]:
		assert_true(presets.has(want), "preset %s" % want)
	for id: String in presets:
		for p in WorldVerb.PARAMS:
			assert_true((presets[id] as Dictionary).has(String(p)), "%s sets %s" % [id, p])
		assert_between(float(presets[id]["wet"]), 0.0, 1.0)
		assert_between(float(presets[id]["predelay_msec"]), 20.0, 500.0)
	for row: Dictionary in AudioData.table(AudioData.MUSIC)["zones"]:
		if row.has("reverb"):
			assert_true(presets.has(str(row["reverb"])), "zone %s names a preset" % row["scene"])
	assert_true(
		float(presets["stone_shrine"]["wet"]) < float(presets["drowned_cave"]["wet"]) / 2.0,
		"the shrine's SFX carry their own room, so its bus reverb stays low"
	)
	_done()


func test_world_and_combat_carry_a_reverb() -> void:
	for bus in [&"World", &"Combat"]:
		assert_true(WorldVerb.effect_on(bus) != null, "%s has an AudioEffectReverb" % bus)
	dir.setup(MIX, MUSIC, {"sfx": {}})
	var idx := AudioServer.get_bus_index(&"World")
	var count := 0
	for i in AudioServer.get_bus_effect_count(idx):
		count += 1 if AudioServer.get_bus_effect(idx, i) is AudioEffectReverb else 0
	assert_eq(count, 1, "set up again, the bus keeps one reverb")
	_done()


func test_zone_swap_ramps_both_buses_to_the_zones_preset() -> void:
	dir.apply_zone("res://lanes.tscn")
	_run(1.1)
	assert_eq(dir.verb.preset, &"lanes")
	assert_between(WorldVerb.effect_on(&"World").wet, 0.099, 0.101)
	dir.apply_zone("res://cave.tscn")
	assert_eq(dir.verb.preset, &"cave")
	_run(0.5)
	assert_true(dir.verb.is_ramping(), "a change ramps")
	assert_between(WorldVerb.effect_on(&"Combat").wet, 0.19, 0.21, "halfway from lanes to cave")
	assert_between(WorldVerb.effect_on(&"Combat").room_size, 0.64, 0.66)
	_run(0.6)
	assert_false(dir.verb.is_ramping())
	for bus in [&"World", &"Combat"]:
		var fx := WorldVerb.effect_on(bus)
		assert_between(fx.wet, 0.299, 0.301, "%s at the cave's wet" % bus)
		assert_between(fx.predelay_msec, 39.9, 40.1)
		assert_true(_enabled(bus), "%s's reverb is on" % bus)
	_done()


func test_a_row_without_reverb_goes_dry_and_switches_off() -> void:
	dir.apply_zone("res://cave.tscn")
	_run(1.1)
	dir.apply_zone("res://title.tscn")
	assert_eq(dir.verb.preset, &"dry", "the default preset")
	_run(0.5)
	assert_true(_enabled(&"World"), "still on while the tail ramps down")
	_run(0.6)
	assert_eq(WorldVerb.effect_on(&"World").wet, 0.0)
	assert_false(_enabled(&"World"), "a dry preset switches the effect off")
	dir.apply_zone("res://nowhere.tscn")
	assert_false(dir.verb.is_ramping(), "an unlisted scene is dry too, and dry is already set")
	_done()


func test_unknown_preset_changes_nothing() -> void:
	dir.apply_zone("res://lanes.tscn")
	_run(1.1)
	assert_false(dir.verb.apply(&"nope"))
	assert_eq(dir.verb.preset, &"lanes")
	_done()


func _enabled(bus: StringName) -> bool:
	var idx := AudioServer.get_bus_index(bus)
	for i in AudioServer.get_bus_effect_count(idx):
		if AudioServer.get_bus_effect(idx, i) is AudioEffectReverb:
			return AudioServer.is_bus_effect_enabled(idx, i)
	return false


func _run(sec: float) -> void:
	var step := 1.0 / 60.0
	var t := 0.0
	while t < sec - 1e-6:
		dir.advance(minf(step, sec - t))
		t += step


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


## Leaves the shared buses dry, as the game's own director expects them.
func _done() -> void:
	dir.verb.apply(&"dry", 0.0)
	dir.free()
