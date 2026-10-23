@tool
extends EditorScenePostImport
## Post-import for hero characters (assets/characters/<hero>/*.glb), M1-ART-02. Rules:
## game/data/import/characters.json; the work is AssetImportRules (no class_name: editor-only base).
## Asha adopts it after M1-CHR-03 (docs/kb/tech/asset_import.md).

const KIND := "characters"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
