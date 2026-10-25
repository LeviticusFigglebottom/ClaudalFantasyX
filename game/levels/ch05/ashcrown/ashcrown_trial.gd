class_name AshcrownTrial
extends RefCounted
## The Ashcrown trial's rules (M3-C05-02; act1_ch05.md B08): catch a strike at the crown and walk it
## down the copper veins tier by tier before it fades. Headless and deterministic, no nodes, like
## ShellShrineTrial. Data: game/data/trials/ashcrown.json (see its "doc"). The zone root
## (Ch05AshcrownZone) is a view of this: its levers, gates, plates and rods call the methods below,
## it reports the metres the party walks, and it shows what the signals say.
##   catch(tier)      the tier's catch-rod charges its bowl and lights the stud ring
##   turn(gate)       one 90° step (its linked twin turns with it); resets the idle clock
##   stand(plate)     the party member on the tier's plates moves to `plate`
##   walk(metres)     darkens a stud every metres_per_stud; the last one fades the charge
##   release(tier)    the strike runs the traced veins: on to the next tier, or lost
##   advance(dt)      counts idle time toward the one hint (never a fail clock)
## No outcome fails the trial: a lost charge is caught again at the tier where it was lost.

signal caught(tier: int)
signal stud_dark(left: int)
signal faded(tier: int)
## A release ran: `outcome` is one of the OUT_* ids; `path` is the traced nodes.
signal ran(tier: int, path: Array[StringName], outcome: StringName)
signal rotated(gate: StringName, rotation: int)
signal plate_moved(plate: StringName)
signal alcove_opened
signal landed
signal hint_due

const DATA_PATH := "res://game/data/trials/ashcrown.json"
const SPOUT := &"spout"
const GROUND := &"ground"
const SEAL := &"seal"
const NONE := &"none"
## release() outcomes.
const OUT_NEXT := &"next"
const OUT_LANDED := &"landed"
const OUT_GROUND := &"ground"
const OUT_SEAL := &"seal"
const OUT_OPEN := &"open"

var data: Dictionary = {}
## The tier the strike is on (charged) or was lost on: the only tier whose pieces answer.
var tier := 0
var charged := false
var studs_left := 0
var walked_m := 0.0
## gate id -> rotation, for every rotating gate of every tier.
var rotations: Dictionary = {}
## The plate the party member stands on (tier 4), or &"".
var plate_held: StringName = &""
var alcove_open := false
var done := false
var turns := 0
var idle_sec := 0.0
var hint_given := false


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("ashcrown")) != TYPE_DICTIONARY:
		push_error("AshcrownTrial: could not read 'ashcrown' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["ashcrown"] as Dictionary


func _init(d: Dictionary = {}) -> void:
	data = d if not d.is_empty() else load_data()
	for t: Dictionary in tiers():
		var g: Dictionary = t.get("gates", {})
		for id: String in g.keys():
			if not bool((g[id] as Dictionary).get("plate", false)):
				rotations[StringName(id)] = int((g[id] as Dictionary).get("rotation", 0))
		if t.has("plate_start"):
			plate_held = StringName(str(t["plate_start"]))


func tiers() -> Array:
	return data.get("tiers", []) as Array


func tier_count() -> int:
	return tiers().size()


func tier_id(index: int) -> StringName:
	return StringName(str((tiers()[index] as Dictionary).get("id", ""))) if index < tier_count() else &""


## The index of tier `id`, or -1.
func tier_index(id: StringName) -> int:
	for i in tier_count():
		if tier_id(i) == id:
			return i
	return -1


func steps() -> int:
	return maxi(int(data.get("steps", 4)), 1)


func studs() -> int:
	return maxi(int(data.get("studs", 1)), 1)


## The tier index a gate or plate belongs to, or -1.
func tier_of(gate: StringName) -> int:
	for i in tier_count():
		if (_gates(i)).has(String(gate)):
			return i
	return -1


## The node gate `gate` faces now (a plate faces its one outlet, or `none` while nobody stands on it).
func outlet(gate: StringName) -> StringName:
	var row: Dictionary = _gates(tier_of(gate)).get(String(gate), {})
	var outs: Array = row.get("outlets", [])
	if outs.is_empty():
		return NONE
	if bool(row.get("plate", false)):
		return StringName(str(outs[0])) if plate_held == gate else NONE
	return StringName(str(outs[int(rotations.get(gate, 0)) % outs.size()]))


## Where tier `index`'s strike runs now: its bowl's first gate, then each outlet, ending on the
## first node that is not a gate (a loop ends on `none`: the circuit never closes).
func trace(index: int = -1) -> Array[StringName]:
	var t := tier if index < 0 else index
	var path: Array[StringName] = []
	if t >= tier_count():
		return path
	var gates := _gates(t)
	var node := StringName(str((tiers()[t] as Dictionary).get("bowl_into", "")))
	while node != &"":
		if path.has(node):
			path.append(NONE)
			break
		path.append(node)
		if not gates.has(String(node)):
			break
		node = outlet(node)
	return path


## The tier's catch-rod charges its bowl. False unless `id` is the current tier and it is dark.
func catch(id: StringName) -> bool:
	if done or charged or tier_index(id) != tier:
		return false
	_charge()
	caught.emit(tier)
	return true


## Turns `gate` one step (and its linked twin). False for a plate, another tier's gate, or once done.
func turn(gate: StringName) -> bool:
	if done or not rotations.has(gate) or tier_of(gate) != tier:
		return false
	_rotate(gate)
	var twin := StringName(str((_gates(tier).get(String(gate), {}) as Dictionary).get("linked", "")))
	if twin != &"" and rotations.has(twin):
		_rotate(twin)
	turns += 1
	idle_sec = 0.0
	return true


## Moves the party member on the plates to `plate` (this tier's). False otherwise.
func stand(plate: StringName) -> bool:
	var row: Dictionary = _gates(tier).get(String(plate), {})
	if done or not bool(row.get("plate", false)) or plate_held == plate:
		return false
	plate_held = plate
	idle_sec = 0.0
	plate_moved.emit(plate)
	return true


## The party walked `metres`: while charged, a stud goes dark every metres_per_stud.
func walk(metres: float) -> void:
	if not charged or metres <= 0.0:
		return
	walked_m += metres
	var per := maxf(float(data.get("metres_per_stud", 1.0)), 0.01)
	while charged and walked_m >= per:
		walked_m -= per
		studs_left -= 1
		stud_dark.emit(studs_left)
		if studs_left <= 0:
			charged = false
			walked_m = 0.0
			faded.emit(tier)


## Pulls tier `id`'s release. Returns the outcome (OUT_*), or &"" when refused (another tier, no
## charge, or done). OUT_OPEN keeps the charge in the bowl; ground and seal lose it.
func release(id: StringName) -> StringName:
	if done or not charged or tier_index(id) != tier:
		return &""
	var path := trace()
	var end: StringName = path.back() if not path.is_empty() else NONE
	var out := OUT_OPEN
	match end:
		SPOUT:
			if tier + 1 >= tier_count():
				out = OUT_LANDED
			else:
				out = OUT_NEXT
		GROUND:
			out = OUT_GROUND
		SEAL:
			out = OUT_SEAL
	if out != OUT_OPEN:
		charged = false
		walked_m = 0.0
	idle_sec = 0.0
	ran.emit(tier, path, out)
	match out:
		OUT_NEXT:
			tier += 1
			_charge()
			caught.emit(tier)
		OUT_LANDED:
			done = true
			landed.emit()
		OUT_SEAL:
			if not alcove_open:
				alcove_open = true
				alcove_opened.emit()
	return out


func advance(delta: float) -> void:
	if done:
		return
	idle_sec += delta
	if not hint_given and idle_sec >= float(data.get("hint_idle_sec", INF)):
		hint_given = true
		hint_due.emit()


## The fewest moves (gate turns and plate moves) from tier `index`'s current state that close its
## circuit to the spout, or -1 if none. A breadth-first search; tests use it.
func min_turns(index: int) -> int:
	var gates := _gates(index)
	var ids: Array[StringName] = []
	var plates: Array[StringName] = [&""]
	for id: String in gates.keys():
		if bool((gates[id] as Dictionary).get("plate", false)):
			plates.append(StringName(id))
		else:
			ids.append(StringName(id))
	var probe := AshcrownTrial.new(data)
	probe.tier = index
	var start: Array = []
	for id in ids:
		start.append(int(rotations[id]))
	start.append(maxi(plates.find(plate_held), 0))
	var seen := {str(start): true}
	var frontier: Array = [start]
	var depth := 0
	while not frontier.is_empty():
		var next: Array = []
		for state: Array in frontier:
			for i in ids.size():
				probe.rotations[ids[i]] = int(state[i])
			probe.plate_held = plates[int(state[ids.size()])]
			var path := probe.trace(index)
			if not path.is_empty() and path.back() == SPOUT:
				return depth
			for s2 in _moves(state, ids, plates, gates):
				if not seen.has(str(s2)):
					seen[str(s2)] = true
					next.append(s2)
		frontier = next
		depth += 1
	return -1


func _moves(state: Array, ids: Array[StringName], plates: Array[StringName], gates: Dictionary) -> Array:
	var out: Array = []
	for i in ids.size():
		var s2: Array = state.duplicate()
		s2[i] = (int(s2[i]) + 1) % steps()
		var twin := StringName(str((gates.get(String(ids[i]), {}) as Dictionary).get("linked", "")))
		var j := ids.find(twin)
		if j >= 0:
			s2[j] = (int(s2[j]) + 1) % steps()
		out.append(s2)
	for p in range(1, plates.size()):
		if p != int(state[ids.size()]):
			var s3: Array = state.duplicate()
			s3[ids.size()] = p
			out.append(s3)
	return out


func _charge() -> void:
	charged = true
	studs_left = studs()
	walked_m = 0.0
	idle_sec = 0.0


func _rotate(gate: StringName) -> void:
	rotations[gate] = (int(rotations[gate]) + 1) % steps()
	rotated.emit(gate, int(rotations[gate]))


func _gates(index: int) -> Dictionary:
	if index < 0 or index >= tier_count():
		return {}
	return (tiers()[index] as Dictionary).get("gates", {}) as Dictionary
