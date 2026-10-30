class_name RippleShotRig
extends Act1ZoneRig
## A shot rig for the first ripples (M4-A2P-047): the zone's RippleField (its `Ripples` node) struck at fixed ages
## before the frame, so the rings are where a still frame needs them. `strikes`: [[x, z, age_s], ...].

@export var strikes: Array = []


func _ready() -> void:
	super._ready()
	var field := zone.get_node_or_null(^"Ripples") as RippleField
	if field == null:
		push_warning("RippleShotRig: the zone has no Ripples node")
		return
	field.set_process(false)
	var oldest := 0.0
	for s: Array in strikes:
		oldest = maxf(oldest, float(s[2]))
	var by_age := strikes.duplicate()
	by_age.sort_custom(func(a: Array, b: Array) -> bool: return float(a[2]) > float(b[2]))
	for s: Array in by_age:
		field.now_s = oldest - float(s[2])
		field.strike(Vector3(float(s[0]), 0.0, float(s[1])))
	field.now_s = oldest
	field.advance(0.0)
