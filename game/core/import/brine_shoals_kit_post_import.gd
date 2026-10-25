@tool
extends EditorScenePostImport
## Post-import for the Brine Shoals kit (assets/environments/kits/brine_shoals/*.glb), M3-ENV-02. Rules:
## game/data/import/brine_shoals_kit.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "brine_shoals_kit"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
