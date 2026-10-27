extends TestCase
## M3-C07-02: Ch7 "The Tidecup" end to end, headless, on the real chapter data
## (game/data/flow/chapters/ch07.json) and the two greybox zones: the port's own entry (Ch6 isn't
## built) → B01 (the chapter becomes 7) → the B02 barks → B03 Tavi ("She couldn't swim, Tavi.";
## Pio's band) → the Bell's galleries (B04, Liss's line unanswered; the checkpoint autosave) → the
## naming at the rim (B05), which hands off to the Reefball match through `start_reefball
## tidecup_opening` → the STAND-IN match (ch07_tidecup_played, no win) and its return to CatchPool →
## B07 (Tavi withdraws) → the moorings side scene (B09) → the port's afternoon barks (B08) → B10 →
## Ch8's ch08/corrow at Mole (M3-C08-02). Instant sequencers; every hand-off is recorded
## through ZoneStory.hand_off. Also: B07 is identical win or lose, and no story script reads the
## match's win flag.

const PORT := "res://game/levels/ch07/tamsule/tamsule.tscn"
const BELL := "res://game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn"
const CH08_ENTRY := {"location": "ch08/corrow", "spawn": "Mole"}
const PORT_ID := &"ch07/tamsule"
const BELL_ID := &"ch07/tamsule_bell_galleries"
const SAVE_DIR := "user://test_ch07_thread_saves"
const DIALOGUE_DIR := "res://game/data/dialogue"
const CHAPTERS := "res://game/data/flow/chapters.json"
const WON := "ch07_tidecup_won"
const MATCH_ID := "tidecup_opening"
## Scripts that may read the win flag: only where the match's reward is given (act1_ch07.md §3,
## §5.4). The reward is the Reefball match's own, so no .dlg gives it yet. Dialogue paths, relative
## to DIALOGUE_DIR.
const REWARD_SCRIPTS: Array[String] = []
## The tests' own fixtures may name any flag.
const FIXTURE_DIR := "test"
## Staging problems a scene must never have on its own stage (music and sounds are Audio's, still to
## come).
const STAGING_WARNINGS: Array[String] = ["no shot", "no mark", "no actor", "cannot place", "no look_at"]

var saved_state: GameStateData
var saved_dir := ""
var zone: Ch07Zone
var story: ZoneStory
var hand_offs: Array[Array] = []
var lines: Array[StringName] = []
var restore_at_line: Dictionary = {}
var warnings: Array[String] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	saved_dir = SaveSystem.save_dir
	SaveSystem.save_dir = SAVE_DIR
	hand_offs.clear()
	lines.clear()
	restore_at_line.clear()
	warnings.clear()


func test_ch7_plays_from_the_port_to_corrow() -> void:
	var reg := LocationRegistry.load_default()
	assert_true(reg.is_playable(PORT_ID), "the port is reachable from its own location (Ch6 isn't built)")
	assert_eq(reg.spawn_of(PORT_ID), &"RiverMouth", "where Ch6 will hand off")
	_port_morning()
	_galleries()
	_naming_and_match()
	_after_the_bell()
	_moorings()
	_afternoon_and_leaving()
	_check_staging()
	_done()


func test_after_the_bell_is_the_same_win_or_lose() -> void:
	var played: Array[Array] = []
	for won: bool in [false, true]:
		Game.state = GameStateData.new()
		for f: StringName in [&"ch07_arrived", &"ch07_met_tavi", &"ch07_saw_galleries", &"ch07_tidecup_played"]:
			Game.set_flag(f)
		if won:
			Game.set_flag(StringName(WON))
		lines.clear()
		_open(BELL)
		story.begin()
		assert_true(bool(Game.get_flag(&"ch07_tavi_withdrew")), "Tavi withdraws (won: %s)" % won)
		assert_true(_at(&"CatchPool"))
		played.append(lines.duplicate())
		_close()
	assert_true(&"ch07_after_003" in played[0], "'Win or lose, she'd have yelled at us the same.'")
	assert_eq(played[1], played[0], "B07 plays line for line the same after a win")
	_done()


func test_no_story_script_reads_the_win_flag() -> void:
	var readers: Array[String] = []
	for path in _dlg_files(DIALOGUE_DIR):
		var rel := path.trim_prefix(DIALOGUE_DIR + "/")
		if rel.begins_with(FIXTURE_DIR + "/") or rel in REWARD_SCRIPTS:
			continue
		if FileAccess.get_file_as_string(path).contains(WON):
			readers.append(rel)
	assert_eq(readers, [] as Array[String], "no story .dlg reads %s (a reward only)" % WON)
	# Nor does any chapter flow branch on it.
	var chapters: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CHAPTERS))
	for f: Variant in (chapters.get("chapters", {}) as Dictionary).get("files", []):
		var text := FileAccess.get_file_as_string(str(f))
		var doc: Dictionary = JSON.parse_string(text)
		doc.erase("doc")
		assert_false(JSON.stringify(doc).contains(WON), "%s never reads %s" % [f, WON])
	_done()


func test_ch5_choices_pay_off_with_tavi_and_at_the_moorings() -> void:
	for f: StringName in [&"ch07_arrived", &"ch05_boat_for_kell", &"ch05_kept_leaf_boat"]:
		Game.set_flag(f)
	_open(PORT)
	story.sequencer.auto_choice = 1  # "I'm sorry."
	assert_true(_trigger(&"tavi").on_touched())
	assert_true(&"ch07_tavi_011" in lines, "'Don't. Not you.'")
	assert_true(&"ch07_tavi_012" in lines, "the boat Rhen sent Kell at Pemakar")
	assert_true(bool(Game.get_flag(&"ch07_told_tavi")), "either branch tells him")
	_close()
	for f: StringName in [&"ch07_saw_galleries", &"ch07_tidecup_played", &"ch07_tavi_withdrew"]:
		Game.set_flag(f)
	_open(BELL)
	story.begin()
	assert_true(_trigger(&"moorings").try_interact())
	assert_true(bool(Game.get_flag(&"ch07_set_leaf_boat")), "the kept leaf-boat goes on the water")
	assert_true(bool(Game.get_flag(&"ch07_blessed_moorings")))
	_close()
	_done()


func test_a_reload_after_the_galleries_waits_at_the_pool_steps() -> void:
	for f: StringName in [&"ch07_arrived", &"ch07_met_tavi", &"ch07_saw_galleries"]:
		Game.set_flag(f)
	_open(BELL)
	assert_true(zone.place_at(&"PoolSteps", zone.spawn_yaw_deg(&"PoolSteps")))
	story.begin()
	assert_eq(lines.size(), 0, "the galleries scene isn't replayed")
	assert_true(_trigger(&"rim").is_available(), "the naming waits at the rim")
	assert_false(_trigger(&"to_port").is_available(), "and the Bell can't be left before the match")
	_close()
	_done()


func _port_morning() -> void:
	_open(PORT)
	story.begin()
	assert_eq(Game.state.chapter, 7, "B01 moves the story to chapter 7")
	assert_true(bool(Game.get_flag(&"ch07_arrived")))
	assert_eq(Game.state.party_ids, [&"rhen", &"asha", &"toma"] as Array[StringName])
	assert_eq(Game.state.reserve_ids, [&"ysolde"] as Array[StringName])
	assert_true(&"ch07_into_003" in lines, "'...Oruvel always came up for this.'")
	assert_true(_at(&"RiverMouth"))
	SaveSystem.cancel_pending_autosave()

	for id: StringName in [&"npc_market", &"npc_board", &"npc_child", &"npc_lane", &"npc_elder", &"npc_gantry"]:
		var before := lines.size()
		assert_true(_trigger(id).try_interact(), "%s answers" % id)
		assert_true(lines.size() > before, "%s spoke" % id)
	assert_true(_trigger(&"npc_ysolde").try_interact())
	assert_true(&"ch07_bark_ysolde_002" in lines, "'It is very short.'")
	assert_false(_trigger(&"to_bell").is_available(), "the Bell waits for Tavi")
	assert_false(_trigger(&"harbour").is_available(), "and the harbour for the match")

	assert_true(_trigger(&"tavi").on_touched())
	assert_true(&"ch07_tavi_006" in lines, "'She couldn't swim, Tavi.'")
	assert_true(&"ch07_tavi_009" in lines, "'I was there.' (the first option): 'She was handing out wicks.'")
	assert_false(&"ch07_tavi_012" in lines, "no Pemakar boat line without the Ch5 choice")
	assert_true(&"ch07_tavi_015" in lines, "'Give me his band.'")
	assert_true(bool(Game.get_flag(&"ch07_told_tavi")))
	assert_true(bool(Game.get_flag(&"ch07_met_tavi")))
	assert_eq(_count(&"pio_side_band"), 1, "Pio's side-band, a key item")
	assert_false(_trigger(&"tavi").is_available(), "B03 plays once")

	assert_true(_trigger(&"to_bell").on_touched())
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": String(BELL_ID), "spawn": "Entrance"}])


func _galleries() -> void:
	_reopen(BELL, &"Entrance")
	assert_true(bool(Game.get_flag(&"ch07_saw_galleries")), "B04")
	assert_true(&"ch07_gall_003" in lines, "Toma's seat")
	assert_eq(lines.back(), &"ch07_gall_004", "Liss's line is the scene's last: nobody answers it")
	assert_true(_at(&"PoolSteps"), "Rhen goes down to the pool")
	assert_eq(Game.state.respawn_location_id, BELL_ID, "the checkpoint before the naming")
	assert_eq(Game.state.respawn_spawn, &"PoolSteps")
	assert_true(SaveSystem.has_pending_autosave(), "an autosave is asked for")
	SaveSystem.cancel_pending_autosave()
	assert_false(bool(Game.get_flag(&"ch07_tidecup_played")), "the match waits for the naming")
	assert_false(_trigger(&"to_port").is_available())


func _naming_and_match() -> void:
	var before := lines.size()
	assert_true(_trigger(&"rim").on_touched())
	var naming := lines.slice(before)
	assert_eq(
		naming,
		[&"ch07_naming_001", &"ch07_naming_002", &"ch07_naming_003", &"ch07_naming_004"] as Array[StringName],
		"two captains, two names, one word"
	)
	var ev: Dictionary = story.sequencer.events.back() if not story.sequencer.events.is_empty() else {}
	assert_eq(str(ev.get("name", "")), "start_reefball", "B05 ends on the hand-off to the Reefball match")
	var args: Array = ev.get("args", [])
	assert_eq(str(args[0]) if args.size() == 1 else "", MATCH_ID, "the Reefball agent's story match")
	# The stand-in match: played, never won, and back to the pool the way the match returns.
	assert_true(bool(Game.get_flag(&"ch07_tidecup_played")), "the stand-in sets ch07_tidecup_played")
	assert_false(bool(Game.get_flag(StringName(WON))), "and reports no win")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": String(BELL_ID), "spawn": "CatchPool"}])
	assert_false(_trigger(&"rim").is_available(), "the naming plays once")


func _after_the_bell() -> void:
	_reopen(BELL, &"CatchPool")
	assert_true(&"ch07_after_001" in lines, "'Oruvel withdraws.'")
	assert_true(&"ch07_after_006" in lines, "'I'll hang a lamp.'")
	assert_true(bool(Game.get_flag(&"ch07_tavi_withdrew")), "B07")
	assert_eq(_count(&"pio_side_band"), 1, "Rhen keeps the band till he wants it back")
	assert_true(_trigger(&"to_port").is_available(), "the Bell can be left")


func _moorings() -> void:
	assert_true(_trigger(&"moorings").try_interact())
	assert_true(&"ch07_moor_017" in lines, "Rhen names Pio")
	assert_true(&"ch07_moor_020" in lines, "'Salt and stone keep you. Come up when you can.'")
	assert_true(bool(Game.get_flag(&"ch07_blessed_moorings")))
	assert_false(bool(Game.get_flag(&"ch07_set_leaf_boat")), "no leaf-boat without the Ch5 choice")
	assert_eq(_count(&"pio_side_band"), 0, "the band is tied to the Gull's ring")
	assert_false(_trigger(&"moorings").is_available(), "the side scene plays once")
	assert_true(_trigger(&"to_port").on_touched())
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": String(PORT_ID), "spawn": "FromBell"}])
	# Back at the Bell later, Tavi has gone.
	_reopen(BELL, &"Entrance")
	assert_false(zone.block_shown("tavi"), "Tavi's boat has gone down the river")


func _afternoon_and_leaving() -> void:
	_reopen(PORT, &"FromBell")
	assert_eq(lines.size(), 0, "no arrival scene on the way back")
	for pair: Array in [[&"npc_market", &"ch07_bark_market_after_001"], [&"npc_lane", &"ch07_bark_lane_after_002"]]:
		assert_true(_trigger(pair[0]).try_interact())
		assert_true(pair[1] in lines, "B08: %s" % pair[1])
	assert_true(_trigger(&"harbour").on_touched())
	assert_true(&"ch07_leave_001" in lines, "'That'll be Tamsule's cup, then.'")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, CH08_ENTRY], "on to Ch8 at Corrow's mole")
	assert_false(restore_at_line.get(&"ch07_leave_001", true), "it hands off on black")
	var cup := 0
	for id in lines:
		if id == &"ch07_leave_001":
			cup += 1
	assert_eq(cup, 1, "the cup's winner is mentioned once")


func _dlg_files(dir: String) -> Array[String]:
	var out: Array[String] = []
	var d := DirAccess.open(dir)
	if d == null:
		return out
	for f in d.get_files():
		if f.ends_with(".dlg"):
			out.append(dir.path_join(f))
	for sub in d.get_directories():
		out.append_array(_dlg_files(dir.path_join(sub)))
	return out


func _open(path: String) -> void:
	zone = (load(path) as PackedScene).instantiate() as Ch07Zone
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
	lines.clear()
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
	SaveSystem.cancel_pending_autosave()
	var dir := DirAccess.open(SAVE_DIR)
	if dir != null:
		for f in dir.get_files():
			DirAccess.remove_absolute(SAVE_DIR.path_join(f))
		DirAccess.remove_absolute(SAVE_DIR)
	SaveSystem.save_dir = saved_dir
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
