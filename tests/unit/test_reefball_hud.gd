extends TestCase
## M3-UI-01: the Reefball HUD is a view over ReefballMatch. Every number it shows is the engine's
## (snapshot, legal_actions / preview, the signals), it never changes match state, and the
## controller lets the player choose on their contacts and the AI play the other side's.

const MATCH := &"tidecup_opening"
const SEED := 7
const SMART := &"smart"
const MAX_STEPS := 600

var db: ReefballDB
var m: ReefballMatch
var hud: ReefballHud
var ctl: ReefballHudController


func before_each() -> void:
	InputDriver.clear_screen()
	UiSettings.set_shared(UiSettings.new())
	db = ReefballDB.load_default()


func test_the_layout_data_has_every_section_and_pin() -> void:
	var d := ReefballHud.load_data()
	for key in ["framing", "scoreboard", "contact", "read", "side", "drop", "commands", "preview", "banner"]:
		var sec := d.get(key, {}) as Dictionary
		assert_false(sec.is_empty(), "section %s" % key)
		assert_true(HudLayout.PINS.has(str(sec.get("pin", ""))), "%s names a known pin" % key)
	assert_true(d.has("pacing") and d.has("reads") and d.has("stakes"))
	_done()


func test_the_kickoff_shows_the_engine_state() -> void:
	_open()
	var snap := m.snapshot()
	assert_true(hud.score_text().contains(tr("RBL_SIDE_ORUVEL")), "the player's side named")
	assert_true(hud.score_text().contains(tr("RBL_SIDE_PEMAKAR")), "the other side named")
	assert_eq(hud.clock_shown(), tr("RBL_HUD_STROKES").format({"n": snap["strokes_left"]}), "the clock")
	var holder := m.diver(StringName(snap["holder"]))
	assert_true(hud.contact_text().contains(tr(holder.name_key)), "who holds the float")
	assert_true(hud.contact_text().contains(hud.band_name(holder.depth)), "and where")
	assert_true(hud.framing_text().contains(tr("RBL_MATCH_TIDECUP_OPENING")), "the match's name")
	assert_true(hud.framing_text().contains(tr("RBL_HUD_STAKES_TIDECUP_OPENING")), "what rides on it")
	assert_eq(hud.read_panel().read_text(), tr("RBL_HUD_READ_BOLD"), "the opponent read: the bold profile")
	assert_eq(hud.read_panel().row_count() + hud.side_panel().row_count(), m.divers.size(), "a row a diver")
	for d in m.divers:
		var panel := hud.side_panel() if d.side == m.player_side else hud.read_panel()
		assert_eq(panel.band_of(d.id), hud.band_name(d.depth), "%s's band" % d.id)
		assert_eq(
			panel.breath_of(d.id),
			tr("RBL_HUD_BREATH").format({"b": d.breath, "max": d.max_breath()}),
			"%s's breath" % d.id
		)
		assert_true(hud.drop_view().dot_centre(d.id).x >= 0.0, "%s has a dot in the drop" % d.id)
	_done()


func test_each_option_shows_the_engines_preview_before_it_is_chosen() -> void:
	_open()
	assert_true(hud.is_choosing(), "the player's contact")
	assert_eq(hud.options, m.legal_actions(), "the menu is legal_actions(), in order")
	var before := m.snapshot()
	var roll_state := m.rng.state
	for i in hud.options.size():
		hud.set_cursor(i)
		var o := hud.options[i]
		var p := m.preview(o["action"], o["target"])
		assert_eq(o, p, "option %d is preview()" % i)
		var lines := "\n".join(hud.preview_lines())
		var odds := float(p["odds"])
		var odds_text := (
			tr("RBL_HUD_PREVIEW_SURE")
			if odds >= 1.0
			else tr("RBL_HUD_PREVIEW_ODDS").format({"odds": ReefballHud.percent(odds)})
		)
		assert_true(lines.contains(odds_text), "option %d shows its odds: %s" % [i, lines])
		var cost := tr("RBL_HUD_PREVIEW_COST").format({"strokes": p["strokes"], "breath": p["breath"]})
		assert_true(lines.contains(cost), "option %d shows its cost" % i)
		var taker := StringName(p["fail_to"])
		if taker != &"":
			assert_true(
				lines.contains(tr("RBL_HUD_PREVIEW_MISS").format({"taker": hud.diver_name(taker)})),
				"option %d names who takes a miss" % i
			)
			assert_eq(hud.read_panel().tag_of(taker), tr("RBL_HUD_TAG_TAKER"), "the read marks the taker")
			assert_eq(hud.drop_view().taker, taker, "and so does the drop")
		if StringName(p["action"]) == ReefballMatch.PASS:
			assert_eq(hud.side_panel().tag_of(p["target"]), tr("RBL_HUD_TAG_TARGET"), "the receiver is marked")
			assert_eq(hud.drop_view().target, StringName(p["target"]), "in the drop too")
		if bool(p["scores"]):
			assert_true(lines.contains(tr("RBL_HUD_PREVIEW_SCORES")), "a scoring option says so")
	assert_eq(m.snapshot(), before, "looking at the options changes nothing")
	assert_eq(m.rng.state, roll_state, "and draws no roll")
	_done()


func test_a_choice_is_performed_and_its_result_shown() -> void:
	_open()
	var o := hud.options[hud.cursor()]
	var results: Array = []
	m.action_resolved.connect(func(r: Dictionary) -> void: results.append(r))
	hud.choose(hud.cursor())
	assert_eq(results.size(), 1, "one contact performed")
	assert_eq(results[0]["action"], o["action"])
	assert_ne(hud.result_text(), "", "the result line says what happened")
	if float(o["odds"]) < 1.0:
		var at := tr("RBL_HUD_RESULT_AT").format({"odds": ReefballHud.percent(float(o["odds"]))})
		assert_true(hud.result_text().ends_with(at), "at the odds it was taken at")
	assert_eq(hud.clock_shown(), tr("RBL_HUD_STROKES").format({"n": m.strokes_left}), "the clock ran")
	_done()


func test_their_contact_waits_for_the_ai_then_plays() -> void:
	_open()
	ctl.pacing_scale = 1.0
	for _i in MAX_STEPS:
		if not m.is_player_contact():
			break
		if ctl.is_waiting():
			ctl.flush()  # the player's own contact opens at once
		hud.choose(0)
	assert_false(m.is_player_contact(), "the other side has the float")
	assert_false(hud.is_choosing(), "no menu on their contact")
	assert_true(hud.contact_text().contains(hud.side_name(1 - m.player_side)), "their contact, by name")
	var think := HudLayout.num(ReefballHud.load_data()["pacing"] as Dictionary, "ai_think_sec")
	var contacts := m.contacts
	ctl.advance(think * 0.5)
	assert_eq(m.contacts, contacts, "the AI is still thinking")
	ctl.advance(think)
	assert_eq(m.contacts, contacts + 1, "then it plays its contact")
	_done()


func test_a_goal_shows_the_banner_and_the_new_score() -> void:
	_open(true)
	var scored: Array = []
	m.float_scored.connect(func(side: int, score: Array) -> void: scored.append([side, score]))
	for _i in MAX_STEPS:
		if not scored.is_empty() or not ctl.flush():
			break
	assert_eq(scored.size(), 1, "a float came up")
	assert_true(hud.banner_shown(), "the banner is up")
	var side: int = scored[0][0]
	var score: Array = scored[0][1]
	assert_true(hud.banner_text().contains(hud.side_name(side)), "naming who scored")
	assert_true(hud.score_text().contains(str(score[side])), "the scoreboard has the new score")
	assert_true(ctl.is_waiting(), "the banner holds before the next contact")
	ctl.flush()
	assert_false(hud.banner_shown(), "and goes when it opens")
	_done()


func test_a_whole_match_ends_on_the_final_banner() -> void:
	_open(true)
	var over: Array = []
	ctl.match_over.connect(func(outcome: StringName, score: Array) -> void: over.append([outcome, score]))
	for _i in MAX_STEPS * 4:
		if not ctl.flush():
			break
	assert_eq(over.size(), 1, "the match ended once")
	assert_true(m.finished)
	assert_true(hud.banner_text().begins_with(tr("RBL_HUD_FINAL_TITLE")), "the final banner")
	assert_false(hud.is_choosing(), "no menu after the end")
	assert_eq(hud.contact_text(), "", "no contact line after the end")
	_done()


func test_overtime_shows_the_golden_rule() -> void:
	_open()
	m.in_overtime = true
	m.overtime_period = 1
	m.strokes_left = 5
	hud.refresh()
	assert_eq(hud.clock_shown(), tr("RBL_HUD_OVERTIME").format({"p": 1, "n": 5}))
	_done()


func test_an_unfetched_float_says_where_to_take_it() -> void:
	_open()
	m.fetched = false
	hud.refresh()
	assert_eq(hud.fetch_text(), tr("RBL_HUD_UNFETCHED").format({"band": hud.band_name(m.fetch_depth())}))
	m.fetched = true
	hud.refresh()
	assert_eq(hud.fetch_text(), tr("RBL_HUD_FETCHED"))
	_done()


## Both shot drivers reach their picture.
func test_the_capture_drivers_reach_their_state() -> void:
	for mode: ReefballHudShot.Mode in [ReefballHudShot.Mode.CHOICE, ReefballHudShot.Mode.GOAL]:
		var shot := (
			(
				(
					load(
						(
							"res://game/ui/reefball/shots/reefball_hud_choice.tscn"
							if mode == ReefballHudShot.Mode.CHOICE
							else "res://game/ui/reefball/shots/reefball_hud_goal.tscn"
						)
					)
					as PackedScene
				)
				. instantiate()
			)
			as ReefballHudShot
		)
		ParityHost.scene_root().add_child(shot)
		if mode == ReefballHudShot.Mode.CHOICE:
			assert_true(shot.hud.is_choosing(), "choice: the menu is open")
			assert_eq(StringName(shot.hud.current_option()["action"]), ReefballMatch.PASS, "on a pass")
		else:
			assert_true(shot.hud.banner_shown(), "goal: the banner is up")
			assert_false(shot.match_state.finished, "just after the first float, not the end")
			assert_true(shot.hud.banner_text().begins_with(tr("RBL_HUD_GOAL_TITLE")), "the goal banner")
		shot.get_parent().remove_child(shot)
		shot.free()
	_done()


func _open(ai_plays_us: bool = false) -> void:
	m = ReefballMatch.new()
	m.setup(db, MATCH, SEED)
	hud = ReefballHud.new()
	ParityHost.scene_root().add_child(hud)
	ctl = ReefballHudController.new()
	ctl.pacing_scale = 0.0
	ctl.manual = true
	if ai_plays_us:
		ctl.player_ai = ReefballAI.new(db.ai_profiles.get(SMART, {}))
	ParityHost.scene_root().add_child(ctl)
	ctl.start(m, hud)
	if ai_plays_us:
		return
	for _i in MAX_STEPS:
		if hud.is_choosing() or not ctl.flush():
			return


func _done() -> void:
	for n: Node in [hud, ctl]:
		if is_instance_valid(n) and n.get_parent() != null:
			n.get_parent().remove_child(n)
			n.free()
	UiSettings.set_shared(null)
