extends TestCase
## M5-A3P-1203 / 1701: the Ending's last stops. From ending_landed, Haluna plays E5 (the dark sea) at the dock at night
## and opens the credits; the credits' beach-rite vignette plays the rite on Haluna's beach; after the roll the game
## travels to Oruvel, whose arrival plays E7 (the first lamp) and opens the title.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const CREDITS := "res://game/data/ui/credits.json"
const CH01 := "res://game/data/flow/chapters/ch01.json"
const RITE := "res://game/flow/ending_beach_rite.tscn"
const POST := "res://game/flow/post_credits.tscn"
const ROLL := "res://game/ui/credits/credits_roll.tscn"

var zone: HalunaZone
var story: HalunaStory
var saved_state: GameStateData
var hand_offs: Array = []
var shots: Array[StringName] = []


func test_haluna_plays_the_dark_sea_then_opens_the_credits() -> void:
	_arrive([&"ch02_met_asha", &"ch03_rhen_sworn_guardian", &"ch18_world_open", &"ending_landed"])
	await story.begin()
	assert_true(&"E11" in shots, "E5 on its one locked shot")
	assert_true(zone.is_night, "the dock at night")
	assert_true(absf(float(zone.mood.get(&"night_sea_glow"))) < 0.0001, "the sea completely dark")
	assert_true(bool(Game.get_flag(&"ending_dark_sea_seen")), "done once")
	assert_false(bool(Game.get_flag(&"credits_seen")), "the roll sets credits_seen at its end, not E5")
	assert_eq(hand_offs, [[&"cutscene", ROLL]], "then the credits")
	_done()


func test_after_the_credits_haluna_is_haluna_again() -> void:
	_arrive([&"ch02_met_asha", &"ending_landed", &"ending_dark_sea_seen"])
	await story.begin()
	assert_true(hand_offs.is_empty(), "the ending plays once")
	_done()


func test_the_credits_are_hooked_to_the_rite_and_the_first_lamp() -> void:
	var c: Dictionary = (JSON.parse_string(FileAccess.get_file_as_string(CREDITS)) as Dictionary)["credits"]
	assert_eq(str((c["vignettes"] as Array)[0]["scene"]), RITE, "the beach rite is the vignette")
	assert_eq(str(c["next_scene"]), POST, "the roll hands on to the post-credits route")
	assert_true(ResourceLoader.exists(RITE) and ResourceLoader.exists(POST))
	var post := (load(POST) as PackedScene).instantiate() as PostCredits
	assert_eq([post.location, post.spawn], [&"ch01/oruvel", &"KellRun"], "to Oruvel")
	post.free()
	var ch01 := FileAccess.get_file_as_string(CH01)
	assert_true(ch01.contains('"play": "ending_first_lamp"'), "Oruvel's arrival plays E7")
	assert_true(ch01.contains('"set": ["credits_seen"], "unset": ["ending_first_lamp_seen"]'), "once, after the roll")


func test_the_vignette_plays_the_rite_on_the_beach() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	var rite := (load(RITE) as PackedScene).instantiate() as EndingBeachRite
	_host().add_child(rite)
	assert_true(rite.story.sequencer.is_playing(), "the rite plays")
	assert_true(rite.zone.stage.shot_node(&"E12") != null, "on E12")
	var toma := rite.zone.stage.actor(&"toma")
	assert_true(toma != null and toma.visible, "Toma on the beach")
	assert_true(hand_offs.is_empty())
	_host().remove_child(rite)
	rite.free()
	Game.state = saved_state


func _arrive(flags: Array[StringName]) -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	hand_offs.clear()
	shots.clear()
	for f in flags:
		Game.set_flag(f, true)
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	story = zone.get_node("Story") as HalunaStory
	story.autostart = false
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	story.active = true
	story.sequencer.instant = true
	story.sequencer.cue_played.connect(
		func(cue: StringName, args: Array, _kw: Dictionary) -> void:
			if cue == &"camera" and not args.is_empty():
				shots.append(StringName(str(args[0])))
	)
	story.hand_off = func(kind: StringName, target: String) -> void: hand_offs.append([kind, target])


func _done() -> void:
	if zone != null:
		_host().remove_child(zone)
		zone.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
