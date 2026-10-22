extends TestCase
## Dialogue integration: the ch02 sample scene end to end, Game-autoload flag access,
## EventBus forwarding, and DialogueRunner's comparison rules.

const FIXTURE := &"test_dialogue_fixture"
const BEACH := &"ch02_girl_on_the_beach"

var flags: DialogueFlagAccess
var runner: DialogueRunner


func before_each() -> void:
	flags = DialogueFlagAccess.new()
	runner = DialogueRunner.new(flags)
	runner.forward_events_to_bus = false


func _start(scene: StringName) -> void:
	assert_true(runner.load_scene(scene), "loads %s" % scene)
	assert_true(runner.start(), "starts %s" % scene)


## Steps until the next LINE / OPTIONS / END, skipping cues.
func _next_visible() -> DialogueStep:
	var step := runner.next()
	while step.is_cue():
		step = runner.next()
	return step


func _expect_line(line_id: String, msg: String = "") -> DialogueStep:
	var step := _next_visible()
	assert_true(step.is_line(), "expected a line %s %s" % [line_id, msg])
	assert_eq(step.line_id, StringName(line_id), msg)
	return step


## Steps until an OPTIONS step and returns it.
func _to_menu() -> DialogueStep:
	var step := _next_visible()
	while not step.is_options() and not step.is_end():
		step = _next_visible()
	assert_true(step.is_options(), "reached an options menu")
	return step


func _option_ids(step: DialogueStep) -> Array[String]:
	var out: Array[String] = []
	for o in step.options:
		out.append(String(o.line_id))
	return out


func test_compare_semantics() -> void:
	assert_true(DialogueRunner.compare("==", 7, 7.0), "int and float compare as numbers")
	assert_true(DialogueRunner.compare("<", false, 1), "unset flag (false) is 0")
	assert_true(DialogueRunner.compare(">=", 3.0, 3))
	assert_true(DialogueRunner.compare("==", "a", &"a"), "String and StringName are text")
	assert_true(DialogueRunner.compare("<", "abc", "abd"))
	assert_false(DialogueRunner.compare("==", "1", 1), "text never equals a number")
	assert_true(DialogueRunner.compare("!=", "1", 1))
	assert_false(DialogueRunner.compare("<", "1", 1), "ordering across types is false")


func test_truthy() -> void:
	assert_false(DialogueRunner.truthy(null))
	assert_false(DialogueRunner.truthy(0.0))
	assert_false(DialogueRunner.truthy(""))
	assert_true(DialogueRunner.truthy(2))
	assert_true(DialogueRunner.truthy("x"))


func test_events_forward_to_event_bus() -> void:
	var bus: Node = (Engine.get_main_loop() as SceneTree).root.get_node(^"EventBus")
	var seen: Array = []
	var cb := func(n: StringName, a: Array) -> void: seen.append([n, a])
	bus.connect(&"dialogue_event", cb)
	runner.forward_events_to_bus = true
	_start(FIXTURE)
	_to_menu()
	bus.disconnect(&"dialogue_event", cb)
	assert_eq(seen.size(), 1)
	assert_eq(seen[0][0], &"fixture_event")


func test_game_flag_access_uses_game_autoload() -> void:
	var game: Node = (Engine.get_main_loop() as SceneTree).root.get_node(^"Game")
	var saved: GameStateData = game.get("state")
	game.set("state", GameStateData.new())
	var access := GameFlagAccess.new()
	assert_eq(access.get_flag(&"test_flag"), false)
	access.set_flag(&"test_flag", true)
	assert_eq(game.call("get_flag", &"test_flag"), true)
	game.set("state", saved)


## Steps to the end, returning the ids of every line seen. Picks option 0 at any menu.
func _lines_to_end() -> Array[String]:
	var seen: Array[String] = []
	var step := _next_visible()
	while not step.is_end():
		if step.is_options():
			runner.choose(0)
		else:
			seen.append(String(step.line_id))
		step = _next_visible()
	return seen


## Full branch coverage of both vertical-slice cutscenes is in test_dialogue_vs_scenes.gd.
func test_beach_scene_named_lantern_path() -> void:
	var events: Array = []
	runner.event_triggered.connect(func(n: StringName, a: Array) -> void: events.append([n, a]))
	_start(BEACH)
	var first := _expect_line("ch02_beach_001")
	assert_eq(first.speaker, &"", "opens on narration")
	for id in ["016", "002", "003", "004", "005", "017", "006", "007"]:
		_expect_line("ch02_beach_" + id)
	var menu := _next_visible()
	assert_eq(_option_ids(menu), ["ch02_beach_008", "ch02_beach_010"] as Array[String])
	runner.choose(0)
	assert_eq(_expect_line("ch02_beach_009").emotion, &"tender")
	var rest := _lines_to_end()
	assert_true("ch02_beach_014" in rest, "lantern variant of the closing line")
	assert_false("ch02_beach_015" in rest)
	assert_eq(flags.get_flag(&"ch02_rhen_named_lantern"), true)
	assert_eq(flags.get_flag(&"ch02_met_asha"), true)
	assert_eq(events, [[&"zone_unlock", ["haluna_village"]]])


func test_beach_scene_deflect_path() -> void:
	_start(BEACH)
	_to_menu()
	runner.choose(1)
	_expect_line("ch02_beach_011")
	var rest := _lines_to_end()
	assert_true("ch02_beach_015" in rest, "plain variant of the closing line")
	assert_false("ch02_beach_014" in rest)
	assert_eq(flags.get_flag(&"ch02_rhen_named_lantern"), false)
	assert_eq(flags.get_flag(&"ch02_met_asha"), true)
