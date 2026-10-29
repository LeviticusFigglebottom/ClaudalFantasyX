extends TestCase
## M3-C05-02: Ch5 "Terraces of Ash" end to end, headless, on the real chapter data
## (game/data/flow/chapters/ch05.json) and the two greybox zones: Pemakar at Harbour (Ch4's hand-off)
## → the ferry and Asha's first band → the barks (the ferryman's tale) → Garo's side scene → the boats
## and Rhen's choice → the weir and Kerrid → the inn gate → Ashcrown's stair (the banters, the
## slag tortoise pair) → the crown → the trial, tier by tier (a faded charge, the sealed side vein and
## the Quench Charm, the plate) → the Matron → Kahre and the second verse → Pemakar after → the dawn
## → the Brine Shoals (Ch6, at Entry). Instant sequencers; every hand-off is recorded through
## ZoneStory.hand_off, and every fight is played in the real field battle to a forced win.
## Also the watches: Kerrid's three lines and nothing to Rhen, no glow on his hands (no @vfx at him),
## Asha leading no rite at Lanternfall, the three exclusive boat flags, and Kell's wick unburned.

const PEMAKAR := "res://game/levels/ch05/pemakar/pemakar.tscn"
const ASHCROWN := "res://game/levels/ch05/ashcrown/ashcrown.tscn"
const BATTLE := "res://game/flow/field_battle.tscn"
const SAVE_DIR := "user://test_ch05_thread_saves"
const MAX_TURNS := 120
const STAGING_WARNINGS: Array[String] = ["no shot", "no mark", "no actor", "cannot place", "no look_at"]
const BOAT_FLAGS: Array[StringName] = [&"ch05_boat_for_kell", &"ch05_boat_for_oruvel", &"ch05_kept_leaf_boat"]
## ADR 0020 (d): Kerrid's whole part in Ch5.
const KERRID_LINES: Array[StringName] = [&"ch05_weir_002", &"ch05_weir_006", &"ch05_weir_008"]
const STORY_PARTY: Array[StringName] = [&"rhen", &"asha", &"kerrid"]
const STORY_RESERVE: Array[StringName] = [&"toma", &"ysolde"]

var saved_state: GameStateData
var saved_dir := ""
var zone: Ch05Zone
var story: ZoneStory
var hand_offs: Array[Array] = []
var travels: Array[Array] = []
var lines: Array[StringName] = []
## line id -> speaker id, for every line the main sequencer showed.
var speakers: Dictionary = {}
## Every @vfx cue played: its kwargs.
var vfx: Array[Dictionary] = []
var restore_at_line: Dictionary = {}
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
	speakers.clear()
	vfx.clear()
	restore_at_line.clear()
	warnings.clear()


func test_ch5_plays_from_the_harbour_to_the_end_card() -> void:
	_give(&"kell_wick", 1)  # Ch1's wick, as a player arrives with it
	_pemakar_night()
	_ashcrown()
	_pemakar_after()
	_check_staging()
	_check_watches()
	_done()


func test_each_boat_choice_sets_exactly_one_flag_and_kells_wick_stays_unburned() -> void:
	for choice in BOAT_FLAGS.size():
		Game.state = GameStateData.new()
		Game.set_flag(&"ch05_arrived")
		_give(&"kell_wick", 1)
		_open(PEMAKAR)
		story.sequencer.auto_choice = choice
		assert_true(_trigger(&"crown_bell").on_touched())
		for i in BOAT_FLAGS.size():
			assert_eq(bool(Game.get_flag(BOAT_FLAGS[i])), i == choice, "choice %d: %s" % [choice, BOAT_FLAGS[i]])
		assert_eq(_count(&"pemakar_leaf_boat"), 1 if BOAT_FLAGS[choice] == &"ch05_kept_leaf_boat" else 0)
		assert_eq(_count(&"kell_wick"), 1, "Kell's wick stays in the tin (ADR 0022 sweep-H)")
		assert_eq(
			&"ch05_boats_004" in lines, BOAT_FLAGS[choice] == &"ch05_kept_leaf_boat", "'Then carry it' only for Not yet"
		)
		_close()
		lines.clear()
		hand_offs.clear()
	_done()


func test_the_smith_is_the_fallback_after_the_binding() -> void:
	for f: StringName in [&"ch05_arrived", &"ch05_met_kerrid", &"ch05_kahre_bound", &"ch05_after_seen"]:
		Game.set_flag(f)
	_open(PEMAKAR)
	story.begin()
	assert_true(_trigger(&"npc_garo").try_interact())
	assert_true(&"ch05_smith_001" in lines, "his boat has already gone down; he asks anyway")
	assert_false(&"ch05_smith_002" in lines)
	assert_true(bool(Game.get_flag(&"ch05_told_the_smith")))
	assert_false(_trigger(&"npc_garo").is_available(), "once")
	_done()


func test_the_trial_answers_only_once_the_rite_is_given() -> void:
	Game.set_flag(&"ch05_tortoises_won")
	_open(ASHCROWN)
	var crown := zone as Ch05AshcrownZone
	assert_false(crown.act("catch", "t1"), "no rite, no catch")
	assert_false(crown.trial.charged)
	assert_true(_trigger(&"crown").on_touched())
	assert_true(crown.act("catch", "t1"))
	_done()


func _pemakar_night() -> void:
	_open(PEMAKAR)
	assert_false(zone.block_shown("kerrid"), "no stranger before the weir")
	story.begin()
	assert_true(bool(Game.get_flag(&"ch05_arrived")), "B01")
	assert_eq(Game.state.chapter, 5, "the chapter step")
	assert_eq(Game.state.party_ids, [&"rhen", &"asha", &"toma"] as Array[StringName])
	assert_eq(Game.state.reserve_ids, [&"ysolde"] as Array[StringName])
	assert_true(&"ch05_ferry_002" in lines, "N-01: Asha's first band")
	assert_true(_at(&"Harbour"))

	assert_true(_trigger(&"bark_ferryman").on_touched())
	assert_true(bool(Game.get_flag(&"ch05_heard_straw_cape_tale")), "the straw-cape tale, overheard")
	for id: StringName in [
		&"bark_boat_folders", &"bark_lacquer", &"bark_forge_child", &"bark_grave_step", &"bark_grave_child"
	]:
		assert_true(_trigger(id).on_touched(), "%s plays" % id)

	assert_true(_trigger(&"npc_garo").try_interact())
	assert_true(bool(Game.get_flag(&"ch05_told_the_smith")), "B03")
	assert_true(&"ch05_smith_002" in lines and &"ch05_smith_014" in lines, "the night opening, then a better version")
	assert_false(story.busy)

	assert_true(_trigger(&"crown_bell").on_touched())
	assert_true(bool(Game.get_flag(&"ch05_boat_for_kell")), "'For Mother Kell.' (the first option)")
	assert_eq(_count(&"kell_wick"), 1, "the seller's wick, not Kell's")
	assert_true(&"ch05_boats_008" in lines, "the motes follow the boats down")
	assert_true(bool(Game.get_flag(&"ch05_met_kerrid")), "B05")
	assert_true(zone.block_shown("kerrid"))
	assert_eq(Game.state.party_ids, STORY_PARTY, "Kerrid joins")
	assert_eq(Game.state.reserve_ids, STORY_RESERVE)
	assert_false(_trigger(&"bark_ferryman").is_available(), "the tale is never told in his sight")
	assert_true(&"ch05_inn_001" in lines, "B06")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch05/ashcrown", "spawn": "StairFoot"}])
	assert_false(restore_at_line.get(&"ch05_inn_001", true), "the night ends on black")
	_close()


func _ashcrown() -> void:
	_open(ASHCROWN)
	assert_true(zone.place_at(&"StairFoot", zone.spawn_yaw_deg(&"StairFoot")))
	story.begin()
	assert_true(_trigger(&"banter_tenders_gate").on_touched())
	assert_true(_trigger(&"tortoises").on_touched())
	_fight(&"ch05_stair_tortoises", &"ch05/ashcrown", &"AfterTortoises", &"ch05_tortoises_won", STORY_PARTY)
	_reopen(ASHCROWN, &"AfterTortoises")
	assert_false(_trigger(&"tortoises").on_touched(), "a won fight never starts again")
	assert_eq(hand_offs.size(), 0)
	assert_true(zone.encounters != null, "the stair has random fights")
	assert_true(_trigger(&"banter_grave_tier").on_touched())
	assert_true(_trigger(&"banter_copper_tier").on_touched())

	assert_true(_trigger(&"crown").on_touched())
	assert_true(bool(Game.get_flag(&"ch05_trial_begun")), "B08: the rite")
	assert_true(&"ch05_crown_002" in lines)
	assert_true(_at(&"Crown"))
	var crown := zone as Ch05AshcrownZone
	var trial := crown.trial

	assert_true(_trigger(&"rod_t1").try_interact())
	assert_true(trial.charged)
	assert_true(_trigger(&"gate_g1").try_interact())
	assert_true(_trigger(&"release_t1").try_interact())
	assert_eq(trial.tier, 1, "tier one teaches the loop")
	assert_false(crown.block_shown("Stair_t2"), "the stair down opens as the strike pours")

	crown.walk_metres(float(trial.data["metres_per_stud"]) * trial.studs())
	assert_false(trial.charged, "walked too far: the charge fades")
	assert_true(_trigger(&"rod_t2").try_interact(), "caught again on tier two")
	assert_true(_trigger(&"gate_g2a").try_interact())
	for _i in 3:
		_trigger(&"gate_g2b").try_interact()
	assert_true(_trigger(&"release_t2").try_interact())
	assert_eq(trial.tier, 2)

	assert_true(_trigger(&"gate_g3a").try_interact())
	assert_false(_trigger(&"quench_charm").is_available(), "the alcove is sealed")
	assert_true(_trigger(&"release_t3").try_interact())
	assert_eq(crown.last_outcome, AshcrownTrial.OUT_SEAL, "the sealed side vein")
	assert_true(bool(Game.get_flag(&"ch05_quench_alcove_open")))
	assert_false(crown.block_shown("QuenchSeal"))
	assert_true(_trigger(&"quench_charm").try_interact())
	assert_true(bool(Game.get_flag(&"ch05_found_quench_charm")))
	assert_eq(_count(&"quench_charm"), 1)
	assert_true(_trigger(&"rod_t3").try_interact())
	assert_true(_trigger(&"gate_g3a").try_interact())
	for _i in 3:
		_trigger(&"gate_g3c").try_interact()
	assert_true(_trigger(&"release_t3").try_interact())
	assert_eq(trial.tier, 3)

	assert_true(_trigger(&"gate_g4a").try_interact())
	assert_true(_trigger(&"gate_g4a").try_interact())
	assert_true(_trigger(&"gate_g4b").try_interact())
	assert_true(_trigger(&"release_t4").try_interact())
	assert_eq(crown.last_outcome, AshcrownTrial.OUT_OPEN, "nobody on the right plate")
	assert_true(_trigger(&"plate_p4a").try_interact())
	var toma := crown.stage.actor(&"toma")
	assert_true(toma.position.distance_to(crown.stage.mark(&"plate_p4a").position) < 0.01, "Toma moves to the plate")
	assert_true(_trigger(&"release_t4").try_interact())
	assert_true(bool(Game.get_flag(&"ch05_strike_landed")), "the strike hits the anvil-stone")
	assert_false(_trigger(&"rod_t1").is_available(), "the trial is over")

	assert_true(_trigger(&"anvil_court").on_touched())
	assert_true(&"ch05_matron_001" in lines, "the Tender's one setup line")
	_fight(
		&"ch05_cinder_matron", &"ch05/ashcrown", &"AnvilCourt", &"ch05_matron_quieted", [&"kerrid", &"rhen", &"asha"]
	)
	_reopen(ASHCROWN, &"AnvilCourt")
	assert_true(bool(Game.get_flag(&"ch05_kahre_bound")), "B10")
	assert_true(bool(Game.get_flag(&"ch05_second_verse_sung")))
	assert_true(&"ch05_kahre_012" in lines, "Asha on the Quench Charm")
	assert_true(&"ch05_kahre_020" in lines, "Lift your chin")
	var kahre := zone.stage.actor(&"kahre")
	assert_true(
		kahre.global_position.distance_to(zone.stage.mark(&"kahre_bound_at").global_position) < 0.01,
		"A11: Kahre's own body stands behind the chamber door"
	)
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch05/pemakar", "spawn": "FromAshcrown"}])
	assert_true((zone as Ch05AshcrownZone).trial.done, "a return after the landing builds the trial solved")
	_close()


func _pemakar_after() -> void:
	_open(PEMAKAR)
	var sun_energy := zone.sun.light_energy
	story.begin()
	assert_true(bool(Game.get_flag(&"ch05_after_seen")), "B11")
	assert_true(_at(&"FromAshcrown"))
	assert_true(zone.block_shown("kerrid"), "a man still standing at the gate")
	assert_true(zone.stage.actor(&"kerrid").position.distance_to(zone.stage.mark(&"inn_gate").position) < 0.01)
	assert_false(zone.block_shown("elder"), "the festival's cast has gone home")
	assert_true(sun_energy > 0.5, "the day variant (the stand-in afternoon light)")
	assert_false(_trigger(&"crown_bell").is_available(), "Lanternfall is over")
	assert_false(_trigger(&"npc_garo").is_available(), "Garo was told already")
	assert_true(_trigger(&"bark_after_band").on_touched())
	assert_true(_trigger(&"harbour_road").on_touched())
	assert_true(bool(Game.get_flag(&"ch05_done")))
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch06/brine_shoals", "spawn": "Entry"}], "on to Ch6")
	assert_false(restore_at_line.has(&"ch05_dawn_001"), "the dawn has no line")
	_close()


func _check_watches() -> void:
	var kerrid: Array[String] = []
	for lid: StringName in speakers:
		if speakers[lid] == &"kerrid":
			kerrid.append(String(lid))
	kerrid.sort()
	var want: Array[String] = []
	for lid in KERRID_LINES:
		want.append(String(lid))
	assert_eq(kerrid, want, "ADR 0020 (d): Kerrid's three lines, and nothing to Rhen")
	for k in vfx:
		assert_ne(str(k.get("at", "")), "kerrid", "ADR 0022 (g): no glow on Kerrid")
	for lid: StringName in speakers:
		if String(lid).begins_with("ch05_boats_") and speakers[lid] == &"asha":
			assert_true(
				lid in [&"ch05_boats_004", &"ch05_boats_006", &"ch05_boats_008"], "ADR 0017: Asha leads no rite"
			)


## Plays the pending request in the real field battle to a forced win and presses Return.
func _fight(
	encounter: StringName, location: StringName, spawn: StringName, flag: StringName, party: Array[StringName]
) -> void:
	assert_true(not hand_offs.is_empty() and hand_offs.back()[0] == ZoneStory.KIND_BATTLE, "%s opens" % encounter)
	if hand_offs.is_empty():
		return
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, encounter)
	assert_eq(r.active, party, "%s: the party" % encounter)
	assert_eq(r.reserve, STORY_RESERVE, "%s: Toma and Ysolde in reserve" % encounter)
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
	assert_true(ctl.engine.find(&"kerrid") != null, "Kerrid fights")
	for _i in MAX_TURNS:
		if ctl.state == BattleController.STATE_RESULT:
			break
		for foe in ctl.engine.enemies:
			foe.hp = mini(foe.hp, 1)  # force a quick win; the controller never writes combatant state
		var foes := ctl.engine.living_foes_of(ctl.engine.current)
		if foes.is_empty():
			break
		ctl.act(&"attack", [foes[0].id])
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY, "%s won" % encounter)
	ctl.hud.result.accept()
	_host().remove_child(ctl)
	ctl.free()
	assert_true(bool(Game.get_flag(flag)), "%s sets %s" % [encounter, flag])
	assert_eq(travels.back(), [location, spawn], "%s returns to the zone" % encounter)


func _open(path: String) -> void:
	zone = (load(path) as PackedScene).instantiate() as Ch05Zone
	story = zone.story
	story.autostart = false
	_host().add_child(zone)
	zone.set_process(false)
	zone.set_physics_process(false)
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
			speakers[s.line_id] = s.speaker
			restore_at_line[s.line_id] = story.sequencer.restore_fade
	)
	story.sequencer.cue_played.connect(
		func(cue: StringName, _a: Array, kw: Dictionary) -> void:
			if cue == &"vfx":
				vfx.append(kw)
	)
	story.hand_off = func(kind: StringName, target: Variant) -> void: hand_offs.append([kind, target])


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


func _give(item: StringName, n: int) -> void:
	Inventory.new(ItemDB.load_default(), Game.state.inventory).add(item, n)


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
