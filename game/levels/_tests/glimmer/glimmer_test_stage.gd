extends Node3D
## Test-scene driver for the glimmer shots (M1-RND-02). It does what a zone or cutscene would do:
## writes the scene globals (hymn_glimmer, hymn_glimmer_focus), registers the living figure as an
## attractor, and optionally starts the release on the first frame. Restores the globals on exit
## so the next screenshot shot starts clean. Deterministic: no input, no wall clock.

@export var field_path: NodePath
@export var figure_path: NodePath
## Scene glimmer intensity: the colour-script mote emission energy for this frame.
@export var glimmer_intensity: float = 1.0
@export var glimmer_tint: Color = Color(1.0, 0.914, 0.722)
@export var figure_attractor_strength: float = 1.0
@export var figure_attractor_radius_m: float = 0.7
@export var figure_attractor_half_height_m: float = 0.8
## Also write hymn_glimmer_focus at the figure with this radius (0 = leave it off).
@export var global_focus_radius_m: float = 0.0
@export var release_on_ready: bool = false
## Negative = glimmer.json release_duration_s.
@export var release_duration_s: float = GlimmerField.USE_DEFAULT


func _ready() -> void:
	GlimmerField.set_scene_glimmer(glimmer_tint, glimmer_intensity)
	var field := get_node_or_null(field_path) as GlimmerField
	var figure := get_node_or_null(figure_path) as Node3D
	if figure != null and global_focus_radius_m > 0.0:
		GlimmerField.set_global_focus(figure.global_position, global_focus_radius_m)
	else:
		GlimmerField.clear_global_focus()
	if field == null:
		return
	if figure != null and figure_attractor_strength > 0.0:
		field.add_attractor(
			figure,
			figure_attractor_strength,
			figure_attractor_radius_m,
			GlimmerField.USE_DEFAULT,
			figure_attractor_half_height_m
		)
	if release_on_ready:
		field.release(release_duration_s, figure)


func _exit_tree() -> void:
	GlimmerField.set_scene_glimmer(glimmer_tint, 0.0)
	GlimmerField.clear_global_focus()
