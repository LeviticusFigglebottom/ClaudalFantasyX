class_name BattleFixture
extends RefCounted
## Frozen battle setups for the HUD capture states and their tests (docs/kb/tech/ui.md § Capture
## fixtures). Data: game/data/ui/battle_fixtures.json, a copy of the sandbox rows that balance
## work never touches, so tuning game/data/battle/*.json cannot move a screenshot baseline.
##
## A fixture names the party, encounter and seed, may deep-merge row overrides by id, and may set
## an opening state (hp, statuses, provoked_by) that prepare() applies after engine.setup() and
## before engine.begin(). That is the only place outside the engine that writes combatant
## state, and only for captures and tests, never in play.

const DATA_PATH := "res://game/data/ui/battle_fixtures.json"

var id: StringName = &""
var db: BattleDB
var active: Array[StringName] = []
var reserve: Array[StringName] = []
var encounter: StringName = &""
var rng_seed := 0
## Combatant id (or base id) -> {hp?, statuses?: [{id, duration}], provoked_by?}.
var opening: Dictionary = {}


static func load_fixture(fixture_id: StringName, path: String = DATA_PATH) -> BattleFixture:
	var root := _root(path)
	var row: Variant = (root.get("fixtures", {}) as Dictionary).get(String(fixture_id))
	if typeof(row) != TYPE_DICTIONARY:
		push_error("BattleFixture: no fixture '%s' in %s" % [fixture_id, path])
		return null
	var spec := row as Dictionary
	var fx := BattleFixture.new()
	fx.id = fixture_id
	fx.db = BattleDB.from_tables(merged_tables(root.get("tables", {}) as Dictionary, spec.get("overrides", {})))
	fx.active = _names(spec.get("active", []))
	fx.reserve = _names(spec.get("reserve", []))
	fx.encounter = StringName(str(spec.get("encounter", "")))
	fx.rng_seed = int(spec.get("seed", 0))
	fx.opening = (spec.get("opening", {}) as Dictionary).duplicate(true)
	return fx


static func fixture_ids(path: String = DATA_PATH) -> Array[StringName]:
	return _names((_root(path).get("fixtures", {}) as Dictionary).keys())


## Deep copy of `tables` ({table: [rows]}) with `overrides` ({table: {row id: partial row}})
## merged into the matching rows (nested Dictionaries merge, everything else replaces).
static func merged_tables(tables: Dictionary, overrides: Variant) -> Dictionary:
	var out := tables.duplicate(true)
	if typeof(overrides) != TYPE_DICTIONARY:
		return out
	for table: Variant in overrides:
		var by_id: Dictionary = (overrides as Dictionary)[table]
		for row: Variant in out.get(table, []):
			var d := row as Dictionary
			if by_id.has(str(d.get("id", ""))):
				_deep_merge(d, by_id[str(d["id"])] as Dictionary)
	return out


## Applies the opening state. Call after engine.setup() and before engine.begin().
func prepare(engine: BattleEngine) -> void:
	for c in engine.party_active + engine.party_reserve + engine.enemies:
		var row: Dictionary = opening.get(String(c.id), opening.get(String(c.id).get_slice("#", 0), {}))
		if row.is_empty():
			continue
		if row.has("hp"):
			c.hp = clampi(int(row["hp"]), 1, c.max_hp)
		for st: Variant in row.get("statuses", []):
			var sd := st as Dictionary
			c.add_status(StringName(str(sd.get("id", ""))), int(sd.get("duration", -1)))
		if row.has("provoked_by"):
			c.provoker_id = StringName(str(row["provoked_by"]))


static func _root(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("battle_fixtures")) != TYPE_DICTIONARY:
		push_error("BattleFixture: could not read 'battle_fixtures' from %s" % path)
		return {}
	return (parsed as Dictionary)["battle_fixtures"] as Dictionary


static func _deep_merge(into: Dictionary, src: Dictionary) -> void:
	for k: Variant in src:
		if typeof(src[k]) == TYPE_DICTIONARY and typeof(into.get(k)) == TYPE_DICTIONARY:
			_deep_merge(into[k] as Dictionary, src[k] as Dictionary)
		else:
			into[k] = src[k]


static func _names(raw: Variant) -> Array[StringName]:
	var out: Array[StringName] = []
	for v: Variant in raw as Array:
		out.append(StringName(str(v)))
	return out
