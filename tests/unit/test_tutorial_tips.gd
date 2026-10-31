extends TestCase
## M2-UI-24: first-time tips. TutorialTips on a scratch flag set and setting; TipCard driven by
## advance() with its own TutorialTips (no FieldController).

var flags: Dictionary = {}
var on := true
var swell_unlocked := false
var made: Array[Node] = []


func before_each() -> void:
	_free_made()
	(Engine.get_main_loop() as SceneTree).paused = false
	UiSettings.set_shared(UiSettings.new())
	flags = {}
	on = true
	swell_unlocked = false


func test_each_trigger_raises_its_tip_once_per_save() -> void:
	var t := _tips()
	t.raise_field_ready()
	assert_true(t.queue.is_empty(), "the objective tip waits for Asha to join")
	flags[&"ch02_met_asha"] = true
	t.raise_field_ready()
	assert_eq(_ids(t), [&"objective"])
	t.raise_field_ready()
	assert_eq(_ids(t), [&"objective"], "never queued twice")
	var shop := Interactable.new()
	shop.payload = {"shop": "haluna_general"}
	t.raise_near(TutorialTips.tags_of(shop))
	shop.free()
	t.raise_flag(&"ch02_tideline_won", true)
	assert_eq(_ids(t), [&"objective", &"shop", &"field_menu"], "in the order raised")
	assert_eq(t.take()["id"], "objective")
	assert_true(flags.get(&"tut_objective_seen", false), "taking a tip marks it seen")
	t.raise_field_ready()
	assert_eq(_ids(t), [&"shop", &"field_menu"], "a seen tip never comes back")
	_done()


## The Lead's Act I onboarding pass (2026-10-29): the Swell tip (the gauge, its techniques and the field menu's fill
## modes) comes on the field after the menu's own tips have been read, never with them.
func test_the_swell_tip_follows_the_menu_tips() -> void:
	var t := _tips()
	flags[&"tut_field_menu_seen"] = true
	t.raise_field_ready()
	assert_eq(_ids(t), [&"menu_save"], "the menu-save tip first")
	assert_eq(t.take()["id"], "menu_save")
	t.raise_field_ready()
	assert_eq(_ids(t), [&"swell"], "then the Swell tip, on the next field")
	assert_eq(t.take()["id"], "swell")
	assert_true(flags.get(&"tut_swell_seen", false))
	t.raise_field_ready()
	assert_true(t.queue.is_empty(), "once per save")
	_done()


func test_a_shrine_is_tagged_and_the_setting_turns_tips_off() -> void:
	var shrine := SaveShrine.new()
	assert_true(TutorialTips.tags_of(shrine).has(TutorialTips.TAG_SHRINE))
	shrine.free()
	on = false
	var t := _tips()
	t.raise_near([TutorialTips.TAG_SHRINE] as Array[StringName])
	assert_true(t.queue.is_empty(), "tips off: nothing raised")
	assert_false(flags.get(&"tut_save_shrine_seen", false), "and nothing saved as seen")
	_done()


func test_the_card_shows_one_tip_reads_then_the_next() -> void:
	flags[&"ch02_met_asha"] = true
	var card := _card()
	card.advance(0.0)
	assert_true(card.is_showing(), "the field took input: the objective tip")
	assert_eq(card.title_text(), tr("TIP_OBJECTIVE_TITLE"))
	assert_false(card.body_text().contains("{"), "bindings filled in")
	assert_true(card.body_text().contains(InputNames.first_name(&"field_objective")))
	card.tips.raise_flag(&"ch02_tideline_won", true)
	var d := TutorialTips.load_data()
	card.advance(float(d["fade_sec"]) + 0.01)
	card.advance(card.hold_for(card.body_text()) + 0.01)
	card.advance(float(d["fade_sec"]) + 0.01)
	assert_false(card.is_showing())
	card.advance(0.0)
	assert_eq(card.title_text(), tr("TIP_FIELD_MENU_TITLE"), "the next tip in turn")
	(Engine.get_main_loop() as SceneTree).paused = true
	var held := card._t
	card.advance(5.0)
	assert_false(card._panel.visible, "a menu hides it")
	assert_eq(card._t, held, "and stops its clock")
	(Engine.get_main_loop() as SceneTree).paused = false
	_done()


## The Lead's first-hour pass (2026-10-30): New Game plays Act I (the prologue, then Ch1), so the Where-to-next tip
## comes with Ch1's first objective and the menu tip after Ch1's first won fight (the wickfry), not a chapter later
## on the slice's flags. Each still comes once.
func test_the_act1_route_teaches_the_objective_and_the_menu_in_ch1() -> void:
	var t := _tips()
	flags[&"ch01_started"] = true
	t.raise_field_ready()
	assert_true(t.queue.is_empty(), "nothing in the fade-in")
	t.raise_flag(&"ch01_saw_bell_room", true)
	flags[&"ch01_saw_bell_room"] = true
	assert_eq(_ids(t), [&"objective"], "the bell room (Ch1's second objective) brings the Where-to-next tip")
	t.raise_flag(&"ch01_wickfry_won", true)
	assert_eq(_ids(t), [&"objective", &"field_menu"], "the first won fight brings the menu tip")
	t.take()
	t.take()
	t.raise_flag(&"ch02_tideline_won", true)
	flags[&"ch02_met_asha"] = true
	t.raise_field_ready()
	assert_eq(_ids(t), [&"menu_save"], "the slice's flags in Ch2 raise neither again; the save tip follows")
	_done()


## The first fight's victory flag is set in the battle scene, where no field tip card listens; the zone then
## reloads. The field's first input catches the menu tip up, once.
func test_a_flag_set_while_no_field_listened_is_caught_up_on_the_field() -> void:
	var t := _tips()
	flags[&"ch01_wickfry_won"] = true
	t.raise_field_ready()
	assert_true(_ids(t).has(&"field_menu"), "the menu tip comes when the field takes input after the fight")
	t.take()
	t.raise_field_ready()
	assert_false(_ids(t).has(&"field_menu"), "and only once")
	_done()


## M4-A2P-1702 (act2-plan's ui/tutorials.md): Act II's field tips, once each: Seven heroes when Ch10 starts (caught up
## on the first field if it was set in the fade-in), Records when the archive's hands are found, and Dark shrines at the
## first shrine in reach after the heresy, not before. A layout trigger's shrine is a shrine too (M4-A2P-1004 F8).
func test_act2_tips_come_once_at_their_moment() -> void:
	var t := _tips()
	for f in [&"tut_objective_seen", &"tut_field_menu_seen", &"tut_menu_save_seen", &"tut_swell_seen"]:
		flags[f] = true
	flags[&"tut_save_shrine_seen"] = true
	flags[&"ch10_started"] = true
	t.raise_field_ready()
	assert_eq(_ids(t), [&"seven"], "Ch10's first field: the seven heroes")
	t.take()
	var shrine := Interactable.new()
	shrine.payload = {"save_shrine": "lowlight_shrine"}
	assert_true(TutorialTips.tags_of(shrine).has(TutorialTips.TAG_SHRINE), "a layout trigger's shrine is tagged")
	t.raise_near(TutorialTips.tags_of(shrine))
	assert_true(t.queue.is_empty(), "no dark-shrine tip before the heresy")
	t.raise_flag(&"ch13_archive_read", true)
	assert_eq(_ids(t), [&"records"])
	t.take()
	flags[&"ch14_declared_heretics"] = true
	t.raise_near(TutorialTips.tags_of(shrine))
	assert_eq(_ids(t), [&"dark_shrine"], "the first shrine after the heresy")
	t.take()
	t.raise_near(TutorialTips.tags_of(shrine))
	t.raise_field_ready()
	assert_true(t.queue.is_empty(), "each once")
	shrine.free()
	_done()


## M4-A2P-1007 A20: the new-Swell-mode tip comes on the first field after play unlocks a fill mode, once.
func test_the_swell_mode_tip_waits_for_an_unlock() -> void:
	var t := _tips()
	for f in [&"tut_objective_seen", &"tut_field_menu_seen", &"tut_menu_save_seen", &"tut_swell_seen"]:
		flags[f] = true
	t.raise_field_ready()
	assert_false(_ids(t).has(&"swell_mode"), "nothing unlocked yet")
	swell_unlocked = true
	t.raise_field_ready()
	assert_eq(_ids(t), [&"swell_mode"], "the first field after an unlock")
	t.take()
	t.raise_field_ready()
	assert_true(t.queue.is_empty(), "once")
	_done()


## A tip fades out when the player presses what it teaches: the menu tip does not wait out a visit to the menu and
## then ask again for what was just done.
func test_pressing_what_a_tip_teaches_dismisses_it() -> void:
	flags[&"ch01_wickfry_won"] = true
	var card := _card()
	card.tips.raise_flag(&"ch01_wickfry_won", true)
	card.advance(0.0)
	assert_eq(card.title_text(), tr("TIP_FIELD_MENU_TITLE"))
	assert_true(TutorialTips.actions_named(card.current).has(&"ui_cancel"), "the menu tip names Cancel")
	var other := InputEventAction.new()
	other.action = &"ui_down"
	other.pressed = true
	card._input(other)
	assert_eq(card.phase, TipCard.Phase.IN, "another key leaves it")
	var ev := InputEventAction.new()
	ev.action = &"ui_cancel"
	ev.pressed = true
	card._input(ev)
	assert_eq(card.phase, TipCard.Phase.OUT, "Cancel (the menu) fades it out")
	card.advance(float(TutorialTips.load_data()["fade_sec"]) + 0.01)
	assert_false(card.is_showing())
	_done()


func test_input_names_fill_bindings() -> void:
	FieldInput.ensure_actions()
	var key := InputNames.first_name(FieldInput.INTERACT, false)
	assert_ne(key, "")
	assert_eq(InputNames.fill("Press {field_interact}.", false), "Press %s." % key)
	assert_eq(InputNames.fill("{no_such_action}", false), "{no_such_action}", "unknown names stay")
	assert_eq(InputNames.first_name(FieldInput.INTERACT, true), tr("CTRL_PAD_A"))
	_done()


func _tips() -> TutorialTips:
	return TutorialTips.new(
		func(f: StringName) -> bool: return bool(flags.get(f, false)),
		func(f: StringName) -> void: flags[f] = true,
		func() -> bool: return on,
		func() -> bool: return swell_unlocked
	)


func _card() -> TipCard:
	FieldInput.ensure_actions()
	ObjectiveHud.ensure_action()
	var c := TipCard.new()
	c.tips = _tips()
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(c)
	made.append(c)
	return c


func _ids(t: TutorialTips) -> Array[StringName]:
	var out: Array[StringName] = []
	for row in t.queue:
		out.append(StringName(str(row["id"])))
	return out


func _done() -> void:
	_free_made()  # a test leaves no card in the tree
	InputNames.using_pad = false
	UiSettings.set_shared(null)


func _free_made() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
