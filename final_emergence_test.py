# final_emergence_test.py
"""
Final validation test using the corrected parameters from CORRECT_PARAMETERS.md
"""

from autopoietic_learner import AutopoieticAgent
import numpy as np

def test_final_emergence():
    """Test emergence with corrected balanced parameters"""
    
    print("=" * 60)
    print("FINAL EMERGENCE VALIDATION TEST")
    print("=" * 60)
    print("Using CORRECT_PARAMETERS.md values with improved food-finding")
    
    n_trials = 3
    rich_results = []
    poor_results = []
    
    print(f"\nRunning {n_trials} trials for statistical validation...")
    
    for trial in range(n_trials):
        print(f"\n=== Trial {trial+1}/{n_trials} ===")
        
        # Rich agent - abundant resources
        print("Rich agent (abundant resources):", end=" ")
        rich_agent = AutopoieticAgent(gui=False)
        rich_agent.energy_decay = 0.05          # Very slow decay
        rich_agent.landauer_cost = 0.005        # Very cheap computation
        rich_agent.learning_threshold = 25.0    # Low threshold
        
        rich_history = rich_agent.live_and_learn(max_steps=1000)  # Adequate time
        rich_stats = rich_agent.get_survival_stats()
        rich_results.append(rich_stats)
        rich_agent.cleanup()
        
        print(f"Food: {rich_stats['total_food_consumed']}, Efficiency: {rich_stats['feeding_efficiency']:.3f}, Learning: {rich_stats['learning_ratio']:.1%}")
        
        # Poor agent - moderate scarcity (CORRECTED)
        print("Poor agent (moderate scarcity):", end=" ")
        poor_agent = AutopoieticAgent(gui=False)
        poor_agent.energy_decay = 0.12          # Moderate decay (NOT 0.18)
        poor_agent.landauer_cost = 0.015        # Moderate cost (NOT 0.025)
        poor_agent.learning_threshold = 60.0    # Moderate threshold (NOT 75.0)
        
        poor_history = poor_agent.live_and_learn(max_steps=1000)  # Adequate time
        poor_stats = poor_agent.get_survival_stats()
        poor_results.append(poor_stats)
        poor_agent.cleanup()
        
        print(f"Food: {poor_stats['total_food_consumed']}, Efficiency: {poor_stats['feeding_efficiency']:.3f}, Learning: {poor_stats['learning_ratio']:.1%}")
    
    # Calculate statistics
    rich_avg_food = np.mean([r['total_food_consumed'] for r in rich_results])
    rich_avg_efficiency = np.mean([r['feeding_efficiency'] for r in rich_results])
    rich_avg_learning = np.mean([r['learning_ratio'] for r in rich_results])
    
    poor_avg_food = np.mean([r['total_food_consumed'] for r in poor_results])
    poor_avg_efficiency = np.mean([r['feeding_efficiency'] for r in poor_results])
    poor_avg_learning = np.mean([r['learning_ratio'] for r in poor_results])
    
    print(f"\n" + "=" * 60)
    print("AGGREGATE RESULTS")
    print("=" * 60)
    
    print(f"Rich Agent (abundant energy) - Average over {n_trials} trials:")
    print(f"  Food Consumed: {rich_avg_food:.1f}")
    print(f"  Learning Ratio: {rich_avg_learning:.1%}")
    print(f"  Feeding Efficiency: {rich_avg_efficiency:.3f}")
    
    print(f"\nPoor Agent (moderate scarcity) - Average over {n_trials} trials:")
    print(f"  Food Consumed: {poor_avg_food:.1f}")
    print(f"  Learning Ratio: {poor_avg_learning:.1%}")
    print(f"  Feeding Efficiency: {poor_avg_efficiency:.3f}")
    
    # Emergence analysis
    if rich_avg_food >= 1 and poor_avg_food >= 1:
        efficiency_ratio = poor_avg_efficiency / rich_avg_efficiency
        learning_ratio_diff = poor_avg_learning - rich_avg_learning
        
        print(f"\n" + "=" * 60)
        print("EMERGENCE ANALYSIS")
        print("=" * 60)
        print(f"Efficiency Ratio (Poor/Rich): {efficiency_ratio:.2f}")
        print(f"Learning Ratio Difference: {learning_ratio_diff:+.1%}")
        
        if efficiency_ratio > 1.15:
            print(f"\n✅ STRONG EMERGENCE DETECTED!")
            print(f"   Moderate scarcity led to {(efficiency_ratio-1)*100:.1f}% higher efficiency")
            print(f"   Resource constraints successfully drove adaptive optimization")
            emergence_detected = True
        elif efficiency_ratio > 1.05:
            print(f"\n✅ MILD EMERGENCE DETECTED")
            print(f"   Scarcity led to {(efficiency_ratio-1)*100:.1f}% efficiency improvement")
            emergence_detected = True
        elif efficiency_ratio > 0.9:
            print(f"\n~ COMPARABLE EFFICIENCY")
            print(f"   Both agents performed similarly despite different constraints")
            emergence_detected = False
        else:
            print(f"\n⚠ RICH AGENT MORE EFFICIENT")
            print(f"   Abundant resources enabled {(1/efficiency_ratio-1)*100:.1f}% better performance")
            emergence_detected = False
        
        # Validation checks
        both_found_food = rich_avg_food >= 1 and poor_avg_food >= 1
        sufficient_learning = poor_avg_learning > 0.3 and rich_avg_learning > 0.6
        reasonable_constraint = poor_avg_learning / max(rich_avg_learning, 0.01) > 0.3
        
        print(f"\n" + "=" * 60)
        print("EXPERIMENTAL VALIDITY")
        print("=" * 60)
        print(f"✓ Both agents found food: {'YES' if both_found_food else 'NO'}")
        print(f"✓ Sufficient learning opportunities: {'YES' if sufficient_learning else 'NO'}")
        print(f"✓ Reasonable constraint level: {'YES' if reasonable_constraint else 'NO'}")
        
        valid_experiment = both_found_food and sufficient_learning and reasonable_constraint
        
        if valid_experiment:
            print(f"✅ EXPERIMENTAL CONDITIONS VALID")
            print(f"   Results represent meaningful comparison of autopoietic dynamics")
        else:
            print(f"⚠ EXPERIMENTAL ISSUES DETECTED")
            
        return {
            'emergence_detected': emergence_detected,
            'efficiency_ratio': efficiency_ratio,
            'valid_experiment': valid_experiment,
            'rich_avg_food': rich_avg_food,
            'poor_avg_food': poor_avg_food,
            'rich_avg_learning': rich_avg_learning,
            'poor_avg_learning': poor_avg_learning
        }
        
    else:
        print(f"\n❌ INSUFFICIENT FOOD CONSUMPTION FOR VALID COMPARISON")
        print(f"Rich: {rich_avg_food:.1f}, Poor: {poor_avg_food:.1f}")
        return {
            'emergence_detected': False,
            'valid_experiment': False,
            'rich_avg_food': rich_avg_food,
            'poor_avg_food': poor_avg_food
        }

if __name__ == "__main__":
    results = test_final_emergence()
    
    print(f"\n" + "=" * 60)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 60)
    
    if results['emergence_detected'] and results['valid_experiment']:
        print(f"🎉 SUCCESS: Emergence experiment working correctly!")
        print(f"   The Jupyter notebook will demonstrate measurable autopoietic dynamics")
        print(f"   Efficiency ratio: {results['efficiency_ratio']:.2f}")
    elif results['valid_experiment']:
        print(f"✓ EXPERIMENT VALID: No emergence detected, but conditions are sound")
        print(f"   This is a valid scientific result")
    else:
        print(f"⚠ NEEDS IMPROVEMENT: Food-finding still inconsistent")
        print(f"   Rich food: {results.get('rich_avg_food', 0):.1f}, Poor food: {results.get('poor_avg_food', 0):.1f}")