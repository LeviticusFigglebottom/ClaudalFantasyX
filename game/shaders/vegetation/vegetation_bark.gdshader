// Trunks and branches (M1-ENV-02): tiling bark albedo + normal, a base-to-top tint gradient along
// UV2.y (height fraction), baked occlusion in UV2.x, and the same wind as the foliage so trunk and
// crown move together. Bark has no flutter weight, so one tier serves every preset.
shader_type spatial;
render_mode cull_back, world_vertex_coords;

#include "res://game/shaders/vegetation/vegetation_wind.gdshaderinc"

group_uniforms surface;
uniform sampler2D tex_albedo : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D tex_normal : hint_default_black, filter_linear_mipmap_anisotropic, repeat_enable;
uniform vec4 col_base : source_color = vec4(0.9, 0.85, 0.78, 1.0); // tint at the root (UV2.y = 0)
uniform vec4 col_top : source_color = vec4(1.0, 1.0, 1.0, 1.0); // tint at the top (UV2.y = 1)
uniform float normal_strength : hint_range(0.0, 2.0) = 1.0;
uniform float roughness_value : hint_range(0.0, 1.0) = 0.85;
uniform float specular_value : hint_range(0.0, 1.0) = 0.3;
uniform float ao_strength : hint_range(0.0, 1.0) = 0.9;
group_uniforms;

void vertex() {
	vec3 origin = MODEL_MATRIX[3].xyz;
	float scale_y = length(MODEL_MATRIX[1].xyz);
	VERTEX = hymn_veg_wind_displace(VERTEX, NORMAL, COLOR, origin, scale_y);
}

void fragment() {
	vec3 albedo = texture(tex_albedo, UV).rgb * mix(col_base.rgb, col_top.rgb, clamp(UV2.y, 0.0, 1.0));
	float ao = mix(1.0, UV2.x, ao_strength);
	ALBEDO = albedo * mix(1.0, ao, 0.5);
	AO = ao;
	NORMAL_MAP = vec3(texture(tex_normal, UV).rg, 1.0);
	NORMAL_MAP_DEPTH = normal_strength;
	ROUGHNESS = roughness_value;
	SPECULAR = specular_value;
}
