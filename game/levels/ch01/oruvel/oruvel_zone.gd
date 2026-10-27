class_name Ch01OruvelZone
extends Ch01Zone
## Oruvel, the raft-town, `ch01/oruvel` (M3-C01-02; act1_ch01.md C1-07 to C1-15): a Ch01Zone with a
## storm variant. The layout's "storm" block says what changes once the gulls cry (C1-11):
##   {"flag": the flag that means the storm is up (ch01_gulls_cried),
##    "sun": {...}, "environment": {...}   the stand-in storm light (until lut_ch01_storm and the
##                                          Undertow preset ch01_landfall), merged over the day's,
##    "environment_res": res://...        with a kit Dressing (M3-C01-100): the storm's whole Environment,
##    "hide": [block or actor ids], "show": [...]   the day's town gone, the storm's cast and rig up,
##    "lashings": {"flags": [...], "frees": block id}  a low hull that drifts clear once every
##                                          lashing flag is set (C1-13's two cuts)}.
## set_storm(true) is the story's `zone` step at C1-11; a zone entered with the flag already set (a
## return from a battle, a load) comes up in the storm at once. refresh_rig() re-reads the lashings
## (each cut's beat calls it).

## True while the storm variant is up.
var storm := false

var _day_environment: Environment


func _ready() -> void:
	super()
	var flag := StringName(str(_storm().get("flag", "")))
	set_storm(flag != &"" and bool(Game.get_flag(flag)))


## Puts up (or takes down) the storm variant.
func set_storm(on: bool) -> void:
	storm = on
	var s := _storm()
	var sun_row: Dictionary = _merged("sun")
	var env_row: Dictionary = _merged("environment")
	if on:
		sun_row.merge(s.get("sun", {}), true)
		env_row.merge(s.get("environment", {}), true)
	sun.light_energy = float(sun_row.get("energy", 1.0))
	sun.light_color = Color.html(str(sun_row.get("color", "#ffffff")))
	sun.rotation_degrees = Vector3(float(sun_row.get("pitch_deg", 0.0)), float(sun_row.get("yaw_deg", 0.0)), 0.0)
	var we := get_node(^"WorldEnvironment") as WorldEnvironment
	if get_node_or_null(^"Dressing") != null:
		# M3-C01-100: dressed with the kit, the zone swaps whole environments (the kit's ch01 frame, env-art's
		# storm stand-in), so the greybox colours never flatten the grade.
		if _day_environment == null:
			_day_environment = we.environment
		var res := str(s.get("environment_res", "")) if on else ""
		we.environment = (load(res) as Environment).duplicate() if res != "" else _day_environment
	else:
		var env := we.environment
		env.background_color = Color.html(str(env_row.get("background", "#000000")))
		env.ambient_light_color = Color.html(str(env_row.get("ambient_color", "#ffffff")))
		env.ambient_light_energy = float(env_row.get("ambient_energy", 1.0))
	for id: Variant in s.get("hide", []):
		_set_block(str(id), not on)
	for id: Variant in s.get("show", []):
		_set_block(str(id), on)
	refresh_rig()


## Hides the lashed low hull once every lashing flag is set.
func refresh_rig() -> void:
	var l: Dictionary = _storm().get("lashings", {})
	var flags: Array = l.get("flags", [])
	if flags.is_empty():
		return
	for f: Variant in flags:
		if not bool(Game.get_flag(StringName(str(f)))):
			return
	hide_block(str(l.get("frees", "")))


func _storm() -> Dictionary:
	return layout.get("storm", {})
