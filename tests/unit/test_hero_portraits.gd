extends TestCase
## M2-MNU-301 (ADR 0120): the baked hero portraits. Every hero and emotion in the renderer's manifest
## (tools/portraits/portraits.json) has its PNG and a PROVENANCE row and names the sources its stage
## really uses; HeroPortraits falls back to the neutral portrait, then to null; HeroPortraitFrame shows
## the picture, or the initial without one; and the Status, Equip, Formation and Lattice pages show the
## hero on show in a TextureRect beside their words. The runner has no after_each: each test that
## opens a page frees it itself (_teardown).

const MANIFEST := "res://tools/portraits/portraits.json"
const PROVENANCE := "res://assets/PROVENANCE.md"
const EMOTIONS := "res://game/data/dialogue/emotions.json"
const HEROES: Array[StringName] = [
	&"rhen",
	&"asha",
	&"toma",
	&"ysolde",
	&"liss",
	&"kerrid",
	&"moll",
	&"sefir",
	&"stillguard",
	&"ivo",
	# The Act I townsfolk who speak (claude/characters' villager stages; dialogue speaker ids).
	&"tavi",
	&"kell",
	&"garo",
	&"neme",
	&"osu",
	&"fenn",
	&"hobb",
	&"marra",
	&"sabe",
	&"ione",
	&"skipper_sadi",
	&"poolkeeper",
	&"scaleman",
	&"ferrymaster",
	&"tender",
	&"reed",
	&"netmender",
	&"fisher",
	&"vendor",
	&"child"
]
## The six party heroes (the pages below stand them up).
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma", &"ysolde", &"liss", &"kerrid"]
## The party the formation case stands up (Kerrid, with no portrait yet, joins it in reserve).
const LINE: Array[StringName] = [&"rhen", &"asha", &"toma"]

var state: GameStateData
var page: FieldSubmenu


func before_each() -> void:
	state = GameStateData.new()
	state.party_ids = PARTY.duplicate()
	page = null


func test_every_manifest_portrait_exists_with_a_provenance_row() -> void:
	var manifest := _json(MANIFEST)
	var heroes: Array = manifest.get("heroes", [])
	var size: Array = (manifest.get("defaults", {}) as Dictionary).get("size", [])
	assert_eq(
		heroes.size(),
		HEROES.size(),
		"the party, and the people who speak or fight with a face (Moll, Sefir, the Stillguard, the townsfolk)"
	)
	assert_true(manifest.get("creatures") is Array, "room for the bestiary's creatures")
	var provenance := FileAccess.get_file_as_string(PROVENANCE)
	var tags: Array[String] = []
	for e: Dictionary in _json(EMOTIONS).get("emotions", []):
		tags.append(str(e["id"]))
	for h: Dictionary in heroes:
		var id := StringName(str(h["id"]))
		var emotions: Array = h["emotions"]
		assert_true(emotions.has(str(HeroPortraits.fallback_emotion())), "%s has the fallback portrait" % id)
		# A speaking extra whose stage has no face-pose table (the Stillguard) has the neutral portrait alone.
		var posed := str(h["face_poses"]) != ""
		assert_true(emotions.size() >= 3 if posed else emotions == ["neutral"], "%s has expressions" % id)
		var poses: Dictionary = _json(str(h["face_poses"])).get("emotions", {}) if posed else {"neutral": {}}
		for emotion: String in emotions:
			var path := HeroPortraits.path_for(id, StringName(emotion))
			assert_eq(path, str(h["out_dir"]).path_join("%s_%s.png" % [id, emotion]), "the lookup's path")
			assert_true(FileAccess.file_exists(path), "%s exists" % path)
			assert_true(ResourceLoader.exists(path), "%s is imported" % path)
			assert_true(provenance.contains("| %s |" % path.trim_prefix("res://")), "%s has a PROVENANCE row" % path)
			assert_true(tags.has(emotion), "%s is an emotion tag" % emotion)
			assert_true(poses.has(emotion), "%s's face poses define %s" % [id, emotion])
			var tex := load(path) as Texture2D
			if tex != null:
				assert_eq(Vector2i(tex.get_size()), Vector2i(int(size[0]), int(size[1])), "%s size" % path)


func test_the_manifest_names_the_sources_each_stage_uses() -> void:
	for h: Dictionary in _json(MANIFEST).get("heroes", []):
		var stage := (load(str(h["stage"])) as PackedScene).instantiate() as AshaStage
		assert_true(stage != null, "%s is a hero review stage" % h["id"])
		if stage == null:
			continue
		assert_eq(stage.character_scene.resource_path, str(h["model"]), "%s model" % h["id"])
		assert_eq(stage.face_poses_path, str(h["face_poses"]), "%s face poses" % h["id"])
		var dir := str(h["materials"])
		for key: String in stage.materials:
			var mat := stage.materials[key] as Material
			assert_true(mat.resource_path.begins_with(dir), "%s %s from %s" % [h["id"], key, dir])
		assert_true(stage.get_node_or_null(^"Cameras/Face") is Camera3D, "the Face camera the renderer aims")
		stage.free()


func test_the_lookup_falls_back_to_neutral_then_to_nothing() -> void:
	var grief := HeroPortraits.texture(&"rhen", &"grief")
	var neutral := HeroPortraits.texture(&"rhen", &"neutral")
	assert_true(grief != null and neutral != null)
	assert_eq(grief.resource_path, HeroPortraits.path_for(&"rhen", &"grief"))
	assert_false(HeroPortraits.has(&"rhen", &"laugh"), "no laugh portrait is baked")
	assert_eq(HeroPortraits.texture(&"rhen", &"laugh"), neutral, "an emotion without a portrait: neutral")
	assert_eq(HeroPortraits.texture(&"rhen"), neutral, "no emotion: neutral")
	assert_eq(HeroPortraits.texture(&"pell", &"grief"), null, "someone without portraits: null")
	assert_eq(HeroPortraits.texture(&"", &"neutral"), null)
	var face := HeroPortraits.face(&"asha", &"smile") as AtlasTexture
	assert_true(face != null, "the head crop")
	if face != null:
		var r: Array = HeroPortraits.data()["face_region"]
		assert_eq(face.region, Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3])))
		assert_eq(face.atlas, HeroPortraits.texture(&"asha", &"smile"))
	assert_eq(HeroPortraits.face(&"pell"), null)
	assert_eq(HeroPortraits.page_emotion(&"status"), &"neutral")
	assert_eq(HeroPortraits.page_emotion(&"status", true), &"worried", "a fallen hero looks worried")
	assert_eq(HeroPortraits.page_emotion(&"equip", true), &"determined", "no fallen pose: the page's own")
	assert_eq(HeroPortraits.page_emotion(&"nowhere"), HeroPortraits.fallback_emotion())


func test_the_frame_shows_the_picture_or_the_initial() -> void:
	var frame := HeroPortraitFrame.new()
	frame.size = Vector2(120.0, 120.0)
	_root().add_child(frame)
	frame.show_hero(&"toma", "Toma", &"worried")
	assert_true(frame.visible)
	assert_eq(frame.picture().texture, HeroPortraits.texture(&"toma", &"worried"))
	assert_true(frame.picture().visible)
	assert_eq(frame.initial_text(), "", "no initial over a picture")
	frame.show_hero(&"pell", "Pell")
	assert_true(frame.picture().texture == null, "no picture")
	assert_eq(frame.initial_text(), "P", "the old initial as the last fallback")
	frame.crop = HeroPortraitFrame.Crop.FACE
	frame.show_hero(&"asha", "Asha")
	assert_true(frame.picture().texture is AtlasTexture, "the head crop")
	frame.show_hero(&"", "")
	assert_false(frame.visible, "nobody: hidden")
	frame.free()


func test_status_shows_the_hero_on_show() -> void:
	page = StatusMenu.create(PartySheet.new(state, PARTY))
	page.pause_tree = false
	_root().add_child(page)
	var status := page as StatusMenu
	var frame := status.portrait()
	assert_true(frame != null and frame.visible)
	assert_eq(frame.hero(), &"rhen")
	assert_true(frame.picture() is TextureRect and frame.picture().texture != null, "a picture, not an initial")
	assert_eq(frame.emotion(), HeroPortraits.page_emotion(&"status"))
	status.show_hero(&"toma")
	assert_eq(frame.hero(), &"toma")
	assert_eq(frame.picture().texture, HeroPortraits.texture(&"toma", HeroPortraits.page_emotion(&"status")))
	var r := frame.get_rect()
	for c: Control in status._detail:
		assert_false(r.intersects(c.get_rect()), "the portrait clears %s %s" % [c, c.get_rect()])
	_teardown()


func test_status_shows_a_fallen_hero_worried() -> void:
	state.party_vitals = {"asha": {"hp": 0}}
	page = StatusMenu.create(PartySheet.new(state, PARTY))
	page.pause_tree = false
	_root().add_child(page)
	var status := page as StatusMenu
	status.show_hero(&"asha")
	assert_true(bool(status.shown_page().get("fallen", false)), "Asha has fallen")
	assert_eq(status.portrait().emotion(), HeroPortraits.page_emotion(&"status", true))
	assert_eq(status.portrait().picture().texture, HeroPortraits.texture(&"asha", &"worried"))
	_teardown()


func test_equip_shows_the_highlighted_hero() -> void:
	page = EquipMenu.create(PartySheet.new(state, PARTY))
	page.pause_tree = false
	_root().add_child(page)
	var equip := page as EquipMenu
	var frame := equip.portrait()
	assert_eq(frame.hero(), &"rhen")
	assert_true(frame.picture().texture != null)
	equip.handle_input(_ev(&"ui_down"))
	assert_eq(frame.hero(), &"asha", "the portrait follows the cursor")
	assert_false(frame.get_rect().intersects(equip.hero_page().get_rect()), "beside the heroes page")
	_teardown()


func test_formation_shows_the_highlighted_hero_beside_the_detail() -> void:
	state.party_ids = LINE.duplicate()
	state.reserve_ids = [&"kerrid"] as Array[StringName]
	page = FormationMenu.create(PartySheet.new(state, LINE + ([&"kerrid"] as Array[StringName])))
	page.pause_tree = false
	_root().add_child(page)
	var formation := page as FormationMenu
	var frame := formation.portrait()
	assert_eq(frame.hero(), &"rhen")
	assert_true(frame.picture().texture != null)
	formation.handle_input(_ev(&"ui_right"))
	assert_eq(formation.current_hero(), &"kerrid")
	assert_true(frame.picture().texture != null, "Kerrid has his portrait now (M3-CHR-505)")
	formation.handle_input(_ev(&"ui_down"))
	assert_eq(formation.current_hero(), &"", "the open place")
	assert_false(frame.visible, "no portrait for an open place")
	_teardown()


func test_lattice_shows_the_hero_on_show_as_a_head() -> void:
	page = LatticeMenu.create(PartySheet.new(state, PARTY))
	page.pause_tree = false
	_root().add_child(page)
	var lattice := page as LatticeMenu
	var frame := lattice.portrait()
	assert_eq(frame.hero(), lattice.model.hero())
	assert_true(frame.picture().texture is AtlasTexture, "the head crop")
	lattice.switch_hero(1)
	assert_eq(frame.hero(), lattice.model.hero(), "follows the hero switch")
	_teardown()


func _ev(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


func _json(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed as Dictionary if parsed is Dictionary else {}


func _teardown() -> void:
	if page != null and is_instance_valid(page):
		page.close()
		if page.get_parent() != null:
			page.get_parent().remove_child(page)
		page.free()
	page = null


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root
