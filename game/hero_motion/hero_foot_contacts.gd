class_name HeroFootContacts
extends RefCounted
## Foot contacts from the clips' footfall markers (M3-AUD-810 for audio; M2-CHR-12 puts Animation markers named
## foot_l_down / foot_r_down, plus _2 for a repeat, on the walk, run, start and stop clips). HeroFieldActor asks
## this once a frame which markers the live clip crossed and emits foot_contact for each. Pure: no Nodes, no clock.
## Tuning: game/data/hero_motion/hero_motion.json field.foot_contacts.

const LEFT := &"l"
const RIGHT := &"r"

## Marker name prefix -> foot (LEFT or RIGHT).
var prefixes: Dictionary = {}
## Clips whose footfalls are run steps (heavier in audio).
var run_clips: Array[StringName] = []

## Last clip and position seen, so a frame knows what it crossed.
var _clip: StringName = &""
var _pos := 0.0


func _init(cfg: Dictionary = {}) -> void:
	for k: String in (cfg.get("markers", {}) as Dictionary).keys():
		prefixes[k] = StringName(str(cfg["markers"][k]))
	for c: Variant in cfg.get("run_clips", []):
		run_clips.append(StringName(str(c)))


## The feet whose markers `anim` crossed going from `from_pos` to `to_pos` (wrapping once on a loop), in order.
func crossed(anim: Animation, from_pos: float, to_pos: float) -> Array[StringName]:
	var out: Array[StringName] = []
	if anim == null or is_equal_approx(from_pos, to_pos):
		return out
	var hits: Array[Dictionary] = []
	var wrapped := to_pos < from_pos and anim.loop_mode != Animation.LOOP_NONE
	for m: StringName in anim.get_marker_names():
		var foot := foot_of(m)
		if foot == &"":
			continue
		var t := anim.get_marker_time(m)
		var key := -1.0
		if not wrapped and t > from_pos and t <= to_pos:
			key = t
		elif wrapped and t > from_pos:
			key = t
		elif wrapped and t <= to_pos:
			key = t + anim.length
		if key >= 0.0:
			hits.append({"t": key, "foot": foot})
	hits.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return float(a["t"]) < float(b["t"]))
	for h: Dictionary in hits:
		out.append(h["foot"] as StringName)
	return out


## The foot a marker names, or &"" for any other marker.
func foot_of(marker: StringName) -> StringName:
	for p: String in prefixes.keys():
		if String(marker).begins_with(p):
			return prefixes[p] as StringName
	return &""


## One frame of the live clip at `pos`: the feet that touched down since the last frame. A new clip starts
## counting from where it is now (a cross-fade never replays a footfall the old clip already made).
func step(clip: StringName, anim: Animation, pos: float) -> Array[StringName]:
	var out: Array[StringName] = []
	if clip == _clip:
		out = crossed(anim, _pos, pos)
	_clip = clip
	_pos = pos
	return out


func is_run(clip: StringName) -> bool:
	return clip in run_clips
