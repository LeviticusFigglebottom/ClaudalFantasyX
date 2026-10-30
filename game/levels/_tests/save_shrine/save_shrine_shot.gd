class_name SaveShrineShot
extends Node3D
## Capture driver for the save shrine shots (M1-ARC-03). Puts the player beside the shrine in the
## save-shrine copy of the field test zone and, for the menu shots, writes the fixture slots from
## save_menu_fixtures.json into their own user:// folder, uses the shrine, and (OVERWRITE) asks to
## write over a record. Everything it changes is restored in _exit_tree.

enum View { FIELD, MENU, OVERWRITE }

const FIXTURES_PATH := "res://game/levels/_tests/save_shrine/save_menu_fixtures.json"

@export var view: View = View.FIELD

var zone: Node3D
var shrine: SaveShrine
var fixtures: Dictionary = {}

var _saved_dir := ""
var _saved_clock: Callable
var _saved_autosave := true
var _saved_state: GameStateData


func _ready() -> void:
	fixtures = load_fixtures()
	zone = get_node("Zone") as Node3D
	shrine = zone.get_node("Interactables/SaveShrine") as SaveShrine
	zone.call(&"place_at", StringName(str(fixtures.get("spawn", ""))), float(fixtures.get("spawn_yaw_deg", 0.0)))
	if view == View.FIELD:
		return
	_saved_dir = SaveSystem.save_dir
	_saved_clock = SaveSystem.clock
	_saved_autosave = SaveSystem.autosave_enabled
	_saved_state = Game.state
	Game.state = GameStateData.new()
	SaveSystem.autosave_enabled = false
	write_fixtures(fixtures)
	var menu := shrine.open_menu()
	menu.animate = false
	menu.set_time_zone_bias(int(fixtures.get("time_zone_bias_min", 0)))
	if view == View.OVERWRITE:
		var target := int(fixtures.get("overwrite_slot", 0))
		for i in menu.model.slots.size():
			if menu.model.slots[i].slot == target:
				menu.model.set_cursor(i)
		menu.model.accept()


func _exit_tree() -> void:
	if view == View.FIELD:
		return
	clear_fixtures(fixtures)
	SaveSystem.save_dir = _saved_dir
	SaveSystem.clock = _saved_clock
	SaveSystem.autosave_enabled = _saved_autosave
	Game.state = _saved_state


static func load_fixtures() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(FIXTURES_PATH))
	return parsed as Dictionary if typeof(parsed) == TYPE_DICTIONARY else {}


## Points SaveSystem at the fixture folder and writes every fixture slot (tests use this too).
static func write_fixtures(fx: Dictionary) -> void:
	SaveSystem.save_dir = str(fx.get("save_dir", ""))
	clear_fixtures(fx)
	for s: Dictionary in fx.get("slots", []) as Array:
		var slot := int(s.get("slot", 0))
		if s.has("corrupt"):
			DirAccess.make_dir_recursive_absolute(SaveSystem.save_dir)
			var f := FileAccess.open(SaveSystem.slot_path(slot), FileAccess.WRITE)
			f.store_string(str(s["corrupt"]))
			f.close()
			continue
		var st := GameStateData.new()
		st.chapter = int(s.get("chapter", 0))
		st.location_id = StringName(str(s.get("location_id", "")))
		st.play_time_sec = float(s.get("play_time_sec", 0.0))
		for f: Variant in s.get("flags", []):  # story flags a slot's line reads (Act II: the heresy's tag)
			st.flags[str(f)] = true
		var at := int(s.get("saved_at", 0))
		SaveSystem.clock = func() -> int: return at
		SaveSystem.save_to_slot(slot, st, StringName(str(s.get("reason", ""))))


## Deletes every slot file in the fixture folder, then the folder.
static func clear_fixtures(fx: Dictionary) -> void:
	var dir_path := str(fx.get("save_dir", ""))
	var dir := DirAccess.open(dir_path)
	if dir == null:
		return
	for f in dir.get_files():
		DirAccess.remove_absolute(dir_path.path_join(f))
	DirAccess.remove_absolute(dir_path)
