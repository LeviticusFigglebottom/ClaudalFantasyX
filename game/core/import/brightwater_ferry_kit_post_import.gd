@tool
extends EditorScenePostImport
## Post-import for the Brightwater ferry kit (assets/environments/kits/brightwater_ferry/*.glb), M3-ENV-08. Rules:
## game/data/import/brightwater_ferry_kit.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "brightwater_ferry_kit"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
