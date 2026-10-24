class_name ReplayStage
extends RefCounted
## Prepares a zone scene to host a replayed cutscene (the Memories gallery, SPEC §6.11). Call it on a
## freshly instanced zone BEFORE it enters the tree: every story driver in it stays idle (a ZoneStory
## or HalunaStory `autostart`, a prologue's or set's `autoplay`, a level's `autostart`), and its field
## encounters never fire. Then play the scene on a CutsceneSequencer with `replay = true`.

const SWITCHES: Array[StringName] = [&"autostart", &"autoplay"]


## Turns every story switch off under (and on) `zone`. Returns how many it turned off.
static func prepare(zone: Node) -> int:
	var n := 0
	var nodes: Array[Node] = [zone]
	nodes.append_array(zone.find_children("*", "", true, false))
	for node in nodes:
		for key in SWITCHES:
			if key in node and node.get(key) is bool:
				node.set(key, false)
				n += 1
	for node in nodes:
		if node is FieldEncounters:
			if "encounters" in zone and zone.get("encounters") == node:
				zone.set("encounters", null)  # GreyboxZone._ready sets up only a live meter
			node.get_parent().remove_child(node)
			node.free()
	return n
