extends TestCase
## The Lead's Act I onboarding pass (2026-10-29): a load restores the music. A load re-enters the saved zone through
## SceneRouter, whose scene_swapping applies the zone's row (Audio.apply_zone -> AudioData.zone_for, the zone's music
## and its first variant whose flag is set). So for every Act I location: its zone has music, the cue it names is a
## real cue, and a save round trip (SaveSystem.serialize, then deserialize) with each variant's flag set picks the
## same cue as before the save. test_qa_save_shrines covers the zone, party and flags of the same round trip.


func test_every_act1_zone_loads_back_into_its_own_music() -> void:
	var music := AudioData.table(AudioData.MUSIC)
	var checked := 0
	for loc: String in HeroGuardSources.scenes_by_location():
		if not (loc.begins_with("prologue") or (loc.begins_with("ch0") and loc.substr(2, 1).is_valid_int())):
			continue
		var scene := str(HeroGuardSources.scenes_by_location()[loc])
		var row := AudioData.zone_for(music, scene, func(_f: StringName) -> bool: return false)
		assert_true(row.has("music"), "%s: its zone has music (a load would be silent)" % loc)
		var states: Array[StringName] = [&""]
		for row_v: Variant in _variants(music, scene):
			states.append(StringName(str((row_v as Dictionary).get("flag", ""))))
		for flag in states:
			var before := GameStateData.new()
			before.location_id = StringName(loc)
			if flag != &"":
				before.flags[String(flag)] = true
			var after := SaveSystem.deserialize(SaveSystem.serialize(before))
			var cue_before := _cue(music, scene, before)
			var cue_after := _cue(music, scene, after)
			assert_eq(cue_after, cue_before, "%s with %s: the same music after a load" % [loc, flag])
			assert_false(
				AudioData.cue(music, StringName(cue_after)).is_empty(), "%s: cue %s is in music.json" % [loc, cue_after]
			)
			checked += 1
	assert_true(checked >= 16, "every Act I zone was checked (%d states)" % checked)


static func _cue(music: Dictionary, scene: String, state: GameStateData) -> String:
	var row := AudioData.zone_for(
		music, scene, func(f: StringName) -> bool: return bool(state.flags.get(String(f), false))
	)
	return str(row.get("music", ""))


static func _variants(music: Dictionary, scene: String) -> Array:
	for row: Variant in music.get("zones", []):
		if row is Dictionary and str((row as Dictionary).get("scene", "")) == scene:
			return (row as Dictionary).get("variants", []) as Array
	return []
