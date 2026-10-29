extends Ch01OruvelZone
## env-art's storm preview of the Oruvel dressing (M3-ENV-746): the zone brought up in its storm variant, as
## M3-ENV-751 asks the zone itself to do it: the WorldEnvironment swapped for the dressing's `storm_environment`,
## and Rendering's UndertowStorm standing where the greybox's StormWall stood (the kit preview's arrival preset,
## its clock held), for the zone_oruvel_storm_* shots.

const KEY_STORM_ENVIRONMENT := "storm_environment"
const STORM_BLOCK := "StormWall"
## The kit preview's (oruvel_preview.gd): the colour script's arrival preset, its clock held, its ambient.
const UNDERTOW_PRESET := "ch01_arrival"
const UNDERTOW_QUALITY := "high"
const UNDERTOW_TIME_S := 205.0
const UNDERTOW_AMBIENT := 0.6


func _ready() -> void:
	super()
	set_storm(true)
	var dressing := get_node(^"Dressing") as ZoneKitDressing
	var path := str(dressing.layout.get(KEY_STORM_ENVIRONMENT, ""))
	var env := load(path) as Environment if path != "" else null
	var world := get_node(^"WorldEnvironment") as WorldEnvironment
	if env != null:
		world.environment = env.duplicate() as Environment
	_stand_undertow(world, dressing.block(STORM_BLOCK))


## The storm front: an UndertowStorm at the town, approaching from the StormWall's bearing.
func _stand_undertow(world: WorldEnvironment, wall: Node3D) -> void:
	if wall == null:
		return
	var undertow := UndertowStorm.new()
	undertow.name = &"Undertow"
	undertow.quality = UNDERTOW_QUALITY
	undertow.start_time_s = UNDERTOW_TIME_S
	undertow.playing = false
	undertow.water = get_node_or_null(^"Water") as WaterSurface
	undertow.sun = sun
	undertow.world_environment = world
	undertow.zone_shadow = false
	undertow.exposure_flash = false
	undertow.ambient_energy = UNDERTOW_AMBIENT
	if world.environment != null:
		undertow.haze_color = world.environment.fog_light_color
	add_child(undertow)
	undertow.apply_preset(UNDERTOW_PRESET)
	var to := wall.global_position
	undertow.approach_azimuth_deg = fposmod(rad_to_deg(atan2(to.x, -to.z)), 360.0)
	undertow.rain_amount = 0.0
