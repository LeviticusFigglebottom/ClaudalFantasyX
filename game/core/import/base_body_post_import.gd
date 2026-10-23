@tool
extends EditorScenePostImport
## Post-import for the base bodies (assets/characters/base_body/*.glb), M1-ART-02. Rules:
## game/data/import/base_body.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "base_body"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
