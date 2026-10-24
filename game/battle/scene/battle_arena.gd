class_name BattleArena
extends RefCounted
## Per-encounter battle arenas (M2-BPR-07; docs/kb/tech/battle_presentation.md "Arenas"). An encounter named in
## game/data/battle/arenas.json fights in its arena scene: each child of that scene replaces the battle scene's
## node of the same name (WorldEnvironment, Sun, Arena) or is added beside them (a fill light). Every other
## encounter keeps the sandbox's own arena, so capture fixtures never move. Presentation only; BattleChoreo.attached
## applies it before the VFX attach, so the flood rig finds the arena's Sun and Arena/Sea.

const DATA_PATH := "res://game/data/battle/arenas.json"
## Meta on the battle scene: the arena scene it shows now ("" = the sandbox's own).
const META_ARENA := &"hymn_arena"

static var _data_cache: Dictionary = {}


static func data() -> Dictionary:
	if _data_cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_data_cache = (parsed as Dictionary).get("arenas", {}) as Dictionary
		else:
			push_warning("BattleArena: cannot read %s" % DATA_PATH)
	return _data_cache


## The arena scene encounter `encounter` fights in ("" for the sandbox's own).
static func scene_for(encounter: StringName) -> String:
	var id := str((data().get("by_encounter", {}) as Dictionary).get(String(encounter), ""))
	return str((data().get("scenes", {}) as Dictionary).get(id, ""))


## Puts encounter `encounter`'s arena into `battle` (the battle scene's root). A retry of the same encounter keeps
## it; returns the arena scene shown ("" for the sandbox's own).
static func apply(battle: Node, encounter: StringName) -> String:
	var path := scene_for(encounter)
	if path == "" or str(battle.get_meta(META_ARENA, "")) == path:
		return str(battle.get_meta(META_ARENA, ""))
	if not ResourceLoader.exists(path):
		push_warning("BattleArena: %s names a missing arena %s" % [encounter, path])
		return ""
	var arena := (load(path) as PackedScene).instantiate()
	for child in arena.get_children():
		var old := battle.get_node_or_null(NodePath(child.name))
		var at := old.get_index() if old != null else -1
		if old != null:
			battle.remove_child(old)
			old.queue_free()
		arena.remove_child(child)
		battle.add_child(child)
		if at >= 0:
			battle.move_child(child, at)
	arena.free()
	battle.set_meta(META_ARENA, path)
	return path
