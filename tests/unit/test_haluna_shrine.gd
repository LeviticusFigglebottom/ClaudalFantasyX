extends TestCase
## M1-ENV-04: Haluna's save shrine is placed in the Haluna zone scene with the values M1-ARC-06
## recorded (architecture.md "Saves"), and the location registry resolves it. The scene is the
## mood-test zone until game/levels/ch02/haluna/ exists; it is instanced, never added to the tree,
## so the zone's dresser does not build.

const ZONE := "res://game/levels/_tests/haluna_mood/haluna_mood.tscn"
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
	assert_eq(reg.scene_of(LOCATION), ZONE)
	assert_eq(reg.name_key_of(LOCATION), "LOCATION_CH02_HALUNA")
	assert_eq(
		reg.shrine_point(NETWORK), {LocationRegistry.KEY_LOCATION: LOCATION, LocationRegistry.KEY_SPAWN: &"Shrine"}
	)
	# M1-ARC-11 (review-sweep-G S1): the mood zone has no player, so the row is marked
	# "playable": false and Continue goes to the default until M1-ENV-06 moves it.
	assert_false(reg.can_enter(LOCATION), "the stand-in is never entered")
	var to := reg.resolve(LOCATION)
	assert_true(bool(to["fallback"]))
	assert_eq(to["reason"], LocationRegistry.REASON_NOT_PLAYABLE)
	assert_eq(to[LocationRegistry.KEY_LOCATION], reg.default_location)
