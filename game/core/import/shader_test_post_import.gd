@tool
extends EditorScenePostImport
## Post-import for the shader-test meshes (assets/characters/shader_test/*.glb), M1-ART-02. Rules:
## game/data/import/shader_test.json; the work is AssetImportRules (no class_name: editor-only base).

const KIND := "shader_test"


func _post_import(scene: Node) -> Object:
	return AssetImportRules.run(scene, KIND, get_source_file())
