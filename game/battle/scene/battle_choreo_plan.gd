class_name BattleChoreoPlan
extends RefCounted
## The choreography's plan, as pure data (M2-BPR-01; moved out of BattleChoreo under the lint cap, no behaviour
## change): which style an action plays, and its beat times, reactions and KOs. BattleChoreo's plan_for(), style()
## and style_id_for() call these with its data and engine; tests call either.


## The style an action plays: item_style for an item, else style_by_skill, swell_style_by_hero (a Swell technique),
## style_by_actor, style_by_target, style_by_kind.
static func style_id_for(data: Dictionary, engine: BattleEngine, result: ActionResult) -> String:
	if result.item_id != &"":
		return str(data.get("item_style", BattleChoreo.FALLBACK_STYLE))
	var sid := String(result.skill_id)
	var by_skill := data.get("style_by_skill", {}) as Dictionary
	if by_skill.has(sid):
		return str(by_skill[sid])
	var row: Dictionary = engine.db.skill(result.skill_id) if engine != null else {}
	var swells := data.get("swell_style_by_hero", {}) as Dictionary
	var hero := String(result.actor_id).get_slice("#", 0)
	if bool(row.get("swell", false)) and swells.has(hero):  # M3-BPR-422: a Swell technique with no row of its own
		return str(swells[hero])
	var actors := data.get("style_by_actor", {}) as Dictionary
	var by_actor := actors.get(String(result.actor_id).get_slice("#", 0), {}) as Dictionary
	if by_actor.has(str(row.get("kind", ""))):  # M3-BPR-408: the Avalanche Ram's charge
		return str(by_actor[str(row["kind"])])
	var by_target := data.get("style_by_target", {}) as Dictionary
	if by_target.has(str(row.get("target", ""))):
		return str(by_target[str(row["target"])])
	return str((data.get("style_by_kind", {}) as Dictionary).get(str(row.get("kind", "")), BattleChoreo.FALLBACK_STYLE))


static func style(data: Dictionary, id: String) -> Dictionary:
	var styles := data.get("styles", {}) as Dictionary
	return styles.get(id, styles.get(BattleChoreo.FALLBACK_STYLE, {})) as Dictionary


## What an action plays, with no nodes: {style, actor, targets, reactions [{target, kind}], kos, and the beat
## times approach_end, contact, strike_end, recover_end, return_end, ko_at, total}. {} for a failed action.
static func plan_for(data: Dictionary, engine: BattleEngine, result: ActionResult) -> Dictionary:
	if result == null or not result.ok:
		return {}
	var sid := style_id_for(data, engine, result)
	var st := style(data, sid)
	var a := float(st.get("approach_sec", 0.0))
	var s := float(st.get("strike_sec", 0.0))
	var c := a + s * float(st.get("contact_at", 1.0))
	var rec := a + s + float(st.get("recover_sec", 0.0))
	var ret := rec + float(st.get("return_sec", 0.0))
	var targets: Array[StringName] = []
	var reactions: Array[Dictionary] = []
	var kos: Array[StringName] = []
	var peak := 0.0
	var stagger := float(st.get("stagger_sec", 0.0))
	var riposte := a + s + float((data.get("counter", {}) as Dictionary).get("delay_sec", 0.0))
	for hit: Dictionary in result.hits:
		var tid := StringName(str(hit.get("target_id", "")))
		var by := StringName(str(hit.get("counter_by", "")))  # M3-BPR-406: a counter stance answers the actor
		if not targets.has(tid) and by == &"":
			targets.append(tid)
		if tid == result.actor_id and by == &"":
			continue
		var amount := int(hit.get("amount", 0))
		var kind := (
			BattleChoreo.REACT_MISS
			if not bool(hit.get("hit", true))
			else (BattleChoreo.REACT_DAMAGE if amount > 0 else "")
		)
		if kind == "" and amount < 0:
			kind = BattleChoreo.REACT_HEAL
		elif kind == "" and int(hit.get("delay_ticks", 0)) > 0:
			kind = BattleChoreo.REACT_PUSH
		elif kind == "" and _immune(engine, tid, result.skill_id):
			kind = BattleChoreo.REACT_IMMUNE  # M3-BPR-406: the blow lands on nothing it can hurt
		var blow := BattleImpact.strength(data, engine, hit)  # M3-BPR-401: the blow's weight
		peak = maxf(peak, blow)
		if kind != "":
			var w := BattleImpact.recoil_weight(data, blow) if kind == BattleChoreo.REACT_DAMAGE else 1.0
			var at := riposte if by != &"" else c + stagger * reactions.size()
			reactions.append({"target": tid, "kind": kind, "at": at, "weight": w, "counter_by": by})
		var t := engine.find(tid) if engine != null else null
		if amount > 0 and t != null and t.hp <= 0 and not kos.has(tid):
			kos.append(tid)
	var plan := {
		"style": sid,
		"shot": str(st.get("shot", "")),
		"actor": result.actor_id,
		"skill": result.skill_id,  # M3-BPR-420: a boss's big moves get their own shot (camera.enemy_by_skill)
		"targets": targets,
		"reactions": reactions,
		"kos": kos,
		"impact": peak,
		"approach_end": a,
		"contact": c,
		"strike_end": a + s,
		"recover_end": rec,
		"return_end": ret,
	}
	retime(data, plan)
	return plan


## Sets a plan's ko_at (a felled target collapses after its own reaction starts) and total from its reactions'
## start times (`at`: the contact, staggered by stagger_sec, or delayed by a wave's travel).
static func retime(data: Dictionary, plan: Dictionary) -> void:
	var reaction := data.get("reaction", {}) as Dictionary
	var kos: Array = plan["kos"]
	var react_end := float(plan["contact"])
	var ko_from := react_end
	var riposte_end := -1.0
	for r: Dictionary in plan["reactions"]:
		var at := float(r["at"])
		var end := at + float((reaction.get(r["kind"], {}) as Dictionary).get("sec", 0.0))
		react_end = maxf(react_end, end)
		if str(r.get("counter_by", "")) != "":
			riposte_end = maxf(riposte_end, end)
		if kos.has(r["target"]):
			ko_from = maxf(ko_from, at)
	# The attacker stays where it struck until the riposte has landed on it and played out, then goes home (the
	# self-rendered battle_ch08_counter showed it already back on its mark when the answer landed).
	var hold := riposte_end - float(plan["recover_end"])
	if hold > 0.0:
		plan["recover_end"] = float(plan["recover_end"]) + hold
		plan["return_end"] = float(plan["return_end"]) + hold
	if kos.has(plan["actor"]):  # felled by a counter: it falls once it is home (M3-BPR-406)
		ko_from = maxf(ko_from, float(plan["return_end"]))
	var ko := data.get("ko", {}) as Dictionary
	plan["ko_at"] = ko_from + float(ko.get("delay_sec", 0.0))
	var total := maxf(float(plan["return_end"]), react_end)
	if not kos.is_empty():
		total = maxf(total, float(plan["ko_at"]) + float(ko.get("collapse_sec", 0.0)))
	plan["total"] = total


## How far a melee run goes along `dir` from `from` (M3-BPR-402): stop_short_m short of the aim, and never so far
## that the actor (radius `ra`), at the end of its lunge, comes within its radius + a body's radius + clearance_m
## (choreo.json spacing) of any body in its path. `bodies`: [[position, radius], ...] of everyone else on the field.
static func melee_gap(
	data: Dictionary, st: Dictionary, from: Vector3, dir: Vector3, aim: Vector3, bodies: Array, ra: float
) -> float:
	var gap := BattleChoreo._flat_len(aim - from) - float(st.get("stop_short_m", 0.0))
	var clear := float((data.get("spacing", {}) as Dictionary).get("clearance_m", 0.0)) + float(st.get("lunge_m", 0.0))
	for b: Array in bodies:
		var rel := (b[0] as Vector3) - from
		rel.y = 0.0
		var along := rel.dot(dir)
		if along <= 0.0:
			continue  # behind the actor
		var side := (rel - dir * along).length()
		var need := ra + float(b[1]) + clear
		if side < need:
			gap = minf(gap, along - sqrt(need * need - side * side))
	return maxf(gap, 0.0)


## A melee run's direction and length (M3-BPR-402): straight at `aim` unless a body beside the path stops it short;
## then it turns by spacing.detour_step_deg each way, up to detour_max_deg, and takes the smallest turn whose run
## ends within detour_reach_m of where an unobstructed run (only `target_bodies` in the way) would. {dir, gap}.
static func melee_approach(
	data: Dictionary, st: Dictionary, from: Vector3, aim: Vector3, bodies: Array, target_bodies: Array, ra: float
) -> Dictionary:
	var dir := BattleChoreo._flat(aim - from)
	var best := {"dir": dir, "gap": melee_gap(data, st, from, dir, aim, bodies, ra)}
	var sp := data.get("spacing", {}) as Dictionary
	var step := float(sp.get("detour_step_deg", 0.0))
	if dir == Vector3.ZERO or step <= 0.0:
		return best
	var ideal := from + dir * melee_gap(data, st, from, dir, aim, target_bodies, ra)
	var reach := BattleChoreo._flat_len(aim - ideal) + float(sp.get("detour_reach_m", 0.0))
	if BattleChoreo._flat_len(aim - (from + dir * float(best["gap"]))) <= reach:
		return best
	var deg := step
	while deg <= float(sp.get("detour_max_deg", 0.0)) + 0.001:
		for sgn: float in [1.0, -1.0]:
			var d := dir.rotated(Vector3.UP, deg_to_rad(deg * sgn))
			var g := melee_gap(data, st, from, d, aim, bodies, ra)
			if BattleChoreo._flat_len(aim - (from + d * g)) <= reach:
				return {"dir": d, "gap": g}
		deg += step
	return best


## A fighter model's footprint radius on the ground (M3-BPR-402): the mean of its visible meshes' half-width and
## half-depth about the stand-in's origin, times spacing.footprint_k. -1 for a primitive stand-in (no model).
static func footprint(f: Node3D, data: Dictionary) -> float:
	if f == null or (BattleClips.player_of(f) == null and BattleClips.creature_of(f) == null):
		return -1.0
	var lo := Vector3.INF
	var hi := -Vector3.INF
	var inv := f.global_transform.affine_inverse()
	for n in f.find_children("*", "VisualInstance3D", true, false):
		var vi := n as VisualInstance3D
		if not vi.is_visible_in_tree() or vi is Light3D:
			continue
		var box := (inv * vi.global_transform) * vi.get_aabb()
		lo = lo.min(box.position)
		hi = hi.max(box.end)
	if not lo.is_finite() or not hi.is_finite():
		return -1.0
	var half_x := maxf(-lo.x, hi.x)
	var half_z := maxf(-lo.z, hi.z)
	return (half_x + half_z) * 0.5 * float((data.get("spacing", {}) as Dictionary).get("footprint_k", 1.0))


## [offset, toward, lean_deg] for a target's reaction `r` at plan time `t` (home when its own clip plays it, except
## clip_recoil_k of the root push). `react_k` is the style's react_scale (a heavy blow, the toll, recoils harder);
## `tilt_k` scales the tilt (reduced motion). Moved from BattleChoreo (its line cap).
static func reaction_pose(
	data: Dictionary, r: Dictionary, t: float, contact: float, react_k: float, tilt_k: float
) -> Array:
	var away: Vector3 = r["dir"]
	var def := (data.get("reaction", {}) as Dictionary).get(r["kind"], {}) as Dictionary
	var sec := float(def.get("sec", 0.0))
	var c := float(r.get("at", contact))
	var shoved := str(r["kind"]) in [BattleChoreo.REACT_DAMAGE, BattleChoreo.REACT_PUSH]
	var clip_k := float(def.get("clip_recoil_k", 0.0)) if shoved else 0.0
	if (bool(r["clip"]) and clip_k <= 0.0) or t < c or sec <= 0.0:
		return [Vector3.ZERO, away, 0.0]
	var w := sin(PI * clampf((t - c) / sec, 0.0, 1.0)) * float(r.get("weight", 1.0))  # M3-BPR-401
	if bool(r["clip"]):
		w *= clip_k  # its own hit clip plays in place: a smaller root push under it
	match str(r["kind"]):
		BattleChoreo.REACT_DAMAGE:
			w *= react_k
			return [away * float(def.get("recoil_m", 0.0)) * w, away, float(def.get("tilt_deg", 0.0)) * w * tilt_k]
		BattleChoreo.REACT_PUSH:  # shoved back down the timeline: a stagger, no blow's weight
			return [away * float(def.get("recoil_m", 0.0)) * w, away, float(def.get("tilt_deg", 0.0)) * w * tilt_k]
		BattleChoreo.REACT_IMMUNE:  # a hard stop: a stiff sideways shudder, no recoil, none under reduced motion
			var side := Vector3.UP.cross(away).normalized()
			var buzz := sin(TAU * float(def.get("shudders", 1.0)) * clampf((t - c) / sec, 0.0, 1.0))
			return [side * float(def.get("shudder_m", 0.0)) * buzz * w * tilt_k, away, 0.0]
		BattleChoreo.REACT_HEAL:
			return [Vector3.UP * float(def.get("lift_m", 0.0)) * w, away, 0.0]
		BattleChoreo.REACT_MISS:
			return [Vector3.UP.cross(away).normalized() * float(def.get("dodge_m", 0.0)) * w, away, 0.0]
	return [Vector3.ZERO, away, 0.0]


## True when `tid` is damage-immune now (a set-piece phase) and `skill_id` would have hurt it (a physical or magical
## blow with power).
static func _immune(engine: BattleEngine, tid: StringName, skill_id: StringName) -> bool:
	var t := engine.find(tid) if engine != null else null
	if t == null or not t.damage_immune:
		return false
	var row := engine.db.skill(skill_id)
	return str(row.get("kind", "")) in ["physical", "magical"] and float(row.get("power", 0)) > 0.0
