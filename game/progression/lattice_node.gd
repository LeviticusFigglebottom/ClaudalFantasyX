class_name LatticeNode
extends RefCounted
## One node of a Lattice board (SPEC §6.4). Read-only after LatticeBoard loads it.
## Field meanings: docs/kb/design/lattice.md.

const KIND_START := &"start"
const KIND_STAT := &"stat"
const KIND_ABILITY := &"ability"
const KIND_GATE := &"gate"
const KIND_EMPTY := &"empty"

var id: StringName
## Node type from the JSON "type" field (start|stat|ability|gate|empty).
var kind: StringName
## Stat nodes: BattleCombatant stat name (hp, mp, strength, ...) and the flat bonus.
var stat: StringName = &""
var value: int = 0
## Ability nodes: the skill id granted (must exist in skills.json).
var skill: StringName = &""
## Gate nodes: the Key Facet level needed to open it.
var gate_level: int = 0
## Start nodes: the character who begins here.
var character: StringName = &""
var region: StringName = &""
## Board coordinates in lattice units (the 3D presenter picks the world scale).
var position: Vector2i = Vector2i.ZERO


static func from_dict(d: Dictionary) -> LatticeNode:
	var n := LatticeNode.new()
	n.id = StringName(str(d.get("id", "")))
	n.kind = StringName(str(d.get("type", KIND_EMPTY)))
	n.stat = StringName(str(d.get("stat", "")))
	n.value = int(d.get("value", 0))
	n.skill = StringName(str(d.get("skill", "")))
	n.gate_level = int(d.get("gate_level", 0))
	n.character = StringName(str(d.get("character", "")))
	n.region = StringName(str(d.get("region", "")))
	n.position = Vector2i(int(d.get("x", 0)), int(d.get("y", 0)))
	return n


## Stat and ability nodes are activated per character with a Facet.
func is_activatable() -> bool:
	return kind == KIND_STAT or kind == KIND_ABILITY


func is_gate() -> bool:
	return kind == KIND_GATE
