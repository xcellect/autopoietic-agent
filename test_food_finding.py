# test_food_finding.py
"""
Quick validation test for autopoietic agent food-finding fixes
"""

from autopoietic_learner import AutopoieticAgent

def test_food_finding():
    """Test that agents can consistently find and consume food"""
    print("=" * 50)
    print("AUTOPOIETIC AGENT FOOD-FINDING VALIDATION")
    print("=" * 50)
    
    # Test parameters
    n_tests = 3
    max_steps = 400
    success_threshold = 1  # At least 1 food consumed
    
    results = []
    
    for test_num in range(n_tests):
        print(f"\nTest {test_num + 1}/{n_tests}:")
        
        agent = AutopoieticAgent(gui=False)
        history = agent.live_and_learn(max_steps=max_steps)
        stats = agent.get_survival_stats()
        
        print(f"  Survival: {stats['survival_time']} steps")
        print(f"  Food consumed: {stats['total_food_consumed']}")
        print(f"  Feeding efficiency: {stats['feeding_efficiency']:.3f}")
        print(f"  Learning ratio: {stats['learning_ratio']:.1%}")
        
        success = stats['total_food_consumed'] >= success_threshold
        results.append({
            'success': success,
            'food_consumed': stats['total_food_consumed'],
            'efficiency': stats['feeding_efficiency']
        })
        
        if success:
            print("  ✅ SUCCESS")
        else:
            print("  ❌ FAILED")
        
        agent.cleanup()
    
    # Summary
    successes = sum([r['success'] for r in results])
    total_food = sum([r['food_consumed'] for r in results])
    avg_efficiency = sum([r['efficiency'] for r in results]) / len(results)
    
    print(f"\n" + "=" * 50)
    print(f"VALIDATION RESULTS:")
    print(f"Success rate: {successes}/{n_tests} ({successes/n_tests*100:.1f}%)")
    print(f"Total food consumed: {total_food}")
    print(f"Average efficiency: {avg_efficiency:.3f}")
    
    if successes == n_tests:
        print("✅ ALL TESTS PASSED - Food-finding fixes working!")
    elif successes >= n_tests * 0.7:
        print("⚠ MOSTLY WORKING - Some agents still struggling")
    else:
        print("❌ FIXES INSUFFICIENT - Need more improvements")
    
    print("=" * 50)
    
    return successes == n_tests

def test_emergence_comparison():
    """Test the emergence comparison with fixed agents"""
    print("\nTesting emergence comparison...")
    
    # Rich agent
    rich_agent = AutopoieticAgent(gui=False)
    rich_agent.energy_decay = 0.05
    rich_agent.landauer_cost = 0.005
    rich_agent.learning_threshold = 25.0
    
    rich_history = rich_agent.live_and_learn(max_steps=400)
    rich_stats = rich_agent.get_survival_stats()
    rich_agent.cleanup()
    
    # Poor agent
    poor_agent = AutopoieticAgent(gui=False)
    poor_agent.energy_decay = 0.18
    poor_agent.landauer_cost = 0.025
    poor_agent.learning_threshold = 75.0
    
    poor_history = poor_agent.live_and_learn(max_steps=400)
    poor_stats = poor_agent.get_survival_stats()
    poor_agent.cleanup()
    
    print(f"\nEmergence Comparison Results:")
    print(f"Rich Agent - Food: {rich_stats['total_food_consumed']}, Efficiency: {rich_stats['feeding_efficiency']:.3f}")
    print(f"Poor Agent - Food: {poor_stats['total_food_consumed']}, Efficiency: {poor_stats['feeding_efficiency']:.3f}")
    
    both_found_food = rich_stats['total_food_consumed'] > 0 and poor_stats['total_food_consumed'] > 0
    
    if both_found_food:
        efficiency_ratio = poor_stats['feeding_efficiency'] / max(rich_stats['feeding_efficiency'], 0.001)
        print(f"Efficiency ratio (Poor/Rich): {efficiency_ratio:.2f}")
        
        if efficiency_ratio > 1.1:
            print("✅ EMERGENCE DETECTED: Poor agent more efficient!")
        elif efficiency_ratio > 0.9:
            print("~ COMPARABLE: Similar efficiency despite constraints")
        else:
            print("⚠ Rich agent more efficient (expected initially)")
        
        return True
    else:
        print("❌ Cannot compare - one or both agents failed to find food")
        return False

if __name__ == "__main__":
    # Run validation tests
    basic_success = test_food_finding()
    emergence_success = test_emergence_comparison()
    
    print(f"\n" + "=" * 50)
    print("FINAL VALIDATION:")
    print(f"Basic food-finding: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"Emergence comparison: {'✅ PASS' if emergence_success else '❌ FAIL'}")
    
    if basic_success and emergence_success:
        print("🎉 ALL FIXES SUCCESSFUL - Autopoietic agents working correctly!")
    else:
        print("⚠ Some issues remain - may need additional fixes")
    print("=" * 50)