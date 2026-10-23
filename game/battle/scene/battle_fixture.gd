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
## The battle's opening (BattleOpening: preemptive or ambush; &"" = normal), so a capture can show
## the opening banner without a roll (M2-UI-02). "battle_opening" in the fixture row.
var battle_opening: StringName = &""


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
	fx.battle_opening = StringName(str(spec.get("battle_opening", "")))
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
## Applies the opening state through the engine (M1-CMB-06): UI code never writes combatant state.
func prepare(engine: BattleEngine) -> void:
	engine.apply_fixture(opening)
	if BattleOpening.OPENINGS.has(battle_opening):
		engine.opening = battle_opening


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
