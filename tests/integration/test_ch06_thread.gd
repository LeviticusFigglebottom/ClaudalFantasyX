extends TestCase
## M3-C06-02: Ch6 "Salt Edict" end to end, headless, on the real chapter data
## (game/data/flow/chapters/ch06.json) and the greybox zone ch06/brine_shoals: Entry (Ch5's hand-off)
## → the road (the banters, the midday stop, the random fights' table) → the smoke and the raid → the
## Stillguard Inquisitor in the real field battle (Toma's blows greyed and refused; both foes yield
## on their feet) → the barge (Sefir's first appearance) → Liss joins → the lantern → the ridge camp
## at dusk (the shrine, the barks) → the burned lamp → the channel at dawn → ch07/tamsule at
## RiverMouth. Instant sequencers; every hand-off is recorded through ZoneStory.hand_off.
## The staging watches a test can see (act1_ch06.md B05, §4, §5; ADR 0017 (a)):
##   - Sefir speaks exactly the sheet's lines, with no contraction; he never moves to a mark; there is
##     no close-up before his first line, no @vfx and no sting in the scene, and his theme enters
##     only after his first line. His eyes rest on Kerrid's back half a beat, and on the crate 1.5 s.
##   - Liss says nothing in B05; "once it had finished" comes after the barge has gone.
##   - Asha has no line in B07. Nobody ever names the burned lamp.
##   - Toma's offensive commands are greyed against the Stillguard and refused by the engine.

const SHOALS := "res://game/levels/ch06/brine_shoals/brine_shoals.tscn"
const BATTLE := "res://game/flow/field_battle.tscn"
const DIALOGUE_CSV := "res://game/data/loc/dialogue.csv"
const SAVE_DIR := "user://test_ch06_thread_saves"
const MAX_TURNS := 200
const STAGING_WARNINGS: Array[String] = ["no shot", "no mark", "no actor", "cannot place", "no look_at"]
## Ch5's party as its dawn leaves it.
const ROAD_PARTY: Array[StringName] = [&"rhen", &"asha", &"kerrid"]
const ROAD_RESERVE: Array[StringName] = [&"toma", &"ysolde"]
const FIGHT_PARTY: Array[StringName] = [&"toma", &"rhen", &"asha"]
const FIGHT_RESERVE: Array[StringName] = [&"kerrid", &"ysolde"]
## B05: the sheet's Sefir lines, every one (the greeting branch; the wake branch swaps 019 for 021).
const SEFIR_LINES: Array[String] = [
	"ch06_barge_002",
	"ch06_barge_004",
	"ch06_barge_005",
	"ch06_barge_006",
	"ch06_barge_007",
	"ch06_barge_009",
	"ch06_barge_011",
	"ch06_barge_013",
	"ch06_barge_015",
	"ch06_barge_017",
	"ch06_barge_019",
	"ch06_barge_023",
	"ch06_barge_024",
]
## The only sounds B05 may play: the poles (wood, no water) and the iron's hiss.
const BARGE_SFX: Array[String] = ["barge_pole", "brine_iron_hiss"]
## The shots before Sefir's first line: wide on the impasse, and the barge from the water.
const WIDE_SHOTS: Array[String] = ["W10", "W11"]
## act1_ch06.md §4: the design truth of whose lamp it was. It is never game text.
const LAMP_NAME := "Pirran"

var saved_state: GameStateData
var saved_dir := ""
var zone: Ch06Zone
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


func test_ch6_plays_from_the_shoals_to_tamsule() -> void:
	_set_party(ROAD_PARTY, ROAD_RESERVE)
	_road()
	_fight()
	_after_the_fight()
	_camp_and_dawn()
	_check_staging()
	_check_barge()
	_done()


func test_digging_without_asking_is_remembered() -> void:
	for f: StringName in [&"ch06_arrived", &"ch06_inquisitor_yielded", &"ch06_met_sefir", &"ch06_camp_made"]:
		Game.set_flag(f)
	_open(SHOALS)
	story.sequencer.auto_choice = 1
	assert_true(_trigger(&"tideline").on_touched())
	assert_true(bool(Game.get_flag(&"ch06_dug_without_asking")), "he knelt and dug")
	assert_true(bool(Game.get_flag(&"ch06_saw_lamp_buried")))
	assert_false(&"ch06_lamp_003" in lines, "nobody asked whose it was")
	assert_false(_trigger(&"tideline").is_available(), "once")
	_done()


func test_the_lantern_answer_follows_the_beach() -> void:
	for named: bool in [true, false]:
		Game.state = GameStateData.new()
		lines.clear()
		if named:
			Game.set_flag(&"ch02_rhen_named_lantern")
		Game.set_flag(&"ch06_inquisitor_yielded")
		_open(SHOALS)
		story.begin()
		assert_eq(&"ch06_lantern_003" in lines, named, "'It was my father's.' only if he said so on the beach")
		assert_eq(&"ch06_lantern_006" in lines, not named)
		assert_true(bool(Game.get_flag(&"ch06_liss_read_lantern")))
		_close()
	_done()


func test_the_road_has_random_fights_and_the_camp_has_none() -> void:
	_open(SHOALS)
	var when: Dictionary = (zone.layout.get("encounters", {}) as Dictionary).get("when", {})
	assert_true(zone.encounters != null, "the road has random fights")
	assert_false(ZoneStory.holds(when), "not before the chapter begins")
	Game.set_flag(&"ch06_arrived")
	assert_true(ZoneStory.holds(when), "on the ridges and the flats")
	Game.set_flag(&"ch06_sheltered_liss")
	assert_false(ZoneStory.holds(when), "none from the raid on")
	_done()


func test_toma_will_not_strike_the_stillguard_on_the_real_data() -> void:
	var engine := BattleEngine.new()
	engine.setup(BattleDB.load_default(), FIGHT_PARTY, FIGHT_RESERVE, &"ch06_inquisitor", 1)
	var toma := engine.find(&"toma")
	assert_eq(toma.forbidden_tag, &"stillguard")
	for sid: StringName in [&"attack", &"shell_breaker"]:
		assert_true(BossMechanics.forbidden_now(engine, toma, engine.db.skill(sid)), "%s is greyed" % sid)
	for sid: StringName in [&"stand_fast", &"brace", &"challenge", &"shield_wall"]:
		assert_true(toma.skills.has(sid), "his guard is all there: %s" % sid)
		assert_false(BossMechanics.forbidden_now(engine, toma, engine.db.skill(sid)))
	for e in engine.enemies:
		assert_true(e.tags.has(&"stillguard"), "%s is the Order's" % e.id)
		assert_eq(e.yield_at_hp_pct, 0, "%s yields at 0 HP, never dies" % e.id)
	assert_eq(engine.find(&"rhen").forbidden_tag, &"", "only Toma")
	_done()


func _road() -> void:
	_open(SHOALS)
	story.begin()
	assert_true(bool(Game.get_flag(&"ch06_arrived")), "B01")
	assert_eq(Game.state.chapter, 6, "the chapter step")
	assert_eq(Game.state.party_ids, ROAD_PARTY, "Ch5's party is kept")
	assert_true(_at(&"Entry"))
	assert_false(zone.block_shown("Barge"), "no barge before the raid")
	assert_false(zone.block_shown("liss"), "no Liss before her run")
	assert_true(_trigger(&"banter_brass").on_touched())
	assert_true(_trigger(&"midday").on_touched())
	assert_true(&"ch06_midday_001" in lines, "Rhen takes Kerrid's share")
	assert_true(bool(Game.get_flag(&"ch06_midday_seen")))
	assert_false(_trigger(&"midday").is_available(), "once")
	assert_true(_trigger(&"banter_marks").on_touched())
	assert_true(_trigger(&"last_ridge").on_touched())
	assert_true(&"ch06_smoke_002" in lines, "B02: Toma's 'No.'")
	assert_true(&"ch06_raid_002" in lines, "B03: Asha's second 'Toma.'")
	assert_true(&"ch06_raid_012" in lines, "On my shield.")
	assert_true(bool(Game.get_flag(&"ch06_sheltered_liss")))
	assert_true(zone.block_shown("liss"))


func _fight() -> void:
	assert_true(not hand_offs.is_empty() and hand_offs.back()[0] == ZoneStory.KIND_BATTLE, "the Inquisitor")
	if hand_offs.is_empty():
		return
	var r := hand_offs.back()[1] as BattleRequest
	assert_eq(r.encounter, &"ch06_inquisitor")
	assert_eq(r.active, FIGHT_PARTY, "Toma steps in front")
	assert_eq(r.reserve, FIGHT_RESERVE)
	assert_eq(r.return_spawn, &"CampWaterline")
	assert_eq(r.victory_flag, &"ch06_inquisitor_yielded")
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
	var refused := false
	for _i in MAX_TURNS:
		if ctl.state == BattleController.STATE_RESULT or ctl.engine.outcome != &"":
			break
		for foe in ctl.engine.enemies:
			foe.hp = mini(foe.hp, 1)  # force a quick win; the controller never writes combatant state
		var actor := ctl.engine.current
		var foes := ctl.engine.living_foes_of(actor)
		if foes.is_empty():
			break
		if actor.id == &"toma":
			refused = _toma_turn(ctl) or refused
			continue
		ctl.act(&"attack", [foes[0].id] as Array[StringName])
	assert_true(refused, "Toma's turn came and his blow was refused")
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY, "the fight is won")
	for e in ctl.engine.enemies:
		assert_true(e.yielded, "%s yielded or ran" % e.id)
		assert_true(e.hp >= 1, "%s is alive: nobody dies" % e.id)
	assert_eq(BattleMenus.victory_title_key(ctl.engine), "HUD_CH06_INQUISITOR_YIELDS")
	ctl.hud.result.accept()
	_host().remove_child(ctl)
	ctl.free()
	assert_true(bool(Game.get_flag(&"ch06_inquisitor_yielded")))
	assert_eq(travels.back(), [&"ch06/brine_shoals", &"CampWaterline"], "back to the camp")


## Toma's turn in the real field battle: Attack and his blows are greyed, the engine refuses one, and
## he guards instead. Returns true when the refusal was seen.
func _toma_turn(ctl: FieldBattle) -> bool:
	var toma := ctl.engine.current
	var rows := ctl.menus.root_rows(ctl.engine, ctl.items)
	assert_false(bool(rows[0].get("enabled", true)), "Attack is greyed for Toma")
	var enabled := {}
	for row in ctl.menus.skill_rows(ctl.engine):
		enabled[row.get("id")] = bool(row.get("enabled", true))
	assert_false(bool(enabled.get(&"shell_breaker", true)), "Shell Breaker is greyed")
	assert_true(bool(enabled.get(&"challenge", false)), "Challenge is his")
	assert_eq(tr(toma.forbidden_key), tr("HUD_FAIL_CH06_TOMA_WILL_NOT_STRIKE"))
	var foe := ctl.engine.living_foes_of(toma)[0]
	var res := ctl.act(&"attack", [foe.id] as Array[StringName])
	assert_false(res.ok, "the engine refuses the blow")
	assert_eq(res.fail_reason, BossMechanics.FAIL_FORBIDDEN)
	assert_eq(ctl.engine.current, toma, "a refused blow costs no turn")
	assert_true(ctl.act(&"stand_fast", [toma.id] as Array[StringName]).ok, "he stands fast instead")
	return res.fail_reason == BossMechanics.FAIL_FORBIDDEN


func _after_the_fight() -> void:
	_open(SHOALS)
	assert_true(zone.place_at(&"CampWaterline", zone.spawn_yaw_deg(&"CampWaterline")))
	assert_true(zone.block_shown("Barge") and zone.block_shown("sefir"), "the barge is in the channel")
	story.begin()
	assert_true(bool(Game.get_flag(&"ch06_met_sefir")), "B05")
	assert_true(bool(Game.get_flag(&"ch06_rhen_greeted_sefir")), "'Be... still?' (the first option)")
	assert_true(bool(Game.get_flag(&"ch06_liss_joined")), "B06")
	assert_eq(Game.state.party_ids, ROAD_PARTY)
	assert_eq(Game.state.reserve_ids, [&"toma", &"ysolde", &"liss"] as Array[StringName], "Liss is written in")
	assert_true(bool(Game.get_flag(&"ch06_liss_read_lantern")), "B07")
	assert_true(bool(Game.get_flag(&"ch06_camp_made")))
	assert_true(_at(&"RidgeCamp"), "B08: the ridge camp")
	assert_false(zone.block_shown("Barge") or zone.block_shown("sefir"), "the barge has gone")
	assert_false(zone.block_shown("inquisitor"), "the raid's cast has gone up the road")
	assert_true(zone.sun.light_energy < float(zone.layout["sun"]["energy"]), "the dusk light, under the day's")
	assert_true(zone.sun.rotation_degrees.x > -10.0, "a low dusk sun")
	assert_true(zone.block_shown("Lamp"), "the burned lamp on the tideline")


func _camp_and_dawn() -> void:
	var rests := zone.rests
	assert_true(_trigger(&"shrine").try_interact())
	assert_eq(zone.rests, rests + 1, "the shrine rests the party")
	assert_eq(Game.state.respawn_spawn, &"RidgeCamp", "and is the checkpoint")
	for id: StringName in [&"bark_ysolde_reading", &"bark_toma_papers", &"bark_asha_day"]:
		assert_true(_trigger(id).try_interact(), "%s plays" % id)
	assert_true(&"ch06_bark_asha_001" in lines)
	assert_true(_trigger(&"tideline").on_touched())
	assert_true(bool(Game.get_flag(&"ch06_saw_lamp_buried")), "B09")
	assert_false(bool(Game.get_flag(&"ch06_dug_without_asking")), "he asked, and she said don't")
	assert_true(&"ch06_lamp_003" in lines)
	var motes := _cues(&"vfx").filter(func(c: Array) -> bool: return c[1][0] == "glimmer_held")
	assert_eq(motes.size(), 1, "one mote")
	assert_eq(str((motes[0][2] as Dictionary).get("drift", "")), "down_seaward", "and it sinks seaward")
	assert_false(zone.block_shown("Lamp"), "buried")
	assert_true(_trigger(&"channel_out").on_touched())
	assert_true(bool(Game.get_flag(&"ch06_done")), "B10")
	assert_true(&"ch06_dawn_003" in lines)
	var liss := zone.stage.actor(&"liss")
	assert_true(
		liss.global_position.distance_to(zone.player.global_position) < 4.0, "B10: Liss wades the channel with Rhen"
	)
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": "ch07/tamsule", "spawn": "RiverMouth"}], "on to Ch7")
	_close()


## B05's rules, on what the sequencer played (see the class comment).
func _check_barge() -> void:
	var start := _index_of_line(&"ch06_barge_001")
	var finish := _index_of_line(&"ch06_barge_024")
	assert_true(start >= 0 and finish > start, "the barge played")
	var scene := played.slice(start, finish + 1)
	var sefir: Array[String] = []
	for lid: StringName in speakers:
		if speakers[lid] == &"sefir":
			sefir.append(String(lid))
			assert_false(_text(lid).contains("'"), "Sefir uses no contraction: %s" % _text(lid))
			assert_false(_text(lid).contains("!"), "and never raises his voice")
	sefir.sort()
	assert_eq(sefir, SEFIR_LINES, "Sefir's lines are the sheet's")
	var first := _index_of_line(&"ch06_barge_002")
	for e in played.slice(start, first):
		if e[0] == &"camera":
			assert_true(str(e[1][0]) in WIDE_SHOTS, "no close-up before his first line: %s" % e[1][0])
		assert_false(e[0] == &"music" and str(e[1][0]) == "sefir_theme", "his theme waits for his voice")
	var theme := false
	for e in scene:
		if e[0] == &"mark":
			assert_ne(str(e[1][0]), "sefir", "he never steps onto the mud")
		if e[0] == &"vfx":
			fail("no @vfx in B05")
		if e[0] == &"sfx":
			assert_true(str(e[1][0]) in BARGE_SFX, "no sting, no water but the iron: %s" % e[1][0])
		if e[0] == &"face":
			assert_false(str(e[1][0]) in ["liss", "kerrid"] and str(e[1][1]) in ["cold", "angry"], "no glare")
		if e[0] == &"line":
			assert_ne(speakers.get(e[1], &""), &"liss", "Liss says nothing while he is there")
		theme = theme or (e[0] == &"music" and str(e[1][0]) == "sefir_theme")
	assert_true(theme, "sefir_theme enters")
	assert_true(_follows(scene, ["anim", "sefir", "look_at", "kerrid"], 0.5), "half a beat on Kerrid's back")
	assert_true(_follows(scene, ["camera", "W12_crate"], 1.5), "the crate, a moment too long")
	assert_true(_index_of_line(&"ch06_after_002") > finish, "'once it had finished' comes after he has gone")
	for lid: StringName in speakers:
		if String(lid).begins_with("ch06_lantern_"):
			assert_ne(speakers[lid], &"asha", "ADR 0022: Asha is off-frame in B07")
	for row in _ch06_rows():
		assert_false(row.contains(LAMP_NAME), "nobody names the lamp: %s" % row)


func _check_staging() -> void:
	for w in warnings:
		for needle in STAGING_WARNINGS:
			assert_false(w.contains(needle), "staged on this zone: %s" % w)


## True when the cue matching `want` (its name, then its positional args) is followed at once by a
## wait of `sec`.
func _follows(scene: Array, want: Array, sec: float) -> bool:
	for i in scene.size() - 1:
		var e: Array = scene[i]
		if e[0] != StringName(want[0]) or e.size() < 2:
			continue
		var args: Array = e[1]
		var ok := args.size() >= want.size() - 1
		for k in range(1, want.size()):
			ok = ok and k - 1 < args.size() and str(args[k - 1]) == want[k]
		var next: Array = scene[i + 1]
		if ok and next[0] == &"wait" and is_equal_approx(float(next[1][0]), sec):
			return true
	return false


func _cues(name: StringName) -> Array:
	return played.filter(func(e: Array) -> bool: return e[0] == name)


func _index_of_line(lid: StringName) -> int:
	for i in played.size():
		if played[i][0] == &"line" and played[i][1] == lid:
			return i
	return -1


func _text(lid: StringName) -> String:
	return tr("DLG_" + String(lid).to_upper())


## Every Ch6 dialogue row of dialogue.csv (key and text).
func _ch06_rows() -> Array[String]:
	var out: Array[String] = []
	for row in FileAccess.get_file_as_string(DIALOGUE_CSV).split("\n"):
		if row.begins_with("DLG_CH06_"):
			out.append(row)
	assert_true(out.size() > 50, "found Ch6's lines")
	return out


func _open(path: String) -> void:
	zone = (load(path) as PackedScene).instantiate() as Ch06Zone
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


func _close() -> void:
	if zone != null and is_instance_valid(zone):
		warnings.append_array(story.sequencer.warnings)
		_host().remove_child(zone)
		zone.free()
	zone = null


func _set_party(active: Array[StringName], reserve: Array[StringName]) -> void:
	Game.state.party_ids = active.duplicate()
	Game.state.reserve_ids = reserve.duplicate()


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
