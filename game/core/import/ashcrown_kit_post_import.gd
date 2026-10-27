@tool
extends EditorScenePostImport
## Post-import for the Ashcrown temple kit (assets/environments/kits/ashcrown/*.glb), M3-ENV-09. Rules:
## game/data/import/ashcrown_kit.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "ashcrown_kit"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
