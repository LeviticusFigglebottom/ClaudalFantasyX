class_name WaterlineCamera
extends Camera3D
## The underwater test scene's waterline camera (M2-RND-09 item 6): rides the wave surface at its own
## xz, so the lens sits on the waterline whatever the weather clock reads (the GPU capture and the
## lavapipe rig start it at different times, and a fixed height landed under a crest on one of them).

@export var water: WaterSurface
## Height of the camera over the surface at its xz (metres; negative = just under it).
@export var offset_m: float = 0.0
## A node with weather_time() (the water test rig, which sets hymn_wind_time itself); null: the game clock.
@export var clock: Node


func _ready() -> void:
	# After the water test rig has stepped the weather clock this frame.
	process_priority = 100


func _process(_delta: float) -> void:
	if water == null:
		return
	var mat := water.material
	var scale: Variant = mat.get_shader_parameter(&"time_scale") if mat != null else null
	var t := (
		float(clock.call(&"weather_time"))
		if clock != null and clock.has_method(&"weather_time")
		else float(ShaderGlobals.get_value(&"hymn_wind_time", 0.0))
	)
	t *= float(scale) if scale != null else 1.0
	var p := global_position
	global_position = Vector3(p.x, water.height_at(Vector2(p.x, p.z), t) + offset_m, p.z)
