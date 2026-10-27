class_name HeroMotionGuard
extends RefCounted
## The no-snapping guards (M2-HER-1110, ADR 0190): measures sampled motion for snaps and pops, so tests can
## flag them across the field, cutscenes and battle. Limits: game/data/hero_motion/motion_guard.json.
##   transform_snaps(samples, dt, limits)   a visible body's root, one Transform3D per frame: a step faster than
##                                          max_speed_mps or a turn faster than max_yaw_rate_deg_per_sec is a
##                                          snap; a step of cut_m or more is a deliberate cut.
##   clip_change(p, skel, from, to, limits) every bone across a clip change on `p`: a per-frame step well above
##                                          both clips' own largest steps is a pop; so is a cross-fade under
##                                          min_blend_sec.
## Presentation only and node-light: it drives the AnimationPlayer by advance(), so it runs headless.

const DATA_PATH := "res://game/data/hero_motion/motion_guard.json"
const MOVE := &"move"
const TURN := &"turn"
const CUT := &"cut"
## A clip is sampled for its own largest step over at most this many loops of it.
const OWN_LOOPS := 1


static func load_data(path: String = DATA_PATH) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("HeroMotionGuard: cannot read %s" % path)
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


## Seconds per sampled frame.
static func frame_sec(data: Dictionary) -> float:
	return 1.0 / float(data.get("frame_hz", 60.0))


## The heading of `t` about +Y (radians), from its basis' Z axis on the ground plane.
static func yaw_of(t: Transform3D) -> float:
	var z := t.basis.z
	return atan2(z.x, z.z)


## The frames of `samples` (one per `dt`) that snap: [{frame, kind (MOVE, TURN or CUT), value}], value in m/s,
## deg/s or metres for a CUT. `limits` is motion_guard.json's "transform" block.
static func transform_snaps(samples: Array[Transform3D], dt: float, limits: Dictionary) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var max_speed := float(limits.get("max_speed_mps", 0.0))
	var max_turn := float(limits.get("max_yaw_rate_deg_per_sec", 0.0))
	var cut_m := float(limits.get("cut_m", INF))
	for i in range(1, samples.size()):
		var step := samples[i].origin.distance_to(samples[i - 1].origin)
		if step >= cut_m:
			out.append({"frame": i, "kind": CUT, "value": step})
			continue
		if step / dt > max_speed:
			out.append({"frame": i, "kind": MOVE, "value": step / dt})
		var turn := rad_to_deg(absf(angle_difference(yaw_of(samples[i - 1]), yaw_of(samples[i])))) / dt
		if turn > max_turn:
			out.append({"frame": i, "kind": TURN, "value": turn})
	return out


## The snaps among `found` (transform_snaps' result) that are not deliberate cuts.
static func snaps_only(found: Array[Dictionary]) -> Array[Dictionary]:
	return found.filter(func(s: Dictionary) -> bool: return s["kind"] != CUT)


## The fastest step (m/s) and turn (deg/s) in `samples` (one per `dt`), cuts of `cut_m` or more left out:
## {speed, turn}. What the field and cutscene audits print next to their verdicts.
static func peak_rates(samples: Array[Transform3D], dt: float, cut_m: float = INF) -> Dictionary:
	var speed := 0.0
	var turn := 0.0
	for i in range(1, samples.size()):
		var step := samples[i].origin.distance_to(samples[i - 1].origin)
		if step >= cut_m:
			continue
		speed = maxf(speed, step / dt)
		turn = maxf(turn, rad_to_deg(absf(angle_difference(yaw_of(samples[i - 1]), yaw_of(samples[i])))) / dt)
	return {"speed": speed, "turn": turn}


## Every bone's position in world space (metres).
static func bone_points(skel: Skeleton3D) -> PackedVector3Array:
	var out := PackedVector3Array()
	var xf := skel.global_transform
	for i in skel.get_bone_count():
		out.append(xf * skel.get_bone_global_pose(i).origin)
	return out


## The largest distance any bone moved between two bone_points() samples.
static func max_bone_step(a: PackedVector3Array, b: PackedVector3Array) -> float:
	var top := 0.0
	for i in mini(a.size(), b.size()):
		top = maxf(top, a[i].distance_to(b[i]))
	return top


## The largest per-frame bone step while `clip` plays on its own from its start (no blend), over its length
## (OWN_LOOPS loops of a looping clip); the first frame, which jumps from whatever came before, is skipped.
static func own_peak(p: AnimationPlayer, skel: Skeleton3D, clip: StringName, dt: float) -> float:
	p.play(clip, 0.0)
	p.seek(0.0, true)
	var frames := ceili(p.get_animation(clip).length * OWN_LOOPS / dt)
	p.advance(dt)
	var prev := bone_points(skel)
	var top := 0.0
	for i in frames:
		p.advance(dt)
		var now := bone_points(skel)
		top = maxf(top, max_bone_step(prev, now))
		prev = now
	return top


## The cross-fade `p` uses from `from` to `to`: its pair blend time, else its default.
static func blend_of(p: AnimationPlayer, from: StringName, to: StringName) -> float:
	var t := p.get_blend_time(from, to)
	return t if t > 0.0 else p.playback_default_blend_time


## Measures the change from `from` to `to` on `p` as the battle and the field make it: a looping `from` is
## left after `limits.window_sec` by play(to); a one-shot `from` runs out into a queued `to`. Returns
## {from, to, blend, peak, own, gap, allowed, pop, cut}: peak is the largest per-frame bone step over
## window_sec from the change; own the larger of the two clips' own peaks; gap the largest bone distance from
## the last frame before the change to the frame the blend ends on. A blend may move a bone by its share of
## the gap per frame (gap * dt / blend) on top of the clips' own motion, each times step_ratio, plus slack_m:
## more is a pop. A blend under one frame earns no gap share. cut when the blend is under min_blend_sec.
## `limits` is motion_guard.json's "clips" block.
static func clip_change(
	p: AnimationPlayer, skel: Skeleton3D, from: StringName, to: StringName, limits: Dictionary, dt: float
) -> Dictionary:
	var own := maxf(own_peak(p, skel, from, dt), own_peak(p, skel, to, dt))
	var window := float(limits.get("window_sec", 0.0))
	var src := p.get_animation(from)
	var loops := src.loop_mode != Animation.LOOP_NONE
	p.play(from, 0.0)
	p.seek(0.0, true)
	var lead := window if loops else src.length
	if not loops:
		p.queue(to)
	var blend := blend_of(p, from, to)
	var prev := PackedVector3Array()
	var before := PackedVector3Array()
	var peak := 0.0
	var gap := 0.0
	var t := 0.0
	var watch_from := lead - dt
	while t < lead + window:
		if loops and t >= lead and StringName(p.current_animation) != to:
			p.play(to)
		p.advance(dt)
		t += dt
		var now := bone_points(skel)
		if t >= watch_from and not prev.is_empty():
			peak = maxf(peak, max_bone_step(prev, now))
			if before.is_empty():
				before = prev
		if not before.is_empty() and t <= lead + maxf(blend, dt) + dt * 0.5:
			gap = max_bone_step(before, now)
		prev = now
	var ratio := float(limits.get("step_ratio", 1.0))
	var share := gap * dt / blend if blend >= dt else 0.0
	var allowed := (own + share) * ratio + float(limits.get("slack_m", 0.0))
	return {
		"from": from,
		"to": to,
		"blend": blend,
		"peak": peak,
		"own": own,
		"gap": gap,
		"allowed": allowed,
		"pop": peak > allowed,
		"cut": blend < float(limits.get("min_blend_sec", 0.0)),
	}
