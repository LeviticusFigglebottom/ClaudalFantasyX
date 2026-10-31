extends TestCase
## M3-MNU-02 (SPEC §6.11): MemoryReplay plays a remembered scene on its stage with no side effect
## (no <<event>> emitted, Game.state and its flags as they were, no autosave) and goes back to the
## title, which opens the gallery on that memory. Instant sequencer, synchronous stage load; the
## change back to the title is recorded (FlowRouting.record).

const RHEN_BY_ASHA := Vector3(19.2, 1.4, 42.3)  # first_playable.json night marks (B11)
const SCENE := "res://game/ui/menus/memories/memory_replay.tscn"

var replay: MemoryReplay
var changes: Array[Array] = []
var lines: Array[StringName] = []
var emitted: Array[StringName] = []
var at_first_line: Dictionary = {}
var _saved_state: GameStateData
var _saved_dir := ""


func before_each() -> void:
	InputDriver.clear_screen()
	_saved_state = Game.state
	_saved_dir = SaveSystem.save_dir
	SaveSystem.save_dir = "user://test_memory_replay"
	changes.clear()
	lines.clear()
	emitted.clear()
	at_first_line = {}
	FlowRouting.record = func(args: Array) -> void: changes.append(args)
	# An earlier test in the suite may leave its own autosave request waiting (the runner ends no
	# frame between tests). Each test here starts with none, so it measures the replay alone.
	SaveSystem.cancel_pending_autosave()


func _done() -> void:
	if is_instance_valid(replay):
		if replay.get_parent() != null:
			replay.get_parent().remove_child(replay)
		replay.free()
	FlowRouting.record = Callable()
	MemoryReplay.take_gallery_request()
	Game.state = _saved_state
	SaveSystem.save_dir = _saved_dir
	(Engine.get_main_loop() as SceneTree).paused = false


## The live record: `flags` set, plus a marker the replay must leave alone.
func _live(flags: Array[StringName]) -> GameStateData:
	var s := GameStateData.new()
	for f in flags:
		s.flags[String(f)] = true
	s.chapter = 3
	Game.state = s
	return s


func _replay(id: StringName) -> MemoryReplay:
	replay = (load(SCENE) as PackedScene).instantiate() as MemoryReplay
	replay.autostart = false
	replay.threaded = false
	replay.memory_id = id
	var records: Array[GameStateData] = [Game.state]
	replay.model = MemoriesModel.new(MemoriesModel.load_data(), records)
	ParityHost.scene_root().add_child(replay)
	replay.sequencer.instant = true
	replay.sequencer.line_shown.connect(_on_line)
	replay.sequencer.event_requested.connect(func(n: StringName, _a: Array) -> void: emitted.append(n))
	return replay


func _on_line(step: DialogueStep) -> void:
	lines.append(step.speaker)
	if at_first_line.is_empty() and replay.zone != null:
		at_first_line = {"zone": replay.zone, "flags": Game.state.flags.duplicate(), "state": Game.state}
		at_first_line["save_asked"] = SaveSystem.has_pending_autosave()
		if replay.zone is HalunaZone:
			var z := replay.zone as HalunaZone
			at_first_line["night"] = z.is_night
			at_first_line["asha"] = z.stage.actor(&"asha").global_position
			# M2-FP-115: Rhen walks out to Asha at the dock end before the first line
			at_first_line["rhen"] = z.player.global_position.distance_to(RHEN_BY_ASHA)
		at_first_line["stories"] = replay.zone.find_children("*", "FieldEncounters", true, false).size()
		at_first_line["hud"] = _hud_shown()


## Field HUD pieces (FieldHud.attach) anywhere under the replay host, and visible Controls on any
## CanvasLayer under the stage (the cutscene's own overlay lives under the sequencer, not the stage).
func _hud_shown() -> Array[String]:
	var out: Array[String] = []
	for n in replay.find_children("*", "", true, false):
		if n is ObjectiveHud or n is InteractPrompt or n is AreaTitleCard or n is TipCard or n is CodexNotice:
			out.append(str(n.name))
	for layer in replay.zone.find_children("*", "CanvasLayer", true, false):
		for c in layer.find_children("*", "Control", true, false):
			if (c as Control).is_visible_in_tree():
				out.append(str(c.get_path()))
	return out


func test_the_first_verse_replays_without_its_battle_and_returns_to_the_title() -> void:
	var live := _live([&"ch03_first_verse_sung", &"ch02_rhen_stayed_with_dead"])
	var before := live.to_dict()
	assert_false(SaveSystem.has_pending_autosave(), "no save is waiting before the replay")
	_replay(&"ch03_the_first_verse")
	replay.run()
	assert_true(replay.played, "it played to its end")
	assert_true(lines.size() > 5, "its lines were spoken")
	assert_eq(emitted, [] as Array[StringName], "no event left the replay")
	var names: Array[StringName] = []
	for e: Dictionary in replay.sequencer.events:
		names.append(StringName(str(e["name"])))
	assert_true(&"start_battle" in names, "the Drownbell was asked for, and only recorded")
	assert_true(Game.state == live, "the real record is back")
	assert_eq(Game.state.to_dict(), before, "and nothing in it changed (the scene's <<set>>s stayed inside)")
	assert_true(at_first_line.get("state") != live, "it played on a copy")
	assert_true(replay.zone == null and not is_instance_valid(at_first_line.get("zone")), "the stage is gone")
	assert_eq(changes, [[MemoryReplay.TITLE_SCENE]] as Array[Array], "back to the title")
	assert_true(replay.is_ended())
	assert_eq(SaveSystem.autosave_holders().has(replay), false, "the autosave is let go")
	assert_false(bool(at_first_line.get("save_asked", true)), "the stage and the replay asked for no save")
	assert_false(SaveSystem.has_pending_autosave(), "and nothing is waiting to be written")
	assert_eq(MemoryReplay.last_memory, &"ch03_the_first_verse")
	assert_true(MemoryReplay.take_gallery_request(), "the title opens the gallery")
	assert_false(MemoryReplay.take_gallery_request(), "once")
	_done()


## M5-A3P-1710: each memory of the rest of Act I and all of Act II (Ch4 to Ch16) plays to its end on its stage, with lines,
## no event and no change to the record, and goes back to the title.
func test_acts_one_and_two_replay_cleanly() -> void:
	var m := MemoriesModel.new(MemoriesModel.load_data())
	var checked := 0
	for row in m.memories:
		var chapter := str(row["chapter"])
		if chapter < "ch04" or chapter > "ch16":
			continue
		var id := StringName(str(row["id"]))
		var live := _live([StringName(str(row["unlock_flag"]))])
		var before := live.to_dict()
		changes.clear()
		lines.clear()
		emitted.clear()
		at_first_line = {}
		_replay(id)
		replay.run()
		assert_true(replay.played, "%s played to its end" % id)
		var compiled := FileAccess.get_file_as_string("res://game/data/dialogue/compiled/%s.json" % row["scene"])
		if compiled.contains('"op": "line"'):  # some have none (Ch15's current-song is sung and staged only)
			assert_true(lines.size() > 0, "%s: its lines were spoken" % id)
		assert_eq(emitted, [] as Array[StringName], "%s: no event left the replay" % id)
		assert_eq(Game.state.to_dict(), before, "%s: the record is as it was" % id)
		assert_eq(changes, [[MemoryReplay.TITLE_SCENE]] as Array[Array], "%s: back to the title" % id)
		if replay.get_parent() != null:
			replay.get_parent().remove_child(replay)
		replay.free()
		MemoryReplay.take_gallery_request()
		checked += 1
	assert_eq(checked, 22, "the ten Ch4-Ch9 memories and the twelve of Act II")
	_done()


func test_the_dock_at_night_replays_at_night_on_the_dock() -> void:
	var live := _live([&"ch03_rhen_sworn_guardian", &"ch03_drownbell_defeated"])
	var before := live.to_dict()
	_replay(&"ch03_dock_at_night")
	replay.run()
	assert_true(replay.played)
	assert_true(bool(at_first_line.get("night", false)), "Haluna's night (the memory's night field)")
	assert_true((at_first_line.get("asha", Vector3.ZERO) as Vector3).distance_to(Vector3(20.6, 1.4, 41.3)) < 0.1)
	assert_true(float(at_first_line.get("rhen", 99.0)) < 0.5, "Rhen on the dock, beside Asha")
	assert_eq(at_first_line.get("stories"), 0, "no field encounters on the stage")
	assert_true(replay.hud_freed >= 5, "Rhen's field HUD was there (%d pieces) and is gone" % replay.hud_freed)
	assert_eq(at_first_line.get("hud"), [] as Array[String], "no HUD element over the memory")
	assert_true(&"asha" in lines and &"toma" in lines)
	assert_eq(Game.state.to_dict(), before)
	assert_eq(changes, [[MemoryReplay.TITLE_SCENE]] as Array[Array])
	_done()


func test_replay_flags_play_a_scene_as_first_seen() -> void:
	var live := _live([&"ch02_heard_pila", &"ch02_met_asha"])
	_replay(&"ch02_pila_granddaughter")
	replay.run()
	assert_true(replay.played)
	assert_true(lines.size() > 3, "the whole scene, not the second visit's one line")
	assert_eq(at_first_line.get("hud"), [] as Array[String], "no HUD element over the memory")
	assert_false(bool((at_first_line.get("flags", {}) as Dictionary).get("ch02_heard_pila", true)))
	assert_true(bool(Game.get_flag(&"ch02_heard_pila")), "the real record still remembers it")
	assert_true(Game.state == live)
	_done()


func test_a_locked_memory_goes_straight_back() -> void:
	_live([])
	_replay(&"ch03_dock_at_night")
	replay.run()
	assert_false(replay.played)
	assert_eq(lines, [] as Array[StringName])
	assert_eq(changes, [[MemoryReplay.TITLE_SCENE]] as Array[Array], "the title again")
	_done()


func test_end_cuts_a_replay_short() -> void:
	var live := _live([&"prologue_seen"])
	_replay(&"prologue_dead_city")
	replay.sequencer.instant = false
	replay.run()
	assert_true(replay.sequencer.is_playing(), "the prologue is under way")
	assert_true(Game.state != live, "on its copy")
	replay.end()
	assert_true(replay.is_ended())
	assert_true(Game.state == live, "the real record is back")
	assert_eq(changes, [[MemoryReplay.TITLE_SCENE]] as Array[Array])
	_done()


func test_the_title_opens_the_gallery_on_the_memory_after_a_replay() -> void:
	_live([&"prologue_seen"])
	_replay(&"prologue_dead_city")
	replay.run()
	assert_true(replay.played)
	var title := TitleMenu.new()
	title.save_system = SaveSystem
	ParityHost.scene_root().add_child(title)
	assert_true(title.is_memories_open(), "the gallery is open again")
	assert_eq(title.memories_menu.current_memory(), &"prologue_dead_city", "on the memory just replayed")
	assert_eq(title.model.current(), TitleMenuModel.CHOICE_MEMORIES)
	title.get_parent().remove_child(title)
	title.free()
	_done()
