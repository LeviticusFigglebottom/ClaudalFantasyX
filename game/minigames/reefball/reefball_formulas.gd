class_name ReefballFormulas
extends RefCounted
## Reefball odds (M3-RBL-01, docs/kb/design/reefball.md § Odds). Pure static functions over the
## rules block of rules.json: every coefficient comes from data, so this file holds no tuning
## numbers. ReefballMatch.preview() and perform() both call these, so the odds a player is shown
## are exactly the odds the roll is made against.


## True when `d` is at or below the rules' winded threshold.
static func winded(rules: Dictionary, d: ReefballDiver) -> bool:
	return d.breath <= int(_block(rules, "breath").get("winded_at", 0))


## The odds penalty `d` takes as the actor while winded (0 otherwise).
static func winded_penalty(rules: Dictionary, d: ReefballDiver) -> float:
	return float(_block(rules, "breath").get("winded_penalty", 0.0)) if winded(rules, d) else 0.0


## Clamps contested odds into [odds_min, odds_max]. Only uncontested actions are ever sure.
static func clamp_odds(rules: Dictionary, p: float) -> float:
	return clampf(p, float(rules.get("odds_min", 0.0)), float(rules.get("odds_max", 1.0)))


## The diver with the highest `stat_name` (ties: lowest order). Null for an empty list.
static func best(divers: Array[ReefballDiver], stat_name: String) -> ReefballDiver:
	var top: ReefballDiver = null
	for d in divers:
		if top == null or d.stat(stat_name) > top.stat(stat_name):
			top = d
		elif d.stat(stat_name) == top.stat(stat_name) and d.order < top.order:
			top = d
	return top


## Rise one band with the float. `contesters` are the opponents in the carrier's band and the band
## above. Open water (no contesters) is sure.
static func rise_odds(rules: Dictionary, carrier: ReefballDiver, contesters: Array[ReefballDiver]) -> float:
	if contesters.is_empty():
		return 1.0
	var r := _block(rules, "rise")
	var edge := (carrier.stat("stroke") + carrier.stat("grip")) / 2.0 - best(contesters, "strip").stat("strip")
	var p := (
		float(r["base"])
		+ float(r["edge_k"]) * edge
		- float(r["crowd_k"]) * (contesters.size() - 1)
		- winded_penalty(rules, carrier)
	)
	return clamp_odds(rules, p)


## Pass to a teammate. `markers` are the opponents in the receiver's band. An open pass within
## open_reach bands is sure; a longer open pass loses dist_k per band beyond the first.
static func pass_odds(
	rules: Dictionary, passer: ReefballDiver, receiver: ReefballDiver, markers: Array[ReefballDiver]
) -> float:
	var r := _block(rules, "pass")
	var dist := absi(passer.depth - receiver.depth)
	if markers.is_empty() and dist <= int(r["open_reach"]):
		return 1.0
	var p := (
		float(r["base"])
		+ float(r["skill_k"]) * (passer.stat("reach") + receiver.stat("grip")) / 2.0
		- float(r["dist_k"]) * maxi(0, dist - 1)
		- winded_penalty(rules, passer)
	)
	if not markers.is_empty():
		p -= float(r["mark_k"]) * best(markers, "strip").stat("strip")
		p -= float(r["crowd_k"]) * (markers.size() - 1)
	return clamp_odds(rules, p)


## Loft the float up through the ring from `carrier.depth` (1..max_depth). `wardens` are the
## opponents at the ring and `pressers` the opponents in the carrier's band.
static func loft_odds(
	rules: Dictionary, carrier: ReefballDiver, wardens: Array[ReefballDiver], pressers: Array[ReefballDiver]
) -> float:
	var r := _block(rules, "loft")
	var p := (
		float(r["base"])
		+ float(r["skill_k"]) * carrier.stat("loft")
		- float(r["depth_k"]) * maxi(0, carrier.depth - 1)
		- float(r["press_k"]) * pressers.size()
		- winded_penalty(rules, carrier)
	)
	if not wardens.is_empty():
		p -= float(r["ward_k"]) * best(wardens, "ward").stat("ward")
	return clamp_odds(rules, p)


static func _block(rules: Dictionary, key: String) -> Dictionary:
	return rules.get(key, {}) as Dictionary
