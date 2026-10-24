class_name BattleArena
extends RefCounted
## Per-encounter battle arenas (M2-BPR-07; docs/kb/tech/battle_presentation.md "Arenas", env-art's
## battle_arenas.md). An encounter whose encounters.json row names an `arena` fights in that arena's scene
## (game/data/battle/arenas.json): the scene's WorldEnvironment and Sun replace the battle scene's, and every other
## child goes under a new Arena node in place of the sandbox's (a child named Sea is Arena/Sea, the flat sea the
## flood rig hides). The fighters keep the battle scene's slot markers. An encounter with no arena keeps the
## sandbox's own, so capture fixtures never move. Presentation only; BattleChoreo.attached applies it before the
## VFX attach, so the flood rig finds the arena's Sun and Arena/Sea.

const DATA_PATH := "res://game/data/battle/arenas.json"
## Meta on the battle scene: the arena scene it shows now ("" = the sandbox's own).
const META_ARENA := &"hymn_arena"
## Arena nodes that replace the battle scene's node of the same name; every other child goes under ARENA_NODE.
const ROOT_NODES: Array[StringName] = [&"WorldEnvironment", &"Sun"]
const ARENA_NODE := &"Arena"

static var _data_cache: Dictionary = {}


static func data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_data_cache = (parsed as Dictionary).get("arenas", {}) as Dictionary
		else:
			push_warning("BattleArena: cannot read %s" % DATA_PATH)
	return _data_cache


## The scene of arena `arena_id` ("" for none or an unknown id).
static func scene_of(arena_id: String) -> String:
	return str((data().get("scenes", {}) as Dictionary).get(arena_id, ""))


## The arena scene encounter `encounter` fights in, from `db` ("" for the sandbox's own).
static func scene_for(db: BattleDB, encounter: StringName) -> String:
	var row: Dictionary = db.encounters.get(encounter, db.encounters.get(String(encounter), {}))
	return scene_of(str(row.get("arena", "")))


## Puts encounter `encounter`'s arena into `battle` (the battle scene's root). A retry of the same encounter keeps
## it; returns the arena scene shown ("" for the sandbox's own).
static func apply(battle: Node, db: BattleDB, encounter: StringName) -> String:
	var path := scene_for(db, encounter)
	if path == "" or str(battle.get_meta(META_ARENA, "")) == path:
		return str(battle.get_meta(META_ARENA, ""))
	if not ResourceLoader.exists(path):
		push_warning("BattleArena: %s names a missing arena %s" % [encounter, path])
		return ""
	var arena := (load(path) as PackedScene).instantiate()
	var holder := Node3D.new()
	holder.name = String(ARENA_NODE)
	_replace(battle, holder)
	for child in arena.get_children():
		arena.remove_child(child)
		if ROOT_NODES.has(child.name):
			_replace(battle, child)
		else:
			holder.add_child(child)
	arena.free()
	battle.set_meta(META_ARENA, path)
	return path


## Puts `node` into `battle` in place of the child of the same name (or at the end).
static func _replace(battle: Node, node: Node) -> void:
	var old := battle.get_node_or_null(NodePath(node.name))
	var at := old.get_index() if old != null else -1
	if old != null:
		battle.remove_child(old)
		old.queue_free()
	battle.add_child(node)
	if at >= 0:
		battle.move_child(node, at)
