extends TestCase
## Integration QA (the human's playtest: on Oruvel's dock town you could step off a deck and walk in the sea): in every
## Act I field zone with water (a WaterSurface), from every spawn, Rhen runs flat out in DIRECTIONS directions for
## RUN_SEC each, as a player pushing at a dock, pier or hull edge would. Every frame, through the real FieldController
## and its FieldShore: he never drops off an edge into the water (a frame's fall of more than shore.edge_drop_m that
## ends him under the surface), and never stands grounded deeper than shore.deep_water_m under it. A spawn already
## more than shore.underwater_m under the surface is a seabed walk (Oruvel's underway) and is skipped.

const DT := 1.0 / 60.0
const DIRECTIONS := 16
const RUN_SEC := 6.0
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]

var _state_was: GameStateData


func before_each() -> void:
	_state_was = Game.state


func test_no_hero_steps_off_a_dock_into_the_water() -> void:
	Game.state = GameStateData.new()
	Game.state.party_ids = PARTY.duplicate()
	var zones := 0
	for path in HeroGuardSources.field_zones():
		var zone := (load(path) as PackedScene).instantiate() as Node3D
		var story := zone.get(&"story") as ZoneStory if "story" in zone else null
		if story != null:
			story.autostart = false
		_host().add_child(zone)
		var player := _controller(zone)
		if player == null or not zone.has_method(&"spawn_names") or not _has_water(zone):
			zone.free()
			continue
		zones += 1
		var director := zone.get_node_or_null("CameraDirector") as FieldCameraDirector
		if director != null:
			director.auto_update = false
		player.set_physics_process(false)
		player.set_process_unhandled_input(false)
		var party := player.get_node_or_null(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
		if party != null:
			party.set_physics_process(false)
		var cfg := player.shore.cfg
		var problems := {}
		for sp: StringName in zone.call(&"spawn_names"):
			for k in DIRECTIONS:
				zone.call(&"place_at", sp, zone.call(&"spawn_yaw_deg", sp))
				player.shore.last_safe = Vector3(NAN, NAN, NAN)
				var yaw := director.camera_yaw() if director != null else 0.0
				var start_water := player.shore.water_y(player, player.global_position)
				if start_water - player.global_position.y > float(cfg["underwater_m"]):
					continue  # a seabed walk (Oruvel's underway): no shore down there
				var stick := Vector2.from_angle(TAU * k / DIRECTIONS)
				player.input_override = stick
				for i in int(RUN_SEC / DT):
					var before := player.global_position
					player.step(DT)
					var p := player.global_position
					var water := player.shore.water_y(player, p)
					if is_nan(water):
						continue
					var key := ""
					if before.y - p.y > float(cfg["edge_drop_m"]) and water - p.y > float(cfg["wade_m"]):
						key = "drops off an edge into the water"
					elif player.grounded() and water - p.y > float(cfg["deep_water_m"]):
						key = "stands %.1f m deep in the water" % (water - p.y)
					if key != "" and not problems.has("%s %s" % [sp, key]):
						problems["%s %s" % [sp, key]] = true
						fail(
							(
								"%s from %s (stick %s, camera yaw %.0f): %s at %s"
								% [path.get_file(), sp, stick.round(), rad_to_deg(yaw), key, p.round()]
							)
						)
						break
		zone.free()
	Game.state = _state_was
	print("  zones with water walked: %d" % zones)
	assert_true(zones >= 5, "the Act I zones with water were found (%d)" % zones)


static func _has_water(zone: Node) -> bool:
	for n in zone.find_children("*", "Node3D", true, false):
		if n is WaterSurface:
			return true
	return false


static func _controller(zone: Node) -> FieldController:
	for n in zone.find_children("*", "CharacterBody3D", true, false):
		if n is FieldController:
			return n as FieldController
	return null


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
