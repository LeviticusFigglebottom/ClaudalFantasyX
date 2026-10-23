extends TestCase
## M2-FP-04: the whole first-playable thread, headless, with instant cutscenes and every scene change
## recorded instead of made: New Game → prologue → Haluna (Cutscene A) → three villagers → walk up
## the beach into the tideline battle → win → back at BattleReturn (not re-triggered) → the shrine
## gate on the causeway head → Cutscene B on its set → end card.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const PROLOGUE := "res://game/levels/prologue/prologue.tscn"
const FIRST_VERSE := "res://game/levels/ch03/first_verse/first_verse.tscn"
const BATTLE := "res://game/flow/field_battle.tscn"
const DT := 1.0 / 60.0
const WALK_SEC := 30.0
const MAX_TURNS := 60
const NPC_IDS: Array[StringName] = [&"npc_market", &"npc_chapel", &"npc_dock"]

var saved_state: GameStateData
var hand_offs: Array[Array] = []
var travels: Array[Array] = []
var lines := 0


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	BattleRequest.clear()


func test_the_first_playable_thread_end_to_end() -> void:
	# New Game lands on the prologue, which hands off to the beach.
	var reg := LocationRegistry.load_default()
	assert_eq(reg.new_game_location, &"prologue")
	var prologue := (load(PROLOGUE) as PackedScene).instantiate() as PrologueScene
	prologue.autoplay = false
	_host().add_child(prologue)
	prologue.sequencer = _instant_sequencer(prologue)
	prologue.travel = _record_travel
	prologue.play()
	assert_true(bool(Game.get_flag(&"prologue_seen")))
	assert_eq(travels, [[&"ch02/haluna", &"Beach"]] as Array[Array])
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

	# Walking up the beach toward the village crosses the tideline battle trigger.
	zone.place_at(&"Beach", zone.spawn_yaw_deg(&"Beach"))
	_walk(zone, Vector3(-1, 0, 0), WALK_SEC, func() -> bool: return not hand_offs.is_empty())
	assert_eq(hand_offs, [[&"battle", "ch02_tideline"]] as Array[Array], "the beach path starts the battle")
	_free(zone)

	# The battle: win, and come back to BattleReturn with the flag set.
	BattleRequest.change_scene = func(_p: String) -> void: pass
	BattleRequest.start(&"ch02_tideline", &"ch02/haluna", &"BattleReturn", &"ch02_tideline_won")
	_win_battle()
	assert_true(bool(Game.get_flag(&"ch02_tideline_won")))
	assert_eq(travels.back(), [&"ch02/haluna", &"BattleReturn"])
	BattleRequest.change_scene = Callable()

	# Back in the zone: the cast is gone, the battle does not fire again, the causeway waits for a save.
	hand_offs.clear()
	zone = _load_zone()
	zone.place_at(&"BattleReturn", zone.spawn_yaw_deg(&"BattleReturn"))
	_walk(zone, Vector3(1, 0, 0), 2.0, func() -> bool: return false)
	assert_eq(hand_offs, [] as Array[Array], "a won battle never starts again")
	var causeway := _interactable(zone, &"causeway_head")
	assert_false(causeway.is_available(), "the causeway head waits for the first save")
	var shrine := zone.find_child("SaveShrine", true, false) as SaveShrine
	assert_true(shrine != null and shrine.sets_flag == &"ch02_saved_once", "Haluna's shrine records the save")
	Game.set_flag(&"ch02_saved_once")  # the save menu itself is covered by test_save_shrine.gd
	assert_true(causeway.on_touched(), "after a save the causeway head opens")
	assert_eq(hand_offs, [[&"cutscene", FIRST_VERSE]] as Array[Array])
	_free(zone)

	# Cutscene B on its set, then the end card.
	var verse := (load(FIRST_VERSE) as PackedScene).instantiate() as FirstVerseScene
	verse.autoplay = false
	var changes: Array[String] = []
	verse.change_scene = func(p: String) -> void: changes.append(p)
	_host().add_child(verse)
	verse.sequencer.instant = true
	verse.run()
	assert_true(bool(Game.get_flag(&"ch03_first_verse_sung")), "the verse was sung")
	assert_eq(changes, [EndCard.SCENE])
	verse.free()
	Game.state = saved_state


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
	story.hand_off = func(kind: StringName, target: String) -> void: hand_offs.append([kind, target])
	return zone


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


func _win_battle() -> void:
	var ctl := (load(BATTLE) as PackedScene).instantiate() as FieldBattle
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.travel = _record_travel
	_host().add_child(ctl)
	ctl.start_sandbox()
	assert_eq(ctl.engine.encounter_id, &"ch02_tideline")
	for foe in ctl.engine.enemies:
		foe.hp = 1  # force a quick win; the controller never writes combatant state
	for _i in MAX_TURNS:
		if ctl.state == BattleController.STATE_RESULT:
			break
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY)
	ctl.hud.result.accept()
	_host().remove_child(ctl)
	ctl.free()


func _free(zone: Node) -> void:
	_host().remove_child(zone)
	zone.free()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
