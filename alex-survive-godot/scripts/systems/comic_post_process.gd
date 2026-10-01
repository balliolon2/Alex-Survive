class_name ComicPostProcess
extends MeshInstance3D

## Reusable Western Comic Post-Process Controller
## Manages global outline inking, cel-shading bands, and halftone screen tones.

@export var outline_color: Color = Color(0.04, 0.04, 0.05, 1.0):
	set(val):
		outline_color = val
		_update_param("outline_color", val)

@export_range(0.5, 4.0, 0.1) var outline_thickness: float = 1.2:
	set(val):
		outline_thickness = val
		_update_param("outline_thickness", val)

@export_range(0.005, 0.2, 0.005) var depth_threshold: float = 0.035:
	set(val):
		depth_threshold = val
		_update_param("depth_threshold", val)

@export_range(0.1, 1.5, 0.05) var normal_threshold: float = 0.45:
	set(val):
		normal_threshold = val
		_update_param("normal_threshold", val)

@export var enable_tone_stepping: bool = true:
	set(val):
		enable_tone_stepping = val
		_update_param("enable_tone_stepping", val)

@export_range(2, 8, 1) var shadow_bands: int = 4:
	set(val):
		shadow_bands = val
		_update_param("shadow_bands", val)

@export var enable_halftone: bool = true:
	set(val):
		enable_halftone = val
		_update_param("enable_halftone", val)

@export_range(1.0, 10.0, 0.5) var halftone_scale: float = 3.5:
	set(val):
		halftone_scale = val
		_update_param("halftone_scale", val)

var _mat: ShaderMaterial

func _ready() -> void:
	extra_cull_margin = 16384.0
	if get_surface_override_material(0) is ShaderMaterial:
		_mat = get_surface_override_material(0)
	elif mesh and mesh.material is ShaderMaterial:
		_mat = mesh.material

func _update_param(param_name: String, val: Variant) -> void:
	if _mat:
		_mat.set_shader_parameter(param_name, val)
