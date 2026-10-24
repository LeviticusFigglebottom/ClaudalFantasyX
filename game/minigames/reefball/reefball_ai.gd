class_name ReefballAI
extends RefCounted
## Reefball decision-maker (M3-RBL-01): scores every legal action from its previewed odds with a
## profile from rules.json "ai_profiles" and picks the best. It plays the opposing side, and the
## balance sim also plays the player's side with it ("smart"). Deterministic: the only roll is
## the profile's whim (whim_pct, drawn from the match rng only when it is above 0), which takes
## the second-best action instead.

var profile: Dictionary = {}


func _init(ai_profile: Dictionary = {}) -> void:
	profile = ai_profile


## The chosen action as ReefballMatch.preview() returns it, or {} when there is none.
func choose(m: ReefballMatch) -> Dictionary:
	var options := m.legal_actions()
	if options.is_empty():
		return {}
	var best_i := -1
	var second_i := -1
	var values: Array[float] = []
	for i in options.size():
		values.append(value(m, options[i]))
		if best_i < 0 or values[i] > values[best_i]:
			second_i = best_i
			best_i = i
		elif second_i < 0 or values[i] > values[second_i]:
			second_i = i
	var whim := float(profile.get("whim_pct", 0)) / 100.0
	if whim > 0.0 and second_i >= 0 and m.rng.randf() < whim:
		return options[second_i]
	return options[best_i]


## The profile's value of one previewed option: odds × what a success is worth, less the miss
## chance × turnover_cost. A success is worth score_value when it brings the float up,
## advance_value per band gained toward the ring (toward the weep while the float is unfetched),
## fetch_value when it fetches the float, and fresh_value × the breath a pass hands on.
## A loft below loft_min_odds is never worth taking.
func value(m: ReefballMatch, option: Dictionary) -> float:
	var odds := float(option["odds"])
	var gain := 0.0
	var action: StringName = option["action"]
	if option["scores"]:
		if action == ReefballMatch.LOFT and odds < float(profile.get("loft_min_odds", 0.0)):
			return -INF
		gain = float(profile.get("score_value", 0.0))
	elif action == ReefballMatch.RISE:
		gain = float(profile.get("advance_value", 0.0)) * (1.0 if m.fetched else -1.0)
	elif action == ReefballMatch.DIVE:
		# Down is the way forward only while the float still has to be fetched.
		var toward := 1.0 if not m.fetched else -1.0
		gain = toward * float(profile.get("advance_value", 0.0)) + _fetch_gain(m, int(option["to_depth"]))
	elif action == ReefballMatch.PASS:
		var mate := m.diver(option["target"])
		var up := 1 if m.fetched else -1
		gain = (
			float(profile.get("advance_value", 0.0)) * (m.holder.depth - mate.depth) * up
			+ float(profile.get("fresh_value", 0.0)) * (mate.breath_frac() - m.holder.breath_frac())
			+ _fetch_gain(m, mate.depth)
		)
	return odds * gain - (1.0 - odds) * float(profile.get("turnover_cost", 0.0))


func _fetch_gain(m: ReefballMatch, depth: int) -> float:
	if m.fetched or depth < m.fetch_depth():
		return 0.0
	return float(profile.get("fetch_value", 0.0))
