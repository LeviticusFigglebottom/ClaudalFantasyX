extends TestCase
## M2-FP-03: the end card shows its loc-keyed text, ignores accept during the hold, and returns to
## the title on accept (the scene change is recorded, never performed).

const RETURN_SCENE := "res://game/core/boot.tscn"
## Longer than first_playable.json end_card.min_hold_sec.
const PAST_HOLD_SEC := 60.0

var swaps: Array[String] = []
var card: EndCard


func before_each() -> void:
	card = (load(EndCard.SCENE) as PackedScene).instantiate() as EndCard
	card.change_scene = func(path: String) -> void: swaps.append(path)
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(card)


func _done() -> void:
	card.get_parent().remove_child(card)
	card.free()


func _accept_event() -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = &"ui_accept"
	ev.pressed = true
	return ev


func test_text_comes_from_loc_keys() -> void:
	var title := card.get_node(^"%Title") as Label
	var line := card.get_node(^"%Line") as Label
	assert_eq(title.text, tr("FLOW_END_CARD_TITLE"))
	assert_ne(title.text, "FLOW_END_CARD_TITLE", "translated")
	assert_eq(line.text, tr("FLOW_END_CARD_LINE"))
	assert_ne(line.text, "FLOW_END_CARD_LINE")
	_done()


func test_accept_waits_for_the_hold_then_returns_to_the_title() -> void:
	card.next_location = &""  # the title case (Act I's end; test_act1_route covers both)
	assert_false(card.prompt_shown(), "no prompt during the hold")
	assert_false(card.handle_input(_accept_event()), "accept is ignored during the hold")
	assert_eq(swaps, [] as Array[String])
	card.advance(PAST_HOLD_SEC)
	assert_true(card.prompt_shown())
	assert_true(card.handle_input(_accept_event()))
	assert_eq(swaps, [RETURN_SCENE] as Array[String], "back to the title")
	assert_false(card.handle_input(_accept_event()), "only once")
	assert_eq(swaps.size(), 1)
	_done()


func test_the_slice_card_goes_on_into_ch4_since_the_switch_flipped() -> void:
	# ADR 0042 (M3-CIN-1233, 2026-10-29): the M2 review is approved, so the slice's end card carries on into Act I.
	assert_eq(card.next_location, &"ch04/haluna_wake", "first_playable.json end_card.next_location")
	assert_eq(card.next_spawn, &"NemeDoor")
	_done()


func test_with_next_location_set_accept_goes_on_into_the_story() -> void:
	var went: Array = []
	FlowRouting.record = func(args: Array) -> void: went.append(args)
	card.next_location = &"ch04/haluna_wake"
	card.next_spawn = &"NemeDoor"
	card.advance(PAST_HOLD_SEC)
	assert_true(card.handle_input(_accept_event()))
	FlowRouting.record = Callable()
	assert_eq(went, [[&"ch04/haluna_wake", &"NemeDoor"]], "on to Ch4's wake night")
	assert_eq(swaps, [] as Array[String], "not back to the title")
	assert_false(card.handle_input(_accept_event()), "only once")
	_done()


func test_it_opens_on_rhens_voice_over_then_rolls_the_credits() -> void:
	var voice := card.get_node(^"%Voice") as Label
	assert_eq(voice.text, tr("FLOW_END_CARD_VOICE"), "B12's voice-over line (M2-FP-26)")
	assert_true("two days" in voice.text, "translated")
	var content := card.get_node(^"%Content") as Control
	card.advance(1.5)
	assert_eq(card.voice_alpha(), 1.0, "the line alone on black")
	assert_eq(content.modulate.a, 0.0, "before the card")
	assert_eq(card.credits_shown(), 0)
	card.advance(6.0)
	assert_eq(card.voice_alpha(), 0.0, "the line has gone")
	assert_true(content.modulate.a > 0.0, "the card comes up")
	card.advance(PAST_HOLD_SEC)
	var credits := card.get_node(^"%Credits") as VBoxContainer
	assert_true(credits.get_child_count() >= 4, "a short credits roll")
	assert_eq(card.credits_shown(), credits.get_child_count(), "every row in by the end of the hold")
	assert_eq((credits.get_child(credits.get_child_count() - 1) as Label).text, tr("CREDITS_THANKS"))
	assert_true(card.prompt_shown())
	_done()
