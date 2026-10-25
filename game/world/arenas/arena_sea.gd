@tool
class_name ArenaSea
extends WaterSurface
## A battle arena's sea (M2-ENV-11, docs/kb/tech/battle_arenas.md). It publishes hymn_water_level only
## while it is visible in the tree. The Drownbell's flood rig hides the arena's `Sea` and becomes the
## battle's one publisher (battle_vfx.md "The flood rig"), so a hidden arena sea must stop writing the
## global, or the two would fight over the wet line. Shown again (the rig restores what it hid), it
## publishes again. In the editor it never publishes (no scene edit, no global writes).


func _enter_tree() -> void:
	if not Engine.is_editor_hint():
		publishes_water_level = is_visible_in_tree()
	super()


func _notification(what: int) -> void:
	if what == NOTIFICATION_VISIBILITY_CHANGED and is_inside_tree() and not Engine.is_editor_hint():
		publishes_water_level = is_visible_in_tree()
