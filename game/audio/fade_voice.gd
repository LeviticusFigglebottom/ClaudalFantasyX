class_name FadeVoice
extends RefCounted
## One player with a linear-gain fade (M2-AUD-02). MusicDeck and the ambience beds use it; time passes only
## through step(delta), so tests drive fades frame by frame.

## The player it drives (AudioStreamPlayer or AudioStreamPlayer3D).
var player: Node
## What it is playing (a cue or bed id).
var id: StringName = &""
## Linear gain now, and where the fade is heading (0..1).
var gain := 0.0
var target := 0.0
## Gain per second toward `target` (0 = jump).
var rate := 0.0
## Stop the player once a fade out reaches 0.
var stop_at_zero := true
## The row's own level (dB), added to the fade.
var base_db := 0.0


func _init(p: Node) -> void:
	player = p


## Fades toward `to` over `sec` seconds (0 or less: at once).
func fade_to(to: float, sec: float) -> void:
	target = clampf(to, 0.0, 1.0)
	if sec <= 0.0:
		gain = target
		rate = 0.0
	else:
		rate = absf(target - gain) / sec


func is_active() -> bool:
	return player != null and bool(player.get(&"playing")) and target > 0.0


## Advances the fade, writes volume_db (scaled by `mult`, a 0..1 hold) and stops at silence.
func step(delta: float, floor_db: float, mult: float = 1.0) -> void:
	if gain != target:
		gain = target if rate <= 0.0 else move_toward(gain, target, rate * delta)
	if player == null:
		return
	var g := gain * clampf(mult, 0.0, 1.0)
	var db := linear_to_db(g) if g > 0.0 else -INF
	player.set(&"volume_db", base_db + db if db > floor_db else -80.0)
	if gain <= 0.0 and target <= 0.0 and stop_at_zero and bool(player.get(&"playing")):
		player.call(&"stop")
