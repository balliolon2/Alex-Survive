extends SceneTree

const VitalsComponent = preload("res://scripts/systems/vitals_component.gd")

func _init() -> void:
	print("--- Running VitalsComponent Unit Tests ---")
	var vitals: VitalsComponent = VitalsComponent.new()
	vitals._ready()
	
	# Test 1: Initial values
	assert(vitals.current_health == 100.0, "Health should start at 100")
	assert(vitals.current_stamina == 100.0, "Stamina should start at 100")
	assert(vitals.current_hunger == 100.0, "Hunger should start at 100")
	print("✓ Test 1: Initial values passed")
	
	# Test 2: Damage and death
	var died_called := [false]
	vitals.died.connect(func(): died_called[0] = true)
	vitals.take_damage(40.0)
	assert(vitals.current_health == 60.0, "Health should drop to 60")
	vitals.take_damage(70.0)
	assert(vitals.current_health == 0.0, "Health should clamp to 0")
	assert(died_called[0] == true, "Died signal should fire")
	print("✓ Test 2: Damage & Death passed")
	
	# Test 3: Stamina consumption
	vitals.is_alive = true
	vitals.current_health = 100.0
	assert(vitals.can_afford_stamina(20.0) == true, "Should afford 20 stamina")
	var success: bool = vitals.consume_stamina(20.0)
	assert(success == true, "Consume should return true")
	assert(vitals.current_stamina == 80.0, "Stamina should be 80")
	assert(vitals.consume_stamina(90.0) == false, "Cannot afford 90 stamina")
	print("✓ Test 3: Stamina consumption passed")
	
	# Test 4: Hunger thresholds
	vitals.current_hunger = 80.0
	vitals._update_hunger_state()
	assert(vitals._current_hunger_state == "well_fed", "Should be well_fed above 75")
	vitals.current_hunger = 50.0
	vitals._update_hunger_state()
	assert(vitals._current_hunger_state == "normal", "Should be normal between 25 and 75")
	vitals.current_hunger = 15.0
	vitals._update_hunger_state()
	assert(vitals._current_hunger_state == "starving", "Should be starving below 25")
	vitals.current_hunger = 0.0
	vitals._update_hunger_state()
	assert(vitals._current_hunger_state == "dying", "Should be dying at 0")
	print("✓ Test 4: Hunger thresholds passed")
	
	print("--- All VitalsComponent Unit Tests Passed Successfully! ---")
	vitals.free()
	quit(0)
