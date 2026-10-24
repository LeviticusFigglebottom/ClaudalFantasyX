extends TestCase
## M2-UI-03: the chant, brace and glyph panels on the battle HUD (SwellRingView with SwellChantDraw,
## SwellBraceDraw and SwellGlyphDraw), driven through the capture scripts and simulated ui_* input
## on the sandbox scene with the frozen fixtures; the grade words, the "unlocked" float, the held
## accept that starts Toma's brace, and the seven-row root page.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"

var ctl: BattleController


func before_each() -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)


func test_every_hero_gets_a_gauge_and_a_swell_row() -> void:
	ctl.start_fixture(BattleFixture.load_fixture(&"swell_chant"))
	for cid: StringName in [&"asha", &"rhen"]:
		assert_true(ctl.hud.party.row_for(cid).swell_gauge() != null, String(cid))
	_to_turn_of(&"asha")
	var row := _root_row(BattleMenus.ROW_SWELL)
	assert_eq(str(row["right"]), tr("SWELL_INPUT_CHANT"), "full: the row names Asha's input")
	_free()


func test_the_chant_panel_follows_asha_s_notes() -> void:
	ctl.run_script(BattleCaptureScript.SCRIPT_SWELL_CHANT)
	var view := ctl.hud.swell_ring
	assert_true(view.is_open())
	var chant := ctl.swell_input() as SwellChant
	assert_true(chant != null, "Asha's input is the chant")
	assert_eq(chant.grades, [&"perfect"] as Array[StringName])
	assert_eq(view.callout_text(), tr("HUD_SWELL_GRADE_PERFECT"), "the perfect note is named")
	assert_eq(view.hint_text(), tr("HUD_SWELL_CHANT_HINT_LOCKED"), "no Cancel once a note is sung")
	assert_eq(view.status_text(), "", "the chant has no status line")
	assert_eq(chant.expected_button(), SwellInput.BUTTON_UP)
	_free()


func test_a_sung_phrase_unleashes_shallows_verse() -> void:
	ctl.start_fixture(BattleFixture.load_fixture(&"swell_chant"))
	var chant := _open(&"asha", &"") as SwellChant
	assert_eq(ctl.hud.swell_ring.hint_text(), tr("HUD_SWELL_CHANT_HINT"), "Cancel until the first note")
	var actions := {
		SwellInput.BUTTON_UP: &"ui_up",
		SwellInput.BUTTON_DOWN: &"ui_down",
		SwellInput.BUTTON_LEFT: &"ui_left",
		SwellInput.BUTTON_RIGHT: &"ui_right",
	}
	while not chant.is_done():
		ctl.tick(chant.time_to_peak())
		_press(actions[chant.expected_button()])
	assert_false(ctl.hud.swell_ring.is_open())
	var grades: Array[StringName] = []
	for i in chant.grade_count():
		grades.append(SwellInput.GRADE_PERFECT)
	var expected := ctl.menus.swell_result_text(grades, 90)
	assert_true(ctl.hud.help_history.has(expected), expected)
	_free()


func test_the_brace_panel_shows_the_hold_and_names_braced() -> void:
	ctl.run_script(BattleCaptureScript.SCRIPT_SWELL_BRACE)
	var view := ctl.hud.swell_ring
	var brace := ctl.swell_input() as SwellBrace
	assert_true(brace.holding)
	assert_eq(brace.grades, [&"braced"] as Array[StringName])
	assert_eq(view.callout_text(), tr("HUD_SWELL_GRADE_BRACED"))
	assert_eq(view.status_text(), tr("HUD_SWELL_BRACE_HOLDING"))
	assert_eq(view.hint_text(), tr("HUD_SWELL_BRACE_HINT_LOCKED"))
	_free()


func test_a_held_brace_released_on_the_counter_unleashes_return_tide() -> void:
	ctl.start_fixture(BattleFixture.load_fixture(&"swell_brace"))
	var brace := _open(&"toma", &"gull_harrier") as SwellBrace
	assert_eq(ctl.hud.swell_ring.status_text(), tr("HUD_SWELL_BRACE_NOT_HOLDING"))
	_press(&"ui_accept")
	assert_eq(ctl.hud.swell_ring.status_text(), tr("HUD_SWELL_BRACE_HOLDING"))
	while brace.blows_left() > 0:
		ctl.tick(brace.time_to_peak())
	ctl.tick(brace.time_to_peak())
	_release(&"ui_accept")
	assert_false(ctl.hud.swell_ring.is_open())
	var expected := ctl.menus.swell_result_text([&"braced", &"braced", &"braced", &"perfect"], 90)
	assert_true(ctl.hud.help_history.has(expected), expected)
	_free()


func test_the_glyph_panel_traces_and_earns_swift() -> void:
	ctl.run_script(BattleCaptureScript.SCRIPT_SWELL_GLYPH)
	var view := ctl.hud.swell_ring
	var glyph := ctl.swell_input() as SwellGlyph
	assert_eq(glyph.grades, [&"traced", &"traced"] as Array[StringName])
	assert_eq(view.callout_text(), tr("HUD_SWELL_GRADE_TRACED"))
	assert_eq(view.hint_text(), tr("HUD_SWELL_GLYPH_HINT_LOCKED"))
	assert_true(glyph.time_to_peak() > 0.0, "Swift is still in reach in the shot")
	ctl.swell_input_live = true
	var actions := {
		SwellInput.BUTTON_UP: &"ui_up",
		SwellInput.BUTTON_DOWN: &"ui_down",
		SwellInput.BUTTON_LEFT: &"ui_left",
		SwellInput.BUTTON_RIGHT: &"ui_right",
	}
	while not glyph.is_done():
		_press(actions[glyph.expected_button()])
	assert_eq(glyph.grades[-1], SwellGlyph.GRADE_SWIFT)
	assert_true(_said(tr("HUD_SWELL_GRADE_SWIFT")), "the result names Swift")
	_free()


func test_every_grade_has_its_word() -> void:
	var m := BattleMenus.new()
	assert_eq(m.grade_text(&"braced"), tr("HUD_SWELL_GRADE_BRACED"))
	assert_eq(m.grade_text(&"traced"), tr("HUD_SWELL_GRADE_TRACED"))
	assert_eq(m.grade_text(&"swift"), tr("HUD_SWELL_GRADE_SWIFT"))
	assert_eq(m.grade_text(&"perfect"), tr("HUD_SWELL_GRADE_PERFECT"))
	assert_eq(m.grade_text(&"unknown"), tr("HUD_SWELL_GRADE_MISS"))
	for kind: StringName in SwellInput.KINDS:
		assert_ne(tr(SwellRingView.hint_key(kind, false)), SwellRingView.hint_key(kind, false), "has a line")
		assert_ne(tr(SwellRingView.hint_key(kind, true)), SwellRingView.hint_key(kind, true), "has a line")


func test_the_panel_follows_every_kind_to_its_end() -> void:
	# Each kind fresh, part-way and done, with and without reduced motion (the figures themselves
	# are drawn in the capture shots: a headless test runs no draw pass).
	var view := ctl.hud.swell_ring
	var rows: Array = BattleSwell.load_config()["inputs"]
	for reduced in [false, true]:
		view.reduced_motion = reduced
		for row: Dictionary in rows:
			var input := SwellInput.create(row)
			view.open(input, "T", "hint")
			assert_eq(view.callout_text(), "", "nothing graded yet")
			input.advance(input.time_to_peak())
			input.press(SwellInput.BUTTON_ACCEPT)
			input.press(SwellInput.BUTTON_DOWN)
			view.refresh()
			input.advance(input.duration_sec())
			view.refresh()
			assert_true(input.is_done(), String(input.kind))
			assert_ne(view.callout_text(), "", "a done input names its last grade")
	view.close()
	_free()


func test_an_unlock_through_play_floats_its_name() -> void:
	ctl.start_fixture(BattleFixture.load_fixture(&"swell_ring"))
	ctl.show_damage_numbers = true
	assert_true(ctl.swell.unlock_mode(&"tether"))
	var want := tr("HUD_SWELL_MODE_UNLOCKED_FMT").format({"mode": tr("SWELL_MODE_TETHER")})
	assert_eq(str(ctl.hud.recent_numbers[-1]["text"]), want)
	ctl.show_damage_numbers = false
	var shown := ctl.hud.damage_numbers_shown
	ctl.swell.unlock_mode(&"salve")
	assert_eq(ctl.hud.damage_numbers_shown, shown, "captures stay still")
	_free()


func test_an_accept_held_from_the_menu_starts_the_brace() -> void:
	ctl.start_fixture(BattleFixture.load_fixture(&"swell_brace"))
	var brace := _open(&"toma", &"gull_harrier") as SwellBrace
	assert_false(brace.holding, "Input holds nothing in a headless test")
	var clock := SwellRingClock.new(brace, func() -> int: return 0)
	assert_true(SwellInputKeys.carry_held(clock, func(_a: StringName) -> bool: return true))
	assert_true(brace.holding)
	_release(&"ui_accept")
	assert_true(brace.grades.is_empty(), "a tap's release in the lead-in only lets go")
	_free()


func test_a_seven_row_root_stands_whole_above_the_foot() -> void:
	# Asha with a bag and Ilun bound: Attack, Swell, Skills, Call, Items, Escape, Swap.
	var m := HudLayout.section(&"commands")
	assert_true(int(HudLayout.num(m, "max_rows")) >= 7, "no row scrolls out of sight")
	var rows: Array[Dictionary] = []
	for i in 7:
		rows.append({"id": StringName("r%d" % i), "label": "Row %d" % i, "enabled": true})
	ctl.start_fixture(BattleFixture.load_fixture(&"swell_chant"))
	ctl.hud.commands.open_root(&"root", "Asha", rows)
	var page := ctl.hud.commands.top_page()
	var foot := HudLayout.rect_of(m).end.y
	assert_true(is_equal_approx(page.position.y + page.size.y, foot), "grows upward from the same foot")
	var help := HudLayout.rect_of(HudLayout.section(&"help_line"))
	assert_true(page.position.y > help.end.y, "clear of the help line")
	for i in 7:
		assert_true(page.row_rect(i).end.y <= page.size.y, "row %d inside the frame" % i)
	_free()


func test_the_lamp_at_rest_is_an_ember_and_has_no_halo() -> void:
	# M2-UI-08 (art/ui.md §10.2): the core at rest measures a warm hue (Oklab 60-90°, C >= 0.05),
	# not the panel's grey, and the halo follows the flare only.
	var view := ctl.hud.swell_ring
	var ring := SwellTimingRing.new(BattleSwell.load_config()["inputs"][0])
	view.reduced_motion = true
	view.open(ring, "Lamp Dive", "hint")
	assert_eq(view.flare(), 0.0, "the lead-in is at rest")
	var lab := _oklab(view.lamp_core(view.brightness()))
	var hue := rad_to_deg(atan2(lab.z, lab.y))
	var chroma := Vector2(lab.y, lab.z).length()
	assert_true(hue >= 60.0 and hue <= 90.0, "warm hue at rest: %.1f°" % hue)
	assert_true(chroma >= 0.05, "not grey at rest: C %.3f" % chroma)
	assert_true(view.lamp_core(1.0).is_equal_approx(view.color(&"swell")), "at the peak the core is the swell color")
	ring.advance(ring.time_to_peak())
	assert_eq(view.flare(), 1.0, "the halo is full at the peak")
	view.close()
	_free()


# --- helpers ------------------------------------------------------------------------------


## sRGB color -> Oklab (L, a, b) (Björn Ottosson's matrices).
static func _oklab(c: Color) -> Vector3:
	var lin := c.srgb_to_linear()
	var l := 0.4122214708 * lin.r + 0.5363325363 * lin.g + 0.0514459929 * lin.b
	var m := 0.2119034982 * lin.r + 0.6806995451 * lin.g + 0.1073969566 * lin.b
	var s := 0.0883024619 * lin.r + 0.2817188376 * lin.g + 0.6299787005 * lin.b
	l = pow(l, 1.0 / 3.0)
	m = pow(m, 1.0 / 3.0)
	s = pow(s, 1.0 / 3.0)
	return Vector3(
		0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
		1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
		0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
	)


## Opens `cid`'s Swell technique on `target` (&"": its default targets); returns the input.
func _open(cid: StringName, target: StringName) -> SwellInput:
	_to_turn_of(cid)
	ctl.hud.commands.select(BattleMenus.ROW_SWELL)
	_press(&"ui_accept")
	_press(&"ui_accept")
	if target != &"":
		ctl.aim_at(target)
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SWELL_INPUT)
	return ctl.swell_input()


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


func _root_row(rid: StringName) -> Dictionary:
	for r in ctl.hud.commands.top_page().rows:
		if StringName(str(r["id"])) == rid:
			return r
	fail("no root row %s" % rid)
	return {}


func _said(text: String) -> bool:
	for line in ctl.hud.help_history:
		if line.contains(text):
			return true
	return false


func _press(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	ctl.handle_input(ev)


func _release(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = false
	ctl.handle_input(ev)


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
