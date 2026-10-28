@tool
extends EditorScenePostImport
## Post-import for hero characters (assets/characters/<hero>/*.glb), M1-ART-02. Rules:
## game/data/import/characters.json; the work is AssetImportRules (no class_name: editor-only base).
## Asha adopts it after M1-CHR-03 (docs/kb/tech/asset_import.md).
## ADR 0140: a skeleton with derived skirt panels gets a HeroSkirtFolds modifier, which sets them every frame.

const KIND := "characters"
const FOLDS_NODE := "SkirtFolds"


func _post_import(scene: Node) -> Object:
	var out := AssetImportRules.run(scene, KIND, get_source_file())
	add_skirt_folds(out)
	return out


## Adds the HeroSkirtFolds modifier under every skeleton whose even-numbered skirt panels are derived (ADR 0140).
static func add_skirt_folds(scene: Node) -> void:
	for node: Node in scene.find_children("*", "Skeleton3D", true, false):
		var skel := node as Skeleton3D
		if HeroHelperBones.fold_rig(skel).is_empty() or skel.has_node(FOLDS_NODE):
			continue
		var folds := HeroSkirtFolds.new()
		folds.name = FOLDS_NODE
		skel.add_child(folds)
		folds.owner = scene
