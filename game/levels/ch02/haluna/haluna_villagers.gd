class_name HalunaVillagers
extends RefCounted
## M2-FP-102 (the human's playtest: placeholder villagers): gives each of Haluna's villager bodies a
## FieldNpc (M3-CRE-610, docs/kb/tech/field_npc.md) wearing its M2-CHR-03 actor, so the village idles out
## of step, breathes, turns to Rhen and talks instead of standing as capsules. The rows are
## game/data/flow/haluna_villagers.json. The body keeps its collision and its Talk Interactable; the
## FieldNpc is the body's child (so first_playable.json night_hide still sends it home) and the
## stand-in meshes it replaces are hidden. HalunaZone runs it in prebuild(), under the router's fade.

const DATA_PATH := "res://game/data/flow/haluna_villagers.json"
const NODE_NAME := "Villager"
const KEY_ROWS := "villagers"
const KEY_HIDE := "hide"


## Adds a FieldNpc to every row's body under `zone`. Returns them. A missing body or actor is skipped
## with a warning.
static func populate(zone: Node, data: Dictionary = {}) -> Array[FieldNpc]:
	var d := data if not data.is_empty() else load_data()
	var out: Array[FieldNpc] = []
	for row: Dictionary in d.get(KEY_ROWS, []):
		var body := zone.get_node_or_null(NodePath(str(row.get("body", "")))) as Node3D
		var actor_path := str(row.get("actor", ""))
		if body == null or not ResourceLoader.exists(actor_path):
			push_warning("HalunaVillagers: no body or actor for %s" % row)
			continue
		if body.get_node_or_null(NODE_NAME) != null:
			continue
		var hidden: Array = (d.get(KEY_HIDE, []) as Array) + (row.get(KEY_HIDE, []) as Array)
		for path: Variant in hidden:
			var mesh := body.get_node_or_null(NodePath(str(path))) as Node3D
			if mesh != null:
				mesh.visible = false
		var npc := FieldNpc.new()
		npc.name = NODE_NAME
		npc.npc_id = StringName(str(row.get("npc_id", "")))
		var talk := str(row.get("talk", ""))
		npc.interactable_path = NodePath("../../%s" % talk) if talk != "" else NodePath()
		# The actor is instanced here, off the main thread under the fade; FieldNpc finds it at actor_path.
		var actor := (load(actor_path) as PackedScene).instantiate() as Node3D
		actor.name = String(npc.actor_path)
		npc.add_child(actor)
		body.add_child(npc)
		out.append(npc)
	return out


static func load_data() -> Dictionary:
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	if f == null:
		push_error("HalunaVillagers: cannot read %s" % DATA_PATH)
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


## Ends every villager's talk under `zone`, VillagerLayer's included (a bark has finished; HalunaStory).
static func end_talks(zone: Node) -> void:
	if zone == null:
		return
	for node: Node in zone.find_children("*", "FieldNpc", true, false):
		var npc := node as FieldNpc
		if npc.is_talking():
			npc.end_talk()
