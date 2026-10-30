extends TestCase
## The Lead's controller-only pass (2026-10-30): Act I's menus walked with the pad alone. Every row of the field
## menu's root is chosen and each page is walked (Down, Confirm into it, Cancel back out, as a player would). After
## every press:
##   - the button prompts on screen are the pad's: no `{action}` left unfilled, and no key's name where the pad has
##     its own button for that action (a prompt that still says "Enter" after a pad press is a missing prompt);
##   - every menu page says how to go back (a help or controls line naming Cancel; the battle's command menu is the
##     exception by design: its help line is the action's cost and turn, and Cancel there opens the pause);
##   - focus is not lost: when a Control holds the focus it is one on screen (a hidden or freed one takes the pad's
##     presses and nothing answers).
## In battle, each command row is chosen and walked the same way (into its page and its target pick, then Cancel back
## to the command menu), and the pause menu is opened with Cancel and walked, Settings and back included.
## Each screen's own parity test covers its moves; test_input_parity_dead_ends covers Cancel walking out.

## Presses into a page: Down then Confirm, DIVE times (its columns, an entry, a picker).
const DIVE := 3
const MAX_BACKS := 8
## Words that are the game's own and only share a key's name: the battle's Escape (flee) command.
const NOT_KEY_KEYS: Array[String] = ["HUD_CMD_ESCAPE"]
## The word every menu's help names the way back with (English: the tests run in it).
const BACK_WORD := "Cancel"
const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const BATTLE_ROWS: Array[StringName] = [
	BattleMenus.ROW_ATTACK,
	BattleMenus.ROW_SKILLS,
	BattleMenus.ROW_ITEMS,
	BattleMenus.ROW_SWELL,
	BattleMenus.ROW_SWAP,
	BattleMenus.ROW_ESCAPE,
]

var menu: FieldMenu
var ctl: BattleController
var _key_names: Dictionary = {}  # key name -> the action it names, for every action whose pad button differs


func before_each() -> void:
	InputDriver.clear_screen()
	UiSettings.set_shared(UiSettings.new())


func after_each() -> void:
	InputNames.using_pad = false
	UiSettings.set_shared(null)


func test_every_field_menu_page_shows_the_pad_s_prompts_and_keeps_focus() -> void:
	FlowRouting.record = func(_change: Array) -> void: pass  # Quit to Title's Confirm changes no scene here
	_collect_key_names()
	var d := InputDriver.new(InputDriver.Kind.PAD)
	menu = ParityHost.open_field_menu(_played_state())
	var ids: Array[StringName] = []
	for i in menu.root_page().row_count():
		ids.append(StringName(str(menu.root_page().rows[i].get("id", ""))))
	ParityHost.free_field_menu(menu)
	for id in ids:
		menu = ParityHost.open_field_menu(_played_state())
		FlowRouting.record = func(_change: Array) -> void: pass  # free_field_menu clears it each time
		d.press(&"ui_down")  # the pad is the device from the first press, as in play
		d.press(&"ui_up")
		ParityHost.choose(d, menu.root_page(), ParityHost.row_of(menu.root_page(), id))
		_settle()
		_check(menu, "%s: opened" % id)
		for n in DIVE:
			if not menu.is_open():
				break
			d.press(&"ui_down")
			_settle()
			_check(menu, "%s: Down %d" % [id, n])
			d.press(&"ui_accept")
			_settle()
			_check(menu, "%s: Confirm %d" % [id, n])
		var backs := 0
		while menu.is_open() and backs < MAX_BACKS:
			ParityHost.back(d, menu)
			_settle()
			if menu.is_open():
				_check(menu, "%s: back %d" % [id, backs])
			backs += 1
		ParityHost.free_field_menu(menu)
	menu = null
	FlowRouting.record = Callable()


func test_every_battle_command_and_the_pause_show_the_pad_s_prompts_and_keep_focus() -> void:
	_collect_key_names()
	var d := InputDriver.new(InputDriver.Kind.PAD)
	for rid in BATTLE_ROWS:
		_start_battle()
		var page := ctl.hud.commands.top_page()
		var at := _row_index(page, rid)
		if at < 0:
			_free_battle()
			continue
		d.press(&"ui_down")
		while page.cursor != at:
			d.press(&"ui_down")
		_check(ctl, "battle %s: on its row" % rid, false)
		for n in DIVE:
			if ctl.state != BattleController.STATE_COMMAND and ctl.state != BattleController.STATE_TARGET:
				break
			d.press(&"ui_accept")
			_check(ctl, "battle %s: Confirm %d" % [rid, n], false)
		var backs := 0
		while ctl.state == BattleController.STATE_TARGET or ctl.hud.commands.depth() > 1:
			if backs >= MAX_BACKS:
				fail("battle %s: Cancel does not walk back to the command menu" % rid)
				break
			d.press(&"ui_cancel")
			_check(ctl, "battle %s: back %d" % [rid, backs], false)
			backs += 1
		_free_battle()
	_start_battle()
	var pauser := ctl.get_node("BattlePause") as BattlePause
	pauser._hook_commands()
	d.press(&"ui_cancel")
	assert_true(pauser.is_paused(), "Cancel at the command root opens the pause")
	_check(ctl, "pause: opened")
	var rows := pauser.menu.rows_page()
	for i in rows.row_count():
		d.press(&"ui_down")
		_check(ctl, "pause: row %d" % rows.cursor)
	var settings_at := _row_index(rows, BattlePauseMenu.ROW_SETTINGS)
	while rows.cursor != settings_at:
		d.press(&"ui_down")
	d.press(&"ui_accept")
	assert_true(pauser.menu.settings_menu != null, "Settings opens from the pause")
	_check(ctl, "pause: Settings")
	d.press(&"ui_down")
	d.press(&"ui_accept")
	_check(ctl, "pause: a Settings page")
	for _n in MAX_BACKS:
		if not pauser.is_paused():
			break
		d.press(&"ui_cancel")
		if pauser.is_paused():
			_check(ctl, "pause: back")
	assert_false(pauser.is_paused(), "Cancel walks out of the pause")
	assert_eq(ctl.state, BattleController.STATE_COMMAND, "and the command menu has the input again")
	_check(ctl, "pause: resumed", false)
	_free_battle()


func _start_battle() -> void:
	InputDriver.clear_screen()
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ParityHost.scene_root().add_child(ctl)
	ctl.hud.apply_settings(UiSettings.new())
	ctl.start_fixture(BattleFixture.load_fixture(&"player_preview"))
	var guard := 0
	while ctl.current_actor_id() != &"rhen" and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_eq(ctl.state, BattleController.STATE_COMMAND)


func _free_battle() -> void:
	if is_instance_valid(ctl):
		ctl.get_tree().paused = false
		ctl.get_parent().remove_child(ctl)
		ctl.free()
	ctl = null


static func _row_index(page: MenuPage, rid: StringName) -> int:
	for i in page.rows.size():
		if StringName(str(page.rows[i].get("id", ""))) == rid:
			return i
	return -1


## A save from mid-Act I: a stocked bag, a spare piece of gear for Equip, a hurt hero for a tonic, some money.
static func _played_state() -> GameStateData:
	var s := GameStateData.new()
	s.party_ids = ParityHost.HEROES.duplicate()
	s.inventory = {"salt_tonic": 3, "quiet_tea": 2, "crab_carapace": 7, "rhen_coral_hooks": 1, "asha_pearl_bangle": 1}
	s.party_vitals = {"rhen": {"hp": 100}}
	s.currency = 240
	return s


## Every visible text under `root` (and the layers it owns) reads as the pad's, and the focus is on screen.
func _check(root: Node, where: String, needs_back_hint: bool = true) -> void:
	assert_true(InputNames.using_pad, "%s: the pad is the device" % where)
	if needs_back_hint:
		var hint := false
		for t in _visible_texts(root):
			hint = hint or t.contains(BACK_WORD)
		assert_true(hint, "%s: nothing on screen says how to go back" % where)
	for text in _visible_texts(root):
		var open := text.find("{")
		if open >= 0 and text.find("}", open) > open:
			var token := text.substr(open, text.find("}", open) - open + 1)
			if InputMap.has_action(StringName(token.trim_prefix("{").trim_suffix("}"))):
				fail("%s: '%s' left %s unfilled" % [where, text, token])
		if _game_words().has(text):
			continue
		for key_name: String in _key_names:
			if _names_word(text, key_name):
				fail("%s: '%s' names the key %s (%s) after a pad press" % [where, text, key_name, _key_names[key_name]])
	var owner := InputDriver.root().gui_get_focus_owner()
	if owner != null:
		assert_true(
			owner.is_visible_in_tree(), "%s: focus is on %s, which is not on screen" % [where, owner.get_path()]
		)


## Each action's key name where its pad name differs (one-letter names left out: "A" is also a word).
func _collect_key_names() -> void:
	_key_names.clear()
	FieldInput.ensure_actions()
	for action: StringName in InputMap.get_actions():
		if String(action).begins_with("ui_text") or String(action).begins_with("ui_") and not _menu_ui(action):
			continue
		if not InputDriver.has_binding(action, InputDriver.Kind.PAD):
			continue
		var k := InputNames.first_name(action, false)
		var p := InputNames.first_name(action, true)
		if k != "" and k != p and k.length() > 1:
			_key_names[k] = action


func _game_words() -> PackedStringArray:
	var out: PackedStringArray = []
	for k in NOT_KEY_KEYS:
		out.append(tr(k))
	return out


static func _menu_ui(action: StringName) -> bool:
	return action in [&"ui_accept", &"ui_cancel", &"ui_page_up", &"ui_page_down", &"ui_focus_next", &"ui_focus_prev"]


static func _names_word(text: String, word: String) -> bool:
	var at := text.find(word)
	while at >= 0:
		var before := at == 0 or not _is_word_char(text[at - 1])
		var end := at + word.length()
		var after := end >= text.length() or not _is_word_char(text[end])
		if before and after:
			return true
		at = text.find(word, at + 1)
	return false


static func _is_word_char(c: String) -> bool:
	return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or (c >= "0" and c <= "9")


static func _visible_texts(root: Node) -> PackedStringArray:
	var out: PackedStringArray = []
	for n in root.find_children("*", "", true, false):
		if n is Label and (n as Label).is_visible_in_tree():
			out.append((n as Label).text)
		elif n is RichTextLabel and (n as RichTextLabel).is_visible_in_tree():
			out.append((n as RichTextLabel).get_parsed_text())
	return out


func _settle() -> void:
	for n in menu.find_children("*", "", true, false):
		if n.has_method(&"motion") and n.call(&"motion") != null:
			(n.call(&"motion") as MenuMotion).finish()
	ParityHost.end_frame()
