class_name FlagRegistry
extends Resource
## Declares every story flag the game may read or write. Keys are flag names, values are
## human-readable descriptions. tools/validate_data.py fails CI on any undeclared flag usage.

@export var flags: Dictionary = {}
## Why the registry could not be loaded ("" when it was; set by load_path, never saved).
var load_error: String = ""


## Loads a registry resource. A missing or unloadable one gives an empty registry that says why in
## load_error, with a push_error (M1-ARC-13). Game uses it for game/data/flags.tres.
static func load_path(path: String) -> FlagRegistry:
	var reg: FlagRegistry = null
	if ResourceLoader.exists(path):
		reg = ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_REUSE) as FlagRegistry
	if reg == null:
		push_error("FlagRegistry: failed to load %s" % path)
		reg = FlagRegistry.new()
		reg.load_error = "%s is missing or could not be loaded" % path
	return reg


## Why the registry cannot be trusted ("" when it can): it failed to load, or declares no flags.
## Nothing prunes saved flags today, but a story build without its registry is broken, so
## SaveSystem's data-tables gate refuses to save while this is non-empty (M1-ARC-13).
func integrity_problem() -> String:
	if load_error != "":
		return load_error
	if flags.is_empty():
		return "the flag registry declares no flags"
	return ""


func is_declared(flag: StringName) -> bool:
	return flags.has(String(flag))


func description(flag: StringName) -> String:
	return String(flags.get(String(flag), ""))
