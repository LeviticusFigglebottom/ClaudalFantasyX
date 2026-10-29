extends TestCase
## M3-CIN-1233 (the Lead, under ADR 0042: the M2 review is approved): New Game plays Act I as one path. New Game →
## the prologue → Ch1's Underway at Drop; the slice's end card → Ch4's wake at NemeDoor; and once Ch9's last scene
## has set Act I's final flag, the same end card returns to the title. Every hand-off resolves to a real scene and
## spawn in the location registry. Travel is recorded, never performed.

const PROLOGUE_SCENE := "res://game/levels/prologue/prologue.tscn"
const CH1 := &"ch01/oruvel_underway"
const CH1_SPAWN := &"Drop"
const CH4 := &"ch04/haluna_wake"
const CH4_SPAWN := &"NemeDoor"
const ACT1_DONE := &"ch09_act_one_complete"
## Longer than first_playable.json end_card.min_hold_sec.
const PAST_HOLD_SEC := 60.0

var _saved_state: GameStateData
var _nodes: Array[Node] = []
var _prompt := ""


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


func test_the_slice_end_card_goes_on_into_ch04() -> void:
	var went := _accept_end_card()
	assert_eq(went, [[CH4, CH4_SPAWN]], "accept carries on into Ch4's wake night")
	assert_eq(_prompt, tr("FLOW_END_CARD_PROMPT_CONTINUE"), "the prompt says it goes on, not back to the title")
	_assert_resolves(LocationRegistry.load_default(), CH4, CH4_SPAWN)
	_done()


func test_after_act_one_the_end_card_returns_to_the_title() -> void:
	Game.set_flag(ACT1_DONE)  # Ch9's ch09_the_road_out sets it, then shows this card
	var went := _accept_end_card()
	assert_eq(went.size(), 1)
	assert_eq(went[0].size(), 1, "a scene change, not a travel")
	assert_eq(str(went[0][0]), EndCard.DEFAULT_RETURN_SCENE, "back to the title")
	assert_eq(_prompt, tr("FLOW_END_CARD_PROMPT"), "and says so")
	_done()


## Opens the end card, waits out its hold, accepts, and returns what FlowRouting / the card recorded.
func _accept_end_card() -> Array:
	var went: Array = []
	FlowRouting.record = func(args: Array) -> void: went.append(args)
	var card := (load(EndCard.SCENE) as PackedScene).instantiate() as EndCard
	card.change_scene = func(path: String) -> void: went.append([path])
	_add(card)
	_prompt = (card.get_node(^"%Prompt") as Label).text
	card.advance(PAST_HOLD_SEC)
	card.accept()
	FlowRouting.record = Callable()
	return went


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
