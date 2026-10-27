@tool
extends EditorScenePostImport
## Post-import for the ambient wildlife (assets/wildlife/<id>/*.glb), M3-CRE-611. Rules:
## game/data/import/wildlife.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "wildlife"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
