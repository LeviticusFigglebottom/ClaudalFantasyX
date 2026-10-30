class_name SaveSlotInfo
extends RefCounted
## One save slot as the save menu shows it (M1-ARC-03). Built from SaveSystem.slot_info(slot);
## every player-facing string comes from game/data/loc/strings.csv.

const SEC_PER_MIN := 60
const SEC_PER_HOUR := 3600
## The longest play time shown (999:59:59); longer journeys stay at the cap.
const PLAY_TIME_DISPLAY_MAX_SEC := 999 * SEC_PER_HOUR + 59 * SEC_PER_MIN + 59

var slot := 0
var status: StringName = &"empty"
var version := -1
var chapter := 0
var play_time_sec := 0.0
var location_id := ""
var location_key := ""
## Unix seconds (UTC).
var saved_at := 0
var reason := ""
## A save made after the wedding trap (Act II, M4-A2P-082): its chapter line carries the heretic tag.
var heretic := false
## The active line when it was saved (party_ids; the row shows their faces).
var party: Array[StringName] = []


static func from_dict(d: Dictionary) -> SaveSlotInfo:
	var info := SaveSlotInfo.new()
	info.slot = int(d.get("slot", 0))
	info.status = StringName(str(d.get("status", "empty")))
	info.version = int(d.get("version", -1))
	info.chapter = int(d.get("chapter", 0))
	info.play_time_sec = float(d.get("play_time_sec", 0.0))
	info.location_id = str(d.get("location_id", ""))
	info.location_key = str(d.get("location_key", ""))
	info.saved_at = int(d.get("saved_at", 0))
	info.reason = str(d.get("reason", ""))
	info.heretic = bool(d.get("heretic", false))
	for v: Variant in d.get("party", []) as Array:
		info.party.append(StringName(str(v)))
	return info


func is_autosave() -> bool:
	return slot == SaveSystem.AUTOSAVE_SLOT


func is_empty() -> bool:
	return status == SaveSystem.STATUS_EMPTY


func is_loadable() -> bool:
	return status == SaveSystem.STATUS_OK


## A file is there (readable or not), so writing to it needs an overwrite confirmation.
func has_file() -> bool:
	return status != SaveSystem.STATUS_EMPTY


func slot_name() -> String:
	if is_autosave():
		return tr("SAVE_SLOT_AUTOSAVE")
	return tr("SAVE_SLOT_NAME_FMT").format({"n": slot})


## "Chapter n"; a save from before Chapter 1 (the prologue, chapter 0) reads "Prologue" (M2-FP-27).
func chapter_text() -> String:
	if chapter <= 0:
		return tr("SAVE_SLOT_PROLOGUE")
	var text := tr("SAVE_SLOT_CHAPTER_FMT").format({"n": chapter})
	return tr("SAVE_SLOT_HERETIC_FMT").format({"chapter": text}) if heretic else text


## The location's display name, or the "unknown place" string when the key has no entry.
func location_name() -> String:
	if location_key != "":
		var t := tr(location_key)
		if t != location_key:
			return t
	return tr("SAVE_LOCATION_UNKNOWN")


func play_time_text() -> String:
	return format_play_time(play_time_sec)


## H:MM:SS, hours unpadded, capped at PLAY_TIME_DISPLAY_MAX_SEC.
func format_play_time(sec: float) -> String:
	var total := clampi(int(floor(sec)), 0, PLAY_TIME_DISPLAY_MAX_SEC)
	var h := floori(total / float(SEC_PER_HOUR))
	var m := floori((total % SEC_PER_HOUR) / float(SEC_PER_MIN))
	var s := total % SEC_PER_MIN
	return tr("SAVE_SLOT_PLAY_TIME_FMT").format({"h": h, "m": "%02d" % m, "s": "%02d" % s})


## The save time in the viewer's time zone: `bias_min` is minutes east of UTC
## (Time.get_time_zone_from_system().bias). Captures pass 0.
func timestamp_text(bias_min: int) -> String:
	if saved_at <= 0:
		return ""
	var dt := Time.get_datetime_dict_from_unix_time(saved_at + bias_min * SEC_PER_MIN)
	var parts := {"year": dt["year"]}
	for k: String in ["month", "day", "hour", "minute"]:
		parts[k] = "%02d" % int(dt[k])
	return tr("SAVE_SLOT_TIMESTAMP_FMT").format(parts)


## The status line shown instead of details for a slot without a readable record ("" when OK).
func status_text() -> String:
	if status == SaveSystem.STATUS_EMPTY:
		return tr("SAVE_SLOT_EMPTY")
	if status == SaveSystem.STATUS_CORRUPT:
		return tr("SAVE_SLOT_CORRUPT")
	if status == SaveSystem.STATUS_NEWER:
		return tr("SAVE_SLOT_NEWER")
	return ""
