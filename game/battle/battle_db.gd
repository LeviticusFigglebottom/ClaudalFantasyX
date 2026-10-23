class_name BattleDB
extends RefCounted
## Read-only battle data tables (skills, statuses, enemies, characters, encounters), indexed
## by id. Source files live in res://game/data/battle/ and are checked by tools/validate_data.py.

const DATA_DIR := "res://game/data/battle"
const TABLES: Array[String] = ["skills", "statuses", "enemies", "characters", "encounters"]

var skills: Dictionary = {}
var statuses: Dictionary = {}
var enemies: Dictionary = {}
var characters: Dictionary = {}
var encounters: Dictionary = {}
## One line per table that was missing or failed to parse at load_dir (read as empty).
var load_errors: Array[String] = []
## The same lines by table name ("enemies" -> why), for checks that judge one table.
var table_errors: Dictionary = {}


static func load_default() -> BattleDB:
	return load_dir(DATA_DIR)


## Loads every table in TABLES from `dir`. A missing or unparseable table is read as empty, with a
## push_error and a line in load_errors (M1-ARC-13). Tests point it at a folder with a broken one.
static func load_dir(dir: String) -> BattleDB:
	var raw: Dictionary = {}
	var errors: Array[String] = []
	var by_table: Dictionary = {}
	for table in TABLES:
		var path := "%s/%s.json" % [dir, table]
		var parsed: Variant = null
		if FileAccess.file_exists(path):
			parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
		if typeof(parsed) != TYPE_DICTIONARY:
			push_error("BattleDB: could not parse %s" % path)
			errors.append("%s is missing or could not be parsed" % path)
			by_table[table] = errors[-1]
			parsed = {}
		raw[table] = (parsed as Dictionary).get(table, [])
	var db := from_tables(raw)
	db.load_errors = errors
	db.table_errors = by_table
	return db


## Why this DB must not judge saved party state ("" when it can): a table failed to load, or there
## are no characters (party_ids, reserve_ids, party_vitals) or no statuses (carried statuses).
## SaveSystem's data-tables gate refuses to save while it is non-empty (M1-ARC-13).
func integrity_problem() -> String:
	if not load_errors.is_empty():
		return "; ".join(load_errors)
	if characters.is_empty() or statuses.is_empty():
		return "the battle tables have no characters or no statuses"
	return ""


## Why the bestiary log must not be judged against enemies.json ("" when it can): the table
## failed to load, or it lists no enemies (M1-CMB-03, the data-tables gate's `bestiary` check).
func enemies_problem() -> String:
	if table_errors.has("enemies"):
		return str(table_errors["enemies"])
	if enemies.is_empty():
		return "the battle tables list no enemies"
	return ""


## Builds a DB from {table_name: [rows with "id"]}. Tests use this to inject fixtures.
static func from_tables(raw: Dictionary) -> BattleDB:
	var db := BattleDB.new()
	db.skills = _index(raw.get("skills", []))
	db.statuses = _index(raw.get("statuses", []))
	db.enemies = _index(raw.get("enemies", []))
	db.characters = _index(raw.get("characters", []))
	db.encounters = _index(raw.get("encounters", []))
	return db


func skill(skill_id: StringName) -> Dictionary:
	return skills.get(skill_id, {})


static func _index(rows: Array) -> Dictionary:
	var out: Dictionary = {}
	for row: Variant in rows:
		var d: Dictionary = row
		out[StringName(str(d["id"]))] = d
	return out
