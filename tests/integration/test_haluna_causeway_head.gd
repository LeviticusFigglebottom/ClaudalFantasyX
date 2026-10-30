extends TestCase
## M2-FP-20 and M2-FP-21 on the real Haluna zone: the causeway head before the first save (an
## overheard bark that sends Rhen to the town shrine, without stopping him or handing off), and B05's
## "Go now" / "Not yet" choice after it ("Not yet" steps Rhen back with nothing handed off and the
## trigger fires again on the next approach; "Go now" opens the Shell Shrine trial).

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const UNSAVED_BARK := &"ch02_bark_causeway_unsaved"
## M2-FP-25: "Go now" travels to the Saltgrass Causeway (B06), which leads on to the Shell Shrine.
const CAUSEWAY := "ch03/saltgrass_causeway"
const ASK_LINE := &"ch02_low_tide_005"
const DECLINE_LINE := &"ch02_low_tide_008"
const DT := 1.0 / 60.0
const GO_NOW := 0
const NOT_YET := 1

var zone: HalunaZone
var story: HalunaStory
var saved_state: GameStateData
var lines: Array[StringName] = []
var overheard: Array[StringName] = []
var hand_offs: Array[Array] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	lines.clear()
	overheard.clear()
	hand_offs.clear()
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	story = zone.get_node("Story") as HalunaStory
	story.autostart = false
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	story.active = true
	story.sequencer.instant = true
	story.sequencer.line_shown.connect(func(s: DialogueStep) -> void: lines.append(s.line_id))
	story.overhear.line_shown.connect(func(s: DialogueStep) -> void: overheard.append(s.line_id))
	story.hand_off = func(kind: StringName, target: String) -> void: hand_offs.append([kind, target])
	Game.set_flag(&"ch02_met_asha", true)
	Game.set_flag(&"ch02_ate_at_nemes", true)  # M4-A2P-115 A4: the causeway rule waits for Neme's table


func test_the_unsaved_trigger_is_an_overheard_bark_on_the_causeway_box() -> void:
	var bark := _interactable(&"causeway_head_unsaved")
	var head := _interactable(&"causeway_head")
	assert_true(bark != null and head != null, "both causeway triggers exist")
	if bark == null or head == null:
		_done()
		return
	assert_eq(bark.activation, Interactable.Activation.TOUCH)
	assert_eq(bark.payload, {"dialogue": String(UNSAVED_BARK), "overheard": true})
	assert_eq(bark.requires_flag, &"ch02_ate_at_nemes", "after Neme's table (M4-A2P-115 A4)")
	assert_eq(bark.blocked_by_flag, &"ch02_saved_once", "silent once Rhen has saved")
	assert_false(bark.once, "every walk-in before the first save")
	assert_true(bark.global_transform.is_equal_approx(head.global_transform), "the same place as the causeway head")
	var a := (bark.get_child(0) as CollisionShape3D).shape
	var b := (head.get_child(0) as CollisionShape3D).shape
	assert_true(a == b, "and the same box")
	assert_false(bark.contains_point(zone.spawn_marker(&"CausewayHead").global_position), "arrives short of it")
	_done()


func test_before_the_save_the_bark_plays_and_rhen_walks_on() -> void:
	_walk_in()
	assert_eq(hand_offs, [] as Array[Array], "no hand-off before the first save")
	assert_true(story.overhear.is_playing(), "the bark plays")
	assert_false(story.sequencer.is_playing(), "B05 does not")
	assert_true(zone.player.accepts_input, "Rhen is not stopped")
	assert_false(story.busy, "nothing is blocked")
	_run_overhear()
	assert_true(&"toma" in _speakers_of(UNSAVED_BARK) and &"asha" in _speakers_of(UNSAVED_BARK), "Toma and Asha")
	assert_eq(overheard.size(), 2, "both lines were heard")
	assert_eq(lines, [] as Array[StringName], "B05 never started")
	# Walk out and back in: it plays again.
	overheard.clear()
	_walk_in()
	assert_true(story.overhear.is_playing(), "plays again on the next approach")
	_run_overhear()
	assert_eq(overheard.size(), 2)
	assert_eq(hand_offs, [] as Array[Array])
	# After the save the bark is silent and the causeway head plays B05.
	Game.set_flag(&"ch02_saved_once", true)
	assert_false(_interactable(&"causeway_head_unsaved").is_available(), "silent after the save")
	overheard.clear()
	_walk_in()
	assert_eq(overheard, [] as Array[StringName])
	assert_true(ASK_LINE in lines, "B05 plays")
	assert_eq(hand_offs.size(), 1, "and hands off (Go now by default)")
	_done()


func test_not_yet_returns_control_and_the_trigger_fires_again() -> void:
	Game.set_flag(&"ch02_saved_once", true)
	story.sequencer.auto_choice = NOT_YET
	_walk_in()
	assert_true(ASK_LINE in lines and DECLINE_LINE in lines, "Asha asks; Rhen says not yet")
	# M4-A2P-115 A3: the tide and the invitation come before the choice; Toma's objection and the walk wait.
	assert_true(&"ch02_low_tide_002" in lines, "Asha's invitation comes before the choice")
	assert_false(&"ch02_low_tide_003" in lines, "the rest of B05 waits")
	assert_eq(hand_offs, [] as Array[Array], "nothing handed off")
	assert_false(story.busy)
	assert_false(story.sequencer.is_playing())
	assert_true(zone.player.accepts_input, "control returns")
	var head := _interactable(&"causeway_head")
	var spawn := zone.spawn_marker(&"CausewayHead").global_position
	assert_true(zone.player.global_position.distance_to(spawn) < 0.6, "Rhen steps back to the causeway spawn")
	assert_false(head.contains_point(zone.player.global_position), "off the trigger")
	assert_true(head.is_available(), "the trigger stays armed")
	# The next approach asks again; this time, go.
	lines.clear()
	story.sequencer.auto_choice = GO_NOW
	_walk_in()
	assert_true(ASK_LINE in lines, "the trigger fired again")
	assert_true(&"ch02_low_tide_004" in lines, "B05 plays to its end")
	assert_eq(hand_offs, [[StringName(HalunaStory.KEY_GO), CAUSEWAY]] as Array[Array], "the causeway")
	_done()


func test_go_now_hands_off_to_the_causeway() -> void:
	Game.set_flag(&"ch02_saved_once", true)
	story.sequencer.auto_choice = GO_NOW
	assert_true(_interactable(&"causeway_head").on_touched())
	assert_false(DECLINE_LINE in lines)
	assert_true(&"ch02_low_tide_001" in lines and &"ch02_low_tide_004" in lines, "B05 as before")
	assert_eq(hand_offs, [[StringName(HalunaStory.KEY_GO), CAUSEWAY]] as Array[Array])
	_done()


func test_the_choice_and_the_decline_event_are_data() -> void:
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_HALUNA)
	assert_eq(str(cfg.get("ending_decline_event", "")), "departure_declined")
	assert_true(zone.spawn_marker(StringName(str(cfg.get("ending_decline_spawn", "")))) != null, "a real spawn")
	var runner := DialogueRunner.new(DialogueFlagAccess.new())
	runner.forward_events_to_bus = false
	var events: Array[StringName] = []
	runner.event_triggered.connect(func(n: StringName, _a: Array) -> void: events.append(n))
	assert_true(runner.load_scene(&"ch02_low_tide") and runner.start())
	var step := runner.next()
	while not step.is_end() and not step.is_options():
		step = runner.next()
	assert_true(step.is_options(), "B05 asks before it starts")
	assert_eq(step.options.size(), 2, "Go now / Not yet")
	runner.choose(step.options[NOT_YET].index)
	step = runner.next()
	while not step.is_end():
		step = runner.next()
	assert_eq(events, [&"departure_declined"] as Array[StringName])
	_done()


## Places Rhen at the causeway spawn and walks him north until a causeway trigger fires (or 4 s).
func _walk_in() -> void:
	zone.place_at(&"CausewayHead", zone.spawn_yaw_deg(&"CausewayHead"))
	zone.player.step(DT)  # leave whatever box he was in, so the next entry counts
	var fired := [false]
	var on_used := func(_i: Interactable) -> void: fired[0] = true
	var watched: Array[Interactable] = [_interactable(&"causeway_head"), _interactable(&"causeway_head_unsaved")]
	for it: Interactable in watched:
		it.used.connect(on_used)
	for _i in int(4.0 / DT):
		if fired[0]:
			break
		var basis := Basis(Vector3.UP, zone.director.camera_yaw())
		var d := Vector3.FORWARD
		zone.player.input_override = Vector2(d.dot(basis * Vector3.RIGHT), -d.dot(basis * Vector3.FORWARD))
		zone.player.step(DT)
		zone.director.update(DT)
	zone.player.input_override = Vector2.ZERO
	for it: Interactable in watched:
		it.used.disconnect(on_used)
	assert_true(fired[0], "walked into the causeway head")


func _run_overhear() -> void:
	var guard := 0
	while story.overhear.is_playing() and guard < 3000:
		guard += 1
		if story.overhear.overlay.box.is_revealing():
			story.overhear.overlay.box.skip_reveal()
		story.overhear.advance(1.0 / 30.0)
	assert_false(story.overhear.is_playing(), "the bark ends by itself")


func _speakers_of(scene: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	var runner := DialogueRunner.new(DialogueFlagAccess.new())
	runner.forward_events_to_bus = false
	if not (runner.load_scene(scene) and runner.start()):
		return out
	var step := runner.next()
	while not step.is_end():
		if step.is_line():
			out.append(step.speaker)
		step = runner.next()
	return out


func _interactable(id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	return null


func _done() -> void:
	if zone != null:
		_host().remove_child(zone)
		zone.free()
		zone = null
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
