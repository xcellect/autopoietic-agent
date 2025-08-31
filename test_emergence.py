# test_emergence.py
"""
Test the improved emergence experiment with better-balanced constraints
"""

from autopoietic_learner import AutopoieticAgent
import numpy as np

def test_improved_emergence():
    """Test emergence with better-balanced agent parameters"""
    
    print("=" * 60)
    print("IMPROVED AUTOPOIETIC EMERGENCE EXPERIMENT")
    print("=" * 60)
    print("Testing moderate scarcity vs abundance for emergence detection")
    
    # Test parameters
    n_runs = 3
    max_steps = 800  # Longer adaptation period
    
    rich_results = []
    poor_results = []
    
    print(f"\nRunning {n_runs} trials of each condition...\n")
    
    for run in range(n_runs):
        print(f"=== Trial {run+1}/{n_runs} ===")
        
        # Rich agent - abundant resources
        print("Rich agent (abundant resources):", end=" ")
        rich_agent = AutopoieticAgent(gui=False)
        rich_agent.energy_decay = 0.05          # Very slow decay
        rich_agent.landauer_cost = 0.005        # Very cheap computation
        rich_agent.learning_threshold = 25.0    # Low threshold
        
        rich_history = rich_agent.live_and_learn(max_steps=max_steps)
        rich_stats = rich_agent.get_survival_stats()
        rich_results.append(rich_stats)
        rich_agent.cleanup()
        
        print(f"Food: {rich_stats['total_food_consumed']}, Efficiency: {rich_stats['feeding_efficiency']:.3f}")
        
        # Poor agent - moderate scarcity (balanced constraints)
        print("Poor agent (moderate scarcity):", end=" ")
        poor_agent = AutopoieticAgent(gui=False)
        poor_agent.energy_decay = 0.12          # Moderate decay (was 0.18)
        poor_agent.landauer_cost = 0.015        # Moderate cost (was 0.025)
        poor_agent.learning_threshold = 60.0    # Moderate threshold (was 75.0)
        
        poor_history = poor_agent.live_and_learn(max_steps=max_steps)
        poor_stats = poor_agent.get_survival_stats()
        poor_results.append(poor_stats)
        poor_agent.cleanup()
        
        print(f"Food: {poor_stats['total_food_consumed']}, Efficiency: {poor_stats['feeding_efficiency']:.3f}")
    
    # Calculate aggregate statistics
    rich_avg_efficiency = np.mean([r['feeding_efficiency'] for r in rich_results])
    rich_std_efficiency = np.std([r['feeding_efficiency'] for r in rich_results])
    rich_avg_learning = np.mean([r['learning_ratio'] for r in rich_results])
    rich_avg_food = np.mean([r['total_food_consumed'] for r in rich_results])
    
    poor_avg_efficiency = np.mean([r['feeding_efficiency'] for r in poor_results])
    poor_std_efficiency = np.std([r['feeding_efficiency'] for r in poor_results])
    poor_avg_learning = np.mean([r['learning_ratio'] for r in poor_results])
    poor_avg_food = np.mean([r['total_food_consumed'] for r in poor_results])
    
    # Analysis
    print(f"\n" + "=" * 60)
    print("AGGREGATE EMERGENCE RESULTS")
    print("=" * 60)
    
    print(f"Rich Agent (abundant energy) - Average over {n_runs} trials:")
    print(f"  Food Consumed: {rich_avg_food:.1f}")
    print(f"  Learning Ratio: {rich_avg_learning:.1%}")
    print(f"  Feeding Efficiency: {rich_avg_efficiency:.3f} ± {rich_std_efficiency:.3f}")
    
    print(f"\nPoor Agent (moderate scarcity) - Average over {n_runs} trials:")
    print(f"  Food Consumed: {poor_avg_food:.1f}")
    print(f"  Learning Ratio: {poor_avg_learning:.1%}")
    print(f"  Feeding Efficiency: {poor_avg_efficiency:.3f} ± {poor_std_efficiency:.3f}")
    
    # Emergence metrics
    efficiency_ratio = poor_avg_efficiency / max(rich_avg_efficiency, 0.001)
    learning_ratio_diff = poor_avg_learning - rich_avg_learning
    food_ratio = poor_avg_food / max(rich_avg_food, 0.001)
    
    print(f"\n" + "=" * 60)
    print("STATISTICAL EMERGENCE ANALYSIS")
    print("=" * 60)
    print(f"Efficiency Ratio (Poor/Rich): {efficiency_ratio:.2f}")
    print(f"Food Consumption Ratio: {food_ratio:.2f}")
    print(f"Learning Time Difference: {learning_ratio_diff:+.1%}")
    
    # Determine emergence outcome
    print(f"\n" + "=" * 60)
    print("EMERGENCE EVALUATION")
    print("=" * 60)
    
    if efficiency_ratio > 1.15:
        print(f"✅ STRONG EMERGENCE DETECTED!")
        print(f"   Moderate scarcity led to {(efficiency_ratio-1)*100:.1f}% higher efficiency")
        print(f"   Resource constraints successfully drove adaptive optimization")
        emergence_detected = True
        emergence_strength = "Strong"
        
    elif efficiency_ratio > 1.05:
        print(f"✅ MILD EMERGENCE DETECTED")
        print(f"   Scarcity led to {(efficiency_ratio-1)*100:.1f}% efficiency improvement")
        print(f"   Autopoietic principle demonstrated")
        emergence_detected = True
        emergence_strength = "Mild"
        
    elif efficiency_ratio > 0.9:
        print(f"~ COMPARABLE EFFICIENCY")
        print(f"   Both agents performed similarly despite different constraints")
        print(f"   Suggests robust adaptation under both conditions")
        emergence_detected = False
        emergence_strength = "None (Comparable)"
        
    else:
        print(f"⚠ RICH AGENT MORE EFFICIENT")
        print(f"   Abundant resources enabled {(1/efficiency_ratio-1)*100:.1f}% better performance")
        print(f"   May need longer adaptation period or different constraint levels")
        emergence_detected = False
        emergence_strength = "None (Rich favored)"
    
    # Experimental validity check
    print(f"\n" + "=" * 60)
    print("EXPERIMENTAL VALIDITY")
    print("=" * 60)
    
    both_found_food = rich_avg_food > 0 and poor_avg_food > 0
    sufficient_learning = poor_avg_learning > 0.4 and rich_avg_learning > 0.7
    reasonable_constraint = poor_avg_learning / max(rich_avg_learning, 0.01) > 0.3
    
    print(f"✓ Both agents found food: {'YES' if both_found_food else 'NO'}")
    print(f"✓ Sufficient learning opportunities: {'YES' if sufficient_learning else 'NO'}")
    print(f"✓ Reasonable constraint level: {'YES' if reasonable_constraint else 'NO'}")
    
    if both_found_food and sufficient_learning and reasonable_constraint:
        print(f"✅ EXPERIMENTAL CONDITIONS VALID")
        print(f"   Results represent meaningful comparison of autopoietic dynamics")
    else:
        print(f"⚠ EXPERIMENTAL ISSUES DETECTED")
        print(f"   Consider adjusting parameters for more reliable emergence detection")
    
    print(f"\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Emergence Detected: {'YES' if emergence_detected else 'NO'}")
    print(f"Emergence Strength: {emergence_strength}")
    print(f"Efficiency Advantage: {abs(efficiency_ratio-1)*100:.1f}% ({'Poor agent' if efficiency_ratio > 1 else 'Rich agent'})")
    print(f"Experimental Validity: {'VALID' if both_found_food and sufficient_learning else 'NEEDS ADJUSTMENT'}")
    
    return {
        'emergence_detected': emergence_detected,
        'emergence_strength': emergence_strength,
        'efficiency_ratio': efficiency_ratio,
        'valid_experiment': both_found_food and sufficient_learning and reasonable_constraint,
        'rich_results': rich_results,
        'poor_results': poor_results
    }

if __name__ == "__main__":
    results = test_improved_emergence()
    
    if results['emergence_detected'] and results['valid_experiment']:
        print(f"\n🎉 SUCCESS: Emergence experiment working correctly!")
        print(f"   The Jupyter notebook should now demonstrate measurable autopoietic dynamics.")
    elif results['valid_experiment']:
        print(f"\n✓ EXPERIMENT VALID: No emergence detected, but conditions are sound")
        print(f"   This is a valid scientific result showing robust adaptation.")
    else:
        print(f"\n⚠ NEEDS IMPROVEMENT: Experimental conditions need refinement")
        print(f"   Consider further parameter adjustments.")