class_name Ch06Zone
extends Ch04Zone
## The Ch6 greybox zone root (M3-C06-02; act1_ch06.md; docs/kb/tech/chapter_flow.md "Ch6"): the Brine
## Shoals. Ch04Zone as it is (Ch01Zone's rest, give, hide_block / show_block; the layout's flag-driven
## "states", so the raid's cast, the barge and the camp follow the flags after the battle or a load)
## plus two things Ch6 needs:
##   layout "lights": [{"flag", "sun"?, "environment"?, "environment_res"?}]  rows whose flag is set apply
##     in order over the layout's own light, on _ready and in refresh_states(): the dusk at the ridge camp.
##     "environment_res" (ADR 0200) swaps the zone's Environment for a copy of that resource (a kit's
##     grade for the state: Corrow's fallen wall); the zone's own, or its dressing's, is the base.
##   checkpoint(spawn)  B08's wayside shrine: respawn here at `spawn` and request an autosave at the
##     next safe point (SaveSystem.request_autosave), as Ch7's checkpoint does. A `zone` step.

const KEY_LIGHTS := "lights"
const KEY_ENVIRONMENT_RES := "environment_res"

var _base_environment: Environment
var _environment_res := ""


func _ready() -> void:
	super()
	apply_lights()


## Ch04Zone's states, then the lights.
func refresh_states() -> void:
	super()
	apply_lights()


## Applies every "lights" row whose flag is set, in order, over the layout's sun and environment.
func apply_lights() -> void:
	if sun == null:
		return
	var sun_row: Dictionary = _merged("sun")
	var env_row: Dictionary = _merged("environment")
	var res := ""
	for r: Variant in layout.get(KEY_LIGHTS, []):
		var row: Dictionary = r
		if bool(Game.get_flag(StringName(str(row.get("flag", ""))))):
			sun_row.merge(row.get("sun", {}), true)
			env_row.merge(row.get("environment", {}), true)
			res = str(row.get(KEY_ENVIRONMENT_RES, res))
	sun.light_energy = float(sun_row.get("energy", 1.0))
	sun.light_color = Color.html(str(sun_row.get("color", "#ffffff")))
	sun.rotation_degrees = Vector3(float(sun_row.get("pitch_deg", 0.0)), float(sun_row.get("yaw_deg", 0.0)), 0.0)
	var we := get_node_or_null(^"WorldEnvironment") as WorldEnvironment
	if we == null:
		return
	_swap_environment(we, res)
	we.environment.background_color = Color.html(str(env_row.get("background", "#000000")))
	we.environment.ambient_light_color = Color.html(str(env_row.get("ambient_color", "#ffffff")))
	we.environment.ambient_light_energy = float(env_row.get("ambient_energy", 1.0))


## Puts a copy of `res` on `we`, or the base environment back when `res` is "" (no change when it is
## already up).
func _swap_environment(we: WorldEnvironment, res: String) -> void:
	if _base_environment == null:
		_base_environment = we.environment
	if res == _environment_res:
		return
	_environment_res = res
	var env := load(res) as Environment if res != "" else null
	we.environment = env.duplicate() if env != null else _base_environment


## Moves the respawn point to this zone's `spawn` and asks for the autosave. False when there is no
## such spawn (nothing changes).
func checkpoint(spawn: String) -> bool:
	if spawn_marker(StringName(spawn)) == null:
		push_warning("Ch06Zone %s: no checkpoint spawn '%s'" % [location_id, spawn])
		return false
	Game.state.respawn_location_id = location_id
	Game.state.respawn_spawn = StringName(spawn)
	SaveSystem.request_autosave(SaveSystem.REASON_CHAPTER)
	return true
