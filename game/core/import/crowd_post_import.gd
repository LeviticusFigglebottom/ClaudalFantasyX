@tool
extends EditorScenePostImport
## Post-import for Act I's crowd bodies (assets/crowd/<body>/<body>.glb), M3-CRE-659 (ADR 0152). Rules:
## game/data/import/crowd.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "crowd"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
