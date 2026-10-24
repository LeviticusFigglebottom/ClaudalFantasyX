class_name ReefballDB
extends RefCounted
## Read-only Reefball tables (M3-RBL-01): the rules block, the sides with their divers, and the
## matches, from res://game/data/reefball/ (checked by tools/validate_data.py). Roles and AI
## profiles are indexed by id out of the rules block.

const DATA_DIR := "res://game/data/reefball"
const TABLES: Array[String] = ["rules", "sides", "matches"]

var rules: Dictionary = {}
var sides: Dictionary = {}
var matches: Dictionary = {}
var roles: Dictionary = {}
var ai_profiles: Dictionary = {}
## One line per table that was missing or failed to parse at load_dir (read as empty).
var load_errors: Array[String] = []


static func load_default() -> ReefballDB:
	return load_dir(DATA_DIR)


## Loads every table in TABLES from `dir`. A missing or unparseable table reads as empty, with a
## push_error and a line in load_errors.
static func load_dir(dir: String) -> ReefballDB:
	var raw: Dictionary = {}
	var errors: Array[String] = []
	for table in TABLES:
		var path := "%s/%s.json" % [dir, table]
		var parsed: Variant = null
		if FileAccess.file_exists(path):
			parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
		if typeof(parsed) != TYPE_DICTIONARY:
			push_error("ReefballDB: could not parse %s" % path)
			errors.append("%s is missing or could not be parsed" % path)
			parsed = {}
		raw[table] = (parsed as Dictionary).get(table, {} if table == "rules" else [])
	var db := from_tables(raw)
	db.load_errors = errors
	return db


## Builds a DB from in-memory tables: {rules: {...}, sides: [...], matches: [...]}. Test fixtures use it.
static func from_tables(raw: Dictionary) -> ReefballDB:
	var db := ReefballDB.new()
	db.rules = (raw.get("rules", {}) as Dictionary).duplicate(true)
	db.sides = _index(raw.get("sides", []))
	db.matches = _index(raw.get("matches", []))
	db.roles = _index(db.rules.get("roles", []))
	db.ai_profiles = _index(db.rules.get("ai_profiles", []))
	return db


static func _index(rows: Variant) -> Dictionary:
	var out: Dictionary = {}
	if typeof(rows) != TYPE_ARRAY:
		return out
	for row: Variant in rows:
		if typeof(row) == TYPE_DICTIONARY and (row as Dictionary).has("id"):
			out[StringName(str(row["id"]))] = (row as Dictionary).duplicate(true)
	return out
