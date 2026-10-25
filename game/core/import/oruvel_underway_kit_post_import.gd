@tool
extends EditorScenePostImport
## Post-import for the Oruvel Underway kit (assets/environments/kits/oruvel_underway/*.glb), M3-ENV-05. Rules:
## game/data/import/oruvel_underway_kit.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "oruvel_underway_kit"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
