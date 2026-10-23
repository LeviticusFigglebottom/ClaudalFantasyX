class_name TitleMenu
extends Control
## The minimal title menu (M1-ARC-06): Continue / New Game / Load under the project name in
## boot.tscn. Logic is TitleMenuModel; this is its view (a MenuPage plus a help line, theme and
## loc keys only) and input. The title stops the play clock while it is shown.
##   Continue  TitleSaveEntry.continue_game(): the newest readable record becomes Game.state;
##             EventBus.game_loaded then sends WorldReturn to the respawn point.
##   New Game  Game.new_game() and WorldReturn.go_to(locations.json "new_game"). When slot 0 holds
##             an autosave the new run would write over, it asks first (M1-ARC-08): the rows
##             become Go back / Begin anew, "Go back" is the default, ui_cancel also goes back.
##   Load      the load list (SaveMenu, LOAD mode); a load routes the same way as Continue.
## Input: ui_up / ui_down move, ui_accept chooses (keyboard and controller); a click chooses;
## ui_cancel closes the New Game question.
## Layout: game/ui/title/title_menu.json.

signal chosen(choice: StringName, error: int)

const DATA_PATH := "res://game/ui/title/title_menu.json"

## Injected by tests; default to the SaveSystem autoload and SceneRouter.world_return.
var save_system: Node
var world_return: WorldReturn
var model: TitleMenuModel
var load_menu: SaveMenu

var _d: Dictionary = {}
var _page: MenuPage
var _help: Label
## Set once a choice has started a scene change, so a second press does nothing.
var _launched := false


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("title_menu")) != TYPE_DICTIONARY:
		push_error("TitleMenu: could not read 'title_menu' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["title_menu"] as Dictionary


func _ready() -> void:
	Game.stop_play_clock()
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_d = load_data()
	if save_system == null:
		save_system = _autoload(&"SaveSystem")
	if world_return == null:
		var router := _autoload(&"SceneRouter")
		world_return = router.get(&"world_return") as WorldReturn if router != null else null
	model = TitleMenuModel.new(save_system)
	_build()
	model.changed.connect(_render)
	_render()


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the menu used it. Tests call this directly.
func handle_input(event: InputEvent) -> bool:
	if _launched or is_load_menu_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		model.move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		model.move(1)
	elif event.is_action_pressed(&"ui_accept"):
		choose(model.accept())
	elif event.is_action_pressed(&"ui_cancel") and model.confirming:
		choose(TitleMenuModel.CHOICE_CONFIRM_BACK)
	else:
		return false
	return true


## Runs a choice. Returns OK, or why nothing happened (ERR_UNAVAILABLE for a greyed row or after
## a scene change already started; a load error from Continue). New Game with an autosave at
## risk only opens the question (OK, and `chosen` is not emitted until it is answered); "Begin
## anew" then emits `chosen` as CHOICE_NEW_GAME.
func choose(choice: StringName) -> Error:
	var err: Error = ERR_UNAVAILABLE
	var reported := choice
	if not _launched and choice != &"" and model.is_enabled(choice):
		match choice:
			TitleMenuModel.CHOICE_CONTINUE:
				err = TitleSaveEntry.continue_game(save_system)
				_launched = err == OK
			TitleMenuModel.CHOICE_NEW_GAME:
				if model.needs_new_game_confirm():
					model.begin_confirm()
					return OK
				err = start_new_game()
			TitleMenuModel.CHOICE_CONFIRM_BACK:
				model.end_confirm()
				err = OK
			TitleMenuModel.CHOICE_CONFIRM_BEGIN:
				model.end_confirm()
				reported = TitleMenuModel.CHOICE_NEW_GAME
				err = start_new_game()
			TitleMenuModel.CHOICE_LOAD:
				open_load()
				err = OK
	if err != OK:
		model.refresh()
	chosen.emit(reported, err)
	return err


## A fresh Game.state at locations.json "new_game".
func start_new_game() -> Error:
	if world_return == null:
		return ERR_UNCONFIGURED
	Game.new_game()
	var reg := world_return.registry if world_return.registry != null else LocationRegistry.load_default()
	if not world_return.go_to(reg.new_game_location, reg.new_game_spawn):
		Game.stop_play_clock()
		return ERR_DOES_NOT_EXIST
	_launched = true
	return OK


func open_load() -> SaveMenu:
	if is_load_menu_open():
		return load_menu
	load_menu = TitleSaveEntry.open_load_menu(self, save_system)
	load_menu.closed.connect(_on_load_closed)
	return load_menu


func is_load_menu_open() -> bool:
	return load_menu != null and is_instance_valid(load_menu) and load_menu.is_open()


func is_launched() -> bool:
	return _launched


## The help line as shown (tests and captures read it).
func help_text() -> String:
	return _help.text


func _on_load_closed(outcome: SaveMenuModel.Outcome) -> void:
	load_menu = null
	if outcome == SaveMenuModel.Outcome.LOADED:
		_launched = true
	else:
		model.refresh()


func _build() -> void:
	_build_page()
	_help = Label.new()
	_help.theme_type_variation = &"HelpLabel"
	HudLayout.place(_help, _d.get("help", {}) as Dictionary)
	_help.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_help.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_help.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_help.add_theme_color_override(&"font_color", get_theme_color(&"text_dim", HymnThemeBuilder.PALETTE_TYPE))
	add_child(_help)


## (Re)builds the choice rows; a row's greyed look is fixed when it is built.
func _build_page() -> void:
	if _page != null:
		_page.queue_free()
	var cm := _d.get("choices", {}) as Dictionary
	_page = MenuPage.new()
	var r := HudLayout.rect_of(cm)
	var ids := model.row_ids()
	_page.position = r.position
	_page.size = Vector2(r.size.x, MenuPage.height_for(cm, ids.size(), false))
	add_child(_page)
	var rows: Array[Dictionary] = []
	for id in ids:
		rows.append({"id": id, "label": tr(model.label_key(id)), "enabled": model.is_enabled(id)})
	_page.setup(cm, &"title", "", rows)
	_page.row_clicked.connect(_on_row_clicked)


func _render() -> void:
	if _page_is_stale():
		_build_page()
	_page.set_cursor(model.row_cursor(), is_inside_tree())
	_help.text = tr(model.help_key())


## True when the page shows other rows than the model (the New Game question opened or closed)
## or a row's greyed look is out of date.
func _page_is_stale() -> bool:
	var ids := model.row_ids()
	if _page.rows.size() != ids.size():
		return true
	for i in ids.size():
		if StringName(_page.rows[i]["id"]) != ids[i] or bool(_page.rows[i]["enabled"]) != model.is_enabled(ids[i]):
			return true
	return false


## The labels of the rows shown now (tests read them).
func row_labels() -> Array[String]:
	var out: Array[String] = []
	for row in _page.rows:
		out.append(str(row["label"]))
	return out


func _on_row_clicked(index: int) -> void:
	if model.set_cursor(index) or model.row_cursor() == index:
		choose(model.accept())


static func _autoload(autoload_name: StringName) -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.root.get_node_or_null(NodePath(String(autoload_name))) if tree != null else null
