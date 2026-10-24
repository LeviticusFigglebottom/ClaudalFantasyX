@tool
extends EditorScenePostImport
## Post-import for battle creatures (assets/creatures/<id>/*.glb), M2-CRE-02. Rules:
## game/data/import/creatures.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "creatures"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
