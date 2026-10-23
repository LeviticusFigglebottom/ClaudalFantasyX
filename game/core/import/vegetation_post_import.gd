@tool
extends EditorScenePostImport
## Post-import for procedural vegetation (assets/environments/vegetation/*.glb), M1-ART-02. Rules:
## game/data/import/vegetation.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "vegetation"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
