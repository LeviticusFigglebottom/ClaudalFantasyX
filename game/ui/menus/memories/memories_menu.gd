class_name MemoriesMenu
extends FieldSubmenu
## The Memories gallery (M3-MNU-02, SPEC §6.11), opened from the title's Memories row: the chapters
## something is remembered from on the left, each with "2 of 3", and the chosen chapter's
## remembered memories on the right under "2 of 3 remembered". Locked memories are never listed,
## and a chapter nothing is remembered from is not named. Choosing a memory replays it
## (MemoryReplay.start, or `play_memory` in tests). Words and unlocks: MemoriesModel. Layout:
## game/data/ui/memories_menu.json.
##
## Input (keyboard and controller through ui_*): ui_up / ui_down move in the list with the input;
## ui_accept or ui_right go from a chapter into its memories; ui_accept on a memory relives it;
## ui_left or ui_cancel come back to the chapters, and ui_cancel there closes. Mouse: hover a
## chapter to show it, click it to open it; hover a memory to take the cursor there, click it to
## relive it; the wheel steps the list under it; right click is Cancel (UiInput).

signal memory_chosen(memory_id: StringName)

enum Column { CHAPTERS, MEMORIES }

const DATA_PATH := "res://game/data/ui/memories_menu.json"
const DATA_SECTION := "memories_menu"
const CHAPTERS_ID := &"memories_chapters"
const MEMORIES_ID := &"memories_list"

var model: MemoriesModel
var column := Column.CHAPTERS
## Replays a memory: (memory_id: StringName) -> void. Unset = MemoryReplay.start.
var play_memory: Callable = Callable()
## The memory the cursor starts on (the one just replayed), or &"".
var start_on: StringName = &""

var _help: Label
var _chapters: MenuPage
var _list: MenuPage
var _chapter_rows: Array[Dictionary] = []
var _shown: Array[Dictionary] = []
## Set once a memory was chosen: the scene is changing, so nothing else is taken.
var _launched := false


static func create(with_model: MemoriesModel = null, on_memory: StringName = &"") -> MemoriesMenu:
	var menu := MemoriesMenu.new()
	menu.model = with_model
	menu.start_on = on_memory
	return menu


## Opens the gallery on its own CanvasLayer under `host` (null model = the game's records). The
## title does not pause the tree for it (its backdrop keeps moving behind the scrim).
static func open_in(host: Node, with_model: MemoriesModel = null, on_memory: StringName = &"") -> MemoriesMenu:
	var menu := create(with_model, on_memory)
	menu.pause_tree = false
	return FieldSubmenu.mount(menu, host) as MemoriesMenu


func data_path() -> String:
	return DATA_PATH


func data_section() -> String:
	return DATA_SECTION


func chapters_page() -> MenuPage:
	return _chapters


func memories_page() -> MenuPage:
	return _list


func help_text() -> String:
	return _help.text


## The chapter on show (&"" when nothing is remembered).
func current_chapter() -> StringName:
	var row := _chapters.current_row()
	return StringName(str(row.get("id", "")))


## The memory under the cursor (&"" while the chapters have the input).
func current_memory() -> StringName:
	if column != Column.MEMORIES:
		return &""
	return StringName(str(_list.current_row().get("id", "")))


func is_launched() -> bool:
	return _launched


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if _launched:
		return true
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	elif event.is_action_pressed(&"ui_right", true):
		if column == Column.CHAPTERS:
			enter()
	elif event.is_action_pressed(&"ui_left", true):
		if column == Column.MEMORIES:
			back()
	elif event.is_action_pressed(&"ui_cancel"):
		back()
	else:
		return false
	return true


## Confirm: a chapter opens its memories, a memory is relived.
func accept() -> void:
	if column == Column.CHAPTERS:
		enter()
	else:
		choose(current_memory())


## From the chapters into the chapter's memories (nothing when none is remembered).
func enter() -> void:
	if column == Column.MEMORIES or _shown.is_empty():
		return
	column = Column.MEMORIES
	_render()


## Back to the chapters; from the chapters, closes.
func back() -> void:
	if column == Column.CHAPTERS:
		close()
		return
	column = Column.CHAPTERS
	_render()


## Relives memory `id` (it must be listed). Returns true when the replay was started.
func choose(id: StringName) -> bool:
	if _launched or id == &"" or not model.is_unlocked(id):
		return false
	_launched = true
	memory_chosen.emit(id)
	if play_memory.is_valid():
		play_memory.call(id)
	else:
		MemoryReplay.start(id)
	return true


func _build_page() -> void:
	if model == null:
		model = MemoriesModel.from_game()
	_help = _framed_panel(_d.get("panel", {}), tr("MEMORIES_TITLE"))
	_chapters = _menu_page(_d.get("chapters", {}), CHAPTERS_ID, "", 1)
	_chapters.row_hovered.connect(_on_chapter_hovered)
	_chapters.row_clicked.connect(_on_chapter_clicked)
	_list = _menu_page(_d.get("memories", {}), MEMORIES_ID, " ", 1)
	_list.row_hovered.connect(_on_memory_hovered)
	_list.row_clicked.connect(_on_memory_clicked)
	_chapter_rows = model.chapter_rows()
	var rows: Array[Dictionary] = []
	for c in _chapter_rows:
		var right := MemoriesModel.count_text(int(c["found"]), int(c["total"]))
		rows.append({"id": c["id"], "label": tr(str(c["name_key"])), "right": right})
	_chapters.replace_rows(rows)
	_chapters.size.y = MenuPage.height_for(_d.get("chapters", {}), rows.size(), false)
	_start_cursor()
	_render()


## The cursor starts on `start_on` (its chapter, then the memory itself), else the first chapter.
func _start_cursor() -> void:
	var mem := model.memory(start_on) if start_on != &"" else {}
	var at := -1
	for i in _chapter_rows.size():
		if StringName(str(_chapter_rows[i]["id"])) == StringName(str(mem.get("chapter", ""))):
			at = i
	if at < 0 or not model.is_unlocked(start_on):
		_show_chapter(0)
		return
	_chapters.set_cursor(at, false)
	_show_chapter(at)
	for i in _shown.size():
		if StringName(str(_shown[i].get("id", ""))) == start_on:
			_list.set_cursor(i, false)
			column = Column.MEMORIES


func _show_chapter(index: int) -> void:
	if _chapter_rows.is_empty():
		_shown = []
		_list.replace_rows(_shown)
		_list.set_header("")
		return
	var c := _chapter_rows[clampi(index, 0, _chapter_rows.size() - 1)]
	_shown = model.unlocked_in(StringName(str(c["id"])))
	var rows: Array[Dictionary] = []
	for m in _shown:
		rows.append({"id": StringName(str(m.get("id", ""))), "label": tr(str(m.get("title_key", "")))})
	_list.cursor = 0  # a new chapter starts on its first memory
	_list.replace_rows(rows)
	_list.set_header(MemoriesModel.count_text(int(c["found"]), int(c["total"]), true))
	_list.size.y = MenuPage.height_for(_d.get("memories", {}), rows.size(), true)


func _move(delta: int) -> void:
	if column == Column.CHAPTERS:
		if _chapters.move(delta):
			_show_chapter(_chapters.cursor)
			_render()
	else:
		_list.move(delta)


func _render() -> void:
	var on_chapters := column == Column.CHAPTERS
	_chapters.set_dimmed(not on_chapters)
	_list.set_cursor_shown(not on_chapters)
	_help.text = tr("MEMORIES_HELP_CHAPTERS" if on_chapters else "MEMORIES_HELP_MEMORIES")


func _on_chapter_hovered(index: int) -> void:
	if column == Column.CHAPTERS:
		_show_chapter(index)
		_render()


func _on_chapter_clicked(index: int) -> void:
	if not is_open() or _launched:
		return
	if column == Column.MEMORIES:
		column = Column.CHAPTERS
	if _chapters.cursor != index:
		_chapters.set_cursor(index, false)
		_show_chapter(index)
	enter()
	_render()


func _on_memory_hovered(_index: int) -> void:
	if column == Column.CHAPTERS and not _shown.is_empty():
		column = Column.MEMORIES
		_render()


func _on_memory_clicked(index: int) -> void:
	if not is_open() or _launched or index < 0 or index >= _shown.size():
		return
	_list.set_cursor(index, false)
	column = Column.MEMORIES
	_render()
	choose(StringName(str(_shown[index].get("id", ""))))
