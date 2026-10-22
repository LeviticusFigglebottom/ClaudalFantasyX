class_name LatticeRules
extends RefCounted
## Board rules and Facet types (SPEC §6.4), loaded from game/data/progression/facets.json.
## Answers "which Facet item activates this node, and how many?".

const DEFAULT_PATH := "res://game/data/progression/facets.json"
const ACTIVATES_STAT := &"stat"
const ACTIVATES_ABILITY := &"ability"
const ACTIVATES_GATE := &"gate"

## Movement-point cost to step onto a node nobody has activated, and onto one that someone has.
var move_cost: int = 0
var move_cost_activated: int = 0
var facets_per_activation: int = 0
var keys_per_gate: int = 0
var max_gate_level: int = 0
## Facet item id -> its row in facets.json.
var facets: Dictionary = {}
var _stat_facet: Dictionary = {}
var _ability_facet: StringName = &""
var _key_facet: Dictionary = {}


static func load_file(path: String = DEFAULT_PATH) -> LatticeRules:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("LatticeRules: could not parse %s" % path)
		return LatticeRules.new()
	return from_dict(parsed as Dictionary)


static func from_dict(d: Dictionary) -> LatticeRules:
	var r := LatticeRules.new()
	var rules: Dictionary = d.get("rules", {})
	r.move_cost = int(rules.get("move_cost", 0))
	r.move_cost_activated = int(rules.get("move_cost_activated", 0))
	r.facets_per_activation = int(rules.get("facets_per_activation", 0))
	r.keys_per_gate = int(rules.get("keys_per_gate", 0))
	r.max_gate_level = int(rules.get("max_gate_level", 0))
	for row: Variant in d.get("facets", []):
		var f: Dictionary = row
		var fid := StringName(str(f.get("id", "")))
		r.facets[fid] = f
		match StringName(str(f.get("activates", ""))):
			ACTIVATES_STAT:
				for s: Variant in f.get("stats", []):
					r._stat_facet[StringName(str(s))] = fid
			ACTIVATES_ABILITY:
				r._ability_facet = fid
			ACTIVATES_GATE:
				r._key_facet[int(f.get("level", 0))] = fid
	return r


## The Facet item id that activates (stat/ability) or opens (gate) this node; &"" if none can.
func facet_for(node: LatticeNode) -> StringName:
	if node == null:
		return &""
	match node.kind:
		LatticeNode.KIND_STAT:
			return _stat_facet.get(node.stat, &"")
		LatticeNode.KIND_ABILITY:
			return _ability_facet
		LatticeNode.KIND_GATE:
			return _key_facet.get(node.gate_level, &"")
	return &""


## How many of facet_for(node) one activation or gate opening consumes.
func facet_cost(node: LatticeNode) -> int:
	if node != null and node.is_gate():
		return keys_per_gate
	return facets_per_activation


func facet_name_key(facet_id: StringName) -> String:
	return str((facets.get(facet_id, {}) as Dictionary).get("name_key", ""))
