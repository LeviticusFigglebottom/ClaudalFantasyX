class_name CutsceneNpcTalk
extends RefCounted
## M2-FP-106 (the playtest: "parts look primitive"): a line whose speaker is no stage actor (Neme at her
## table, a villager's bark) finds the zone's FieldNpc of that id (M3-CRE-610), which turns to Rhen and
## plays its talk clip for the rest of the scene; the scene's end lets every one of them go back to its work.

var _talking: Array[FieldNpc] = []


## Starts `id`'s talk under `root` (once per scene). Does nothing when no visible FieldNpc has that id.
func speak(root: Node, id: StringName, player: Node3D = null) -> void:
	if root == null or id == &"":
		return
	for node: Node in root.find_children("*", "FieldNpc", true, false):
		var npc := node as FieldNpc
		if npc != null and npc.npc_id == id and npc.is_visible_in_tree():
			if not npc.is_talking():
				npc.begin_talk(player)
			if not npc in _talking:
				_talking.append(npc)
			return


## Ends every talk this scene started.
func end_all() -> void:
	for npc in _talking:
		if is_instance_valid(npc) and npc.is_talking():
			npc.end_talk()
	_talking.clear()


func talking() -> Array[FieldNpc]:
	return _talking
