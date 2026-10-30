extends TestCase
## M3-AUD-864, the Act I foley detail pass: the Coilspire flue-key trial is heard (coilspire_sfx.json, through the
## Ashcrown listener: a key turned open or shut by its argument, the cough, a tier lit, the niche, the seized key), a
## used field object plays its own row (interact_sfx.json, by its zone's location and id), every hero carries
## their own gear on the step (footsteps.json foley.gear), and a landed blow says what it struck while a bracing
## shell says it braced (choreo_sfx.json materials, struck, guards). Sounds are recorded through the listeners' player
## Callables, so nothing plays.


class TrialStandIn:
	extends RefCounted
	signal turned(key: StringName, open: bool)
	signal coughed(tier: int)
	signal lit(tier: int)
	signal niche_opened
	signal seized(key: StringName)


class ZoneStandIn:
	extends Node3D
	var trial := TrialStandIn.new()
	var location_id: StringName = &"ch01/oruvel"


var played: Array = []


func before_each() -> void:
	played = []


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func test_the_coilspire_trial_is_heard() -> void:
	var zone := ZoneStandIn.new()
	_host().add_child(zone)
	var a := AshcrownAudio.new(AudioData.table(AudioData.COILSPIRE_SFX))
	a.player_at = func(id: StringName, at: Vector3) -> void: played.append(id)
	_host().add_child(a)
	a.attach(zone)
	zone.trial.turned.emit(&"t1_a", true)
	zone.trial.turned.emit(&"t1_a", false)
	zone.trial.coughed.emit(1)
	zone.trial.lit.emit(1)
	zone.trial.niche_opened.emit()
	zone.trial.seized.emit(&"t3_seized")
	assert_eq(
		played,
		[&"flue_key_open", &"flue_key_shut", &"flue_cough", &"flue_lit", &"flue_niche_open", &"flue_key_seized"],
		"each flue-key event plays its own row, the turn by open or shut"
	)
	var bank := AudioData.sfx_rows()
	for id: StringName in played:
		assert_true(bank.has(String(id)), "%s is a row" % id)
	a.free()
	zone.free()
	_done()


func test_a_used_object_plays_its_own_row_at_its_place() -> void:
	var zone := ZoneStandIn.new()
	_host().add_child(zone)
	var area := Interactable.new()
	area.id = &"lashing_a"
	area.position = Vector3(2, 0, 3)
	zone.add_child(area)
	var a := InteractAudio.new(AudioData.table(AudioData.INTERACT_SFX))
	a.player_at = func(id: StringName, at: Vector3) -> void: played.append([id, at])
	_host().add_child(a)
	a.watch(area)
	a.watch(area)  # watched once
	area.used.emit(area)
	assert_eq(played.size(), 1, "one sound for one use")
	assert_eq(played[0][0], &"obj_rope_cut", "the Oruvel lashing is cut")
	assert_true((played[0][1] as Vector3).is_equal_approx(Vector3(2, 0.9, 3)), "at the object")
	var other := Interactable.new()
	other.id = &"npc_cook"
	zone.add_child(other)
	a.watch(other)
	other.used.emit(other)
	assert_eq(played.size(), 1, "a talker has no object sound (its dialogue speaks)")
	var bank := AudioData.sfx_rows()
	for row: Variant in (AudioData.table(AudioData.INTERACT_SFX)["by_id"] as Dictionary).values():
		assert_true(bank.has(str(row)), "%s is a row" % row)
	a.free()
	zone.free()
	_done()


func test_every_hero_carries_their_own_gear() -> void:
	var foley := AudioData.table(AudioData.FOOTSTEPS)["foley"] as Dictionary
	var gear := foley["gear"] as Dictionary
	var bank := AudioData.sfx_rows()
	var seen := {}
	for hero: String in ["rhen", "asha", "toma", "ysolde", "kerrid", "liss"]:
		assert_true(gear.has(hero), "%s has gear (not the default lantern)" % hero)
		assert_true(bank.has(str(gear.get(hero, ""))), "%s's gear is a row" % hero)
		seen[str(gear.get(hero, ""))] = true
	assert_eq(seen.size(), 6, "six heroes, six sounds")
	_done()


func _result(actor: StringName, target: StringName, amount: int) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = actor
	r.skill_id = &"attack"
	r.hits = [{"target_id": target, "hit": true, "amount": amount}]
	return r


func test_a_blow_says_what_it_struck() -> void:
	var c := ChoreoAudio.new(AudioData.table(&"choreo_sfx"))
	assert_eq(c.struck_row("melee", _result(&"rhen", &"reef_crab#1", 12)), &"struck_shell", "hooks on a crab's shell")
	assert_eq(c.struck_row("melee", _result(&"rhen", &"lantern_eel", 12)), &"struck_soft", "and on an eel's flank")
	assert_eq(c.struck_row("melee", _result(&"kerrid", &"drownbell", 30)), &"struck_metal", "the cleaver on the bell")
	assert_eq(c.struck_row("melee", _result(&"rhen", &"reef_crab", 0)), &"", "a miss strikes nothing")
	assert_eq(c.struck_row("cast", _result(&"asha", &"reef_crab", 12)), &"", "a spell is the element hit's alone")
	assert_eq(c.struck_row("guard", _result(&"slag_tortoise", &"slag_tortoise", 0)), &"guard_stone", "a stone brace")
	assert_eq(c.struck_row("guard", _result(&"rhen", &"rhen", 0)), &"", "a hero's guard keeps the shared accent")
	assert_eq(c.weapon_of(&"liss"), "launcher", "Liss's launcher, not a claw")
	var bank := AudioData.sfx_rows()
	var table := AudioData.table(&"choreo_sfx")
	for section: String in ["struck", "guards"]:
		for row: Variant in (table[section] as Dictionary).values():
			assert_true(bank.has(str(row)), "%s is a row" % row)
	c.free()
	_done()


func _done() -> void:
	pass
