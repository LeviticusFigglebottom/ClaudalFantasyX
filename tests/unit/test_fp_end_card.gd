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
