class_name EbbingShotRig
extends Act1ZoneRig
## The Ebbing's test scene (M3-C09-03): Ch9's Corrow at night with every Ebbing field playing at once (the hero frame
## N11 and the stream N08 hold them all), at the colour script's ch09 mote energy. `fields` empty plays every field.

## The colour script's ch09 mote energy (glimmer_held, 4.0) and its tint.
const CH09_GLIMMER_ENERGY := 4.0
const CH09_GLIMMER_TINT := Color("#7FC6D9")

@export var fields: PackedStringArray = []

var ebbing: EbbingMotes


func _ready() -> void:
	super._ready()
	GlimmerField.set_scene_glimmer(CH09_GLIMMER_TINT, CH09_GLIMMER_ENERGY)
	ebbing = zone.find_child("Ebbing", true, false) as EbbingMotes
	if ebbing == null:
		push_warning("EbbingShotRig: the zone has no Ebbing")
		return
	var ids: Array = fields if not fields.is_empty() else (ebbing.data.get("fields", {}) as Dictionary).keys()
	for id: String in ids:
		ebbing.play(StringName(id), false)
