class_name WildlifeConfig
extends RefCounted
## Data access for the ambient wildlife (M3-CRE-611, docs/kb/art/wildlife.md): the kinds file
## (game/data/world/wildlife/wildlife.json: meshes, motion tuning, budgets, culling) and the per-zone placement
## files (game/data/world/wildlife/<zone id with / as _>.json). Also the zone seed and the range helpers the
## flock, beach and shoal simulations share.

const DIR := "res://game/data/world/wildlife/"
const KINDS_PATH := DIR + "wildlife.json"
const EXT := ".json"
const FNV_OFFSET := 2166136261
const FNV_PRIME := 16777619
const MASK_32 := 0xFFFFFFFF


## The parsed JSON object at `path`, or {} (with an error) when it is missing or not an object.
static func load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_error("WildlifeConfig: no file %s" % path)
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		push_error("WildlifeConfig: %s is not a JSON object" % path)
		return {}
	return parsed


static func load_kinds() -> Dictionary:
	return load_json(KINDS_PATH)


## The placement file of a zone: ch02/haluna -> res://game/data/world/wildlife/ch02_haluna.json.
static func zone_path(zone_id: StringName) -> String:
	return DIR + String(zone_id).replace("/", "_") + EXT


## A stable 32-bit seed from the zone id (FNV-1a over its UTF-8 bytes), the same on every platform and run.
static func seed_for(zone_id: StringName) -> int:
	var h := FNV_OFFSET
	for b in String(zone_id).to_utf8_buffer():
		h = ((h ^ b) * FNV_PRIME) & MASK_32
	return h


## A [lo, hi] array (or a single number) drawn once from `rng`.
static func draw(rng: RandomNumberGenerator, v: Variant) -> float:
	if v is Array:
		var a: Array = v
		return rng.randf_range(float(a[0]), float(a[1]))
	return float(v)


static func vec2(v: Variant) -> Vector2:
	var a: Array = v
	return Vector2(float(a[0]), float(a[1]))


static func vec3(v: Variant) -> Vector3:
	var a: Array = v
	return Vector3(float(a[0]), float(a[1]), float(a[2]))


## Moves `current` toward `target` by a first-order rate (per second), frame-rate independent.
static func approach(current: float, target: float, rate: float, delta: float) -> float:
	return lerpf(current, target, 1.0 - exp(-rate * delta))


static func approach_angle(current: float, target: float, rate: float, delta: float) -> float:
	return current + angle_difference(current, target) * (1.0 - exp(-rate * delta))
