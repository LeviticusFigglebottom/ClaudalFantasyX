class_name CrowdClipLibrary
extends RefCounted
## The crowd bodies' shared clip libraries (M3-CRE-662, ADR 0152; docs/kb/art/creatures/crowd.md "Clips"). Every
## crowd body is the villager rig (one skeleton, the same bone names), so a group of bodies (adult, elder, child,
## child_small) shares one AnimationLibrary built on a reference body (assets_src/crowd/build_crowd.py). Its tracks
## are rooted at one armature name, and it records the reference's hips rest height as metadata. At import
## (game/core/import/crowd_post_import.gd) prepare() points the rules at the body's library and names its armature,
## and fit() scales the hips track to the body's own height (Skeleton3D.motion_scale). No editor dependency, so
## tests/unit/test_crowd_villagers.gd drives it on loaded bodies too.

const LIBRARY_TOKEN := "{library}"


## The rules' `animations` with `library` resolved for `source_file`'s body (from `libraries`); the body's armature
## node (the Skeleton3D's parent under the scene root) renamed to `armature`. Returns the rules to apply.
static func prepare(scene: Node, rules: Dictionary, source_file: String) -> Dictionary:
	var anim := (rules.get("animations", {}) as Dictionary).duplicate()
	var body := source_file.get_file().get_basename()
	var lib := str((anim.get("libraries", {}) as Dictionary).get(body, ""))
	if lib == "":
		push_warning("CrowdClipLibrary: %s has no clip library in the crowd rules" % body)
		anim["library"] = ""
	else:
		anim["library"] = str(anim.get("library", "")).replace(LIBRARY_TOKEN, lib)
	var armature := armature_of(scene)
	var armature_name := str(anim.get("armature", ""))
	if armature != null and armature_name != "":
		armature.name = armature_name
	var out := rules.duplicate()
	out["animations"] = anim
	return out


## The node the library's tracks are rooted at: the Skeleton3D's parent, when that is not the scene root.
static func armature_of(scene: Node) -> Node:
	var found := scene.find_children("*", "Skeleton3D", true, false)
	if found.is_empty():
		return null
	var parent := found[0].get_parent()
	return null if parent == scene else parent


## Sets the body's Skeleton3D.motion_scale to its hips rest height over the library's (`hips_meta`), so the library's
## hips position track, keyed for the reference body, fits this one. Returns the scale (0.0 when it cannot).
static func fit(scene: Node, rules: Dictionary) -> float:
	var anim := rules.get("animations", {}) as Dictionary
	var path := str(anim.get("library", ""))
	if path == "" or not ResourceLoader.exists(path):
		return 0.0
	var lib := load(path) as AnimationLibrary
	var found := scene.find_children("*", "Skeleton3D", true, false)
	if lib == null or found.is_empty():
		return 0.0
	var skel := found[0] as Skeleton3D
	var bone := skel.find_bone(str(anim.get("hips_bone", "")))
	var ref := float(lib.get_meta(StringName(str(anim.get("hips_meta", ""))), 0.0))
	if bone < 0 or ref <= 0.0:
		push_warning("CrowdClipLibrary: no hips bone or reference height for %s" % path)
		return 0.0
	skel.motion_scale = skel.get_bone_rest(bone).origin.y / ref
	return skel.motion_scale
