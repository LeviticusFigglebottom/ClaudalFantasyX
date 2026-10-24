extends TestCase
## M1-ENV-04: Haluna's save shrine is placed in the Haluna zone scene with the values M1-ARC-06
## recorded (architecture.md "Saves"), and the location registry resolves it. The shrine lives in the
## mood-test zone, which the playable zone game/levels/ch02/haluna/ instances (M2-FP-02); it is
## instanced here, never added to the tree, so the zone's dresser does not build.

const ZONE := "res://game/levels/ch02/haluna/haluna_dressing.tscn"
const PLAYABLE_ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const LOCATION := &"ch02/haluna"
const NETWORK := &"haluna_shrine"


func test_the_zone_holds_the_haluna_shrine_with_its_story_values() -> void:
	var zone := (load(ZONE) as PackedScene).instantiate()
	var shrine := zone.get_node_or_null("SaveShrine") as SaveShrine
	assert_true(shrine != null, "a SaveShrine is in the zone")
	if shrine != null:
		assert_eq(shrine.id, NETWORK)
		assert_eq(shrine.sets_flag, &"ch02_saved_once")
		assert_eq(shrine.location_id, LOCATION)
		assert_eq(shrine.network_id, NETWORK)
		assert_true(Game.registry.is_declared(shrine.sets_flag), "the flag is declared")
	var marker := zone.get_node_or_null("Spawns/Shrine") as Marker3D
	assert_true(marker != null, "the zone has the Shrine spawn")
	if marker != null and shrine != null:
		var gap := Vector2(marker.position.x - shrine.position.x, marker.position.z - shrine.position.z)
		assert_true(gap.length() < 4.0, "the party appears beside the shrine (%.1f m)" % gap.length())
	zone.free()


func test_the_registry_resolves_haluna_and_its_shrine() -> void:
	var reg := LocationRegistry.load_default()
	assert_true(reg.has_location(LOCATION))
	# M2-FP-02 (M1-ENV-06's intent): the row now points at the playable zone, which instances the
	# mood scene (and so its shrine) and adds the player.
	assert_eq(reg.scene_of(LOCATION), PLAYABLE_ZONE)
	assert_eq(reg.name_key_of(LOCATION), "LOCATION_CH02_HALUNA")
	assert_eq(
		reg.shrine_point(NETWORK), {LocationRegistry.KEY_LOCATION: LOCATION, LocationRegistry.KEY_SPAWN: &"Shrine"}
	)
	assert_true(reg.can_enter(LOCATION), "the playable zone is entered")
	var to := reg.resolve(LOCATION)
	assert_false(bool(to["fallback"]))
	assert_eq(to[LocationRegistry.KEY_LOCATION], LOCATION)
	assert_eq(to[LocationRegistry.KEY_SCENE], PLAYABLE_ZONE)
