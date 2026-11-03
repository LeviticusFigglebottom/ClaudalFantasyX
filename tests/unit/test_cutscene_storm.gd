extends TestCase
## FAST-TRACK (the 11-03 playtest: the storm scenes must show the vortex): `@storm view` runs the Undertow's clock,
## thins the zone fog and lights the storm's top for a storm shot, and `@storm off` puts every one of them back.

const SEQUENCER_JSON := "res://game/data/cutscene/sequencer.json"
const CUES_JSON := "res://game/data/dialogue/cues.json"
const ZONE_FOG := 0.0012
const ZONE_SUN := 0.55
const LOOK := {"playing": true, "time_scale": 1.0, "fog_density": 0.00001, "sun_energy": 2.0}


func _storm() -> UndertowStorm:
	var storm := UndertowStorm.new()
	storm.playing = false
	var we := WorldEnvironment.new()
	we.environment = Environment.new()
	we.environment.fog_enabled = true
	we.environment.fog_density = ZONE_FOG
	storm.world_environment = we
	var sun := DirectionalLight3D.new()
	sun.light_energy = ZONE_SUN
	storm.sun = sun
	return storm


func _free(storm: UndertowStorm) -> void:
	storm.world_environment.free()
	storm.sun.free()
	storm.free()


func test_view_runs_the_clock_thins_the_fog_and_lights_the_top() -> void:
	var storm := _storm()
	var zone_env := storm.world_environment.environment
	CutsceneStorm.view(storm, LOOK)
	assert_true(storm.playing, "the vortex turns during the view")
	assert_true(absf(storm.world_environment.environment.fog_density - 0.00001) < 1e-9, "the look's fog")
	assert_true(absf(zone_env.fog_density - ZONE_FOG) < 1e-9, "the zone's own Environment is never edited")
	assert_true(absf(storm.sun.light_energy - 2.0) < 1e-6, "the storm's top in full sun")
	_free(storm)


func test_off_restores_everything() -> void:
	var storm := _storm()
	var zone_env := storm.world_environment.environment
	CutsceneStorm.view(storm, LOOK)
	CutsceneStorm.view(storm, LOOK)  # a second view keeps the first saved state
	CutsceneStorm.restore(storm)
	assert_false(storm.playing, "the zone's held clock again")
	assert_eq(storm.world_environment.environment, zone_env, "the zone's Environment back")
	assert_true(absf(storm.sun.light_energy - ZONE_SUN) < 1e-6, "the zone's sun back")
	assert_false(storm.has_meta(CutsceneStorm.META_SAVED), "nothing left armed")
	CutsceneStorm.restore(storm)  # a second off is harmless
	assert_false(storm.playing)
	_free(storm)


func test_find_skips_a_scene_without_a_storm() -> void:
	var root := Node3D.new()
	root.add_child(Node3D.new())
	assert_true(CutsceneStorm.find(root) == null, "no Undertow, no storm shot")
	root.free()


func test_every_storm_look_is_in_the_data_and_the_vocabulary() -> void:
	var seq: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SEQUENCER_JSON))
	var cues: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CUES_JSON))
	var looks: Dictionary = seq[CutsceneStorm.KEY][CutsceneStorm.KEY_LOOKS]
	assert_true(looks.has(str(seq[CutsceneStorm.KEY][CutsceneStorm.KEY_DEFAULT])), "the default look exists")
	var vocab: Array = cues["sets"]["storm_looks"]
	assert_eq(vocab.size(), looks.size(), "cues.json storm_looks names every look")
	for id: String in looks.keys():
		assert_true(vocab.has(id), "%s is a dlgc storm look" % id)
