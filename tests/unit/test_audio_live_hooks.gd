extends TestCase
## M3-AUD-801: hooks switched live once their targets landed (big7). ReefballAudio hooks the real WaterSphereRig (no
## stand-in) and reads its radius from radius_m(); the Ch1 encounter ch01_hullgnaw plays the Hullgnaw theme.

const HULLGNAW_ENCOUNTER := &"ch01_hullgnaw"

var beds: Array[StringName] = []


func test_the_real_water_sphere_rig_is_heard() -> void:
	var table := AudioData.table(AudioData.REEFBALL_HOOKS)
	var hook := {}
	for h: Variant in table.get("hooks", []):
		if str((h as Dictionary).get("class", "")) == "WaterSphereRig":
			hook = h
	assert_false(hook.is_empty(), "a WaterSphereRig hook")
	assert_false(bool(hook.get("pending", false)), "live: the rig is on this branch")
	var r := ReefballAudio.new(table)
	r.player = func(_id: StringName) -> void: pass
	r.player_at = func(_id: StringName, _at: Vector3) -> void: pass
	r.beds_now = func() -> Array[StringName]: return beds.duplicate()
	r.ambience = func(ids: Array[StringName], _sec: float) -> void: beds = ids.duplicate()
	_host().add_child(r)
	var rig := WaterSphereRig.new()
	assert_true(r.wants(rig), "the real class matches by its class_name")
	_host().add_child(rig)
	assert_between(r.radius_of(rig), rig.radius_m() - 0.001, rig.radius_m() + 0.001, "the radius from radius_m()")
	r.watch(rig)
	assert_true(beds.has(&"reefball_crowd_murmur"), "the arena opens on the murmur")
	rig.free()
	r.advance(0.1)
	assert_false(beds.has(&"reefball_crowd_murmur"), "and the stands go quiet with it")
	r.free()


func test_the_hullgnaw_encounter_plays_its_theme() -> void:
	var music := AudioData.table(AudioData.MUSIC)
	var encounters: Array = (
		JSON.parse_string(FileAccess.get_file_as_string("res://game/data/battle/encounters.json")) as Dictionary
	)["encounters"]
	assert_true(encounters.any(func(e: Dictionary) -> bool: return e["id"] == String(HULLGNAW_ENCOUNTER)))
	assert_eq(AudioData.battle_cue(music, HULLGNAW_ENCOUNTER), &"hullgnaw")
	assert_true(ResourceLoader.exists(str((music["cues"] as Dictionary)["hullgnaw"]["file"])), "its file imports")


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
