// Hymn of the Undertow: Pemakar's ash-plume (M3-ENV-03, pemakar.md §0 and §2.4). The kit's ash_plume
// mesh is a lofted billowing column; UV.y runs 0 at the caldera vent to 1 at the top. The body is dark,
// matte ash lit by the scene (sky fill); its silhouette softens toward grazing view angles so it never
// reads as a hard-edged solid; the lowest part glows a dull ember from below (the caldera's light), no
// brighter than the night sea-glow, so the lamp pools stay the brightest things in the frame. While the
// sun is only just under the horizon (dusk), the billows facing it catch a thin afterglow rim; by full
// night (sun 18 degrees down) the rim is gone. Fog is off: the plume is a silhouette against the sky,
// and the zone's warm ash-haze fog turned it brown at 900 m.
// Close up (M3-ENV-11: Ashcrown's crater, inside ~800 m) a column of matte ash lit only by the sky's ambient
// went near-black on its shaded side, though real ash cloud keeps value there: the sky and the sunlit
// billows around it light it, and its thin edges glow with the sun behind them. The `near` group puts that
// back: a sky-coloured lift, strongest on the side away from the sun, back-scatter through the edges when the view
// looks toward the sun, and the vent's ember on the column's foot. All three default to 0 and fade out
// between near_fade_m.x and .y from the camera, so the far plume (kit_plume, 900 m) is unchanged.
shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_lambert_wrap, specular_disabled, fog_disabled;

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"

group_uniforms body;
uniform vec4 col_body : source_color = vec4(0.243, 0.290, 0.341, 1.0); // storm_slate #3E4A57
uniform vec4 col_body_top : source_color = vec4(0.30, 0.31, 0.33, 1.0); // thinner, paler ash aloft
uniform float body_darken : hint_range(0.0, 1.0) = 0.2; // multiplies the albedo (ash is dark)
uniform float mottle : hint_range(0.0, 1.0) = 0.45;
uniform float mottle_scale_m = 55.0;
uniform float drift_m_s = 1.5; // billows roll upward with hymn_wind_time
group_uniforms;

group_uniforms silhouette;
uniform float opacity : hint_range(0.0, 1.0) = 0.97;
uniform float edge_soft : hint_range(0.01, 1.0) = 0.3; // N.V below this fades out
uniform float top_fade : hint_range(0.0, 1.0) = 0.3; // the last part of the column thins away
// How much the mottle thins the ash (alpha 1 - m/2 .. 1 + m/2 of opacity). Close up, a dark plume with
// the sky behind it shows even a few per cent of see-through, so the near material lowers it.
uniform float alpha_mottle : hint_range(0.0, 1.0) = 0.4;
group_uniforms;

group_uniforms ember;
uniform vec4 col_ember : source_color = vec4(0.878, 0.439, 0.180, 1.0); // ember_orange #E0702E
uniform float ember_energy : hint_range(0.0, 2.0) = 0.3;
uniform float ember_height : hint_range(0.0, 1.0) = 0.2; // fraction of the column the glow reaches
uniform float ember_underside : hint_range(0.0, 1.0) = 0.8; // extra glow on down-facing billows
// The festival's own glow on the undersides of the billows all the way up (very faint: it only lets the
// lumps read against the night sky).
uniform float town_glow : hint_range(0.0, 0.5) = 0.012;
group_uniforms;

group_uniforms afterglow;
uniform vec4 col_rim : source_color = vec4(0.788, 0.471, 0.29, 1.0); // the dusk afterglow #C9784A
uniform float rim_energy : hint_range(0.0, 2.0) = 0.35;
uniform float rim_power : hint_range(0.5, 8.0) = 2.5;
group_uniforms;

group_uniforms near;
uniform vec4 col_shade : source_color = vec4(0.596, 0.643, 0.69, 1.0); // sky-lit ash in shade (#98A4B0)
uniform float shade_lift : hint_range(0.0, 1.0) = 0.0; // emission on the side away from the sun
// The part of the lift that also reaches the sun side: billows in the cast shadow of the temple or the
// crater rim face the sun but get none (the shader cannot see the shadow), and the sky still lights them.
uniform float lift_all_round : hint_range(0.0, 1.0) = 0.5;
uniform float back_scatter : hint_range(0.0, 2.0) = 0.0; // the sun through the edges, looking sunward
uniform float back_scatter_power : hint_range(0.5, 8.0) = 3.0;
uniform float vent_glow : hint_range(0.0, 4.0) = 0.0; // the throat's ember on the column's foot
uniform float vent_glow_height : hint_range(0.0, 0.5) = 0.12; // fraction of the column it reaches
// The near mesh (ash_plume_near) carries its billows' heads in UV2.x (crowns 1, creases 0; the far mesh
// has 1): in the temple's or the rim's shadow the sun shades nothing, so this keeps the heads readable.
uniform float billow_shade : hint_range(0.0, 1.0) = 0.0;
// More of the lift on sky-facing billows than on the undersides (the sky is above).
uniform float sky_up : hint_range(0.0, 1.0) = 0.0;
uniform vec2 near_fade_m = vec2(400.0, 800.0); // the near treatment fades out between these distances
// Inside a few tens of metres (the crater rim, the loggia) even the near mesh's smallest heads (11 m) are
// wider than the frame: small rolling heads bumped into the normal (billow noise; creases a little darker),
// drifting up with the billows, fading out between near_detail_fade_m.x and .y.
uniform float near_detail : hint_range(0.0, 1.0) = 0.0;
uniform float near_detail_m = 7.0;
uniform float detail_bump : hint_range(0.0, 4.0) = 1.2;
uniform vec2 near_detail_fade_m = vec2(80.0, 240.0);
group_uniforms;

varying vec3 v_world;

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec3 q = v_world / mottle_scale_m + vec3(0.0, -hymn_wind_time * drift_m_s / mottle_scale_m, 0.0);
	float n = hymn_fbm3(q, 3, 2.03, 0.5);
	vec3 base = mix(col_body.rgb, col_body_top.rgb, smoothstep(0.2, 0.9, UV.y)) * body_darken;
	ALBEDO = base * (1.0 - mottle + mottle * 2.0 * n);
	ROUGHNESS = 1.0;
	float ndv = abs(dot(normalize(NORMAL), normalize(VIEW)));
	float edge = smoothstep(0.0, edge_soft, ndv);
	float top = 1.0 - smoothstep(1.0 - top_fade, 1.0, UV.y);
	ALPHA = clamp(opacity * edge * top * (1.0 - 0.5 * alpha_mottle + alpha_mottle * n), 0.0, 1.0);
	vec3 world_n = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	float detail_shade = 1.0;
	float detail_k = near_detail
		* (1.0 - smoothstep(near_detail_fade_m.x, near_detail_fade_m.y, distance(v_world, CAMERA_POSITION_WORLD)));
	if (detail_k > 0.0) {
		// Billow noise (|2 fbm - 1|: round heads, sharp creases) as a bump on the normal, so the sun and the
		// lift turn over each small head; the silhouette (ALPHA, from the mesh normal) is left alone.
		vec3 q2 = v_world / near_detail_m + vec3(0.0, -hymn_wind_time * drift_m_s / near_detail_m, 17.0);
		float e = 0.12;
		float h0 = abs(2.0 * hymn_fbm3(q2, 3, 2.1, 0.5) - 1.0);
		vec3 g = vec3(
			abs(2.0 * hymn_fbm3(q2 + vec3(e, 0.0, 0.0), 3, 2.1, 0.5) - 1.0),
			abs(2.0 * hymn_fbm3(q2 + vec3(0.0, e, 0.0), 3, 2.1, 0.5) - 1.0),
			abs(2.0 * hymn_fbm3(q2 + vec3(0.0, 0.0, e), 3, 2.1, 0.5) - 1.0)
		) - vec3(h0);
		g = (g - world_n * dot(g, world_n)) / e;
		world_n = normalize(world_n - g * detail_bump * detail_k);
		NORMAL = normalize((VIEW_MATRIX * vec4(world_n, 0.0)).xyz);
		detail_shade = mix(1.0, 0.7 + 0.6 * smoothstep(0.0, 0.5, h0), detail_k);
	}
	float low = 1.0 - smoothstep(0.0, ember_height, UV.y);
	float under = clamp(-world_n.y, 0.0, 1.0) * ember_underside;
	vec3 ember = col_ember.rgb * ember_energy * low * (0.55 + 0.9 * n) * (1.0 + under);
	ember += col_ember.rgb * town_glow * clamp(-world_n.y + 0.25, 0.0, 1.0) * (0.4 + 1.2 * n);
	vec3 sun = normalize(hymn_sun_direction);
	float dusk = smoothstep(-0.3, -0.03, sun.y) * (1.0 - smoothstep(0.05, 0.25, sun.y));
	vec3 sun_flat = normalize(vec3(sun.x, 0.0, sun.z) + vec3(0.0, 1e-4, 0.0));
	float facing = clamp(dot(world_n, sun_flat), 0.0, 1.0);
	float rim = pow(1.0 - ndv, rim_power) * facing * dusk * smoothstep(0.1, 0.6, UV.y);
	EMISSION = ember + col_rim.rgb * rim_energy * rim * (0.6 + 0.8 * n);
	float near_k = 1.0 - smoothstep(near_fade_m.x, near_fade_m.y, distance(v_world, CAMERA_POSITION_WORLD));
	float day = smoothstep(-0.1, 0.2, sun.y);
	float away = 1.0 - smoothstep(-0.25, 0.55, dot(world_n, sun));
	vec3 look = normalize(v_world - CAMERA_POSITION_WORLD);
	float sunward = pow(clamp(dot(look, sun), 0.0, 1.0), back_scatter_power);
	float thin = (1.0 - ndv) * (1.0 - ndv);
	float foot = 1.0 - smoothstep(0.0, vent_glow_height, UV.y);
	float billow = mix(1.0, 0.45 + 0.8 * UV2.x, billow_shade * near_k);
	billow *= detail_shade;
	float sky_k = mix(1.0, 0.55 + 0.45 * world_n.y, sky_up);
	vec3 lift = col_shade.rgb * (shade_lift * mix(lift_all_round, 1.0, away) * (0.7 + 0.6 * n) * sky_k * billow
		+ back_scatter * sunward * thin) * day;
	ALBEDO *= billow;
	lift += col_ember.rgb * vent_glow * foot * foot * (0.5 + 0.5 * clamp(-world_n.y + 0.5, 0.0, 1.0)) * (0.6 + 0.8 * n);
	EMISSION += lift * near_k;
}
