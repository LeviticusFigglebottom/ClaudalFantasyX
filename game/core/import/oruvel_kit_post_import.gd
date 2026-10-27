@tool
extends EditorScenePostImport
## Post-import for the Oruvel raft-town kit (assets/environments/kits/oruvel/*.glb), M3-ENV-07. Rules:
## game/data/import/oruvel_kit.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "oruvel_kit"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
