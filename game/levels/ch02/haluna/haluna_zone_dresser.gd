class_name HalunaZoneDresser
extends HalunaDresser
## The mood scene's HalunaDresser as the playable zone uses it (M2-FP-05). HalunaZone.prebuild()
## dresses the mood scene while the zone is being instantiated (on SceneRouter's worker thread, off
## the tree), so the dresser must not dress a second time when it enters the tree: this subclass
## only drops the dress() call from _ready. Environment's haluna_dresser.gd is not edited; the zone
## swaps the instanced node's script to this one (adopt) before dressing.


## Already dressed by HalunaZone.prebuild(); nothing to do on entering the tree.
func _ready() -> void:
	pass


## Swaps `d`'s script to this class, keeping the exported values the mood scene set on it.
static func adopt(d: HalunaDresser) -> HalunaZoneDresser:
	if d is HalunaZoneDresser:
		return d as HalunaZoneDresser
	var keep := {
		&"layout_path": d.layout_path,
		&"terrain": d.terrain,
		&"tide": d.tide,
		&"ground_material": d.ground_material,
	}
	d.set_script(HalunaZoneDresser)
	for key: StringName in keep:
		d.set(key, keep[key])
	return d as HalunaZoneDresser
