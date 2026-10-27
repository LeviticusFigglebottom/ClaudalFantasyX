extends TestCase
## M2-FP-111: a greybox stage actor row with a "model" stands as that villager's actor (Kell in Oruvel), idling,
## instead of a capsule; rows without one keep the capsule.

const ZONE := "res://game/levels/ch01/oruvel/oruvel.tscn"


func test_kell_stands_as_her_model_idling() -> void:
	var zone := (load(ZONE) as PackedScene).instantiate() as GreyboxZone
	var host := (Engine.get_main_loop() as SceneTree).root
	host.add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	var kell := zone.stage.actor(&"kell")
	assert_true(kell != null, "Kell is on the stage")
	assert_true(kell.find_children("*", "MeshInstance3D", false, false).is_empty(), "no capsule")
	var ap := HeroMotion.player_of(kell)
	assert_true(ap != null and ap.has_animation(&"idle"), "her actor has an idle clip")
	assert_eq(String(ap.current_animation), "idle", "and idles, never a T-pose")
	# M2-FP-118: every Oruvel townsperson wears a villager body (stand-ins until M3-CHR-101), none a capsule.
	for id: StringName in [&"cook", &"scaleman", &"netmender", &"netmender_2", &"roof_child", &"skipper_sadi", &"sabe"]:
		var a := zone.stage.actor(id)
		assert_true(a.find_children("*", "MeshInstance3D", false, false).is_empty(), "%s is no capsule" % id)
		assert_true(HeroMotion.player_of(a) != null, "%s wears a body" % id)
	host.remove_child(zone)
	zone.free()
