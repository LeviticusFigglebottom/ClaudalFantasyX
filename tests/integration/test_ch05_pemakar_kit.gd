extends KitWalkProbe
## M3-C05-1213, ADR 0200: ch05/pemakar on env-art's Pemakar kit. The Lanternfall night (the lamps, the
## leaf-boats, the far and sea lights) follows the greybox's Lamps block, so the day variant puts it out; and the
## town is walkable where the story walks (KitWalkProbe): from the quay up the slope and every stair flight to the
## crown channel, and along the tiers to the market, the forge, the inn gate and the grave terrace. Every mark and
## actor stands on a floor, and no story point is inside a house, the smithy or a market stall.

const PEMAKAR := "res://game/levels/ch05/pemakar/pemakar.tscn"
const TIER_D := 7.0
const TIER_RISE := 2.4
const TIER0_Y := 8.0
const TIERS := 10
const QUAY_Y := 1.2
const STAIR_HEAD_D := 1.6  # behind a tier's front: the lane between the channel and the house fronts
const FLOAT_IDS: Array[String] = ["sea"]
const TERRAIN: Array[String] = ["mountain_massif.glb"]


func before_each() -> void:
	open(PEMAKAR)
	kit_terrain = TERRAIN
	check_kit = true


func _dressing() -> ZoneKitDressing:
	return zone.get_node(^"Dressing") as ZoneKitDressing


## A point on tier t's tread, d m behind its front, at lateral x (the kit's arcs about (0, -150)).
static func on_tier(t: int, x: float, d: float) -> Vector3:
	var r := 150.0 - TIER_D * t - d
	var th := asin(x / r)
	return Vector3(r * sin(th), TIER0_Y + TIER_RISE * t, -150.0 + r * cos(th))


func _trigger(id: String) -> Vector3:
	return (zone.get_node(NodePath("Triggers/%s" % id)) as Node3D).position


func _up_the_stairs(to_tier: int) -> Array[Vector3]:
	var pts: Array[Vector3] = []
	for t in to_tier + 1:
		pts.append(on_tier(t, 0.0, -4.4))  # the flight's foot, out on the tier below
		pts.append(on_tier(t, 0.0, STAIR_HEAD_D))
	return pts


func test_the_festival_follows_the_lamps_block() -> void:
	var d := _dressing()
	var night := d.followers("Lamps")
	var lamps := night.filter(func(n: Node3D) -> bool: return n is OmniLight3D)
	assert_true(lamps.size() > 300, "the kit's lamps (%d)" % lamps.size())
	var names := (
		night
		. filter(func(n: Node3D) -> bool: return n is MultiMeshInstance3D)
		. map(func(n: Node3D) -> String: return String(n.name))
	)
	assert_eq(names, ["LeafBoats", "FarLights", "SeaLights"], "the boats and the far and sea lights")
	for l: OmniLight3D in lamps:
		assert_eq(l.light_volumetric_fog_energy, 0.0, "fog-lamp rule")
	zone.hide_block("Lamps")
	for n: Node3D in night:
		assert_false(n.visible, "%s goes out with the night" % n.name)
	close()


func test_the_quay_climbs_to_the_crown_channel() -> void:
	var start := zone.spawn_marker(&"Harbour").position
	var pts: Array[Vector3] = [start, Vector3(0.0, 0.0, 12.0)]
	pts.append_array(_up_the_stairs(TIERS - 1))
	pts.append(_trigger("crown_bell"))
	var end := walk("to the crown", pts, start.y)
	assert_true(absf(end - (TIER0_Y + TIER_RISE * (TIERS - 1))) < 0.2, "on the top tier (y %.2f)" % end)
	close()


func test_the_tiers_reach_the_market_forge_inn_and_graves() -> void:
	var pts: Array[Vector3] = [zone.spawn_marker(&"HarbourRoad").position, Vector3(0.0, 0.0, 12.0)]
	pts.append_array(_up_the_stairs(0))
	pts.append_array([_trigger("bark_boat_folders"), on_tier(0, 3.0, 1.6), _trigger("npc_garo")])
	var end := walk("to the forge", pts, QUAY_Y)
	assert_true(absf(end - TIER0_Y) < 0.2, "the forge is on tier 0 (y %.2f)" % end)
	var inn: Array[Vector3] = [on_tier(0, 0.0, STAIR_HEAD_D)]
	inn.append_array(_up_the_stairs(2).slice(2))
	inn.append_array([on_tier(2, -2.0, 1.6), zone.spawn_marker(&"InnGate").position])
	end = walk("to the inn gate", inn, TIER0_Y)
	assert_true(absf(end - (TIER0_Y + 2 * TIER_RISE)) < 0.2, "the inn is on tier 2 (y %.2f)" % end)
	var graves: Array[Vector3] = [on_tier(2, 0.0, STAIR_HEAD_D)]
	graves.append_array(_up_the_stairs(4).slice(6))
	graves.append_array([on_tier(4, 6.0, 1.6), _trigger("bark_grave_step"), _trigger("bark_grave_child")])
	end = walk("to the graves", graves, TIER0_Y + 2 * TIER_RISE)
	assert_true(absf(end - (TIER0_Y + 4 * TIER_RISE)) < 0.2, "the graves are on tier 4 (y %.2f)" % end)
	close()


func test_every_mark_and_actor_stands_on_a_floor() -> void:
	var nodes: Array[Node] = zone.stage.get_node(^"Marks").get_children()
	nodes.append_array(zone.stage.get_node(^"Actors").get_children())
	for n: Node in nodes:
		if FLOAT_IDS.has(String(n.name)):
			continue
		var p := (n as Node3D).position
		var f := floor_y(p.x, p.z, p.y + 0.3)
		assert_true(absf(f - p.y) < 0.35, "%s stands on a floor (y %.2f, floor %.2f)" % [n.name, p.y, f])
		assert_eq(inside_kit(p, TERRAIN), "", "%s is not inside a house, the smithy or a stall" % n.name)
	for s: Node in zone.get_node(^"Spawns").get_children():
		assert_eq(inside_kit((s as Node3D).position, TERRAIN), "", "spawn %s is in the open" % s.name)
	for t: Node in zone.get_node(^"Triggers").get_children():
		assert_eq(inside_kit((t as Node3D).position, TERRAIN), "", "trigger %s is in the open" % t.name)
	close()
