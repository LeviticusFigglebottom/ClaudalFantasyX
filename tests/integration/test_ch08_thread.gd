extends TestCase
## M3-C08-02: Ch8 "The Seawall" end to end, headless, on the real chapter data
## (game/data/flow/chapters/ch08.json) and the two greybox zones: ch08/corrow at Mole (Ch7's hand-off)
## → B01 (the chapter becomes 8; Kerrid's "Later." and the party step that drops him) → B02 (Ivo, the
## stair, the barks, the shrine) → the wall-gate → ch08/coilspire: the headland's forced fight, Fenn's
## hearth (B03), the Tender's door (B04), the four-tier flue trial (B05: a cough, the side flue's
## needle, Liss's seized key and the mark, two placed fights), the binding (B06), the storm and the
## great key (B07) → Corrow in the storm: B08-B09 and the checkpoint, then the set piece in the REAL
## field battle, four fights with the stair meter carried (Wave 1, the hoist, Wave 2, the stranger,
## Wave 3, "Captain?", the Reach's scripted escape), each between-beat mending the party → B17 (the
## wall falls; the choice) → B18 (the cut rope) → ch09/corrow_night at Strand.
## Instant sequencers; every hand-off is recorded through ZoneStory.hand_off.
## The staging rules a test can see (act1_ch08.md §0): nothing bound is used against the storm (no
## @vfx on Kerrid, no glimmer in B15); "Captain?" has no music line; Kerrid's only line is "Later.";
## Pell says nothing; the figure is gone before Kerrid's hand comes in; Rhen freezes without a word.

const CORROW := "res://game/levels/ch08/corrow/corrow.tscn"
const COILSPIRE := "res://game/levels/ch08/coilspire/coilspire.tscn"
const BATTLE := "res://game/flow/field_battle.tscn"
const SAVE_DIR := "user://test_ch08_thread_saves"
const DIALOGUE_DIR := "res://game/data/dialogue/ch08"
const METER := &"ch08_stair_groups_up"
const MAX_TURNS := 600
## Keeps the Reach just above its floor so one blow takes it into the Breach (its phases are 60/30%).
const REACH_NEAR_FLOOR_PCT := 31
const PCT := 100.0
const STAGING_WARNINGS: Array[String] = ["no shot", "no mark", "no actor", "cannot place", "no look_at"]
## The party as Ch7 leaves it (Ch6's, kept).
const ROAD_PARTY: Array[StringName] = [&"rhen", &"asha", &"kerrid"]
const ROAD_RESERVE: Array[StringName] = [&"toma", &"ysolde", &"liss"]
const CH8_PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]
const CH8_RESERVE: Array[StringName] = [&"ysolde", &"liss"]
## The set piece, in order: encounter, battle party, the victory flag, the quota, the outcome.
const FIGHTS := [
	[&"ch08_stair_hold_1", [&"toma", &"ysolde", &"liss"], &"ch08_wave1_held", 3, &"victory"],
	[&"ch08_stair_hold_2", [&"toma", &"rhen", &"liss"], &"ch08_wave2_held", 4, &"victory"],
	[&"ch08_stair_hold_3", [&"toma", &"liss", &"ysolde"], &"ch08_wave3_held", 4, &"victory"],
	[&"undertows_reach", [&"toma", &"asha", &"liss"], &"ch08_reach_survived", 2, &"scripted_escape"],
]
## The line each between-beat must play before its fight.
const BETWEEN: Array[StringName] = [
	&"ch08_first_down_004", &"ch08_hoist_002", &"ch08_stranger_004", &"ch08_captain_001"
]

var saved_state: GameStateData
var saved_dir := ""
var zone: Ch08Zone
var story: ZoneStory
var hand_offs: Array[Array] = []
var travels: Array[Array] = []
var lines: Array[StringName] = []
var speakers: Dictionary = {}
## Every line and cue the main sequencer played, in order: [&"line", id] or [cue, args, kwargs].
var played: Array[Array] = []
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
	played.clear()
	warnings.clear()


func test_ch8_plays_from_the_mole_to_the_strand() -> void:
	var reg := LocationRegistry.load_default()
	assert_true(reg.is_playable(&"ch08/corrow"), "Corrow is a location")
	assert_eq(reg.spawn_of(&"ch08/corrow"), &"Mole", "where Ch7 hands off")
	Game.state.party_ids = ROAD_PARTY.duplicate()
	Game.state.reserve_ids = ROAD_RESERVE.duplicate()
	_corrow_by_day()
	_coilspire()
	_the_set_piece()
	_the_wall_falls()
	_check_staging()
	_done()


func test_fight_again_puts_the_stair_meter_back() -> void:
	Game.set_flag(&"ch08_hoist_rigged")
	Game.set_flag(METER, 7)
	var r := BattleRequest.make(&"ch08_stair_hold_3", &"ch08/corrow", &"WallHead", &"ch08_wave3_held")
	r.active = [&"toma", &"liss", &"ysolde"] as Array[StringName]
	r.reserve = [&"rhen", &"asha"] as Array[StringName]
	r.objective_flag = METER
	r.objective_start = int(Game.get_flag(METER, 0))
	var ctl := _battle(r)
	Game.set_flag(METER, 9)  # whatever the fight wrote, a retry starts the wave over
	ctl._on_result_choice(BattleController.CHOICE_RETRY)
	assert_eq(int(Game.get_flag(METER, 0)), 7, "the meter as the wave began")
	assert_eq(ctl.engine.encounter_id, &"ch08_stair_hold_3", "the same wave again")
	_host().remove_child(ctl)
	ctl.free()
	_done()


func test_the_flue_trial_rules() -> void:
	var data: Dictionary = GreyboxZone.read_json(Ch08Zone.CH08_FIELD_PATH).get("trial", {})
	var t := CoilspireTrial.new(data)
	var hints := [0]
	t.hint_due.connect(func() -> void: hints[0] += 1)
	assert_eq(t.tier_count(), 4, "four tiers")
	assert_eq(t.turn(&"t2_a"), CoilspireTrial.OUT_NONE, "only the current tier answers")
	assert_eq(t.turn(&"t1_a"), CoilspireTrial.OUT_OPEN)
	assert_eq(t.turn(&"t1_b"), CoilspireTrial.OUT_COUGH, "a key outside the draw splits it")
	assert_true(t.open.is_empty(), "and the tier resets")
	assert_eq(t.turn(&"t1_a"), CoilspireTrial.OUT_OPEN)
	assert_eq(t.turn(&"t1_c"), CoilspireTrial.OUT_LIT)
	assert_eq(t.tier, 1)
	assert_eq(t.turn(&"t2_b"), CoilspireTrial.OUT_OPEN)
	assert_eq(t.turn(&"t2_side"), CoilspireTrial.OUT_COUGH, "the side flue draws only alone")
	assert_false(t.niche_open)
	assert_eq(t.turn(&"t2_side"), CoilspireTrial.OUT_NICHE, "alone, it opens the niche")
	assert_eq(t.turn(&"t2_side"), CoilspireTrial.OUT_SHUT)
	for k: StringName in [&"t2_b", &"t2_c"]:
		t.turn(k)
	assert_eq(t.tier, 2)
	assert_eq(t.turn(&"t3_seized"), CoilspireTrial.OUT_SEIZED, "the seized key won't turn")
	t.advance(float(data.get("hint_sec", 0.0)))
	t.advance(float(data.get("hint_sec", 0.0)))
	assert_eq(hints[0], 1, "one hint a tier")
	t.freed = true
	assert_eq(t.turn(&"t3_seized"), CoilspireTrial.OUT_OPEN, "freed, it turns")
	assert_eq(t.turn(&"t3_a"), CoilspireTrial.OUT_LIT)
	for k: StringName in [&"t4_a", &"t4_b", &"t4_d"]:
		t.turn(k)
	assert_true(t.is_done(), "the flame is at the crown")
	assert_eq(t.turn(&"t4_a"), CoilspireTrial.OUT_NONE, "and the trial is over")
	_done()


func test_only_liss_frees_the_seized_key() -> void:
	Game.set_flag(&"ch08_entered_coilspire")
	Game.set_flag(&"ch08_flue_tiers_lit", 2)
	Game.state.party_ids = CH8_PARTY.duplicate()
	_open(COILSPIRE)
	var coil := zone as Ch08CoilspireZone
	assert_eq(coil.trial.tier, 2, "the climb is restored from its flag")
	assert_false(coil.block_shown("Gate_t2"), "the gates it passed are open")
	assert_false(coil.act("t3_seized"), "nobody else can turn it")
	assert_false(bool(Game.get_flag(&"ch08_liss_found_marks")))
	Game.state.reserve_ids = [&"liss"] as Array[StringName]
	assert_true(coil.act("t3_seized"))
	assert_true(bool(Game.get_flag(&"ch08_liss_found_marks")), "Liss frees it and finds the mark")
	assert_true(coil.trial.open.has(&"t3_seized"), "and the key turns")
	assert_true(&"ch08_stuck_key_007" in lines, "'Don't tell them.'")
	_done()


func test_mend_raises_the_party_to_half() -> void:
	Game.state.party_ids = CH8_PARTY.duplicate()
	Game.state.reserve_ids = CH8_RESERVE.duplicate()
	Game.state.party_vitals = {"rhen": {"hp": 1, "mp": 0}, "asha": {"hp": 0}}
	_open(CORROW)
	var raised := zone.mend("test")
	assert_true(raised.has(&"rhen") and raised.has(&"asha"))
	assert_false(raised.has(&"toma"), "a member at full is left alone")
	var engine := BattleEngine.new()
	var plan := {"active": CH8_PARTY.duplicate(), "reserve": CH8_RESERVE.duplicate(), "encounter": &"ch08_stair_hold_1"}
	var ids: Array[StringName] = CH8_PARTY.duplicate()
	ids.append_array(CH8_RESERVE)
	BattleVitals.setup(engine, BattleDB.load_default(), plan, BattleStage.lattice_for(ids, Game.state.lattice), true)
	var pct := float((zone.ch08_field.get("mend", {}) as Dictionary).get("hp_pct", 0.0))
	assert_true(pct > 0.0)
	for id: StringName in [&"rhen", &"asha"]:
		var c := engine.find(id)
		assert_true(c.hp >= ceili(float(c.max_hp) * pct / PCT), "%s is up to half" % id)
	assert_eq(int(Game.state.vitals_of(&"rhen").get("mp", -1)), 0, "MP is not restored")
	_done()


func test_ch8_scripts_keep_the_chapter_rules() -> void:
	var kerrid_lines: Array[String] = []
	for path in _dlg_files():
		var text := FileAccess.get_file_as_string(path)
		for row in text.split("\n"):
			if row.begins_with("Kerrid"):
				kerrid_lines.append(row)
			assert_false(row.begins_with("Pell"), "Pell says nothing in Ch8: %s" % row)
			assert_false(row.begins_with("@vfx") and row.contains("kerrid"), "no glow on Kerrid: %s" % row)
		if path.ends_with("ch08_captain.dlg"):
			for row in text.split("\n"):
				if row.begins_with("//"):
					continue
				assert_false(row.begins_with("@vfx"), "B15: nothing glows at the stair foot")
				assert_false(row.contains("blend="), "B15: all cuts")
				assert_false(row.begins_with("@music") and not row.contains("silence"), "B15: no music line")
	assert_eq(kerrid_lines.size(), 1, "Kerrid's only line in Ch8 is 'Later.'")
	_done()


func _corrow_by_day() -> void:
	_open(CORROW)
	story.begin()
	assert_eq(Game.state.chapter, 8, "the chapter step")
	assert_true(bool(Game.get_flag(&"ch08_arrived_corrow")), "B01")
	assert_true(&"ch08_landfall_004" in lines, "'Later.'")
	assert_eq(speakers.get(&"ch08_landfall_004"), &"kerrid")
	assert_eq(Game.state.party_ids, CH8_PARTY, "Kerrid has gone")
	assert_eq(Game.state.reserve_ids, CH8_RESERVE)
	assert_false(zone.block_shown("kerrid"), "and isn't on the wall")
	assert_false(zone.block_shown("Lake") or zone.block_shown("Breach"), "the wall stands")
	assert_true(_at(&"MoleStair"), "on the mole stair with the townsfolk (B01 is played there, after W01's arrival)")
	assert_false(_trigger(&"gate").is_available(), "not through the gate before Ivo")
	assert_true(_trigger(&"ivo").on_touched())
	assert_true(bool(Game.get_flag(&"ch08_met_ivo")), "B02: 'Okeru!'")
	assert_true(&"ch08_okeru_001" in lines)
	assert_true(_trigger(&"stair_look").on_touched())
	assert_true(bool(Game.get_flag(&"ch08_saw_the_stair")), "Asha at the stair-head")
	assert_false(_trigger(&"stair_look").is_available(), "once")
	for id: StringName in [&"bark_hobb", &"bark_stillguard", &"bark_kites"]:
		assert_true(_trigger(id).on_touched(), "%s is overheard" % id)
	assert_true(_trigger(&"bark_netmender").try_interact())
	assert_true(&"ch08_bark_netmender_002" in lines, "the pale blocks")
	var rests := zone.rests
	assert_true(_trigger(&"shrine").try_interact())
	assert_eq(zone.rests, rests + 1, "the shrine rests the party")
	assert_eq(Game.state.respawn_spawn, &"Bastion")
	assert_true(_trigger(&"gate").try_interact())
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch08/coilspire", "spawn": "PathFoot"}], "B04")
	_close()


func _coilspire() -> void:
	_open(COILSPIRE)
	var coil := zone as Ch08CoilspireZone
	story.begin()
	assert_true(coil.encounters != null, "the headland has random fights")
	assert_true(ZoneStory.holds((coil.layout.get("encounters", {}) as Dictionary).get("when", {})), "on the path")
	assert_true(_trigger(&"path_fight").on_touched())
	_expect_battle(&"ch08_headland_gulls", &"PathMid", &"ch08_path_fight_won")
	_reopen(COILSPIRE, &"PathMid")
	coil = zone as Ch08CoilspireZone
	assert_false(_trigger(&"path_fight").is_available(), "the forced fight is once")
	assert_true(_trigger(&"hearth").try_interact())
	assert_true(bool(Game.get_flag(&"ch08_fed_the_beacon")), "B03: the keeping flame")
	assert_true(&"ch08_flame_007" in lines, "'Said the girl'd be braver than her.'")
	assert_false(coil.act("t1_a"), "the keys wait for the door")
	assert_true(_trigger(&"door").on_touched())
	assert_true(bool(Game.get_flag(&"ch08_entered_coilspire")), "B04: the Tender lets her in")
	assert_true(_at(&"SpireBase"))
	var inside: Dictionary = (coil.layout.get("encounters", {}) as Dictionary).get("when", {})
	assert_false(ZoneStory.holds(inside), "no random fights inside")
	assert_true(coil.block_shown("Gate_t1") and not coil.block_shown("Flame_t1"), "the flame is at the hearth")
	assert_true(_flue(coil, &"t1_b"), "t1_b")
	assert_eq(coil.last_outcome, CoilspireTrial.OUT_COUGH, "the wrong flue coughs")
	for k: StringName in [&"t1_a", &"t1_c"]:
		assert_true(_flue(coil, k))
	assert_eq(coil.last_outcome, CoilspireTrial.OUT_LIT, "tier 1 draws")
	assert_eq(int(Game.get_flag(&"ch08_flue_tiers_lit", 0)), 1)
	assert_false(coil.block_shown("Gate_t1"), "the way up opens")
	assert_true(coil.block_shown("Flame_t1"))
	assert_true(_trigger(&"moths_1").on_touched())
	_expect_battle(&"ch08_flue_moths", &"Tier2", &"ch08_moths_1_won")
	_reopen(COILSPIRE, &"Tier2")
	coil = zone as Ch08CoilspireZone
	assert_eq(coil.trial.tier, 1, "the trial survives the fight's reload")
	assert_true(_flue(coil, &"t2_side"))
	assert_true(bool(Game.get_flag(&"ch08_found_sail_needle")), "the side flue's niche: the needle")
	assert_false(coil.block_shown("NicheSeal"))
	for k: StringName in [&"t2_side", &"t2_b", &"t2_c"]:
		assert_true(_flue(coil, k))
	assert_eq(coil.trial.tier, 2, "tier 2 draws")
	assert_true(_flue(coil, &"t3_seized"))
	assert_true(bool(Game.get_flag(&"ch08_liss_found_marks")), "B05: Liss and the mark")
	assert_true(&"ch08_stuck_key_004" in lines, "'My—'")
	assert_true(_flue(coil, &"t3_a"))
	assert_eq(coil.trial.tier, 3, "tier 3 draws")
	assert_true(_trigger(&"moths_2").on_touched())
	_expect_battle(&"ch08_flue_moths", &"Tier4", &"ch08_moths_2_won")
	_reopen(COILSPIRE, &"Tier4")
	coil = zone as Ch08CoilspireZone
	for k: StringName in [&"t4_a", &"t4_b", &"t4_d"]:
		assert_true(_flue(coil, k))
	assert_true(bool(Game.get_flag(&"ch08_flame_at_crown")), "the flame is at the crown")
	assert_false(coil.block_shown("Gate_t4"), "the crown door opens")
	assert_true(_trigger(&"crown").on_touched())
	assert_true(bool(Game.get_flag(&"ch08_virel_bound")), "B06: Virel is bound")
	assert_true(&"ch08_binding_002" in lines)
	assert_true(&"ch08_storm_002" in lines, "Ysolde gives the Tender the words")
	assert_true(&"ch08_storm_004" in lines and not &"ch08_storm_005" in lines, "Fenn hands her the key")
	assert_true(_at(&"Gallery"))
	assert_true(coil.block_shown("StormWall"), "the storm against the wind")
	assert_false(bool(Game.get_flag(&"ch08_beacon_opened")), "the player opens it")
	assert_true(_trigger(&"great_key").try_interact())
	assert_true(bool(Game.get_flag(&"ch08_beacon_opened")), "B07")
	assert_true(&"ch08_beacon_opened_001" in lines, "'Down. Now. The stair.'")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch08/corrow", "spawn": "WallGate"}])
	_close()


func _the_set_piece() -> void:
	for i in FIGHTS.size():
		var fight: Array = FIGHTS[i]
		Game.state.party_vitals[String(&"ysolde")] = {"hp": 1}  # hurt; the beat before the fight mends her
		_open(CORROW)
		story.begin()
		assert_true(BETWEEN[i] in lines, "the beat before %s" % fight[0])
		if i == 0:
			assert_true(&"ch08_run_back_002" in lines, "B08: 'He will be where he is needed.'")
			assert_eq(Game.state.respawn_spawn, &"WallHead", "B09's checkpoint")
			assert_true(zone.sun.light_energy < 1.0, "the storm")
		else:
			assert_true(zone.mends.size() == 1, "the party is mended between waves")
			assert_true(int(Game.state.vitals_of(&"ysolde").get("hp", 1 << 20)) > 1, "Ysolde is mended")
		if i == 1:
			assert_true(bool(Game.get_flag(&"ch08_hoist_rigged")), "B11: the hoist")
			assert_true(zone.block_shown("HoistRope"))
		if i == 2:
			assert_true(bool(Game.get_flag(&"ch08_pell_seen")), "B13: the Kirru on the parapet")
			assert_true(zone.block_shown("pell"))
		if i == 3:
			assert_true(bool(Game.get_flag(&"ch08_fishwife_called")), "B15: 'Captain?'")
			assert_eq(speakers.get(&"ch08_captain_001"), &"marra")
		var before := int(Game.get_flag(METER, 0))
		var r := _expect_battle(fight[0], &"WallHead", fight[2])
		assert_eq(str(r.active), str(fight[1]), "the suite's party for %s" % fight[0])
		assert_eq(r.objective_flag, METER, "the stair meter is carried")
		assert_eq(r.objective_start, before)
		Game.set_flag(fight[2], false)
		_play_set_piece(r, fight[4])
		assert_true(bool(Game.get_flag(fight[2])), "%s is held" % fight[0])
		assert_eq(int(Game.get_flag(METER, 0)), before + int(fight[3]), "%s: the groups up are added" % fight[0])
		assert_eq(travels.back(), [&"ch08/corrow", &"WallHead"], "back to the wall-head")
	assert_eq(int(Game.get_flag(METER, 0)), 13, "thirteen groups up the stair in all")


func _the_wall_falls() -> void:
	_open(CORROW)
	story.sequencer.auto_choice = 0
	story.begin()
	assert_true(bool(Game.get_flag(&"ch08_wall_fell")), "B17")
	assert_true(bool(Game.get_flag(&"ch08_rhen_froze")))
	assert_true(bool(Game.get_flag(&"ch08_rhen_told_asha")), "'Someone. In the storm.'")
	assert_true(&"ch08_wall_falls_003" in lines)
	assert_true(bool(Game.get_flag(&"ch08_hoist_cut_down")), "B18: the cut rope")
	assert_true(&"ch08_cut_rope_005" in lines, "'Has anyone seen Ivo Brannick?'")
	assert_true(bool(Game.get_flag(&"ch08_done")))
	assert_true(Game.state.reserve_ids.has(&"kerrid"), "Kerrid walks with them again")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch09/corrow_night", "spawn": "Strand"}], "on to Ch9")
	_check_the_freeze()
	_close()


## B17's frame rule and the freeze, on what the sequencer played.
func _check_the_freeze() -> void:
	var first := _index_of_cue(&"sfx", "wall_breach")
	var start := _index_of_line(&"ch08_wall_falls_001")
	assert_true(first >= 0 and start > first, "the scene played")
	var gone := -1
	var hand := -1
	for i in range(first, start):
		var e: Array = played[i]
		if e[0] == &"mark" and str(e[1][0]) == "figure" and str(e[1][1]) == "figure_gone":
			gone = i
		if hand < 0 and e[0] in [&"mark", &"anim"] and str(e[1][0]) == "kerrid" and gone >= 0:
			hand = i
	assert_true(gone > 0 and hand > gone, "the figure turns away before Kerrid's hand comes in")
	for i in range(first, gone):
		var e: Array = played[i]
		if e[0] == &"line":
			assert_ne(speakers.get(e[1], &""), &"rhen", "Rhen freezes without a word")


func _play_set_piece(r: BattleRequest, want: StringName) -> void:
	var ctl := _battle(r)
	for _i in MAX_TURNS:
		var e := ctl.engine
		if ctl.state == BattleController.STATE_RESULT or e.outcome != &"":
			break
		for c in e.party_active + e.party_reserve:
			if c.hp > 0:
				c.hp = c.max_hp  # the test holds the line; the controller never writes combatant state
		var actor := e.current
		if not e.is_party_turn():
			fail("the controller left a foe's turn open")
			break
		if actor.id == &"toma":
			assert_true(ctl.act(&"hold_the_stair", [actor.id] as Array[StringName]).ok, "Toma holds the stair")
			continue
		var reach := _phased_foe(e)
		if reach != null:
			reach.hp = mini(reach.hp, ceili(float(reach.max_hp) * REACH_NEAR_FLOOR_PCT / PCT))
			assert_true(ctl.act(&"attack", [reach.id] as Array[StringName]).ok)
			continue
		assert_true(ctl.act(&"stand_fast", [actor.id] as Array[StringName]).ok)
	assert_eq(ctl.engine.outcome, want, "%s ends in %s" % [r.encounter, want])
	ctl.hud.result.accept()
	_host().remove_child(ctl)
	ctl.free()


## The Reach while it can still be struck (before the Breach), else null.
func _phased_foe(e: BattleEngine) -> BattleCombatant:
	for f in e.enemies:
		if f.hp > 0 and not f.untargetable and BattleEngine.enemy_id(f) == &"undertows_reach":
			return f
	return null


func _battle(r: BattleRequest) -> FieldBattle:
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
	return ctl


## The last hand-off is a battle on `encounter` that returns to `spawn` and sets `flag`: closes the
## zone and sets the flag, as the battle's Return would. Returns the request.
func _expect_battle(encounter: StringName, spawn: StringName, flag: StringName) -> BattleRequest:
	assert_true(not hand_offs.is_empty() and hand_offs.back()[0] == ZoneStory.KIND_BATTLE, "a fight: %s" % encounter)
	if hand_offs.is_empty() or hand_offs.back()[0] != ZoneStory.KIND_BATTLE:
		return BattleRequest.new()
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, encounter)
	assert_eq(r.return_spawn, spawn)
	assert_eq(r.victory_flag, flag)
	_close()
	Game.set_flag(flag)
	return r


func _flue(coil: Ch08CoilspireZone, key: StringName) -> bool:
	return _trigger(StringName("key_" + String(key))).try_interact() and coil.last_outcome != CoilspireTrial.OUT_NONE


func _check_staging() -> void:
	for w in warnings:
		for needle in STAGING_WARNINGS:
			assert_false(w.contains(needle), "staged on this zone: %s" % w)


func _index_of_cue(cue: StringName, first_arg: String) -> int:
	for i in played.size():
		if played[i][0] == cue and (played[i][1] as Array).size() > 0 and str(played[i][1][0]) == first_arg:
			return i
	return -1


func _index_of_line(lid: StringName) -> int:
	for i in played.size():
		if played[i][0] == &"line" and played[i][1] == lid:
			return i
	return -1


func _dlg_files() -> Array[String]:
	var out: Array[String] = []
	var d := DirAccess.open(DIALOGUE_DIR)
	assert_true(d != null, "the Ch8 scripts")
	if d == null:
		return out
	for f in d.get_files():
		if f.ends_with(".dlg"):
			out.append(DIALOGUE_DIR.path_join(f))
	return out


func _open(path: String) -> void:
	zone = (load(path) as PackedScene).instantiate() as Ch08Zone
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
			played.append([&"line", s.line_id])
	)
	story.sequencer.cue_played.connect(
		func(cue: StringName, a: Array, kw: Dictionary) -> void: played.append([cue, a, kw])
	)
	story.hand_off = func(kind: StringName, target: Variant) -> void: hand_offs.append([kind, target])


func _reopen(path: String, spawn: StringName) -> void:
	_close()
	_open(path)
	assert_true(zone.place_at(spawn, zone.spawn_yaw_deg(spawn)))
	story.begin()


func _close() -> void:
	if zone != null and is_instance_valid(zone):
		warnings.append_array(story.sequencer.warnings)
		_host().remove_child(zone)
		zone.free()
	zone = null


func _trigger(id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	fail("no trigger %s" % id)
	return Interactable.new()


func _at(spawn: StringName) -> bool:
	return zone.player.position.distance_to(zone.spawn_marker(spawn).position) < 0.01


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
