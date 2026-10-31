extends TestCase
## ZoneKitDressing's ambient life (env-art-b's Act II pass, 2026-10-30): Hollowmere's oil flames flicker and the tide's
## litter rides the swell off the dock. A flicker only ever dims a light (never past its "flicker" share); a drifting
## piece stays within its eddy and bob of where it was placed.

const ZONE := "res://game/levels/ch17/hollowmere/hollowmere.tscn"
const LAYOUT := "res://game/levels/ch17/hollowmere/hollowmere_dressing.json"
const DEBRIS := "tide_debris"
const STEP_S := 0.37
const STEPS := 40
const SLACK := 0.001


func test_flames_flicker_and_debris_drifts() -> void:
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(LAYOUT))
	var flickers := 0
	for r: Variant in layout["fire_lights"]:
		flickers += 1 if (r as Dictionary).has(ZoneKitDressing.KEY_FLICKER) else 0
	assert_true(flickers > 0, "Hollowmere's flames flicker")
	var zone := (load(ZONE) as PackedScene).instantiate() as Node3D
	var tree := Engine.get_main_loop() as SceneTree
	var host: Node = tree.current_scene if tree.current_scene != null else tree.root
	host.add_child(zone)
	var dressing := zone.get_node(^"Dressing") as ZoneKitDressing
	var lights := dressing.get_node(NodePath(String(ZoneKitDressing.FIRE_LIGHTS))).get_children()
	var base: Array[float] = []
	for l: Node in lights:
		base.append((l as OmniLight3D).light_energy)
	var debris: Array[Node3D] = []
	for p: Node in dressing.get_children():
		if p is Node3D and p.get_child_count() > 0 and String(p.get_child(0).name) == DEBRIS:
			debris.append(p as Node3D)
	var drift_rows: Array = layout["pieces"].filter(func(r: Dictionary) -> bool: return r["piece"] == DEBRIS)
	assert_eq(debris.size(), drift_rows.size(), "every drift row is dressed")
	assert_true(debris.size() > 0, "the tide's litter is afloat")
	var placed: Array[Vector3] = []
	for d in debris:
		placed.append(d.position)
	var moved := false
	var dimmed := false
	for i in STEPS:
		dressing._process(STEP_S)
		for k in lights.size():
			var e := (lights[k] as OmniLight3D).light_energy
			assert_true(e <= base[k] + SLACK, "a flicker never brightens %s" % lights[k].name)
			assert_true(
				e >= base[k] * (1.0 - float(layout["fire_lights"][k].get("flicker", 0.0))) - SLACK,
				"nor dims past its share"
			)
			dimmed = dimmed or e < base[k] - SLACK
		for k in debris.size():
			var row: Dictionary = drift_rows[k]["drift"]
			var off := debris[k].position - placed[k]
			moved = moved or off.length() > SLACK
			assert_true(
				Vector2(off.x, off.z).length() <= 2.0 * float(row["wander_m"]) + SLACK, "%s stays in its eddy" % k
			)
			assert_true(absf(off.y) <= 2.0 * float(row["bob_m"]) + SLACK, "%s bobs, never sinks" % k)
	assert_true(dimmed, "the flames flicker")
	assert_true(moved, "the litter drifts")
	host.remove_child(zone)
	zone.free()


func test_a_zone_fire_fade_reaches_every_lamp() -> void:
	var dressing := ZoneKitDressing.new()
	dressing.layout = {
		ZoneKitDressing.KEY_FIRE: [{"at": [0, 1, 0]}, {"at": [5, 1, 0], "flicker": 0.2}],
		ZoneKitDressing.KEY_FIRE_FADE: [70.0, 20.0],
	}
	dressing._place_fire_lights()
	var lights := dressing.get_node(NodePath(String(ZoneKitDressing.FIRE_LIGHTS))).get_children()
	assert_eq(lights.size(), 2, "both lamps")
	for l: Node in lights:
		var o := l as OmniLight3D
		assert_true(o.distance_fade_enabled, "%s fades with distance" % o.name)
		assert_eq(o.distance_fade_begin, 70.0, "from 70 m")
		assert_eq(o.distance_fade_length, 20.0, "over 20 m")
	dressing.free()


func test_fill_lights_are_shadowless_and_out_of_the_fog() -> void:
	var dressing := ZoneKitDressing.new()
	dressing.layout = {
		ZoneKitDressing.KEY_FILL: [{"pitch_deg": -25.0, "yaw_deg": -135.0, "color": "#9FB4C8", "energy": 0.6}],
	}
	dressing._place_fill_lights()
	var lights := dressing.get_node(NodePath(String(ZoneKitDressing.FILL_LIGHTS))).get_children()
	assert_eq(lights.size(), 1, "one fill")
	var l := lights[0] as DirectionalLight3D
	assert_false(l.shadow_enabled, "a fill casts no shadow (the cutscene stage takes shadowed lights for the key)")
	assert_eq(l.light_volumetric_fog_energy, 0.0, "fog-lamp rule")
	assert_between(l.light_energy, 0.599, 0.601, "its energy")
	dressing.free()
