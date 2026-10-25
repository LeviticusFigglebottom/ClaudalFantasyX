class_name CoilspireTrial
extends RefCounted
## The rules of Coilspire's flue trial (M3-C08-02; act1_ch08.md §2 B05; data: ch08_field.json "trial").
## No Node, no flags: Ch08CoilspireZone is its view, and keeps its state in flags.
## The spire is a chimney. A Cantor walks the keeping flame up it, tier by tier: each tier has flue-keys
## (copper dampers), and the flame climbs to the next tier when exactly the tier's "draw" keys are open.
##   turn(key)   opens or shuts a key on the current tier. Opening one that isn't in the draw splits the
##               draught: the flame coughs soot and the tier resets (every key shut). There is no fail
##               state and no timer; a wrong setting only resets that tier.
##   side key    a tier's "side" flue (tier 2) draws only when every other key on the tier is shut: then
##               it opens the sealed lamp-niche once (the sailmaker's needle). With any other key open it
##               splits the draught like any wrong key.
##   seized key  a tier's "seized" key won't turn until `freed` (Liss frees it; the zone plays her scene).
##   advance()   the idle clock: after hint_sec on one tier without a turn, hint_due fires (once a tier).

signal turned(key: StringName, open: bool)
signal coughed(tier: int)
signal lit(tier: int)
signal niche_opened
signal seized(key: StringName)
signal hint_due

const OUT_NONE := &""
const OUT_OPEN := &"open"
const OUT_SHUT := &"shut"
const OUT_COUGH := &"cough"
const OUT_LIT := &"lit"
const OUT_NICHE := &"niche"
const OUT_SEIZED := &"seized"
const KEY_TIERS := "tiers"
const KEY_KEYS := "keys"
const KEY_DRAW := "draw"
const KEY_SIDE := "side"
const KEY_SEIZED := "seized"
const KEY_ID := "id"
const KEY_HINT_SEC := "hint_sec"

## The trial's data (ch08_field.json "trial").
var data: Dictionary = {}
## Tiers the flame has climbed (0 .. tier_count()).
var tier := 0
## The open keys on the current tier.
var open: Array[StringName] = []
var niche_open := false
var freed := false

var _idle := 0.0
var _hinted := -1


func _init(trial_data: Dictionary = {}) -> void:
	data = trial_data


## Restores a saved state: `lit_tiers` climbed, the niche opened or not, the seized key freed or not.
func restore(lit_tiers: int, niche: bool, seized_freed: bool) -> void:
	tier = clampi(lit_tiers, 0, tier_count())
	niche_open = niche
	freed = seized_freed
	open.clear()
	_idle = 0.0


func tier_count() -> int:
	return (data.get(KEY_TIERS, []) as Array).size()


func is_done() -> bool:
	return tier >= tier_count()


func tier_id(i: int) -> StringName:
	return StringName(str(_row(i).get(KEY_ID, "")))


## The keys of tier `i`, in data order.
func keys_of(i: int) -> Array[StringName]:
	var out: Array[StringName] = []
	for k: Variant in _row(i).get(KEY_KEYS, []):
		out.append(StringName(str(k)))
	return out


## The tier that owns `key`, or -1.
func tier_of(key: StringName) -> int:
	for i in tier_count():
		if keys_of(i).has(key):
			return i
	return -1


## True when `key` is the current tier's seized key and nobody has freed it yet.
func is_seized(key: StringName) -> bool:
	return not freed and key != &"" and StringName(str(_row(tier).get(KEY_SEIZED, ""))) == key


## Turns `key` (see the class comment). Returns the outcome; OUT_NONE when it isn't on the current tier.
func turn(key: StringName) -> StringName:
	if is_done() or tier_of(key) != tier:
		return OUT_NONE
	if is_seized(key):
		seized.emit(key)
		return OUT_SEIZED
	_idle = 0.0
	var opening := not open.has(key)
	if opening:
		open.append(key)
	else:
		open.erase(key)
	turned.emit(key, opening)
	return _settle(opening)


## The idle clock (seconds), while the trial is live.
func advance(delta: float) -> void:
	if is_done():
		return
	_idle += delta
	if _idle >= float(data.get(KEY_HINT_SEC, INF)) and _hinted != tier:
		_hinted = tier
		hint_due.emit()


func _settle(opening: bool) -> StringName:
	var row := _row(tier)
	var side := StringName(str(row.get(KEY_SIDE, "")))
	var draw: Array[StringName] = []
	for k: Variant in row.get(KEY_DRAW, []):
		draw.append(StringName(str(k)))
	if side != &"" and open.has(side):
		if open.size() > 1:
			return _cough()
		if not niche_open:
			niche_open = true
			niche_opened.emit()
			return OUT_NICHE
		return OUT_OPEN
	for k in open:
		if not draw.has(k):
			return _cough()
	if open.size() == draw.size():
		open.clear()
		tier += 1
		lit.emit(tier - 1)
		return OUT_LIT
	return OUT_OPEN if opening else OUT_SHUT


func _cough() -> StringName:
	open.clear()
	coughed.emit(tier)
	return OUT_COUGH


func _row(i: int) -> Dictionary:
	var tiers: Array = data.get(KEY_TIERS, [])
	return tiers[i] if i >= 0 and i < tiers.size() else {}
