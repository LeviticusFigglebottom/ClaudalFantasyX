class_name ShrineTravelMenu
extends FieldSubmenu
## The save shrines' travel list (SPEC §6.6, the teleport network; ShrineNetwork, M1-ARC-06): after a rest
## and the save menu, a shrine with other attuned shrines offers to send the party to one. The list names each
## destination by its location (locations.json name_key), in attunement order, with "Stay here" last; choosing
## one asks first (Stay under the cursor). Going closes the page and travels through the location registry
## (SaveShrine.request_teleport: the SceneRouter's own fade, and the destination becomes the respawn point). A
## refused trip (a stand-in location, the router busy) says so and keeps the list open. Layout:
## game/data/ui/shrine_travel.json.
##
## Input: ui_up / ui_down move, ui_accept chooses, ui_cancel stays (or backs out of the confirm). Mouse: hover
## moves, click chooses.

## The party is leaving for `destination` (emitted before the trip, the page already closing).
signal travel_chosen(destination: StringName)

enum Level { LIST, CONFIRM }

const DATA_PATH := "res://game/data/ui/shrine_travel.json"
const ROW_STAY := &"stay"
const ROW_GO := &"go"

var level := Level.LIST
var shrine: SaveShrine
## The attuned shrines on offer (network ids), as SaveShrine.teleport_destinations() gave them.
var destinations: Array[StringName] = []
## The destination being confirmed (&"" on the list).
var picked: StringName = &""
## Sends the party (tests swap it): (destination) -> bool. Defaults to shrine.request_teleport.
var travel: Callable = Callable()

var _rows: MenuPage
var _desc: Label
var _help: Label
var _notice := ""


static func create(from: SaveShrine, offer: Array[StringName]) -> ShrineTravelMenu:
	var menu := ShrineTravelMenu.new()
	menu.shrine = from
	menu.destinations = offer
	return menu


## Opens the page on its own CanvasLayer under `host` (the shrine).
static func open_in(host: Node, from: SaveShrine, offer: Array[StringName]) -> ShrineTravelMenu:
	return FieldSubmenu.mount(create(from, offer), host) as ShrineTravelMenu


func data_path() -> String:
	return DATA_PATH


func data_section() -> String:
	return "shrine_travel"


func rows_page() -> MenuPage:
	return _rows


func desc_text() -> String:
	return _desc.text


## A destination's words: its location's name (the network id when the registry has none).
static func place_name(network_id: StringName) -> String:
	var key := ShrineNetwork.name_key_of(network_id)
	return TranslationServer.translate(key) if key != "" else String(network_id)


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		_move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		_move(1)
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	elif event.is_action_pressed(&"ui_cancel"):
		back()
	else:
		return false
	return true


## Chooses the highlighted row: a destination asks first; Go travels; Stay stays.
func accept() -> void:
	var id := StringName(str(_rows.current_row().get("id", "")))
	if level == Level.CONFIRM:
		if id == ROW_GO:
			go(picked)
		else:
			back()
		return
	if id == ROW_STAY:
		close()
		return
	picked = id
	level = Level.CONFIRM
	_notice = ""
	_show_rows(_confirm_rows(), 0)  # Stay under the cursor


## Backs out of the confirm, or stays.
func back() -> void:
	if level == Level.CONFIRM:
		level = Level.LIST
		var at := maxi(destinations.find(picked), 0)
		picked = &""
		_show_rows(_list_rows(), at)
	else:
		close()


## Travels to `destination`: closes the page first (the router fades the field), then asks the network. A
## refusal reopens the list with why.
func go(destination: StringName) -> bool:
	var send := travel if travel.is_valid() else Callable(shrine, &"request_teleport")
	travel_chosen.emit(destination)
	if send.is_valid() and bool(send.call(destination)):
		close()
		return true
	level = Level.LIST
	picked = &""
	_notice = tr("SHRINE_TRAVEL_REFUSED_FMT").format({"place": place_name(destination)})
	_show_rows(_list_rows(), maxi(destinations.find(destination), 0))
	return false


func _build_page() -> void:
	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dim.color = Color(_c(&"panel_low"), HudLayout.num(_d, "dim_alpha"))
	add_child(dim)
	_help = _framed_panel(_d.get("panel", {}), tr("SHRINE_TRAVEL_TITLE"))
	var rm: Dictionary = _d.get("rows", {})
	_rows = _menu_page(rm, &"shrine_travel", "", int(HudLayout.num(rm, "max_rows")))
	_rows.row_hovered.connect(func(_i: int) -> void: _render())
	_rows.row_clicked.connect(_on_clicked)
	var em: Dictionary = _d.get("desc", {})
	var top := _rows.position.y + _rows.size.y + HudLayout.num(em, "gap")
	_desc = _label(
		&"BodyLabel", Rect2(Vector2(_rows.position.x, top), Vector2(_rows.size.x, HudLayout.num(em, "height")))
	)
	_desc.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_show_rows(_list_rows(), 0)


func _list_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for nid in destinations:
		# A dark Order shrine stays on the list, greyed, saying why (heresy.md section 1).
		var dark := ShrineNetwork.is_dark(nid)
		(
			out
			. append(
				{
					"id": nid,
					"label": place_name(nid),
					"right": tr("SHRINE_TRAVEL_DARK") if dark else "",
					"right_role": &"text_dim",
					"enabled": not dark,
				}
			)
		)
	out.append({"id": ROW_STAY, "label": tr("SHRINE_TRAVEL_STAY"), "enabled": true})
	return out


func _confirm_rows() -> Array[Dictionary]:
	return [
		{"id": ROW_STAY, "label": tr("SHRINE_TRAVEL_STAY"), "enabled": true},
		{"id": ROW_GO, "label": tr("SHRINE_TRAVEL_GO"), "enabled": true},
	]


func _show_rows(rows: Array[Dictionary], cursor: int) -> void:
	_rows.replace_rows(rows)
	_rows.set_cursor(cursor, false)
	_render()


func _move(delta: int) -> void:
	if _rows.move(delta):
		_render()


func _render() -> void:
	var id := StringName(str(_rows.current_row().get("id", "")))
	if level == Level.CONFIRM:
		var place := place_name(picked)
		_desc.text = (
			tr("SHRINE_TRAVEL_CONFIRM_FMT").format({"place": place}) if id == ROW_GO else tr("SHRINE_TRAVEL_STAY_DESC")
		)
		_help.text = tr("SHRINE_TRAVEL_HELP_CONFIRM")
	else:
		var line := (
			tr("SHRINE_TRAVEL_STAY_DESC")
			if id == ROW_STAY
			else tr("SHRINE_TRAVEL_DEST_FMT").format({"place": place_name(id)})
		)
		_desc.text = _notice if _notice != "" else line
		_help.text = tr("SHRINE_TRAVEL_HELP")
	_desc.add_theme_color_override(&"font_color", _c(&"danger") if _notice != "" else _c(&"text"))
	var pm: Dictionary = _d.get("panel", {})
	UiFrame.fit_line(_help, HudLayout.rect_of(pm).size.x - HudLayout.num(pm, "pad") * 2.0)


func _on_clicked(index: int) -> void:
	if not is_open():
		return
	_rows.set_cursor(index, false)
	accept()
