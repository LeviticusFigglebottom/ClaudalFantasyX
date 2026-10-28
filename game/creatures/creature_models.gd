class_name CreatureModels
extends RefCounted
## Which enemies have a creature model (M2-CRE-03). enemies.json's `model` names a creature actor scene; the
## battle stage shows it through FighterStandIn's `scene` hook (M2-UI-07), with creatures.json's `stand_in`
## overrides (the yaw that turns a +Z-facing model toward the party). Visual only: the engine never reads `model`.
## A Vowbound (M3-CRE-638) has no enemies.json row: its creatures.json row has its id and `vowbound` true.

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


## The creatures.json row id that is Vowbound `base_id`'s actor (M3-CRE-638): the row with that id when it carries
## `vowbound` true and a `scene` (&"" otherwise). The Vowbound has no enemies.json row, so its row is found by id.
static func vowbound_creature(base_id: String) -> StringName:
	var raw: Variant = (CreatureActor.data().get("creatures", {}) as Dictionary).get(base_id, null)
	if typeof(raw) != TYPE_DICTIONARY:
		return &""
	var row := raw as Dictionary
	if not bool(row.get("vowbound", false)) or str(row.get("scene", "")) == "":
		return &""
	return StringName(base_id)


## Stand-in spec keys for combatant `base_id`: {scene, yaw_deg, ...} when it is an enemy with a model or a Vowbound
## with a creature actor (M3-CRE-638), else {}.
static func stand_in_overrides(base_id: String) -> Dictionary:
	var path := str(models().get(base_id, ""))
	var creature := &""
	if path != "":
		creature = creature_for_scene(path)
	else:
		creature = vowbound_creature(base_id)
		if creature == &"":
			return {}
		path = str(CreatureActor.row_for(creature)["scene"])
	var out := (CreatureActor.row_for(creature).get("stand_in", {}) as Dictionary).duplicate()
	out["scene"] = path
	return out
