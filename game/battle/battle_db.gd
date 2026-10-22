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


static func load_default() -> BattleDB:
	var raw: Dictionary = {}
	for table in TABLES:
		var path := "%s/%s.json" % [DATA_DIR, table]
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		if typeof(parsed) != TYPE_DICTIONARY:
			push_error("BattleDB: could not parse %s" % path)
			parsed = {}
		raw[table] = (parsed as Dictionary).get(table, [])
	return from_tables(raw)


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
