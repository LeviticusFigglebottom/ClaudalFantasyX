@tool
extends EditorScenePostImport
## Post-import for the Tamsule Bell kit (assets/environments/kits/tamsule_bell/*.glb), M3-ENV-01. Rules:
## game/data/import/tamsule_bell_kit.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "tamsule_bell_kit"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
