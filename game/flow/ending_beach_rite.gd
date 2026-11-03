class_name EndingBeachRite
extends Node3D
## M5-A3P-1701 / 1203: the credits' beach-rite vignette (act3_ending.md §2 CR; ending_beach_rite.dlg, about 20 s).
## CreditsRoll instances this behind its black (credits.json vignettes[0].scene), fades out for the vignette's
## hold_sec, then frees it. It stands up Haluna by day without its story (nothing hands off), puts the rite's cast
## on the beach (first_playable.json haluna.ending.rite) and plays the scene on the zone's own sequencer and stage.
## ch18_haluna_lifted chooses the opening line inside the script.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"

var zone: HalunaZone
var story: HalunaStory


func _ready() -> void:
	var rite: Dictionary = (
		(FirstPlayableConfig.section(FirstPlayableConfig.SECTION_HALUNA).get("ending", {}) as Dictionary)
		. get("rite", {})
	)
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	story = zone.get_node("Story") as HalunaStory
	story.autostart = false
	story.hand_off = func(_kind: StringName, _target: String) -> void: pass
	add_child(zone)
	var spawn := StringName(str(rite.get("spawn", "")))
	zone.place_at(spawn, zone.spawn_yaw_deg(spawn))
	zone.set_beach_cast_visible(false)
	zone.player.visible = false  # Rhen is the voice, not in the rite (the field body would stand on the spawn)
	zone.place_cast(rite.get("cast", {}), {})
	story.sequencer.restore_fade = false
	story.sequencer.play(StringName(str(rite.get("scene_id", ""))), zone.stage)
