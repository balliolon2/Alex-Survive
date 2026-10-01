extends SceneTree

const PlayerController = preload("res://scripts/characters/player_controller.gd")
const VitalsComponent = preload("res://scripts/systems/vitals_component.gd")

func _init() -> void:
	print("--- Running PlayerController & Dodge Unit Tests ---")
	
	var player := PlayerController.new()
	var vitals := VitalsComponent.new()
	player.name = "Player"
	vitals.name = "VitalsComponent"
	player.add_child(vitals)
	vitals._ready()
	player.vitals = vitals
	player._ready()
	
	# Test 1: Initial state is IDLE
	assert(player.current_state == PlayerController.State.IDLE, "Initial state should be IDLE")
	print("✓ Test 1: Initial state passed")
	
	# Test 2: Can dodge with full stamina
	assert(player._can_dodge() == true, "Should be able to dodge with full stamina")
	player._start_dodge(Vector3.FORWARD)
	assert(player.current_state == PlayerController.State.DODGE, "State should be DODGE")
	assert(vitals.current_stamina == 80.0, "Dodge should consume 20 stamina")
	assert(vitals.is_invulnerable == true, "Should be invulnerable during dodge startup")
	print("✓ Test 2: Dodge execution & stamina deduction passed")
	
	# Test 3: Cooldown prevents instant second dodge
	assert(player._can_dodge() == false, "Should be on cooldown immediately after dodge")
	print("✓ Test 3: Dodge cooldown gating passed")
	
	# Test 4: i-frame expiration and dodge completion
	player._process_dodge(0.22) # advance beyond iframe window (0.20s)
	assert(vitals.is_invulnerable == false, "i-frames should expire after 0.20s")
	player._process_dodge(0.10) # advance beyond dodge duration (0.28s)
	assert(player.current_state == PlayerController.State.IDLE, "Should return to IDLE after dodge ends")
	print("✓ Test 4: i-frame expiration & return to IDLE passed")
	
	# Test 5: Dodge fails when stamina is exhausted
	vitals.current_stamina = 10.0 # less than 20
	player._dodge_cooldown_timer = 0.0 # reset cooldown
	assert(player._can_dodge() == false, "Cannot dodge with insufficient stamina")
	print("✓ Test 5: Insufficient stamina rejection passed")
	
	print("--- All PlayerController Unit Tests Passed Successfully! ---")
	player.free()
	quit(0)
