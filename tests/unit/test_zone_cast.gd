extends TestCase
## Queue item "real casts": ZoneCast puts the villager models on the Act I zones' stage actors. Every "cast" in a
## zone layout names a villager actor scene, and every zone with casts has a Cast node; in a zone (Tamsule's port),
## a cast actor shows its model and not its capsule, idles, and two actors with the same model idle out of step.

const ZONES := [
	"res://game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn",
	"res://game/levels/ch04/haluna_wake/haluna_wake.tscn",
	"res://game/levels/ch05/ashcrown/ashcrown.tscn",
	"res://game/levels/ch05/pemakar/pemakar.tscn",
	"res://game/levels/ch06/brine_shoals/brine_shoals.tscn",
	"res://game/levels/ch07/tamsule/tamsule.tscn",
	"res://game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn",
	"res://game/levels/ch08/coilspire/coilspire.tscn",
	"res://game/levels/ch08/corrow/corrow.tscn",
	"res://game/levels/ch09/corrow_night/corrow_night.tscn",
]
const PORT := "res://game/levels/ch07/tamsule/tamsule.tscn"

var zone: GreyboxZone


func _close() -> void:
	if zone != null and is_instance_valid(zone):
		zone.get_parent().remove_child(zone)
		zone.free()
	zone = null


func test_every_cast_names_a_villager_and_every_zone_casts() -> void:
	for path: String in ZONES:
		var text := FileAccess.get_file_as_string(path)
		assert_true(text.contains("zone_cast.gd"), "%s has a Cast node" % path)
		var layout_path := text.get_slice('layout_path = "', 1).get_slice('"', 0)
		var actors: Dictionary = GreyboxZone.read_json(layout_path).get("actors", {})
		var casts := 0
		for id: String in actors.keys():
			var v := str((actors[id] as Dictionary).get(ZoneCast.KEY_CAST, ""))
			if v == "":
				continue
			casts += 1
			assert_ne(ZoneCast.scene_path(v), "", "%s: %s's villager '%s' has an actor scene" % [layout_path, id, v])
		assert_true(casts > 0, "%s casts someone" % layout_path)


func test_a_cast_actor_shows_its_model_and_idles_out_of_step() -> void:
	Game.new_game()
	zone = (load(PORT) as PackedScene).instantiate() as GreyboxZone
	zone.story.autostart = false
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(zone)
	var cast := zone.get_node(^"Cast") as ZoneCast
	assert_true(cast.cast.size() >= 6, "the port's folk are cast (%d)" % cast.cast.size())
	var fisher := zone.stage.actor(&"fisher")
	var boatman := zone.stage.actor(&"boatman")
	assert_false((fisher.get_node(^"StandIn") as Node3D).visible, "the capsule is hidden")
	# The body is the Cast, or a crowd person that replaced it once the zone has a villager file (M3-CRE-657):
	# either way the actor's AnimationPlayer is the one the cutscenes' @anim lines play.
	var a := HeroMotion.player_of(fisher)
	var b := HeroMotion.player_of(boatman)
	assert_true(a != null and a.is_playing() and a.current_animation == "idle", "the fisher idles")
	assert_true(b != null and b.is_playing(), "the boatman idles")
	assert_true(absf(a.current_animation_position - b.current_animation_position) > 0.05, "out of step")
	_close()


func test_a_creature_or_a_hero_cast_finds_its_body() -> void:
	var hound := ZoneCast.scene_path("creature:raid_hound")
	assert_ne(hound, "", "a creature: cast names the creature's model scene")
	assert_eq(ZoneCast.scene_path("creature:no_such_beast"), "", "an unknown creature has none")
	assert_ne(ZoneCast.scene_path("hero:rhen"), "", "a hero: cast takes the hero's field body")
	Game.new_game()
	zone = (load(PORT) as PackedScene).instantiate() as GreyboxZone
	zone.story.autostart = false
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(zone)
	var cast := zone.get_node(^"Cast") as ZoneCast
	var model := cast.cast_actor(&"board", "creature:raid_hound")
	assert_true(model != null, "the hound stands on the actor")
	assert_true(is_equal_approx(model.rotation.y, PI), "turned to face the actor's -Z")
	var a := HeroMotion.player_of(model)
	assert_true(a != null and a.is_playing(), "it idles")
	assert_eq(HeroMotion.body_of(zone.stage.actor(&"board")), null, "no battle play_clip for the sequencer to call")
	_close()


func test_a_cast_row_can_hold_its_body_still() -> void:
	Game.new_game()
	zone = (load(PORT) as PackedScene).instantiate() as GreyboxZone
	zone.story.autostart = false
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(zone)
	var cast := zone.get_node(^"Cast") as ZoneCast
	var model := cast.cast_actor(&"board", "creature:virel")
	assert_true(model != null, "Virel stands on the actor")
	ZoneCast.shape(model, {"cast_still": true})
	var a := HeroMotion.player_of(model)
	assert_true(a != null and not a.is_playing(), "held still on her idle's first frame")
	var micro := HeroMotion.micro_of(model)
	assert_true(micro == null or not micro.active, "and no breathing")
	_close()


func test_coilspire_draws_virel_as_her_body_not_the_block() -> void:
	var layout := GreyboxZone.read_json("res://game/levels/ch08/coilspire/coilspire_layout.json")
	var row: Dictionary = (layout["actors"] as Dictionary).get("virel", {})
	assert_eq(str(row.get("cast", "")), "creature:virel")
	var dressing := GreyboxZone.read_json("res://game/levels/ch08/coilspire/coilspire_dressing.json")
	assert_false("Virel" in (dressing["greybox"]["keep"] as Array), "the greybox block is hidden")
