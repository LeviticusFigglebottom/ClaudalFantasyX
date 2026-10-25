@tool
extends EditorScenePostImport
## Post-import for the Corrow seawall kit (assets/environments/kits/corrow/*.glb), M3-ENV-04. Rules:
## game/data/import/corrow_kit.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "corrow_kit"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
