extends TestCase
## FAST-TRACK 11-03 (the human's playtest: the storm fights used the normal sunny backdrop and never showed the
## Undertow). BattleStorm: every listed fight is a real encounter with a real look; a storm fight gets rain, wind
## and the Undertow in front of the battle camera, its sun dimmed, and the arena's own resources untouched; a calm
## fight gets none.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const PALETTE := "res://docs/kb/art/palette.json"
const UNDERTOW := "res://game/data/vfx/undertow.json"
## The sim suites' party per fight (tools/balance/targets.json), as the sweep tools use.
const SWEEP := preload("res://tools/vfx/encounter_sweep.gd")


func test_data_names_real_fights_presets_and_swatches() -> void:
	var data := BattleStorm.load_data()
	var db := BattleDB.load_default()
	var presets := (JSON.parse_string(FileAccess.get_file_as_string(UNDERTOW)) as Dictionary)["presets"] as Dictionary
	var swatches := (JSON.parse_string(FileAccess.get_file_as_string(PALETTE)) as Dictionary)["swatches"] as Dictionary
	var looks := data["looks"] as Dictionary
	for enc: String in data["fights"]:
		assert_true(db.encounters.has(StringName(enc)) or db.encounters.has(enc), "%s is an encounter" % enc)
		assert_true(looks.has(str(data["fights"][enc])), "%s has a look" % enc)
	for id: String in looks:
		var look := looks[id] as Dictionary
		assert_true(presets.has(str(look["preset"])), "%s: an undertow.json preset" % id)
		var res := str(look.get("environment_res", ""))
		assert_true(res == "" or ResourceLoader.exists(res), "%s: its environment exists" % id)
		for part in ["rain", "wind", "sun"]:
			var row := look.get(part, {}) as Dictionary
			if row.has("color"):
				assert_eq(str(row["color"]), str((swatches[row["swatch"]] as Dictionary)["hex"]).to_upper(), id)
	for enc in ["ch01_scuttlers", "ch01_hullgnaw", "ch08_stair_hold_1", "undertows_reach", "ch16_storm_wakes"]:
		assert_ne(BattleStorm.look_for(StringName(enc)), &"", "%s is a storm fight" % enc)
	assert_eq(BattleStorm.look_for(&"ch01_wickfry"), &"", "the Underway is calm")
	for enc in ["ch08_headland_gulls", "ch08_headland_crabs", "ch08_flue_moths"]:  # before the storm (B05 < B07)
		assert_eq(BattleStorm.look_for(StringName(enc)), &"", "%s is fought before the storm" % enc)


func test_a_storm_fight_shows_rain_wind_and_the_undertow_in_view() -> void:
	var ctl := _battle(&"ch01_scuttlers", [&"rhen"] as Array[StringName])
	var storm := ctl.stage.get_node_or_null(^"BattleStorm") as BattleStorm
	assert_true(storm != null, "the scuttlers are fought in the storm")
	assert_true(storm.rain != null and storm.rain.emitting, "rain")
	assert_true(storm.wind != null and storm.wind.emitting, "wind")
	assert_true(storm.undertow != null, "the Undertow stands in the background")
	var to_storm := storm.undertow.storm_center() - ctl.stage.camera.global_position
	var fwd := -ctl.stage.choreo.camera.default_transform.basis.z
	var flat := Vector2(to_storm.x, to_storm.z).normalized().dot(Vector2(fwd.x, fwd.z).normalized())
	assert_true(flat > cos(deg_to_rad(40.0)), "it stands in front of the battle camera (%.2f)" % flat)
	assert_false(storm.undertow.exposure_flash, "no screen flashes (battle flash safety)")
	ctl.get_parent().remove_child(ctl)
	ctl.free()


## The Lead (11-03, big47): ONE Undertow per fight. Every storm fight draws exactly one: the arena's, or ours.
func test_no_storm_fight_draws_two_undertows() -> void:
	for enc: String in BattleStorm.load_data()["fights"]:
		var party: Array[StringName] = []
		party.assign(SWEEP.party_for(StringName(enc))[0])
		var ctl := _battle(StringName(enc), party)
		assert_eq(BattleStorm.undertows_in(ctl), 1, "%s draws one Undertow" % enc)
		ctl.get_parent().remove_child(ctl)
		ctl.free()


## A storm arena with its own Undertow owns the vortex and the sky: ours adds wind and no second storm.
func test_an_arena_undertow_is_never_doubled() -> void:
	var ctl := _battle(&"ch01_hullgnaw", [&"rhen"] as Array[StringName])
	var own := UndertowStorm.new()
	own.name = "Undertow"
	own.preset = "ch01_arrival"
	own.rain_amount = 0.5
	ctl.get_node(NodePath(String(BattleArena.ARENA_NODE))).add_child(own)
	var storm := BattleStorm.attached_if_storm(ctl, ctl.engine)
	assert_true(storm.undertow == null, "no Undertow of ours")
	assert_eq(storm.arena_storm, own, "the arena's is the one")
	assert_true(storm.rain == null, "the arena's storm brings the rain")
	assert_true(storm.wind != null, "the wind is ours")
	assert_eq(BattleStorm.undertows_in(ctl), 1, "one Undertow")
	ctl.get_parent().remove_child(ctl)
	ctl.free()


func test_a_calm_fight_has_no_storm() -> void:
	var ctl := _battle(&"sandbox_reef", [&"rhen", &"asha"] as Array[StringName])
	assert_true(ctl.stage.get_node_or_null(^"BattleStorm") == null, "no storm in the sandbox")
	ctl.get_parent().remove_child(ctl)
	ctl.free()


func _battle(enc: StringName, party: Array[StringName]) -> BattleController:
	var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.set_meta(BattleBossIntro.META_PLAYED, String(enc))
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle(party, [] as Array[StringName], enc, 7)
	return ctl


## The storm fights' rest frame tilts up (choreo.json camera.rest_by_encounter) so the sky with the Undertow is in it.
func test_a_storm_fight_rest_frame_tilts_up_to_the_sky() -> void:
	var cam := BattleChoreo.load_data().get("camera", {}) as Dictionary
	var xf := Transform3D(Basis.looking_at(Vector3(0.0, -0.5, -1.0), Vector3.UP), Vector3(0.0, 3.0, 8.0))
	var tilted := BattleCameraDirector.rest_tilt(cam, xf, &"ch01_hullgnaw")
	assert_true((-tilted.basis.z).y > (-xf.basis.z).y, "it looks higher")
	assert_eq(tilted.origin, xf.origin, "from the same place")
	assert_eq(BattleCameraDirector.rest_tilt(cam, xf, &"ch01_wickfry"), xf, "a calm fight keeps its frame")
	for enc: String in BattleStorm.load_data()["fights"]:
		if enc.begins_with("ch01"):  # Ch8's arenas hide the sky (the headland hill, the wall): M3-ENV-1340
			assert_true(
				((cam.get("rest_by_encounter", {}) as Dictionary).get(enc, {}) as Dictionary).has("tilt_up_deg"),
				"%s tilts up to its storm" % enc
			)
