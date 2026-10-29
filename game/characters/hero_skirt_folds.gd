class_name HeroSkirtFolds
extends SkeletonModifier3D
## ADR 0140: every frame, after the animation, sets a hero's even-numbered skirt panels from their odd neighbours
## (the clips bake only the odd ones, which lie over the legs; HeroHelperBones.apply_folds). The characters import
## adds one under each skeleton that has derived panels.

var _rig: Dictionary = {}
var _ready_rig := false


func _process_modification_with_delta(_delta: float) -> void:
	var skel := get_skeleton()
	if skel == null:
		return
	if not _ready_rig:
		_rig = HeroHelperBones.fold_rig(skel)
		_ready_rig = true
	HeroHelperBones.apply_folds(skel, _rig)
