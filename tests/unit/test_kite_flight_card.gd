extends TestCase
## The Kite's flight card (KiteFlightCard, M5-A3P-1711): it names where the Kite is bound, follows the router's fade
## (up as the screen goes black, down as the new place comes in), and goes once the fade has covered and lifted,
## or after max_sec. Fly puts it up only when a change has really started.

var alpha := 0.0


func test_the_card_names_the_place_and_follows_the_fade() -> void:
	UiSettings.set_shared(UiSettings.new())
	var card := _card()
	assert_eq(card.line_text(), tr("KITE_FLIGHT_BOUND_FMT").format({"place": "Oruvel"}))
	assert_eq(card.region_text(), "The Low Reaches")
	alpha = 0.5
	card.advance(0.1)
	assert_between(card.alpha(), 0.49, 0.51, "half up with the fade")
	alpha = 1.0
	card.advance(0.1)
	assert_eq(card.alpha(), 1.0, "full on the black")
	alpha = 0.3
	card.advance(0.1)
	assert_false(card.is_queued_for_deletion(), "still there while the new place fades in")
	alpha = 0.0
	card.advance(0.1)
	assert_true(card.is_queued_for_deletion(), "gone once the fade has lifted")
	_free(card)


func test_the_card_waits_for_the_cover_and_never_outstays_max_sec() -> void:
	UiSettings.set_shared(UiSettings.new())
	var card := _card()
	alpha = 0.0
	card.advance(0.1)
	assert_false(card.is_queued_for_deletion(), "a clear screen before the cover is not the end")
	card.advance(float(card.data["max_sec"]))
	assert_true(card.is_queued_for_deletion(), "max_sec in any case")
	_free(card)


func test_a_flight_that_changes_nothing_puts_up_no_card() -> void:
	UiSettings.set_shared(UiSettings.new())
	var bag := {&"kite_flying": true}
	var m := KiteMapModel.new(
		KiteMapModel.load_data(),
		func(f: StringName) -> Variant: return bag.get(f, false) or f == &"ch01_started",
		func(_f: StringName, _v: Variant) -> void: pass,
		func(_loc: StringName, _spawn: StringName) -> bool: return true
	)
	var host := Node.new()
	ParityHost.scene_root().add_child(host)
	var menu := KiteMapMenu.open_in(host, m)
	assert_true(menu.fly(&"oruvel"))
	var router := host.get_tree().root.get_node_or_null(^"SceneRouter")
	var cards := 0
	for n in (router.get_children() if router != null else []) + host.find_children("*", "", true, false):
		if n is KiteFlightCard:
			cards += 1
	assert_eq(cards, 0, "the travel was only recorded: no card")
	if menu.motion() != null:
		menu.motion().finish()
	host.get_tree().paused = false
	host.get_parent().remove_child(host)
	host.free()
	UiSettings.set_shared(null)


func _card() -> KiteFlightCard:
	var card := KiteFlightCard.new()
	card.data = KiteFlightCard.load_data()
	card.fade = func() -> float: return alpha
	alpha = 0.0
	ParityHost.scene_root().add_child(card)
	card.set_place("Oruvel", "The Low Reaches")
	return card


func _free(card: KiteFlightCard) -> void:
	card.get_parent().remove_child(card)
	card.free()
	UiSettings.set_shared(null)
