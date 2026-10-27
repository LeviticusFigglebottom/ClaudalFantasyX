extends TestCase
## M3-AUD-825: the Ashcrown strike trial's sounds. AshcrownAudio hears the zone's AshcrownTrial (a real one; it is
## headless) and plays ashcrown_sfx.json's rows: each event's own, a release's run by its outcome, at the bowl or
## the gate when the zone has that node. Then the real zone, attached by the director, catching a strike. Sounds are
## recorded through the listener's player Callable, so nothing plays.

const ZONE := "res://game/levels/ch05/ashcrown/ashcrown.tscn"


class ZoneStandIn:
	extends Node3D
	var trial := AshcrownTrial.new()


var played: Array = []
var saved_state: GameStateData


func before_each() -> void:
	played = []
	saved_state = Game.state
	Game.state = GameStateData.new()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _audio(zone: Node3D) -> AshcrownAudio:
	var a := AshcrownAudio.new(AudioData.table(AudioData.ASHCROWN_SFX))
	a.player_at = func(id: StringName, at: Vector3) -> void: played.append([id, at])
	_host().add_child(a)
	a.attach(zone)
	return a


func _stand_in() -> ZoneStandIn:
	var z := ZoneStandIn.new()
	_host().add_child(z)
	var greybox := Node3D.new()
	greybox.name = "Greybox"
	z.add_child(greybox)
	var bowl := Node3D.new()
	bowl.name = "Bowl_t1"
	bowl.position = Vector3(3, 0, 4)
	greybox.add_child(bowl)
	return z


func _ids() -> Array:
	return played.map(func(p: Array) -> String: return String(p[0]))


func test_every_row_exists() -> void:
	var rows := AudioData.sfx_rows()
	var d := AudioData.table(AudioData.ASHCROWN_SFX)
	var ids: Array = (d.get("events", {}) as Dictionary).values() + (d.get("ran", {}) as Dictionary).values()
	for id: String in ids:
		assert_true(rows.has(id), "%s is an sfx row" % id)
		for f: String in (rows.get(id, {}) as Dictionary).get("files", []):
			assert_true(ResourceLoader.exists(f), "%s exists" % f)


func test_trial_signals_play_their_rows_where_they_happen() -> void:
	var z := _stand_in()
	var a := _audio(z)
	var t := z.trial
	t.caught.emit(&"t1")
	assert_eq(_ids(), ["ash_catch"])
	assert_true((played[0][1] as Vector3).is_equal_approx(Vector3(3, 1, 4)), "at the bowl, lifted off the floor")
	for outcome: StringName in [
		AshcrownTrial.OUT_NEXT, AshcrownTrial.OUT_GROUND, AshcrownTrial.OUT_SEAL, AshcrownTrial.OUT_LANDED
	]:
		t.ran.emit(&"t1", [] as Array[StringName], outcome)
	assert_eq(
		_ids().slice(1),
		["ash_vein_run", "ash_vein_ground", "ash_vein_seal", "ash_vein_run"],
		"a release runs, grounds or meets the seal by its outcome"
	)
	played.clear()
	t.landed.emit()
	t.stud_dark.emit(3)
	t.rotated.emit(&"g_missing", 1)
	assert_eq(_ids(), ["ash_landed", "ash_stud", "ash_gate"], "a gate without a node still sounds")
	a.free()
	z.free()
	_done()


func test_the_real_zone_is_heard_when_a_strike_is_caught() -> void:
	var dir := AudioDirector.new()
	_host().add_child(dir)
	dir.setup(AudioData.table(AudioData.MIX), AudioData.table(AudioData.MUSIC), {"sfx": AudioData.sfx_rows()})
	dir.set_process(false)
	var zone := (load(ZONE) as PackedScene).instantiate() as Ch05AshcrownZone
	_host().add_child(zone)
	dir.attach_ashcrown(zone)
	var a := dir.listeners.get(zone) as AshcrownAudio
	assert_true(a != null, "the director built the listener")
	if a != null:
		a.player_at = func(id: StringName, at: Vector3) -> void: played.append([id, at])
		zone.trial.catch(zone.trial.tier_id(0))
		assert_true(_ids().has("ash_catch"), "catching the first tier's strike sounds (%s)" % [_ids()])
	_host().remove_child(zone)
	zone.free()
	dir.free()
	_done()


func _done() -> void:
	Game.state = saved_state
