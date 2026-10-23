@tool
extends EditorScenePostImport
## Post-import for the Haluna kit (assets/environments/kits/haluna/*.glb), M1-ART-02. Rules:
## game/data/import/haluna_kit.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "haluna_kit"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
