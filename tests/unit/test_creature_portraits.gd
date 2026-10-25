extends TestCase
## M2-MNU-302 (ADR 0120): the bestiary's baked creature portraits. Every creature in the renderer's manifest
## (tools/portraits/portraits.json) has its PNG and a PROVENANCE row and names its creatures.json scene; every
## creatures.json row and every enemy with a model is in the manifest (a new model fails here until it is
## rendered); CreaturePortraits finds an enemy's picture through its model; and CreaturePortraitFrame shows the
## picture, a silhouette or nothing. (The bestiary page itself uses the UI track's live BestiaryPortraitSlot.)

const MANIFEST := "res://tools/portraits/portraits.json"
const PROVENANCE := "res://assets/PROVENANCE.md"
const NO_MODEL := &"no_model_foe"
const THEME := "res://game/ui/theme/hymn_theme.tres"


func test_every_manifest_creature_exists_with_a_provenance_row() -> void:
	var manifest := _json(MANIFEST)
	var creatures: Array = manifest.get("creatures", [])
	var size: Array = (manifest.get("defaults", {}) as Dictionary).get("size", [])
	var rows: Dictionary = CreatureActor.data().get("creatures", {})
	var provenance := FileAccess.get_file_as_string(PROVENANCE)
	assert_true(creatures.size() > 0, "the bestiary has creatures")
	var ids: Array[String] = []
	for c: Dictionary in creatures:
		var id := str(c["id"])
		assert_false(ids.has(id), "%s is listed once" % id)
		ids.append(id)
		assert_true(rows.has(id), "%s is a creatures.json row" % id)
		assert_eq(str(c["scene"]), str((rows.get(id, {}) as Dictionary).get("scene", "")), "%s scene" % id)
		var path := CreaturePortraits.path_for(StringName(id))
		assert_eq(path, str(c["out_dir"]).path_join("%s.png" % id), "the lookup's path")
		assert_true(FileAccess.file_exists(path), "%s exists" % path)
		assert_true(ResourceLoader.exists(path), "%s is imported" % path)
		assert_true(provenance.contains("| %s |" % path.trim_prefix("res://")), "%s has a PROVENANCE row" % path)
		var tex := load(path) as Texture2D
		if tex != null:
			assert_eq(Vector2i(tex.get_size()), Vector2i(int(size[0]), int(size[1])), "%s size" % path)
	for id: Variant in rows:
		assert_true(ids.has(str(id)), "creatures.json row %s has a portrait in the manifest" % id)
	var on_disk := DirAccess.get_files_at(str(CreaturePortraits.data()["dir"]))
	for f: String in on_disk:
		if f.ends_with(".png"):
			assert_true(ids.has(f.get_basename()), "%s is a manifest creature (no stray PNG)" % f)


func test_every_enemy_with_a_model_has_a_portrait() -> void:
	var models := CreatureModels.models()
	assert_true(models.size() > 0)
	for enemy: Variant in models:
		var id := StringName(str(enemy))
		var creature := CreaturePortraits.creature_for(id)
		assert_true(creature != &"", "%s's model is a creatures.json scene" % id)
		assert_true(CreaturePortraits.has(id), "%s has a portrait (render it: tools/portraits/render.sh)" % id)
		var tex := CreaturePortraits.texture(id)
		assert_true(tex != null and tex.resource_path == CreaturePortraits.path_for(creature), "%s's picture" % id)


func test_an_enemy_without_a_model_has_none() -> void:
	assert_eq(CreaturePortraits.creature_for(NO_MODEL), &"")
	assert_false(CreaturePortraits.has(NO_MODEL))
	assert_eq(CreaturePortraits.texture(NO_MODEL), null)
	assert_eq(CreaturePortraits.texture(&""), null)


func test_the_frame_shows_the_picture_a_silhouette_or_nothing() -> void:
	var frame := CreaturePortraitFrame.new()
	frame.theme = load(THEME) as Theme
	frame.size = Vector2(200.0, 200.0)
	_root().add_child(frame)
	frame.show_creature(&"reef_crab")
	assert_true(frame.visible)
	assert_eq(frame.enemy(), &"reef_crab")
	assert_eq(frame.picture().texture, CreaturePortraits.texture(&"reef_crab"))
	assert_eq(frame.picture().modulate, Color.WHITE, "in its own colours")
	assert_false(frame.is_silhouette())
	frame.show_creature(&"reef_crab", true)
	assert_true(frame.is_silhouette())
	assert_eq(frame.picture().texture, CreaturePortraits.texture(&"reef_crab"), "the same picture")
	var dark := _role(frame, "silhouette_role")
	assert_eq(frame.picture().modulate, dark, "modulated to the dark theme colour")
	assert_true(dark.get_luminance() < Color.WHITE.get_luminance() * 0.25, "a dark shape")
	frame.show_creature(NO_MODEL)
	assert_false(frame.visible, "no model: no frame")
	assert_eq(frame.enemy(), &"")
	frame.show_creature(&"")
	assert_false(frame.visible)
	_root().remove_child(frame)
	frame.free()


func _role(c: Control, key: String) -> Color:
	var role := StringName(str((CreaturePortraits.data()["frame"] as Dictionary)[key]))
	return c.get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _json(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed as Dictionary if parsed is Dictionary else {}


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root
