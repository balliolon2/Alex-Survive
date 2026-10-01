class_name PlayerController
extends CharacterBody3D

const VitalsComponentScript = preload("res://scripts/systems/vitals_component.gd")

## Player Controller for Alex
## Handles third-person locomotion, FSM, over-the-shoulder camera, and vitals integration.

enum State {
	IDLE,
	WALK,
	SPRINT,
	CROUCH,
	DODGE,
	DEAD
}

signal state_changed(old_state: State, new_state: State)

@export_group("Movement Speeds")
@export var walk_speed: float = 3.2
@export var sprint_speed: float = 6.0
@export var crouch_speed: float = 1.8
@export var acceleration: float = 18.0
@export var friction: float = 22.0
@export var rotation_speed: float = 12.0

@export_group("Stamina Costs")
@export var sprint_stamina_cost: float = 16.0 # per second
@export var dodge_stamina_cost: float = 20.0

@export_group("Dodge Parameters")
@export var dodge_speed: float = 9.0
@export var dodge_duration: float = 0.28 # seconds
@export var dodge_cooldown: float = 0.55 # seconds
@export var dodge_iframe_duration: float = 0.20 # invulnerability window

@export_group("Camera Settings")
@export var mouse_sensitivity: float = 0.0028
@export var min_pitch: float = -75.0
@export var max_pitch: float = 60.0

@export_group("Node References")
@export var camera_pivot: Node3D
@export var spring_arm: SpringArm3D
@export var camera: Camera3D
@export var collision_shape: CollisionShape3D
@export var mesh_instance: Node3D

@onready var vitals: VitalsComponentScript = $VitalsComponent as VitalsComponentScript

var current_state: State = State.IDLE
var is_crouching: bool = false

var _cam_yaw: float = 0.0
var _cam_pitch: float = 0.0
var _dodge_timer: float = 0.0
var _dodge_cooldown_timer: float = 0.0
var _dodge_direction: Vector3 = Vector3.ZERO
var _gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity", 9.8)

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	if vitals:
		vitals.died.connect(_on_died)
		
	if camera_pivot:
		_cam_yaw = camera_pivot.rotation.y
		_cam_pitch = camera_pivot.rotation.x

func _unhandled_input(event: InputEvent) -> void:
	if current_state == State.DEAD:
		return
		
	# Mouse look
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		_cam_yaw -= event.relative.x * mouse_sensitivity
		_cam_pitch = clampf(_cam_pitch - event.relative.y * mouse_sensitivity, deg_to_rad(min_pitch), deg_to_rad(max_pitch))
		if camera_pivot:
			camera_pivot.rotation.y = _cam_yaw
			camera_pivot.rotation.x = _cam_pitch

	# Toggle mouse capture with ESC
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _physics_process(delta: float) -> void:
	if current_state == State.DEAD:
		_apply_gravity(delta)
		move_and_slide()
		return
		
	_update_timers(delta)
	
	match current_state:
		State.DODGE:
			_process_dodge(delta)
		_:
			_process_locomotion(delta)
			
	move_and_slide()

func _update_timers(delta: float) -> void:
	if _dodge_cooldown_timer > 0.0:
		_dodge_cooldown_timer -= delta

func _process_locomotion(delta: float) -> void:
	var input_vec := _get_input_vector()
	var move_dir := _get_camera_relative_direction(input_vec)
	
	# Check crouch toggle
	if _is_action_just_pressed("crouch"):
		is_crouching = not is_crouching
		_adjust_crouch_height(is_crouching)
		
	# Check dodge action (Ticket 03)
	if _is_action_just_pressed("dodge") and _can_dodge():
		_start_dodge(move_dir)
		return
		
	# Determine target speed and state
	var target_speed := 0.0
	if move_dir.length_squared() > 0.001:
		if is_crouching:
			_change_state(State.CROUCH)
			target_speed = crouch_speed
		elif _is_action_pressed("sprint") and vitals and vitals.can_afford_stamina(1.0):
			var drained := vitals.drain_stamina_continuous(sprint_stamina_cost, delta)
			if drained:
				_change_state(State.SPRINT)
				target_speed = sprint_speed
			else:
				_change_state(State.WALK)
				target_speed = walk_speed
		else:
			_change_state(State.WALK)
			target_speed = walk_speed
			
		# Rotate character model smoothly towards movement direction
		if mesh_instance:
			var target_rot_y := atan2(move_dir.x, move_dir.z)
			mesh_instance.rotation.y = lerp_angle(mesh_instance.rotation.y, target_rot_y, rotation_speed * delta)
	else:
		if is_crouching:
			_change_state(State.CROUCH)
		else:
			_change_state(State.IDLE)
		target_speed = 0.0

	# Apply acceleration and friction
	var h_vel := Vector3(velocity.x, 0.0, velocity.z)
	var target_vel := move_dir * target_speed
	
	if target_speed > 0.0:
		h_vel = h_vel.move_toward(target_vel, acceleration * delta)
	else:
		h_vel = h_vel.move_toward(Vector3.ZERO, friction * delta)
		
	velocity.x = h_vel.x
	velocity.z = h_vel.z
	_apply_gravity(delta)

func _can_dodge() -> bool:
	return _dodge_cooldown_timer <= 0.0 and vitals and vitals.can_afford_stamina(dodge_stamina_cost)

func _start_dodge(input_move_dir: Vector3) -> void:
	if not vitals.consume_stamina(dodge_stamina_cost):
		return
		
	_change_state(State.DODGE)
	_dodge_timer = dodge_duration
	_dodge_cooldown_timer = dodge_cooldown
	
	# If moving, dodge in move direction; otherwise dodge backwards
	if input_move_dir.length_squared() > 0.001:
		_dodge_direction = input_move_dir.normalized()
	else:
		var cam_basis := camera_pivot.global_basis if camera_pivot else global_basis
		_dodge_direction = cam_basis.z.normalized() # Backwards from camera
		_dodge_direction.y = 0.0
		_dodge_direction = _dodge_direction.normalized()

	# Activate i-frames on vitals
	vitals.is_invulnerable = true
	
	# Align mesh with dodge
	if mesh_instance and _dodge_direction.length_squared() > 0.001:
		mesh_instance.rotation.y = atan2(_dodge_direction.x, _dodge_direction.z)

func _process_dodge(delta: float) -> void:
	_dodge_timer -= delta
	
	# Check i-frame window
	if dodge_duration - _dodge_timer >= dodge_iframe_duration:
		vitals.is_invulnerable = false
		
	# Evasion velocity with slight decay
	var speed_factor := clampf(_dodge_timer / dodge_duration, 0.4, 1.0)
	var dodge_vel := _dodge_direction * (dodge_speed * speed_factor)
	velocity.x = dodge_vel.x
	velocity.z = dodge_vel.z
	_apply_gravity(delta)
	
	if _dodge_timer <= 0.0:
		vitals.is_invulnerable = false
		if _get_input_vector().length_squared() > 0.001:
			_change_state(State.WALK)
		else:
			_change_state(State.IDLE)

func _apply_gravity(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= _gravity * delta
	else:
		velocity.y = -0.1

func _get_input_vector() -> Vector2:
	var x := 0.0
	var y := 0.0
	
	if _is_action_pressed("move_right"): x += 1.0
	if _is_action_pressed("move_left"):  x -= 1.0
	if _is_action_pressed("move_forward"): y += 1.0
	if _is_action_pressed("move_back"):    y -= 1.0
	
	return Vector2(x, y).normalized()

func _get_camera_relative_direction(input_vec: Vector2) -> Vector3:
	if input_vec == Vector2.ZERO:
		return Vector3.ZERO
		
	var cam_basis := camera_pivot.global_basis if camera_pivot else global_basis
	var fwd := -cam_basis.z
	var right := cam_basis.x
	fwd.y = 0.0
	right.y = 0.0
	fwd = fwd.normalized()
	right = right.normalized()
	
	return (fwd * input_vec.y + right * input_vec.x).normalized()

func _adjust_crouch_height(crouching: bool) -> void:
	if collision_shape and collision_shape.shape is CapsuleShape3D:
		var capsule := collision_shape.shape as CapsuleShape3D
		if crouching:
			capsule.height = 1.2
			collision_shape.position.y = 0.6
		else:
			capsule.height = 1.8
			collision_shape.position.y = 0.9

func _change_state(new_state: State) -> void:
	if current_state != new_state:
		var old_state := current_state
		current_state = new_state
		state_changed.emit(old_state, new_state)

func _on_died() -> void:
	_change_state(State.DEAD)
	velocity = Vector3.ZERO

# Fallback-aware input checks
func _is_action_pressed(action_name: String) -> bool:
	if InputMap.has_action(action_name) and Input.is_action_pressed(action_name):
		return true
	# Direct key fallbacks
	match action_name:
		"move_forward": return Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP)
		"move_back":    return Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN)
		"move_left":    return Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT)
		"move_right":   return Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT)
		"sprint":       return Input.is_key_pressed(KEY_SHIFT)
		"crouch":       return Input.is_key_pressed(KEY_CTRL) or Input.is_key_pressed(KEY_C)
		"dodge":        return Input.is_key_pressed(KEY_SPACE) or Input.is_key_pressed(KEY_ALT)
	return false

func _is_action_just_pressed(action_name: String) -> bool:
	if InputMap.has_action(action_name) and Input.is_action_just_pressed(action_name):
		return true
	match action_name:
		"crouch": return Input.is_key_pressed(KEY_CTRL) or Input.is_key_pressed(KEY_C)
		"dodge":  return Input.is_key_pressed(KEY_SPACE) or Input.is_key_pressed(KEY_ALT)
	return false
