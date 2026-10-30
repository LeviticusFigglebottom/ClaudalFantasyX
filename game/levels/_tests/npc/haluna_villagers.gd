extends Node3D
## M3-CRE-613 review stage: a real zone with a VillagerLayer, so the villagers are seen in place. In Haluna:
## the dock pair chatting and mending, the vendor at the stall, Reed sweeping the chapel court, the child on the
## lane (npc_haluna_*); on the wake night, the feast tables (npc_wake_*). The shots pick one of the Cameras.
## Haluna's vignettes (the Lead, 2026-10-30): the causeway head, the lane's games and work, the dock's work
## (npc_haluna_vignette_*); with `night`, the dock at night as the story stages it (first_playable.json haluna:
## HalunaZone.set_night with its night_hide), so the day's people are gone and the night's are out.

const FIRST_PLAYABLE := "res://game/data/flow/first_playable.json"

@export_file("*.tscn") var zone_scene: String = "res://game/levels/ch02/haluna/haluna.tscn"
@export var zone_id: StringName = &"ch02/haluna"
## Set before the zone loads, so a stage can show a later story state (M3-HER-1142: Corrow's storm figure).
@export var flags: PackedStringArray = []
## Haluna's dock at night (HalunaZone.set_night with first_playable.json's night and night_hide).
## A shot's setup sets it after _ready (and again each frame): it applies once.
@export var night := false:
	set(value):
		night = value
		_apply_night()

var zone: Node3D
var layer: VillagerLayer
var _night_done := false


func _ready() -> void:
	for f: String in flags:
		Game.set_flag(StringName(f))
	zone = (load(zone_scene) as PackedScene).instantiate() as Node3D
	add_child(zone)
	# A zone that adds its own layer (Haluna, M2-FP-113) keeps it: a second one would show every villager twice
	# (M3-CRE-100). Only a zone without one gets one here.
	layer = zone.get_node_or_null(^"VillagerLayer") as VillagerLayer
	if layer == null:
		layer = VillagerLayer.new()
		layer.name = "VillagerLayer"
		layer.zone_id = zone_id
		zone.add_child(layer)
	_apply_night()


func _apply_night() -> void:
	if not night or _night_done or zone == null or not zone.has_method(&"set_night"):
		return
	_night_done = true
	var flow := VillagerLayer.load_data(FIRST_PLAYABLE)
	var cfg := ((flow.get("first_playable", {}) as Dictionary).get("haluna", {})) as Dictionary
	zone.call(&"set_night", cfg.get("night", {}), cfg.get("night_hide", []))
