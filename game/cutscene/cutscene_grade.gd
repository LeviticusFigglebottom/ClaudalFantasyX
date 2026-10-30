class_name CutsceneGrade
extends RefCounted
## M2-FP-120: a cutscene's grade, the colour script's sub-frame (docs/kb/art/color_script.md) as a look. A scene's
## `grade:` header applies as its node starts, and `@camera <shot> grade=<id>` as the cut lands. The looks are the
## zones' own grade tables (assets/environments/zones/<zone>/<zone>_grades.json, ADR 0200: an Environment and the
## sun it wants), so a cutscene and a zone's light rows share one source. Applying swaps a copy of the row's
## Environment onto the stage level's WorldEnvironment and sets its sun (energy, colour, pitch and yaw, as the zones'
## light rows do); restore() puts both back at the scene's end. A grade with no row is a soft failure: the colour
## script names grades nobody has built yet (M3-ENV-106), and test_cutscene_directives lists them.

const ZONES_DIR := "res://assets/environments/zones"
const TABLE_SUFFIX := "_grades.json"
const KEY_ENVIRONMENT := "environment"
const KEY_SUN := "sun"

static var _table: Dictionary = {}
static var _loaded := false
static var _missed: Dictionary = {}

## The grade on now (&"" for the level's own look).
var active: StringName = &""
var _world_env: WorldEnvironment
var _sun: DirectionalLight3D
var _saved_env: Environment
var _saved_sun: Array = []


## Every grade row in the zones' tables, by id (loaded once).
static func table() -> Dictionary:
	if _loaded:
		return _table
	_loaded = true
	for zone in DirAccess.get_directories_at(ZONES_DIR):
		var dir := "%s/%s" % [ZONES_DIR, zone]
		for f in DirAccess.get_files_at(dir):
			if not f.ends_with(TABLE_SUFFIX):
				continue
			var data: Variant = JSON.parse_string(FileAccess.get_file_as_string("%s/%s" % [dir, f]))
			if typeof(data) != TYPE_DICTIONARY:
				continue
			for id: String in data as Dictionary:
				var row: Variant = data[id]
				if not id.begins_with("_") and typeof(row) == TYPE_DICTIONARY:
					_table[StringName(id)] = row
	return _table


static func has_grade(id: StringName) -> bool:
	return table().has(id)


## Puts grade `id` on the level that holds `stage`. False (and nothing changes) when no row has it, or the level
## has no WorldEnvironment.
func apply(stage: Node, id: StringName) -> bool:
	if id == active:
		return true
	var row: Dictionary = table().get(id, {})
	if row.is_empty() and not _missed.has(id):
		_missed[id] = true
		# Not a warning: test_cutscene_directives' known list tracks the grades Rendering hasn't built (M3-ENV-106).
		print_verbose("CutsceneGrade: no grade '%s' in the zones' grade tables yet" % id)
	var env := load(str(row.get(KEY_ENVIRONMENT, ""))) as Environment if row.has(KEY_ENVIRONMENT) else null
	if env == null or not _find(stage):
		return false
	if _saved_env == null:
		_saved_env = _world_env.environment
		if _sun != null:
			_saved_sun = [_sun.light_energy, _sun.light_color, _sun.rotation_degrees]
	_world_env.environment = env.duplicate()
	var sun_row: Dictionary = row.get(KEY_SUN, {})
	if _sun != null and not sun_row.is_empty():
		_sun.light_energy = float(sun_row.get("energy", _sun.light_energy))
		_sun.light_color = Color.html(str(sun_row.get("color", _sun.light_color.to_html())))
		_sun.rotation_degrees = Vector3(
			float(sun_row.get("pitch_deg", _sun.rotation_degrees.x)),
			float(sun_row.get("yaw_deg", _sun.rotation_degrees.y)),
			0.0
		)
	active = id
	return true


## The level's own look back (the scene's end).
func restore() -> void:
	if _saved_env != null and is_instance_valid(_world_env):
		_world_env.environment = _saved_env
	if not _saved_sun.is_empty() and is_instance_valid(_sun):
		_sun.light_energy = float(_saved_sun[0])
		_sun.light_color = _saved_sun[1]
		_sun.rotation_degrees = _saved_sun[2]
	_saved_env = null
	_saved_sun = []
	active = &""


## The stage level's WorldEnvironment and sun (a DirectionalLight3D named Sun, else the first one).
func _find(stage: Node) -> bool:
	if _world_env != null and is_instance_valid(_world_env):
		return true
	var level: Node = stage.owner if stage != null and stage.owner != null else stage
	if level == null:
		return false
	var envs := level.find_children("*", "WorldEnvironment", true, false)
	if envs.is_empty():
		return false
	_world_env = envs[0] as WorldEnvironment
	var suns := level.find_children("*", "DirectionalLight3D", true, false)
	for s: Node in suns:
		if s.name == &"Sun":
			_sun = s as DirectionalLight3D
	if _sun == null and not suns.is_empty():
		_sun = suns[0] as DirectionalLight3D
	return true
