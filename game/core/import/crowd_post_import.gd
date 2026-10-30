@tool
extends EditorScenePostImport
## Post-import for Act I's crowd bodies (assets/crowd/<body>/<body>.glb), M3-CRE-659 (ADR 0152). Rules:
## game/data/import/crowd.json; the work is AssetImportRules (no class_name: editor-only base). M3-CRE-662: the
## clips are a group's shared library, so CrowdClipLibrary resolves the body's library and names its armature first,
## and fits the hips track to the body's height after.

const KIND := "crowd"


func _post_import(scene: Node) -> Object:
	var rules := AssetImportRules.load_rules(KIND)
	if rules.is_empty():
		return scene
	var source := get_source_file()
	rules = CrowdClipLibrary.prepare(scene, rules, source)
	AssetImportRules.apply(scene, rules, source)
	CrowdClipLibrary.fit(scene, rules)
	return scene
