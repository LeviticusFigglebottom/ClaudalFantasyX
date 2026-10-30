extends TestCase
## M5-A3P-1980 (Act III, Kite traversal; SPEC §6.6): every place the Kite can land (game/data/world/kite.json, its
## destinations and secrets) lands the party on firm, dry ground. With the world open (the Kite's open_flag and every
## destination's requires_flag set, as in Act III), each landing's location is enterable, its zone has the named
## spawn, and the party placed there through the zone's own place_at settles grounded within SETTLE_SEC, close to
## the spawn's height (no fall through the floor), above the shore's deep_water_m under any WaterSurface, and stays
## grounded through a short walk out from the spawn (no landing on a ledge with nothing past it).

const DT := 1.0 / 60.0
const SETTLE_SEC := 1.0
const WALK_SEC := 1.5
## How far the hero may settle below the spawn marker (a marker a little above a slope, a step).
const SETTLE_DROP_M := 1.0
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]

var _state_was: GameStateData


func before_each() -> void:
	_state_was = Game.state


func test_every_kite_landing_is_on_firm_dry_ground() -> void:
	var kite := KiteMapModel.load_data()
	var registry := LocationRegistry.load_default()
	Game.state = GameStateData.new()
	Game.state.party_ids = PARTY.duplicate()
	var rows := _landings(kite)
	Game.set_flag(StringName(str(kite.get("open_flag", ""))), true)
	for row in rows:
		for key in ["requires_flag", "found_flag"]:
			if str(row.get(key, "")) != "":
				Game.set_flag(StringName(str(row[key])), true)
	var landed := 0
	for row in rows:
		var loc := StringName(str(row.get("location_id", "")))
		var spawn := StringName(str(row.get("spawn", "")))
		var label := "%s (%s, %s)" % [row.get("id", "?"), loc, spawn]
		if not registry.can_enter(loc):
			fail("%s: the Kite lands somewhere that can't be entered" % label)
			continue
		var zone := (load(registry.scene_of(loc)) as PackedScene).instantiate() as Node3D
		var story := zone.get(&"story") as ZoneStory if "story" in zone else null
		if story != null:
			story.autostart = false
		var haluna := zone.get_node_or_null(^"Story") as HalunaStory
		if haluna != null:
			haluna.autostart = false
		_host().add_child(zone)
		var problem := _landing_problem(zone, spawn)
		if problem != "":
			fail("%s: %s" % [label, problem])
		landed += 1
		zone.free()
	Game.state = _state_was
	print("  kite landings checked: %d" % landed)
	assert_true(landed >= 8, "the Kite's destinations were found (%d)" % landed)


## Empty when the party lands well at `spawn`, else what went wrong.
func _landing_problem(zone: Node3D, spawn: StringName) -> String:
	if not zone.has_method(&"spawn_names") or not (zone.call(&"spawn_names") as Array).has(spawn):
		return "the zone has no such spawn"
	var player := _controller(zone)
	if player == null:
		return "the zone has no field hero"
	var director := zone.get_node_or_null("CameraDirector") as FieldCameraDirector
	if director != null:
		director.auto_update = false
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	zone.call(&"place_at", spawn, zone.call(&"spawn_yaw_deg", spawn))
	var start := player.global_position
	player.input_override = Vector2.ZERO
	for i in int(SETTLE_SEC / DT):
		player.step(DT)
	var settled := _settle_problem(player, start)
	if settled != "":
		return settled
	player.input_override = Vector2(0, -1)
	for i in int(WALK_SEC / DT):
		player.step(DT)
		if player.global_position.y < start.y - SETTLE_DROP_M - 2.0:
			return "walking out from the landing, the party falls (at %s)" % player.global_position.round()
	player.input_override = Vector2.ZERO
	return ""


## Empty when the hero stands grounded, near the spawn's height and out of deep water, else what is wrong.
static func _settle_problem(player: FieldController, start: Vector3) -> String:
	var at := player.global_position
	var water := player.shore.water_y(player, at)
	var deep := float(player.shore.cfg.get("deep_water_m", INF))
	if not player.grounded():
		return "the party is not on the ground %.1f s after landing (at %s)" % [SETTLE_SEC, at.round()]
	if start.y - at.y > SETTLE_DROP_M:
		return "the party fell %.1f m below the spawn" % (start.y - at.y)
	if not is_nan(water) and water - at.y > deep:
		return "the party lands %.1f m deep in the water" % (water - at.y)
	return ""


static func _landings(kite: Dictionary) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for key in ["destinations", "secrets"]:
		for row: Variant in kite.get(key, []):
			out.append(row as Dictionary)
	return out


static func _controller(zone: Node) -> FieldController:
	for n in zone.find_children("*", "CharacterBody3D", true, false):
		if n is FieldController:
			return n as FieldController
	return null


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
