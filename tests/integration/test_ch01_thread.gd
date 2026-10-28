extends TestCase
## M3-C01-02: Ch1 "Lamp-Diver" end to end, headless, on the real chapter data
## (game/data/flow/chapters/ch01.json) and the two greybox zones: the prologue's hand-off → the
## Underway (the card and the drop, the tether, the first bell-room's rest and scene, the hinge, the
## shutter prompt and the old tin the open shutter finds, the glassfry shoal, the low lights, the oil
## slug, the gauge-wheel, the shaft) → Oruvel (the scale-hull sale, the barks, Kell's stall and the
## wick, the gulls and the Rising, the run, the scuttlers, the lashings, the children, Hullgnaw) →
## going under → ch02/haluna at Beach, where Cutscene A plays as before. Instant sequencers; every
## hand-off is recorded through ZoneStory.hand_off, and every fight is played in the real field
## battle (one hero, no reserve) to a forced win, as test_fp_thread does.

const PROLOGUE := "res://game/levels/prologue/prologue.tscn"
const UNDERWAY := "res://game/levels/ch01/oruvel_underway/oruvel_underway.tscn"
const ORUVEL := "res://game/levels/ch01/oruvel/oruvel.tscn"
const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const BATTLE := "res://game/flow/field_battle.tscn"
const SAVE_DIR := "user://test_ch01_thread_saves"
const MAX_TURNS := 80
## Staging problems a scene must never have on its own stage (music and sounds are Audio's, still to
## come; placeholder cue keys are the sequencer's).
const STAGING_WARNINGS: Array[String] = ["no shot", "no mark", "no actor", "cannot place", "no look_at"]

var saved_state: GameStateData
var saved_dir := ""
var zone: Ch01Zone
var story: ZoneStory
var hand_offs: Array[Array] = []
var travels: Array[Array] = []
var lines: Array[StringName] = []
var restore_at_line: Dictionary = {}
## Every sequencer warning of every zone opened in the test (collected as each closes).
var warnings: Array[String] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	BattleRequest.clear()
	BattleRequest.change_scene = func(_p: String) -> void: pass
	saved_dir = SaveSystem.save_dir
	SaveSystem.save_dir = SAVE_DIR
	hand_offs.clear()
	travels.clear()
	lines.clear()
	restore_at_line.clear()
	warnings.clear()


func test_ch1_plays_from_the_prologue_to_haluna() -> void:
	# The prologue hands off to the Underway's drop.
	var prologue := (load(PROLOGUE) as PackedScene).instantiate() as PrologueScene
	prologue.autoplay = false
	_host().add_child(prologue)
	var pseq := CutsceneSequencer.new()
	pseq.instant = true
	prologue.add_child(pseq)
	prologue.sequencer = pseq
	prologue.travel = func(loc: StringName, spawn: StringName) -> bool:
		travels.append([loc, spawn])
		return true
	# Act I's route (the M2 review build still goes to Haluna until the Lead flips the switch).
	prologue.next_location = &"ch01/oruvel_underway"
	prologue.next_spawn = &"Drop"
	prologue.play()
	_host().remove_child(prologue)
	prologue.free()
	assert_eq(travels, [[&"ch01/oruvel_underway", &"Drop"]] as Array[Array], "the prologue hands off to Ch1")

	_underway()
	_oruvel()
	_going_under_to_haluna()
	_check_staging()
	_done()


func test_kell_first_starts_the_run_at_her_bridge() -> void:
	for f: StringName in [&"ch01_cut_gauge_wheel", &"ch01_sold_gauge_wheel", &"ch01_has_kell_wick"]:
		Game.set_flag(f)
	_open(ORUVEL)
	story.sequencer.auto_choice = 1  # "Kell first."
	assert_true(_trigger(&"dive_mooring").on_touched())
	assert_true(bool(Game.get_flag(&"ch01_ran_for_kell")), "the choice is recorded for Ch7")
	assert_true(_at(&"KellRun"), "the run starts at her bridge")
	assert_true(&"ch01_bridge_001" in lines, "and the bridge goes")
	assert_false((zone as Ch01OruvelZone).block_shown("DiveBridge"), "the way to her is gone")
	assert_false(story.busy)
	_close()
	_done()


func _underway() -> void:
	_open(UNDERWAY)
	var uw := zone as Ch01UnderwayZone
	story.begin()
	assert_true(bool(Game.get_flag(&"ch01_started")), "C1-01")
	assert_eq(Game.state.party_ids, [&"rhen"] as Array[StringName], "Rhen alone")
	assert_true(&"ch01_drop_002" in lines, "the drop's VO")
	assert_true(bool(Game.get_flag(&"tut_movement_seen")), "the movement prompt, once")
	assert_eq(_count(&"salt_tonic"), 2, "the diver's kit")
	assert_true(_at(&"Drop"))

	assert_true(_trigger(&"tether_hint").on_touched())
	assert_true(bool(Game.get_flag(&"tut_tether_seen")), "the tether prompt")
	assert_true(_trigger(&"tether_crown").try_interact())
	assert_true(_at(&"BellRoom1"), "the tether drops a floor")

	assert_true(_trigger(&"bell_room_1").on_touched())
	assert_eq(uw.rests, 1, "a bell-room is a rest point")
	assert_true(&"ch01_bell_003" in lines, "C1-03")
	assert_false(_trigger(&"bell_room_1").is_available(), "the scene plays once")
	assert_true(_trigger(&"bell_rest_1").on_touched())
	assert_eq(uw.rests, 2, "and rests on every entry")
	assert_true(_trigger(&"hinge").try_interact())
	assert_eq(_count(&"lit_age_brass"), 1, "the interact lesson: a brass hinge")

	assert_true(_trigger(&"tether_bell").try_interact())
	assert_true(_at(&"Gallery"))
	assert_true(_trigger(&"shutter_hint").on_touched())
	assert_true(bool(Game.get_flag(&"tut_shutter_seen")), "the shutter prompt")
	var tin := _trigger(&"old_tin")
	assert_false(tin.is_in_group(Interactable.GROUP), "the old tin is hidden behind the coral curtain")
	uw.set_shutter(true)
	assert_true(tin.is_in_group(Interactable.GROUP) and not uw.block_shown("CoralCurtain"), "the open light finds it")
	assert_true(tin.try_interact())
	assert_true(bool(Game.get_flag(&"ch01_found_old_tin")))
	assert_eq(_count(&"salt_tonic"), 4, "two Salt Tonic in the tin")
	uw.set_shutter(false)

	assert_true(_trigger(&"wickfry").on_touched())
	_fight(&"ch01_wickfry", &"ch01/oruvel_underway", &"GalleryAfter", &"ch01_wickfry_won")
	_reopen(UNDERWAY, &"GalleryAfter")
	assert_true(_trigger(&"wickfry").on_touched())
	assert_eq(hand_offs.size(), 0, "a won fight never starts again")

	assert_true(_trigger(&"low_lights").on_touched())
	assert_true(bool(Game.get_flag(&"ch01_saw_low_lights")), "C1-05")
	assert_true(&"ch01_low_003" in lines)

	assert_false(_trigger(&"gauge_wheel").try_interact(), "the wheel waits for the slug")
	assert_true(_trigger(&"oil_slug").on_touched())
	_fight(&"ch01_oil_slug", &"ch01/oruvel_underway", &"GaugeRoom", &"ch01_oil_slug_won")
	_reopen(UNDERWAY, &"GaugeRoom")
	assert_true(_trigger(&"gauge_wheel").try_interact())
	assert_true(bool(Game.get_flag(&"ch01_cut_gauge_wheel")), "C1-06")
	assert_eq(_count(&"gauge_wheel_brass"), 1, "the key item")

	assert_true(_trigger(&"limpet").try_interact())
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, &"ch01_shaft_limpet", "the optional limpet")
	assert_eq(r.escape_spawn, &"ShaftFoot", "can be fled")
	_reopen(UNDERWAY, &"ShaftFoot")

	assert_true(_trigger(&"current_shaft").try_interact())
	assert_true(bool(Game.get_flag(&"ch01_underway_done")), "C1-07")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch01/oruvel", "spawn": "Surface"}])
	assert_false(restore_at_line.get(&"ch01_shaft_001", true), "the rise ends on the fade into Oruvel")
	_close()


func _oruvel() -> void:
	_open(ORUVEL)
	var town := zone as Ch01OruvelZone
	assert_false(town.storm, "Oruvel by day")
	assert_false(town.block_shown("StormWall"))
	var purse := Game.state.currency
	story.begin()
	assert_true(bool(Game.get_flag(&"ch01_sold_gauge_wheel")), "C1-08")
	assert_eq(_count(&"gauge_wheel_brass"), 0, "the wheel is sold")
	assert_eq(Game.state.currency - purse, 50, "forty lume, and ten for haggling (the first option)")
	assert_true(_at(&"ScaleHull"))

	for id: StringName in [&"npc_cook", &"npc_nets", &"npc_pen", &"npc_sadi", &"npc_sabe"]:
		var before := lines.size()
		assert_true(_trigger(id).try_interact(), "%s answers" % id)
		assert_true(lines.size() > before, "%s spoke" % id)
	assert_true(_trigger(&"npc_roof").try_interact())
	assert_true(bool(Game.get_flag(&"ch01_roof_dared")), "he declines with dignity")
	assert_true(_trigger(&"npc_roof").try_interact())
	assert_true(&"ch01_bark_roof_005" in lines, "then does it")

	assert_false(_trigger(&"dive_mooring").is_available(), "the dive waits for Kell's stall")
	assert_true(_trigger(&"kell_stall").on_touched())
	assert_true(bool(Game.get_flag(&"ch01_has_kell_wick")), "C1-10, every path")
	assert_eq(_count(&"kell_wick"), 1, "the key item")
	assert_true(bool(Game.get_flag(&"ch01_kell_side_scene")), "'Stay a minute.' (the first option)")
	assert_true(&"ch01_kell_012" in lines, "the line Rhen repeats on Ch2's beach")

	assert_true(_trigger(&"dive_mooring").on_touched())
	assert_true(bool(Game.get_flag(&"ch01_gulls_cried")), "C1-11")
	var undertow := town.get_node_or_null(^"Undertow") as Node3D
	assert_true(town.storm and (town.block_shown("StormWall") or (undertow != null and undertow.visible)), "the storm")
	assert_false(town.block_shown("SeventhTerrace"), "the Seventh Terrace has run for sea room")
	assert_false(bool(Game.get_flag(&"ch01_ran_for_kell")), "'Go to the net-pen.' (the first option)")
	assert_true(_at(&"RunStart"))
	assert_false(_trigger(&"npc_cook").is_available(), "the town's barks are over")

	assert_true(_trigger(&"scuttlers").on_touched())
	assert_true(&"ch01_scuttlers_001" in lines)
	_fight(&"ch01_scuttlers", &"ch01/oruvel", &"AfterScuttlers", &"ch01_scuttlers_won")
	_reopen(ORUVEL, &"AfterScuttlers")
	town = zone as Ch01OruvelZone
	assert_true(town.storm, "a return from the fight comes up in the storm")
	assert_true(town.block_shown("LowHull"), "the low hull is lashed across the run")
	assert_true(_trigger(&"lashing_a").try_interact())
	assert_true(town.block_shown("LowHull"), "one lashing holds it")
	assert_true(_trigger(&"lashing_b").try_interact())
	assert_false(town.block_shown("LowHull"), "two and it drifts clear")

	assert_false(_trigger(&"hullgnaw").is_available(), "Hullgnaw waits for the children")
	assert_true(_trigger(&"net_pen").on_touched())
	assert_true(bool(Game.get_flag(&"ch01_children_safe")))
	assert_true(_trigger(&"hullgnaw").on_touched())
	assert_eq(town.rests, 1, "a breath before the boss (ADR 0034)")
	assert_true(&"ch01_hullgnaw_002" in lines)
	assert_true(_fight(&"ch01_hullgnaw", &"ch01/oruvel", &"NetPenAfter", &"ch01_hullgnaw_defeated"))


func _going_under_to_haluna() -> void:
	_reopen(ORUVEL, &"NetPenAfter")
	assert_true(bool(Game.get_flag(&"ch01_went_under")), "C1-15")
	assert_true(&"ch01_under_002" in lines, "his father's current-song, then nothing")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch02/haluna", "spawn": "Beach"}])
	assert_false(restore_at_line.get(&"ch01_under_002", true), "it hands off on black")
	_close()
	assert_true(LocationRegistry.load_default().has_location(&"ch02/haluna"))
	# Ch2 is unchanged: Cutscene A plays on arrival at the beach.
	var haluna := (load(HALUNA) as PackedScene).instantiate() as HalunaZone
	_host().add_child(haluna)
	haluna.director.auto_update = false
	haluna.player.set_physics_process(false)
	var hstory := haluna.get_node("Story") as HalunaStory
	hstory.active = true
	hstory.sequencer.instant = true
	hstory.begin()
	assert_true(bool(Game.get_flag(&"ch02_met_asha")), "Cutscene A")
	assert_eq(Game.state.party_ids, [&"rhen", &"asha"] as Array[StringName], "Asha joins on the beach")
	_host().remove_child(haluna)
	haluna.free()


## Plays the pending request in the real field battle (Rhen alone) to a forced win and presses
## Return. Checks the request and the travel back. Returns true when it went as expected.
func _fight(encounter: StringName, location: StringName, spawn: StringName, flag: StringName) -> bool:
	assert_true(not hand_offs.is_empty() and hand_offs.back()[0] == ZoneStory.KIND_BATTLE, "%s opens" % encounter)
	if hand_offs.is_empty():
		return false
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, encounter)
	assert_eq(r.active, [&"rhen"] as Array[StringName], "%s: Rhen alone" % encounter)
	assert_eq(r.reserve, [] as Array[StringName], "%s: no reserve" % encounter)
	assert_eq(r.return_spawn, spawn)
	assert_eq(r.victory_flag, flag)
	_close()
	BattleRequest.submit(r)
	var ctl := (load(BATTLE) as PackedScene).instantiate() as FieldBattle
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.travel = func(loc: StringName, sp: StringName) -> bool:
		travels.append([loc, sp])
		return true
	ctl.open_title = func(_p: String) -> void: pass
	ctl.save_system = SaveSystem
	_host().add_child(ctl)
	ctl.start_sandbox()
	assert_eq(ctl.engine.encounter_id, encounter)
	assert_eq(ctl.engine.party_active.size(), 1, "one hero on the field")
	if encounter == &"ch01_hullgnaw":
		assert_true(ctl.engine.party_active[0].skills.has(&"kick_off"), "Hullgnaw lends Kick Off")
	for _i in MAX_TURNS:
		if ctl.state == BattleController.STATE_RESULT:
			break
		for foe in ctl.engine.enemies:
			foe.hp = mini(foe.hp, 1)  # force a quick win; the controller never writes combatant state
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY, "%s won" % encounter)
	ctl.hud.result.accept()
	_host().remove_child(ctl)
	ctl.free()
	assert_true(bool(Game.get_flag(flag)), "%s sets %s" % [encounter, flag])
	assert_eq(travels.back(), [location, spawn], "%s returns to the zone" % encounter)
	return true


func _open(path: String) -> void:
	zone = (load(path) as PackedScene).instantiate() as Ch01Zone
	story = zone.story
	story.autostart = false
	_host().add_child(zone)
	zone.set_process(false)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	zone.hint.instant = true
	story.active = true
	story.sequencer.instant = true
	story.overhear.instant = true
	story.sequencer.line_shown.connect(
		func(s: DialogueStep) -> void:
			lines.append(s.line_id)
			restore_at_line[s.line_id] = story.sequencer.restore_fade
	)
	story.hand_off = func(kind: StringName, target: Variant) -> void: hand_offs.append([kind, target])


## Opens the zone again where a hand-off left it (the router would), and runs its arrival.
func _reopen(path: String, spawn: StringName) -> void:
	_close()
	hand_offs.clear()
	_open(path)
	assert_true(zone.place_at(spawn, zone.spawn_yaw_deg(spawn)))
	story.begin()


func _close() -> void:
	if zone != null and is_instance_valid(zone):
		warnings.append_array(story.sequencer.warnings)
		_host().remove_child(zone)
		zone.free()
	zone = null


func _check_staging() -> void:
	for w in warnings:
		for needle in STAGING_WARNINGS:
			assert_false(w.contains(needle), "staged on this zone: %s" % w)


func _trigger(id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	fail("no trigger %s" % id)
	return Interactable.new()


func _at(spawn: StringName) -> bool:
	return zone.player.position.distance_to(zone.spawn_marker(spawn).position) < 0.01


func _count(item: StringName) -> int:
	return Inventory.new(ItemDB.load_default(), Game.state.inventory).count(item)


func _done() -> void:
	_close()
	BattleRequest.clear()
	BattleRequest.change_scene = Callable()
	var dir := DirAccess.open(SAVE_DIR)
	if dir != null:
		for f in dir.get_files():
			DirAccess.remove_absolute(SAVE_DIR.path_join(f))
		DirAccess.remove_absolute(SAVE_DIR)
	SaveSystem.save_dir = saved_dir
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
