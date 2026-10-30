extends Node
## The clip sheet (creatures, 2026-10-29: the Lead's Act I final-quality audit). One row per actor: a close-up, then
## its idle, attack, hit and KO held at set shares of each clip, side on, on a neutral mid-grey floor and a darker
## backdrop (so a dark or a pale body reads). For viewing the clips' poses (feet, popping, a missing reaction) without
## playing a battle. Rendered on the software wrapper as the screenshots are:
## godot-render --path . --rendering-driver vulkan res://tools/creatures/clip_sheet.tscn -- --out=DIR id [id ...]
## (an id is a creatures.json row, or a crowd body: assets/crowd/<id>/<id>_actor.tscn). Writes DIR/<id>.png.

const CELL := Vector2i(256, 256)
const CREATURES := "res://game/data/creatures/creatures.json"
const CROWD_ACTOR := "res://assets/crowd/%s/%s_actor.tscn"
## [clip, share of its length] per cell after the close-up; a missing clip leaves its cell red.
const FOE_CELLS := [
	["idle", 0.0],
	["idle", 0.5],
	["attack", 0.3],
	["attack", 0.45],
	["attack", 0.6],
	["hit", 0.15],
	["hit", 0.35],
	["ko", 0.35],
	["ko", 0.7],
	["ko", 1.0],
]
const NPC_CELLS := [
	["idle", 0.0],
	["idle", 0.5],
	["talk", 0.3],
	["walk", 0.0],
	["walk", 0.25],
	["walk", 0.5],
	["walk", 0.75],
]
const YAW_DEG := 70.0
const PITCH_DEG := 12.0
const FOV_DEG := 30.0
const CLOSE_SHARE := 0.45  # a creature's close-up frames its front share of its length
const NPC_CLOSE_SHARE := 0.22  # a villager's close-up frames the top share of its height: head and shoulders
const CLOSE_YAW_DEG := 25.0
const FLOOR_GREY := Color(0.42, 0.42, 0.42)
const BACK_GREY := Color(0.16, 0.17, 0.19)
const MISSING := Color(0.8, 0.1, 0.1)
const CHECKS := 200.0  # 20 cm checks on the 40 m floor


func _checker() -> ImageTexture:
	var img := Image.create(2, 2, false, Image.FORMAT_RGB8)
	img.set_pixel(0, 0, Color.WHITE)
	img.set_pixel(1, 1, Color.WHITE)
	img.set_pixel(1, 0, Color(0.75, 0.75, 0.75))
	img.set_pixel(0, 1, Color(0.75, 0.75, 0.75))
	return ImageTexture.create_from_image(img)


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var out := ""
	var ids: Array[String] = []
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
		else:
			ids.append(a)
	DirAccess.make_dir_recursive_absolute(out)
	var rows: Dictionary = GreyboxZone.read_json(CREATURES).get("creatures", {})
	for id in ids:
		var path := str((rows.get(id, {}) as Dictionary).get("scene", ""))
		var npc := path == ""
		if npc:
			path = CROWD_ACTOR % [id, id]
		if not ResourceLoader.exists(path):
			print("%s: no scene" % id)
			continue
		var image := await _sheet(load(path) as PackedScene, NPC_CELLS if npc else FOE_CELLS, npc)
		image.save_png(out.path_join("%s.png" % id))
		print("%s: %s" % [id, out.path_join("%s.png" % id)])
	get_tree().quit()


## Holds `spec` ([clip, share]) on the player; false when the actor has no such clip.
func _hold(anim: AnimationPlayer, spec: Array) -> bool:
	var clip := StringName(str(spec[0]))
	if anim == null or not anim.has_animation(clip):
		return false
	anim.speed_scale = 0.0
	anim.play(clip, 0.0)
	anim.seek(float(spec[1]) * anim.get_animation(clip).length, true)
	return true


func _sheet(packed: PackedScene, cells: Array, npc: bool) -> Image:
	var sheet := Image.create(CELL.x * (cells.size() + 1), CELL.y, false, Image.FORMAT_RGBA8)
	var vp := SubViewport.new()
	vp.size = CELL
	vp.own_world_3d = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	var world := Node3D.new()
	vp.add_child(world)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = BACK_GREY
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.55, 0.58, 0.62)
	env.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	world.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50.0, 30.0, 0.0)
	sun.shadow_enabled = true
	world.add_child(sun)
	var floor_mesh := MeshInstance3D.new()
	floor_mesh.mesh = PlaneMesh.new()
	(floor_mesh.mesh as PlaneMesh).size = Vector2(40.0, 40.0)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = FLOOR_GREY
	mat.albedo_texture = _checker()
	mat.uv1_scale = Vector3(CHECKS, CHECKS, 1.0)
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	floor_mesh.material_override = mat
	world.add_child(floor_mesh)
	var actor := packed.instantiate() as Node3D
	if actor is CreatureActor:
		actor.set_script(null)  # held clips only: no idle fidget
	world.add_child(actor)
	var cam := Camera3D.new()
	world.add_child(cam)
	cam.make_current()
	var anim := HeroMotion.player_of(actor)
	if anim == null:
		var players := actor.find_children("*", "AnimationPlayer", true, false)
		anim = players[0] as AnimationPlayer if not players.is_empty() else null
	# one camera for every pose (the union of their bounds), so a foot that slides moves against the floor's checks
	var box := CreatureFraming.bounds([actor])
	for spec: Array in cells:
		if _hold(anim, spec):
			box = box.merge(CreatureFraming.bounds([actor]))
	for i in cells.size() + 1:
		var spec: Array = ["idle", 0.0] if i == 0 else cells[i - 1]
		var have := _hold(anim, spec)
		if i == 0:
			# the close-up, from the front: a person's head and shoulders (a villager faces -Z), a creature's front half
			# (a creature faces +Z)
			var close := (
				AABB(
					box.position + box.size * Vector3(0.25, 1.0 - NPC_CLOSE_SHARE, 0.0),
					box.size * Vector3(0.5, NPC_CLOSE_SHARE, 1.0)
				)
				if npc
				else AABB(
					box.position + box.size * Vector3(0.0, 0.0, 1.0 - CLOSE_SHARE),
					box.size * Vector3(1.0, 1.0, CLOSE_SHARE)
				)
			)
			CreatureFraming.frame_fit(cam, close, CLOSE_YAW_DEG + (180.0 if npc else 0.0), PITCH_DEG, FOV_DEG, 1.1)
		elif i == 1:
			CreatureFraming.frame_fit(cam, box, YAW_DEG, PITCH_DEG, FOV_DEG, 1.1)
		await get_tree().process_frame
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		var img := vp.get_texture().get_image()
		img.convert(Image.FORMAT_RGBA8)
		if not have:
			img.fill(MISSING)
		sheet.blit_rect(img, Rect2i(Vector2i.ZERO, CELL), Vector2i(CELL.x * i, 0))
	vp.queue_free()
	await get_tree().process_frame
	return sheet
