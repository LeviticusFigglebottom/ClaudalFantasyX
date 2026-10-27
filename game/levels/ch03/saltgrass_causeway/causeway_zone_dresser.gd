class_name CausewayZoneDresser
extends CausewayDresser
## env-art's CausewayDresser as the playable causeway uses it (M2-FP-108), like HalunaZoneDresser: GreyboxZone
## dresses the route while the zone is instantiated on SceneRouter's worker thread, off the tree, so it must not
## dress a second time on entering the tree. env-art's causeway_dresser.gd is not edited; the zone swaps the
## instanced node's script to this one (adopt) before dressing.


## Already dressed by GreyboxZone.build(); nothing to do on entering the tree.
func _ready() -> void:
	pass


## Swaps `d`'s script to this class, keeping the exported values the dressing scene set on it.
static func adopt(d: Node) -> CausewayZoneDresser:
	if d is CausewayZoneDresser:
		return d as CausewayZoneDresser
	var keep := {&"layout_path": d.get(&"layout_path"), &"tide": d.get(&"tide")}
	d.set_script(CausewayZoneDresser)
	for key: StringName in keep:
		d.set(key, keep[key])
	return d as CausewayZoneDresser
