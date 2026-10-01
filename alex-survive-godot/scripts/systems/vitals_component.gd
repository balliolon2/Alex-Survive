class_name VitalsComponent
extends Node

## Survival Vitals Component
## Calculates Health, Stamina depletion/recovery, and Hunger decay over time.
## Communicates strictly via Godot signals for UI and gameplay systems.

signal health_changed(current: float, max_val: float)
signal stamina_changed(current: float, max_val: float)
signal hunger_changed(current: float, max_val: float)
signal hunger_state_changed(state: String) # "well_fed", "normal", "starving", "dying"
signal died()

@export_group("Health")
@export var max_health: float = 100.0
@export var current_health: float = 100.0

@export_group("Stamina")
@export var max_stamina: float = 100.0
@export var current_stamina: float = 100.0
@export var base_stamina_recovery_rate: float = 22.0
@export var stamina_recovery_delay: float = 0.5

@export_group("Hunger")
@export var max_hunger: float = 100.0
@export var current_hunger: float = 100.0
## Base decay rate: 100 units / 900 seconds (~15 mins for full decay)
@export var base_hunger_decay_rate: float = 100.0 / 900.0
@export var starvation_damage_interval: float = 3.0
@export var starvation_damage_amount: float = 2.0

var is_alive: bool = true
var is_invulnerable: bool = false # Managed during dodge i-frames

var _stamina_delay_timer: float = 0.0
var _starvation_tick_timer: float = 0.0
var _current_hunger_state: String = "normal"

func _ready() -> void:
	current_health = clampf(current_health, 0.0, max_health)
	current_stamina = clampf(current_stamina, 0.0, max_stamina)
	current_hunger = clampf(current_hunger, 0.0, max_hunger)
	_update_hunger_state(true)

func _process(delta: float) -> void:
	if not is_alive:
		return
		
	_process_hunger(delta)
	_process_stamina(delta)

## Apply damage to health. Ignored if dead or invulnerable.
func take_damage(amount: float) -> void:
	if not is_alive or is_invulnerable or amount <= 0.0:
		return
		
	current_health = maxf(0.0, current_health - amount)
	health_changed.emit(current_health, max_health)
	
	if current_health <= 0.0:
		is_alive = false
		died.emit()

## Restore health up to max_health.
func heal(amount: float) -> void:
	if not is_alive or amount <= 0.0:
		return
		
	current_health = minf(max_health, current_health + amount)
	health_changed.emit(current_health, max_health)

## Check if entity has enough stamina for an action.
func can_afford_stamina(amount: float) -> bool:
	return is_alive and current_stamina >= amount

## Instantly consume stamina (e.g. for dodge or heavy attack).
func consume_stamina(amount: float) -> bool:
	if not can_afford_stamina(amount):
		return false
		
	current_stamina = maxf(0.0, current_stamina - amount)
	_stamina_delay_timer = stamina_recovery_delay
	stamina_changed.emit(current_stamina, max_stamina)
	return true

## Continuously drain stamina (e.g. for sprinting).
func drain_stamina_continuous(rate_per_sec: float, delta: float) -> bool:
	if not is_alive or current_stamina <= 0.0:
		return false
		
	var cost := rate_per_sec * delta
	if current_stamina >= cost:
		current_stamina -= cost
		_stamina_delay_timer = stamina_recovery_delay
		stamina_changed.emit(current_stamina, max_stamina)
		return true
	else:
		current_stamina = 0.0
		_stamina_delay_timer = stamina_recovery_delay
		stamina_changed.emit(current_stamina, max_stamina)
		return false

## Consume food rations to restore hunger.
func consume_food(amount: float) -> void:
	if not is_alive or amount <= 0.0:
		return
		
	current_hunger = minf(max_hunger, current_hunger + amount)
	hunger_changed.emit(current_hunger, max_hunger)
	_update_hunger_state()

func _process_hunger(delta: float) -> void:
	if current_hunger > 0.0:
		current_hunger = maxf(0.0, current_hunger - base_hunger_decay_rate * delta)
		hunger_changed.emit(current_hunger, max_hunger)
		_update_hunger_state()
		
	# Starvation damage at 0 hunger
	if current_hunger <= 0.0:
		_starvation_tick_timer += delta
		if _starvation_tick_timer >= starvation_damage_interval:
			_starvation_tick_timer = 0.0
			take_damage(starvation_damage_amount)
	else:
		_starvation_tick_timer = 0.0

func _process_stamina(delta: float) -> void:
	if _stamina_delay_timer > 0.0:
		_stamina_delay_timer -= delta
		return
		
	if current_stamina < max_stamina:
		var multiplier := 1.0
		if _current_hunger_state == "well_fed":
			multiplier = 1.1 # +10% boost
		elif _current_hunger_state in ["starving", "dying"]:
			multiplier = 0.5 # -50% penalty
			
		current_stamina = minf(max_stamina, current_stamina + base_stamina_recovery_rate * multiplier * delta)
		stamina_changed.emit(current_stamina, max_stamina)

func _update_hunger_state(force_emit: bool = false) -> void:
	var new_state: String
	if current_hunger > 75.0:
		new_state = "well_fed"
	elif current_hunger >= 25.0:
		new_state = "normal"
	elif current_hunger > 0.0:
		new_state = "starving"
	else:
		new_state = "dying"
		
	if new_state != _current_hunger_state or force_emit:
		_current_hunger_state = new_state
		hunger_state_changed.emit(_current_hunger_state)
