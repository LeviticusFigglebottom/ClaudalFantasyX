extends SceneTree
## Writes the prewarm resources for water and glimmer (M1-RND-07): ShaderMaterials for every water
## tier variant and for the three glimmer shaders, and a tiny water-grid mesh with the ocean's exact
## surface format (WaterMeshBuilder; a test keeps the two equal) so the prewarm stage compiles the
## ocean's pipeline, not the quad's. Registered in game/data/settings/prewarm_materials.json.
##   godot --headless --path . --script res://tools/rendering/build_prewarm_resources.gd

const WATER_DIR := "res://game/world/water/prewarm"
const GLIMMER_DIR := "res://game/vfx/glimmer/materials"
## A few cells of the ocean grid: same format as the zone mesh, negligible size.
const GRID_CORE_HALF_M := 1.0
const GRID_CELL_M := 0.5
const GRID_OUTER_HALF_M := 2.0
const GRID_GROWTH := 1.1


func _init() -> void:
	DirAccess.make_dir_recursive_absolute(WATER_DIR)
	DirAccess.make_dir_recursive_absolute(GLIMMER_DIR)
	var saved := 0
	var paths := {}
	for q: int in WaterSurface.Quality.values():
		for river in [false, true]:
			paths[WaterSurface.shader_path(q, river)] = true
	for shader_path: String in paths:
		saved += _save_material(shader_path, WATER_DIR.path_join(shader_path.get_file().get_basename() + ".tres"))
	var grid := WaterMeshBuilder.build(GRID_CORE_HALF_M, GRID_CELL_M, GRID_OUTER_HALF_M, GRID_GROWTH)
	saved += int(ResourceSaver.save(grid, WATER_DIR.path_join("water_grid_prewarm.tres")) == OK)
	for shader: Shader in [GlimmerField.PROCESS_SHADER, GlimmerField.DRAW_SHADER, GlimmerField.REFLECT_SHADER]:
		saved += _save_material(shader.resource_path, GLIMMER_DIR.path_join(shader.resource_path.get_file().get_basename() + ".tres"))
	print("build_prewarm_resources: saved %d resource(s)" % saved)
	quit()


func _save_material(shader_path: String, out_path: String) -> int:
	var mat := ShaderMaterial.new()
	mat.shader = load(shader_path) as Shader
	return int(ResourceSaver.save(mat, out_path) == OK)
