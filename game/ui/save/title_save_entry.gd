class_name TitleSaveEntry
extends RefCounted
## Stub API for the title screen's "Continue" and "Load" entries (M1-ARC-03). The title screen
## (a UI task) does not exist yet; when it does, it calls only these:
##
##   TitleSaveEntry.can_continue()          show or grey out "Continue"
##   TitleSaveEntry.continue_slot()         the newest readable slot (autosave included), or -1
##   TitleSaveEntry.continue_game()         loads it into Game.state (then route on game_loaded)
##   TitleSaveEntry.open_load_menu(host)    the load list (SaveMenu in LOAD mode)
##
## Routing to the saved location after a load is not built: GameStateData has a location_id
## but no location -> scene registry exists yet (see architecture.md, "Saves").


static func slot_ids() -> Array[int]:
	return SaveMenuModel.default_slot_ids(int(SaveMenu.load_data().get("manual_slots", 0)))


static func can_continue(save_system: Node = null) -> bool:
	return continue_slot(save_system) >= 0


## The readable slot with the newest save time, or -1 when there is none.
static func continue_slot(save_system: Node = null) -> int:
	var saves := _saves(save_system)
	var best := -1
	var best_at := -1
	for d: Dictionary in saves.call(&"list_slots", slot_ids()) as Array:
		var info := SaveSlotInfo.from_dict(d)
		if info.is_loadable() and info.saved_at > best_at:
			best = info.slot
			best_at = info.saved_at
	return best


## The location Continue would load into (the newest readable record's location_id), read without loading it;
## &"" when there is none (M3-HER-1167: the title starts that zone's loads while it shows).
static func continue_location(save_system: Node = null) -> StringName:
	var slot := continue_slot(save_system)
	if slot < 0:
		return &""
	var info: Dictionary = _saves(save_system).call(&"slot_info", slot)
	return StringName(str(info.get("location_id", "")))


## M1-ARC-08: true when slot 0 holds an autosave that a new run's first chapter autosave would
## write over: a readable one, or one from a newer build (still somebody's run). An empty or
## damaged slot 0 has nothing to lose. The title asks before New Game when this is true.
static func new_game_overwrites_autosave(save_system: Node = null) -> bool:
	var saves := _saves(save_system)
	if saves == null:
		return false
	var info: Dictionary = saves.call(&"slot_info", SaveSystem.AUTOSAVE_SLOT)
	var status := StringName(str(info.get("status", "")))
	return status == SaveSystem.STATUS_OK or status == SaveSystem.STATUS_NEWER


static func continue_game(save_system: Node = null) -> Error:
	var slot := continue_slot(save_system)
	if slot < 0:
		return ERR_FILE_NOT_FOUND
	return int(_saves(save_system).call(&"load_into_game", slot)) as Error


static func open_load_menu(host: Node, save_system: Node = null) -> SaveMenu:
	return SaveMenu.open_in(host, SaveMenuModel.Mode.LOAD, {}, "", save_system)


static func _saves(save_system: Node) -> Node:
	if save_system != null:
		return save_system
	var tree := Engine.get_main_loop() as SceneTree
	return tree.root.get_node_or_null(^"SaveSystem") if tree != null else null
