extends TestCase
## M2-FP-04, hardened in M2-FP-09: the whole first-playable thread, headless, with instant cutscenes
## and every scene change recorded instead of made (FlowRouting.record, BattleRequest.change_scene,
## the battle's travel hooks): New Game → prologue (which hands off to Ch1 since the M2 review switch flipped;
## Ch1 to the beach is tests/integration/test_ch01_thread.gd) → Haluna (Cutscene A) → three villagers → walk up
## the beach into the story's real tideline trigger → lose, Fight again, lose, Return to last save
## (none yet: the title) → walk in again and win → back at BattleReturn (not re-triggered) → save at
## the shrine, load it back → the causeway head → the Saltgrass Causeway (M2-FP-25: Ch3 starts, the
## harrier lesson) → the Shell Shrine trial (its checkpoint autosave, M2-FP-27) → Cutscene B → lose the
## Drownbell and Return to last save (back at the shrine's open door, not the trial) → win it → the
## dock at night → end card.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const PROLOGUE := "res://game/levels/prologue/prologue.tscn"
const FIRST_VERSE := "res://game/levels/ch03/first_verse/first_verse.tscn"
const SHRINE := "res://game/levels/ch03/shell_shrine/shell_shrine.tscn"
const CAUSEWAY := "res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn"
const BATTLE := "res://game/flow/field_battle.tscn"
const DT := 1.0 / 60.0
const WALK_SEC := 30.0
const MAX_TURNS := 60
const NPC_IDS: Array[StringName] = [&"npc_market", &"npc_chapel", &"npc_dock"]
const SAVE_DIR := "user://test_fp_thread_saves"
const TITLE := "res://game/core/boot.tscn"

var saved_state: GameStateData
var travels: Array[Array] = []
var lines := 0
var routed: Array[Array] = []
var battle_opens := 0
var saved_dir := ""


func before_each() -> void:
	FieldEncounters.reset()
	saved_state = Game.state
	Game.state = GameStateData.new()
	BattleRequest.clear()
	BattleRequest.change_scene = func(_p: String) -> void: battle_opens += 1
	FlowRouting.record = func(change: Array) -> void: routed.append(change)
	saved_dir = SaveSystem.save_dir
	SaveSystem.save_dir = SAVE_DIR
	_clear_saves()


func _done() -> void:
	SaveSystem.cancel_pending_autosave()
	BattleRequest.clear()
	BattleRequest.change_scene = Callable()
	FlowRouting.record = Callable()
	_clear_saves()
	SaveSystem.save_dir = saved_dir
	Game.state = saved_state


func test_the_first_playable_thread_end_to_end() -> void:
	# New Game lands on the prologue, which hands off to Ch1 (the M2 review switch flipped on 2026-10-29, ADR 0042;
	# test_ch01_thread plays Ch1 through to the beach). The slice thread picks up at Ch1's hand-off, Haluna's Beach.
	var reg := LocationRegistry.load_default()
	assert_eq(reg.new_game_location, &"prologue")
	var prologue := (load(PROLOGUE) as PackedScene).instantiate() as PrologueScene
	prologue.autoplay = false
	_host().add_child(prologue)
	prologue.sequencer = _instant_sequencer(prologue)
	prologue.travel = _record_travel
	prologue.play()
	assert_true(bool(Game.get_flag(&"prologue_seen")))
	assert_eq(travels, [[&"ch01/oruvel_underway", &"Drop"]] as Array[Array], "on to Ch1 (Act I's route)")
	prologue.free()
	var beach := reg.resolve(&"ch02/haluna", &"Beach")
	assert_eq(beach.get("scene"), ZONE, "the registry enters the playable zone")

	# Cutscene A on arrival, then free play.
	var zone := _load_zone()
	var story := zone.get_node("Story") as HalunaStory
	story.begin()
	assert_true(bool(Game.get_flag(&"ch02_met_asha")), "Cutscene A played")
	assert_true(zone.player.accepts_input, "Rhen is free to walk")
	assert_false(story.busy)

	# Three villagers, each a bark scene.
	for id in NPC_IDS:
		var npc := _interactable(zone, id)
		var before := lines
		assert_true(npc.try_interact(), "%s answers" % id)
		assert_true(lines > before, "%s spoke" % id)
		assert_false(story.busy, "%s's bark finished" % id)

	# Walking up the beach toward the village crosses the story's real tideline trigger.
	_walk_into_battle(zone)
	_free(zone)

	# Lose: Fight again starts it over; lose again: Return to last save (none yet) opens the title.
	var lost := _lose_battle()
	assert_eq(lost, [TITLE] as Array[String], "no save yet: Return to last save is the title")
	assert_false(bool(Game.get_flag(&"ch02_tideline_won")), "a defeat never sets the flag")
	assert_eq(travels, [[&"ch02/haluna", &"Beach"]] as Array[Array], "and never travels to the field")

	# Continue would find nothing; New Game's way back is the prologue, so walk in again and win.
	assert_eq(TitleSaveEntry.continue_slot(SaveSystem), -1, "no record to continue")
	zone = _load_zone()
	_walk_into_battle(zone)
	_free(zone)
	_win_battle(&"ch02_tideline")
	assert_true(bool(Game.get_flag(&"ch02_tideline_won")))
	assert_eq(travels.back(), [&"ch02/haluna", &"BattleReturn"])

	# Back in the zone: the cast is gone, the battle does not fire again, the causeway waits for a save.
	zone = _load_zone()
	zone.place_at(&"BattleReturn", zone.spawn_yaw_deg(&"BattleReturn"))
	_walk(zone, Vector3(1, 0, 0), 2.0, func() -> bool: return false)
	assert_eq(battle_opens, 2, "a won battle never starts again")
	var causeway := _interactable(zone, &"causeway_head")
	assert_false(causeway.is_available(), "the causeway head waits for the first save")
	var shrine := zone.find_child("SaveShrine", true, false) as SaveShrine
	assert_true(shrine != null and shrine.sets_flag == &"ch02_saved_once", "Haluna's shrine records the save")
	# The shrine's rest without its menu (the menu is covered by test_save_shrine.gd): flag, place,
	# respawn, then the write the menu makes.
	Game.set_flag(shrine.sets_flag)
	Game.state.location_id = shrine.location_id
	Game.state.respawn_location_id = shrine.location_id
	Game.state.respawn_spawn = &"Shrine"
	assert_eq(SaveSystem.save_to_slot(1, Game.state), OK, "saved at the shrine")
	var before_load := Game.state.to_dict()
	Game.state = GameStateData.new()
	assert_eq(SaveSystem.load_into_game(1), OK, "and loaded back")
	assert_eq(Game.state.flags, before_load["flags"], "every story flag survives the round trip")
	assert_eq(TitleSaveEntry.continue_slot(SaveSystem), 1, "Continue picks the shrine record")
	var wr := WorldReturn.new()
	assert_eq(wr.resolve(Game.state).get("spawn"), &"Shrine", "and continues at the shrine")
	wr.free()
	assert_eq(Game.state.chapter, 2, "Haluna is Chapter 2 (M2-FP-27)")
	assert_true(causeway.on_touched(), "after a save the causeway head opens")
	assert_eq(routed.back(), [&"ch03/saltgrass_causeway", &"FromHaluna"], "onto the Saltgrass Causeway (M2-FP-25)")
	_free(zone)

	# B06, the Saltgrass Causeway: arriving starts Ch3, the harrier at C07 is the first fight, and the
	# islet steps open the trial.
	var route := _load_route()
	route.story.begin()
	assert_eq(Game.state.chapter, 3, "Ch3 starts on the causeway (the chapter autosave)")
	assert_true(_interactable(route, &"harrier").on_touched())
	assert_true(BattleRequest.pending() != null and BattleRequest.pending().encounter == &"ch03_causeway_harrier")
	_free(route)
	_win_battle(&"ch03_causeway_harrier")
	assert_eq(travels.back(), [&"ch03/saltgrass_causeway", &"AfterHarrier"], "back on the causeway past C07")
	assert_true(bool(Game.get_flag(&"ch03_harrier_won")), "the flier lesson is won")
	route = _load_route()
	route.place_at(&"AfterHarrier")
	route.story.begin()
	assert_eq(route.encounters.walked(route.encounters.next_m + 0.1), &"ch03_causeway_shore", "then random fights")
	assert_true(_interactable(route, &"to_shrine").on_touched())
	assert_eq(routed.back(), [&"ch03/shell_shrine", &"Entry"], "the islet steps open the Shell Shrine trial")
	_free(route)
	Game.state.location_id = &"ch03/shell_shrine"

	# The trial: turn basins until the water reaches the inner pool, let it fill, go through the door.
	var trial_level := (load(SHRINE) as PackedScene).instantiate() as ShellShrineLevel
	trial_level.autostart = false
	trial_level.hand_off = func(target: String) -> void: routed.append([target])
	_host().add_child(trial_level)
	trial_level.set_process(false)
	trial_level.director.auto_update = false
	trial_level.player.set_physics_process(false)
	var guard := 0
	while not trial_level.trial.reaches(trial_level.trial.goal()) and guard < 16:
		guard += 1
		trial_level.trial.rotate(_next_turn(trial_level.trial))
	trial_level.advance(float(trial_level.trial.data["insert_sec"]) + float(trial_level.trial.data["fill_sec"]) + 0.1)
	assert_true(trial_level.trial.door_open, "the trial is solved")
	assert_eq(Game.state.respawn_location_id, &"ch03/shell_shrine", "the checkpoint moves the respawn (M2-FP-27)")
	assert_eq(Game.state.respawn_spawn, &"Exit")
	assert_true(SaveSystem.has_pending_autosave(), "and asks for the checkpoint autosave")
	SaveSystem.cancel_pending_autosave()
	assert_eq(SaveSystem.autosave(&"checkpoint"), OK, "written at the next safe point (here, at once)")
	assert_true(_interactable(trial_level, &"shrine_exit").on_touched())
	assert_eq(routed.back(), [FIRST_VERSE], "through the door, Cutscene B")
	_host().remove_child(trial_level)
	trial_level.free()

	# Cutscene B on its set, then the Drownbell, then the end card.
	var verse := (load(FIRST_VERSE) as PackedScene).instantiate() as FirstVerseScene
	verse.autoplay = false
	var requests: Array[BattleRequest] = []
	verse.start_battle = func(r: BattleRequest) -> void: requests.append(r)
	_host().add_child(verse)
	verse.sequencer.instant = true
	verse.run()
	assert_true(bool(Game.get_flag(&"ch03_first_verse_sung")), "the verse was sung")
	assert_true(bool(Game.get_flag(&"ch03_ilun_bound")), "Ilun answers Asha in the fight")
	verse.free()
	assert_eq(requests.size(), 1, "Cutscene B calls the Drownbell")
	# Lose it, then Return to last save: the checkpoint, at the shrine's open door, not the trial.
	BattleRequest.submit(requests[0])
	_lose_battle()
	assert_eq(travels.back(), [&"ch03/shell_shrine", &"Exit"], "Return to last save resumes past the trial")
	assert_true(bool(Game.get_flag(&"ch03_shrine_door_open")), "with the door open")
	BattleRequest.submit(requests[0])
	var opened := _win_battle(&"drownbell")
	assert_true(bool(Game.get_flag(&"ch03_drownbell_defeated")))
	assert_eq(opened, [] as Array[String], "no scene opens: the party travels")
	assert_eq(travels.back(), [&"ch02/haluna", &"DockNight"], "after the Drownbell, Haluna's dock at night (M2-FP-15)")

	# B11: the dock at night, then Ch4's chapter card (M3-CIN-1233: no demo end card mid-Act I).
	zone = _load_zone()
	zone.place_at(&"DockNight", zone.spawn_yaw_deg(&"DockNight"))
	var night_story := zone.get_node("Story") as HalunaStory
	night_story.begin()
	assert_true(zone.is_night, "Haluna at night")
	assert_true(bool(Game.get_flag(&"ch03_rhen_sworn_guardian")), "Rhen is sworn")
	assert_eq(routed.back(), [ChapterCard.SCENE], "then Ch4's chapter card")
	_free(zone)
	_done()


func test_the_battle_strip_cannot_be_walked_around() -> void:
	Game.set_flag(&"ch02_met_asha")
	var zone := _load_zone()
	for a in zone.stage.get_node(CutsceneStage.ACTORS).get_children():
		assert_false((a as Node3D).visible, "the beach cast is gone once the JSON's intro flag is set")
	var strip := _interactable(zone, &"tideline_battle")
	var shrine := zone.spawn_marker(&"Shrine").global_position
	var beach := zone.spawn_marker(&"Beach").global_position
	# Every straight line from the beach (along its whole length) to the shrine crosses the strip.
	for i in range(-10, 11):
		var from := beach + Vector3(0, 0, i * 10.0)
		var crossed := false
		for k in 101:
			if strip.contains_point(from.lerp(shrine, k / 100.0) + Vector3.UP * 0.9):
				crossed = true
				break
		assert_true(crossed, "the line from the beach at z=%.0f to the shrine crosses the strip" % from.z)
	# Walking up the beach to the causeway head and then inland: the strip or the walls stop Rhen.
	zone.place_at(&"CausewayHead", zone.spawn_yaw_deg(&"CausewayHead"))
	_walk(zone, Vector3(-1, 0, 0), WALK_SEC, func() -> bool: return battle_opens > 0)
	var p := zone.player.global_position
	assert_true(battle_opens > 0 or p.x > shrine.x * 0.5, "inland from the causeway head: fight or wall (at %s)" % p)
	_free(zone)
	_done()


## Walks west from the Beach spawn until the story opens the battle, and checks the request it made.
func _walk_into_battle(zone: HalunaZone) -> void:
	var opens := battle_opens
	zone.place_at(&"Beach", zone.spawn_yaw_deg(&"Beach"))
	_walk(zone, Vector3(-1, 0, 0), WALK_SEC, func() -> bool: return battle_opens > opens)
	assert_eq(battle_opens, opens + 1, "the beach path starts the battle")
	var r := BattleRequest.pending()
	assert_true(r != null, "the story made a real request")
	if r != null:
		assert_eq(r.encounter, &"ch02_tideline")
		assert_eq(r.return_spawn, &"BattleReturn")
		assert_eq(r.escape_spawn, &"BeforeBattle")
		assert_eq(r.victory_flag, &"ch02_tideline_won")


## Plays the pending request to a defeat, Fight again, a second defeat, then Return to last save.
## Returns the scenes that opened.
func _lose_battle() -> Array[String]:
	var opened: Array[String] = []
	var ctl := _battle(opened)
	for round_no in 2:
		for c in ctl.engine.party_active + ctl.engine.party_reserve:
			c.hp = 1  # force a quick loss; the controller never writes combatant state
		for _i in MAX_TURNS:
			if ctl.state == BattleController.STATE_RESULT:
				break
			ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
		assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_DEFEAT, "defeat %d" % (round_no + 1))
		if round_no == 0:
			assert_eq(ctl.hud.result.current_choice(), BattleController.CHOICE_RETRY)
			ctl.hud.result.accept()
			assert_eq(ctl.state, BattleController.STATE_COMMAND, "Fight again starts it over")
	ctl.hud.result.move_cursor(1)
	assert_eq(ctl.hud.result.current_choice(), FieldBattle.CHOICE_LAST_SAVE)
	ctl.hud.result.accept()
	_host().remove_child(ctl)
	ctl.free()
	return opened


func _load_route() -> GreyboxZone:
	var route := (load(CAUSEWAY) as PackedScene).instantiate() as GreyboxZone
	route.story.autostart = false
	_host().add_child(route)
	route.director.auto_update = false
	route.player.set_physics_process(false)
	route.encounters.set_physics_process(false)
	route.encounters.on_encounter = func(_id: StringName) -> void: pass
	route.story.active = true
	route.story.sequencer.instant = true
	route.story.overhear.instant = true
	return route


func _load_zone() -> HalunaZone:
	var zone := (load(ZONE) as PackedScene).instantiate() as HalunaZone
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	var story := zone.get_node("Story") as HalunaStory
	story.active = true
	story.sequencer.instant = true
	story.sequencer.line_shown.connect(func(_s: DialogueStep) -> void: lines += 1)
	return zone


## The basin whose turn brings the water closest to the inner pool (the trial's own search).
func _next_turn(trial: ShellShrineTrial) -> StringName:
	var best := &""
	var best_n := 1 << 20
	for b in trial.basin_ids():
		var probe := ShellShrineTrial.new(trial.data)
		probe.rotations = trial.rotations.duplicate()
		probe.rotate(b)
		var n := probe.min_turns_to(probe.goal())
		if n >= 0 and n < best_n:
			best_n = n
			best = b
	return best


func _instant_sequencer(host: Node) -> CutsceneSequencer:
	var seq := CutsceneSequencer.new()
	seq.instant = true
	host.add_child(seq)
	return seq


func _record_travel(loc: StringName, spawn: StringName) -> bool:
	travels.append([loc, spawn])
	return true


func _interactable(zone: Node, id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	fail("no interactable %s" % id)
	return null


## Holds the stick along `world_dir` under the live camera until `stop` or `seconds`.
func _walk(zone: HalunaZone, world_dir: Vector3, seconds: float, stop: Callable) -> void:
	var d := world_dir.normalized()
	for _i in int(seconds / DT):
		if stop.call():
			break
		var basis := Basis(Vector3.UP, zone.director.camera_yaw())
		zone.player.input_override = Vector2(d.dot(basis * Vector3.RIGHT), -d.dot(basis * Vector3.FORWARD))
		zone.player.step(DT)
		zone.director.update(DT)
	zone.player.input_override = Vector2.ZERO


## Plays the pending request to a forced win (every foe at 1 HP, attacks only) and presses Return.
## Returns the scenes Return opened (a request with return_scene) instead of travelling.
func _win_battle(encounter: StringName) -> Array[String]:
	var opened: Array[String] = []
	var ctl := _battle(opened)
	assert_eq(ctl.engine.encounter_id, encounter)
	for _i in MAX_TURNS:
		if ctl.state == BattleController.STATE_RESULT:
			break
		for foe in ctl.engine.enemies:
			foe.hp = mini(foe.hp, 1)  # force a quick win; the controller never writes combatant state
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY)
	ctl.hud.result.accept()
	_host().remove_child(ctl)
	ctl.free()
	return opened


func _battle(opened: Array[String]) -> FieldBattle:
	var ctl := (load(BATTLE) as PackedScene).instantiate() as FieldBattle
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.travel = _record_travel
	ctl.open_title = func(p: String) -> void: opened.append(p)
	ctl.save_system = SaveSystem
	_host().add_child(ctl)
	ctl.start_sandbox()
	return ctl


func _clear_saves() -> void:
	var dir := DirAccess.open(SAVE_DIR)
	if dir == null:
		return
	for f in dir.get_files():
		DirAccess.remove_absolute(SAVE_DIR.path_join(f))
	DirAccess.remove_absolute(SAVE_DIR)


func _free(zone: Node) -> void:
	_host().remove_child(zone)
	zone.free()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
