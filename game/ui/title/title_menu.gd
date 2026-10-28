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
##   Settings  the Settings hub (SettingsMenu, M2-UI-09): the Graphics page (M1-UI-10) and the
##             Accessibility page; each saves and applies as you change it.
##   Memories  M3-MNU-02: the Memories gallery (MemoriesMenu), only once a memory is remembered
##             (TitleMenuModel.has_memories). A replay comes back here with the gallery open on it
##             (MemoryReplay.take_gallery_request). The page grows upward by a row for it
##             (`choices.anchor_rows`), so the four-row title never moves.
## Input: ui_up / ui_down move, ui_accept chooses (keyboard and controller); hover moves, a click
## chooses; ui_cancel closes the New Game question. It follows UiSettings (text size, palette).
## M2-UI-22: behind the menu, a TitleBackdrop (caustics, light shafts, drifting motes) and the drawn
## TitleLogo; the build label in the corner shows only in debug builds (`shows_version`).
## Layout: game/ui/title/title_menu.json.

signal chosen(choice: StringName, error: int)

const DATA_PATH := "res://game/ui/title/title_menu.json"

## Injected by tests; default to the SaveSystem autoload and SceneRouter.world_return.
var save_system: Node
var world_return: WorldReturn
var model: TitleMenuModel
var load_menu: SaveMenu
var settings_menu: SettingsMenu
var memories_menu: MemoriesMenu
## True in debug builds; tests set it before the menu enters the tree to stand in for a release.
var debug_build := OS.is_debug_build()
var backdrop: TitleBackdrop
var logo: TitleLogo
## The opening reveal (logo, then the choices, then the help line; TitleReveal).
var reveal := TitleReveal.new()

var _d: Dictionary = {}
var _page: MenuPage
var _help: Label
var _version: Label
## Set once a choice has started a scene change, so a second press does nothing.
var _launched := false


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("title_menu")) != TYPE_DICTIONARY:
		push_error("TitleMenu: could not read 'title_menu' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["title_menu"] as Dictionary


## True when the build label shows: always in a debug build, and in a release only if the data's
## `debug_only` is false.
static func shows_version(version_data: Dictionary, debug: bool) -> bool:
	return debug or not bool(version_data.get("debug_only", true))


## The build label's words: project.godot's version, or the data's fallback name when it has none.
static func version_text(version_data: Dictionary) -> String:
	var v := str(ProjectSettings.get_setting("application/config/version", ""))
	if v == "":
		v = str(version_data.get("fallback", ""))
	return TranslationServer.translate("TITLE_BUILD_LABEL") % v


func _ready() -> void:
	Game.stop_play_clock()
	AreaTitleCard.forget()  # M2-UI-21: the next start shows its area title card
	DialogueBacklog.forget()  # M2-UI-25: a new start keeps no earlier run's lines
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_d = load_data()
	if save_system == null:
		save_system = _autoload(&"SaveSystem")
	if world_return == null:
		var router := _autoload(&"SceneRouter")
		world_return = router.get(&"world_return") as WorldReturn if router != null else null
	model = TitleMenuModel.new(save_system)
	UiSettings.shared().follow(self)
	_build()
	UiFrame.centre(self)  # M2-UI-29
	model.changed.connect(_render)
	_render()
	reveal.play(self, logo, _page, _help, _d.get("reveal", {}) as Dictionary)
	# ADR 0111: the hero bodies load on worker threads while the title shows, so New Game's first frame finds
	# them cached. Not in a headless run (tests): nothing draws there, and a load in flight at quit is noise.
	var resident := ResidentLoads.shared()
	if resident != null and DisplayServer.get_name() != "headless":
		resident.warm()
	if MemoryReplay.take_gallery_request() and model.has_memories:
		model.set_cursor(model.row_ids().find(TitleMenuModel.CHOICE_MEMORIES))
		open_memories(MemoryReplay.last_memory)


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the menu used it. Tests call this directly.
func handle_input(event: InputEvent) -> bool:
	if _launched or is_load_menu_open() or is_settings_open() or is_memories_open():
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
			TitleMenuModel.CHOICE_SETTINGS:
				open_settings()
				err = OK
			TitleMenuModel.CHOICE_MEMORIES:
				open_memories()
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


func open_settings() -> SettingsMenu:
	if is_settings_open():
		return settings_menu
	settings_menu = SettingsMenu.new()
	add_child(settings_menu)
	settings_menu.closed.connect(_on_settings_closed)
	return settings_menu


## The Memories gallery, its cursor on `on_memory` when given (the one just replayed).
func open_memories(on_memory: StringName = &"") -> MemoriesMenu:
	if is_memories_open():
		return memories_menu
	memories_menu = MemoriesMenu.open_in(self, MemoriesModel.from_game(save_system), on_memory)
	memories_menu.closed.connect(_on_memories_closed)
	memories_menu.memory_chosen.connect(func(_id: StringName) -> void: _launched = true)
	return memories_menu


func is_memories_open() -> bool:
	return memories_menu != null and is_instance_valid(memories_menu) and memories_menu.is_open()


func is_settings_open() -> bool:
	return settings_menu != null and is_instance_valid(settings_menu) and settings_menu.is_open()


func is_load_menu_open() -> bool:
	return load_menu != null and is_instance_valid(load_menu) and load_menu.is_open()


func is_launched() -> bool:
	return _launched


## The help line as shown (tests and captures read it).
func help_text() -> String:
	return _help.text


func _on_memories_closed() -> void:
	memories_menu = null
	model.refresh()


func _on_load_closed(outcome: SaveMenuModel.Outcome) -> void:
	load_menu = null
	if outcome == SaveMenuModel.Outcome.LOADED:
		_launched = true
	else:
		model.refresh()


## The build label (null in a release build unless the data shows it).
func version_label() -> Label:
	return _version


func _build() -> void:
	backdrop = TitleBackdrop.new()
	add_child(backdrop)
	backdrop.setup(_d.get("backdrop", {}) as Dictionary)
	logo = TitleLogo.new()
	add_child(logo)
	logo.setup(_d.get("logo", {}) as Dictionary)
	_build_page()
	_help = Label.new()
	_help.theme_type_variation = &"HelpDimLabel"
	HudLayout.place(_help, _d.get("help", {}) as Dictionary)
	_help.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_help.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_help.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_help)
	var vd := _d.get("version", {}) as Dictionary
	if shows_version(vd, debug_build):
		_version = Label.new()
		_version.name = &"VersionLabel"
		_version.theme_type_variation = &"DimLabel"
		HudLayout.place(_version, vd)
		_version.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		_version.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		_version.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_version.text = version_text(vd)
		add_child(_version)


## (Re)builds the choice rows; a row's greyed look is fixed when it is built.
func _build_page() -> void:
	if _page != null:
		_page.queue_free()
	var cm := _d.get("choices", {}) as Dictionary
	_page = MenuPage.new()
	var r := HudLayout.rect_of(cm)
	var ids := model.row_ids()
	# Rows past anchor_rows (the Memories row) raise the page, so its foot stays where it was.
	var extra := maxi(ids.size() - int(cm.get("anchor_rows", ids.size())), 0)
	_page.position = r.position - Vector2(0.0, extra * HudLayout.num(cm, "row_pitch"))
	_page.size = Vector2(r.size.x, MenuPage.height_for(cm, ids.size(), false))
	add_child(_page)
	var rows: Array[Dictionary] = []
	for id in ids:
		rows.append({"id": id, "label": tr(model.label_key(id)), "enabled": model.is_enabled(id)})
	_page.reduced_motion = UiSettings.shared().reduced_motion()
	_page.setup(cm, &"title", "", rows)
	_page.row_clicked.connect(_on_row_clicked)
	# Hover moves the model's cursor too, so the help line and the next key press agree (M2-UI-09).
	_page.row_hovered.connect(func(index: int) -> void: model.set_cursor(index))


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


## Back from Settings: the rows are rebuilt in the text size or palette just chosen.
func _on_settings_closed() -> void:
	settings_menu = null
	_build_page()
	_render()


func _on_row_clicked(index: int) -> void:
	if model.set_cursor(index) or model.row_cursor() == index:
		choose(model.accept())


static func _autoload(autoload_name: StringName) -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.root.get_node_or_null(NodePath(String(autoload_name))) if tree != null else null
