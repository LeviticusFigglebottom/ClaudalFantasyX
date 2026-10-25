class_name BattleArenaRoot
extends Node3D
## The root of a battle arena scene (M2-ENV-11; the contract is docs/kb/tech/battle_arenas.md):
## assets/environments/arenas/<arena_id>/<arena_id>.tscn. It carries its own WorldEnvironment, Sun
## (DirectionalLight3D) and dressing, built around the battle sandbox's slot layout at the origin. The
## slot markers and the BattleCamera stay in the battle scene; the arena has a flat, clear floor under
## every slot and no camera. Presentation only: nothing here reads or writes combat state.
##
## Named children the battle scene may look up (the constants below):
##   WorldEnvironment  the arena's grade (colour script sub-frame)
##   Sun               the key light (the Drownbell flood rig scales its energy)
##   Sea               an ArenaSea, the arena's one hymn_water_level publisher while visible
##   CameraHints       optional Marker3Ds for the battle-presentation camera (see the doc)
##   BossAnchor        optional: where a boss set piece stands (the Drownbell's sunk pool)
##   FloodAnchor       optional: the flood rig's water origin and datum (x, z = 0; y = from_m)

const WORLD_ENVIRONMENT := &"WorldEnvironment"
const SUN := &"Sun"
const SEA := &"Sea"
const CAMERA_HINTS := &"CameraHints"
const BOSS_ANCHOR := &"BossAnchor"
const FLOOD_ANCHOR := &"FloodAnchor"
## Arena scenes live at ARENA_DIR/<arena_id>/<arena_id>.tscn.
const ARENA_DIR := "res://assets/environments/arenas"

## This arena's id (encounters.json `arena`, added by the battle-presentation track).
@export var arena_id: StringName = &""
## The colour script sub-frame this arena is graded to (for reviews and the shot table).
@export var sub_frame: StringName = &""


## The scene path of an arena id.
static func path_for(id: StringName) -> String:
	return "%s/%s/%s.tscn" % [ARENA_DIR, id, id]


func sun() -> DirectionalLight3D:
	return get_node_or_null(NodePath(SUN)) as DirectionalLight3D


func world_environment() -> WorldEnvironment:
	return get_node_or_null(NodePath(WORLD_ENVIRONMENT)) as WorldEnvironment


func sea() -> WaterSurface:
	return get_node_or_null(NodePath(SEA)) as WaterSurface


## The camera hint markers by name ({} when the arena has none).
func camera_hints() -> Dictionary:
	var out := {}
	var root := get_node_or_null(NodePath(CAMERA_HINTS))
	if root == null:
		return out
	for c in root.get_children():
		if c is Marker3D:
			out[StringName(c.name)] = c
	return out
