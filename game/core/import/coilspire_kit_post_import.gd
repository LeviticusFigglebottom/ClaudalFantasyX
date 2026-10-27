@tool
extends EditorScenePostImport
## Post-import for the Coilspire temple kit (assets/environments/kits/coilspire/*.glb), M3-ENV-10. Rules:
## game/data/import/coilspire_kit.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "coilspire_kit"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
