class_name AccessibilityMenuModel
extends SettingsPageModel
## Logic of the Accessibility settings page (M2-UI-09; SPEC §6.11; tech/ui.md § Accessibility),
## no nodes. One row per UiSettings setting, in accessibility.json order (reduced motion, text
## size, color palette, timing assist); each shows its option's loc key (a bool shows On / Off).
## cycle() steps the value through UiSettings.set_value, which every view following the settings
## sees at once (UiSettings.follow), and saves user://settings.cfg.

## The settings it reads and writes (UiSettings.shared() for the game; tests pass their own).
var settings: UiSettings
## Where cycle() saves ("" = do not save; tests).
var config_path := UiSettings.CONFIG_PATH


func _init(with_settings: UiSettings = null, save_path: String = UiSettings.CONFIG_PATH) -> void:
	settings = with_settings if with_settings != null else UiSettings.shared()
	config_path = save_path


## Every UiSettings row but the Audio page's (audio_menu.json, M3-UI-02).
func row_ids() -> Array[StringName]:
	var audio := AudioMenuModel.audio_ids()
	var out: Array[StringName] = []
	for id in settings.settings():
		if not audio.has(id):
			out.append(id)
	return out


func title_key() -> String:
	return "SET_MENU_ACCESSIBILITY"


func label(row: StringName) -> String:
	return tr(str(settings.setting_row(row).get("label_key", row)))


## The value as shown: On / Off for a bool, else the option's loc key.
func value_text(row: StringName) -> String:
	var value: Variant = settings.get_value(row)
	var info := settings.setting_row(row)
	if str(info.get("type", "")) == UiSettings.KIND_BOOL:
		return tr("GFX_VALUE_ON" if bool(value) else "GFX_VALUE_OFF")
	var keys: Array = info.get("option_keys", [])
	var at := _index_of(row, value)
	return tr(str(keys[at])) if at >= 0 and at < keys.size() else str(value)


func cycle(delta: int) -> bool:
	var row := current()
	var opts := settings.options(row)
	if opts.is_empty():
		return false
	var next: Variant = opts[posmod(_index_of(row, settings.get_value(row)) + delta, opts.size())]
	if next == settings.get_value(row) or not settings.set_value(row, next):
		return false
	if config_path != "":
		settings.save_to(config_path)
	changed.emit()
	return true


func help_key() -> String:
	return str(settings.setting_row(current()).get("help_key", ""))


func _index_of(row: StringName, value: Variant) -> int:
	var opts := settings.options(row)
	for i in opts.size():
		if typeof(opts[i]) in [TYPE_INT, TYPE_FLOAT] and typeof(value) in [TYPE_INT, TYPE_FLOAT]:
			if is_equal_approx(float(opts[i]), float(value)):
				return i
		elif opts[i] == value:
			return i
	return 0
