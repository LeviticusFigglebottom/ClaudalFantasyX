class_name AudioMenuModel
extends AccessibilityMenuModel
## Logic of the Audio settings page (M3-UI-02; SPEC §6.11), no nodes: the UiSettings rows named
## in game/data/ui/audio_menu.json (the volumes AudioDirector applies, M2-AUD-06), shown and
## stepped exactly as the Accessibility page shows its rows, which leaves these out.

const DATA_PATH := "res://game/data/ui/audio_menu.json"


## The ids audio_menu.json lists (whether or not UiSettings has them).
static func audio_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("AudioMenuModel: could not read %s" % DATA_PATH)
		return out
	for id: Variant in ((parsed as Dictionary).get("audio_menu", {}) as Dictionary).get("rows", []):
		out.append(StringName(str(id)))
	return out


func row_ids() -> Array[StringName]:
	var have := settings.settings()
	var out: Array[StringName] = []
	for id in audio_ids():
		if have.has(id):
			out.append(id)
	return out


func title_key() -> String:
	return "SET_MENU_AUDIO"
