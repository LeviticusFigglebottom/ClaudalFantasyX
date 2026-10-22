class_name GameStateData
extends Resource
## All persistent, savable game state. Serialized by SaveSystem via to_dict()/from_dict().

@export var flags: Dictionary = {}
@export var party_ids: Array[StringName] = []
@export var reserve_ids: Array[StringName] = []
@export var inventory: Dictionary = {}
@export var currency: int = 0
@export var play_time_sec: float = 0.0
@export var location_id: StringName = &""
@export var chapter: int = 0


func to_dict() -> Dictionary:
	return {
		"flags": flags.duplicate(true),
		"party_ids": party_ids.map(func(s: StringName) -> String: return String(s)),
		"reserve_ids": reserve_ids.map(func(s: StringName) -> String: return String(s)),
		"inventory": inventory.duplicate(true),
		"currency": currency,
		"play_time_sec": play_time_sec,
		"location_id": String(location_id),
		"chapter": chapter,
	}


static func from_dict(d: Dictionary) -> GameStateData:
	var s := GameStateData.new()
	s.flags = (d.get("flags", {}) as Dictionary).duplicate(true)
	for id: Variant in d.get("party_ids", []):
		s.party_ids.append(StringName(str(id)))
	for id: Variant in d.get("reserve_ids", []):
		s.reserve_ids.append(StringName(str(id)))
	s.inventory = (d.get("inventory", {}) as Dictionary).duplicate(true)
	s.currency = int(d.get("currency", 0))
	s.play_time_sec = float(d.get("play_time_sec", 0.0))
	s.location_id = StringName(str(d.get("location_id", "")))
	s.chapter = int(d.get("chapter", 0))
	return s
