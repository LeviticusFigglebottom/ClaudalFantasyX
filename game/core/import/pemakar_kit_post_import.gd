@tool
extends EditorScenePostImport
## Post-import for the Pemakar kit (assets/environments/kits/pemakar/*.glb), M3-ENV-03. Rules:
## game/data/import/pemakar_kit.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "pemakar_kit"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
