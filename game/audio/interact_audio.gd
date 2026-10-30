class_name InteractAudio
extends Node
## A field object's own sound when it is used (M3-AUD-864, the Act I foley detail pass; interact_sfx.json). **Listens
## only**: every Interactable's `used`, by its zone's location and its id ("ch01/oruvel:lashing_a"), else its id
## alone, plays that row at the object, over the menu's soft `ui_interact` touch (ui_sfx.json). Objects whose use
## opens a cutscene or a trial are voiced there and have no row here.

## Plays a row at a place: (id: StringName, at: Vector3) -> void.
var player_at: Callable = Callable()
var data: Dictionary = {}
## Every row played, in order: [interactable key, sfx id] (tests).
var played: Array = []


func _init(table: Dictionary = {}) -> void:
	data = table


func bind_director(dir: AudioDirector) -> void:
	player_at = func(id: StringName, at: Vector3) -> void: dir.play_sfx_at(id, at)


## Connects `area`'s `used` (once).
func watch(area: Node) -> void:
	if not is_instance_valid(area) or not area.has_signal(&"used"):
		return
	if area.has_meta(&"interact_audio"):
		return
	area.set_meta(&"interact_audio", true)
	area.connect(&"used", func(_a: Variant) -> void: on_used(area))


## The row for `area`: by "<location>:<id>", else by its id ("" when it has none).
func row_for(area: Node) -> String:
	var rows := data.get("by_id", {}) as Dictionary
	var id := str(area.get(&"id"))
	var loc := location_of(area)
	if loc != "" and rows.has("%s:%s" % [loc, id]):
		return str(rows["%s:%s" % [loc, id]])
	return str(rows.get(id, ""))


## The location id of the zone `area` sits in (the nearest ancestor with a `location_id`), else "".
static func location_of(area: Node) -> String:
	var n := area.get_parent()
	while n != null:
		var loc: Variant = n.get(&"location_id")
		if loc != null and str(loc) != "":
			return str(loc)
		n = n.get_parent()
	return ""


func on_used(area: Node) -> void:
	var row := row_for(area)
	if row == "":
		return
	played.append([str(area.get(&"id")), StringName(row)])
	if player_at.is_valid():
		var at := (area as Node3D).global_position if area is Node3D and area.is_inside_tree() else Vector3.ZERO
		player_at.call(StringName(row), at + Vector3.UP * float(data.get("height_m", 0.0)))
