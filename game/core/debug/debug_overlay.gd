class_name DebugOverlay
extends CanvasLayer
## Debug overlays F1–F12 (SPEC §5.4, M1-ARC-02). Debug builds only: boot.gd instances this scene
## by path under the tree root when OS.is_debug_build(), so nothing in release references it and
## the export filter can drop game/core/debug/ entirely (docs/kb/tech/architecture.md).
##
## Pages (bindings in game/data/debug/debug_overlay.json, added to the InputMap at runtime):
##   F1 help · F2 turn-order internals · F3 encounter rate · F4 flag inspector (Enter toggles a
##   bool) · F5 teleport (Enter goes) · F6 Lattice cheat (Enter grants) · F7 field camera ·
##   F9 battle sandbox · F12 hide. Pressing a page's key again hides the overlay.
## Lists move with ui_up / ui_down and act with ui_accept, only on list pages ("list": true in the
## data: flags, teleport, Lattice). Every other page lets those keys through to the game, so F2 and
## F7 can stay open while playing (M1-ARC-05).
## All logic lives in DebugReadouts / DebugHooks; this node only routes input and draws text.

signal page_changed(page_id: StringName)

const SCENE_PATH := "res://game/core/debug/debug_overlay.tscn"
const NODE_NAME := "DebugOverlay"
const PAGE_NONE := &""
const PAGE_HELP := &"help"
const PAGE_TURN_ORDER := &"turn_order"
const PAGE_ENCOUNTERS := &"encounters"
const PAGE_FLAGS := &"flags"
const PAGE_TELEPORT := &"teleport"
const PAGE_LATTICE := &"lattice"
const PAGE_CAMERA := &"camera"
const ACTION_SANDBOX := &"debug_battle_sandbox"
const ACTION_HIDE := &"debug_overlay_hide"
const MONO_FONTS: PackedStringArray = ["monospace", "DejaVu Sans Mono", "Consolas", "Menlo"]
const CURSOR := "> "
const NO_CURSOR := "  "

var cfg: Dictionary = {}
var page: StringName = PAGE_NONE
var selection := 0
var last_message := ""

var _pages: Array[Dictionary] = []
var _teleports: Array[Dictionary] = []
var _refresh_left := 0.0
var _pending_spawn: StringName = &""
var _global_actions: Dictionary = {}
var _list_actions: Dictionary = {}
var _list_pages: Dictionary = {}

@onready var _panel: PanelContainer = $Panel
@onready var _title: Label = $Panel/Margin/Rows/Title
@onready var _body: Label = $Panel/Margin/Rows/Body


## Instances the overlay under `root` once (debug builds only). Returns it, or null in release.
static func install(root: Node) -> DebugOverlay:
	if not OS.is_debug_build():
		return null
	var existing := root.get_node_or_null(NODE_NAME) as DebugOverlay
	if existing != null:
		return existing
	var overlay := (load(SCENE_PATH) as PackedScene).instantiate() as DebugOverlay
	overlay.name = NODE_NAME
	root.add_child(overlay)
	return overlay


func _ready() -> void:
	cfg = DebugReadouts.config()
	FieldInput.add_actions(cfg.get("actions", {}) as Dictionary, float(cfg.get("deadzone", 0.0)))
	for p: Variant in cfg.get("pages", []):
		_pages.append(p as Dictionary)
	_teleports = DebugReadouts.teleports(str(cfg.get("teleports_path", "")))
	_build_action_tables()
	layer = int(cfg.get("layer", layer))
	_style()
	close()


func _process(delta: float) -> void:
	if page == PAGE_NONE:
		return
	_refresh_left -= delta
	if _refresh_left <= 0.0:
		refresh()


func _input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Routes one event. Returns true when the overlay consumed it.
func handle_input(event: InputEvent) -> bool:
	if not event.is_pressed() or event.is_echo():
		return false
	var handler := _handler_for(event)
	if handler.is_valid():
		handler.call()
	return handler.is_valid()


## The action an event triggers: page keys and F9/F12 always, list keys only on a list page.
func _handler_for(event: InputEvent) -> Callable:
	var tables: Array[Dictionary] = [_global_actions]
	if is_list_page(page):
		tables.append(_list_actions)
	for table in tables:
		for action: StringName in table:
			if event.is_action_pressed(action):
				return table[action]
	return Callable()


func _build_action_tables() -> void:
	for p in _pages:
		_global_actions[StringName(str(p["action"]))] = toggle_page.bind(StringName(str(p["id"])))
		if bool(p.get("list", false)):
			_list_pages[StringName(str(p["id"]))] = true
	_global_actions[ACTION_SANDBOX] = launch_battle_sandbox
	_global_actions[ACTION_HIDE] = close
	_list_actions = {&"ui_up": move_selection.bind(-1), &"ui_down": move_selection.bind(1), &"ui_accept": activate}


func toggle_page(id: StringName) -> void:
	if page == id:
		close()
	else:
		open_page(id)


func open_page(id: StringName) -> void:
	page = id
	selection = 0
	last_message = ""
	_panel.visible = true
	refresh()
	page_changed.emit(page)


func close() -> void:
	page = PAGE_NONE
	if _panel != null:
		_panel.visible = false
	page_changed.emit(page)


func is_open() -> bool:
	return page != PAGE_NONE


## True for pages that take the list keys (ui_up / ui_down / ui_accept).
func is_list_page(id: StringName) -> bool:
	return _list_pages.has(id)


func move_selection(step: int) -> void:
	var n := _row_count()
	if n > 0:
		selection = posmod(selection + step, n)
	refresh()


## Enter on the current page: toggle a flag, teleport, or apply the Lattice cheat.
func activate() -> void:
	match page:
		PAGE_FLAGS:
			var rows := DebugReadouts.flag_rows()
			if selection < rows.size():
				var f: StringName = rows[selection]["name"]
				var ok := DebugReadouts.toggle_flag(f)
				last_message = ("%s -> %s" % [f, Game.get_flag(f)]) if ok else ("%s is not a bool" % f)
		PAGE_TELEPORT:
			if selection < _teleports.size():
				teleport(_teleports[selection])
		PAGE_LATTICE:
			var r := DebugReadouts.apply_lattice_cheat(DebugHooks.lattice_source(get_tree()), _lattice_cfg())
			last_message = "granted: %s; facets %s" % [r["characters"], r["facets"]]
	refresh()


## Goes to a teleport entry through SceneRouter; the spawn reaches the new root's place_at().
func teleport(entry: Dictionary) -> bool:
	if SceneRouter.is_busy():
		last_message = "SceneRouter busy"
		return false
	_pending_spawn = entry.get("spawn", &"")
	if _pending_spawn != &"" and not EventBus.scene_changed.is_connected(_on_scene_changed):
		EventBus.scene_changed.connect(_on_scene_changed, CONNECT_ONE_SHOT)
	last_message = "teleport -> %s" % entry["label"]
	close()
	SceneRouter.change_scene(str(entry["scene"]))
	return true


func launch_battle_sandbox() -> bool:
	if SceneRouter.is_busy():
		return false
	close()
	SceneRouter.change_scene(str(cfg.get("battle_sandbox_scene", "")))
	return true


## Re-renders the open page now.
func refresh() -> void:
	_refresh_left = float(cfg.get("refresh_sec", 0.0))
	if page == PAGE_NONE or _title == null:
		return
	_title.text = _page_title(page)
	var lines := render_page(page)
	if last_message != "":
		lines.append("")
		lines.append(last_message)
	_body.text = "\n".join(lines)


## The text of a page (what the overlay draws), for tests and for the panel.
func render_page(id: StringName) -> PackedStringArray:
	var tree := get_tree()
	var lines := PackedStringArray()
	match id:
		PAGE_TURN_ORDER:
			lines = DebugReadouts.turn_order_lines(
				DebugHooks.battle_engine(tree), int(cfg.get("turn_order_preview", 0))
			)
		PAGE_ENCOUNTERS:
			lines = DebugReadouts.encounter_lines(DebugHooks.encounter_provider(tree))
		PAGE_FLAGS:
			lines = _list_lines(_flag_lines())
		PAGE_TELEPORT:
			var labels := PackedStringArray()
			for t in _teleports:
				labels.append("%-16s %s" % [t["id"], t["label"]])
			lines = _list_lines(labels)
		PAGE_LATTICE:
			lines = DebugReadouts.lattice_lines(DebugHooks.lattice_source(tree), _lattice_cfg())
		PAGE_CAMERA:
			lines = DebugReadouts.camera_lines(DebugHooks.camera_director(tree))
		_:
			lines = _help_lines()
	return lines


func teleport_entries() -> Array[Dictionary]:
	return _teleports


func _flag_lines() -> PackedStringArray:
	var out := PackedStringArray()
	for r in DebugReadouts.flag_rows():
		var v: Variant = r["value"]
		out.append("%-30s %-7s %s" % [r["name"], "unset" if v == null else str(v), r["description"]])
	return out


## A scrolling window of `rows` around the selection, with a cursor.
func _list_lines(rows: PackedStringArray) -> PackedStringArray:
	var out := PackedStringArray()
	if rows.is_empty():
		out.append("(empty)")
		return out
	var window := int(cfg.get("list_window_rows", rows.size()))
	var first := clampi(selection - window / 2, 0, maxi(rows.size() - window, 0))
	for i in range(first, mini(first + window, rows.size())):
		out.append((CURSOR if i == selection else NO_CURSOR) + rows[i])
	return out


func _help_lines() -> PackedStringArray:
	var out := PackedStringArray()
	for p in _pages:
		out.append("%-26s %s" % [_keys_for(StringName(str(p["action"]))), p["title"]])
	out.append("%-26s battle sandbox" % _keys_for(ACTION_SANDBOX))
	out.append("%-26s hide" % _keys_for(ACTION_HIDE))
	out.append("list pages: ui_up / ui_down move, ui_accept acts; other pages pass those keys to the game")
	return out


func _row_count() -> int:
	match page:
		PAGE_FLAGS:
			return DebugReadouts.flag_rows().size()
		PAGE_TELEPORT:
			return _teleports.size()
	return 0


func _page_title(id: StringName) -> String:
	for p in _pages:
		if StringName(str(p["id"])) == id:
			return str(p["title"])
	return String(id)


func _keys_for(action: StringName) -> String:
	if not InputMap.has_action(action):
		return "-"
	var names := PackedStringArray()
	for ev in InputMap.action_get_events(action):
		names.append(ev.as_text())
	return ", ".join(names)


func _lattice_cfg() -> Dictionary:
	return cfg.get("lattice_cheat", {}) as Dictionary


func _on_scene_changed(_path: String) -> void:
	var root := get_tree().current_scene
	if _pending_spawn != &"" and root != null and root.has_method(&"place_at"):
		root.call(&"place_at", _pending_spawn)
	_pending_spawn = &""


func _style() -> void:
	var margin := int(cfg.get("panel_margin_px", 0))
	_panel.position = Vector2(margin, margin)
	_panel.custom_minimum_size.x = float(cfg.get("panel_width_px", 0))
	var box := StyleBoxFlat.new()
	box.bg_color = Color.html(str(cfg.get("background", "#000000")))
	_panel.add_theme_stylebox_override(&"panel", box)
	var mono := SystemFont.new()
	mono.font_names = MONO_FONTS
	var size := int(cfg.get("font_size", 0))
	var text_color := Color.html(str(cfg.get("text_color", "#FFFFFF")))
	for l: Label in [_title, _body]:
		l.add_theme_font_override(&"font", mono)
		l.add_theme_font_size_override(&"font_size", size)
		l.add_theme_color_override(&"font_color", text_color)
	_title.add_theme_color_override(&"font_color", Color.html(str(cfg.get("highlight_color", "#FFFFFF"))))
