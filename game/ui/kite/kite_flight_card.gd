class_name KiteFlightCard
extends CanvasLayer
## The Kite's flight card (M5-A3P-1711; SPEC §6.6): while the scene changes after Fly, "The Kite" over "Bound for
## {place}" and the region, on the black of the router's fade. It hangs under the SceneRouter so the change doesn't
## free it, and its opacity follows the fade: up as the screen goes black, down as the new place comes in. It goes
## once the fade has covered and lifted again, or after max_sec. It takes no input. Data:
## game/data/ui/kite_flight.json.

const DATA_PATH := "res://game/data/ui/kite_flight.json"

var data: Dictionary = {}
## The fade's alpha now: Callable() -> float. Unset: the SceneRouter's (none: 1, fully covered).
var fade: Callable = Callable()

var _root: Control
var _line: Label
var _region: Label
var _covered := false
var _t := 0.0


## Puts up the card for `place` in `region` under the router (or `host` when there is none).
static func launch(host: Node, place: String, region: String) -> KiteFlightCard:
	var card := KiteFlightCard.new()
	card.data = load_data()
	var router := host.get_tree().root.get_node_or_null(^"SceneRouter") if host.is_inside_tree() else null
	if router != null:
		card.fade = Callable(router, &"fade_alpha")
	(router if router != null else host).add_child(card)
	card.set_place(place, region)
	return card


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if not parsed is Dictionary or not (parsed as Dictionary).get("kite_flight") is Dictionary:
		push_error("KiteFlightCard: could not read 'kite_flight' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["kite_flight"] as Dictionary


func _ready() -> void:
	if data.is_empty():
		data = load_data()
	layer = int(data.get("canvas_layer", 1))
	_build()
	advance(0.0)


func _process(delta: float) -> void:
	advance(delta)


## Names the place the Kite is bound for.
func set_place(place: String, region: String) -> void:
	if _line == null:
		_build()
	_line.text = tr("KITE_FLIGHT_BOUND_FMT").format({"place": place})
	_region.text = region if region != place else ""


func line_text() -> String:
	return _line.text


func region_text() -> String:
	return _region.text


## The card's opacity now.
func alpha() -> float:
	return _root.modulate.a


## Steps the card by `delta` seconds: its opacity follows the fade, and it goes once the fade has come and gone.
func advance(delta: float) -> void:
	if _root == null or is_queued_for_deletion():
		return
	_t += delta
	var a := float(fade.call()) if fade.is_valid() else 1.0
	_root.modulate.a = clampf(a, 0.0, 1.0)
	if a >= float(data.get("covered_alpha", 1.0)):
		_covered = true
	var lifted := _covered and a <= float(data.get("lifted_alpha", 0.0))
	if lifted or _t >= float(data.get("max_sec", 0.0)):
		queue_free()


func _build() -> void:
	if _root != null:
		return
	_root = Control.new()
	_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root)
	UiSettings.shared().follow(_root)
	var r := HudLayout.rect_of(data)
	var y := r.position.y
	var title := _label(&"TitleLabel", Rect2(r.position.x, y, r.size.x, HudLayout.num(data, "title_height")))
	title.text = tr("KITE_TITLE")
	y += title.size.y
	_line = _label(&"BannerLabel", Rect2(r.position.x, y, r.size.x, HudLayout.num(data, "line_height")))
	y += _line.size.y
	_region = _label(&"HelpDimLabel", Rect2(r.position.x, y, r.size.x, HudLayout.num(data, "region_height")))
	UiFrame.centre(_root)


func _label(variation: StringName, rect: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.position = rect.position
	l.size = rect.size
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(l)
	return l
