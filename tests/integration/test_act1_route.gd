extends TestCase
## M3-CIN-1233 (the Lead, under ADR 0041/0042: Act I as played is one path): New Game → the prologue → Ch1's Underway at
## Drop; the slice's end (B11, the dock at night) → Ch4's chapter card (B12's voice-over, then "Chapter 4" and its
## name) → Ch4's wake at NemeDoor, with no demo card and no credits; and Ch9's end → the end card with the credits →
## the title. Every hand-off resolves to a real scene and spawn in the location registry. Travel is recorded.

const PROLOGUE_SCENE := "res://game/levels/prologue/prologue.tscn"
const CH1 := &"ch01/oruvel_underway"
const CH1_SPAWN := &"Drop"
const CH4 := &"ch04/haluna_wake"
const CH4_SPAWN := &"NemeDoor"
## Longer than first_playable.json end_card.min_hold_sec.
const PAST_HOLD_SEC := 60.0
const DT := 1.0 / 30.0
const MAX_FRAMES := 3000

var _saved_state: GameStateData
var _nodes: Array[Node] = []


func before_each() -> void:
	_saved_state = Game.state
	Game.state = GameStateData.new()


func test_new_game_runs_the_prologue_into_ch01() -> void:
	var reg := LocationRegistry.load_default()
	var start := reg.resolve(reg.new_game_location, reg.new_game_spawn)
	assert_eq(start["scene"], PROLOGUE_SCENE, "New Game starts at the prologue")
	var scene := (load(PROLOGUE_SCENE) as PackedScene).instantiate() as PrologueScene
	scene.autoplay = false
	var travels: Array = []
	scene.travel = func(loc: StringName, spawn: StringName) -> bool:
		travels.append([loc, spawn])
		return true
	_add(scene)
	var seq := CutsceneSequencer.new()
	seq.instant = true
	scene.add_child(seq)
	scene.sequencer = seq
	scene.play()
	assert_eq(travels, [[CH1, CH1_SPAWN]], "the prologue hands off to Ch1's Underway at Drop")
	_assert_resolves(reg, CH1, CH1_SPAWN)
	_done()


func test_the_slice_ends_on_ch04s_chapter_card_then_ch04() -> void:
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_HALUNA)
	assert_eq(str(cfg.get("night_end_scene", "")), ChapterCard.SCENE, "B11 hands off to the chapter card")
	var cc := (load(ChapterCard.SCENE) as PackedScene).instantiate() as ChapterCard
	var went: Array = []
	cc.travel = func(loc: StringName, spawn: StringName) -> void: went.append([loc, spawn])
	_add(cc)
	assert_true(cc.voice_showing(), "B12's voice-over first, alone on black")
	var saw_title := false
	var frames := 0
	while went.is_empty() and frames < MAX_FRAMES:
		cc.advance(DT)
		saw_title = saw_title or (not cc.voice_showing() and cc.card.is_showing())
		frames += 1
	assert_true(saw_title, "then the chapter's title")
	assert_eq(went, [[CH4, CH4_SPAWN]], "then on to Ch4's wake night")
	assert_false(cc.go_on(), "once")
	assert_eq(tr("CHAPTER_CARD_CH04_TITLE"), "The Pilgrim's Wake", "the card's words are loc keys")
	_assert_resolves(LocationRegistry.load_default(), CH4, CH4_SPAWN)
	_done()


func test_act_ones_end_rolls_the_credits_then_the_title() -> void:
	var ch9: Dictionary = GreyboxZone.read_json("res://game/data/flow/chapters/ch09.json")
	assert_true(JSON.stringify(ch9).contains(EndCard.SCENE), "Ch9's last beat opens the end card")
	var went: Array = []
	FlowRouting.record = func(args: Array) -> void: went.append(args)
	var card := (load(EndCard.SCENE) as PackedScene).instantiate() as EndCard
	card.change_scene = func(path: String) -> void: went.append([path])
	_add(card)
	card.advance(PAST_HOLD_SEC)
	assert_true(card.credits_shown() > 0, "the credits roll")
	card.accept()
	FlowRouting.record = Callable()
	assert_eq(went, [[EndCard.DEFAULT_RETURN_SCENE]], "then the title")
	_done()


func _assert_resolves(reg: LocationRegistry, location: StringName, spawn: StringName) -> void:
	assert_true(reg.has_location(location), "%s is registered" % location)
	var to := reg.resolve(location, spawn)
	assert_eq(to["spawn"], spawn, "%s has spawn %s" % [location, spawn])
	assert_false(bool(to["fallback"]), "%s/%s resolves without a fallback" % [location, spawn])
	assert_true(ResourceLoader.exists(str(to["scene"])), "%s's scene exists" % location)


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	_nodes.append(n)


func _done() -> void:
	for n in _nodes:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	_nodes.clear()
	Game.state = _saved_state
