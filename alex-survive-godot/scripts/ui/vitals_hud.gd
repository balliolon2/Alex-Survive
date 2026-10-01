class_name VitalsHUD
extends CanvasLayer

const VitalsComponentScript = preload("res://scripts/systems/vitals_component.gd")

## Western Comic styled Survival HUD
## Displays real-time Health, Stamina, and Hunger status connected to VitalsComponent.

@export var player_path: NodePath
@export var health_bar: ProgressBar
@export var stamina_bar: ProgressBar
@export var hunger_bar: ProgressBar
@export var hunger_badge: Label
@export var health_label: Label
@export var stamina_label: Label
@export var hunger_label: Label

var _vitals: VitalsComponentScript

func _ready() -> void:
	if not player_path.is_empty():
		var player := get_node_or_null(player_path)
		if player:
			_vitals = player.get_node_or_null("VitalsComponent") as VitalsComponentScript
			
	if _vitals:
		bind_vitals(_vitals)

func bind_vitals(v: VitalsComponentScript) -> void:
	_vitals = v
	_vitals.health_changed.connect(_on_health_changed)
	_vitals.stamina_changed.connect(_on_stamina_changed)
	_vitals.hunger_changed.connect(_on_hunger_changed)
	_vitals.hunger_state_changed.connect(_on_hunger_state_changed)
	
	# Initial sync
	_on_health_changed(_vitals.current_health, _vitals.max_health)
	_on_stamina_changed(_vitals.current_stamina, _vitals.max_stamina)
	_on_hunger_changed(_vitals.current_hunger, _vitals.max_hunger)
	_on_hunger_state_changed(_vitals._current_hunger_state)

func _on_health_changed(current: float, max_val: float) -> void:
	if health_bar:
		health_bar.max_value = max_val
		health_bar.value = current
	if health_label:
		health_label.text = "HP  %d / %d" % [int(current), int(max_val)]

func _on_stamina_changed(current: float, max_val: float) -> void:
	if stamina_bar:
		stamina_bar.max_value = max_val
		stamina_bar.value = current
	if stamina_label:
		stamina_label.text = "STAMINA  %d / %d" % [int(current), int(max_val)]

func _on_hunger_changed(current: float, max_val: float) -> void:
	if hunger_bar:
		hunger_bar.max_value = max_val
		hunger_bar.value = current
	if hunger_label:
		hunger_label.text = "HUNGER  %d%%" % [int((current / max_val) * 100.0)]

func _on_hunger_state_changed(state: String) -> void:
	if not hunger_badge:
		return
		
	match state:
		"well_fed":
			hunger_badge.text = "[ WELL-FED +10% STAMINA ]"
			hunger_badge.modulate = Color(0.4, 0.9, 0.4, 1.0)
		"normal":
			hunger_badge.text = "[ NORMAL ]"
			hunger_badge.modulate = Color(0.85, 0.85, 0.85, 0.8)
		"starving":
			hunger_badge.text = "[ STARVING -50% STAMINA ]"
			hunger_badge.modulate = Color(1.0, 0.45, 0.2, 1.0)
		"dying":
			hunger_badge.text = "[ STARVING TO DEATH ]"
			hunger_badge.modulate = Color(1.0, 0.2, 0.2, 1.0)
