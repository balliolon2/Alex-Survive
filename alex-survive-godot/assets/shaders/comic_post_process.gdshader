shader_type spatial;
render_mode unshaded, fog_disabled, depth_test_disabled, depth_draw_never, cull_disabled;

// Texture samplers for Forward+ screen reading
uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;
uniform sampler2D depth_texture : hint_depth_texture, filter_linear_mipmap;
uniform sampler2D normal_roughness_texture : hint_normal_roughness_texture, filter_linear_mipmap;

// Group: Edge Outline
uniform vec4 outline_color : source_color = vec4(0.04, 0.04, 0.05, 1.0);
uniform float outline_thickness : hint_range(0.5, 4.0, 0.1) = 1.2;
uniform float depth_threshold : hint_range(0.005, 0.2, 0.005) = 0.035;
uniform float normal_threshold : hint_range(0.1, 1.5, 0.05) = 0.45;

// Group: Comic Tone & Posterization
uniform bool enable_tone_stepping = true;
uniform int shadow_bands : hint_range(2, 8, 1) = 4;

// Group: Halftone / Screen Tone
uniform bool enable_halftone = true;
uniform float halftone_scale : hint_range(1.0, 10.0, 0.5) = 3.5;
uniform float halftone_intensity : hint_range(0.0, 1.0, 0.05) = 0.45;
uniform float halftone_shadow_cutoff : hint_range(0.1, 0.8, 0.05) = 0.42;

void vertex() {
	// Fullscreen quad spanning NDC (-1 to 1)
	POSITION = vec4(VERTEX.xy, 1.0, 1.0);
}

float get_linear_depth(vec2 uv, mat4 inv_proj) {
	float raw_depth = texture(depth_texture, uv).r;
	vec3 ndc = vec3(uv * 2.0 - 1.0, raw_depth);
	vec4 view = inv_proj * vec4(ndc, 1.0);
	return -view.z / max(view.w, 0.00001);
}

vec3 get_view_normal(vec2 uv) {
	return normalize(texture(normal_roughness_texture, uv).xyz * 2.0 - 1.0);
}

void fragment() {
	vec2 tex_size = vec2(textureSize(screen_texture, 0));
	vec2 pixel_size = (1.0 / tex_size) * outline_thickness;
	
	// Sample center
	vec3 base_color = texture(screen_texture, SCREEN_UV).rgb;
	float center_depth = get_linear_depth(SCREEN_UV, INV_PROJECTION_MATRIX);
	vec3 center_norm = get_view_normal(SCREEN_UV);
	
	// 8-neighbor sampling for Sobel kernel
	float d_tl = get_linear_depth(SCREEN_UV + vec2(-pixel_size.x, -pixel_size.y), INV_PROJECTION_MATRIX);
	float d_tc = get_linear_depth(SCREEN_UV + vec2(0.0,           -pixel_size.y), INV_PROJECTION_MATRIX);
	float d_tr = get_linear_depth(SCREEN_UV + vec2( pixel_size.x, -pixel_size.y), INV_PROJECTION_MATRIX);
	float d_ml = get_linear_depth(SCREEN_UV + vec2(-pixel_size.x,  0.0),           INV_PROJECTION_MATRIX);
	float d_mr = get_linear_depth(SCREEN_UV + vec2( pixel_size.x,  0.0),           INV_PROJECTION_MATRIX);
	float d_bl = get_linear_depth(SCREEN_UV + vec2(-pixel_size.x,  pixel_size.y), INV_PROJECTION_MATRIX);
	float d_bc = get_linear_depth(SCREEN_UV + vec2(0.0,            pixel_size.y), INV_PROJECTION_MATRIX);
	float d_br = get_linear_depth(SCREEN_UV + vec2( pixel_size.x,  pixel_size.y), INV_PROJECTION_MATRIX);
	
	// Depth edge detection using second derivative (Laplacian / opposite pairs)
	// A first-derivative Sobel operator falsely detects constant slope on flat ground/walls.
	// Second derivative is mathematically ZERO on any sloping plane, but spikes at depth jumps.
	float raw_center = texture(depth_texture, SCREEN_UV).r;
	bool is_sky = (raw_center <= 0.0001);
	
	float depth_edge = 0.0;
	if (!is_sky) {
		float max_d = center_depth * 10.0;
		float d_l = min(d_ml, max_d);
		float d_r = min(d_mr, max_d);
		float d_t = min(d_tc, max_d);
		float d_b = min(d_bc, max_d);
		
		float diff_x = abs(d_l + d_r - 2.0 * center_depth);
		float diff_y = abs(d_t + d_b - 2.0 * center_depth);
		
		float d_1 = min(d_tl, max_d);
		float d_2 = min(d_br, max_d);
		float d_3 = min(d_tr, max_d);
		float d_4 = min(d_bl, max_d);
		
		float diff_d1 = abs(d_1 + d_2 - 2.0 * center_depth);
		float diff_d2 = abs(d_3 + d_4 - 2.0 * center_depth);
		
		float total_diff = max(max(diff_x, diff_y), max(diff_d1, diff_d2));
		depth_edge = total_diff / max(center_depth, 0.5);
	}
	
	// Sample 8-neighbor normals
	vec3 n_tl = get_view_normal(SCREEN_UV + vec2(-pixel_size.x, -pixel_size.y));
	vec3 n_tc = get_view_normal(SCREEN_UV + vec2(0.0,           -pixel_size.y));
	vec3 n_tr = get_view_normal(SCREEN_UV + vec2( pixel_size.x, -pixel_size.y));
	vec3 n_ml = get_view_normal(SCREEN_UV + vec2(-pixel_size.x,  0.0));
	vec3 n_mr = get_view_normal(SCREEN_UV + vec2( pixel_size.x,  0.0));
	vec3 n_bl = get_view_normal(SCREEN_UV + vec2(-pixel_size.x,  pixel_size.y));
	vec3 n_bc = get_view_normal(SCREEN_UV + vec2(0.0,            pixel_size.y));
	vec3 n_br = get_view_normal(SCREEN_UV + vec2( pixel_size.x,  pixel_size.y));
	
	// Normal crease detection using dot product of opposite neighbors
	// Normal dot product measures the true angular difference between surfaces.
	// Gentle curves have 1.0 - dot ~= 0, while creases (> 45 deg) spike to > 0.3.
	float norm_edge = 0.0;
	if (!is_sky) {
		float d_lr = 1.0 - dot(n_ml, n_mr);
		float d_tb = 1.0 - dot(n_tc, n_bc);
		float d_d1 = 1.0 - dot(n_tl, n_br);
		float d_d2 = 1.0 - dot(n_tr, n_bl);
		norm_edge = max(max(d_lr, d_tb), max(d_d1, d_d2));
	}
	
	// Evaluate edge thresholds
	float is_depth_edge = step(depth_threshold, depth_edge);
	float is_norm_edge = step(normal_threshold, norm_edge);
	float edge = clamp(max(is_depth_edge, is_norm_edge), 0.0, 1.0);
	
	vec3 final_color = base_color;
	
	// Stepped comic lighting (preserves color hue while quantizing brightness into graphic novel bands)
	if (enable_tone_stepping && !is_sky) {
		float bands = float(max(shadow_bands, 2));
		float luma = dot(final_color, vec3(0.299, 0.587, 0.114));
		float stepped_luma = (floor(luma * bands) + 0.5) / bands;
		float factor = clamp(stepped_luma / max(luma, 0.02), 0.4, 2.0);
		final_color = clamp(final_color * factor, vec3(0.02), vec3(1.0));
	}
	
	// Halftone / Ben-Day screen tone in shaded areas (angled at 45 degrees)
	// Bounded dot radius prevents halftone dots from coalescing into solid black sheets.
	if (enable_halftone) {
		float luma = dot(final_color, vec3(0.299, 0.587, 0.114));
		if (luma < halftone_shadow_cutoff) {
			// 45-degree rotation for graphic novel print angle
			mat2 rot45 = mat2(vec2(0.7071, -0.7071), vec2(0.7071, 0.7071));
			vec2 dot_uv = rot45 * ((SCREEN_UV * tex_size) / (halftone_scale * 2.5));
			vec2 grid = fract(dot_uv) - vec2(0.5);
			float dist = length(grid);
			// Max dot radius capped at 0.38 so dots never merge into a solid black mass
			float dot_radius = clamp((halftone_shadow_cutoff - luma) * 0.65, 0.0, 0.38);
			if (dist < dot_radius) {
				final_color = mix(final_color, outline_color.rgb, halftone_intensity);
			}
		}
	}
	
	// Ink Outline blending
	final_color = mix(final_color, outline_color.rgb, edge * outline_color.a);
	
	ALBEDO = final_color;
}
