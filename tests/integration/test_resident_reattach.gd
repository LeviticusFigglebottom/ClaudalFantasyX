extends TestCase
## The resident field (SceneRouter keeps the zone through a fight and re-attaches the same instance; the human's
## playtest): a zone taken out of the tree and put back must come back whole, as nothing re-runs its _ready. For every
## field zone: what it connected to EventBus, the shrines it registered, and what it put beside itself at the root
## are the same after a detach and re-attach (with SceneRouter.zone_links / restore_links, as the router does) as
## before. Every ZoneStory let its interactions and triggers go in _exit_tree and took them only in _ready.

var _state_was: GameStateData


func before_each() -> void:
	_state_was = Game.state


func test_every_zone_comes_back_whole_after_a_detach() -> void:
	Game.state = GameStateData.new()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	var checked := 0
	for path in HeroGuardSources.field_zones():
		var zone := (load(path) as PackedScene).instantiate() as Node3D
		var story := zone.get(&"story") as ZoneStory if "story" in zone else null
		if story != null:
			story.autostart = false
		var haluna := zone.get_node_or_null(^"Story") as HalunaStory
		if haluna != null:
			haluna.autostart = false
		var host := _host()
		host.add_child(zone)
		var before := _wiring()
		var links := SceneRouter.zone_links(zone)  # as SceneRouter keeps a resident zone through a fight
		host.remove_child(zone)
		host.add_child(zone)
		SceneRouter.restore_links(links)
		var after := _wiring()
		for key: String in before:
			if int(after.get(key, 0)) != int(before[key]):
				fail(
					(
						"%s: %s was %d, %d after a detach and re-attach"
						% [path.get_file(), key, before[key], after.get(key, 0)]
					)
				)
		checked += 1
		zone.free()
	Game.state = _state_was
	assert_true(checked > 10, "the field zones were checked (%d)" % checked)


## What a zone wires up outside itself: EventBus connections per signal, the shrine network, root children.
static func _wiring() -> Dictionary:
	var out := {}
	for s: Dictionary in EventBus.get_signal_list():
		var name := str(s["name"])
		out["EventBus.%s connections" % name] = EventBus.get_signal_connection_list(name).size()
	out["registered shrines"] = ShrineNetwork.loaded_shrines().size()
	out["root children"] = (Engine.get_main_loop() as SceneTree).root.get_child_count()
	return out


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
