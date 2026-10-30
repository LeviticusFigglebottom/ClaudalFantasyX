class_name KitSlotSwaps
extends Node
## M3-ENV-1325 (env-art-b): a written scene's kit slot swaps, ZoneKitDressing's `material_paths` for scenes that are not
## dressed from a layout (the battle arenas). On ready, every kit surface under the parent whose slot (its source
## material's name) is a key of `paths` takes that path's material: the arena then wears the same zone looks as the
## zone it stands in (Ashcrown's weathered copper and lacquer, its stone's lighter baked occlusion).

## kit slot -> res:// path of the material that replaces it.
@export var paths: Dictionary = {}


func _ready() -> void:
	ZoneKitDressing.swap_slots(get_parent(), paths)
