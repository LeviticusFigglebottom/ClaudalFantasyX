class_name CostumeVariant
extends Node
## A costume variant on a character (M4-A2P-050: Merel's bloodied sleeve, act2_ch14.md B08). A villager's
## write_materials writes the variant as `<slot>_<variant>.tres` next to the slot's own material (no glTF slot takes
## that name, so the import never wears it); this node, under a character or any node holding one, makes every
## surface whose glTF material is `slot` wear `material` instead, once the scene has dressed its model.

@export var slot: StringName = &""
@export var material: Material


func _ready() -> void:
	_apply.call_deferred()


func _apply() -> void:
	apply(get_parent(), slot, material)


## Every surface under `root` whose glTF material is `slot_name` wears `mat`. Returns how many surfaces changed.
static func apply(root: Node, slot_name: StringName, mat: Material) -> int:
	var changed := 0
	if root == null or mat == null:
		return 0
	for node: Node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			if NpcTints.slot_of(mi, i) == slot_name:
				mi.set_surface_override_material(i, mat)
				changed += 1
	return changed
