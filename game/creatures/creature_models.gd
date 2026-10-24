class_name CreatureModels
extends RefCounted
## Which enemies have a creature model (M2-CRE-03). enemies.json's `model` names a creature actor scene; the
## battle stage shows it through FighterStandIn's `scene` hook (M2-UI-07), with creatures.json's `stand_in`
## overrides (the yaw that turns a +Z-facing model toward the party). Visual only: the engine never reads `model`.

const ENEMIES_PATH := "res://game/data/battle/enemies.json"

static var _models: Dictionary = {}
static var _loaded := false


## Enemy id -> its model scene path, from enemies.json (an enemy without `model` is absent).
static func models() -> Dictionary:
	if not _loaded:
		_loaded = true
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(ENEMIES_PATH))
		if typeof(parsed) != TYPE_DICTIONARY:
			push_error("CreatureModels: could not read %s" % ENEMIES_PATH)
			return _models
		for row: Variant in (parsed as Dictionary).get("enemies", []):
			var d := row as Dictionary
			if d.has("model"):
				_models[str(d.get("id", ""))] = str(d["model"])
	return _models


## The creatures.json row id whose `scene` is `scene_path` (&"" if none).
static func creature_for_scene(scene_path: String) -> StringName:
	var rows: Dictionary = CreatureActor.data().get("creatures", {})
	for id: Variant in rows:
		if str((rows[id] as Dictionary).get("scene", "")) == scene_path:
			return StringName(str(id))
	return &""


## Stand-in spec keys for enemy `base_id`: {scene, yaw_deg, ...} when it has a model, else {}.
static func stand_in_overrides(base_id: String) -> Dictionary:
	var path := str(models().get(base_id, ""))
	if path == "":
		return {}
	var row := CreatureActor.row_for(creature_for_scene(path))
	var out := (row.get("stand_in", {}) as Dictionary).duplicate()
	out["scene"] = path
	return out
