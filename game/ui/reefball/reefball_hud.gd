class_name ReefballHud
extends Control
## The Reefball match HUD (M3-UI-01, SPEC §6.10, docs/kb/design/reefball.md, docs/kb/tech/ui.md
## "Reefball HUD"). Views over a ReefballMatch, and nothing else: every number it shows comes from
## the engine (snapshot(), legal_actions() / preview(), the signals' results), and it never changes
## match state. Choosing an action only emits `action_chosen`; ReefballHudController performs it.
##   - framing (top left): the match's name and what rides on it;
##   - scoreboard (top): both sides' scores and the clock (strokes left, overtime);
##   - contact (under it): whose contact it is, who holds the float and where, whether the float is
##     fetched, and what the last contact did (at its odds);
##   - the opponent read (top right): their side's play from its AI profile, and each opponent's band,
##     breath and part in the choice under the cursor (who takes the float on a miss);
##   - the drop (right): every diver's band, the holder, the fetch depth, the cursor's marks;
##   - the player's side (bottom right): each diver's band, breath and state;
##   - the choices (bottom left, the battle UI's MenuPage): rise, dive, a pass per teammate, loft,
##     each with its odds; the preview beside it shows the odds, the cost on the clock and in breath,
##     where it ends or that it scores, and who takes the float on a miss, before anything is chosen;
##   - a banner (centre) for a float brought up and for the end of the match.
## Input (keyboard, pad, mouse alike): ui_up / ui_down or hover move the cursor, ui_accept or a click
## chooses. Layout: game/data/ui/reefball_hud.json (M2-UI-29 pins).

signal action_chosen(action: StringName, target: StringName)

const DATA_PATH := "res://game/data/ui/reefball_hud.json"

## The match this HUD shows (read only).
var match_ref: ReefballMatch
## The options on the menu, as legal_actions() gave them (empty when the player is not choosing).
var options: Array[Dictionary] = []
## The actions not legal now, as refused_actions() gave them: greyed under the options with why (M3-RBL-201).
var refused: Array[Dictionary] = []
## The settings the HUD follows (UiSettings.shared() unless set before _ready).
var settings: UiSettings

var _d: Dictionary = {}
var _framing: PanelContainer
var _match_name: Label
var _stakes: Label
## The Reefball-only gear the player's side wears (ADR 0040; hidden when none).
var _gear: Label
var _scoreboard: PanelContainer
var _side_names: Array[Label] = []
var _scores: Array[Label] = []
var _clock: Label
var _contact_panel: PanelContainer
var _contact: Label
var _fetch: Label
var _result: Label
var _read: ReefballSidePanel
var _ours: ReefballSidePanel
var _drop: ReefballDropView
var _page: MenuPage
var _preview_panel: PanelContainer
var _p_title: Label
var _p_odds: Label
var _p_cost: Label
var _p_outcome: Label
var _p_miss: Label
var _p_winded: Label
var _banner: PanelContainer
var _banner_title: Label
var _banner_line: Label
var _built := false


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("reefball_hud")) != TYPE_DICTIONARY:
		push_error("ReefballHud: could not read 'reefball_hud' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["reefball_hud"] as Dictionary


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_d = load_data()
	if settings == null:
		settings = UiSettings.shared()
	settings.follow(self)
	_build()
	_built = true
	if match_ref != null:
		refresh()


## Shows `m` from now on (call before or after the HUD enters the tree).
func bind(m: ReefballMatch) -> void:
	match_ref = m
	if _built:
		_build_drop()
		refresh()


func section(key: String) -> Dictionary:
	return _d.get(key, {}) as Dictionary


# --- What the engine says, in words --------------------------------------------------------------


func diver_name(id: StringName) -> String:
	var d := match_ref.diver(id) if match_ref != null else null
	return tr(d.name_key) if d != null else ""


func band_name(depth: int) -> String:
	var bands: Array = match_ref.rules.get("bands", []) if match_ref != null else []
	return tr(str((bands[depth] as Dictionary).get("name_key", ""))) if depth >= 0 and depth < bands.size() else ""


func side_name(side: int) -> String:
	if match_ref == null or side < 0 or side >= match_ref.side_ids.size():
		return ""
	return tr(str((match_ref.db.sides[match_ref.side_ids[side]] as Dictionary).get("name_key", "")))


func action_name(action: StringName) -> String:
	var a := (match_ref.rules.get("actions", {}) as Dictionary).get(String(action), {}) as Dictionary
	return tr(str(a.get("name_key", "")))


## The menu label of one option: the action, or "Pass to <name>".
func option_label(o: Dictionary) -> String:
	if StringName(o["action"]) == ReefballMatch.PASS:
		return tr("RBL_HUD_PASS_TO").format({"name": diver_name(o["target"])})
	return action_name(o["action"])


static func percent(odds: float) -> int:
	return roundi(odds * 100.0)


# --- Refresh from the engine ---------------------------------------------------------------------


## Redraws every view from match_ref.snapshot(), keeping the cursor's marks.
func refresh() -> void:
	if match_ref == null or not _built:
		return
	var snap := match_ref.snapshot()
	var mine := int(snap["player_side"])
	var score: Array = snap["score"]
	for i in 2:
		var side := mine if i == 0 else 1 - mine
		_side_names[i].text = side_name(side)
		HudLayout.fit_label(_side_names[i], HudLayout.num(section("scoreboard"), "side_width"))
		_scores[i].text = str(score[side])
	_clock.text = clock_text()
	_match_name.text = tr(str(match_ref.match_row.get("name_key", "")))
	_stakes.text = tr(stakes_key())
	_stakes.visible = stakes_key() != ""
	_gear.text = gear_text()
	_gear.visible = _gear.text != ""
	_refresh_contact()
	_refresh_divers()


## The clock line: strokes left, or the overtime period with the golden rule. The last action may
## spend more strokes than were left (the engine lets it): the clock shows none left, not fewer.
func clock_text() -> String:
	var n := maxi(0, match_ref.strokes_left)
	if match_ref.in_overtime:
		return tr("RBL_HUD_OVERTIME").format({"p": match_ref.overtime_period, "n": n})
	return tr("RBL_HUD_STROKES").format({"n": n})


## What rides on the match: the match row's stakes_key (M3-RBL-201; "" when it has none).
func stakes_key() -> String:
	return str(match_ref.match_row.get("stakes_key", ""))


## The gear the player's side wears, by name ("" when none; ReefballMatch.worn_gear, ADR 0040).
func gear_text() -> String:
	var names: Array[String] = []
	for gid in match_ref.worn_gear:
		names.append(tr(str((match_ref.db.gear.get(gid, {}) as Dictionary).get("name_key", ""))))
	if names.is_empty():
		return ""
	return tr("RBL_HUD_WEARING_FMT").format({"gear": tr("RBL_OUTFIT_BONUS_JOIN").join(names)})


## The opponent read: the line for the opposing AI profile ("" when none).
func read_key() -> String:
	return str(section("reads").get(str(match_ref.match_row.get("ai_profile", "")), ""))


func _refresh_contact() -> void:
	var h := match_ref.holder
	if h == null or match_ref.finished:
		_contact.text = ""
		_fetch.text = ""
		_contact.visible = false
		_fetch.visible = false
		return
	_contact.visible = true
	_fetch.visible = true
	var yours := h.side == match_ref.player_side
	var key := "RBL_HUD_CONTACT_YOURS" if yours else "RBL_HUD_CONTACT_THEIRS"
	_contact.text = tr(key).format({"name": diver_name(h.id), "band": band_name(h.depth), "side": side_name(h.side)})
	var role := StringName(str(section("contact")["yours_role" if yours else "theirs_role"]))
	_contact.add_theme_color_override(&"font_color", _c(role))
	if match_ref.fetched:
		_fetch.text = tr("RBL_HUD_FETCHED")
	else:
		_fetch.text = tr("RBL_HUD_UNFETCHED").format({"band": band_name(match_ref.fetch_depth())})


func _refresh_divers() -> void:
	var o := current_option()
	var target: StringName = o.get("target", &"") if not o.is_empty() else &""
	var taker: StringName = o.get("fail_to", &"") if not o.is_empty() else &""
	var against: Array = o.get("against", []) if not o.is_empty() else []
	var mine := match_ref.player_side
	var ours: Array[Dictionary] = []
	var theirs: Array[Dictionary] = []
	var dots: Array[Dictionary] = []
	var holder_id := match_ref.holder.id if match_ref.holder != null else &""
	for d in match_ref.divers:
		var row := {
			"id": d.id,
			"name": tr(d.name_key),
			"band": band_name(d.depth),
			"breath": d.breath,
			"max_breath": d.max_breath(),
			"low_fraction": _low_fraction(d),
		}
		var tag := ""
		var tag_role := &""
		if d.id == taker:
			tag = tr("RBL_HUD_TAG_TAKER")
			tag_role = StringName(str(section("read")["tag_role"]))
		elif against.has(d.id):
			tag = tr("RBL_HUD_TAG_AGAINST")  # counted in the odds (M3-RBL-201)
			tag_role = StringName(str(section("read")["against_role"]))
		elif d.id == target:
			tag = tr("RBL_HUD_TAG_TARGET")
			tag_role = StringName(str(section("side")["tag_role"]))
		elif d.id == holder_id and not match_ref.finished:
			tag = tr("RBL_HUD_TAG_FLOAT")
			tag_role = &"focus_gold"
		elif d.resting:
			tag = tr("RBL_HUD_TAG_RESTING")
		elif ReefballFormulas.winded(match_ref.rules, d):
			tag = tr("RBL_HUD_TAG_WINDED")
			tag_role = &"danger"
		row["tag"] = tag
		row["tag_role"] = tag_role
		(ours if d.side == mine else theirs).append(row)
		dots.append({"id": d.id, "side": 0 if d.side == mine else 1, "depth": d.depth, "resting": d.resting})
	_ours.set_header(tr("RBL_HUD_SIDE_TITLE").format({"side": side_name(mine)}))
	_ours.set_rows(ours)
	_read.set_header(tr("RBL_HUD_READ_TITLE").format({"side": side_name(1 - mine)}))
	_read.set_read(tr(read_key()) if read_key() != "" else "")
	_read.set_rows(theirs)
	if _drop != null:
		var shown_holder := holder_id if not match_ref.finished else &""
		_drop.show_state(dots, shown_holder, match_ref.fetch_depth(), target, taker)


## The gauge turns to its warning look at the engine's winded line (rules breath.winded_at).
func _low_fraction(d: ReefballDiver) -> float:
	var at := float((match_ref.rules.get("breath", {}) as Dictionary).get("winded_at", 0))
	return (at + 0.5) / float(maxi(1, d.max_breath()))


# --- The choice ----------------------------------------------------------------------------------


## Opens the menu on `opts` (ReefballMatch.legal_actions()), cursor on the first; `not_now`
## (ReefballMatch.refused_actions()) are listed greyed after them with a short reason.
func show_choices(opts: Array[Dictionary], not_now: Array[Dictionary] = []) -> void:
	options = opts
	refused = not_now
	_rebuild_page()
	_refresh_preview()
	refresh()


## Closes the menu and the preview (the other side's contact, a result, the end).
func hide_choices() -> void:
	options = []
	refused = []
	if _page != null:
		_page.queue_free()
		remove_child(_page)
		_page = null
	_preview_panel.visible = false
	if match_ref != null:
		refresh()


func is_choosing() -> bool:
	return not options.is_empty() and _page != null


func cursor() -> int:
	return _page.cursor if _page != null else -1


## Moves the cursor to option `index` (a test or a capture driver; the player hovers or presses).
func set_cursor(index: int) -> void:
	if _page == null:
		return
	_page.set_cursor(index, false)
	_on_cursor_moved()


func current_option() -> Dictionary:
	var i := cursor()
	return options[i] if i >= 0 and i < options.size() else {}


## The menu page (input parity tests hover and click its rows).
func page() -> MenuPage:
	return _page


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event while choosing. Returns true when it was used.
func handle_input(event: InputEvent) -> bool:
	if not is_choosing():
		return false
	if event.is_action_pressed(&"ui_up", true):
		if _page.move(-1):
			_on_cursor_moved()
	elif event.is_action_pressed(&"ui_down", true):
		if _page.move(1):
			_on_cursor_moved()
	elif event.is_action_pressed(&"ui_accept"):
		choose(cursor())
	else:
		return false
	return true


## Chooses option `index`: emits action_chosen (the controller performs it).
func choose(index: int) -> void:
	if index < 0 or index >= options.size():
		return
	var o := options[index]
	action_chosen.emit(StringName(o["action"]), StringName(o.get("target", &"")))


func _rebuild_page() -> void:
	if _page != null:
		_page.queue_free()
		remove_child(_page)
	var m := section("commands")
	var rows: Array[Dictionary] = []
	for o in options:
		var sure := float(o["odds"]) >= 1.0
		(
			rows
			. append(
				{
					"id": o["action"],
					"label": option_label(o),
					"right": tr("RBL_HUD_ODDS").format({"odds": percent(float(o["odds"]))}),
					"right_role": StringName(str(m["sure_role" if sure else "odds_role"])),
				}
			)
		)
	var short := section("refused_short")
	for r in refused:
		var why := str(r.get("reason_key", ""))
		var row := {"id": r["action"], "label": option_label(r), "right": tr(str(short.get(why, why)))}
		row["right_role"] = &"text_dim"
		row["enabled"] = false  # listed so the player sees what is not on offer, and why
		rows.append(row)
	_page = MenuPage.new()
	_page.name = &"Choices"
	var r := HudLayout.rect_of(m)
	var h := MenuPage.height_for(m, rows.size())
	# The page sits on the commands rect's foot: fewer rows, a shorter page, same bottom margin.
	HudLayout.place_rect(_page, Rect2(r.position.x, r.end.y - h, r.size.x, h), HudLayout.pin_of(m))
	_page.size = Vector2(r.size.x, h)
	add_child(_page)
	_page.reduced_motion = settings.reduced_motion()
	_page.setup(m, &"reefball", tr("RBL_HUD_COMMANDS_TITLE"), rows)
	_page.row_hovered.connect(func(_i: int) -> void: _on_cursor_moved())
	_page.row_clicked.connect(choose)


func _on_cursor_moved() -> void:
	_refresh_preview()
	_refresh_divers()


## The preview of the option under the cursor: everything about it before it is chosen.
func _refresh_preview() -> void:
	var o := current_option()
	_preview_panel.visible = not o.is_empty()
	if o.is_empty():
		return
	var pm := section("preview")
	_p_title.text = option_label(o)
	var odds := float(o["odds"])
	_p_odds.text = (
		tr("RBL_HUD_PREVIEW_SURE") if odds >= 1.0 else tr("RBL_HUD_PREVIEW_ODDS").format({"odds": percent(odds)})
	)
	_p_cost.text = tr("RBL_HUD_PREVIEW_COST").format({"strokes": int(o["strokes"]), "breath": int(o["breath"])})
	if bool(o["scores"]):
		_p_outcome.text = tr("RBL_HUD_PREVIEW_SCORES")
		_p_outcome.add_theme_color_override(&"font_color", _c(StringName(str(pm["score_role"]))))
	else:
		_p_outcome.text = tr("RBL_HUD_PREVIEW_ENDS").format({"band": band_name(int(o["to_depth"]))})
		if bool(o.get("fetches", false)):
			_p_outcome.text = tr("RBL_HUD_PREVIEW_FETCHES").format({"line": _p_outcome.text})
		_p_outcome.remove_theme_color_override(&"font_color")
	var taker := StringName(o.get("fail_to", &""))
	_p_miss.visible = taker != &""
	_p_miss.text = tr("RBL_HUD_PREVIEW_MISS").format({"taker": diver_name(taker)}) if taker != &"" else ""
	var actor := match_ref.diver(StringName(o["actor"]))
	var winded := actor != null and ReefballFormulas.winded(match_ref.rules, actor)
	_p_winded.visible = winded
	_p_winded.text = tr("RBL_HUD_PREVIEW_WINDED").format({"name": diver_name(actor.id)}) if winded else ""


func preview_lines() -> PackedStringArray:
	var out := PackedStringArray()
	if not _preview_panel.visible:
		return out
	for l: Label in [_p_title, _p_odds, _p_cost, _p_outcome, _p_miss, _p_winded]:
		if l.visible and l.text != "":
			out.append(l.text)
	return out


# --- Results, scores, the end --------------------------------------------------------------------


## Shows what the last contact did (ReefballMatch.action_resolved's result), at its odds.
func show_result(r: Dictionary) -> void:
	if not bool(r.get("ok", false)):
		return
	var action := StringName(r["action"])
	var words := {
		"actor": diver_name(r["actor"]),
		"target": diver_name(r.get("target", &"")),
		"taker": diver_name(r.get("holder", &"")),
		"band": band_name(int(r["to_depth"])),
	}
	var key := ""
	if bool(r["success"]):
		if bool(r["scored"]):
			key = "RBL_HUD_RESULT_SCORE"
		else:
			key = (
				{
					ReefballMatch.RISE: "RBL_HUD_RESULT_RISE",
					ReefballMatch.DIVE: "RBL_HUD_RESULT_DIVE",
					ReefballMatch.PASS: "RBL_HUD_RESULT_PASS",
				}
				. get(action, "")
			)
	else:
		key = (
			{
				ReefballMatch.RISE: "RBL_HUD_RESULT_RISE_MISS",
				ReefballMatch.PASS: "RBL_HUD_RESULT_PASS_MISS",
				ReefballMatch.LOFT: "RBL_HUD_RESULT_LOFT_MISS",
			}
			. get(action, "")
		)
	var line := tr(key).format(words) if key != "" else ""
	if float(r["odds"]) < 1.0:
		line += " " + tr("RBL_HUD_RESULT_AT").format({"odds": percent(float(r["odds"]))})
	_result.text = line
	_result.visible = line != ""


func result_text() -> String:
	return _result.text if _result.visible else ""


## The banner for a float brought up by `side`, with the score (ReefballMatch.float_scored).
func show_goal(side: int, score: Array) -> void:
	var mine := match_ref.player_side
	_show_banner(
		tr("RBL_HUD_GOAL_TITLE"),
		tr("RBL_HUD_GOAL_LINE").format({"side": side_name(side), "a": score[mine], "b": score[1 - mine]})
	)
	refresh()


## The banner for the end of the match (ReefballMatch.match_finished).
func show_final(outcome: StringName, score: Array) -> void:
	var mine := match_ref.player_side
	var key := "RBL_HUD_FINAL_DRAW"
	var side := mine
	if outcome == ReefballMatch.WIN:
		key = "RBL_HUD_FINAL_WIN"
	elif outcome == ReefballMatch.LOSS:
		key = "RBL_HUD_FINAL_LOSS"
		side = 1 - mine
	_show_banner(
		tr("RBL_HUD_FINAL_TITLE"), tr(key).format({"side": side_name(side), "a": score[mine], "b": score[1 - mine]})
	)
	refresh()


func hide_banner() -> void:
	_banner.visible = false


func banner_shown() -> bool:
	return _banner.visible


func banner_text() -> String:
	return "%s\n%s" % [_banner_title.text, _banner_line.text] if _banner.visible else ""


func _show_banner(title: String, line: String) -> void:
	_banner_title.text = title
	_banner_line.text = line
	_banner.visible = true


# --- Read-outs for tests --------------------------------------------------------------------------


func score_text() -> String:
	return "%s %s %s %s" % [_side_names[0].text, _scores[0].text, _scores[1].text, _side_names[1].text]


func contact_text() -> String:
	return _contact.text if _contact.visible else ""


func fetch_text() -> String:
	return _fetch.text if _fetch.visible else ""


func framing_text() -> String:
	return "%s\n%s" % [_match_name.text, _stakes.text if _stakes.visible else ""]


func clock_shown() -> String:
	return _clock.text


func side_panel() -> ReefballSidePanel:
	return _ours


func read_panel() -> ReefballSidePanel:
	return _read


func drop_view() -> ReefballDropView:
	return _drop


## The HUD's pinned pieces: [[label, Control, pin], ...] (the aspect audit, M2-UI-29).
func pieces() -> Array:
	var out: Array = [
		["framing", _framing, str(section("framing")["pin"])],
		["scoreboard", _scoreboard, str(section("scoreboard")["pin"])],
		["contact", _contact_panel, str(section("contact")["pin"])],
		["read", _read, str(section("read")["pin"])],
		["side", _ours, str(section("side")["pin"])],
	]
	if _drop != null:
		out.append(["drop", _drop, str(section("drop")["pin"])])
	if _page != null:
		out.append(["choices", _page, str(section("commands")["pin"])])
	if _preview_panel.visible:
		out.append(["preview", _preview_panel, str(section("preview")["pin"])])
	if _banner.visible:
		out.append(["banner", _banner, str(section("banner")["pin"])])
	return out


# --- Build ---------------------------------------------------------------------------------------


func _build() -> void:
	var fm := section("framing")
	_framing = _panel(fm)
	var fbox := _vbox(_framing, fm)
	_match_name = _label(&"HeaderLabel", fbox)
	_match_name.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_stakes = _wrap(&"HelpDimLabel", fbox, fm)
	_gear = _wrap(&"HelpDimLabel", fbox, fm)

	var sm := section("scoreboard")
	_scoreboard = _panel(sm)
	var sbox := _vbox(_scoreboard, sm)
	var line := HBoxContainer.new()
	line.mouse_filter = Control.MOUSE_FILTER_IGNORE
	line.alignment = BoxContainer.ALIGNMENT_CENTER
	sbox.add_child(line)
	for i in 2:
		var n := _label(&"HudName", null)
		n.custom_minimum_size.x = HudLayout.num(sm, "side_width")
		n.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		n.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT if i == 0 else HORIZONTAL_ALIGNMENT_LEFT
		var s := _label(&"DamageNumber", null)
		s.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_side_names.append(n)
		_scores.append(s)
	line.add_child(_side_names[0])
	line.add_child(_scores[0])
	var dash := _label(&"DamageNumber", line)
	dash.text = tr("RBL_HUD_SCORE_DASH")
	dash.custom_minimum_size.x = HudLayout.num(sm, "dash_width")
	dash.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	line.add_child(_scores[1])
	line.add_child(_side_names[1])
	_clock = _wrap(&"HelpLabel", sbox, sm)
	_clock.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	var cm := section("contact")
	_contact_panel = _panel(cm)
	var cbox := _vbox(_contact_panel, cm)
	_contact = _wrap(&"MenuLabel", cbox, cm)
	_fetch = _wrap(&"HelpDimLabel", cbox, cm)
	_result = _wrap(&"HelpLabel", cbox, cm)
	_result.visible = false

	_read = ReefballSidePanel.new()
	_read.name = &"Read"
	add_child(_read)
	_read.setup(section("read"))
	_ours = ReefballSidePanel.new()
	_ours.name = &"Ours"
	add_child(_ours)
	_ours.setup(section("side"))
	_build_drop()

	var pm := section("preview")
	_preview_panel = _panel(pm)
	var pbox := _vbox(_preview_panel, pm)
	_p_title = _wrap(&"MenuLabel", pbox, pm)
	_p_odds = _wrap(&"HudNumber", pbox, pm)
	_p_odds.add_theme_color_override(&"font_color", _c(StringName(str(section("commands")["odds_role"]))))
	_p_cost = _wrap(&"HelpLabel", pbox, pm)
	_p_outcome = _wrap(&"HelpLabel", pbox, pm)
	_p_miss = _wrap(&"HelpLabel", pbox, pm)
	_p_miss.add_theme_color_override(&"font_color", _c(StringName(str(pm["miss_role"]))))
	_p_winded = _wrap(&"HelpDimLabel", pbox, pm)
	_preview_panel.visible = false

	var bm := section("banner")
	_banner = _panel(bm)
	var bbox := _vbox(_banner, bm)
	_banner_title = _wrap(&"BannerLabel", bbox, bm)
	_banner_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_banner_line = _wrap(&"HelpLabel", bbox, bm)
	_banner_line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_banner.visible = false


func _build_drop() -> void:
	if match_ref == null or _drop != null or _read == null:
		return
	var names := PackedStringArray()
	for i in (match_ref.rules.get("bands", []) as Array).size():
		names.append(band_name(i))
	_drop = ReefballDropView.new()
	_drop.name = &"Drop"
	add_child(_drop)
	move_child(_drop, _ours.get_index())
	_drop.setup(section("drop"), names)


func _panel(sec: Dictionary) -> PanelContainer:
	var p := PanelContainer.new()
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(p)
	HudLayout.place(p, sec)
	return p


func _vbox(p: PanelContainer, sec: Dictionary) -> VBoxContainer:
	var box := VBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_theme_constant_override(&"separation", int(HudLayout.num(sec, "gap")))
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	p.add_child(box)
	return box


func _label(variation: StringName, parent: Node) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if parent != null:
		parent.add_child(l)
	return l


## A label that wraps onto as many lines as it needs inside its panel (the panel grows with it).
func _wrap(variation: StringName, parent: Node, sec: Dictionary) -> Label:
	var l := _label(variation, parent)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var p := parent
	while p != null and not p is PanelContainer:
		p = p.get_parent()
	var sb := (p as PanelContainer).get_theme_stylebox(&"panel") if p != null else null
	l.custom_minimum_size.x = HudLayout.rect_of(sec).size.x - (sb.get_minimum_size().x if sb != null else 0.0)
	return l


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)
