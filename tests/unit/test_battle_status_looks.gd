extends TestCase
## FAST-TRACK 11-03 (the human's playtest: statuses must be OBVIOUS on the character). BattleStatusLooks: every one of
## the 21 statuses has a look (an icon, and an overlay, aura or prop), each look differs from the others in shape or
## motion and not by colour alone, its colours are palette swatches, and on the real stage a status shows on its
## fighter while it lasts and goes when it ends.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const PALETTE := "res://docs/kb/art/palette.json"
const STATUSES := "res://game/data/battle/statuses.json"


func _status_ids() -> Array[String]:
	var out: Array[String] = []
	var rows := (JSON.parse_string(FileAccess.get_file_as_string(STATUSES)) as Dictionary)["statuses"] as Array
	for r: Dictionary in rows:
		out.append(str(r["id"]))
	return out


func test_every_status_has_an_icon_and_a_body_look() -> void:
	var looks := BattleStatusLooks.load_data()["looks"] as Dictionary
	var dir := str((BattleStatusLooks.load_data()["icons"] as Dictionary)["dir"])
	var ids := _status_ids()
	assert_eq(ids.size(), 21, "the 21 statuses")
	for sid in ids:
		assert_true(looks.has(sid), "%s has a look" % sid)
		var look := looks.get(sid, {}) as Dictionary
		assert_true(ResourceLoader.exists("%s/%s.svg" % [dir, sid]), "%s has an icon" % sid)
		if sid != "petrify":  # Petrify's body look is the stage's stone material (BattleStage.refresh_ko)
			assert_true(
				look.has("overlay") or look.has("aura") or look.has("prop") or bool(look.get("count", false)),
				"%s shows on the body" % sid
			)


## Colour-blind safety: no two statuses share the same body signature (overlay pattern, aura motion and anchor,
## prop kind), so each reads by shape or motion, not only by hue.
func test_each_look_differs_by_shape_or_motion() -> void:
	var looks := BattleStatusLooks.load_data()["looks"] as Dictionary
	var seen := {}
	for sid: String in looks:
		var look := looks[sid] as Dictionary
		var sig := (
			"%s|%s@%s|%s|%s"
			% [
				(look.get("overlay", {}) as Dictionary).get("pattern", ""),
				(look.get("aura", {}) as Dictionary).get("motion", ""),
				(look.get("aura", {}) as Dictionary).get("at", ""),
				(look.get("prop", {}) as Dictionary).get("kind", ""),
				look.get("count", false),
			]
		)
		assert_false(seen.has(sig), "%s and %s look alike (%s)" % [sid, seen.get(sig, ""), sig])
		seen[sig] = sid


func test_colours_are_palette_swatches() -> void:
	var swatches := (JSON.parse_string(FileAccess.get_file_as_string(PALETTE)) as Dictionary)["swatches"] as Dictionary
	var looks := BattleStatusLooks.load_data()["looks"] as Dictionary
	for sid: String in looks:
		var look := looks[sid] as Dictionary
		assert_eq(str(look["icon_color"]), str((swatches[look["icon_swatch"]] as Dictionary)["hex"]).to_upper(), sid)
		for part in ["overlay", "aura", "prop"]:
			if look.has(part):
				var row := look[part] as Dictionary
				assert_true(swatches.has(row["swatch"]), "%s.%s: swatch %s" % [sid, part, row["swatch"]])
				assert_eq(str(row["color"]), str((swatches[row["swatch"]] as Dictionary)["hex"]).to_upper(), sid)
		if look.has("overlay"):
			assert_true(
				BattleStatusLooks.PATTERNS.has(str((look["overlay"] as Dictionary)["pattern"])), "%s pattern" % sid
			)


func test_a_status_shows_on_its_fighter_while_it_lasts() -> void:
	var ctl := _battle()
	var looks := ctl.stage.get_node(^"BattleStatusLooks") as BattleStatusLooks
	var hero := ctl.engine.party_active[0]
	var foe := ctl.engine.enemies[0]
	hero.statuses[&"poison"] = -1
	hero.statuses[&"protect"] = 3
	foe.statuses[&"doom"] = 3
	looks.refresh()
	var f := ctl.stage.stand_in(hero.id)
	var holder := f.get_node(NodePath(String(BattleStatusLooks.HOLDER)))
	assert_true(holder.has_node(^"poison/Aura"), "poison bubbles on the hero")
	assert_true(holder.has_node(^"poison/Icon"), "poison's icon over the hero")
	assert_true(holder.has_node(^"protect/Prop"), "protect's rings around the hero")
	var overlaid := 0
	for m in BattleStatusLooks.surfaces(f):
		if m.material_overlay != null:
			overlaid += 1
	assert_true(overlaid > 0, "the hero's body takes poison's overlay")
	assert_true(BattleStatusLooks.surfaces(f).size() == overlaid, "on every surface")
	var fh := ctl.stage.stand_in(foe.id).get_node(NodePath(String(BattleStatusLooks.HOLDER)))
	assert_eq((fh.get_node(^"doom/Count") as Label3D).text, "3", "Doom's count by its icon")
	hero.statuses.erase(&"poison")
	looks.refresh()
	assert_false(holder.has_node(^"poison"), "poison's look leaves with poison")
	for m in BattleStatusLooks.surfaces(f):
		assert_true(m.material_overlay == null, "the overlay goes too (protect has none)")
	assert_true(holder.has_node(^"protect"), "protect stays")
	hero.hp = 0
	looks.refresh()
	assert_false(holder.has_node(^"protect"), "a fallen hero shows no status")
	ctl.get_parent().remove_child(ctl)
	ctl.free()


func test_overlay_pick_is_the_highest_priority() -> void:
	var v := BattleStatusLooks.new()
	assert_eq(v.overlay_pick([&"regen", &"stop", &"poison"] as Array[StringName]), &"stop")
	assert_eq(v.overlay_pick([&"protect", &"shell"] as Array[StringName]), &"", "props only: no overlay")
	v.free()


func _battle() -> BattleController:
	var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle([&"rhen", &"asha"] as Array[StringName], [] as Array[StringName], &"sandbox_reef", 7)
	return ctl
