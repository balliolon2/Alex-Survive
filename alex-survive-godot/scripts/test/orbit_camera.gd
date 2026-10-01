extends Camera3D

@export var target: Vector3 = Vector3(0.0, 1.0, 0.0)
@export var distance: float = 6.0
@export var orbit_speed: float = 0.5
@export var auto_rotate: bool = true
@export var auto_rotate_speed: float = 0.3

var _yaw: float = 0.5
var _pitch: float = 0.35
var _is_dragging: bool = false

func _ready() -> void:
	_update_transform()

func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		if event.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
			_is_dragging = event.pressed
	elif event is InputEventMouseMotion and _is_dragging:
		auto_rotate = false
		_yaw -= event.relative.x * 0.005 * orbit_speed
		_pitch = clampf(_pitch - event.relative.y * 0.005 * orbit_speed, -1.2, 1.2)
		_update_transform()
	elif event is InputEventKey and event.pressed:
		if event.keycode == KEY_SPACE:
			auto_rotate = not auto_rotate

func _process(delta: float) -> void:
	if auto_rotate:
		_yaw += auto_rotate_speed * delta
		_update_transform()
	
	# Keyboard controls
	var key_input := false
	if Input.is_key_pressed(KEY_LEFT) or Input.is_key_pressed(KEY_A):
		_yaw -= 1.5 * delta
		key_input = true
	if Input.is_key_pressed(KEY_RIGHT) or Input.is_key_pressed(KEY_D):
		_yaw += 1.5 * delta
		key_input = true
	if Input.is_key_pressed(KEY_UP) or Input.is_key_pressed(KEY_W):
		_pitch = clampf(_pitch + 1.5 * delta, -1.2, 1.2)
		key_input = true
	if Input.is_key_pressed(KEY_DOWN) or Input.is_key_pressed(KEY_S):
		_pitch = clampf(_pitch - 1.5 * delta, -1.2, 1.2)
		key_input = true
		
	if key_input:
		auto_rotate = false
		_update_transform()

func _update_transform() -> void:
	var pos := target + Vector3(
		distance * cos(_pitch) * sin(_yaw),
		distance * sin(_pitch),
		distance * cos(_pitch) * cos(_yaw)
	)
	global_position = pos
	look_at(target, Vector3.UP)
